import logging
from stage.common.constants import ObjectType
from stage.entities.entity import Entity
from stage.entities.category import Category
LOG = logging.getLogger(__name__)

class Task(Entity):
    object_type = ObjectType.TASK

    def __init__(
        self,
        name=None,
        creator=None,
        artist=None,
        categories=None,
        path="",
        parent_sub=None,
        task_id=None,
        metadata_overrides=None,
    ):
        super().__init__()
        self._parent_sub = parent_sub
        self._name =  name
        self._nice_name =  name
        self._creator = creator
        self._artist = artist
        self._works = {}
        self._publishes = {}
        self._task_id =  task_id
        self._relative_path = path
        self._state =  "active"
        self._deleted = False



        self.metadata_overrides = metadata_overrides or {}
        self._type = self.metadata.get("mode")
        self._categories = {}
        self.build_categories(categories or [])


    @property
    def name(self):
        """Name of the task."""
        return self._name

    @property
    def nice_name(self):
        """Nice name of the task."""
        return self._nice_name
    @property
    def artist(self):
        return self._artist

    @property
    def id(self):
        """Unique ID of the task."""
        return self._task_id

    @property
    def type(self):
        """Type of the task."""
        return self._type

    @property
    def creator(self):
        """Creator of the task."""
        return self._creator

    @property
    def categories(self):
        """Available categories in the task."""
        return self._categories

    @property
    def parent_sub(self):
        """Parent sub of the task."""
        return self._parent_sub

    @property
    def metadata(self):
        """Metadata of the task."""
        if self._parent_sub:
            _metadata = self._parent_sub._metadata
            _metadata.update({key: data for key, data in self.metadata_overrides.items()})
            return _metadata


    @property
    def state(self):
        """State of the task."""
        return self._state

    @property
    def deleted(self):
        """Deleted state of the task."""
        return self._deleted

    def build_categories(self, category_list):

        self._categories = {}

        for category, abridge in category_list.items():
            category_definition={category:abridge}
            self._categories[category] = Category(name=category, parent_task=self ,definition=category_definition)

        return self._categories