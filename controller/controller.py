import datetime, os, shutil

from PySide6.QtCore import QEventLoop

from controller.base import BaseController
from picture_metadata import load_xmp_from_file, write_xmp_to_file, load_exif_from_file, write_exif_to_file, exif_timestamp_to_datetime
from util import list_files, optimize_image, rotate_image, set_image_permissions, set_image_timestamp

class Controller(BaseController):
    """Controller for keeping the application state, updating the UI
    accordingly, and for performing filesystem operations."""

    def __init__(self, config, context):
        super().__init__(config, context)

        self.current_path = None
        self.current_files = None
        self.currently_selected = None
        # Give list offsets for each identifier.
        self.offsets = {
            "path":            0,
            "edited":          1,
            "delete":          2,
            "metadata":        3,
            "transformations": 4,
        }

        self.answer = None
        self.loop = QEventLoop()

        self._setup_state_machine()

        # Signals.
        self.context.request_directory_change.connect(self.handle_request_directory_change)
        self.context.request_selected_changed.connect(self.handle_request_select_files)
        self.context.discard_edits.connect(self.handle_discard_edits)
        self.context.event_edit.connect(self.handle_event_edit)
        self.context.request_rename.connect(self.handle_request_rename)
        self.context.request_delete.connect(self.handle_request_delete)
        self.context.request_undelete.connect(self.handle_request_undelete)
        self.context.request_rotation.connect(self.handle_request_rotation)
        self.context.request_save.connect(self.handle_request_save)
        self.context.request_adjust_time.connect(self.handle_request_adjust_time)
        self.context.request_adjust_utc_offset.connect(self.handle_request_utc_offset)

    def get_current(self, idx, identifier=None):
        """Return data for the current file at the given idx. If identifier is
        None, return all data."""

        if identifier is None:
            return self.current_files[idx]

        if identifier not in self.offsets:
            raise ValueError(f"Unknown identifier {identifier}.")
        else:
            return self.current_files[idx][self.offsets[identifier]]

    def set_current(self, idx, identifier, value):
        """Set data for the current file at the given idx."""

        if identifier not in self.offsets:
            raise ValueError(f"Unknown identifier {identifier}.")
        else:
            self.current_files[idx][self.offsets[identifier]] = value

    def handle_request_directory_change(self, path, recursive=False):
        """Handles a directory change request."""

        # If the path is already open, do nothing.
        if path == self.current_path: return

        # First, we check if we have edited but unchanged metadata. If so, we
        # ask the user to explicitly discard the edits before changing the
        # directory.
        state = self.get_state()
        if state.group_edited == "edited":
            # There are unsaved and edited changes.
            # If cancelled, do nothing.
            # If discarded, emit a discard signal, change state to unedited,
            # and continue.

            # TODO: Make this a generic pattern as we will likely use it again.

            def wait(answer):
                self.answer = answer
                self.loop.quit()

            self.context.answer_received.connect(wait)
            self.context.ask_discard_changes.emit()
            if self.answer is None:
                self.loop.exec()
            self.context.answer_received.disconnect(wait)
            proceed = self.answer
            self.answer = None

            if not proceed:
                # Do nothing, but restore the previously clicked item.
                self.context.files_not_updated.emit()
                return
            else:
                # Discard the edits (changes state).
                self.context.discard_edits.emit()

        # Now we are going to load the contents of a new directory.
        files = list_files(path, recursive=recursive)
        # Save the files and set the associated metadata to None.
        self.current_path = path
        self.current_files = [[f, False, False, None, {}] for f in files] # file path, edited, delete, metadata, transformations
        self.currently_selected = []
        self.context.update_files.emit(path, files)

    def handle_discard_edits(self):
        """Handles the request to discard all edits."""

        # We simply reset the following variables:
        self.current_path = None
        self.current_files = None
        self.currently_selected = None

    def set_metadata(self, files_idx, metadata):
        """Sets the metadata of the specified files."""

        # We set all files for the given indices to have the given metadata.
        # The value None works differently depending on the number of files. If
        # there is one file, None means that the corresponding metadata entry
        # is set to None. If there are multiple files, value None means that
        # nothing is done.
        multiple = len(files_idx) > 1
        for idx in files_idx:
            for k in metadata:
                if not multiple or (multiple and metadata[k] is not None):
                    self.get_current(idx, "metadata")[k] = metadata[k]

    def save_selected_metadata(self):
        """Gets the metadata of the selected and edited files from the UI, and
        saves it."""

        edited = [idx for idx in self.currently_selected if self.get_current(idx, "edited")]
        if len(edited) > 0:
            metadata_for_edited = self.app.get_metadata()
            self.set_metadata(edited, metadata_for_edited)

    def handle_request_select_files(self, files_idx):
        """Handles the request to edit the metadata of the given files."""

        # Before changing the selection, we save the changes in selected and
        # edited files.
        self.save_selected_metadata()

        if len(files_idx) == 0:
            self.currently_selected = []
            self.context.edit_zero_files.emit()
            return

        # First, we load the metadata from the files if necessary so that the
        # data is available later.
        # NOTE: This can be slow for many files. Maybe this should be cancellable?
        for n, idx in enumerate(files_idx):
            file_name = self.get_current(idx, "path")
            if self.get_current(idx, "metadata") is None:
                # No data loaded yet, load it from file.
                try:
                    metadata = load_xmp_from_file(file_name, default_time_zone=self.config.general.default_time_zone, ignore_errors=True)
                    # If there is no XMP date time in the file, attempt to load
                    # this information from EXIF tags.
                    if metadata["date_time"] is None:
                        r = load_exif_from_file(file_name, ["Exif.Image.DateTime"])
                        if "Exif.Image.DateTime" in r:
                            metadata["date_time"] = exif_timestamp_to_datetime(r["Exif.Image.DateTime"], time_zone=self.config.general.default_time_zone)

                    self.set_current(idx, "metadata", metadata)
                except:
                    # TODO: Exception handling.
                    raise

            # Signal how many files have been handled.
            self.context.indicate_progress.emit(n + 1)

        if len(files_idx) == 1:
            # Edit a single file's metadata.
            idx = files_idx[0]
            metadata = self.get_current(idx, "metadata")

            # Display the selected data.
            self.context.update_metadata.emit(
                metadata["author"],
                metadata["date_time"],
                metadata["city"],
                metadata["country"],
                metadata["title"],
                metadata["description"],
                metadata["tags"],
                True,                    # Single file to edit.
            )

            # Set the currently selected files.
            self.currently_selected = [idx]

            # Change state.
            self.context.edit_one_file.emit()
        else:
            # Edit multiple files' metadata.
            #
            # We figure out the common values in all entries. The entries with
            # a common value, we set to contain that value; other entries are
            # set to None. Datetime is always set None as its common value
            # rarely makes sense.
            common_entries = {}
            for entry in ["author", "city", "country", "title", "description"]:
                entries = list({self.get_current(idx, "metadata")[entry] for idx in files_idx})
                common_entry = entries[0] if len(entries) == 1 else None
                common_entries[entry] = common_entry
            common_entries["date_time"] = None
            # We handle tags separately as we want to check equality up to
            # order.
            # NOTE: This is done simply but not necessarily efficiently if
            # there are really many selected files.
            tags = []
            for file_tags in [self.get_current(idx, "metadata")["tags"] for idx in files_idx]:
                tag_set = set(file_tags) if file_tags is not None else None
                if tag_set not in tags:
                    tags.append(tag_set)
            common_entries["tags"] = (list(tags[0]) if tags[0] is not None else None) if len(tags) == 1 else None

            self.context.update_metadata.emit(
                common_entries["author"],
                common_entries["date_time"],
                common_entries["city"],
                common_entries["country"],
                common_entries["title"],
                common_entries["description"],
                common_entries["tags"],
                False,                         # Multiple files to edit.
            )

            # Set the currently selected files.
            self.currently_selected = files_idx

            # Change state.
            self.context.edit_many_files.emit()

    def handle_event_edit(self, files_idx):
        """Handles the event that the metadata entries of the selected files
        are edited or the files are edited otherwise."""

        for idx in files_idx:
            self.set_current(idx, "edited", True)

    def handle_request_rename(self, files_idx):
        """Handles the event that the given files are renamed."""

        # We simply set the new names according to the date times.
        # TODO: The rename method should be user-selectable.

        # Get the current metadata from the UI in case the data needed for
        # rename has changed.
        self.save_selected_metadata()

        def format_file_name(current_file_name, metadata):
            """Format a new file name according to the metadata."""

            extension = current_file_name.split(".")[-1]
            if extension == "jpeg":
                extension = "jpg"
            extension = extension.lower() if extension.lower() == "jpg" else extension

            if metadata is None:
                return None

            if metadata["date_time"] is not None:
                d = metadata["date_time"]
                return f"{d.year:04}{d.month:02}{d.day:02}_{d.hour:02}{d.minute:02}{d.second:02}.{extension}"
            else:
                return None

        renamed = []
        for idx in files_idx:
            new_file_name = format_file_name(self.get_current(idx, "path"), self.get_current(idx, "metadata"))
            if new_file_name is None: continue
            if "rename" not in self.get_current(idx, "transformations"):
                self.get_current(idx, "transformations")["rename"] = None

            self.get_current(idx, "transformations")["rename"] = new_file_name
            renamed.append((idx, new_file_name))

        self.context.rename_files.emit(renamed)

    def handle_request_delete(self, files_idx):
        """Handles the event that the given files are deleted."""

        for idx in files_idx:
            self.set_current(idx, "delete", True)

    def handle_request_undelete(self, files_idx):
        """Handles the event that the given files are undeleted."""

        for idx in files_idx:
            self.set_current(idx, "delete", False)

    def handle_request_rotation(self, files_idx):
        """Handles the event that the given files are rotated by 90 degrees."""

        for idx in files_idx:
            if "rotate" not in self.get_current(idx, "transformations"):
                self.get_current(idx, "transformations")["rotate"] = 0

            self.get_current(idx, "transformations")["rotate"] = (self.get_current(idx, "transformations")["rotate"] + 90) % 360

    def handle_request_save(self, optimize=False):
        """Handles the event that the edited files are requested to be saved."""

        # Save the changes in selected edited files.
        self.save_selected_metadata()

        for n, idx in enumerate(range(len(self.current_files))):
            file_name = self.get_current(idx, "path")
            metadata = self.get_current(idx, "metadata")
            transformations = self.get_current(idx, "transformations")

            # Remove the file if requested.
            # Notice that this must be done before we consider if a file has
            # been edited.
            if self.get_current(idx, "delete"):
                # Only delete if the file exists (the file might have already
                # been removed by a previous save event).
                if os.path.exists(file_name):
                    os.unlink(file_name)
                self.context.file_deleted.emit(idx)
                self.context.indicate_progress.emit(n + 1)
                continue

            # Skip files that have not been edited.
            if not self.get_current(idx, "edited"):
                self.context.indicate_progress.emit(n + 1)
                continue

            # Write the XMP tags.
            write_xmp_to_file(file_name, metadata, language=self.config.general.default_language)

            # Check if XMP date time and existing EXIF tag date times mismatch,
            # and update EXIF tags if necessary.
            #
            # First we list some possible tags that contain the date time. This
            # list is probably not exhaustive.
            exif_tags = [
                "Exif.Image.DateTime",
                "Exif.Photo.DateTimeOriginal",
                "Exif.Photo.DateTimeDigitized",
                "Exif.SonySInfo1.SonyDateTime"
            ]
            r = load_exif_from_file(file_name, exif_tags)
            s_xmp = metadata["date_time"].strftime("%Y:%m:%d %H:%M:%S") if metadata["date_time"] is not None else None
            updated = {}
            for tag in exif_tags:
                if tag in r:
                    dt_exif = exif_timestamp_to_datetime(r[tag])
                    s_exif = dt_exif.strftime("%Y:%m:%d %H:%M:%S")
                    if s_exif != s_xmp:
                        updated[tag] = s_xmp
            if len(updated) > 0:
                write_exif_to_file(file_name, updated)

            # Perform transformations.
            # Rotation.
            if "rotate" in transformations:
                angle = transformations["rotate"]
                rotate_image(file_name, angle)
            # Rename.
            if "rename" in transformations:
                new_file_name = os.path.join(os.path.dirname(file_name), transformations["rename"])
                if file_name != new_file_name:
                    prefix = ".".join(transformations["rename"].split(".")[:-1])
                    extension = transformations["rename"].split(".")[-1]
                    count = 1
                    while os.path.exists(new_file_name):
                        new_file_name = os.path.join(os.path.dirname(file_name), f"{prefix} ({count}).{extension}")
                        count += 1
                    shutil.move(file_name, new_file_name)
                    self.set_current(idx, "path", new_file_name)
                    file_name = new_file_name

            # Optimize.
            if optimize:
                optimize_image(file_name)

            # Set the edit times to match the date time.
            dt = metadata["date_time"]
            if dt is not None:
                set_image_timestamp(file_name, dt)

            # Set permissions to 644.
            set_image_permissions(file_name)

            # Set the edited flag to False.
            self.set_current(idx, "edited", False)

            # Signal how many files have been handled.
            self.context.indicate_progress.emit(n + 1)

        self.context.saved_edits.emit()

    def handle_request_adjust_time(self, seconds):
        """Handles the event that the given number of seconds should be added
        to the timestamps of the selected files."""

        timedelta = datetime.timedelta(seconds=seconds)
        for idx in self.currently_selected:
            self.get_current(idx, "metadata")["date_time"] += timedelta

    def handle_request_utc_offset(self, utc_offset):
        """Handles the event that the given number of hours should be added to
        the UTC offsets of the selected files."""

        for idx in self.currently_selected:
            dt = self.get_current(idx, "metadata")["date_time"]

            # Make sure that the new offset is between -12 and 12.
            old_offset = float(dt.utcoffset().total_seconds() / 3600)
            new_offset = old_offset + 12 + utc_offset
            new_offset = (new_offset % 25) - 12
            timedelta = datetime.timedelta(seconds=new_offset*3600)
            new_tz = datetime.timezone(timedelta)

            dt = dt.replace(tzinfo=new_tz)
            self.get_current(idx, "metadata")["date_time"] = dt

