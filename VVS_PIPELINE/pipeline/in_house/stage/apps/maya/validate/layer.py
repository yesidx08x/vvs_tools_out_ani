"""Locked Normals validation for Maya."""

from maya.api import OpenMaya
from maya import cmds
from stage.apps.validate_core import ValidateCore

class Layer(ValidateCore):


    nice_name = "图层"

    def __init__(self):
        super(Layer, self).__init__()
        self.autofixable = True
        self.ignorable = False
        self.selectable = True

        self.layer_nodes = []

    def collect(self):
        self.collection = [lay for lay in cmds.ls(type=['displayLayer','renderLayer','animLayer']) if lay not in  ['defaultLayer', 'defaultRenderLayer','BaseAnimation']]

    def validate(self):

        self.collect()

        if self.collection:
            self.failed(msg=f"layer found: {self.collection}")
        else:
            self.passed()

    def fix(self):
        cmds.delete(self.collection)

    def select(self):

        cmds.select(self.collection)


