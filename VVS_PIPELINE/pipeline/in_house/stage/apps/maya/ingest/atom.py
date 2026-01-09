from maya import cmds
from maya import OpenMaya as om
from stage.external.fileseq import filesequence as fileseq
from stage.apps.ingest_core import IngestCore
from pathlib import Path

class Atom(IngestCore):
    """Ingest image sequence as image plane."""

    nice_name = "Atom"
    valid_extensions = [".atom"]
    referencable = False

    def __init__(self):
        super(Atom, self).__init__()
        om.MGlobal.displayInfo("Atom Extractor loaded")
        if not cmds.pluginInfo("atomImportExport", loaded=True, query=True):
            try:
                cmds.loadPlugin("atomImportExport")
            except Exception as e:  # pylint: disable=broad-except
                om.MGlobal.displayInfo("atomImportExport Plugin cannot be initialized")
                raise e

    def _reference_default(self):
        self._bring_in_default()

    def _bring_in_default(self):
        """Import the atom."""

        name=self.parameter.get(self.__class__.__name__.lower()).format(name=Path(self.ingest_path).stem)

        if name:
            cmds.select(name, hierarchy=True, replace=True)
            cmds.file(
                self.ingest_path,
                i=True,
                # ra=True,
                type="atomImport",
                options=(
                    "targetTime=2;"
                    "option=scaleReplace;"
                    "match=hierarchy;"
                    "selected=childrenToo;"
                    "mapFile=;"
                )
            )
        else:
            om.MGlobal.displayError("Not a valid parameter:%s"%str(self.parameter))