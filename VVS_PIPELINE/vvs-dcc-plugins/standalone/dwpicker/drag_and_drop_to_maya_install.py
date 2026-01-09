# -*- coding: utf-8 -*-
# This file is the installation script for Dream Wall Picker.
# author: wangruilong
# date: 20250624

import os
import shutil

try:
    from shiboken2 import wrapInstance
    from PySide2 import QtWidgets, QtCore
except ModuleNotFoundError:
    from shiboken6 import wrapInstance
    from PySide6 import QtWidgets, QtCore

from maya import cmds, mel
import maya.OpenMayaUI as omui


RELATIVE_INSTALL_COMMAND = """
import os
import sys
from maya import cmds

if not os.path.exists(r'{path}'):
    message = (
        "DreamWall Picker folder is missing!\\n"
        "Did you moved the installation folder ?\\n"
        "Please re-install.")
    cmds.confirmDialog(message=message, button=["ok"])
    raise FileNotFoundError('DreamWall Picker is gone :/')

if r'{path}' not in sys.path:
    sys.path.insert(0, r'{path}')

import dwpicker
dwpicker.show(editable=False,pickers=None,ignore_scene_pickers=True)
"""


def get_maya_window():
    if os.name == 'posix':
        return None
    ptr = omui.MQtUtil.mainWindow()
    if ptr is not None:
        return wrapInstance(int(ptr), QtWidgets.QWidget)


def list_shelves():
    shelf_layout = "ShelfLayout"
    if cmds.layout(shelf_layout, exists=True):
        shelves = cmds.layout(shelf_layout, query=True, childArray=True)
        return shelves
    else:
        return []


def get_active_shelf():
    if cmds.shelfTabLayout("ShelfLayout", exists=True):
        active_shelf = cmds.shelfTabLayout(
            "ShelfLayout", query=True, selectTab=True)
        return active_shelf
    else:
        return None


def get_user_scripts_dir():
    user_dir = cmds.internalVar(userAppDir=True)
    scripts_dir = os.path.join(
        user_dir, cmds.about(majorVersion=True), "scripts")
    return scripts_dir


class InstallOptions(QtWidgets.QDialog):
    def __init__(self):
        super(InstallOptions, self).__init__(get_maya_window())
        self.setWindowTitle('Install DreamWall Picker')
        self.mayafolder = QtWidgets.QRadioButton('Into Maya scripts folder.')
        #self.mayafolder.setChecked(True)
        self.mayafolder.setEnabled(False)
        self.relative = QtWidgets.QRadioButton('From current folder.')
        self.relative.setChecked(True)

        self.button_group = QtWidgets.QButtonGroup()
        self.button_group.addButton(self.relative, 1)
        self.button_group.addButton(self.mayafolder, 0)

        self.shelves = QtWidgets.QListWidget()
        self.add_shelves()
        self.shelf_name = QtWidgets.QLineEdit()
        self.shelf_name.setEnabled(False)
        self.shelf_name.setText('DWPicker')

        self.add_to_existing_shelf = QtWidgets.QRadioButton('Add to Shelf')
        self.add_to_existing_shelf.setChecked(True)
        self.add_to_existing_shelf.toggled.connect(self.shelves.setEnabled)
        self.create_shelf = QtWidgets.QRadioButton('Create Shelf')
        self.create_shelf.toggled.connect(self.shelf_name.setEnabled)

        self.button_group2 = QtWidgets.QButtonGroup()
        self.button_group2.addButton(self.add_to_existing_shelf, 0)
        self.button_group2.addButton(self.create_shelf, 1)

        install = QtWidgets.QPushButton('Install')
        install.released.connect(self.accept)
        cancel = QtWidgets.QPushButton('Cancel')
        cancel.released.connect(self.reject)

        group = QtWidgets.QGroupBox('Location')
        radios = QtWidgets.QVBoxLayout(group)
        radios.addWidget(self.mayafolder)
        radios.addWidget(self.relative)

        group_2 = QtWidgets.QGroupBox('Shelf')
        shelf_options = QtWidgets.QVBoxLayout(group_2)
        shelf_options.addWidget(self.add_to_existing_shelf)
        shelf_options.addWidget(self.shelves)
        shelf_options.addWidget(self.create_shelf)
        shelf_options.addWidget(self.shelf_name)

        buttons = QtWidgets.QHBoxLayout()
        buttons.addStretch()
        buttons.addWidget(install)
        buttons.addWidget(cancel)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(group)
        layout.addWidget(group_2)
        layout.addLayout(buttons)

    def add_shelves(self):
        shelves = list_shelves()
        if not shelves:
            return

        self.shelves.addItems(shelves)
        active_shelf = get_active_shelf()
        if not active_shelf and 'Custom' in shelves:
            active_shelf = 'Custom'
        elif not active_shelf:
            active_shelf = shelves[0]
        items = self.shelves.findItems(active_shelf, QtCore.Qt.MatchExactly)
        self.shelves.setCurrentItem(items[0])

    def is_relative_install(self):
        return self.relative.isChecked()

    def is_create_shelf(self):
        return self.create_shelf.isChecked()

    def get_shelf_name(self):
        if self.is_create_shelf():
            return self.shelf_name.text()
        return self.shelves.selectedItems()[0].text()


def onMayaDroppedPythonFile(*_):
    dwpicker_directory = os.path.join(os.path.dirname(__file__))
    dwpicker_directory = os.path.normpath(dwpicker_directory)
    dialog = InstallOptions()
    if not dialog.exec_():
        return

    if dialog.is_relative_install():
        command = RELATIVE_INSTALL_COMMAND.format(path=dwpicker_directory)
        icon_path = os.path.join(
            dwpicker_directory, 'dwpicker/icons/dreamwallpicker.png')
        
        command_02 = 'import load_picker\nload_picker.create_picker_loader()'
        icon_path_02 = os.path.join(
            dwpicker_directory, 'dwpicker/icons/mini-open.png')
        
        maya_app_dir = cmds.internalVar(userAppDir=True)
        modules_dir = os.path.join(maya_app_dir, 'modules').replace('\\', '/')

        # 确保modules目录存在
        os.makedirs(modules_dir, exist_ok=True)

        # 创建.mod文件路径
        mod_file_path = os.path.join(modules_dir, "dwpicker.mod")

        # 写入.mod文件内容
        mod_content = f"+ dwpicker 1.0.4 {dwpicker_directory}\nscripts: .\nDWPICKER_PROJECT_DIRECTORY = {dwpicker_directory}/pickers"

        try:
            with open(mod_file_path, 'w') as f:
                f.write(mod_content)
            
            # 显示安装结果
            result = (
                f"模块安装成功！\n\n"
                f"模块名称: dwpicker\n"
                f"模块路径: {dwpicker_directory}\n"
                f".mod文件: {mod_file_path}\n\n"
                f"重启Maya后生效"
            )
            cmds.confirmDialog(title='安装成功', message=result, button=['确定'])

        except Exception as e:
            cmds.error(f"安装失败: {str(e)}")

    else:
        destination = os.path.join(get_user_scripts_dir(), 'dwpicker')
        source = os.path.join(dwpicker_directory, 'dwpicker')
        if os.path.exists(destination):
            result = QtWidgets.QMessageBox.question(
                get_maya_window(), 'Warning',
                ('DwPicker seems already installed,'
                 '\nWould you like to replace it ?'))
            if result == QtWidgets.QMessageBox.No:
                return
            shutil.rmtree(destination)
        shutil.copytree(source, destination)
        command = "import dwpicker;dwpicker.show(editable=False,pickers=None,ignore_scene_pickers=True)"
        icon_path = os.path.join(destination, 'icons/dreamwallpicker.png')

    shelf_name = dialog.get_shelf_name()
    if dialog.is_create_shelf():
        cmds.shelfLayout(shelf_name, parent='ShelfLayout')

    # shelf = mel.eval('$gShelfTopLevel=$gShelfTopLevel')
    cmds.shelfButton(
        command=command,
        image=icon_path,
        sourceType='python',
        annotation='DreamWall Picker',
        parent=shelf_name)
    cmds.shelfTabLayout('ShelfLayout', edit=True, selectTab=shelf_name)

    cmds.shelfButton(
        command=command_02,
        image=icon_path_02,
        sourceType='python',
        annotation='Picker Loader',
        parent=shelf_name)
    cmds.shelfTabLayout('ShelfLayout', edit=True, selectTab=shelf_name)
