# -*- coding: utf-8 -*-
"""
@Module     SARibbonPannelOptionButton
@Author     ROOT

@brief Pannel右下角的操作按钮
此按钮和一个action关联，使用SARibbonPannel.addOptionAction 函数用于生成此按钮，正常来说
用户并不需要直接操作此类，仅仅用于样式设计
如果一定要重载此按钮，可以通过重载 SARibbonElementCreateDelegate
的 SARibbonElementCreateDelegate.createRibbonPannelOptionButton来实现新的OptionButton
"""
import PySARibbon.resource_rc
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import QToolButton, QAction


class SARibbonPannelOptionButton(QToolButton):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAutoRaise(True)
        self.setCheckable(False)
        self.setFixedSize(QSize(16, 16))
        self.setIconSize(QSize(16, 16))
        self.setIcon(QIcon(':/icon/resource/ribbonPannelOptionButton.png'))

    def connectAction(self, act: QAction):
        self.clicked.connect(act.toggled)
