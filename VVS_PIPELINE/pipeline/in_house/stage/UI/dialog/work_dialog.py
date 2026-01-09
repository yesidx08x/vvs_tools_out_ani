import os.path
from pathlib import Path
from stage.external.Qt import QtWidgets, QtCore, QtGui
from stage.UI.widgets.common import HeaderLabel, ResolvedText,RadioButton
from stage.UI.dialog.message_box import SMessageBox
from stage.UI.widgets.common import ButtonBox
from stage.common.utils import format_path_join
from stage.UI.widgets.utils import SettingsLayout
from stage.UI.widgets import style
from stage.entities.work import Work


class NewWorkDialog(QtWidgets.QDialog):
    """Dialog for creating new work files."""

    def __init__(
        self,
        main_object,
        subproject=None,
        task_object=None,
        category_object=None,
        subproject_id=None,
        task_id=None,
        category_index=None,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.setWindowFlag(QtCore.Qt.WindowContextHelpButtonHint, False)
        self.feedback = SMessageBox(parent=self)
        self.main_object = main_object
        self.dcc=self.main_object.dcc
        self.setWindowTitle("Create New Work File")
        self.work = None
        self.alias = ''
        self.version=''
        # variables
        self.subproject = subproject
        self.task = task_object
        self.category = category_object
        self.layouts = QtWidgets.QVBoxLayout()

        self.format=self.dcc.formats[0]
        self.primary_definition = self.define_primary_ui()
        self.primary_content = SettingsLayout(self.primary_definition,parent=self)
        self.build_layouts()
        self.build_ui()
        self.build_connect()
        self.update_labels()


    def build_layouts(self):
        self.master_layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.master_layout)
        self.header_layout = QtWidgets.QVBoxLayout()
        self.file_layout = QtWidgets.QHBoxLayout()
        self.buttons_layout = QtWidgets.QHBoxLayout()
        self.master_layout.addLayout(self.header_layout)
        self.master_layout.addLayout(self.file_layout)
        self.master_layout.addLayout(self.primary_content)
        self.master_layout.addLayout(self.buttons_layout)


    def build_ui(self):
        self.header_lbl = HeaderLabel("New Work")
        self.header_lbl.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
        self.header_lbl.set_color("orange")
        self.header_layout.addWidget(self.header_lbl)

        self.name_label = ResolvedText(self.get_work_name())
        self.name_label.set_color("rgb(0, 150, 200)")
        self.header_layout.addWidget(self.name_label)
        self.resolved_path_lbl = ResolvedText("" * 30)
        self.resolved_path_lbl.set_color("gray")
        self.resolved_path_lbl.setWordWrap(False)
        self.header_layout.addWidget(self.resolved_path_lbl)
        self.tasks_combo = self.primary_content.find("task")
        self.alias_combo = self.primary_content.find("alias")
        self.custom_string=self.primary_content.find("custom")
        self.categories_combo = self.primary_content.find("category")
        #self.file_name_grp = self.primary_content.find("file_name")


        self.file_format_combo = self.primary_content.find("file_format")
        #self.tasks_combo.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents, True)

        self.button_box = ButtonBox(parent=self)
        self.create_btn = self.button_box.addButton(
            "Create Work", QtWidgets.QDialogButtonBox.AcceptRole
        )
        self.cancel_btn = self.button_box.addButton(
            "Cancel", QtWidgets.QDialogButtonBox.RejectRole
        )
        self.buttons_layout.addWidget(self.button_box)

        base_name=os.path.basename(self.dcc.get_scene_file())

        if self.alias_combo:
            for alias in self.main_object.current_project_setting.alias:
                if alias and alias in base_name:
                    self.alias_combo.setCurrentIndex(self.alias_combo.findText(alias))
                    break
            self.set_custom(self.alias_combo.currentText())

    def build_connect(self):
        self.tasks_combo.currentTextChanged.connect(self.set_task)
        self.categories_combo.currentTextChanged.connect(self.set_category)
        if self.alias_combo:
            self.alias_combo.currentTextChanged.connect(self.set_alias)
            self.alias=self.alias_combo.currentText()
        if self.custom_string:
            self.custom_string.textChanged.connect(self.set_custom)

        self.file_format_combo.currentTextChanged.connect(self.set_file_format)
        #self.file_name_grp.button_group.buttonToggled.connect(self.select_file_name)
        self.button_box.accepted.connect(self.on_create_work)
        self.button_box.rejected.connect(self.reject)

    def get_work_name(self):

        works=self.task.categories[self.category].works
        constructed_path = self.task.metadata.get('work_path').format(category_folder=self.main_object.current_project_setting.get_category_folder(self.category),category=self.category,abridge=self.task.categories[self.category].abridge, alias=self.alias,version='{version}')
        if hasattr(self.main_object.current_project_setting,'remap_category_path'):
            constructed_path=self.main_object.current_project_setting.remap_category_path(constructed_path)
        
        if os.environ.get('project_name').lower() == 'phhz':
            constructed_path = constructed_path.replace('Modeling', 'Model')
            constructed_path = constructed_path.replace('Shading', 'LookDev')

        base_name=os.path.basename(constructed_path)
        for rel in ['__{version}','_{version}','..{version}','.{version}','__{alias}','_{alias}','..{alias}','.{alias}']:
            base_name=base_name.replace(rel, '')

        work=works.get('%s/%s' % (base_name, self.format.replace('.', '')))

        if  work:
            version = work.all_versions[-1][0]
            if 'v' in version.lower():
                lenght = len(version.replace('v', ''))
                ver_num = 'v' + str(int(version.replace('v', '')) + 1).zfill(lenght)
            else:
                lenght = len(version)
                ver_num = str(int(version) + 1).zfill(lenght)
        else:
            ver_num = self.main_object.current_project_setting.default_version

        return os.path.basename(constructed_path.format(version=ver_num)).replace('__','_').replace('..','.')

    def define_primary_ui(self):
        """Define the primary UI elements with settings layout"""
        sub_path = self.subproject.path if self.subproject else ""
        tasks = list(self.subproject.tasks.keys()) if self.subproject else []
        task_name = self.task.name if self.task else ""
        categories = list(self.task.categories) if self.task else []
        category_name = self.category if self.category else ""


        _primary_ui = {
            #
            # "file_name": {
            # "display_name": "File Name",
            # "type": "buttongroupradio",
            # "items": self.get_work_name(),
            # "value": self.get_work_name(),
            # "tooltip": "File name of the work file",
            #  },

        "subproject": {
                "display_name": "Sub-project",
                "type": "Label",
                "project_object": self.main_object,
                "value": sub_path,
                "tooltip": "Path of the sub-project",
            },
            "task": {
                "display_name": "Task",
                "type": "combo",
                "items": tasks,
                "value": task_name,
                "tooltip": "Name of the Task",
            },
            "category": {
                "display_name": "Category",
                "type": "combo",
                "items": categories,
                "value": category_name,
                "tooltip": "Category of the work file",
            },
            "name": {
                "display_name": "label",
                "type": "validatedString",
                "value": "",
                "tooltip": "Name of the work file that will be added as a label tag.",
                "placeholder": "(Optional)",
            },

            "file_format": {
                "display_name": "File Format",
                "type": "combo",
                "items": self.dcc.formats,
                "value": self.dcc.formats[0],
                "tooltip": "File format of the work file",
            }


        }

        if self.task.parent_sub.parent_sub.name=='Shots' and category_name not in['DMP']:
            _primary_ui['custom'] = {
                "display_name": "Custom",
                "type": "String",
                "value": "",
                "tooltip": "Custom name of the work file",
            }
        else:
            _primary_ui['alias']={
                "display_name": "Custom",
                "type": "combo",
                "items":self.main_object.current_project_setting.alias,
                "value": self.main_object.current_project_setting.alias[0],
                "tooltip": "File Alias of the work file",
            }



        return _primary_ui

    def set_task(self, task_name):
        self.task_name = task_name
        if not task_name:
            return

        self.task = self.subproject.tasks[task_name]
        work_names = self.get_work_name()
        self.name_label.setText(work_names)
        self.update_labels()
        return self.task

    def set_category(self, category_name):

        if not category_name:
            return

        self.category = category_name
        work_names = self.get_work_name()
        self.name_label.setText(work_names)
        self.update_labels()
        return self.category

    def set_alias(self,alias):

        self.alias = alias
        work_names = self.get_work_name()
        self.name_label.setText(work_names)
        self.update_labels()
        return self.alias

    def set_custom(self,text):
        self.alias = text
        work_names = self.get_work_name()
        self.name_label.setText(work_names)
        self.update_labels()
        return self.alias

    def set_file_format(self,format):
        if not format:
            return
        self.format = format

        work_names = self.get_work_name()
        self.name_label.setText(work_names)
        self.update_labels()

    def select_file_name(self, button, checked):
        self.update_labels()

    def update_labels(self):
        if self.alias_combo:
            self.alias = self.alias_combo.currentText()
        if self.custom_string:
            self.alias = self.custom_string.text()

        constructed_path = self.task.metadata.get('work_path').format(category_folder=self.main_object.current_project_setting.get_category_folder(self.category),category=self.category,abridge=self.task.categories[self.category].abridge,alias=self.alias,version='')



        if hasattr(self.main_object.current_project_setting,'remap_category_path'):
            constructed_path=self.main_object.current_project_setting.remap_category_path(constructed_path)
            
        if os.environ.get('project_name').lower() == 'phhz':
            constructed_path = constructed_path.replace('Modeling', 'Model')
            constructed_path = constructed_path.replace('Shading', 'LookDev')
            
        file_format=self.file_format_combo.currentText()
        file_name=self.name_label.text()
        work_path=os.path.dirname(constructed_path)
        work_file=format_path_join(work_path,file_name)+file_format

        self.header_lbl.setText(work_file)

    def on_create_work(self):
        name = self.name_label.text()
        file_format = self.file_format_combo.currentText()
        work_file=self.header_lbl.text()

        try:
            self.work=self.task.categories[self.category].create_work(work_file,name, file_format=file_format)
        except Exception as e:
            if self.dcc.name=='photoshop':
                self.feedback.pop_info(
                    title="保存失败",
                    text=f"请先创建文件或打开文件在保存 work 文件...",
                )
            print(e)
        self.accept()

class WorkFromTemplateDialog(NewWorkDialog):


    def __init__(self, main_object, template_names=None, *args, **kwargs):
        self.template_names = template_names

        super().__init__(main_object, *args, **kwargs)
        self.setWindowTitle("Create Work From Template")

        #self.header_lbl.setText("Create Work From Template")
        #self.header_lbl.set_color("green")

    def define_primary_ui(self):

        # available_templates = self.main_object.get_template_names()

        _primary_ui = {
            "template": {
                "display_name": "Template",
                "type": "combo",
                "items": [v.stem for v in self.template_names],
                "value": self.template_names[0].stem,
                "datas":[v.as_posix() for v in self.template_names],
                "tooltip": "Template file to create the work from",
            }
        }
        _orig_dict = super().define_primary_ui()
        _primary_ui.update(_orig_dict)
        return _primary_ui

    def on_create_work(self):

        template_combo = self.primary_content.find("template")
        template_path = template_combo.currentData()

        name = self.name_label.text()
        work_file = self.header_lbl.text()

        self.work=self.task.categories[self.category].create_work_from_template(work_file,name, template_path)

        self.accept()


class NewVersionDialog(QtWidgets.QDialog):
    def __init__(self, main_object, ingest=False, *args, **kwargs):
        super(NewVersionDialog, self).__init__(*args, **kwargs)
        self.setWindowFlag(QtCore.Qt.WindowContextHelpButtonHint, False)

        self.feedback = SMessageBox(parent=self)
        self.main_object = main_object
        self.dcc = self.main_object.dcc

        self.ingest = ingest
        _title = "New Version" if not self.ingest else "Ingest Version"
        self.setWindowTitle(_title)

        self.master_layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.master_layout)

        self.build_ui()
        # resize the dialog slightly bigger than actually is
        size_hint = self.sizeHint()
        self.resize(QtCore.QSize(size_hint.width() + 10, 300))

        style_file = style.style_file()
        self.setStyleSheet(str(style_file.readAll(), "utf-8"))

    def build_ui(self):
        self.header_lbl = HeaderLabel(self.windowTitle())
        _color = "orange" if not self.ingest else "pink"
        self.header_lbl.set_color(_color)
        self.master_layout.addWidget(self.header_lbl)

        notes_label = QtWidgets.QLabel("Notes: ")
        self.notes_text = QtWidgets.QPlainTextEdit()
        self.notes_text.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.notes_text.setMinimumHeight(50)
        # make its initial size not bigger than the minimum size
        self.notes_text.setSizePolicy(
            QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum
        )

        self.master_layout.addWidget(notes_label)
        self.master_layout.addWidget(self.notes_text)

        # format
        self.format_combo = QtWidgets.QComboBox()
        self.format_combo.addItems(self.dcc.formats)
        # align texts in combo to the right
        self.format_combo.setItemDelegate(QtWidgets.QStyledItemDelegate())

        _format=Path(self.dcc.get_scene_file()).suffix

        self.format_combo.setCurrentText(_format)
        self.on_format_changed(_format)  # initialize the name label with the format

        self.master_layout.addWidget(self.format_combo)

        # add a separator before buttons
        separator = QtWidgets.QLabel()
        separator.setFrameShape(QtWidgets.QFrame.HLine)
        separator.setFrameShadow(QtWidgets.QFrame.Sunken)
        # separator.setStyleSheet("background-color: rgb(174, 215, 91);")
        separator.setFixedHeight(10)
        self.master_layout.addWidget(separator)

        # buttons
        button_box = ButtonBox()
        button_box.addButton(
            "Create New Version", QtWidgets.QDialogButtonBox.AcceptRole
        )
        button_box.addButton("Cancel", QtWidgets.QDialogButtonBox.RejectRole)
        self.master_layout.addWidget(button_box)

        # Signals
        button_box.accepted.connect(self.on_create_version)
        button_box.rejected.connect(self.reject)
        self.format_combo.currentTextChanged.connect(self.on_format_changed)

    def on_create_version(self):
        work_file_path = Path(self.dcc.get_scene_file())
        work_path = work_file_path.parent

        work = Work(work_path.as_posix(), dcc_handler=self.dcc)
        work_file=work_path.joinpath(self.header_lbl.text())

        if os.path.exists(work_file):
            self.feedback.pop_info(
                title="Error",
                text="无法创建新版本。新版本文件已经存在.",
                critical=True,
            )

        _version=work.increment_new_version(full_path=work_file, file_format=self.format_combo.currentText(), notes=self.notes_text.toPlainText())


        if _version != -1:
            self.accept()
        else:
            self.feedback.pop_info(
                title="Error",
                text="无法创建版本。请查看脚本编辑器以获取详细信息.",
                critical=True,
            )
            self.reject()

    def on_format_changed(self, file_format):

        work_file_path=Path(self.dcc.get_scene_file())

        def find_new_version(work_file_path):
            file_name=work_file_path.stem
            version = file_name.rsplit("_", 1)[-1].rsplit(".", 1)[-1]
            file_base_name = file_name.rsplit("_", 1)[0].rsplit(".", 1)[0]

            if 'v' in version.lower():
                lenght = len(version.replace('v', ''))
                ver_num = 'v' + str(int(version.replace('v', '')) + 1).zfill(lenght)
            else:
                lenght = len(version)
                ver_num = str(int(version) + 1).zfill(lenght)

            version_name=file_name.replace(version, ver_num)+file_format
            work_path = work_file_path.parent
            work_file = work_path.joinpath(version_name)

            if os.path.exists(work_file):
                version_name=find_new_version(work_file)
            return version_name
        version_name=find_new_version(work_file_path)

        self.header_lbl.setText(version_name)