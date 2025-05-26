from PySide6.QtCore import QObject, Signal

class Context(QObject):
    """Context for managing signals between states."""

    # Signaling between the application and the controller.
    update_files = Signal(str, list)
    files_not_updated = Signal()
    update_metadata = Signal(object, object, object, object, object, object, object, bool)
    file_deleted = Signal(int)
    ask_discard_changes = Signal()
    discard_edits = Signal()
    rename_files = Signal(list)
    answer_received = Signal(bool)
    request_directory_change = Signal(str, bool)
    request_selected_changed = Signal(list)
    request_rename = Signal(list)
    request_delete = Signal(list)
    request_undelete = Signal(list)
    request_rotation = Signal(list)
    request_save = Signal(bool)
    request_adjust_time = Signal(int)
    request_adjust_utc_offset = Signal(float)
    indicate_progress = Signal(int)

    # State machine state change signaling.
    enter_initial = Signal()
    edit_zero_files = Signal()
    edit_one_file = Signal()
    edit_many_files = Signal()
    metadata_entry_changed = Signal()
    event_edit = Signal(list)
    saved_edits = Signal()

