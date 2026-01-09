import re
from maya import cmds
from maya import OpenMaya as om
from pathlib import Path
from stage.apps.extract_core import ExtractCore
from stage.apps.maya import extract_infos


class Atom(ExtractCore):
    nice_name = "Animation"
    color = (255, 255, 255)

    def __init__(self):
        super(Atom, self).__init__()
        om.MGlobal.displayInfo("Atom Extractor loaded")
        if not cmds.pluginInfo("atomImportExport", loaded=True, query=True):
            try:
                cmds.loadPlugin("atomImportExport")
            except Exception as e:  # pylint: disable=broad-except
                om.MGlobal.displayInfo("atomImportExport Plugin cannot be initialized")
                raise e

        self._extension = ".atom"

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
        if not self.parameter:
            print(self.nice_name, 'not parameter')
            return

        # print(self.nice_name,self.parameter)
        file_path_without_suffix = self.resolve_output()
        file_path = Path(file_path_without_suffix)

        path = file_path.parent
        # base_name = file_path.stem
        suffix = file_path.suffix


        nodes = self.ls_regex(self.parameter.get('name'))

        for node, value in nodes.items():
            cmds.select(node, hierarchy=True, replace=True)
            _file_path = path.joinpath(value.get('name_space')).with_suffix(suffix).as_posix()
            print(node,_file_path)

            cmds.file(
                _file_path,
                type="atomExport",
                force=True,
                exportSelected=True,
                options=(
                    "precision=8;"
                    "statics=1;"
                    "baked=True;"
                    "sdk=0;"
                    "constraint=1;"
                    "animLayers=1;"
                    "selected=childrenToo;"
                    "whichRange=2;"
                    "range=1:100;"
                    "hierarchy=none;"
                    "controlPoints=1;"
                    "useChannelBox=1;"
                    "options=keys;"
                    "copyKeyCmd="
                    "-animation objects"
                    "-option keys"
                    "-hierarchy none"
                    "-controlPoints 1"
                ),
            )
            self._resolve_outputs.append(_file_path)
            full_path_name = cmds.ls(sl=True, long=True)[0]
            self.extract_json[self.__class__.name].update(extract_infos.get_extract_infos(_file_path, full_path_name=full_path_name))


