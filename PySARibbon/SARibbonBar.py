# -*- coding: utf-8 -*-
"""
@Module     SARibbonBar
@Author     ROOT

@brief SARibbonBar继承于QMenuBar,在SARibbonMainWindow中直接替换了原来的QMenuBar
通过setRibbonStyle()函数设置ribbon的风格
SARibbonBar参考office和wps，提供了四种风格的Ribbon模式,@ref SARibbonBar.RibbonStyle
如果想ribbon占用的空间足够小，WpsLiteStyleTwoRow模式能比OfficeStyle节省35%的高度空间

传统的Menu/ToolBar主要通过QMenu的addMenu添加菜单,通过addToolBar生成QToolBar,
再把QAction设置进QMenu和QToolBar中

SARibbonBar和传统方法相似，不过相对于传统的Menu/ToolBar QMenu和QToolBar是平级的，
Ribbon是有明显的层级关系:
SARibbonBar下面是 @ref SARibbonCategory，
SARibbonCategory下面是@ref SARibbonPannel，
SARibbonPannel下面是@ref SARibbonToolButton，
SARibbonToolButton管理着QAction

生成一个ribbon只需以下几个函数：
SARibbonBar.addCategoryPage(title: str) -> SARibbonCategory
SARibbonCategory.addPannel(title: str) -> SARibbonPannel
SARibbonPannel.addLargeAction(action: QAction) -> SARibbonToolButton
SARibbonPannel.addSmallAction(action: QAction) -> SARibbonToolButton

因此生成步骤如下：
@code
de setupRibbonUi():
    ......
    # ribbonwindow为SARibbonMainWindow
    categoryMain = SARibbonCategory()
    filePannel = SARibbonPannel()

    ribbon = ribbonwindow.ribbonBar()
    ribbon.setRibbonStyle(SARibbonBar::WpsLiteStyle)
    # 添加一个Main标签
    categoryMain = ribbon.addCategoryPage("Main")
    # Main标签下添加一个FilePannel
    filePannel = categoryMain.addPannel("FilePannel")
    # 开始为File Pannel添加action
    filePannel.addLargeAction(actionNew)
    filePannel.addLargeAction(actionOpen)
    filePannel.addLargeAction(actionSave)
    filePannel.addSmallAction(actionImportMesh)
    filePannel.addSmallAction(actionImportGeometry)
    ......
@endcode
"""
import PySARibbon.resource_rc
from typing import List, Union
from PyQt5.QtCore import Qt, QSize, pyqtSignal, QObject, QEvent, QRect, QPoint, QMargins
from PyQt5.QtGui import QIcon, QPainter, QColor, QResizeEvent, QMouseEvent, QPen, QHoverEvent, QCursor
from PyQt5.QtWidgets import QMenuBar, QAbstractButton, QApplication, QAction, QFrame, QStyle

from .SAWidgets.SARibbonStackedWidget import SARibbonStackedWidget
from .SAWidgets.SARibbonTabBar import SARibbonTabBar
from .SATools.SARibbonElementManager import RibbonSubElementStyleOpt, RibbonSubElementDelegate
from .SARibbonButtonGroupWidget import SARibbonButtonGroupWidget
from .SARibbonQuickAccessBar import SARibbonQuickAccessBar
from .SARibbonPannel import SARibbonPannel
from .SARibbonCategory import SARibbonCategory
from .SARibbonContextCategory import SARibbonContextCategory


class _SAContextCategoryManagerData:
    def __init__(self):
        self.contextCategory: SARibbonContextCategory = None
        self.tabPageIndex: List[int] = list()

    def compare(self, context: SARibbonContextCategory):
        return self.contextCategory == context


class _SARibbonTabData:
    def __init__(self):
        self.category: SARibbonCategory = None
        self.index = -1


class SARibbonBarPrivate:
    def __init__(self, parent):
        self.mainClass = parent
        self.iconRightBorderPosition = 1
        self.mContextCategoryColorListIndex = -1    # 记录contextCategory色系索引
        self.ribbonStyle: int = SARibbonBar.OfficeStyle
        self.lastShowStyle: int = SARibbonBar.OfficeStyle
        self.currentRibbonMode: int = SARibbonBar.NormalRibbonMode

        self.applitionButton: QAbstractButton = RibbonSubElementDelegate.createRibbonApplicationButton(self.mainClass)
        self.ribbonTabBar: SARibbonTabBar = RibbonSubElementDelegate.createRibbonTabBar(self.mainClass)
        self.stackedContainerWidget: SARibbonStackedWidget = RibbonSubElementDelegate.createRibbonStackedWidget(self.mainClass)
        self.quickAccessBar: SARibbonQuickAccessBar = SARibbonQuickAccessBar(self.mainClass)
        self.minimumCaterogyAction: QAction = None
        self.tabBarRightSizeButtonGroupWidget: SARibbonButtonGroupWidget = None
        self.windowButtonSize = QSize(100, RibbonSubElementStyleOpt.titleBarHeight)

        self.mHidedCategoryList: List[_SARibbonTabData] = list()
        self.mContextCategoryList: List[SARibbonContextCategory] = list()   # 存放所有的上下文标签
        self.currentShowingContextCategory: List[_SAContextCategoryManagerData] = list()
        # contextCategory的色系
        self.mContextCategoryColorList: List[QColor] = [
            QColor(201, 89, 156),   # 玫红
            QColor(242, 203, 29),   # 黄
            QColor(255, 157, 0),    # 橙
            QColor(14, 81, 167),    # 蓝
            QColor(228, 0, 69),     # 红
            QColor(67, 148, 0),     # 绿
        ]

    def init(self):
        """初始化ApplicationButton, RibbonTabBar, StackedContainerWidget, QuickAccessBar相关设置"""
        self.applitionButton.setObjectName("objSAApplicationButton")
        self.applitionButton.clicked.connect(self.mainClass.applitionButtonClicked)

        self.ribbonTabBar.setObjectName("objSARibbonTabBar")
        # self.ribbonTabBar.setDrawBase(False)
        self.ribbonTabBar.setDrawBase(True)
        self.ribbonTabBar.tabBarClicked.connect(self.mainClass.onCurrentRibbonTabClicked)
        self.ribbonTabBar.tabBarDoubleClicked.connect(self.mainClass.onCurrentRibbonTabDoubleClicked)
        self.ribbonTabBar.tabMoved.connect(self.mainClass.onTabMoved)
        self.ribbonTabBar.currentChanged.connect(self.mainClass.onCurrentRibbonTabChanged)

        self.stackedContainerWidget.setObjectName("objSAStackedContainerWidget")
        self.stackedContainerWidget.hidWindow.connect(self.mainClass.onStackWidgetHided)
        self.stackedContainerWidget.installEventFilter(self.mainClass)

        self.quickAccessBar.setObjectName("objSARibbonQuickAccessBar")
        self.setNormalMode()

    def setApplicationButton(self, btn: QAbstractButton):
        if not btn:
            return

        if btn.parent() != self.mainClass:
            btn.setParent(self.mainClass)
        if not btn.objectName():
            btn.setObjectName('objSAApplicationButton')
        btn.setVisible(True)
        btn.move(0, RibbonSubElementStyleOpt.titleBarHeight)
        self.applitionButton = btn
        self.applitionButton.clicked.connect(self.mainClass.applitionButtonClicked)

    def isContainContextCategoryInList(self, contextCategory: SARibbonContextCategory) -> bool:
        for iContextCategory in self.currentShowingContextCategory:
            if iContextCategory.compare(contextCategory):
                return True
        return False

    def setHideMode(self):
        self.currentRibbonMode = SARibbonBar.MinimumRibbonMode
        self.stackedContainerWidget.setPopupMode()
        self.stackedContainerWidget.setFocusPolicy(Qt.NoFocus)
        self.stackedContainerWidget.clearFocus()
        self.ribbonTabBar.setFocus()
        self.stackedContainerWidget.hide()
        self.mainClass.setFixedHeight(self.ribbonTabBar.geometry().bottom())

    def setNormalMode(self):
        self.currentRibbonMode = SARibbonBar.NormalRibbonMode
        self.stackedContainerWidget.setNormalMode()
        self.stackedContainerWidget.setFocus()
        self.stackedContainerWidget.show()

    def getContextCategoryColor(self) -> QColor:
        if not self.mContextCategoryColorList:
            self.mContextCategoryColorListIndex = -1
            return QColor()
        self.mContextCategoryColorListIndex += 1
        if self.mContextCategoryColorListIndex >= len(self.mContextCategoryColorList) or self.mContextCategoryColorListIndex < 0:
            self.mContextCategoryColorListIndex = 0
        return self.mContextCategoryColorList[self.mContextCategoryColorListIndex]


class SARibbonBar(QMenuBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.m_d = SARibbonBarPrivate(self)
        self.m_d.init()
        self.setRibbonStyle(SARibbonBar.OfficeStyle)

        if parent:
            parent.windowTitleChanged.connect(self.onWindowTitleChanged)
            parent.windowIconChanged.connect(self.onWindowIconChanged)
        # 重绘，若不执行此，会出现刚开始applicationButton尺寸异常
        QApplication.postEvent(self, QResizeEvent(self.size(), self.size()))

    @staticmethod
    def checkTwoRowStyle(style) -> bool:    # C++为isTwoRowStyle
        """判断RibbonStyle是否为2行模式"""
        return style & 0xFF00 > 0

    @staticmethod
    def checkOfficeStyle(style) -> bool:    # C++为isOfficeStyle
        """判断是否是office样式"""
        return style & 0xFF == 0

    def setTitle(self, title: str):
        self.applicationButton().setText(title)

    def applicationButton(self) -> QAbstractButton:
        """
        获取applicationButton
        """
        return self.m_d.applitionButton

    def setApplicationButton(self, btn: QAbstractButton):
        """
        设置applicationButton
        """
        self.m_d.setApplicationButton(btn)
        # 无论设置什么都触发resize
        QApplication.postEvent(self, QResizeEvent(self.size(), self.size()))

    def ribbonTabBar(self) -> SARibbonTabBar:
        """
        获取tabbar
        """
        return self.m_d.ribbonTabBar

    def addCategoryPage(self, *__args):
        """ 添加一个标签
        addCategoryPage(self, str) -> SARibbonCategory
        addCategoryPage(self, SARibbonCategory)
        """
        if len(__args) < 1:
            raise Exception('parameters length < 1')

        if isinstance(__args[0], str):
            title: str = __args[0]
            category = SARibbonCategory(self)
            category.setObjectName(title)
            category.setWindowTitle(title)
            self.addCategoryPage(category)
            return category
        else:
            category: SARibbonCategory = __args[0]
            category.setRibbonBar(self)
            mode = SARibbonPannel.TwoRowMode if self.isTwoRowStyle() else SARibbonPannel.ThreeRowMode
            category.setRibbonPannelLayoutMode(mode)
            index = self.m_d.ribbonTabBar.addTab(category.windowTitle())

            tabdata = _SARibbonTabData()
            tabdata.category = category
            tabdata.index = index
            self.m_d.ribbonTabBar.setTabData(index, tabdata)
            self.m_d.stackedContainerWidget.insertWidget(index, category)
            category.windowTitleChanged.connect(self.onCategoryWindowTitleChanged)

    def insertCategoryPage(self, *__args):
        """在index添加一个category，如果当前category数量少于index，则插入到最后
        insertCategoryPage(self, str, int) -> SARibbonCategory
        insertCategoryPage(self, SARibbonCategory, int)
        """
        if len(__args) < 2:
            raise Exception('parameters length < 2')

        if isinstance(__args[0], str):
            title = __args[0]
            index = __args[1]
            category = SARibbonCategory(self)
            category.setObjectName(title)
            category.setWindowTitle(title)
            self.insertCategoryPage(category, index)
            return category
        else:
            category: SARibbonCategory = __args[0]
            index = __args[1]
            i = self.m_d.ribbonTabBar.insertTab(index, category.windowTitle())
            mode = SARibbonPannel.TwoRowMode if self.isTwoRowStyle() else SARibbonPannel.ThreeRowMode
            category.setRibbonPannelLayoutMode(mode)

            tabdata = _SARibbonTabData()
            tabdata.category = category
            tabdata.index = i
            self.m_d.ribbonTabBar.setTabData(i, tabdata)
            self.m_d.stackedContainerWidget.insertWidget(index, category)
            category.windowTitleChanged.connect(self.onCategoryWindowTitleChanged)
            QApplication.postEvent(self, QResizeEvent(self.size(), self.size()))

    def categoryByName(self, title: str) -> Union[SARibbonCategory, None]:
        """通过名字查找Category"""
        c = self.m_d.stackedContainerWidget.count()
        for i in range(c):
            w = self.m_d.stackedContainerWidget.widget(i)
            if w and w.windowTitle() == title:
                return w
        return None

    def categoryByObjectName(self, objname: str) -> Union[SARibbonCategory, None]:
        """通过ObjectName查找Category"""
        c = self.m_d.stackedContainerWidget.count()
        for i in range(c):
            w = self.m_d.stackedContainerWidget.widget(i)
            if w and w.objectName() == objname:
                return w
        return None

    def categoryByIndex(self, index: int) -> Union[SARibbonCategory, None]:
        """
        通过索引找到category，如果超过索引范围，会返回None
        """
        var: _SARibbonTabData = self.m_d.ribbonTabBar.tabData(index)
        if var:
            return var.category
        return None

    def hideCategory(self, category: SARibbonCategory):
        """隐藏category,并不会删除或者取走，只是隐藏"""
        c = self.m_d.ribbonTabBar.count()
        for i in range(c):
            var: _SARibbonTabData = self.m_d.ribbonTabBar.tabData(i)
            if var.category == category:
                self.m_d.mHidedCategoryList.append(var)
                self.m_d.ribbonTabBar.removeTab(i)  # 仅仅把tab移除

    def showCategory(self, category: SARibbonCategory):
        """显示被隐藏的category"""
        for i, c in enumerate(self.m_d.mHidedCategoryList):
            if category == c.category:
                index = self.m_d.ribbonTabBar.insertTab(c.index, c.category.windowTitle())
                c.index = index
                self.m_d.ribbonTabBar.setTabData(index, c)
                self.m_d.mHidedCategoryList.pop(i)
                return
        self.raiseCategory(category)

    def isCategoryVisible(self, category: SARibbonCategory) -> bool:
        """
        判断这个category是否在显示状态，也就是tabbar有这个category
        """
        return self.categoryIndex(category) >= 0

    def categoryIndex(self, category: SARibbonCategory) -> int:
        """
        获取category的索引
        """
        cnt = self.m_d.ribbonTabBar.count()
        for i in range(cnt):
            c: _SARibbonTabData = self.m_d.ribbonTabBar.tabData(i)
            if category == c.category:
                return i
        return -1

    def moveCategory(self, fr: int, to: int):
        """移动一个Category从fr index到to index"""
        self.m_d.ribbonTabBar.moveTab(fr, to)
        # 这时要刷新所有tabdata的index信息
        cnt = self.m_d.ribbonTabBar.count()
        for i in range(cnt):
            c: _SARibbonTabData = self.m_d.ribbonTabBar.tabData(i)
            c.index = i
            self.m_d.ribbonTabBar.setTabData(i, c)
        # 这里会触发tabMoved信号，在tabMoved信号中调整stacked里窗口的位置

    def categoryPages(self, allGet: bool=True) -> List[SARibbonCategory]:
        """
        获取当前显示的所有的SARibbonCategory
        """
        res = list()
        cnt = self.m_d.stackedContainerWidget.count()
        for i in range(cnt):
            w = self.m_d.stackedContainerWidget.widget(i)
            if not allGet and w.isContextCategory():
                continue
            res.append(w)
        return res

    def removeCategory(self, category: SARibbonCategory):
        """移除SARibbonCategory，表现在tabbar会移除，面板会移除"""
        index = self.tabIndex(category)
        if index >= 0:
            self.m_d.ribbonTabBar.removeTab(index)
        self.m_d.stackedContainerWidget.removeWidget(category)
        # 同时验证这个category是否是contexcategory里的
        for c in self.m_d.mContextCategoryList:
            c.takeCategory(category)
            self.updateContextCategoryManagerData()
        # 移除完后需要重绘
        self.repaint()
        QApplication.postEvent(self, QResizeEvent(self.size(), self.size()))

    def addContextCategory(self, *_args) -> Union[None, SARibbonContextCategory]:
        """添加一个上下文标签
        addContextCategory(self, str, color=None, id=None) -> SARibbonContextCategory
        addContextCategory(self, SARibbonContextCategory)
        """
        if len(_args) < 1:
            raise Exception('parameters length < 1')

        if isinstance(_args[0], str):
            title: str = _args[0]
            color: QColor = None if len(_args) < 2 else _args[1]
            index = None if len(_args) < 3 else _args[2]
            if not(color and color.isValid()):
                color = self.m_d.getContextCategoryColor()
            context = SARibbonContextCategory(self)
            context.setObjectName(title)
            context.setContextTitle(title)
            context.setContextColor(color)
            context.setId(index)
            self.addContextCategory(context)
            return context
        else:
            context: SARibbonContextCategory = _args[0]
            context.categoryPageAdded.connect(self.onContextsCategoryPageAdded)
            # remove并没有绑定，主要是remove后在stacked里也不会显示，remove且delete的话，stacked里也会删除
            if self.currentRibbonStyle() == SARibbonBar.WpsLiteStyle:
                self.resizeInWpsLiteStyle()
            self.m_d.mContextCategoryList.append(context)

    def showContextCategory(self, context: SARibbonContextCategory):
        """显示上下文标签"""
        if self.isContextCategoryVisible(context):
            return

        contextCategoryData = _SAContextCategoryManagerData()
        contextCategoryData.contextCategory = context
        for i in range(context.categoryCount()):
            category = context.categoryPage(i)
            mode = SARibbonPannel.TwoRowMode if self.isTwoRowStyle() else SARibbonPannel.ThreeRowMode
            category.setRibbonPannelLayoutMode(mode)
            index = self.m_d.ribbonTabBar.addTab(category.windowTitle())
            contextCategoryData.tabPageIndex.append(index)

            tabdata = _SARibbonTabData()
            tabdata.category = category
            tabdata.index = index
            self.m_d.ribbonTabBar.setTabData(index, tabdata)
        self.m_d.currentShowingContextCategory.append(contextCategoryData)
        QApplication.postEvent(self, QResizeEvent(self.size(), self.size()))
        self.repaint()

    def hideContextCategory(self, context: SARibbonContextCategory):
        """隐藏上下文标签"""
        ishide = False
        for i, category in enumerate(self.m_d.currentShowingContextCategory):
            if context.compare(category.contextCategory):
                indexs = category.tabPageIndex
                for index in reversed(indexs):
                    self.m_d.ribbonTabBar.removeTab(index)
                self.m_d.currentShowingContextCategory.pop(i)
                ishide = True
        if ishide:
            QApplication.postEvent(self, QResizeEvent(self.size(), self.size()))
            self.repaint()

    def isContextCategoryVisible(self, context: SARibbonContextCategory) -> bool:
        """
        判断上下文是否在显示状态
        """
        return self.m_d.isContainContextCategoryInList(context)

    def setContextCategoryVisible(self, context: SARibbonContextCategory, visible: bool):
        """设置上下文标签的显示状态"""
        if visible:
            self.showContextCategory(context)
        else:
            self.hideContextCategory(context)

    def contextCategoryList(self) -> List[SARibbonContextCategory]:
        """
        获取所有的上下文标签
        """
        return self.m_d.mContextCategoryList

    def destroyContextCategory(self, context: SARibbonContextCategory):
        """销毁上下文标签，上下文标签的SARibbonCategory也会随之销毁"""
        # 如果上下文标签显示中，先隐藏
        if self.isContextCategoryVisible(context):
            self.hideContextCategory(context)
        # 删除上下文标签的相关内容
        self.m_d.mContextCategoryList.remove(context)  # C++是removeAll
        # self.m_d.mContextCategoryList = [c for c in self.m_d.mContextCategoryList if c != context]
        res = context.categoryList()
        for c in res:
            c.hide()
            c.deleteLater()
        context.deleteLater()
        QApplication.postEvent(self, QResizeEvent(self.size(), self.size()))

    def setMinimumMode(self, isMinimum: bool):
        """设置为最小/正常模式
        默认下双击tabbar会切换隐藏显示模式，如果想禁用此功能，
        可重载onCurrentRibbonTabDoubleClicked() 函数，不对函数进行任何处理即可
        """
        if isMinimum:
            self.m_d.setHideMode()
        else:
            self.m_d.setNormalMode()
        QApplication.sendEvent(self, QResizeEvent(self.size(), self.size()))

    def isMinimumMode(self) -> bool:
        """当前ribbon是否是隐藏模式"""
        return self.m_d.stackedContainerWidget.isPopupMode()

    def showMinimumModeButton(self, isShow=True):
        """设置显示隐藏ribbon按钮"""
        if isShow:
            rightBar = self.activeTabBarRightButtonGroup()
            if not self.m_d.minimumCaterogyAction:
                panBtn = RibbonSubElementDelegate.createHidePannelButton(self)
                panBtn.ensurePolished()     # 载入样式图标
                icon = QStyle.SP_TitleBarShadeButton if self.isMinimumMode() else QStyle.SP_TitleBarUnshadeButton
                action = QAction(self.style().standardIcon(icon), 'Hide', panBtn)
                action.setCheckable(True)
                action.triggered.connect(lambda on: self.setMinimumMode(on))
                panBtn.setDefaultAction(action)
                self.m_d.minimumCaterogyAction = rightBar.addWidget(panBtn)
                self.update()
        else:
            if self.m_d.minimumCaterogyAction:
                self.m_d.tabBarRightSizeButtonGroupWidget.hideWidget(self.m_d.minimumCaterogyAction)
                self.m_d.minimumCaterogyAction = None
        QApplication.sendEvent(self, QResizeEvent(self.size(), self.size()))

    def haveShowMinimumModeButton(self) -> bool:
        """是否显示隐藏ribbon按钮"""
        ret = self.m_d.minimumCaterogyAction is None
        return not ret

    def tabBarHeight(self) -> int:
        """ribbon tab的高度"""
        return RibbonSubElementStyleOpt.tabBarHeight

    def titleBarHeight(self) -> int:
        """ribbon title的高度"""
        return RibbonSubElementStyleOpt.titleBarHeight

    def activeTabBarRightButtonGroup(self) -> SARibbonButtonGroupWidget:
        """激活tabbar右边的按钮群"""
        if not self.m_d.tabBarRightSizeButtonGroupWidget:
            self.m_d.tabBarRightSizeButtonGroupWidget = SARibbonButtonGroupWidget(self)
            self.m_d.tabBarRightSizeButtonGroupWidget.setFrameShape(QFrame.NoFrame)
        self.m_d.tabBarRightSizeButtonGroupWidget.show()
        if not self.m_d.tabBarRightSizeButtonGroupWidget.isVisible():
            self.m_d.tabBarRightSizeButtonGroupWidget.setVisible(True)
        return self.m_d.tabBarRightSizeButtonGroupWidget

    def quickAccessBar(self) -> SARibbonQuickAccessBar:
        """快速响应栏"""
        return self.m_d.quickAccessBar

    def setRibbonStyle(self, style):
        """设置ribbonbar的风格，此函数会重新设置所有元素"""
        self.m_d.ribbonStyle = style
        self.m_d.lastShowStyle = style
        self.updateRibbonElementGeometry()
        oldSize = self.size()
        newSize = QSize(oldSize.width(), self.mainBarHeight())
        QApplication.sendEvent(self, QResizeEvent(newSize, oldSize))

        if SARibbonBar.MinimumRibbonMode == self.currentRibbonState():
            # 处于最小模式下时，bar的高度为tabbar的bottom，这个调整必须在resize event之后
            self.setFixedHeight(self.m_d.ribbonTabBar.geometry().bottom())

    def currentRibbonStyle(self) -> int:
        """返回当前ribbon的风格"""
        return self.m_d.ribbonStyle

    def currentRibbonState(self) -> int:
        """当前的模式"""
        return self.m_d.currentRibbonMode

    def setCurrentIndex(self, index: int):
        """设置当前ribbon的index"""
        self.m_d.ribbonTabBar.setCurrentIndex(index)

    def currentIndex(self) -> int:
        """返回当前的tab索引"""
        return self.m_d.ribbonTabBar.currentIndex()

    def raiseCategory(self, category: SARibbonCategory):
        """确保标签显示出来，tab并切换到对应页"""
        index = self.m_d.stackedContainerWidget.indexOf(category)
        if index >= 0:
            self.setCurrentIndex(index)

    def isTwoRowStyle(self) -> bool:
        """判断当前的样式是否为两行"""
        return SARibbonBar.checkTwoRowStyle(self.currentRibbonStyle())

    def isOfficeStyle(self) -> bool:
        """判断当前的样式是否为office样式"""
        return SARibbonBar.checkOfficeStyle(self.currentRibbonStyle())

    def setWindowButtonSize(self, size: QSize):
        """告诉saribbonbar，window button的尺寸"""
        self.m_d.windowButtonSize = size

    def eventFilter(self, obj: QObject, e: QEvent) -> bool:
        if not obj:
            return super().eventFilter(obj, e)

        if obj == self.cornerWidget(Qt.TopLeftCorner) or obj == self.cornerWidget(Qt.TopRightCorner):
            if e.type() in [QEvent.UpdateLater, QEvent.MouseButtonRelease, QEvent.WindowActivate]:
                QApplication.postEvent(self, QResizeEvent(self.size(), self.size()))
        elif obj == self.m_d.stackedContainerWidget:
            '''
            在stack 是popup模式时，点击的是stackedContainerWidget区域外的时候，如果是在ribbonTabBar上点击
            那么忽略掉这次点击，把点击下发到ribbonTabBar,这样可以避免stackedContainerWidget在点击ribbonTabBar后
            隐藏又显示，出现闪烁
            '''
            if e.type() in [QEvent.MouseButtonPress, QEvent.MouseButtonDblClick] and \
                    self.m_d.stackedContainerWidget.isPopupMode():
                mouseEvent: QMouseEvent = e
                if not self.m_d.stackedContainerWidget.rect().contains(mouseEvent.pos()):
                    clickedWidget = QApplication.widgetAt(mouseEvent.globalPos())
                    if clickedWidget == self.m_d.ribbonTabBar:
                        targetPoint = clickedWidget.mapFromGlobal(mouseEvent.globalPos())
                        ePress = QMouseEvent(mouseEvent.type(), targetPoint, mouseEvent.globalPos(),
                                             mouseEvent.button(), mouseEvent.buttons(),
                                             mouseEvent.modifiers())
                        QApplication.postEvent(clickedWidget, ePress)
                        return True
        return super().eventFilter(obj, e)

    def calcMinTabBarWidth(self) -> int:
        """
        根据情况重置tabbar的宽度，主要针对wps模式
        """
        # 宽度需要根据tab的size来进行设置，让tabbar的长度刚刚好
        mg = self.m_d.ribbonTabBar.tabMargin()
        mintabBarWidth = 0
        for i in range(self.m_d.ribbonTabBar.count()):
            mintabBarWidth += self.m_d.ribbonTabBar.tabRect(i).width()
        mintabBarWidth += mg.left() + mg.right()
        return mintabBarWidth

    def mainBarHeight(self) -> int:
        """
        mainBarHeight的计算高度
        """
        currentStyle = self.currentRibbonStyle()
        styleDict = {
            SARibbonBar.OfficeStyle: RibbonSubElementStyleOpt.mainbarHeightOfficeStyleThreeRow,
            SARibbonBar.WpsLiteStyle: RibbonSubElementStyleOpt.mainbarHeightWPSStyleThreeRow,
            SARibbonBar.OfficeStyleTwoRow: RibbonSubElementStyleOpt.mainbarHeightOfficeStyleTwoRow,
            SARibbonBar.WpsLiteStyleTwoRow: RibbonSubElementStyleOpt.mainbarHeightWPSStyleTwoRow,
        }
        return styleDict.get(currentStyle, RibbonSubElementStyleOpt.mainbarHeightOfficeStyleThreeRow)

    def applitionButtonWidth(self) -> int:
        """
        应用按钮的宽度
        """
        return 56

    def tabIndex(self, category: SARibbonCategory) -> int:
        """
        根据SARibbonCategory查找tabbar的index
        """
        size = self.m_d.ribbonTabBar.count()
        for i in range(size):
            var = self.m_d.ribbonTabBar.tabData(i)
            if category == var.category:
                return i
        return -1

    def updateRibbonElementGeometry(self):
        """根据样式调整SARibbonCategory的布局形式"""
        categorys = self.categoryPages()
        for c in categorys:
            mode = SARibbonPannel.TwoRowMode if self.isTwoRowStyle() else SARibbonPannel.ThreeRowMode
            c.setRibbonPannelLayoutMode(mode)
        if SARibbonBar.NormalRibbonMode == self.currentRibbonState():
            self.setFixedHeight(self.mainBarHeight())

    def resizeInOfficeStyle(self):
        """按照Office风格重新定义尺寸"""
        self.updateRibbonElementGeometry()
        x = RibbonSubElementStyleOpt.widgetBord.left()
        y = RibbonSubElementStyleOpt.widgetBord.top()

        titleH = self.titleBarHeight()
        validTitleBarHeight = titleH - y
        tabH = self.tabBarHeight()
        x += self.m_d.iconRightBorderPosition + 5
        connerL = self.cornerWidget(Qt.TopLeftCorner)
        if connerL and connerL.isVisible():
            connerSize = connerL.sizeHint()
            if connerSize.height() < validTitleBarHeight:
                detal = (validTitleBarHeight - connerSize.height()) / 2
                connerL.setGeometry(x, y+detal, connerSize.width(), connerSize.height())
            else:
                connerL.setGeometry(x, y, connerSize.width(), validTitleBarHeight)
            x = connerL.geometry().right() + 5
        # quick access bar定位
        if self.m_d.quickAccessBar and self.m_d.quickAccessBar.isVisible():
            quickAccessBarSize = self.m_d.quickAccessBar.sizeHint()
            self.m_d.quickAccessBar.setGeometry(x, y, quickAccessBarSize.width(), validTitleBarHeight)

        # 第二行，开始布局applitionButton，tabbar，tabBarRightSizeButtonGroupWidget，TopRightCorner
        x = RibbonSubElementStyleOpt.widgetBord.left()
        y = titleH + RibbonSubElementStyleOpt.widgetBord.top()
        if self.m_d.applitionButton and self.m_d.applitionButton.isVisible():
            self.m_d.applitionButton.setGeometry(x, y, self.applitionButtonWidth(), tabH)
            x = self.m_d.applitionButton.geometry().right()
        # top right是一定要配置的，对于多文档窗口，子窗口的缩放等按钮就是通过这个窗口实现
        endX = self.width() - RibbonSubElementStyleOpt.widgetBord.right()
        connerR = self.cornerWidget(Qt.TopRightCorner)
        if connerR and connerR.isVisible():
            connerSize = connerR.sizeHint()
            endX -= connerSize.width()
            if connerSize.height() < tabH:
                detal = (tabH - connerSize.height()) / 2
                connerR.setGeometry(endX, y+detal, connerSize.width(), connerSize.height())
            else:
                connerR.setGeometry(endX, y, connerSize.width(), tabH)
        # tabBar 右边的附加按钮组，这里一般会附加一些类似登录等按钮组
        if self.m_d.tabBarRightSizeButtonGroupWidget and self.m_d.tabBarRightSizeButtonGroupWidget.isVisible():
            wSize = self.m_d.tabBarRightSizeButtonGroupWidget.sizeHint()
            endX -= wSize.width()
            self.m_d.tabBarRightSizeButtonGroupWidget.setGeometry(endX, y, wSize.width(), tabH)
        # 最后确定tabbar宽度
        tabBarWidth = endX - x
        self.m_d.ribbonTabBar.setGeometry(x, y, tabBarWidth, tabH)
        # 调整整个stackedContainer
        self.resizeStackedContainerWidget()

    def resizeInWpsLiteStyle(self):
        """按照WPS风格重新定义尺寸"""
        self.updateRibbonElementGeometry()
        x = RibbonSubElementStyleOpt.widgetBord.left()
        y = RibbonSubElementStyleOpt.widgetBord.top()
        titleH = self.titleBarHeight()
        validTitleBarHeight = titleH - y
        # WPS风格下applitionButton 先定位
        if self.m_d.applitionButton and self.m_d.applitionButton.isVisible():
            self.m_d.applitionButton.setGeometry(x, y, self.applitionButtonWidth(), titleH)
            x = self.m_d.applitionButton.geometry().right() + 2

        # applitionButton定位完后先布局右边内容
        endX = self.width() - RibbonSubElementStyleOpt.widgetBord.right() - self.m_d.windowButtonSize.width()
        connerR = self.cornerWidget(Qt.TopRightCorner)
        if connerR and connerR.isVisible():
            connerSize = connerR.sizeHint()
            endX -= connerSize.width()
            if connerSize.height() < validTitleBarHeight:
                detal = (validTitleBarHeight - connerSize.height()) / 2
                connerR.setGeometry(endX, y + detal, connerSize.width(), connerSize.height())
            else:
                connerR.setGeometry(endX, y, connerSize.width(), validTitleBarHeight)
        # quickAccessBar定位右边邻接buttonGroup
        if self.m_d.quickAccessBar and self.m_d.quickAccessBar.isVisible():
            quickAccessBarSize = self.m_d.quickAccessBar.sizeHint()
            endX -= quickAccessBarSize.width()
            self.m_d.quickAccessBar.setGeometry(endX, y, quickAccessBarSize.width(), validTitleBarHeight)

        connerL = self.cornerWidget(Qt.TopLeftCorner)
        if connerL and connerL.isVisible():
            connerSize = connerL.sizeHint()
            endX -= connerSize.width()
            if connerSize.height() < validTitleBarHeight:
                detal = (validTitleBarHeight - connerSize.height()) / 2
                connerL.setGeometry(endX, y + detal, connerSize.width(), connerSize.height())
            else:
                connerL.setGeometry(endX, y, connerSize.width(), validTitleBarHeight)

        # 开始定位tabbar以及tabBarRightSizeButtonGroupWidget
        # tab bar 定位 wps模式下applitionButton的右边就是tab bar, tabBar 右边的附加按钮组
        if self.m_d.tabBarRightSizeButtonGroupWidget and self.m_d.tabBarRightSizeButtonGroupWidget.isVisible():
            wSize = self.m_d.tabBarRightSizeButtonGroupWidget.sizeHint()
            endX -= wSize.width()
            self.m_d.tabBarRightSizeButtonGroupWidget.setGeometry(endX, y, wSize.width(), validTitleBarHeight)

        # 计算tab所占用的宽度，最后确定tabbar宽度
        tabBarWidth = min(endX - x, self.calcMinTabBarWidth())
        tabH = min(self.tabBarHeight(), validTitleBarHeight)
        # 如果tabH较小，则下以，让tab底部和title的底部对齐
        y = y + validTitleBarHeight - tabH
        self.m_d.ribbonTabBar.setGeometry(x, y, tabBarWidth, tabH)
        # 调整整个stackedContainer
        self.resizeStackedContainerWidget()

    def paintInNormalStyle(self):
        """绘制Office Style背景"""
        p = QPainter(self)
        self.paintBackground(p)

        p.save()
        # 显示上下文标签
        contextCategoryRegion = QPoint(self.width(), -1)
        for ccd in self.m_d.currentShowingContextCategory:
            indexs = ccd.tabPageIndex
            clr = ccd.contextCategory.contextColor()
            if indexs:
                contextTitleRect = QRect(self.m_d.ribbonTabBar.tabRect(indexs[0]))
                endRect = QRect(self.m_d.ribbonTabBar.tabRect(indexs[-1]))
                contextTitleRect.setRight(endRect.right())
                contextTitleRect.translate(self.m_d.ribbonTabBar.x(), self.m_d.ribbonTabBar.y())
                contextTitleRect.setHeight(self.m_d.ribbonTabBar.height()-1)    # 减1像素，避免tabbar基线覆盖
                contextTitleRect -= self.m_d.ribbonTabBar.tabMargin()
                # 把区域顶部扩展到窗口顶部
                contextTitleRect.setTop(RibbonSubElementStyleOpt.widgetBord.top())
                # 绘制
                self.paintContextCategoryTab(p, ccd.contextCategory.contextTitle(), contextTitleRect, clr)
                # 更新上下文标签的范围，用于控制标题栏的显示
                if contextTitleRect.left() < contextCategoryRegion.x():
                    contextCategoryRegion.setX(contextTitleRect.left())
                if contextTitleRect.right() > contextCategoryRegion.y():
                    contextCategoryRegion.setY(contextTitleRect.right())

            if self.m_d.ribbonTabBar.currentIndex() in indexs:
                pen = QPen()
                pen.setColor(clr)
                pen.setWidth(1)
                p.setPen(pen)
                p.setBrush(Qt.NoBrush)
                p.drawRect(self.m_d.stackedContainerWidget.geometry())

        p.restore()
        # 显示标题等
        parWindow = self.parentWidget()
        if parWindow:
            titleRegion = QRect()
            if contextCategoryRegion.y() < 0:
                titleRegion.setRect(
                    self.m_d.quickAccessBar.geometry().right()+1,
                    RibbonSubElementStyleOpt.widgetBord.top(),
                    self.width()-self.m_d.iconRightBorderPosition-RibbonSubElementStyleOpt.widgetBord.right()
                    - self.m_d.windowButtonSize.width()-self.m_d.quickAccessBar.geometry().right()-1,
                    RibbonSubElementStyleOpt.titleBarHeight,
                )
            else:
                leftwidth = contextCategoryRegion.x() - self.m_d.quickAccessBar.geometry().right() - self.m_d.iconRightBorderPosition
                rightwidth = self.width() - contextCategoryRegion.y() - self.m_d.windowButtonSize.width()
                if rightwidth > leftwidth:  # 说明右边的区域大一点，标题显示在右
                    titleRegion.setRect(
                        contextCategoryRegion.y(),
                        RibbonSubElementStyleOpt.widgetBord.top(),
                        rightwidth,
                        RibbonSubElementStyleOpt.titleBarHeight,
                    )
                else:   # 说明左边的区域大一点，标题显示在右
                    titleRegion.setRect(
                        self.m_d.iconRightBorderPosition+self.m_d.quickAccessBar.geometry().right(),
                        RibbonSubElementStyleOpt.widgetBord.top(),
                        leftwidth,
                        RibbonSubElementStyleOpt.titleBarHeight,
                    )
            self.paintWindowTitle(p, parWindow.windowTitle(), titleRegion)
            self.paintWindowIcon(p, parWindow.windowIcon())

    def paintInWpsLiteStyle(self):
        """绘制WPS Style背景"""
        p = QPainter(self)
        self.paintBackground(p)

        p.save()
        for ccd in self.m_d.currentShowingContextCategory:
            indexs = ccd.tabPageIndex
            clr = ccd.contextCategory.contextColor()
            if indexs:
                contextTitleRect = QRect(self.m_d.ribbonTabBar.tabRect(indexs[0]))
                endRect = QRect(self.m_d.ribbonTabBar.tabRect(indexs[-1]))
                contextTitleRect.setRight(endRect.right())
                contextTitleRect.translate(self.m_d.ribbonTabBar.x(), self.m_d.ribbonTabBar.y())
                contextTitleRect.setHeight(self.m_d.ribbonTabBar.height()-1)    # 减1像素，避免tabbar基线覆盖
                contextTitleRect -= self.m_d.ribbonTabBar.tabMargin()
                # 把区域顶部扩展到窗口顶部
                contextTitleRect.setTop(RibbonSubElementStyleOpt.widgetBord.top())
                # 绘制
                self.paintContextCategoryTab(p, '', contextTitleRect, clr)

            if self.m_d.ribbonTabBar.currentIndex() in indexs:
                pen = QPen()
                pen.setColor(clr)
                pen.setWidth(1)
                p.setPen(pen)
                p.setBrush(Qt.NoBrush)
                p.drawRect(self.m_d.stackedContainerWidget.geometry())
        p.restore()

        # 显示标题等
        parWindow = self.parentWidget()
        if parWindow:
            start = self.m_d.ribbonTabBar.x() + self.m_d.ribbonTabBar.width()
            width = self.m_d.quickAccessBar.x() - start
            if width > 20:
                titleRegion = QRect(start, RibbonSubElementStyleOpt.widgetBord.top(), width, RibbonSubElementStyleOpt.titleBarHeight)
                self.paintWindowTitle(p, parWindow.windowTitle(), titleRegion)
                self.paintWindowIcon(p, parWindow.windowIcon())

    def resizeStackedContainerWidget(self):
        if self.m_d.stackedContainerWidget.isPopupMode():
            # 弹出模式时，高度
            absPosition = self.mapToGlobal(QPoint(RibbonSubElementStyleOpt.widgetBord.left(), self.m_d.ribbonTabBar.geometry().bottom()+1))
            self.m_d.stackedContainerWidget.setGeometry(
                absPosition.x(),
                absPosition.y(),
                self.width()-RibbonSubElementStyleOpt.widgetBord.left()-RibbonSubElementStyleOpt.widgetBord.right(),
                self.mainBarHeight()-self.m_d.ribbonTabBar.geometry().bottom()-RibbonSubElementStyleOpt.widgetBord.bottom()-1
            )
        else:
            self.m_d.stackedContainerWidget.setGeometry(
                RibbonSubElementStyleOpt.widgetBord.left(),
                self.m_d.ribbonTabBar.geometry().bottom()+1,
                self.width()-RibbonSubElementStyleOpt.widgetBord.left()-RibbonSubElementStyleOpt.widgetBord.right(),
                self.mainBarHeight()-self.m_d.ribbonTabBar.geometry().bottom()-RibbonSubElementStyleOpt.widgetBord.bottom()-1
            )

    def updateContextCategoryManagerData(self):
        """刷新所有ContextCategoryManagerData，这个在单独一个Category删除时调用"""
        for cd in self.m_d.currentShowingContextCategory:
            cd.tabPageIndex.clear()
            for i in range(cd.contextCategory.categoryCount()):
                category = cd.contextCategory.categoryPage(i)
                for j in range(self.m_d.ribbonTabBar.count()):
                    var: _SARibbonTabData = self.m_d.ribbonTabBar.tabData(j)
                    if var:
                        if var.category == category:
                            cd.tabPageIndex.append(j)
                    else:
                        cd.tabPageIndex.append(-1)

    def paintBackground(self, painter: QPainter):
        painter.save()
        pl = self.palette()
        # painter.setPen(Qt.NoPen)
        painter.setPen(RibbonSubElementStyleOpt.tabBarBaseLineColor)
        painter.setBrush(pl.window())   # C++使用的是pl.background()已被弃用，使用pl.window()代替
        painter.drawRect(self.rect().adjusted(0, 0, -1, 0))

        # 在tabbar下绘制一条线
        lineY = self.m_d.ribbonTabBar.geometry().bottom()
        pen = QPen(RibbonSubElementStyleOpt.tabBarBaseLineColor)
        pen.setWidth(1)
        pen.setStyle(Qt.SolidLine)
        painter.setPen(pen)
        painter.drawLine(QPoint(RibbonSubElementStyleOpt.widgetBord.left(), lineY),
                         QPoint(self.width()-RibbonSubElementStyleOpt.widgetBord.right()-1, lineY))
        painter.restore()

    def paintWindowTitle(self, painter: QPainter, title: str, titleRegion: QRect):
        """绘制标题栏"""
        painter.save()
        painter.setPen(RibbonSubElementStyleOpt.titleTextColor)
        painter.drawText(titleRegion, Qt.AlignCenter, title)
        painter.restore()

    def paintWindowIcon(self, painter: QPainter, icon: QIcon):
        """绘制ICon"""
        painter.save()
        if not icon.isNull():
            iconMinSize = RibbonSubElementStyleOpt.titleBarHeight - 6
            icon.paint(painter, RibbonSubElementStyleOpt.widgetBord.left() + 3,
                       RibbonSubElementStyleOpt.widgetBord.top() + 3, iconMinSize, iconMinSize)
            self.m_d.iconRightBorderPosition = RibbonSubElementStyleOpt.widgetBord.left()+iconMinSize
        else:
            self.m_d.iconRightBorderPosition = RibbonSubElementStyleOpt.widgetBord.left()
        painter.restore()

    def paintContextCategoryTab(self, painter: QPainter, title: str, contextRect: QRect, color: QColor):
        """绘制上下文标签的背景"""
        # 首先有5像素的实体粗线位于顶部
        painter.save()
        painter.setPen(Qt.NoPen)
        painter.setBrush(color)
        painter.drawRect(QRect(contextRect.x(), RibbonSubElementStyleOpt.widgetBord.top(), contextRect.width(), 5))

        # 剩下把颜色变亮90%
        gColor = color.lighter(190)     # c++使用的light()已停用，使用ligher()代替
        # 减去之前的5像素
        newContextRect = QRect(contextRect)
        newContextRect -= QMargins(0, 5, 0, 0)
        painter.fillRect(newContextRect, gColor)
        # 只有在office模式下才需要绘制ContextCategory的标题
        if self.isOfficeStyle() and title:
            newContextRect.setBottom(self.m_d.ribbonTabBar.geometry().top())
            painter.setPen(color)
            painter.drawText(newContextRect, Qt.AlignCenter, title)

        painter.restore()

    # 事件
    def paintEvent(self, e):
        if self.isOfficeStyle():
            self.paintInNormalStyle()
        else:
            self.paintInWpsLiteStyle()

    def resizeEvent(self, e):
        if self.isOfficeStyle():
            self.resizeInOfficeStyle()
        else:
            self.resizeInWpsLiteStyle()

    def moveEvent(self, e):
        if self.m_d.stackedContainerWidget and self.m_d.stackedContainerWidget.isPopupMode():
            # 弹出模式时，窗口发生了移动，同步调整StackedContainerWidget的位置
            self.resizeStackedContainerWidget()
        super().moveEvent(e)

    # 槽函数
    def onWindowTitleChanged(self, title: str):
        self.update()

    def onWindowIconChanged(self, icon: QIcon):
        if not icon.isNull():
            iconMinSize = RibbonSubElementStyleOpt.titleBarHeight - 6
            s = icon.actualSize(QSize(iconMinSize, iconMinSize))
            self.m_d.iconRightBorderPosition = RibbonSubElementStyleOpt.widgetBord.left() + s.width()
        self.update()

    def onCategoryWindowTitleChanged(self, title: str):
        w = self.sender()
        if not w:
            return
        for i in range(self.m_d.ribbonTabBar.count()):
            p = self.m_d.ribbonTabBar.tabData(i)
            if w == p.category:
                self.m_d.ribbonTabBar.setTabText(i, title)

    def onStackWidgetHided(self):
        pass

    def onCurrentRibbonTabChanged(self, index: int):
        """标签切换触发槽函数"""
        tabData: _SARibbonTabData = self.m_d.ribbonTabBar.tabData(index)
        if tabData and tabData.category:
            category = tabData.category
            if self.m_d.stackedContainerWidget.currentWidget() != category:
                self.m_d.stackedContainerWidget.setCurrentWidget(category)
            if self.isMinimumMode():
                self.m_d.ribbonTabBar.clearFocus()
                if not self.m_d.stackedContainerWidget.isVisible() and self.m_d.stackedContainerWidget.isPopupMode():
                    # 在stackedContainerWidget弹出前，先给tabbar一个QHoverEvent,让tabbar知道鼠标已经移开
                    ehl = QHoverEvent(QEvent.HoverLeave, self.m_d.ribbonTabBar.mapToGlobal(QCursor.pos()),
                                      self.m_d.ribbonTabBar.mapToGlobal(QCursor.pos()))
                    QApplication.sendEvent(self.m_d.ribbonTabBar, ehl)
                    self.resizeStackedContainerWidget()
                    self.m_d.stackedContainerWidget.setFocus()
                    self.m_d.stackedContainerWidget.exec()
        self.currentRibbonTabChanged.emit(index)

    def onCurrentRibbonTabClicked(self, index: int):
        """此实现必须在eventfilter中传递stackedwidget的QEvent.MouseButtonDblClick事件到tabbar中，否则会导致双击变两次单击"""
        if index != self.m_d.ribbonTabBar.currentIndex():
            # 点击的标签不一致通过changed槽去处理
            return
        if self.isMinimumMode():
            if not self.m_d.stackedContainerWidget.isVisible() and self.m_d.stackedContainerWidget.isPopupMode():
                # 在stackedContainerWidget弹出前，先给tabbar一个QHoverEvent,让tabbar知道鼠标已经移开
                ehl = QHoverEvent(QEvent.HoverLeave, self.m_d.ribbonTabBar.mapToGlobal(QCursor.pos()),
                                  self.m_d.ribbonTabBar.mapToGlobal(QCursor.pos()))
                QApplication.sendEvent(self.m_d.ribbonTabBar, ehl)
                self.resizeStackedContainerWidget()
                self.m_d.stackedContainerWidget.setFocus()
                self.m_d.stackedContainerWidget.exec()

    def onCurrentRibbonTabDoubleClicked(self, index: int):
        """默认情况下双击会切换最小和正常模式"""
        self.setMinimumMode(not self.isMinimumMode())

    def onContextsCategoryPageAdded(self, category: SARibbonCategory):
        # 这里stackedWidget用append，其他地方都应该使用insert
        self.m_d.stackedContainerWidget.addWidget(category)

    def onTabMoved(self, fr: int, to: int):
        # 调整stacked widget的顺序，调整顺序是为了调用categoryPages函数返回的QList<SARibbonCategory *>顺序和tabbar一致
        self.m_d.stackedContainerWidget.moveWidget(fr, to)

    # 信号
    applitionButtonClicked = pyqtSignal()       # 应用按钮点击响应 - 左上角的按钮，通过关联此信号触发应用按钮点击的效果
    currentRibbonTabChanged = pyqtSignal(int)   # 标签页变化触发的信号

    # 枚举
    OfficeStyle = 0x0000            # 类似office 的ribbon风格
    OfficeStyleTwoRow = 0x0100      # 类似office 的ribbon风格 2行工具栏 三行布局模式，默认模式
    WpsLiteStyle = 0x0001           # 类似wps的紧凑风格
    WpsLiteStyleTwoRow = 0x0101     # 类似wps的紧凑风格  2行工具栏
    MinimumRibbonMode = 0x0000
    NormalRibbonMode = 0x0001


if __name__ == '__main__':
    app = QApplication([])
    mainWindow = SARibbonBar()

    mainWindow.setWindowFlags(mainWindow.windowFlags() | Qt.FramelessWindowHint)  # 设置无边框

    mainWindow.setMinimumWidth(500)
    mainWindow.show()
    app.exec()
