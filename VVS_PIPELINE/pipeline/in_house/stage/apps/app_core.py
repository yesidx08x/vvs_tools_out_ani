import os
import sys
import inspect
import importlib.util
from pathlib import Path

def import_from_path(module_name, file_path, cleanup=True):
    file_path = Path(file_path)

    # Get the parent directory of the file
    parent_dir = str(file_path.parent)

    # Check if the directory is already in sys.path
    was_in_sys_path = parent_dir in sys.path

    # Prepend the directory to sys.path if it's not already there
    if not was_in_sys_path:
        sys.path.insert(0, parent_dir)

    try:
        # Create a module spec
        spec = importlib.util.spec_from_file_location(module_name, file_path)

        # Create a new module based on the spec
        module = importlib.util.module_from_spec(spec)

        # Execute the module
        spec.loader.exec_module(module)

    finally:
        # Cleanup: Remove the directory from sys.path if it wasn't there before
        if cleanup and not was_in_sys_path and parent_dir in sys.path:
            sys.path.remove(parent_dir)

    return module

class AppCore():
    name = ""
    formats = []
    preview_enabled = True
    validations = {}
    extracts = {}
    ingests = {}
    extensions = {}
    custom_launcher = False

    EXTENSION_DICT = {
        "3dsmax": [".max"],
        "blender": [".blend"],
        "gaffer": [".gfr"],
        "houdini": [".hip", ".hipnc", ".hiplc"],
        "katana": [".katana"],
        "mari": [".mri"],
        "maya": [".ma", ".mb"],
        "nuke": [".nk"],
        "photoshop": [".psd", ".psb"],
        # "standalone": [".*"],
        "substance": [".spp"],
        "trigger": [".trg"],
        "fbx": [".fbx"],
        'alembic':[".abc"],
        'atom': [".atom"],
        'usd':[".usd"],
        'player':['.mov'],
        'uv':['.uv'],
        'shader':['.shader'],
        'jpg':['.jpg','jpeg'],
        'tif':['.tif','.tiff'],
    }

    # _DCC_NAME = os.getenv("STAGE_DCC").lower()
    _DCC_NAME=""

    @property
    def DCC_NAME(self):
        """Return the _DCC_NAME of the entity."""
        return self._DCC_NAME

    @DCC_NAME.setter
    def DCC_NAME(self, val):
        """Set the _DCC_NAME of the entity."""
        self._DCC_NAME = val

    @staticmethod
    def pre_publish():
        """Actions to be done before publishing."""
        pass

    @staticmethod
    def post_publish():
        """Actions to be done after publishing."""
        pass

    @staticmethod
    def pre_save():
        """Actions to be done before saving."""
        pass

    @staticmethod
    def post_save():
        """Actions to be done after saving."""
        pass

    @staticmethod
    def pre_open_issues():
        """Checks to be done before opening a file."""
        pass

    @staticmethod
    def pre_save_issues():
        """Checks to be done before saving a file."""
        pass

    @staticmethod
    def pre_publish_issues():
        """Checks to be done before publishing."""
        pass

    @staticmethod
    def get_main_window():
        """Returns the main window of the DCC"""
        pass

    @staticmethod
    def save_scene():
        """Saves the current file"""
        pass

    @staticmethod
    def save_as(file_path):
        """
        Saves the file to the given path
        Args:
            file_path: (String) File path that will be written
            file_format: (String) File format
            **extra_arguments: Compatibility arguments

        Returns:

        """
        pass

    @staticmethod
    def save_prompt():
        """Pop up the save prompt."""
        pass

    @staticmethod
    def open(file_path, force=True, **extra_arguments):
        """
        Opens the given file path
        Args:
            file_path: (String) File path to open
            force: (Bool) if true any unsaved changes on current scene will be lost
            **extra_arguments: Compatibility arguments for other DCCs

        Returns: None

        """
        pass

    @staticmethod
    def get_ranges():
        """Get the viewport ranges.
        Returns: (list) [<absolute range start>, <user range start>, <user range end>,
        <absolute range end>
        """
        pass

    @staticmethod
    def set_ranges(range_list):
        """Set the timeline ranges.

        Args:
            range_list: list of ranges as [<animation start>, <user min>, <user max>,
            <animation end>]

        Returns: None

        """
        pass

    @staticmethod
    def set_project(file_path):
        """
        Sets the project path
        Args:
            file_path: (String) File path to set as project

        Returns: None

        """
        pass

    @staticmethod
    def is_modified():
        """Returns True if the scene has unsaved changes"""
        False

    @staticmethod
    def get_scene_file():
        """Gets the current loaded scene file"""
        pass

    @staticmethod
    def get_project():
        """Return currently set project by dcc.
        If dcc does not support project management, return None.
        """
        return None

    @staticmethod
    def get_current_frame():
        """Return current frame in timeline.
        If dcc does not have a timeline, return None.
        """
        return None

    @staticmethod
    def get_current_selection():
        """Returns current selection or None if it is not supported"""
        return None

    @staticmethod
    def get_scene_fps():
        """Return the current FPS value set by DCC. None if not supported."""
        return None

    @staticmethod
    def set_scene_fps(fps_value):
        """
        Set the FPS value in DCC if supported.
        Args:
            fps_value: (integer) fps value

        Returns: None

        """
        pass

    @staticmethod
    def get_scene_cameras():
        """
        Return all the cameras in the scene.
        Returns: (list) List of camera names
        """
        pass

    @staticmethod
    def generate_thumbnail(file_path, width, height):
        """Generate a thumbnail for the given file path."""
        pass


    @staticmethod
    def generate_preview(name, folder, camera_code, resolution, range, settings=None):
        """
        Create a preview from the current scene
        Args:
            name: (String) Name of the preview
            folder: (String) Folder to save the preview
            camera_code: (String) Camera code. In Maya, this is the UUID of the camera transform node.
            resolution: (list) Resolution of the preview
            range: (list) Range of the preview
            settings: (dict) Global Settings dictionary
        """
        pass

    @staticmethod
    def get_dcc_version():
        """Returns the current DCC version"""
        pass

    @staticmethod
    def test():
        """Test function"""
        pass

    @staticmethod
    def launch():
        """Open main menu with DCC custom commands."""
        pass

    @classmethod
    def add_validation(cls, key, value):
        """Add a validation to the validations dictionary."""
        cls.validations[key] = value

    @classmethod
    def add_extract(cls, key, value):
        """Add an extract to the extracts dictionary."""
        cls.extracts[key] = value

    @classmethod
    def add_ingest(cls, key, value):
        """Add an ingest to the ingests dictionary."""
        cls.ingests[key] = value

    @classmethod
    def add_extension(cls, key, value):
        """Add an extension to the extensions dictionary."""
        cls.extensions[key] = value



