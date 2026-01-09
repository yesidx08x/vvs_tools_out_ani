from pathlib import Path
import shutil
import logging
from stage.apps.app_core import AppCore

LOG = logging.getLogger(__name__)


class Dcc(AppCore):
    name = "Standalone"
    formats = [""]
    preview_enabled = False

    @staticmethod
    def save_as(file_path, source_path=None, **extra_arguments):

        if not source_path:
            LOG.warning("Source path is not defined. Creating Test File.")
            with open(file_path, "w") as f:
                f.write("test")
            return file_path

        if not Path(source_path).exists():
            LOG.warning(f"Source path does not exist: {source_path}")
            return None

        if Path(source_path).is_file():

            shutil.copyfile(source_path, file_path)
        else:
            shutil.copytree(source_path, file_path)

        return file_path
