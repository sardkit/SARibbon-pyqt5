# -*- coding: utf-8 -*-
"""
@Module     SARibbonMainWindow
@Author     ROOT

@brief 如果要使用SARibbonBar，必须使用此类代替QMainWindow

由于ribbon的风格和传统的Toolbar风格差异较大，
SARibbonBar使用需要把原有的QMainWindow替换为SARibbonMainWindow,
SARibbonMainWindow是个无边框窗体，继承自QMainWindow，其构造函数的参数useRibbon
用于指定是否使用ribbon风格，默认为true

如果想换回非ribbon风格，只需要把useRibbon设置为false即可,
成员函数isUseRibbon用于判断当前是否为ribbon模式，这个函数在兼容传统Toolbar风格和ribbon风格时非常有用。

@ref SARibbonMainWindow 提供了几种常用的ribbon样式，样式可见@ref RibbonTheme
通过@ref setRibbonTheme 可改变ribbon的样式，用户也可通过qss自己定义自己的样式
"""
from PyQt5.QtCore import QFile, QIODevice
from PyQt5.QtCore import QObject, QEvent
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QMenuBar

from .SAFramelessHelper import SAFramelessHelper
from .SAWindowButtonGroup import SAWindowButtonGroup
from .SARibbonBar import SARibbonBar


class SARibbonMainWindow(QMainWindow):
    def __init__(self, parent=None, useRibbon=True):
        super().__init__(parent)
        self.m_useRibbon = useRibbon
        self.m_currentRibbonTheme = SARibbonMainWindow.Office2013
        self.m_ribbonBar: SARibbonBar = None
        self.m_windowButtonGroup: SAWindowButtonGroup = None
        self.m_framelessHelper: SAFramelessHelper = None

        if self.m_useRibbon:
            self.setRibbonTheme(self.ribbonTheme())
            self.setMenuWidget(SARibbonBar(self))

    def ribbonBar(self) -> SARibbonBar:
        """
        返回SARibbonBar，如果useRibbon为false，会返回None
        """
        return self.m_ribbonBar

    def setRibbonTheme(self, theme):
        if theme == SARibbonMainWindow.NormalTheme:
            self.loadTheme(':/theme/resource/default.qss')
        elif theme == SARibbonMainWindow.Office2013:
            self.loadTheme(':/theme/resource/office2013.qss')
        else:
            self.loadTheme(':/theme/resource/default.qss')

    def ribbonTheme(self) -> int:
        return self.m_currentRibbonTheme

    def isUseRibbon(self) -> bool:
        """
        判断当前是否使用ribbon模式
        """
        return self.m_useRibbon

    def updateWindowFlag(self, flags):
        """
        此函数仅用于控制最小最大化和关闭按钮的显示
        """
        if self.isUseRibbon():
            self.m_windowButtonGroup.updateWindowFlag(flags)
        self.repaint()

    def windowButtonFlags(self) -> int:
        """
        获取系统按钮的状态
        """
        if self.isUseRibbon():
            return self.m_windowButtonGroup.windowButtonFlags()
        return self.windowFlags()

    def loadTheme(self, filepath: str):
        """加载主题"""
        qFile = QFile(filepath)
        if not qFile.open(QIODevice.ReadOnly | QIODevice.Text):
            return
        style_str = str(qFile.readAll(), encoding='utf-8')
        self.setStyleSheet(style_str)

    def setMenuWidget(self, ribbonBar: QWidget):
        """
        覆写setMenuWidget
        """
        if ribbonBar:
            self.m_ribbonBar: SARibbonBar = ribbonBar
            self.m_ribbonBar.installEventFilter(self)

            if self.m_framelessHelper is None:
                self.m_framelessHelper = SAFramelessHelper(self)
            # 设置窗体的标题栏高度
            self.m_framelessHelper.setTitleHeight(ribbonBar.titleBarHeight())

            # 设置window按钮
            if self.m_windowButtonGroup is None:
                self.m_windowButtonGroup = SAWindowButtonGroup(self)
            s = self.m_windowButtonGroup.size()
            s.setHeight(ribbonBar.titleBarHeight())
            self.m_windowButtonGroup.setFixedSize(s)
            self.m_windowButtonGroup.setWindowStates(self.windowState())
            self.m_useRibbon = True

        super().setMenuWidget(ribbonBar)

    def setMenuBar(self, ribbonBar: QMenuBar):
        """
        覆写setMenuBar
        """
        if ribbonBar:
            self.m_ribbonBar = ribbonBar
            self.m_ribbonBar.installEventFilter(self)
            # 设置窗体的标题栏高度
            if self.m_framelessHelper is None:
                self.m_framelessHelper = SAFramelessHelper(self)
            self.m_framelessHelper.setTitleHeight(self.m_ribbonBar.titleBarHeight())

            # 设置window按钮
            if self.m_windowButtonGroup is None:
                self.m_windowButtonGroup = SAWindowButtonGroup(self)
            s = self.m_windowButtonGroup.size()
            s.setHeight(self.m_ribbonBar.titleBarHeight())
            self.m_windowButtonGroup.setFixedSize(s)
            self.m_windowButtonGroup.setWindowStates(self.windowState())
            self.m_useRibbon = True

        super().setMenuBar(ribbonBar)

    def eventFilter(self, obj: QObject, e: QEvent) -> bool:
        """
        过滤是为了把ribbonBar上的动作传递到mainwindow，再传递到frameless
        由于ribbonbar会遮挡frameless的区域，导致frameless无法捕获这些消息
        """
        if obj == self.m_ribbonBar:
            e_list = [
                QEvent.MouseButtonPress,
                QEvent.MouseButtonRelease,
                QEvent.MouseMove,
                QEvent.Leave,
                QEvent.HoverMove,
                QEvent.MouseButtonDblClick
            ]
            if e.type() in e_list:
                QApplication.sendEvent(self, e)
        return super().eventFilter(obj, e)

    # 事件
    def event(self, e: QEvent):
        if e and e.type() == QEvent.WindowStateChange:
            if self.isUseRibbon():
                self.m_windowButtonGroup.setWindowStates(self.windowState())
        return super().event(e)

    def resizeEvent(self, e):
        if self.m_ribbonBar:
            if self.m_ribbonBar.size().width() != self.size().width():
                self.m_ribbonBar.setFixedWidth(self.size().width())
            if self.m_windowButtonGroup:
                self.m_ribbonBar.setWindowButtonSize(self.m_windowButtonGroup.size())
        super().resizeEvent(e)

    NormalTheme = 0  # 普通主题
    Office2013 = 1  # office2013主题
