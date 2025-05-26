from PySide6.QtWidgets import QDialog

from ui.ui_time_adjuster import Ui_TimeAdjuster

class TimeAdjuster(QDialog,Ui_TimeAdjuster):

    def __init__(self, parent=None):
        QDialog.__init__(self, parent)
        self.setupUi(self)

        self.setWindowTitle("Adjust time")
        self.setModal(True) # Block input to other windows.

        self.hour_spinBox.setRange(-23, 23)
        self.minute_spinBox.setRange(-59, 59)
        self.second_spinBox.setRange(-59, 59)
        self.utc_spinBox.setRange(-12, 12)

        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

