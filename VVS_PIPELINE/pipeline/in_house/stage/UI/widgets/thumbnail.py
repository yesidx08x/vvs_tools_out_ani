from stage.external.Qt import QtCore, QtGui, QtWidgets
from stage.UI.widgets.screen_thumbnail import screen_thumbnail
import tempfile
import re



class Thumbnail(QtWidgets.QLabel):
    screen_thumbnailed = QtCore.Signal(object)

    _do_screengrab = QtCore.Signal()

    def __init__(self, parent=None):

        QtWidgets.QLabel.__init__(self, parent)

        self._multiple_values = False

        self._thumbnail = None
        self._enabled = True
        self.setMinimumSize(QtCore.QSize(160, 90))
        self.setMaximumSize(QtCore.QSize(160, 90))
        self.setAutoFillBackground(True)
        self.setCursor(QtCore.Qt.PointingHandCursor)
        self._no_thumb_pixmap = QtGui.QPixmap(":/resources/camera.png")
        self.set_thumbnail(self._no_thumb_pixmap)
        self.setAcceptDrops(True)
        #self.setStyleSheet("QLabel {border: 1px solid rgb(48, 167, 227);}")
        self._do_screengrab.connect(self._on_screengrab)

    def setEnabled(self, enabled):

        self._enabled = enabled
        if enabled:
            self.setCursor(QtCore.Qt.PointingHandCursor)
        else:
            self.unsetCursor()

    def set_thumbnail(self, pixmap):

        if pixmap is None:
            self._set_screenshot_pixmap(self._no_thumb_pixmap)
        else:

            self._set_screenshot_pixmap(pixmap)

    def mousePressEvent(self, event):

        QtWidgets.QLabel.mousePressEvent(self, event)

        if self._enabled:
            self.setStyleSheet("QLabel {border: 1px solid #eee;}")


    def mouseReleaseEvent(self, event):

        QtWidgets.QLabel.mouseReleaseEvent(self, event)

        if self._enabled:

            self.setStyleSheet(None)

            pos_mouse = event.pos()
            if self.rect().contains(pos_mouse):
                self._do_screengrab.emit()

    def _on_screengrab(self):
        self.window().hide()
        try:

            pixmap = screen_thumbnail.screen_capture()
            #pixmap = screen_thumbnail.screen_capture_file()

            self.pixmap=pixmap

        finally:
            self.window().show()

        if pixmap:
            print(
                "screenshot %sx%s" % (pixmap.width(), pixmap.height())
            )
            if pixmap.width()<5:
                self.pixmap = None
                return
            self._multiple_values = False
            self._set_screenshot_pixmap(pixmap)
            self.screen_thumbnailed.emit(pixmap)
            self.pixmap = pixmap

        else:
            self.pixmap=None

    def _set_multiple_values_indicator(self, is_multiple_values):

        self._multiple_values = is_multiple_values

    def paintEvent(self, paint_event):

        if self._multiple_values == True:
            p = QtWidgets.QPainter(self)
            p.drawPixmap(0, 0, self.width(), self.height(), self._no_thumb_pixmap, 0, 0, self._no_thumb_pixmap.width(),
                         self._no_thumb_pixmap.height())
            p.fillRect(0, 0, self.width(), self.height(), QtWidgets.QColor(42, 42, 42, 237))
            p.setFont(QtWidgets.QFont("Arial", 15, QtWidgets.QFont.Bold))
            pen = QtWidgets.QPen(QtWidgets.QColor("#18A7E3"))
            p.setPen(pen)
            p.drawText(self.rect(), QtCore.Qt.AlignCenter, "Multiple Values")

        else:
            QtWidgets.QLabel.paintEvent(self, paint_event)

    def _set_screenshot_pixmap(self, pixmap):

        self._thumbnail = pixmap
        thumb = self._thumbnail.scaled(
            self.width(),
            self.height(),
            QtCore.Qt.KeepAspectRatio,
            QtCore.Qt.SmoothTransformation
        )

        self.setPixmap(thumb)


    def get_screenshot_file(self,output_path=None):
        if output_path is None:
            output_path = tempfile.NamedTemporaryFile(suffix=".jpg",
                                                      prefix="screencapture_",
                                                      delete=False).name
        if  hasattr(self.pixmap, 'save'):
            self.pixmap.save(output_path)
        else:
            return None

        return output_path

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        file_list = []
        if event.mimeData().hasUrls():
            row = 0
            for url in event.mimeData().urls():
                file_name = url.toLocalFile()
                file_list.append(url.toLocalFile())
                # file_list.append(str(url))

            event.acceptProposedAction()
        else:
            event.ignore()

        for f in file_list:
            if re.findall('.jpg', f, re.IGNORECASE) or re.findall('.png', f, re.IGNORECASE):
                self.set_thumb(f)
                break

    def set_thumb(self,file):
        pixmap = QtGui.QPixmap(file)
        self._set_screenshot_pixmap(pixmap)
        self.screen_thumbnailed.emit(pixmap)
        self.pixmap = pixmap