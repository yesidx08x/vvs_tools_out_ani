
from stage.external.Qt import QtWidgets
from stage.UI.dialog.message_box import SMessageBox

class ExtensionCore:
    """Core class for DCC specific UI extensions."""

    def __init__(self, main_window):
        self.parent = main_window
        self.main = main_window
        self.feedback = SMessageBox(parent=self.parent)
        self.menu_item = None

    def execute(self):
        """Mandatory method to execute the extension."""
        raise NotImplementedError("Method 'execute' must be implemented.")

    def add_function_to_main_menu(self, function, name):
        """Add a function to the main menu."""
        if not self.menu_item:
            raise ValueError("Menu item is not set.")

        action = QtWidgets.QAction(name, self.parent)
        self.menu_item.addAction(action)
        action.triggered.connect(lambda: function())

    def get_work_and_version(self):
        """Get the work and version objects from the scene file."""
        scene_file_path = self.main.app.get_scene_file()
        if not scene_file_path:
            self.feedback.pop_info(
                title="Scene file cannot be found.",
                text="Scene file cannot be found. "
                     "Please either save your scene by creating a new work or "
                     "ingest it into an existing one.",
                critical=True,
            )
            return None, None

        work, version = self.main.project.find_work_by_absolute_path(
            scene_file_path)
        if not work:
            self.feedback.pop_info(
                title="Work object cannot be found.",
                text="Work cannot be found. Versions can only saved on work objects.\n"
                     "If there is no work associated with current scene either create a work "
                     "or use the ingest method to save it into an existing work",
                critical=True,
            )
            return None, None
        return work, version
