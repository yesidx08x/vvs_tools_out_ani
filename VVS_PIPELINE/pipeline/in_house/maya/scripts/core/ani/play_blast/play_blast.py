import copy
import json
import os
import re
import sys
import tempfile
import time
import traceback

from functools import partial

from Qt import QtCore
from Qt import QtGui
from Qt import QtWidgets
try:
    from shiboken2 import getCppPointer
    from shiboken2 import wrapInstance
except:
    from shiboken6 import getCppPointer
    from shiboken6 import wrapInstance

import maya.cmds as cmds
import maya.mel as mel
import os
import maya.api.OpenMaya as om
import maya.OpenMayaUI as omui

from .play_blast_presets import PlayblastCustomPresets, PlayBlastCustomPresets


def module_exists(module_name):
    if sys.version_info.major == 3:
        import importlib.util
        spec = importlib.util.find_spec(module_name)
        return spec is not None
    else:
        import imp
        imp.find_module(module_name)
        return True


class PlayBlastUtils(object):
    PLUG_IN_NAME = os.path.dirname(__file__) + "/play_blast_plugin.py"

    @classmethod
    def is_plugin_loaded(cls):
        return cmds.pluginInfo(cls.PLUG_IN_NAME, q=True, loaded=True)

    @classmethod
    def load_plugin(cls):
        if not cls.is_plugin_loaded():
            try:
                cmds.loadPlugin(cls.PLUG_IN_NAME)
                cmds.loadPlugin('matrixNodes', quiet=True)
            except:
                om.MGlobal.displayError("Failed to load  Playblast plug-in: {0}".format(cls.PLUG_IN_NAME))
                return

        return True

    @classmethod
    def get_version(cls):
        return cmds.PlayBlastSlate(v=True)[0]  # pylint: disable=E1101

    @classmethod
    def get_ffmpeg_path(cls):
        return cmds.PlayBlastSlate(q=True, fp=True)[0]  # pylint: disable=E1101

    @classmethod
    def set_ffmpeg_path(cls, path):
        cmds.PlayBlastSlate(e=True, fp=path)  # pylint: disable=E1101

    @classmethod
    def is_ffmpeg_env_var_set(cls):
        return cmds.PlayBlastSlate(fev=True)[0]  # pylint: disable=E1101

    @classmethod
    def get_temp_output_dir_path(self):
        return cmds.PlayBlastSlate(q=True, tp=True)[0]  # pylint: disable=E1101

    @classmethod
    def set_temp_output_dir_path(self, path):
        cmds.PlayBlastSlate(e=True, tp=path)  # pylint: disable=E1101

    @classmethod
    def is_temp_output_env_var_set(cls):
        return cmds.PlayBlastSlate(tev=True)[0]  # pylint: disable=E1101

    @classmethod
    def get_temp_file_format(self):
        return cmds.PlayBlastSlate(q=True, tf=True)[0]

    @classmethod
    def set_temp_file_format(self, file_format):
        cmds.PlayBlastSlate(e=True, tf=file_format)

    @classmethod
    def is_temp_format_env_set(cls):
        return cmds.PlayBlastSlate(tfe=True)[0]

    @classmethod
    def get_logo_path(cls):
        return cmds.PlayBlastSlate(q=True, lp=True)[0]  # pylint: disable=E1101

    @classmethod
    def set_logo_path(cls, path):
        cmds.PlayBlastSlate(e=True, lp=path)  # pylint: disable=E1101

    @classmethod
    def is_logo_env_var_set(cls):
        return cmds.PlayBlastSlate(lev=True)[0]  # pylint: disable=E1101

    @classmethod
    def cameras_in_scene(cls, include_defaults=True, user_created_first=True):
        default_cameras = ["front", "persp", "side", "top","|front", "|persp", "|side", "|top","front1", "persp1", "side1", "top1"]

        cameras = cmds.listCameras()

        if include_defaults and user_created_first or not include_defaults:
            for name in default_cameras:
                if name in cameras:
                    try:
                        cameras.remove(name)
                    except Exception as e:
                        print(name,e)
                        

            if user_created_first:
                for name in default_cameras:
                    cameras.append(name)

        return cameras

    @classmethod
    def get_opt_var_str(cls, name):
        if cmds.optionVar(exists=name):
            return cmds.optionVar(q=name)

        return ""


class CollapsibleGrpHeader(QtWidgets.QWidget):
    clicked = QtCore.Signal()

    def __init__(self, text, parent=None):
        super(CollapsibleGrpHeader, self).__init__(parent)

        self.setAutoFillBackground(True)
        self.set_background_color(None)

        self.collapsed_pixmap = QtGui.QPixmap(":teRightArrow.png")
        self.expanded_pixmap = QtGui.QPixmap(":teDownArrow.png")

        self.icon_label = QtWidgets.QLabel()
        self.icon_label.setFixedWidth(self.collapsed_pixmap.width())
        self.icon_label.setPixmap(self.collapsed_pixmap)
        self.icon_label.setAlignment(QtCore.Qt.AlignTop)

        self.text_label = QtWidgets.QLabel()
        self.text_label.setTextFormat(QtCore.Qt.RichText)
        self.text_label.setAlignment(QtCore.Qt.AlignLeft)
        self.text_label.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents)

        self.main_layout = QtWidgets.QHBoxLayout(self)
        self.main_layout.setContentsMargins(4, 4, 4, 4)
        self.main_layout.addWidget(self.icon_label)
        self.main_layout.addWidget(self.text_label)

        self.set_text(text)
        self.set_expanded(False)

    def set_text(self, text):
        self.text_label.setText("<b>{0}</b>".format(text))

    def set_background_color(self, color):
        if not color:
            color = QtWidgets.QPushButton().palette().color(QtGui.QPalette.Button)

        palette = self.palette()
        palette.setColor(QtGui.QPalette.Window, color)
        self.setPalette(palette)

    def is_expanded(self):
        return self._expanded

    def set_expanded(self, expanded):
        self._expanded = expanded

        if (self._expanded):
            self.icon_label.setPixmap(self.expanded_pixmap)
        else:
            self.icon_label.setPixmap(self.collapsed_pixmap)

    def mouseReleaseEvent(self, event):
        self.clicked.emit()  # pylint: disable=E1101


class CollapsibleGrpWidget(QtWidgets.QWidget):
    collapsed_state_changed = QtCore.Signal()

    def __init__(self, text, parent=None):
        super(CollapsibleGrpWidget, self).__init__(parent)

        self.append_stretch_on_collapse = False
        self.stretch_appended = False

        self.header_wdg = CollapsibleGrpHeader(text)
        self.header_wdg.clicked.connect(self.on_header_clicked)  # pylint: disable=E1101

        self.body_wdg = QtWidgets.QWidget()
        self.body_wdg.setAutoFillBackground(True)

        palette = self.body_wdg.palette()
        palette.setColor(QtGui.QPalette.Window, palette.color(QtGui.QPalette.Window).lighter(110))
        self.body_wdg.setPalette(palette)

        self.body_layout = QtWidgets.QVBoxLayout(self.body_wdg)
        self.body_layout.setContentsMargins(4, 2, 4, 2)
        self.body_layout.setSpacing(3)
        self.body_layout.setAlignment(QtCore.Qt.AlignTop)

        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.addWidget(self.header_wdg)
        self.main_layout.addWidget(self.body_wdg)

        self.set_expanded(True)

    def add_widget(self, widget):
        self.body_layout.addWidget(widget)

    def add_layout(self, layout):
        self.body_layout.addLayout(layout)

    def set_expanded(self, expanded):
        self.header_wdg.set_expanded(expanded)
        self.body_wdg.setVisible(expanded)

        if self.append_stretch_on_collapse:
            if expanded:
                if self.stretch_appended:
                    self.main_layout.takeAt(self.main_layout.count() - 1)
                    self.stretch_appended = False
            elif not self.stretch_appended:
                self.main_layout.addStretch()
                self.stretch_appended = True

    def is_expanded(self):
        return self.header_wdg.is_expanded()

    def set_collapsed(self, collapsed):
        self.set_expanded(not collapsed)

    def is_collapsed(self):
        return not self.header_wdg.is_expanded()

    def set_header_background_color(self, color):
        self.header_wdg.set_background_color(color)

    def on_header_clicked(self):
        self.set_expanded(not self.header_wdg.is_expanded())

        self.collapsed_state_changed.emit()  # pylint: disable=E1101


class ColorButton(QtWidgets.QWidget):
    color_changed = QtCore.Signal()

    def __init__(self, color=(1.0, 1.0, 1.0), parent=None):
        super(ColorButton, self).__init__(parent)

        self.setObjectName("ColorButton")

        self.create_control()

        self.set_size(50, 16)
        self.set_color(color)

    def create_control(self):
        window = cmds.window()
        color_slider_name = cmds.colorSliderGrp()

        self._color_slider_obj = omui.MQtUtil.findControl(color_slider_name)
        if self._color_slider_obj:
            if sys.version_info.major >= 3:
                self._color_slider_widget = wrapInstance(int(self._color_slider_obj), QtWidgets.QWidget)
            else:
                self._color_slider_widget = wrapInstance(long(self._color_slider_obj), QtWidgets.QWidget)

            main_layout = QtWidgets.QVBoxLayout(self)
            main_layout.setObjectName("main_layout")
            main_layout.setContentsMargins(0, 0, 0, 0)
            main_layout.addWidget(self._color_slider_widget)

            self._slider_widget = self._color_slider_widget.findChild(QtWidgets.QWidget, "slider")
            if self._slider_widget:
                self._slider_widget.hide()

            self._color_widget = self._color_slider_widget.findChild(QtWidgets.QWidget, "port")

            cmds.colorSliderGrp(self.get_full_name(), e=True, changeCommand=partial(self.on_color_changed))

        cmds.deleteUI(window, window=True)

    def get_full_name(self):
        if sys.version_info.major >= 3:
            return omui.MQtUtil.fullName(int(self._color_slider_obj))
        else:
            return omui.MQtUtil.fullName(long(self._color_slider_obj))

    def set_size(self, width, height):
        self._color_slider_widget.setFixedWidth(width)
        self._color_widget.setFixedHeight(height)

    def set_color(self, color):
        cmds.colorSliderGrp(self.get_full_name(), e=True, rgbValue=(color[0], color[1], color[2]))
        self.on_color_changed()

    def get_color(self):
        return cmds.colorSliderGrp(self.get_full_name(), q=True, rgbValue=True)

    def on_color_changed(self, *args):
        self.color_changed.emit()  # pylint: disable=E1101


class LineEdit(QtWidgets.QLineEdit):
    TYPE_PLAYBLAST_OUTPUT_PATH = 0
    TYPE_PLAYBLAST_OUTPUT_FILENAME = 1
    TYPE_SHOT_MASK_LABEL = 2

    PLAYBLAST_OUTPUT_PATH_LOOKUP = [
        ("Project", "{project}"),
        ("Temp", "{temp}"),
    ]

    PLAYBLAST_OUTPUT_FILENAME_LOOKUP = [
        ("Scene Name", "{scene}"),
        ("Camera Name", "{camera}"),
        ("Timestamp", "{timestamp}"),
    ]

    SHOT_MASK_LABEL_LOOKUP = [
        ("Scene Name", "{scene}"),
        ("Frame Counter", "{counter}"),
        ("Camera Name", "{camera}"),
        ("Focal Length", "{focal_length}"),
        ("Time Code", "{time_code}"),
        ("Fps", "{fps}"),
        {"Camera Speed","{camera_speed_km}"},
        ("Logo", "{logo}"),
        ("Image", "{image=<image_path>}"),
        ("User Name", "{username}"),
        ("Date", "{date}"),
    ]

    def __init__(self, le_type, parent=None):
        super(LineEdit, self).__init__(parent)

        self.le_type = le_type

        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)

        self.customContextMenuRequested.connect(self.show_context_menu)

    def show_context_menu(self, pos):
        context_menu = QtWidgets.QMenu(self)

        action = context_menu.addAction("Insert {tag}")
        action.setEnabled(False)

        context_menu.addSeparator()

        lookup = []
        if self.le_type == LineEdit.TYPE_PLAYBLAST_OUTPUT_PATH:
            lookup = LineEdit.PLAYBLAST_OUTPUT_PATH_LOOKUP
            lookup.extend(PlayblastCustomPresets.PLAYBLAST_OUTPUT_PATH_LOOKUP)
        elif self.le_type == LineEdit.TYPE_PLAYBLAST_OUTPUT_FILENAME:
            lookup = LineEdit.PLAYBLAST_OUTPUT_FILENAME_LOOKUP
            lookup.extend(PlayblastCustomPresets.PLAYBLAST_OUTPUT_FILENAME_LOOKUP)
        elif self.le_type == LineEdit.TYPE_SHOT_MASK_LABEL:
            lookup = LineEdit.SHOT_MASK_LABEL_LOOKUP
            lookup.extend(PlayBlastCustomPresets.SHOT_MASK_LABEL_LOOKUP)

        for item in lookup:
            action = context_menu.addAction(item[0])
            action.setData(item[1])
            action.triggered.connect(self.on_context_menu_item_selected)

        context_menu.exec_(self.mapToGlobal(pos))

    def on_context_menu_item_selected(self):
        self.insert(self.sender().data())


class FormLayout(QtWidgets.QGridLayout):

    def __init__(self, parent=None):
        super(FormLayout, self).__init__(parent)

        self.setContentsMargins(0, 0, 0, 8)
        self.setColumnMinimumWidth(0, 80)
        self.setHorizontalSpacing(6)

    def addWidgetRow(self, row, label, widget):
        self.addWidget(QtWidgets.QLabel(label), row, 0, QtCore.Qt.AlignRight)
        self.addWidget(widget, row, 1)

    def addLayoutRow(self, row, label, layout):
        self.addWidget(QtWidgets.QLabel(label), row, 0, QtCore.Qt.AlignRight)
        self.addLayout(layout, row, 1)


class CameraSelectDialog(QtWidgets.QDialog):

    def __init__(self, parent):
        super(CameraSelectDialog, self).__init__(parent)

        self.setWindowTitle("Camera Select")
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)
        self.setModal(True)

        self.camera_list_label = QtWidgets.QLabel()
        self.camera_list_label.setVisible(False)

        self.camera_list_wdg = QtWidgets.QListWidget()
        self.camera_list_wdg.doubleClicked.connect(self.accept)

        self.select_btn = QtWidgets.QPushButton("Select")
        self.select_btn.clicked.connect(self.accept)

        self.cancel_btn = QtWidgets.QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.close)

        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.select_btn)
        button_layout.addWidget(self.cancel_btn)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(2, 4, 2, 2)
        main_layout.setSpacing(4)
        main_layout.addWidget(self.camera_list_label)
        main_layout.addWidget(self.camera_list_wdg)
        main_layout.addLayout(button_layout)

    def set_multi_select_enabled(self, enabled):
        if enabled:
            self.camera_list_wdg.setSelectionMode(QtWidgets.QListWidget.ExtendedSelection)
        else:
            self.camera_list_wdg.setSelectionMode(QtWidgets.QListWidget.SingleSelection)

    def set_camera_list_text(self, text):
        self.camera_list_label.setText(text)
        self.camera_list_label.setVisible(True)

    def set_select_btn_text(self, text):
        self.select_btn.setText(text)

    def refresh_list(self, selected=[], include_defaults=True, user_created_first=True, prepend=[], append=[]):
        self.camera_list_wdg.clear()

        if prepend:
            self.camera_list_wdg.addItems(prepend)

        self.camera_list_wdg.addItems(PlayBlastUtils.cameras_in_scene(include_defaults, user_created_first))

        if append:
            self.camera_list_wdg.addItems(append)

        if selected:
            for text in selected:
                items = self.camera_list_wdg.findItems(text, QtCore.Qt.MatchCaseSensitive)
                if len(items) > 0:
                    self.camera_list_wdg.setCurrentItem(items[0], QtCore.QItemSelectionModel.Select)

    def get_selected(self):
        selected = []

        items = self.camera_list_wdg.selectedItems()
        for item in items:
            selected.append(item.text())

        return selected


class WorkspaceControl(object):

    def __init__(self, name):
        self.name = name
        self.widget = None

    def create(self, label, widget, ui_script=None):

        cmds.workspaceControl(self.name, label=label)

        if ui_script:
            cmds.workspaceControl(self.name, e=True, uiScript=ui_script)

        self.add_widget_to_layout(widget)
        self.set_visible(True)

    def restore(self, widget):
        self.add_widget_to_layout(widget)

    def add_widget_to_layout(self, widget):
        if widget:
            self.widget = widget
            self.widget.setAttribute(QtCore.Qt.WA_DontCreateNativeAncestors)

            if sys.version_info.major >= 3:
                workspace_control_ptr = int(omui.MQtUtil.findControl(self.name))
                widget_ptr = int(getCppPointer(self.widget)[0])
            else:
                workspace_control_ptr = long(omui.MQtUtil.findControl(self.name))
                widget_ptr = long(getCppPointer(self.widget)[0])

            omui.MQtUtil.addWidgetToMayaLayout(widget_ptr, workspace_control_ptr)

    def exists(self):
        return cmds.workspaceControl(self.name, q=True, exists=True)

    def is_visible(self):
        return cmds.workspaceControl(self.name, q=True, visible=True)

    def set_visible(self, visible):
        if visible:
            cmds.workspaceControl(self.name, e=True, restore=True)
        else:
            cmds.workspaceControl(self.name, e=True, visible=False)

    def set_label(self, label):
        cmds.workspaceControl(self.name, e=True, label=label)

    def is_floating(self):
        return cmds.workspaceControl(self.name, q=True, floating=True)

    def is_collapsed(self):
        return cmds.workspaceControl(self.name, q=True, collapse=True)


class Playblast(QtCore.QObject):
    DEFAULT_FFMPEG_PATH = ""

    RESOLUTION_PRESETS = [
        ["Render", ()],
    ]

    FRAME_RANGE_PRESETS = [
        "Animation",
        "Playback",
        "Render",
        "Camera",
    ]

    VIDEO_ENCODER_LOOKUP = {
        "mov": ["h264"],
        "mp4": ["h264"],
        "Image": ["jpg", "png", "tif"],
    }

    H264_QUALITIES = {
        "Very High": 18,
        "High": 20,
        "Medium": 23,
        "Low": 26,
    }

    H264_PRESETS = [
        "veryslow",
        "slow",
        "medium",
        "fast",
        "faster",
        "ultrafast",
    ]

    VIEWPORT_VISIBILITY_LOOKUP = [
        ["Controllers", "controllers"],
        ["NURBS Curves", "nurbsCurves"],
        ["NURBS Surfaces", "nurbsSurfaces"],
        ["NURBS CVs", "cv"],
        ["NURBS Hulls", "hulls"],
        ["Polygons", "polymeshes"],
        ["Subdiv Surfaces", "subdivSurfaces"],
        ["Planes", "planes"],
        ["Lights", "lights"],
        ["Cameras", "cameras"],
        ["Image Planes", "imagePlane"],
        ["Joints", "joints"],
        ["IK Handles", "ikHandles"],
        ["Deformers", "deformers"],
        ["Dynamics", "dynamics"],
        ["Particle Instancers", "particleInstancers"],
        ["Fluids", "fluids"],
        ["Hair Systems", "hairSystems"],
        ["Follicles", "follicles"],
        ["nCloths", "nCloths"],
        ["nParticles", "nParticles"],
        ["nRigids", "nRigids"],
        ["Dynamic Constraints", "dynamicConstraints"],
        ["Locators", "locators"],
        ["Dimensions", "dimensions"],
        ["Pivots", "pivots"],
        ["Handles", "handles"],
        ["Texture Placements", "textures"],
        ["Strokes", "strokes"],
        ["Motion Trails", "motionTrails"],
        ["Plugin Shapes", "pluginShapes"],
        ["Clip Ghosts", "clipGhosts"],
        ["Grease Pencil", "greasePencils"],
        ["Grid", "grid"],
        ["HUD", "hud"],
        ["Hold-Outs", "hos"],
        ["Selection Highlighting", "sel"],
    ]

    VIEWPORT_VISIBILITY_PRESETS = [
        ["Viewport", []],
    ]

    DEFAULT_CAMERA = None
    DEFAULT_RESOLUTION = "Render"
    DEFAULT_FRAME_RANGE = "Playback"

    DEFAULT_CONTAINER = "mov"
    DEFAULT_ENCODER = "h264"
    DEFAULT_H264_QUALITY = "High"
    DEFAULT_H264_PRESET = "fast"
    DEFAULT_IMAGE_QUALITY = 100

    DEFAULT_VISIBILITY = "Viewport"

    DEFAULT_PADDING = 4

    DEFAULT_MAYA_LOGGING_ENABLED = False

    CAMERA_PLAYBLAST_START_ATTR = "playblastStart"
    CAMERA_PLAYBLAST_END_ATTR = "playblastEnd"

    output_logged = QtCore.Signal(str)

    def __init__(self):
        super(Playblast, self).__init__()

        self.set_maya_logging_enabled(Playblast.DEFAULT_MAYA_LOGGING_ENABLED)

        self.build_presets()

        self.set_camera(Playblast.DEFAULT_CAMERA)
        self.set_resolution(Playblast.DEFAULT_RESOLUTION)
        self.set_frame_range(Playblast.DEFAULT_FRAME_RANGE)

        self.set_encoding(Playblast.DEFAULT_CONTAINER, Playblast.DEFAULT_ENCODER)
        self.set_h264_settings(Playblast.DEFAULT_H264_QUALITY, Playblast.DEFAULT_H264_PRESET)
        self.set_image_settings(Playblast.DEFAULT_IMAGE_QUALITY)

        self.set_visibility(Playblast.DEFAULT_VISIBILITY)

        self.initialize_ffmpeg_process()

    def build_presets(self):
        self.resolution_preset_names = []
        self.resolution_presets = {}

        for preset in Playblast.RESOLUTION_PRESETS:
            self.resolution_preset_names.append(preset[0])
            self.resolution_presets[preset[0]] = preset[1]

        try:
            for preset in PlayblastCustomPresets.RESOLUTION_PRESETS:
                self.resolution_preset_names.append(preset[0])
                self.resolution_presets[preset[0]] = preset[1]
        except:
            traceback.print_exc()
            self.log_error("Failed to add custom resolution presets. See script editor for details.")

        self.viewport_visibility_preset_names = []
        self.viewport_visibility_presets = {}

        for preset in Playblast.VIEWPORT_VISIBILITY_PRESETS:
            self.viewport_visibility_preset_names.append(preset[0])
            self.viewport_visibility_presets[preset[0]] = preset[1]

        try:
            for preset in PlayblastCustomPresets.VIEWPORT_VISIBILITY_PRESETS:
                self.viewport_visibility_preset_names.append(preset[0])
                self.viewport_visibility_presets[preset[0]] = preset[1]

        except:
            traceback.print_exc()
            self.log_error("Failed to add custom viewport visibility presets. See script editor for details.")

    def set_maya_logging_enabled(self, enabled):
        self._log_to_maya = enabled

    def is_maya_logging_enabled(self):
        return self._log_to_maya

    def set_camera(self, camera):
        if camera and camera not in cmds.listCameras():
            self.log_error("Camera does not exist: {0}".format(camera))
            camera = None

        self._camera = camera

    def set_resolution(self, resolution):
        self._resolution_preset = None

        try:
            widthHeight = self.preset_to_resolution(resolution)
            self._resolution_preset = resolution
        except:
            widthHeight = resolution

        valid_resolution = True
        try:
            if not (isinstance(widthHeight[0], int) and isinstance(widthHeight[1], int)):
                valid_resolution = False
        except:
            valid_resolution = False

        if valid_resolution:
            if widthHeight[0] <= 0 or widthHeight[1] <= 0:
                self.log_error("Invalid resolution: {0}. Values must be greater than zero.".format(widthHeight))
                return
        else:
            self.log_error("Invalid resoluton: {0}. Expected one of [int, int], {1}".format(widthHeight, ", ".join(
                self.resolution_preset_names)))
            return

        self._widthHeight = (widthHeight[0], widthHeight[1])

    def get_resolution_width_height(self):
        if self._resolution_preset:
            return self.preset_to_resolution(self._resolution_preset)

        return self._widthHeight

    def preset_to_resolution(self, resolution_preset_name):
        if resolution_preset_name == "Render":
            width = cmds.getAttr("defaultResolution.width")
            height = cmds.getAttr("defaultResolution.height")
            return (width, height)
        elif resolution_preset_name in self.resolution_preset_names:
            return self.resolution_presets[resolution_preset_name]
        else:
            raise RuntimeError("Invalid resolution preset: {0}".format(resolution_preset_name))

    def set_frame_range(self, frame_range):
        resolved_frame_range = self.resolve_frame_range(frame_range)
        if not resolved_frame_range:
            return

        self._frame_range_preset = None
        if frame_range in Playblast.FRAME_RANGE_PRESETS:
            self._frame_range_preset = frame_range

        self._start_frame = resolved_frame_range[0]
        self._end_frame = resolved_frame_range[1]

    def get_start_end_frame(self):
        if self._frame_range_preset:
            return self.preset_to_frame_range(self._frame_range_preset)

        return (self._start_frame, self._end_frame)

    def resolve_frame_range(self, frame_range):
        try:
            if type(frame_range) in [list, tuple]:
                start_frame = frame_range[0]
                end_frame = frame_range[1]
            else:
                start_frame, end_frame = self.preset_to_frame_range(frame_range)

            return (start_frame, end_frame)

        except:
            presets = []
            for preset in Playblast.FRAME_RANGE_PRESETS:
                presets.append("'{0}'".format(preset))
            self.log_error(
                'Invalid frame range. Expected one of (start_frame, end_frame), {0}'.format(", ".join(presets)))

        return None

    def preset_to_frame_range(self, frame_range_preset):
        if frame_range_preset == "Render":
            start_frame = int(cmds.getAttr("defaultRenderGlobals.startFrame"))
            end_frame = int(cmds.getAttr("defaultRenderGlobals.endFrame"))
        elif frame_range_preset == "Playback":
            if mel.eval("timeControl -q -rangeVisible $gPlayBackSlider"):
                start_frame, end_frame = mel.eval("timeControl -q -rangeArray $gPlayBackSlider")
                end_frame = end_frame - 1
            else:
                start_frame = int(cmds.playbackOptions(q=True, minTime=True))
                end_frame = int(cmds.playbackOptions(q=True, maxTime=True))
        elif frame_range_preset == "Animation":
            start_frame = int(cmds.playbackOptions(q=True, animationStartTime=True))
            end_frame = int(cmds.playbackOptions(q=True, animationEndTime=True))
        elif frame_range_preset == "Camera":
            return self.preset_to_frame_range("Playback")
        else:
            raise RuntimeError("Invalid frame range preset: {0}".format(frame_range_preset))

        return (start_frame, end_frame)

    def set_visibility(self, visibility_data):
        if not visibility_data:
            visibility_data = []

        if not type(visibility_data) in [list, tuple]:
            visibility_data = self.preset_to_visibility(visibility_data)

            if visibility_data is None:
                return

        self._visibility = copy.copy(visibility_data)

    def get_visibility(self):
        if not self._visibility:
            return self.get_viewport_visibility()

        return self._visibility

    def preset_to_visibility(self, visibility_preset_name):
        if not visibility_preset_name in self.viewport_visibility_preset_names:
            self.log_error("Invaild visibility preset: {0}".format(visibility_preset_name))
            return None

        visibility_data = []

        preset_names = self.viewport_visibility_presets[visibility_preset_name]
        if preset_names:
            for lookup_item in Playblast.VIEWPORT_VISIBILITY_LOOKUP:
                visibility_data.append(lookup_item[0] in preset_names)

        return visibility_data

    def get_viewport_visibility(self):
        model_panel = self.get_viewport_panel()
        if not model_panel:
            return None

        viewport_visibility = []
        try:
            for item in Playblast.VIEWPORT_VISIBILITY_LOOKUP:
                kwargs = {item[1]: True}
                viewport_visibility.append(cmds.modelEditor(model_panel, q=True, **kwargs))
        except:
            traceback.print_exc()
            self.log_error("Failed to get active viewport visibility. See script editor for details.")
            return None

        return viewport_visibility

    def set_viewport_visibility(self, model_editor, visibility_flags):
        cmds.modelEditor(model_editor, e=True, **visibility_flags)

    def create_viewport_visibility_flags(self, visibility_data):
        visibility_flags = {}

        data_index = 0
        for item in Playblast.VIEWPORT_VISIBILITY_LOOKUP:
            visibility_flags[item[1]] = visibility_data[data_index]
            data_index += 1

        return visibility_flags

    def set_encoding(self, container_format, encoder):
        if container_format not in Playblast.VIDEO_ENCODER_LOOKUP.keys():
            self.log_error("Invalid container: {0}. Expected one of {1}".format(container_format,
                                                                                Playblast.VIDEO_ENCODER_LOOKUP.keys()))
            return

        if encoder not in Playblast.VIDEO_ENCODER_LOOKUP[container_format]:
            self.log_error("Invalid encoder: {0}. Expected one of {1}".format(encoder, Playblast.VIDEO_ENCODER_LOOKUP[
                container_format]))
            return

        self._container_format = container_format
        self._encoder = encoder

    def set_h264_settings(self, quality, preset):
        if not quality in Playblast.H264_QUALITIES.keys():
            self.log_error(
                "Invalid h264 quality: {0}. Expected one of {1}".format(quality, Playblast.H264_QUALITIES.keys()))
            return

        if not preset in Playblast.H264_PRESETS:
            self.log_error("Invalid h264 preset: {0}. Expected one of {1}".format(preset, Playblast.H264_PRESETS))
            return

        self._h264_quality = quality
        self._h264_preset = preset

    def get_h264_settings(self):
        return {
            "quality": self._h264_quality,
            "preset": self._h264_preset,
        }

    def set_image_settings(self, quality):
        if quality > 0 and quality <= 100:
            self._image_quality = quality
        else:
            self.log_error("Invalid image quality: {0}. Expected value between 1-100")

    def get_image_settings(self):
        return {
            "quality": self._image_quality,
        }
        
    def generateAllUvTilePreviews(self):
        fileNodes =cmds.ls(type="file")
        for fn in fileNodes:
            if cmds.getAttr(fn + ".uvTilingMode") != 0 and cmds.getAttr(fn + ".uvTileProxyQuality") != 0:
                cmds.ogs(regenerateUVTilePreview=fn)
                
    def execute_thumb(self, offscreen=False, overscan=True,start_frame=1000, end_frame=1000,):
        current_frame=int(cmds.currentTime(q=True))
        start_frame+=1
        end_frame+=1
        viewport_model_panel = self.get_viewport_panel()
        if not viewport_model_panel:
            self.log_error("An active viewport is not selected. Select a viewport and retry.")
            self.log_error(u'未选择活动视口。选择一个视口并重试')
            return

        # Store original camera
        orig_camera = self.get_active_camera()
        camera_override=''

        if camera_override:
            camera = camera_override
        else:
            camera = self._camera

        if not camera:
            camera = orig_camera

        if not camera in cmds.listCameras():
            self.log_error("Camera does not exist: {0}".format(camera))
            return

        output_dir_file = tempfile.mkdtemp(prefix='thumbnail_')

        widthHeight = self.get_resolution_width_height()

        options = {
            "filename": output_dir_file,
            "widthHeight": widthHeight,
            "percent": 100,
            "startTime": start_frame,
            "endTime": end_frame,
            "clearCache": True,
            "forceOverwrite": True,
            "format": "image",
            "compression": "png",
            "quality": 100,
            "framePadding": 4,
            "showOrnaments": False,
            "viewer": False,
            "offScreen": offscreen
        }

        QtCore.QCoreApplication.processEvents()

        self.set_active_camera(camera)

        orig_visibility_flags = self.create_viewport_visibility_flags(self.get_viewport_visibility())
        playblast_visibility_flags = self.create_viewport_visibility_flags(self.get_visibility())

        model_editor = cmds.modelPanel(viewport_model_panel, q=True, modelEditor=True)
        self.set_viewport_visibility(model_editor, playblast_visibility_flags)

        # Store original camera settings
        if not overscan:
            overscan_attr = "{0}.overscan".format(camera)
            orig_overscan = cmds.getAttr(overscan_attr)
            cmds.setAttr(overscan_attr, 1.0)

        playblast_failed = False
        mask = ShotMask.get_mask()

        try:
            is_visibility=cmds.getAttr("{0}.{1}".format(mask, "visibility"))
            if is_visibility:
                cmds.setAttr("{0}.{1}".format(mask, "visibility"), 0)
                
           

            image_seq = cmds.playblast(**options)

            cmds.setAttr("{0}.{1}".format(mask, "visibility"), 1)
            

        except:
            traceback.print_exc()
            self.log_error("Failed to create thumbnail. See script editor for details.")
            playblast_failed = True
        finally:
            # Restore original camera settings
            if not overscan:
                cmds.setAttr(overscan_attr, orig_overscan)

            # Restore original viewport settings
            self.set_active_camera(orig_camera)
            self.set_viewport_visibility(model_editor, orig_visibility_flags)

        if playblast_failed:
            return
        image_pattern = re.sub('\.#{4}\.', '.%s.'%start_frame, image_seq)


        cmds.setAttr("{0}.{1}".format(mask, "firstFrameImage"), image_pattern, type="string")

        cmds.currentTime(current_frame)
        self.log_output("thumbnail complete...\n")



    def execute(self, output_dir, filename, padding=4, overscan=False, show_ornaments=True, show_in_viewer=True,
                offscreen=False, overwrite=False, camera_override="", enable_camera_frame_range=False):


        ffmpeg_path = PlayBlastUtils.get_ffmpeg_path()
        if not os.path.exists(ffmpeg_path):
            ffmpeg_path = os.path.dirname(__file__) + '/ffmpeg.exe'

        if self.requires_ffmpeg() and not self.validate_ffmpeg(ffmpeg_path):
            self.log_error("ffmpeg executable is not configured. See script editor for details.")
            return

        temp_file_format = PlayBlastUtils.get_temp_file_format()
        temp_file_is_movie = temp_file_format == "movie"

        if temp_file_is_movie:
            if sys.platform == "win32":
                temp_file_extension = "avi"
            else:
                temp_file_extension = "mov"
        else:
            temp_file_extension = temp_file_format

        viewport_model_panel = self.get_viewport_panel()
        if not viewport_model_panel:
            self.log_error("An active viewport is not selected. Select a viewport and retry.")
            return

        if not output_dir:
            self.log_error("Output directory path not set")
            return
        if not filename:
            self.log_error("Output file name not set")
            return
        
        self.generateAllUvTilePreviews()
        # close displayFilmGate 



        mask = ShotMask.get_mask()

        if mask:
            if cmds.getAttr("{0}.{1}".format(mask, 'firstHandle')):
                frame = cmds.getAttr("{0}.{1}".format(mask, 'firstFrame'))
                start_frame = frame
                end_frame = frame
                self.log_warning("Start  thumbnail image...")
                self.execute_thumb(start_frame=start_frame, end_frame=end_frame)



        # Store original camera
        orig_camera = self.get_active_camera()

        if camera_override:
            camera = camera_override
        else:
            camera = self._camera

        if not camera:
            camera = orig_camera

        if not camera in cmds.listCameras():
            self.log_error("Camera does not exist: {0}".format(camera))
            return

        output_dir = self.resolve_output_directory_path(output_dir)
        filename = self.resolve_output_filename(filename, camera)

        if padding <= 0:
            padding = Playblast.DEFAULT_PADDING

        if self.requires_ffmpeg():
            self._container_format = ShotMask.refresh_config()
            output_path = os.path.normpath(os.path.join(output_dir, "{0}.{1}".format(filename, self._container_format)))
            if not overwrite and os.path.exists(output_path):
                self.log_error("Output file already exists. Eanble overwrite to ignore.")
                return

            playblast_output_dir = "{0}/playblast_temp".format(output_dir)
            playblast_output = os.path.normpath(os.path.join(playblast_output_dir, filename))
            force_overwrite = True
            viewer = False
            quality = 100

            if temp_file_is_movie:
                format_ = "movie"
                compression = None
                index_from_zero = False
            else:
                format_ = "image"
                compression = temp_file_format
                index_from_zero = True
        else:
            playblast_output = os.path.normpath(os.path.join(output_dir, filename))
            force_overwrite = overwrite
            format_ = "image"
            compression = self._encoder
            quality = self._image_quality
            index_from_zero = False
            viewer = show_in_viewer

        widthHeight = self.get_resolution_width_height()
        start_frame, end_frame = self.get_start_end_frame()

        if enable_camera_frame_range:
            if cmds.attributeQuery(Playblast.CAMERA_PLAYBLAST_START_ATTR, node=camera,
                                   exists=True) and cmds.attributeQuery(Playblast.CAMERA_PLAYBLAST_END_ATTR,
                                                                        node=camera, exists=True):
                try:
                    start_frame = int(cmds.getAttr("{0}.{1}".format(camera, Playblast.CAMERA_PLAYBLAST_START_ATTR)))
                    end_frame = int(cmds.getAttr("{0}.{1}".format(camera, Playblast.CAMERA_PLAYBLAST_END_ATTR)))

                    self.log_output(
                        "Camera frame range enabled for '{0}' camera: ({1}, {2})\n".format(camera, start_frame,
                                                                                           end_frame))
                except:
                    self.log_warning(
                        "Camera frame range disabled. Invalid attribute type(s) on '{0}' camera (expected integer or float). Defaulting to Playback range.\n".format(
                            camera))

            else:
                self.log_warning(
                    "Camera frame range disabled. Attributes '{0}' and '{1}' do not exist on '{2}' camera. Defaulting to Playback range.\n".format(
                        Playblast.CAMERA_PLAYBLAST_START_ATTR, Playblast.CAMERA_PLAYBLAST_END_ATTR, camera))

        if start_frame > end_frame:
            self.log_error(
                "Invalid frame range. The start frame ({0}) is greater than the end frame ({1}).".format(start_frame,
                                                                                                         end_frame))
            return

        options = {
            "filename": playblast_output,
            "widthHeight": widthHeight,
            "percent": 100,
            "startTime": start_frame,
            "endTime": end_frame,
            "clearCache": True,
            "forceOverwrite": force_overwrite,
            "format": format_,
            "compression": compression,
            "quality": quality,
            "indexFromZero": index_from_zero,
            "framePadding": padding,
            "showOrnaments": show_ornaments,
            "viewer": viewer,
            "offScreen": offscreen
        }

        if temp_file_is_movie:
            if self.use_trax_sounds():
                options["useTraxSounds"] = True
            else:
                sound_node = self.get_sound_node()
                if sound_node:
                    options["sound"] = sound_node

        self.log_output("Starting '{0}' playblast...".format(camera))
        self.log_output("Playblast options: {0}\n".format(options))
        QtCore.QCoreApplication.processEvents()

        self.set_active_camera(camera)

        dfg = cmds.getAttr("{0}.displayResolution".format(camera))
        over_scan = cmds.getAttr("{0}.overscan".format(camera))
        # cmds.camera(camera, e=1, displayFilmGate=False)
        cmds.setAttr("{0}.displayResolution".format(camera), 0)




        orig_visibility_flags = self.create_viewport_visibility_flags(self.get_viewport_visibility())
        playblast_visibility_flags = self.create_viewport_visibility_flags(self.get_visibility())

        model_editor = cmds.modelPanel(viewport_model_panel, q=True, modelEditor=True)
        self.set_viewport_visibility(model_editor, playblast_visibility_flags)

        # Store original camera settings
        if not overscan:
            overscan_attr = "{0}.overscan".format(camera)
            orig_overscan = cmds.getAttr(overscan_attr)
            cmds.setAttr(overscan_attr, 1.0)

        playblast_failed = False
        
        try:
            is_clamp_texture=cmds.getAttr("hardwareRenderingGlobals.{0}".format("enableTextureMaxRes"))
            if is_clamp_texture:
                cmds.setAttr("hardwareRenderingGlobals.{0}".format("enableTextureMaxRes"), 0)
            cmds.playblast(**options)
            cmds.setAttr("hardwareRenderingGlobals.{0}".format("enableTextureMaxRes"), is_clamp_texture)
        except:
            traceback.print_exc()
            self.log_error("Failed to create playblast. See script editor for details.")
            playblast_failed = True
        finally:
            # Restore original camera settings
            if not overscan:
                cmds.setAttr(overscan_attr, orig_overscan)

            # Restore original viewport settings
            self.set_active_camera(orig_camera)
            self.set_viewport_visibility(model_editor, orig_visibility_flags)

        if playblast_failed:
            return
      
        if self.requires_ffmpeg():
            if temp_file_is_movie:
                source_path = "{0}/{1}.{2}".format(playblast_output_dir, filename, temp_file_extension)
            else:
                source_path = "{0}/{1}.%0{2}d.{3}".format(playblast_output_dir, filename, padding, temp_file_extension)

            if self._encoder == "h264":
                if temp_file_is_movie:
                    self.transcode_h264(ffmpeg_path, source_path, output_path)
                else:
                    self.encode_h264(ffmpeg_path, source_path, output_path, start_frame)
            else:
                self.log_error("Encoding failed. Unsupported encoder ({0}) for container ({1}).".format(self._encoder,
                                                                                                        self._container_format))
                self.remove_temp_dir(playblast_output_dir, temp_file_extension)
                return

            self.remove_temp_dir(playblast_output_dir, temp_file_extension)

            if show_in_viewer:
                self.open_in_viewer(output_path)

        cmds.setAttr("{0}.displayResolution".format(camera),dfg)
        cmds.setAttr("{0}.overscan".format(camera), over_scan)



        self.log_output("Playblast complete\n")

    def remove_temp_dir(self, temp_dir_path, temp_file_extension):

        playblast_dir = QtCore.QDir(temp_dir_path)
        playblast_dir.setNameFilters(["*.{0}".format(temp_file_extension)])
        playblast_dir.setFilter(QtCore.QDir.Files)
        for f in playblast_dir.entryList():
            playblast_dir.remove(f)

        if not playblast_dir.rmdir(temp_dir_path):
            self.log_warning("Failed to remove temporary directory: {0}".format(temp_dir_path))

    def open_in_viewer(self, path):
        if not os.path.exists(path):
            self.log_error("Failed to open in viewer. File does not exists: {0}".format(path))
            return

        if self._container_format in ("mov", "mp4") and cmds.optionVar(exists="PlayblastCmdQuicktime"):
            executable_path = cmds.optionVar(q="PlayblastCmdQuicktime")
            if executable_path:
                QtCore.QProcess.startDetached(executable_path, [path])
                return

        QtGui.QDesktopServices.openUrl(QtCore.QUrl.fromLocalFile(path))

    def requires_ffmpeg(self):
        return self._container_format != "Image"

    def validate_ffmpeg(self, ffmpeg_path):
        if not ffmpeg_path:
            self.log_error("ffmpeg executable path not set")
            return False
        elif not os.path.exists(ffmpeg_path):
            self.log_error("ffmpeg executable path does not exist: {0}".format(ffmpeg_path))
            return False
        elif os.path.isdir(ffmpeg_path):
            self.log_error("Invalid ffmpeg path: {0}".format(ffmpeg_path))
            return False

        return True

    def initialize_ffmpeg_process(self):
        self._ffmpeg_process = QtCore.QProcess()
        self._ffmpeg_process.readyReadStandardError.connect(self.process_ffmpeg_output)

    def execute_ffmpeg_command(self, program, arguments):
        self._ffmpeg_process.start(program, arguments)
        if self._ffmpeg_process.waitForStarted():
            while self._ffmpeg_process.state() != QtCore.QProcess.NotRunning:
                QtCore.QCoreApplication.processEvents()
                QtCore.QThread.usleep(10)

    def process_ffmpeg_output(self):
        byte_array_output = self._ffmpeg_process.readAllStandardError()

        if sys.version_info.major < 3:
            output = str(byte_array_output)
        else:
            output = str(byte_array_output, "utf-8")

        self.log_output(output)

    def encode_h264(self, ffmpeg_path, source_path, output_path, start_frame):
        self.log_output("Starting h264 encoding...")
        self.log_output("ffmpeg path: {0}".format(ffmpeg_path))

        framerate = self.get_frame_rate()

        audio_file_path, audio_frame_offset = self.get_audio_attributes()
        if audio_file_path:
            audio_offset = self.get_audio_offset_in_sec(start_frame, audio_frame_offset, framerate)

        crf = Playblast.H264_QUALITIES[self._h264_quality]
        preset = self._h264_preset

        arguments = []
        arguments.append("-y")
        arguments.extend(["-framerate", "{0}".format(framerate), "-i", source_path])

        if audio_file_path:
            arguments.extend(["-ss", "{0}".format(audio_offset), "-i", audio_file_path])

        arguments.extend(
            ["-c:v", "libx264", "-crf:v", "{0}".format(crf), "-preset:v", preset, "-profile:v", "high", "-pix_fmt",
             "yuv420p"])

        if audio_file_path:
            arguments.extend(["-filter_complex", "[1:0] apad", "-shortest"])

        arguments.append(output_path)

        self.log_output("ffmpeg arguments: {0}\n".format(arguments))

        self.execute_ffmpeg_command(ffmpeg_path, arguments)

    def transcode_h264(self, ffmpeg_path, source_path, output_path):
        self.log_output("Starting h264 transcoding...")
        self.log_output("ffmpeg path: {0}".format(ffmpeg_path))

        crf = Playblast.H264_QUALITIES[self._h264_quality]
        preset = self._h264_preset

        arguments = []
        arguments.append("-y")
        arguments.extend(["-i", source_path])
        arguments.extend(
            ["-c:v", "libx264", "-crf:v", "{0}".format(crf), "-preset:v", preset, "-profile:v", "high", "-pix_fmt",
             "yuv420p"])
        arguments.append(output_path)

        self.log_output("ffmpeg arguments: {0}\n".format(arguments))

        self.execute_ffmpeg_command(ffmpeg_path, arguments)

    def get_frame_rate(self):
        rate_str = cmds.currentUnit(q=True, time=True)

        if rate_str == "game":
            frame_rate = 15.0
        elif rate_str == "film":
            frame_rate = 24.0
        elif rate_str == "pal":
            frame_rate = 25.0
        elif rate_str == "ntsc":
            frame_rate = 30.0
        elif rate_str == "show":
            frame_rate = 48.0
        elif rate_str == "palf":
            frame_rate = 50.0
        elif rate_str == "ntscf":
            frame_rate = 60.0
        elif rate_str.endswith("fps"):
            frame_rate = float(rate_str[0:-3])
        else:
            raise RuntimeError("Unsupported frame rate: {0}".format(rate_str))

        return frame_rate

    def get_sound_node(self):
        return mel.eval("timeControl -q -sound $gPlayBackSlider;")

    def display_sound(self):
        return mel.eval("timeControl -q -displaySound $gPlayBackSlider;")

    def use_trax_sounds(self):
        return self.display_sound() and not self.get_sound_node()

    def get_audio_attributes(self):
        sound_node = self.get_sound_node()
        if sound_node:
            file_path = cmds.getAttr("{0}.filename".format(sound_node))
            file_info = QtCore.QFileInfo(file_path)
            if file_info.exists():
                offset = cmds.getAttr("{0}.offset".format(sound_node))

                return (file_path, offset)

        return (None, None)

    def get_audio_offset_in_sec(self, start_frame, audio_frame_offset, frame_rate):
        return (start_frame - audio_frame_offset) / frame_rate

    def resolve_output_directory_path(self, dir_path):
        dir_path = PlayblastCustomPresets.parse_playblast_output_dir_path(dir_path)

        if "{project}" in dir_path:
            dir_path = dir_path.replace("{project}", self.get_project_dir_path())
        if "{temp}" in dir_path:
            temp_dir_path = PlayBlastUtils.get_temp_output_dir_path()

            if not temp_dir_path:
                self.log_warning("The {temp} directory path is not set")

            dir_path = dir_path.replace("{temp}", temp_dir_path)

        return dir_path

    def resolve_output_filename(self, filename, camera):
        filename = PlayblastCustomPresets.parse_playblast_output_filename(filename)

        if "{scene}" in filename:
            filename = filename.replace("{scene}", self.get_scene_name())
        if "{timestamp}" in filename:
            filename = filename.replace("{timestamp}", self.get_timestamp())

        if "{camera}" in filename:
            new_camera_name = camera

            new_camera_name = new_camera_name.split(':')[-1]
            new_camera_name = new_camera_name.split('|')[-1]

            filename = filename.replace("{camera}", new_camera_name)

        return filename

    def get_project_dir_path(self):
        return cmds.workspace(q=True, rootDirectory=True)

    def get_scene_name(self):
        scene_name = cmds.file(q=True, sceneName=True, shortName=True)
        if scene_name:
            scene_name = os.path.splitext(scene_name)[0]
        else:
            scene_name = "untitled"

        return scene_name

    def get_timestamp(self):
        return "{0}".format(int(time.time()))

    def get_viewport_panel(self):
        model_panel = cmds.getPanel(withFocus=True)
        try:
            cmds.modelPanel(model_panel, q=True, modelEditor=True)
        except:
            return None

        return model_panel

    def get_active_camera(self):
        model_panel = self.get_viewport_panel()
        if not model_panel:
            self.log_error("Failed to get active camera. A viewport is not active.")
            return None

        return cmds.modelPanel(model_panel, q=True, camera=True)

    def set_active_camera(self, camera):
        model_panel = self.get_viewport_panel()
        if model_panel:
            mel.eval("lookThroughModelPanel {0} {1}".format(camera, model_panel))
        else:
            self.log_error("Failed to set active camera. A viewport is not active.")

    def log_error(self, text):
        if self._log_to_maya:
            om.MGlobal.displayError("[Playblast] {0}".format(text))

        self.output_logged.emit("[ERROR] {0}".format(text))  # pylint: disable=E1101

    def log_warning(self, text):
        if self._log_to_maya:
            om.MGlobal.displayWarning("[Playblast] {0}".format(text))

        self.output_logged.emit("[WARNING] {0}".format(text))  # pylint: disable=E1101

    def log_output(self, text):
        if self._log_to_maya:
            om.MGlobal.displayInfo(text)

        self.output_logged.emit(text)  # pylint: disable=E1101


class PlayblastEncoderSettingsDialog(QtWidgets.QDialog):
    ENCODER_PAGES = {
        "h264": 0,
        "Image": 1,
    }

    H264_QUALITIES = [
        "Very High",
        "High",
        "Medium",
        "Low",
    ]

    def __init__(self, parent):
        super(PlayblastEncoderSettingsDialog, self).__init__(parent)

        self.setWindowTitle("Encoder Settings")
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)
        self.setModal(True)
        self.setMinimumWidth(220)

        self.create_widgets()
        self.create_layouts()
        self.create_connections()

    def create_widgets(self):
        # h264
        self.h264_quality_combo = QtWidgets.QComboBox()
        self.h264_quality_combo.addItems(PlayblastEncoderSettingsDialog.H264_QUALITIES)

        self.h264_preset_combo = QtWidgets.QComboBox()
        self.h264_preset_combo.addItems(Playblast.H264_PRESETS)

        h264_layout = QtWidgets.QFormLayout()
        h264_layout.addRow("Quality:", self.h264_quality_combo)
        h264_layout.addRow("Preset:", self.h264_preset_combo)

        h264_settings_wdg = QtWidgets.QGroupBox("h264 Options")
        h264_settings_wdg.setLayout(h264_layout)

        # image
        self.image_quality_sb = QtWidgets.QSpinBox()
        self.image_quality_sb.setMinimumWidth(40)
        self.image_quality_sb.setButtonSymbols(QtWidgets.QSpinBox.NoButtons)
        self.image_quality_sb.setMinimum(1)
        self.image_quality_sb.setMaximum(100)

        image_layout = QtWidgets.QFormLayout()
        image_layout.addRow("Quality:", self.image_quality_sb)

        image_settings_wdg = QtWidgets.QGroupBox("Image Options")
        image_settings_wdg.setLayout(image_layout)

        self.settings_stacked_wdg = QtWidgets.QStackedWidget()
        self.settings_stacked_wdg.addWidget(h264_settings_wdg)
        self.settings_stacked_wdg.addWidget(image_settings_wdg)

        self.accept_btn = QtWidgets.QPushButton("Accept")
        self.cancel_btn = QtWidgets.QPushButton("Cancel")

    def create_layouts(self):
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.accept_btn)
        button_layout.addWidget(self.cancel_btn)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(2, 2, 2, 2)
        main_layout.setSpacing(4)
        main_layout.addWidget(self.settings_stacked_wdg)
        main_layout.addLayout(button_layout)

    def create_connections(self):
        self.accept_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.close)

    def set_page(self, page):
        if not page in PlayblastEncoderSettingsDialog.ENCODER_PAGES:
            return False

        self.settings_stacked_wdg.setCurrentIndex(PlayblastEncoderSettingsDialog.ENCODER_PAGES[page])
        return True

    def set_h264_settings(self, quality, preset):
        self.h264_quality_combo.setCurrentText(quality)
        self.h264_preset_combo.setCurrentText(preset)

    def get_h264_settings(self):
        return {
            "quality": self.h264_quality_combo.currentText(),
            "preset": self.h264_preset_combo.currentText(),
        }

    def set_image_settings(self, quality):
        self.image_quality_sb.setValue(quality)

    def get_image_settings(self):
        return {
            "quality": self.image_quality_sb.value(),
        }


class PlayblastVisibilityDialog(QtWidgets.QDialog):

    def __init__(self, parent):
        super(PlayblastVisibilityDialog, self).__init__(parent)

        self.setWindowTitle("Customize Visibility")
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)
        self.setModal(True)

        visibility_layout = QtWidgets.QGridLayout()

        index = 0
        self.visibility_checkboxes = []

        for i in range(len(Playblast.VIEWPORT_VISIBILITY_LOOKUP)):
            checkbox = QtWidgets.QCheckBox(Playblast.VIEWPORT_VISIBILITY_LOOKUP[i][0])

            visibility_layout.addWidget(checkbox, index / 3, index % 3)
            self.visibility_checkboxes.append(checkbox)

            index += 1

        visibility_grp = QtWidgets.QGroupBox("")
        visibility_grp.setLayout(visibility_layout)

        apply_btn = QtWidgets.QPushButton("Apply")
        apply_btn.clicked.connect(self.accept)

        cancel_btn = QtWidgets.QPushButton("Cancel")
        cancel_btn.clicked.connect(self.close)

        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(apply_btn)
        button_layout.addWidget(cancel_btn)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(4, 4, 4, 4)
        main_layout.setSpacing(4)
        main_layout.addWidget(visibility_grp)
        main_layout.addStretch()
        main_layout.addLayout(button_layout)

    def get_visibility_data(self):
        data = []
        for checkbox in self.visibility_checkboxes:
            data.append(checkbox.isChecked())

        return data

    def set_visibility_data(self, data):
        if len(self.visibility_checkboxes) != len(data):
            raise RuntimeError("Visibility property/data mismatch")

        for i in range(len(data)):
            self.visibility_checkboxes[i].setChecked(data[i])


class PlayblastWidget(QtWidgets.QWidget):
    OPT_VAR_OUTPUT_DIR = "PlayblastOutputDir"
    OPT_VAR_OUTPUT_FILENAME = "PlayblastOutputFilename"
    OPT_VAR_FORCE_OVERWRITE = "PlayblastForceOverwrite"

    OPT_VAR_CAMERA = "PlayblastCamera"
    OPT_VAR_HIDE_DEFAULT_CAMERAS = "PlayblastHideDefaultCameras"

    OPT_VAR_RESOLUTION_PRESET = "PlayblastResolutionPreset"
    OPT_VAR_RESOLUTION_WIDTH = "PlayblastResolutionWidth"
    OPT_VAR_RESOLUTION_HEIGHT = "PlayblastResolutionHeight"

    OPT_VAR_FRAME_RANGE_PRESET = "PlayblastFrameRangePreset"
    OPT_VAR_FRAME_RANGE_START = "PlayblastFrameRangeStart"
    OPT_VAR_FRAME_RANGE_END = "PlayblastFrameRangeEnd"

    OPT_VAR_ENCODING_CONTAINER = "PlayblastEncodingContainer"
    OPT_VAR_ENCODING_VIDEO_CODEC = "PlayblastEncodingVideoCodec"

    OPT_VAR_H264_QUALITY = "PlayblastH264Quality"
    OPT_VAR_H264_PRESET = "PlayblastH264Preset"

    OPT_VAR_IMAGE_QUALITY = "PlayblastImageQuality"

    OPT_VAR_VISIBILITY_PRESET = "PlayblastVisibilityPreset"
    OPT_VAR_VISIBILITY_DATA = "PlayblastVisibilityData"

    OPT_VAR_OVERSCAN = "PlayblastOverscan"
    OPT_VAR_ORNAMENTS = "PlayblastOrnaments"
    OPT_VAR_OFFSCREEN = "PlayblastOffscreen"
    OPT_VAR_SHOT_MASK = "PlayblastShotMask"
    OPT_VAR_SHOT_MASK_CROP = "PlayblastShotMaskCrop"
    OPT_VAR_FIT_SHOT_MASK = "PlayblastFitShotMask"
    OPT_VAR_VIEWER = "PlayblastViewer"
    OPT_VAR_FIRST_HANDLE = "PlayblastFirstHandle"

    OPT_VAR_LOG_TO_SCRIPT_EDITOR = "PlayblastLogToSE"

    CONTAINER_PRESETS = [
        "mov",
        "mp4",
        "Image",
    ]

    collapsed_state_changed = QtCore.Signal()

    def __init__(self, parent=None):
        super(PlayblastWidget, self).__init__(parent)

        self._playblast = Playblast()

        self._settings_dialog = None
        self._encoder_settings_dialog = None
        self._visibility_dialog = None

        self.create_widgets()
        self.create_layouts()

        encoder = ShotMask.refresh_config()
        self.encoding_video_codec_cmb.setCurrentText(encoder)

        self.create_connections()

        self.load_settings()

    def create_widgets(self):
        button_height = 19
        icon_button_height = 18
        combo_box_min_width = 100

        self.output_dir_path_le = LineEdit(LineEdit.TYPE_PLAYBLAST_OUTPUT_PATH)
        self.output_dir_path_le.setPlaceholderText("{project}/movies")

        self.output_dir_path_select_btn = QtWidgets.QPushButton("...")
        self.output_dir_path_select_btn.setFixedSize(24, icon_button_height)
        self.output_dir_path_select_btn.setToolTip("Select Output Directory")

        self.output_dir_path_show_folder_btn = QtWidgets.QPushButton(QtGui.QIcon(":fileOpen.png"), "")
        self.output_dir_path_show_folder_btn.setFixedSize(24, icon_button_height)
        self.output_dir_path_show_folder_btn.setToolTip("Show in Folder")

        self.output_filename_le = LineEdit(LineEdit.TYPE_PLAYBLAST_OUTPUT_FILENAME)
        self.output_filename_le.setPlaceholderText("{scene}")
        self.output_filename_le.setText("{scene}")
        self.output_filename_le.setMaximumWidth(200)
        self.force_overwrite_cb = QtWidgets.QCheckBox("Force overwrite")

        self.resolution_select_cmb = QtWidgets.QComboBox()
        self.resolution_select_cmb.setMinimumWidth(combo_box_min_width)
        self.resolution_select_cmb.addItems(self._playblast.resolution_preset_names)
        self.resolution_select_cmb.addItem("Custom")
        self.resolution_select_cmb.setCurrentText(Playblast.DEFAULT_RESOLUTION)

        self.resolution_width_sb = QtWidgets.QSpinBox()
        self.resolution_width_sb.setButtonSymbols(QtWidgets.QSpinBox.NoButtons)
        self.resolution_width_sb.setRange(1, 9999)
        self.resolution_width_sb.setMinimumWidth(40)
        self.resolution_width_sb.setAlignment(QtCore.Qt.AlignRight)
        self.resolution_height_sb = QtWidgets.QSpinBox()
        self.resolution_height_sb.setButtonSymbols(QtWidgets.QSpinBox.NoButtons)
        self.resolution_height_sb.setRange(1, 9999)
        self.resolution_height_sb.setMinimumWidth(40)
        self.resolution_height_sb.setAlignment(QtCore.Qt.AlignRight)

        self.camera_select_cmb = QtWidgets.QComboBox()
        self.camera_select_cmb.setMinimumWidth(combo_box_min_width)
        self.camera_select_hide_defaults_cb = QtWidgets.QCheckBox("Hide defaults")
        self.refresh_cameras()

        self.frame_range_cmb = QtWidgets.QComboBox()
        self.frame_range_cmb.setMinimumWidth(combo_box_min_width)
        self.frame_range_cmb.addItems(Playblast.FRAME_RANGE_PRESETS)
        self.frame_range_cmb.addItem("Custom")
        self.frame_range_cmb.setCurrentText(Playblast.DEFAULT_FRAME_RANGE)

        self.frame_range_start_sb = QtWidgets.QSpinBox()
        self.frame_range_start_sb.setButtonSymbols(QtWidgets.QSpinBox.NoButtons)
        self.frame_range_start_sb.setRange(-9999, 9999)
        self.frame_range_start_sb.setMinimumWidth(40)
        self.frame_range_start_sb.setAlignment(QtCore.Qt.AlignRight)

        self.frame_range_end_sb = QtWidgets.QSpinBox()
        self.frame_range_end_sb.setButtonSymbols(QtWidgets.QSpinBox.NoButtons)
        self.frame_range_end_sb.setRange(-9999, 9999)
        self.frame_range_end_sb.setMinimumWidth(40)
        self.frame_range_end_sb.setAlignment(QtCore.Qt.AlignRight)

        self.encoding_container_cmb = QtWidgets.QComboBox()
        self.encoding_container_cmb.setMinimumWidth(combo_box_min_width)
        self.encoding_container_cmb.addItems(PlayblastWidget.CONTAINER_PRESETS)
        self.encoding_container_cmb.setCurrentText(Playblast.DEFAULT_CONTAINER)
        self.encoding_container_cmb.setVisible(False)

        self.encoding_video_codec_cmb = QtWidgets.QComboBox()
        self.encoding_video_codec_cmb.setMinimumWidth(combo_box_min_width)
        self.encoding_video_codec_settings_btn = QtWidgets.QPushButton("Settings...")
        self.encoding_video_codec_settings_btn.setFixedHeight(button_height)
        self.encoding_video_codec_cmb.setVisible(False)
        self.encoding_video_codec_settings_btn.setVisible(False)

        self.visibility_cmb = QtWidgets.QComboBox()
        self.visibility_cmb.setMinimumWidth(combo_box_min_width)
        self.visibility_cmb.addItems(self._playblast.viewport_visibility_preset_names)
        self.visibility_cmb.addItem("Custom")
        self.visibility_cmb.setCurrentText(Playblast.DEFAULT_VISIBILITY)
        self.visibility_cmb.setVisible(False)

        self.visibility_customize_btn = QtWidgets.QPushButton("Customize...")
        self.visibility_customize_btn.setFixedHeight(button_height)
        self.visibility_customize_btn.setVisible(False)
        self.overscan_cb = QtWidgets.QCheckBox("Overscan")
        self.overscan_cb.setChecked(False)

        self.ornaments_cb = QtWidgets.QCheckBox("Ornaments")
        self.ornaments_cb.setChecked(False)

        self.offscreen_cb = QtWidgets.QCheckBox("Offscreen")
        self.offscreen_cb.setChecked(False)

        self.crop_cb = QtWidgets.QCheckBox("Mask")
        self.crop_cb.setChecked(True)

        self.viewer_cb = QtWidgets.QCheckBox("Show in Viewer")
        self.viewer_cb.setChecked(True)

        self.shot_mask_cb = QtWidgets.QCheckBox("Shot Mask")
        self.shot_mask_cb.setChecked(True)

        self.fit_shot_mask_cb = QtWidgets.QCheckBox("Fit Shot Mask")
        self.fit_shot_mask_cb.setChecked(False)

        self.output_edit = QtWidgets.QPlainTextEdit()
        self.output_edit.setFocusPolicy(QtCore.Qt.NoFocus)
        self.output_edit.setReadOnly(True)
        self.output_edit.setWordWrapMode(QtGui.QTextOption.NoWrap)

        self.log_to_script_editor_cb = QtWidgets.QCheckBox("Log to Script Editor")
        self.log_to_script_editor_cb.setChecked(self._playblast.is_maya_logging_enabled())

        self.clear_btn = QtWidgets.QPushButton("Clear")
        self.clear_btn.setMinimumWidth(70)
        self.clear_btn.setFixedHeight(button_height)

        self.first_handle_editor_cb = QtWidgets.QCheckBox("First Handle")
        self.first_handle_editor_cb.setChecked(True)
        self.descrption_edit = QtWidgets.QPlainTextEdit()

    def create_layouts(self):
        output_path_layout = QtWidgets.QHBoxLayout()
        output_path_layout.setSpacing(2)
        output_path_layout.addWidget(self.output_dir_path_le)
        output_path_layout.addWidget(self.output_dir_path_select_btn)
        output_path_layout.addWidget(self.output_dir_path_show_folder_btn)

        output_file_layout = QtWidgets.QHBoxLayout()
        output_file_layout.setSpacing(4)
        output_file_layout.addWidget(self.output_filename_le)
        output_file_layout.addWidget(self.force_overwrite_cb)

        output_layout = FormLayout()
        output_layout.setContentsMargins(4, 14, 4, 14)
        output_layout.addLayoutRow(0, "Output Dir:", output_path_layout)
        output_layout.addLayoutRow(1, "Filename:", output_file_layout)

        camera_options_layout = QtWidgets.QHBoxLayout()
        camera_options_layout.setSpacing(6)
        camera_options_layout.addWidget(self.camera_select_cmb)
        camera_options_layout.addWidget(self.camera_select_hide_defaults_cb)
        camera_options_layout.addStretch()

        resolution_layout = QtWidgets.QHBoxLayout()
        resolution_layout.setSpacing(4)
        resolution_layout.addWidget(self.resolution_select_cmb)
        resolution_layout.addSpacing(2)
        resolution_layout.addWidget(self.resolution_width_sb)
        resolution_layout.addWidget(QtWidgets.QLabel("x"))
        resolution_layout.addWidget(self.resolution_height_sb)
        resolution_layout.addStretch()

        frame_range_layout = QtWidgets.QHBoxLayout()
        frame_range_layout.setSpacing(4)
        frame_range_layout.addWidget(self.frame_range_cmb)
        frame_range_layout.addSpacing(2)
        frame_range_layout.addWidget(self.frame_range_start_sb)
        frame_range_layout.addWidget(self.frame_range_end_sb)
        frame_range_layout.addStretch()

        encoding_layout = QtWidgets.QHBoxLayout()
        encoding_layout.setSpacing(2)
        encoding_layout.addWidget(self.encoding_container_cmb)
        encoding_layout.addWidget(self.encoding_video_codec_cmb)
        encoding_layout.addWidget(self.encoding_video_codec_settings_btn)
        encoding_layout.addStretch()

        visibility_layout = QtWidgets.QHBoxLayout()
        visibility_layout.setSpacing(4)
        visibility_layout.addWidget(self.visibility_cmb)
        visibility_layout.addWidget(self.visibility_customize_btn)
        visibility_layout.addStretch()

        cb_options_layout_a = QtWidgets.QGridLayout()
        cb_options_layout_a.setColumnMinimumWidth(0, 100)
        cb_options_layout_a.addWidget(self.ornaments_cb, 0, 0)
        cb_options_layout_a.addWidget(self.overscan_cb, 0, 1)
        cb_options_layout_a.addWidget(self.offscreen_cb, 0, 2)
        cb_options_layout_a.addWidget(self.crop_cb, 0, 3)
        cb_options_layout_a.setColumnStretch(3, 1)

        cb_options_layout_b = QtWidgets.QGridLayout()
        cb_options_layout_b.setColumnMinimumWidth(0, 100)
        cb_options_layout_b.addWidget(self.shot_mask_cb, 0, 0)
        cb_options_layout_b.addWidget(self.fit_shot_mask_cb, 0, 1)
        cb_options_layout_b.addWidget(self.viewer_cb, 0, 2)
        cb_options_layout_b.setColumnStretch(2, 1)

        options_layout = FormLayout()
        options_layout.setVerticalSpacing(5)
        options_layout.addLayoutRow(0, "Camera:", camera_options_layout)
        options_layout.addLayoutRow(1, "Resolution:", resolution_layout)
        options_layout.addLayoutRow(2, "Frame Range:", frame_range_layout)
        # options_layout.addLayoutRow(3, "Encoding:", encoding_layout)
        # options_layout.addLayoutRow(4, "Visiblity:", visibility_layout)
        options_layout.addLayoutRow(5, "", cb_options_layout_a)
        options_layout.addLayoutRow(6, "", cb_options_layout_b)

        self.options_grp = CollapsibleGrpWidget("Options")
        self.options_grp.add_layout(options_layout)

        # first handle

        first_handle_layout = QtWidgets.QHBoxLayout()
        first_handle_layout.setContentsMargins(4, 0, 4, 10)
        first_handle_layout.addWidget(self.first_handle_editor_cb)
        first_handle_layout.addStretch()
        # first_handle_layout.addWidget(self.clear_btn)

        self.first_handle_grp = CollapsibleGrpWidget("First Handle")
        self.first_handle_grp.body_layout.setContentsMargins(0, 0, 0, 0)
        self.first_handle_grp.append_stretch_on_collapse = True
        self.first_handle_grp.setContentsMargins(0, 0, 0, 0)
        self.first_handle_grp.add_widget(self.descrption_edit)
        self.first_handle_grp.add_layout(first_handle_layout)

        logging_button_layout = QtWidgets.QHBoxLayout()
        logging_button_layout.setContentsMargins(4, 0, 4, 10)
        logging_button_layout.addWidget(self.log_to_script_editor_cb)
        logging_button_layout.addStretch()
        logging_button_layout.addWidget(self.clear_btn)

        self.logging_grp = CollapsibleGrpWidget("Logging")
        self.logging_grp.body_layout.setContentsMargins(0, 0, 0, 0)
        self.logging_grp.append_stretch_on_collapse = True
        self.logging_grp.setContentsMargins(0, 0, 0, 0)
        self.logging_grp.add_widget(self.output_edit)
        self.logging_grp.add_layout(logging_button_layout)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(4, 4, 4, 4)
        main_layout.setSpacing(4)
        main_layout.addLayout(output_layout)
        main_layout.addWidget(self.options_grp)
        main_layout.addWidget(self.first_handle_grp)
        main_layout.addWidget(self.logging_grp)

    def create_connections(self):
        self.output_dir_path_select_btn.clicked.connect(self.select_output_directory)
        self.output_dir_path_show_folder_btn.clicked.connect(self.open_output_directory)

        self.camera_select_cmb.currentTextChanged.connect(self.on_camera_changed)
        self.camera_select_hide_defaults_cb.toggled.connect(self.refresh_cameras)

        self.frame_range_cmb.currentTextChanged.connect(self.refresh_frame_range)
        self.frame_range_start_sb.editingFinished.connect(self.on_frame_range_changed)
        self.frame_range_end_sb.editingFinished.connect(self.on_frame_range_changed)

        self.encoding_container_cmb.currentTextChanged.connect(self.refresh_video_encoders)
        self.encoding_video_codec_cmb.currentTextChanged.connect(self.on_video_encoder_changed)
        self.encoding_video_codec_settings_btn.clicked.connect(self.show_encoder_settings_dialog)

        self.resolution_select_cmb.currentTextChanged.connect(self.refresh_resolution)
        self.resolution_width_sb.editingFinished.connect(self.on_resolution_changed)
        self.resolution_height_sb.editingFinished.connect(self.on_resolution_changed)

        self.visibility_cmb.currentTextChanged.connect(self.on_visibility_preset_changed)
        self.visibility_customize_btn.clicked.connect(self.show_visibility_dialog)

        self._playblast.output_logged.connect(self.append_output)  # pylint: disable=E1101

        self.log_to_script_editor_cb.toggled.connect(self.on_log_to_script_editor_changed)
        self.clear_btn.clicked.connect(self.output_edit.clear)

        self.options_grp.collapsed_state_changed.connect(self.on_collapsed_state_changed)  # pylint: disable=E1101
        self.logging_grp.collapsed_state_changed.connect(self.on_collapsed_state_changed)  # pylint: disable=E1101

        self.crop_cb.toggled.connect(self.on_crop_changed)
        self.output_filename_le.textChanged.connect(self.on_output_filename_changed)

        self.descrption_edit.textChanged.connect(self.on_descrption_edit_changed)
        self.first_handle_editor_cb.toggled.connect(self.on_first_handle_editor_cb_changed)

    def on_first_handle_editor_cb_changed(self, state):

        mask = ShotMask.get_mask()
        if mask:
            self.on_descrption_edit_changed()
            mask = ShotMask.get_mask()
            cmds.setAttr("{0}.{1}".format(mask, 'firstHandle'), state)

            if cmds.getAttr("{0}.{1}".format(mask, 'firstHandle')):
                frame = cmds.getAttr("{0}.{1}".format(mask, 'firstFrame'))
                start_frame = frame
                end_frame = frame
                cmds.evalDeferred(partial(self._playblast.execute_thumb, start_frame, end_frame))

        ShotMask.refresh_config()
        ShotMask.refresh_mask()

    def on_descrption_edit_changed(self):
        current_text = self.descrption_edit.toPlainText()
        mask = ShotMask.get_mask()

        if mask:
            if current_text:

                cmds.setAttr("{0}.{1}".format(mask, 'descrption'), 'Descrption:' + current_text, type="string")
            else:
                cmds.setAttr("{0}.{1}".format(mask, 'descrption'), '', type="string")

            ShotMask.refresh_mask()

    def on_output_filename_changed(self, text):

        cmds.optionVar(sv=(PlayblastWidget.OPT_VAR_OUTPUT_FILENAME, self.output_filename_le.text()))
        ShotMask.refresh_config()

        ShotMask.refresh_mask()

    def on_crop_changed(self, state):
        cmds.optionVar(iv=(PlayblastWidget.OPT_VAR_SHOT_MASK_CROP, state))
        ShotMask.set_visible_mask(state)

    def do_playblast(self, batch_cameras=[]):
        output_dir_path = self.output_dir_path_le.text()
        if not output_dir_path:
            output_dir_path = self.output_dir_path_le.placeholderText()

        filename = self.output_filename_le.text()
        if not filename:
            filename = self.output_filename_le.placeholderText()

        padding = Playblast.DEFAULT_PADDING

        overscan = self.overscan_cb.isChecked()
        show_ornaments = self.ornaments_cb.isChecked()
        show_in_viewer = self.viewer_cb.isChecked()
        overwrite = self.force_overwrite_cb.isChecked()
        use_camera_frame_range = self.frame_range_cmb.currentText() == "Camera"
        offscreen = self.offscreen_cb.isChecked()

        display_shot_mask = self.shot_mask_cb.isChecked()
        shot_mask_visible = ShotMask.get_mask()
        fit_shot_mask = self.fit_shot_mask_cb.isChecked()
        display_view_mask=self.crop_cb.isChecked()
        orig_camera = ShotMask.get_camera_name()

        cmds.evalDeferred(partial(self.pre_playblast, display_shot_mask, shot_mask_visible, fit_shot_mask))

        if batch_cameras:
            for batch_camera in batch_cameras:
                batch_camera_filename = filename
                if "{camera}" not in batch_camera_filename:
                    batch_camera_filename = "{0}_{{camera}}".format(filename)

                cmds.evalDeferred(
                    partial(self._playblast.execute, output_dir_path, batch_camera_filename, padding, overscan,
                            show_ornaments, show_in_viewer, offscreen, overwrite, batch_camera, use_camera_frame_range))
        else:
            cmds.evalDeferred(
                partial(self._playblast.execute, output_dir_path, filename, padding, overscan, show_ornaments,
                        show_in_viewer, offscreen, overwrite, "", use_camera_frame_range))

        cmds.evalDeferred(
            partial(self.post_playblast, display_shot_mask, shot_mask_visible, display_view_mask,fit_shot_mask, orig_camera))

    def pre_playblast(self, display_shot_mask, shot_mask_visible, fit_shot_mask):
        if display_shot_mask:
            if fit_shot_mask:
                # Fit shot mask to playbast width/height
                self.orig_render_width = cmds.getAttr("defaultResolution.width")
                self.orig_render_device_aspect_ratio = cmds.getAttr("defaultResolution.deviceAspectRatio")

                playblast_width, playblast_height = self._playblast.get_resolution_width_height()
                cmds.setAttr("defaultResolution.width", playblast_width)
                cmds.setAttr("defaultResolution.deviceAspectRatio", playblast_width / float(playblast_height))

            ShotMask.set_camera_name("")
            if shot_mask_visible:
                ShotMask.refresh_mask()
            else:
                ShotMask.create_mask()
        else:
            ShotMask.delete_mask()



    def post_playblast(self, display_shot_mask, shot_mask_visible,display_view_mask, fit_shot_mask, orig_camera):
        if display_shot_mask:
            if fit_shot_mask:
                cmds.setAttr("defaultResolution.width", self.orig_render_width)
                cmds.setAttr("defaultResolution.deviceAspectRatio", self.orig_render_device_aspect_ratio)

            ShotMask.set_camera_name(orig_camera)
            if shot_mask_visible:
                ShotMask.refresh_mask()
            else:
                ShotMask.delete_mask()
        elif shot_mask_visible:
            ShotMask.create_mask()

        if display_view_mask:
            ShotMask.set_visible_mask(1)
        else:
            ShotMask.set_visible_mask(0)

    def select_output_directory(self):
        current_dir_path = self.output_dir_path_le.text()
        if not current_dir_path:
            current_dir_path = self.output_dir_path_le.placeholderText()

        current_dir_path = self._playblast.resolve_output_directory_path(current_dir_path)

        file_info = QtCore.QFileInfo(current_dir_path)
        if not file_info.exists():
            current_dir_path = self._playblast.get_project_dir_path()

        new_dir_path = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Directory", current_dir_path)
        if new_dir_path:
            self.output_dir_path_le.setText(new_dir_path)

    def open_output_directory(self):
        output_dir_path = self.output_dir_path_le.text()
        if not output_dir_path:
            output_dir_path = self.output_dir_path_le.placeholderText()

        output_dir_path = self._playblast.resolve_output_directory_path(output_dir_path)

        file_info = QtCore.QFileInfo(output_dir_path)
        if file_info.isDir():
            if cmds.about(win=True):
                file_prefix = "file:///"
            else:
                file_prefix = "file://"

            QtGui.QDesktopServices.openUrl(
                QtCore.QUrl("{0}{1}".format(file_prefix, file_info.absoluteFilePath()), QtCore.QUrl.TolerantMode))
        else:
            self.append_output("[ERROR] Invalid directory path: {0}".format(output_dir_path))

    def refresh_all(self):
        self.refresh_cameras()
        self.refresh_resolution()
        self.refresh_frame_range()
        self.refresh_video_encoders()

    def refresh_cameras(self):
        current_camera = self.camera_select_cmb.currentText()
        self.camera_select_cmb.clear()

        self.camera_select_cmb.addItem("<Active>")
        self.camera_select_cmb.addItems(
            PlayBlastUtils.cameras_in_scene(self.camera_select_hide_defaults_cb.isChecked(), True))

        self.camera_select_cmb.setCurrentText(current_camera)

    def on_camera_changed(self):
        camera = self.camera_select_cmb.currentText()

        if camera == "<Active>":
            camera = None

        self._playblast.set_camera(camera)

    def refresh_resolution(self):
        resolution_preset = self.resolution_select_cmb.currentText()
        if resolution_preset != "Custom":
            self._playblast.set_resolution(resolution_preset)

            resolution = self._playblast.get_resolution_width_height()
            self.resolution_width_sb.setValue(resolution[0])
            self.resolution_height_sb.setValue(resolution[1])

    def on_resolution_changed(self):
        resolution = (self.resolution_width_sb.value(), self.resolution_height_sb.value())

        for key in self._playblast.resolution_presets.keys():
            if self._playblast.resolution_presets[key] == resolution:
                self.resolution_select_cmb.setCurrentText(key)
                return

        self.resolution_select_cmb.setCurrentText("Custom")

        self._playblast.set_resolution(resolution)

    def refresh_frame_range(self):
        frame_range_preset = self.frame_range_cmb.currentText()
        if frame_range_preset != "Custom":
            frame_range = self._playblast.preset_to_frame_range(frame_range_preset)

            self.frame_range_start_sb.setValue(frame_range[0])
            self.frame_range_end_sb.setValue(frame_range[1])

            self._playblast.set_frame_range(frame_range_preset)

        enable_frame_range_spinboxes = frame_range_preset != "Camera"
        self.frame_range_start_sb.setEnabled(enable_frame_range_spinboxes)
        self.frame_range_end_sb.setEnabled(enable_frame_range_spinboxes)

    def on_frame_range_changed(self):
        self.frame_range_cmb.setCurrentText("Custom")

        frame_range = (self.frame_range_start_sb.value(), self.frame_range_end_sb.value())
        self._playblast.set_frame_range(frame_range)

    def refresh_video_encoders(self):
        encoder = self.encoding_video_codec_cmb.currentText()
        self.encoding_video_codec_cmb.clear()

        container = self.encoding_container_cmb.currentText()
        self.encoding_video_codec_cmb.addItems(Playblast.VIDEO_ENCODER_LOOKUP[container])
        self.encoding_video_codec_cmb.setCurrentText(encoder)

    def on_video_encoder_changed(self):
        container = self.encoding_container_cmb.currentText()
        encoder = self.encoding_video_codec_cmb.currentText()

        if container and encoder:
            self._playblast.set_encoding(container, encoder)

    def show_encoder_settings_dialog(self):
        if not self._encoder_settings_dialog:
            self._encoder_settings_dialog = PlayblastEncoderSettingsDialog(self)
            self._encoder_settings_dialog.accepted.connect(self.on_encoder_settings_dialog_modified)

        if self.encoding_container_cmb.currentText() == "Image":
            self._encoder_settings_dialog.set_page("Image")

            image_settings = self._playblast.get_image_settings()
            self._encoder_settings_dialog.set_image_settings(image_settings["quality"])

        else:
            encoder = self.encoding_video_codec_cmb.currentText()
            if encoder == "h264":
                self._encoder_settings_dialog.set_page("h264")

                h264_settings = self._playblast.get_h264_settings()
                self._encoder_settings_dialog.set_h264_settings(h264_settings["quality"], h264_settings["preset"])
            else:
                self.append_output("[ERROR] Settings page not found for encoder: {0}".format(encoder))

        self._encoder_settings_dialog.show()

    def on_encoder_settings_dialog_modified(self):
        if self.encoding_container_cmb.currentText() == "Image":
            image_settings = self._encoder_settings_dialog.get_image_settings()
            self._playblast.set_image_settings(image_settings["quality"])
        else:
            encoder = self.encoding_video_codec_cmb.currentText()
            if encoder == "h264":
                h264_settings = self._encoder_settings_dialog.get_h264_settings()
                self._playblast.set_h264_settings(h264_settings["quality"], h264_settings["preset"])
            else:
                self.append_output("[ERROR] Failed to set encoder settings. Unknown encoder: {0}".format(encoder))

    def on_visibility_preset_changed(self):
        visibility_preset = self.visibility_cmb.currentText()
        if visibility_preset != "Custom":
            self._playblast.set_visibility(visibility_preset)

    def show_visibility_dialog(self):
        if not self._visibility_dialog:
            self._visibility_dialog = PlayblastVisibilityDialog(self)
            self._visibility_dialog.accepted.connect(self.on_visibility_dialog_modified)

        self._visibility_dialog.set_visibility_data(self._playblast.get_visibility())

        self._visibility_dialog.show()

    def on_visibility_dialog_modified(self):
        self.visibility_cmb.setCurrentText("Custom")
        self._playblast.set_visibility(self._visibility_dialog.get_visibility_data())

    def on_log_to_script_editor_changed(self):
        self._playblast.set_maya_logging_enabled(self.log_to_script_editor_cb.isChecked())

    def on_collapsed_state_changed(self):
        self.collapsed_state_changed.emit()  # pylint: disable=E1101

    def get_collapsed_states(self):
        collapsed = 0
        collapsed += int(self.options_grp.is_collapsed())
        collapsed += int(self.logging_grp.is_collapsed()) << 1

        return collapsed

    def set_collapsed_states(self, collapsed):
        self.options_grp.set_collapsed(collapsed & 1)
        self.logging_grp.set_collapsed(collapsed & 2)

    def save_settings(self):
        cmds.optionVar(sv=(PlayblastWidget.OPT_VAR_OUTPUT_DIR, self.output_dir_path_le.text()))
        cmds.optionVar(sv=(PlayblastWidget.OPT_VAR_OUTPUT_FILENAME, self.output_filename_le.text()))
        cmds.optionVar(iv=(PlayblastWidget.OPT_VAR_FORCE_OVERWRITE, self.force_overwrite_cb.isChecked()))

        cmds.optionVar(sv=(PlayblastWidget.OPT_VAR_CAMERA, self.camera_select_cmb.currentText()))
        cmds.optionVar(
            iv=(PlayblastWidget.OPT_VAR_HIDE_DEFAULT_CAMERAS, self.camera_select_hide_defaults_cb.isChecked()))

        cmds.optionVar(sv=(PlayblastWidget.OPT_VAR_RESOLUTION_PRESET, self.resolution_select_cmb.currentText()))
        cmds.optionVar(iv=(PlayblastWidget.OPT_VAR_RESOLUTION_WIDTH, self.resolution_width_sb.value()))
        cmds.optionVar(iv=(PlayblastWidget.OPT_VAR_RESOLUTION_HEIGHT, self.resolution_height_sb.value()))

        cmds.optionVar(sv=(PlayblastWidget.OPT_VAR_FRAME_RANGE_PRESET, self.frame_range_cmb.currentText()))
        cmds.optionVar(iv=(PlayblastWidget.OPT_VAR_FRAME_RANGE_START, self.frame_range_start_sb.value()))
        cmds.optionVar(iv=(PlayblastWidget.OPT_VAR_FRAME_RANGE_END, self.frame_range_end_sb.value()))

        cmds.optionVar(sv=(PlayblastWidget.OPT_VAR_ENCODING_CONTAINER, self.encoding_container_cmb.currentText()))
        cmds.optionVar(sv=(PlayblastWidget.OPT_VAR_ENCODING_VIDEO_CODEC, self.encoding_video_codec_cmb.currentText()))

        h264_settings = self._playblast.get_h264_settings()
        cmds.optionVar(sv=(PlayblastWidget.OPT_VAR_H264_QUALITY, h264_settings["quality"]))
        cmds.optionVar(sv=(PlayblastWidget.OPT_VAR_H264_PRESET, h264_settings["preset"]))

        image_settings = self._playblast.get_image_settings()
        cmds.optionVar(iv=(PlayblastWidget.OPT_VAR_IMAGE_QUALITY, image_settings["quality"]))

        cmds.optionVar(sv=(PlayblastWidget.OPT_VAR_VISIBILITY_PRESET, self.visibility_cmb.currentText()))

        visibility_data = self._playblast.get_visibility()
        if visibility_data:
            visibility_str = ""
            for item in visibility_data:
                visibility_str = "{0} {1}".format(visibility_str, int(item))
            cmds.optionVar(sv=(PlayblastWidget.OPT_VAR_VISIBILITY_DATA, visibility_str))

        cmds.optionVar(iv=(PlayblastWidget.OPT_VAR_OVERSCAN, self.overscan_cb.isChecked()))
        cmds.optionVar(iv=(PlayblastWidget.OPT_VAR_ORNAMENTS, self.ornaments_cb.isChecked()))
        cmds.optionVar(iv=(PlayblastWidget.OPT_VAR_OFFSCREEN, self.offscreen_cb.isChecked()))
        cmds.optionVar(iv=(PlayblastWidget.OPT_VAR_SHOT_MASK, self.shot_mask_cb.isChecked()))
        cmds.optionVar(iv=(PlayblastWidget.OPT_VAR_SHOT_MASK_CROP, self.crop_cb.isChecked()))
        cmds.optionVar(iv=(PlayblastWidget.OPT_VAR_FIT_SHOT_MASK, self.fit_shot_mask_cb.isChecked()))
        cmds.optionVar(iv=(PlayblastWidget.OPT_VAR_VIEWER, self.viewer_cb.isChecked()))

        cmds.optionVar(iv=(PlayblastWidget.OPT_VAR_LOG_TO_SCRIPT_EDITOR, self.log_to_script_editor_cb.isChecked()))

        cmds.optionVar(iv=(PlayblastWidget.OPT_VAR_FIRST_HANDLE, self.first_handle_editor_cb.isChecked()))

    def load_settings(self):
        if cmds.optionVar(exists=PlayblastWidget.OPT_VAR_OUTPUT_DIR):
            self.output_dir_path_le.setText(cmds.optionVar(q=PlayblastWidget.OPT_VAR_OUTPUT_DIR))
        if cmds.optionVar(exists=PlayblastWidget.OPT_VAR_OUTPUT_FILENAME):
            self.output_filename_le.setText(cmds.optionVar(q=PlayblastWidget.OPT_VAR_OUTPUT_FILENAME))
        if cmds.optionVar(exists=PlayblastWidget.OPT_VAR_FORCE_OVERWRITE):
            self.force_overwrite_cb.setChecked(cmds.optionVar(q=PlayblastWidget.OPT_VAR_FORCE_OVERWRITE))

        if cmds.optionVar(exists=PlayblastWidget.OPT_VAR_CAMERA):
            self.camera_select_cmb.setCurrentText(cmds.optionVar(q=PlayblastWidget.OPT_VAR_CAMERA))
        if cmds.optionVar(exists=PlayblastWidget.OPT_VAR_HIDE_DEFAULT_CAMERAS):
            self.camera_select_hide_defaults_cb.setChecked(
                cmds.optionVar(q=PlayblastWidget.OPT_VAR_HIDE_DEFAULT_CAMERAS))

        if cmds.optionVar(exists=PlayblastWidget.OPT_VAR_RESOLUTION_PRESET):
            self.resolution_select_cmb.setCurrentText(cmds.optionVar(q=PlayblastWidget.OPT_VAR_RESOLUTION_PRESET))
        if self.resolution_select_cmb.currentText() == "Custom":
            if cmds.optionVar(exists=PlayblastWidget.OPT_VAR_RESOLUTION_WIDTH):
                self.resolution_width_sb.setValue(cmds.optionVar(q=PlayblastWidget.OPT_VAR_RESOLUTION_WIDTH))
            if cmds.optionVar(exists=PlayblastWidget.OPT_VAR_RESOLUTION_HEIGHT):
                self.resolution_height_sb.setValue(cmds.optionVar(q=PlayblastWidget.OPT_VAR_RESOLUTION_HEIGHT))
            self.on_resolution_changed()

        if cmds.optionVar(exists=PlayblastWidget.OPT_VAR_FRAME_RANGE_PRESET):
            self.frame_range_cmb.setCurrentText(cmds.optionVar(q=PlayblastWidget.OPT_VAR_FRAME_RANGE_PRESET))
        if self.frame_range_cmb.currentText() == "Custom":
            if cmds.optionVar(exists=PlayblastWidget.OPT_VAR_FRAME_RANGE_START):
                self.frame_range_start_sb.setValue(cmds.optionVar(q=PlayblastWidget.OPT_VAR_FRAME_RANGE_START))
            if cmds.optionVar(exists=PlayblastWidget.OPT_VAR_FRAME_RANGE_END):
                self.frame_range_end_sb.setValue(cmds.optionVar(q=PlayblastWidget.OPT_VAR_FRAME_RANGE_END))
            self.on_frame_range_changed()

        if cmds.optionVar(exists=PlayblastWidget.OPT_VAR_ENCODING_CONTAINER):
            self.encoding_container_cmb.setCurrentText(cmds.optionVar(q=PlayblastWidget.OPT_VAR_ENCODING_CONTAINER))
        if cmds.optionVar(exists=PlayblastWidget.OPT_VAR_ENCODING_VIDEO_CODEC):
            self.encoding_video_codec_cmb.setCurrentText(cmds.optionVar(q=PlayblastWidget.OPT_VAR_ENCODING_VIDEO_CODEC))

        if cmds.optionVar(exists=PlayblastWidget.OPT_VAR_H264_QUALITY) and cmds.optionVar(
                exists=PlayblastWidget.OPT_VAR_H264_PRESET):
            self._playblast.set_h264_settings(cmds.optionVar(q=PlayblastWidget.OPT_VAR_H264_QUALITY),
                                              cmds.optionVar(q=PlayblastWidget.OPT_VAR_H264_PRESET))

        if cmds.optionVar(exists=PlayblastWidget.OPT_VAR_IMAGE_QUALITY):
            self._playblast.set_image_settings(cmds.optionVar(q=PlayblastWidget.OPT_VAR_IMAGE_QUALITY))

        if cmds.optionVar(exists=PlayblastWidget.OPT_VAR_VISIBILITY_PRESET):
            self.visibility_cmb.setCurrentText(cmds.optionVar(q=PlayblastWidget.OPT_VAR_VISIBILITY_PRESET))
        if self.visibility_cmb.currentText() == "Custom":
            if cmds.optionVar(exists=PlayblastWidget.OPT_VAR_VISIBILITY_DATA):
                visibility_str_list = cmds.optionVar(q=PlayblastWidget.OPT_VAR_VISIBILITY_DATA).split()
                visibility_data = []
                for item in visibility_str_list:
                    if item:
                        visibility_data.append(bool(int(item)))

                self._playblast.set_visibility(visibility_data)

        if cmds.optionVar(exists=PlayblastWidget.OPT_VAR_OVERSCAN):
            self.overscan_cb.setChecked(cmds.optionVar(q=PlayblastWidget.OPT_VAR_OVERSCAN))
        if cmds.optionVar(exists=PlayblastWidget.OPT_VAR_ORNAMENTS):
            self.ornaments_cb.setChecked(cmds.optionVar(q=PlayblastWidget.OPT_VAR_ORNAMENTS))
        if cmds.optionVar(exists=PlayblastWidget.OPT_VAR_OFFSCREEN):
            self.offscreen_cb.setChecked(cmds.optionVar(q=PlayblastWidget.OPT_VAR_OFFSCREEN))
        if cmds.optionVar(exists=PlayblastWidget.OPT_VAR_SHOT_MASK):
            self.shot_mask_cb.setChecked(cmds.optionVar(q=PlayblastWidget.OPT_VAR_SHOT_MASK))

        if cmds.optionVar(exists=PlayblastWidget.OPT_VAR_SHOT_MASK_CROP):
            self.crop_cb.setChecked(cmds.optionVar(q=PlayblastWidget.OPT_VAR_SHOT_MASK_CROP))

        if cmds.optionVar(exists=PlayblastWidget.OPT_VAR_FIT_SHOT_MASK):
            self.fit_shot_mask_cb.setChecked(cmds.optionVar(q=PlayblastWidget.OPT_VAR_FIT_SHOT_MASK))
        if cmds.optionVar(exists=PlayblastWidget.OPT_VAR_VIEWER):
            self.viewer_cb.setChecked(cmds.optionVar(q=PlayblastWidget.OPT_VAR_VIEWER))

        if cmds.optionVar(exists=PlayblastWidget.OPT_VAR_LOG_TO_SCRIPT_EDITOR):
            self.log_to_script_editor_cb.setChecked(cmds.optionVar(q=PlayblastWidget.OPT_VAR_LOG_TO_SCRIPT_EDITOR))

        if cmds.optionVar(exists=PlayblastWidget.OPT_VAR_FIRST_HANDLE):
            self.first_handle_editor_cb.setChecked(cmds.optionVar(q=PlayblastWidget.OPT_VAR_FIRST_HANDLE))

    def append_output(self, text):
        self.output_edit.appendPlainText(text)

        cursor = self.output_edit.textCursor()
        cursor.movePosition(QtGui.QTextCursor.End)
        self.output_edit.setTextCursor(cursor)

    def reset_settings(self):
        self.output_dir_path_le.setText("")
        self.output_filename_le.setText("")
        self.force_overwrite_cb.setChecked(False)

        self.camera_select_cmb.setCurrentIndex(0)
        self.camera_select_hide_defaults_cb.setChecked(False)

        self.resolution_select_cmb.setCurrentText(Playblast.DEFAULT_RESOLUTION)

        self.frame_range_cmb.setCurrentText(Playblast.DEFAULT_FRAME_RANGE)

        self.encoding_container_cmb.setCurrentText(Playblast.DEFAULT_CONTAINER)
        self.encoding_video_codec_cmb.setCurrentText(Playblast.DEFAULT_ENCODER)

        self._playblast.set_h264_settings(Playblast.DEFAULT_H264_QUALITY, Playblast.DEFAULT_H264_PRESET)
        self._playblast.set_image_settings(Playblast.DEFAULT_IMAGE_QUALITY)

        self.visibility_cmb.setCurrentText(Playblast.DEFAULT_VISIBILITY)
        self._playblast.set_viewport_visibility

        self.ornaments_cb.setChecked(False)
        self.overscan_cb.setChecked(False)
        self.shot_mask_cb.setChecked(True)
        self.fit_shot_mask_cb.setChecked(False)
        self.viewer_cb.setChecked(True)

        self.log_to_script_editor_cb.setChecked(Playblast.DEFAULT_MAYA_LOGGING_ENABLED)

        self.save_settings()

    def log_warning(self, msg):
        self._playblast.log_warning(msg)

    def showEvent(self, e):
        self.refresh_all()

    def hideEvent(self, e):
        self.save_settings()


class ShotMask(object):
    NODE_NAME = "ShotMask"

    TRANSFORM_NODE_NAME = "PlayBlastSlate"
    SHAPE_NODE_NAME = "PlayBlastSlateShape"

    DEFAULT_BORDER_COLOR = [0.0, 0.0, 0.0, 1.0]
    # second
    IN_DEFAULT_BORDER_COLOR = [0.0, 0.0, 0.0, 1.0]

    DEFAULT_LABEL_COLOR = [1.0, 1.0, 1.0, 1.0]

    LABEL_COUNT = 10
    MIN_COUNTER_PADDING = 1
    MAX_COUNTER_PADDING = 6
    DEFAULT_COUNTER_PADDING = 4

    OPT_VAR_CAMERA_NAME = "ShotMaskCameraName"
    OPT_VAR_LABEL_TEXT = "ShotMaskLabelText"
    OPT_VAR_LABEL_FONT = "ShotMaskLabelFont"
    OPT_VAR_LABEL_COLOR = "ShotMaskLabelColor"
    OPT_VAR_LABEL_SCALE = "ShotMaskLabelScale"
    OPT_VAR_BORDER_VISIBLE = "ShotMaskBorderVisible"
    OPT_VAR_BORDER_COLOR = "ShotMaskBorderColor"
    OPT_VAR_BORDER_SCALE = "ShotMaskBorderScale"
    OPT_VAR_BORDER_AR_ENABLED = "ShotMaskBorderAREnabled"
    OPT_VAR_BORDER_AR = "ShotMaskBorderAR"

    # second
    IN_OPT_VAR_BORDER_VISIBLE = "InShotMaskBorderVisible"
    IN_OPT_VAR_BORDER_COLOR = "InShotMaskBorderColor"
    IN_OPT_VAR_BORDER_SCALE = "InShotMaskBorderScale"
    IN_OPT_VAR_BORDER_AR_ENABLED = "InShotMaskBorderAREnabled"
    IN_OPT_VAR_BORDER_AR = "InShotMaskBorderAR"

    OPT_VAR_COUNTER_PADDING = "ShotMaskCounterPadding"

    @classmethod
    def create_mask(cls):
        if not PlayBlastUtils.load_plugin():
            return

        if not cls.get_mask():
            selection = cmds.ls(sl=True)

            transform_node = cmds.createNode("transform", name=cls.TRANSFORM_NODE_NAME)
            cmds.createNode(cls.NODE_NAME, name=cls.SHAPE_NODE_NAME, parent=transform_node)

            cmds.select(selection, r=True)

        cls.refresh_mask()

    @classmethod
    def delete_mask(cls):
        mask = cls.get_mask()
        if mask:
            transform = cmds.listRelatives(mask, fullPath=True, parent=True)
            if transform:
                cmds.delete(transform)
            else:
                cmds.delete(mask)

    @classmethod
    def get_mask(cls):
        if PlayBlastUtils.is_plugin_loaded():
            nodes = cmds.ls(type=cls.NODE_NAME)
            if len(nodes) > 0:
                return nodes[0]

        return None

    @classmethod
    def set_visible_mask(cls, visible):
        mask = cls.get_mask()
        if not mask:
            return

        cmds.setAttr("{0}.topBorder".format(mask), visible)
        cmds.setAttr("{0}.bottomBorder".format(mask), visible)

    @classmethod
    def in_set_visible_mask(cls, visible):
        mask = cls.get_mask()
        if not mask:
            return
        cmds.setAttr("{0}.in_topBorder".format(mask), visible)
        cmds.setAttr("{0}.in_bottomBorder".format(mask), visible)

    @classmethod
    def refresh_mask(cls):
        mask = cls.get_mask()
        if not mask:
            return

        cmds.setAttr("{0}.camera".format(mask), cls.get_camera_name(), type="string")

        try:
            label_text = cls.get_label_text()
            cmds.setAttr("{0}.topLeftText".format(mask), label_text[0], type="string")
            cmds.setAttr("{0}.topCenterText".format(mask), label_text[1], type="string")
            cmds.setAttr("{0}.topRightText".format(mask), label_text[2], type="string")
            cmds.setAttr("{0}.bottomLeftText".format(mask), label_text[3], type="string")
            cmds.setAttr("{0}.bottomCenterText".format(mask), label_text[4], type="string")
            cmds.setAttr("{0}.bottomRightText".format(mask), label_text[5], type="string")
            cmds.setAttr("{0}.topLeftCenterText".format(mask), label_text[6], type="string")
            cmds.setAttr("{0}.topRightCenterText".format(mask), label_text[7], type="string")
            cmds.setAttr("{0}.bottomLeftCenterText".format(mask), label_text[8], type="string")
            cmds.setAttr("{0}.bottomRightCenterText".format(mask), label_text[9], type="string")
        except:
            pass

        label_color = cls.get_label_color()
        try:
            cmds.setAttr("{0}.fontName".format(mask), cls.get_label_font(), type="string")
            cmds.setAttr("{0}.fontColor".format(mask), label_color[0], label_color[1], label_color[2], type="double3")
            cmds.setAttr("{0}.fontAlpha".format(mask), label_color[3])
            cmds.setAttr("{0}.fontScale".format(mask), cls.get_label_scale())

            border_visibility = cls.get_border_visible()
            border_color = cls.get_border_color()
            cmds.setAttr("{0}.topBorder".format(mask), border_visibility[0])
            cmds.setAttr("{0}.bottomBorder".format(mask), border_visibility[1])
            cmds.setAttr("{0}.borderColor".format(mask), border_color[0], border_color[1], border_color[2], type="double3")
            cmds.setAttr("{0}.borderAlpha".format(mask), border_color[3])
            cmds.setAttr("{0}.borderScale".format(mask), cls.get_border_scale())
            cmds.setAttr("{0}.aspectRatioBorders".format(mask), cls.is_border_aspect_ratio_enabled())

            cmds.setAttr("{0}.borderAspectRatio".format(mask), cls.get_border_aspect_ratio())

            # seconde
            in_border_visibility = cls.in_get_border_visible()
            in_border_color = cls.in_get_border_color()
            cmds.setAttr("{0}.in_topBorder".format(mask), in_border_visibility[0])
            cmds.setAttr("{0}.in_bottomBorder".format(mask), in_border_visibility[1])
            cmds.setAttr("{0}.in_borderColor".format(mask), in_border_color[0], in_border_color[1], in_border_color[2],
                         type="double3")
            cmds.setAttr("{0}.in_borderAlpha".format(mask), in_border_color[3])
            cmds.setAttr("{0}.in_borderScale".format(mask), cls.in_get_border_scale())
            cmds.setAttr("{0}.in_aspectRatioBorders".format(mask), cls.in_is_border_aspect_ratio_enabled())
            cmds.setAttr("{0}.in_borderAspectRatio".format(mask), cls.in_get_border_aspect_ratio())

            cmds.setAttr("{0}.counterPadding".format(mask), cls.get_counter_padding())
        except Exception as e:
            om.MGlobal.displayWarning("[Playblast] {0}".format(e))
            pass

        cls.refresh_config(mask)

    @classmethod
    def refresh_config(cls, mask=None, widget=None):

        with open(os.path.dirname(__file__) + os.sep + 'config' + os.sep + os.environ['project_name'] + '.json',
                  'r') as f:
            config = json.load(f)

            for key, value in config.items():
                if key == 'DEFAULT_CONTAINER':
                    if not mask:
                        return value

                else:
                    if mask:
                        if type(value) == str:
                            if os.path.exists(value.rsplit('*',1)[0]):
                                PlayBlastUtils.set_logo_path(value)
                                cmds.setAttr("{0}.{1}".format(mask, key), "{logo}", type="string")
                            elif re.findall('python\(', value, re.I):
                                s_list = value.split('|')
                                if len(s_list)>1:
                                    values=[]
                                    for s in s_list:
                                        if re.findall('python\(', s, re.I):
                                            values.append(mel.eval(s))
                                        else:
                                            values.append(s)

                                    cmds.setAttr("{0}.{1}".format(mask, key), '|'.join(values),type="string")
                                else:
                                    cmds.setAttr("{0}.{1}".format(mask, key), mel.eval(value), type="string")

                            elif re.match('{output_filename}', value, re.I):
                                cmds.setAttr("{0}.{1}".format(mask, key),
                                             cls.get_out_file_name().replace('}', '').replace('{', ''), type="string")
                            else:
                                try:
                                    cmds.setAttr("{0}.{1}".format(mask, key), value, type="string")
                                except Exception as e:
                                    om.MGlobal.displayWarning("[Playblast] {0}.{1} {2}".format(mask,key,e))
                                    pass
                        try:
                            if type(value) == int:
                                cmds.setAttr("{0}.{1}".format(mask, key), value)

                            if type(value) == float:
                                cmds.setAttr("{0}.{1}".format(mask, key), value)

                            if type(value) == list:
                                cmds.setAttr("{0}.{1}".format(mask, key), value[0], value[1], value[2], typ='double3')
                        except Exception as e:
                            om.MGlobal.displayWarning("[Playblast] {0}.{1} {2}".format(mask, key, e))
                            pass

                if key == 'backGround':

                    for k, v in value.items():
                        #print(k,v)
                        try:
                            if type(v) == str:
                                cmds.setAttr("{0}.{1}".format(mask, k), v, type="string")
                                if re.findall('python', v, re.I):
                                    t_list = v.split('|')
                                    if len(t_list) > 1:
                                        #print(t_list)
                                        cmds.setAttr("{0}.{1}".format(mask, k), t_list[0] + mel.eval(t_list[1]),
                                                     type="string")
                                    else:
                                        cmds.setAttr("{0}.{1}".format(mask, k), mel.eval(v), type="string")
                                else:
                                    cmds.setAttr("{0}.{1}".format(mask, k), v, type="string")

                            if type(v) == int:
                                cmds.setAttr("{0}.{1}".format(mask, k), v)

                            if type(v) == float:
                                cmds.setAttr("{0}.{1}".format(mask, k), v)
                        except Exception as e:
                            om.MGlobal.displayWarning("[Playblast] {0}.{1} {2}".format(mask, k, e))
                            pass

    @classmethod
    def set_camera_name(cls, name):
        cmds.optionVar(sv=[cls.OPT_VAR_CAMERA_NAME, name])

    @classmethod
    def get_camera_name(cls):
        if cmds.optionVar(exists=cls.OPT_VAR_CAMERA_NAME):
            return cmds.optionVar(q=cls.OPT_VAR_CAMERA_NAME)
        else:
            return ""

    @classmethod
    def set_label_text(cls, text_array):
        array_len = len(text_array)
        if array_len != cls.LABEL_COUNT:
            om.MGlobal.displayError(
                "Failed to set label text. Invalid number of text values in array: {0} (expected 6)".format(array_len))
            return

        cmds.optionVar(sv=[cls.OPT_VAR_LABEL_TEXT, text_array[0]])
        for i in range(1, array_len):
            cmds.optionVar(sva=[cls.OPT_VAR_LABEL_TEXT, text_array[i]])

    @classmethod
    def get_label_text(cls):
        if cmds.optionVar(exists=cls.OPT_VAR_LABEL_TEXT):
            return cmds.optionVar(q=cls.OPT_VAR_LABEL_TEXT)

        return ["", "{scene}", "", "{username}", "", "{counter}"]

    @classmethod
    def get_out_file_name(cls):
        if cmds.optionVar(exists=PlayblastWidget.OPT_VAR_OUTPUT_FILENAME):
            return cmds.optionVar(q=PlayblastWidget.OPT_VAR_OUTPUT_FILENAME)

    @classmethod
    def set_label_font(cls, font):
        cmds.optionVar(sv=[cls.OPT_VAR_LABEL_FONT, font])

    @classmethod
    def get_label_font(cls):
        if cmds.optionVar(exists=cls.OPT_VAR_LABEL_FONT):
            label_font = cmds.optionVar(q=cls.OPT_VAR_LABEL_FONT)
            if label_font:
                return label_font

        if cmds.about(win=True):
            return "Times New Roman"
        elif cmds.about(mac=True):
            return "Times New Roman-Regular"
        elif cmds.about(linux=True):
            return "Courier"
        else:
            return "Times-Roman"

    @classmethod
    def set_label_color(cls, red, green, blue, alpha):
        cmds.optionVar(fv=[cls.OPT_VAR_LABEL_COLOR, red])
        cmds.optionVar(fva=[cls.OPT_VAR_LABEL_COLOR, green])
        cmds.optionVar(fva=[cls.OPT_VAR_LABEL_COLOR, blue])
        cmds.optionVar(fva=[cls.OPT_VAR_LABEL_COLOR, alpha])

    @classmethod
    def get_label_color(cls):
        if cmds.optionVar(exists=cls.OPT_VAR_LABEL_COLOR):
            return cmds.optionVar(q=cls.OPT_VAR_LABEL_COLOR)
        else:
            return cls.DEFAULT_LABEL_COLOR

    @classmethod
    def set_label_scale(cls, scale):
        cmds.optionVar(fv=[cls.OPT_VAR_LABEL_SCALE, scale])

    @classmethod
    def get_label_scale(cls):
        if cmds.optionVar(exists=cls.OPT_VAR_LABEL_SCALE):
            return cmds.optionVar(q=cls.OPT_VAR_LABEL_SCALE)
        else:
            return 1.0

    @classmethod
    def set_border_visible(cls, top, bottom):
        cmds.optionVar(iv=[cls.OPT_VAR_BORDER_VISIBLE, top])
        cmds.optionVar(iva=[cls.OPT_VAR_BORDER_VISIBLE, bottom])

    @classmethod
    def in_set_border_visible(cls, top, bottom):
        cmds.optionVar(iv=[cls.IN_OPT_VAR_BORDER_VISIBLE, top])
        cmds.optionVar(iva=[cls.IN_OPT_VAR_BORDER_VISIBLE, bottom])

    @classmethod
    def get_border_visible(cls):
        if cmds.optionVar(exists=cls.OPT_VAR_BORDER_VISIBLE):
            border_visibility = cmds.optionVar(q=cls.OPT_VAR_BORDER_VISIBLE)
            try:
                if len(border_visibility) == 2:
                    return border_visibility
            except:
                pass

        return [1, 1]

    @classmethod
    def in_get_border_visible(cls):
        if cmds.optionVar(exists=cls.IN_OPT_VAR_BORDER_VISIBLE):
            in_border_visibility = cmds.optionVar(q=cls.IN_OPT_VAR_BORDER_VISIBLE)
            try:
                if len(in_border_visibility) == 2:
                    return in_border_visibility
            except:
                pass

        return [1, 1]

    @classmethod
    def set_border_color(cls, red, green, blue, alpha):
        cmds.optionVar(fv=[cls.OPT_VAR_BORDER_COLOR, red])
        cmds.optionVar(fva=[cls.OPT_VAR_BORDER_COLOR, green])
        cmds.optionVar(fva=[cls.OPT_VAR_BORDER_COLOR, blue])
        cmds.optionVar(fva=[cls.OPT_VAR_BORDER_COLOR, alpha])

    @classmethod
    def in_set_border_color(cls, red, green, blue, alpha):
        cmds.optionVar(fv=[cls.IN_OPT_VAR_BORDER_COLOR, red])
        cmds.optionVar(fva=[cls.IN_OPT_VAR_BORDER_COLOR, green])
        cmds.optionVar(fva=[cls.IN_OPT_VAR_BORDER_COLOR, blue])
        cmds.optionVar(fva=[cls.IN_OPT_VAR_BORDER_COLOR, alpha])

    @classmethod
    def get_border_color(cls):
        if cmds.optionVar(exists=cls.OPT_VAR_BORDER_COLOR):
            return cmds.optionVar(q=cls.OPT_VAR_BORDER_COLOR)
        else:
            return cls.DEFAULT_BORDER_COLOR

    @classmethod
    def in_get_border_color(cls):
        if cmds.optionVar(exists=cls.IN_OPT_VAR_BORDER_COLOR):
            return cmds.optionVar(q=cls.IN_OPT_VAR_BORDER_COLOR)
        else:
            return cls.IN_DEFAULT_BORDER_COLOR

    @classmethod
    def set_border_scale(cls, scale):
        cmds.optionVar(fv=[cls.OPT_VAR_BORDER_SCALE, scale])

    @classmethod
    def in_set_border_scale(cls, scale):
        cmds.optionVar(fv=[cls.IN_OPT_VAR_BORDER_SCALE, scale])

    @classmethod
    def get_border_scale(cls):
        if cmds.optionVar(exists=cls.OPT_VAR_BORDER_SCALE):
            return cmds.optionVar(q=cls.OPT_VAR_BORDER_SCALE)
        else:
            return 1.0

    @classmethod
    def in_get_border_scale(cls):
        if cmds.optionVar(exists=cls.IN_OPT_VAR_BORDER_SCALE):
            return cmds.optionVar(q=cls.IN_OPT_VAR_BORDER_SCALE)
        else:
            return 1.0

    @classmethod
    def set_border_aspect_ratio_enabled(cls, enabled):
        cmds.optionVar(iv=[cls.OPT_VAR_BORDER_AR_ENABLED, enabled])

    @classmethod
    def in_set_border_aspect_ratio_enabled(cls, enabled):
        cmds.optionVar(iv=[cls.IN_OPT_VAR_BORDER_AR_ENABLED, enabled])

    @classmethod
    def is_border_aspect_ratio_enabled(cls):
        if cmds.optionVar(exists=cls.OPT_VAR_BORDER_AR_ENABLED):
            return cmds.optionVar(q=cls.OPT_VAR_BORDER_AR_ENABLED)
        else:
            return 0

    @classmethod
    def in_is_border_aspect_ratio_enabled(cls):
        if cmds.optionVar(exists=cls.IN_OPT_VAR_BORDER_AR_ENABLED):
            return cmds.optionVar(q=cls.IN_OPT_VAR_BORDER_AR_ENABLED)
        else:
            return 0

    @classmethod
    def set_border_aspect_ratin(cls, aspect_ratio):
        cmds.optionVar(fv=[cls.OPT_VAR_BORDER_AR, aspect_ratio])

    @classmethod
    def in_set_border_aspect_ratio(cls, aspect_ratio):
        cmds.optionVar(fv=[cls.IN_OPT_VAR_BORDER_AR, aspect_ratio])

    @classmethod
    def get_border_aspect_ratio(cls):
        if cmds.optionVar(exists=cls.OPT_VAR_BORDER_AR):
            return cmds.optionVar(q=cls.OPT_VAR_BORDER_AR)
        else:
            return 2.35

    @classmethod
    def in_get_border_aspect_ratio(cls):
        if cmds.optionVar(exists=cls.IN_OPT_VAR_BORDER_AR):
            return cmds.optionVar(q=cls.IN_OPT_VAR_BORDER_AR)
        else:
            return 2.35

    @classmethod
    def set_counter_padding(cls, padding):
        cmds.optionVar(iv=[cls.OPT_VAR_COUNTER_PADDING, padding])

    @classmethod
    def get_counter_padding(cls):
        if cmds.optionVar(exists=cls.OPT_VAR_COUNTER_PADDING):
            pos = cmds.optionVar(q=cls.OPT_VAR_COUNTER_PADDING)
            if pos >= cls.MIN_COUNTER_PADDING and pos <= cls.MAX_COUNTER_PADDING:
                return pos

        return cls.DEFAULT_COUNTER_PADDING

    @classmethod
    def reset_settings(cls):
        cmds.optionVar(remove=cls.OPT_VAR_BORDER_COLOR)
        cmds.optionVar(remove=cls.OPT_VAR_BORDER_SCALE)
        cmds.optionVar(remove=cls.OPT_VAR_BORDER_VISIBLE)
        cmds.optionVar(remove=cls.OPT_VAR_BORDER_AR_ENABLED)
        cmds.optionVar(remove=cls.OPT_VAR_BORDER_AR)

        # second
        cmds.optionVar(remove=cls.IN_OPT_VAR_BORDER_COLOR)
        cmds.optionVar(remove=cls.IN_OPT_VAR_BORDER_SCALE)
        cmds.optionVar(remove=cls.IN_OPT_VAR_BORDER_VISIBLE)
        cmds.optionVar(remove=cls.IN_OPT_VAR_BORDER_AR_ENABLED)
        cmds.optionVar(remove=cls.IN_OPT_VAR_BORDER_AR)

        cmds.optionVar(remove=cls.OPT_VAR_CAMERA_NAME)
        cmds.optionVar(remove=cls.OPT_VAR_COUNTER_PADDING)
        cmds.optionVar(remove=cls.OPT_VAR_LABEL_COLOR)
        cmds.optionVar(remove=cls.OPT_VAR_LABEL_FONT)
        cmds.optionVar(remove=cls.OPT_VAR_LABEL_SCALE)
        cmds.optionVar(remove=cls.OPT_VAR_LABEL_TEXT)


class ShotMaskWidget(QtWidgets.QWidget):
    LABELS = ["Top-Left", "Top-Center", "Top-Right", "Bottom-Left", "Bottom-Center", "Bottom-Right","Top-Left-Center"]

    ALL_CAMERAS = "<All Cameras>"

    collapsed_state_changed = QtCore.Signal()

    def __init__(self, parent=None):
        super(ShotMaskWidget, self).__init__(parent)

        self._camera_select_dialog = None
        self._update_mask_enabled = True

        self.create_widgets()
        self.create_layouts()
        self.create_connections()

    def create_widgets(self):
        button_width = 60
        button_height = 18
        spin_box_width = 50

        self.camera_le = QtWidgets.QLineEdit()
        self.camera_select_btn = QtWidgets.QPushButton("Select...")
        self.camera_select_btn.setFixedSize(button_width, button_height)

        self.label_line_edits = []
        for i in range(len(ShotMaskWidget.LABELS)):  # pylint: disable=W0612
            line_edit = LineEdit(LineEdit.TYPE_SHOT_MASK_LABEL)
            self.label_line_edits.append(line_edit)

        self.font_le = QtWidgets.QLineEdit()
        self.font_le.setEnabled(False)

        self.font_select_btn = QtWidgets.QPushButton("Select...")
        self.font_select_btn.setFixedSize(button_width, button_height)

        self.label_color_btn = ColorButton()

        self.label_transparency_dsb = QtWidgets.QDoubleSpinBox()
        self.label_transparency_dsb.setMinimumWidth(spin_box_width)
        self.label_transparency_dsb.setSingleStep(0.05)
        self.label_transparency_dsb.setMinimum(0.0)
        self.label_transparency_dsb.setMaximum(1.0)
        self.label_transparency_dsb.setValue(1.0)
        self.label_transparency_dsb.setDecimals(3)
        self.label_transparency_dsb.setButtonSymbols(QtWidgets.QSpinBox.NoButtons)

        self.label_scale_dsb = QtWidgets.QDoubleSpinBox()
        self.label_scale_dsb.setMinimumWidth(spin_box_width)
        self.label_scale_dsb.setSingleStep(0.05)
        self.label_scale_dsb.setMinimum(0.1)
        self.label_scale_dsb.setMaximum(2.0)
        self.label_scale_dsb.setValue(1.0)
        self.label_scale_dsb.setDecimals(3)
        self.label_scale_dsb.setButtonSymbols(QtWidgets.QSpinBox.NoButtons)

        self.top_border_cb = QtWidgets.QCheckBox("Top")
        self.top_border_cb.setChecked(True)
        self.bottom_border_cb = QtWidgets.QCheckBox("Bottom")
        self.bottom_border_cb.setChecked(True)

        self.border_color_btn = ColorButton()

        self.border_transparency_dsb = QtWidgets.QDoubleSpinBox()
        self.border_transparency_dsb.setMinimumWidth(spin_box_width)
        self.border_transparency_dsb.setSingleStep(0.05)
        self.border_transparency_dsb.setMinimum(0.0)
        self.border_transparency_dsb.setMaximum(1.0)
        self.border_transparency_dsb.setValue(1.0)
        self.border_transparency_dsb.setDecimals(3)
        self.border_transparency_dsb.setButtonSymbols(QtWidgets.QSpinBox.NoButtons)

        self.border_scale_dsb = QtWidgets.QDoubleSpinBox()
        self.border_scale_dsb.setMinimumWidth(spin_box_width)
        self.border_scale_dsb.setSingleStep(0.05)
        self.border_scale_dsb.setMinimum(0.1)
        self.border_scale_dsb.setMaximum(5.0)
        self.border_scale_dsb.setValue(1.0)
        self.border_scale_dsb.setDecimals(3)
        self.border_scale_dsb.setButtonSymbols(QtWidgets.QSpinBox.NoButtons)

        self.border_aspect_ratio_dsb = QtWidgets.QDoubleSpinBox()
        self.border_aspect_ratio_dsb.setMinimumWidth(spin_box_width)
        self.border_aspect_ratio_dsb.setSingleStep(0.05)
        self.border_aspect_ratio_dsb.setMinimum(0.1)
        self.border_aspect_ratio_dsb.setMaximum(10.0)
        self.border_aspect_ratio_dsb.setValue(2.35)
        self.border_aspect_ratio_dsb.setDecimals(3)
        self.border_aspect_ratio_dsb.setButtonSymbols(QtWidgets.QSpinBox.NoButtons)

        self.frame_border_to_aspect_ratio_cb = QtWidgets.QCheckBox("Frame border to aspect ratio")
        self.border_size_type_text = QtWidgets.QLabel("Scale")

        # second
        self.in_top_border_cb = QtWidgets.QCheckBox("In_Top")
        self.in_top_border_cb.setChecked(True)
        self.in_bottom_border_cb = QtWidgets.QCheckBox("In_Bottom")
        self.in_bottom_border_cb.setChecked(True)

        self.in_border_color_btn = ColorButton()

        self.in_border_transparency_dsb = QtWidgets.QDoubleSpinBox()
        self.in_border_transparency_dsb.setMinimumWidth(spin_box_width)
        self.in_border_transparency_dsb.setSingleStep(0.05)
        self.in_border_transparency_dsb.setMinimum(0.0)
        self.in_border_transparency_dsb.setMaximum(1.0)
        self.in_border_transparency_dsb.setValue(1.0)
        self.in_border_transparency_dsb.setDecimals(3)
        self.in_border_transparency_dsb.setButtonSymbols(QtWidgets.QSpinBox.NoButtons)

        self.in_border_scale_dsb = QtWidgets.QDoubleSpinBox()
        self.in_border_scale_dsb.setMinimumWidth(spin_box_width)
        self.in_border_scale_dsb.setSingleStep(0.05)
        self.in_border_scale_dsb.setMinimum(0.1)
        self.in_border_scale_dsb.setMaximum(5.0)
        self.in_border_scale_dsb.setValue(1.0)
        self.in_border_scale_dsb.setDecimals(3)
        self.in_border_scale_dsb.setButtonSymbols(QtWidgets.QSpinBox.NoButtons)

        self.in_border_aspect_ratio_dsb = QtWidgets.QDoubleSpinBox()
        self.in_border_aspect_ratio_dsb.setMinimumWidth(spin_box_width)
        self.in_border_aspect_ratio_dsb.setSingleStep(0.05)
        self.in_border_aspect_ratio_dsb.setMinimum(0.1)
        self.in_border_aspect_ratio_dsb.setMaximum(10.0)
        self.in_border_aspect_ratio_dsb.setValue(2.35)
        self.in_border_aspect_ratio_dsb.setDecimals(3)
        self.in_border_aspect_ratio_dsb.setButtonSymbols(QtWidgets.QSpinBox.NoButtons)

        self.in_frame_border_to_aspect_ratio_cb = QtWidgets.QCheckBox("In Frame border to aspect ratio")
        self.in_border_size_type_text = QtWidgets.QLabel("In_Scale")

        self.counter_padding_sb = QtWidgets.QSpinBox()
        self.counter_padding_sb.setMinimumWidth(spin_box_width)
        self.counter_padding_sb.setSingleStep(1)
        self.counter_padding_sb.setMinimum(1)
        self.counter_padding_sb.setMaximum(6)
        self.counter_padding_sb.setButtonSymbols(QtWidgets.QSpinBox.NoButtons)

        self.update_ui_elements()

    def create_layouts(self):
        camera_layout = QtWidgets.QHBoxLayout()
        camera_layout.setContentsMargins(4, 14, 4, 14)
        camera_layout.setSpacing(2)
        camera_layout.addWidget(self.camera_le)
        camera_layout.addWidget(self.camera_select_btn)

        camera_grp_layout = FormLayout()
        camera_grp_layout.addLayoutRow(0, "Camera", camera_layout)

        labels_layout = FormLayout()
        for i in range(len(ShotMaskWidget.LABELS)):
            labels_layout.addWidgetRow(i, ShotMaskWidget.LABELS[i], self.label_line_edits[i])

        self.labels_grp = CollapsibleGrpWidget("Labels")
        self.labels_grp.add_layout(labels_layout)

        font_layout = QtWidgets.QHBoxLayout()
        font_layout.setSpacing(2)
        font_layout.addWidget(self.font_le)
        font_layout.addWidget(self.font_select_btn)

        text_color_layout = QtWidgets.QHBoxLayout()
        text_color_layout.addWidget(self.label_color_btn)
        text_color_layout.addSpacing(4)
        text_color_layout.addWidget(QtWidgets.QLabel("Alpha"))
        text_color_layout.addWidget(self.label_transparency_dsb)
        text_color_layout.addSpacing(4)
        text_color_layout.addWidget(QtWidgets.QLabel("Scale"))
        text_color_layout.addWidget(self.label_scale_dsb)
        text_color_layout.addStretch()

        text_layout = FormLayout()
        text_layout.addLayoutRow(0, "Font", font_layout)
        text_layout.addLayoutRow(1, "Color", text_color_layout)

        self.text_grp = CollapsibleGrpWidget("Text")
        self.text_grp.add_layout(text_layout)

        border_visibility_layout = QtWidgets.QHBoxLayout()
        border_visibility_layout.addWidget(self.top_border_cb)
        border_visibility_layout.addWidget(self.bottom_border_cb)
        border_visibility_layout.addWidget(self.frame_border_to_aspect_ratio_cb)
        border_visibility_layout.addStretch()

        border_color_layout = QtWidgets.QHBoxLayout()
        border_color_layout.addWidget(self.border_color_btn)
        border_color_layout.addSpacing(4)
        border_color_layout.addWidget(QtWidgets.QLabel("Alpha"))
        border_color_layout.addWidget(self.border_transparency_dsb)
        border_color_layout.addSpacing(4)
        border_color_layout.addWidget(self.border_size_type_text)
        border_color_layout.addWidget(self.border_scale_dsb)
        border_color_layout.addWidget(self.border_aspect_ratio_dsb)
        border_color_layout.addStretch()

        borders_layout = FormLayout()
        # borders_layout.setSpacing(4)
        borders_layout.addLayoutRow(0, "", border_visibility_layout)
        borders_layout.addLayoutRow(1, "Color", border_color_layout)

        self.borders_grp = CollapsibleGrpWidget("Borders")
        self.borders_grp.add_layout(borders_layout)

        # second
        in_border_visibility_layout = QtWidgets.QHBoxLayout()
        in_border_visibility_layout.addWidget(self.in_top_border_cb)
        in_border_visibility_layout.addWidget(self.in_bottom_border_cb)
        in_border_visibility_layout.addWidget(self.in_frame_border_to_aspect_ratio_cb)
        in_border_visibility_layout.addStretch()

        in_border_color_layout = QtWidgets.QHBoxLayout()
        in_border_color_layout.addWidget(self.in_border_color_btn)
        in_border_color_layout.addSpacing(4)
        in_border_color_layout.addWidget(QtWidgets.QLabel("InAlpha"))
        in_border_color_layout.addWidget(self.in_border_transparency_dsb)
        in_border_color_layout.addSpacing(4)
        in_border_color_layout.addWidget(self.in_border_size_type_text)
        in_border_color_layout.addWidget(self.in_border_scale_dsb)
        in_border_color_layout.addWidget(self.in_border_aspect_ratio_dsb)
        in_border_color_layout.addStretch()

        in_borders_layout = FormLayout()
        # borders_layout.setSpacing(4)
        in_borders_layout.addLayoutRow(0, "", in_border_visibility_layout)
        in_borders_layout.addLayoutRow(1, "InColor", in_border_color_layout)

        self.in_borders_grp = CollapsibleGrpWidget("InBorders")
        self.in_borders_grp.add_layout(in_borders_layout)

        counter_padding_layout = QtWidgets.QHBoxLayout()
        counter_padding_layout.addWidget(self.counter_padding_sb)
        counter_padding_layout.addStretch()

        counter_layout = FormLayout()
        counter_layout.addLayoutRow(0, "Padding", counter_padding_layout)

        self.counter_grp = CollapsibleGrpWidget("Counter")
        self.counter_grp.add_layout(counter_layout)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(4, 4, 4, 4)
        main_layout.setSpacing(2)
        main_layout.addLayout(camera_grp_layout)
        main_layout.addWidget(self.labels_grp)
        main_layout.addWidget(self.text_grp)
        main_layout.addWidget(self.borders_grp)
        main_layout.addWidget(self.in_borders_grp)
        main_layout.addWidget(self.counter_grp)
        main_layout.addStretch()

    def create_connections(self):
        self.camera_le.editingFinished.connect(self.update_mask)
        self.camera_select_btn.clicked.connect(self.show_camera_select_dialog)

        for label_le in self.label_line_edits:
            label_le.editingFinished.connect(self.update_mask)

        self.font_select_btn.clicked.connect(self.show_font_select_dialog)
        self.label_color_btn.color_changed.connect(self.update_mask)  # pylint: disable=E1101
        self.label_transparency_dsb.valueChanged.connect(self.update_mask)
        self.label_scale_dsb.valueChanged.connect(self.update_mask)

        self.top_border_cb.toggled.connect(self.update_mask)
        self.bottom_border_cb.toggled.connect(self.update_mask)
        self.frame_border_to_aspect_ratio_cb.toggled.connect(self.on_border_aspect_ratio_enabled_changed)
        self.border_color_btn.color_changed.connect(self.update_mask)  # pylint: disable=E1101
        self.border_transparency_dsb.valueChanged.connect(self.update_mask)
        self.border_scale_dsb.valueChanged.connect(self.update_mask)
        self.border_aspect_ratio_dsb.editingFinished.connect(self.update_mask)

        # second
        self.in_top_border_cb.toggled.connect(self.update_mask)
        self.in_bottom_border_cb.toggled.connect(self.update_mask)
        self.in_frame_border_to_aspect_ratio_cb.toggled.connect(self.in_on_border_aspect_ratio_enabled_changed)
        self.in_border_color_btn.color_changed.connect(self.update_mask)  # pylint: disable=E1101
        self.in_border_transparency_dsb.valueChanged.connect(self.update_mask)
        self.in_border_scale_dsb.valueChanged.connect(self.update_mask)
        self.in_border_aspect_ratio_dsb.editingFinished.connect(self.update_mask)

        self.counter_padding_sb.valueChanged.connect(self.update_mask)

        self.labels_grp.collapsed_state_changed.connect(self.on_collapsed_state_changed)  # pylint: disable=E1101
        self.text_grp.collapsed_state_changed.connect(self.on_collapsed_state_changed)  # pylint: disable=E1101
        self.borders_grp.collapsed_state_changed.connect(self.on_collapsed_state_changed)  # pylint: disable=E1101
        self.in_borders_grp.collapsed_state_changed.connect(self.on_collapsed_state_changed)  # pylint: disable=E1101
        self.counter_grp.collapsed_state_changed.connect(self.on_collapsed_state_changed)  # pylint: disable=E1101

    def refresh_cameras(self):

        cameras = cmds.listCameras()
        cameras.insert(0, ShotMaskWidget.ALL_CAMERAS)

    def create_mask(self):
        ShotMask.create_mask()

    def delete_mask(self):
        ShotMask.delete_mask()

    def toggle_mask(self):
        if ShotMask.get_mask():
            self.delete_mask()
        else:
            self.create_mask()
            if cmds.optionVar(exists=PlayblastWidget.OPT_VAR_SHOT_MASK_CROP):
                state=cmds.optionVar(q=PlayblastWidget.OPT_VAR_SHOT_MASK_CROP)
                ShotMask.set_visible_mask(state)

    def update_mask(self):
        if not self._update_mask_enabled:
            return

        ShotMask.set_camera_name(self.camera_le.text())

        label_text = []
        for line_edit in self.label_line_edits:
            label_text.append(line_edit.text())
        ShotMask.set_label_text(label_text)

        ShotMask.set_label_font(self.font_le.text())
        ShotMask.set_label_scale(self.label_scale_dsb.value())

        label_color = self.label_color_btn.get_color()
        label_alpha = self.label_transparency_dsb.value()
        ShotMask.set_label_color(label_color[0], label_color[1], label_color[2], label_alpha)

        ShotMask.set_border_visible(self.top_border_cb.isChecked(), self.bottom_border_cb.isChecked())
        ShotMask.set_border_scale(self.border_scale_dsb.value())
        ShotMask.set_border_aspect_ratio_enabled(self.frame_border_to_aspect_ratio_cb.isChecked())
        ShotMask.set_border_aspect_ratio(self.border_aspect_ratio_dsb.value())

        border_color = self.border_color_btn.get_color()
        border_alpha = self.border_transparency_dsb.value()
        ShotMask.set_border_color(border_color[0], border_color[1], border_color[2], border_alpha)

        # second

        ShotMask.in_set_border_visible(self.in_top_border_cb.isChecked(), self.in_bottom_border_cb.isChecked())
        ShotMask.in_set_border_scale(self.in_border_scale_dsb.value())
        ShotMask.in_set_border_aspect_ratio_enabled(self.in_frame_border_to_aspect_ratio_cb.isChecked())
        ShotMask.in_set_border_aspect_ratio(self.in_border_aspect_ratio_dsb.value())

        in_border_color = self.in_border_color_btn.get_color()
        in_border_alpha = self.in_border_transparency_dsb.value()
        ShotMask.in_set_border_color(in_border_color[0], in_border_color[1], in_border_color[2], in_border_alpha)

        ShotMask.set_counter_padding(self.counter_padding_sb.value())

        ShotMask.refresh_mask()

    def update_ui_elements(self):
        self._update_mask_enabled = False

        camera_name = ShotMask.get_camera_name()
        if not camera_name:
            camera_name = ShotMaskWidget.ALL_CAMERAS
        self.camera_le.setText(camera_name)

        label_text = ShotMask.get_label_text()
        for i in range(len(label_text)):
            self.label_line_edits[i].setText(label_text[i])

        self.font_le.setText(ShotMask.get_label_font())
        self.label_scale_dsb.setValue(ShotMask.get_label_scale())

        label_color = ShotMask.get_label_color()
        self.label_color_btn.set_color(label_color)
        self.label_transparency_dsb.setValue(label_color[3])

        border_visible = ShotMask.get_border_visible()
        self.top_border_cb.setChecked(border_visible[0])
        self.bottom_border_cb.setChecked(border_visible[1])
        self.border_scale_dsb.setValue(ShotMask.get_border_scale())

        border_color = ShotMask.get_border_color()
        self.border_color_btn.set_color(border_color)
        self.border_transparency_dsb.setValue(border_color[3])

        self.frame_border_to_aspect_ratio_cb.setChecked(ShotMask.is_border_aspect_ratio_enabled())
        self.border_aspect_ratio_dsb.setValue(ShotMask.get_border_aspect_ratio())
        self.on_border_aspect_ratio_enabled_changed()

        # second

        in_border_visible = ShotMask.in_get_border_visible()
        self.in_top_border_cb.setChecked(in_border_visible[0])
        self.in_bottom_border_cb.setChecked(in_border_visible[1])
        self.in_border_scale_dsb.setValue(ShotMask.in_get_border_scale())

        in_border_color = ShotMask.in_get_border_color()
        self.in_border_color_btn.set_color(in_border_color)
        self.in_border_transparency_dsb.setValue(in_border_color[3])

        self.in_frame_border_to_aspect_ratio_cb.setChecked(ShotMask.in_is_border_aspect_ratio_enabled())
        self.in_border_aspect_ratio_dsb.setValue(ShotMask.in_get_border_aspect_ratio())
        self.in_on_border_aspect_ratio_enabled_changed()

        self.counter_padding_sb.setValue(ShotMask.get_counter_padding())

        self._update_mask_enabled = True

    def reset_settings(self):
        ShotMask.reset_settings()

        self.update_ui_elements()
        self.update_mask()

    def show_camera_select_dialog(self):
        if not self._camera_select_dialog:
            self._camera_select_dialog = CameraSelectDialog(self)
            self._camera_select_dialog.setWindowTitle("Shot Mask Camera")
            self._camera_select_dialog.set_camera_list_text("Select shot mask camera:")
            self._camera_select_dialog.accepted.connect(self.on_camera_select_accepted)

        self._camera_select_dialog.refresh_list(selected=[self.camera_le.text()], prepend=[ShotMaskWidget.ALL_CAMERAS])

        self._camera_select_dialog.show()

    def on_camera_select_accepted(self):
        selected = self._camera_select_dialog.get_selected()
        if selected:
            self.camera_le.setText(selected[0])

            self.update_mask()

    def on_border_aspect_ratio_enabled_changed(self):
        enabled = self.frame_border_to_aspect_ratio_cb.isChecked()
        if enabled:
            self.border_size_type_text.setText("Aspect Ratio")
        else:
            self.border_size_type_text.setText("Scale")

        self.border_aspect_ratio_dsb.setVisible(enabled)
        self.border_scale_dsb.setHidden(enabled)

        self.update_mask()

    def in_on_border_aspect_ratio_enabled_changed(self):
        enabled = self.in_frame_border_to_aspect_ratio_cb.isChecked()
        if enabled:
            self.in_border_size_type_text.setText("InAspect Ratio")
        else:
            self.in_border_size_type_text.setText("InScale")

        self.in_border_aspect_ratio_dsb.setVisible(enabled)
        self.in_border_scale_dsb.setHidden(enabled)

        self.update_mask()

    def on_collapsed_state_changed(self):
        self.collapsed_state_changed.emit()  # pylint: disable=E1101

    def get_collapsed_states(self):
        collapsed = 0
        collapsed += int(self.labels_grp.is_collapsed())
        collapsed += int(self.text_grp.is_collapsed()) << 1
        collapsed += int(self.borders_grp.is_collapsed()) << 2
        collapsed += int(self.in_borders_grp.is_collapsed()) << 2
        collapsed += int(self.counter_grp.is_collapsed()) << 3

        return collapsed

    def set_collapsed_states(self, collapsed):
        self.labels_grp.set_collapsed(collapsed & 1)
        self.text_grp.set_collapsed(collapsed & 2)
        self.borders_grp.set_collapsed(collapsed & 4)
        self.in_borders_grp.set_collapsed(collapsed & 4)
        self.counter_grp.set_collapsed(collapsed & 8)

    def show_font_select_dialog(self):
        current_font = QtGui.QFont(self.font_le.text())

        font = QtWidgets.QFontDialog.getFont(current_font, self)

        # Order of the tuple returned by getFont changed in newer versions of Qt
        if type(font[0]) == bool:
            ok = font[0]
            family = font[1].family()
        else:
            family = font[0].family()
            ok = font[1]

        if (ok):
            self.font_le.setText(family)

            self.update_mask()


class PlayBlastSettingsWidget(QtWidgets.QWidget):
    TEMP_FILE_FORMATS = [
        "movie",
        "png",
        "tga"
    ]

    shot_mask_reset = QtCore.Signal()
    playblast_reset = QtCore.Signal()

    logo_path_updated = QtCore.Signal()

    collapsed_state_changed = QtCore.Signal()

    def __init__(self, parent=None):
        super(PlayBlastSettingsWidget, self).__init__(parent)

        self.create_widgets()
        self.create_layouts()
        self.create_connections()

    def create_widgets(self):
        text = '<h3>{0}</h3>'.format(PlayBlastWidget.WINDOW_TITLE)
        text += '<h3>v{0}</h3>'.format(PlayBlastUtils.get_version())

        self.about_label = QtWidgets.QLabel(text)
        self.about_label.setOpenExternalLinks(True)
        self.about_label.setAlignment(QtCore.Qt.AlignCenter)

        self.ffmpeg_path_le = QtWidgets.QLineEdit()
        self.ffmpeg_path_le.setPlaceholderText("<path to {0}>".format(self.get_ffmpeg_executable_text()))
        self.ffmpeg_path_select_btn = QtWidgets.QPushButton("...")
        self.ffmpeg_path_select_btn.setFixedSize(24, 19)

        self.temp_dir_le = QtWidgets.QLineEdit()
        self.temp_dir_le.setPlaceholderText("<path to {temp} output directory>")
        self.temp_dir_select_btn = QtWidgets.QPushButton("...")
        self.temp_dir_select_btn.setFixedSize(24, 19)

        self.temp_file_format_cmb = QtWidgets.QComboBox()
        self.temp_file_format_cmb.addItems(self.TEMP_FILE_FORMATS)

        self.playblast_reset_btn = QtWidgets.QPushButton("Reset Playblast")
        self.playblast_reset_btn.setMinimumWidth(200)

        self.logo_path_le = QtWidgets.QLineEdit()
        self.logo_path_le.setPlaceholderText("<path to {logo} image>")
        self.logo_path_select_btn = QtWidgets.QPushButton("...")
        self.logo_path_select_btn.setFixedSize(24, 19)

        self.shot_mask_reset_btn = QtWidgets.QPushButton("Reset Shot Mask")
        self.shot_mask_reset_btn.setMinimumWidth(200)

    def create_layouts(self):
        about_layout = QtWidgets.QVBoxLayout()
        about_layout.setContentsMargins(0, 14, 0, 14)
        about_layout.addWidget(self.about_label)

        ffmpeg_path_layout = QtWidgets.QHBoxLayout()
        ffmpeg_path_layout.setSpacing(2)
        ffmpeg_path_layout.addWidget(self.ffmpeg_path_le)
        ffmpeg_path_layout.addWidget(self.ffmpeg_path_select_btn)

        temp_dir_layout = QtWidgets.QHBoxLayout()
        temp_dir_layout.setSpacing(2)
        temp_dir_layout.addWidget(self.temp_dir_le)
        temp_dir_layout.addWidget(self.temp_dir_select_btn)

        temp_format_layout = QtWidgets.QHBoxLayout()
        temp_format_layout.addWidget(self.temp_file_format_cmb)
        temp_format_layout.addStretch()

        playblast_layout = FormLayout()
        playblast_layout.addLayoutRow(0, "ffmpeg Path", ffmpeg_path_layout)
        playblast_layout.addLayoutRow(1, "Temp Dir", temp_dir_layout)
        playblast_layout.addLayoutRow(2, "Temp Format", temp_format_layout)

        playblast_reset_layout = QtWidgets.QHBoxLayout()
        playblast_reset_layout.setContentsMargins(0, 0, 0, 10)
        playblast_reset_layout.addStretch()
        playblast_reset_layout.addWidget(self.playblast_reset_btn)
        playblast_reset_layout.addStretch()

        self.playblast_grp = CollapsibleGrpWidget("Playblast")
        self.playblast_grp.add_layout(playblast_layout)
        self.playblast_grp.add_layout(playblast_reset_layout)

        logo_path_layout = QtWidgets.QHBoxLayout()
        logo_path_layout.setSpacing(2)
        logo_path_layout.addWidget(self.logo_path_le)
        logo_path_layout.addWidget(self.logo_path_select_btn)

        shot_mask_tags_layout = FormLayout()
        shot_mask_tags_layout.addLayoutRow(0, "Logo Path", logo_path_layout)

        shot_mask_reset_layout = QtWidgets.QHBoxLayout()
        shot_mask_reset_layout.setContentsMargins(0, 0, 0, 10)
        shot_mask_reset_layout.addStretch()
        shot_mask_reset_layout.addWidget(self.shot_mask_reset_btn)
        shot_mask_reset_layout.addStretch()

        self.shot_mask_grp = CollapsibleGrpWidget("Shot Mask")
        self.shot_mask_grp.add_layout(shot_mask_tags_layout)
        self.shot_mask_grp.add_layout(shot_mask_reset_layout)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addLayout(about_layout)
        main_layout.addWidget(self.playblast_grp)
        main_layout.addWidget(self.shot_mask_grp)
        main_layout.addStretch()

    def create_connections(self):
        self.ffmpeg_path_le.editingFinished.connect(self.update_ffmpeg_path)
        self.ffmpeg_path_select_btn.clicked.connect(self.open_ffmpeg_select_dialog)

        self.temp_dir_le.editingFinished.connect(self.update_temp_dir_path)
        self.temp_dir_select_btn.clicked.connect(self.open_temp_dir_select_dialog)

        self.temp_file_format_cmb.currentTextChanged.connect(self.update_temp_file_format)

        self.playblast_reset_btn.clicked.connect(self.on_reset_playblast)

        self.logo_path_le.editingFinished.connect(self.update_logo_path)
        self.logo_path_select_btn.clicked.connect(self.open_logo_select_dialog)

        self.shot_mask_reset_btn.clicked.connect(self.on_reset_shot_mask)

        self.playblast_grp.collapsed_state_changed.connect(self.on_collapsed_state_changed)  # pylint: disable=E1101
        self.shot_mask_grp.collapsed_state_changed.connect(self.on_collapsed_state_changed)  # pylint: disable=E1101

    def get_ffmpeg_executable_text(self):
        if cmds.about(win=True):
            return "ffmpeg.exe"

        return "ffmpeg executable"

    def open_ffmpeg_select_dialog(self):

        if PlayBlastUtils.is_ffmpeg_env_var_set():
            QtWidgets.QMessageBox.information(self, "Select ffmpeg Executable",
                                              "The ffmpeg path is currently set using the _FFMPEG environment variable.")
            return

        current_path = self.ffmpeg_path_le.text()

        new_path = QtWidgets.QFileDialog.getOpenFileName(self, "Select ffmpeg Executable", current_path)[0]
        if new_path and new_path != self.ffmpeg_path_le.text():
            self.ffmpeg_path_le.setText(new_path)
            self.update_ffmpeg_path()

    def update_ffmpeg_path(self):
        PlayBlastUtils.set_ffmpeg_path(self.ffmpeg_path_le.text())

    def open_temp_dir_select_dialog(self):
        if PlayBlastUtils.is_temp_output_env_var_set():
            QtWidgets.QMessageBox.information(self, "Select Temp Output Directory",
                                              "The temp output directory is currently set using the PLAYBLAST_TEMP_OUTPUT_DIR environment variable.")
            return

        current_path = self.temp_dir_le.text()

        new_path = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Temp Directory", current_path)
        if new_path and new_path != self.temp_dir_le.text():
            self.temp_dir_le.setText(new_path)
            self.update_temp_dir_path()

    def update_temp_dir_path(self):
        PlayBlastUtils.set_temp_output_dir_path(self.temp_dir_le.text())

    def update_temp_file_format(self, text):
        PlayBlastUtils.set_temp_file_format(text)

    def open_logo_select_dialog(self):

        if PlayBlastUtils.is_logo_env_var_set():
            QtWidgets.QMessageBox.information(self, "Select Logo",
                                              "The logo path is currently set using the PLAYBLAST_LOGO environment variable.")
            return

        current_path = self.logo_path_le.text()

        new_path = QtWidgets.QFileDialog.getOpenFileName(self, "Select Logo", current_path)[0]
        if new_path and new_path != self.logo_path_le.text():
            self.logo_path_le.setText(new_path)
            self.update_logo_path()

    def update_logo_path(self):
        PlayBlastUtils.set_logo_path(self.logo_path_le.text())

        self.logo_path_updated.emit()  # pylint: disable=E1101

    def on_reset_playblast(self):
        result = QtWidgets.QMessageBox.question(self, "Confirm Reset", "Restore playblast defaults?")
        if result != QtWidgets.QMessageBox.Yes:
            return

        self.playblast_reset.emit()  # pylint: disable=E1101

    def on_reset_shot_mask(self):
        result = QtWidgets.QMessageBox.question(self, "Confirm Reset", "Restore shot mask defaults?")
        if result != QtWidgets.QMessageBox.Yes:
            return

        self.shot_mask_reset.emit()  # pylint: disable=E1101

    def on_collapsed_state_changed(self):
        self.collapsed_state_changed.emit()  # pylint: disable=E1101

    def refresh_settings(self):
        self.ffmpeg_path_le.setText(PlayBlastUtils.get_ffmpeg_path())
        self.ffmpeg_path_le.setDisabled(PlayBlastUtils.is_ffmpeg_env_var_set())

        self.temp_dir_le.setText(PlayBlastUtils.get_temp_output_dir_path())
        self.temp_dir_le.setDisabled(PlayBlastUtils.is_temp_output_env_var_set())

        self.temp_file_format_cmb.setCurrentText(PlayBlastUtils.get_temp_file_format())
        self.temp_file_format_cmb.setDisabled(PlayBlastUtils.is_temp_format_env_set())

        self.logo_path_le.setText(PlayBlastUtils.get_logo_path())
        self.logo_path_le.setDisabled(PlayBlastUtils.is_logo_env_var_set())

    def get_collapsed_states(self):
        collapsed = 0
        collapsed += int(self.playblast_grp.is_collapsed())
        collapsed += int(self.shot_mask_grp.is_collapsed()) << 1

        return collapsed

    def set_collapsed_states(self, collapsed):
        self.playblast_grp.set_collapsed(collapsed & 1)
        self.shot_mask_grp.set_collapsed(collapsed & 2)

    def showEvent(self, e):
        self.refresh_settings()


class PlayBlastWidget(QtWidgets.QWidget):
    WINDOW_TITLE = "Playblast"
    UI_NAME = "PlayBlast"

    OPT_VAR_GROUP_STATE = "APGroupState"

    ui_instance = None

    @classmethod
    def display(cls):
        if cls.ui_instance:
            cls.ui_instance.show_workspace_control()
        else:
            if PlayBlastUtils.load_plugin():
                cls.ui_instance = PlayBlastWidget()

    @classmethod
    def get_workspace_control_name(cls):
        return "{0}WorkspaceControl".format(cls.UI_NAME)

    def __init__(self):
        super(PlayBlastWidget, self).__init__()

        self.setObjectName(PlayBlastWidget.UI_NAME)

        self.setMinimumWidth(400)
        self.setMinimumHeight(420)

        self._batch_playblast_dialog = None

        self.create_widgets()
        self.create_layouts()
        self.create_connections()
        self.create_workspace_control()

        self.restore_collaspsed_states()

        self.main_tab_wdg.setCurrentIndex(0)

    def create_widgets(self):
        button_width = 120
        button_height = 40

        self.playblast_wdg = PlayblastWidget()
        self.playblast_wdg.setAutoFillBackground(True)

        playblast_scroll_area = QtWidgets.QScrollArea()
        playblast_scroll_area.setFrameShape(QtWidgets.QFrame.NoFrame)
        playblast_scroll_area.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        playblast_scroll_area.setWidgetResizable(True)
        playblast_scroll_area.setWidget(self.playblast_wdg)

        self.shot_mask_wdg = ShotMaskWidget()
        self.shot_mask_wdg.setAutoFillBackground(True)

        shot_mask_scroll_area = QtWidgets.QScrollArea()
        shot_mask_scroll_area.setFrameShape(QtWidgets.QFrame.NoFrame)
        shot_mask_scroll_area.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        shot_mask_scroll_area.setWidgetResizable(True)
        shot_mask_scroll_area.setWidget(self.shot_mask_wdg)

        self.settings_wdg = PlayBlastSettingsWidget()
        self.settings_wdg.setAutoFillBackground(True)

        settings_scroll_area = QtWidgets.QScrollArea()
        settings_scroll_area.setFrameShape(QtWidgets.QFrame.NoFrame)
        settings_scroll_area.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        settings_scroll_area.setWidgetResizable(True)
        settings_scroll_area.setWidget(self.settings_wdg)

        self.main_tab_wdg = QtWidgets.QTabWidget()
        self.main_tab_wdg.setAutoFillBackground(True)
        self.main_tab_wdg.setStyleSheet("QTabWidget::pane { border: 0; }")
        self.main_tab_wdg.setMinimumHeight(200)
        self.main_tab_wdg.addTab(playblast_scroll_area, "Playblast")
        self.main_tab_wdg.addTab(shot_mask_scroll_area, "Shot Mask")
        self.main_tab_wdg.addTab(settings_scroll_area, "Settings")
        self.main_tab_wdg.removeTab(1)
        self.main_tab_wdg.removeTab(1)

        palette = self.main_tab_wdg.palette()
        palette.setColor(QtGui.QPalette.Window, QtWidgets.QWidget().palette().color(QtGui.QPalette.Midlight))
        self.main_tab_wdg.setPalette(palette)

        self.toggle_mask_btn = QtWidgets.QPushButton("Shot Info")
        self.toggle_mask_btn.setFixedSize(button_width, button_height)

        self.playblast_btn = QtWidgets.QPushButton("Playblast")
        self.playblast_btn.setMinimumSize(button_width, button_height)

        self.batch_playblast_btn = QtWidgets.QPushButton("...")
        self.batch_playblast_btn.setFixedSize(40, button_height)

        font = self.toggle_mask_btn.font()
        font.setPointSize(10)
        font.setBold(True)
        self.toggle_mask_btn.setFont(font)
        self.playblast_btn.setFont(font)

        pal = self.toggle_mask_btn.palette()
        pal.setColor(QtGui.QPalette.Button, QtGui.QColor(QtCore.Qt.darkCyan).darker())
        self.toggle_mask_btn.setPalette(pal)

        pal.setColor(QtGui.QPalette.Button, QtGui.QColor(QtCore.Qt.darkGreen).darker())
        self.playblast_btn.setPalette(pal)
        self.batch_playblast_btn.setPalette(pal)

    def create_layouts(self):

        button_layout = QtWidgets.QHBoxLayout()
        button_layout.setContentsMargins(0, 10, 0, 0)
        button_layout.addWidget(self.toggle_mask_btn)
        button_layout.addWidget(self.playblast_btn)
        button_layout.addWidget(self.batch_playblast_btn)

        status_bar_layout = QtWidgets.QHBoxLayout()
        status_bar_layout.setContentsMargins(4, 6, 4, 0)
        status_bar_layout.addStretch()
        status_bar_layout.addWidget(QtWidgets.QLabel("v{0}".format(PlayBlastUtils.get_version())))

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(6, 6, 6, 0)
        main_layout.setSpacing(2)
        main_layout.addWidget(self.main_tab_wdg)
        main_layout.addLayout(button_layout)
        main_layout.addLayout(status_bar_layout)

    def create_connections(self):
        self.settings_wdg.playblast_reset.connect(self.playblast_wdg.reset_settings)  # pylint: disable=E1101
        self.settings_wdg.logo_path_updated.connect(self.shot_mask_wdg.update_mask)  # pylint: disable=E1101
        self.settings_wdg.shot_mask_reset.connect(self.shot_mask_wdg.reset_settings)  # pylint: disable=E1101

        self.playblast_wdg.collapsed_state_changed.connect(self.on_collapsed_state_changed)  # pylint: disable=E1101
        self.shot_mask_wdg.collapsed_state_changed.connect(self.on_collapsed_state_changed)  # pylint: disable=E1101
        self.settings_wdg.collapsed_state_changed.connect(self.on_collapsed_state_changed)  # pylint: disable=E1101

        self.toggle_mask_btn.clicked.connect(self.shot_mask_wdg.toggle_mask)
        self.playblast_btn.clicked.connect(self.playblast_wdg.do_playblast)
        self.batch_playblast_btn.clicked.connect(self.show_batch_playblast_dialog)

    def create_workspace_control(self):
        self.workspace_control_instance = WorkspaceControl(self.get_workspace_control_name())
        if self.workspace_control_instance.exists():
            self.workspace_control_instance.restore(self)
        else:
            self.workspace_control_instance.create(self.WINDOW_TITLE, self,
                                                   ui_script="import core.ani.play_blast.play_blast as pl;pl.PlayBlastWidget.display()")

    def show_batch_playblast_dialog(self):
        if not self._batch_playblast_dialog:
            self._batch_playblast_dialog = CameraSelectDialog(self)
            self._batch_playblast_dialog.setWindowTitle("Batch Playblast")
            self._batch_playblast_dialog.set_multi_select_enabled(True)
            self._batch_playblast_dialog.set_camera_list_text("Select one or more cameras:")
            self._batch_playblast_dialog.set_select_btn_text("Playblast")
            self._batch_playblast_dialog.accepted.connect(self.on_batch_playblast_accepted)

            selected = []
        else:
            selected = self._batch_playblast_dialog.get_selected()

        self._batch_playblast_dialog.refresh_list(selected=selected)

        self._batch_playblast_dialog.show()

    def on_batch_playblast_accepted(self):
        batch_cameras = self._batch_playblast_dialog.get_selected()

        if batch_cameras:
            self.playblast_wdg.do_playblast(batch_cameras)
        else:
            self.playblast_wdg.log_warning("No cameras selected for batch playblast.")

    def on_collapsed_state_changed(self):
        cmds.optionVar(iv=[PlayBlastWidget.OPT_VAR_GROUP_STATE, self.playblast_wdg.get_collapsed_states()])
        cmds.optionVar(iva=[PlayBlastWidget.OPT_VAR_GROUP_STATE, self.shot_mask_wdg.get_collapsed_states()])
        cmds.optionVar(iva=[PlayBlastWidget.OPT_VAR_GROUP_STATE, self.settings_wdg.get_collapsed_states()])

    def restore_collaspsed_states(self):
        if cmds.optionVar(exists=PlayBlastWidget.OPT_VAR_GROUP_STATE):
            collasped_states = cmds.optionVar(q=PlayBlastWidget.OPT_VAR_GROUP_STATE)

            self.playblast_wdg.set_collapsed_states(collasped_states[0])
            self.shot_mask_wdg.set_collapsed_states(collasped_states[1])
            self.settings_wdg.set_collapsed_states(collasped_states[2])

    def show_workspace_control(self):
        self.workspace_control_instance.set_visible(True)

    def keyPressEvent(self, e):
        pass

    def event(self, e):
        if e.type() == QtCore.QEvent.WindowActivate:
            if self.playblast_wdg.isVisible():
                self.playblast_wdg.refresh_all()

        elif e.type() == QtCore.QEvent.WindowDeactivate:
            if self.playblast_wdg.isVisible():
                self.playblast_wdg.save_settings()

        return super(PlayBlastWidget, self).event(e)


if __name__ == "__main__":

    if PlayBlastUtils.load_plugin():
        workspace_control_name = PlayBlastWidget.get_workspace_control_name()
        if cmds.window(workspace_control_name, exists=True):
            cmds.deleteUI(workspace_control_name)

        zap_test_ui = PlayBlastWidget()
