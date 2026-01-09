import os
import re
from datetime import datetime
from pathlib import Path
from pypinyin import pinyin, Style
from collections import defaultdict
from stage.config.project_core import ProjectCore
from stage.server.api import ServerAPI
from stage.common.utils import format_path_join


class Project(ProjectCore):
    version_count = 3
    file_version_pattern = rf'(v\d{{{version_count}}})'
    folder_version_pattern = rf'(v\d{{{version_count}}})'
    default_version = 'v' + str(1).zfill(version_count)
    max_version = 'v{}'

    # outliner_render='poly'
    outliner_render = 'render'  # export cache , assign shader

    asset_work_path = 'R:/{id}_{project}/VFX/Assets/CGassets/{type}/{task}/{category}/Work/{task}_{abridge}_{alias}_{version}'
    asset_publish_path = 'R:/{id}_{project}/VFX/Assets/CGassets/{type}/{task}/{category}/Publish/{version}/{task}_{abridge}_{alias}'

    shot_work_path = 'R:/{id}_{project}/VFX/Sequences/{seq}/{shot}/{category_folder}/{category}/Work/{seq}_{shot}_{abridge}_{alias}_{version}'
    shot_publish_path = 'R:/{id}_{project}/VFX/Sequences/{seq}/{shot}/{category_folder}/{category}/Publish/{version}/{seq}_{shot}_{abridge}_{alias}'

    asset_review_path = 'R:/{id}_{project}/Assets/CGassets/{type}/{task}/Review/{category}/Publish/Internal/{task}_{abridge}_{alias}_{version}'
    shot_review_path = 'R:/{id}_{project}/VFX/Sequences/{seq}/{shot}/Review/{category}/Publish/Internal/{seq}_{shot}_{abridge}_{alias}_{version}'

    dailies_asset_path = 'R:/{id}_{project}/ProductionFolder/VFX_Dailies/Date/' + datetime.now().strftime(
        "%Y%m%d") + '/{category}/{project}_{task}_{abridge}_{alias}_{version}'
    dailies_shot_path = 'R:/{id}_{project}/ProductionFolder/VFX_Dailies/Date/' + datetime.now().strftime(
        "%Y%m%d") + '/{category}/{project}_{seq}_{shot}_{abridge}_{alias}_{version}'

    template_path = 'L:/VVS_PIPELINE/pipeline/in_house/stage/config/template'
    template_file = '{template_path}/{project}/{app}/{category}/template.*'

    asset_file_name_patterns = [
        rf'^(?P<task>[^_]+)_(?P<abridge>[^_]+)_(?P<version>v\d{{{version_count}}})',
        rf'^(?P<task>[^_]+)_(?P<abridge>[^_]+)_(?P<alias>[^_]+)_(?P<version>v\d{{{version_count}}})']

    shot_file_name_patterns = [
        rf'^(?P<seq>[^_]+)_(?P<shot>[^_]+)_(?P<abridge>[^_]+)_(?P<version>v\d{{{version_count}}})',
        rf'^(?P<seq>[^_]+)_(?P<shot>[^_]+)_(?P<abridge>[^_]+)_(?P<alias>[^_]+)_(?P<version>v\d{{{version_count}}})']

    category_folder = {
        '2D': ['Comp', 'DMP', 'Roto', 'Paint', 'Graphics'],
        'CG': ['Animation', 'Cfx', 'EFX', 'Lighting', 'Matchmove', 'Layout', 'Environment']
    }

    asset_categories = {'Rig': 'rig', 'Modeling': 'mdl', 'Animation': 'anim', 'Texture': 'tex', 'Concept': 'cpt',
                        'Effects': 'efx', 'Shading': 'shd'}

    shot_categories = {'Matchmove': 'trk', 'Roto': 'rto', 'Lighting': 'lgt', 'IO': 'io', 'EFX': 'efx', 'Layout': 'lay',
                       'Comp': 'cmp', 'DMP': 'mp', 'Animation': 'anim', 'Paint': 'pnt'}

    asset_types = {'Environment': 'env', 'Ref': 'ref', 'Sets': 'set', 'Props': 'prp', 'Characters': 'chr',
                   'Effects': 'efx'}

    _validations = {
        'mdl': [
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
            "mesh_transforms",

            {
                'outliner': {
                    'ASSET': {
                        'geo': {
                            'proxy': {},
                            outliner_render: {}
                        },
                        'simproxy': {}
                    }
                },

                'units': 'cm'
            }
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
            "mesh_transforms",

            {
                'outliner': {
                    'ASSET': {
                        'geo': {
                            'proxy': {},
                            outliner_render: {}
                        },
                        'simproxy': {}
                    }
                },
                'units': 'cm'
            }

        ],
        'shd': [
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
            "mesh_transforms",

            {
                'outliner': {
                    'ASSET': {
                        'geo': {
                            'proxy': {},
                            outliner_render: {}
                        },
                        'simproxy': {}
                    }
                },

                'units': 'cm'
            }

        ],

        'rig': [
            "layer",
            "forbidden_nodes",
            "unique_names",
            "turtle",
            {
                'outliner': {
                    'ASSET': {
                        'geo': {
                            'proxy': {},
                            outliner_render: {}
                        },
                        'rig': {},
                        'simproxy': {}
                    }
                },

                'units': 'cm'
            }
        ],
        'trk': [
            "forbidden_nodes",
            "fps",
            "empty_groups",
            "unique_names",
            "turtle",
        ],
        'lay': [
            "forbidden_nodes",
            "fps",
            "empty_groups",
            "unique_names",
            "turtle",

        ],
        'anim': [
            "forbidden_nodes",
            "fps",
            "empty_groups",
            "unique_names",
            "turtle",
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
        'mdl':
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
        'shd':
            [
                "maya",
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

            ],
        'anim':
            [
                "maya",
            ],
        'efx':
            [
                "maya",
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

    _extracts_mode = {
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
        'mdl': 'Model',
        'rig': 'Rig',
        'tex': 'Texture',
        'shd': 'Shading',
        'anim': 'Animation',
        'lgt': 'Lighting',
        'lay': 'Layout',
        'trk': 'Matchmove',
        'efx': 'Fx',
        'cpt': 'Concept',
        'mp': 'DMP'
    }

    def __init__(self, dcc=None, pipeline=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mode = None
        self.api = ServerAPI()
        self.api.login('artist@vvs.com', '123456')

        if dcc.name == 'photoshop':
            self.alias = [self.chinese_2_pinyin(pipeline.get_current_user()[1])]

        else:
            self.alias = ['', 'lod50', 'lod100', 'lod200', 'lod300', 'lod500',
                          'lod999']  # 群集50  远景100  中远200  近景300  特写500 扫描999

    def create_publish_data(self):

        self._validations['lay'].append(

            {
                'outliner': {
                    'cam': {},
                    'lgt': {},
                    'mdl': {
                        'chr': {},
                        'env': {},
                        'prp': {}
                    }
                },
                'camera': {
                    'name': '{seq}_{shot}_{version}_cam'.format(
                        seq=self.get_seq() if self.mode == 'shot' else None,
                        shot=self.get_shot() if self.mode == 'shot' else None,
                        version=self.get_version()
                    )
                }
            }
        )

        self._validations['anim'].append(

            {
                'outliner': {
                    'cam': {},
                    'lgt': {},
                    'mdl': {
                        'chr': {},
                        'env': {},
                        'prp': {}
                    }
                },
                'camera': {
                    'name': '{seq}_{shot}_{version}_cam'.format(
                        seq=self.get_seq() if self.mode == 'shot' else None,
                        shot=self.get_shot() if self.mode == 'shot' else None,
                        version=self.get_version()
                    )
                }
            }
        )

        self._extracts['lay'].append(
            {
                'atom': {
                    'name': fr'(?P<name_space>\w+):(?P<transform_node>{self.outliner_top})'
                },
                'camera': {
                    'name': '{seq}_{shot}_{version}_cam'.format(
                        seq=self.get_seq() if self.mode == 'shot' else None,
                        shot=self.get_shot() if self.mode == 'shot' else None,
                        version=self.get_version()
                    )
                }
            }
        )

        self._extracts['anim'].append(
            {
                'abccache': {
                    'root': fr'(?P<name_space>\w+):(?P<transform_node>{self.outliner_top}$)',
                    'prefix': self.get_prefix_path(),
                    'name': '{seq}_{shot}_{name_space}'.format(
                        seq=self.get_seq() if self.mode == 'shot' else None,
                        shot=self.get_shot() if self.mode == 'shot' else None,
                        name_space='{name_space}')
                },
                'camera': {
                    'name': '{seq}_{shot}_{version}_cam'.format(
                        seq=self.get_seq() if self.mode == 'shot' else None,
                        shot=self.get_shot() if self.mode == 'shot' else None,
                        version=self.get_version()
                    )
                },
            }
        )

    # create import data
    def ingests(self, category, task):
        asset_type = task.metadata.get('asset_type')
        asset_type_abridge = self.asset_types.get(asset_type)
        self._ingests = {
            'rig': {
                'source': {'name_space': lambda s: s.split('_')[0] + '_%s' % asset_type_abridge},
            },
            'shd': {
                'source': {'name_space': lambda s: s.split('_')[0] + '_%s' % asset_type_abridge},
                'shader': {'name_space': lambda s: s.split('_')[0] + '_%s' % asset_type_abridge},
            },
            'lay': {
                'atom': '{name}:' + self.outliner_top,
                'source':  {'name_space': lambda s: ':'},
                'camera':  {'name_space': lambda s: ':'},
            },
            'anim': {
                'camera': {'name_space': lambda s: ':'},
                'abccache': {'name_space': lambda s: s.split('_', 2)[-1]},
                'source': {'name_space': lambda s: ':'},
            },
        }

        return self._ingests.get({v: k for k, v in self.category_mapping.items()}.get(category))

    def chinese_2_pinyin(self, name):
        initials = pinyin(name, style=Style.FIRST_LETTER)
        abbreviation = "".join([i[0] for i in initials])
        return abbreviation

    def remap_category_path(self, subcategory):
        return subcategory.replace('Shading', 'Lookdev').replace('Modeling', 'Model')

    def get_category_folder(self, subcategory):
        for category, subcategories in self.category_folder.items():
            if subcategory in subcategories:
                return category.replace('Shading', 'Lookdev')
        return 'CG'

    @property
    def outliner_top(self):
        return list(self.get_outliner().keys())[0]

    def get_outliner(self):
        outliner = {}
        for validation in self._validations.get(self.asset_categories.get('Modeling'), []):
            if isinstance(validation, dict):
                for k, v in validation.items():
                    if k == 'outliner':
                        outliner = v
                        break
        return outliner

    def get_prefix_path(self):

        def find_key_path(data, target_key, path=None):
            if path is None:
                path = []
            if isinstance(data, dict):
                for k, v in data.items():
                    current_path = path + [k]
                    if k == target_key:
                        return current_path
                    result = find_key_path(v, target_key, current_path)
                    if result:
                        return result
            return None

        outliner = self.get_outliner()

        render_path = find_key_path(outliner, self.outliner_render)

        result = '|' + '|'.join(render_path)
        return result

        # if render_path and len(render_path) >= 2:
        #     result = '|' + '|'.join(render_path[:-1]) + '|'
        #     return result
        # return None

    def get_shot_category_by_abridge(self, value):

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
        self.mode = mode
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

    def get_seq(self):
        return self.file_infos['seq'] if hasattr(self, 'file_infos') else None

    def get_shot(self):
        return self.file_infos['shot'] if hasattr(self, 'file_infos') else None

    def get_version(self):
        return self.file_infos['version'] if hasattr(self, 'file_infos') else None

    @property
    def validations(self):

        if not self.file_infos:
            print('not file_infos')
            return
        category_name = self.file_infos['abridge']
        return self._validations[category_name]

    @property
    def extracts(self):
        if not self.file_infos:
            print('not file_infos')
            return
        category_name = self.file_infos['abridge']
        return self._extracts[category_name]

    @property
    def extracts_mode(self):
        return self._extracts_mode

    # folder version
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

    def get_work_files(self, constructed_path, name, abridge):

        _work_path = os.path.dirname(constructed_path).replace('Shading', 'Lookdev')
        classified_files = defaultdict(lambda: defaultdict(list))
        regex = re.compile(r'^(.*)({0})'.format(self.file_version_pattern))
        if not os.path.exists(_work_path):
            return

        for file in os.listdir(_work_path):
            base, ext = os.path.splitext(file)
            file_infos = base.split('_')
            # if file_infos[0] != os.getenv('project_name') or (file_infos[2] not in self.asset_categories.values() and file_infos[2] not in self.shot_categories.values()):
            #     print('get work files error',os.getenv('project_name'),file_infos[2])
            #     continue
            file_matches = regex.match(base)
            if file_matches:
                if ((name in base.split('_') or name in base.split('.')) and (
                        abridge in base.split('_') or abridge in base.split('.'))):
                    base_name = file_matches.group(1)[:-1]
                    version = file_matches.group(2)
                    note = ''
                    classified_files[base_name][ext.replace('.', '')].append(
                        (version, format_path_join(_work_path, file), note))
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
                    max_version = str(max(list(set(version_nums))) + 1).zfill(self.version_count)
                    new_folder_version_str = re.sub(r'\d+', max_version, folder_version_str)
                    new_file = file.replace(folder_version_str, new_folder_version_str).replace('Shading', 'Lookdev')
            new_file_path = Path(new_file)
        else:
            max_version = str(1).zfill(self.version_count)
            new_file_path = Path(file_path.format(version=self.default_version, alias='{alias}').replace('Shading',
                                                                                                         'Lookdev')).parent.joinpath(
                base_name)
        return new_file_path, base_name, self.max_version.format(max_version)

    def get_asset_last_version(self, file_path, asset_type, mode):
        project_name = self.file_infos.get('project') or os.environ['project_name']
        project_id = self.api.get_project_info(project_name).get('id')
        if not project_id:
            project_id = self.api.create_project(project_name, os.getenv('fps'), os.getenv('resolutions'), 'None')

        asset_name = self.file_infos.get('task')
        category_name = self.file_infos['abridge']
        base_name = self.file_infos.get('base_name')
        db_asset_infos = self.api.get_assets_from_basename(project_id, category_name, asset_type, asset_name, base_name,
                                                           mode)
        return self.get_publish_version(file_path, db_asset_infos)

    def get_shot_last_version(self, file_path, mode):

        project_name = self.file_infos.get('project') or os.environ['project_name']
        project_id = self.api.get_project_info(project_name).get('id')
        if not project_id:
            project_id = self.api.create_project(project_name, os.getenv('fps'), os.getenv('resolutions'), 'None')
        sequence = self.file_infos.get('seq')
        shot = self.file_infos.get('shot')
        category_name = self.file_infos['abridge']
        base_name = self.file_infos.get('base_name')
        db_shot_infos = self.api.get_shots_from_basename(project_id, category_name, base_name, mode)
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
