"""Locked Normals validation for Maya."""

from maya.api import OpenMaya
from maya import cmds
from maya import mel
from stage.apps.validate_core import ValidateCore

class Historys(ValidateCore):


    nice_name = "历史记录"

    def __init__(self):
        super(Historys, self).__init__()
        self.autofixable = True
        self.ignorable = False
        self.selectable = True

        self.history_nodes = []

    def collect(self):
        self.collection = cmds.ls(transforms=True, long=True)

    def validate(self):

        self.history_nodes = []
        self.collect()

        for node in self.collection:

            shape = cmds.listRelatives(node, shapes=True, fullPath=True)
            if shape and cmds.nodeType(shape[0]) == 'mesh':
                history_size = cmds.listConnections(shape[0]+'.inMesh', source=True, destination=False, plugs=True)
                if history_size:
                    self.history_nodes.append(node)

        if self.history_nodes:
            self.failed(msg=f"Meshes history found: {self.history_nodes}")
        else:
            self.passed()

    def fix(self):
        mel.eval('DeleteAllHistory;')
    def select(self):

        cmds.select(self.history_nodes)


