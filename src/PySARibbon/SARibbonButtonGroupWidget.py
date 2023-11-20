# -*- coding: utf-8 -*-
"""
@Module     SARibbonButtonGroupWidget
@Author     ROOT
"""
from typing import List, Union
from PyQt5.QtCore import pyqtSignal, QSize, Qt, QEvent
from PyQt5.QtGui import QActionEvent
from PyQt5.QtWidgets import QFrame, QAction, QMenu, QToolButton, QWidget, QHBoxLayout, QSizePolicy, QWidgetAction

from .SAWidgets.SARibbonToolButton import SARibbonToolButton
from .SATools.SARibbonElementManager import RibbonSubElementDelegate


class SARibbonButtonGroupWidgetItem:
    def __init__(self, *_args):
        """
        SARibbonButtonGroupWidgetItem()
        SARibbonButtonGroupWidgetItem(QAction, QWidget, bool)
        """
        if len(_args) < 3:
            self.action: QAction = None
            self.widget: QWidget = None
            self.customWidget: bool = False
        else:
            self.action: QAction = _args[0]
            self.widget: QWidget = _args[1]
            self.customWidget: bool = _args[2]

    def compare(self, *_args) -> bool:
        """
        compare(QAction) -> bool
        compare(SARibbonButtonGroupWidgetItem) -> bool
        """
        if len(_args) < 1:
            return False

        if isinstance(_args[0], QAction):
            return self.action == _args[0]
        else:
            return self.action == _args[0].action


class SARibbonButtonGroupWidget(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.mItems: List[SARibbonButtonGroupWidgetItem] = list()

        layout = QHBoxLayout()  # 水平排布
        layout.setContentsMargins(0, 0, 0, 0)  # C++是setMargin(0)
        layout.setSpacing(0)
        self.setLayout(layout)
        self.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)

    def addAction(self, *_args) -> Union[None, QAction]:
        """
        addAction(QAction)
        addAction(QString, QIcon, popMode=QToolButton.InstantPopup) -> QAction
        """
        if len(_args) == 1:
            super().addAction(_args[0])
        else:
            a = QAction(_args[1], _args[0], self)
            super().addAction(a)
            popMode = QToolButton.InstantPopup if len(_args) < 3 else _args[2]
            if self.mItems:
                button: SARibbonToolButton = self.mItems[-1].widget
                button.setPopupMode(popMode)
            return a

    def addMenu(self, menu: QMenu, popMode=QToolButton.InstantPopup) -> QAction:
        a = menu.menuAction()
        self.addAction(a)
        btn = self.mItems[-1].widget
        btn.setPopupMode(popMode)
        return a

    def addSeparator(self) -> QAction:
        a = QAction()
        a.setSeparator(True)
        self.addAction(a)
        return a

    def addWidget(self, w: QWidget) -> QAction:
        a = QWidgetAction(self)
        a.setDefaultWidget(w)
        w.setAttribute(Qt.WA_Hover)
        self.addAction(a)
        return a

    def hideWidget(self, act: QAction):
        """隐藏指定Widget"""
        i = len(self.mItems)
        for i, it in enumerate(self.mItems):
            if isinstance(it.action, QWidgetAction) and it.action == act:
                it.widget.hide()
                widgetAction: QWidgetAction = it.action
                widgetAction.releaseWidget(it.widget)
                break
        if i < len(self.mItems):
            self.mItems.pop(i)

    def sizeHint(self) -> QSize:
        return self.layout().sizeHint()

    def minimumSizeHint(self) -> QSize:
        return self.layout().minimumSize()

    def actionEvent(self, e: QActionEvent):
        """处理action的事件"""
        item = SARibbonButtonGroupWidgetItem()
        item.action = e.action()

        if e.type() == QEvent.ActionAdded:
            if item.action and item.action.parent() != self:
                item.action.setParent(self)

            if item.action.isSeparator():
                sp = RibbonSubElementDelegate.createRibbonSeparatorWidget(self)
                sp.setTopBottomMargins(3, 3)
                item.widget = sp
            elif isinstance(item.action, QWidgetAction):
                widgetAction: QWidgetAction = item.action
                item.widget = widgetAction.requestWidget(self)
                item.widget.setAttribute(Qt.WA_LayoutUsesWidgetRect)
                item.widget.show()
                item.customWidget = True
            # 不是widget，自动生成SARibbonToolButton
            if not item.widget:
                btn = RibbonSubElementDelegate.createRibbonToolButton(self)
                btn.setAutoRaise(True)
                btn.setFocusPolicy(Qt.NoFocus)
                btn.setButtonType(SARibbonToolButton.SmallButton)
                btn.setToolButtonStyle(Qt.ToolButtonIconOnly)
                btn.setDefaultAction(item.action)
                btn.triggered.connect(self.actionTriggered)
                item.widget = btn
            self.layout().addWidget(item.widget)
            self.mItems.append(item)
        elif e.type() == QEvent.ActionChanged:
            # 让布局重新绘制
            self.layout().invalidate()
        elif e.type() == QEvent.ActionRemoved:
            item.action.disconnect(self)
            for it in self.mItems:
                if isinstance(it.action, QWidgetAction) and it.customWidget:
                    widgetAction: QWidgetAction = it.action
                    widgetAction.releaseWidget(it.widget)
                else:
                    it.widget.hide()
                    it.widget.deleteLater()
            self.mItems.clear()
            self.layout().invalidate()

    # 参考QToolBar.actionTriggered的信号
    actionTriggered = pyqtSignal(QAction)
