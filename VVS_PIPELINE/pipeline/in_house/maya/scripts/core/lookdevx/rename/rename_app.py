import pymel.core as pm
import ufe
import re
import maya.cmds as cmds
import maya.internal.ufeSupport.utils as ufeUtils
from Qt import QtWidgets, QtCore, QtGui
from utils import strutils, wutils

class RenameWindow(QtWidgets.QDialog):
    TITLE = "Rename LookDevX"

    def __init__(self, parent=wutils.maya_main_window()):
        self.close_existing_window()
        super(RenameWindow, self).__init__(parent)
        self.table_widget = parent
        self.setMinimumWidth(300)


        self.setWindowTitle(self.TITLE)

        self.setWindowFlag(QtCore.Qt.WindowContextHelpButtonHint, False)

        self.create_widgets()
        self.create_layout()
        self.create_connections()


    def close_existing_window(self):
        for qt in QtWidgets.QApplication.topLevelWidgets():
            try:
                if qt.__class__.__name__ == self.__class__.__name__:
                    qt.close()
            except:
                pass

    def create_widgets(self):
        self.search_lable = QtWidgets.QLabel(u'查找')
        self.search_le = QtWidgets.QLineEdit()
        self.replace_lable = QtWidgets.QLabel(u'替换')
        self.replace_le = QtWidgets.QLineEdit()
        self.search_replace_btn = QtWidgets.QPushButton(u'查找替换')

        self.prefix_lable = QtWidgets.QLabel(u'前缀')
        self.prefix_le = QtWidgets.QLineEdit()
        self.prefix_btn = QtWidgets.QPushButton(u'添加前缀')

        self.suffix_lable = QtWidgets.QLabel(u'后缀')
        self.suffix_le = QtWidgets.QLineEdit()
        self.suffix_btn = QtWidgets.QPushButton(u'添加后缀')

        self.close_btn = QtWidgets.QPushButton(u'关闭')

    def create_layout(self):
        h_layout = QtWidgets.QHBoxLayout()
        main_layout = QtWidgets.QVBoxLayout(self)
        h_layout.addWidget(self.search_lable)
        h_layout.addWidget(self.search_le)

        main_layout.addLayout(h_layout)

        h_layout = QtWidgets.QHBoxLayout()
        h_layout.addWidget(self.replace_lable)
        h_layout.addWidget(self.replace_le)

        main_layout.addLayout(h_layout)
        main_layout.addWidget(self.search_replace_btn)

        line = QtWidgets.QFrame()
        line.setObjectName(u"line")
        line.setFrameShape(QtWidgets.QFrame.HLine)
        line.setFrameShadow(QtWidgets.QFrame.Sunken)
        main_layout.addWidget(line)

        h_layout = QtWidgets.QHBoxLayout()
        h_layout.addWidget(self.prefix_lable)
        h_layout.addWidget(self.prefix_le)
        main_layout.addLayout(h_layout)
        main_layout.addWidget(self.prefix_btn)

        line = QtWidgets.QFrame()
        line.setObjectName(u"line")
        line.setFrameShape(QtWidgets.QFrame.HLine)
        line.setFrameShadow(QtWidgets.QFrame.Sunken)

        main_layout.addWidget(line)

        h_layout = QtWidgets.QHBoxLayout()
        h_layout.addWidget(self.suffix_lable)
        h_layout.addWidget(self.suffix_le)
        main_layout.addLayout(h_layout)
        main_layout.addWidget(self.suffix_btn)
        main_layout.addWidget(line)

        main_layout.addWidget(self.close_btn)

    def create_connections(self):
        self.search_replace_btn.clicked.connect(self.search_replace_slot)
        self.prefix_btn.clicked.connect(self.prefix_slot)
        self.suffix_btn.clicked.connect(self.suffix_slot)
        self.close_btn.clicked.connect(self.close_slot)

    def search_replace_slot(self):
        search_text = self.search_le.text()
        replace_text = self.replace_le.text()
        #|materialXStack1|materialXStackShape1,%document1%standard_surface1
        non_maya_selects = ufeUtils.getNonMayaSelectedItems()
        maya_selects=pm.ls(sl=1)
        for select in non_maya_selects:
            shape_list=select.split(',')
            if len(shape_list) == 2:
                shape_name=shape_list[0]
                ducument_list=shape_list[1].split('%')
                if len(ducument_list) == 2:
                    new_name = re.sub(search_text, replace_text, ducument_list[1], flags=re.I)
                else:
                    new_name = re.sub(search_text, replace_text, ducument_list[-1], flags=re.I)
                cmds.rename(select, new_name)
        for select in maya_selects:
            new_name = re.sub(search_text, replace_text, select.name(), flags=re.I)
            pm.rename(select, new_name)


    def prefix_slot(self):
        prefix_text = self.prefix_le.text()
        non_maya_selects = ufeUtils.getNonMayaSelectedItems()
        maya_selects = pm.ls(sl=1)

        for select in non_maya_selects:
            shape_list = select.split(',')
            if len(shape_list) == 2:
                shape_name = shape_list[0]
                ducument_list = shape_list[1].split('%')
                if len(ducument_list) == 2:
                    new_name = prefix_text + '_' + ducument_list[1]
                else:
                    new_name = prefix_text + '_' +  ducument_list[-1]
                cmds.rename(select, new_name)

        for select in maya_selects:
            new_name = prefix_text + '_' +  select.name()
            pm.rename(select, new_name)

    def suffix_slot(self):
        suffix_text = self.suffix_le.text()

        non_maya_selects = ufeUtils.getNonMayaSelectedItems()
        maya_selects = pm.ls(sl=1)

        for select in non_maya_selects:
            shape_list = select.split(',')
            if len(shape_list) == 2:
                shape_name = shape_list[0]
                ducument_list = shape_list[1].split('%')
                if len(ducument_list) == 2:
                    new_name =  ducument_list[1]+ '_' + suffix_text
                else:
                    new_name = ducument_list[-1]+ '_' + suffix_text
                cmds.rename(select, new_name)

        for select in maya_selects:
            new_name =  select.name()+ '_' + suffix_text
            pm.rename(select, new_name)


    def close_slot(self):
        self.close()

def main():
    app = RenameWindow()
    app.show()