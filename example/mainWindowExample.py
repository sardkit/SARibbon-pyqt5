# -*- coding: utf-8 -*-
"""
@Module     test
@Author     ROOT
"""
import sys

from PyQt5.QtCore import Qt, QFile, QIODevice, QXmlStreamWriter, QTextStream
from PyQt5.QtGui import QIcon, QKeySequence, QColor
from PyQt5.QtWidgets import QApplication, QTextEdit, QStatusBar, QButtonGroup, QRadioButton, QToolButton, \
    QCalendarWidget, QSizePolicy, QMenu, QAction, QComboBox, QLineEdit, QCheckBox

from PySARibbon.SAWidgets import SARibbonMenu, SARibbonPannelItem
from PySARibbon.SACustomize import SARibbonActionsManager, SARibbonCustomizeWidget, SARibbonCustomizeDialog
from PySARibbon import SARibbonMainWindow, SARibbonBar, SARibbonCategory, SARibbonPannel, \
    SARibbonGallery, SARibbonButtonGroupWidget


class MainWindow(SARibbonMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.m_contextCategory = None
        self.m_contextCategory2 = None
        self.m_edit = QTextEdit(self)
        self.m_customizeWidget = None
        self.m_actMgr = None
        self.m_actionTagText = 0
        self.m_actionTagWithIcon = 0
        self.loadCustomizeXmlHascall = False

        self.initWidgets()

    def initWidgets(self):
        helper = self.m_framelessHelper
        helper.setRubberBandOnResize(False)
        self.setWindowTitle('Ribbon Test')
        self.setCentralWidget(self.m_edit)
        self.setStatusBar(QStatusBar())

        ribbon = self.ribbonBar()
        ribbon.setTitle('File')
        print(__file__, '[initWidgets]', 'starts.')

        # 添加方法1
        categoryMain = ribbon.addCategoryPage('Main')
        self.createCategoryMain(categoryMain)
        # 添加方法2
        categoryOther = SARibbonCategory()
        categoryOther.setCategoryName('Other')
        categoryOther.setObjectName('categoryOther')
        ribbon.addCategoryPage(categoryOther)
        self.createCategoryOther(categoryOther)

        # 添加第三个标签，用于测试删除
        categoryDelete = SARibbonCategory()
        categoryDelete.setCategoryName('Delete')
        categoryDelete.setObjectName('categoryDelete')
        ribbon.addCategoryPage(categoryDelete)
        self.createCategoryDelete(categoryDelete)

        # 上下文标签
        self.m_contextCategory = ribbon.addContextCategory('context', QColor(), 1)
        contextCategoryPage1 = self.m_contextCategory.addCategoryPage('Page1')
        self.createContextCategoryPage1(contextCategoryPage1)
        contextCategoryPage2 = self.m_contextCategory.addCategoryPage('Page2')
        self.createContextCategoryPage2(contextCategoryPage2)
        self.m_contextCategory2 = ribbon.addContextCategory('context2', QColor(), 2)
        self.m_contextCategory2.addCategoryPage('context2 Page1')
        self.m_contextCategory2.addCategoryPage('context2 Page2')

        quickAccessBar = ribbon.quickAccessBar()
        quickAccessBar.addAction(QAction(QIcon("resource/icon/chartDataManager.png"), 'action1', self))
        quickAccessBar.addAction(QAction(QIcon("resource/icon/figureIcon.png"), 'action2', self))
        quickAccessBar.addSeparator()
        quickAccessBar.addAction(QAction(QIcon("resource/icon/information.png"), 'action3', self))
        m = QMenu('action menu', self)
        m.setIcon(QIcon('resource/icon/inRangDataRemove.png'))
        m.addAction(QIcon('resource/icon/506355.png'), '1')
        m.addAction(QIcon('resource/icon/506356.png'), '2')
        m.addAction(QIcon('resource/icon/506357.png'), '3')
        m.addAction(QIcon('resource/icon/506358.png'), '4')
        m.addAction(QIcon('resource/icon/506359.png'), '5')
        quickAccessBar.addMenu(m)

        self.addSomeOtherAction()

        quickAccessBar.addSeparator()
        customize = QAction(QIcon("resource/icon/layerBarChart.png"), 'customize', self)
        customize.triggered.connect(self.onActionCustomizeTriggered)
        quickAccessBar.addAction(customize)
        customize2 = QAction(QIcon("resource/icon/openProject.png"), 'customize', self)
        customize2.triggered.connect(self.onActionCustomizeAndSaveTriggered)
        quickAccessBar.addAction(customize2)

        rightBar = ribbon.activeTabBarRightButtonGroup()
        atc = rightBar.addAction('Help', QIcon('resource/icon/help.png'))
        atc.triggered.connect(lambda on: self.m_edit.append('Help Button triggered'))

        self.setMinimumWidth(500)
        self.showMaximized()
        self.setWindowIcon(QIcon('resource/icon/icon2.png'))

    def createCategoryMain(self, page: SARibbonCategory):
        pannel = page.addPannel('Panel 1')
        # act 1
        act = QAction(self)
        act.setObjectName('Save')
        act.setText('保存')
        act.setToolTip('Save')
        act.setIcon(QIcon('resource/icon/save.png'))
        act.setShortcut(QKeySequence('Ctrl+S'))
        pannel.addLargeAction(act)
        act.triggered.connect(lambda b: self.m_edit.append('action clicked'))
        # act 2
        act = QAction(self)
        act.setObjectName('Hide')
        act.setText('展示/隐藏 ribbon')
        act.setIcon(QIcon('resource/icon/filter.png'))
        act.setCheckable(True)
        pannel.addSmallAction(act)
        act.triggered.connect(lambda b: self.ribbonBar().setMinimumMode(b))
        # act 3
        act = QAction(self)
        act.setObjectName('Show')
        act.setText('显示操作ribbon按钮')
        act.setIcon(QIcon('resource/icon/information.png'))
        act.setCheckable(True)
        pannel.addSmallAction(act)
        act.triggered.connect(lambda b: self.ribbonBar().showMinimumModeButton(b))
        act.trigger()

        self.btnGroup = QButtonGroup(page)
        r = QRadioButton('use office style', self)
        r.setObjectName('use office style')
        r.setChecked(True)
        self.btnGroup.addButton(r, SARibbonBar.OfficeStyle)
        pannel.addSmallWidget(r)
        r = QRadioButton('use wps style', self)
        r.setObjectName('use wps style')
        r.setChecked(False)
        self.btnGroup.addButton(r, SARibbonBar.WpsLiteStyle)
        pannel.addSmallWidget(r)
        r = QRadioButton('use office 2row style', self)
        r.setObjectName('use office 2row style')
        r.setChecked(False)
        self.btnGroup.addButton(r, SARibbonBar.OfficeStyleTwoRow)
        pannel.addSmallWidget(r)
        r = QRadioButton('use wps 2row style', self)
        r.setObjectName('use wps 2row style')
        r.setChecked(False)
        self.btnGroup.addButton(r, SARibbonBar.WpsLiteStyleTwoRow)
        pannel.addSmallWidget(r)
        self.btnGroup.buttonClicked[int].connect(self.onStyleClicked)

        pannel.addSeparator()   # 分割线

        menu = SARibbonMenu(self)
        a = menu.addAction(QIcon('resource/icon/folder.png'), 'item 1')
        a.setObjectName('item 1')
        a = menu.addAction(QIcon('resource/icon/folder.png'), 'item 2')
        a.setObjectName('item 2')
        a = menu.addAction(QIcon('resource/icon/folder.png'), 'item 3')
        a.setObjectName('item 3')
        a = menu.addAction(QIcon('resource/icon/folder.png'), 'item 4')
        a.setObjectName('item 4')
        a = menu.addAction(QIcon('resource/icon/folder.png'), 'item 5')
        a.setObjectName('item 5')
        a = menu.addAction(QIcon('resource/icon/folder.png'), 'item 6')
        a.setObjectName('item 6')
        a = menu.addAction(QIcon('resource/icon/folder.png'), 'item 7')
        a.setObjectName('item 7')
        a = menu.addAction(QIcon('resource/icon/folder.png'), 'item 8')
        a.setObjectName('item 8')
        a = menu.addAction(QIcon('resource/icon/folder.png'), 'item 9')
        a.setObjectName('item 9')
        a = menu.addAction(QIcon('resource/icon/folder.png'), 'item 10')
        a.setObjectName('item 10')

        act = QAction(QIcon('resource/icon/folder.png'), 'test 1', self)
        act.setObjectName('test 1')
        act.setMenu(menu)
        btn = pannel.addSmallAction(act)
        btn.setPopupMode(QToolButton.MenuButtonPopup)
        act = QAction(QIcon('resource/icon/folder.png'), 'test 2', self)
        act.setObjectName('test 2')
        act.setMenu(menu)
        btn = pannel.addSmallAction(act)
        btn.setPopupMode(QToolButton.InstantPopup)

        pannel.addSeparator()  # 分割线

        act = QAction(QIcon('resource/icon/folder.png'), 'DelayedPopup', self)
        act.setObjectName('DelayedPopup')
        act.setMenu(menu)
        act.triggered.connect(self.onDelayedPopupCheckabletriggered)
        btn = pannel.addLargeAction(act)
        btn.setObjectName('SA_DelayedPopup')
        btn.setPopupMode(QToolButton.DelayedPopup)
        act = QAction(QIcon('resource/icon/folder.png'), 'MenuButtonPopup', self)
        act.setObjectName('MenuButtonPopup')
        act.setMenu(menu)
        act.triggered.connect(self.onMenuButtonPopupCheckabletriggered)
        btn = pannel.addLargeAction(act)
        btn.setObjectName('SA_MenuButtonPopup')
        btn.setPopupMode(QToolButton.MenuButtonPopup)
        act = QAction(QIcon('resource/icon/Graph-add.png'), 'InstantPopup', self)
        act.setObjectName('InstantPopup')
        act.setMenu(menu)
        act.triggered.connect(self.onInstantPopupCheckabletriggered)
        btn = pannel.addLargeAction(act)
        btn.setObjectName('SA_InstantPopup')
        btn.setPopupMode(QToolButton.InstantPopup)
        act = QAction(QIcon('resource/icon/folder.png'), 'DelayedPopup checkable', self)
        act.setObjectName('DelayedPopup checkable')
        act.setCheckable(True)
        act.setMenu(menu)
        act.triggered.connect(self.onDelayedPopupCheckableTest)
        btn = pannel.addLargeAction(act)
        btn.setObjectName('SA_DelayedPopup checkable')
        btn.setCheckable(True)
        btn.setPopupMode(QToolButton.DelayedPopup)
        act = QAction(QIcon('resource/icon/folder.png'), 'MenuButtonPopup checkable', self)
        act.setObjectName('MenuButtonPopup checkable')
        act.setCheckable(True)
        act.setMenu(menu)
        act.triggered.connect(self.onMenuButtonPopupCheckableTest)
        btn = pannel.addLargeAction(act)
        btn.setObjectName('SA_MenuButtonPopup checkable')
        btn.setCheckable(True)
        btn.setPopupMode(QToolButton.MenuButtonPopup)

        pannel2 = page.addPannel('pannel 2')

        def tmp_func1(on: bool):
            if on:
                self.ribbonBar().showContextCategory(self.m_contextCategory)
            else:
                self.ribbonBar().hideContextCategory(self.m_contextCategory)
        act = QAction(self)
        act.setObjectName('show Context')
        act.setText('show Context')
        act.setIcon(QIcon('resource/icon/Graph-add.png'))
        act.setCheckable(True)
        act.triggered.connect(tmp_func1)
        btn = pannel2.addLargeAction(act)
        btn.setCheckable(True)

        def tmp_func2(on: bool):
            if self.m_contextCategory:
                self.ribbonBar().destroyContextCategory(self.m_contextCategory)
                self.m_contextCategory = None
                act.setDisabled(True)
        act2 = QAction(self)
        act2.setObjectName('delete Context')
        act2.setText('delete Context')
        act2.setIcon(QIcon('resource/icon/529398.png'))
        act2.setCheckable(True)
        act2.triggered.connect(tmp_func2)
        pannel2.addLargeAction(act2)

        act = QAction(self)
        act.setObjectName('unactive')
        act.setText('unactive')
        act.setIcon(QIcon('resource/icon/Graph-add.png'))
        act.setCheckable(True)
        act.setMenu(menu)
        btn = pannel2.addLargeAction(act)
        btn.setCheckable(True)
        btn.setPopupMode(QToolButton.InstantPopup)
        btn.setEnabled(False)

        # QComboBox, QLineEdit, QCheckBox
        com = QComboBox(self)
        com.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        com.setWindowTitle("ComboBox Editable")
        for i in range(20):
            com.addItem("item: {0}".format(i + 1))
        com.setEditable(True)
        pannel2.addSmallWidget(com)

        com2 = QComboBox(self)
        com2.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        com2.setWindowTitle("ComboBox")
        for i in range(20):
            com2.addItem("item: {0}".format(i + 1))
        pannel2.addSmallWidget(com2)

        lineEdit = QLineEdit(self)
        lineEdit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        lineEdit.setWindowTitle("Line Edit")
        lineEdit.setText("Test LineEdit")
        pannel2.addSmallWidget(lineEdit)

        checkBox = QCheckBox(self)
        checkBox.setText("checkBox")
        pannel2.addSmallWidget(checkBox)

        pannel2.addSeparator()
        calendarWidget = QCalendarWidget(self)
        calendarWidget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        calendarWidget.setObjectName('CalendarWidget')
        pannel2.addLargeWidget(calendarWidget)
        pannel2.setExpanding()
        optAct = QAction(self)
        optAct.toggled.connect(lambda on: self.m_edit.append('OptionAction triggered'))
        pannel2.addOptionAction(optAct)
        pannel2.setVisible(True)

    def createCategoryOther(self, page: SARibbonCategory):
        pannel = SARibbonPannel('Pannel One')
        page.addPannel(pannel)

        btnGroup = SARibbonButtonGroupWidget(pannel)
        btnGroup.addAction(QAction(QIcon("resource/icon/figureIcon.png"), 'test1', self))
        btnGroup.addAction(QAction(QIcon("resource/icon/information.png"), 'test2', self))
        btnGroup.addAction(QAction(QIcon("resource/icon/chartDataManager.png"), 'test3', self))
        btnGroup.addAction(QAction(QIcon("resource/icon/inRangDataRemove.png"), 'test4', self))
        pannel.addLargeWidget(btnGroup)

        pannel.addSeparator()

        menu = SARibbonMenu(self)
        item = menu.addAction(QIcon("resource/icon/folder.png"), 'menu item test')
        item.setObjectName('menu item test')
        menu.addAction(QIcon("resource/icon/folder.png"), '1')
        menu.addAction(QIcon("resource/icon/folder.png"), '2')
        menu.addAction(QIcon("resource/icon/folder.png"), '3')
        menu.addAction(QIcon("resource/icon/folder.png"), '4')
        menu.addAction(QIcon("resource/icon/folder.png"), '5')
        menu.addAction(QIcon("resource/icon/folder.png"), '6')
        menu.addAction(QIcon("resource/icon/folder.png"), '7')
        menu.addAction(QIcon("resource/icon/folder.png"), '8')
        menu.addAction(QIcon("resource/icon/folder.png"), '9')

        btn = pannel.addLargeAction(QAction(item))
        btn.setText('un format icon')
        btn.setIcon(QIcon('resource/icon/folder.png'))
        btn.setFixedHeight(78)
        btn.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        btn.setPopupMode(QToolButton.DelayedPopup)
        btn.setMenu(menu)
        btn = pannel.addLargeAction(QAction(item))
        btn.setText('change page test')
        btn.setIcon(QIcon('resource/icon/folder.png'))
        btn.setFixedHeight(78)
        btn.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        btn.setPopupMode(QToolButton.MenuButtonPopup)
        btn.setMenu(menu)
        btn = pannel.addLargeAction(QAction(item))
        btn.setText('LargeBtn')
        btn.setIcon(QIcon('resource/icon/folder.png'))
        btn.setFixedHeight(78)
        btn.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        btn.setPopupMode(QToolButton.InstantPopup)
        btn.setMenu(menu)

        optAct = QAction(self)
        optAct.setObjectName('Debug')
        pannel.addOptionAction(optAct)
        pannel.setObjectName('Debug')

        pannel.addSeparator()
        appAct = QAction(QIcon("resource/icon/icon2.png"), 'no application button and very long word test', self)
        appAct.setObjectName('no application button and very long word test')
        appAct.setCheckable(True)

        def tmp_func1(on: bool):
            sAppBtn = self.ribbonBar().applicationButton()
            if on:
                sAppBtn.setText('TestFile')
            else:
                sAppBtn.setText('File')
        appAct.toggled.connect(tmp_func1)
        btn = pannel.addLargeAction(appAct)
        btn.setObjectName('ApplicationButtonTest')

        def tmp_func2(on: bool):
            fileName = 'resource/default.qss' if on else 'resource/office2013.qss'
            f = QFile(fileName)
            if not f.open(QIODevice.ReadWrite):
                print('error, read file error', fileName)
                return
            qss = str(f.readAll(), encoding='utf-8')
            self.ribbonBar().setStyleSheet(qss)
        useqss = QAction(QIcon("resource/icon/icon2.png"), 'use qss', self)
        useqss.setObjectName('use qss')
        useqss.setCheckable(True)
        useqss.triggered.connect(tmp_func2)
        pannel.addLargeAction(useqss)

        # 定制化 TODO 待验证
        def tmp_func3(on: bool):
            if not self.loadCustomizeXmlHascall:
                self.loadCustomizeXmlHascall = SARibbonCustomizeWidget.sa_apply_customize_from_xml_file("customize.xml", self, self.m_actMgr)
        loadCustomizeXmlFile = QAction(QIcon("resource/icon/506405.png"), "load customize from xml file", self)
        loadCustomizeXmlFile.triggered.connect(tmp_func3)
        pannel.addLargeAction(loadCustomizeXmlFile)

        normalButton = QAction(QIcon("resource/icon/506354.png"), '正常模式', self)
        normalButton.setObjectName('normalButton')
        pannel.addLargeAction(normalButton)
        normalButton.triggered.connect(lambda on: self.updateWindowFlag(self.windowFlags() | Qt.WindowMinMaxButtonsHint
                                                                        | Qt.WindowCloseButtonHint))
        noneButton = QAction(QIcon("resource/icon/506359.png"), '无按钮模式', self)
        noneButton.setObjectName('noneButton')
        pannel.addLargeAction(noneButton)
        noneButton.triggered.connect(lambda on: self.updateWindowFlag(self.windowFlags() & ~Qt.WindowMinMaxButtonsHint
                                                                      & ~Qt.WindowCloseButtonHint))
        changename = QAction(QIcon("resource/icon/529398.png"), '改变pannel名字', self)
        changename.setObjectName('changename')
        pannel.addLargeAction(changename)
        changename.triggered.connect(lambda on: pannel.setPannelName('变、变、变'))

        pannel.addSeparator()
        gallery = SARibbonGallery(pannel)
        group = gallery.addGalleryGroup()
        for i in range(10):
            group.addItem(str(i+1), QIcon('resource/icon/folder.png'))
        pannel.addGallery(gallery)

        pannel2 = SARibbonPannel('ContextCategory')
        page.addPannel(pannel2)
        a1 = QAction(QIcon("resource/icon/529398.png"), 'Context Category 1', self)
        a1.setCheckable(True)
        a1.triggered.connect(lambda on: self.ribbonBar().setContextCategoryVisible(self.m_contextCategory, on))
        pannel2.addLargeAction(a1)
        a2 = QAction(QIcon("resource/icon/529398.png"), 'Context Category 2', self)
        a2.setCheckable(True)
        a2.triggered.connect(lambda on: self.ribbonBar().setContextCategoryVisible(self.m_contextCategory2, on))
        pannel2.addLargeAction(a2)

    def createCategoryDelete(self, page: SARibbonCategory):
        pannel1 = page.addPannel('pannel 1')
        pannel2 = page.addPannel('pannel 2')
        act = QAction(self)
        act.setText('删除Pannel2')
        act.setIcon(QIcon('resource/icon/506356.png'))
        pannel1.addLargeAction(act)
        act.triggered.connect(lambda: page.removePannel(pannel2))

        act = QAction(self)
        act.setText('删除本页')
        act.setIcon(QIcon('resource/icon/506357.png'))
        pannel2.addLargeAction(act)

        def tmp_func(on: bool):
            self.ribbonBar().removeCategory(page)
            page.hide()
            page.deleteLater()
            act.setDisabled(True)
        act.triggered.connect(tmp_func)

    def createContextCategoryPage1(self, page: SARibbonCategory):
        pannel = page.addPannel('显示隐藏操作')
        act = QAction(QIcon('resource/icon/530150.png'), '隐藏pannel', self)
        act.setCheckable(True)
        pannel.addLargeAction(act)

        actd = QAction(QIcon('resource/icon/529398.png'), 'Disable', self)
        actd.setDisabled(True)
        pannel.addLargeAction(actd)
        actd.triggered.connect(lambda on: actd.setDisabled(True) or actd.setText('Disable'))

        def tmp_func1(on: bool):
            actd.setEnabled(True)
            actd.setText('Enabled')
        act1 = QAction(QIcon('resource/icon/529398.png'), '解锁左边的按钮', self)
        act1.setShortcut('Ctrl+E')
        act1.triggered.connect(tmp_func1)
        pannel.addLargeAction(act1)

        act = QAction(QIcon('resource/icon/530767.png'), 'setText测试\r\nCtrl+D', self)
        act.setCheckable(True)
        act.setShortcut('Ctrl+D')
        pannel.addLargeAction(act)
        act.toggled.connect(lambda on: act.setText('点击了') if on else act.setText('setText测试'))

        # 隐藏pannel
        act1 = QAction(QIcon('resource/icon/arror.png'), '显示旁边的pannel', self)
        act1.setCheckable(True)
        pannel.addLargeAction(act1)

        pannel2 = page.addPannel('用于隐藏显示的测试')
        pannel2.addLargeAction(act)

        def tmp_func2(on: bool):
            pannel2.setVisible(not on)
            text = '隐藏旁边的pannel' if on else '显示旁边的pannel'
            act1.setText(text)
            self.ribbonBar().repaint()
        act1.toggled.connect(tmp_func2)

        pannel3 = page.addPannel('action隐藏显示的测试')

        act1 = QAction(QIcon('resource/icon/arror.png'), '隐藏action2', self)
        act1.setCheckable(True)
        act1.setChecked(True)
        pannel3.addLargeAction(act1)
        act2 = QAction(QIcon('resource/icon/arror.png'), 'action 2', self)
        pannel3.addSmallAction(act2)
        act3 = QAction(QIcon('resource/icon/arror.png'), 'action 3', self)
        pannel3.addSmallAction(act3)
        act4 = QAction(QIcon('resource/icon/arror.png'), 'action 4', self)
        pannel3.addSmallAction(act4)

        def tmp_func3(on: bool):
            text = '隐藏action2' if on else '显示action2'
            act2.setVisible(on)
            act1.setText(text)
        act1.triggered.connect(tmp_func3)

    def createContextCategoryPage2(self, page: SARibbonCategory):
        pannel = page.addPannel('删除CategoryPage测试')

        def tmp_func(on: bool):
            self.ribbonBar().removeCategory(page)
            page.deleteLater()
        act = QAction(QIcon('resource/icon/529398.png'), '删除本页', self)
        act.triggered.connect(tmp_func)
        pannel.addLargeAction(act)

        pannel2 = page.addPannel('特殊布局')

        pannel2.addAction('Large', QIcon('resource/icon/530767.png'), QToolButton.InstantPopup, SARibbonPannelItem.RPLarge)
        pannel2.addAction('Small', QIcon('resource/icon/530767.png'), QToolButton.InstantPopup, SARibbonPannelItem.RPSmall)
        pannel2.addAction('Small', QIcon('resource/icon/530767.png'), QToolButton.InstantPopup, SARibbonPannelItem.RPSmall)
        pannel2.addSeparator()
        pannel2.addAction('Small', QIcon('resource/icon/530767.png'), QToolButton.InstantPopup, SARibbonPannelItem.RPSmall)
        pannel2.addAction('Small', QIcon('resource/icon/530767.png'), QToolButton.InstantPopup, SARibbonPannelItem.RPSmall)
        pannel2.addAction('Small', QIcon('resource/icon/530767.png'), QToolButton.InstantPopup, SARibbonPannelItem.RPSmall)
        pannel2.addAction('Small', QIcon('resource/icon/530767.png'), QToolButton.InstantPopup, SARibbonPannelItem.RPSmall)
        pannel2.addSeparator()
        pannel2.addAction('Large', QIcon('resource/icon/530767.png'), QToolButton.InstantPopup, SARibbonPannelItem.RPLarge)
        pannel2.addAction('Medium', QIcon('resource/icon/530767.png'), QToolButton.InstantPopup, SARibbonPannelItem.RPMedium)
        pannel2.addAction('Medium', QIcon('resource/icon/530767.png'), QToolButton.InstantPopup, SARibbonPannelItem.RPMedium)
        pannel2.addAction('Small', QIcon('resource/icon/530767.png'), QToolButton.InstantPopup, SARibbonPannelItem.RPSmall)
        pannel2.addAction('Medium', QIcon('resource/icon/530767.png'), QToolButton.InstantPopup, SARibbonPannelItem.RPMedium)
        pannel2.addAction('Large', QIcon('resource/icon/530767.png'), QToolButton.InstantPopup, SARibbonPannelItem.RPLarge)
        pannel2.addAction('Medium', QIcon('resource/icon/530767.png'), QToolButton.InstantPopup, SARibbonPannelItem.RPMedium)
        pannel2.addAction('Medium', QIcon('resource/icon/530767.png'), QToolButton.InstantPopup, SARibbonPannelItem.RPMedium)
        pannel2.addAction('Large', QIcon('resource/icon/530767.png'), QToolButton.InstantPopup, SARibbonPannelItem.RPLarge)
        pannel2.addSeparator()
        pannel2.addAction('Medium', QIcon('resource/icon/530767.png'), QToolButton.InstantPopup, SARibbonPannelItem.RPMedium)
        pannel2.addAction('Large', QIcon('resource/icon/530767.png'), QToolButton.InstantPopup, SARibbonPannelItem.RPLarge)
        pannel2.addAction('Medium', QIcon('resource/icon/530767.png'), QToolButton.InstantPopup, SARibbonPannelItem.RPMedium)
        pannel2.addAction('Large', QIcon('resource/icon/530767.png'), QToolButton.InstantPopup, SARibbonPannelItem.RPLarge)

    def addSomeOtherAction(self):
        # 添加其他的action，这些action并不在ribbon管理范围，主要用于SARibbonCustomizeWidget自定义用
        acttext1 = QAction('纯文本 acttext1', self)
        acttext2 = QAction('纯文本 acttext2', self)
        acttext3 = QAction('纯文本 acttext3', self)
        acttext4 = QAction('纯文本 acttext4', self)
        acttext5 = QAction('纯文本 acttext5', self)

        actIcon1 = QAction(QIcon("resource/icon/506353.png"), '带图标 actIcon1', self)

        self.m_actionTagText = SARibbonActionsManager.UserDefineActionTag + 1
        self.m_actionTagWithIcon = SARibbonActionsManager.UserDefineActionTag + 2

        self.m_actMgr = SARibbonActionsManager(self)  # 申明过程已经自动注册所有action

        # 以下注册特别的action
        # self.m_actMgr.registeAction(acttext1, SARibbonActionsManager.CommonlyUsedActionTag)
        # self.m_actMgr.registeAction(acttext2, SARibbonActionsManager.CommonlyUsedActionTag)
        # self.m_actMgr.registeAction(acttext3, SARibbonActionsManager.CommonlyUsedActionTag)
        # self.m_actMgr.registeAction(acttext4, SARibbonActionsManager.CommonlyUsedActionTag)
        # self.m_actMgr.registeAction(acttext5, SARibbonActionsManager.CommonlyUsedActionTag)
        # self.m_actMgr.registeAction(actIcon1, SARibbonActionsManager.CommonlyUsedActionTag)

        self.m_actMgr.registeAction(acttext1, self.m_actionTagText)
        self.m_actMgr.registeAction(acttext2, self.m_actionTagText)
        self.m_actMgr.registeAction(acttext3, self.m_actionTagText)
        self.m_actMgr.registeAction(acttext4, self.m_actionTagText)
        self.m_actMgr.registeAction(acttext5, self.m_actionTagText)
        self.m_actMgr.registeAction(actIcon1, self.m_actionTagWithIcon)

        self.m_actMgr.setTagName(SARibbonActionsManager.CommonlyUsedActionTag, "in common use")  #
        self.m_actMgr.setTagName(self.m_actionTagText, "no icon action")
        self.m_actMgr.setTagName(self.m_actionTagWithIcon, "have icon action")

    # 槽函数
    def onShowContextCategory(self, on: bool):
        self.ribbonBar().setContextCategoryVisible(self.m_contextCategory, on)

    def onStyleClicked(self, sty: int):
        self.ribbonBar().setRibbonStyle(sty)

    def onActionCustomizeTriggered(self, b: bool) -> None:
        # TODO 待验证
        if not self.m_customizeWidget:
            print('Test onActionCustomizeTriggered -----0')
            self.m_customizeWidget = SARibbonCustomizeWidget(self, self, Qt.WindowMinMaxButtonsHint | Qt.WindowCloseButtonHint | Qt.Dialog)
            print('Test onActionCustomizeTriggered -----1')
            self.m_customizeWidget.setWindowModality(Qt.ApplicationModal)  # 设置阻塞类型
            self.m_customizeWidget.setAttribute(Qt.WA_ShowModal, True)  # 属性设置 True:模态 False:非模态
            self.m_customizeWidget.setupActionsManager(self.m_actMgr)
            print('Test onActionCustomizeTriggered -----2')

        self.m_customizeWidget.show()
        self.m_customizeWidget.applys()

    def onActionCustomizeAndSaveTriggered(self, b: bool) -> None:
        # TODO 待验证
        dlg = SARibbonCustomizeDialog(self)
        dlg.setupActionsManager(self.m_actMgr)
        dlg.fromXml("customize.xml")
        if SARibbonCustomizeDialog.Accepted == dlg.exec():
            dlg.applys()
            string: bytes = bytes()
            xml = QXmlStreamWriter(string)
            xml.setAutoFormatting(True)
            xml.setAutoFormattingIndent(2)
            xml.setCodec("utf-8")

            xml.writeStartDocument()
            isok: bool = dlg.toXml(xml)
            xml.writeEndDocument()
            if isok:
                f = QFile("customize.xml")
                if f.open(QIODevice.ReadWrite | QIODevice.Text | QIODevice.Truncate):
                    s = QTextStream(f)
                    s.setCodec("utf-8")
                    s << string
                    s.flush()

                self.m_edit.append("write xml:")
                self.m_edit.append(string.decode('utf-8'))

    def onMenuButtonPopupCheckableTest(self, on: bool):
        self.m_edit.append('MenuButtonPopupCheckableTest : %s' % on)

    def onInstantPopupCheckableTest(self, on: bool):
        self.m_edit.append('InstantPopupCheckableTest : %s' % on)

    def onDelayedPopupCheckableTest(self, on: bool):
        self.m_edit.append('DelayedPopupCheckableTest : %s' % on)

    def onMenuButtonPopupCheckabletriggered(self, on: bool):
        self.m_edit.append('MenuButtonPopupCheckabletriggered : %s' % on)

    def onInstantPopupCheckabletriggered(self, on: bool):
        self.m_edit.append('InstantPopupCheckabletriggered : %s' % on)

    def onDelayedPopupCheckabletriggered(self, on: bool):
        self.m_edit.append('DelayedPopupCheckabletriggered : %s' % on)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    # 设置默认字体
    font = app.font()
    font.setFamily('微软雅黑')
    app.setFont(font)

    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec())
