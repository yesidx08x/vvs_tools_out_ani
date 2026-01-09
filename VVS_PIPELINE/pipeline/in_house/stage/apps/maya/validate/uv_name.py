
import maya.api.OpenMaya as om
from maya import cmds

from stage.apps.validate_core import ValidateCore

class UvName(ValidateCore):

    nice_name = "默认UV集合名称"

    def __init__(self):
        super().__init__()
        self.autofixable = False
        self.ignorable = True
        self.selectable = True

        self.failed_meshes = []

    def collect(self):
        pass

    def validate(self):
        self.failed_meshes = self._check_for_uv_name()

        if self.failed_meshes:
            self.failed(msg=f"multiple UVs found on meshes: {self.failed_meshes}")
        else:
            self.passed()

    def select(self):
        cmds.select(self.failed_meshes)

    @staticmethod
    def _check_for_uv_name():
        iterations = om.MItDag(om.MItDag.kDepthFirst, om.MFn.kMesh)
        invalid_meshes = []

        while not iterations.isDone():
            dag_path = iterations.getPath()
            mesh_fn = om.MFnMesh(dag_path)
            uv_sets = mesh_fn.getUVSetNames()
            if 'map1' not in uv_sets:
                invalid_meshes.append(dag_path.fullPathName())
            iterations.next()
        return invalid_meshes
