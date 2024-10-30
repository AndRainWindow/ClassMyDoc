# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'mainwvyUvE.ui'
##
## Created by: Qt User Interface Compiler version 6.8.0
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
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QLineEdit, QListView,
                               QProgressBar, QPushButton, QSizePolicy, QSpacerItem,
                               QVBoxLayout, QWidget)

class Ui_ClassForm(object):
    def setupUi(self, ClassForm):
        if not ClassForm.objectName():
            ClassForm.setObjectName(u"ClassForm")
        ClassForm.resize(594, 421)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(ClassForm.sizePolicy().hasHeightForWidth())
        ClassForm.setSizePolicy(sizePolicy)
        ClassForm.setMinimumSize(QSize(0, 50))
        ClassForm.setStyleSheet(u"")
        self.verticalLayout = QVBoxLayout(ClassForm)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(-1, -1, 20, -1)
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.file_choose_button = QPushButton(ClassForm)
        self.file_choose_button.setObjectName(u"file_choose_button")
        self.file_choose_button.setEnabled(True)
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(99)
        sizePolicy1.setHeightForWidth(self.file_choose_button.sizePolicy().hasHeightForWidth())
        self.file_choose_button.setSizePolicy(sizePolicy1)
        self.file_choose_button.setMinimumSize(QSize(0, 30))
        self.file_choose_button.setMaximumSize(QSize(16777215, 23))
        self.file_choose_button.setSizeIncrement(QSize(0, 100))
        self.file_choose_button.setStyleSheet(u"QPushButton { \n"
                                              "	font-family:\u5fae\u8f6f\u96c5\u9ed1;\n"
                                              "    font-size:14px;\n"
                                              "}")
        self.file_choose_button.setAutoDefault(False)

        self.horizontalLayout.addWidget(self.file_choose_button)

        self.file_choose_line = QLineEdit(ClassForm)
        self.file_choose_line.setObjectName(u"file_choose_line")

        self.horizontalLayout.addWidget(self.file_choose_line)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.excel_choose_button = QPushButton(ClassForm)
        self.excel_choose_button.setObjectName(u"excel_choose_button")
        self.excel_choose_button.setMinimumSize(QSize(0, 30))
        self.excel_choose_button.setStyleSheet(u"QPushButton { \n"
                                               "    font-family:\u5fae\u8f6f\u96c5\u9ed1;\n"
                                               "    font-size:14px;\n"
                                               "}")

        self.horizontalLayout_2.addWidget(self.excel_choose_button)

        self.excel_choose_line = QLineEdit(ClassForm)
        self.excel_choose_line.setObjectName(u"excel_choose_line")

        self.horizontalLayout_2.addWidget(self.excel_choose_line)


        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.verticalLayout_4 = QVBoxLayout()
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_4.addItem(self.verticalSpacer)

        self.start_button = QPushButton(ClassForm)
        self.start_button.setObjectName(u"start_button")
        self.start_button.setMinimumSize(QSize(0, 30))
        self.start_button.setStyleSheet(u"QPushButton { \n"
                                        "    font-family:\u5fae\u8f6f\u96c5\u9ed1;\n"
                                        "    font-size:14px;\n"
                                        "}")

        self.verticalLayout_4.addWidget(self.start_button)

        self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_4.addItem(self.verticalSpacer_2)


        self.horizontalLayout_3.addLayout(self.verticalLayout_4)

        self.error_listView = QListView(ClassForm)
        self.error_listView.setObjectName(u"error_listView")

        self.horizontalLayout_3.addWidget(self.error_listView)


        self.verticalLayout.addLayout(self.horizontalLayout_3)

        self.progressBar = QProgressBar(ClassForm)
        self.progressBar.setObjectName(u"progressBar")
        self.progressBar.setValue(0)

        self.verticalLayout.addWidget(self.progressBar)

        self.verticalLayout.setStretch(1, 1)
        self.verticalLayout.setStretch(2, 4)

        self.retranslateUi(ClassForm)

        QMetaObject.connectSlotsByName(ClassForm)
    # setupUi

    def retranslateUi(self, ClassForm):
        ClassForm.setWindowTitle(QCoreApplication.translate("ClassForm", u"\u5206\u4ef6\u5c0f\u7a0b\u5e8f", None))
        self.file_choose_button.setText(QCoreApplication.translate("ClassForm", u"\u9009\u62e9\u6587\u4ef6", None))
        self.excel_choose_button.setText(QCoreApplication.translate("ClassForm", u"\u9009\u62e9\u76ee\u5f55", None))
        self.start_button.setText(QCoreApplication.translate("ClassForm", u"\u5f00\u59cb\u6267\u884c", None))
    # retranslateUi

