import logging
from collections import deque
from pathlib import Path
from stage.entities.entity import Entity
from stage.entities.task import Task
LOG = logging.getLogger(__name__)

class SubProduction(Entity):
    def __init__(self, parent_sub=None, metadata=None,**kwargs):
        super(SubProduction, self).__init__(**kwargs)
        self.__parent_sub = parent_sub
        self._sub_productions: dict = {}
        self._tasks: dict = {}
        self._metadata = metadata or {}


    @property
    def parent(self):
        """The Parent subproject."""
        return self.__parent_sub

    @property
    def subs(self):
        """All subprojects as dictionary."""

        return self._sub_productions

    @property
    def parent_sub(self):
        """The parent subproject."""
        return self.__parent_sub
    @property
    def type(self):
        """The type of the subproject."""
        return self._metadata.get('mode') or 'global'

    @property
    def tasks(self):
        return {task_name: task_obj for task_name, task_obj in self._tasks.items()}

    def add_sub_production(self, name,parent_sub=None, uid=None, **properties):
        new_sub = self.__build_sub_production(name,parent_sub,uid,**properties)
        return new_sub

    def __build_sub_production(self, name, parent_sub, uid,**properties):
        _metadata = self._metadata or {}
        properties = {k: v for k, v in properties.items() if v is not None}
        _metadata.update({key: data for key, data in properties.items()})
        sub_pr = SubProduction(
            name=name,
            parent_sub=parent_sub,
            uid=uid,
            metadata=_metadata)

        sub_pr.path = str(Path(self.path, name))
        self._sub_productions[name] = sub_pr

        return sub_pr

    def set_sub_tree(self, data):

        self._sub_productions = {}
        persistent_keys = ["id", "name", "path", "subs"]
        visited = set()
        queue = deque()
        self.id = data.get("id", None)
        self._name = data.get("name", None)


        queue.append([self, data.get("subs", [])])

        while queue:
            current = queue.popleft()
            sub, data_position = current

            for neighbour in data_position:
                if neighbour not in visited:
                    _deleted = neighbour.get("deleted", False)
                    _id = neighbour.get("id", None)
                    _name = neighbour.get("name", None)
                    _relative_path = neighbour.get("path", None)

                    properties = {}
                    for key, value in neighbour.items():
                        if key not in persistent_keys:
                            properties[key] = value

                    sub_project = sub.__build_sub_project(_name, sub, _id)

                    visited.add(neighbour)
                    queue.append([sub_project, neighbour.get("subs", [])])

    def add_task(self,
                 name,
                 creator,
                 artist,
                 categories,
                 task_type=None,
                 uid=None,
                 **properties
                 ):

        task_type = task_type
        relative_path = Path(self.path, name)
        properties = {k: v for k, v in properties.items() if v is not None}

        _task_id = uid or self.generate_id()
        _task = Task(
            name=name,
            creator=creator,
            artist=artist,
            categories=categories,
            path=self.path,
            parent_sub=self,
            task_id=_task_id,
            metadata_overrides=properties,

        )

        self._tasks[name] = _task

        return _task

    def scan_tasks(self):
        return self._tasks