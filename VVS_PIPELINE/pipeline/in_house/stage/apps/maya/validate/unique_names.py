"""Validation for unique names in Maya scene"""

import maya.cmds as cmds
import  maya.OpenMaya as om
from stage.apps.validate_core import ValidateCore


class UniqueNames(ValidateCore):
    """Validate class for Maya"""

    nice_name = "同名"

    def __init__(self):
        super(UniqueNames, self).__init__()

        self.autofixable = True
        self.ignorable = True
        self.selectable = True

        # dynamic variables
        self.non_unique_nodes = []

    def collect(self):
        """Collect data"""
        self.collection = map( str, self.iter_nonUnique_names() ) # everything in the scene

    def validate(self):
        """Validate unique names in Maya scene."""
        self.non_unique_nodes = []
        self.collect()
        self._get_non_unique_names()
        if self.non_unique_nodes:
            self.failed(msg=f"发现同名: {self.non_unique_nodes}")
        else:
            self.passed()

    def _get_non_unique_names(self):
        """Returns the non-unique names in the scene"""
        self.non_unique_nodes = []
        for obj in self.collection:
                self.non_unique_nodes.append(obj)

        return self.non_unique_nodes

    def fix(self):
        """Auto fix the validation."""
        self.make_names_unique()

    def select(self):
        """Selects the objects with non-unique names"""
        cmds.select(cl=True)
        cmds.select(self.non_unique_nodes)
        pass

    @staticmethod
    def iter_nonUnique_names():
        iter_nodes = om.MItDag(om.MItDag.kDepthFirst,
                               om.MFn.kTransform)  # type=MFn.kTransform )  #NOTE: only dag objects can have non-unique names...  despite the fact that the hasUniqueName method lives on MFnDependencyNode (wtf?!)
        while not iter_nodes.isDone():
            mobject = iter_nodes.currentItem()
            if not om.MFnDependencyNode(
                    mobject).hasUniqueName():  # thankfully instantiating MFn objects isn't slow - just MObject and MDagPath
                dag_node = om.MFnDagNode(mobject)
                full_path = dag_node.fullPathName()
                yield full_path
            iter_nodes.next()

    def make_names_unique(self):

        collection = []
        for obj in self.collection:
            pathway = obj.split("|")
            if len(pathway) > 1:
                self.unique_name(pathway[-1])
                collection.append(obj)
        collection.reverse()
        old_names = []
        new_names = []
        for xe in collection:
            pathway = xe.split("|")
            old_names.append(pathway[-1])
            new_names.append(cmds.rename(xe, self.unique_name(pathway[-1])))
        return old_names, new_names