
from maya import cmds
from maya import OpenMaya as om
from stage.apps.extract_core import ExtractCore
from stage.apps.maya import extract_infos

class Source(ExtractCore):

    nice_name = "Maya Scene"
    color = (255, 255, 255)
    def __init__(self):
        super(Source, self).__init__()

        om.MGlobal.displayInfo("Maya Scene Extractor loaded")

        self.extension = ".ma"


    def _extract_default(self):

        _file_path = self.resolve_output()
        file_format = "mayaAscii" if self.extension == ".ma" else "mayaBinary"
        _original_path = cmds.file(query=True, sceneName=True)
        cmds.file(rename=_file_path)
        try:
            cmds.file(save=True, type=file_format)
        except RuntimeError as e:
            cmds.file(rename=_original_path)
            raise RuntimeError(e)
        finally:
            cmds.file(rename=_original_path)

        self.extract_json[self.__class__.name].update(extract_infos.get_extract_infos(_file_path))