import os
import re
from collections import defaultdict
import glob
import logging
from pathlib import Path
from fnmatch import fnmatch

from stage.common.constants import ObjectType
from stage.entities.entity import Entity
from stage.entities.work import Work
from stage.common.utils import format_path_join

LOG = logging.getLogger(__name__)


class Category(Entity):
    """Category object to handle works and publishes under a task."""
    object_type = ObjectType.CATEGORY

    def __init__(self, parent_task, definition=None, **kwargs):
        """Initializes the Category object."""
        super().__init__(**kwargs)
        definition = definition or {}
        self._works = {}
        self._publishes = {}
        self._exporters={}

        self._abridge = definition.get(self.name, None)
        self.type = definition.get("type", None)
        self.display_name = definition.get("display_name", None)
        self.validations = definition.get("validate", [])
        self.extracts = definition.get("extracts", [])
        self.parent_task = parent_task
        self._relative_path = str(Path(self.parent_task._relative_path, self.parent_task.name, self.name))

        self._dcc = self.parent_task.parent_sub.parent_sub.parent_sub.dcc
        self.all_dcc_extensions = self.parent_task.parent_sub.parent_sub.parent_sub.all_dcc_extensions
        self.current_project_setting = self.parent_task.parent_sub.parent_sub.parent_sub.current_project_setting
        try:
            self.current_formats = self.dcc.formats
        except:
            self.current_formats = []

    @property
    def abridge(self):
        return self._abridge or self.name

    @property
    def works(self):
        """Return the works under the category."""
        self.scan_works()

        valid_works = {key: value for key, value in self._works.items() if
                       '.' + key.rsplit('/', 1)[1].lower() in self.current_formats}
        return {key: value for key, value in self._works.items()}
        return valid_works

    @property
    def all_works(self):
        """Return all the works under the category."""
        self.scan_works()
        return self._works

    def scan_works(self):

        _type=self.parent_task.parent_sub.name  #asset_type or sequence

        constructed_path = self.parent_task.metadata.get('work_path').format(
            category_folder=self.current_project_setting.get_category_folder(self.name), category=self.name,
            abridge=self.abridge, alias='{alias}', version='{version}')

        if hasattr(self.current_project_setting,'remap_category_path'):
            constructed_path=self.current_project_setting.remap_category_path(constructed_path)

        if os.environ.get('project_name').lower() == 'phhz':
            constructed_path = constructed_path.replace('Modeling', 'Model')
            constructed_path = constructed_path.replace('Shading', 'LookDev')

        all_extensions = [ext for exts in self.all_dcc_extensions.values() for ext in exts]
        extensions_pattern = '({})'.format('|'.join(ext.lstrip('.') for ext in all_extensions))

        _work_path = os.path.dirname(constructed_path)

        classified_files = self.current_project_setting.get_work_files(constructed_path, self.parent_task.name,
                                                                       self.abridge)

        if not classified_files:
            return

        for name, extensions in classified_files.items():
            for extension, files in extensions.items():
                # file_list = [file_name for _, file_name in sorted(files, key=lambda x: x[0])]
                existing_work = self._works.get(os.path.dirname(extension[1]), None)
                if not existing_work:
                    dcc = next((key for key, exts in self.all_dcc_extensions.items() if '.' + extension in exts), None)
                    if not dcc:
                        continue
                    work = Work(absolute_path=os.path.dirname(files[0][1]),
                                extension=extension,
                                name=name,
                                dcc=dcc,
                                versions=files,
                                category=self.name,
                                _type=_type,
                                parent_task=self.parent_task)
                    self._works[name + '/' + extension] = work

        return self._works

    @property
    def publishes(self):
        return self.scan_publishes('publish')

    @property
    def exporters(self):
        return self.scan_publishes('export')

    def scan_publishes(self, mode):
        _publishes={}

        category = self.name  # categor name
        abridge = self.abridge  # categor lower
        task_name = self.parent_task.name  # asset name
        task_type = self.parent_task.type  # asset or shot
        path = self.parent_task.parent_sub.name  # asset type, Props or Char

        _type = self.parent_task.parent_sub.name  # asset_type or sequence
        project_name = self.parent_task.parent_sub.parent_sub.parent_sub.name

        project_id = self.current_project_setting.api.get_project_info(project_name).get('id')

        if self.parent_task.type == 'asset':
            assets = self.current_project_setting.api.get_assets(project_id, abridge, path, task_name, mode)

            if not assets:
                # print('no publish assets: ',project_name,project_id, abridge,path,task_name)
                return {}
            if not isinstance(assets, list):
                LOG.warning(assets)
                return {}

            classified_files = defaultdict(lambda: defaultdict(list))

            for asset in assets:
                file_path = asset.get('path')
                name = asset.get('baseName')
                extension = asset.get('format')
                version = asset.get('version')
                note = asset.get('description')
                extract=asset.get('extract')
                _master_path = Path(asset.get('masterPath'))

                classified_files[name][extension].append((version, file_path, note,_master_path,extract))

            for name, extensions in classified_files.items():
                for extension, files in extensions.items():
                    # file_list = [file_name for _, file_name in sorted(files, key=lambda x: x[0])]
                    # existing_work = _publishes.get(_master_path.parent, None)
                    # if not existing_work:
                    dcc = next((key for key, exts in self.all_dcc_extensions.items() if '.' + extension in exts),
                               None)
                    work = Work(absolute_path=_master_path.parent, name=name, dcc=dcc,
                                versions=files,
                                extension=extension,
                                category = self.name,
                                _type=_type,
                                parent_task = self.parent_task,
                                state = mode)
                    _publishes[name + '/' + extension] = work

        if self.parent_task.type == 'shot':
            shots = self.current_project_setting.api.get_shots(project_id, abridge, path, task_name, mode)
            if not shots:
                # print('no publish shots: ', project_name, project_id, abridge, path, task_name)
                return {}

            if not isinstance(shots, list):
                if shots.get('status'):
                    print(shots)
                    return {}

            classified_files = defaultdict(lambda: defaultdict(list))

            for shot in shots:
                file_path = shot.get('path')
                name = shot.get('baseName')
                extension = shot.get('format')
                version = shot.get('version')
                note = shot.get('description')
                extract=shot.get('extract')
                _master_path = Path(shot.get('masterPath'))
                classified_files[name][extension].append((version, file_path, note,_master_path,extract))

            for name, extensions in classified_files.items():
                for extension, files in extensions.items():
                    # file_list = [file_name for _, file_name in sorted(files, key=lambda x: x[0])]
                    # existing_work = _publishes.get(_master_path.parent, None)
                    # if not existing_work:
                    dcc = next((key for key, exts in self.all_dcc_extensions.items() if '.' + extension in exts),
                               None)
                    work = Work(absolute_path=_master_path.parent
                                ,extension=extension,
                                name=name,
                                dcc=dcc,
                                versions=files,
                                category=self.name,
                                _type=_type,
                                parent_task=self.parent_task,
                                state=mode)
                    _publishes[name + '/' + extension] = work

        return _publishes

    def is_empty(self):

        return not bool(self.works)

    def create_work_from_template(self, work_file, constructed_name, template_file, notes=""):

        work_file_path = Path(work_file)
        work_path = work_file_path.parent

        work = Work(work_path.as_posix(), name=constructed_name, dcc=self.dcc, category=self.name,
                    parent_task=self.parent_task)

        work.new_version_from_path(full_path=work_file, template_file_path=template_file, notes=notes)

        return work

    def create_work(self, work_file, constructed_name, file_format=None, notes=""):

        work_file_path = Path(work_file)
        work_path = work_file_path.parent

        work = Work(work_path.as_posix(), name=constructed_name, dcc=self.dcc, category=self.name,
                    parent_task=self.parent_task)

        work.new_version(full_path=work_file, file_format=file_format, notes=notes)

        return work

    def get_relative_work_path(self, override_dcc=None):
        dcc = override_dcc or self.dcc
        return Path(self.path, dcc).as_posix()

    def construct_name(self, name):
        parts = [self.parent_task.name, self.name]
        if name:
            parts.append(name)
        return "_".join(parts)
