# -*- coding: utf-8 -*-
"""
@Module     SARibbonCtrlContainer
@Author     ROOT
"""
from typing import Union
from PyQt5.QtCore import Qt, QSize, QRect
from PyQt5.QtWidgets import QWidget, QStyleOption, QSizePolicy, QStylePainter

from ..SATools.SARibbonDrawHelper import SARibbonDrawHelper


class SARibbonCtrlContainer(QWidget):
    def __init__(self, container: Union[QWidget, None], parent):
        super().__init__(parent)
        self.containerWidget: QWidget = container
        self.enableDrawIcon = False
        self.enableDrawTitle = False

        if self.containerWidget:
            self.containerWidget.setParent(self)
        self.setSizePolicy(QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed))

    def sizeHint(self) -> QSize:
        if not self.containerWidget:
            return super().sizeHint()
        sizeHint = self.containerWidget.sizeHint()
        if self.enableDrawIcon:
            icon = self.windowIcon()
            if not icon.isNull():
                sizeHint.setWidth(sizeHint.width() + sizeHint.height())
        if self.enableDrawTitle:
            text = self.windowTitle()
            if text:
                textWidth = self.fontMetrics().horizontalAdvance(text)
                sizeHint.setWidth(sizeHint.width() + textWidth)
        return sizeHint

    def minimumSizeHint(self) -> QSize:
        if not self.containerWidget:
            return super().minimumSizeHint()
        sizeHint = self.containerWidget.minimumSizeHint()
        if self.enableDrawIcon:
            icon = self.windowIcon()
            if not icon.isNull():
                sizeHint.setWidth(sizeHint.width() + sizeHint.height())
        if self.enableDrawTitle:
            text = self.windowTitle()
            if text:
                textWidth = self.fontMetrics().horizontalAdvance(text[0])
                sizeHint.setWidth(sizeHint.width() + textWidth * 2)
        return sizeHint

    def containerWidget(self) -> QWidget:
        return self.containerWidget

    def setEnableShowIcon(self, b: bool):
        self.enableDrawIcon = b
        self.update()

    def setEnableShowTitle(self, b: bool):
        self.enableDrawTitle = b
        self.update()

    def setContainerWidget(self, container: QWidget):
        if self.containerWidget:
            self.containerWidget.hide()
            self.containerWidget.deleteLater()
        if not container:
            return
        self.containerWidget = container
        self.containerWidget.setParent(self)

    def paintEvent(self, w):
        painter = QStylePainter(self)
        opt = QStyleOption()
        self.initStyleOption(opt)
        widgetHeight = self.height()
        x = 0
        # 绘制图标
        if self.enableDrawIcon:
            icon = self.windowIcon()
            if not icon.isNull():
                iconSize = SARibbonDrawHelper.iconActualSize(icon, opt, QSize(widgetHeight, widgetHeight))
                SARibbonDrawHelper.drawIcon(icon, painter, opt, x, 0, widgetHeight, widgetHeight)
                x += iconSize.width() + 4
        # 绘制文字
        if self.enableDrawTitle:
            text = self.windowTitle()
            if text:
                textWidth = self.fontMetrics().horizontalAdvance(text)
                if textWidth > opt.rect.width() - widgetHeight - x:
                    textWidth = opt.rect.width() - widgetHeight - x
                    text = opt.fontMetrics.elidedText(text, Qt.ElideRight, textWidth)
                if textWidth > 0:
                    SARibbonDrawHelper.drawText(
                        text, painter, opt,
                        Qt.AlignLeft | Qt.AlignVCenter,
                        QRect(x, 0, textWidth, opt.rect.height())
                    )

    def resizeEvent(self, e):
        opt = QStyleOption()
        self.initStyleOption(opt)
        widgetHeight = self.height()
        x = 0
        # 绘制图标
        if self.enableDrawIcon:
            icon = self.windowIcon()
            if not icon.isNull():
                iconSize = SARibbonDrawHelper.iconActualSize(icon, opt, QSize(widgetHeight, widgetHeight))
                x += iconSize.width() + 4
        # 绘制文字
        if self.enableDrawTitle:
            text = self.windowTitle()
            if text:
                textWidth = self.fontMetrics().horizontalAdvance(text)
                if textWidth > opt.rect.width() - widgetHeight - x:
                    textWidth = opt.rect.width() - widgetHeight - x
                    # text = opt.fontMetrics.elidedText(text, Qt.ElideRight, textWidth)
                if textWidth > 0:
                    x += textWidth + 2

        if self.containerWidget:
            self.containerWidget.setGeometry(x, 0, self.width() - x, self.height())

    def initStyleOption(self, opt: QStyleOption):
        opt.initFrom(self)
