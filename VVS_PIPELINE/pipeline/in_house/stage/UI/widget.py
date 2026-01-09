# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'widget.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from stage.external.Qt.QtCore import *
from stage.external.Qt.QtGui import *
from stage.external.Qt.QtWidgets import *


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1447, 806)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalLayout = QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setSizeConstraint(QLayout.SetDefaultConstraint)
        self.verticalLayoutProject = QVBoxLayout()
        self.verticalLayoutProject.setObjectName(u"verticalLayoutProject")

        self.verticalLayout.addLayout(self.verticalLayoutProject)

        self.splitter = QSplitter(self.centralwidget)
        self.splitter.setObjectName(u"splitter")
        self.splitter.setOrientation(Qt.Horizontal)
        self.splitter.setChildrenCollapsible(True)
        self.layoutWidget = QWidget(self.splitter)
        self.layoutWidget.setObjectName(u"layoutWidget")
        self.verticalLayoutProductions = QVBoxLayout(self.layoutWidget)
        self.verticalLayoutProductions.setObjectName(u"verticalLayoutProductions")
        self.verticalLayoutProductions.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayoutProductions = QHBoxLayout()
        self.horizontalLayoutProductions.setObjectName(u"horizontalLayoutProductions")

        self.verticalLayoutProductions.addLayout(self.horizontalLayoutProductions)

        self.splitter.addWidget(self.layoutWidget)
        self.layoutWidget1 = QWidget(self.splitter)
        self.layoutWidget1.setObjectName(u"layoutWidget1")
        self.verticalLayoutTasks = QVBoxLayout(self.layoutWidget1)
        self.verticalLayoutTasks.setObjectName(u"verticalLayoutTasks")
        self.verticalLayoutTasks.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayoutTasks = QHBoxLayout()
        self.horizontalLayoutTasks.setObjectName(u"horizontalLayoutTasks")

        self.verticalLayoutTasks.addLayout(self.horizontalLayoutTasks)

        self.splitter.addWidget(self.layoutWidget1)
        self.layoutWidget2 = QWidget(self.splitter)
        self.layoutWidget2.setObjectName(u"layoutWidget2")
        self.verticalLayoutCategory = QVBoxLayout(self.layoutWidget2)
        self.verticalLayoutCategory.setObjectName(u"verticalLayoutCategory")
        self.verticalLayoutCategory.setContentsMargins(0, 0, 0, 0)
        self.splitter.addWidget(self.layoutWidget2)
        self.verticalLayoutWidget = QWidget(self.splitter)
        self.verticalLayoutWidget.setObjectName(u"verticalLayoutWidget")
        self.verticalLayoutVersion = QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayoutVersion.setObjectName(u"verticalLayoutVersion")
        self.verticalLayoutVersion.setSizeConstraint(QLayout.SetDefaultConstraint)
        self.verticalLayoutVersion.setContentsMargins(0, 0, 0, 0)
        self.splitter.addWidget(self.verticalLayoutWidget)

        self.verticalLayout.addWidget(self.splitter)

        self.horizontalLayoutBottom = QHBoxLayout()
        self.horizontalLayoutBottom.setObjectName(u"horizontalLayoutBottom")

        self.verticalLayout.addLayout(self.horizontalLayoutBottom)

        self.verticalLayout.setStretch(1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 1447, 23))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
    # retranslateUi

