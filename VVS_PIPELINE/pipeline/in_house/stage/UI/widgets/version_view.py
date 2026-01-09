import logging
import os
import sys
import time
import platform
from pathlib import Path
from datetime import datetime
from stage.external.Qt import  QtWidgets, QtCore, QtGui
from stage.common.utils import format_path_join
from stage.UI.widgets.common import HorizontalSeparator,MessageBox
from stage.UI.widgets import style
try:
    import numpy
except:
    pass

if sys.version[0] == "3":
    pVersion = 3
else:
    pVersion = 2

LOG = logging.getLogger(__name__)


class ScenefileItem(QtWidgets.QWidget):
    signalSelect = QtCore.Signal(object)
    signalReleased = QtCore.Signal(object)
    scenePreviewWidth = 500
    scenePreviewHeight = 281
    videoFormats = [".mp4", ".mov", ".avi", ".m4v"]
    def __init__(self, browser, data):
        super(ScenefileItem, self).__init__()
        #self.core = browser.core
        self.browser = browser
        self.data = data
        self.state = "deselected"
        self.previewSize = [self.scenePreviewWidth, self.scenePreviewHeight]
        self.itemPreviewWidth = 120
        self.itemPreviewHeight = 69
        self.setupUi()
        self.refreshUi()

    def mouseReleaseEvent(self, event):
        super(ScenefileItem, self).mouseReleaseEvent(event)
        self.signalReleased.emit(self)
        event.accept()


    def setupUi(self):
        self.setObjectName("texture")
        self.applyStyle(self.state)
        self.setAttribute(QtCore.Qt.WA_StyledBackground, True)
        self.lo_main = QtWidgets.QHBoxLayout()
        self.setLayout(self.lo_main)
        self.lo_main.setSpacing(15)
        self.lo_main.setContentsMargins(10, 0, 0, 0)

        self.l_preview = QtWidgets.QLabel()
        self.l_preview.setMinimumWidth(self.itemPreviewWidth)
        self.l_preview.setMinimumHeight(self.itemPreviewHeight)
        self.l_preview.setMaximumWidth(self.itemPreviewWidth)
        self.l_preview.setMaximumHeight(self.itemPreviewHeight)
        self.spacer1 = QtWidgets.QSpacerItem(0, 10, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)

        self.l_version = QtWidgets.QLabel()
        # self.l_version.setWordWrap(True)
        font = self.l_version.font()
        font.setBold(True)
        self.l_version.setStyleSheet("font-size: 8pt;")
        self.l_version.setFont(font)

        self.spacer2 = QtWidgets.QSpacerItem(0, 10, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.lo_info = QtWidgets.QVBoxLayout()
        self.lo_info.setSpacing(0)
        self.l_icon = QtWidgets.QLabel()

        self.lo_description = QtWidgets.QVBoxLayout()
        self.l_comment = QtWidgets.QLabel()
        self.l_description = QtWidgets.QLabel()

        self.lo_user = QtWidgets.QVBoxLayout()
        # path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "Scripts", "UserInterfacesPrism", "user.png")
        # icon = self.core.media.getColoredIcon(path)
        icon=style.icon('user')
        self.w_user = QtWidgets.QWidget()
        self.lo_userIcon = QtWidgets.QHBoxLayout(self.w_user)
        self.lo_userIcon.setContentsMargins(0, 0, 0, 0)
        self.l_userIcon = QtWidgets.QLabel()
        self.l_userIcon.setPixmap(icon.pixmap(15, 15))
        self.l_user = QtWidgets.QLabel()
        self.l_user.setAlignment(QtCore.Qt.AlignRight)
        self.lo_userIcon.addStretch()
        self.lo_userIcon.addWidget(self.l_userIcon)
        self.lo_userIcon.addWidget(self.l_user)

        # path = os.path.join(self.core.prismRoot, "Scripts", "UserInterfacesPrism", "date.png")
        # icon = self.core.media.getColoredIcon(path)
        icon = style.icon('date')

        self.w_date = QtWidgets.QWidget()
        self.lo_dateIcon = QtWidgets.QHBoxLayout(self.w_date)
        self.lo_dateIcon.setContentsMargins(0, 0, 0, 0)
        self.l_dateIcon = QtWidgets.QLabel()
        self.l_dateIcon.setPixmap(icon.pixmap(15, 15))
        self.l_date = QtWidgets.QLabel()
        self.l_date.setAlignment(QtCore.Qt.AlignRight)
        self.lo_dateIcon.addStretch()
        self.lo_dateIcon.addWidget(self.l_dateIcon)
        self.lo_dateIcon.addWidget(self.l_date)

        self.spacer3 = QtWidgets.QSpacerItem(0, 10, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.spacer4 = QtWidgets.QSpacerItem(15, 0, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.spacer5 = QtWidgets.QSpacerItem(0, 10, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.spacer6 = QtWidgets.QSpacerItem(0, 10, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.spacer7 = QtWidgets.QSpacerItem(20, 10, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)

        self.lo_info.addItem(self.spacer1)
        self.lo_info.addWidget(self.l_version)
        self.lo_info.addItem(self.spacer2)
        self.lo_info.addWidget(self.l_icon)
        self.lo_info.addStretch()

        self.lo_description.addItem(self.spacer3)
        self.lo_description.addWidget(self.l_comment)
        self.lo_description.addWidget(self.l_description)
        self.lo_description.addStretch()

        self.lo_user.addItem(self.spacer5)
        self.lo_user.addWidget(self.w_user)
        self.lo_user.addStretch()
        self.lo_user.addWidget(self.w_date)
        self.lo_user.addItem(self.spacer6)

        #self.lo_main.addWidget(self.l_preview)

        self.lo_main.addLayout(self.lo_info)
        self.lo_main.addItem(self.spacer7)
        self.lo_main.addLayout(self.lo_description)
        self.lo_main.addStretch(1000)
        self.locationLabels = {}


        self.spacer7 = QtWidgets.QSpacerItem(0, 10, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.spacer8 = QtWidgets.QSpacerItem(0, 20, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.lo_location = QtWidgets.QVBoxLayout()
        self.lo_location.addItem(self.spacer7)



        self.lo_location.addItem(self.spacer8)
        self.lo_main.addLayout(self.lo_location)

        # ***************************

        self.lo_main.addLayout(self.lo_user)
        self.lo_main.addItem(self.spacer4)

        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.rightClicked)
        self.l_preview.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.l_preview.customContextMenuRequested.connect(self.previewRightClicked)


    def refreshUi(self):
        version = self.getVersion()
        descr = self.getDescription()
        comment = self.getComment()
        date = self.getDate()
        user = self.getUser()
        icon = self.getIcon()

        if not comment and not version:
            comment = os.path.basename(self.data.get("filename", ""))

        self.refreshPreview()
        self.l_version.setText(version)
        self.setIcon(icon)
        self.l_comment.setText(comment)
        self.l_description.setText(descr)
        self.l_date.setText(date)
        self.l_user.setText(user)


    def setIcon(self, icon):
        self.l_icon.setToolTip(os.path.basename(self.data["filename"]))
        if isinstance(icon, QtGui.QIcon):
            self.l_icon.setPixmap(icon.pixmap(24, 24))
        else:
            pmap = QtGui.QPixmap(20, 20)
            pmap.fill(QtCore.Qt.transparent)
            painter = QtGui.QPainter(pmap)
            painter.setPen(QtCore.Qt.NoPen)
            painter.setBrush(icon)
            painter.drawEllipse(0, 0, 10, 10)
            painter.setRenderHint(QtGui.QPainter.Antialiasing, True)
            painter.end()
            self.l_icon.setPixmap(pmap)

    def scalePixmap(self, pixmap, width, height, keepRatio=True, fitIntoBounds=True, crop=False, fillBackground=False):
        if not pixmap:
            return pixmap

        if keepRatio:
            if fitIntoBounds:
                mode = QtCore.Qt.KeepAspectRatio
            else:
                mode = QtCore.Qt.KeepAspectRatioByExpanding
        else:
            mode = QtCore.Qt.IgnoreAspectRatio

        try:
            pixmap = pixmap.scaled(
                width, height, mode, transformMode=QtCore.Qt.SmoothTransformation
            )
        except AttributeError:
            pixmap = pixmap.scaled(
                width, height, mode
            )

        if fitIntoBounds:
            if fillBackground:
                new_pixmap = QtGui.QPixmap(width, height)
                if fillBackground is True:
                    new_pixmap.fill(QtCore.Qt.black)
                else:
                    new_pixmap.fill(fillBackground)

                painter = QtGui.QPainter(new_pixmap)
                painter.drawPixmap((width - pixmap.width()) / 2, (height - pixmap.height()) / 2, pixmap)
                painter.end()
                pixmap = new_pixmap
        else:
            if crop:
                rect = QtCore.QRect(int((pixmap.width() - width) / 2), int((pixmap.height() - height) / 2), width, height)
                pixmap = pixmap.copy(rect)

        return pixmap

    def getPixmapFromExrPath(self, path, width=None, height=None, channel=None, allowThumb=True, regenerateThumb=False):
        thumbEnabled = self.getUseThumbnails()
        if allowThumb and thumbEnabled and not regenerateThumb and path:
            thumbPath = self.getThumbnailPath(path)
            if os.path.exists(thumbPath):
                return self.getPixmapFromPath(thumbPath, width=width, height=height)

        oiio = self.getOIIO()
        if not oiio:
            # msg = "OpenImageIO is not available. Unable to read the file."
            # self.core.popup(msg)
            return

        path = str(path)  # for python 2
        imgInput = oiio.ImageInput.open(path)
        if not imgInput:
            LOG.debug("failed to read media file: %s" % path)
            return

        chbegin = 0
        chend = 3
        subimage = 0
        if channel:
            while imgInput.seek_subimage(subimage, 0):
                idx = imgInput.spec().channelindex(channel + ".R")
                if idx == -1:
                    idx = imgInput.spec().channelindex(channel + ".red")
                    if idx == -1:
                        idx = imgInput.spec().channelindex(channel + ".r")
                        if idx == -1:
                            idx = imgInput.spec().channelindex(channel + ".x")
                            if idx == -1 and channel in ["RGB", "RGBA"]:
                                idx = imgInput.spec().channelindex("R")

                if idx == -1:
                    subimage += 1
                else:
                    chbegin = idx
                    chend = chbegin + 3
                    break

        try:
            pixels = imgInput.read_image(subimage=subimage, miplevel=0, chbegin=chbegin, chend=chend)
        except Exception as e:
            LOG.warning("failed to read image: %s - %s" % (path, e))
            return

        if pixels is None:
            LOG.warning("failed to read image (no pixels): %s" % (path))
            return

        rgbImgSrc = oiio.ImageBuf(
            oiio.ImageSpec(imgInput.spec().full_width, imgInput.spec().full_height, 3, oiio.UINT16)
        )
        imgInput.close()

        if "numpy" in globals():
            rgbImgSrc.set_pixels(imgInput.spec().roi, numpy.array(pixels))
        else:
            for h in range(height):
                for w in range(width):
                    color = [pixels[h][w][0], pixels[h][w][1], pixels[h][w][2]]
                    rgbImgSrc.setpixel(w, h, 0, color)

        # slow when many channels are in the exr file
        # imgSrc = oiio.ImageBuf(path)
        # rgbImgSrc = oiio.ImageBuf()
        # oiio.ImageBufAlgo.channels(rgbImgSrc, imgSrc, (0, 1, 2))
        imgWidth = rgbImgSrc.spec().full_width
        imgHeight = rgbImgSrc.spec().full_height
        if not imgWidth or not imgHeight:
            return

        xOffset = 0
        yOffset = 0
        if width and height:
            if (imgWidth / float(imgHeight)) > width / float(height):
                newImgWidth = width
                newImgHeight = width / float(imgWidth) * imgHeight
            else:
                newImgHeight = height
                newImgWidth = height / float(imgHeight) * imgWidth
        else:
            newImgWidth = imgWidth
            newImgHeight = imgHeight

        imgDst = oiio.ImageBuf(
            oiio.ImageSpec(int(newImgWidth), int(newImgHeight), 3, oiio.UINT16)
        )
        oiio.ImageBufAlgo.resample(imgDst, rgbImgSrc)
        sRGBimg = oiio.ImageBuf()
        oiio.ImageBufAlgo.pow(sRGBimg, imgDst, (1.0 / 2.2, 1.0 / 2.2, 1.0 / 2.2))
        bckImg = oiio.ImageBuf(
            oiio.ImageSpec(int(newImgWidth), int(newImgHeight), 3, oiio.UINT16)
        )
        oiio.ImageBufAlgo.fill(bckImg, (0.5, 0.5, 0.5))
        oiio.ImageBufAlgo.paste(bckImg, xOffset, yOffset, 0, 0, sRGBimg)
        qimg = QtGui.QImage(int(newImgWidth), int(newImgHeight), QtGui.QImage.Format_RGB32)
        for i in range(int(newImgWidth)):
            for k in range(int(newImgHeight)):
                rgb = QtGui.qRgb(
                    bckImg.getpixel(i, k)[0] * 255,
                    bckImg.getpixel(i, k)[1] * 255,
                    bckImg.getpixel(i, k)[2] * 255,
                )
                qimg.setPixel(i, k, rgb)

        pixmap = QtGui.QPixmap.fromImage(qimg)
        if thumbEnabled and allowThumb:
            thumbPath = self.getThumbnailPath(path)
            self.savePixmap(pixmap, thumbPath)

        return pixmap

    def popupQuestion(
            self,
            text,
            title=None,
            buttons=None,
            default=None,
            icon=None,
            widget=None,
            parent=None,
            escapeButton=None,
            doExec=True,
    ):
        text = str(text)
        title = str(title or "Prism")
        buttons = buttons or ["Yes", "No"]
        icon = QtWidgets.QMessageBox.Question if icon is None else icon
        parent = parent or getattr(self, "messageParent", None)
        isGuiThread = QtWidgets.QApplication.instance() and QtWidgets.QApplication.instance().thread() == QtCore.QThread.currentThread()

        if "silent" in self.prismArgs or not self.uiAvailable or not isGuiThread:
            LOG.info("%s - %s - %s" % (title, text, default))
            return default

        msg = QtWidgets.QMessageBox(
            icon,
            title,
            text,
            parent=parent,
        )
        for button in buttons:
            if button in ["Close", "Cancel", "Ignore"]:
                role = QtWidgets.QMessageBox.RejectRole
            else:
                role = QtWidgets.QMessageBox.YesRole
            b = msg.addButton(button, role)
            if default == button:
                msg.setDefaultButton(b)

            if escapeButton == button:
                msg.setEscapeButton(b)


        if widget:
            msg.layout().addWidget(widget, 1, 2)

        if doExec:
            msg.exec_()
            button = msg.clickedButton()
            if button:
                result = button.text()
            else:
                result = None

            return result
        else:
            msg.setModal(False)
            return msg

    def getPixmapFromPath(self, path, width=None, height=None, colorAdjust=False):
        if path:
            ext = os.path.splitext(path)[1].lower()
            if ext in self.videoFormats:
                return self.getPixmapFromVideoPath(path)
            elif ext in [".exr", ".dpx", ".hdr"]:
                return self.getPixmapFromExrPath(
                    path, width, height
                )

        pixmap = QtGui.QPixmap(path)
        if pixmap.isNull():
            pixmap = self.getPixmapFromExrPath(
                path, width, height
            )

        if (width or height) and pixmap and not pixmap.isNull():
            pixmap = self.scalePixmap(pixmap, width, height)

        return pixmap

    def getThumbnailPath(self, path):
        thumbPath = os.path.join(os.path.dirname(path), "_thumbs", os.path.basename(os.path.splitext(path)[0]) + ".jpg")
        return thumbPath

    def refreshPreview(self):
        ppixmap = self.getPreviewImage()
        ppixmap = self.scalePixmap(
            ppixmap, self.itemPreviewWidth, self.itemPreviewHeight, fitIntoBounds=False, crop=True
        )
        self.l_preview.setPixmap(ppixmap)

    def getPreviewImage(self):
        if self.data.get("preview", ""):
            pixmap = self.getPixmapFromPath(self.data.get("preview", ""))
        else:
            pixmap = QtGui.QPixmap(300, 169)
            pixmap.fill(QtCore.Qt.black)

        return pixmap


    def getVersion(self):
        version = self.data.get("version", "")
        return version


    def getComment(self):
        comment = self.data.get("comment", "")
        return comment

    def getDescription(self):
        description = self.data.get("description", "")
        return description

    def getDate(self):
        dateStr = self.data.get("date")
        #dateStr = self.core.getFormattedDate(date) if date else ""


        if "size" in self.data:
            size = self.data["size"]
        elif os.path.exists(self.data["filename"]):
            size = float(os.stat(self.data["filename"]).st_size / 1024.0 / 1024.0)
        else:
            size = 0

        dateStr += " - %.2f mb" % size

        return dateStr

    def getUser(self):
        user = self.data.get("username", "")
        if user:
            return user

        user = self.data.get("user", "")
        return user

    def getIcon(self):
        if self.data.get("icon", ""):
            return self.data["icon"]
        else:
            return self.data["color"]

    def applyStyle(self, styleType):
        borderColor = (
            "rgb(17, 200, 171)" if self.state == "selected" else "rgba(17, 200, 171,50)"
        )
        ssheet = (
                """
                QWidget#texture {
                    border: 1px solid %s;
                    border-radius: 2px;
                }
            """
                % borderColor
        )
        if styleType == "deselected":
            pass
        elif styleType == "selected":
            ssheet = """
                QWidget#texture {
                    border: 1px solid rgb(17, 215, 191);
                    background-color: rgba(255, 255, 255, 30);
                    border-radius: 2px;
                }
                QWidget {
                    background-color: rgba(255, 255, 255, 0);
                }

            """
        elif styleType == "hoverSelected":
            ssheet = """
                QWidget#texture {
                    border: 1px solid rgb(17, 215, 191);
                    background-color: rgba(255, 255, 255, 35);
                    border-radius: 2px;
                }
                QWidget {
                    background-color: rgba(255, 255, 255, 0);
                }

            """
        elif styleType == "hover":
            ssheet += """
                QWidget {
                    background-color: rgba(255, 255, 255, 0);
                }
                QWidget#texture {
                    background-color: rgba(255, 255, 255, 20);
                }
            """

        self.setStyleSheet(ssheet)

    def mousePressEvent(self, event):
        self.select()


    def enterEvent(self, event):
        if self.isSelected():
            self.applyStyle("hoverSelected")
        else:
            self.applyStyle("hover")

    def leaveEvent(self, event):
        self.applyStyle(self.state)


    def mouseDoubleClickEvent(self, event):
        self.browser.exeFile(self.data["filename"])


    def select(self):
        wasSelected = self.isSelected()
        self.signalSelect.emit(self)
        if not wasSelected:
            self.state = "selected"
            self.applyStyle(self.state)
            self.setFocus()

    def deselect(self):
        if self.state != "deselected":
            self.state = "deselected"
            self.applyStyle(self.state)


    def isSelected(self):
        return self.state == "selected"

    def rightClicked(self, pos):
        self.browser.openScenefileContextMenu(self.data["filename"])

    def previewRightClicked(self, pos):
        rcmenu = QtWidgets.QMenu(self.browser)

        copAct = QtWidgets.QAction("Capture preview", self.browser)
        copAct.triggered.connect(lambda: self.captureScenePreview(self.data))

        exp = QtWidgets.QAction("Browse preview...", self.browser)
        exp.triggered.connect(self.browseScenePreview)
        rcmenu.addAction(exp)

        rcmenu.addAction(copAct)
        clipAct = QtWidgets.QAction("Paste preview from clipboard", self.browser)
        clipAct.triggered.connect(
            lambda: self.pasteScenePreviewFromClipboard(self.data)
        )
        rcmenu.addAction(clipAct)

        prvAct = QtWidgets.QAction("Set as %spreview" % self.data.get("type", ""), self)
        prvAct.triggered.connect(self.setPreview)
        rcmenu.addAction(prvAct)
        rcmenu.exec_(QtGui.QCursor.pos())


    def setPreview(self):
        pm = self.getPreviewImage()
        self.core.entities.setEntityPreview(self.data, pm)
        self.browser.refreshEntityInfo()


    def browseScenePreview(self):
        formats = "Image File (*.jpg *.png *.exr)"

        imgPath = QtWidgets.QFileDialog.getOpenFileName(
            self, "Select preview-image", self.core.projectPath, formats
        )[0]

        if not imgPath:
            return

        if os.path.splitext(imgPath)[1] == ".exr":
            pmsmall = self.core.media.getPixmapFromExrPath(
                imgPath, width=self.previewSize[0], height=self.previewSize[1]
            )
        else:
            pm = self.core.media.getPixmapFromPath(imgPath)
            if pm.width() == 0:
                warnStr = "Cannot read image: %s" % imgPath
                self.core.popup(warnStr)
                return

            pmsmall = self.core.media.scalePixmap(
                pm, self.previewSize[0], self.previewSize[1], fitIntoBounds=False, crop=True
            )

        self.core.entities.setScenePreview(self.data["filename"], pmsmall)
        self.data.update(self.core.entities.getScenefileData(
            self.data["filename"], preview=True
        ))
        self.refreshPreview()


    def captureScenePreview(self, entity):
        from stage.UI.widgets import ScreenShot
        self.window().setWindowOpacity(0)
        previewImg = ScreenShot.grabScreenArea(self.core)
        self.window().setWindowOpacity(1)
        if previewImg:
            previewImg = self.core.media.scalePixmap(
                previewImg,
                self.previewSize[0],
                self.previewSize[1],
                fitIntoBounds=False, crop=True
            )
            self.core.entities.setScenePreview(self.data["filename"], previewImg)
            self.data.update(self.core.entities.getScenefileData(
                self.data["filename"], preview=True
            ))
            self.refreshPreview()


    def pasteScenePreviewFromClipboard(self, pos):
        pmap = self.core.media.getPixmapFromClipboard()
        if not pmap:
            self.core.popup("No image in clipboard.")
            return

        pmap = self.core.media.scalePixmap(
            pmap, self.previewSize[0], self.previewSize[1], fitIntoBounds=False, crop=True
        )
        self.core.entities.setScenePreview(self.data["filename"], pmap)
        self.data.update(self.core.entities.getScenefileData(
            self.data["filename"], preview=True
        ))
        self.refreshPreview()


class VersionLayout(QtWidgets.QWidget):
    open_file_path = QtCore.Signal(str)
    import_file_path = QtCore.Signal(str)
    def __init__(self, *args, **kwargs):

        super(VersionLayout, self).__init__(*args, **kwargs)

        self.base = None
        self.feedback = MessageBox(self)
        self.create_init_ui()
        self.create_init_data()

    def create_init_ui(self):
        self.verticalLayout = QtWidgets.QVBoxLayout()
        header_lay = QtWidgets.QHBoxLayout()
        header_lay.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.addLayout(header_lay)
        self.label = QtWidgets.QLabel("Versions")
        self.label.setStyleSheet("font-size: 14px; font-weight: bold;")
        header_lay.addWidget(self.label)
        header_lay.addStretch()

        self.verticalLayout.addWidget(HorizontalSeparator(color=(174, 215, 91)))



        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.details_image = QtWidgets.QLabel()
        self.details_image.setObjectName(u"details_image")
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.details_image.sizePolicy().hasHeightForWidth())
        self.details_image.setSizePolicy(sizePolicy)
        self.details_image.setMinimumSize(QtCore.QSize(256, 200))
        self.details_image.setMaximumSize(QtCore.QSize(256, 200))
        self.details_image.setScaledContents(False)
        self.details_image.setAlignment(QtCore.Qt.AlignCenter)

        self.setMinimumSize(QtCore.QSize(256, 200))

        self.horizontalLayout.addWidget(self.details_image)

        #self.verticalLayout.addLayout(self.horizontalLayout)



        self.sa_scenefileItems = QtWidgets.QScrollArea()

        self.sa_scenefileItems.setObjectName(u"sa_scenefileItems")
        self.sa_scenefileItems.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)


        self.w_scenefileItems = QtWidgets.QWidget()
        self.w_scenefileItems.setObjectName("itemview")
        self.lo_scenefileItems = QtWidgets.QVBoxLayout()
        self.lo_scenefileItems.setContentsMargins(1, 0, 1, 0)
        self.w_scenefileItems.setLayout(self.lo_scenefileItems)
        self.sa_scenefileItems.setWidget(self.w_scenefileItems)
        self.sa_scenefileItems.setWidgetResizable(True)


        self.verticalLayout.addWidget(self.sa_scenefileItems)
        self.setLayout(self.verticalLayout)
        self.layout().setContentsMargins(0, 0, 0, 0)


    def create_init_data(self):
        self.sceneItemWidgets = []

    def isStr(self, data):
        if pVersion == 3:
            return isinstance(data, str)
        else:
            return isinstance(data, basestring)

    def getFormattedDate(self, stamp=None, datetimeInst=None):
        if self.isStr(stamp):
            return ""

        if datetimeInst:
            cdate = datetimeInst
        else:
            cdate = datetime.fromtimestamp(stamp)

        cdate = cdate.replace(microsecond=0)
        fmt = "%d.%m.%y,  %H:%M:%S"
        if os.getenv("PRISM_DATE_FORMAT"):
            fmt = os.getenv("PRISM_DATE_FORMAT")

        cdate = cdate.strftime(fmt)
        return cdate


    def refreshScenefileItems(self, sceneData):
        self.clearScenefileItems()
        # if sceneData:
        for data in sorted(sceneData, key=lambda x: x.get("version", ""), reverse=True):
            self.addScenefileItem(data)

        self.w_sceneItemsStretch = QtWidgets.QWidget()
        self.w_sceneItemsStretch.setObjectName('versionSceneItem')
        self.lo_sceneItemsStretch = QtWidgets.QVBoxLayout()
        self.lo_sceneItemsStretch.setContentsMargins(0, 0, 0, 0)
        self.w_sceneItemsStretch.setLayout(self.lo_sceneItemsStretch)
        self.lo_sceneItemsStretch.addStretch()
        self.lo_scenefileItems.addWidget(self.w_sceneItemsStretch)
        self._policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        self._policy.setVerticalStretch(10)
        self.w_sceneItemsStretch.setSizePolicy(self._policy)

    def addScenefileItem(self, data):
        item = ScenefileItem(self, data)
        item.signalSelect.connect(self.itemSelected)
        item.signalReleased.connect(self.itemReleased)
        self.sceneItemWidgets.append(item)
        #print(self.lo_scenefileItems)

        self.lo_scenefileItems.addWidget(item)

    def clearScenefileItems(self):
        self.sceneItemWidgets = []
        for idx in reversed(range(self.lo_scenefileItems.count())):
            item = self.lo_scenefileItems.takeAt(idx)
            if not item:
                continue
            w = item.widget()
            if w:
                w.setVisible(False)
                w.setParent(None)
                w.deleteLater()

    def itemSelected(self, item):
        if not item.isSelected():
            self.deselectItems(ignore=[item])

    def itemReleased(self, item):
        self.deselectItems(ignore=[item])

    def deselectItems(self, ignore=None):
        for item in self.sceneItemWidgets:
            if ignore and item in ignore:
                continue
            item.deselect()

    def openScenefileContextMenu(self, file_path=None):
        right_click_menu = QtWidgets.QMenu(self)

        load_act = right_click_menu.addAction(self.tr("Open"))
        load_act.triggered.connect(lambda: self.on_open(file_path))
        right_click_menu.addSeparator()

        import_act = right_click_menu.addAction(self.tr("Import To the Scene"))
        import_act.triggered.connect(lambda: self.on_import(file_path))
        right_click_menu.addSeparator()

        url=os.path.dirname(file_path)
        openex = QtWidgets.QAction("Open Scene Folder", self)
        openex.triggered.connect(lambda: QtGui.QDesktopServices.openUrl(url))
        right_click_menu.addAction(openex)

        right_click_menu.exec_(QtGui.QCursor.pos())

    def on_open(self,file_path):
        self.open_file_path.emit(file_path)

    def on_import(self,file_path):
        parameter = None
        if hasattr(self.stage_project_setting, "ingests"):
            category = self.work.category
            parameter=self.stage_project_setting.ingests(category)

        self.work.import_version(file_path,parameter=parameter)

    def populate_versions(self, work):
        scene_data=[]
        versions = work.all_versions
        location_path=work.settings_file.absolute()
        for version in versions:
            if not os.path.exists(version[1]):
                continue
            version_data = {}
            version_data['version'] = version[0]
            version_data['type'] = work.parent_task.type
            version_data['locations'] = {'global': version[1]},
            version_data['comment'] = version[2]
            version_data['user'] = ''
            version_data['filename'] = version[1]
            version_data['extension'] = '.' + work.extension
            version_data['preview'] = ''
            version_data['icon'] = style.icon(work.dcc.lower())
            version_data['date'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(os.path.getmtime(version[1])))
            version_data['public'] = False
            scene_data.append(version_data)

        self.refreshScenefileItems(scene_data)


    def set_base(self, work,project_setting):

        if not work:
            self.clearScenefileItems()
            return

        self.work = work
        self.stage_project_setting = project_setting
        self.populate_versions(work)

    def get_selected_version_number(self):

        for item in self.sceneItemWidgets:
            if item.isSelected():
                return item.getVersion()

    def set_version(self,version):

        for item in self.sceneItemWidgets:
            if item.getVersion()==version:
                item.select()
                break

