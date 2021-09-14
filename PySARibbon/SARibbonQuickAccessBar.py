# -*- coding: utf-8 -*-
"""
@Module     SARibbonQuickAccessBar
@Author     ROOT

@brief ribbon左上顶部的快速响应栏（WPS风格在右上角）
"""
from PyQt5.QtWidgets import QAction, QWidget, QToolButton, QMenu, QStyleOption

from .SARibbonButtonGroupWidget import SARibbonButtonGroupWidget
from .SAWidgets.SARibbonCtrlContainer import SARibbonCtrlContainer


class SARibbonQuickAccessBar(SARibbonCtrlContainer):
    def __init__(self, parent=None):
        super().__init__(None, parent)
        self.groupWidget = SARibbonButtonGroupWidget()
        self.setContainerWidget(self.groupWidget)

    def addSeparator(self):
        self.groupWidget.addSeparator()

    def addAction(self, act: QAction):
        self.groupWidget.addAction(act)

    def addWidget(self, w: QWidget):
        self.groupWidget.addWidget(w)

    def addMenu(self, m: QMenu, popmode=QToolButton.InstantPopup):
        self.groupWidget.addMenu(m, popmode)

    def initStyleOption(self, opt: QStyleOption):
        opt.initFrom(self)
