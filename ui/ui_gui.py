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
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient,
    QCursor, QFont, QFontDatabase, QGradient,
    QIcon, QImage, QKeySequence, QLinearGradient,
    QPainter, QPalette, QPixmap, QRadialGradient,
    QTransform)
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QDateTimeEdit,
    QDoubleSpinBox, QGridLayout, QGroupBox, QHBoxLayout,
    QHeaderView, QLabel, QLineEdit, QListWidget,
    QListWidgetItem, QMainWindow, QMenuBar, QPushButton,
    QScrollArea, QSizePolicy, QSpacerItem, QStatusBar,
    QTabWidget, QTextEdit, QToolBar, QToolButton,
    QTreeView, QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1519, 954)
        self.actionSave = QAction(MainWindow)
        self.actionSave.setObjectName(u"actionSave")
        icon = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.DocumentSave))
        self.actionSave.setIcon(icon)
        self.actionSave.setMenuRole(QAction.MenuRole.NoRole)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalLayout_2 = QVBoxLayout(self.centralwidget)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.tabWidget = QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tab = QWidget()
        self.tab.setObjectName(u"tab")
        self.gridLayout = QGridLayout(self.tab)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout_4 = QGridLayout()
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.image_container_scrollArea = QScrollArea(self.tab)
        self.image_container_scrollArea.setObjectName(u"image_container_scrollArea")
        self.image_container_scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 582, 778))
        self.image_container_scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.gridLayout_4.addWidget(self.image_container_scrollArea, 0, 4, 1, 1)

        self.files_listWidget = QListWidget(self.tab)
        self.files_listWidget.setObjectName(u"files_listWidget")

        self.gridLayout_4.addWidget(self.files_listWidget, 0, 1, 1, 1)

        self.filesystem_treeView = QTreeView(self.tab)
        self.filesystem_treeView.setObjectName(u"filesystem_treeView")

        self.gridLayout_4.addWidget(self.filesystem_treeView, 0, 0, 1, 1)

        self.metadata_groupBox = QGroupBox(self.tab)
        self.metadata_groupBox.setObjectName(u"metadata_groupBox")
        self.metadata_groupBox.setCheckable(False)
        self.gridLayout_2 = QGridLayout(self.metadata_groupBox)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.verticalLayout_3 = QVBoxLayout()
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.label = QLabel(self.metadata_groupBox)
        self.label.setObjectName(u"label")

        self.verticalLayout_3.addWidget(self.label)

        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.metadata_author = QLineEdit(self.metadata_groupBox)
        self.metadata_author.setObjectName(u"metadata_author")
        self.metadata_author.setClearButtonEnabled(False)

        self.horizontalLayout_5.addWidget(self.metadata_author)

        self.metadata_author_checkBox = QCheckBox(self.metadata_groupBox)
        self.metadata_author_checkBox.setObjectName(u"metadata_author_checkBox")
        self.metadata_author_checkBox.setChecked(True)

        self.horizontalLayout_5.addWidget(self.metadata_author_checkBox)


        self.verticalLayout_3.addLayout(self.horizontalLayout_5)

        self.label_2 = QLabel(self.metadata_groupBox)
        self.label_2.setObjectName(u"label_2")

        self.verticalLayout_3.addWidget(self.label_2)

        self.date_time_horizontalLayout = QHBoxLayout()
        self.date_time_horizontalLayout.setObjectName(u"date_time_horizontalLayout")
        self.metadata_date = QDateTimeEdit(self.metadata_groupBox)
        self.metadata_date.setObjectName(u"metadata_date")

        self.date_time_horizontalLayout.addWidget(self.metadata_date)

        self.label_7 = QLabel(self.metadata_groupBox)
        self.label_7.setObjectName(u"label_7")

        self.date_time_horizontalLayout.addWidget(self.label_7)

        self.metadata_utc = QDoubleSpinBox(self.metadata_groupBox)
        self.metadata_utc.setObjectName(u"metadata_utc")

        self.date_time_horizontalLayout.addWidget(self.metadata_utc)

        self.metadata_date_checkBox = QCheckBox(self.metadata_groupBox)
        self.metadata_date_checkBox.setObjectName(u"metadata_date_checkBox")
        self.metadata_date_checkBox.setChecked(True)

        self.date_time_horizontalLayout.addWidget(self.metadata_date_checkBox)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.date_time_horizontalLayout.addItem(self.horizontalSpacer)


        self.verticalLayout_3.addLayout(self.date_time_horizontalLayout)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.label_3 = QLabel(self.metadata_groupBox)
        self.label_3.setObjectName(u"label_3")

        self.verticalLayout.addWidget(self.label_3)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.metadata_city = QComboBox(self.metadata_groupBox)
        self.metadata_city.setObjectName(u"metadata_city")
        self.metadata_city.setEditable(True)

        self.horizontalLayout_3.addWidget(self.metadata_city)

        self.metadata_city_checkBox = QCheckBox(self.metadata_groupBox)
        self.metadata_city_checkBox.setObjectName(u"metadata_city_checkBox")
        self.metadata_city_checkBox.setChecked(True)

        self.horizontalLayout_3.addWidget(self.metadata_city_checkBox)


        self.verticalLayout.addLayout(self.horizontalLayout_3)


        self.horizontalLayout_2.addLayout(self.verticalLayout)

        self.verticalLayout_5 = QVBoxLayout()
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.label_4 = QLabel(self.metadata_groupBox)
        self.label_4.setObjectName(u"label_4")

        self.verticalLayout_5.addWidget(self.label_4)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.metadata_country = QComboBox(self.metadata_groupBox)
        self.metadata_country.setObjectName(u"metadata_country")
        self.metadata_country.setEditable(True)

        self.horizontalLayout_4.addWidget(self.metadata_country)

        self.metadata_country_checkBox = QCheckBox(self.metadata_groupBox)
        self.metadata_country_checkBox.setObjectName(u"metadata_country_checkBox")
        self.metadata_country_checkBox.setChecked(True)

        self.horizontalLayout_4.addWidget(self.metadata_country_checkBox)


        self.verticalLayout_5.addLayout(self.horizontalLayout_4)


        self.horizontalLayout_2.addLayout(self.verticalLayout_5)

        self.horizontalSpacer_3 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer_3)


        self.verticalLayout_3.addLayout(self.horizontalLayout_2)

        self.label_5 = QLabel(self.metadata_groupBox)
        self.label_5.setObjectName(u"label_5")

        self.verticalLayout_3.addWidget(self.label_5)

        self.horizontalLayout_6 = QHBoxLayout()
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.metadata_title = QLineEdit(self.metadata_groupBox)
        self.metadata_title.setObjectName(u"metadata_title")

        self.horizontalLayout_6.addWidget(self.metadata_title)

        self.metadata_title_checkBox = QCheckBox(self.metadata_groupBox)
        self.metadata_title_checkBox.setObjectName(u"metadata_title_checkBox")
        self.metadata_title_checkBox.setChecked(True)

        self.horizontalLayout_6.addWidget(self.metadata_title_checkBox)


        self.verticalLayout_3.addLayout(self.horizontalLayout_6)

        self.label_6 = QLabel(self.metadata_groupBox)
        self.label_6.setObjectName(u"label_6")

        self.verticalLayout_3.addWidget(self.label_6)

        self.horizontalLayout_7 = QHBoxLayout()
        self.horizontalLayout_7.setObjectName(u"horizontalLayout_7")
        self.metadata_description = QTextEdit(self.metadata_groupBox)
        self.metadata_description.setObjectName(u"metadata_description")

        self.horizontalLayout_7.addWidget(self.metadata_description)

        self.metadata_description_checkBox = QCheckBox(self.metadata_groupBox)
        self.metadata_description_checkBox.setObjectName(u"metadata_description_checkBox")
        self.metadata_description_checkBox.setChecked(True)

        self.horizontalLayout_7.addWidget(self.metadata_description_checkBox)


        self.verticalLayout_3.addLayout(self.horizontalLayout_7)

        self.label_8 = QLabel(self.metadata_groupBox)
        self.label_8.setObjectName(u"label_8")

        self.verticalLayout_3.addWidget(self.label_8)

        self.horizontalLayout_8 = QHBoxLayout()
        self.horizontalLayout_8.setObjectName(u"horizontalLayout_8")
        self.metadata_tags = QLineEdit(self.metadata_groupBox)
        self.metadata_tags.setObjectName(u"metadata_tags")

        self.horizontalLayout_8.addWidget(self.metadata_tags)

        self.tagadder_button = QToolButton(self.metadata_groupBox)
        self.tagadder_button.setObjectName(u"tagadder_button")

        self.horizontalLayout_8.addWidget(self.tagadder_button)

        self.metadata_tags_checkBox = QCheckBox(self.metadata_groupBox)
        self.metadata_tags_checkBox.setObjectName(u"metadata_tags_checkBox")
        self.metadata_tags_checkBox.setChecked(True)

        self.horizontalLayout_8.addWidget(self.metadata_tags_checkBox)


        self.verticalLayout_3.addLayout(self.horizontalLayout_8)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_3.addItem(self.verticalSpacer)

        self.verticalLayout_4 = QVBoxLayout()
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.horizontalLayout_9 = QHBoxLayout()
        self.horizontalLayout_9.setObjectName(u"horizontalLayout_9")
        self.rotate_button = QPushButton(self.metadata_groupBox)
        self.rotate_button.setObjectName(u"rotate_button")

        self.horizontalLayout_9.addWidget(self.rotate_button)

        self.adjust_time_button = QPushButton(self.metadata_groupBox)
        self.adjust_time_button.setObjectName(u"adjust_time_button")

        self.horizontalLayout_9.addWidget(self.adjust_time_button)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_9.addItem(self.horizontalSpacer_2)


        self.verticalLayout_4.addLayout(self.horizontalLayout_9)

        self.horizontalLayout_10 = QHBoxLayout()
        self.horizontalLayout_10.setObjectName(u"horizontalLayout_10")
        self.rename_button = QPushButton(self.metadata_groupBox)
        self.rename_button.setObjectName(u"rename_button")

        self.horizontalLayout_10.addWidget(self.rename_button)

        self.delete_button = QPushButton(self.metadata_groupBox)
        self.delete_button.setObjectName(u"delete_button")

        self.horizontalLayout_10.addWidget(self.delete_button)

        self.undelete_button = QPushButton(self.metadata_groupBox)
        self.undelete_button.setObjectName(u"undelete_button")

        self.horizontalLayout_10.addWidget(self.undelete_button)

        self.horizontalSpacer_4 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_10.addItem(self.horizontalSpacer_4)


        self.verticalLayout_4.addLayout(self.horizontalLayout_10)


        self.verticalLayout_3.addLayout(self.verticalLayout_4)


        self.gridLayout_2.addLayout(self.verticalLayout_3, 1, 2, 1, 1)


        self.gridLayout_4.addWidget(self.metadata_groupBox, 0, 3, 1, 1)

        self.recursive_load_checkBox = QCheckBox(self.tab)
        self.recursive_load_checkBox.setObjectName(u"recursive_load_checkBox")

        self.gridLayout_4.addWidget(self.recursive_load_checkBox, 1, 0, 1, 1)

        self.optimize_checkBox = QCheckBox(self.tab)
        self.optimize_checkBox.setObjectName(u"optimize_checkBox")
        self.optimize_checkBox.setChecked(True)

        self.gridLayout_4.addWidget(self.optimize_checkBox, 1, 1, 1, 1)

        self.gridLayout_4.setColumnStretch(0, 15)
        self.gridLayout_4.setColumnStretch(1, 15)
        self.gridLayout_4.setColumnStretch(3, 30)
        self.gridLayout_4.setColumnStretch(4, 40)

        self.gridLayout.addLayout(self.gridLayout_4, 1, 2, 1, 1)

        self.tabWidget.addTab(self.tab, "")
        self.tab_2 = QWidget()
        self.tab_2.setObjectName(u"tab_2")
        self.tabWidget.addTab(self.tab_2, "")

        self.verticalLayout_2.addWidget(self.tabWidget)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 1519, 22))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.toolBar = QToolBar(MainWindow)
        self.toolBar.setObjectName(u"toolBar")
        MainWindow.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.toolBar)

        self.toolBar.addAction(self.actionSave)

        self.retranslateUi(MainWindow)

        self.tabWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.actionSave.setText(QCoreApplication.translate("MainWindow", u"Save", None))
#if QT_CONFIG(tooltip)
        self.actionSave.setToolTip(QCoreApplication.translate("MainWindow", u"Save metadata", None))
#endif // QT_CONFIG(tooltip)
        self.metadata_groupBox.setTitle(QCoreApplication.translate("MainWindow", u"Media file metadata:", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"Author", None))
        self.metadata_author_checkBox.setText("")
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"Date/Time", None))
        self.label_7.setText(QCoreApplication.translate("MainWindow", u"+", None))
        self.metadata_date_checkBox.setText("")
        self.label_3.setText(QCoreApplication.translate("MainWindow", u"City", None))
        self.metadata_city_checkBox.setText("")
        self.label_4.setText(QCoreApplication.translate("MainWindow", u"Country", None))
        self.metadata_country_checkBox.setText("")
        self.label_5.setText(QCoreApplication.translate("MainWindow", u"Title", None))
        self.metadata_title_checkBox.setText("")
        self.label_6.setText(QCoreApplication.translate("MainWindow", u"Description", None))
        self.metadata_description_checkBox.setText("")
        self.label_8.setText(QCoreApplication.translate("MainWindow", u"Tags", None))
        self.tagadder_button.setText(QCoreApplication.translate("MainWindow", u"...", None))
        self.metadata_tags_checkBox.setText("")
        self.rotate_button.setText(QCoreApplication.translate("MainWindow", u"Rotate 90\u00b0", None))
        self.adjust_time_button.setText(QCoreApplication.translate("MainWindow", u"Adjust time", None))
        self.rename_button.setText(QCoreApplication.translate("MainWindow", u"Rename", None))
        self.delete_button.setText(QCoreApplication.translate("MainWindow", u"Delete", None))
        self.undelete_button.setText(QCoreApplication.translate("MainWindow", u"Undelete", None))
        self.recursive_load_checkBox.setText(QCoreApplication.translate("MainWindow", u"Recurse into subdirectories", None))
        self.optimize_checkBox.setText(QCoreApplication.translate("MainWindow", u"Optimize saved files", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), QCoreApplication.translate("MainWindow", u"Editor", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), QCoreApplication.translate("MainWindow", u"Browser", None))
        self.toolBar.setWindowTitle(QCoreApplication.translate("MainWindow", u"toolBar", None))
    # retranslateUi

