
import os
from collections import defaultdict
from .version import __version__
try:
    from libs.cg_api import api as cg_api
except :
    from libs.cg_api import api_test as cg_api
from stage.server.cache import PipelineCache
from stage.addons.addon_core import AddonCore
CGTW_ROOT = os.path.dirname(os.path.abspath(__file__))
pipeline_cache = PipelineCache()
class CgteamworkAddon(AddonCore):
    label = "cgteawork Connect"
    name = "cgteamwork"
    version = __version__
    num=0
    shots_artist=defaultdict(lambda: defaultdict(list))
    assets_artist=defaultdict(lambda: defaultdict(list))
    def __init__(self, production):
        self.project = production
        self.stage_project_setting= self.project.current_project_setting
        self.current_project = self.get_current_project(os.environ.get('project_name'))

    def initialize(self):
        pass

    @property
    def host(self):
        pass

    @classmethod
    @pipeline_cache
    def get_current_user(self):
        user = cg_api.get_login_user()
        user_cn=cg_api.get_user_cn_name(user)
        return user,user_cn

    @classmethod
    def get_current_user_name(self):
        user = cg_api.get_login_user()
        user_cn = cg_api.get_user_cn_name(user)
        return user_cn

    def get_projects(self):
        return cg_api.get_all_project()

    @pipeline_cache
    def get_current_project(self,project_name):

        return cg_api.get_project_by_tag(project_name)

    @pipeline_cache
    def get_all_assets(self,project_entity):
        return cg_api.get_all_assets(project_entity)

    @pipeline_cache
    def get_all_shots(self,project_entity):
        return cg_api.get_all_shots(project_entity)

    def _get_assets_sub(self):

        assets_sub = self.project.subs.get("Assets") or self.project.create_sub_production(
            "Assets",
            parent_path="",
            mode="asset"
        )
        return assets_sub

    def _get_shots_sub(self):

        shots_sub = self.project.subs.get("Shots") or self.project.create_sub_production(
            "Shots",
            parent_path="",
            mode="shot"
        )

        return shots_sub

    @pipeline_cache
    def _get_asset_categories(self,project_entity):

        return cg_api.get_asset_links(project_entity)

    @pipeline_cache
    def _get_shot_categorise(self,project_entity):
        return cg_api.get_shot_links(project_entity)

    def get_asset_work_path(self,asset_type,asset_name):

        return self.stage_project_setting.asset_work_path.format(id=self.current_project.get('project.entity'),
                                                                  project=self.current_project.get('project.tag'),
                                                                  type=asset_type,
                                                                  task=asset_name,
                                                                  abridge='{abridge}',
                                                                  category='{category}',
                                                                  version='{version}',
                                                                  alias='{alias}'
                                                                  )


    # def get_asset_publish_path(self,asset_type,asset_name):
    #
    #     return self.stage_project_setting.asset_publish_path.format(project_entity=self.current_project.get('project.entity'),
    #                                                               project_full_name=self.current_project.get('project.full_name'),
    #                                                               asset_type_entity=asset_type,
    #                                                               asset_entity=asset_name,
    #                                                               pipeline_abridge='{abridge}',
    #                                                               category='{category}',
    #                                                                 alias='{alias}'
    #                                                               )
    def get_shot_work_path(self,seq,shot):
        return self.stage_project_setting.shot_work_path.format(id=self.current_project.get('project.entity'),
                                                                project=self.current_project.get('project.tag'),
                                                                seq=seq,
                                                                shot=shot,
                                                                category_folder='{category_folder}',
                                                                abridge='{abridge}',
                                                                category='{category}',
                                                                version='{version}',
                                                                alias='{alias}'
                                                                )

    def _new_asset(self,assets_sub,asset,categories):
        asset_id = asset["asset.id"]
        asset_name = asset["asset.entity"]
        asset_type = asset["asset_type.entity"]
        creator=asset["asset.create_by"]
        artist = asset["task.artist"]
        asset_cn_name = asset["asset.cn_name"]
        if artist not in self.assets_artist[asset_name][asset_type]:
            self.assets_artist[asset_name][asset_type].append(artist)

        if asset_type:
            if assets_sub.subs.get(asset_type) is None:
                sub = self.project.create_sub_production(
                    asset_type, parent_path="Assets"
                )
            else:
                sub = self.project.subs["Assets"].subs[asset_type]
        else:
            sub = assets_sub

        work_path=self.get_asset_work_path(asset_type,asset_name)
        # publish_path = self.get_asset_publish_path(asset_type, asset_name)

        task = sub.add_task(asset_name,
                            creator,
                            ','.join(self.assets_artist[asset_name][asset_type]),
                            categories=categories,
                            uid=asset_id,
                            asset_cn_name=asset_cn_name,
                            asset_type=asset_type,
                            work_path=work_path)
        return task

    def _new_shot(self,shots_sub,shot,categories):

        shot_id = shot["shot.id"]
        shot_name = shot["shot.entity"]
        seq_name=shot["seq.entity"]
        seq_id=shot["seq.id"]
        creator = shot["seq.create_by"]
        artist = shot["task.artist"]
        if artist not in self.shots_artist[seq_name][shot_name]:
            self.shots_artist[seq_name][shot_name].append(artist)
        query_sub = shots_sub

        is_episodic=False
        if is_episodic:
            episode_data={"id":"01","name":"EP01"}
            episode = episode_data["name"]
            if query_sub.subs.get(episode) is None:
                query_sub = self.project.create_sub_production(
                    episode,
                    parent_path=query_sub.path,
                    uid=episode_data["id"],
                    mode="episode",
                )
            else:
                query_sub = query_sub.subs[episode]

        if query_sub.subs.get(seq_name) is None:
            query_sub = self.project.create_sub_production(
                seq_name,
                parent_path=query_sub.path,
                uid=seq_id,
            )
        else:
            query_sub = query_sub.subs[seq_name]

        work_path = self.get_shot_work_path(seq_name, shot_name)
        task = query_sub.add_task(
            shot_name,
            creator,
            ','.join(self.shots_artist[seq_name][shot_name]),
            categories=categories,
            uid=shot_id,
            work_path=work_path
        )


        return task


    def create_project_data(self,__refresh_cache__=False):
        project_name = self.current_project.get('project.tag')
        project_entity= self.current_project.get('project.entity')

        asset_categories = self._get_asset_categories(project_entity,__refresh_cache__=__refresh_cache__)
        shot_categories=self._get_shot_categorise(project_entity,__refresh_cache__=__refresh_cache__)

        self.project.create_project(project_name)

        #Asset
        all_assets = self.get_all_assets(project_entity,__refresh_cache__=__refresh_cache__)
        all_shots = self.get_all_shots(project_entity,__refresh_cache__=__refresh_cache__)

        assets_sub = self._get_assets_sub()
        shots_sub = self._get_shots_sub()

        for asset in all_assets:
            self._new_asset(assets_sub,asset,asset_categories)

        if all_shots:
            for shot in all_shots:
                self._new_shot(shots_sub,shot,shot_categories)


    def get_asset(self, abridge, asset_name,alias,mode):

        ret={}
        user = cg_api.get_login_user()

        asset_dict=cg_api.get_asset_infos_by_tag(self.current_project.get('project.tag'),abridge, asset_name)

        if not asset_dict:
            return

        file_path=self.stage_project_setting.asset_publish_path.format(
            id=self.current_project.get('project.entity'),
            project=self.current_project.get('project.tag'),
            type=asset_dict["asset_type.entity"],
            task=asset_name,
            abridge=abridge,
            category=asset_dict["pipeline.entity"],
            version='{version}',
            alias=alias
        )
        review_version=cg_api.get_asset_submit_rules(self.current_project.get('project.tag'), asset_dict["asset_type.entity"], asset_name, abridge)[0].rsplit('_',1)[-1]
        # review_file_path = cg_api.get_asset_infos_by_tag(self.current_project.get('project.tag'), abridge, asset_name)

        review_file_path = self.stage_project_setting.asset_review_path.format(
            id=self.current_project.get('project.entity'),
            project=self.current_project.get('project.tag'),
            type=asset_dict["asset_type.entity"],
            task=asset_name,
            abridge=abridge,
            category=asset_dict["pipeline.entity"],
            version=review_version,
            alias=alias
        )

        dailies_path = self.stage_project_setting.dailies_asset_path.format(
            id=self.current_project.get('project.entity'),
            project=self.current_project.get('project.tag'),
            type=asset_dict["asset_type.entity"],
            task=asset_name,
            abridge=abridge,
            category=asset_dict["pipeline.entity"],
            version=review_version,
            alias=alias

        )


        source_file_path,base_name,version=self.stage_project_setting.get_asset_last_version(file_path,asset_dict["asset_type.entity"],mode)

        # patterns = cg_api.get_asset_submit_rules(self.current_project.get('project.full_name'),
        #                                       asset["asset_type.entity"],
        #                                       asset_name,
        #                                       abridge
        #                                       )



        ret['name']=asset_name
        ret['version']=version
        ret['base_name']=base_name
        ret['category']=abridge
        ret['type']=asset_dict["asset_type.entity"]
        ret["file_path"] = source_file_path
        ret["review_path"] = review_file_path
        ret["dailies_path"] = dailies_path
        ret['artist']=user
        print('get_asset',ret)
        return ret

    def get_shot(self, abridge, seq,shot,alias,mode):

        ret={}
        user = cg_api.get_login_user()

        shot_dict=cg_api.get_shot_infos_by_tag(self.current_project.get('project.tag'),abridge, seq,shot)

        if not shot_dict:
            return

        file_path=self.stage_project_setting.shot_publish_path.format(
            id=self.current_project.get('project.entity'),
            project=self.current_project.get('project.tag'),
            seq=shot_dict['seq.entity'],
            shot=shot_dict['shot.entity'],
            abridge=abridge,
            category=shot_dict["pipeline.entity"],
            alias=alias,
            version='{version}',
            category_folder=self.stage_project_setting.get_category_folder(self.stage_project_setting.get_shot_category_by_abridge(abridge))
        )
        print(shot_dict,file_path)


        review_version=cg_api.get_shot_submit_rules(self.current_project.get('project.tag'), seq, shot, abridge)[0].rsplit('_',1)[-1]

        review_file_path = self.stage_project_setting.shot_review_path.format(
            id=self.current_project.get('project.entity'),
            project=self.current_project.get('project.tag'),
            seq=shot_dict['seq.entity'],
            shot=shot_dict['shot.entity'],
            abridge=abridge,
            category=shot_dict["pipeline.entity"],
            alias=alias,
            version=review_version,
            category_folder=self.stage_project_setting.get_category_folder(
                self.stage_project_setting.get_shot_category_by_abridge(abridge))
        )
        # review_file_path = cg_api.get_shot_review_dir_by_tag(self.current_project.get('project.tag'), seq, shot, abridge)
        dailies_path =self.stage_project_setting.dailies_shot_path.format(
            id=self.current_project.get('project.entity'),
            project=self.current_project.get('project.tag'),
            seq=shot_dict['seq.entity'],
            shot=shot_dict['shot.entity'],
            abridge=abridge,
            category=shot_dict["pipeline.entity"],
            alias=alias,
            version=review_version,
            category_folder=self.stage_project_setting.get_category_folder(
                self.stage_project_setting.get_shot_category_by_abridge(abridge))
        )

        source_file_path,base_name,version=self.stage_project_setting.get_shot_last_version(file_path,mode)


        ret['sequence']=seq
        ret['shot']=shot
        ret['version']=version
        ret['base_name']=base_name
        ret['category']=abridge
        ret["file_path"] = source_file_path
        ret["review_path"] = review_file_path
        ret["dailies_path"] = dailies_path
        ret['artist']=user
        print('get_shot',ret)
        return ret

    def submit_asset(self,
                     project_tag,
                         asset_type,
                         asset_name,
                         asset_step,
                         publish_files,
                         filebox_sign='publish'):
        cg_api.submit_asset(
            project_tag,
            asset_type,
            asset_name,
            asset_step,
            publish_files,
            filebox_sign)

    def send_asset_message(self,
            project_tag,
            asset_type,
            asset_name,
            asset_step,
            user_name,
            notes,
            imgages
        ):
        cg_api.send_asset_message_by_tag(
            project_tag,
            asset_type,
            asset_name,
            asset_step,
            user_name,
            notes,
            imgages
        )

    def submit_shot(self,
                     project_tag,
                     sequence,
                     shot,
                     step,
                     publish_files,
                     filebox_sign='publish'):
        cg_api.submit_shot(
            project_tag,
            sequence,
            shot,
            step,
            publish_files,
            filebox_sign)

    def send_shot_message(self,
                           project_tag,
                           sequence,
                           shot,
                           step,
                           user_name,
                           notes,
                           imgages
                           ):
        cg_api.send_shot_message_by_tag(
            project_tag,
            sequence,
            shot,
            step,
            user_name,
            notes,
            imgages
        )
