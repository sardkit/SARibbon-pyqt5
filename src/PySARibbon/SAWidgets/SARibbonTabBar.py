# -*- coding: utf-8 -*-
"""
@Module     SARibbonTabBar
@Author     ROOT
"""
from PyQt5.QtCore import QMargins
from PyQt5.QtWidgets import QTabBar


class SARibbonTabBar(QTabBar):
    def __init__(self, parent):
        super().__init__(parent)
        self.m_tabMargin: QMargins = QMargins(6, 0, 0, 0)
        self.setExpanding(False)

    def tabMargin(self) -> QMargins:
        return self.m_tabMargin

    def setTabMargin(self, margin: QMargins):
        self.m_tabMargin = margin
