import os
import logging
import socket
import shutil
from pathlib import Path

from stage.common.constants import ObjectType
from stage.entities.entity import Entity

LOG = logging.getLogger(__name__)

class Publish(Entity):

    object_type = ObjectType.WORK

    def __init__(self, absolute_path, abridge=None,name=None,sequence=None,shot=None,base_name=None,asset_type=None,user=None,version=None, category=None,review_path=None,dailies_path=None):
        super(Publish, self).__init__()
        self._name = name
        self._sequence = sequence
        self._shot = shot
        self._base_name = base_name
        self._user = user
        self._category = category
        self._absolute_path = absolute_path
        self._abridge = abridge
        self._asset_type = asset_type
        self._version = version
        self._review_path = review_path
        self._dailies_path = dailies_path



    @property
    def category(self):
        return self._category

    @property
    def user(self):
        return self._user

    @property
    def absolute_path(self):
        return self._absolute_path

    @property
    def asset_type(self):
        return self._asset_type
    @property
    def abridge(self):
        return self._abridge
    @property
    def base_name(self):
        return self._base_name

    @property
    def version(self):
        return self._version

    @property
    def sequence(self):
        return self._sequence

    @property
    def shot(self):
        return self._shot

    @property
    def review_path(self):
        return self._review_path
    @property
    def dailies_path(self):
        return self._dailies_path
