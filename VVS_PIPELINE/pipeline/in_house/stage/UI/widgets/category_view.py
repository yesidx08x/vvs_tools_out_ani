import os
from datetime import datetime
from functools import partial
from stage.common.constants import ObjectType
from stage.external.Qt import QtWidgets, QtCore, QtGui
from stage.external.Qt.QtWidgets import QMessageBox
# from stage.UI.dialog.work_dialog import NewVersionDialog
from stage.UI.widgets.common import HorizontalSeparator, IconButton
from stage.UI.widgets.color_delegate import ColorKeepingDelegate
from stage.UI.widgets.filter import FilterModel,FilterWidget
from stage.UI.widgets.common import CheckButton,BootstrapButton,FlowLayout
from stage.UI.widgets import style


class WorkItem(QtGui.QStandardItem):
    """Custom QStandardItem for the work items in the category view."""
    state_color_dict = {
        "active": (255, 255, 0),
        # "working": (255, 255, 0),
        # "published": (0, 255, 0),
        "publish": (0, 255, 0),
        "omitted": (255, 255, 0),
        "promoted": (0, 255, 0),
    }

    def __init__(self, work_obj):

        super(WorkItem, self).__init__()

        self.work_obj = work_obj
        self.fnt = QtGui.QFont("Open Sans", 10)
        self.fnt.setBold(False)
        self.setEditable(False)

        version=self.work_obj.all_versions[-1][0]

        self.setToolTip(version)
        self.setFont(self.fnt)
        self.setText(work_obj.name)
        self.state = None
        self.refresh()
        self.setIcon(style.icon(self.work_obj.dcc.lower()))


    def refresh(self):
        """Refresh the item state."""
        self.set_state(self.work_obj.state)

    def set_state(self, state):

        self.state = state
        if self.work_obj.deleted:
            _state_color = (255, 0, 0)
        else:
            _state_color = self.state_color_dict.get(state, (255, 255, 0))
        # cross out omitted items
        self.fnt.setStrikeOut(state == "omitted")
        self.setFont(self.fnt)
        # if the work not saved with the same dcc of the current dcc, make it italic
        if not self.dcc_check():
            self.fnt.setItalic(True)
            self.setFont(self.fnt)
            _state_color = tuple(int(x * 0.5) for x in _state_color)
        self.setForeground(QtGui.QColor(*_state_color))

    def dcc_check(self):
        return self.work_obj.dcc.lower() == self.work_obj.dcc_handler.name.lower()


class PublishItem(QtGui.QStandardItem):

    state_color_dict = {
        "active": (0, 255, 255),
        # "published": (0, 255, 255),
        "publish": (0, 255, 255),
        "export": (255, 0 ,255),
        "omitted": (0, 255, 255),
        "promoted": (0, 255, 0),
    }

    def __init__(self, publish_obj):

        super(PublishItem, self).__init__()

        self.work_obj = publish_obj

        self.fnt = QtGui.QFont("Open Sans", 10)
        self.fnt.setBold(False)
        self.setEditable(False)

        self.setFont(self.fnt)
        self.setText(str(publish_obj.name))
        self.state = None

        self.setIcon(style.icon(self.work_obj.dcc.lower()))
        #self.setIcon(style.icon("published"))

        self.refresh()

    def refresh(self):
        """Refresh the item state."""
        self.set_state(self.work_obj.state)

    def set_state(self, state):
        self.state = state
        if self.work_obj.deleted:
            _state_color = (255, 0, 0)
        else:
            _state_color = self.state_color_dict.get(state, (255, 255, 0))
        # cross out omitted items
        self.fnt.setStrikeOut(state == "omitted")
        self.setFont(self.fnt)
        # if the work not saved with the same dcc of the current dcc, make it italic
        if not self.dcc_check():
            self.fnt.setItalic(True)
            self.setFont(self.fnt)
            if state=='export':
                _state_color = tuple(int(x * 0.8) for x in _state_color)
            else:
                _state_color = tuple(int(x * 0.5) for x in _state_color)
        self.setForeground(QtGui.QColor(*_state_color))

    def dcc_check(self):
        return self.work_obj.dcc.lower() == self.work_obj.dcc_handler.name.lower()


class CategoryColumnItem(QtGui.QStandardItem):
    """Custom QStandardItem for the category columns in the category view."""
    def __init__(self, text):
        super(CategoryColumnItem, self).__init__(text)
        self.setEditable(False)


class CategoryModel(QtGui.QStandardItemModel):
    """Custom QStandardItemModel for the category view."""
    columns = ["name", "id", "path", "creator", "dcc","extension","date", "version count"]

    def __init__(self):
        """Initialize the model."""
        super(CategoryModel, self).__init__()
        self.purgatory_mode = False
        self.setHorizontalHeaderLabels(self.columns)

        self._works = []
        self._publishes = []

    def clear(self):
        """Clear the model."""
        self.setRowCount(0)

    def set_works(self, works_list):
        """Set the works to the model.
        Args:
            works_list (list): A list of work objects.
        """
        # TODO: validate
        self._works = works_list
        self.populate()

    def set_publishes(self, publishes_list):
        """Set the publishes to the model.
        Args:
            publishes_list (list): A list of publish objects.
        """
        self._publishes = publishes_list
        self.populate(publishes=True)

    def populate(self, publishes=False):

        self.clear()
        if not publishes:
            for work in self._works:
                self.append_work(work)
        else:
            for publish in self._publishes:
                self.append_publish(publish)

    def append_publish(self, publish):

        if not publish.master_path.exists():
            return

        _item = PublishItem(publish)
        pid = CategoryColumnItem(str(publish.id))
        path = CategoryColumnItem(publish.path)
        creator = CategoryColumnItem(publish.creator)
        dcc = CategoryColumnItem(publish.dcc)
        extension=CategoryColumnItem(publish.extension)
        date = CategoryColumnItem( datetime.fromtimestamp(publish.date_modified).strftime("%Y/%m/%d %H:%M:%S"))
        version_count = CategoryColumnItem(str(publish.version_count))

        self.appendRow([_item, pid, path, creator, dcc,extension, date, version_count])

        return _item

    def append_work(self, work):

        _item = WorkItem(work)
        pid = CategoryColumnItem(str(work.id))
        path = CategoryColumnItem(work.path)
        creator = CategoryColumnItem(work.creator)
        dcc = CategoryColumnItem(work.dcc)
        extension=CategoryColumnItem(work.extension)
        date = CategoryColumnItem(
            datetime.fromtimestamp(work.date_modified).strftime("%Y/%m/%d %H:%M:%S")
        )
        version_count = CategoryColumnItem(str(work.version_count))

        self.appendRow([_item, pid, path, creator, dcc,extension,date,version_count])

        return _item




class CategoryView(QtWidgets.QTreeView):

    item_selected = QtCore.Signal(object)
    version_created = QtCore.Signal()
    file_dropped = QtCore.Signal(str)
    work_resurrected = QtCore.Signal()
    load_event = QtCore.Signal(object)
    # import_event = QtCore.Signal(object)
    import_event = QtCore.Signal(list)
    # reference_event = (QtCore.Signal(object))
    reference_event = (QtCore.Signal(list))
    save_new_work_event = QtCore.Signal()
    work_from_template_event = QtCore.Signal()

    def __init__(self, parent=None):

        super(CategoryView, self).__init__(parent)
        self.purgatory_mode = False
        self.setItemDelegate(ColorKeepingDelegate())
        self.publish_mode = False
        self.feedback = QMessageBox(self)
        self.setUniformRowHeights(True)
        self.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)


        # do not show branches
        self.setRootIsDecorated(False)

        # make it expandable
        self.setExpandsOnDoubleClick(True)

        self.model = CategoryModel()
        self.proxy_model = FilterModel()
        self.proxy_model.setSourceModel(self.model)
        self.proxy_model.setRecursiveFilteringEnabled(True)
        self.setSortingEnabled(True)

        self.setModel(self.proxy_model)

        # SIGNALS

        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.right_click_menu)

        # create another context menu for columns
        self.header().setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.header().customContextMenuRequested.connect(self.header_right_click_menu)

        self.setAcceptDrops(True)
        self.setMouseTracking(True)
        self.setIconSize(QtCore.QSize(32, 32))

        self.expandAll()

    def dragEnterEvent(self, event):
        """Override the drag enter event to accept file drops."""
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        """Override the drag move event to accept file drops."""
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        """Override the drop event to accept file drops."""
        if event.mimeData().hasUrls():
            event.accept()
            # Extract file path from dropped URLs
            for url in event.mimeData().urls():
                file_path = url.toLocalFile()
                self.file_dropped.emit(file_path)
        else:
            event.ignore()

    def select_by_id(self, unique_id):

        for row in range(self.model.rowCount()):
            idx = self.model.index(row, 1)
            if idx.data() == str(unique_id):
                idx = idx.sibling(idx.row(), 0)
                index = self.proxy_model.mapFromSource(idx)
                self.setCurrentIndex(index)
                return True
        return False

    def select_by_name(self, name_dcc):
        name,dcc=name_dcc.split('&')
        for row in range(self.model.rowCount()):
            idx = self.model.index(row, 0)
            idc = self.model.index(row, 4)
            if idx.data() == str(name) and idc.data() == str(dcc) :
                idx = idx.sibling(idx.row(), 0)
                index = self.proxy_model.mapFromSource(idx)
                self.setCurrentIndex(index)
                return True
        return False

    def currentChanged(self, *args, **kwargs):
        """Override the currentChanged method to emit the item_selected
        signal when an item is clicked.
        Args:
            *args (list): List of arguments.
            **kwargs (dict): Dictionary of keyword arguments.
        """
        super(CategoryView, self).currentChanged(*args, **kwargs)
        self.item_clicked(self.currentIndex())

    def get_selected_item(self):
        """Return the current item"""
        idx = self.currentIndex()
        if not idx.isValid():
            return None
        idx = idx.sibling(idx.row(), 0)

        # the id needs to mapped from proxy to source
        index = self.proxy_model.mapToSource(idx)
        _item = self.model.itemFromIndex(index)
        return _item

    def item_clicked(self, idx):
        """Emit the item_selected signal when an item is clicked.
        Args:
            idx (QtCore.QModelIndex): The index of the clicked item.
        """
        # block signals to prevent infinite loop
        self.blockSignals(True)
        # make sure the index is pointing to the first column
        idx = idx.sibling(idx.row(), 0)

        # the id needs to mapped from proxy to source
        index = self.proxy_model.mapToSource(idx)
        _item = self.model.itemFromIndex(index)

        self.blockSignals(False)
        if _item:
            self.item_selected.emit(_item.work_obj)
        else:
            self.item_selected.emit(None)

    def expandAll(self):
        """Expand all the items in the view"""
        super(CategoryView, self).expandAll()
        for column in range(self.model.columnCount()):
            self.resizeColumnToContents(column)
        self.resizeColumnToContents(0)

    def hide_columns(self, columns):
        """Hide the given columns.
        Args:
            columns (str or list): A column name or list of column names to be hidden.
        """
        if not isinstance(columns, list):
            columns = [columns]

        for column in columns:
            if column in self.model.columns:
                self.setColumnHidden(self.model.columns.index(column), True)

    def unhide_columns(self, columns):
        """Unhide the given columns.
        Args:
            columns (str or list): A column name or list of column names to be unhidden.
        """
        if not isinstance(columns, list):
            columns = [columns]

        for column in columns:
            if column in self.model.columns:
                self.setColumnHidden(self.model.columns.index(column), False)

    def toggle_column(self, column, state):
        """Toggle the visibility of the given column.
        Args:
            column (str): The name of the column to be toggled.
            state (bool): The state of the column visibility.
        """
        if state:
            self.unhide_columns(column)
        else:
            self.hide_columns(column)

    def show_columns(self, list_of_columns):
        """Show the given columns.
        Args:
            list_of_columns (list): A list of column names to be shown.
        """
        for column in list_of_columns:
            self.unhide_columns(column)

    def get_visible_columns(self):
        """Return the visible columns."""
        return [
            self.model.columns[x]
            for x in range(self.model.columnCount())
            if not self.isColumnHidden(x)
        ]

    def get_column_sizes(self):
        """Return all column sizes in a dictionary."""
        return {x: int(self.columnWidth(x)) for x in range(self.model.columnCount())}

    def set_column_sizes(self, column_sizes):
        """Set the column sizes from the given dictionary.
        Args:
            column_sizes (dict): A dictionary of column sizes.
        """
        for column, size in column_sizes.items():
            self.setColumnWidth(int(column), size)

    def header_right_click_menu(self, position):
        """Create a right click menu for the header.
        Args:
            position (QtCore.QPoint): The position of the right click.
        """
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

    def _right_click_on_blank(self, right_click_menu, position):
        """Create a right click menu for the blank space."""
        # if the dcc is not standalone, add the save new work action

        save_work_act = right_click_menu.addAction(self.tr("Save New Work"))
        work_from_template_act = right_click_menu.addAction(self.tr("Create Work From Template"))
        save_work_act.triggered.connect(self.save_new_work_event.emit)
        work_from_template_act.triggered.connect(self.work_from_template_event.emit)
        right_click_menu.exec_(self.sender().viewport().mapToGlobal(position))


    def right_click_menu(self, position):
        """Create a right click menu for the view.
        Args:
            position (QtCore.QPoint): The position of the right click.
        """
        right_click_menu = QtWidgets.QMenu(self)
        indexes = self.sender().selectedIndexes()
        index_under_pointer = self.indexAt(position)
        if not index_under_pointer.isValid():
            self._right_click_on_blank(right_click_menu, position)
            return
        # make sure the idx is pointing to the first column
        index_under_pointer = index_under_pointer.sibling(index_under_pointer.row(), 0)
        mapped_index = self.proxy_model.mapToSource(index_under_pointer)
        works=[]
        if len(indexes) > 1:
            for index in indexes:
                index = index.sibling(index.row(), 0)
                source_index = self.proxy_model.mapToSource(index)
                item = self.model.itemFromIndex(source_index)
                works.append(item.work_obj)
        else:
            item = self.model.itemFromIndex(mapped_index)
            load_act = right_click_menu.addAction(self.tr("Open"))
            load_act.triggered.connect(lambda: self.load_event.emit(item.work_obj))
            right_click_menu.addSeparator()
            works.append(item.work_obj)

        if self.publish_mode:
            reference_act = right_click_menu.addAction(self.tr("Reference To the Scene"))
            reference_act.triggered.connect(lambda:self.reference_event.emit(works))

        right_click_menu.addSeparator()
        import_act = right_click_menu.addAction(self.tr("Import To the Scene"))
        import_act.triggered.connect(lambda:self.import_event.emit(works))



        right_click_menu.addSeparator()


        open_scene_folder_act = right_click_menu.addAction(self.tr("Open Scene Folder"))
        open_scene_folder_act.triggered.connect(
            lambda _=None, x=item: self.open_scene_folder(item)
        )
        # separator
        right_click_menu.addSeparator()
        copy_scene_path_act = right_click_menu.addAction(
            self.tr("Copy Scene Directory to Clipboard")
        )
        copy_scene_path_act.triggered.connect(
            lambda _=None, x=item: self.copy_scene_path(item)
        )

        right_click_menu.exec_(self.sender().viewport().mapToGlobal(position))

    def refresh(self):
        """Re-populate the model keeping the expanded state."""
        self.model.populate(publishes=self.publish_mode)


    def open_scene_folder(self, item):
        """Open the scene folder for the given item.
        Args:
            item (WorkItem or PublishItem):
                The work or publish item to be opened.
        """
        item.work_obj.show_file_folder()

    def copy_scene_path(self, item):
        """Copy the absolute path of the scene file to the clipboard.
        Args:
            item (WorkItem or PublishItem):
                The work or publish item to be copied.
        """
        item.work_obj.copy_path_to_clipboard(item.work_obj.settings_file.absolute())


class CategoryLayout(QtWidgets.QVBoxLayout):

    mode_changed = QtCore.Signal(int)

    def __init__(self, *args, **kwargs):

        super(CategoryLayout, self).__init__(*args, **kwargs)
        self.create_init_ui()
        self.create_init_data()
        self.create_connect()

    def create_init_ui(self):
        header_lay = QtWidgets.QHBoxLayout()
        header_lay.setContentsMargins(0, 0, 0, 0)
        self.addLayout(header_lay)
        self.label = QtWidgets.QLabel("Works")
        self.label.setStyleSheet("font-size: 14px; font-weight: bold;")
        header_lay.addWidget(self.label)
        header_lay.addStretch()

        # self.refresh_btn = IconButton(icon_name="refresh", circle=True, size=18, icon_size=14)
        # header_lay.addWidget(self.refresh_btn)

        self.addWidget(HorizontalSeparator(color=(190, 135, 120)))

        self.work_mode_group = QtWidgets.QButtonGroup()
        self.work_radio_button = CheckButton(
            "Work",
            indicator_size=8,
            indicator_color="#00FF00",
            indicator_margin=10
        )

        self.work_radio_button.setFont(QtGui.QFont("Arial", 10))

        self.publish_radio_button = CheckButton(
            "Publish",
            indicator_size=8,
            indicator_color="#00FF00",
            indicator_margin=10
        )
        self.publish_radio_button.setFont(QtGui.QFont("Arial", 10))

        self.work_radio_button.setChecked(True)
        self.radio_button_layout = QtWidgets.QHBoxLayout()
        self.radio_button_layout.setSpacing(6)
        self.radio_button_layout.addWidget(self.work_radio_button)
        self.radio_button_layout.addWidget(self.publish_radio_button)
        self.work_mode_group.addButton(self.work_radio_button)
        self.work_mode_group.addButton(self.publish_radio_button)
        self.work_mode_group.setExclusive(True)

        self.radio_button_layout.addStretch()
        self.radio_button_layout.setContentsMargins(5, 1, 1, 5)

        self.addLayout(self.radio_button_layout)

        self.work_tree_view = CategoryView()


        self.flow_layout = FlowLayout(spacing=1, margin=1)
        self.addLayout(self.flow_layout)

        self.addWidget(self.work_tree_view)

        self.filter_widget = FilterWidget(self.work_tree_view.proxy_model)
        self.addWidget(self.filter_widget)

    def create_init_data(self):
        self._purgatory_mode = False
        self._last_category = None
        self.task=None
        self.mode = 0

    def create_connect(self):
        self.work_radio_button.clicked.connect(self.on_mode_change)
        self.publish_radio_button.clicked.connect(self.on_mode_change)

    def populate_categories(self, categories):
        self.flow_layout.clearWidgets()
        self.categories_group = QtWidgets.QButtonGroup()
        for category in categories:
            category_btn=BootstrapButton(category)
            category_btn.update_style({
                'main_color': '#6c757d',
                'hover_color': '#0069d9',
                'active_color':'#007bff',
                'border_color': '#ff8e53',
                'padding': (1, 5),
                'font_size': 13
            })
            self.flow_layout.addWidget(category_btn)
            self.categories_group.addButton(category_btn)
            category_btn.clicked.connect(partial(self.on_category_change, category_btn))


    def on_category_change(self, clicked_button):

        if not self.task:
            return

        checked_button = self.categories_group.checkedButton()
        if not checked_button:
            return
        self._last_category=checked_button.text()



        if not self._last_category:
            return

        if self.mode == 0 and self._last_category:
            works = self.task.categories[self._last_category].works
            works_values=works.values()
            self.work_tree_view.model.set_works(works_values)
            self.work_tree_view.setSelectionMode(QtWidgets.QTreeView.SingleSelection)

        else:
            publishes = self.task.categories[self._last_category].publishes
            publishes_values=list(publishes.values())

            exporters = self.task.categories[self._last_category].exporters
            exporters_values = list(exporters.values())

            self.work_tree_view.model.set_publishes(publishes_values+exporters_values)
            self.work_tree_view.setSelectionMode(QtWidgets.QTreeView.ExtendedSelection)



    def on_mode_change(self):

        if self.work_radio_button.isChecked():
            self.mode = 0
            self.work_tree_view.publish_mode = False
            self.mode_changed.emit(0)
        else:
            self.mode = 1
            self.work_tree_view.publish_mode = True
            self.mode_changed.emit(1)

        self.on_category_change(self.categories_group.checkedButton())

    def set_last_category(self):
        if self._last_category and self.categories_group:
            for btn in self.categories_group.buttons():
                if btn.text() == self._last_category:
                    btn.setChecked(True)
        else:
            self.categories_group.buttons()[0].setChecked(True)
            self._last_category = self.categories_group.checkedButton().text()

    def get_active_category(self):
        return self._last_category

    def get_category_index(self):
        return self._last_category

    def get_mode_index(self):
        return self.mode

    def set_mode_index(self, mode_index):

        if mode_index == 0:
            self.work_radio_button.setChecked(True)
        elif mode_index == 1:
            self.publish_radio_button.setChecked(True)
        self.on_mode_change()

    def set_category_by_index(self, category_index):
        if  self.categories_group:
            for btn in self.categories_group.buttons():
                if btn.text() == category_index:
                    btn.setChecked(True)
                    self.on_category_change(self.categories_group.checkedButton())
                    break

    def set_task(self, task):
        if not task:
            self.clear()
            return

        self.task = task
        self.populate_categories(self.task.categories)
        self.set_last_category()
        self.on_category_change(self.categories_group.checkedButton())
        self.work_tree_view.expandAll()

    def clear(self):
        self._last_category=None
        self.flow_layout.clearWidgets()
        self.work_tree_view.model.clear()

    def refresh(self):
        if hasattr(self, 'categories_group'):
            self.on_category_change(self.categories_group.checkedButton())