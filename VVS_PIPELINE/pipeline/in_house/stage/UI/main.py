import getpass
import sys, os
from stage.common.log import Filelog
import importlib
from pathlib import Path
from stage.external.Qt import QtWidgets, QtCore, QtGui
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from stage import plugin
from stage.UI import widget
from stage.UI.widgets import style
from stage.version import __version__
from stage.common.utils import format_path_join
from stage.UI.widgets.task_view import TasksLayout
from stage.entities.project import Project
from stage.UI.dialog.message_box import SMessageBox
from stage.UI.widgets.category_view import CategoryLayout
from stage.UI.widgets.production_view import ProductionLayout
from stage.UI.widgets.version_view import VersionLayout
from stage.UI.dialog.publish_dialog import PublishSceneDialog
from stage.UI.widgets.project_widget import ProjectWidget
from stage.UI.dialog.work_dialog import NewWorkDialog, WorkFromTemplateDialog, NewVersionDialog
from stage.UI.widgets.common import Button,TagBar

LOG = Filelog(logname=__name__, filename='logging')



def launch(app='maya', pipeline='cgteamwork', dont_show=False):
    window_name = f"Stage {__version__}-{app}"
    all_widgets = QtWidgets.QApplication.allWidgets()
    for entry in all_widgets:
        try:
            if entry.objectName() == window_name:
                entry.close()
                entry.deleteLater()
        except Exception as e:
            print(e)
            pass

    stage_pipeline = plugin.addon_initialize(pipeline)

    stage_app = plugin.app_initialize(app)()
    stage_app.DCC_NAME = app
    parent = stage_app.get_main_window()

    win = StageMainWindow(stage_app, stage_pipeline, parent=parent, window_name=window_name)

    if not dont_show:
        win.show()

    return win


class StageMainWindow(QtWidgets.QMainWindow, widget.Ui_MainWindow):
    WINDOW_NAME = 'Stage'

    def __init__(self, app_object, pipeline_object, window_name=WINDOW_NAME, parent=None):

        super().__init__(parent)
        self.setupUi(self)
        self.parent = parent
        self.app = app_object

        self.project_name = os.environ.get('project_name')

        if os.path.exists(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'project', self.project_name)):
            module = importlib.import_module(f'stage.config.project.{self.project_name}.settings')
        else:
            module = importlib.import_module(f'stage.config.project.default.settings')

        self.stage_project_setting = module.Project(dcc=self.app, pipeline=pipeline_object)

        # self.stage_project_setting = plugin.project_initialize(os.environ.get('project_name'))(dcc=self.app,pipeline=pipeline_object)

        self.project = Project(dcc=self.app, project=self.stage_project_setting)
        self.pip = pipeline_object(self.project)

        self.setWindowTitle(window_name)
        self.setObjectName(window_name)
        self.create_menu()
        self.create_widgets()
        self.create_layout()
        self.build_extensions()
        self.create_data()
        self.create_connect()
        self.resume_last_state()
        LOG.info(f"User '{getpass.getuser()}' has logged in.")
        LOG.warning(self.stage_project_setting.__class__.__module__)

    def create_menu(self):
        self.menu_bar = QtWidgets.QMenuBar(self)
        self.setMenuBar(self.menu_bar)

    def create_widgets(self):
        _style_file = style.style_file(file_name="style.qss")
        self.setStyleSheet(str(_style_file.readAll(), "utf-8"))

        self.project_widget = ProjectWidget(self)

        # production
        self.production_lay = ProductionLayout(self.project)
        self.production_lay.production_view.hide_no_name_columns()

        # task
        self.task_layout = TasksLayout(self.pip)
        self.task_layout.task_view.hide_columns(["id", "path", "cn.name", "user"])

        # work
        self.work_Category = CategoryLayout()
        self.work_Category.work_tree_view.hide_columns(
            ["id", "path", "creator", "dcc", "extension", "date", "version count"])


        self.version_widget = VersionLayout()
        self.feedback = SMessageBox(self)

        self.book_mark_btn=Button("Add BookMark")

        self.save_new_work_btn = Button("Save New Work")
        #self.save_new_work_btn.setMinimumSize(10, 35)

        self.work_from_template_btn = Button("Work from Template")
        #self.work_from_template_btn.setMinimumSize(10, 35)

        self.increment_version_btn = Button("Increment Version")
        #self.increment_version_btn.setMinimumSize(10, 35)

        self.publish_btn = Button("Publish Work")
        #self.publish_btn.setMinimumSize(10, 35)

        self.publish_review_btn = Button("Publish Review")
       # self.publish_review_btn.setMinimumSize(10, 35)

        self.horizontal_spacer = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding,
                                                       QtWidgets.QSizePolicy.Minimum)

        self.horizontalLayoutBottom.setContentsMargins(15, 0, 15, 0)

        self.tag_bar=TagBar()

    def create_data(self, refresh=False):
        self.pip.create_project_data(__refresh_cache__=refresh)
        self.refresh_production()

    def create_layout(self):
        self.verticalLayoutProject.addWidget(self.project_widget)
        self.verticalLayoutProductions.addLayout(self.production_lay)
        self.verticalLayoutTasks.addLayout(self.task_layout)
        self.verticalLayoutCategory.addLayout(self.work_Category)
        self.verticalLayoutVersion.addWidget(self.version_widget)
        self.horizontalLayoutBottom.addWidget(self.tag_bar)
        self.horizontalLayoutBottom.addItem(self.horizontal_spacer)
        self.horizontalLayoutBottom.addWidget(self.book_mark_btn)
        self.horizontalLayoutBottom.addWidget(self.save_new_work_btn)
        self.horizontalLayoutBottom.addWidget(self.work_from_template_btn)
        self.horizontalLayoutBottom.addWidget(self.increment_version_btn)

        if self.app.name == 'photoshop':
            self.horizontalLayoutBottom.addWidget(self.publish_review_btn)
        self.horizontalLayoutBottom.addWidget(self.publish_btn)

    def create_connect(self):
        self.production_lay.production_view.item_selected.connect(self.task_layout.task_view.set_tasks)
        self.task_layout.task_view.item_selected.connect(self.work_Category.set_task)

        self.work_Category.work_tree_view.save_new_work_event.connect(self.on_save_new_work)
        self.work_Category.work_tree_view.work_from_template_event.connect(self.on_work_from_template)
        self.work_Category.work_tree_view.item_selected.connect(self.on_set_version)
        self.work_Category.work_tree_view.load_event.connect(self.on_open)
        self.work_Category.work_tree_view.import_event.connect(self.on_import)
        self.work_Category.work_tree_view.reference_event.connect(self.on_reference)


        self.version_widget.open_file_path.connect(self.on_open)
        self.book_mark_btn.clicked.connect(self.on_add_book_mark)
        self.save_new_work_btn.clicked.connect(self.on_save_new_work)
        self.work_from_template_btn.clicked.connect(self.on_work_from_template)
        self.increment_version_btn.clicked.connect(self.on_new_version)
        self.publish_btn.clicked.connect(self.publish_scene)

        self.publish_review_btn.clicked.connect(self.publish_review)



    def on_set_version(self, work):

        self.version_widget.set_base(work,self.stage_project_setting)

    def refresh_production(self):
        self.production_lay.production_view.refresh()
        self.task_layout.task_view.refresh()
        self.work_Category.work_tree_view.refresh()

    def resume_last_state(self):
        self.production_lay.production_view.expand_first_item()
        self.production_lay.production_view.expandAll()
        self.work_Category.work_tree_view.expandAll()

    def build_extensions(self):

        if self.app.extensions:
            dcc_menu = self.menu_bar.addMenu(f"{self.app.name}")
        else:
            return
        for _key, extension_class in self.app.extensions.items():
            extension = extension_class(self)
            extension.menu_item = dcc_menu
            extension.execute()

    def on_tag(self,settings):
        last_subproject, last_task, last_task_mode, last_mode, last_category, last_work, last_version=settings
        subproject_path = last_subproject
        if subproject_path:
            state = self.production_lay.production_view.select_by_path(subproject_path)
            if state:
                task_name = last_task
                if task_name:
                    state = self.task_layout.task_view.select_by_name(task_name)
                    if state:
                        category_index = last_category or 0
                        mode_index = last_mode or 0
                        task_mode_index = last_task_mode or 0
                        self.work_Category.set_mode_index(mode_index)
                        self.work_Category.set_category_by_index(category_index)
                        self.task_layout.set_task_mode_index(task_mode_index)
                        work_dcc_name = last_work
                        if work_dcc_name:
                            state = self.work_Category.work_tree_view.select_by_name(work_dcc_name)
                            if state:
                                version_id = last_version
                                if version_id:
                                    self.version_widget.set_version(version_id)
                    else:
                        self.task_layout.task_view.select_first_item()
                else:
                    self.task_layout.task_view.select_first_item()
        else:
            self.production_lay.production_view.select_first_item()

            self.task_layout.task_view.select_first_item()

        self.production_lay.production_view.set_expanded_state(
            self.project.user.expanded_subprojects
        )

        self.production_lay.production_view.expand_first_item()

    def on_add_book_mark(self):

        last_subproject = last_task = last_task_mode = last_mode = last_category = last_work = last_version = ''
        _subproject_item = self.production_lay.production_view.get_selected_items()
        if _subproject_item:
            _subproject_item = _subproject_item[0]
            last_subproject = _subproject_item.subproject.path
            _task_item = self.task_layout.task_view.get_selected_item()
            if _task_item:
                last_task = _task_item.task.name
                _mode_index = self.work_Category.get_mode_index()
                _task_mode_index = self.task_layout.get_task_mode_index()
                last_task_mode = _task_mode_index
                last_mode = _mode_index
                _category_index = self.work_Category.get_category_index()
                last_category = _category_index
                _work_item = self.work_Category.work_tree_view.get_selected_item()
                if _work_item:
                    last_work = _work_item.work_obj.name + '&' + _work_item.work_obj.dcc
                    _version_nmb = self.version_widget.get_selected_version_number()
                    last_version = _version_nmb


        self.tag_bar.create_tags(last_subproject,last_task,last_task_mode,last_mode,last_category,last_work,last_version)
        self.tag_bar.tag_click.connect(self.on_tag)



    def get_template(self):

        if hasattr(self.stage_project_setting, 'template_file'):
            category = self.work_Category.get_active_category()
            if not category:
                self.feedback.pop_info(
                    title="No tasks found.",
                    text="所选子对象下没有任何任务.\n"
                         "请先选择任务，再创建工作.",
                    critical=True,
                )
                return

            template_path = Path(self.stage_project_setting.template_file.format(template_path=self.stage_project_setting.template_path,
                                                                                 project=os.environ.get('project_name'),
                                                                                 app=self.app.DCC_NAME,
                                                                                 category=category))
            if not template_path.parent.exists():
                template_path = Path(self.stage_project_setting.template_file.format(
                    template_path=self.stage_project_setting.template_path,
                    project='default',
                    app=self.app.DCC_NAME,
                    category=category))
            return list(template_path.parent.glob(template_path.name))

    def on_save_new_work(self):

        category = self.work_Category.get_active_category()

        if category:
            task = self.work_Category.task
            subproject = task.parent_sub
        else:
            task = self.task_layout.task_view.get_active_task()
            if not task:
                self.feedback.pop_info(
                    title="No tasks found.",
                    text="所选子对象下没有任何任务.\n"
                         "请先选择任务，再创建工作.",
                    critical=True,
                )
                return
            subproject = task.parent_sub

        dialog = NewWorkDialog(
            self.project,
            parent=self,
            subproject=subproject,
            task_object=task,
            category_object=category,
        )
        if not self.__scene_modified_check(dialog.work):
            return

        state = dialog.exec_()
        if state:
            self.set_last_state()
            self.refresh_versions()
            self.statusbar.showMessage("新工作已成功创建.", 5000)
            self.resume_last_state()

    def on_work_from_template(self):

        available_templates = self.get_template()
        if not available_templates:
            self.feedback.pop_info(
                title="No Templates",
                text="没有可用的模板.",
                critical=True,
            )
            return

        category = self.work_Category.get_active_category()
        if category:
            task = self.work_Category.task
            subproject = task.parent_sub
        else:
            task = self.task_layout.task_view.get_active_task()
            if not task:
                self.feedback.pop_info(
                    title="No tasks found.",
                    text="所选子对象下没有任何任务.\n"
                         "请先选择任务，再创建工作.",
                    critical=True,
                )
                return
            subproject = task.parent_sub

        dialog = WorkFromTemplateDialog(
            self.project,
            template_names=available_templates,
            parent=self,
            subproject=subproject,
            task_object=task,
            category_object=category,
        )

        if not self.__scene_modified_check(dialog.work):
            return

        state = dialog.exec_()
        if state:
            self.set_last_state()
            self.refresh_versions()
            self.statusbar.showMessage("新工作已成功创建", 5000)
            self.resume_last_state()

            if not dialog.work:
                self.feedback.pop_info(
                    title="创建工作文件失败",
                    text=f"请先创建空场景文件...",
                )
                return

            self.on_open(dialog.work)

    def on_new_version(self):

        scene_file_path = self.project.dcc.get_scene_file()
        if not scene_file_path:
            self.feedback.pop_info(
                title="Scene file cannot be found.",
                text="找不到场景文件. "
                     "请通过 Save New Work 保存您的场景",
                critical=True,
            )
            return

        dialog = NewVersionDialog(self.project, parent=self.parent)
        state = dialog.exec_()

        if state:
            self.set_last_state()
            self.refresh_versions()
            self.set_last_state()
            self.statusbar.showMessage("新版本已成功创建.", 5000)

    def __scene_modified_check(self,work):
        if self.app.is_modified():
            question = "当前场景已被修改。是否要保存？"
            state = self.feedback.pop_question(
                title="Save current scene?",
                text=question,
                buttons=["yes", "no", "cancel"],
            )
            if state == "cancel":
                return False
            if state == "yes":
                if self.app.get_scene_file() == "":
                    _state = self.app.save_prompt()
                    if _state:
                        self.on_open(work)
                    return False
                self.app.save_scene()
        return True

    def on_open(self, work):

        if not self.__scene_modified_check(work):
            return


        if isinstance(work, str):
            self.app.open(work)
        else:
            if work.state == 'working':
                file_path = format_path_join(work.settings_file.absolute(), work.get_last_version())
            else:
                file_path = work.master_path

            self.app.open(file_path)

    def on_import(self, works):
        parameter=None
        if hasattr(self.stage_project_setting, "ingests"):
            category = self.work_Category.get_active_category()
            task = self.work_Category.task
            parameter=self.stage_project_setting.ingests(category,task)

        for work in works:
            if work.state == 'working':
                file_path = format_path_join(work.settings_file.absolute(), work.get_last_version())
            else:
                file_path = work.master_path

            work.import_version(file_path,parameter=parameter)

    def on_reference(self, works):

        parameter = None
        if hasattr(self.stage_project_setting, "ingests"):
            category = self.work_Category.get_active_category()
            task=self.work_Category.task
            parameter = self.stage_project_setting.ingests(category,task)

        for work in works:
            extract=None
            if work.state == 'working':
                file_path = format_path_join(work.settings_file.absolute(), work.get_last_version())
            else:
                file_path = work.master_path
                extract=work.extract

            work.reference_version(file_path,extract=extract,parameter=parameter)

    def refresh_versions(self):
        self.work_Category.refresh()

    def publish_scene(self):

        publish_dialog = PublishSceneDialog(self.app, self.pip, self.project, self.stage_project_setting,
                                            parent=self.parent)
        publish_dialog.show()

    def publish_review(self):

        publish_dialog = PublishSceneDialog(self.app, self.pip, self.project, self.stage_project_setting,
                                            publish_signal='review',
                                            parent=self.parent)
        publish_dialog.show()

    def set_last_state(self):

        _subproject_item = self.production_lay.production_view.get_selected_items()
        if _subproject_item:
            _subproject_item = _subproject_item[0]
            self.project.user.last_subproject = _subproject_item.subproject.path
            _task_item = self.task_layout.task_view.get_selected_item()
            if _task_item:
                self.project.user.last_task = _task_item.task.name
                _mode_index = self.work_Category.get_mode_index()
                _task_mode_index = self.task_layout.get_task_mode_index()
                self.project.user.last_task_mode = _task_mode_index
                self.project.user.last_mode = _mode_index
                _category_index = self.work_Category.get_category_index()
                self.project.user.last_category = _category_index
                _work_item = self.work_Category.work_tree_view.get_selected_item()
                if _work_item:
                    self.project.user.last_work = _work_item.work_obj.name + '&' + _work_item.work_obj.dcc
                    _version_nmb = self.version_widget.get_selected_version_number()
                    self.project.user.last_version = _version_nmb

        self.project.user.split_sizes = self.splitter.sizes()

        columns_states = {
            "subprojects": self.production_lay.production_view.get_visible_columns(),
            "tasks": self.task_layout.task_view.get_visible_columns(),
            "categories": self.work_Category.work_tree_view.get_visible_columns(),
        }
        self.project.user.visible_columns = columns_states

        column_sizes = {
            "subprojects": self.production_lay.production_view.get_column_sizes(),
            "tasks": self.task_layout.task_view.get_column_sizes(),
            "categories": self.work_Category.work_tree_view.get_column_sizes(),
        }
        self.project.user.column_sizes = column_sizes

        self.project.user.main_window_state = (
            self.geometry().x(),
            self.geometry().y(),
            self.geometry().width(),
            self.geometry().height(),
        )
        self.project.user.tags=self.tag_bar.setting

        self.project.user.last_project = self.project_name

    def resume_last_state(self):

        subproject_path = self.project.user.last_subproject
        if subproject_path:
            state = self.production_lay.production_view.select_by_path(subproject_path)
            if state:
                task_name = self.project.user.last_task
                if task_name:
                    state = self.task_layout.task_view.select_by_name(task_name)
                    if state:
                        category_index = self.project.user.last_category or 0
                        mode_index = self.project.user.last_mode or 0
                        task_mode_index = self.project.user.last_task_mode or 0
                        self.work_Category.set_mode_index(mode_index)
                        self.work_Category.set_category_by_index(category_index)
                        self.task_layout.set_task_mode_index(task_mode_index)
                        work_dcc_name = self.project.user.last_work
                        if work_dcc_name:
                            state = self.work_Category.work_tree_view.select_by_name(work_dcc_name)
                            if state:
                                version_id = self.project.user.last_version
                                if version_id:
                                    self.version_widget.set_version(version_id)
                    else:
                        self.task_layout.task_view.select_first_item()
                else:
                    self.task_layout.task_view.select_first_item()
        else:
            self.production_lay.production_view.select_first_item()

            self.task_layout.task_view.select_first_item()

        self.production_lay.production_view.set_expanded_state(
            self.project.user.expanded_subprojects
        )

        self.production_lay.production_view.expand_first_item()

        _sizes = self.project.user.split_sizes or [291, 180, 290, 291]
        self.splitter.setSizes(_sizes)

        self.production_lay.production_view.show_columns(
            self.project.user.visible_columns.get("subprojects", [])
        )
        self.task_layout.task_view.show_columns(
            self.project.user.visible_columns.get("tasks", [])
        )
        self.work_Category.work_tree_view.show_columns(
            self.project.user.visible_columns.get("categories", [])
        )

        self.production_lay.production_view.set_column_sizes(
            self.project.user.column_sizes.get("subprojects", {})
        )
        self.task_layout.task_view.set_column_sizes(
            self.project.user.column_sizes.get("tasks", {})
        )
        self.work_Category.work_tree_view.set_column_sizes(
            self.project.user.column_sizes.get("categories", {})
        )

        window_state = self.project.user.main_window_state
        if window_state:
            self.setGeometry(QtCore.QRect(*self.project.user.main_window_state))

        for tags in self.project.user.tags.values():
            self.tag_bar.create_tags(*tags)
            self.tag_bar.tag_click.connect(self.on_tag)

    def closeEvent(self, event):
        self.project.user.last_subproject = None
        self.project.user.last_task = None
        self.project.user.last_category = None
        self.project.user.last_work = None
        self.project.user.last_version = None
        self.set_last_state()
        self.project.user.expanded_subprojects = (
            self.production_lay.production_view.get_expanded_state()
        )

        self.project.user.resume.apply_settings()
        _ = QtWidgets.QApplication.allWidgets()
        event.accept()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    from time import time

    start = time()
    win = launch()
    end = time()
    LOG.info("Took %s seconds", (end - start))
    print("Took %s seconds", (end - start))

    sys.exit(app.exec_())