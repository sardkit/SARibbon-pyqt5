# -*- coding: utf-8 -*-
"""
@Module     SARibbonSeparatorWidget
@Author     ROOT
"""
from PyQt5.QtCore import QSize, QPoint
from PyQt5.QtGui import QPainter
from PyQt5.QtWidgets import QWidget, QSizePolicy


class SARibbonSeparatorWidget(QWidget):
    def __init__(self, *_args):
        """
        __init__(parent=None)
        __init__(int, parent=None)
        """
        parent = None
        h: int = None
        arg_len = len(_args)
        if arg_len > 0 and isinstance(_args[0], int):
            h = _args[0]
            if arg_len > 1:
                parent = _args[1]
        elif arg_len > 0:
            parent = _args[0]
        super().__init__(parent)
        if h is not None:
            self.setFixedSize(6, h)
        else:
            self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
            self.setFixedWidth(6)
        self.m_topMargins = 4
        self.m_bottomMargins = 4

    def sizeHint(self) -> QSize:
        return QSize(6, self.height())

    def setTopBottomMargins(self, top: int, bottom: int):
        """
        设置分割线的上下距离
        """
        self.m_topMargins = top
        self.m_bottomMargins = bottom

    def paintEvent(self, e):
        """自定义分割线"""
        painter = QPainter(self)
        painter.setPen(self.palette().window().color().darker(114))
        x1 = self.rect().center().x()
        painter.drawLine(QPoint(x1, self.rect().top() + self.m_topMargins),
                         QPoint(x1, self.rect().bottom() - self.m_bottomMargins))
