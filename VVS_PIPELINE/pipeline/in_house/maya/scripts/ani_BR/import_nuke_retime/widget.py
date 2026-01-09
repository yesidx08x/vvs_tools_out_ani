# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'widget.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from Qt.QtCore import *
from Qt.QtGui import *
from Qt.QtWidgets import *


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName(u"Dialog")
        Dialog.resize(531, 46)
        self.verticalLayout = QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.label = QLabel(Dialog)
        self.label.setObjectName(u"label")

        self.horizontalLayout.addWidget(self.label)

        self.lineEditPath = QLineEdit(Dialog)
        self.lineEditPath.setObjectName(u"lineEditPath")

        self.horizontalLayout.addWidget(self.lineEditPath)

        self.pushButtonImport = QPushButton(Dialog)
        self.pushButtonImport.setObjectName(u"pushButtonImport")

        self.horizontalLayout.addWidget(self.pushButtonImport)


        self.verticalLayout.addLayout(self.horizontalLayout)


        self.retranslateUi(Dialog)

        QMetaObject.connectSlotsByName(Dialog)
    # setupUi

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", u"Import Retime", None))
        self.label.setText(QCoreApplication.translate("Dialog", u"\u6587\u4ef6\u8def\u5f84:", None))
        self.pushButtonImport.setText(QCoreApplication.translate("Dialog", u"\u5bfc\u5165Retime", None))
    # retranslateUi

