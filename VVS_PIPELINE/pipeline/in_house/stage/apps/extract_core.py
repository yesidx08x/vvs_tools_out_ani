
import logging
import traceback
from pathlib import Path
import importlib
from stage.external import fileseq
from stage.common.settings import Settings


LOG = logging.getLogger(__name__)


class ExtractCore:

    nice_name: str = ""
    color: tuple = (255, 255, 255)  # RGB
    # exposed_settings: dict = {}
    # global_exposed_settings: dict = {}
    optional: bool = False
    bundled: bool = False
    bundle_match_id = 0

    def __init__(self, exposed_settings=None, global_exposed_settings=None):
        self.global_exposed_settings_ui: dict = global_exposed_settings or {}
        self.exposed_settings_ui: dict = exposed_settings or {}
        _global_exposed_settings_data, _exposed_settings_data = self.process_settings()


        self._extension: str = ""
        self.extension_second: str = ""

        self._extract_folder: str = ""
        self._category: str = ""
        self._state = "idle"
        self._extract_name = ""
        self._enabled: bool = True
        self._message: str = ""
        self._parameter:dict = {}

        self.extract_json:dict = {}
        self.extract_json[self.__class__.name]={}

        # self._bundled: bool = False # if bundled, the extract will be a folder

        self.category_functions = {}

        self.global_settings = Settings()
        self.global_settings.set_data(_global_exposed_settings_data)
        self.settings: dict = {}
        self._bundle_info: dict = {}
        self._resolve_outputs:list = []

        for key, value in _exposed_settings_data.items():
            _settings = Settings()
            _settings.set_data(value)
            self.settings[key] = _settings

    def process_settings(self):
        global_settings_data = {}
        for key, data in self.global_exposed_settings_ui.items():
            global_settings_data[key] = data["value"]

        settings_data = {}
        for key, data in self.exposed_settings_ui.items():
            settings_data[key] = {}
            for sub_key, sub_data in data.items():
                settings_data[key][sub_key] = sub_data["value"]

        return global_settings_data, settings_data

    def __init_subclass__(cls, **kwargs):
        # Get the base name of the file without the extension using pathlib
        module = importlib.import_module(cls.__module__)
        module_file_path = Path(module.__file__).resolve()
        module_name = module_file_path.stem
        # Set the 'name' variable in the subclass
        cls.name = module_name
        super().__init_subclass__(**kwargs)


    @property
    def parameter(self):
        return self._parameter

    @parameter.setter
    def parameter(self,parameter):
        self._parameter=parameter

    @property
    def enabled(self):
        """Return the enabled state of the extractor."""
        return self._enabled

    @enabled.setter
    def enabled(self, enabled):
        """Set the enabled state of the extractor."""
        self._enabled = enabled

    @property
    def extract_name(self):
        """Return the name of the extracted file."""
        return self._extract_name

    @extract_name.setter
    def extract_name(self, name):
        """Set the name of the extracted file."""
        self._extract_name = name

    @property
    def extension(self):
        """Return the extension of the extracted file."""
        return self._extension

    @extension.setter
    def extension(self, extension):
        """Set the extension of the extracted file."""
        self._extension = extension

    @property
    def bundle_info(self):
        """The bundle information dictionary."""
        return self._bundle_info

    @bundle_info.setter
    def bundle_info(self, bundle_info):
        """Set the bundle information dictionary."""
        self._bundle_info = bundle_info

    @property
    def extract_folder(self):
        """Return the folder path where the extracted file will be saved."""
        return self._extract_folder

    @extract_folder.setter
    def extract_folder(self, folder_path):
        """Set the folder path where the extracted file will be saved."""
        _folder_path_obj = Path(folder_path)
        _folder_path_obj.mkdir(parents=True, exist_ok=True)
        self._extract_folder = str(_folder_path_obj)

    @property
    def category(self):
        """Return the category which will rules."""
        return self._category

    @category.setter
    def category(self, category):
        """Set the category which will rules."""
        # TODO some validation here
        self._category = category

    @property
    def state(self):
        """Return the state of the extractor."""
        return self._state

    @property
    def message(self):
        """Return the message of the extractor."""
        return self._message

    @property
    def resolve_outputs(self):
        return self._resolve_outputs

    def set_message(self, message):
        """Set the message of the extractor.

        Args:
            message (str): The message to set.
        """
        self._message = message

    def extract(self):
        """Execute the extract."""
        func = self.category_functions.get(self.category, self._extract_default)
        try:
            func()
            self._state = "success"
            if self.bundled and not self._bundle_info:
                self._collect_bundle_info()
        except Exception as exc:  # pylint: disable=broad-except
            # print the FULL STACK TRACEBACK
            LOG.exception(exc)
            LOG.error(f"Error while extracting {self.name} to {self.extract_folder}")
            full_traceback = traceback.format_exc()
            self._state = "failed"
            self._message = full_traceback

    def _extract_default(self):
        """Extract for any non-specified category."""
        pass

    def resolve_output(self):
        """Resolve the output path."""
        if self.bundled:
            output_path = (
                Path(self.extract_folder) / f"{self._extract_name}"
            )
        else:
            output_path = (
                Path(self.extract_folder)
                / f"{self._extract_name}{self.extension}"
            )
        return output_path.as_posix()

    def resolve_output_second(self):
        """Resolve the output path."""
        if self.bundled:
            output_path = (
                Path(self.extract_folder) / f"{self._extract_name}"
            )
        else:
            output_path = (
                Path(self.extract_folder)
                / f"{self._extract_name}{self.extension_second}"
            )
        return output_path.as_posix()

    def _collect_bundle_info(self):

        self._bundle_info = {}
        _path = self.resolve_output()

        # get everything in the path as fileseq
        # f_handler = fileseq.FileSequence("")
        # found_seqs = f_handler.findSequencesOnDisk(_path)
        found_seqs = fileseq.findSequencesOnDisk(_path)

        for seq in found_seqs:
            self._bundle_info[seq.basename()] = {
                "extension": seq.extension(), # e.g ".txt"
                "path": seq.format(), # e.g "file.txt" or "color.1009,1019.exr"
                "sequential": bool(seq.frameRange()), # e.g True or False
            }
