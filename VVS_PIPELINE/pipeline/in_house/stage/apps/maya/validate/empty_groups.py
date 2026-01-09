

from maya import cmds

from stage.apps.validate_core import ValidateCore

class EmptyGroups(ValidateCore):


    nice_name = "空组"

    def __init__(self):
        super().__init__()
        self.autofixable = True
        self.ignorable = True
        self.selectable = True

        self.empty_groups = []

    def collect(self):
        """Collect data"""
        pass  # no need to collect data

    def validate(self):

        self.empty_groups = list(self._get_empty_groups())
        if self.empty_groups:
            self.failed(msg=f"Forbidden nodes found: {self.empty_groups}")
        else:
            self.passed()

    def fix(self):

        self.delete_object(self.empty_groups)
        self.validate()

    def select(self):

        cmds.select(self.empty_groups)

    def _get_empty_groups(self):

        transforms = cmds.ls(type="transform")
        for transform in transforms:
            if not cmds.listRelatives(transform, allDescendents=True):
                yield transform

    @staticmethod
    def delete_object(keyword, force=True):

        node_list = cmds.ls(keyword)
        non_existing = []
        for node in node_list:
            if cmds.objExists(node):
                if force:
                    cmds.lockNode(node, lock=False)
                cmds.delete(node)
            else:
                non_existing.append(node)
        return non_existing
