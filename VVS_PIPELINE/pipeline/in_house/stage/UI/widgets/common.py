from stage.external.Qt import QtCore, QtGui, QtWidgets
import math
from functools import partial
from collections import OrderedDict
import collections.abc
import re
from stage.UI.widgets import style

FONT = "Arial"

BUTTON_STYLE = """
QPushButton
{
    color: #b1b1b1;
    background-color: #404040;
    border-width: 1px;
    border-color: #1e1e1e;
    border-style: solid;
    padding: 5px;
    font-size: 12x;
    border-radius: 4px;
}

QPushButton:hover
{
    background-color: #505050;
    border: 1px solid #ff8d1c;
}

QPushButton:hover[circle=true]
{
    background-color: #505050;
    border: 2px solid #ff8d1c;
}

QPushButton:disabled {
    color: #505050;
    background-color: #303030;
    border: 1px solid #404040;
    border-width: 1px;
    border-color: #1e1e1e;
    border-style: solid;
    padding: 5px;
    font-size: 12x;
}

QPushButton:pressed {
  background-color: #ff8d1c;
  border: 1px solid #ff8d1c;
}
"""


class StyleEditor:
    """Convenience class to edit the style of a widget."""

    background_color = "#404040"
    text_color = "#b1b1b1"
    border_color = "#1e1e1e"

    def _update(self, old, new):
        for k, v in new.items():
            if isinstance(v, collections.abc.Mapping):
                old[k] = self._update(old.get(k, {}), v)
            else:
                old[k] = v
        return old

    def _append_style(self, new_style):
        """Append style to the current style sheet."""
        # if the style argument is not dictionary, convert it to dictionary
        if not isinstance(new_style, dict):
            new_style = self.stylesheet_to_dictionary(new_style)
        current_style_dict = self.stylesheet_to_dictionary(self.styleSheet())

        current_style_dict = self._update(current_style_dict, new_style)

        self.setStyleSheet(self.dictionary_to_stylesheet(current_style_dict))
        self.style().unpolish(self)
        self.style().polish(self)

    @staticmethod
    def stylesheet_to_dictionary(stylesheet):
        # Regular expression patterns for extracting style information
        selector_pattern = re.compile(
            r"(\w+(?:\s*:\s*\w+)?(?:\[[^\]]+\])?)\s*{([^}]*)}"
        )
        property_pattern = re.compile(r"\s*([^:]+)\s*:\s*([^;]+);")

        styles = {}
        for match in selector_pattern.finditer(stylesheet):
            selector = match.group(1)
            properties = {}
            for prop_match in property_pattern.finditer(match.group(2)):
                properties[prop_match.group(1)] = prop_match.group(2)
            styles[selector] = properties

        return styles

    @staticmethod
    def dictionary_to_stylesheet(styles):
        stylesheet = ""
        for selector, properties in styles.items():
            stylesheet += f"{selector} {{\n"
            for prop, value in properties.items():
                stylesheet += f"    {prop}: {value};\n"
            stylesheet += "}\n"

        return stylesheet


class ClickableFrame(QtWidgets.QFrame):
    """Clickable frame widget."""

    clicked = QtCore.Signal()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def mousePressEvent(self, event):
        self.clicked.emit()
        return super().mousePressEvent(event)


class StyleFrame(ClickableFrame, StyleEditor):
    """Frame with custom styler."""

    pass


def lighten_color(color_str, factor=110):
    """
    Lightens the given color.

    Args:
        color_str (str): The color to lighten as a hex string.
        factor (int): The percentage to lighten (100 = no change, >100 = lighter, <100 = darker).

    Returns:
        str: A lighter color as a hex string.
    """
    color = QtGui.QColor(
        color_str)  # Automatically handles both #RRGGBB and "rgb(r,g,b)"
    lighter_color = color.lighter(
        factor)  # Increase brightness by the given factor
    return lighter_color.name()  # Returns as hex string


class Button(QtWidgets.QPushButton, StyleEditor):
    """Unified button class for the whole app."""

    def __init__(self,
                 text="",
                 font_size=10,
                 text_color="#b1b1b1",
                 border_color="#1e1e1e",
                 background_color="#404040",
                 *args,
                 **kwargs,
                 ):
        super().__init__()
        # make sure the button has a font defined for different OS scales
        self.setText(text)
        self.text_color = text_color
        self.border_color = border_color
        self.background_color = background_color
        self.set_font_size(font_size)
        self.setStyleSheet(BUTTON_STYLE)
        self.set_color(text_color, background_color, border_color)

    def set_font_size(self, font_size):
        self.setFont(QtGui.QFont(FONT, font_size))

    def set_color(self, text_color=None, background_color=None, border_color=None):
        color, background_color, border_color = [
            "rgb({}, {}, {})".format(*var) if isinstance(var, (tuple, list)) else var
            for var in [text_color, background_color, border_color]
        ]

        text_color = text_color or self.text_color
        background_color = background_color or self.background_color
        border_color = border_color or self.border_color

        color_style = f"""
        QPushButton
        {{
        color: {text_color};
        background-color: {background_color};
        border-color: {border_color};
        }}
        QPushButton:hover
        {{
        background-color: {lighten_color(background_color)};
        border: 1px solid #ff8d1c;
        }}
        """

        self._append_style(color_style)


class IconButton(Button):
    """Button specific for fixed sized icons."""

    def __init__(self, icon_name=None, circle=True, size=22, icon_size=None, **kwargs):
        super().__init__(**kwargs)
        self.radius = int(size * 0.5)
        self.circle = circle
        self.set_size(size)
        self._icon_size = icon_size

        if icon_name:
            self.set_icon(icon_name)

    def set_icon(self, icon_name):
        self.setIcon(style.icon(icon_name))
        # double the size of the icon
        if self._icon_size:
            self.setIconSize(QtCore.QSize(self._icon_size, self._icon_size))

    def set_size(self, size):
        self.setFixedSize(size, size)
        self.radius = int(size * 0.5)
        if self.circle:
            borders_style = {
                "QPushButton": {"border-radius": f"{self.radius}"},
                "QPushButton:disabled": {"border-radius": f"{self.radius}"},
            }
        else:
            borders_style = {
                "QPushButton": {"border-radius": "4px"},
                "QPushButton:disabled": {"border-radius": "4px"},
            }
        self._append_style(borders_style)

    @staticmethod
    def square_to_circle_multiplier(side_length):
        diagonal = math.sqrt(2) * side_length
        radius = diagonal * 0.5
        multiplier = radius / side_length
        return multiplier


class ButtonBox(QtWidgets.QDialogButtonBox):
    """Unified button box class for the whole app."""

    def __init__(self, *args, font_size=10, **kwargs):
        super(ButtonBox, self).__init__(*args, **kwargs)
        self.font_size = font_size
        for button in self.buttons():
            self.modifyButton(button)

    def set_font_size(self, font_size):
        self.font_size = font_size
        for button in self.buttons():
            self.modifyButton(button)

    def event(self, event):
        if event.type() == QtCore.QEvent.ChildAdded:
            child = event.child()
            self.modifyButton(child)
        return super(ButtonBox, self).event(event)

    def modifyButton(self, button):
        button.setFont(QtGui.QFont(FONT, self.font_size))
        button.setMinimumWidth(100)
        button.setStyleSheet(BUTTON_STYLE)


class MessageBox(QtWidgets.QMessageBox):
    def __init__(self, *args, font_size=10, **kwargs):
        super(MessageBox, self).__init__(*args, **kwargs)
        self.set_font_size(font_size)

    def set_font_size(self, font_size):
        self.setFont(QtGui.QFont(FONT, font_size))


class SLabel(QtWidgets.QLabel, StyleEditor):
    """Unified label class for the whole app."""

    def __init__(self, *args, text="", font_size=10, color=(255, 255, 255), **kwargs):
        super(SLabel, self).__init__(*args, **kwargs)
        self.color = color
        self.set_font_size(font_size)
        self.set_color(text_color=self.color, border_color=self.color)

    def set_font_size(self, font_size, bold=False):
        if bold:
            self.setFont(QtGui.QFont(FONT, font_size, QtGui.QFont.Bold))
        else:
            self.setFont(QtGui.QFont(FONT, font_size))

    def set_color(self, text_color=None, background_color=None, border_color=None):

        color, background_color, border_color = [
            "rgb({}, {}, {})".format(*var) if isinstance(var, (tuple, list)) else var
            for var in [text_color, background_color, border_color]
        ]

        text_color = text_color or self.text_color
        border_color = border_color or self.border_color

        color_style = f"""
        QLabel
        {{
        color: {text_color};
        border-color: {border_color};
        }}"""

        self._append_style(color_style)

    def set_text(self, text):
        self.setText(text)


class LabelButton(Button):
    """Customize the button to be used next to the header."""

    style_sheet = """
    QPushButton
    {{
        color: {0};
        background-color: #404040;
        border-width: 1px;
        border-color: {0};
        border-style: solid;
        padding: 5px;
        font-size: 12x;
        border-radius: 0px;
    }}"""

    def __init__(self, *args, color=(255, 255, 255), **kwargs):
        super(LabelButton, self).__init__(*args, **kwargs)
        self.normal_text = kwargs.get("text", ">")
        self.clicked_text = "˅"
        self.setText(self.normal_text)
        # make the button checkable
        self.setCheckable(True)
        self.setProperty("label", True)
        self.set_color(text_color=color, border_color=color)
        self.toggled.connect(self.set_state_text)

    # override the checked state
    def set_state_text(self, checked):
        if checked:
            self.setText(self.clicked_text)
        else:
            self.setText(self.normal_text)


class HeaderLabel(SLabel):
    """Label with bold font and indent."""

    style_sheet = """
QLabel
{
    background-color: #404040;
    border-width: 1px;
    border-color: #1e1e1e;
    border-style: solid;
    padding: 5px;
    font-size: 12x;
    border-radius: 5px;
}
"""

    def __init__(self, *args, **kwargs):
        super(HeaderLabel, self).__init__(*args, **kwargs)
        self.setProperty("header", True)
        self.setIndent(10)
        self.setFixedHeight(30)
        self.setFrameShape(QtWidgets.QFrame.Box)
        # center text
        self.setAlignment(QtCore.Qt.AlignCenter)
        self.color = (255, 0, 255)
        self.setStyleSheet(self.style_sheet)
        self.style().unpolish(self)
        self.style().polish(self)

    def set_font_size(self, font_size, bold=True):
        super(HeaderLabel, self).set_font_size(font_size, bold)


class ResolvedText(SLabel):
    """Label for resolved paths, names etc."""

    def __init__(self, *args, **kwargs):
        super(ResolvedText, self).__init__(*args, **kwargs)
        # make is selectable
        self.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
        # make is wrap
        self.setWordWrap(True)

    def set_font_size(self, font_size, bold=True):
        super(ResolvedText, self).set_font_size(font_size, bold)


class VerticalSeparator(QtWidgets.QLabel):
    """Simple horizontal separator."""

    def __init__(self, color=(100, 100, 100), height=25, width=20):
        super(VerticalSeparator, self).__init__()
        self._pixmap = QtGui.QPixmap(2, 100)
        self.set_color(color)
        self.setPixmap(self._pixmap)
        self.setFixedHeight(height)
        self.setFixedWidth(width)
        self.setAlignment(QtCore.Qt.AlignCenter)

    def set_color(self, color):
        self._pixmap.fill(QtGui.QColor(*color))


class HorizontalSeparator(QtWidgets.QLabel):
    """Simple vertical separator."""

    def __init__(self, color=(100, 100, 100), height=1, width=None):
        super(HorizontalSeparator, self).__init__()
        self.set_color(color)
        self.setFrameShape(QtWidgets.QFrame.HLine)
        self.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.setFixedHeight(height)
        if width:
            self.setFixedWidth(width)

    def set_color(self, color):
        if isinstance(color, (tuple, list)):
            color = f"rgb({color[0]}, {color[1]}, {color[2]});"
        self.setStyleSheet(f"background-color: {color};")


class FlowLayout(QtWidgets.QLayout):
    def __init__(self, parent=None, margin=0, spacing=-1):
        super(FlowLayout, self).__init__(parent)

        self.itemList = []
        self.setSpacing(spacing)
        self.setContentsMargins(margin, margin, margin, margin)

    def __del__(self):
        item = self.takeAt(0)
        while item:
            item = self.takeAt(0)

    def addItem(self, item):
        """将子控件项添加进布局"""
        self.itemList.append(item)

    def count(self):
        return len(self.itemList)

    def itemAt(self, index):
        if 0 <= index < len(self.itemList):
            return self.itemList[index]
        return None

    def takeAt(self, index):
        if 0 <= index < len(self.itemList):
            return self.itemList.pop(index)
        return None

    def expandingDirections(self):
        """流式布局通常不在某个方向上强行扩展"""
        return QtCore.Qt.Orientations(QtCore.Qt.Orientation(0))

    def hasHeightForWidth(self):
        """如果返回 True，则意味着 height 依赖于 width"""
        return True

    def heightForWidth(self, width):
        """根据给定宽度计算合适的高度"""
        height = self.doLayout(QtCore.QRect(0, 0, width, 0), True)
        return height

    def setGeometry(self, rect):
        """实际摆放子控件的位置"""
        super(FlowLayout, self).setGeometry(rect)
        self.doLayout(rect, False)

    def sizeHint(self):
        return self.minimumSize()

    def minimumSize(self):
        size = QtCore.QSize()
        for item in self.itemList:
            sizeItem = item.sizeHint()
            size.setWidth(max(size.width(), sizeItem.width()))
            size.setHeight(size.height() + sizeItem.height())
        return size

    def doLayout(self, rect, testOnly):
        x = rect.x()
        y = rect.y()
        lineHeight = 0

        for item in self.itemList:
            w = item.widget()
            spaceX = self.spacing()
            spaceY = self.spacing()
            nextX = x + item.sizeHint().width() + spaceX
            if nextX - spaceX > rect.right() and lineHeight > 0:
                # 换行
                x = rect.x()
                y = y + lineHeight + spaceY
                nextX = x + item.sizeHint().width() + spaceX
                lineHeight = 0

            if not testOnly:
                item.setGeometry(QtCore.QRect(QtCore.QPoint(x, y), item.sizeHint()))

            x = nextX
            lineHeight = max(lineHeight, item.sizeHint().height())
        return y + lineHeight - rect.y()

    def clearWidgets(self):
        while self.count():
            item = self.takeAt(0)
            if item.widget():
                w = item.widget()
                w.setParent(None)
                w.deleteLater()

            elif item.layout():
                self.clearWidgets(item.layout())


class BootstrapButton(QtWidgets.QPushButton):

    def __init__(self, text="", icon=None, parent=None):
        super().__init__(text, parent)
        self._default_config = {
            'font_family': 'Segoe UI',
            'font_size': 13,
            'icon_size': QtCore.QSize(16, 16),
            'padding': (1, 5),  # (垂直, 水平)
            'border_radius': 5,
            'main_color': '#6c757d',
            'hover_color': '#5a6268',
            'active_color': '#5a6268',
            'border_color': '#007bff',
            'border_width': 2,
            'text_color': '#ffffff',
            'box_shadow': '0 2px 4px rgba(0, 0, 0, 0.15)',
            'hover_shadow': '0 3px 6px rgba(0, 0, 0, 0.2)'
        }
        self.setup_ui(icon)

    def setup_ui(self, icon):
        """初始化界面设置"""
        self.setCheckable(True)
        self.setCursor(QtCore.Qt.PointingHandCursor)
        self.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)

        # 图标设置
        if icon:
            self.setIcon(QtGui.QIcon(icon))
            self.setIconSize(self._default_config['icon_size'])

        # 应用默认样式
        self.update_style()

    def update_style(self, config=None):
        """动态更新按钮样式"""
        style_config = {**self._default_config, **(config or {})}

        base_style = f"""
        QPushButton {{
            font-family: {style_config['font_family']};
            font-size: {style_config['font_size']}px;
            color: {style_config['text_color']};
            padding: {style_config['padding'][0]}px {style_config['padding'][1]}px;
            border-radius: {style_config['border_radius']}px;
            background-color: {style_config['main_color']};
            border: none;
            border-bottom: {style_config['border_width']}px solid transparent;
            margin: 2px;
        }}
        QPushButton:hover {{
            background-color: {style_config['hover_color']};
        }}
        QPushButton:checked {{
            background-color: {style_config['active_color']};
            border-bottom: {style_config['border_width']}px solid {style_config['border_color']};
        }}
        QPushButton::icon {{
            margin-right: 6px;
        }}
        """
        self.setStyleSheet(base_style)

    def set_colors(self, main_color, hover_color, active_color, border_color):
        """快速设置颜色方案"""
        self.update_style({
            'main_color': main_color,
            'hover_color': hover_color,
            'active_color': active_color,
            'border_color': border_color
        })


class CheckButton(QtWidgets.QPushButton):
    def __init__(self,
                 text="Toggle",
                 parent=None,
                 checked_color1=QtGui.QColor(255, 107, 107),
                 checked_color2=QtGui.QColor(255, 142, 83),
                 unchecked_color1=QtGui.QColor(108 * 0.8, 117 * 0.8, 125 * 0.8),
                 unchecked_color2=QtGui.QColor(108, 117, 125),
                 corner_radius=5,
                 animation_duration=200,
                 indicator_size=20,
                 indicator_color=QtCore.Qt.white,
                 indicator_margin=10):
        super().__init__(text, parent)
        self.setCheckable(True)
        self.setCursor(QtCore.Qt.PointingHandCursor)

        # 初始化自定义参数
        self._indicator_size = indicator_size
        self._indicator_color = QtGui.QColor(indicator_color)
        self._indicator_margin = indicator_margin
        self.checked_color1 = checked_color1
        self.checked_color2 = checked_color2
        self.unchecked_color1 = unchecked_color1
        self.unchecked_color2 = unchecked_color2
        self.corner_radius = corner_radius
        self.animation_duration = animation_duration

        # self._init_style()
        self._init_animation()
        self.update_style()

    # 属性访问器
    def getIndicatorSize(self):
        return self._indicator_size

    def setIndicatorSize(self, size):
        self._indicator_size = size
        self.update()

    def getIndicatorColor(self):
        return self._indicator_color

    def setIndicatorColor(self, color):
        if isinstance(color, str):
            self._indicator_color = QtGui.QColor(color)
        else:
            self._indicator_color = QtGui.QColor(color)
        self.update()

    def getIndicatorMargin(self):
        return self._indicator_margin

    def setIndicatorMargin(self, margin):
        self._indicator_margin = margin
        self.update()

    indicatorSize = QtCore.Property(int, getIndicatorSize, setIndicatorSize)
    indicatorColor = QtCore.Property(QtGui.QColor, getIndicatorColor, setIndicatorColor)
    indicatorMargin = QtCore.Property(int, getIndicatorMargin, setIndicatorMargin)

    def _init_style(self):
        # self.setMinimumSize(120, 40)
        # self.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Fixed)
        self.setContentsMargins(20, 10, 20, 10)

    def _init_animation(self):
        # 缩放动画
        self.scale_animation = QtCore.QPropertyAnimation(self, b"geometry")
        self.scale_animation.setDuration(self.animation_duration)
        self.scale_animation.setEasingCurve(QtCore.QEasingCurve.OutBack)

        # 颜色动画
        self.color_animation = QtCore.QPropertyAnimation(self, b"color_progress")
        self.color_animation.setDuration(self.animation_duration)
        self.color_animation.setEasingCurve(QtCore.QEasingCurve.OutQuad)
        self.color_animation.valueChanged.connect(self.update)

        self.toggled.connect(self._handle_toggle)

    def _handle_toggle(self, checked):
        # self._start_scale_animation(checked)
        self._start_color_animation(checked)

    def _start_scale_animation(self, checked):
        original = self.geometry()
        offset = 2 if checked else -2
        self.scale_animation.stop()
        self.scale_animation.setStartValue(original)
        self.scale_animation.setEndValue(original.adjusted(-offset, -offset, offset, offset))
        self.scale_animation.start()

    def _start_color_animation(self, checked):
        self.color_animation.stop()
        self.color_animation.setStartValue(0.0 if checked else 1.0)
        self.color_animation.setEndValue(1.0 if checked else 0.0)
        self.color_animation.start()

    def update_style(self):
        style = f"""
        QPushButton {{
            border: none;
            border-radius: {self.corner_radius}px;
            font-size: 13px;
            font-weight: bold;
            padding: 1px 5px;
        }}
        """
        self.setStyleSheet(style)

    # 颜色过渡属性
    def get_color_progress(self):
        return getattr(self, "_color_progress", 0.0)

    def set_color_progress(self, value):
        self._color_progress = value
        self.update()

    color_progress = QtCore.Property(float, get_color_progress, set_color_progress)

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)

        # 背景渐变
        c1 = self._interpolate_color(self.unchecked_color1, self.checked_color1)
        c2 = self._interpolate_color(self.unchecked_color2, self.checked_color2)

        gradient = QtGui.QLinearGradient(0, 0, self.width(), self.height())
        gradient.setColorAt(0, c1)
        gradient.setColorAt(1, c2)

        painter.setBrush(gradient)
        painter.setPen(QtCore.Qt.NoPen)
        painter.drawRoundedRect(self.rect(), self.corner_radius, self.corner_radius)

        # 边框
        border_width = 1
        border_color = self._interpolate_color(QtGui.QColor(255, 255, 255, 50), QtGui.QColor(255, 255, 255, 100))
        painter.setPen(QtGui.QPen(border_color, border_width))
        painter.drawRoundedRect(self.rect().adjusted(1, 1, -1, -1),
                                self.corner_radius, self.corner_radius)

        # 文字
        painter.setPen(QtCore.Qt.white)
        painter.drawText(self.rect(), QtCore.Qt.AlignCenter, self.text())

        # # 指示器
        # if self.isChecked():
        #     pos_x = self.width() - self._indicator_size/2 - self._indicator_margin
        #     pos_y = (self.height() - self._indicator_size) // 2
        #
        #     # 外圈
        #     painter.setPen(QtGui.QPen(self._indicator_color.darker(120), 1.5))
        #     painter.setBrush(QtGui.QBrush(self._indicator_color))
        #     painter.drawEllipse(pos_x, pos_y,
        #                         self._indicator_size, self._indicator_size)
        #
        #     # 高光
        #     painter.setPen(QtCore.Qt.NoPen)
        #     painter.setBrush(QtGui.QColor(255, 255, 255, 80))
        #     painter.drawEllipse(pos_x + 1, pos_y + 1,
        #                         self._indicator_size - 2, self._indicator_size - 2)

    def _interpolate_color(self, start, end):
        return QtGui.QColor(
            start.red() + (end.red() - start.red()) * self.color_progress,
            start.green() + (end.green() - start.green()) * self.color_progress,
            start.blue() + (end.blue() - start.blue()) * self.color_progress,
            start.alpha() + (end.alpha() - start.alpha()) * self.color_progress
        )


class Combo(QtWidgets.QComboBox):
    def __init__(
            self, name, object_name=None, value=None, datas=None, items=None, disables=None, **kwargs
    ):
        super(Combo, self).__init__()
        self.value = value
        self.setObjectName(object_name or name)

        if datas:
            for item, data in zip(items, datas):
                self.addItem(item, data)
        else:
            self.addItems(items or [])

        self.setCurrentText(value)
        self.currentTextChanged.connect(self.value_change_event)
        self.disables = disables or []
        self.setFocusPolicy(QtCore.Qt.StrongFocus)

    def value_change_event(self, e):
        self.value = e

    def wheelEvent(self, *args, **kwargs):  # pylint: disable=invalid-name
        """Override the wheel event to not the scroll if the widget is not focused"""
        if self.hasFocus():
            super(Combo, self).wheelEvent(*args, **kwargs)


class RadioButton(QtWidgets.QRadioButton, StyleEditor):
    def __init__(
            self, name, object_name=None, value="", disables=None, **kwargs):
        super(RadioButton, self).__init__()
        self.value = value
        self.setObjectName(object_name or name)
        self.setText(name)
        self.disables = disables or []
        self.set_color("orange")
        self.set_font_size(10, True)

    def set_font_size(self, font_size, bold=False):
        if bold:
            self.setFont(QtGui.QFont(FONT, font_size, QtGui.QFont.Bold))
        else:
            self.setFont(QtGui.QFont(FONT, font_size))

    def set_color(self, text_color=None, background_color=None, border_color=None):

        color, background_color, border_color = [
            "rgb({}, {}, {})".format(*var) if isinstance(var, (tuple, list)) else var
            for var in [text_color, background_color, border_color]
        ]

        text_color = text_color or self.text_color
        border_color = border_color or self.border_color

        color_style = f"""
        QRadioButton
        {{
        color: {text_color};
        border-color: {border_color};
        }}"""

        self._append_style(color_style)


class ButtonGroupRadio(QtWidgets.QWidget):
    def __init__(
            self, name, object_name=None, value=None, items=None, disables=None, **kwargs):
        super(ButtonGroupRadio, self).__init__()
        self.value = value
        self.widgets = []
        self.setObjectName(object_name or name)
        self.disables = disables or []
        self.buttons_layout = QtWidgets.QHBoxLayout()
        self.buttons_layout.setSpacing(1)
        self.button_group = QtWidgets.QButtonGroup(self)
        self.setLayout(self.buttons_layout)

        radio_btn = RadioButton(items)
        self.button_group.addButton(radio_btn)
        self.buttons_layout.addWidget(radio_btn)
        self.widgets.append(radio_btn)
        self.button_group.buttons()[0].setChecked(True)

    def set_text(self, texts):
        for btn in self.widgets:
            btn.setText(texts)


class String(QtWidgets.QLineEdit):
    def __init__(
            self, name, object_name=None, value="", placeholder="", disables=None, **kwargs):
        super(String, self).__init__()
        self.value = value
        self.setObjectName(object_name or name)
        self.setText(value)
        self.setPlaceholderText(placeholder)
        self.textEdited.connect(self.value_change_event)
        self.disables = disables or []

    def value_change_event(self, e):
        self.value = e


class Label(QtWidgets.QLabel, StyleEditor):
    def __init__(
            self, name, object_name=None, value="", disables=None, **kwargs):
        super(Label, self).__init__()
        self.value = value
        self.setObjectName(object_name or name)
        self.setText(value)
        self.disables = disables or []
        self.set_color("orange")

    def set_font_size(self, font_size, bold=False):
        if bold:
            self.setFont(QtGui.QFont(FONT, font_size, QtGui.QFont.Bold))
        else:
            self.setFont(QtGui.QFont(FONT, font_size))

    def set_color(self, text_color=None, background_color=None, border_color=None):

        color, background_color, border_color = [
            "rgb({}, {}, {})".format(*var) if isinstance(var, (tuple, list)) else var
            for var in [text_color, background_color, border_color]
        ]

        text_color = text_color or self.text_color
        border_color = border_color or self.border_color

        color_style = f"""
        QLabel
        {{
        color: {text_color};
        border-color: {border_color};
        }}"""

        self._append_style(color_style)


class TagBar(QtWidgets.QWidget, ):
    tag_click = QtCore.Signal(list)

    def __init__(self):
        super(TagBar, self).__init__()

        self.setContentsMargins(0, 0, 0, 0)
        #self.setMinimumHeight(28)
        self.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        self.tags = []
        self.setting = OrderedDict()
        self.h_layout = QtWidgets.QHBoxLayout()
        self.h_layout.setAlignment(QtCore.Qt.AlignVCenter)
        # self.h_layout.setSpacing(6)
        self.h_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.h_layout)

        self.refresh()

    def create_tags(self,
                    last_subproject,
                    last_task,
                    last_task_mode,
                    last_mode, last_category, last_work, last_version):

        new_tags = [f'{last_subproject}/{last_task}']
        if new_tags[0] not in self.tags:
            self.tags.extend(new_tags)
            # self.tags = sorted(set(self.tags), key=lambda x: x.lower())
            self.refresh()
        self.setting[new_tags[0]] = [last_subproject,
                                     last_task,
                                     last_task_mode,
                                     last_mode,
                                     last_category,
                                     last_work,
                                     last_version]

    def refresh(self):
        # 清除旧 widgets
        for i in reversed(range(self.h_layout.count())):
            widget = self.h_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        # 重新添加 tags
        for tag in self.tags:
            self.add_tag_to_bar(tag)

    def add_tag_to_bar(self, text):
        tag_frame = QtWidgets.QFrame()
        tag_frame.setObjectName(text.replace('|', '').replace('/', ''))

        tag_frame.setStyleSheet('''
            QFrame {
                color: #b1b1b1;
                background-color: #404040;
                border-width: 1px;
                border-color: #1e1e1e;
                border-style: solid;
                font-size: 12px;
                border-radius: 4px;
                padding-bottom: 0px;
            }
            QFrame:hover{
                background-color: #505050;
                border: 1px solid #ff8d1c;
            }''')

        tag_frame.setMinimumHeight(28)
        #tag_frame.setSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Fixed)

        hbox = QtWidgets.QHBoxLayout()
        hbox.setContentsMargins(4, 0, 4, 0)
        hbox.setAlignment(QtCore.Qt.AlignVCenter)
        hbox.setSpacing(4)
        tag_frame.setLayout(hbox)

        label_button = QtWidgets.QPushButton(text)
        label_button.setStyleSheet('''
            QPushButton {
                border: none;
                background-color: transparent;
                font-size: 12px;
                padding-top: 0px;
                padding-bottom: 1px;
            }
            QPushButton:hover {
                text-decoration: underline;
                color: #00bbb8;
            }
        ''')
        label_button.setMinimumHeight(28)
        label_button.clicked.connect(partial(self.tag_clicked, text))
        label_button.pressed.connect(lambda: tag_frame.setStyleSheet(
            '''
            QFrame {
            background-color: #ff8d1c;
            border: 1px solid #ff8d1c;
            }'''
        ))

        label_button.released.connect(lambda: tag_frame.setStyleSheet(
            '''
            QFrame {
            background-color: #404040;
            }'''
        ))
        hbox.addWidget(label_button)

        x_button = QtWidgets.QPushButton('×')
        x_button.setMinimumSize(20, 28)
        x_button.setStyleSheet('''
            QPushButton {
                border: none;
                font-weight: bold;
                font-size: 14px;
                color: #b1b1b1;
                padding-top: 0px;
                padding-bottom: 4px;
                background-color: transparent;
            }
            QPushButton:hover {
                color: red;
            }
        ''')
        x_button.setSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum)
        x_button.clicked.connect(partial(self.delete_tag, text))
        hbox.addWidget(x_button)

        self.h_layout.addWidget(tag_frame)

    def delete_tag(self, tag_name):
        self.tags.remove(tag_name)
        self.setting.pop(tag_name, None)
        self.refresh()

    def tag_clicked(self, tag_name):
        # print(self.setting.get(tag_name))
        self.tag_click.emit(self.setting.get(tag_name))
        self.refresh()


class DemoWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        layout = QtWidgets.QVBoxLayout()

        btn1 = CheckButton(
            "Security Mode",
            indicator_size=30,
            indicator_color="#00FF00",
            indicator_margin=10
        )

        btn2 = CheckButton("Dynamic Settings")
        btn2.toggled.connect(lambda s: (
            btn2.setIndicatorSize(10 if s else 6),
            btn2.setIndicatorColor(QtCore.Qt.green if s else QtCore.Qt.red)
        ))

        layout.addWidget(btn1)
        layout.addWidget(btn2)
        self.setLayout(layout)


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    window = DemoWindow()
    window.resize(300, 200)
    window.show()
    sys.exit(app.exec_())
