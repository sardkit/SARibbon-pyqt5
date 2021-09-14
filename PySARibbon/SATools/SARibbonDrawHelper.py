# -*- coding: utf-8 -*-
"""
@Module     SARibbonDrawHelper
@Author     ROOT
"""
from PyQt5.QtCore import Qt, QSize, QRect
from PyQt5.QtGui import QPixmap, QIcon, QPainter
from PyQt5.QtWidgets import QWidget, QStyleOption, QStyle


class SARibbonDrawHelper:
    """
    绘图辅助
    """
    @staticmethod
    def iconToPixmap(icon: QIcon, widget: QWidget, opt: QStyleOption, icoSize: QSize) -> QPixmap:
        mode = QIcon.Normal
        if not (opt.state & QStyle.State_Enabled):
            mode = QIcon.Disabled
        elif (opt.state & QStyle.State_MouseOver) and (opt.state & QStyle.State_AutoRaise):
            mode = QIcon.Active

        state = QIcon.Off
        if (opt.state & QStyle.State_Selected) or (opt.state & QStyle.State_On):
            state = QIcon.On

        return icon.pixmap(widget.window().windowHandle(), icoSize, mode, state)

    @staticmethod
    def drawIcon(icon: QIcon, painter: QPainter, opt: QStyleOption, *_args):
        """
        drawIcon(QIcon, QPainter, QStyleOption, int, int, int, int)
        drawIcon(QIcon, QPainter, QStyleOption, QRect)
        """
        if len(_args) < 1:
            return
        if isinstance(_args[0], int):
            rect = QRect(_args[0], _args[1], _args[2], _args[3])
        else:
            rect = _args[0]

        mode = QIcon.Normal
        if not (opt.state & QStyle.State_Enabled):
            mode = QIcon.Disabled
        elif (opt.state & QStyle.State_MouseOver) and (opt.state & QStyle.State_AutoRaise):
            mode = QIcon.Active

        state = QIcon.Off
        if (opt.state & QStyle.State_Selected) or (opt.state & QStyle.State_On):
            state = QIcon.On

        icon.paint(painter, rect, Qt.AlignCenter, mode, state)

    @staticmethod
    def iconActualSize(icon: QIcon, opt: QStyleOption, icoSize: QSize) -> QSize:
        mode = QIcon.Normal
        if not (opt.state & QStyle.State_Enabled):
            mode = QIcon.Disabled
        elif (opt.state & QStyle.State_MouseOver) and (opt.state & QStyle.State_AutoRaise):
            mode = QIcon.Active

        state = QIcon.Off
        if (opt.state & QStyle.State_Selected) or (opt.state & QStyle.State_On):
            state = QIcon.On

        return icon.actualSize(icoSize, mode, state)

    @staticmethod
    def drawText(text: str, painter: QPainter, opt: QStyleOption, align,  *_args):
        """
        drawText(str, QPainter, QStyleOption, Qt.Alignment, int, int, int, int)
        drawText(str, QPainter, QStyleOption, Qt.Alignment, QRect)
        """
        if len(_args) < 1:
            return
        if isinstance(_args[0], int):
            rect = QRect(_args[0], _args[1], _args[2], _args[3])
        else:
            rect = _args[0]

        painter.drawItemText(rect, align, opt.palette,
                             opt.state & QStyle.State_Enabled, text)
