# -*- coding: utf-8 -*-
"""
@Module     SARibbonStackedWidget
@Author     ROOT

@brief 有qdialog功能的stackwidget，用于在最小化时stack能像dialog那样弹出来
"""
from PyQt5.QtCore import pyqtSignal, QEventLoop, Qt
from PyQt5.QtWidgets import QStackedWidget, QFrame


class SARibbonStackedWidget(QStackedWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.eventLoop: QEventLoop = None
        self.isAutoResize = True

    def setPopupMode(self):
        self.setMouseTracking(True)
        self.setWindowFlags(Qt.Popup | Qt.FramelessWindowHint)
        self.setFrameShape(QFrame.Panel)

    def isPopupMode(self) -> bool:
        return self.windowFlags() & Qt.Popup

    def setNormalMode(self):
        if self.eventLoop:
            self.eventLoop.exit()
            self.eventLoop = None
        self.setMouseTracking(False)
        self.setWindowFlags(Qt.Widget | Qt.FramelessWindowHint)
        self.setFrameShape(QFrame.NoFrame)

    def isNormalMode(self) -> bool:
        return not self.isPopupMode()

    def exec(self):
        self.show()
        if not self.isPopupMode():
            self.eventLoop = None
            return
        event = QEventLoop()
        self.eventLoop = event
        event.exec()
        self.eventLoop = None

    def setAutoResize(self, autoresize: bool):
        self.isAutoResize = autoresize

    def isAutoResize(self) -> bool:
        return self.isAutoResize

    def moveWidget(self, fr: int, to: int):
        """
        类似tabbar的moveTab函数，交换两个窗口的index
        此操作会触发widgetRemoved(int index)信号
        """
        w = self.widget(fr)
        self.removeWidget(w)
        self.insertWidget(to, w)

    def hideEvent(self, e):
        if self.isPopupMode() and self.eventLoop:
            self.eventLoop.exit()
        self.setFocus()
        self.hidWindow.emit()
        super().hideEvent(e)

    def resizeEvent(self, e):
        if self.isAutoResize:
            for i in range(self.count()):
                w = self.widget(i)
                if w:
                    w.resize(e.size())
        return super().resizeEvent(e)

    # 信号
    hidWindow = pyqtSignal()
