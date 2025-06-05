from PySide6.QtCore import Qt, QSize, QTimer
from PySide6.QtGui import QGuiApplication, QTransform
from PySide6.QtWidgets import QDialog, QLabel, QVBoxLayout

from util import load_photo

class ImageDialog(QDialog):

    def __init__(self, path, rotation_angle):
        super().__init__()
        self.rotation_angle = rotation_angle
        self.wait = False 
        self.is_full_screen = False
        self.old_size = None

        self.setWindowTitle("Image Viewer")
        # Set height to half of screen estate.
        height = QGuiApplication.primaryScreen().availableGeometry().height()
        self.resize(int(height//2*1.5), height//2)

        self.pixmap = load_photo(path)
        transform = QTransform()
        transform.rotate(self.rotation_angle)
        self.pixmap = self.pixmap.transformed(transform)

        layout = QVBoxLayout(self)
        self.image_label = QLabel(self)
        self.image_label.setAlignment(Qt.AlignCenter)

        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        layout.addWidget(self.image_label)

        #button = QDialogButtonBox(QDialogButtonBox.Close)
        #button.rejected.connect(self.accept)
        #layout.addWidget(button)

        self.update_image(self.size().width(), self.size().height())

    def resizeEvent(self, event):
        # We need to wait on a timer to not cause repeated resize events.
        if not self.wait:
            self.wait = True
            QTimer.singleShot(100, lambda: setattr(self, "wait", False))
            self.update_image(self.size().width(), self.size().height())
        super().resizeEvent(event)

    def keyPressEvent(self, event):
        # Go to full screen if F is pressed.
        if event.key() == Qt.Key_F:
            if self.is_full_screen:
                self.update_image(self.old_size.width(), self.old_size.height())
                self.showNormal()
                self.old_size = None
            else:
                self.old_size = self.size()
                self.showFullScreen()
            self.is_full_screen = not self.is_full_screen

        super().keyPressEvent(event)

    def update_image(self, width, height):
        # Scale the pixmap to fit the available space.
        scaled_pixmap = self.pixmap.scaled(QSize(width, height), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.image_label.setPixmap(scaled_pixmap)

