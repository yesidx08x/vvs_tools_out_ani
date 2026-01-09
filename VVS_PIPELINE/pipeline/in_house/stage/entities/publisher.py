import re
import os
import logging
import shutil
from pathlib import Path
from stage.entities.publish import Publish
from stage.common.utils import get_file_size, format_path_join,save_json

LOG = logging.getLogger(__name__)


class Publisher:

    def __init__(self, project_object):

        self._project_object = project_object
        self._resolved_extracts = {}
        self._resolved_validators = {}
        self._file_infos = {}
        self._publish_file_name = None
        self._abs_publish_scene_folder = None
        self._dcc = project_object.dcc
        self._mode = None
        self._formats = project_object.dcc.formats

        self.stage_project_setting = project_object.current_project_setting
        self._publish_object = None
        self._resolve_outputs = []
        self._no_resolve_outputs = []
        self._extract_json={}

    @property
    def dcc(self):
        return self._dcc

    @property
    def mode(self):
        return self._mode

    @property
    def formats(self):
        return self._formats

    @property
    def validators(self):

        return self._resolved_validators

    @property
    def extracts(self):
        return self._resolved_extracts

    @property
    def publish_name(self):
        return self._publish_file_name

    @property
    def absolute_scene_path(self):
        return self._abs_publish_scene_folder

    @property
    def resolve_outputs(self):
        return self._resolve_outputs

    @property
    def file_infos(self):
        return self._file_infos

    def resolve(self, pipeline):
        self._resolve_outputs = []

        file_path = self._project_object.get_current_work()

        if file_path == (None, None):
            LOG.warning("No work object found. Aborting.")
            return False

        self._file_infos, self._mode = self.stage_project_setting.get_file_infos(file_path)

        if not self._file_infos:
            return False

        self.stage_project_setting.create_publish_data()

        self._resolved_extracts = {}
        self._resolved_validators = {}

        extracts = self.stage_project_setting.extracts
        dcc_extracts = self.dcc.extracts

        # for extract, handler in dcc_extracts.items():
        #
        #     if extract.lower() in extracts:
        #         resolved = handler()
        #         self._resolved_extracts[extract] = resolved

        for extract in extracts:
            if isinstance(extract, dict):
                for k, v in extract.items():
                    if k in list(self.dcc.extracts.keys()):
                        self._resolved_extracts[k] = [self.dcc.extracts[k](),v]
            else:
                if extract in list(self.dcc.extracts.keys()):
                        self._resolved_extracts[extract] = self.dcc.extracts[extract]()



        # self._resolved_extracts = dict(
        #     sorted(self._resolved_extracts.items(),
        #            key=lambda x: extracts.index(x[0].lower()))
        # )

        validations = self.stage_project_setting.validations
        for validation in validations:
            if isinstance(validation, dict):
                for k, v in validation.items():
                    if k in list(self.dcc.validations.keys()):
                        self._resolved_validators[k] = [self.dcc.validations[k](),v]
            else:
                if validation in list(self.dcc.validations.keys()):
                        self._resolved_validators[validation] = self.dcc.validations[validation]()


        # self._resolved_validators = dict(
        #     sorted(self._resolved_validators.items(),
        #            key=lambda x: validations.index(x[0].lower()))
        # )

        return self._file_infos

    def reserve(self, pipeline, publish_signal='publish'):
        self._resolve_outputs = []
        # project_name = self.file_infos['project']

        if self.mode == 'asset':
            asset_name = self.file_infos['task']
            abridge = self.file_infos['abridge']
            alias = self.file_infos.get('alias') or '{alias}'
            asset_dict = pipeline.get_asset(abridge, asset_name, alias,publish_signal)

            if publish_signal == 'publish':
                self._abs_publish_scene_folder = asset_dict['file_path']

            elif publish_signal == 'review':
                self._abs_publish_scene_folder = asset_dict['review_path']

            if os.environ.get('project_name').lower() == 'phhz':
                self._abs_publish_scene_folder = str(self._abs_publish_scene_folder).replace('Modeling', 'Model')
                self._abs_publish_scene_folder = str(self._abs_publish_scene_folder).replace('Shading', 'LookDev')

            self._publish_object = Publish(self._abs_publish_scene_folder,
                                           name=asset_name,
                                           base_name=asset_dict['base_name'],
                                           version=asset_dict['version'],
                                           user=asset_dict['artist'],
                                           abridge=asset_dict['category'],
                                           asset_type=asset_dict["type"],
                                           dailies_path=asset_dict["dailies_path"],
                                           category=self.stage_project_setting.category_mapping.get(abridge),
                                           )
        elif self.mode == 'shot':
            seq = self.file_infos['seq']
            shot = self.file_infos['shot']
            abridge = self.file_infos['abridge']
            alias = self.file_infos.get('alias') or '{alias}'
            shot_dict = pipeline.get_shot(abridge, seq, shot, alias,publish_signal)

            if publish_signal == 'publish':
                self._abs_publish_scene_folder = shot_dict['file_path']
                self._publish_object = Publish(self._abs_publish_scene_folder,
                                               sequence=seq,
                                               shot=shot,
                                               base_name=shot_dict['base_name'],
                                               version=shot_dict['version'],
                                               user=shot_dict['artist'],
                                               dailies_path=shot_dict["dailies_path"],
                                               abridge=abridge,
                                               category=self.stage_project_setting.category_mapping.get(abridge),
                                               )

            elif publish_signal == 'review':
                self._abs_publish_scene_folder = shot_dict['review_path']
                self._publish_object = Publish(self._abs_publish_scene_folder,
                                               sequence=seq,
                                               shot=shot,
                                               base_name=os.path.basename(shot_dict["dailies_path"]),
                                               version=shot_dict['version'],
                                               user=shot_dict['artist'],
                                               dailies_path=shot_dict["dailies_path"],
                                               abridge=abridge,
                                               category=self.stage_project_setting.category_mapping.get(abridge),
                                               )



        return self._abs_publish_scene_folder

    def extract_single(self, extract_object,parameter):
        if parameter:
            extract_object.parameter=parameter

        publish_path = Path(self._abs_publish_scene_folder).parent
        extract_object.category = self._publish_object.category
        extract_object.extract_folder = publish_path.as_posix()
        extract_object.extract_name = self._publish_object.base_name
        extract_object.extract()
        self._resolve_outputs.append([extract_object.resolve_output(),extract_object.__class__.__name__])

        if extract_object.extension_second:
            self._resolve_outputs.append([extract_object.resolve_output_second(),extract_object.__class__.__name__])
            self._no_resolve_outputs.append([extract_object.resolve_output_second(),extract_object.__class__.__name__])

        if extract_object.resolve_outputs:
            self._resolve_outputs+=[[extract,extract_object.__class__.__name__] for extract in extract_object.resolve_outputs]
            self._no_resolve_outputs+=[[extract,extract_object.__class__.__name__] for extract in extract_object.resolve_outputs]
            self._resolve_outputs.remove([extract_object.resolve_output(),extract_object.__class__.__name__])

        # print('test',self._resolve_outputs)
        # print('test',self._no_resolve_outputs)
        self._resolve_outputs=[resolve for resolve in self._resolve_outputs if os.path.exists(resolve[0])]

        self._extract_json.update(extract_object.extract_json)


    def publish(self,
                pipeline,
                image,
                notes=None,
                publish_signal='publish'
                ):

        if not self.resolve_outputs:
            return


        # print('test:',[item[0] for item in self._resolve_outputs if item not in self._no_resolve_outputs])

        project_name = os.environ.get('project_name')
        user_name = self._publish_object.user
        if self.mode == 'asset':
            try:
                pipeline.submit_asset(
                    project_name,
                    self._publish_object.asset_type,
                    self._publish_object.name,
                    self._publish_object.abridge,
                    [item[0] for item in self._resolve_outputs if item not in self._no_resolve_outputs],
                    filebox_sign='publish')
            except Exception as e:
                print('submit asset error', e)
                return

            try:
                pipeline.send_asset_message(
                    project_name,
                    self._publish_object.asset_type,
                    self._publish_object.name,
                    self._publish_object.abridge,
                    user_name,
                    notes,
                    [image] or []
                )
            except Exception as e:
                print('send message error:', e)
                return

        elif self.mode == 'shot':
            try:
                pipeline.submit_shot(
                    project_name,
                    self._publish_object.sequence,
                    self._publish_object.shot,
                    self._publish_object.abridge,
                    [item[0] for item in self._resolve_outputs if item not in self._no_resolve_outputs],
                    filebox_sign='publish')
            except Exception as e:
                print('submit shot error:', e)
                return

            try:
                pipeline.send_shot_message(
                    project_name,
                    self._publish_object.sequence,
                    self._publish_object.shot,
                    self._publish_object.abridge,
                    user_name,
                    notes,
                    [image] or []
                )
            except Exception as e:
                print('send message error:', e)
                return

        project_id = self.stage_project_setting.api.get_project_info(project_name).get('id')


        for resolve_output,class_name in self.resolve_outputs:
            if hasattr(self.stage_project_setting, 'folder_version_pattern'):
                master_path = format_path_join(Path(resolve_output).parent.parent, Path(resolve_output).name)

                with open(resolve_output, 'rb') as f_source, open(master_path, 'wb') as f_target:
                    shutil.copyfileobj(f_source, f_target)

                if class_name.lower() == 'source':
                    save_json(Path(resolve_output).parent.joinpath(Path(resolve_output).stem).with_suffix('.json'),
                              self._extract_json)
                    save_json(Path(master_path).parent.joinpath(Path(master_path).stem).with_suffix('.json'),
                              self._extract_json)

            # if publish_signal=='review':

            format = resolve_output.rsplit('.', 1)[-1]

            if class_name.lower() == 'source':
                publish_mode='publish'

            else:
                publish_mode='export'

            if self.mode == 'asset':
                ret = self.stage_project_setting.api.create_asset(project_id,
                                                                  self._publish_object.name,
                                                                  self._publish_object.base_name,
                                                                  self._publish_object.version,
                                                                  self._publish_object.abridge,
                                                                  self._publish_object.asset_type,
                                                                  get_file_size(resolve_output),
                                                                  resolve_output,
                                                                  master_path,
                                                                  image,
                                                                  self._publish_object.user,
                                                                  format,
                                                                  class_name.lower(),
                                                                  publish_mode,
                                                                  notes)
            elif self.mode == 'shot':
                ret = self.stage_project_setting.api.create_shot(project_id,
                                                                 self._publish_object.sequence,
                                                                 self._publish_object.shot,
                                                                 # self._publish_object.base_name,
                                                                 Path(master_path).stem,
                                                                 self._publish_object.version,
                                                                 self._publish_object.abridge,
                                                                 get_file_size(resolve_output),
                                                                 resolve_output,
                                                                 master_path,
                                                                 image,
                                                                 self._publish_object.user,
                                                                 format,
                                                                 class_name.lower(),
                                                                 publish_mode,
                                                                 notes)

            if ret.get('status') != 200:
                print(project_id, resolve_output)
                raise Exception(ret)



        return True

    def publish_review(self,
                       pipeline,
                       image,
                       notes=None,
                       publish_signal='publish'
                       ):
        if not self.resolve_outputs:
            return

        project_name = os.environ.get('project_name')
        user_name = self._publish_object.user
        if self.mode == 'asset':
            try:
                pipeline.submit_asset(
                    project_name,
                    self._publish_object.asset_type,
                    self._publish_object.name,
                    self._publish_object.abridge,
                    [item for item in self._resolve_outputs if item not in self._no_resolve_outputs],
                    filebox_sign='review')
            except Exception as e:
                print('submit asset error', e)
                return

            try:
                pipeline.send_asset_message(
                    project_name,
                    self._publish_object.asset_type,
                    self._publish_object.name,
                    self._publish_object.abridge,
                    user_name,
                    notes,
                    [image] or []
                )
            except Exception as e:
                print('send message error:', e)
                return

        elif self.mode == 'shot':
            try:
                pipeline.submit_shot(
                    project_name,
                    self._publish_object.sequence,
                    self._publish_object.shot,
                    self._publish_object.abridge,
                    [item for item in self._resolve_outputs if item not in self._no_resolve_outputs],
                    filebox_sign='review')
            except Exception as e:
                print('submit shot error:', e)
                return

            try:
                pipeline.send_shot_message(
                    project_name,
                    self._publish_object.sequence,
                    self._publish_object.shot,
                    self._publish_object.abridge,
                    user_name,
                    notes,
                    [image] or []
                )
            except Exception as e:
                print('send message error:', e)
                return

        project_id = self.stage_project_setting.api.get_project_info(project_name).get('id')

        for resolve_output in self.resolve_outputs:
            if hasattr(self.stage_project_setting, 'folder_version_pattern'):
                master_path = format_path_join(Path(resolve_output).parent.parent, Path(resolve_output).name)

                with open(resolve_output, 'rb') as f_source, open(master_path, 'wb') as f_target:
                    shutil.copyfileobj(f_source, f_target)
            else:
                master_path = ''
            dailies_path= Path(self._publish_object.dailies_path).parent.joinpath(Path(resolve_output).name)
            if not os.path.exists(os.path.dirname(dailies_path)):
                os.makedirs(os.path.dirname(dailies_path))


            with open(resolve_output, 'rb') as f_source, open(dailies_path, 'wb') as f_target:
                shutil.copyfileobj(f_source, f_target)

            format = resolve_output.rsplit('.', 1)[-1]
            if self.mode == 'asset':
                ret = self.stage_project_setting.api.create_asset(project_id,
                                                                  self._publish_object.name,
                                                                  self._publish_object.base_name,
                                                                  self._publish_object.version,
                                                                  self._publish_object.abridge,
                                                                  self._publish_object.asset_type,
                                                                  get_file_size(resolve_output),
                                                                  resolve_output,
                                                                  master_path,
                                                                  image,
                                                                  self._publish_object.user,
                                                                  format,
                                                                  'review',
                                                                  notes)
            elif self.mode == 'shot':
                ret = self.stage_project_setting.api.create_shot(project_id,
                                                                 self._publish_object.sequence,
                                                                 self._publish_object.shot,
                                                                 self._publish_object.base_name,
                                                                 self._publish_object.version,
                                                                 self._publish_object.abridge,
                                                                 get_file_size(resolve_output),
                                                                 resolve_output,
                                                                 master_path,
                                                                 image,
                                                                 self._publish_object.user,
                                                                 format,
                                                                 'review',
                                                                 notes)

            if ret.get('status') != 200:
                print(ret,project_id, resolve_output)
                raise Exception(ret)

        return True