# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file ''
##
## Created by: Qt User Interface Compiler version 6.9.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QAbstractButton, QApplication, QDialog, QDialogButtonBox,
    QDoubleSpinBox, QHBoxLayout, QLabel, QSizePolicy,
    QSpinBox, QVBoxLayout, QWidget)

class Ui_TimeAdjuster(object):
    def setupUi(self, TimeAdjuster):
        if not TimeAdjuster.objectName():
            TimeAdjuster.setObjectName(u"TimeAdjuster")
        TimeAdjuster.resize(389, 90)
        self.verticalLayoutWidget = QWidget(TimeAdjuster)
        self.verticalLayoutWidget.setObjectName(u"verticalLayoutWidget")
        self.verticalLayoutWidget.setGeometry(QRect(10, 10, 371, 71))
        self.verticalLayout = QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.label = QLabel(self.verticalLayoutWidget)
        self.label.setObjectName(u"label")

        self.horizontalLayout.addWidget(self.label)

        self.hour_spinBox = QSpinBox(self.verticalLayoutWidget)
        self.hour_spinBox.setObjectName(u"hour_spinBox")

        self.horizontalLayout.addWidget(self.hour_spinBox)

        self.label_2 = QLabel(self.verticalLayoutWidget)
        self.label_2.setObjectName(u"label_2")

        self.horizontalLayout.addWidget(self.label_2)

        self.minute_spinBox = QSpinBox(self.verticalLayoutWidget)
        self.minute_spinBox.setObjectName(u"minute_spinBox")

        self.horizontalLayout.addWidget(self.minute_spinBox)

        self.label_3 = QLabel(self.verticalLayoutWidget)
        self.label_3.setObjectName(u"label_3")

        self.horizontalLayout.addWidget(self.label_3)

        self.second_spinBox = QSpinBox(self.verticalLayoutWidget)
        self.second_spinBox.setObjectName(u"second_spinBox")

        self.horizontalLayout.addWidget(self.second_spinBox)

        self.label_4 = QLabel(self.verticalLayoutWidget)
        self.label_4.setObjectName(u"label_4")

        self.horizontalLayout.addWidget(self.label_4)

        self.utc_spinBox = QDoubleSpinBox(self.verticalLayoutWidget)
        self.utc_spinBox.setObjectName(u"utc_spinBox")

        self.horizontalLayout.addWidget(self.utc_spinBox)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.buttonBox = QDialogButtonBox(self.verticalLayoutWidget)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Cancel|QDialogButtonBox.StandardButton.Ok)

        self.verticalLayout.addWidget(self.buttonBox)


        self.retranslateUi(TimeAdjuster)
        self.buttonBox.accepted.connect(TimeAdjuster.accept)
        self.buttonBox.rejected.connect(TimeAdjuster.reject)

        QMetaObject.connectSlotsByName(TimeAdjuster)
    # setupUi

    def retranslateUi(self, TimeAdjuster):
        TimeAdjuster.setWindowTitle(QCoreApplication.translate("TimeAdjuster", u"Dialog", None))
        self.label.setText(QCoreApplication.translate("TimeAdjuster", u"Hours", None))
        self.label_2.setText(QCoreApplication.translate("TimeAdjuster", u"Minutes", None))
        self.label_3.setText(QCoreApplication.translate("TimeAdjuster", u"Seconds", None))
        self.label_4.setText(QCoreApplication.translate("TimeAdjuster", u"UTC", None))
    # retranslateUi

