import os, sys
import maya.cmds as cmds

import glob
import pymel.core as pm
from Qt import QtWidgets, QtCore, QtGui

import maya.OpenMayaUI as omui
from Qt import QtCompat
from common import fileseq



class SequenceIdentifier:
    def __init__(self, filepath):
        self.filepath = filepath
        self.name_pattern = re.compile(r"^(.*?)(\d+)(\..+)$")
        self.start_frame = None
        self.end_frame = None
        self.padding = None
        self.format = None
        self.frame_range = []
        if self.filepath:
            self._analyze_sequence()

    def _analyze_sequence(self):

        dirname, basename = os.path.split(self.filepath)
        match = self.name_pattern.match(basename)
        if not match:
            raise ValueError("The file name format does not match a recognized sequence pattern.")

        name, frame_str, ext = match.groups()
        frame_len = len(frame_str)
        prefix = name
        suffix = ext
        self.format = format_path_join(dirname, "{}{}{}".format(prefix, '#' * frame_len, suffix))

        files = os.listdir(dirname)
        sequence_files = []
        for file in files:
            file_match = self.name_pattern.match(file)
            if file_match:
                file_name, file_frame_str, file_ext = file_match.groups()
                if file_name == prefix and file_ext == suffix and len(file_frame_str) == frame_len:
                    sequence_files.append(int(file_frame_str))

        if not sequence_files:
            raise ValueError("No matching sequence files found.")

        sequence_files.sort()
        self.start_frame = sequence_files[0]
        self.end_frame = sequence_files[-1]
        self.padding = frame_len
        self.frame_range = sequence_files

    def get_start_frame(self):
        return self.start_frame

    def get_end_frame(self):
        return self.end_frame

    def get_frame_range(self):
        return self.frame_range

    def get_padding_num(self):
        return self.padding

    def get_format(self):
        return self.format





def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    if sys.version_info.major >= 3:
        return QtCompat.wrapInstance(int(main_window_ptr), QtWidgets.QWidget)
    else:
        return QtCompat.wrapInstance(long(main_window_ptr), QtWidgets.QWidget)


def abc_2_maya():

    dialog = QtWidgets.QFileDialog(maya_main_window())
    dialog.setWindowTitle("选择多个ABC文件夹")
    dialog.setFileMode(QtWidgets.QFileDialog.Directory)
    dialog.setOption(QtWidgets.QFileDialog.DontUseNativeDialog, True)
    dialog.setOption(QtWidgets.QFileDialog.ShowDirsOnly, True)
    dialog.setFilter(QtCore.QDir.Dirs | QtCore.QDir.NoDotAndDotDot)

    list_view = dialog.findChild(QtWidgets.QListView)
    if list_view:
        list_view.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)

    tree_view = dialog.findChild(QtWidgets.QTreeView)
    if tree_view:
        tree_view.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)

    dialog.setAcceptMode(QtWidgets.QFileDialog.AcceptOpen)

    button_box = dialog.findChild(QtWidgets.QDialogButtonBox)

    if button_box:
        for button in button_box.buttons():
            button_box.removeButton(button)

        choose_button = QtWidgets.QPushButton("Import")
        choose_button.clicked.connect(dialog.accept)
        button_box.addButton(choose_button, QtWidgets.QDialogButtonBox.AcceptRole)

        cancel_button =QtWidgets.QPushButton("Close")
        cancel_button.clicked.connect(dialog.reject)
        button_box.addButton(cancel_button, QtWidgets.QDialogButtonBox.RejectRole)

    dialog.setDefaultSuffix("")
    dialog.setOption(QtWidgets.QFileDialog.DontConfirmOverwrite, True)

    def on_item_double_clicked(index):
        if dialog.isDirectory(index):
            dialog.setDirectory(dialog.selectedFiles()[0])

    if list_view:
        list_view.doubleClicked.connect(on_item_double_clicked)

    if tree_view:
        tree_view.doubleClicked.connect(on_item_double_clicked)

    if dialog.exec_():
        folders = dialog.selectedFiles()
        print(folders)
        if not folders:
            return
        for folder in folders:
            abc = glob.glob(os.path.join(folder, '*.abc'))
            first_frame_abc = abc[0]
            node_name = folder.split('\\')[-1].split('/')[-1]
            node_shape = pm.createNode('aiStandIn', name=node_name + '_aiStandInShape')
            node_shape.getParent().rename(node_name + '#')
            node_shape.attr('dso').set(first_frame_abc)
            node_shape.attr('useFrameExtension').set(1)



def import_abc():
    abc_2_maya()
