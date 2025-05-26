import rawpy

from PySide6.QtCore import Qt, QThread, QTimer, Signal
from PySide6.QtGui import QImage, QPixmap

from util import load_photo

class ThumbnailLoader(QThread):
    """A thread for loading thumbnails asynchronously."""

    thumbnail_loaded = Signal(int, int, QPixmap)
    
    def __init__(self, files, width):
        super().__init__()
        self.files = files
        self.width = width
        # Flag to control the thread stop.
        self._stop_requested = False

    def run(self):
        for grid_idx, list_idx, file_name in self.files:
            if self._stop_requested:
                break

            pixmap = load_photo(file_name)
            thumbnail = pixmap.scaled(self.width, self.width, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            QThread.msleep(100)
            self.thumbnail_loaded.emit(grid_idx, list_idx, thumbnail)

    def stop(self):
        """Stop the thread by setting the stop flag."""

        self._stop_requested = True
        # Block until thread has finished.
        self.wait()

