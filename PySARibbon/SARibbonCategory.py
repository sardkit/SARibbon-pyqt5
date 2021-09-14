# -*- coding: utf-8 -*-
"""
@Module     SARibbonCategory
@Author     ROOT

@brief 一项ribbon tab页
@note SARibbonCategory的windowTitle影响了其在SARibbonBar的标签显示，
如果要改标签名字，直接调用SARibbonCategory的setWindowTitle函数
"""
from typing import List, Union
from PyQt5.QtCore import QSize, QRect, QMargins, Qt, QEvent
from PyQt5.QtGui import QBrush, QPalette
from PyQt5.QtWidgets import QWidget, QMenuBar

from .SAWidgets.SARibbonSeparatorWidget import SARibbonSeparatorWidget
from .SAWidgets.SARibbonCategoryScrollButton import SARibbonCategoryScrollButton
from .SATools.SARibbonElementManager import RibbonSubElementDelegate
from .SARibbonPannel import SARibbonPannel


class SARibbonCategoryItem:
    def __init__(self, pannel=None, sep=None):
        self.pannelWidget: SARibbonPannel = pannel
        self.separatorWidget: SARibbonSeparatorWidget = sep
        self.mWillSetGeometry = QRect()             # pannel将要设置的Geometry
        self.mWillSetSeparatorGeometry = QRect()    # pannel将要设置的Separator的Geometry

    def isEmpty(self) -> bool:
        if self.pannelWidget:
            return self.pannelWidget.isHidden()
        return True

    def isNull(self) -> bool:
        return self.pannelWidget is None


class SARibbonCategoryPrivate:
    """
    @brief ribbon页的代理类
    """
    def __init__(self, parent):
        self.mainClass = parent
        self.mDefaultPannelLayoutMode = SARibbonPannel.ThreeRowMode
        self.mIsRightScrollBtnShow = False
        self.mIsLeftScrollBtnShow = False
        self.mTotalWidth = 0
        self.mXBase = 0
        self.mIsContextCategory = False     # 标记是否是上下文标签
        self.isCanCustomize = True          # 标记是否可以自定义
        self.mSizeHint = QSize(50, 50)
        self.mContentsMargins = QMargins(1, 1, 1, 1)
        self.mItemList: List[SARibbonCategoryItem] = list()
        self.mBar: QMenuBar = None
        self.mLeftScrollBtn = SARibbonCategoryScrollButton(Qt.LeftArrow, self.mainClass)
        self.mRightScrollBtn = SARibbonCategoryScrollButton(Qt.RightArrow, self.mainClass)

        self.mLeftScrollBtn.setVisible(False)
        self.mLeftScrollBtn.clicked.connect(self.ribbonCategory().onLeftScrollButtonClicked)
        self.mRightScrollBtn.setVisible(False)
        self.mRightScrollBtn.clicked.connect(self.ribbonCategory().onRightScrollButtonClicked)

    def ribbonCategory(self) -> QWidget:
        return self.mainClass

    def addPannel(self, *_args) -> Union[None, SARibbonPannel]:
        """
        addPannel(str) -> SARibbonPannel
        addPannel(SARibbonPannel)
        """
        if len(_args) < 1:
            return
        if isinstance(_args[0], str):
            return self.insertPannel(_args[0], len(self.mItemList))
        else:
            self.insertPannel(len(self.mItemList), _args[0])

    def insertPannel(self, *_args) -> Union[None, SARibbonPannel]:
        """
        addPannel(str, int) -> SARibbonPannel
        addPannel(int, SARibbonPannel)
        """
        if len(_args) < 2:
            raise Exception('parameter number < 2')
        if isinstance(_args[0], str):
            title = _args[0]
            index = _args[1]
            pannel = SARibbonPannel(self.ribbonCategory())
            pannel.setWindowTitle(title)
            pannel.setObjectName(title)
            pannel.setPannelLayoutMode(self.ribbonPannelLayoutMode())
            pannel.installEventFilter(self.mainClass)
            pannel.setVisible(True)
            self.insertPannel(index, pannel)
            return pannel
        else:
            if not _args[1]:
                return
            pannel: SARibbonPannel = _args[1]
            if pannel.parentWidget() != self.mainClass:
                pannel.setParent(self.mainClass)
            index = max(_args[0], 0)                    # 如果index<0，则插入开头
            index = min(len(self.mItemList), index)     # 如果index>当前长度，则插入末尾
            item = SARibbonCategoryItem(pannel, RibbonSubElementDelegate.createRibbonSeparatorWidget(self.mainClass))
            self.mItemList.insert(index, item)
            self.updateItemGeometry()

    def takePannel(self, pannel: SARibbonPannel) -> bool:
        item = None
        for i, it in enumerate(self.mItemList):
            if pannel == it.pannelWidget:
                item = it
                self.mItemList.pop(i)
                break
        if not item or item.isNull():
            return False

        if item.separatorWidget:
            item.separatorWidget.hide()
            item.separatorWidget.deleteLater()  # 对应的分割线删除，但pannel不删除
        return True

    def removePannel(self, pannel: SARibbonPannel) -> bool:
        if self.takePannel(pannel):
            pannel.hide()
            pannel.deleteLater()
            return True
        return False

    def setBackgroundBrush(self, brush: QBrush):
        p = self.ribbonCategory().palette()
        p.setBrush(QPalette.Background, brush)
        self.ribbonCategory().setPalette(p)

    def setRibbonPannelLayoutMode(self, m: int):
        """设置pannel的模式"""
        if self.mDefaultPannelLayoutMode == m:
            return
        self.mDefaultPannelLayoutMode = m
        ps = self.pannelList()
        for p in ps:
            p.setPannelLayoutMode(m)
        self.updateItemGeometry()

    def ribbonPannelLayoutMode(self) -> int:
        return self.mDefaultPannelLayoutMode

    def pannelList(self) -> List[SARibbonPannel]:
        res = [i.pannelWidget for i in self.mItemList]
        return res

    def totalSizeHintWidth(self) -> int:
        """计算所有元素的SizeHint宽度总和"""
        total = 0
        mag = self.mContentsMargins
        if not mag.isNull():
            total += mag.left() + mag.right()
        for item in self.mItemList:
            if item.isEmpty():
                continue    # 如果是hide就直接跳过
            pannelSize = item.pannelWidget.sizeHint()
            total += pannelSize.width()
            separatorSize = item.separatorWidget.sizeHint() if item.separatorWidget else QSize(0, 0)
            total += separatorSize.width()
        return total

    def categoryContentSize(self) -> QSize:
        category = self.ribbonCategory()
        s = category.size()
        mag = self.mContentsMargins
        if not mag.isNull():
            s.setHeight(s.height() - (mag.top() + mag.bottom()))
            s.setWidth(s.width() - (mag.right() + mag.left()))
        return s

    def updateItemGeometry(self):
        """更新item的布局，此函数会调用doItemLayout"""
        category = self.ribbonCategory()
        contentSize = self.categoryContentSize()
        y = 0 if self.mContentsMargins.isNull() else self.mContentsMargins.top()
        total = self.totalSizeHintWidth()
        canExpandingCount = 0   # 记录可以扩展的数量
        expandWidth = 0         # 扩展的宽度
        if total <= contentSize.width():
            self.mXBase = 0
            for item in self.mItemList:
                if not item.isEmpty() and item.pannelWidget.isExpanding():  # pannel可扩展
                    canExpandingCount += 1
            expandWidth = (contentSize.width()-total)/canExpandingCount if canExpandingCount > 0 else 0

        total = 0   # total重新计算
        x = self.mXBase
        # 先按照sizeHint设置所有的尺寸
        for item in self.mItemList:
            if item.isEmpty():
                if item.separatorWidget:
                    item.separatorWidget.hide()
                item.mWillSetGeometry = QRect(0, 0, 0, 0)
                item.mWillSetSeparatorGeometry = QRect(0, 0, 0, 0)
                continue
            p: SARibbonPannel = item.pannelWidget
            if not p:
                print('unknow widget in SARibbonCategoryLayout')
                continue
            pSize = p.sizeHint()
            separatorSize = item.separatorWidget.sizeHint() if item.separatorWidget else QSize(0, 0)
            if p.isExpanding():
                # 可扩展，就把pannel扩展到最大
                pSize.setWidth(pSize.width() + expandWidth)
            w = pSize.width()
            item.mWillSetGeometry = QRect(x, y, w, contentSize.height())
            x += w
            total += w
            w = separatorSize.width()
            item.mWillSetSeparatorGeometry = QRect(x, y, w, contentSize.height())
            x += w
            total += w
        self.mTotalWidth = total

        # 判断滚动按钮是否显示
        if total > contentSize.width():
            # 超过总长度，需要显示滚动按钮
            if self.mXBase == 0:
                # 已经移动到最左，需要可以向右移动
                self.mIsRightScrollBtnShow = True
                self.mIsLeftScrollBtnShow = False
            elif self.mXBase <= contentSize.width() - total:
                # 已经移动到最右，需要可以向左移动
                self.mIsRightScrollBtnShow = False
                self.mIsLeftScrollBtnShow = True
            else:
                # 移动到中间两边都可以动
                self.mIsRightScrollBtnShow = True
                self.mIsLeftScrollBtnShow = True
        else:
            # total 小于 categoryWidth
            self.mIsRightScrollBtnShow = False
            self.mIsLeftScrollBtnShow = False

        cp = category.parentWidget()
        parentHeight = cp.height() if cp else contentSize.height()
        parentWidth = cp.width() if not cp else total
        self.mSizeHint = QSize(parentWidth, parentHeight)
        self.doItemLayout()

    def doItemLayout(self):
        category: SARibbonCategory = self.ribbonCategory()
        # 两个滚动按钮的位置永远不变
        self.mLeftScrollBtn.setGeometry(1, 0, 12, category.height())
        self.mRightScrollBtn.setGeometry(category.width()-13, 0, 12, category.height())
        showWidgets = list()
        hideWidgets = list()
        for item in self.mItemList:
            if item.isNull():
                continue
            if item.isEmpty():
                hideWidgets.append(item.pannelWidget)
                if item.separatorWidget:
                    hideWidgets.append(item.separatorWidget)
            else:
                item.pannelWidget.setGeometry(item.mWillSetGeometry)
                showWidgets.append(item.pannelWidget)
                if item.separatorWidget:
                    item.separatorWidget.setGeometry(item.mWillSetSeparatorGeometry)
                    showWidgets.append(item.separatorWidget)
        self.mRightScrollBtn.setVisible(self.mIsRightScrollBtnShow)
        self.mLeftScrollBtn.setVisible(self.mIsLeftScrollBtnShow)
        if self.mIsRightScrollBtnShow:
            self.mRightScrollBtn.raise_()
        if self.mIsLeftScrollBtnShow:
            self.mLeftScrollBtn.raise_()
        # 不在上面进行show和hide因为会触发SARibbonPannelLayout的重绘，导致循环绘制，非常影响效率
        for w in showWidgets:
            w.show()
        for w in hideWidgets:
            w.hide()


class SARibbonCategory(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.m_d = SARibbonCategoryPrivate(self)

        self.setAutoFillBackground(True)
        self.setBackgroundBrush(Qt.white)

    def categoryName(self) -> str:
        """category的名字,等同windowTitle函数"""
        return self.windowTitle()

    def setCategoryName(self, title: str):
        """设置category名字，等同setWindowTitle"""
        self.setWindowTitle(title)

    def ribbonPannelLayoutMode(self) -> int:
        """设置pannel的模式"""
        return self.m_d.ribbonPannelLayoutMode()

    def addPannel(self, *_args):
        """添加pannel
        addPannel(str) -> SARibbonPannel
        addPannel(SARibbonPannel)
        """
        return self.m_d.addPannel(*_args)

    def insertPannel(self, title: str, index: int) -> SARibbonPannel:
        """新建一个pannel，并插入到index位置"""
        return self.m_d.insertPannel(title, index)

    def pannelByName(self, title: str) -> Union[SARibbonPannel, None]:
        """通过名字查找pannel"""
        for item in self.m_d.mItemList:
            if item.pannelWidget and item.pannelWidget.windowTitle() == title:
                return item.pannelWidget
        return None

    def pannelByObjectName(self, objname: str) -> Union[SARibbonPannel, None]:
        """通过ObjectName查找pannel"""
        for item in self.m_d.mItemList:
            if item.pannelWidget and item.pannelWidget.objectName() == objname:
                return item.pannelWidget
        return None

    def pannelByIndex(self, index: int) -> Union[SARibbonPannel, None]:
        """通过索引找到pannel，如果超过索引范围，会返回None"""
        if index >= 0 and index < len(self.m_d.mItemList):
            return self.m_d.mItemList[index].pannelWidget
        return None

    def pannelIndex(self, p: SARibbonPannel) -> int:
        """查找pannel对应的索引"""
        for i, item in enumerate(self.m_d.mItemList):
            if item.pannelWidget == p:
                return i
        return -1

    def movePannel(self, fr: int, to: int):
        """移动一个Pannel从from index到to index"""
        if fr == to:
            return
        if to < 0:
            to = 0
        count = self.pannelCount()
        if to >= count:
            to = count - 1
        item = self.m_d.mItemList[fr]
        self.m_d.mItemList.pop(fr)
        self.m_d.mItemList.insert(to, item)
        self.m_d.updateItemGeometry()

    def takePannel(self, p: SARibbonPannel) -> bool:
        """pannel脱离SARibbonCategory的管理"""
        return self.m_d.takePannel(p)

    def removePannel(self, *_args) -> bool:
        """
        removePannel(SARibbonPannel) -> bool
        removePannel(int) -> bool

        移除Pannel，Category会直接回收SARibbonPannel内存
        """
        if len(_args) < 1:
            return False
        if isinstance(_args[0], int):
            p = self.pannelByIndex(_args[0])
            if not p:
                return False
            else:
                return self.removePannel(p)
        return self.m_d.removePannel(_args[0])

    def setBackgroundBrush(self, brush: QBrush):
        self.m_d.setBackgroundBrush(brush)

    def pannelList(self) -> List[SARibbonPannel]:
        return self.m_d.pannelList()

    def sizeHint(self) -> QSize:
        return self.m_d.mSizeHint

    def isContextCategory(self) -> bool:
        return self.m_d.mIsContextCategory

    def pannelCount(self) -> int:
        return len(self.m_d.mItemList)

    def isCanCustomize(self) -> bool:
        return self.m_d.isCanCustomize

    def setCanCustomize(self, b: bool):
        self.m_d.isCanCustomize = b

    def ribbonBar(self) -> QMenuBar:
        return self.m_d.mBar

    def setRibbonBar(self, bar: QMenuBar):
        self.m_d.mBar = bar

    def setRibbonPannelLayoutMode(self, m: int):
        self.m_d.setRibbonPannelLayoutMode(m)

    def markIsContextCategory(self, isContextCategory=True):
        """标记这个是上下文标签"""
        self.m_d.mIsContextCategory = isContextCategory

    # 事件
    def event(self, e):
        if e.type() == QEvent.LayoutRequest:
            self.m_d.updateItemGeometry()
        return super().event(e)

    def resizeEvent(self, e):
        super().resizeEvent(e)
        self.m_d.updateItemGeometry()

    def wheelEvent(self, e):
        """在超出边界情况下，滚轮可滚动pannel"""
        catWidth = self.m_d.categoryContentSize().width()
        totalWidth = self.m_d.mTotalWidth   # 求总宽
        if totalWidth > catWidth:
            # 这个时候滚动有效
            scrollpix = int(e.angleDelta().y() / 4)  # C++使用的e.delta()已弃用，使用e.angleDelta().y()代替
            if scrollpix < 0:
                # 当滚轮向上滑，SARibbonCategory向左走
                tmp = self.m_d.mXBase - scrollpix
                delta = catWidth - totalWidth
                self.m_d.mXBase = tmp if tmp < delta else delta
            else:
                # 当滚轮向下滑，SARibbonCategory向右走
                tmp = self.m_d.mXBase - scrollpix
                self.m_d.mXBase = tmp if tmp > 0 else 0
            self.m_d.updateItemGeometry()
        else:
            e.ignore()
            self.m_d.mXBase = 0

    def eventFilter(self, watched, e) -> bool:
        # if watched is None:
        #     return False
        return False

    # 槽函数
    def onLeftScrollButtonClicked(self):
        width = self.m_d.categoryContentSize().width()
        totalWidth = self.m_d.mTotalWidth   # 所有widget的总宽
        if totalWidth > width:
            tmp = self.m_d.mXBase + width
            self.m_d.mXBase = tmp if tmp > 0 else 0
        else:
            self.m_d.mXBase = 0
        self.m_d.updateItemGeometry()

    def onRightScrollButtonClicked(self):
        width = self.m_d.categoryContentSize().width()
        totalWidth = self.m_d.mTotalWidth   # 所有widget的总宽
        if totalWidth > width:
            tmp = self.m_d.mXBase - width
            delta = width - totalWidth
            self.m_d.mXBase = tmp if tmp < delta else delta
        else:
            self.m_d.mXBase = 0
        self.m_d.updateItemGeometry()


if __name__ == '__main__':
    from PyQt5.QtGui import QIcon
    from PyQt5.QtWidgets import QApplication, QAction

    app = QApplication([])
    # mainWindow = SARibbonCategory()
    # pannel = mainWindow.addPannel('Panel 1')
    mainWindow = SARibbonPannel('Panel 1')
    pannel = mainWindow

    act = QAction(mainWindow)
    act.setObjectName('Save')
    act.setText('Save')
    act.setIcon(QIcon('resource/icon/save.png'))
    pannel.addLargeAction(act)
    act = QAction(mainWindow)
    act.setObjectName('Save')
    act.setText('Save')
    act.setIcon(QIcon('resource/icon/save.png'))
    pannel.addLargeAction(act)

    mainWindow.setMinimumWidth(500)
    mainWindow.show()
    app.exec()

