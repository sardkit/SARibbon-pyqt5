# -*- coding: utf-8 -*-
"""
@Module     SARibbonElementCreateDelegate
@Author     ROOT
"""
from PyQt5.QtCore import Qt, QMargins
from PyQt5.QtGui import QColor

from ..SAWidgets.SARibbonTabBar import SARibbonTabBar
from ..SAWidgets.SARibbonApplicationButton import SARibbonApplicationButton
from ..SAWidgets.SARibbonSeparatorWidget import SARibbonSeparatorWidget
from ..SAWidgets.SARibbonGalleryGroup import SARibbonGalleryGroup
from ..SAWidgets.SARibbonToolButton import SARibbonToolButton
from ..SAWidgets.SARibbonStackedWidget import SARibbonStackedWidget
from ..SAWidgets.SARibbonControlButton import SARibbonControlButton
from ..SAWidgets.SARibbonPannelOptionButton import SARibbonPannelOptionButton


class SARibbonStyleOption:
    """
    @brief 定义了saribbon所有尺寸相关信息，saribbon的建立都基于此类的尺寸，如果想调整，
    可以重载 @ref SARibbonElementCreateDelegate 的 @ref getRibbonStyleOption 函数
    """
    def __init__(self):
        self.mainbarHeightOfficeStyleThreeRow: int = 160    # OfficeStyle 样式下的mainbar高度
        self.mainbarHeightWPSStyleThreeRow: int = 130       # WpsLiteStyle 样式下的mainbar高度
        self.mainbarHeightOfficeStyleTwoRow: int = 134      # OfficeStyleTwoRow 样式下的mainbar高度
        self.mainbarHeightWPSStyleTwoRow: int = 104         # WpsLiteStyleTwoRow 样式下的mainbar高度
        self.titleBarHeight: int = 30                       # 标题栏高度
        self.tabBarHeight: int = 25                         # ribbon tab 的高度
        self.titleTextColor: QColor = Qt.black              # 标题颜色
        self.widgetBord: QMargins = QMargins(5, 1, 5, 5)    # 整个ribbonbar的四个边框
        self.tabBarBaseLineColor: QColor = QColor(186, 201, 219)     # tabbar 底部线条颜色


class SARibbonElementCreateDelegate:
    """
    @brief SARibbon的子元素创建的代理，SARibbon内部创建SAWidgets子元素都通过SARibbonElementCreateDelegate来创建
    """
    def __init__(self):
        self.m_opt: SARibbonStyleOption = SARibbonStyleOption()

    def createRibbonTabBar(self, parent):
        return SARibbonTabBar(parent)

    def createRibbonApplicationButton(self, parent):
        return SARibbonApplicationButton(parent)

    def createRibbonSeparatorWidget(self, parent, height: int=None):
        if height is not None:
            return SARibbonSeparatorWidget(height, parent)
        return SARibbonSeparatorWidget(parent)

    def createRibbonGalleryGroup(self, parent):
        return SARibbonGalleryGroup(parent)

    def createRibbonToolButton(self, parent):
        return SARibbonToolButton(parent)

    def createRibbonStackedWidget(self, parent):
        return SARibbonStackedWidget(parent)

    def createHidePannelButton(self, parent):
        """
        创建隐藏ribbon的按钮代理函数,
        :param parent: SARibbonBar
        """
        btn = SARibbonControlButton(parent)
        btn.setAutoRaise(False)
        btn.setObjectName('SARibbonBarHidePannelButton')
        btn.setToolButtonStyle(Qt.ToolButtonIconOnly)
        btn.setFixedSize(parent.tabBarHeight()-4, parent.tabBarHeight()-4)
        return btn

    def createRibbonPannelOptionButton(self, parent):
        """
        创建SARibbonPannelOptionButton
        """
        return SARibbonPannelOptionButton(parent)

    def createRibbonCommonWidget(self, parent, WidgetClass):
        """
        通用方式创建SARibbon原生的对象，WidgetClass为需要创建对象的类名
        """
        return WidgetClass(parent)

    def getRibbonStyleOption(self) -> SARibbonStyleOption:
        return self.m_opt

    def setRibbonStyleOption(self, opt: SARibbonStyleOption):
        self.m_opt = opt
