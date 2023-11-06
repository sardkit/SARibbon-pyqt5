# -*- coding: utf-8 -*-
"""
@Module     SARibbonCustomizeWidget
@Author     ROOT

@brief 用于管理SARibbon的所有Action

@note SARibbonActionsManager维护着两个表，一个是tag（标签）对应的Action list，
一个是所有接受SARibbonActionsManager管理的action list。

SARibbonActionsManager的标签对应一组actions，每个标签对应的action可以重复出现，
但SARibbonActionsManager维护的action list里只有一份action，不会重复出现。

tag用于对action list分组，每个tag的实体名字通过@ref setTagName 进行设置，在语言变化时需要及时调用
setTagName设置新的标签对应的文本。

SARibbonActionsManager默认预设了6个常用标签见@ref SARibbonActionsManager.ActionTag ，用户自定义标签需要在
SARibbonActionsManager.UserDefineActionTag值的基础上进行累加。

@ref filter （等同@ref actions ）函数用于提取标签管理的action list，@ref allActions 函数返回SARibbonActionsManager
管理的所有标签。

通过@ref autoRegisteActions 函数可以快速的建立action的管理，此函数会遍历@ref SARibbonMainWindow 下的所有子object，
同时遍历SARibbonMainWindow下所有@ref SARibbonPannel 添加的action,并给予Category建立tag，正常使用用户仅需关注此autoRegisteActions函数即可
"""
from typing import Any
from PyQt5.QtCore import Qt, QObject, QAbstractListModel, QModelIndex, pyqtSignal
from PyQt5.QtWidgets import QAction, QWidget


class SARibbonActionsManagerPrivate:
    def __init__(self, p:QObject):
        self.mParent = p

        self.mTagToActions: dict = dict()   # tag : dict
        self.mTagToName: dict = dict()      # tag对应的名字
        self.mKeyToAction: dict = dict()    # key对应action
        self.mActionToKey: dict = dict()    # action对应key
        self.mTagToCategory: dict = dict()  # 仅仅在autoRegisteActions函数会有用
        self.mSale: int = 0                 # 用于生成固定的id，在用户不主动设置key时，id基于msale生成

    def clear(self) -> None:
        self.mTagToActions.clear()
        self.mTagToName.clear()
        self.mKeyToAction.clear()
        self.mActionToKey.clear()
        self.mTagToCategory.clear()
        self.mSale = 0


class SARibbonActionsManager(QObject):
    """
       @brief 定义action的标签
    """
    UnknowActionTag                 = 0x00
    CommonlyUsedActionTag           = 0x01
    NotInFunctionalAreaActionTag    = 0x02
    AutoCategoryDistinguishBeginTag = 0x1000
    AutoCategoryDistinguishEndTag   = 0x2000
    NotInRibbonCategoryTag          = 0x2001
    UserDefineActionTag             = 0x8000

    """标签变化触发的信号，变化包括新增和删除"""
    actionTagChanged = pyqtSignal(int, bool)

    def __init__(self, p:QObject):
        super().__init__(p)
        self.QObject = p
        self.m_d = SARibbonActionsManagerPrivate(self)
        self.autoRegisteActions(p)

    def setTagName(self, tag:int, name:str) -> None:
        """设置tag对应的名字"""
        self.m_d.mTagToName[tag] = name

    def tagName(self, tag:int) -> str:
        """获取tag对应的名字"""
        return self.m_d.mTagToName.get(tag, "")

    def removeTag(self, tag:int) -> None:
        """移除tag，注意，这个函数非常耗时"""
        oldacts: list = self.actions(tag)

        # 开始移除
        self.m_d.mTagToActions.pop(tag)
        self.m_d.mTagToName.pop(tag)
        # 开始查找需要移出总表的action
        needRemoveAct: list = list()
        total: list = list()

        for i in self.m_d.mTagToActions:
            total.append(i)

        for a in oldacts:
            if not a in total:
                needRemoveAct.append(a)

        # 从总表移除action
        for a in needRemoveAct:
            i = self.m_d.mActionToKey.get(a, '')
            if i:
                self.m_d.mKeyToAction.pop(i)
                self.m_d.mActionToKey.pop(a)

    def registeAction(self, act:QAction, tag:int, key:str = '', enableEmit:bool = True) -> bool:
        """注册action"""
        if not act:
            return False

        k: str = key
        if not k:
            k = "id_{0}_{1}".format(self.m_d.mSale, act.objectName())
            self.m_d.mSale += 1

        if k in self.m_d.mKeyToAction:
            print("key: ", k, "have been exist, can you set key in an unique value when use SARibbonActionsManager.registeAction")
            return False

        self.m_d.mKeyToAction[k] = act
        self.m_d.mActionToKey[act] = k
        # 记录tag 对 action
        isneedemit: bool = tag not in self.m_d.mTagToActions  # 记录是否需要发射信号
        if isneedemit:
            self.m_d.mTagToActions[tag] = list()
        self.m_d.mTagToActions[tag].append(act)
        # 绑定槽
        act.destroyed.connect(self.onActionDestroyed)
        if isneedemit and enableEmit:
            # 说明新增tag
            self.actionTagChanged.emit(tag, False)

        return True

    def unregisteAction(self, act:QAction, enableEmit:bool = True) -> None:
        """取消action的注册"""
        if act is None:
            return

        # 绑定槽
        act.destroyed.disconnect(self.onActionDestroyed)
        self.removeAction(act, enableEmit)

    def filter(self, tag:int) -> list:
        """过滤得到actions对应的引用，实际是一个迭代器"""
        return self.actions(tag)

    def actions(self, tag:int) -> list:
        """通过tag筛选出系列action"""
        return self.m_d.mTagToActions.get(tag, list())

    def actionTags(self) -> list:
        """获取所有的标签"""
        return list(self.m_d.mTagToActions.keys())

    def action(self, key:str) -> QAction:
        """通过key获取action"""
        return self.m_d.mKeyToAction.get(key, None)

    def key(self, act:QAction) -> str:
        """通过action找到key"""
        return self.m_d.mActionToKey.get(act, '')

    def count(self) -> int:
        """返回所有管理的action数"""
        return len(self.m_d.mKeyToAction)

    def allActions(self) -> list:
        """返回所有管理的actions"""
        return list(self.m_d.mKeyToAction.values())

    def autoRegisteActions(self, w:QObject) -> dict:
        """自动加载action,返回tag对应的Category指针"""
        res: dict = dict()
        # 先遍历SARibbonMainWindow下的所有子对象，把所有action找到
        mainwindowActions: set = set()

        for o in w.children():
            if isinstance(o, QAction) and o.objectName():
                mainwindowActions.add(o)

        # 开始遍历每个category，加入action
        bar = w.ribbonBar()
        # 非ribbon模式，直接退出
        if not bar:
            return res

        categoryActions: set = set()
        categorys: list = bar.categoryPages()
        tag: int = self.AutoCategoryDistinguishBeginTag

        for c in categorys:
            pannels: list = c.pannelList()
            for p in pannels:
                categoryActions.union(self.autoRegisteWidgetActions(p, tag, False))
            self.setTagName(tag, c.windowTitle())
            res[tag] = c
            tag += 1

        # 找到不在功能区的actions
        notincategory: set = mainwindowActions - categoryActions
        for a in notincategory:
            if a.objectName():
                self.registeAction(a, self.NotInRibbonCategoryTag, a.objectName(), False)

        if len(notincategory) > 0:
            self.setTagName(self.NotInRibbonCategoryTag, "not in ribbon")

        for i in res.values():
            i.windowTitleChanged.connect(self.onCategoryTitleChanged)

        self.m_d.mTagToCategory = res
        return res

    def autoRegisteWidgetActions(self, w:QWidget, tag:int, enableEmit:bool = False) -> set:
        """自动加载widget下的actions函数返回的action,返回加载的数量，这些"""
        res: set = set()
        was: list = w.actions()
        for a in was:
            if a in res or not a.objectName():
                # 重复内容不重复加入，没有object name不加入
                continue
            if self.registeAction(a, tag, a.objectName(), enableEmit):
                res.add(a)

        return res

    def search(self, text:str) -> list:
        """根据标题查找action"""
        res: list = list()
        if not text:
            return res

        kws: list = text.split(" ")
        if not kws:
            kws.append(text)

        for k in kws:
            for i in self.m_d.mActionToKey.keys():
                if i.text().contains(k, Qt.CaseInsensitive):
                    res.append(i.key())

        return res

    def clear(self) -> None:
        """清除"""
        self.m_d.clear()

    def ribbonWindow(self) -> QObject:
        """获取ribbonwindow"""
        return self.parent()

    def onActionDestroyed(self, o:QObject) -> None:
        self.removeAction(o, False)

    def onCategoryTitleChanged(self, title:str) -> None:
        c = self.sender()

        tag: int = -1
        for key, val in self.m_d.mTagToCategory.items():
            if val == c:
                tag = key
                break
        if tag == -1:
            return

        self.setTagName(tag, title)

    def removeAction(self, act:QAction, enableEmit:bool = True) -> None:
        deletedTags: list = list()   # 记录删除的tag，用于触发actionTagChanged
        tagToActions: dict = dict()  # tag : list

        for key, value in self.m_d.mTagToActions.items():
            # 把不是act的内容转移到tagToActions和tagToActionKeys中，之后再和m_d里的替换
            tagToActions[key] = list()
            tmpi = tagToActions[key]
            count = 0
            for jval in value:
                if jval != act:
                    tmpi.append(act)
                    count += 1

            if 0 == count:
                # 说明这个tag没有内容
                tagToActions.pop(tmpi)
                deletedTags.append(key)

        # 删除mKeyToAction
        key: str = self.m_d.mActionToKey.get(act, '')
        if key:
            self.m_d.mActionToKey.pop(act)
            self.m_d.mKeyToAction.pop(key)

        # 置换
        self.m_d.mTagToActions = tagToActions
        # 发射信号
        if enableEmit:
            for tagdelete in deletedTags:
                self.actionTagChanged.emit(tagdelete, True)


class SARibbonActionsModelPrivete:
    def __init__(self, m:QObject):
        self.mParent: SARibbonActionsManagerModel = m
        self.mMgr: SARibbonActionsManager = None
        self.mTag: int = SARibbonActionsManager.CommonlyUsedActionTag
        self.mSeatchText: str = ''
        self.mActions: list = list()

    def updateRef(self) -> None:
        if self.isNull():
            return

        if self.mSeatchText:
            self.mActions = self.mMgr.search(self.mSeatchText)
        else:
            self.mActions = self.mMgr.actions(self.mTag)

    def count(self) -> int:
        if self.isNull():
            return 0

        return len(self.mActions)

    def at(self, index:int) -> QAction:
        if self.isNull():
            return None
        if index >= self.count():
            return None

        return self.mActions[index]

    def isNull(self) -> bool:
        return self.mMgr is None


class SARibbonActionsManagerModel(QAbstractListModel):
    """
    SARibbonActionsManager 对应的model
    """
    def __init__(self, *_args):
        """
        SARibbonActionsManagerModel(p:QObject = None)
        SARibbonActionsManagerModel(m:SARibbonActionsManager, p:QObject = None)
        """
        m: SARibbonActionsManager = None
        p: QObject = None
        if len(_args) == 1:
            p = _args[0]
        elif len(_args) == 2:
            m = _args[0]
            p = _args[1]

        super().__init__(p)
        self.QAbstractListModel = p
        self.m_d = SARibbonActionsModelPrivete(self)
        if m:
            self.setupActionsManager(m)

    def rowCount(self, parent:QModelIndex) -> int:
        if parent.isValid():  # 非顶层
            return 0
        # 顶层
        return self.m_d.count()

    def headerData(self, section:int, orientation:int, role:int = Qt.DisplayRole) -> Any:
        if role != Qt.DisplayRole:
            return None
        if Qt.Horizontal == orientation:
            return "action name"

        return None

    def flags(self, index:QModelIndex) -> int:
        if not index.isValid():
            return Qt.NoItemFlags

        return Qt.ItemIsSelectable | Qt.ItemIsEnabled

    def data(self, index:QModelIndex, role:int) -> Any:
        act: QAction = self.indexToAction(index)
        if act is None:
            return None

        if Qt.DisplayRole == role:
            return act.text()
        elif Qt.DecorationRole == role:
            return act.icon()

        return None

    def setFilter(self, tag:int) -> None:
        self.m_d.mTag = tag
        self.update()

    def update(self) -> None:
        self.beginResetModel()
        self.m_d.updateRef()
        self.endResetModel()

    def setupActionsManager(self, m:SARibbonActionsManager) -> None:
        self.m_d.mMgr = m
        self.m_d.mTag = SARibbonActionsManager.CommonlyUsedActionTag
        self.m_d.mActions = m.filter(self.m_d.mTag)
        self.m_d.mMgr.actionTagChanged.connect(self.onActionTagChanged)
        self.update()

    def uninstallActionsManager(self) -> None:
        if not self.m_d.isNull():
            self.m_d.mMgr.actionTagChanged.disconnect(self.onActionTagChanged)
            self.m_d.mMgr = None
            self.m_d.mTag = SARibbonActionsManager.CommonlyUsedActionTag
        self.update()

    def indexToAction(self, index:QModelIndex) -> QAction:
        if not index.isValid():
            return None
        if index.row() >= self.m_d.count():
            return None

        return self.m_d.at(index.row())

    def search(self, text:str) -> None:
        self.m_d.mSeatchText = text
        self.update()

    def onActionTagChanged(self, tag:int, isdelete:bool) -> None:
        if isdelete and (tag == self.m_d.mTag):
            self.m_d.mTag = SARibbonActionsManager.UnknowActionTag
            self.update()
        else:
            if tag == self.m_d.mTag:
                self.update()
