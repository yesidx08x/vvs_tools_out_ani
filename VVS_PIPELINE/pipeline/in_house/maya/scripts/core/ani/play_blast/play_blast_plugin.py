import datetime
import json
import getpass
import os
import sys
import re
import math

import maya.api.OpenMaya as om
import maya.api.OpenMayaRender as omr
import maya.api.OpenMayaUI as omui

import maya.cmds as cmds
import maya.mel as mel

from play_blast_presets import PlayBlastCustomPresets
import comp_first_frame


def maya_useNewAPI():
    pass


class PlayBlastCmd(om.MPxCommand):
    COMMAND_NAME = "PlayBlastSlate"

    PLUG_IN_VERSION = "1.0.0"

    FFMPEG_PATH_ENV_VAR = "_FFMPEG"
    TEMP_OUTPUT_DIR_ENV_VAR = "PLAYBLAST_TEMP_OUTPUT_DIR"
    TEMP_FILE_FORMAT_ENV_VAR = "PLAYBLAST_TEMP_FILE_FORMAT"
    LOGO_PATH_ENV_VAR = "PLAYBLAST_LOGO"

    FFMPEG_PATH_OPTION_VAR = "PlayblastFFmpegPath"
    TEMP_OUTPUT_DIR_OPTION_VAR = "PlayblastTempOutputPath"
    TEMP_FILE_FORMAT_OPTION_VAR = "PlayblastTempFileFormat"
    LOGO_PATH_OPTION_VAR = "ShotMaskLogoPath"

    FFMPEG_PATH_FLAG = ["-fp", "-ffmpegPath", om.MSyntax.kString]
    FFMPEG_ENV_VAR_FLAG = ["-fev", "-ffmpegEnvVar"]

    TEMP_OUTPUT_DIR_FLAG = ["-tp", "-tempOutputPath", om.MSyntax.kString]
    TEMP_OUTPUT_ENV_VAR_FLAG = ["-tev", "-tempOutputEnvVar"]

    TEMP_FILE_FORMAT_FLAG = ["-tf", "-tempFileFormat", om.MSyntax.kString]
    TEMP_FILE_FORMAT_ENV_VAR_FLAG = ["-tfe", "-tempFileFormatEnvVar"]

    LOGO_PATH_FLAG = ["-lp", "-logoPath", om.MSyntax.kString]

    LOGO_PATH_ENV_VAR_FLAG = ["-lev", "logoEnvVar"]

    VERSION_FLAG = ["-v", "-version"]

    TEMP_FILE_FORMATS = [
        "movie",
        "png",
        "tga"
    ]

    def __init__(self):
        """
        """
        super(PlayBlastCmd, self).__init__()

        self.undoable = False

        self.str_values = []

    def doIt(self, arg_list):
        """
        """
        try:
            arg_db = om.MArgDatabase(self.syntax(), arg_list)
        except:
            self.log_error("Error parsing arguments")
            raise

        self.edit = arg_db.isEdit
        self.query = arg_db.isQuery

        self.ffmpeg_path = arg_db.isFlagSet(PlayBlastCmd.FFMPEG_PATH_FLAG[0])
        if self.ffmpeg_path:
            if self.edit:
                self.str_values.append(arg_db.flagArgumentString(PlayBlastCmd.FFMPEG_PATH_FLAG[0], 0))

        self.ffmpeg_env_var = arg_db.isFlagSet(PlayBlastCmd.FFMPEG_ENV_VAR_FLAG[0])

        self.temp_output_dir_path = arg_db.isFlagSet(PlayBlastCmd.TEMP_OUTPUT_DIR_FLAG[0])
        if self.temp_output_dir_path:
            if self.edit:
                self.str_values.append(arg_db.flagArgumentString(PlayBlastCmd.TEMP_OUTPUT_DIR_FLAG[0], 0))

        self.temp_output_env_var = arg_db.isFlagSet(PlayBlastCmd.TEMP_OUTPUT_ENV_VAR_FLAG[0])

        self.temp_file_format = arg_db.isFlagSet(PlayBlastCmd.TEMP_FILE_FORMAT_FLAG[0])
        if self.temp_file_format:
            if self.edit:
                self.str_values.append(arg_db.flagArgumentString(PlayBlastCmd.TEMP_FILE_FORMAT_FLAG[0], 0))

        self.temp_file_format_env_var = arg_db.isFlagSet(PlayBlastCmd.TEMP_FILE_FORMAT_ENV_VAR_FLAG[0])

        self.logo_path = arg_db.isFlagSet(PlayBlastCmd.LOGO_PATH_FLAG[0])
        if self.logo_path:
            if self.edit:
                self.str_values.append(arg_db.flagArgumentString(PlayBlastCmd.LOGO_PATH_FLAG[0], 0))

        self.logo_path_env_var = arg_db.isFlagSet(PlayBlastCmd.LOGO_PATH_ENV_VAR_FLAG[0])

        self.version = arg_db.isFlagSet(PlayBlastCmd.VERSION_FLAG[0])

        self.redoIt()

    def redoIt(self):
        """
        """
        if self.ffmpeg_path:
            if self.edit:
                self.set_ffmpeg_path()
            elif self.query:
                self.get_ffmpeg_path()

        elif self.ffmpeg_env_var:
            self.is_ffmpeg_env_var_set()

        elif self.temp_output_dir_path:
            if self.edit:
                self.set_temp_output_dir_path()
            elif self.query:
                self.get_temp_output_dir_path()

        elif self.temp_output_env_var:
            self.is_temp_output_env_var_set()

        elif self.temp_file_format:
            if self.edit:
                self.set_temp_file_format()
            elif self.query:
                self.get_temp_file_format()

        elif self.temp_file_format_env_var:
            self.is_temp_file_format_env_var_set()

        elif self.logo_path:
            if self.edit:
                self.set_logo_path()
            elif self.query:
                self.get_logo_path()

        elif self.logo_path_env_var:
            self.is_logo_path_env_var_set()

        elif self.version:
            self.get_version()

    def isUndoable(self):
        """
        """
        return self.undoable

    def get_ffmpeg_path(self):
        """
        """
        self.setResult(
            PlayBlastCmd.resolve_env_var(PlayBlastCmd.FFMPEG_PATH_ENV_VAR, PlayBlastCmd.FFMPEG_PATH_OPTION_VAR))

    def set_ffmpeg_path(self):
        """
        """
        PlayBlastCmd.set_opt_var_str(PlayBlastCmd.FFMPEG_PATH_OPTION_VAR, self.str_values[0])

    def is_ffmpeg_env_var_set(self):
        """
        """
        self.setResult(PlayBlastCmd.is_env_var_set(PlayBlastCmd.FFMPEG_PATH_ENV_VAR))

    def get_temp_output_dir_path(self):
        """
        """
        self.setResult(
            PlayBlastCmd.resolve_env_var(PlayBlastCmd.TEMP_OUTPUT_DIR_ENV_VAR, PlayBlastCmd.TEMP_OUTPUT_DIR_OPTION_VAR))

    def set_temp_output_dir_path(self):
        """
        """
        PlayBlastCmd.set_opt_var_str(PlayBlastCmd.TEMP_OUTPUT_DIR_OPTION_VAR, self.str_values[0])

    def is_temp_output_env_var_set(self):
        """
        """
        self.setResult(PlayBlastCmd.is_env_var_set(PlayBlastCmd.TEMP_OUTPUT_DIR_ENV_VAR))

    def get_temp_file_format(self):
        """
        """
        temp_file_format = PlayBlastCmd.resolve_env_var(PlayBlastCmd.TEMP_FILE_FORMAT_ENV_VAR,
                                                        PlayBlastCmd.TEMP_FILE_FORMAT_OPTION_VAR)

        if temp_file_format not in PlayBlastCmd.TEMP_FILE_FORMATS:
            temp_file_format = "png"

        self.setResult(temp_file_format)

    def set_temp_file_format(self):
        if self.str_values[0] not in PlayBlastCmd.TEMP_FILE_FORMATS:
            PlayBlastCmd.log_error(
                "Invalid temp file format. Expected one of: {0}".format(PlayBlastCmd.TEMP_FILE_FORMATS))

        PlayBlastCmd.set_opt_var_str(PlayBlastCmd.TEMP_FILE_FORMAT_OPTION_VAR, self.str_values[0])

    def is_temp_file_format_env_var_set(self):
        self.setResult(PlayBlastCmd.is_env_var_set(PlayBlastCmd.TEMP_FILE_FORMAT_ENV_VAR))

    def get_logo_path(self):
        """
        """
        self.setResult(PlayBlastCmd.resolve_env_var(PlayBlastCmd.LOGO_PATH_ENV_VAR, PlayBlastCmd.LOGO_PATH_OPTION_VAR))

    def set_logo_path(self):
        """
        """
        PlayBlastCmd.set_opt_var_str(PlayBlastCmd.LOGO_PATH_OPTION_VAR, self.str_values[0])

    def is_logo_path_env_var_set(self):
        """
        """
        self.setResult(PlayBlastCmd.is_env_var_set(PlayBlastCmd.LOGO_PATH_ENV_VAR))

    def get_version(self):
        self.setResult(PlayBlastCmd.PLUG_IN_VERSION)

    @classmethod
    def is_env_var_set(cls, name):
        return name in os.environ.keys()

    @classmethod
    def get_env_var_value(cls, name):
        return os.environ.get(name)

    @classmethod
    def get_opt_var_str(cls, name):
        if cmds.optionVar(exists=name):
            return cmds.optionVar(q=name)

        return ""

    @classmethod
    def set_opt_var_str(cls, name, value):
        cmds.optionVar(sv=(name, value))

    @classmethod
    def remove_option_var(cls, name):
        cmds.optionVar(remove=name)

    @classmethod
    def resolve_env_var(cls, env_var_name, opt_var_name):
        if cls.is_env_var_set(env_var_name):
            return cls.get_env_var_value(env_var_name)

        return cls.get_opt_var_str(opt_var_name)

    @classmethod
    def log_error(cls, msg):
        om.MGlobal.displayError("[PlayBlastSlate] {0}".format(msg))

    @classmethod
    def creator(cls):
        """
        """
        return PlayBlastCmd()

    @classmethod
    def create_syntax(cls):
        """
        """
        syntax = om.MSyntax()

        syntax.enableEdit = True
        syntax.enableQuery = True

        syntax.addFlag(*cls.FFMPEG_PATH_FLAG)
        syntax.addFlag(*cls.FFMPEG_ENV_VAR_FLAG)
        syntax.addFlag(*cls.TEMP_OUTPUT_DIR_FLAG)
        syntax.addFlag(*cls.TEMP_OUTPUT_ENV_VAR_FLAG)
        syntax.addFlag(*cls.TEMP_FILE_FORMAT_FLAG)
        syntax.addFlag(*cls.TEMP_FILE_FORMAT_ENV_VAR_FLAG)
        syntax.addFlag(*cls.LOGO_PATH_FLAG)
        syntax.addFlag(*cls.LOGO_PATH_ENV_VAR_FLAG)
        syntax.addFlag(*cls.VERSION_FLAG)

        return syntax


class MaskLocator(omui.MPxLocatorNode):
    """
    """

    NAME = "ShotMask"
    TYPE_ID = om.MTypeId(0x0011A888)
    DRAW_DB_CLASSIFICATION = "drawdb/geometry/ShotMask"
    DRAW_REGISTRANT_ID = "MaskLocator"

    TEXT_ATTRS = ["topLeftText", "tlt", "topCenterText", "tct", "topRightText", "trt",
                  "bottomLeftText", "blt", "bottomCenterText", "bct", "bottomRightText", "brt", "topLeftCenterText",
                  "tlct", "topRightCenterText", "trct","bottomLeftCenterText", "blct","bottomRightCenterText", "brct"]


    def __init__(self):
        """
        """
        super(MaskLocator, self).__init__()

    def postConstructor(self):
        """
        """
        node_fn = om.MFnDependencyNode(self.thisMObject())

        node_fn.findPlug("castsShadows", False).setBool(False)
        node_fn.findPlug("receiveShadows", False).setBool(False)
        node_fn.findPlug("motionBlur", False).setBool(False)

    def excludeAsLocator(self):
        """
        """
        return False

    @classmethod
    def creator(cls):
        """
        """
        return MaskLocator()

    @classmethod
    def initialize(cls):
        """
        """
        numeric_attr = om.MFnNumericAttribute()
        typed_attr = om.MFnTypedAttribute()
        stringData = om.MFnStringData()


        obj = stringData.create("")
        camera_name = typed_attr.create("camera", "cam", om.MFnData.kString, obj)
        cls.update_attr_properties(typed_attr)
        MaskLocator.addAttribute(camera_name)

        for i in range(0, len(cls.TEXT_ATTRS), 2):
            obj = stringData.create("Position {0}".format(str(i / 2 + 1).zfill(2)))
            position = typed_attr.create(cls.TEXT_ATTRS[i], cls.TEXT_ATTRS[i + 1], om.MFnData.kString, obj)
            cls.update_attr_properties(typed_attr)
            MaskLocator.addAttribute(position)

        text_padding = numeric_attr.create("textPadding", "tp", om.MFnNumericData.kShort, 10)
        cls.update_attr_properties(numeric_attr)
        numeric_attr.setMin(0)
        numeric_attr.setMax(50)
        MaskLocator.addAttribute(text_padding)

        obj = stringData.create("Consolas")
        font_name = typed_attr.create("fontName", "fn", om.MFnData.kString, obj)
        cls.update_attr_properties(typed_attr)
        MaskLocator.addAttribute(font_name)

        obj = stringData.create("Bold")
        font_weight = typed_attr.create("fontWeight", "fw", om.MFnData.kString, obj)
        cls.update_attr_properties(typed_attr)
        MaskLocator.addAttribute(font_weight)

        font_color = numeric_attr.createColor("fontColor", "fc")
        cls.update_attr_properties(numeric_attr)
        numeric_attr.default = (1.0, 1.0, 1.0)
        MaskLocator.addAttribute(font_color)

        font_alpha = numeric_attr.create("fontAlpha", "fa", om.MFnNumericData.kFloat, 1.0)
        cls.update_attr_properties(numeric_attr)
        numeric_attr.setMin(0.0)
        numeric_attr.setMax(1.0)
        MaskLocator.addAttribute(font_alpha)

        font_scale = numeric_attr.create("fontScale", "fs", om.MFnNumericData.kFloat, 1.0)
        cls.update_attr_properties(numeric_attr)
        numeric_attr.setMin(0.1)
        numeric_attr.setMax(2.0)
        MaskLocator.addAttribute(font_scale)

        image_scale = numeric_attr.create("imageScale", "is", om.MFnNumericData.kFloat, 1.0)
        cls.update_attr_properties(numeric_attr)
        numeric_attr.setMin(0.1)
        numeric_attr.setMax(2.0)
        MaskLocator.addAttribute(image_scale)

        top_border = numeric_attr.create("topBorder", "tbd", om.MFnNumericData.kBoolean, True)
        cls.update_attr_properties(numeric_attr)
        MaskLocator.addAttribute(top_border)

        bottom_border = numeric_attr.create("bottomBorder", "bbd", om.MFnNumericData.kBoolean, True)
        cls.update_attr_properties(numeric_attr)
        MaskLocator.addAttribute(bottom_border)

        border_color = numeric_attr.createColor("borderColor", "bc")
        cls.update_attr_properties(numeric_attr)
        numeric_attr.default = (0.0, 0.0, 0.0)
        MaskLocator.addAttribute(border_color)

        border_alpha = numeric_attr.create("borderAlpha", "ba", om.MFnNumericData.kFloat, 1.0)
        cls.update_attr_properties(numeric_attr)
        numeric_attr.setMin(0.0)
        numeric_attr.setMax(1.0)
        MaskLocator.addAttribute(border_alpha)

        border_scale = numeric_attr.create("borderScale", "bs", om.MFnNumericData.kFloat, 1.0)
        cls.update_attr_properties(numeric_attr)
        numeric_attr.setMin(0.5)
        numeric_attr.setMax(5.0)
        MaskLocator.addAttribute(border_scale)

        border_aspect_ratio_enabled = numeric_attr.create("aspectRatioBorders", "arb", om.MFnNumericData.kBoolean,
                                                          False)
        cls.update_attr_properties(numeric_attr)
        MaskLocator.addAttribute(border_aspect_ratio_enabled)

        border_aspect_ratio = numeric_attr.create("borderAspectRatio", "bar", om.MFnNumericData.kFloat, 2.35)
        cls.update_attr_properties(numeric_attr)
        numeric_attr.setMin(0.1)
        numeric_attr.setMax(10.0)
        MaskLocator.addAttribute(border_aspect_ratio)

        # second border
        in_top_border = numeric_attr.create("in_topBorder", "in_tbd", om.MFnNumericData.kBoolean, True)
        cls.update_attr_properties(numeric_attr)
        MaskLocator.addAttribute(in_top_border)

        in_bottom_border = numeric_attr.create("in_bottomBorder", "in_bbd", om.MFnNumericData.kBoolean, True)
        cls.update_attr_properties(numeric_attr)
        MaskLocator.addAttribute(in_bottom_border)

        in_border_color = numeric_attr.createColor("in_borderColor", "in_bc")
        cls.update_attr_properties(numeric_attr)
        numeric_attr.default = (0.0, 0.0, 0.0)
        MaskLocator.addAttribute(in_border_color)

        in_border_alpha = numeric_attr.create("in_borderAlpha", "in_ba", om.MFnNumericData.kFloat, 1.0)
        cls.update_attr_properties(numeric_attr)
        numeric_attr.setMin(0.0)
        numeric_attr.setMax(1.0)
        MaskLocator.addAttribute(in_border_alpha)

        in_border_scale = numeric_attr.create("in_borderScale", "in_bs", om.MFnNumericData.kFloat, 1.0)
        cls.update_attr_properties(numeric_attr)
        numeric_attr.setMin(0.5)
        numeric_attr.setMax(5.0)
        MaskLocator.addAttribute(in_border_scale)

        in_border_aspect_ratio_enabled = numeric_attr.create("in_aspectRatioBorders", "in_arb",
                                                             om.MFnNumericData.kBoolean,
                                                             False)
        cls.update_attr_properties(numeric_attr)
        MaskLocator.addAttribute(in_border_aspect_ratio_enabled)

        in_border_aspect_ratio = numeric_attr.create("in_borderAspectRatio", "in_bar", om.MFnNumericData.kFloat, 2.35)
        cls.update_attr_properties(numeric_attr)
        numeric_attr.setMin(0.1)
        numeric_attr.setMax(10.0)
        MaskLocator.addAttribute(in_border_aspect_ratio)

        border_mode = numeric_attr.create("borderMode", "bm", om.MFnNumericData.kShort, 2)
        cls.update_attr_properties(numeric_attr)
        numeric_attr.setMin(0)
        numeric_attr.setMax(2)
        MaskLocator.addAttribute(border_mode)

        border_line_width = numeric_attr.create("borderLineWidth", "blw", om.MFnNumericData.kShort, 1)
        cls.update_attr_properties(numeric_attr)
        numeric_attr.setMin(0)
        numeric_attr.setMax(5.0)
        MaskLocator.addAttribute(border_line_width)

        border_line_color = numeric_attr.createColor("borderLineColor", "blc")
        cls.update_attr_properties(numeric_attr)
        numeric_attr.default = (0.0, 0.0, 0.0)
        MaskLocator.addAttribute(border_line_color)

        line_alpha = numeric_attr.create("borderLineAlpha", "la", om.MFnNumericData.kFloat, 1.0)
        cls.update_attr_properties(numeric_attr)
        numeric_attr.setMin(0.0)
        numeric_attr.setMax(1.0)
        MaskLocator.addAttribute(line_alpha)

        counter_padding = numeric_attr.create("counterPadding", "cpd", om.MFnNumericData.kShort, 4)
        cls.update_attr_properties(numeric_attr)
        numeric_attr.setMin(1)
        numeric_attr.setMax(6)
        MaskLocator.addAttribute(counter_padding)

        # background
        obj = stringData.create("")
        back_image_path = typed_attr.create("imagePath", "bg", om.MFnData.kString, obj)
        cls.update_attr_properties(typed_attr)
        MaskLocator.addAttribute(back_image_path)

        obj = stringData.create("")
        back_title = typed_attr.create("title", "bt", om.MFnData.kString, obj)
        cls.update_attr_properties(typed_attr)
        MaskLocator.addAttribute(back_title)

        obj = stringData.create("")
        back_frame = typed_attr.create("frame", "bf", om.MFnData.kString, obj)
        cls.update_attr_properties(typed_attr)
        MaskLocator.addAttribute(back_frame)

        first_frame = numeric_attr.create("firstFrame", "ff", om.MFnNumericData.kShort, 1)
        cls.update_attr_properties(numeric_attr)
        numeric_attr.setMin(-10000)
        numeric_attr.setMax(10000)
        MaskLocator.addAttribute(first_frame)

        title_size = numeric_attr.create("titleSize", "tis", om.MFnNumericData.kShort, 1)
        cls.update_attr_properties(numeric_attr)
        numeric_attr.setMin(1)
        numeric_attr.setMax(500)
        MaskLocator.addAttribute(title_size)

        text_size = numeric_attr.create("textSize", "tes", om.MFnNumericData.kShort, 1)
        cls.update_attr_properties(numeric_attr)
        numeric_attr.setMin(1)
        numeric_attr.setMax(500)
        MaskLocator.addAttribute(text_size)

        space = numeric_attr.create("space", "sp", om.MFnNumericData.kShort, 20)
        cls.update_attr_properties(numeric_attr)
        numeric_attr.setMin(1)
        numeric_attr.setMax(500)
        MaskLocator.addAttribute(space)

        obj = stringData.create("")
        back_date = typed_attr.create("date", "bd", om.MFnData.kString, obj)
        cls.update_attr_properties(typed_attr)
        MaskLocator.addAttribute(back_date)

        x_pos = numeric_attr.create("xPos", "xp", om.MFnNumericData.kShort, 1)
        cls.update_attr_properties(numeric_attr)
        numeric_attr.setMin(-10000)
        numeric_attr.setMax(10000)
        MaskLocator.addAttribute(x_pos)

        y_pos = numeric_attr.create("yPos", "yp", om.MFnNumericData.kShort, 1)
        cls.update_attr_properties(numeric_attr)
        numeric_attr.setMin(-10000)
        numeric_attr.setMax(10000)
        MaskLocator.addAttribute(y_pos)

        obj = stringData.create("")
        shot_name = typed_attr.create("shotName", "sn", om.MFnData.kString, obj)
        cls.update_attr_properties(typed_attr)
        MaskLocator.addAttribute(shot_name)

        obj = stringData.create("")
        descrption = typed_attr.create("descrption", "dp", om.MFnData.kString, obj)
        cls.update_attr_properties(typed_attr)
        MaskLocator.addAttribute(descrption)

        first_handle = numeric_attr.create("firstHandle", "fh", om.MFnNumericData.kBoolean, True)
        cls.update_attr_properties(numeric_attr)
        MaskLocator.addAttribute(first_handle)

        obj = stringData.create("")
        first_frame_image = typed_attr.create("firstFrameImage", "ffi", om.MFnData.kString, obj)
        cls.update_attr_properties(typed_attr)
        MaskLocator.addAttribute(first_frame_image)

        x_pos_thumb = numeric_attr.create("xPosThumb", "xpt", om.MFnNumericData.kShort, 1)
        cls.update_attr_properties(numeric_attr)
        numeric_attr.setMin(-10000)
        numeric_attr.setMax(10000)
        MaskLocator.addAttribute(x_pos_thumb)

        y_pos_thumb = numeric_attr.create("yPosThumb", "ypt", om.MFnNumericData.kShort, 1)
        cls.update_attr_properties(numeric_attr)
        numeric_attr.setMin(-10000)
        numeric_attr.setMax(10000)
        MaskLocator.addAttribute(y_pos_thumb)

    @classmethod
    def update_attr_properties(cls, attr):
        attr.writable = True
        attr.storable = True
        if attr.type() == om.MFn.kNumericAttribute:
            attr.keyable = True


class ShotMaskData(om.MUserData):
    """
    """

    def __init__(self):
        """
        """
        super(ShotMaskData, self).__init__(False)  # don't delete after draw

        self.parsed_fields = []

        self.current_time = 0
        self.start_time = 0
        self.end_time = 0
        self.counter_padding = 4

        self.font_color = om.MColor((1.0, 1.0, 1.0))
        self.font_scale = 1.0
        self.image_scale = 1.0
        self.text_padding = 10

        self.top_border = True
        self.bottom_border = True
        self.border_color = om.MColor((0.0, 0.0, 0.0))

        # sconder border
        self.in_top_border = True
        self.in_bottom_border = True
        self.in_border_color = om.MColor((0.0, 0.0, 0.0))

        self.border_mode = 2
        self.border_line_width = 1
        self.border_line_color = om.MColor((0.0, 0.0, 0.0))

        self.vp_width = 0
        self.vp_height = 0

        self.mask_width = 0
        self.mask_height = 0
        self.in_mask_height = 0


class ShotMaskDrawOverride(omr.MPxDrawOverride):
    """
    """

    NAME = "play_blast_draw_override"

    def __init__(self, obj):
        """
        """
        super(ShotMaskDrawOverride, self).__init__(obj, ShotMaskDrawOverride.draw)

    def supportedDrawAPIs(self):
        """
        """
        return (omr.MRenderer.kAllDevices)

    def hasUIDrawables(self):
        """
        """
        return True

    def prepareForDraw(self, obj_path, camera_path, frame_context, old_data):
        """
        """
        data = old_data
        if not isinstance(data, ShotMaskData):
            data = ShotMaskData()

        # --- Shot mask attribute values
        dag_fn = om.MFnDagNode(obj_path)

        camera_name = dag_fn.findPlug("camera", False).asString()
        if camera_name and self.camera_exists(camera_name) and not self.is_camera_match(camera_path, camera_name):
            return None

        data.current_time = int(cmds.currentTime(q=True))
        data.start_time = int(cmds.playbackOptions(q=True, min=True))
        data.end_time = int(cmds.playbackOptions(q=True, max=True))

        data.counter_padding = dag_fn.findPlug("counterPadding", False).asInt()

        data.text_padding = dag_fn.findPlug("textPadding", False).asInt()

        data.font_name = dag_fn.findPlug("fontName", False).asString()
        data.font_weight = dag_fn.findPlug("fontWeight", False).asString()

        r = dag_fn.findPlug("fontColorR", False).asFloat()
        g = dag_fn.findPlug("fontColorG", False).asFloat()
        b = dag_fn.findPlug("fontColorB", False).asFloat()
        a = dag_fn.findPlug("fontAlpha", False).asFloat()
        data.font_color = om.MColor((r, g, b, a))

        data.font_scale = dag_fn.findPlug("fontScale", False).asFloat()
        data.image_scale = dag_fn.findPlug("imageScale", False).asFloat()

        r = dag_fn.findPlug("borderColorR", False).asFloat()
        g = dag_fn.findPlug("borderColorG", False).asFloat()
        b = dag_fn.findPlug("borderColorB", False).asFloat()
        a = dag_fn.findPlug("borderAlpha", False).asFloat()
        data.border_color = om.MColor((r, g, b, a))

        data.border_scale = dag_fn.findPlug("borderScale", False).asFloat()

        data.top_border = dag_fn.findPlug("topBorder", False).asBool()
        data.bottom_border = dag_fn.findPlug("bottomBorder", False).asBool()

        # second
        r = dag_fn.findPlug("in_borderColorR", False).asFloat()
        g = dag_fn.findPlug("in_borderColorG", False).asFloat()
        b = dag_fn.findPlug("in_borderColorB", False).asFloat()
        a = dag_fn.findPlug("in_borderAlpha", False).asFloat()
        data.in_border_color = om.MColor((r, g, b, a))

        data.in_border_scale = dag_fn.findPlug("in_borderScale", False).asFloat()

        data.in_top_border = dag_fn.findPlug("in_topBorder", False).asBool()
        data.in_bottom_border = dag_fn.findPlug("in_bottomBorder", False).asBool()

        data.border_mode = dag_fn.findPlug("borderMode", False).asShort()
        data.border_line_width = dag_fn.findPlug("borderLineWidth", False).asShort()

        r = dag_fn.findPlug("borderLineColorR", False).asFloat()
        g = dag_fn.findPlug("borderLineColorG", False).asFloat()
        b = dag_fn.findPlug("borderLineColorB", False).asFloat()
        a = dag_fn.findPlug("borderLineAlpha", False).asFloat()
        data.border_line_color = om.MColor((r, g, b, a))

        data.parsed_fields = []
        for i in range(0, len(MaskLocator.TEXT_ATTRS), 2):
            parsed_text = self.parse_text(dag_fn.findPlug(MaskLocator.TEXT_ATTRS[i], False).asString(), camera_path,
                                          data)
            data.parsed_fields.append(parsed_text)

        # --- Shot mask dimension data
        vp_x, vp_y, data.vp_width, data.vp_height = frame_context.getViewportDimensions()  # pylint: disable=W0612
        if not (data.vp_width and data.vp_height):
            return None

        data.mask_width, data.mask_height = self.get_mask_width_height(camera_path, data.vp_width, data.vp_height)
        if not (data.mask_width and data.mask_height):
            return None

        data.mask_aspect_ratio = data.mask_width / data.mask_height
        data.border_aspect_ratio = dag_fn.findPlug("borderAspectRatio", False).asFloat()
        data.aspect_ratio_borders = dag_fn.findPlug("aspectRatioBorders", False).asBool()

        # second
        data.in_border_aspect_ratio = dag_fn.findPlug("in_borderAspectRatio", False).asFloat()
        data.in_aspect_ratio_borders = dag_fn.findPlug("in_aspectRatioBorders", False).asBool()

        # background
        data.back_image_path = dag_fn.findPlug("imagePath", False).asString()
        data.back_title = dag_fn.findPlug("title", False).asString()
        data.back_date = dag_fn.findPlug("date", False).asString()
        data.back_frame = dag_fn.findPlug("frame", False).asString()
        data.first_frame = dag_fn.findPlug("firstFrame", False).asShort()
        data.title_size = dag_fn.findPlug("titleSize", False).asShort()
        data.text_size = dag_fn.findPlug("textSize", False).asShort()
        data.space = dag_fn.findPlug("space", False).asShort()
        data.x_pos = dag_fn.findPlug("xPos", False).asShort()
        data.y_pos = dag_fn.findPlug("yPos", False).asShort()
        data.shot_name = dag_fn.findPlug("shotName", False).asString()

        data.first_handle = dag_fn.findPlug("firstHandle", False).asBool()

        data.descrption = dag_fn.findPlug("descrption", False).asString()

        data.first_frame_image = dag_fn.findPlug("firstFrameImage", False).asString()
        data.x_pos_thumb = dag_fn.findPlug("xPosThumb", False).asShort()
        data.y_pos_thumb = dag_fn.findPlug("yPosThumb", False).asShort()



        return data

    def addUIDrawables(self, obj_path, draw_manager, frame_context, data):
        """
        """
        if not (data and isinstance(data, ShotMaskData)):
            return

        vp_half_width = 0.5 * data.vp_width
        vp_half_height = 0.5 * data.vp_height

        mask_half_width = 0.5 * data.mask_width
        mask_x = vp_half_width - mask_half_width

        mask_l_x=0.5 * data.vp_width-0.25 * data.mask_width

        mask_r_x = 0.5 * data.vp_width + 0.25 * data.mask_width

        mask_half_height = 0.5 * data.mask_height
        mask_bottom_y = vp_half_height - mask_half_height
        mask_top_y = vp_half_height + mask_half_height

        border_height = int(0.05 * data.mask_height * data.border_scale)

        if data.aspect_ratio_borders:
            border_aspect_ratio_height = data.mask_width / data.border_aspect_ratio
            aspect_ratio_border_height = int(0.5 * (data.mask_height - border_aspect_ratio_height))

            if (aspect_ratio_border_height > 0):
                border_height = aspect_ratio_border_height
            else:
                om.MGlobal.displayWarning(
                    "Border aspect ratio ({0}) <= mask aspect ratio ({1}). Reverting to border scale mode.".format(
                        round(data.border_aspect_ratio, 3), round(data.mask_aspect_ratio, 3)))

        # second
        in_border_height = int(0.05 * data.mask_height * data.in_border_scale)

        if data.in_aspect_ratio_borders:
            in_border_aspect_ratio_height = data.mask_width / data.in_border_aspect_ratio
            in_aspect_ratio_border_height = int(0.5 * (data.mask_height - in_border_aspect_ratio_height))

            if (in_aspect_ratio_border_height > 0):
                in_border_height = in_aspect_ratio_border_height
            else:
                om.MGlobal.displayWarning(
                    "Border aspect ratio ({0}) <= mask aspect ratio ({1}). Reverting to border scale mode.".format(
                        round(data.in_border_aspect_ratio, 3), round(data.mask_aspect_ratio, 3)))

        font_size = int((border_height - border_height * 0.15) * data.font_scale)
        background_size = (int(data.mask_width), border_height)

        in_background_size = (int(data.mask_width), in_border_height)

        image_size = data.image_scale

        if not data.top_border:
            font_size *= 2
            image_size *= 1.2

        draw_manager.beginDrawable()
        draw_manager.setFontName(data.font_name)
        if data.font_weight.lower() == 'nold':
            draw_manager.setFontWeight(700)
        elif data.font_weight.lower() == 'normal':
            draw_manager.setFontWeight(400)

        draw_manager.setColor(data.font_color)

        # print(mask_bottom_y)

        # second
        # line
        if data.border_mode == 1:
            if data.in_top_border:
                self.draw_border(draw_manager, om.MPoint(mask_x, mask_top_y - in_border_height, 0.1),
                                 (in_background_size[0], data.border_line_width),
                                 data.border_line_color)
            if data.in_bottom_border:
                self.draw_border(draw_manager, om.MPoint(mask_x, mask_bottom_y + in_border_height - 1, 0.1),
                                 (in_background_size[0], data.border_line_width),
                                 data.border_line_color)

        # mask
        if data.border_mode == 2:
            if data.in_top_border:
                self.draw_border(draw_manager, om.MPoint(mask_x, mask_top_y - in_border_height, 0.1),
                                 in_background_size,
                                 data.in_border_color)
            if data.in_bottom_border:
                self.draw_border(draw_manager, om.MPoint(mask_x, mask_bottom_y, 0.1), in_background_size,
                                 data.in_border_color)

        if data.top_border:
            self.draw_border(draw_manager, om.MPoint(mask_x, mask_top_y - border_height, 0.1), background_size,
                             data.border_color)
        if data.bottom_border:
            self.draw_border(draw_manager, om.MPoint(mask_x, mask_bottom_y, 0.1), background_size, data.border_color)

        self.draw_label(draw_manager, om.MPoint(mask_x + data.text_padding, mask_top_y - border_height, 0.0), data, 0,
                        omr.MUIDrawManager.kLeft, font_size, image_size, background_size)

        self.draw_label(draw_manager, om.MPoint(mask_l_x, mask_top_y - border_height, 0.0), data, 6,
                        omr.MUIDrawManager.kCenter, font_size, image_size, background_size)

        self.draw_label(draw_manager, om.MPoint(vp_half_width, mask_top_y - border_height, 0.0), data, 1,
                        omr.MUIDrawManager.kCenter, font_size, image_size, background_size)

        self.draw_label(draw_manager, om.MPoint(mask_r_x, mask_top_y - border_height, 0.0),
                        data, 7,
                        omr.MUIDrawManager.kCenter, font_size, image_size, background_size)

        self.draw_label(draw_manager,
                        om.MPoint(mask_x + data.mask_width - data.text_padding, mask_top_y - border_height, 0.0), data,
                        2, omr.MUIDrawManager.kRight, font_size, image_size, background_size)

        self.draw_label(draw_manager, om.MPoint(mask_x + data.text_padding, mask_bottom_y, 0.0), data, 3,
                        omr.MUIDrawManager.kLeft, font_size, image_size, background_size)

        self.draw_label(draw_manager, om.MPoint(vp_half_width, mask_bottom_y, 0.0), data, 4, omr.MUIDrawManager.kCenter,
                        font_size, image_size, background_size)

        self.draw_label(draw_manager, om.MPoint(mask_l_x, mask_bottom_y, 0.0), data, 8, omr.MUIDrawManager.kCenter,
                        font_size, image_size, background_size)

        self.draw_label(draw_manager, om.MPoint(mask_r_x, mask_bottom_y, 0.0), data, 9,
                        omr.MUIDrawManager.kCenter,
                        font_size, image_size, background_size)

        self.draw_label(draw_manager, om.MPoint(mask_x + data.mask_width - data.text_padding, mask_bottom_y, 0.0), data,
                        5, omr.MUIDrawManager.kRight, font_size, image_size, background_size)

        # first handle
        if data.first_handle:
            undo_state = cmds.undoInfo(q=True, state=True)
            if os.path.exists(data.back_image_path):
                if data.current_time <= data.first_frame:
                    position = om.MPoint(vp_half_width, vp_half_height, 0.1)
                    background_image_size = (int(data.mask_width), int(data.mask_height))
                    text_list = [data.back_date, data.back_frame, data.shot_name, data.descrption]

                    image_path = comp_first_frame.comp(
                        (data.x_pos, data.y_pos),
                        data.back_title,
                        data.title_size,
                        text_list,
                        data.text_size,
                        data.back_image_path,
                        data.first_frame_image,
                        data.x_pos_thumb,
                        data.y_pos_thumb,
                        [255, 255, 255],
                        data.space)
                    self.draw_back_ground_image(draw_manager, position, data, background_image_size, image_path)

        draw_manager.endDrawable()

    def get_resolution_width_height(self):
        width = cmds.getAttr("defaultResolution.width")
        height = cmds.getAttr("defaultResolution.height")
        return (width, height)

    def get_mask_width_height(self, camera_path, vp_width, vp_height):
        """
        """
        camera_fn = om.MFnCamera(camera_path)

        camera_aspect_ratio = camera_fn.aspectRatio()
        device_aspect_ratio = cmds.getAttr("defaultResolution.deviceAspectRatio")
        vp_aspect_ratio = vp_width / float(vp_height)

        scale = 1.0

        if camera_fn.filmFit == om.MFnCamera.kHorizontalFilmFit:
            mask_width = vp_width / camera_fn.overscan
            mask_height = mask_width / device_aspect_ratio
        elif camera_fn.filmFit == om.MFnCamera.kVerticalFilmFit:
            mask_height = vp_height / camera_fn.overscan
            mask_width = mask_height * device_aspect_ratio
        elif camera_fn.filmFit == om.MFnCamera.kFillFilmFit:
            if vp_aspect_ratio < camera_aspect_ratio:
                if camera_aspect_ratio < device_aspect_ratio:
                    scale = camera_aspect_ratio / vp_aspect_ratio
                else:
                    scale = device_aspect_ratio / vp_aspect_ratio
            elif camera_aspect_ratio > device_aspect_ratio:
                scale = device_aspect_ratio / camera_aspect_ratio

            mask_width = vp_width / camera_fn.overscan * scale
            mask_height = mask_width / device_aspect_ratio

        elif camera_fn.filmFit == om.MFnCamera.kOverscanFilmFit:
            if vp_aspect_ratio < camera_aspect_ratio:
                if camera_aspect_ratio < device_aspect_ratio:
                    scale = camera_aspect_ratio / vp_aspect_ratio
                else:
                    scale = device_aspect_ratio / vp_aspect_ratio
            elif camera_aspect_ratio > device_aspect_ratio:
                scale = device_aspect_ratio / camera_aspect_ratio

            mask_height = vp_height / camera_fn.overscan / scale
            mask_width = mask_height * device_aspect_ratio
        else:
            om.MGlobal.displayError("[ShotMask] Unsupported Film Fit value")
            return None, None

        return mask_width, mask_height

    def draw_border(self, draw_manager, position, background_size, color):
        """
        """
        draw_manager.text2d(position, " ", alignment=omr.MUIDrawManager.kLeft, backgroundSize=background_size,
                            backgroundColor=color)

    def draw_back_ground(self, draw_manager, data, position, background_size, color):

        draw_manager.text2d(position, " ", alignment=omr.MUIDrawManager.kLeft, backgroundSize=background_size,
                            backgroundColor=color)

        background_size = (int(data.mask_width), int(data.mask_height))

        # title
        position = om.MPoint(position.x / 2, position.y / 2, 0.0)

        self.draw_text(draw_manager, position, data.back_title, data, omr.MUIDrawManager.kCenter,
                       data.title_size, background_size)

    def draw_txt(self, draw_manager, text, font_size, position, alignment, background_size, offset_value,data):
        if '|' in text:
            split_text = text.split('|', 1)
            half_font_size = int(font_size * 0.5)
            draw_manager.setFontSize(half_font_size)
            if split_text[1] == '' or re.findall(r'.*?\*[+-]?\d+(?:\.\d+)?', text):
                position_new = om.MPoint(position)
                position_new.x = position_new.x + offset_value*data.mask_width


                draw_manager.text2d(position_new, split_text[0], alignment=alignment, backgroundSize=background_size,
                                    backgroundColor=om.MColor((0.0, 0.0, 0.0, 0.0)))
            else:
                top_position = om.MPoint(position)

                top_position.x = top_position.x + offset_value*data.mask_width


                top_position.y = top_position.y + int(0.6 * half_font_size)
                draw_manager.text2d(top_position, split_text[0], alignment=alignment, backgroundSize=background_size,
                                    backgroundColor=om.MColor((0.0, 0.0, 0.0, 0.0)))
                bottom_position = om.MPoint(position)

                bottom_position.x = bottom_position.x + offset_value*data.mask_width

                bottom_position.y = bottom_position.y - (0.5 * half_font_size)
                draw_manager.text2d(bottom_position, split_text[1], alignment=alignment, backgroundSize=background_size,
                                    backgroundColor=om.MColor((0.0, 0.0, 0.0, 0.0)))
        else:
            draw_manager.setFontSize(font_size)
            position_new = om.MPoint(position)

            position_new.x = position_new.x + offset_value*data.mask_width


            draw_manager.text2d(position_new, text, alignment=alignment, backgroundSize=background_size,
                                backgroundColor=om.MColor((0.0, 0.0, 0.0, 0.0)))

    def draw_label(self, draw_manager, position, data, data_index, alignment, font_size, image_size, background_size):
        """
        """
        if data.parsed_fields[data_index]["image_path"]:
            self.draw_image(draw_manager, position, data, data_index, alignment, font_size, background_size, image_size)
            return

        draw_manager.setColor(data.font_color)

        text = data.parsed_fields[data_index]["text"]
        offset_list = re.findall(r'.*?\*[+-]?\d+(?:\.\d+)?', text)
        if offset_list:
            for txt in offset_list:
                text = txt.rsplit('*', 1)[0]
                offset_value = float(txt.rsplit('*', 1)[1])

                self.draw_txt(draw_manager, text, font_size, position, alignment, background_size, offset_value,data)
        else:
            if text:
                self.draw_txt(draw_manager, text, font_size, position, alignment, background_size, 0,data)

    def draw_image(self, draw_manager, position, data, data_index, alignment, font_size, background_size, image_size):
        """
        """
        texture_manager = omr.MRenderer.getTextureManager()
        image_path = data.parsed_fields[data_index]["image_path"]
        offset_list = re.findall(r'.*?\*[+-]?\d+(?:\.\d+)?', image_path)
        if offset_list:
            image = offset_list[0].rsplit('*', 1)[0]
            offset_value = float(offset_list[0].rsplit('*', 1)[1])
        else:
            image = image_path
            offset_value = 0

        texture = texture_manager.acquireTexture(image)
        if not texture:
            # om.MGlobal.displayError("[ShotMask] Unsupported image file: {0}".format(data.image_paths[data_index]))
            om.MGlobal.displayError("[ShotMask] Unsupported image file: {0}".format(data.image_path[data_index]))
            return

        draw_manager.setTexture(texture)
        draw_manager.setTextureSampler(omr.MSamplerState.kMinMagMipLinear, omr.MSamplerState.kTexClamp)
        draw_manager.setTextureMask(omr.MBlendState.kRGBAChannels)
        draw_manager.setColor(om.MColor((1.0, 0.0, 0.0, data.font_color.a)))

        # Scale the image based on the border height
        half_font_size = int(font_size * 0.5)
        texture_desc = texture.textureDescription()

        # scale_y = (0.5 * background_size[1]) - 4

        scale_y = half_font_size * image_size

        scale_x = scale_y / texture_desc.fHeight * texture_desc.fWidth

        if alignment == omr.MUIDrawManager.kLeft:
            position = om.MPoint(position.x + scale_x, position.y + int(0.5 * background_size[1]))
        elif alignment == omr.MUIDrawManager.kRight:
            position = om.MPoint(position.x - scale_x, position.y + int(0.5 * background_size[1]))
        else:
            position = om.MPoint(position.x, position.y + int(0.5 * background_size[1]))
        position_new = om.MPoint(position)

        position_new.x = position_new.x + offset_value*data.mask_width

        position_new.y += 1
        draw_manager.rect2d(position_new, om.MVector(0.0, 1.0, 0.0), scale_x, scale_y, True)

    def draw_text(self, draw_manager, position, text, data, alignment, font_size, background_size):

        draw_manager.setColor(data.font_color)

        if text:
            if '|' in text:
                split_text = text.split('|', 1)

                half_font_size = int(font_size * 0.5)
                draw_manager.setFontSize(half_font_size)

                top_position = om.MPoint(position)
                top_position.y = top_position.y + int(0.6 * half_font_size)
                draw_manager.text2d(top_position, split_text[0], alignment=alignment, backgroundSize=background_size,
                                    backgroundColor=om.MColor((0.0, 0.0, 0.0, 0.0)))

                bottom_position = om.MPoint(position)
                bottom_position.y = bottom_position.y - (0.5 * half_font_size)
                draw_manager.text2d(bottom_position, split_text[1], alignment=alignment, backgroundSize=background_size,
                                    backgroundColor=om.MColor((0.0, 0.0, 0.0, 0.0)))

            else:
                draw_manager.setFontSize(font_size)
                draw_manager.text2d(position, text, alignment=alignment, backgroundSize=background_size,
                                    backgroundColor=om.MColor((0.0, 0.0, 0.0, 0.0)))

    def draw_back_ground_image(self, draw_manager, position, data, background_size, image_path):

        if not os.path.exists(data.back_image_path):
            print('not set backGround image...')
            return

        texture_manager = omr.MRenderer.getTextureManager()
        texture = texture_manager.acquireTexture(image_path)

        if not texture:
            om.MGlobal.displayError("[ShotMask] Unsupported image file: {0}")
            return

        draw_manager.setTexture(texture)
        draw_manager.setTextureSampler(omr.MSamplerState.kMinMagMipLinear, omr.MSamplerState.kTexClamp)
        draw_manager.setTextureMask(omr.MBlendState.kRGBAChannels)
        draw_manager.setColor(om.MColor((1.0, 1.0, 1.0, data.font_color.a)))

        # Scale the image based on the border height

        texture_desc = texture.textureDescription()

        scale_y = 0.5 * background_size[1]

        scale_x = scale_y / texture_desc.fHeight * texture_desc.fWidth

        # position = om.MPoint(position.x, position.y,0.1)

        draw_manager.rect2d(position, om.MVector(0.0, 1.0, 0.0), scale_x, scale_y, True)

    def camera_exists(self, name):
        """
        """
        dg_iter = om.MItDependencyNodes(om.MFn.kCamera)
        while not dg_iter.isDone():
            if dg_iter.thisNode().hasFn(om.MFn.kDagNode):
                camera_path = om.MDagPath.getAPathTo(dg_iter.thisNode())
                if self.is_camera_match(camera_path, name):
                    return True
            dg_iter.next()

        return False

    def is_camera_match(self, camera_path, name):
        """
        """
        if self.camera_transform_name(camera_path) == name or self.camera_shape_name(camera_path) == name:
            return True

        return False

    def camera_transform_name(self, camera_path):
        """
        """
        camera_transform = camera_path.transform()
        if camera_transform:
            return om.MFnTransform(camera_transform).name()

        return ""

    def camera_shape_name(self, camera_path):
        """
        """
        camera_shape = camera_path.node()
        if camera_shape:
            return om.MFnCamera(camera_shape).name()

        return ""

    def get_scene_name(self):
        scene_name = cmds.file(q=True, sceneName=True, shortName=True)
        if scene_name:
            scene_name = os.path.splitext(scene_name)[0]
        else:
            scene_name = "untitled"

        return scene_name

    def get_focal_length(self, camera_path):
        camera = om.MFnCamera(camera_path)
        return "{0}".format(int(round(camera.focalLength)))

    def get_time_code(self):
        start_frame = 86401
        current_frame = int(cmds.currentTime(q=True))
        frame_rate = 24
        total_frames = start_frame + current_frame - 1
        total_seconds = total_frames // frame_rate
        remaining_frames = total_frames % frame_rate
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        timecode = "%01d:%02d:%02d:%02d" % (hours, minutes, seconds, remaining_frames)
        return timecode

    def get_unit_scale(self):
        linear_unit = cmds.currentUnit(query=True, linear=True)
        return {
            'millimeter': 0.001,
            'centimeter': 0.01,
            'meter': 1.0,
            'kilometer': 1000.0,
            'inch': 0.0254,
            'foot': 0.3048,
            'yard': 0.9144,
            'mile': 1609.34
        }.get(linear_unit, 1.0)

    def get_fps(self):
        # fps = cmds.currentUnit(query=True, time=True)
        # fps_map = {'film': 24, 'pal': 25, 'ntsc': 30, 'show': 48, 'palf': 50, 'ntscf': 60}
        # frame_rate = fps_map.get(fps, 24)
        # return frame_rate

        second_time_value = om.MTime(1.0, om.MTime.kSeconds)
        fps = second_time_value.asUnits(om.MTime.uiUnit())
        return int(fps)

    def get_world_translate(self,dep_node,dg_context):
        world_matrix_plug = dep_node.findPlug("worldMatrix", False)
        world_matrix_plug_ele = world_matrix_plug.elementByLogicalIndex(0)
        matrix_obj = world_matrix_plug_ele.asMObject(dg_context)
        matrix_data = om.MFnMatrixData(matrix_obj)
        matrix = matrix_data.matrix()
        transform = om.MTransformationMatrix(matrix)
        translation = transform.translation(om.MSpace.kWorld)
        return translation

    def get_camera_speed_km(self, camera_path, data):

        dep_node=om.MFnDependencyNode(camera_path.transform())
        frame = int(cmds.currentTime(q=True))

        time = om.MTime(frame, om.MTime.uiUnit())
        time_interval = om.MTime(1, om.MTime.uiUnit())
        interval = time_interval.asUnits(om.MTime.uiUnit()) * 2

        dg_context_prev = om.MDGContext(time - time_interval)
        dg_context_now = om.MDGContext(time)
        dg_context_next = om.MDGContext(time + time_interval)
        camera_transform = camera_path.transform()

        if camera_transform:
            point_prev=self.get_world_translate(dep_node,dg_context_prev)
            point_now=self.get_world_translate(dep_node,dg_context_now)
            point_next=self.get_world_translate(dep_node,dg_context_next)

            linear_unit = cmds.currentUnit(query=True, linear=True)
            scale_factor = {
                'mm': 0.001,
                'cm': 0.01,
                'm': 1.0,
                'kilometer': 1000.0,
                'in': 0.0254,
                'ft': 0.3048,
                'yd': 0.9144,
                'mile': 1609.34
            }.get(linear_unit, 1.0)

            second_time_value = om.MTime(1.0, om.MTime.kSeconds)
            fps = second_time_value.asUnits(om.MTime.uiUnit())


            display_unit_factor = fps * 60 * 60 * 0.001 #km/h

            dx = point_now[0] - point_prev[0]
            dy = point_now[1] - point_prev[1]
            dz = point_now[2] - point_prev[2]
            speed_raw = math.sqrt((dx * dx) + (dy * dy) + (dz * dz))
            dx = point_now[0] - point_next[0]
            dy = point_now[1] - point_next[1]
            dz = point_now[2] - point_next[2]
            speed_raw += math.sqrt((dx * dx) + (dy * dy) + (dz * dz))

            speed = (speed_raw * scale_factor * display_unit_factor) / interval
            return round(speed,3)

    def get_username(self):
        return getpass.getuser()

    def get_date(self):
        """
        """
        return datetime.date.today().strftime('%Y/%m/%d')

    def get_image(self, image_path):
        """
        """
        image_path = image_path.strip()
        if os.path.exists(image_path.rsplit('*', 1)[0]):
            return image_path, ""

        return "", "Image not found"

    def parse_text(self, orig_text, camera_path, data):
        """
        """
        label = ""
        image_path = ""

        text = orig_text
        text = PlayBlastCustomPresets.parse_shot_mask_text(text)
        if "{start_time}" in text:
            text = text.replace("{start_time}", "{0}".format(str(data.start_time).zfill(data.counter_padding)))
        if "{end_time}" in text:
            text = text.replace("{end_time}", "{0}".format(str(data.end_time).zfill(data.counter_padding)))

        if "{counter}" in text:
            text = text.replace("{counter}", "{0}".format(str(data.current_time).zfill(data.counter_padding)))

        if "{time_code}" in text:
            text = text.replace("{time_code}", "{0}".format(self.get_time_code()))

        if "{fps}"in text:
            text = text.replace("{fps}", "{0}".format(self.get_fps()))

        if "{camera_speed_km}" in text:
            text = text.replace("{camera_speed_km}", "{0}".format(self.get_camera_speed_km(camera_path, data)))

        if "{scene}" in text:
            text = text.replace("{scene}", "{0}".format(self.get_scene_name()))
        if "{camera}" in text:
            text = text.replace("{camera}", "{0}".format(self.camera_transform_name(camera_path)))
        if "{focal_length}" in text:
            text = text.replace("{focal_length}", "{0}".format(self.get_focal_length(camera_path)))
        if "{username}" in text:
            text = text.replace("{username}", "{0}".format(self.get_username()))
        if "{date}" in text:
            text = text.replace("{date}", "{0}".format(self.get_date()))

        stripped_text = text.strip()
        if stripped_text.startswith("{logo}"):
            logo_path = PlayBlastCmd.resolve_env_var(PlayBlastCmd.LOGO_PATH_ENV_VAR, PlayBlastCmd.LOGO_PATH_OPTION_VAR)
            image_path, text = self.get_image(logo_path)

        if stripped_text.startswith("{image=") and stripped_text.endswith("}"):
            image_path, text = self.get_image(stripped_text[7:-1])

        return {"label": label, "text": text, "image_path": image_path}

    @staticmethod
    def creator(obj):
        """
        """
        return ShotMaskDrawOverride(obj)

    @staticmethod
    def draw(context, data):
        """
        """
        return


def initializePlugin(obj):
    """
    """
    plugin_fn = om.MFnPlugin(obj, "Slate", PlayBlastCmd.PLUG_IN_VERSION, "Any")

    try:
        plugin_fn.registerCommand(PlayBlastCmd.COMMAND_NAME, PlayBlastCmd.creator, PlayBlastCmd.create_syntax)
    except:
        om.MGlobal.displayError("Failed to register command: {0}".format(PlayBlastCmd.COMMAND_NAME))

    try:
        plugin_fn.registerNode(MaskLocator.NAME,
                               MaskLocator.TYPE_ID,
                               MaskLocator.creator,
                               MaskLocator.initialize,
                               om.MPxNode.kLocatorNode,
                               MaskLocator.DRAW_DB_CLASSIFICATION)
    except:
        om.MGlobal.displayError("Failed to register node: {0}".format(MaskLocator.NAME))

    try:
        omr.MDrawRegistry.registerDrawOverrideCreator(MaskLocator.DRAW_DB_CLASSIFICATION,
                                                      MaskLocator.DRAW_REGISTRANT_ID,
                                                      ShotMaskDrawOverride.creator)
    except:
        om.MGlobal.displayError("Failed to register draw override: {0}".format(ShotMaskDrawOverride.NAME))


def uninitializePlugin(obj):
    """
    """
    plugin_fn = om.MFnPlugin(obj)

    try:
        omr.MDrawRegistry.deregisterDrawOverrideCreator(MaskLocator.DRAW_DB_CLASSIFICATION,
                                                        MaskLocator.DRAW_REGISTRANT_ID)
    except:
        om.MGlobal.displayError("Failed to deregister draw override: {0}".format(ShotMaskDrawOverride.NAME))

    try:
        plugin_fn.deregisterNode(MaskLocator.TYPE_ID)
    except:
        om.MGlobal.displayError("Failed to unregister node: {0}".format(MaskLocator.NAME))

    try:
        plugin_fn.deregisterCommand(PlayBlastCmd.COMMAND_NAME)
    except:
        om.MGlobal.displayError("Failed to deregister command: {0}".format(PlayBlastCmd.COMMAND_NAME))


if __name__ == "__main__":
    cmds.file(f=True, new=True)

    plugin_name = "play_blast_plugin.py"
    cmds.evalDeferred('if cmds.pluginInfo("{0}", q=True, loaded=True): cmds.unloadPlugin("{0}")'.format(plugin_name))
    cmds.evalDeferred('if not cmds.pluginInfo("{0}", q=True, loaded=True): cmds.loadPlugin("{0}")'.format(plugin_name))

    cmds.evalDeferred('cmds.createNode("ShotMask")')
