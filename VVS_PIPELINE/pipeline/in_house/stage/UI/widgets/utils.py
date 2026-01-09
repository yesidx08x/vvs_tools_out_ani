from stage.external.Qt import QtCore, QtGui, QtWidgets
from stage.UI.widgets import style
from stage.UI.widgets.common import Combo,String,Label,ButtonGroupRadio
class SettingsLayout(QtWidgets.QFormLayout):
    widget_dict = {
        "combo": Combo,
        "String": String,
        "button": QtWidgets.QPushButton,
        "label": Label,
        "buttongroupradio": ButtonGroupRadio,
    }
    def __init__(self, ui_definition, *args, **kwargs):
        super(SettingsLayout, self).__init__()
        self.ui_definition = ui_definition
        self.widgets =self.build_template_widget()

    def build_template_widget(self):
        widgets=[]
        for name, properties in self.ui_definition.items():
            display_name = properties.pop("display_name", name)
            label = QtWidgets.QLabel(text=display_name)
            tooltip = properties.pop("tooltip", "")
            label.setToolTip(tooltip)
            _type = properties.pop("type", None)

            widget_class = self.widget_dict.get(_type)
            if not widget_class:
                continue
            widget = widget_class(name,**properties)
            self.addRow(label, widget)
            widgets.append(widget)
        return widgets

    @staticmethod
    def __find_widget(object_name, widget_list):
        for widget in widget_list:
            if widget.objectName() == object_name:
                return widget
        return None

    def find(self, object_name):
        return self.__find_widget(object_name, self.widgets)


def getColoredIcon(icon_name, r=150, g=210, b=240):

    image = QtGui.QImage(str(style.RC_FOLDER / icon_name))
    cimage = QtGui.QImage(image)
    cimage.fill((QtGui.QColor(r, g, b)))
    cimage.setAlphaChannel(image.convertToFormat(QtGui.QImage.Format_Alpha8))
    pixmap = QtGui.QPixmap.fromImage(cimage)

    return QtGui.QIcon(pixmap)