# -*- coding: utf-8 -*-
"""
@Module     SARibbonCategoryLayout
@Author     ROOT
"""
from typing import List
from PyQt5.QtCore import QRect, QSize, QMargins, Qt
from PyQt5.QtWidgets import QLayout, QWidgetItem, QLayoutItem, QWidget

from .SAWidgets.SARibbonCategoryScrollButton import SARibbonCategoryScrollButton
from .SAWidgets.SARibbonSeparatorWidget import SARibbonSeparatorWidget
from .SATools.SARibbonElementManager import RibbonSubElementDelegate


class SARibbonCategoryLayoutItem(QWidgetItem):
    def __init__(self, parent):
        super().__init__(parent)
        self.separatorWidget: SARibbonSeparatorWidget = None
        self.mWillSetGeometry = QRect()             # pannel将要设置的Geometry
        self.mWillSetSeparatorGeometry = QRect()    # pannel将要设置的Separator的Geometry


class SARibbonCategoryLayoutPrivate:
    def __init__(self, parent):
        self.q_d = parent
        self.mDirty = True
        self.mSizeHint = QSize(50, 50)
        self.mTotalWidth = 0
        self.mXBase = 0
        self.mLeftScrollBtn: SARibbonCategoryScrollButton = None
        self.mRightScrollBtn: SARibbonCategoryScrollButton = None
        self.mIsLeftScrollBtnShow = False
        self.mIsRightScrollBtnShow = False
        self.mItemList: List[SARibbonCategoryLayoutItem] = list()

    def totalSizeHintWidth(self) -> int:
        """计算所有元素的SizeHint宽度总和"""
        mag: QMargins = self.q_d.contentsMargins()
        total = 0
        if not mag.isNull():
            total += mag.left() + mag.right()
        for item in self.mItemList:
            if item.isEmpty():
                continue
            pannelSize = item.widget().sizeHint()
            separatorSize = QSize(0, 0)
            if item.separatorWidget:
                separatorSize = item.separatorWidget.sizeHint()
            total += pannelSize.width()
            total += separatorSize.width()
        return total


class SARibbonCategoryLayout(QLayout):
    def __init__(self, parent):
        super().__init__(parent)
        self.m_d = SARibbonCategoryLayoutPrivate(self)
        self.m_d.mLeftScrollBtn = SARibbonCategoryScrollButton(Qt.LeftArrow, parent)
        self.m_d.mLeftScrollBtn.setVisible(False)
        self.m_d.mLeftScrollBtn.clicked.connect(self.onLeftScrollButtonClicked)
        self.m_d.mRightScrollBtn = SARibbonCategoryScrollButton(Qt.RightArrow, parent)
        self.m_d.mRightScrollBtn.setVisible(False)
        self.m_d.mLeftScrollBtn.clicked.connect(self.onRightScrollButtonClicked)
        self.setContentsMargins(1, 1, 1, 1)

    def ribbonCategory(self) -> QWidget:
        return self.parentWidget()

    def addItem(self, item: QLayoutItem):
        print('Warning: in SARibbonCategoryLayout cannot addItem, use addPannel() instead')
        self.invalidate()

    def itemAt(self, index: int) -> QLayoutItem:
        """返回pannel的layout"""
        item = self.m_d.mItemList[index] if index <= len(self.m_d.mItemList)-1 else None
        return item

    def takeAt(self, index: int) -> QLayoutItem:
        return self.takePannelItem(index)

    def count(self) -> int:
        return len(self.m_d.mItemList)

    def takePannelItem(self, index: int) -> SARibbonCategoryLayoutItem:
        if index < 0 or index > len(self.m_d.mItemList)-1:
            return None
        self.invalidate()
        item = self.m_d.mItemList[index]
        if item.widget():
            item.widget().hide()
        if item.separatorWidget:
            item.separatorWidget.hide()
        return item

    def takePannel(self, pannel: QWidget) -> SARibbonCategoryLayoutItem:
        for i, item in enumerate(self.m_d.mItemList):
            if item.widget() == pannel:
                return self.takePannelItem(i)
        return None

    def addPannel(self, pannel: QWidget):
        """追加一个pannel"""
        self.insertPannel(self.count(), pannel)

    def insertPannel(self, index: int, pannel: QWidget):
        """插入一个pannel"""
        index = max(0, index)
        index = min(self.count(), index)
        item = SARibbonCategoryLayoutItem(pannel)
        item.separatorWidget = RibbonSubElementDelegate.createRibbonSeparatorWidget(self.parentWidget())
        self.m_d.mItemList.insert(index, item)
        self.invalidate()   # 标记需要重新计算尺寸

    def setGeometry(self, rect: QRect):
        self.m_d.mDirty = False
        self.updateGeometryArr()
        super().setGeometry(rect)
        self.doLayout()

    def sizeHint(self) -> QSize:
        return self.m_d.mSizeHint

    def minimumSize(self) -> QSize:
        return self.m_d.mSizeHint

    def expandingDirections(self) -> int:
        """SARibbonCategory充满整个stacked widget"""
        return Qt.Horizontal | Qt.Vertical

    def invalidate(self):
        self.m_d.mDirty = True
        super().invalidate()

    def updateGeometryArr(self):
        """更新尺寸"""
        category: QWidget = self.parentWidget()
        categoryWidth = category.width()
        mag = self.contentsMargins()
        height = category.height()
        y = 0
        if mag.isNull():
            y = mag.top()
            height -= mag.top() + mag.bottom()
            categoryWidth -= mag.r + mag.left()
        total = self.m_d.totalSizeHintWidth()
        canExpandingCount = 0
        expandWidth = 0
        # 判断是否超过总长度
        if total > categoryWidth:
            # 超过总长度，需要显示滚动按钮
            if self.m_d.mXBase == 0:
                # 已经移动到最左，需要可以向右移动
                self.m_d.mIsRightScrollBtnShow = True
                self.m_d.mIsLeftScrollBtnShow = False
            elif self.m_d.mXBase <= categoryWidth - total:
                # 已经移动到最右，需要可以向左移动
                self.m_d.mIsRightScrollBtnShow = False
                self.m_d.mIsLeftScrollBtnShow = True
            else:
                # 移动到中间两边都可以动
                self.m_d.mIsRightScrollBtnShow = True
                self.m_d.mIsLeftScrollBtnShow = True
        else:
            # total 小于 categoryWidth
            self.m_d.mIsRightScrollBtnShow = False
            self.m_d.mIsLeftScrollBtnShow = False
            # 必须这里把mBaseX设置为0，防止滚动按钮调整尺寸导致category无法显示
            self.m_d.mXBase = 0
            for item in self.m_d.mItemList:
                p: QWidget = item.widget()
                if p.isExpanding():     # pannel可扩展
                    canExpandingCount += 1
                expandWidth = (categoryWidth-total)/canExpandingCount if canExpandingCount > 0 else 0

        total = 0   # total重新计算
        x = self.m_d.mXBase
        # 先按照sizeHint设置所有的尺寸
        for item in self.m_d.mItemList:
            if item.isEmpty():
                if item.separatorWidget:
                    item.separatorWidget.hide()
                item.mWillSetGeometry = QRect(0, 0, 0, 0)
                item.mWillSetSeparatorGeometry = QRect(0, 0, 0, 0)
                continue
            p: QWidget = item.widget()
            if not p:
                print('unknow widget in SARibbonCategoryLayout')
                continue
            pSize = p.sizeHint()
            separatorSize = item.separatorWidget.sizeHint() if item.separatorWidget else QSize(0, 0)
            if p.isExpanding():
                # 可扩展，就把pannel扩展到最大
                pSize.setWidth(pSize.width() + expandWidth)
            w = pSize.width()
            item.mWillSetGeometry = QRect(x, y, w, height)
            x += w
            total += w
            w = separatorSize.width()
            item.mWillSetSeparatorGeometry = QRect(x, y, w, height)
            x += w
            total += w
        self.m_d.mTotalWidth = total
        cp = category.parentWidget()
        parentHeight = height if not cp else cp.height()
        parentWidth = total if not cp else cp.width()
        self.m_d.mSizeHint = QSize(parentWidth, parentHeight)

    def doLayout(self):
        if self.m_d.mDirty:
            self.updateGeometryArr()
        category: QWidget = self.parentWidget()
        # 两个滚动按钮的位置永远不变
        self.m_d.mLeftScrollBtn.setGeometry(0, 0, 12, category.height())
        self.m_d.mRightScrollBtn.setGeometry(category.width()-12, 0, 12, category.height())
        showWidgets = list()
        hideWidgets = list()
        for item in self.m_d.mItemList:
            if item.isEmpty():
                hideWidgets.append(item.widget())
                if item.separatorWidget:
                    hideWidgets.append(item.separatorWidget)
            else:
                item.widget().setFixedSize(item.mWillSetGeometry.size())
                item.widget().move(item.mWillSetGeometry.topLeft())
                showWidgets.append(item.widget())
                if item.separatorWidget:
                    item.separatorWidget.setGeometry(item.mWillSetSeparatorGeometry)
                    showWidgets.append(item.separatorWidget)
        self.m_d.mRightScrollBtn.setVisible(self.m_d.mIsRightScrollBtnShow)
        self.m_d.mLeftScrollBtn.setVisible(self.m_d.mIsLeftScrollBtnShow)
        if self.m_d.mIsRightScrollBtnShow:
            self.m_d.mRightScrollBtn.raise_()
        if self.m_d.mIsLeftScrollBtnShow:
            self.m_d.mLeftScrollBtn.raise_()
        # 不在上面进行show和hide因为会触发SARibbonPannelLayout的重绘，导致循环绘制，非常影响效率
        for w in showWidgets:
            w.show()
        for w in hideWidgets:
            w.hide()

    def pannels(self) -> List[QWidget]:
        """返回所有pannels"""
        res = [item.widget() for item in self.m_d.mItemList]
        return res

    # 槽函数
    def onLeftScrollButtonClicked(self):
        category: QWidget = self.parentWidget()
        width = category.width()
        # 求总宽
        totalWidth = self.m_d.mTotalWidth
        if totalWidth > width:
            tmp = self.m_d.mXBase + width
            if tmp > 0:
                tmp = 0
            self.m_d.mXBase = tmp
        else:
            self.m_d.mXBase = 0
        self.invalidate()

    def onRightScrollButtonClicked(self):
        category: QWidget = self.parentWidget()
        width = category.width()
        # 求总宽
        totalWidth = self.m_d.mTotalWidth
        if totalWidth > width:
            tmp = self.m_d.mXBase - width
            if tmp < width - totalWidth:
                tmp = width - totalWidth
            self.m_d.mXBase = tmp
        else:
            self.m_d.mXBase = 0
        self.invalidate()


