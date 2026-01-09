import tempfile
import sys
import os

from stage.external.Qt import QtCore, QtGui, QtWidgets


class ScreenThumbnail(QtWidgets.QDialog):
    SCREEN_GRAB_CALLBACK = None

    def __init__(self, parent=None):

        super(ScreenThumbnail, self).__init__(parent)

        self._opacity = 1
        self._click_pos = None
        self._capture_rect = QtCore.QRect()

        self.setWindowFlags(QtCore.Qt.FramelessWindowHint |
                            QtCore.Qt.WindowStaysOnTopHint |
                            QtCore.Qt.CustomizeWindowHint |
                            QtCore.Qt.Tool)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setCursor(QtCore.Qt.CrossCursor)
        self.setMouseTracking(True)

        # desktop = QtWidgets.QApplication.desktop()
        # desktop.resized.connect(self._fit_screen_geometry)
        # desktop.screenCountChanged.connect(self._fit_screen_geometry)

    @property
    def capture_rect(self):

        return self._capture_rect

    def paintEvent(self, event):

        mouse_pos = self.mapFromGlobal(QtGui.QCursor.pos())
        click_pos = None
        if self._click_pos is not None:
            click_pos = self.mapFromGlobal(self._click_pos)

        painter = QtGui.QPainter(self)

        painter.setBrush(QtGui.QColor(0, 0, 0, self._opacity))
        painter.setPen(QtCore.Qt.NoPen)
        painter.drawRect(event.rect())

        # Clear the capture area
        if click_pos is not None:
            capture_rect = QtCore.QRect(click_pos, mouse_pos)
            painter.setCompositionMode(QtGui.QPainter.CompositionMode_Clear)
            painter.drawRect(capture_rect)
            painter.setCompositionMode(QtGui.QPainter.CompositionMode_SourceOver)

        pen = QtGui.QPen(QtGui.QColor(255, 255, 255, 64), 1, QtCore.Qt.DotLine)
        painter.setPen(pen)

        # Draw cropping markers at click position
        if click_pos is not None:
            painter.drawLine(event.rect().left(), click_pos.y(),
                             event.rect().right(), click_pos.y())
            painter.drawLine(click_pos.x(), event.rect().top(),
                             click_pos.x(), event.rect().bottom())

        # Draw cropping markers at current mouse position
        painter.drawLine(event.rect().left(), mouse_pos.y(),
                         event.rect().right(), mouse_pos.y())
        painter.drawLine(mouse_pos.x(), event.rect().top(),
                         mouse_pos.x(), event.rect().bottom())

    def keyPressEvent(self, event):
        pass

    def mousePressEvent(self, event):

        if event.button() == QtCore.Qt.LeftButton:
            # Begin click drag operation
            self._click_pos = event.globalPos()

    def mouseReleaseEvent(self, event):

        if event.button() == QtCore.Qt.LeftButton and self._click_pos is not None:
            # End click drag operation and commit the current capture rect
            self._capture_rect = QtCore.QRect(self._click_pos,
                                              event.globalPos()).normalized()
            self._click_pos = None
        self.close()

    def mouseMoveEvent(self, event):

        self.repaint()

    @classmethod
    def screen_capture(cls):

        if cls.SCREEN_GRAB_CALLBACK:
            # use an external callback for screen grabbing
            return cls.SCREEN_GRAB_CALLBACK()

        else:

            tool = ScreenThumbnail()
            tool.exec_()
            return get_desktop_pixmap(tool.capture_rect)

    def showEvent(self, event):

        self._fit_screen_geometry()
        # Start fade in animation
        fade_anim = QtCore.QPropertyAnimation(self, b"_opacity_anim_prop", self)
        fade_anim.setStartValue(self._opacity)
        fade_anim.setEndValue(127)
        fade_anim.setDuration(300)
        fade_anim.setEasingCurve(QtCore.QEasingCurve.OutCubic)
        fade_anim.start(QtCore.QAbstractAnimation.DeleteWhenStopped)

    def _set_opacity(self, value):

        self._opacity = value
        self.repaint()

    def _get_opacity(self):

        return self._opacity

    _opacity_anim_prop = QtCore.Property(int, _get_opacity, _set_opacity)

    def _fit_screen_geometry(self):

        screen_rect = QtCore.QRect()
        for screen_index in range(len(QtWidgets.QApplication.screens())):
            screen_rect = screen_rect.united(
                QtWidgets.QApplication.screens()[screen_index].geometry())
        #self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        #self.setCursor(QtCore.Qt.CrossCursor)
        self.setGeometry(screen_rect)


class ExternalCaptureThread(QtCore.QThread):

    def __init__(self, path):
        QtCore.QThread.__init__(self)
        self._path = path
        self._error = None

    @property
    def error_message(self):
        return self._error

    def run(self):
        pass


def _external_screenshot():
    output_path = tempfile.NamedTemporaryFile(suffix=".png",
                                              prefix="screencapture_",
                                              delete=False).name

    pm = None
    try:

        screenshot_thread = ExternalCaptureThread(output_path)
        screenshot_thread.start()
        while not screenshot_thread.isFinished():
            screenshot_thread.wait(100)
            QtWidgets.QApplication.processEvents()

        if screenshot_thread.error_message:

            print(
                "Failed to capture "
                "screenshot: %s" % screenshot_thread.error_message
            )
        else:
            # load into pixmap
            pm = QtGui.QPixmap(output_path)
    finally:
        # remove the temporary file
        if output_path and os.path.exists(output_path):
            os.remove(output_path)

    return pm


def get_desktop_pixmap(rect):
    # desktop = QtWidgets.QApplication.desktop()
    # return QtGui.QPixmap.grabWindow(desktop.winId(), rect.x(), rect.y(),
                                        # rect.width(), rect.height())

    screen = QtWidgets.QApplication.primaryScreen()

    return screen.grabWindow(0, rect.x(), rect.y(),
                                       rect.width(),
                                       rect.height())


screen_capture = ScreenThumbnail.screen_capture


def screen_capture_file(output_path=None):
    if output_path is None:
        output_path = tempfile.NamedTemporaryFile(suffix=".png",
                                                  prefix="screencapture_",
                                                  delete=False).name
    pixmap = screen_capture()
    pixmap.save(output_path)
    return output_path
