# -*-coding:utf-8-*-
import json
import os
import pymel.core as pm
from Qt import QtWidgets, QtCore, QtGui
from utils import strutils, wutils

from . import widget


class AppDialog(widget.Ui_Dialog, QtWidgets.QDialog):
    VERSION = "1.0.0"
    TITLE = "Import  Retime{}".format(VERSION)

    def __init__(self, parent=wutils.maya_main_window()):
        self.close_existing_window()
        super(AppDialog, self).__init__(parent)
        self.setupUi(self)
        self.setWindowTitle(self.TITLE)
        # self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)
        self.setWindowFlag(QtCore.Qt.WindowContextHelpButtonHint, False)
        self.create_connect()
        wutils.set_font(self)
    def close_existing_window(self, *args):
        for qt in QtWidgets.QApplication.topLevelWidgets():
            try:
                if qt.__class__.__name__ == self.__class__.__name__:
                    qt.close()
            except:
                pass

    def create_connect(self):
        self.pushButtonImport.clicked.connect(self.import_retime_slot)

    def import_retime_slot(self):

        txt_file, file_type = QtWidgets.QFileDialog.getOpenFileName(wutils.maya_main_window(),
                                                                    'retime txt%s Txt [ txt ]',
                                                                    os.getcwd(),
                                                                    'Txt Files (*.txt)')
        if not txt_file:
            return

        pm.mel.eval('sceneTimeWarp "add";')

        with open(txt_file) as f:

            for line in f:
                frame, speed = line.rstrip('\n').split(' ')
                pm.setKeyframe('timewarp', time=float(frame), value=float(speed))
                print(frame, speed)

        self.close()

def main():
    retime_app = AppDialog()
    retime_app.show()