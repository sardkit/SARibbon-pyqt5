# -*- coding: utf-8 -*-
"""
@Module     SARibbonMenu
@Author     ROOT
"""
from typing import Union

from PyQt5.QtWidgets import QMenu, QAction, QWidget, QSizePolicy, QWidgetAction


class SARibbonMenu(QMenu):
    def __init__(self, *_args):
        """
        __init__(parent=None)
        __init__(str, parent=None)
        """
        parent = None
        arg_len = len(_args)
        if arg_len > 0 and isinstance(_args[0], str):
            title = _args[0]
            parent = _args[1] if arg_len >= 2 else None
            super().__init__(title, parent)
        else:
            super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def addRibbonMenu(self, *_args) -> Union[QAction, QMenu]:
        """
        addRibbonMenu(SARibbonMenu) -> QAction
        addRibbonMenu(str) -> SARibbonMenu
        addRibbonMenu(QIcon, str) -> SARibbonMenu
        """
        arg_len = len(_args)
        if arg_len == 1 and isinstance(_args[0], SARibbonMenu):
            return super().addMenu(_args[0])
        elif arg_len == 1 and isinstance(_args[0], str):
            menu = SARibbonMenu(_args[0], self)
            super().addMenu(menu)
            return menu
        else:
            menu = SARibbonMenu(_args[1], self)
            menu.setIcon(_args[0])
            super().addMenu(menu)
            return menu

    def addWidget(self, w: QWidget) -> QAction:
        action = QWidgetAction(self)
        action.setDefaultWidget(w)
        self.addAction(action)
        return action
