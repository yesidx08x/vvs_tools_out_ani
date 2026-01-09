
import re
from maya import cmds
from stage.apps.validate_core import ValidateCore

class Camera(ValidateCore):
    """Validate the Camera"""

    nice_name = "相机"

    def __init__(self):
        super(Camera, self).__init__()
        self.autofixable = True
        self.ignorable = False
        self.selectable = True
        self.camera_name=None
        self.bad_names = []
        self.parameter=None

    def collect(self):
        """Collect all camera nodes in the scene."""
        cameras = cmds.ls(type="camera")
        self.collection = [cmds.listRelatives(cam, parent=True)[0] for cam in cameras if cam not in ['frontShape', 'perspShape', 'sideShape', 'topShape']]

    def validate(self,parameter):
        """Validate the camera."""
        self.bad_names = []
        self.parameter = parameter
        self.camera_name = None
        self.collect()
        self.camera_name = parameter.get('name')
        if len(self.collection)<1:
            self.failed(msg="没有发现相机")
        elif len(self.collection)>1:
            self.failed(msg="发现多个相机: {}".format(self.collection))
        elif len(self.collection)==1:
            for transform in self.collection:
                if not self.check_name(transform):
                    self.bad_names.append(transform)
            if self.bad_names:
                self.failed(msg="相机名字不符合规范: {}".format(self.bad_names))
            else:
                self.passed()


    def fix(self):
        if self.camera_name:
            if len(self.bad_names)==1:
                cmds.rename(self.bad_names[0],self.camera_name)


    def select(self):
        cmds.select(self.bad_names)

    def check_name(self, cam):
        #print(cam,self.camera_name)
        if cam.lower() != self.camera_name.lower():
            return False
        return True
