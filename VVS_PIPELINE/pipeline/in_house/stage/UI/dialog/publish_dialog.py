import os
import logging
import tempfile
from time import time
from stage.external.Qt import QtWidgets, QtCore
import stage
from stage.UI.widgets.common import Label, ResolvedText, ButtonBox, Button, IconButton, VerticalSeparator
from stage.version import __version__
from stage.UI.dialog.message_box import SMessageBox
from stage.UI.widgets import style
from stage.entities.project import Project
from stage.UI.widgets.collapsible_layout import CollapsibleLayout
from stage.UI.widgets.pop import WaitDialog
from stage.UI.widgets import thumbnail
from stage.UI.widgets.resources import resources_rc

LOG = logging.getLogger(__name__)


class PublishSceneDialog(QtWidgets.QDialog):

    def __init__(self, app_object, pipeline_object, project, stage_project_setting, publish_signal='publish', *args,
                 **kwargs):

        super().__init__(*args, **kwargs)
        self.setWindowFlag(QtCore.Qt.WindowContextHelpButtonHint, False)
        self.publish_signal = publish_signal
        self.app = app_object
        self.project = project
        self.pipeline = pipeline_object
        self.stage_project_setting = stage_project_setting
        style_file = style.style_file()
        self.setStyleSheet(str(style_file.readAll(), "utf-8"))

        self._validator_widgets = []
        self._extractor_widgets = []

        self.feedback = SMessageBox(parent=self)

        ret = self.project.publisher.resolve(self.pipeline)

        if not ret:
            self.feedback.pop_info(title="发布", text='文件名解析错误')

        if self.publish_signal == 'publish':
            self.setWindowTitle("Publish Scene")
        if self.publish_signal == 'review':
            self.setWindowTitle("Publish Review")

        self.dialog_layout = QtWidgets.QVBoxLayout(self)

        self.vertical_splitter = None
        self.horizontal_splitter = None

        # layout variables
        self.header_layout = None
        self.validation_header_lay = None
        self.validations_scroll_lay = None
        self.extract_header_lay = None
        self.extracts_scroll_lay = None
        self.bottom_layout = None
        self.notes_text = None
        self.build_ui()

        self.setMinimumWidth(1000)
        self.setMinimumHeight(400)

        self.horizontal_splitter.setSizes([500, 500])
        self.vertical_splitter.setSizes([600, 400])

        self._generate_thumbnail()

    def _generate_thumbnail(self):

        if self.project.publisher.dcc.name not in ['photoshop']:
            return
        output_path = tempfile.NamedTemporaryFile(suffix=".jpg",
                                                  prefix="screencapture_",
                                                  delete=False).name
        self.project.publisher.dcc.generate_thumbnail_full(output_path)
        self.item_thumbnail.set_thumb(output_path)

        if not self.project.publisher.validators.items():
            self.horizontal_splitter.setSizes([0, sum(self.horizontal_splitter.sizes())])
            self.validate_pb.hide()

        return output_path

    def build_ui(self):
        _style_file = style.style_file(file_name="style.qss")
        self.setStyleSheet(str(_style_file.readAll(), "utf-8"))

        master_layout = QtWidgets.QVBoxLayout()
        self.header_layout = QtWidgets.QVBoxLayout()

        self.header_layout.setContentsMargins(10, 10, 10, 10)

        # self._build_header()

        master_layout.addLayout(self.header_layout)

        self.vertical_splitter = QtWidgets.QSplitter(self)
        self.vertical_splitter.setOrientation(QtCore.Qt.Vertical)
        self.vertical_splitter.setHandleWidth(5)
        self.vertical_splitter.setProperty(
            "horizontal", True
        )

        self.vertical_splitter.setChildrenCollapsible(False)

        _body_layout_widget = QtWidgets.QWidget(self.vertical_splitter)
        body_layout = QtWidgets.QHBoxLayout(_body_layout_widget)
        body_layout.setContentsMargins(0, 0, 0, 0)
        self.horizontal_splitter = QtWidgets.QSplitter(_body_layout_widget)
        self.horizontal_splitter.setOrientation(QtCore.Qt.Horizontal)
        self.horizontal_splitter.setHandleWidth(5)
        self.horizontal_splitter.setProperty(
            "vertical", True
        )  # the icon is vertical shaped. IT IS NOT A BUG

        _left_layout_widget = QtWidgets.QWidget(self.horizontal_splitter)
        left_layout = QtWidgets.QVBoxLayout(_left_layout_widget)
        left_layout.setContentsMargins(5, 5, 5, 5)
        self.validation_header_lay = QtWidgets.QVBoxLayout()
        left_layout.addLayout(self.validation_header_lay)

        scroll_area_left = QtWidgets.QScrollArea(_left_layout_widget)
        scroll_area_left.setWidgetResizable(True)
        scroll_area_left_contents = QtWidgets.QWidget()
        self.validations_scroll_lay = QtWidgets.QVBoxLayout(scroll_area_left_contents)
        self._build_validations()
        scroll_area_left.setWidget(scroll_area_left_contents)
        left_layout.addWidget(scroll_area_left)

        _right_layout_widget = QtWidgets.QWidget(self.horizontal_splitter)
        right_layout = QtWidgets.QVBoxLayout(_right_layout_widget)
        right_layout.setContentsMargins(5, 5, 5, 5)
        self.extract_header_lay = QtWidgets.QVBoxLayout()
        right_layout.addLayout(self.extract_header_lay)

        scroll_area_right = QtWidgets.QScrollArea(_right_layout_widget)
        scroll_area_right.setWidgetResizable(True)
        scroll_area_right_contents = QtWidgets.QWidget()
        self.extracts_scroll_lay = QtWidgets.QVBoxLayout(scroll_area_right_contents)

        self._build_extractions()
        scroll_area_right.setWidget(scroll_area_right_contents)
        right_layout.addWidget(scroll_area_right)

        body_layout.addWidget(self.horizontal_splitter)
        # _bottom_layout_widget = QtWidgets.QWidget(self.vertical_splitter)
        self.bottom_layout = QtWidgets.QVBoxLayout()
        self.bottom_layout.setContentsMargins(5, 5, 5, 5)
        self.bottom_lv_layout = QtWidgets.QVBoxLayout()
        self.bottom_rv_layout = QtWidgets.QVBoxLayout()
        self.bottom_h_layout = QtWidgets.QHBoxLayout()
        self.bottom_h_layout.addLayout(self.bottom_lv_layout)
        self.bottom_h_layout.addLayout(self.bottom_rv_layout)
        self.bottom_layout.addLayout(self.bottom_h_layout)
        right_layout.addLayout(self.bottom_layout)

        self._build_bottom()

        master_layout.addWidget(self.vertical_splitter)
        self.dialog_layout.addLayout(master_layout)

    def _build_validations(self):

        validations_label = QtWidgets.QLabel("Validations")
        validations_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        self.validation_header_lay.addWidget(validations_label)
        separator = QtWidgets.QLabel()
        separator.setFrameShape(QtWidgets.QFrame.HLine)
        separator.setFrameShadow(QtWidgets.QFrame.Sunken)
        separator.setStyleSheet("background-color: rgb(221, 160, 221);")
        separator.setFixedHeight(1)
        self.validation_header_lay.addWidget(separator)
        for validator_name, validator in self.project.publisher.validators.items():
            validate_row = ValidateRow(validator_object=validator)
            self.validations_scroll_lay.addLayout(validate_row)
            self._validator_widgets.append(validate_row)

        self.validations_scroll_lay.addStretch()

    def _build_extractions(self):

        extracts_label = QtWidgets.QLabel("extracts")
        extracts_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        self.extract_header_lay.addWidget(extracts_label)
        separator = QtWidgets.QLabel()
        separator.setFrameShape(QtWidgets.QFrame.HLine)
        separator.setFrameShadow(QtWidgets.QFrame.Sunken)
        separator.setStyleSheet("background-color: rgb(221, 160, 221);")
        separator.setFixedHeight(1)
        self.extract_header_lay.addWidget(separator)

        # ADD extracts HERE
        # -------------------
        for _extractor_name, extractor in self.project.publisher.extracts.items():

            extracts_mode = self.stage_project_setting.extracts_mode
            if self.project.publisher.file_infos['abridge'] in extracts_mode.keys():
                if extractor.name not in list(extracts_mode.values())[0].get(self.publish_signal):
                    continue
            extract_row = ExtractRow(extract_object=extractor)
            self.extracts_scroll_lay.addLayout(extract_row)
            self._extractor_widgets.append(extract_row)
        # -------------------

        self.extracts_scroll_lay.addStretch()

    def _build_bottom(self):

        thumbnail_label = QtWidgets.QLabel("Thumbnail:")
        self.item_thumbnail = thumbnail.Thumbnail()
        self.item_thumbnail.setMinimumSize(QtCore.QSize(160, 90))
        self.item_thumbnail.setMaximumSize(QtCore.QSize(160, 90))
        self.item_thumbnail.setText("")
        self.item_thumbnail.setScaledContents(False)
        self.item_thumbnail.setAlignment(QtCore.Qt.AlignCenter)
        self.item_thumbnail.setObjectName("item_thumbnail")
        self.item_thumbnail.setToolTip("Click to take a screenshot.")
        self.item_thumbnail.setAcceptDrops(True)
        self.bottom_rv_layout.addWidget(thumbnail_label)
        self.bottom_rv_layout.addWidget(self.item_thumbnail)
        self.bottom_h_layout.addLayout(self.bottom_rv_layout)

        # notes layout
        notes_label = QtWidgets.QLabel("Notes:")
        # self.bottom_layout.addWidget(notes_label)
        self.notes_text = QtWidgets.QTextEdit()
        self.notes_text.setMaximumHeight(90)
        # add a placeholder text
        self.notes_text.setPlaceholderText("输入发布信息...")
        self.bottom_lv_layout.addWidget(notes_label)
        self.bottom_lv_layout.addWidget(self.notes_text)

        # buttons layout
        button_box = ButtonBox()
        self.validate_pb = button_box.addButton(
            "Validate", QtWidgets.QDialogButtonBox.YesRole
        )
        self.validate_pb.setToolTip("Run all active and available validations checks.")
        publish_pb = button_box.addButton(
            "Publish", QtWidgets.QDialogButtonBox.AcceptRole
        )
        publish_pb.setEnabled(False)  # disable the publish button by default
        publish_pb.setToolTip(
            "Extract the elements and publish the scene. Notes are Mandatory."
        )
        button_box.addButton("Cancel", QtWidgets.QDialogButtonBox.RejectRole)
        self.bottom_layout.addWidget(button_box)

        def _toggle_publish_button():
            """Enable/Disable the publish button. According to the notes."""
            if self.notes_text.toPlainText():
                publish_pb.setEnabled(True)
            else:
                publish_pb.setEnabled(False)

        # SIGNALS
        self.notes_text.textChanged.connect(_toggle_publish_button)
        button_box.rejected.connect(self.reject)
        self.validate_pb.clicked.connect(self.validate_all)
        publish_pb.clicked.connect(self.publish)

    def validate_all(self):
        self.reset_validators()
        for validator_widget in self._validator_widgets:
            # if it is already validated or unchecked skip
            if (
                    validator_widget.validator.state == "passed"
                    or not validator_widget.checkbox.isChecked()
            ):
                continue
            validator_widget.validate()
            # keep updating the ui
            QtWidgets.QApplication.processEvents()

    def extract_all(self, callback_handler=None):

        self.project.publisher.dcc.save_scene()

        for extractor_widget in self._extractor_widgets:
            if not extractor_widget.extract.enabled:
                continue
            if callback_handler:
                callback_handler.set_message(f"Extracting {extractor_widget.extract.name}...")
                callback_handler.display()

            if hasattr(extractor_widget,'parameter'):
                self.project.publisher.extract_single(extractor_widget.extract,extractor_widget.parameter)
            else:
                self.project.publisher.extract_single(extractor_widget.extract,[])

            extractor_widget.set_state(extractor_widget.extract.state)
            if extractor_widget.extract.state == "failed":
                callback_handler.kill()
                q = self.feedback.pop_question(
                    title="Extraction Failed",
                    text=f"Extraction failed for: \n\n{extractor_widget.extract.name}\n\nDo you want to continue?",
                    buttons=["continue", "cancel"],
                )
                if q == "cancel":
                    # self.project.publisher.discard()
                    # self.__init__(self.project)
                    return False
                    # raise Exception("Extraction Failed")
                if q == "continue":
                    continue
            QtWidgets.QApplication.processEvents()
        return True

    def reset_validators(self):
        if self.project.publisher.dcc.is_modified():
            for validator_widget in self._validator_widgets:
                validator_widget.reset()
                validator_widget.update_state()

    def check_validation_state(self):
        """Check all validations and return current state."""
        passes = []
        warnings = []
        fails = []
        idle = []
        for validator_widget in self._validator_widgets:
            if validator_widget.validator.state != "passed":
                passes.append(validator_widget.name)
            if validator_widget.validator.state == "idle":
                idle.append(validator_widget.name)
            if validator_widget.validator.state == "failed":
                if validator_widget.validator.ignorable:
                    warnings.append(validator_widget.name)
                else:
                    fails.append(validator_widget.name)
        return passes, warnings, fails, idle

    def check_extraction_status(self):
        """Check all extractions and return current state."""
        unavailable = []
        for extractor_widget in self._extractor_widgets:
            if extractor_widget.extract.state == "unavailable":
                unavailable.append(extractor_widget.extract.name)
        return unavailable

    def publish(self):

        # self.project.publisher.reserve(self.pipeline)

        img_file = self.item_thumbnail.get_screenshot_file()
        if not img_file:
            self.feedback.pop_info(
                title="截图",
                text=f"截图失败: \n\n请点击截图.",
            )
            return

        pop = WaitDialog(message="Publishing...", parent=self)
        pop.display()

        self.reset_validators()  # only resets if the scene is modified
        self.validate_all()
        # check the state of the validations
        passes, warnings, fails, idle = self.check_validation_state()
        # check for unavailable extractions
        unavailable_extracts = self.check_extraction_status()

        # if there are fails, pop up a dialog
        if fails:
            pop.kill()
            self.feedback.pop_info(
                title="Validation Failed",
                text=f"Validation failed for: \n\n{fails}\n\nPlease fix the validation issues before publishing.",
            )
            return
        # if there are warnings, pop up a dialog
        if warnings:
            pop.kill()
            q = self.feedback.pop_question(
                title="Validation Warnings",
                text=f"Validation warnings for: \n\n{warnings}\n\nDo you want IGNORE them and continue?",
                buttons=["continue", "cancel"],
            )
            if q == "cancel":
                return

        if unavailable_extracts:
            pop.kill()
            q = self.feedback.pop_question(
                title="Extraction Unavailable",
                text=f"Extraction unavailable for: \n\n{unavailable_extracts}\n\nDo you want to continue?",
                buttons=["continue", "cancel"],
            )
            if q == "cancel":
                return

        # reserve the slot
        pop.set_message("Reserving Slot...")
        pop.display()
        self.project.publisher.reserve(self.pipeline, self.publish_signal)
        # extract the elements
        state = self.extract_all(callback_handler=pop)
        if not state:
            pop.kill()
            # user cancellation due to failed extracts
            return

        ret = None
        if self.publish_signal == 'publish':
            ret = self.project.publisher.publish(
                self.pipeline,
                img_file,

                notes=self.notes_text.toPlainText(),
                publish_signal=self.publish_signal
            )
        elif self.publish_signal == 'review':
            ret = self.project.publisher.publish_review(
                self.pipeline,
                img_file,
                notes=self.notes_text.toPlainText(),
                publish_signal=self.publish_signal
            )

        pop.kill()

        if not ret:
            msg = f"Publish Failed"
            self.feedback.pop_info(title="Publish Successful", text=msg)
            return

        msg = f"Publish Successful"
        self.feedback.pop_info(title="Publish Successful", text=msg)
        self.close()
        self.deleteLater()
        return


class ValidateRow(QtWidgets.QHBoxLayout):
    """Custom Layout for validation rows."""

    def __init__(self, validator_object, toaster=None, *args, **kwargs):
        """Initialize the ValidateRow."""
        super(ValidateRow, self).__init__(*args, **kwargs)

        if isinstance(validator_object, list):
            self.validator = validator_object[0]
            self.parameter = validator_object[1]
        else:
            self.validator = validator_object

        self.name = self.validator.nice_name or self.validator.name
        self.build_widgets()
        self.update_state()

    def build_widgets(self):
        """Build the widgets."""
        # status icon
        # create a vertical line with color
        self.status_icon = QtWidgets.QFrame()
        # make it gray
        self.status_icon.setStyleSheet("background-color: gray;")
        # set the width to 10px
        self.status_icon.setFixedWidth(10)
        self.addWidget(self.status_icon)

        # checkbox
        self.checkbox = QtWidgets.QCheckBox()
        self.checkbox.setChecked(self.validator.checked_by_default)
        self.checkbox.setVisible(False)
        self.addWidget(self.checkbox)

        # button
        self.button = Button(text=self.name)
        # stretch it to the layout
        self.button.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding
        )
        self.button.setFixedHeight(26)
        self.addWidget(self.button)

        # maintenance icons
        self.info_pb = IconButton(icon_name="info.png")
        self.info_pb.set_size(26)
        self.select_pb = IconButton(icon_name="select.png")
        self.select_pb.set_size(26)
        self.fix_pb = IconButton(icon_name="fix.png")
        self.fix_pb.set_size(26)
        self.addWidget(self.info_pb)
        self.addWidget(self.select_pb)
        self.addWidget(self.fix_pb)

        # SIGNALS
        self.checkbox.stateChanged.connect(self.update_state)
        self.button.clicked.connect(self.validate)
        self.info_pb.clicked.connect(self.pop_info)
        self.fix_pb.clicked.connect(self.fix)
        self.select_pb.clicked.connect(self.select)

    def validate(self):
        """Validate the validator."""
        start = time()
        LOG.info("validating %s...", self.button.text())
        if hasattr(self, "parameter"):
            self.validator.validate(self.parameter)

        else:
            self.validator.validate()
        self.update_state()
        end = time()
        LOG.info("took %s seconds", end - start)

    def pop_info(self):
        """Pop up an information dialog for informing the user what went wrong."""
        information = self.validator.fail_message
        if information:
            # create a mini dialog with non-editable text
            pop_info_dialog = QtWidgets.QDialog()
            pop_info_dialog.setWindowTitle(f"{self.validator.nice_name} Message")
            pop_info_dialog.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
            pop_info_dialog.setModal(True)
            pop_info_dialog.setMinimumWidth(300)
            pop_info_dialog.setMinimumHeight(200)
            pop_info_dialog.setLayout(QtWidgets.QVBoxLayout())
            text = QtWidgets.QTextEdit()
            text.setReadOnly(True)
            text.setText(information)
            pop_info_dialog.layout().addWidget(text)
            pop_info_dialog.exec_()
        else:
            return

    def fix(self):
        """Auto Fix the scene."""
        start = time()
        LOG.info("fixing %s...", self.button.text())
        self.validator.fix()
        if hasattr(self, "parameter"):
            self.validator.validate(self.parameter)
        else:
            self.validator.validate()

        end = time()
        if self.validator.state != "passed":
            # TODO: pop up a dialog to inform the user that the fix failed
            LOG.info("fix failed")
        self.update_state()

        LOG.info("took %s seconds", end - start)

    def select(self):
        """Select the objects related to the validator."""
        self.validator.select()
        self.update_state()

    def reset(self):
        """Reset the validator."""
        self.validator.reset()
        self.update_state()

    def update_state(self):
        """Update the availablity of the buttons."""

        _autofixable = self.validator.autofixable
        _ignorable = self.validator.ignorable
        _selectable = self.validator.selectable
        _state = self.validator.state

        # update the buttons
        if not _ignorable:
            self.checkbox.setCheckState(QtCore.Qt.Checked)
            self.checkbox.setEnabled(False)

        if self.checkbox.isChecked():
            self.button.setEnabled(True)
        else:
            self.status_icon.setStyleSheet("background-color: gray;")
            self.button.setEnabled(False)
            self.info_pb.setEnabled(False)
            self.select_pb.setEnabled(False)
            self.fix_pb.setEnabled(False)
            return

        if _state == "passed":
            self.status_icon.setStyleSheet("background-color: green;")
            self.info_pb.setEnabled(False)
            self.select_pb.setEnabled(False)
            self.fix_pb.setEnabled(False)

        elif _state == "idle":
            self.status_icon.setStyleSheet("background-color: gray;")
            self.info_pb.setEnabled(False)
            self.select_pb.setEnabled(False)
            self.fix_pb.setEnabled(False)

        else:
            _fail_colour = "yellow" if _ignorable else "red"
            self.status_icon.setStyleSheet(f"background-color: {_fail_colour};")
            if _autofixable:
                self.fix_pb.setEnabled(True)
            else:
                self.fix_pb.setEnabled(False)
            if _selectable:
                self.select_pb.setEnabled(True)
            else:
                self.select_pb.setEnabled(False)
            self.info_pb.setEnabled(True)


class ExtractRow(QtWidgets.QHBoxLayout):
    """Custom Layout for extract rows."""

    def __init__(self, extract_object, *args, **kwargs):
        """Initialize the ExtractRow."""
        super().__init__(*args, **kwargs)

        if isinstance(extract_object, list):
            self.extract = extract_object[0]
            self.parameter = extract_object[1]
        else:
            self.extract = extract_object

        # self.class_name=extract_object.__class__.__name__

        self.status_icon = None
        self.label = None
        self.settings_btn = None
        self.settings_frame = None
        self.global_settings_data = None
        self.settings_data = None
        self.info = None

        self.build_widgets()

    def build_widgets(self):
        """Build the widgets."""
        # status icon
        # create a vertical line with color
        self.status_icon = QtWidgets.QFrame()
        # set the width to 10px
        self.status_icon.setFixedWidth(10)
        self.addWidget(self.status_icon)

        # main
        main_layout = QtWidgets.QVBoxLayout()
        self.addLayout(main_layout)
        header_layout = QtWidgets.QHBoxLayout()
        header_layout.setSpacing(0)
        main_layout.addLayout(header_layout)

        # add a checkbox if the extract is optional
        if self.extract.optional:
            self.checkbox = QtWidgets.QCheckBox()
            # make it to occupy minimum space
            self.checkbox.setFixedWidth(30)
            self.checkbox.setChecked(self.extract.enabled)
            header_layout.addWidget(self.checkbox)
            # SIGNALS
            self.checkbox.stateChanged.connect(self.toggle_enabled)

        self.collapsible_layout = CollapsibleLayout(
            text=self.extract.nice_name or self.extract.name
        )
        self.collapsible_layout.set_color(
            text_color=self.extract.color, border_color=self.extract.color
        )
        self.collapsible_layout.label.set_font_size(10, bold=True)
        header_layout.addLayout(self.collapsible_layout)

        # maintenance icons
        self.info = IconButton(icon_name=self.extract.name, circle=True)
        self.info.set_size(32)
        self.addWidget(self.info)

        # SIGNALS
        self.info.clicked.connect(self.pop_info)

        self.set_state(self.extract.state)
        self.update_message_box()
        self.toggle_enabled(self.extract.enabled)

    def update_message_box(self):
        """Update the info icons border color if there is a message to show."""
        if self.extract.message:
            self.info.set_color(border_color="red")
        else:
            self.info.set_color(border_color=self.extract.color)

    def pop_info(self):
        """Pops up an information dialog."""
        information = self.extract.message
        if information:
            # create a mini dialog with non-editable text
            pop_info_dialog = QtWidgets.QDialog()
            pop_info_dialog.setWindowTitle(f"{self.extract.nice_name} Information")
            pop_info_dialog.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
            pop_info_dialog.setModal(True)
            pop_info_dialog.setMinimumWidth(300)
            pop_info_dialog.setMinimumHeight(200)
            pop_info_dialog.setLayout(QtWidgets.QVBoxLayout())
            text = QtWidgets.QTextEdit()
            text.setReadOnly(True)
            text.setText(information)
            pop_info_dialog.layout().addWidget(text)
            pop_info_dialog.exec_()
        else:
            return

    def toggle_enabled(self, is_enabled):
        """Toggle the enabled state of the extract."""
        self.extract.enabled = is_enabled
        self.collapsible_layout.contents_widget.setEnabled(is_enabled)
        self.set_state(self.extract.state)
        self.info.setEnabled(is_enabled)

    def toggle_settings_visibility(self, state):
        """Toggle the visibility of the settings frame."""
        self.settings_frame.setVisible(state)

    def set_state(self, state):
        """Set the state of the extract."""
        if state == "success":
            self.status_icon.setStyleSheet("background-color: green;")
        elif state == "idle":
            self.status_icon.setStyleSheet("background-color: #FF8D1C;")
        elif state == "failed":
            self.status_icon.setStyleSheet("background-color: red;")
        elif state == "unavailable":
            self.status_icon.setStyleSheet("background-color: gray;")
        elif state == "disabled":  # this is for optional extracts
            self.status_icon.setStyleSheet("background-color: gray;")
        else:
            pass
        return
