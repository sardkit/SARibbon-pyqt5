# -*- coding: utf-8 -*-
"""
@Module     SARibbonGallery
@Author     ROOT
"""
import PySARibbon.resource_rc
from typing import List
from PyQt5.QtCore import QSize, pyqtSignal, Qt, QPoint, QModelIndex
from PyQt5.QtGui import QIcon, QResizeEvent
from PyQt5.QtWidgets import QFrame, QActionGroup, QAction, QWidget, QVBoxLayout, QSizePolicy, QApplication

from .SAWidgets.SARibbonGalleryGroup import SARibbonGalleryGroup, SARibbonGalleryGroupModel
from .SAWidgets.SARibbonControlButton import SARibbonControlButton
from .SATools.SARibbonElementManager import RibbonSubElementDelegate

ICON_ARROW_UP = ":/icon/resource/ArrowUp.png"
ICON_ARROW_DOWN = ":/icon/resource/ArrowDown.png"
ICON_ARROW_MORE = ":/icon/resource/ArrowMore.png"


class RibbonGalleryViewport(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.m_layout: QVBoxLayout = QVBoxLayout(self)
        self.m_layout.setSpacing(0)
        self.m_layout.setContentsMargins(1, 1, 1, 1)
        self.setWindowFlags(Qt.Popup)

    def addWidget(self, w: QWidget):
        self.m_layout.addWidget(w)


class SARibbonGallery(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.buttonUp: SARibbonControlButton = SARibbonControlButton(self)
        self.buttonDown: SARibbonControlButton = SARibbonControlButton(self)
        self.buttonMore: SARibbonControlButton = SARibbonControlButton(self)
        self.actionGroup: QActionGroup = QActionGroup(self)
        self.popupWidget: RibbonGalleryViewport = None
        self.viewportGroup: SARibbonGalleryGroup = None

        self.init()
        self.setFrameShape(QFrame.Box)
        self.setFixedHeight(60)
        self.setMinimumWidth(88)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

    def init(self):
        self.buttonUp.setObjectName("SARibbonGalleryButtonUp")
        self.buttonUp.setToolButtonStyle(Qt.ToolButtonIconOnly)
        self.buttonUp.setFixedSize(15, 20)
        self.buttonUp.setIcon(QIcon(ICON_ARROW_UP))
        self.buttonUp.clicked.connect(self.onPageUp)

        self.buttonDown.setObjectName("SARibbonGalleryButtonDown")
        self.buttonDown.setToolButtonStyle(Qt.ToolButtonIconOnly)
        self.buttonDown.setFixedSize(15, 20)
        self.buttonDown.setIcon(QIcon(ICON_ARROW_DOWN))
        self.buttonDown.clicked.connect(self.onPageDown)

        self.buttonMore.setObjectName("SARibbonGalleryButtonMore")
        self.buttonMore.setToolButtonStyle(Qt.ToolButtonIconOnly)
        self.buttonMore.setFixedSize(15, 20)
        self.buttonMore.setIcon(QIcon(ICON_ARROW_MORE))
        self.buttonMore.clicked.connect(self.onShowMoreDetail)

        # self.actionGroup.triggered(self.triggered)
        # self.actionGroup.hovered(self.hovered)

    def createPopupWidget(self):
        if not self.popupWidget:
            self.popupWidget = RibbonGalleryViewport(self)

    def setViewPort(self, group: SARibbonGalleryGroup):
        if not self.viewportGroup:
            self.viewportGroup = RibbonSubElementDelegate.createRibbonGalleryGroup(self)
        self.viewportGroup.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.viewportGroup.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.viewportGroup.setModel(group.model())
        self.viewportGroup.setEnableIconText(group.enableIconText())
        self.viewportGroup.show()

    def addGalleryGroup(self, *_atgs):
        """
        addGalleryGroup() -> SARibbonGalleryGroup
        addGalleryGroup(SARibbonGalleryGroup)
        """
        if len(_atgs) == 0:
            group = RibbonSubElementDelegate.createRibbonGalleryGroup(self)
            self.addGalleryGroup(group)
            return group
        else:
            group: SARibbonGalleryGroup = _atgs[0]
            group.setModel(SARibbonGalleryGroupModel(self))
            if self.viewportGroup is None:
                self.setCurrentViewGroup(group)
            group.clicked.connect(self.onItemClicked)
            viewport = self.ensureGetPopupViewPort()
            viewport.addWidget(group)

    def setCurrentViewGroup(self, group: SARibbonGalleryGroup):
        self.setViewPort(group)
        QApplication.postEvent(self, QResizeEvent(self.size(), self.size()))

    def currentViewGroup(self) -> SARibbonGalleryGroup:
        return self.viewportGroup

    def addCategoryActions(self, title: str, actions: List[QAction]) -> SARibbonGalleryGroup:
        group = RibbonSubElementDelegate.createRibbonGalleryGroup(self)
        model = SARibbonGalleryGroupModel(self)
        group.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        group.setModel(model)
        if title:
            group.setGroupTitle(title)
        for a in actions:
            self.actionGroup.addAction(a)
        group.addActionItemList(actions)
        group.clicked.connect(self.onItemClicked)
        viewport = self.ensureGetPopupViewPort()
        viewport.addWidget(group)
        self.setCurrentViewGroup(group)
        return group

    def getActionGroup(self) -> QActionGroup:
        return self.actionGroup

    def ensureGetPopupViewPort(self) -> RibbonGalleryViewport:
        if self.popupWidget is None:
            self.createPopupWidget()
        return self.popupWidget

    def sizeHint(self) -> QSize:
        return QSize(232, 60)

    def minimumSizeHint(self) -> QSize:
        return QSize(88, 60)

    # 槽函数
    def onPageDown(self):
        if self.viewportGroup:
            vscrollBar = self.viewportGroup.verticalScrollBar()
            v = vscrollBar.value()
            v += vscrollBar.singleStep()
            vscrollBar.setValue(v)

    def onPageUp(self):
        if self.viewportGroup:
            vscrollBar = self.viewportGroup.verticalScrollBar()
            v = vscrollBar.value()
            v -= vscrollBar.singleStep()
            vscrollBar.setValue(v)

    def onShowMoreDetail(self):
        if self.popupWidget:
            return
        popupMenuSize = self.popupWidget.minimumSizeHint()
        start = self.mapToGlobal(QPoint(0, 0))
        self.popupWidget.setGeometry(start.x(), start.y(), self.width(), popupMenuSize.height())
        self.popupWidget.show()

    def onItemClicked(self, index: QModelIndex):
        group = self.sender()
        curGroup = self.currentViewGroup()
        if not curGroup:
            self.setCurrentViewGroup(group)
            curGroup = self.currentViewGroup()
        if curGroup.model() != group.model():
            curGroup.setModel(group.model())
        curGroup.scrollTo(index)
        curGroup.setCurrentIndex(index)
        curGroup.repaint()

    # 事件
    def resizeEvent(self, e):
        r = e.size()
        subW = 0
        self.buttonUp.move(r.width() - self.buttonUp.width(), 0)
        subW = max(subW, self.buttonUp.width())
        self.buttonDown.move(r.width() - self.buttonDown.width(), self.buttonDown.height())
        subW = max(subW, self.buttonDown.width())
        self.buttonMore.move(r.width() - self.buttonMore.width(), self.buttonDown.geometry().bottom())
        subW = max(subW, self.buttonMore.width())
        if self.viewportGroup:
            self.viewportGroup.setGeometry(0, 0, r.width() - subW, r.height())
        super().resizeEvent(e)

    # 信号
    triggered = pyqtSignal(QAction)
    hovered = pyqtSignal(QAction)


if __name__ == '__main__':
    from PyQt5.QtWidgets import QApplication

    app = QApplication([])
    mainWindow = QWidget()

    gallery = SARibbonGallery(mainWindow)
    # gallery.resize(mainWindow.width(), gallery.size().height())
    group = gallery.addGalleryGroup()
    group.addActionItem(QAction(QIcon('resource/icon/folder.png'), 'test'))
    for i in range(10):
        group.addItem('test '+str(i), QIcon('resource/icon/folder.png'))

    mainWindow.setMinimumWidth(500)
    mainWindow.show()
    app.exec()

