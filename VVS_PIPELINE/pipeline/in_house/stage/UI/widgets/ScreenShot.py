# -*- coding: utf-8 -*-


import sys

from stage.external.Qt.QtCore import *
from stage.external.Qt.QtGui import *
from stage.external.Qt.QtWidgets import *



class ScreenShot(QDialog):
    def __init__(self, core):
        super(ScreenShot, self).__init__()
        self.core = core

        self.imgmap = None
        self.origin = None

        uRect = QRect()
        for i in range(len(QApplication.screens())):
            uRect = uRect.united(QApplication.screens()[i].geometry())

        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setCursor(Qt.CrossCursor)
        self.setGeometry(uRect)

        self.setWindowFlags(
            Qt.FramelessWindowHint  # hides the window controls
            | Qt.WindowStaysOnTopHint  # forces window to top... maybe
            | Qt.SplashScreen  # this one hides it from the task bar!
        )

        self.rubberband = QRubberBand(QRubberBand.Rectangle, self)
        self.rubberband.setWindowOpacity(0)

        self.setMouseTracking(True)

    def mousePressEvent(self, event):
        self.origin = event.pos()
        self.rubberband.setGeometry(QRect(self.origin, QSize()))
        QWidget.mousePressEvent(self, event)

    def mouseMoveEvent(self, event):
        if self.origin is not None:
            rect = QRect(self.origin, event.pos()).normalized()
            self.rubberband.setGeometry(rect)

        self.repaint()
        QWidget.mouseMoveEvent(self, event)

    def paintEvent(self, event):
        painter = QPainter(self)

        painter.setBrush(QColor(0, 0, 0, 100))
        painter.setPen(Qt.NoPen)
        painter.drawRect(event.rect())

        if self.origin is not None:
            rect = QRect(self.origin, self.mapFromGlobal(QCursor.pos()))
            painter.setCompositionMode(QPainter.CompositionMode_Clear)
            painter.drawRect(rect)
            painter.setCompositionMode(QPainter.CompositionMode_SourceOver)

            pen = QPen(QColor(200, 150, 0, 255), 1)
            painter.setPen(pen)
            painter.drawLine(rect.left(), rect.top(), rect.right(), rect.top())
            painter.drawLine(rect.left(), rect.top(), rect.left(), rect.bottom())
            painter.drawLine(rect.right(), rect.top(), rect.right(), rect.bottom())
            painter.drawLine(rect.left(), rect.bottom(), rect.right(), rect.bottom())

        QWidget.paintEvent(self, event)

    def mouseReleaseEvent(self, event):
        if self.origin is not None:
            self.rubberband.hide()
            self.hide()
            rect = self.rubberband.geometry()
            if hasattr(QApplication, "primaryScreen"):
                screen = QApplication.primaryScreen()
            else:
                screen = QPixmap

            pos = self.mapToGlobal(rect.topLeft())
            self.imgmap = screen.grabWindow(
                0, pos.x(), pos.y(), rect.width(), rect.height()
            )
            self.close()

        QWidget.mouseReleaseEvent(self, event)


def grabScreenArea(core):
    ss = ScreenShot(core)
    ss.exec_()
    return ss.imgmap
