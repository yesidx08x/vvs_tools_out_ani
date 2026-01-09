from collections import deque
from stage.external.Qt import QtWidgets, QtCore, QtGui
from stage.external.Qt.QtWidgets import QMessageBox
import stage
from stage.UI.widgets import style
from stage.UI.widgets.filter import FilterModel,FilterWidget
from stage.UI.widgets.color_delegate import ColorKeepingDelegate
from stage.UI.widgets.common import IconButton,HorizontalSeparator


class ProxyModel(FilterModel):
    def __init__(self, parent=None):
        super(ProxyModel, self).__init__(parent=parent)

    def filterAcceptsRow(self, source_row, source_parent):
        model = self.sourceModel()
        index = model.index(source_row, 0, QtCore.QModelIndex())

        item = model.itemFromIndex(index)
        if isinstance(item, ProductionItem):
            pass

        return super(ProxyModel, self).filterAcceptsRow(source_row, source_parent)


class ProductionItem(QtGui.QStandardItem):
    def __init__(self, sub_obj):
        super(ProductionItem, self).__init__()
        self.subproject = sub_obj
        self.setText(sub_obj.name)
        self.setEditable(False)
        self.refresh()

    def refresh(self):
        self.setForeground(QtGui.QColor(255, 255 ,255))
        self.setFont(QtGui.QFont("Open Sans", 12, italic=False))
        _icon = style.icon(f"{self.subproject.type}.png")
        self.setIcon(_icon)

class ProductionColumnItem(QtGui.QStandardItem):
    def __init__(self, name, overridden=False):
        super(ProductionColumnItem, self).__init__()

        self.setEditable(False)
        self.setText(name)
        self.set_overridden(overridden)

    def set_value(self, value):
        self.setText(str(value))

    def set_overridden(self, value):
        if value:
            self.tag_overridden()
        else:
            self.tag_normal()

    def tag_overridden(self):
        fnt = QtGui.QFont("Open Sans", 10)
        fnt.setBold(False)
        # make it yellow
        self.setForeground(QtGui.QColor(0, 0, 0))
        self.setFont(fnt)

    def tag_normal(self):
        fnt = QtGui.QFont("Open Sans", 10)
        fnt.setBold(False)
        self.setFont(fnt)

class ProductionModel(QtGui.QStandardItemModel):
    def __init__(self, project_object):
        super(ProductionModel, self).__init__()
        self.columns = ["name", "id","path"]
        self.setHorizontalHeaderLabels(self.columns)
        self.project = None
        self.root_item = None
        self.set_data(project_object)

    def set_data(self, project_object):
        self.project = project_object

    def populate(self):
        self.setRowCount(0)
        visited = set()
        queue = deque()

        all_data = {
            "id": self.project.id,
            "name": self.project.name,
            "tasks": self.project.tasks,
            "subs": [],
        }

        parent_row = self
        self.root_item = ProductionItem(self.project)
        self.root_item.setForeground(QtGui.QColor(255, 255, 255, 0))
        self.root_item.setText("Project Root")
        parent_row.appendRow(self.root_item)
        queue.append([all_data, self.project, self.root_item])
        while queue:
            current = queue.popleft()
            parent, sub, parent_row = current
            for neighbour in list(sub.subs.values()):
                if neighbour not in visited:
                    sub_data = {
                        "id": neighbour.id,
                        "name": neighbour.name,
                        "path": neighbour.path,
                        "tasks": neighbour.tasks,
                        "subs": [],
                    }

                    parent["subs"].append(sub_data)
                    _item = self.append_sub(neighbour, parent_row)

                    visited.add(neighbour)
                    queue.append([sub_data, neighbour, _item])
        return all_data

    def append_sub(self, sub_obj, parent):
        _sub_item = ProductionItem(sub_obj)
        _row = [_sub_item,
                ProductionColumnItem(str(sub_obj.id)),
                ProductionColumnItem(sub_obj.path)
                ]
        for column in self.columns[3:]:  # skip the first 3 columns which are mandatory
            _column_value = 'aa'
            _overridden = True
            _column_item = ProductionColumnItem(str(_column_value), _overridden)
            _row.append(_column_item)
        parent.appendRow(_row)
        return _sub_item

    def update_item(self, item, sub_obj):
        """Update the item with the new subproject object"""
        item.subproject = sub_obj
        item.setText(sub_obj.name)

        # get the parent item
        _parent = item.parent()

        # get the row of the item
        _row = item.row()

        for index, column in enumerate(self.columns):
            if _parent:
                _column_item = _parent.child(_row, index)
            else:
                _column_item = self.item(_row, index)
            if isinstance(_column_item, ProductionColumnItem):
                _column_value = sub_obj.metadata.get_value(column, "")
                _overridden = sub_obj.metadata.is_overridden(column)
                _column_item.set_overridden(_overridden)
                _column_item.set_value(str(_column_value))

    def find_item_by_id_column(self, unique_id):
        """Search entire tree and find the matching item."""

        # get EVERY item in this model
        _all_items = self.findItems(
            "*", QtCore.Qt.MatchWildcard | QtCore.Qt.MatchRecursive
        )
        for x in _all_items:
            if isinstance(x, ProductionItem):
                if x.subproject.id == unique_id:
                    return x

    def find_item_by_path_column(self, path):
        """Search entire tree and find the matching item."""

        # get EVERY item in this model
        _all_items = self.findItems(
            "*", QtCore.Qt.MatchWildcard | QtCore.Qt.MatchRecursive
        )
        for x in _all_items:
            if isinstance(x, ProductionItem):
                if x.subproject.path == path:
                    return x

class ProductionView(QtWidgets.QTreeView):
    item_selected = QtCore.Signal(object)
    add_item = QtCore.Signal(object)

    def __init__(self, project_obj=None, right_click_enabled=True):
        super(ProductionView, self).__init__()
        self.purgatory_mode = False
        self.setItemDelegate(ColorKeepingDelegate())

        self._recursive_task_scan = False
        self._feedback = QMessageBox(self)
        self.setUniformRowHeights(True)
        self.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)

        self.model = None
        self.proxy_model = None
        if project_obj:
            self.set_project(project_obj)

        # SIGNALS

        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        if right_click_enabled:
            self.customContextMenuRequested.connect(self.right_click_menu)

        # create another context menu for columns
        self.header().setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.header().customContextMenuRequested.connect(self.header_right_click_menu)

        self.setItemsExpandable(True)

        # show the root
        self.setRootIsDecorated(False)

        self.is_management_locked = False

        # allow multiple selection but only with ctrl
        self.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Control:
            self.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        else:
            super().keyPressEvent(event)

    def keyReleaseEvent(self, event):
        if event.key() == QtCore.Qt.Key_Control:
            self.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        else:
            super().keyReleaseEvent(event)

    # override the right click Event
    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.RightButton:
            self.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        else:
            super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.RightButton:
            self.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        else:
            super().mouseReleaseEvent(event)

    def expand_first_item(self):
        """Try to expand the first item in the tree"""
        index = self.proxy_model.mapFromSource(self.model.index(0, 0))
        self.expand(index)

    def select_first_item(self):
        """Select the first item in the tree"""
        index = self.proxy_model.mapFromSource(self.model.index(0, 0))
        self.setCurrentIndex(index)

    def find_items_in_tree(self, root_item, text):
        matched_items = []

        # Search for items in the root item
        matched_items += root_item.findItems(text, QtCore.Qt.MatchExactly, column=1)

        # Recursively search for items in each child item
        for child_item in root_item.childItems():
            matched_items += self.find_items_in_tree(child_item, text)

        return matched_items

    def get_items_count(self):
        """Return the number of items in the tree under selected one"""

        # count all items
        _all_items = self.model.findItems(
            "*", QtCore.Qt.MatchWildcard | QtCore.Qt.MatchRecursive
        )
        return len(_all_items)

    def select_by_id(self, unique_id, append=False):

        match_item = self.model.find_item_by_id_column(unique_id)
        if match_item:
            idx = match_item.index()
            idx = idx.sibling(idx.row(), 0)
            index = self.proxy_model.mapFromSource(idx)
            if append:
                self.selectionModel().select(
                    index, QtCore.QItemSelectionModel.Select | QtCore.QItemSelectionModel.Rows
                )
            else:
                self.setCurrentIndex(index)
            return True

        return False

    def select_by_path(self, path, append=False):

        match_item = self.model.find_item_by_path_column(path)
        if match_item:
            idx = match_item.index()
            idx = idx.sibling(idx.row(), 0)
            index = self.proxy_model.mapFromSource(idx)
            if append:
                self.selectionModel().select(
                    index, QtCore.QItemSelectionModel.Select | QtCore.QItemSelectionModel.Rows
                )
            else:
                self.setCurrentIndex(index)
            return True

        return False

    def selectionChanged(self, *args, **kwargs):
        super(ProductionView, self).selectionChanged(*args, **kwargs)
        self.get_tasks()

    def get_selected_items(self):
        """Return the current item."""
        selected_items = []
        # get selected indexes
        selected_indexes = self.selectedIndexes()
        # idx = self.currentIndex()
        for idx in selected_indexes:
            if not idx.isValid():
                return None
            idx = idx.sibling(idx.row(), 0)

            # the id needs to mapped from proxy to source
            index = self.proxy_model.mapToSource(idx)
            _item = self.model.itemFromIndex(index)
            if _item not in selected_items:
                selected_items.append(_item)
        return selected_items

    def set_recursive_task_scan(self, value):
        self._recursive_task_scan = value
        # refresh the view
        self.get_tasks()

    def _save_expanded_state(self, index, expanded_state):
        """Stores the subproject ids of the expanded items"""
        view_index = self.proxy_model.mapFromSource(index)
        if self.isExpanded(view_index):
            # get the item from index
            _item = self.model.itemFromIndex(index)
            expanded_state.append(_item.subproject.id)

        for row in range(self.model.rowCount(index)):
            child_index = self.model.index(row, 0, index)
            self._save_expanded_state(child_index, expanded_state)

    def _restore_expanded_state(self, index, expanded_state):
        """Restores the expanded state of the items by matching the subproject ids"""
        view_index = self.proxy_model.mapFromSource(index)
        _item = self.model.itemFromIndex(index)
        if _item:
            if _item.subproject.id in expanded_state:
                self.expand(view_index)

        for row in range(self.model.rowCount(index)):
            child_index = self.model.index(row, 0, index)
            self._restore_expanded_state(child_index, expanded_state)

    def get_expanded_state(self):
        """Returns the subproject ids of the expanded items"""
        expanded_state = []
        self._save_expanded_state(QtCore.QModelIndex(), expanded_state)
        return expanded_state

    def set_expanded_state(self, expanded_state):
        """Sets the expanded state of the items by matching the subproject ids"""
        self._restore_expanded_state(QtCore.QModelIndex(), expanded_state)

    def refresh(self):
        """Re-populates the model keeping the expanded state"""
        # store the expanded items
        # get the selected items
        selected_items = self.get_selected_items()

        expanded_state = self.get_expanded_state()

        self.model.populate()
        self.set_expanded_state(expanded_state)
        self.clearSelection()
        # self.select_first_item()
        # re-select the selected items
        if not selected_items:
            self.select_first_item()
            return
        for item in selected_items:
            self.select_by_id(item.subproject.id, append=True)
        return

    def expandAll(self):
        super(ProductionView, self).expandAll()
        self.resizeColumnToContents(0)
        self.resizeColumnToContents(1)
        self.resizeColumnToContents(2)
        self.resizeColumnToContents(3)
        self.resizeColumnToContents(4)

    @staticmethod
    def collect_tasks(sub_items, recursive=True, filtered=True):
        if not isinstance(sub_items, list):
            sub_items = [sub_items]
        for sub_item in sub_items:
            if not isinstance(sub_item, stage.entities.sub_production.SubProduction):
                # just to prevent crashes if something goes wrong
                return
            sub_item.scan_tasks()
            tasks = sub_item.tasks if filtered else sub_item.all_tasks
            for key, value in tasks.items():
                yield value

            if recursive:
                queue = list(sub_item.subs.values())
                while queue:
                    sub = queue.pop(0)
                    sub.scan_tasks()
                    tasks = sub.tasks if filtered else sub.all_tasks
                    for key, value in tasks.items():
                        yield value
                    queue.extend(list(sub.subs.values()))

    def get_tasks(self, idx=None):
        """Returns the tasks of the selected subproject"""
        selected_indexes = self.selectedIndexes()

        if not selected_indexes:
            self.item_selected.emit([])
            return
        sub_project_objects = []
        for idx in selected_indexes:
            # Make sure the idx is pointing to the first column
            first_idx = idx.sibling(idx.row(), 0)
            # The id needs to be mapped from proxy to source
            index = self.proxy_model.mapToSource(first_idx)
            _item = self.model.itemFromIndex(index) or self.model.root_item
            if _item:
                sub_project_objects.append(_item.subproject)
        _tasks = self.collect_tasks(
            sub_project_objects, recursive=self._recursive_task_scan, filtered=not self.purgatory_mode
        )
        self.item_selected.emit(_tasks)

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
        """Hide/unhide the given column."""
        if state:
            self.unhide_columns(column)
        else:
            self.hide_columns(column)

    def hide_all_columns(self):
        """Hides all columns."""
        for column in self.model.columns:
            self.hide_columns(column)

    def hide_no_name_columns(self):
        for idx in range(1, self.header().count()):
            self.hideColumn(idx)

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

    def set_project(self, project_obj):
        self.model = ProductionModel(project_obj)

        self.proxy_model = ProxyModel()
        self.proxy_model.setSourceModel(self.model)
        self.proxy_model.setRecursiveFilteringEnabled(True)
        self.setSortingEnabled(True)
        # set sort indicator to ascending
        self.sortByColumn(0, QtCore.Qt.AscendingOrder)
        self.setModel(self.proxy_model)
        self.model.populate()

    def header_right_click_menu(self, position):
        """Creates a right click menu for the header"""

        menu = QtWidgets.QMenu(self)

        # add checkable actions for each column
        for column in self.model.columns:
            action = QtWidgets.QAction(column, self)
            action.setCheckable(True)
            action.setChecked(not self.isColumnHidden(self.model.columns.index(column)))
            # connect the action to the column's visibility
            action.toggled.connect(lambda state, c=column: self.toggle_column(c, state))
            menu.addAction(action)
        # add a separator
        menu.addSeparator()
        # add a ALL item to select all columns
        all_action = QtWidgets.QAction("All", self)
        menu.addAction(all_action)
        all_action.triggered.connect(lambda: self.show_columns(self.model.columns))
        # add a NONE item to select no columns
        none_action = QtWidgets.QAction("None", self)
        menu.addAction(none_action)
        none_action.triggered.connect(lambda: self.hide_all_columns())
        menu.exec_(self.mapToGlobal(position))

    def right_click_menu(self, position):
        """Create a right click menu for the view.

        Args:
            position (QPoint): The position of the right click.
        """
        indexes = self.sender().selectedIndexes()
        index_under_pointer = self.indexAt(position)
        if not index_under_pointer.isValid():
            # If nothing is selected, that means we are referring to the root item
            item = self.model.root_item
        else:
            # make sure the idx is pointing to the first column
            index_under_pointer = index_under_pointer.sibling(
                index_under_pointer.row(), 0
            )
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
        right_click_menu = QtWidgets.QMenu(self)


        right_click_menu.exec_(self.sender().viewport().mapToGlobal(position))


class ProductionLayout(QtWidgets.QVBoxLayout):

    mode_changed = QtCore.Signal(int)

    def __init__(self, project,*args, **kwargs):

        super(ProductionLayout, self).__init__(*args, **kwargs)
        self.project = project
        self.create_init_ui()

    def create_init_ui(self):
        header_lay = QtWidgets.QHBoxLayout()
        header_lay.setContentsMargins(0, 0, 0, 0)
        self.addLayout(header_lay)
        self.label = QtWidgets.QLabel("Productions")
        self.label.setStyleSheet("font-size: 14px; font-weight: bold;")
        header_lay.addWidget(self.label)
        header_lay.addStretch()

        # self.refresh_btn = IconButton(icon_name="refresh", circle=True, size=18, icon_size=14)
        # header_lay.addWidget(self.refresh_btn)

        self.addWidget(HorizontalSeparator(color=(17, 215, 191)))
        self.production_view=ProductionView(self.project)
        self.addWidget(self.production_view)

        self.filter_widget = FilterWidget(self.production_view.proxy_model)
        self.addWidget(self.filter_widget)