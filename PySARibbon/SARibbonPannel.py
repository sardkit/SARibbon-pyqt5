# -*- coding: utf-8 -*-
"""
@Module     SARibbonPannel
@Author     ROOT

@brief pannel页窗口，pannel是ribbon的面板用于承放控件
ribbon的pannel分为两行模式和三行模式，以office为代表的ribbon为3行模式，以WPS为代表的“紧凑派”就是2行模式，
SARibbon可通过SARibbonBar的 SARibbonBar.RibbonStyle 来指定模式(通过函数 SARibbonBar.setRibbonStyle)

在pannel中，可以通过setExpanding 函数指定pannel水平扩展，如果pannel里面没有能水平扩展的控件，将会留白，
因此，建议在pannel里面有水平扩展的控件如（SARibbonGallery）才指定这个函数

pannel的布局通过 SARibbonPannelLayout 来实现，如果有其他布局，可以通过继承 SARibbonElementCreateDelegate.createRibbonPannel
函数返回带有自己布局的pannel，但你必须继承对应的虚函数
"""
from typing import List, Union

from PyQt5.QtCore import pyqtSignal, Qt, QEvent, QSize
from PyQt5.QtGui import QPainter
from PyQt5.QtWidgets import QApplication, QWidget, QAction, QToolButton, QMenu, QSizePolicy

from .SAWidgets.SARibbonPannelOptionButton import SARibbonPannelOptionButton
from .SAWidgets.SARibbonSeparatorWidget import SARibbonSeparatorWidget
from .SAWidgets.SARibbonToolButton import SARibbonToolButton
from .SAWidgets.SARibbonPannelItem import SARibbonPannelItem
from .SATools.SARibbonElementManager import RibbonSubElementDelegate
from .SARibbonGallery import SARibbonGallery
from .SARibbonPannelLayout import SARibbonPannelLayout


class SARibbonPannel(QWidget):
    def __init__(self, *_args):
        """
        SARibbonPannel(parent=None)
        SARibbonPannel(str, parent=None)
        """
        parent = None
        name = ''
        arg_len = len(_args)
        if arg_len > 0 and isinstance(_args[0], str):
            parent = _args[1] if arg_len >= 2 else None
            name = _args[0]
        elif arg_len > 0:
            parent = _args[0]
        super().__init__(parent)

        self.m_pannelLayoutMode = SARibbonPannel.ThreeRowMode
        self.m_lastRp = SARibbonPannelItem.RPNone
        self.m_optionActionButton: SARibbonPannelOptionButton = None
        self.m_layout: SARibbonPannelLayout = None
        self.m_isCanCustomize = True

        self.createLayout()
        self.setPannelLayoutMode(SARibbonPannel.ThreeRowMode)
        self.setPannelName(name)

    def createLayout(self):
        layout = SARibbonPannelLayout(self)
        layout.setRowCount(self.rowCount())
        layout.setSpacing(2)
        layout.setContentsMargins(2, 2, 2, 2)
        self.setLayout(layout)
        self.m_layout = layout

    def rowCount(self) -> int:
        # SARibbonPannel.TwoRowMode 或 SARibbonPannel.ThreeRowMode
        count = 2 if self.pannelLayoutMode() == SARibbonPannel.TwoRowMode else 3
        return count

    def pannelLayoutMode(self) -> int:
        return self.m_pannelLayoutMode

    def isTwoRow(self) -> bool:
        """判断是否为2行模式"""
        return self.rowCount() == 2

    def lastAddActionButton(self) -> SARibbonToolButton:
        lastWidget = self.m_layout.lastWidget()
        if not isinstance(lastWidget, SARibbonToolButton):
            print(__file__, 'lastAddActionButton', type(lastWidget))
            raise Exception('lastAddActionButton: last Widget is not SARibbonToolButton')
        return lastWidget

    def setActionRowProportion(self, act: QAction, rp):
        lay = self.m_layout
        it = lay.pannelItem(act)
        if it:
            it.rowProportion = rp
            lay.invalidate()

    def addAction(self, *_args) -> Union[SARibbonToolButton, QAction]:
        """
        addAction(QAction, rp: int) -> SARibbonToolButton
        addAction(str, QIcon, popMode: int, rp=SARibbonPannelItem.RPLarge) -> QAction
        """

        if len(_args) >= 3:
            rp = SARibbonPannelItem.RPLarge if len(_args) < 4 else _args[3]
            act = QAction(_args[1], _args[0], self)
            self.m_lastRp = rp
            super().addAction(act)
            btn = self.lastAddActionButton()
            if btn:
                btn.setPopupMode(_args[2])
            return act
        else:   # if len(_args) == 2
            self.m_lastRp = _args[1]
            super().addAction(_args[0])
            return self.lastAddActionButton()

    def addLargeAction(self, act: QAction) -> SARibbonToolButton:
        return self.addAction(act, SARibbonPannelItem.RPLarge)

    def addMediumAction(self, act: QAction) -> SARibbonToolButton:
        return self.addAction(act, SARibbonPannelItem.RPMedium)

    def addSmallAction(self, act: QAction) -> SARibbonToolButton:
        return self.addAction(act, SARibbonPannelItem.RPSmall)

    def addMenu(self, menu: QMenu, rp, popMode=QToolButton.InstantPopup) -> SARibbonToolButton:
        """添加一个普通菜单"""
        act = menu.menuAction()
        self.addAction(act, rp)
        btn = self.lastAddActionButton()
        btn.setPopupMode(popMode)
        return btn

    def addActionMenu(self, action: QAction, menu: QMenu, rp) -> SARibbonToolButton:
        """添加一个ActionMenu"""
        self.addAction(action, rp)
        btn = self.lastAddActionButton()
        btn.setMenu(menu)
        btn.setPopupMode(QToolButton.MenuButtonPopup)
        return btn

    def addLargeActionMenu(self, action: QAction, menu: QMenu) -> SARibbonToolButton:
        return self.addActionMenu(action, menu, SARibbonPannelItem.RPLarge)

    def addLargeMenu(self, menu: QMenu, popMode=QToolButton.InstantPopup) -> SARibbonToolButton:
        return self.addMenu(menu, SARibbonPannelItem.RPLarge, popMode)

    def addSmallMenu(self, menu: QMenu, popMode=QToolButton.InstantPopup) -> SARibbonToolButton:
        return self.addMenu(menu, SARibbonPannelItem.RPSmall, popMode)

    def addWidget(self, w: QWidget, rp):
        """添加Widget窗口"""
        w.setAttribute(Qt.WA_Hover)
        self.m_layout.addWidget(w, rp)
        self.updateGeometry()

    def addSmallWidget(self, w: QWidget):
        return self.addWidget(w, SARibbonPannelItem.RPSmall)

    def addLargeWidget(self, w: QWidget):
        return self.addWidget(w, SARibbonPannelItem.RPLarge)

    def addGallery(self, gallery: SARibbonGallery):
        """SARibbonPannel将拥有SARibbonGallery的管理权"""
        self.addLargeWidget(gallery)
        self.setExpanding()

    def addSeparator(self, top=6, bottom=6):
        """添加分割线"""
        sep = SARibbonSeparatorWidget(self)
        sep.setTopBottomMargins(top, bottom)
        self.m_layout.addWidget(sep)
        self.updateGeometry()

    def actionToRibbonToolButton(self, action: QAction) -> Union[SARibbonToolButton, None]:
        """从pannel中把action对应的button提取出来"""
        lay = self.layout()
        if not lay:
            return None

        index = lay.indexOf(action)
        if index == -1:
            return None
        item = lay.takeAt(index)
        btn = item.widget() if item else None
        return btn

    def addOptionAction(self, action: QAction = None):
        """添加操作action，如果要去除，传入None即可"""
        if action is None and self.m_optionActionButton:
            self.m_optionActionButton = None
            self.m_layout.setOptionAction(True, self.optionActionButtonSize())
            return
        if self.m_optionActionButton is None:
            self.m_optionActionButton = RibbonSubElementDelegate.createRibbonPannelOptionButton(self)
        self.m_optionActionButton.setFixedSize(self.optionActionButtonSize())
        self.m_optionActionButton.setIconSize(self.optionActionButtonSize() - QSize(-2, -2))
        self.m_optionActionButton.connectAction(action)
        self.m_layout.setOptionAction(True, self.optionActionButtonSize())
        self.updateGeometry()
        self.repaint()

    def isHaveOptionAction(self) -> bool:
        """判断是否存在OptionAction"""
        return not (self.m_optionActionButton is None)

    def optionActionButtonSize(self) -> QSize:
        """返回optionActionButton的尺寸"""
        size = QSize(12, 12) if self.isTwoRow() else QSize(16, 16)
        return size

    def ribbonToolButtons(self) -> List[SARibbonToolButton]:
        """获取pannel下面的所有toolbutton"""
        objs = self.children()
        return [obj for obj in objs if isinstance(obj, SARibbonToolButton)]

    def sizeHint(self):
        laySize = self.layout().sizeHint()
        maxWidth = laySize.width() + 2
        if self.pannelLayoutMode() == self.ThreeRowMode:
            # 三行模式
            fm = self.fontMetrics()
            titleSize = fm.size(Qt.TextShowMnemonic, self.windowTitle())
            if self.m_optionActionButton:
                # optionActionButton的宽度需要预留
                titleSize.setWidth(titleSize.width()+self.m_optionActionButton.width()+4)
            maxWidth = max(maxWidth, laySize.height())
        return QSize(maxWidth, laySize.height())

    def minimumSizeHint(self):
        return self.layout().minimumSize()

    def setExpanding(self, isExpanding=True):
        """把pannel设置为扩展模式，此时会撑大水平区域"""
        p = QSizePolicy.Expanding if isExpanding else QSizePolicy.Preferred
        self.setSizePolicy(p, QSizePolicy.Preferred)

    def isExpanding(self) -> bool:
        """判断此pannel是否为（水平）扩展模式"""
        sp = self.sizePolicy()
        return sp.horizontalPolicy() == QSizePolicy.Expanding

    def titleHeight(self) -> int:
        """标题栏高度，仅在三行模式下生效"""
        h = 0 if self.isTwoRow() else 21
        return h

    def actionIndex(self, act: QAction):
        """action对应的布局index，此操作一般用于移动，其他意义不大"""
        return self.m_layout.indexOf(act)

    def moveAction(self, fr: int, to: int):
        """移动action"""
        self.m_layout.move(fr, to)
        self.updateGeometry()

    def isCanCustomize(self) -> bool:
        """判断是否可以自定义"""
        return self.m_isCanCustomize

    def setCanCustomize(self, b: bool):
        """设置是否可以自定义"""
        self.m_isCanCustomize = b

    def pannelName(self) -> str:
        """pannel的标题"""
        return self.windowTitle()

    def setPannelName(self, title: str):
        """设置pannel的标题"""
        if not title:
            return
        self.setWindowTitle(title)
        self.update()   # 注意会触发windowTitleChange信号

    def setPannelLayoutMode(self, mode):
        if self.m_pannelLayoutMode == mode:
            return
        self.m_pannelLayoutMode = mode
        self.resetLayout(mode)
        self.resetLargeToolButtonStyle()

    def resetLayout(self, mode):
        sp = 4 if self.TwoRowMode == mode else 2
        self.layout().setSpacing(sp)
        self.updateGeometry()   # 通知layout进行重新布局

    def resetLargeToolButtonStyle(self):
        """重置大按钮的类型"""
        btns = self.ribbonToolButtons()
        for b in btns:
            if not b or SARibbonToolButton.LargeButton != b.buttonType():
                continue
            if SARibbonPannel.ThreeRowMode == self.pannelLayoutMode():
                if SARibbonToolButton.Normal != b.largeButtonType():
                    b.setLargeButtonType(SARibbonToolButton.Normal)
            else:
                if SARibbonToolButton.Lite != b.largeButtonType():
                    b.setLargeButtonType(SARibbonToolButton.Lite)

    def ribbonPannelItem(self) -> List[SARibbonPannelItem]:
        return self.m_layout.m_items

    @staticmethod
    def maxHightIconSize(size: QSize, h: int) -> QSize:
        if size.height() < h:
            r = h / size.height()
            return QSize(int(size.width() * r), h)
        return size

    # 事件
    def paintEvent(self, e):
        # 绘制小标题
        if SARibbonPannel.ThreeRowMode == self.pannelLayoutMode():
            p = QPainter(self)
            f = self.font()
            p.setFont(f)
            th = self.titleHeight()
            tw = self.width()-self.m_optionActionButton.width()-4 if self.m_optionActionButton else self.width()
            p.drawText(1, self.height() - th, tw, th, Qt.AlignCenter, self.windowTitle())
        super().paintEvent(e)

    def resizeEvent(self, e):
        # 首先，移动操作按钮到角落
        if self.m_optionActionButton:
            if SARibbonPannel.ThreeRowMode == self.pannelLayoutMode():
                self.m_optionActionButton.move(
                    self.width() - self.m_optionActionButton.width() - 2,
                    self.height() - int((self.titleHeight() + self.m_optionActionButton.height()) / 2)
                )
            else:
                self.m_optionActionButton.move(
                    self.width() - self.m_optionActionButton.width(),
                    self.height() - self.m_optionActionButton.height()
                )
        # 由于分割线在布局中，只要分割线足够高就可以，不需要重新设置
        return super().resizeEvent(e)

    def actionEvent(self, e):
        """
        处理action的事件
        这里处理了ActionAdded，ActionChanged，ActionRemoved三个事件
        """
        action: QAction = e.action()
        if e.type() == QEvent.ActionAdded:
            if action and action.parent() != self:
                action.setParent(self)
            # if e.before():  # 说明是插入
            #     index = lay.indexOf(action)
            self.m_layout.addAction(action, self.m_lastRp)
            self.m_lastRp = SARibbonPannelItem.RPNone   # 插入完后重置为None
            # 由于pannel的尺寸发生变化，需要让category也调整
            if self.parentWidget():
                QApplication.postEvent(self.parentWidget(), QEvent(QEvent.LayoutRequest))
        elif e.type() == QEvent.ActionChanged:
            # 让布局重新绘制
            self.layout().invalidate()
            # 由于pannel的尺寸发生变化，需要让category也调整
            if self.parentWidget():
                QApplication.postEvent(self.parentWidget(), QEvent(QEvent.LayoutRequest))
        elif e.type() == QEvent.ActionRemoved:
            action.disconnect(self)
            index = self.m_layout.indexOf(action)
            if index != -1:
                self.m_layout.takeAt(index)
            # 由于pannel的尺寸发生变化，需要让category也调整
            if self.parentWidget():
                QApplication.postEvent(self.parentWidget(), QEvent(QEvent.LayoutRequest))

    # 信号
    actionTriggered = pyqtSignal(QAction)

    # PannelLayoutMode
    ThreeRowMode = SARibbonPannelLayout.ThreeRowMode
    TwoRowMode = SARibbonPannelLayout.TwoRowMode


if __name__ == '__main__':
    from PyQt5.QtGui import QIcon

    app = QApplication([])
    # mainWindow = QWidget()
    pannel = SARibbonPannel('Pannel One', None)
    mainWindow = pannel

    act = QAction(QIcon("resource/icon/figureIcon.png"), 'test1', pannel)
    pannel.addLargeAction(act)

    act = QAction(QIcon("resource/icon/figureIcon.png"), 'test1', pannel)
    pannel.addSmallAction(act)
    act = QAction(QIcon("resource/icon/figureIcon.png"), 'test1', pannel)
    pannel.addSmallAction(act)
    act = QAction(QIcon("resource/icon/figureIcon.png"), 'test1', pannel)
    pannel.addSmallAction(act)

    pannel.addSeparator()

    gallery = SARibbonGallery(pannel)
    group = gallery.addGalleryGroup()
    group.addActionItem(QAction(QIcon('resource/icon/folder.png'), 'test'))
    for i in range(10):
        group.addItem('test ' + str(i), QIcon('resource/icon/folder.png'))

    pannel.addGallery(gallery)
    # pannel.addLargeWidget(gallery)

    mainWindow.setMinimumWidth(500)
    mainWindow.show()
    app.exec()
