import uuid
import os
import subprocess
import platform
from pathlib import Path
from stage.external import pyperclip
import logging
LOG = logging.getLogger(__name__)

class Entity:

    def __init__(self, name="", uid=None):

        self._id = uid
        self._relative_path = ""
        self._name = name
        self.__mode = "entity"
        self._dcc=None
        self.all_dcc_extensions={}
        self.current_project_setting=None
    @property
    def id(self):
        """Return the unique id of the entity."""
        if not self._id:
            self._id = self.generate_id()
        return self._id

    @id.setter
    def id(self, val):
        """Set the unique id of the entity."""
        self._id = val

    @property
    def path(self):
        """Return the relative path of the entity."""
        return str(Path(self._relative_path).as_posix())

    @path.setter
    def path(self, val):
        """Set the relative path of the entity."""
        self._relative_path = val

    @property
    def name(self):
        """Return the name of the entity."""
        return self._name

    @name.setter
    def name(self, val):
        """Set the name of the entity."""
        self._name = val

    @staticmethod
    def generate_id():
        """Generate a unique id for the entity."""
        return uuid.uuid1().time_low

    @property
    def dcc(self):
        return self._dcc

    @staticmethod
    def _open_folder(target):
        """Open the path in Windows Explorer(Windows) or Nautilus(Linux).

        Args:
            target (str): The path to open.
        """
        if Path(target).is_file():
            target = Path(target).stem
        if platform.system() == "Windows":
            os.startfile(target)
        elif platform.system() == "Linux":
            subprocess.Popen(["xdg-open", target])
        else:
            subprocess.Popen(["open", target])

    def copy_path_to_clipboard(self, file_or_folder_path):
        """Copy the path to the clipboard."""
        pyperclip.copy(file_or_folder_path.as_posix())

