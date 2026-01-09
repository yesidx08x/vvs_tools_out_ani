import re
from pathlib import Path
from maya import cmds
from maya import OpenMaya as om
from stage.apps.extract_core import ExtractCore
from stage.apps.maya import utils
from stage.apps.maya import extract_infos


class AbcCache(ExtractCore):
    """Extract AniCache from Maya scene."""

    nice_name = "AbcCache"
    color = (244, 132, 132)

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
                "sub_steps":{
                    "display_name": "Sub Steps",
                    "type": "integer",
                    "value": 1,
                },
            },
        }
        super().__init__(exposed_settings=exposed_settings)
        if not cmds.pluginInfo("tomatoAbcExport", loaded=True, query=True):
            try:
                cmds.loadPlugin("tomatoAbcExport")
            except Exception as e:  # pylint: disable=broad-except
                om.MGlobal.displayInfo("Alembic Plugin cannot be initialized")
                raise e

        om.MGlobal.displayInfo("Alembic Extractor loaded")

        self._extension = ".abc"

    def ls_regex(self, val):
        res = {}
        reg = re.compile(r'(\||^)' + val, re.IGNORECASE)
        transforms = cmds.ls(type='transform')
        for transform in transforms:
            match = reg.search(transform)
            if match:
                res[transform] = match.groupdict()

        return res

    def _extract_default(self):
        """Extract method for any non-specified category"""


        if not self.parameter:
            print(self.nice_name, 'not parameter')
            return

        # print(self.nice_name,self.parameter)
        file_path_without_suffix = self.resolve_output()
        file_path = Path(file_path_without_suffix)

        path = file_path.parent
        # base_name = file_path.stem
        suffix = file_path.suffix

        nodes = self.ls_regex(self.parameter.get('root'))
        prefix=self.parameter.get('prefix')
        name=self.parameter.get('name')
        settings = self.settings.get("Animation")
        _start_frame = settings.get("start_frame")
        _end_frame = settings.get("end_frame")

        for node, value in nodes.items():
            file_name=name.format(name_space=value.get('name_space'))
            full_path_name = cmds.ls(node, long=True)[0]
            _file_path = path.joinpath(file_name).with_suffix(suffix).as_posix()
            print(_file_path)
            _flags = f"-frameRange {_start_frame} {_end_frame} -step 1.0 -uvWrite -worldSpace -writeUVSets -renderableOnly -writeVisibility -dataFormat ogawa -root {full_path_name} -prefix {prefix} "
            command = f"{_flags} -file {_file_path}"
            cmds.tomatoAbcExport(j=command)
            self._resolve_outputs.append(_file_path)
            self.extract_json[self.__class__.name].update(extract_infos.get_extract_infos(_file_path, full_path_name=full_path_name))