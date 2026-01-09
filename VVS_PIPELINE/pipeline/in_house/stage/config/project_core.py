
import importlib
from pathlib import Path



class ProjectCore:
    """Core class for validations."""

    nice_name: str = ""
    checked_by_default: bool = True

    def __init__(self, *args, **kwargs):

        self.name = str(Path(__file__).stem)
        self._args = args
        self._kwargs = kwargs


    def get_asset_infos(self, file_path):
        pass

    @property
    def validations(self):
        pass

    @property
    def extractors(self):
        pass