from pathlib import Path
import logging
import platform
try:
    from maya.app.general.mayaMixin import MayaQWidgetDockableMixin
    from maya import cmds
    from maya import mel
    import maya.OpenMaya as om
    from maya import OpenMayaUI as omui
except ImportError:
    pass
from stage.external.Qt import QtCore, QtGui, QtWidgets
from stage.external.Qt import QtCompat
from stage.apps.app_core import AppCore

from stage.apps.maya import validate,extract,ingest,extension

LOG = logging.getLogger(__name__)


class Dcc(AppCore):
    """Maya DCC class."""
    name = "Maya"
    formats = [".ma", ".mb"]
    preview_enabled = True
    custom_launcher = True
    validations = validate.classes
    extracts = extract.classes
    ingests = ingest.classes
    extensions = extension.classes
    @staticmethod
    def get_main_window():

        try:
            win = omui.MQtUtil_mainWindow()
        except AttributeError:  # Maya 2025 / Qt 6
            win = omui.MQtUtil.mainWindow()
        ptr = QtCompat.wrapInstance(int(win), QtWidgets.QMainWindow)
        return ptr
    @staticmethod
    def new_scene():
        cmds.file(new=True, force=True)

    @staticmethod
    def save_scene():
        cmds.file(save=True)

    @staticmethod
    def save_as(file_path):
        extension = Path(file_path).suffix
        file_format = "mayaAscii" if extension == ".ma" else "mayaBinary"
        cmds.file(rename=file_path)
        cmds.file(save=True, type=file_format)
        return file_path

    @staticmethod
    def save_prompt():
        cmds.SaveScene()
        return True

    @staticmethod
    def open(file_path, force=True, **_extra_arguments):
        cmds.file(file_path, open=True, force=force)

    @staticmethod
    def get_scene_file():

        untitled_file_name = mel.eval("untitledFileName()")
        path = om.MFileIO.currentFile()

        file_name = Path(path).name

        if (
                file_name.startswith(untitled_file_name)
                and cmds.file(q=1, sceneName=1) == ""
        ):
            return ""
        return path

    @staticmethod
    def is_modified():
        default_dag_nodes = [
            "persp",
            "perspShape",
            "top",
            "topShape",
            "front",
            "frontShape",
            "side",
            "sideShape",
        ]
        if cmds.ls(dag=True) == default_dag_nodes:
            return False
        return cmds.file(query=True, modified=True)