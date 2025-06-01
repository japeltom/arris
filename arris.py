#!/usr/bin/python3
# -*- coding: utf-8 -*-

import copy, datetime, os, shutil, sys

from PySide6.QtCore import Qt
from PySide6.QtGui import QTransform
from PySide6.QtWidgets import QApplication, QMainWindow, QMessageBox

from ui.image_dialog import ImageDialog
from ui.base import Base_MainWindow
from ui.ui_gui import Ui_MainWindow 

from config import read_config_file
from context import Context
from controller.controller import Controller
from util import items

class Arris(QMainWindow,Ui_MainWindow,Base_MainWindow):
    """The main window of the application."""

    def __init__(self, config, context, default_path=None):
        super().__init__()
        Base_MainWindow.__init__(self)
        self.setupUi(self)

        self.config = config
        self.context = context

        self.setWindowTitle("Arris")

        self._setup_widgets(default_path=default_path)
        self._setup_signals()

        # For clearing the datetime entry.
        self.default_date_time = copy.copy(self.metadata_date.dateTime())

        # Check if needed command line utilities exist and inform the user if
        # they do not.
        for cli_tool in ["exiv2", "jpegtran"]:
            exists = shutil.which(cli_tool) is not None
            if not exists:
                msg_box = QMessageBox(self)
                msg_box.setWindowTitle(f"Missing {cli_tool}")
                msg_box.setText(f"The required command line tool {cli_tool} is not installed on your system or it is not on the path.")
                msg_box.setIcon(QMessageBox.Critical)
                msg_box.setStandardButtons(QMessageBox.Abort)

                msg_box.exec()
                sys.exit(1)

    def enter_edited(self):
        """Handles the event that the edited state changes to 'edited'."""

        # Enable the save button.
        self.actionSave.setEnabled(True)

    def enter_not_edited(self):
        """Handles the event that the edited state changes to 'not_edited'."""

        # Disable the save button.
        self.actionSave.setEnabled(False)

        for item in items(self.files_listWidget):
            # Disable bolding on edited files.
            font = item.font()
            font.setBold(False)
            item.setFont(font)

            # Disable rotation.
            item.setData(self.OFFSET_ROTATE, 0)

    def enter_initial(self):
        """Handles the event that the action state changes to 'initial'."""

        self.clear_thumbnails()
        self.clear_metadata_entries()
        self.metadata_groupBox.setEnabled(False)
        self.depopulate_listWidget()

    def enter_edit_zero_files(self):
        """Handles the event that the action state changes to
        'edit_zero_files'."""

        self.clear_thumbnails()
        self.clear_metadata_entries()
        self.metadata_groupBox.setEnabled(False)

    def enter_edit_one_file(self):
        """Handles the event that the action state changes to
        'edit_one_file'."""

        self.signals_metadata(connect=True)
        self.metadata_groupBox.setEnabled(True)

    def enter_edit_many_files(self):
        """Handles the event that the action state changes to
        'edit_many_files'."""

        self.signals_metadata(connect=True)
        self.metadata_groupBox.setEnabled(True)

    def on_directory_clicked(self, index):
        """Handles the event that a directory was clicked in the filesystem
        tree view.

        Args:
        index (QModelIndex): The index of the clicked element.
        """

        # Save previously selected index for restoration (if exists).
        if not hasattr(self.filesystem_treeView, "currently_selected"):
            self.filesystem_treeView.currently_selected = None
        self.filesystem_treeView.previously_selected = self.filesystem_treeView.currently_selected
        self.filesystem_treeView.currently_selected = index

        path = self.model.filePath(index)
        recursive = self.recursive_load_checkBox.isChecked()
        self.context.request_directory_change.emit(path, recursive)

    def on_selection_changed(self):
        """Handles the event that the selection in the list widget changes."""

        selected, files_idx = self.get_selected_idx()

        # Set up the progress bar to display metadata loading progress (not
        # thumbnails).
        self.setup_progress_bar(len(files_idx))

        # Request selection change (will eventually call
        # self.populate_metadata).
        self.context.request_selected_changed.emit(files_idx)

        # Load thumbnails.
        self.load_thumbnails(selected)

    def on_event_edit(self):
        """Handles the event that files are edited."""

        selected, files_idx = self.get_selected_idx()

        # We bold the selected entries in the list widget.
        for item in selected:
            font = item.font()
            font.setBold(True)
            item.setFont(font)

        # We signal that all selected entries have been edited.
        self.context.event_edit.emit(files_idx)

    def on_thumbnail_clicked(self, event, path, rotation_angle=0):
        """Handle the event that a thumbnail is clicked."""

        # Display the image viewer dialog.
        dialog = ImageDialog(path, rotation_angle)
        dialog.exec()

    def ask_discard_changes(self):
        """Asks the user to discard edited metadata entries or cancel."""

        discard = self.ask_user_discard(
            title="Directory Change with Unsaved Edits",
            text="Media metadata has been edited but not saved. To change directory, these changes must be discarded. Do you want to proceed?"
        )

        self.context.answer_received.emit(discard)

    def on_rename(self):
        """Handles the event that the user wants to rename the selected
        images."""

        # We simply pass the selected images to the controller as we cannot
        # directly access the rename information.
        _, files_idx = self.get_selected_idx()
        self.context.request_rename.emit(files_idx)

        # We signal that all selected entries have been renamed.
        self.on_event_edit()

    def on_delete(self):
        """Handles the event that the user wants to delete the selected
        images."""

        selected, files_idx = self.get_selected_idx()
        self.context.request_delete.emit(files_idx)

        # Make deleted items unselectable and greyed out.
        for item in selected:
            item.setFlags(item.flags() & ~Qt.ItemIsSelectable & ~Qt.ItemIsEnabled)

        # Request selection change to empty.
        self.context.request_selected_changed.emit([])

        # Enable the undelete button.
        self.undelete_button.setEnabled(True)

        # We signal that all selected entries have been deleted.
        self.on_event_edit()

    def on_undelete(self):
        """Handles the event that the user wants to undelete the deleted
        images."""

        self.undelete_button.setEnabled(False)

        def is_enabled(item):
            return item.flags() & Qt.ItemIsEnabled == Qt.ItemIsEnabled

        # Enable the deleted list items again and collect the indices of
        # deleted files.
        files_idx = []
        for item in items(self.files_listWidget):
            if not is_enabled(item):
                files_idx.append(item.data(self.OFFSET_IDX))
                item.setFlags(item.flags() | Qt.ItemIsSelectable | Qt.ItemIsEnabled)

        self.context.request_undelete.emit(files_idx)

    def on_rotate(self):
        """Handle the event that the user wants to rotate the selected images
        by 90 degrees."""

        # Rotate the thumbnails by 90 degrees.
        selected, files_idx = self.get_selected_idx()
        transform = QTransform()
        transform.rotate(90)
        for item in selected:
            angle = (item.data(self.OFFSET_ROTATE) + 90) % 360
            item.setData(self.OFFSET_ROTATE, angle)
            thumbnail = item.data(self.OFFSET_THUMBNAIL)
            item.setData(self.OFFSET_THUMBNAIL, thumbnail.transformed(transform))

        self.load_thumbnails(selected)

        # Signal the controller to set the rotation of the selected elements.
        self.context.request_rotation.emit(files_idx)

        # We signal that all selected entries have been rotated.
        self.on_event_edit()

    def on_save(self):
        """Handle the event that the user clicked the save button."""

        total_images = self.files_listWidget.count()
        self.setup_progress_bar(total_images)

        self.context.request_save.emit(self.optimize_checkBox.isChecked())

if __name__ == "__main__":
    if len(sys.argv) > 1:
        default_path = sys.argv[1]
        if not os.path.isdir(default_path):
            raise SystemExit(f"ERROR: The provided path '{default_path}' is not a directory.")
    else:
        default_path = None

    config_file_name = os.path.expanduser("~/.arris.cfg")
    config = read_config_file(config_file_name)

    app = QApplication(sys.argv)

    context = Context()
    window = Arris(config, context, default_path=default_path)
    controller = Controller(config, context)
    controller.app = window

    window.show()
    sys.exit(app.exec())

