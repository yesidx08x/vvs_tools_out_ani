import os
import re
from pathlib import Path
from stage.config.project_core import ProjectCore
from stage.server.api import ServerAPI

class Project(ProjectCore):
    #N:\NZT\assets\char\c014001lt\surface\look\main\workarea
    #N:\NZT\assets\char\c014001lt\mod\geo\main\workarea\v015
    #N:\NZT\assets\char\c014001lt\mod\geo\main\workarea

    #N:\NZT\assets\char\c014001lt\mod\geo\main\daily\v015

    #N:\NZT\assets\char\c014001lt\mod\geo\main\ok
    #N:\NZT\assets\char\c014001lt\mod\geo\main\ok\v015

    #N:\NZT\assets\char\c014001lt\mod\geo\main\source      zbrush file
    #N:\NZT\assets\char\c014001lt\mod\geo\main\source\v004 zbrush file version

    #N:\NZT\assets\char\c014001lt\mod\geo\main\upload
    #N:\NZT\assets\char\c014001lt\mod\geo\main\upload\v004

    #N:\NZT\assets\char\c014001lt\mod\modhair\main\daily
    #N:\NZT\assets\char\c014001lt\mod\modhair\main\OK
    #N:\NZT\assets\char\c014001lt\mod\modhair\main\workarea

    #N:\NZT\assets\char\c014001lt\mod\uv\main\daily
    #N:\NZT\assets\char\c014001lt\mod\uv\main\OK
    #N:\NZT\assets\char\c014001lt\mod\uv\main\workarea

    #N:\NZT\assets\char\c027001wlxwkind\surface\look\main\daily\v009
    #N:\NZT\assets\char\c027001wlxwkind\surface\look\main\ok
    #N:\NZT\assets\char\c027001wlxwkind\surface\look\main\ok\v021
    #N:\NZT\assets\char\c027001wlxwkind\surface\look\main\workarea\v021

    #N:\NZT\assets\char\c027001wlxwkind\assembly\rig\main\ok
    #N:\NZT\assets\char\c027001wlxwkind\assembly\rig\nemo\ok
    #N:\NZT\assets\char\c027001wlxwkind\assembly\cfx\main\ok

    #N:\NZT\assets\char\c027001wlxwkind\ani\face\main\ok\face01.pose
    #N:\NZT\assets\char\c027001wlxwkind\ani\motion\main\ok\huxi.anim
    #N:\NZT\assets\char\c027001wlxwkind\ani\phoneme\main\ok


    asset_work_path = 'R:/{project_entity}_{project_full_name}/VFX/Assets/CGassets/{asset_type_entity}/{asset_entity}/{category}/Work/{project_full_name}_{asset_entity}_{pipeline_abridge}_v0001|{project_full_name}_{asset_entity}_{pipeline_abridge}_lod{lod}_v0001'
    asset_publish_path = 'R:/{project_entity}_{project_full_name}/VFX/Assets/CGassets/{asset_type_entity}/{asset_entity}/{category}/Publish/{project_full_name}_{asset_entity}_{pipeline_abridge}_v0001|{project_full_name}_{asset_entity}_{pipeline_abridge}_lod{lod}'
    asset_publish_version_path = 'R:/{project_entity}_{project_full_name}/VFX/Assets/CGassets/{asset_type_entity}/{asset_entity}/{category}/Publish/{project_full_name}_{asset_entity}_{pipeline_abridge}_v0001|{project_full_name}_{asset_entity}_{pipeline_abridge}_lod{lod}_v0001'

    version_pattern = r'_v(\d{4})'
    version_format="v%04d"

    file_name_patterns = [
        r'^(?P<project_full_name>[^_]+)_(?P<asset_entity>[^_]+)_(?P<pipeline_abridge>[^_]+)_v(\d{4})$',
        r'^(?P<project_full_name>[^_]+)_(?P<asset_entity>[^_]+)_(?P<pipeline_abridge>[^_]+)_lod\d+_v(\d{4})$']

    _validations = {'mod': [
        "forbidden_nodes",
        "shape_names",
        "udim_crossing_uvs",
        "fps",
        "empty_groups",
        "unique_names",
        "non_centered_pivots",
        "overlapping_uvs",
        "turtle",
        "missing_uv",
        "ngons",
        "locked_normals",
        "mesh_transforms"]
    }

    _extracts={
        'mod': [
            "maya",
            "fbx",
            "usd",
            "alembic"
        ]
    }


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.api = ServerAPI()
        self.api.login('artist@vvs.com', '123456')

    def get_asset_infos(self, file_path):
        _file_path_obj = Path(file_path)
        work_path = _file_path_obj.parent
        base_name = _file_path_obj.stem
        match = next((m for m in (re.match(p, base_name) for p in self.file_name_patterns) if m), None)
        if not match:
            return

        self.file_infos = match.groupdict()

    @property
    def validations(self):
        if not self.file_infos:
            print('not file_infos')
            return

        project_name = self.file_infos['project_full_name']
        asset_name = self.file_infos['asset_entity']
        category_name = self.file_infos['pipeline_abridge']
        return self._validations[category_name]

    @property
    def extractors(self):
        if not self.file_infos:
            print('not file_infos')
            return

        project_name = self.file_infos['project_full_name']
        asset_name = self.file_infos['asset_entity']
        category_name = self.file_infos['pipeline_abridge']
        return self._extracts[category_name]

    def get_last_version(self):
        versions=[]
        project_name=self.file_infos.get('project_full_name') or os.environ['project_name']
        project_id = self.api.get_project_info(project_name).get('id')
        asset_name = self.file_infos.get('asset_entity')
        asset_infos = self.api.get_assets(project_id, asset_name)
        for asset in asset_infos:
            file_path=asset.get('path')
            versions.append(file_path)
        #file_list=sorted(versions, key=lambda x: int(re.search(self.version_pattern, x).group(1)), reverse=True)
        max_version = max(int(re.search(self.version_pattern, f).group(1)) for f in versions)+1

        return  self.version_format % max_version




