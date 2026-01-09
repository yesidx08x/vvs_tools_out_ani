"""Ingest source scene."""

from pathlib import Path

from maya import cmds
from maya import OpenMaya as om
from stage.apps.ingest_core import IngestCore


class Source(IngestCore):
    """Ingest Source Maya Scene."""

    nice_name = "Ingest Source Scene"
    valid_extensions = [".mb", ".ma"]
    referencable = True

    def __init__(self):
        super(Source, self).__init__()

    def _bring_in_default(self):
        """Import the Maya scene."""
        om.MGlobal.displayInfo("Bringing in Source Scene")
        # cmds.file(self.ingest_path, i=True)
        cmds.file(self.ingest_path, preserveReferences=True,i=True)

    def _reference_default(self):
        """Reference the Maya scene."""

        if  self.parameter:
            func=self.parameter.get(self.__class__.__name__.lower()).get('name_space')
            namespace=func(Path(self.ingest_path).stem)
        else:
            namespace=Path(self.ingest_path).stem

        om.MGlobal.displayInfo("Referencing Source Scene")

        ref = cmds.file(
            self.ingest_path,
            reference=True,
            groupLocator=True,
            mergeNamespacesOnClash=False,
            namespace=namespace,
            returnNewNodes=True,
        )
        return ref
