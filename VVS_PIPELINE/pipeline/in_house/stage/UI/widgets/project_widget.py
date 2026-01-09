import os
from stage.external.Qt import QtCore, QtGui, QtWidgets
from stage.UI.widgets.common import IconButton,HorizontalSeparator
from stage.UI.widgets import style
from stage.UI.widgets import utils
from stage.UI.widgets.pop import WaitDialog

class ProjectWidget(QtWidgets.QWidget):

    def __init__(self, main_object, parent=None):
        super().__init__()
        self.parent = parent
        self.main_object = main_object
        self.v_lay = QtWidgets.QVBoxLayout()
        self.v_lay.setContentsMargins(0, 0, 0, 0)
        self.h_lay = ProjectLayout(main_object, parent=self.v_lay)
        self.v_lay.addLayout(self.h_lay)
        #self.v_lay.addWidget(HorizontalSeparator(color=(121, 17, 191),height=1))
        self.setLayout(self.v_lay)


        self.h_lay.project_refresh_sig.connect(self.refresh)

    def refresh(self):
        pop = WaitDialog(message="Refresh ... ", parent=self.parent)
        pop.display()
        self.main_object.set_last_state()
        self.main_object.create_data(refresh=True)
        self.main_object.resume_last_state()
        pop.kill()

class ProjectLayout(QtWidgets.QHBoxLayout):

    project_refresh_sig = QtCore.Signal()

    def __init__(self, main_object, parent=None):
        super().__init__()
        self.parent = parent
        self.main_object = main_object

        self.management_icon = QtWidgets.QLabel()
        self.management_icon.setScaledContents(True)

        self.project_name_label = QtWidgets.QLabel(os.environ.get('project_name'))
        #self.project_name_label.setVisible(False)

        self.project_name_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        self.addWidget(self.project_name_label)
        self.horizontal_spacer = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.addItem(self.horizontal_spacer)
        self.refresh_btn = QtWidgets.QToolButton()
        icon = utils.getColoredIcon("refresh_color")
        self.refresh_btn.setIcon(icon)
        self.refresh_btn.setIconSize(QtCore.QSize(24, 24))
        self.refresh_btn.setToolTip("Refresh")

        #self.refresh_btn = IconButton(icon_name="refresh", circle=True, size=24, icon_size=20)
        self.addWidget(self.refresh_btn)
        self.refresh_btn.clicked.connect(self.refresh)
        self._set_management_icon()
        self.setContentsMargins(10, 0, 10, 0)


    def _set_management_icon(self):

        management_platform_name ='stage'
        logo = f"logo-{management_platform_name}.png"
        # set the size to 32x32
        self.management_icon.setPixmap(style.pixmap(logo))
        self.management_icon.setFixedSize(40, 40)


    def refresh(self):
        self.project_refresh_sig.emit()

