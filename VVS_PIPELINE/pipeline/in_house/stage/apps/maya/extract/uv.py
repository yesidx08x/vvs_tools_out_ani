
from maya import cmds
from maya import OpenMaya as om
from stage.apps.extract_core import ExtractCore
from stage.apps.maya import extract_infos

class Uv(ExtractCore):

    nice_name = "UV"
    color = (255, 255, 255)
    def __init__(self):
        super(Uv, self).__init__()
        om.MGlobal.displayInfo("UV Extractor loaded")
        if not cmds.pluginInfo("exportUvCmd", loaded=True, query=True):
            try:
                cmds.loadPlugin("exportUvCmd")
            except Exception as e:  # pylint: disable=broad-except
                om.MGlobal.displayInfo("exportUvCmd Plugin cannot be initialized")
                raise e

        self._extension = ".uv"


    def _extract_default(self):

        _file_path = self.resolve_output()

        cmds.exportUv(filename=_file_path,sn=True,auv=True)
        self.extract_json[self.__class__.name].update(extract_infos.get_extract_infos(_file_path))
