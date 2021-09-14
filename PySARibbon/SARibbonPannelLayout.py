# -*- coding: utf-8 -*-
"""
@Module     SARibbonPannelLayout
@Author     ROOT

@brief 针对SARibbonPannel的布局

SARibbonPannelLayout实际是一个列布局，每一列有2~3行，看窗口定占几行
核心函数：SARibbonPannelLayout.createItem
"""
from typing import List, Union
from PyQt5.QtCore import QRect, QSize, Qt
from PyQt5.QtWidgets import QLayout, QAction, QLayoutItem, QWidget, QWidgetAction, QSizePolicy

from .SAWidgets.SARibbonPannelItem import SARibbonPannelItem
from .SAWidgets.SARibbonSeparatorWidget import SARibbonSeparatorWidget
from .SAWidgets.SARibbonToolButton import SARibbonToolButton

G_HIGHER_MODE_HEIGHT = 98
G_LOWER_MODE_HEIGHT = 72
G_ICON_HIGH_FOR_HIGHER_LARGE = 32
G_ICON_HIGH_FOR_HIGHER_SMALL = 16


class SARibbonPannelLayout(QLayout):
    def __init__(self, parent):
        super().__init__(parent)

        self.m_items: List[SARibbonPannelItem] = list()
        self.m_rowCount = 3         # 默认3行，可通过setRowCount()函数设置
        self.m_columnCount = 0      # 记录有多少列
        self.m_expandFlag = False   # 标记是否是会扩展的
        self.m_sizeHint = QSize()   # sizeHint()返回的尺寸
        self.m_dirty = True         # 用于标记是否需要刷新元素，参考QToolBarLayout源码
        self.m_largeHeight = 0      # 记录大图标的高度
        self.m_hasOptionAction = False              # Panel是否存在OptionAction
        self.m_optionActionSize = QSize(12, 12)     # Panel中OptionAction的尺寸

        self.setSpacing(1)

    def setRowCount(self, count: int):
        self.m_rowCount = count

    def setOptionAction(self, on: bool, size: QSize):
        self.m_hasOptionAction = on
        self.m_optionActionSize = size

    def indexOf(self, action: QAction) -> int:
        """通过action查找索引，用于actionEvent添加action用"""
        for i, item in enumerate(self.m_items):
            if item.action == action:
                return i
        return -1

    def addItem(self, item: QLayoutItem):
        # print('addItem(): please use addAction() instead')
        # super().addItem(item)
        self.m_items.append(item)
        self.invalidate()  # 标记需要重新计算尺寸
        return

    def addWidget(self, widget: QWidget, rp=SARibbonPannelItem.RPLarge) -> SARibbonPannelItem:
        widget.setParent(self.parentWidget())

        widget.setAttribute(Qt.WA_LayoutUsesWidgetRect)
        widget.hide()
        item = SARibbonPannelItem(widget)
        item.rowProportion = rp
        if isinstance(widget, SARibbonToolButton):
            btn: SARibbonToolButton = widget
            item.action = btn.defaultAction()
            item.customWidget = False
        self.addItem(item)
        return item

    def addAction(self, action: QAction, rp=SARibbonPannelItem.RPNone) -> SARibbonPannelItem:
        if not isinstance(action, QAction):
            raise Exception('addAction() must get an QAction, please check you parameters')

        parent = self.parentWidget()
        button = SARibbonToolButton(parent)
        button.setAutoRaise(True)
        button.setFocusPolicy(Qt.NoFocus)
        buttonType = SARibbonToolButton.LargeButton if rp == SARibbonPannelItem.RPLarge else SARibbonToolButton.SmallButton
        if buttonType == SARibbonToolButton.LargeButton:
            ltp = SARibbonToolButton.Lite if self.m_rowCount == 2 else SARibbonToolButton.Normal
            button.setLargeButtonType(ltp)

        button.setButtonType(buttonType)
        button.setDefaultAction(action)
        # button.triggered.connect(action.triggered)
        return self.addWidget(button, rp)

    def itemAt(self, index: int) -> Union[None, QLayoutItem]:
        if index < 0 or index >= len(self.m_items):
            return None
        return self.m_items[index]

    def takeAt(self, index: int) -> Union[None, QLayoutItem]:
        if index < 0 or index >= len(self.m_items):
            return None
        item = self.m_items[index]
        self.m_items.pop(index)
        item.widget().hide()
        item.widget().deleteLater()
        self.invalidate()
        return item

    def count(self) -> int:
        return len(self.m_items)

    def isEmpty(self) -> bool:
        return bool(self.m_items)

    def invalidate(self):
        self.m_dirty = True
        super().invalidate()

    def expandingDirections(self) -> int:
        return Qt.Horizontal

    def setGeometry(self, rect: QRect):
        self.m_dirty = False
        self.updateGeomArray(rect)
        # super().setGeometry(rect)
        self.layoutActions()

    def minimumSize(self) -> QSize:
        return self.m_sizeHint

    def sizeHint(self) -> QSize:
        return self.m_sizeHint

    def pannelItem(self, action: QAction) -> Union[None, SARibbonPannelItem]:
        """通过action获取SARibbonPannelItem"""
        index = self.indexOf(action)
        if index >= 0:
            return self.m_items[index]
        return None

    def lastItem(self) -> Union[None, SARibbonPannelItem]:
        """获取最后一个添加的item"""
        if not self.m_items:
            return None
        return self.m_items[-1]

    def lastWidget(self) -> Union[None, QWidget]:
        """获取最后生成的窗口"""
        item = self.lastItem()
        if item:
            return item.widget()
        return None

    def defaultPannelHeight(self) -> int:
        """根据pannel的默认参数得到的pannel高度"""
        pannel = self.parentWidget()
        high = G_HIGHER_MODE_HEIGHT
        if not pannel:
            return high
        if pannel.pannelLayoutMode() == SARibbonPannelLayout.ThreeRowMode:
            high = G_HIGHER_MODE_HEIGHT
        elif pannel.pannelLayoutMode() == SARibbonPannelLayout.ThreeRowMode:
            high = G_LOWER_MODE_HEIGHT
        return high

    def move(self, fr: int, to: int):
        count = self.count()
        if fr < 0 or fr >= count:
            return
        if to < 0:
            to = 0
        elif to >= count:
            to = count - 1
        if fr == to:    # 位置相同直接返回
            return
        item = self.m_items[fr]
        self.m_items.pop(fr)
        if to == count - 1:
            self.m_items.append(item)
        else:
            self.m_items.insert(to, item)
        self.invalidate()

    def isDirty(self) -> bool:
        """判断是否需要重新布局"""
        return self.m_dirty

    def layoutActions(self):
        """布局所有action"""
        if self.m_dirty:
            self.updateGeomArray(self.geometry())
        showWidgets = list()
        hideWidgets = list()
        for item in self.m_items:
            if item.isEmpty():
                hideWidgets.append(item.widget())
            else:
                item.setGeometry(item.itemWillSetGeometry)
                showWidgets.append(item.widget())
        # 不在上面那里进行show和hide因为会触发SARibbonPannelLayout的重绘，导致循环绘制，非常影响效率
        for w in showWidgets:
            w.show()
        for w in hideWidgets:
            w.hide()

    def createItem(self, action: QAction, rp=SARibbonPannelItem.RPNone) -> Union[None, SARibbonPannelItem]:
        """把action转换为item"""
        pannel = self.parentWidget()
        if not pannel:
            return None
        customWidget = False
        widget = None
        if isinstance(action, QWidgetAction):
            widget = action.requestWidget(pannel)
            print(__file__, 'createItem', type(widget))
            print(__file__, 'createItem', widget.sizeHint())
            if widget:
                widget.setAttribute(Qt.WA_LayoutUsesWidgetRect)
                customWidget = True
        elif action.isSeparator():
            sep = SARibbonSeparatorWidget(pannel)
            widget = sep
        if not widget:
            button = SARibbonToolButton(pannel)
            button.setAutoRaise(True)
            button.setFocusPolicy(Qt.NoFocus)
            buttonType = SARibbonToolButton.LargeButton if rp == SARibbonPannelItem.RPLarge else SARibbonToolButton.SmallButton
            button.setButtonType(buttonType)
            if buttonType == SARibbonToolButton.LargeButton:
                ltp = SARibbonToolButton.Lite if pannel.isTwoRow() else SARibbonToolButton.Normal
                button.setLargeButtonType(ltp)
            button.setDefaultAction(action)
            button.triggered.connect(pannel.actionTriggered)
            widget = button
        widget.hide()
        result = SARibbonPannelItem(widget)
        result.rowProportion = rp
        result.customWidget = customWidget
        result.action = action
        return result

    def updateGeomArray(self, setRect: QRect):
        if not self.parentWidget():
            return

        height = setRect.height()
        pannel = self.parentWidget()
        titleH = pannel.titleHeight() if hasattr(pannel, 'titleHeight') else 0
        magin = self.contentsMargins()
        spacing = self.spacing()
        rowCount = self.m_rowCount  # rowcount 是ribbon的行，有2行和3行两种

        largeH = height - (magin.top() + magin.bottom()) - titleH
        smallH = (largeH - (rowCount - 1) * spacing) / rowCount
        self.m_largeHeight = largeH
        # row用于记录下个item应该属于第几行，item->rowIndex用于记录当前处于第几行
        row, column = 0, 0
        columMaxWidth = 0   # 记录每列最大的宽度
        totalWidth = 0      # 记录总宽度
        x = magin.left()    # x坐标
        lastRow0RP = SARibbonPannelItem.RPNone
        # Medium行的y坐标
        medy0 = magin.top() if rowCount == 2 else magin.top() + (largeH - 2 * smallH) / 3
        medy1 = magin.top() + smallH + spacing if rowCount == 2 else magin.top() + (
                (largeH - 2 * smallH) / 3) * 2 + smallH
        # Small行的y坐标
        smly0 = magin.top()
        smly1 = magin.top() + smallH + spacing
        smly2 = magin.top() + 2 * (smallH + spacing)
        for i, item in enumerate(self.m_items):
            if item.isEmpty():
                item.rowIndex = -1
                item.columnIndex = -1
                continue

            if item.widget() and (item.widget().sizePolicy().horizontalPolicy() & QSizePolicy.ExpandFlag):
                self.m_expandFlag = True
            exp = item.expandingDirections()
            rp = item.rowProportion
            if SARibbonPannelItem.RPNone == rp:
                rp = SARibbonPannelItem.RPLarge if (exp & Qt.Vertical) else SARibbonPannelItem.RPSmall
            hint = item.sizeHint()
            if SARibbonPannelItem.RPLarge == rp:
                # 在Large模式，如果不是处于新列的第一行，就需要进行换列处理
                if row != 0:
                    x += columMaxWidth + spacing
                    column += 1
                item.rowIndex = 0
                item.columnIndex = column
                item.itemWillSetGeometry = QRect(x, magin.top(), hint.width(), largeH)
                # 换列，x自动递增到下个坐标，列数增加，行数归零，最大列宽归零
                x += hint.width() + spacing
                row = 0
                column += 1
                columMaxWidth = 0
            elif SARibbonPannelItem.RPMedium == rp:
                if row > 1:  # row == 2表示前面一个item是small模式
                    x += columMaxWidth + spacing
                    row = 0
                    column += 1

                item.rowIndex = row
                item.columnIndex = column
                if row == 0:
                    item.itemWillSetGeometry = QRect(x, medy0, hint.width(), smallH)
                    row = 1
                    columMaxWidth = hint.width()
                    lastRow0RP = SARibbonPannelItem.RPMedium
                else:
                    item.itemWillSetGeometry = QRect(x, medy1, hint.width(), smallH)
                    # 换列
                    x += max(columMaxWidth, hint.width()) + spacing
                    row = 0
                    column += 1
                    columMaxWidth = 0
            else:   # SARibbonPannelItem.RPSmall
                item.rowIndex = row
                item.columnIndex = column
                if row == 0:
                    item.itemWillSetGeometry = QRect(x, smly0, hint.width(), smallH)
                    columMaxWidth = hint.width()
                    row = 1
                    lastRow0RP = SARibbonPannelItem.RPSmall
                elif row == 1:
                    # 若第一行是Medium，按Medium排列
                    y1 = medy1 if lastRow0RP == SARibbonPannelItem.RPMedium else smly1
                    item.itemWillSetGeometry = QRect(x, y1, hint.width(), smallH)
                    if 2 == rowCount or lastRow0RP == SARibbonPannelItem.RPMedium:
                        x += max(columMaxWidth, hint.width()) + spacing
                        row = 0
                        column += 1
                        columMaxWidth = 0
                    else:
                        row = 2
                        columMaxWidth = max(columMaxWidth, hint.width())
                else:
                    item.itemWillSetGeometry = QRect(x, smly2, hint.width(), smallH)
                    # 换列
                    x += max(columMaxWidth, hint.width()) + spacing
                    row = 0
                    column += 1
                    columMaxWidth = 0

            # 最后1个元素，更新totalWidth
            if i == len(self.m_items) - 1:
                # 触发了换列，直接等于column索引
                # 没有触发换列，真实列数等于column+1
                if item.columnIndex != column:
                    self.m_columnCount = column
                    totalWidth = x + magin.right()
                else:
                    self.m_columnCount = column + 1
                    totalWidth = x + magin.right() + columMaxWidth + spacing

        # 在有optionButton的2行模式的情况下，需要调整totalWidth
        if rowCount == 2 and self.m_hasOptionAction:
            totalWidth += self.m_optionActionSize.width()

        # 在设置完所有窗口后，再设置扩展属性的窗口
        if totalWidth < setRect.width():
            self.recalcExpandGeomArray(setRect)
        self.m_sizeHint = QSize(totalWidth, height)

    def recalcExpandGeomArray(self, setrect: QRect):
        """重新计算扩展item，此函数必须在updateGeomArray()函数之后调用"""
        expandwidth = setrect.width() - self.m_sizeHint.width()     # 能扩展的尺寸
        if expandwidth <= 0:
            return

        columnExpandInfo = dict()   # columnExpandInfo用于记录可以水平扩展的列和控件
        for item in self.m_items:
            if not item.isEmpty() and (item.expandingDirections() & Qt.Horizontal):
                value = columnExpandInfo.get(item.columnIndex, None)
                if not value:
                    columnExpandInfo[item.columnIndex] = {
                        'oldColumnWidth': 0,
                        'columnMaximumWidth': -1,
                        'columnExpandedWidth': 0,
                        'expandItems': list()
                    }.copy()
                    value = columnExpandInfo[item.columnIndex]
                value['expandItems'].append(item)
        # 没有需要扩展的就退出
        if not columnExpandInfo:
            return

        oneColCanexpandWidth = expandwidth / len(columnExpandInfo)
        for key, value in columnExpandInfo.items():
            oldColumnWidth, columnMaximumWidth = self.columnWidthInfo(key, value['oldColumnWidth'], value['columnMaximumWidth'])
            value['oldColumnWidth'] = oldColumnWidth
            value['columnMaximumWidth'] = columnMaximumWidth
            if oldColumnWidth < 0 or oldColumnWidth > columnMaximumWidth:
                columnExpandInfo.pop(key)
                continue
            # 开始调整
            colwidth = oneColCanexpandWidth + oldColumnWidth
            value['columnExpandedWidth'] = columnMaximumWidth if colwidth > columnMaximumWidth else colwidth
        # 重新调整尺寸，由于会涉及其他列的变更，因此需要所有都遍历一遍
        for key, value in columnExpandInfo.items():
            moveXLen = value['columnExpandedWidth'] - value['oldColumnWidth']
            for item in self.m_items:
                if item.isEmpty() or item.columnIndex < key:
                    continue
                if item.columnIndex == key:     # 此列的扩展
                    if item in value['expandItems']:
                        item.itemWillSetGeometry.setWidth(value['columnExpandedWidth'])
                    else:
                        continue
                else:
                    # 后面item的往左移动
                    item.itemWillSetGeometry.moveLeft(item.itemWillSetGeometry.x()+moveXLen)

    def columnWidthInfo(self, colindex: int, width: int, maximum: int) -> (int, int):
        rwidth = width
        rmaximum = maximum
        for item in self.m_items:
            if not item.isEmpty() and item.columnIndex == colindex:
                rwidth = max(rwidth, item.itemWillSetGeometry.width())
                rmaximum = max(rmaximum, item.widget().maximumWidth())
        return rwidth, rmaximum

    # PannelLayoutMode
    ThreeRowMode = 0
    TwoRowMode = 1
