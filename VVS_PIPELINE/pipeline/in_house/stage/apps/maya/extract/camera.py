import re
from maya import cmds
from maya import  mel
from maya import OpenMaya as om
from pathlib import Path
from stage.apps.extract_core import ExtractCore
from stage.apps.maya import utils
from stage.apps.maya import extract_infos

class Camera(ExtractCore):
    nice_name = "Camera"
    color = (255, 255, 255)

    def __init__(self):
        _ranges = utils.get_ranges()
        exposed_settings = {
            "Animation": {
                "start_frame": {
                    "display_name": "Start Frame",
                    "type": "integer",
                    "value": _ranges[0],
                },
                "end_frame": {
                    "display_name": "End Frame",
                    "type": "integer",
                    "value": _ranges[3],
                },
                "sub_steps": {
                    "display_name": "Sub Steps",
                    "type": "integer",
                    "value": 1,
                },
            },
            "Layout": {
                "start_frame": {
                    "display_name": "Start Frame",
                    "type": "integer",
                    "value": _ranges[0],
                },
                "end_frame": {
                    "display_name": "End Frame",
                    "type": "integer",
                    "value": _ranges[3],
                },
            },
        }

        super().__init__(exposed_settings=exposed_settings)
        _ranges = utils.get_ranges()
        if not cmds.pluginInfo("AbcExport", loaded=True, query=True):
            try:
                cmds.loadPlugin("AbcExport")
            except Exception as e:  # pylint: disable=broad-except
                om.MGlobal.displayInfo("Alembic Plugin cannot be initialized")
                raise e

        om.MGlobal.displayInfo("Alembic Extractor loaded")

        self._extension = ".abc"

    def ls_regex(self, val):
        res = {}
        reg = re.compile(r'(\||^)' + val, re.IGNORECASE)
        cameras = cmds.ls(type='camera')
        for camera in cameras:
            match = reg.search(camera)
            if match:
                res[cmds.listRelatives(camera, parent=True)[0]] = match.groupdict()

        return res

    def _extract_default(self):
        if not self.parameter:
            print(self.nice_name, 'not parameter')
            return

        file_path_without_suffix = self.resolve_output()
        file_path = Path(file_path_without_suffix)

        path = file_path.parent
        # base_name = file_path.stem
        suffix = file_path.suffix
        settings = self.settings.get("Layout")

        _start_frame = settings.get("start_frame")
        _end_frame = settings.get("end_frame")

        nodes = self.ls_regex(self.parameter.get('name'))

        for node, value in nodes.items():
            _file_path = path.joinpath(node).with_suffix(suffix).as_posix()
            _flags = f"-frameRange {_start_frame} {_end_frame} -step 1.0 -uvWrite -stripNamespaces -worldSpace -writeUVSets -renderableOnly -writeVisibility -dataFormat ogawa -root {node}"
            command = f"{_flags} -file {_file_path}"
            #mel.eval(f'AbcExport -j "{command}"')
            cmds.AbcExport(j=command)
            self._resolve_outputs.append(_file_path)
            full_path_name = cmds.ls(node, long=True)[0]
            self.extract_json[self.__class__.name].update(extract_infos.get_extract_infos(_file_path,full_path_name=full_path_name))