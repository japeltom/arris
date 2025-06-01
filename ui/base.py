import os, datetime

from PySide6.QtCore import QCoreApplication, Qt, QDir, QTimer
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QAbstractItemView, QFileSystemModel, QGridLayout, QLabel, QListWidgetItem, QMessageBox, QProgressBar, QSizePolicy, QStyle, QSpacerItem, QVBoxLayout, QWidget

from ui.tag_adder import TagAdder
from ui.thumbnail_loader import ThumbnailLoader
from ui.time_adjuster import TimeAdjuster

from util import items, setup_separator_completer, datetime_to_qdatetime, qdatetime_to_datetime
from picture_metadata import get_empty_picture_data

class Base_MainWindow:
    """An abstract base class for element setup, signal setup, and some generic
    GUI code that is not tied to program logic."""

    # Data offsets for various data saved in a list view item.
    OFFSET_IDX = 256
    OFFSET_PATH = 257
    OFFSET_RELATIVE_PATH = 258
    OFFSET_THUMBNAIL = 259
    OFFSET_ROTATE = 260

    THUMBNAIL_WIDTH = 200 # Width for thumbnails (we preserve aspect ratio).
    PREVIEW_COLUMNS = 2   # Into how many columns the thumbnails are put.

    ACCURACY = 2 # Number of digits for fractional UTC offsets.

    def __init__(self):
        # Create custom context managers for disabling signals.

        class CtxSelectionChanged:
            """For disabling the signals that are emitted when the list widget
            selection changes."""

            def __init__(self, app):
                self.app = app
                self.count = 0

            def __enter__(self):
                if self.count == 0:
                    self.app.files_listWidget.itemSelectionChanged.disconnect(self.app.on_selection_changed)
                self.count += 1

            def __exit__(self, type, value, traceback):
                if self.count == 1:
                    self.app.files_listWidget.itemSelectionChanged.connect(self.app.on_selection_changed)
                self.count -= 1

        class CtxMetadataSignals:
            """For disabling the signals that are emitted when the metadata
            entries are edited."""

            def __init__(self, app):
                self.app = app
                self.count = 0

            def __enter__(self):
                if self.count == 0:
                    self.app.signals_metadata(connect=False)
                self.count += 1

            def __exit__(self, type, value, traceback):
                if self.count == 1:
                    self.app.signals_metadata(connect=True)
                self.count -= 1

        self.disabled_selection_changed_signals = CtxSelectionChanged(self)
        self.disabled_edit_signals = CtxMetadataSignals(self)

    def _setup_widgets(self, default_path=None):
        self._setup_toolbar()
        self._setup_statusbar()
        self._setup_filesystem_treeView(default_path=default_path)
        self._setup_files_listWidget()
        self._setup_metadata_widgets()
        self._setup_buttons()
        self._setup_image_container()

    def _setup_signals(self):
        self._setup_signals_context()
        self._setup_signals_ui()
        self._setup_signals_metadata()

        # Metadata entries checkbox toggles.
        checkboxes = {
            "metadata_author_checkBox": ["metadata_author"],
            "metadata_date_checkBox": ["metadata_date", "metadata_utc"],
            "metadata_city_checkBox": ["metadata_city"],
            "metadata_country_checkBox": ["metadata_country"],
            "metadata_title_checkBox": ["metadata_title"],
            "metadata_description_checkBox": ["metadata_description"],
            "metadata_tags_checkBox": ["metadata_tags", "tagadder_button"],
        }
        for checkbox_id, widget_ids in checkboxes.items():
            checkbox = getattr(self, checkbox_id)
            widgets = [getattr(self, widget_id) for widget_id in widget_ids]
            f = lambda x, checkbox=checkbox, widgets=widgets: [widget.setEnabled(checkbox.isChecked()) for widget in widgets]
            checkbox.checkStateChanged.connect(f)

    def _setup_toolbar(self):
        style = self.style()
        icon = style.standardIcon(QStyle.SP_DriveFDIcon)
        #icon = QIcon("path/to/icon")
        self.actionSave.setIcon(icon)
        self.actionSave.setEnabled(False)

    def _setup_statusbar(self):
        self.progress_bar = QProgressBar()
        self.statusbar.addPermanentWidget(self.progress_bar)
        self.progress_bar.setVisible(False)
        self.progress_value = 0

    def _setup_filesystem_treeView(self, default_path):
        # Set up file system model.
        self.model = QFileSystemModel()
        path = QDir.rootPath() if default_path is None else default_path
        self.model.setRootPath(path)
        # List only directories and no . and ..
        self.model.setFilter(QDir.AllDirs | QDir.NoDotAndDotDot)

        # Set the model for the tree view.
        self.filesystem_treeView.setModel(self.model)

        # Set the root index to home directory.
        path = QDir.homePath() if default_path is None else default_path
        self.filesystem_treeView.setRootIndex(self.model.index(path))

        # Hide columns (only show Name, hide Size, Type, Date Modified).
        for i in range(1, 4):
            self.filesystem_treeView.hideColumn(i)

    def _setup_files_listWidget(self):
        # Allow multiple selection
        self.files_listWidget.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.files_listWidget.setSelectionBehavior(QAbstractItemView.SelectItems)

    def _setup_metadata_widgets(self):
        # Set up completers.
        word_list = self.config.completion.author
        setup_separator_completer(self.metadata_author, word_list, separator="")

        self.metadata_groupBox.setEnabled(False)

        self.metadata_date.setCalendarPopup(True)
        self.metadata_date.setDisplayFormat("dd.MM.yyyy HH:mm:ss")
        self.metadata_utc.setRange(-12, 12)
        self.metadata_utc.setValue(0)
        self.metadata_utc.setSuffix(" UTC")
        self.metadata_utc.setDecimals(self.ACCURACY)

        self.metadata_city.setEditable(True)
        self.metadata_country.setEditable(True)
        self.metadata_city.addItems(self.config.completion.city)
        self.metadata_country.addItems(self.config.completion.country)

    def _setup_buttons(self):
        # Set up the buttons in the metadata group box.
        self.undelete_button.setEnabled(False)

    def _setup_image_container(self):
        # For reasons beyond me, we must create the container QWidget here and
        # explicitly attach it to the scroll area via the setWidget method. If
        # this is not done (e.g., when creating the container directly in Qt
        # Creator), the scroll bars do not work correctly.
        self.image_container = QWidget()
        self.image_container_scrollArea.setWidgetResizable(True)
        self.image_container_scrollArea.setWidget(self.image_container)
        self.grid_layout = QGridLayout(self.image_container)
        self.image_container.setLayout(self.grid_layout)
        self.image_container_scrollArea.setEnabled(False)

    def _setup_signals_context(self):
        # State changes.
        self.context.enter_initial.connect(self.enter_initial)
        self.context.edit_zero_files.connect(self.enter_edit_zero_files)
        self.context.edit_one_file.connect(self.enter_edit_one_file)
        self.context.edit_many_files.connect(self.enter_edit_many_files)

        # Other.
        self.context.update_files.connect(self.populate_listWidget)
        self.context.files_not_updated.connect(self.restore_selection)
        self.context.ask_discard_changes.connect(self.ask_discard_changes)
        self.context.update_metadata.connect(self.populate_metadata_entries)
        self.context.file_deleted.connect(self.remove_listWidget)
        self.context.rename_files.connect(self.rename_files)
        self.context.indicate_progress.connect(self.indicate_progress)

    def _setup_signals_ui(self):
        self.filesystem_treeView.clicked.connect(self.on_directory_clicked)
        self.files_listWidget.itemSelectionChanged.connect(self.on_selection_changed)
        self.rename_button.clicked.connect(self.on_rename)
        self.delete_button.clicked.connect(self.on_delete)
        self.undelete_button.clicked.connect(self.on_undelete)
        self.rotate_button.clicked.connect(self.on_rotate)
        self.tagadder_button.clicked.connect(self.open_tag_adder)
        self.adjust_time_button.clicked.connect(self.open_time_adjuster)
        self.actionSave.triggered.connect(self.on_save)

    def _setup_signals_metadata(self):
        entries = {
            "author":      [self.metadata_author.textChanged, self.metadata_author_checkBox.checkStateChanged],
            "date":        [self.metadata_date.dateTimeChanged, self.metadata_date_checkBox.checkStateChanged],
            "utc":         [self.metadata_utc.textChanged],
            "city":        [self.metadata_city.editTextChanged, self.metadata_city_checkBox.checkStateChanged],
            "country":     [self.metadata_country.editTextChanged, self.metadata_country_checkBox.checkStateChanged],
            "title":       [self.metadata_title.textChanged, self.metadata_title_checkBox.checkStateChanged],
            "description": [self.metadata_description.textChanged, self.metadata_description_checkBox.checkStateChanged],
            "tags":        [self.metadata_tags.textChanged, self.metadata_tags_checkBox.checkStateChanged]
        }

        for entry, signals in entries.items():
            for signal in signals:
                func = lambda: self.context.metadata_entry_changed.emit()
                signal.connect(func)

    def signals_metadata(self, connect=True):
        """Connects or disconnects the metadata edits to the metadata_edited
        signals."""

        if not hasattr(self, "signals_metadata_connected"):
            self.signals_metadata_connected = False

        if connect:
            if self.signals_metadata_connected: return
            self.context.metadata_entry_changed.connect(self.on_event_edit)
            self.signals_metadata_connected = True
        else:
            if not self.signals_metadata_connected: return
            self.context.metadata_entry_changed.disconnect(self.on_event_edit)
            self.signals_metadata_connected = False

    def get_selected_idx(self):
        """Returns the selected items and their indices."""

        selected = self.files_listWidget.selectedItems()
        files_idx = [item.data(self.OFFSET_IDX) for item in selected]

        return selected, files_idx

    def ask_user_discard(self, title, text):
        """Prompts the user with a dialog with the given title and text and
        buttons 'Discard' and 'Cancel'. The return value is True if and only if
        the discard button was pressed."""

        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(title)
        msg_box.setText(text)
        msg_box.setIcon(QMessageBox.Question)
        msg_box.setStandardButtons(QMessageBox.Discard | QMessageBox.Cancel)

        result = msg_box.exec()

        return result == QMessageBox.Discard

    def setup_thumbnail_loading(self, files):
        """Sets up a thread that loads thumbnails for the given list of
        grid_index, list_index, filename triples."""

        if not hasattr(self, "thumbnail_loader_thread"):
            self.thumbnail_loader_thread = None
        if self.thumbnail_loader_thread is not None and not self.thumbnail_loader_thread.isFinished():
            self.thumbnail_loader_thread.stop()

        self.thumbnail_loader_thread = ThumbnailLoader(files, width=self.THUMBNAIL_WIDTH)
        self.thumbnail_loader_thread.thumbnail_loaded.connect(self.display_thumbnail)

        self.thumbnail_loader_thread.start()

    def display_thumbnail(self, grid_idx, list_idx, thumbnail):
        width = self.THUMBNAIL_WIDTH + 10

        selected, _ = self.get_selected_idx()
        item = None
        for x in selected:
            if x.data(self.OFFSET_IDX) == list_idx:
                item = x
                break
        if item is None:
            # This can happen if the user changes the selection while the
            # thumbnails are being loaded.
            return

        item.setData(self.OFFSET_THUMBNAIL, thumbnail)

        # Caption.
        caption_label = QLabel(item.data(self.OFFSET_RELATIVE_PATH))
        caption_label.setAlignment(Qt.AlignCenter)
        caption_label.setWordWrap(True)
        caption_label.setFixedWidth(width)
        caption_label.setStyleSheet("font-size: 12px;")

        # Thumbnail.
        image_label = QLabel()
        image_label.setPixmap(thumbnail)
        image_label.setAlignment(Qt.AlignCenter)
        image_label.setFixedWidth(width)

        # Vertical spacer.
        spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        # Vertical layout: caption above image.
        thumb_widget = QWidget()
        thumb_layout = QVBoxLayout(thumb_widget)
        thumb_layout.setContentsMargins(0, 0, 0, 0)
        thumb_layout.addWidget(caption_label)
        thumb_layout.addWidget(image_label)
        thumb_layout.addItem(spacer)

        # Add to grid.
        row = grid_idx // self.PREVIEW_COLUMNS
        col = grid_idx % self.PREVIEW_COLUMNS
        self.grid_layout.addWidget(thumb_widget, row, col)

        # Signals for clicking.
        image_label.mousePressEvent = lambda event, item=item: self.on_thumbnail_clicked(event, item.data(self.OFFSET_PATH), rotation_angle=item.data(self.OFFSET_ROTATE))

    def setup_progress_bar(self, maximum):
        """Enables the progress bar in the status bar. The maximum is set to
        the given value, and the current value is set to 0."""

        def disable_with_delay():
            if self.progress_value < self.progress_bar.maximum():
                self.setEnabled(False)

        self.progress_value = 0
        self.progress_bar.setValue(self.progress_value)
        self.progress_bar.setMaximum(maximum)
        if maximum > 0:
            self.progress_bar.setVisible(True)
            # We delay setting all elements disabled to avoid flicker when the
            # load is fast.
            QTimer.singleShot(200, disable_with_delay)

    def indicate_progress(self, progress):
        """Advances the status bar progress bar to the indicated value."""

        QCoreApplication.processEvents()
        self.progress_value = progress
        self.progress_bar.setValue(self.progress_value)
        if self.progress_value >= self.progress_bar.maximum():
            self.progress_bar.setVisible(False)
            self.setEnabled(True)

    def get_metadata(self):
        """Return the metadata currently written in the metadata entries."""

        # If the entry is disabled (via the checkbox), we leave the value to be
        # None. An empty value is always treated as None.

        metadata = get_empty_picture_data()

        # We handle date time and tags separately and others with a common code.
        entries = {
            "author":      self.metadata_author.text(),
            "city":        self.metadata_city.currentText(),
            "country":     self.metadata_country.currentText(),
            "title":       self.metadata_title.text(),
            "description": self.metadata_description.toPlainText(),
        }
        for entry, content in entries.items():
            is_empty = len(content) == 0
            if not is_empty:
                metadata[entry] = content

        # Date time.
        if self.metadata_date_checkBox.isChecked():
            date_time = self.metadata_date.dateTime()
            date = date_time.date()
            time = date_time.time()
            utc_offset = float(self.metadata_utc.text().split(" ")[0])
            timedelta = datetime.timedelta(seconds=utc_offset*3600)
            dt = datetime.datetime(
                year=date.year(),
                month=date.month(),
                day=date.day(),
                hour=time.hour(),
                minute=time.minute(),
                second=time.second(),
                tzinfo=datetime.timezone(timedelta)
            )
            metadata["date_time"] = dt
        else:
            metadata["date_time"] = None

        # Tags.
        if self.metadata_tags_checkBox.isChecked():
            split_tags = self.metadata_tags.text().split(",")
            if len(split_tags) == 1 and len(split_tags[0]) == 0:
                metadata["tags"] = None
            else:
                metadata["tags"] = split_tags

        return metadata

    def populate_listWidget(self, path, files):
        """Populate the list widget with the given files."""

        self.depopulate_listWidget()
        for n, f in enumerate(files):
            item = QListWidgetItem(os.path.relpath(f, path))
            item.setData(self.OFFSET_IDX, n)
            item.setData(self.OFFSET_PATH, f)
            item.setData(self.OFFSET_RELATIVE_PATH, os.path.relpath(f, path))
            item.setData(self.OFFSET_THUMBNAIL, None)
            item.setData(self.OFFSET_ROTATE, 0)
            self.files_listWidget.addItem(item)

    def depopulate_listWidget(self):
        """Depopulates the list widget."""

        with self.disabled_selection_changed_signals:
            self.clear_thumbnails()
            self.clear_metadata_entries()
            self.metadata_groupBox.setEnabled(False)
            self.files_listWidget.clear()

    def remove_listWidget(self, idx):
        """Removes file with the given index from the list widget."""

        with self.disabled_selection_changed_signals:
            # Remove the file from the list widget.
            for item in items(self.files_listWidget):
                if item.data(self.OFFSET_IDX) == idx:
                    row = self.files_listWidget.row(item)
                    self.files_listWidget.takeItem(row)
                    break

    def restore_selection(self):
        """Restores the previous filesystem tree view selection in the event
        that the directory was not changed but something was clicked."""

        previous = self.filesystem_treeView.previously_selected
        if previous is not None:
            self.filesystem_treeView.setCurrentIndex(previous)
            self.filesystem_treeView.currently_selected = previous
            self.filesystem_treeView.previously_selected = None

    def populate_metadata_entries(self, author, date_time, city, country, title, description, tags, edit_single_file=False):
        """Populate the metadata entries with the given information."""

        # We do not want the metadata entry edits here to cause any side effects.
        with self.disabled_edit_signals:
            # If a metadata entry is None, we set the corresponding elements disabled.
            edit_multiple = not edit_single_file

            # We handle date time separately and others with a common code.
            entries = {
                "author":      (author, self.metadata_author.setText, self.metadata_author.clear, self.metadata_author_checkBox.setChecked),
                "city":        (city, self.metadata_city.setEditText, self.metadata_city.clear, self.metadata_city_checkBox.setChecked),
                "country":     (country, self.metadata_country.setEditText, self.metadata_country.clear, self.metadata_country_checkBox.setChecked),
                "title":       (title, self.metadata_title.setText, self.metadata_title.clear, self.metadata_title_checkBox.setChecked),
                "description": (description, self.metadata_description.setText, self.metadata_description.clear, self.metadata_description_checkBox.setChecked),
                "tags":        (",".join(tags) if tags is not None else None, self.metadata_tags.setText, self.metadata_tags.clear, self.metadata_tags_checkBox.setChecked),
            }
            for entry, (value, setValue, clear, setChecked) in entries.items():
                clear()

                # Completion for combo boxes must me set here as later it
                # would override the value. We also set it in all cases, so
                # that the check box toggling works.
                if entry == "city":
                    self.metadata_city.addItems(self.config.completion.city)
                if entry == "country":
                    self.metadata_country.addItems(self.config.completion.country)

                if value is None and edit_multiple:
                    setValue(None)
                    setChecked(False)
                else:
                    setValue(value)
                    setChecked(True)

            # Date time.
            if date_time is None:
                self.metadata_date.setDateTime(self.default_date_time)
                self.metadata_utc.setValue(0)
                self.metadata_date_checkBox.setChecked(False)
            else:
                dt = datetime_to_qdatetime(date_time)
                offset = dt.offsetFromUtc() / 3600
                if round(offset, self.ACCURACY) != offset:
                    raise ValueError(f"UTC offset cannot be represented with a precision of {self.ACCURACY} digits.")
                self.metadata_date.setTimeZone(dt.timeZone())
                self.metadata_date.setDateTime(dt)
                self.metadata_utc.setValue(offset)
                self.metadata_date_checkBox.setChecked(True)

    def clear_metadata_entries(self):
        """Clears the metadata entries."""

        # We do not want the metadata entry edits here to cause any side effects.
        with self.disabled_edit_signals:
            self.metadata_author.clear()
            self.metadata_date.setDateTime(self.default_date_time)
            self.metadata_utc.clear()
            self.metadata_city.clear()
            self.metadata_city.clearEditText()
            self.metadata_country.clear()
            self.metadata_country.clearEditText()
            self.metadata_title.clear()
            self.metadata_description.clear()
            self.metadata_tags.clear()

    def load_thumbnails(self, items):
        """Set the thumbnails according to the given list widget items."""

        self.clear_thumbnails()

        # Sort the items so that the thumbnails are set in top to bottom order
        # and not in the order the selection was created.
        sorted_items = sorted(items, key=lambda x: (x.data(self.OFFSET_IDX), x))

        # Figure out which thumbnails have not been loaded into memory.
        loaded = []
        not_loaded = []
        for n, item in enumerate(sorted_items):
            if item.data(self.OFFSET_THUMBNAIL) is None:
                not_loaded.append( (n, item.data(self.OFFSET_IDX), item.data(self.OFFSET_PATH)) )
            else:
                loaded.append( (n, item.data(self.OFFSET_IDX), item.data(self.OFFSET_THUMBNAIL)) )

        # Set up a thread to load the unloaded thumbnails.
        self.setup_thumbnail_loading(not_loaded)

        # Load the already loaded thumbnails.
        for grid_idx, list_idx, thumbnail in loaded:
            self.display_thumbnail(grid_idx, list_idx, thumbnail)

        enabled = len(sorted_items) > 0
        self.image_container_scrollArea.setEnabled(enabled)

    def clear_thumbnails(self):
        """Clear the thumbnails."""

        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        self.image_container_scrollArea.setEnabled(False)

    def rename_files(self, data):
        """Renames the files based on the given data."""

        for idx, new_file_name in data:
            item = self.files_listWidget.item(idx)
            current_path = item.data(self.OFFSET_PATH)
            current_relative_path = item.data(self.OFFSET_RELATIVE_PATH)

            new_path = os.path.join(os.path.dirname(current_path), new_file_name)
            new_relative_path = os.path.join(os.path.dirname(current_relative_path), new_file_name)

            item.setData(self.OFFSET_PATH, new_path)
            item.setData(self.OFFSET_RELATIVE_PATH, new_relative_path)
            item.setText(os.path.basename(new_file_name))

    def get_selected_tags(self):
        return [x.lower() for x in self.metadata_tags.text().split(",") if len(x) > 0]

    def set_selected_tags(self, tags):
        text = ",".join(tags)
        self.metadata_tags.setText(text)

    def open_tag_adder(self):
        """Open the tag adder dialog."""

        tags = self.get_selected_tags()
        dialog = TagAdder(self)
        dialog.set_selected_tags(tags)
        return_status = dialog.exec()
        match return_status:
            case 0:
                pass
            case 1:
                tags = dialog.get_selected_tags()
                self.set_selected_tags(tags)
            case _:
                raise ValueError(f"Unknown return status {return_status}.")

    def adjust_selected_time(self, hours, minutes, seconds):
        """Adjusts the time of the selected files by adding the given hours,
        minutes, and seconds."""

        add_seconds = hours*3600 + minutes*60 + seconds
        # Adjust the metadata entry only if one file is selected.
        if len(self.files_listWidget.selectedItems()) == 1:
            dt = self.metadata_date.dateTime()
            new_dt = dt.addSecs(add_seconds)
            self.metadata_date.setDateTime(new_dt)

        # Signal the controller to adjust for all selected files.
        self.context.request_adjust_time.emit(add_seconds)

    def adjust_utc_offset(self, utc_offset):
        """Adjusts the UTC offset of the selected files by adding the given
        hourly offset."""

        # Adjust the metadata entry only if one file is selected.
        if len(self.files_listWidget.selectedItems()) == 1:
            old = float(self.metadata_utc.text().split(" ")[0])
            # Make sure that the new offset is between -12 and 12.
            new = (old + 12 + utc_offset) % 25 - 12

            self.metadata_utc.setValue(new)

        # Signal the controller to adjust for all selected files.
        self.context.request_adjust_utc_offset.emit(utc_offset)

    def open_time_adjuster(self):
        """Open the time adjuster dialog."""

        dialog = TimeAdjuster(self)
        return_status = dialog.exec()
        match return_status:
            case 0:
                pass
            case 1:
                hours = int(dialog.hour_spinBox.text())
                minutes = int(dialog.minute_spinBox.text())
                seconds = int(dialog.second_spinBox.text())
                utc_offset = float(dialog.utc_spinBox.text())
                self.adjust_selected_time(hours, minutes, seconds)
                self.adjust_utc_offset(utc_offset)

                # We signal that all selected entries have been edited.
                self.on_event_edit()
            case _:
                raise ValueError(f"Unknown return status {return_status}.")

