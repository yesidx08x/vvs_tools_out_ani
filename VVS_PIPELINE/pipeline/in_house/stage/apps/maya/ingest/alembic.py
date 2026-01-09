"""Ingest Alembic."""

from pathlib import Path
from maya import cmds
from maya import OpenMaya as om
from stage.apps.ingest_core import IngestCore

class Alembic(IngestCore):
    """Ingest Alembic."""

    nice_name =  "Ingest Alembic"
    valid_extensions = [".abc"]
    referencable = True

    def __init__(self):
        super(Alembic, self).__init__()
        if not cmds.pluginInfo("AbcImport", loaded=True, query=True):
            try:
                cmds.loadPlugin("AbcImport")
            except Exception as exc:
                om.MGlobal.displayInfo("Alembic Import Plugin cannot be initialized")
                raise exc

        self.category_functions = {"Model": self._bring_in_model,
                                   "Animation": self._bring_in_animation,
                                   "Fx": self._bring_in_fx,
                                   "Layout": self._bring_in_layout,
                                   "Lighting": self._bring_in_lighting,
                                   }

    def _bring_in_model(self):
        """Import Alembic File."""
        om.MGlobal.displayInfo("Bringing in Alembic Model")
        cmds.AbcImport(self.ingest_path, mode="import", fitTimeRange=False, setToStartFrame=False)

    def _bring_in_animation(self):
        """Import Alembic File."""
        om.MGlobal.displayInfo("Bringing in Alembic Animation")
        cmds.AbcImport(self.ingest_path, mode="import", fitTimeRange=True, setToStartFrame=True)

    def _bring_in_fx(self):
        """Import Alembic File."""
        om.MGlobal.displayInfo("Bringing in Alembic FX")
        # identical to animation
        self._bring_in_animation()

    def _bring_in_layout(self):
        """Import Alembic File."""
        om.MGlobal.displayInfo("Bringing in Alembic Layout")
        # identical to animation
        self._bring_in_animation()

    def _bring_in_lighting(self):
        """Import Alembic File."""
        om.MGlobal.displayInfo("Bringing in Alembic Lighting")
        # identical to animation
        self._bring_in_animation()

    def _bring_in_default(self):
        """Import Alembic File."""
        om.MGlobal.displayInfo("Bringing in Alembic with default settings")
        cmds.AbcImport(self.ingest_path)

    def _reference_default(self):
        """Create a GPU Cache for alembics instead of reference."""

        if self.parameter and self.extract:
            func = self.parameter[self.extract].get('name_space')
            name_space = func(Path(self.ingest_path).stem)

        else:
            name_space = Path(self.ingest_path).stem


        ref = cmds.file(
            self.ingest_path,
            reference=True,
            groupLocator=True,
            mergeNamespacesOnClash=False,
            namespace=name_space,
            returnNewNodes=True,
        )
        return ref