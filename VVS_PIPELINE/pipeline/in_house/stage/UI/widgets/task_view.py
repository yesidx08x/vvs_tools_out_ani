import logging
import webbrowser
from stage.external.Qt import  QtWidgets, QtCore, QtGui
from stage.external.Qt.QtWidgets import QMessageBox
from stage.UI.widgets.color_delegate import ColorKeepingDelegate
from stage.UI.widgets.filter import FilterModel,FilterWidget
from stage.UI.widgets import style
from stage.UI.widgets.common import IconButton,HorizontalSeparator
from stage.UI.widgets.common import CheckButton,BootstrapButton,FlowLayout
LOG = logging.getLogger(__name__)


class TaskItem(QtGui.QStandardItem):
    """Item class for the task view"""
    color_dict = {
        "asset": (0, 187, 184),
        "shot": (0, 115, 255),
        "global": (255, 141, 28),
        "other": (255, 255, 255),
        "deleted": (255, 0, 0),
    }

    def __init__(self, task_obj):
        super(TaskItem, self).__init__()

        # # test
        _icon = style.icon(f"{task_obj.type}.png")
        self.setIcon(_icon)

        self.task = task_obj
        #
        self.fnt = QtGui.QFont("Microsoft YaHei", 10)
        self.fnt.setBold(True)
        self.setEditable(False)

        self._state = None

        self.setText(task_obj.nice_name or task_obj.name)

        self.refresh()

    def refresh(self):
        """Refresh the item"""
        self.set_state(self.task.state)

        if self.task.deleted:
            self.setForeground(QtGui.QColor(255, 0, 0))
            self.setFont(QtGui.QFont("Microsoft YaHei", 12, italic=True))
            _icon = style.icon(f"{self.task.type}-ghost.png")
            self.setIcon(_icon)

    def set_state(self, state):
        """Set the state of the item.

        Args:
            state (str): State of the task
        """
        self._state = state
        _color = self.color_dict.get(self.task.type, (255, 255, 255))
        self.fnt.setStrikeOut(state == "omitted")
        self.setFont(self.fnt)
        self.setForeground(QtGui.QColor(*_color))

        # it its deleted make is transparent and italic
        if state == "deleted":
            self.setForeground(QtGui.QColor(255, 0, 0, 100))
            self.setFont(QtGui.QFont("Open Sans", 12, italic=True))


class TaskColumnItem(QtGui.QStandardItem):
    def __init__(self, text):
        super(TaskColumnItem, self).__init__(text)
        self.setEditable(False)
        self.fnt = QtGui.QFont("Microsoft YaHei", 10)
        self.setFont(self.fnt)

class TaskModel(QtGui.QStandardItemModel):
    columns = ["name", "id", "path","cn.name","user"]
    filter_key = "super"

    def __init__(self):
        """Initialize the model"""
        super(TaskModel, self).__init__()
        self.purgatory_mode = False
        self.setHorizontalHeaderLabels(self.columns)

        self._tasks = []

    def clear(self):
        """Clear the model"""
        self.setRowCount(0)

    def append_task(self, task_obj):
        """Append a task to the model"""
        _task_item = TaskItem(task_obj)
        pid = TaskColumnItem(str(task_obj.id))
        path = TaskColumnItem(task_obj.path)
        cn_name= TaskColumnItem(task_obj.metadata.get('asset_cn_name') or '')
        user = TaskColumnItem(task_obj.artist or '')
        self.appendRow(
            [
                _task_item,
                pid,
                path,
                cn_name,
                user
            ]
        )
        return _task_item

    def find_item_by_id_column(self, unique_id):
        """Search entire tree and find the matching item."""
        # get EVERY item in this model
        _all_items = self.findItems(
            "*", QtCore.Qt.MatchWildcard | QtCore.Qt.MatchRecursive
        )
        for x in _all_items:
            if isinstance(x, TaskItem):
                if x.task.id == unique_id:
                    return x

    def find_item_by_name_column(self, name):
        """Search entire tree and find the matching item."""
        # get EVERY item in this model
        _all_items = self.findItems(
            "*", QtCore.Qt.MatchWildcard | QtCore.Qt.MatchRecursive
        )
        for x in _all_items:
            if isinstance(x, TaskItem):
                if x.task.name == name:
                    return x


class TaskView(QtWidgets.QTreeView):
    item_selected = QtCore.Signal(object)
    refresh_requested = QtCore.Signal()
    task_resurrected = QtCore.Signal()

    def __init__(self):
        """Initialize the view"""
        super(TaskView, self).__init__()
        self.purgatory_mode = False
        self.setItemDelegate(ColorKeepingDelegate())
        self._feedback = QMessageBox(self)
        self.setUniformRowHeights(True)
        self.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        # do not show branches
        self.setRootIsDecorated(False)

        self.model = TaskModel()
        self.proxy_model = FilterModel(parent=self)
        self.proxy_model.setSourceModel(self.model)
        self.proxy_model.setRecursiveFilteringEnabled(True)
        self.setSortingEnabled(True)
        # sort it alphabetically
        self.sortByColumn(0, QtCore.Qt.AscendingOrder)

        self.setModel(self.proxy_model)

        self.is_management_locked = False

        # SIGNALS

        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.right_click_menu)

        # create another context menu for columns
        self.header().setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.header().customContextMenuRequested.connect(self.header_right_click_menu)

        self.expandAll()

    def currentChanged(self, *args, **kwargs):
        super(TaskView, self).currentChanged(*args, **kwargs)
        self.item_clicked(self.currentIndex())

    def item_clicked(self, idx):
        """Emit the item_selected signal when an item is clicked"""
        # make sure the index is pointing to the first column
        idx = idx.sibling(idx.row(), 0)

        # the id needs to mapped from proxy to source
        index = self.proxy_model.mapToSource(idx)
        _item = self.model.itemFromIndex(index)
        if _item:
            self.item_selected.emit(_item.task)
        else:
            self.item_selected.emit(None)

    def expandAll(self):
        """Expand all the items in the view"""
        super(TaskView, self).expandAll()
        for x in range(self.model.columnCount()):
            self.resizeColumnToContents(x)

    def hide_columns(self, columns):
        """If the given column exists in the model, hides it"""
        if not isinstance(columns, list):
            columns = [columns]

        for column in columns:
            if column in self.model.columns:
                self.setColumnHidden(self.model.columns.index(column), True)

    def unhide_columns(self, columns):
        """If the given column exists in the model, unhides it"""
        if not isinstance(columns, list):
            columns = [columns]

        for column in columns:
            if column in self.model.columns:
                self.setColumnHidden(self.model.columns.index(column), False)

    def toggle_column(self, column, state):
        """If the given column exists in the model, unhides it"""
        if state:
            self.unhide_columns(column)
        else:
            self.hide_columns(column)

    def show_columns(self, list_of_columns):
        """Shows the given columns."""
        for column in list_of_columns:
            self.unhide_columns(column)

    def get_visible_columns(self):
        """Returns the visible columns."""
        return [
            self.model.columns[x]
            for x in range(self.model.columnCount())
            if not self.isColumnHidden(x)
        ]

    def get_column_sizes(self):
        """Return all column sizes in a dictionary."""
        return {x: int(self.columnWidth(x)) for x in range(self.model.columnCount())}

    def set_column_sizes(self, column_sizes):
        """Set the column sizes from the given dictionary."""
        for column, size in column_sizes.items():
            self.setColumnWidth(int(column), size)

    def select_first_item(self):
        """Select the first item in the view."""
        idx = self.proxy_model.index(0, 0)
        self.setCurrentIndex(idx)

    def get_items_count(self):
        """Return the number of items in the view."""
        return self.proxy_model.rowCount()

    def select_by_id(self, unique_id):
        """Select the item with the given id"""
        # get the index of the item
        match_item = self.model.find_item_by_id_column(unique_id)
        if match_item:
            idx = match_item.index()
            idx = idx.sibling(idx.row(), 0)
            index = self.proxy_model.mapFromSource(idx)
            self.setCurrentIndex(index)
            return True
        return False

    def select_by_name(self, name):
        """Select the item with the given id"""
        # get the index of the item
        match_item = self.model.find_item_by_name_column(name)
        if match_item:
            idx = match_item.index()
            idx = idx.sibling(idx.row(), 0)
            index = self.proxy_model.mapFromSource(idx)
            self.setCurrentIndex(index)
            return True
        return False

    def set_tasks(self, tasks_gen):
        """Set the data for the model"""
        # get the selected item
        selected_item = self.get_selected_item()
        self.model.clear()
        for task in tasks_gen:
            # if the task is already in model, skip it
            if self.model.find_item_by_id_column(task.id):
                continue

            self.model.append_task(task)
        self.expandAll()
        # if the item still exists, select it
        if selected_item:
            self.select_by_id(selected_item.task.id)

    def get_selected_item(self):
        """Return the selected item"""
        idx = self.currentIndex()
        if not idx.isValid():
            return None
        idx = idx.sibling(idx.row(), 0)
        # the id needs to mapped from proxy to source
        index = self.proxy_model.mapToSource(idx)
        _item = self.model.itemFromIndex(index)
        return _item

    def add_tasks(self, tasks):
        """Add a task to the model"""
        _ = [self.model.append_task(x) for x in tasks]
        self.expandAll()

    def header_right_click_menu(self, position):
        menu = QtWidgets.QMenu(self)

        # add checkable actions for each column
        for column in self.model.columns:
            action = QtWidgets.QAction(column, self)
            action.setCheckable(True)
            action.setChecked(not self.isColumnHidden(self.model.columns.index(column)))
            # connect the action to the column's visibility
            action.toggled.connect(lambda state, c=column: self.toggle_column(c, state))

            menu.addAction(action)

        menu.exec_(self.mapToGlobal(position))

    def right_click_menu(self, position):
        return

        indexes = self.sender().selectedIndexes()
        index_under_pointer = self.indexAt(position)
        right_click_menu = QtWidgets.QMenu(self)
        if not index_under_pointer.isValid():
            return
        # make sure the idx is pointing to the first column
        index_under_pointer = index_under_pointer.sibling(index_under_pointer.row(), 0)
        mapped_index = self.proxy_model.mapToSource(index_under_pointer)
        item = self.model.itemFromIndex(mapped_index)
        if len(indexes) > 0:
            level = 0
            index = indexes[0]
            while index.parent().isValid():
                index = index.parent()
                level += 1
        else:
            level = 0

        if self.purgatory_mode:
            if item.task.deleted:
                act_resurrect = right_click_menu.addAction(self.tr("Resurrect Task"))
                act_resurrect.setEnabled(not self.is_management_locked)
                act_resurrect.triggered.connect(
                    lambda _=None, x=item: self.on_resurrect(item)
                )
                right_click_menu.addSeparator()
        else:
            act_edit_task = right_click_menu.addAction(self.tr("Edit Task"))
            right_click_menu.addSeparator()

            act_edit_task.triggered.connect(lambda _=None, x=item: self.edit_task(item))

            right_click_menu.addSeparator()

        open_url_act = right_click_menu.addAction(self.tr("Open URL"))
        open_url_act.setVisible(self.is_management_locked)
        # open_url_act.triggered.connect(lambda _=None, x=item: self.open_url_requested.emit(item))
        open_url_act.triggered.connect(lambda _=None, x=item: self.test(item))

        # emit signal to open the url
        right_click_menu.exec_(self.sender().viewport().mapToGlobal(position))



    def test(self, item):
        if not self.guard.management_handler:
            return
        url = self.guard.management_handler.get_entity_url(item.task.type, item.task.id)
        if url:
            webbrowser.open(url)



    def refresh(self):
        """Re-populate the model."""
        self.refresh_requested.emit()


    def get_active_task(self):
        """Get the selected item and return the task object."""
        selected_item = self.get_selected_item()
        if selected_item:
            return selected_item.task
        return None

class TasksLayout(QtWidgets.QVBoxLayout):

    mode_changed = QtCore.Signal(int)

    def __init__(self, pipeline,*args, **kwargs):

        super(TasksLayout, self).__init__(*args, **kwargs)
        self.task_mode = 1
        self.current_user=''
        self.pipeline = pipeline
        self.create_init_ui()
        self.create_connect()

    def create_init_ui(self):
        header_lay = QtWidgets.QHBoxLayout()
        header_lay.setContentsMargins(0, 0, 0, 0)
        self.addLayout(header_lay)
        self.label = QtWidgets.QLabel("Tasks")
        self.label.setStyleSheet("font-size: 14px; font-weight: bold;")
        header_lay.addWidget(self.label)
        header_lay.addStretch()
        self.addWidget(HorizontalSeparator(color=(191, 17, 191)))
        # self.refresh_btn = IconButton(icon_name="refresh", circle=True, size=18, icon_size=14)
        # header_lay.addWidget(self.refresh_btn)



        #tasks mode
        self.task_mode_group = QtWidgets.QButtonGroup()
        self.my_task_radio_button = CheckButton(
            "My Tasks",
            indicator_size=8,
            indicator_color="#00FF00",
            indicator_margin=10
        )

        self.my_task_radio_button.setFont(QtGui.QFont("Arial", 10))

        self.all_task_radio_button = CheckButton(
            "All Tasks",
            indicator_size=8,
            indicator_color="#00FF00",
            indicator_margin=10
        )
        self.all_task_radio_button.setFont(QtGui.QFont("Arial", 10))

        self.all_task_radio_button.setChecked(True)
        self.radio_button_layout = QtWidgets.QHBoxLayout()
        self.radio_button_layout.setSpacing(6)
        self.radio_button_layout.addWidget(self.my_task_radio_button)
        self.radio_button_layout.addWidget(self.all_task_radio_button)
        self.task_mode_group.addButton(self.my_task_radio_button)
        self.task_mode_group.addButton(self.all_task_radio_button)
        self.task_mode_group.setExclusive(True)
        self.radio_button_layout.addStretch()
        self.radio_button_layout.setContentsMargins(5, 1, 1, 5)
        self.addLayout(self.radio_button_layout)

        #########
        self.task_view = TaskView()
        self.addWidget(self.task_view)
        self.filter_widget = FilterWidget(self.task_view.proxy_model)
        self.addWidget(self.filter_widget)

    def create_connect(self):
        self.my_task_radio_button.clicked.connect(self.on_task_mode)
        self.all_task_radio_button.clicked.connect(self.on_task_mode)

    def on_task_mode(self):
        if self.my_task_radio_button.isChecked():
            self.task_mode = 0
            if not self.current_user:
                self.current_user=self.pipeline.get_current_user_name()
            self.task_view.proxy_model.set_filter_user(self.current_user)
        else:
            self.task_mode = 1
            self.task_view.proxy_model.set_filter_user('')

    def get_task_mode_index(self):
        return self.task_mode

    def set_task_mode_index(self, mode_index):
        if mode_index == 0:
            self.my_task_radio_button.setChecked(True)
        elif mode_index == 1:
            self.all_task_radio_button.setChecked(True)
        self.on_task_mode()