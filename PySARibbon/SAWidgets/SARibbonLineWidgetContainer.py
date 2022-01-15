# -*- coding: utf-8 -*-
"""
@Module     SARibbonControlButton
@Author     ROOT

@brief 一个窗口容器，把窗口放置中间，前面后面都可以设置文本，主要用于放置在pannel上的小窗口
实现如下效果：
PrefixLabel|_Widget_|SuffixLabel
"""

from PyQt5.QtWidgets import QWidget, QLabel, QHBoxLayout


class SARibbonLineWidgetContainer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.m_innerWidget: QWidget = None
        self.m_labelPrefix = QLabel(self)
        self.m_labelSuffix = QLabel(self)

        lay = QHBoxLayout()
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)
        lay.addWidget(self.m_labelPrefix)
        lay.addWidget(self.m_labelSuffix)
        self.setLayout(lay)

    def setWidget(self, innerWidget):
        """设置widget,不允许设置一个None"""
        lay: QHBoxLayout = self.layout()

        if self.m_innerWidget:
            lay.replaceWidget(self.m_innerWidget, innerWidget)
        else:
            lay.insertLayout(1, innerWidget)
        self.m_innerWidget = innerWidget

    def setPrefix(self, prefix: str):
        """设置前缀"""
        self.m_labelPrefix.setText(prefix)

    def setSuffix(self, suffix: str):
        """设置后缀"""
        self.m_labelSuffix.setText(suffix)

    def labelPrefix(self) -> QLabel:
        """前缀文本框"""
        return self.m_labelPrefix

    def labelSuffix(self) -> QLabel:
        """后缀文本框"""
        return self.m_labelSuffix
