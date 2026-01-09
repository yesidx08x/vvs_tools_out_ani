import os
import logging
from pathlib import Path
from stage.common.constants import ObjectType
from stage.entities.entity import Entity
from stage.apps.standalone.main import Dcc as StandaloneDcc

LOG = logging.getLogger(__name__)


class Work(Entity):
    object_type = ObjectType.WORK
    _standalone_handler = StandaloneDcc()

    def __init__(self, absolute_path, name=None,extension=None, dcc=None, dcc_handler=None, versions=None,
                 category=None, parent_task=None,_type=None, state='working'):

        super(Work, self).__init__()
        self.settings_file = Path(absolute_path)

        self._dcc_handler = dcc_handler or parent_task.parent_sub.parent_sub.parent_sub.dcc
        self._dcc = dcc
        self.extension = extension
        self._name = name
        self._creator = None
        self._category = category
        self._dcc_version = None
        self._versions = versions or []
        self._task_name = None
        self._task_id = None
        self._type = _type


        self._software_version = None

        self._parent_task = None
        if parent_task:
            self._relative_path = parent_task.path + '/' + parent_task.name + '/' + category
            self.set_parent_task(parent_task)
        self._state = state

        self.modified_time = None  # to compare and update if necessary

        # self.init_properties()

    def init_properties(self):
        """Initialize the properties of the work from the inherited dictionary."""
        self._name = self._name

    @property
    def extract(self):
        if self._versions:
            # return self._versions[-1].version
            if isinstance(self.all_versions[-1], tuple):
                return self.all_versions[-1][4]

            if isinstance(self.all_versions[-1], str):
                return self.all_versions[-1]
        else:
            return

    @property
    def path_type(self):
        return self._type

    @property
    def state(self):
        """Current state of the work."""
        return self._state

    @property
    def dcc_version(self):
        """Version of the dcc that the work is originated from."""
        return self._dcc_version

    @property
    def dcc_handler(self):
        """DCC handler object."""
        return self._dcc_handler

    @property
    def task_id(self):
        """Unique id of the task that the work belongs to."""
        return self._task_id

    @property
    def task_name(self):
        """Name of the task that the work belongs to."""
        return self._task_name

    @property
    def parent_task(self):
        """Parent task object that the work lives in."""
        return self._parent_task

    @property
    def creator(self):
        """The creator of the work."""
        return self._creator

    @property
    def category(self):
        """The category of the work."""
        return self._category


    @property
    def versions(self):
        """Versions of the work in a list."""
        # filter out the deleted versions
        return [version for version in self._versions if not version.deleted]

    @property
    def all_versions(self):
        """All versions of the work including deleted ones."""
        return self._versions

    @property
    def version_count(self):
        """Total number of versions belonging to the work."""
        return len(self._versions)

    @property
    def deleted(self):
        """Check if the work is deleted."""
        return False
        # return not self.has_valid_versions()

    @property
    def date_modified(self):
        """Return the date modified of the settings file."""
        return os.path.getmtime(self.settings_file.absolute())

    def has_valid_versions(self):
        """Check if the work has at least one valid version."""
        for version in self._versions:
            if not version.deleted:
                return True
        return False

    def set_parent_task(self, task_obj):
        """Set the parent task of the work."""
        self._parent_task = task_obj
        self._task_id = task_obj.id
        self._task_name = task_obj.name

    def get_last_version(self):
        """Return the last version of the work."""
        # First try to get the last version from the versions list. If not found, return 0.
        if self._versions:
            # return self._versions[-1].version
            if isinstance(self.all_versions[-1], tuple):
                return self.all_versions[-1][1]

            if isinstance(self.all_versions[-1], str):
                return self.all_versions[-1]
        else:
            return 0
    @property
    def master_path(self):
        if self._versions:
            # return self._versions[-1].version
            if isinstance(self.all_versions[-1], tuple):
                return self.all_versions[-1][3]

            if isinstance(self.all_versions[-1], str):
                return self.all_versions[-1]
        else:
            return 0

    def get_version(self, version_number):
        """Return the version dictionary by version number.

        Args:
            version_number (int): Version number.
        """
        for version in self._versions:
            if version.version == version_number:
                return version

    def show_file_folder(self):
        file_folder = self.settings_file.absolute()
        self._open_folder(file_folder)

    def new_version_from_path(self, full_path=None, template_file_path=None, notes=""):

        Path(full_path).parent.mkdir(parents=True, exist_ok=True)

        output_path = self._standalone_handler.save_as(
            full_path, source_path=template_file_path
        )
        version_obj = os.path.basename(output_path)

        self._versions.append(version_obj)
        return version_obj

    def new_version(self, full_path=None, file_format=None, notes=""):

        Path(full_path).parent.mkdir(parents=True, exist_ok=True)
        self._dcc_handler.pre_save()
        self._dcc_handler.new_scene()
        returned_output_path = self._dcc_handler.save_as(full_path)
        version_obj = os.path.basename(full_path)
        self._versions.append(version_obj)
        self._dcc_handler.post_save()
        return version_obj


    def increment_new_version(self, full_path=None, file_format=None, notes=""):

        Path(full_path).parent.mkdir(parents=True, exist_ok=True)
        self._dcc_handler.pre_save()
        returned_output_path = self._dcc_handler.save_as(full_path)
        version_obj = os.path.basename(full_path)
        self._versions.append(version_obj)
        self._dcc_handler.post_save()
        return version_obj


    def import_version(self, file_path,parameter=None,sequential=False):

        abs_path = Path(file_path)
        format = abs_path.suffix
        if format in self.dcc_handler.formats:
            element_type = 'source'

        elif format == '.abc':
            element_type = 'alembic'
        elif format == '.fbx':
            element_type = 'fbx'
        else:
            element_type = format.replace('.', '')

        _func = self._dcc_handler.ingests.get(element_type, None)
        if not _func:
            raise ValueError(f"Element type not supported: {element_type}")
        _ingest_obj = _func()

        if parameter:
            _ingest_obj.parameter = parameter

        _ingest_obj.sequential = sequential
        _ingest_obj.namespace = self.name
        _ingest_obj.category = self.category
        _ingest_obj.ingest_path = (
            abs_path
        )
        _ingest_obj.bring_in()

    def reference_version(self, file_path,extract=None, parameter=None,ingestor=None):

        abs_path = Path(file_path)
        format = abs_path.suffix
        if format in self.dcc_handler.formats:
            element_type = 'source'

        elif format == '.abc':
            element_type = 'alembic'
        elif format == '.fbx':
            element_type = 'fbx'
        else:
            element_type = format.replace('.', '')

        _func = self._dcc_handler.ingests.get(element_type, None)
        if not _func:
            raise ValueError(f"Element type not supported: {element_type}")



        _ingest_obj = _func()

        if parameter:
            _ingest_obj.parameter = parameter
        if extract:
            _ingest_obj.extract = extract
        _ingest_obj.namespace = self.name

        _ingest_obj.category = self.category
        _ingest_obj.ingest_path = (
            abs_path
        )
        _ingest_obj.reference()
