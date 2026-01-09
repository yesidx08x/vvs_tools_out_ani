import logging
from pathlib import Path
from stage.entities import user
from stage.entities.sub_production import SubProduction
from stage.entities.publisher import Publisher

LOG = logging.getLogger(__name__)


class Project(SubProduction):

    def __init__(self, parent_sub=None, dcc=None, project=None, **kwargs):
        super(Project, self).__init__(**kwargs)
        self._dcc = dcc
        self.current_project_setting = project
        self.user = user.User()
        self.all_dcc_extensions = self.dcc.EXTENSION_DICT

        self.publisher = Publisher(self)

    def __validate_and_get_sub(self, parent_uid, parent_path):

        if not parent_uid and parent_path is None:
            raise Exception("Requires at least a parent uid or parent path ")
        if parent_uid is not None:
            parent = self.find_sub_by_id(parent_uid)
        else:
            parent = self.find_sub_by_path(parent_path)
        if parent == -1:
            LOG.error("Parent subproject does not exist")
        return parent

    def find_sub_by_id(self, uid):
        if self.id == uid:
            return self
        queue = list(self.subs.values())
        while queue:
            current = queue.pop(0)
            if current.id == uid:
                return current
            queue.extend(list(current.subs.values()))
        return -1

    def find_sub_by_path(self, path):
        if path in ("", "."):  # this is root
            return self
        queue = list(self.subs.values())
        while queue:
            current = queue.pop(0)
            if current.path == path:
                return current
            queue.extend(list(current.subs.values()))
        return -1

    def create_project(self, name):

        structure_data = {
            "name": name,
            "path": "",
            "mode": "root",
            "subs": [],
        }

        self.set_sub_tree(structure_data)

    def create_sub_production(self, name, parent_uid=None, parent_path=None, uid=None, **properties):

        parent_sub = self.__validate_and_get_sub(parent_uid, parent_path)
        if parent_sub == -1:
            return -1

        new_sub = parent_sub.add_sub_production(
            name, parent_sub=parent_sub, uid=uid, **properties
        )

        if new_sub == -1:
            return -1

        return new_sub

    def get_current_work(self):

        current_scene_path = self.dcc.get_scene_file()

        if not current_scene_path:
            return None, None

        return current_scene_path.replace('\\', '/')

