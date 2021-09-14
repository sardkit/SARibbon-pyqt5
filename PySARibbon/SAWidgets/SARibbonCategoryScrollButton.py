# -*- coding: utf-8 -*-
"""
@Module     SARibbonCategoryScrollButton
@Author     ROOT

@brief SARibbonCategory无法完全显示时，显示的调整按钮
重新定义是为了防止被外部的样式影响,同时可以使用SARibbonCategoryScrollButton的样式定义
"""
from PyQt5.QtWidgets import QToolButton


class SARibbonCategoryScrollButton(QToolButton):
    def __init__(self, arrType, parent):
        super().__init__(parent)
        self.setArrowType(arrType)
