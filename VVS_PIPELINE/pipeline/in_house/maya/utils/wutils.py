# -*-coding:utf-8-*-
import sys
import maya.OpenMayaUI as omui
from Qt import QtWidgets, QtCore, QtGui
from Qt import QtCompat


def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    if sys.version_info.major >= 3:
        return QtCompat.wrapInstance(int(main_window_ptr), QtWidgets.QWidget)
    else:
        return QtCompat.wrapInstance(long(main_window_ptr), QtWidgets.QWidget)

def set_font(widget):
    font = QtGui.QFont()
    font.setFamily(u"微软雅黑")
    # font.setFamily('Courier')
    font.setPointSize(9)
    widget.setFont(font)
    return font
