import os
import hashlib
import logging
from pathlib import Path
from stage.common.constants import ObjectType

from stage.common import utils
from stage.common.settings import Settings

from stage.UI.dialog import message_box

LOG = logging.getLogger(__name__)

FEED = message_box.SMessageBox()


class User:
    object_type = ObjectType.USER

    config = {
        "resume": {
            "user": "Generic",
            "project": "",
            "subproject": "",
            "task": "",
            "category": "",
            "work": "",
            "version": ""
        }
    }

    def __init__(self, common_directory=None):
        """Initializes the User class."""
        super().__init__()


        self.resume = Settings()

        self.user_directory = None
        self.common_directory = (
            common_directory
        )
        self.commons = None

        self._active_user = None
        self._validate_user_data()

    @property
    def name(self):
        return self._active_user


    @property
    def last_project(self):

        return self.resume.get_property("project")

    @last_project.setter
    def last_project(self, value):
        self.resume.edit_property("project", value)

    @property
    def last_subproject(self):
        """The last subproject interacted with."""
        return self.resume.get_property("subproject")

    @last_subproject.setter
    def last_subproject(self, value):
        """Sets the last subproject.

        Args:
            value (str): The subproject name.
        """
        self.resume.edit_property("subproject", value)

    @property
    def last_task(self):
        """The last task interacted with."""
        return self.resume.get_property("task")

    @last_task.setter
    def last_task(self, value):
        """Set the last task.

        Args:
            value (str): The task name.
        """
        self.resume.edit_property("task", value)

    @property
    def last_category(self):
        """The last category interacted with."""
        return self.resume.get_property("category")

    @last_category.setter
    def last_category(self, value):
        """Set the last category.

        Args:
            value (str): The category name.
        """
        self.resume.edit_property("category", value)

    @property
    def last_mode(self):
        """The last mode interacted with."""
        return self.resume.get_property("mode")

    @last_mode.setter
    def last_mode(self, value):
        """Set the last mode.
        Args:
            value (str): The mode name.
        """
        self.resume.edit_property("mode", value)

    @property
    def last_task_mode(self):
        return self.resume.get_property("task_mode")

    @last_task_mode.setter
    def last_task_mode(self, value):
        self.resume.edit_property("task_mode", value)



    @property
    def last_work(self):
        """The last category interacted with."""
        return self.resume.get_property("work")

    @last_work.setter
    def last_work(self, value):

        self.resume.edit_property("work", value)

    @property
    def last_version(self):
        return self.resume.get_property("version")

    @last_version.setter
    def last_version(self, value):
        self.resume.edit_property("version", value)

    @property
    def expanded_subprojects(self):
        """The expansion states of subprojects."""
        return self.resume.get_property("expanded_subprojects", [])

    @expanded_subprojects.setter
    def expanded_subprojects(self, value):
        self.resume.edit_property("expanded_subprojects", value)

    @property
    def split_sizes(self):
        """The split sizes to apply to the main UI."""
        return self.resume.get_property("split_sizes", [])

    @split_sizes.setter
    def split_sizes(self, value):
        self.resume.edit_property("split_sizes", value)

    @property
    def visible_columns(self):
        """The column visibilities."""
        return self.resume.get_property("visible_columns", {})

    @visible_columns.setter
    def visible_columns(self, value):
        self.resume.edit_property("visible_columns", value)

    @property
    def tags(self):
        """The tags."""
        return self.resume.get_property("tags", {})

    @tags.setter
    def tags(self, value):
        self.resume.edit_property("tags", value)

    @property
    def column_sizes(self):
        """Column sizes."""
        return self.resume.get_property("column_sizes", {})

    @column_sizes.setter
    def column_sizes(self, value):
        self.resume.edit_property("column_sizes", value)

    @property
    def main_window_state(self):

        return self.resume.get_property("main_window_state", None)

    @main_window_state.setter
    def main_window_state(self, value):
          self.resume.edit_property("main_window_state", value)

    @property
    def ui_elements(self):
        """The GUI elements."""
        return self.resume.get_property("ui_elements", {})

    @ui_elements.setter
    def ui_elements(self, value):
        self.resume.edit_property("ui_elements", value)

    def get(self):
        """Return the currently active user."""
        return self._active_user

    def set(self, user_name, password=None, save_to_db=True, clear_db=False):

        self._active_user = user_name

        if save_to_db:
            self.resume.edit_property("user", self._active_user)
            _d_hash = self.__hash_pass(
                "{0}{1}".format(
                    self._active_user,
                    self.commons.users.get_property(self._active_user).get("pass"),
                )
            )
            self.resume.edit_property("user_dhash", _d_hash)
            self.resume.apply_settings()
        if clear_db:
            self.resume.edit_property("user", None)
            self.resume.edit_property("user_dhash", None)
            self.resume.apply_settings()

        return user_name, "Success"

    @staticmethod
    def __clamp_level(level):
        """Clamp the level between 0-3 and makes sure its integer."""
        return max(0, min(int(level), 3))

    @staticmethod
    def __hash_pass(password):

        return hashlib.sha1(str(password).encode("utf-8")).hexdigest()


    def _validate_user_data(self):

        _user_root = utils.get_home_dir()
        _user_dir = Path(_user_root, "stage")
        _user_dir.mkdir(exist_ok=True)
        self.user_directory = str(_user_dir)

        self.resume.settings_file = str(Path(self.user_directory, f"{os.environ.get('project_name')}_resume.json"))

        for key, val in self.config.get("resume").items():
            if not self.resume.get_property(key=key):
                self.resume.add_property(key=key, val=val)

        active_user = self.resume.get_property("user")
        state, _msg = self.set(active_user, save_to_db=False)
        if state == -1:
            self.set("Generic", save_to_db=False)

        self.resume.apply_settings()
        return 1
