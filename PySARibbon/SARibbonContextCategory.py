# -*- coding: utf-8 -*-
"""
@Module     SARibbonContextCategory
@Author     ROOT

@brief 管理上下文(SARibbonCategory)标签的类
"""
from typing import Any, List

from PyQt5.QtCore import QObject, pyqtSignal, QEvent
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QWidget

from .SARibbonCategory import SARibbonCategory


class SARibbonContextCategory(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.contextID_ = None
        self.contextTitle_ = ''
        self.contextColor_ = QColor()
        self.categoryDataList: List[SARibbonCategory] = list()

    def addCategoryPage(self, title: str) -> SARibbonCategory:
        """上下文目录添加下属目录"""
        category = SARibbonCategory(self.parentWidget())
        category.markIsContextCategory(True)
        category.setWindowTitle(title)
        category.installEventFilter(self)
        self.categoryDataList.append(category)
        self.categoryPageAdded.emit(category)

        return category

    def categoryCount(self) -> int:
        """获取上下文标签下管理的标签个数"""
        return len(self.categoryDataList)

    def setId(self, idx):
        self.contextID_ = idx

    def id(self) -> Any:
        return self.contextID_

    def setContextColor(self, color: QColor):
        self.contextColor_ = color

    def contextColor(self) -> QColor:
        return self.contextColor_

    def setContextTitle(self, contextTitle: str):
        self.contextTitle_ = contextTitle

    def contextTitle(self) -> str:
        return self.contextTitle_

    def categoryPage(self, index) -> SARibbonCategory:
        """获取对应的tab页"""
        return self.categoryDataList[index]

    def categoryList(self) -> List[SARibbonCategory]:
        """获取所有的SARibbonCategory"""
        return self.categoryDataList

    def takeCategory(self, category: SARibbonCategory) -> bool:
        """移除category"""
        for i, cat in enumerate(self.categoryDataList):
            if category == cat:
                self.categoryDataList.pop(i)
                return True
        return False

    def parentWidget(self) -> QWidget:
        """获取父级窗口"""
        return self.parent()

    def eventFilter(self, watched, e):
        if watched is None:
            return False
        if e.type() == QEvent.Close:
            self.takeCategory(watched)
        return False

    # 信号
    categoryPageAdded = pyqtSignal(SARibbonCategory)
    categoryPageRemoved = pyqtSignal(SARibbonCategory)
