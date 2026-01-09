from maya import cmds

from stage.apps.validate_core import ValidateCore

class Freeze(ValidateCore):


    nice_name = "冻结"

    def __init__(self):
        super().__init__()
        self.autofixable = True
        self.ignorable = True
        self.selectable = True

        self.freeze_groups = []

    def collect(self):
        """Collect data"""
        pass  # no need to collect data

    def validate(self):

        self.freeze_groups = list(self._get_not_freeze_transforms())
        if self.freeze_groups:
            self.failed(msg=f"Forbidden nodes found: {self.freeze_groups}")
        else:
            self.passed()

    def fix(self):
        for group in self.freeze_groups:
            cmds.makeIdentity(group,apply=True, t=1, r=1, s=1, n=0, pn=1)
        self.validate()

    def select(self):

        cmds.select(self.freeze_groups)

    def _get_not_freeze_transforms(self):
        default_transforms = ['persp', 'top', 'front', 'side']
        transforms = list(set(cmds.ls(type="transform"))-set(default_transforms))
        for transform in transforms:
            if (cmds.getAttr(transform + '.translate') != [(0.0, 0.0, 0.0)]) or (cmds.getAttr(transform + '.rotate') != [(0.0, 0.0, 0.0)]) or (cmds.getAttr(transform + '.scale') != [(1.0, 1.0, 1.0)]):
                    yield transform


