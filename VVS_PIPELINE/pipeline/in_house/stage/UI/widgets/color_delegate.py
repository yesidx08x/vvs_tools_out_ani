from stage.external.Qt import QtCore, QtGui, QtWidgets

class ColorKeepingDelegate(QtWidgets.QStyledItemDelegate):

    def paint(self, painter, option, index):
        if option.state & QtWidgets.QStyle.State_Selected:
            painter.save()
            painter.setPen(QtCore.Qt.NoPen)
            painter.setBrush(option.palette.highlight())
            painter.drawRect(option.rect)
            painter.restore()
            option.state &= ~QtWidgets.QStyle.State_Selected
        super().paint(painter, option, index)