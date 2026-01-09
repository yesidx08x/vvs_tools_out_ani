import os
import re
from datetime import datetime
import getpass
from pathlib import Path
from collections import defaultdict
from stage.server.api import ServerAPI
from stage.common.utils import format_path_join
from stage.config.project_core import ProjectCore

class Project(ProjectCore):
    file_version_pattern = r'(v\d{4})'
    folder_version_pattern = r'(v\d{4})'
    default_version='v0001'
    max_version = 'v{}'

    asset_work_path = 'R:/{id}_{project}/VFX/Assets/CGassets/{type}/{task}/{category}/Work/{task}_{abridge}_{alias}_{version}'
    asset_publish_path = 'R:/{id}_{project}/VFX/Assets/CGassets/{type}/{task}/{category}/Publish/{version}/{task}_{abridge}_{alias}'

    shot_work_path = 'R:/{id}_{project}/VFX/Sequences/{seq}/{shot}/{category_folder}/{category}/Work/{seq}_{shot}_{abridge}_{alias}_{version}'
    shot_publish_path = 'R:/{id}_{project}/VFX/Sequences/{seq}/{shot}/{category_folder}/{category}/Publish/{version}/{seq}_{shot}_{abridge}_{alias}'

    asset_review_path = 'R:/{id}_{project}/Assets/CGassets/{type}/{task}/Review/{category}/Publish/Internal/{project}_{task}_{abridge}_{alias}_{version}'
    shot_review_path = r'R:/{id}_{project}/VFX/Sequences/{seq}/{shot}/Review/{category}/Publish/Internal/{project}_{seq}_{shot}_{abridge}_{alias}_{version}'

    dailies_asset_path = 'R:/{id}_{project}ProductionFolder/VFX_Dailies/Date/' + datetime.now().strftime(
        "%Y%m%d") + '/{category}/{project}_{task}_{abridge}_{alias}_{version}'
    dailies_shot_path = 'R:/{id}_{project}/ProductionFolder/VFX_Dailies/Date/' + datetime.now().strftime(
        "%Y%m%d") + '/{category}/{project}_{seq}_{shot}_{abridge}_{alias}_{version}'

    asset_file_name_patterns = [
        r'^(?P<task>[^_]+)_(?P<abridge>[^_]+)_(?P<version>v\d{4})',
        r'^(?P<task>[^_]+)_(?P<abridge>[^_]+)_(?P<alias>[^_]+)_(?P<version>v\d{4})']

    shot_file_name_patterns = [
        r'^(?P<seq>[^_]+)_(?P<shot>[^_]+)_(?P<abridge>[^_]+)_(?P<version>v\d{4})',
        r'^(?P<seq>[^_]+)_(?P<shot>[^_]+)_(?P<abridge>[^_]+)_(?P<alias>[^_]+)_(?P<version>v\d{4})']

    category_folder = {'2D': ['Comp', 'DMP', 'Roto', 'Paint', 'Graphics'],
                       'CG': ['Animation', 'Cfx', 'EFX', 'Lighting', 'Matchmove', 'Layout', 'Environment']
                       }

    asset_categories = {'Rig': 'rig', 'Model': 'mod', 'Animation': '', 'Texture': 'tex', 'Concept': 'cpt',
                        'Lookdev': 'ldv', 'Effects': 'efx'}
    shot_categories = {'Matchmove': 'trk', 'Roto': 'rto', 'Lighting': 'lgt', 'IO': 'io', 'EFX': 'efx', 'Layout': 'lay',
                       'Comp': 'cmp', 'DMP': 'mp', 'Animation': 'ani', 'Paint': 'pnt'}
    asset_types = ['Environment', 'Ref', 'Sets', 'Props', 'Characters', 'Effects']

    _validations = {
        'mod': [
            "history",
            "layer",
            "forbidden_nodes",
            "shape_names",
            "udim_crossing_uvs",
            "empty_groups",
            "unique_names",
            "non_centered_pivots",
            "overlapping_uvs",
            "uv_set",
            "uv_name",
            "freeze",
            "turtle",
            "missing_uv",
            "ngons",
            "locked_normals",
            "mesh_transforms"
        ],
        'tex': [
            "history",
            "layer",
            "forbidden_nodes",
            "shape_names",
            "udim_crossing_uvs",
            "empty_groups",
            "unique_names",
            "non_centered_pivots",
            "overlapping_uvs",
            "uv_set",
            "uv_name",
            "freeze",
            "turtle",
            "missing_uv",
            "ngons",
            "locked_normals",
            "mesh_transforms"
        ],
        'ldv': [
            "history",
            "layer",
            "forbidden_nodes",
            "shape_names",
            "udim_crossing_uvs",
            "empty_groups",
            "unique_names",
            "non_centered_pivots",
            "overlapping_uvs",
            "uv_set",
            "uv_name",
            "freeze",
            "turtle",
            "missing_uv",
            "ngons",
            "locked_normals",
            "mesh_transforms"
        ],
        'rig': [
            "layer",
            "forbidden_nodes",
            "unique_names",

        ],
        'trk': [
            "forbidden_nodes",
            "fps",
            "empty_groups",
            "unique_names",
            "turtle",
            "mesh_transforms"
        ],
        'lay': [
            "forbidden_nodes",
            "fps",
            "empty_groups",
            "unique_names",
            "turtle",
            "mesh_transforms"
        ],
        'ani': [
            "forbidden_nodes",
            "fps",
            "empty_groups",
            "unique_names",
            "turtle",
            "mesh_transforms"
        ],

        'lgt': [

        ],
        'cpt': [

        ],
        'mp': [

        ],
        'efx': [

        ]
    }

    _extracts = {
        'mod':
            [
                "maya",
                "alembic"
            ],
        'rig':
            [
                "maya",
            ],
        'tex':
            [
                "maya",
            ],
        'ldv':
            [
                "maya",
                "uv",
                "shader"
            ],
        'trk':
            [
                "maya",
                "fbx"
            ],
        'lay':
            [
                "maya",
                "fbx"
            ],
        'ani':
            [
                "maya",
                "fbx"
            ],
        'efx':
            [
                "maya",
                "fbx",
                "alembic"
            ],
        'lgt':
            [
                "maya",

            ],
        'cpt':
            [
                "photoshop",
            ],
         'mp':
            [
                "photoshop",
                "jpg",
                "tif"
            ],
    }
    _extracts_mode={
        'mp':
            {
                'publish':
                    [
                        "photoshop",
                        "tif"
                    ],
                'review':
                    [
                        "jpg",
                    ]
            }
    }

    category_mapping = {
        'mod': 'Model',
        'rig': 'Rig',
        'tex': 'Texture',
        'ldv': 'Lookdev',
        'ani': 'Animation',
        'lgt': 'Lighting',
        'lay': 'Layout',
        'trk': 'Matchmove',
        'efx': 'Fx',
        'cpt':'Concept',
        'mp':'DMP'
    }


    def __init__(self,dcc=None,pipeline=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.api = ServerAPI()
        self.api.login('artist@vvs.com', '123456')

        if dcc.name=='photoshop':
            self.alias = [getpass.getuser()]
            # self.alias = [self.chinese_2_pinyin(pipeline.get_current_user()[1])]
        else:
            self.alias = ['', 'lod50', 'lod100', 'lod200', 'lod300', 'lod500','lod999']  # 群集50  远景100  中远200  近景300  特写500

    def get_category_folder(self,subcategory):
        for category, subcategories in self.category_folder.items():
            if subcategory in subcategories:
                return category

        return 'CG'
    def get_shot_category_by_abridge(self,value):

        for category, abridge in self.shot_categories.items():
            if abridge == value:
                return category
        return None

    def get_file_infos(self, file_path):

        if '/Assets/' in file_path:
            mode = 'asset'
            infos = self.get_asset_infos(file_path)

        if '/Sequences/' in file_path:
            mode = 'shot'
            infos = self.get_shot_infos(file_path)

        return infos, mode

    def get_asset_infos(self, file_path):
        _file_path_obj = Path(file_path)
        work_path = _file_path_obj.parent
        base_name = _file_path_obj.stem

        match = next((m for m in (re.search(p, base_name) for p in self.asset_file_name_patterns) if m), None)
        if not match:
            return
        self.file_infos = match.groupdict()
        regex = re.compile(r'^(.*)_({})'.format(self.file_version_pattern))

        self.file_infos['base_name'] = regex.match(base_name).group(1)
        print('asset file infos: ', self.file_infos)
        return self.file_infos

    def get_shot_infos(self, file_path):
        _file_path_obj = Path(file_path)
        work_path = _file_path_obj.parent
        base_name = _file_path_obj.stem

        match = next((m for m in (re.search(p, base_name) for p in self.shot_file_name_patterns) if m), None)
        if not match:
            return
        self.file_infos = match.groupdict()
        regex = re.compile(r'^(.*)_({})'.format(self.file_version_pattern))
        self.file_infos['base_name'] = regex.match(base_name).group(1)
        print('shot file infos: ', self.file_infos)
        return self.file_infos

    @property
    def validations(self):
        if not self.file_infos:
            print('not file_infos')
            return
        category_name = self.file_infos['abridge']
        return self._validations[category_name]

    @property
    def extractors(self):
        if not self.file_infos:
            print('not file_infos')
            return
        category_name = self.file_infos['abridge']
        return self._extracts[category_name]

    @property
    def extracts_mode(self):
        return self._extracts_mode

    #folder version
    # def get_work_files(self,constructed_path, name, abridge):
    #     version_path = constructed_path.split('/{version}/')[0]
    #     version_pattern = self.folder_version_pattern
    #     classified_files = defaultdict(lambda: defaultdict(list))
    #     if not os.path.exists(_work_path):
    #        return
    #     for dir in os.listdir(version_path):
    #         dir_matches = re.match(version_pattern, dir)
    #         if not dir_matches:
    #             continue
    #         version = dir_matches.group(1)
    #         for file in os.listdir(format_path_join(version_path, dir)):
    #             for file_pattern in self.asset_file_name_patterns + self.shot_file_name_patterns:
    #                 base, ext = os.path.splitext(file)
    #                 file_matches = re.match(file_pattern, base)
    #                 if file_matches:
    #                     if ((name in base.split('_') or name in base.split('.')) and (abridge in base.split('_') or abridge in base.split('.'))):
    #                         classified_files[base][ext.replace('.', '')].append((version, format_path_join(version_path, dir, file)))
    #                         break
    #     return classified_files

    def get_work_files(self,constructed_path, name, abridge):
        _work_path = os.path.dirname(constructed_path)
        classified_files = defaultdict(lambda: defaultdict(list))
        regex = re.compile(r'^(.*)({0})'.format(self.file_version_pattern))
        if not os.path.exists(_work_path):
            return

        for file in os.listdir(_work_path):
            base, ext = os.path.splitext(file)
            file_matches = regex.match(base)
            if file_matches:
                if ((name in base.split('_') or name in base.split('.')) and (
                        abridge in base.split('_') or abridge in base.split('.'))):
                    base_name = file_matches.group(1)[:-1]
                    version = file_matches.group(2)
                    note=''
                    classified_files[base_name][ext.replace('.', '')].append((version, format_path_join(_work_path, file),note))
        return classified_files

    def get_publish_version(self, file_path, db_infos):
        base_name = self.file_infos.get('base_name')
        new_file = None
        max_version = 1
        if db_infos:
            version_nums = [0]
            file_versions = [x.get('path') for x in db_infos]
            for file in file_versions:
                folder_matches = re.search(self.folder_version_pattern, file)
                if folder_matches:
                    folder_version_str = folder_matches.group(1)
                    version_num = int(re.search(r'\d+', folder_version_str).group(0))
                    version_nums.append(version_num)
                    max_version = str(max(list(set(version_nums))) + 1).zfill(4)
                    new_folder_version_str = re.sub(r'\d+', max_version, folder_version_str)
                    new_file = file.replace(folder_version_str, new_folder_version_str)
            new_file_path = Path(new_file)
        else:
            max_version = str(1).zfill(4)
            new_file_path = Path(file_path.format(version=self.default_version,alias='{alias}')).parent.joinpath(base_name)
        return new_file_path, base_name, self.max_version.format(max_version)

    def get_asset_last_version(self, file_path, asset_type,mode):
        project_name = self.file_infos.get('project') or os.environ['project_name']
        project_id = self.api.get_project_info(project_name).get('id')
        if not project_id:
            project_id = self.api.create_project(project_name, os.getenv('fps'), os.getenv('resolutions'), 'None')

        asset_name = self.file_infos.get('task')
        category_name = self.file_infos['abridge']
        base_name = self.file_infos.get('base_name')
        db_asset_infos = self.api.get_assets_from_basename(project_id, category_name, asset_type, asset_name, base_name,mode)
        return self.get_publish_version(file_path, db_asset_infos)

    def get_shot_last_version(self, file_path,mode):

        project_name = self.file_infos.get('project') or os.environ['project_name']
        project_id = self.api.get_project_info(project_name).get('id')
        if not project_id:
            project_id = self.api.create_project(project_name, os.getenv('fps'), os.getenv('resolutions'), 'None')
        sequence = self.file_infos.get('seq')
        shot = self.file_infos.get('shot')
        category_name = self.file_infos['abridge']
        base_name = self.file_infos.get('base_name')
        db_shot_infos = self.api.get_shots_from_basename(project_id, category_name, base_name,mode)

        return self.get_publish_version(file_path, db_shot_infos)

    def match_to_dict(self, match, check_duplicate_placeholders=True):

        data = {}
        for key, value in match.groupdict().items():
            if check_duplicate_placeholders:
                if key in data:
                    if data[key] != value:
                        raise (
                            'Different extracted values for placeholder '
                            '{0!r} detected. Values were {1!r} and {2!r}.'
                            .format(key, data[key], value)
                        )
            data[key] = value
        return data

if __name__ == '__main__':
    p = Project()
    path = 'R:/1031_XHRM/VFX/Sequences/GYD/4030/CG/Matchmove/Work/XHRM_GYD_4030_trk_v0001.ma'
    a = p.get_asset_infos(path)
