# -*- coding: utf-8 -*-
import os.path

import requests
from requests_toolbelt import MultipartEncoder

REMOTE_SERVER_URL = "http://192.168.100.27:8083"


# REMOTE_SERVER_URL = "http://127.0.0.1:8083"


class ServerAPI:

    def __init__(self):
        self.token = ''
        self.session = requests.Session()

    def login(self, email, password):

        try:
            response = self.session.post('%s/api/auth/login' % REMOTE_SERVER_URL,
                                         json={'email': email,
                                               'password': password
                                               }
                                         )

            self.token = response.json().get('token')

            return response.json()
        except requests.exceptions.RequestException as e:
            print(u"登录请求错误: {}".format(e))
            return None

    def get_token(self):
        return self.token

    def create_user(self, name, email, password, phoneNumber):
        try:
            response = self.session.post('%s/api/auth/register' % REMOTE_SERVER_URL,
                                         json={
                                             'name': name,
                                             'email': email,
                                             'password': password,
                                             'phoneNumber': phoneNumber,
                                         }
                                         )

            return response.json()
        except requests.exceptions.RequestException as e:
            print(u"注册请求错误: {}".format(e))
            return None

    def create_project(self, name, fps, resolutions, description):
        headers = {'Authorization': 'Bearer {}'.format(self.get_token()),
                   "Content-Type": "application/json"
                   }

        try:
            response = self.session.post('%s/api/projects/add' % REMOTE_SERVER_URL,
                                         json={'name': name,
                                               'fps': fps,
                                               'resolution': resolutions,
                                               'description': description
                                               },
                                         headers=headers
                                         )
            if response.status_code == 200:
                project_id = self.get_project_info(name).get('id')
                return project_id
            else:
                return response.json()
        except requests.exceptions.RequestException as e:
            print(u"创建项目请求错误: {}".format(e))
            return None

    def update_project(self, project_id, name, fps, resolutions, description):
        headers = {'Authorization': 'Bearer {}'.format(self.get_token()),
                   "Content-Type": "application/json"
                   }

        try:
            response = self.session.put('%s/api/projects/update' % REMOTE_SERVER_URL,
                                        json={'projectId': project_id,
                                              'name': name,
                                              'fps': fps,
                                              'resolution': resolutions,
                                              'description': description
                                              },
                                        headers=headers
                                        )
            return response.json()
        except requests.exceptions.RequestException as e:
            print(u"创建项目请求错误: {}".format(e))
            return None

    def delete_project(self, project_id):

        headers = {'Authorization': 'Bearer {}'.format(self.get_token())}
        try:
            response = requests.delete('%s/api/projects/delete/%s' % (REMOTE_SERVER_URL, project_id),
                                       headers=headers
                                       )
            return response.json()
        except requests.exceptions.RequestException as e:
            print(u"删除项目请求错误: {}".format(e))
            return None

    def get_projects(self):
        headers = {'Authorization': 'Bearer {}'.format(self.get_token()),
                   "Content-Type": "application/json"
                   }
        try:
            response = requests.get('%s/api/projects/all' % REMOTE_SERVER_URL, headers=headers)
            ret = response.json()['projects']
            return ret
        except requests.exceptions.RequestException as e:
            print(u"请求错误: {}".format(e))
            return None

    def get_project_info(self, project_name):

        headers = {'Authorization': 'Bearer {}'.format(self.get_token())
                   }
        try:
            response = requests.get('%s/api/projects/get/%s' % (REMOTE_SERVER_URL, project_name),
                                    headers=headers)

            if response.status_code == 200:
                ret = response.json().get('project')
                return ret
            else:
                return response.json()
        except requests.exceptions.RequestException as e:
            print(u"请求错误: {}".format(e))
            return None

    def create_asset(self,
                     project_id,
                     asset_name,
                     base_name,
                     version,
                     asset_step,
                     asset_type,
                     file_size,
                     file_path,
                     master_path,
                     thumbnail_path,
                     artist_name,
                     file_format,
                     extract,
                     mode,
                     description):
        fields = {
            'name': asset_name,
            'baseName': base_name,
            'version': str(version),
            'step': asset_step,
            'type': asset_type,
            'size': file_size,
            'path': file_path,
            'masterPath': master_path,
            'imageFile': (os.path.basename(thumbnail_path), open(thumbnail_path, 'rb'), 'image/jpeg'),
            'format': file_format,
            'extract': extract,
            'artist': artist_name,
            'mode': mode,
            'description': description,
            'projectId': str(project_id)
        }

        form_data = MultipartEncoder(fields)
        headers = {'Authorization': 'Bearer {}'.format(self.get_token()),
                   "Content-Type": form_data.content_type
                   }
        try:
            response = requests.post('%s/api/assets/add' % REMOTE_SERVER_URL,
                                     data=form_data,
                                     headers=headers
                                     )
            fields['imageFile'][1].close()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(u"创建资产请求错误: {}".format(e))
            return None

    def update_asset(self,
                     project_id,
                     asset_id,
                     asset_name,
                     base_name,
                     version,
                     asset_step,
                     asset_type,
                     file_size,
                     file_path,
                     thumbnail_path,
                     artist_name,
                     file_format,
                     extract,
                     description):
        fields = {
            'name': asset_name,
            'baseName': base_name,
            'version': version,
            'step': asset_step,
            'type': asset_type,
            'size': file_size,
            'path': file_path,
            'imageFile': (os.path.basename(thumbnail_path), open(thumbnail_path, 'rb'), 'image/jpeg'),  # 文件字段
            'format': file_format,
            'extract': extract,
            'artist': artist_name,
            'description': description,
            'projectId': str(project_id),
            'assetId': str(asset_id)
        }

        form_data = MultipartEncoder(fields)
        headers = {'Authorization': 'Bearer {}'.format(self.get_token()),
                   "Content-Type": form_data.content_type
                   }
        try:
            response = requests.put('%s/api/assets/update' % REMOTE_SERVER_URL,
                                    data=form_data,
                                    headers=headers
                                    )
            fields['imageFile'][1].close()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(u"创建资产请求错误: {}".format(e))
            return None

    def delete_asset(self, asset_id):

        headers = {'Authorization': 'Bearer {}'.format(self.get_token())}
        try:
            response = requests.delete('%s/api/assets/delete/%s' % (REMOTE_SERVER_URL, asset_id),
                                       headers=headers
                                       )
            return response.json()
        except requests.exceptions.RequestException as e:
            print(u"删除资产请求错误: {}".format(e))
            return None

    def get_asset_from_project(self, project_id):
        headers = {'Authorization': 'Bearer {}'.format(self.get_token())}
        try:
            response = requests.get('%s/api/assets/project/%s' % (REMOTE_SERVER_URL, project_id),
                                    headers=headers)
            ret = response.json()['assets']
            return ret
        except requests.exceptions.RequestException as e:
            print(u"请求资产错误: {}".format(e))
            return None

    def get_assets(self, project_id, category, type, asset_name, mode):
        headers = {'Authorization': 'Bearer {}'.format(self.get_token())}
        try:
            response = requests.get(
                '%s/api/assets/%s/%s/%s/%s/%s' % (REMOTE_SERVER_URL, project_id, category, type, asset_name, mode),
                headers=headers)
            if response.status_code == 200:
                ret = response.json()['assets']
                return ret
            elif response.status_code == 404:
                return None
            else:
                return response.json()

        except requests.exceptions.RequestException as e:
            print(u"请求资产错误: {}".format(e))
            return None

    def get_assets_from_basename(self, project_id, category, type, name, basename, mode):
        headers = {'Authorization': 'Bearer {}'.format(self.get_token())}
        try:
            response = requests.get(
                '%s/api/assets/%s/%s/%s/%s/%s/%s' % (REMOTE_SERVER_URL, project_id, category, type, name, basename,
                                                     mode),
                headers=headers)
            if response.status_code == 200:
                ret = response.json()['assets']
                return ret
            elif response.status_code == 404:
                return None
            else:
                return response.json()

        except requests.exceptions.RequestException as e:
            print(u"请求资产错误: {}".format(e))
            return None

    def get_category_assets(self, project_id, category, asset_name):
        headers = {'Authorization': 'Bearer {}'.format(self.get_token())}
        try:
            response = requests.get(
                '%s/api/assets/%s/%s/%s' % (REMOTE_SERVER_URL, project_id, category, asset_name),
                headers=headers)
            if response.status_code == 200:
                ret = response.json()['assets']
                return ret
            elif response.status_code == 404:
                return None
            else:
                return response.json()

        except requests.exceptions.RequestException as e:
            print(u"请求资产错误: {}".format(e))
            return None

    def get_image(self, image_path):
        # url = "http://192.168.100.27:8083/image/23eccf82-fdee-41ba-ae93-27292a633b15_test.jpg"
        url = "http://192.168.100.27:8083/image/23eccf82-fdee-41ba-ae93-27292a633b15_test.jpg"
        headers = {'Authorization': 'Bearer {}'.format(self.get_token())}
        local_save_path = "./downloaded_image.jpg"
        try:
            response = requests.get('%s/api/assets/image/%s' % (REMOTE_SERVER_URL, image_path),
                                    headers=headers)

            # 检查响应状态
            if response.status_code == 200:
                # 保存二进制内容到本地文件
                with open(local_save_path, "wb") as f:
                    f.write(response.content)
                print(f"图片已保存至：{local_save_path}")
            else:
                print(response.content)
                print(f"下载失败，状态码：{response.status_code}")

        except requests.exceptions.RequestException as e:
            print(f"请求发生异常：{str(e)}")
        return response.status_code

    def get_shots(self, project_id, category, sequence, shot, mode):
        headers = {'Authorization': 'Bearer {}'.format(self.get_token())}
        try:
            response = requests.get(
                '%s/api/shots/%s/%s/%s/%s/%s' % (REMOTE_SERVER_URL, project_id, sequence, shot, category, mode),
                headers=headers)
            if response.status_code == 200:
                ret = response.json()['shots']
                return ret
            elif response.status_code == 404:
                return None
            else:
                return response.json()

        except requests.exceptions.RequestException as e:
            print(u"请求镜头错误: {}".format(e))
            return None

    def get_shots_from_basename(self, project_id, category, base_name, mode):
        headers = {'Authorization': 'Bearer {}'.format(self.get_token())}
        try:
            response = requests.get(
                '%s/api/shots/%s/%s/%s/%s' % (REMOTE_SERVER_URL, project_id, base_name, category, mode),
                headers=headers)
            if response.status_code == 200:
                ret = response.json()['shots']
                return ret
            elif response.status_code == 404:
                return None
            else:
                return response.json()

        except requests.exceptions.RequestException as e:
            print(u"请求镜头错误: {}".format(e))
            return None

    def create_shot(self,
                    project_id,
                    sequence,
                    shot,
                    base_name,
                    version,
                    step,
                    file_size,
                    file_path,
                    master_path,
                    thumbnail_path,
                    artist_name,
                    file_format,
                    extract,
                    mode,
                    description):
        fields = {
            'sequence': sequence,
            'shot': shot,
            'baseName': base_name,
            'version': str(version),
            'step': step,
            'size': file_size,
            'path': file_path,
            'masterPath': master_path,
            'imageFile': (os.path.basename(thumbnail_path), open(thumbnail_path, 'rb'), 'image/jpeg'),
            'format': file_format,
            'extract': extract,
            'artist': artist_name,
            'mode': mode,
            'description': description,
            'projectId': str(project_id)
        }

        form_data = MultipartEncoder(fields)
        headers = {'Authorization': 'Bearer {}'.format(self.get_token()),
                   "Content-Type": form_data.content_type
                   }
        try:
            response = requests.post('%s/api/shots/add' % REMOTE_SERVER_URL,
                                     data=form_data,
                                     headers=headers
                                     )
            fields['imageFile'][1].close()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(u"创建镜头请求错误: {}".format(e))
            return None


if __name__ == '__main__':
    api = ServerAPI()

    api.create_user('artist','artist@vvs.com','123456','+9999999999')

    ret = api.login('artist@vvs.com', '123456')

    # # -------------------project----------------------
    # ret = api.create_project('TST', 25, '1920X1080', 'None')
    print(ret)
    # ret = api.get_projects()
    # ret = api.update_project(2, 'sdfsadf', 25, '1920','description')
    # ret = api.delete_project(3)
    ret = api.get_project_info('DM').get('id')

    print(ret)

    # -------------------asset----------------------
    # ret=api.create_asset(4,'Billboard001', 'mod', 'prp', '32mb', "R:/1031_XHRM/VFX/Assets/CGassets/Props/Billboard001/Model/Work/XHRM_Billboard001_mod_v0001.ma","D:/test.jpg", "weta", "ma",'publish','')
    # ret=api.update_asset(1,3,'ship', 'mod', 'prp', '32mb', "d:/stone.ma","C:/Users/soul/Pictures/thumbnail.jpg", "weta", "ma",'')
    # ret = api.delete_asset(2)
    # ret = api.get_asset_from_project(1)

    # assets = api.get_assets(4, 'mod', 'Props', 'Billboard001')
    # assets = api.get_assets_from_basename(4, 'mod', 'Props', 'Billboard001','XHRM_Billboard001_mod')
    # print(assets)
    # print(ret)
    # ret=api.get_image('a02fe1f3-b47f-44dc-bf92-b4fd737323a6_screencapture_o3tm9u9s.jpg')
    # print(ret)
    # print(ret)
    # ret=api.create_shot(4,
    #                   'AAB',
    #                   '0010',
    #                   'XHRM_GYD_4030_ani',
    #                   'v001',
    #                   'ani',
    #                   '20mb',
    #                   'R:/1031_XHRM/VFX/Sequences/GYD/4030/CG/Matchmove/Publish/v0001/XHRM_GYD_4030_ani.fbx',
    #                   'R:/1031_XHRM/VFX/Sequences/GYD/4030/CG/Matchmove/Publish/XHRM_GYD_4030_ani.fbx',
    #                   "C:/Users/soul/Pictures/thumbnail.jpg",
    #                   'weta',
    #                   'fbx',
    #                   'publish',
    #                   '')
    # ret=api.get_shots(4, 'ani', 'GYD', '4030')
    # ret=api.get_shots_from_basename(4,'ani','XHRM_GYD_4030_ani_smoke')
