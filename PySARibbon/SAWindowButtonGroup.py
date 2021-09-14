# -*- coding: utf-8 -*-
"""
@Module     SAWindowButtonGroup
@Author     ROOT

@brief 窗口的最大最小化按钮
"""
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtCore import QEvent
from PyQt5.QtWidgets import QWidget, QToolButton, QStyle


class SAWindowToolButton(QToolButton):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAutoRaise(True)


class SAWindowButtonGroup(QWidget):
    def __init__(self, parent, flags=None):
        super().__init__(parent)
        self.mCloseStretch = 4
        self.mMaxStretch = 3
        self.mMinStretch = 3
        self.mIconscale = 0.5
        self.mFlags = Qt.Widget
        self.buttonClose = None
        self.buttonMinimize = None
        self.buttonMaximize = None

        if flags:
            self.mFlags = flags
        self.updateWindowFlag()
        if parent:
            parent.installEventFilter(self)

    def setupMinimizeButton(self, on: bool):
        if on:
            if self.buttonMinimize:
                self.buttonMinimize.show()
                return
            self.buttonMinimize = SAWindowToolButton(self)
            self.buttonMinimize.setObjectName('SAMinimizeWindowButton')
            self.buttonMinimize.setFixedSize(30, 28)
            self.buttonMinimize.setFocusPolicy(Qt.NoFocus)
            self.buttonMinimize.setStyleSheet("""
                SAWindowToolButton { 
                    background-color: transparent; 
                    border:none;
                }
                SAWindowToolButton:hover {background-color:#C1D1B8;}
                SAWindowToolButton:pressed {background-color:#A5AF9B;}
                SAWindowToolButton:focus{outline: none}
            """)
            icon = self.style().standardIcon(QStyle.SP_TitleBarMinButton)
            w = int(self.buttonMinimize.size().width() * self.mIconscale)
            h = int(self.buttonMinimize.size().height() * self.mIconscale)
            self.buttonMinimize.setIconSize(QSize(w, h))
            self.buttonMinimize.setIcon(icon)
            self.buttonMinimize.show()
            self.buttonMinimize.clicked.connect(self.onMinimizeWindow)
        elif self.buttonMinimize:
            self.buttonMinimize.hide()

        self.updateSize()

    def setupMaximizeButton(self, on: bool):
        if on:
            if self.buttonMaximize:
                self.buttonMaximize.show()
                return
            self.buttonMaximize = SAWindowToolButton(self)
            self.buttonMaximize.setObjectName('SAMaximizeWindowButton')
            self.buttonMaximize.setFixedSize(30, 28)
            self.buttonMaximize.setFocusPolicy(Qt.NoFocus)
            self.buttonMaximize.setStyleSheet("""
                SAWindowToolButton { 
                    background-color: transparent; 
                    border:none;
                }
                SAWindowToolButton:hover {background-color:#C1D1B8;}
                SAWindowToolButton:pressed {background-color:#A5AF9B;}
                SAWindowToolButton:focus{outline: none}
            """)
            icon = self.style().standardIcon(QStyle.SP_TitleBarMaxButton)
            w = int(self.buttonMaximize.size().width() * self.mIconscale)
            h = int(self.buttonMaximize.size().height() * self.mIconscale)
            self.buttonMaximize.setIconSize(QSize(w, h))
            self.buttonMaximize.setIcon(icon)
            self.buttonMaximize.show()
            self.buttonMaximize.clicked.connect(self.onMaximizeWindow)
        elif self.buttonMaximize:
            self.buttonMaximize.hide()

        self.updateSize()

    def setupCloseButton(self, on: bool):
        if on:
            if self.buttonClose:
                self.buttonClose.show()
                return
            self.buttonClose = SAWindowToolButton(self)
            self.buttonClose.setObjectName('SAMaximizeWindowButton')
            self.buttonClose.setFixedSize(40, 28)
            self.buttonClose.setFocusPolicy(Qt.NoFocus)
            self.buttonClose.setStyleSheet("""
               SAWindowToolButton { 
                   background-color: transparent; 
                   border:none;
               }
               SAWindowToolButton:hover {background-color:#F0604D;}
               SAWindowToolButton:pressed {background-color:#F0604D;}
               SAWindowToolButton:focus{outline: none}
            """)
            icon = self.style().standardIcon(QStyle.SP_TitleBarCloseButton)
            w = int(self.buttonClose.size().width() * self.mIconscale)
            h = int(self.buttonClose.size().height() * self.mIconscale)
            self.buttonClose.setIconSize(QSize(w, h))
            self.buttonClose.setIcon(icon)
            self.buttonClose.show()
            self.buttonClose.clicked.connect(self.onCloseWindow)
        elif self.buttonClose:
            self.buttonClose.hide()

        self.updateSize()

    def updateWindowFlag(self, flags=None):
        if flags:
            if flags & Qt.WindowCloseButtonHint:
                self.mFlags |= Qt.WindowCloseButtonHint
            else:
                self.mFlags &= ~Qt.WindowCloseButtonHint
            if flags & Qt.WindowMaximizeButtonHint:
                self.mFlags |= Qt.WindowMaximizeButtonHint
            else:
                self.mFlags &= ~Qt.WindowMaximizeButtonHint
            if flags & Qt.WindowMinimizeButtonHint:
                self.mFlags |= Qt.WindowMinimizeButtonHint
            else:
                self.mFlags &= ~Qt.WindowMinimizeButtonHint
        else:
            flags = self.parentWidget().windowFlags()
            self.mFlags = flags

        self.setupMinimizeButton(flags & Qt.WindowMinimizeButtonHint)
        self.setupMaximizeButton(flags & Qt.WindowMaximizeButtonHint)
        self.setupCloseButton(flags & Qt.WindowCloseButtonHint)

    def setButtonWidthStretch(self, close=4, maxst=3, minst=3):
        """
        设置按钮的宽度比例,最终按钮宽度将按照此比例进行设置
        """
        self.mCloseStretch = close
        self.mMaxStretch = maxst
        self.mMinStretch = minst

    def setIconScale(self, iconscale=0.5):
        """
        设置按钮的缩放比例
        """
        self.mIconscale = iconscale

    def setWindowStates(self, states):
        """
        设置窗口状态（最大最小化按钮状态）
        """
        if states == Qt.WindowNoState:
            if self.buttonMaximize:
                self.buttonMaximize.setIcon(self.style().standardIcon(QStyle.SP_TitleBarMaxButton))
        if states == Qt.WindowMaximized:
            if self.buttonMaximize:
                self.buttonMaximize.setIcon(self.style().standardIcon(QStyle.SP_TitleBarNormalButton))

    def windowButtonFlags(self) -> int:
        """
        仅获取按钮的状态
        """
        f = Qt.Widget   # widget是000
        if self.mFlags & Qt.WindowCloseButtonHint:
            f |= Qt.WindowCloseButtonHint
        if self.mFlags & Qt.WindowMaximizeButtonHint:
            f |= Qt.WindowMaximizeButtonHint
        if self.mFlags & Qt.WindowMinimizeButtonHint:
            f |= Qt.WindowMinimizeButtonHint
        return f

    def parentResize(self):
        par = self.parentWidget()
        if par:
            pSize = par.size()
            self.move(pSize.width()-self.width()-1, 1)

    def updateSize(self):
        self.setFixedSize(self.sizeHint())
        self.resize(self.size())

    def resize(self, size: QSize):
        tw = 0
        if self.buttonClose:
            tw += self.mCloseStretch
        if self.buttonMaximize:
            tw += self.mMaxStretch
        if self.buttonMinimize:
            tw += self.mMinStretch

        x = 0
        if self.buttonMinimize:
            w = (self.mMinStretch / tw) * size.width()
            self.buttonMinimize.setGeometry(x, 0, w, size.height())
            x += w
        if self.buttonMaximize:
            w = (self.mMaxStretch / tw) * size.width()
            self.buttonMaximize.setGeometry(x, 0, w, size.height())
            x += w
        if self.buttonClose:
            w = (self.mCloseStretch / tw) * size.width()
            self.buttonClose.setGeometry(x, 0, w, size.height())

    def sizeHint(self) -> QSize:
        w = 0
        h = 28

        if self.buttonClose:
            w += 40
        if self.buttonMaximize:
            w += 30
        if self.buttonMinimize:
            w += 30
        return QSize(w, h)

    # 事件
    def eventFilter(self, watched, e: QEvent) -> bool:
        """
        用于监听父窗口改变尺寸
        """
        if watched == self.parentWidget():
            if e.type() == QEvent.Resize:
                self.parentResize()
        return False    # 不截断任何事件

    def resizeEvent(self, e):
        self.resize(e.size())

    # 槽函数
    def onCloseWindow(self):
        try:
            if self.parentWidget():
                self.parentWidget().close()
        except Exception as e:
            print(__file__, 'onCloseWindow:', e)

    def onMinimizeWindow(self):
        if self.parentWidget():
            self.parentWidget().showMinimized()

    def onMaximizeWindow(self):
        par = self.parentWidget()
        if par:
            if par.isMaximized():
                par.showNormal()
            else:
                par.showMaximized()


