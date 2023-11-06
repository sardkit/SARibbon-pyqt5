# -*- coding: utf-8 -*-
"""
@Module     SARibbonCustomizeData
@Author     ROOT


@brief 记录所有自定义操作的数据类
@note 此数据依赖于@ref SARibbonActionsManager 要在SARibbonActionsManager之后使用此类
"""
from typing import List

from PyQt5.QtCore import QObject
from PyQt5.QtWidgets import QWidget

from PySARibbon.SAWidgets import SARibbonPannelItem
from PySARibbon.SATools.SARibbonGlobal import SA_RIBBON_BAR_PROP_CAN_CUSTOMIZE


class SARibbonCustomizeData(object):
    def __init__(self, tp=0, mgr=None):
        # 标记这个data是category还是pannel亦或是action
        self.m_type = tp
        self.m_actionsManagerPointer: QWidget = mgr

        """
       @brief 记录顺序的参数
       在actionType==AddCategoryActionType时，此参数记录Category的insert位置,
       在actionType==AddPannelActionType时，此参数记录pannel的insert位置,
       在actionType==AddActionActionType时，此参数记录pannel的insert位置
       """
        self.indexValue = -1
        """
       @brief 记录标题、索引等参数
       在actionType==AddCategoryActionType时，key为category标题，
       在actionType==AddPannelActionType时，key为pannel标题，
       在actionType==AddActionActionType时，key为action的查询依据，基于SARibbonActionsManager::action查询
       """
        self.keyValue = ''
        """@brief 记录categoryObjName，用于定位Category"""
        self.categoryObjNameValue = ''
        """@brief 记录pannelObjName，saribbon的Customize索引大部分基于objname"""
        self.pannelObjNameValue = ''
        # 行的占比，ribbon中有large，media和small三种占比,见@ref RowProportion
        self.actionRowProportionValue: int = SARibbonPannelItem.RPLarge

    def actionType(self) -> int:
        """获取CustomizeData的action type"""
        return self.m_type

    def setActionType(self, tp: int):
        """设置CustomizeData的action type"""
        self.m_type = tp

    def isValid(self) -> bool:
        """判断是否是一个正常的CustomizeData"""
        return self.actionType() != self.UnknowActionType

    def apply(self, window) -> bool:
        """应用SARibbonCustomizeData到SARibbonMainWindow"""
        bar = window.ribbonBar()
        if not bar:
            return False

        tp = self.actionType()
        if tp == self.UnknowActionType:
            return False
        elif tp == self.AddCategoryActionType:
            c = bar.insertCategoryPage(self.keyValue, self.indexValue)
            if not c:
                return False
            c.setObjectName(self.categoryObjNameValue)
            self.setCanCustomize(c)
            return True
        elif tp == self.AddPannelActionType:
            c = bar.categoryByObjectName(self.categoryObjNameValue)
            if not c:
                return False
            p = c.insertPannel(self.keyValue, self.indexValue)
            p.setObjectName(self.pannelObjNameValue)
            self.setCanCustomize(p)
            return True
        elif tp == self.AddActionActionType:
            if not self.m_actionsManagerPointer:
                return False
            c = bar.categoryByObjectName(self.categoryObjNameValue)
            if not c:
                return False
            p = c.pannelByObjectName(self.pannelObjNameValue)
            if not p:
                return False
            act = self.m_actionsManagerPointer.action(self.keyValue)
            if not act:
                return False
            self.setCanCustomize(act)
            p.addAction(act, self.actionRowProportionValue)
            return True
        elif tp == self.RemoveCategoryActionType:
            c = bar.categoryByObjectName(self.categoryObjNameValue)
            if not c:
                return False
            bar.removeCategory(c)
            return True
        elif tp == self.RemovePannelActionType:
            c = bar.categoryByObjectName(self.categoryObjNameValue)
            if not c:
                return False
            p = c.pannelByObjectName(self.pannelObjNameValue)
            if not p:
                return False
            c.removePannel(p)
            return True
        elif tp == self.RemoveActionActionType:
            c = bar.categoryByObjectName(self.categoryObjNameValue)
            if not c:
                return False
            p = c.pannelByObjectName(self.pannelObjNameValue)
            if not p:
                return False
            act = self.m_actionsManagerPointer.action(self.keyValue)
            if not act:
                return False
            p.removeAction(act)
            return True
        elif tp == self.ChangeCategoryOrderActionType:
            c = bar.categoryByObjectName(self.categoryObjNameValue)
            if not c:
                return False
            currentIdx = bar.categoryIndex(c)
            if currentIdx == -1:
                return False
            bar.moveCategory(currentIdx, currentIdx + self.indexValue)
            return True
        elif tp == self.ChangePannelOrderActionType:
            c = bar.categoryByObjectName(self.categoryObjNameValue)
            if not c:
                return False
            p = c.pannelByObjectName(self.pannelObjNameValue)
            if not p:
                return False
            pannelIdx = c.pannelIndex(p)
            if p == -1:
                return False
            c.movePannel(pannelIdx, pannelIdx + self.indexValue)
            return True
        elif tp == self.ChangeActionOrderActionType:
            c = bar.categoryByObjectName(self.categoryObjNameValue)
            if not c:
                return False
            p = c.pannelByObjectName(self.pannelObjNameValue)
            if not p:
                return False
            act = self.m_actionsManagerPointer.action(self.keyValue)
            if not act:
                return False
            actIdx = p.actionIndex(act)
            if actIdx <= -1:
                return False
            p.moveAction(actIdx, actIdx + self.indexValue)
            return True
        elif tp == self.RenameCategoryActionType:
            c = bar.categoryByObjectName(self.categoryObjNameValue)
            if not c:
                return False
            c.setWindowTitle(self.keyValue)
            return True
        elif tp == self.RenamePannelActionType:
            c = bar.categoryByObjectName(self.categoryObjNameValue)
            if not c:
                return False
            p = c.pannelByObjectName(self.pannelObjNameValue)
            if not p:
                return False
            p.setWindowTitle(self.keyValue)
            return True
        elif tp == self.VisibleCategoryActionType:
            c = bar.categoryByObjectName(self.categoryObjNameValue)
            if not c:
                return False
            if self.indexValue == 1:
                bar.showCategory(c)
            else:
                bar.hideCategory(c)
            return True

        return False

    def actionManager(self) -> QWidget:
        """获取actionmanager指针"""
        return self.m_actionsManagerPointer

    def setActionsManager(self, mgr: QWidget):
        """设置ActionsManager"""
        self.m_actionsManagerPointer = mgr

    @classmethod
    def makeAddCategoryCustomizeData(cls, title: str, index: int, objName: str) -> object:
        """创建一个AddCategoryActionType的SARibbonCustomizeData"""
        d = SARibbonCustomizeData(cls.AddCategoryActionType)
        d.indexValue = index
        d.keyValue = title
        d.categoryObjNameValue = objName
        return d

    @classmethod
    def makeAddPannelCustomizeData(cls, title: str, index: int, categoryobjName: str, objName: str) -> object:
        """创建一个AddPannelActionType的SARibbonCustomizeData"""
        d = SARibbonCustomizeData(cls.AddPannelActionType)
        d.indexValue = index
        d.keyValue = title
        d.pannelObjNameValue = objName
        d.categoryObjNameValue = categoryobjName
        return d

    @classmethod
    def makeAddActionCustomizeData(cls, key: str,  mgr: QWidget, rp: int,
                                   categoryobjName: str, pannelObjName: str) -> object:
        """添加action"""
        d = SARibbonCustomizeData(cls.AddActionActionType, mgr)
        d.keyValue = key
        d.pannelObjNameValue = pannelObjName
        d.categoryObjNameValue = categoryobjName
        d.actionRowProportionValue = rp
        return d

    @classmethod
    def makeRenameCategoryCustomizeData(cls, newname: str, categoryobjName: str) -> object:
        """创建一个RenameCategoryActionType的SARibbonCustomizeData"""
        d = SARibbonCustomizeData(cls.RenameCategoryActionType)
        if not categoryobjName:
            print("SARibbon Warning !!! customize rename category, but get an empty category object name,"
                  "if you want to customize SARibbon, please make sure every element has been set object name.")
        d.keyValue = newname
        d.categoryObjNameValue = categoryobjName
        return d

    @classmethod
    def makeRenamePannelCustomizeData(cls, newname: str, categoryobjName: str, pannelObjName: str) -> object:
        """创建一个RenamePannelActionType的SARibbonCustomizeData"""
        d = SARibbonCustomizeData(cls.RenamePannelActionType)
        if not categoryobjName or not pannelObjName:
            print("SARibbon Warning !!! customize rename category, but get an empty category object name,"
                  "if you want to customize SARibbon, please make sure every element has been set object name.")
        d.keyValue = newname
        d.categoryObjNameValue = categoryobjName
        d.pannelObjNameValue = pannelObjName
        return d

    @classmethod
    def makeChangeCategoryOrderCustomizeData(cls, categoryobjName: str, moveIndex: int) -> object:
        """对应ChangeCategoryOrderActionType"""
        d = SARibbonCustomizeData(cls.ChangeCategoryOrderActionType)
        if not categoryobjName:
            print("SARibbon Warning !!! customize rename category, but get an empty category object name,"
                  "if you want to customize SARibbon, please make sure every element has been set object name.")
        d.categoryObjNameValue = categoryobjName
        d.indexValue = moveIndex
        return d

    @classmethod
    def makeChangePannelOrderCustomizeData(cls, categoryobjName: str, pannelObjName: str, moveIndex: int) -> object:
        """对应ChangePannelOrderActionType"""
        d = SARibbonCustomizeData(cls.ChangePannelOrderActionType)
        if not categoryobjName or not pannelObjName:
            print("SARibbon Warning !!! customize rename category, but get an empty category object name,"
                  "if you want to customize SARibbon, please make sure every element has been set object name.")
        d.categoryObjNameValue = categoryobjName
        d.pannelObjNameValue = pannelObjName
        d.indexValue = moveIndex
        return d

    @classmethod
    def makeChangeActionOrderCustomizeData(cls, categoryobjName: str, pannelObjName: str,
                                           key: str, mgr: QWidget, moveIndex: int) -> object:
        """对应ChangeActionOrderActionType"""
        d = SARibbonCustomizeData(cls.ChangeActionOrderActionType, mgr)
        if not categoryobjName or not pannelObjName:
            print("SARibbon Warning !!! customize rename category, but get an empty category object name,"
                  "if you want to customize SARibbon, please make sure every element has been set object name.")
        d.categoryObjNameValue = categoryobjName
        d.pannelObjNameValue = pannelObjName
        d.keyValue = key
        d.indexValue = moveIndex
        return d

    @classmethod
    def makeRemoveCategoryCustomizeData(cls, categoryobjName: str) -> object:
        """对应RemoveCategoryActionType"""
        d = SARibbonCustomizeData(cls.RemoveCategoryActionType)
        if not categoryobjName:
            print("SARibbon Warning !!! customize rename category, but get an empty category object name,"
                  "if you want to customize SARibbon, please make sure every element has been set object name.")
        d.categoryObjNameValue = categoryobjName
        return d

    @classmethod
    def makeRemovePannelCustomizeData(cls, categoryobjName: str, pannelObjName: str) -> object:
        """对应RemovePannelActionType"""
        d = SARibbonCustomizeData(cls.RemovePannelActionType)
        if not categoryobjName or not pannelObjName:
            print("SARibbon Warning !!! customize rename category, but get an empty category object name,"
                  "if you want to customize SARibbon, please make sure every element has been set object name.")
        d.categoryObjNameValue = categoryobjName
        d.pannelObjNameValue = pannelObjName
        return d

    @classmethod
    def makeRemoveActionCustomizeData(cls, categoryobjName: str, pannelObjName: str, key: str, mgr: QWidget) -> object:
        """对应RemoveActionActionType"""
        d = SARibbonCustomizeData(cls.RemoveActionActionType, mgr)
        if not categoryobjName or not pannelObjName:
            print("SARibbon Warning !!! customize rename category, but get an empty category object name,"
                  "if you want to customize SARibbon, please make sure every element has been set object name.")
        d.categoryObjNameValue = categoryobjName
        d.pannelObjNameValue = pannelObjName
        d.keyValue = key
        return d

    @classmethod
    def makeVisibleCategoryCustomizeData(cls, categoryobjName: str, isShow: bool) -> object:
        """对应VisibleCategoryActionType"""
        d = SARibbonCustomizeData(cls.VisibleCategoryActionType)
        if not categoryobjName:
            print("SARibbon Warning !!! customize rename category, but get an empty category object name,"
                  "if you want to customize SARibbon, please make sure every element has been set object name.")
        d.categoryObjNameValue = categoryobjName
        d.keyValue = 1 if isShow else 0
        return d

    @staticmethod
    def isCanCustomize(obj: QObject) -> bool:
        """判断外置属性，是否允许自定义"""
        v = obj.property(SA_RIBBON_BAR_PROP_CAN_CUSTOMIZE)
        return bool(v)

    @staticmethod
    def setCanCustomize(obj: QObject, canbe=True):
        """设置外置属性允许自定义"""
        obj.setProperty(SA_RIBBON_BAR_PROP_CAN_CUSTOMIZE, canbe)

    @classmethod
    def simplify(cls, csd: List) -> List:
        """对List[SARibbonCustomizeData]进行简化操作
         *此函数会执行如下操作：
         1、针对同一个category/pannel连续出现的添加和删除操作进行移除（前一步添加，后一步删除）
         2、针对VisibleCategoryActionType，对于连续出现的操作只保留最后一步
         3、针对RenameCategoryActionType和RenamePannelActionType操作，只保留最后一个
         4、针对连续的ChangeCategoryOrderActionType，ChangePannelOrderActionType，
            ChangeActionOrderActionType进行合并为一个动作，如果合并后原地不动，则删除
        """
        size = len(csd)
        if size <= 1:
            return csd

        willremoveIndex = list()    # 记录要删除的index
        # 首先针对连续出现的添加和删除操作进行优化
        for i in range(size):
            if (csd[i-1].actionType() == cls.AddCategoryActionType and
                csd[i].actionType() == cls.RemoveCategoryActionType):
                if csd[i-1].categoryObjNameValue == csd[i].categoryObjNameValue:
                    willremoveIndex.append(i-1)
                    willremoveIndex.append(i)
            elif (csd[i-1].actionType() == cls.AddPannelActionType and
                   csd[i].actionType() == cls.RemovePannelActionType):
                if (csd[i-1].categoryObjNameValue == csd[i].categoryObjNameValue and
                     csd[i-1].pannelObjNameValue == csd[i].pannelObjNameValue):
                    willremoveIndex.append(i-1)
                    willremoveIndex.append(i)
            elif (csd[i-1].actionType() == cls.AddActionActionType and
                   csd[i].actionType() == cls.RemoveActionActionType):
                if (csd[i-1].categoryObjNameValue == csd[i].categoryObjNameValue and
                     csd[i-1].pannelObjNameValue == csd[i].pannelObjNameValue and
                     csd[i-1].keyValue == csd[i].keyValue):
                    willremoveIndex.append(i-1)
                    willremoveIndex.append(i)
        res = cls.remove_indexs(csd, willremoveIndex)
        willremoveIndex.clear()

        # 筛选VisibleCategoryActionType，对于连续出现的操作只保留最后一步
        size = len(res)
        for i in range(size):
            if (res[i-1].actionType() == cls.VisibleCategoryActionType and
                 res[i].actionType() == cls.VisibleCategoryActionType):
                # 要保证操作的是同一个内容
                if res[i-1].categoryObjNameValue == res[i].categoryObjNameValue:
                    willremoveIndex.append(i-1)     # 删除前一个只保留最后一个
        res = cls.remove_indexs(res, willremoveIndex)
        willremoveIndex.clear()

        # 针对RenameCategoryActionType和RenamePannelActionType操作，只需保留最后一个
        for i, val in enumerate(res):
            if val.actionType() == cls.RenameCategoryActionType:
                # 向后查询，如果查询到有同一个Category改名，把这个索引加入删除队列
                for v in res[i+1:]:
                    if (v.actionType() == val.actionType() and
                         v.categoryObjNameValue == val.categoryObjNameValue):
                        willremoveIndex.append(i)
            elif val.actionType() == cls.RenamePannelActionType:
                # 向后查询，如果查询到有同一个pannel改名，把这个索引加入删除队列
                for v in res[i+1:]:
                    if (v.actionType() == val.actionType() and
                         v.categoryObjNameValue == val.categoryObjNameValue and
                         v.pannelObjNameValue == val.pannelObjNameValue):
                        willremoveIndex.append(i)
        res = cls.remove_indexs(res, willremoveIndex)
        willremoveIndex.clear()

        # 针对连续的ChangeCategoryOrderActionType，ChangePannelOrderActionType，ChangeActionOrderActionType进行合并
        size = res.size()
        for i in range(size):
            if (res[i-1].actionType() == cls.ChangeCategoryOrderActionType and
                        res[i].actionType() == cls.ChangeCategoryOrderActionType):
                if res[i-1].categoryObjNameValue == res[i].categoryObjNameValue:
                    # 说明连续两个顺序调整，把前一个indexvalue和后一个indexvalue相加，前一个删除
                    res[i].indexValue += res[i-1].indexValue
                    willremoveIndex.append(i-1)
            elif (res[i-1].actionType() == cls.ChangePannelOrderActionType and
                   res[i].actionType() == cls.ChangePannelOrderActionType):
                if (res[i-1].categoryObjNameValue == res[i].categoryObjNameValue and
                     res[i-1].pannelObjNameValue == res[i].pannelObjNameValue):
                    # 说明连续两个顺序调整，把前一个indexvalue和后一个indexvalue相加，前一个删除
                    res[i].indexValue += res[i - 1].indexValue
                    willremoveIndex.append(i-1)
            elif (res[i-1].actionType() == cls.ChangeActionOrderActionType and
                   res[i].actionType() == cls.ChangeActionOrderActionType):
                if (res[i-1].categoryObjNameValue == res[i].categoryObjNameValue and
                     res[i-1].pannelObjNameValue == res[i].pannelObjNameValue and
                     res[i-1].keyValue == res[i].keyValue):
                    res[i].indexValue += res[i - 1].indexValue
                    willremoveIndex.append(i-1)
        res = cls.remove_indexs(res, willremoveIndex)
        willremoveIndex.clear()

        # 上一步操作可能会产生indexvalue为0的情况，此操作把indexvalue为0的删除
        for i, val in enumerate(res):
            if (val.actionType() == cls.ChangeCategoryOrderActionType and
                        val.actionType() == cls.ChangeCategoryOrderActionType or
                        val.actionType() == cls.ChangeCategoryOrderActionType):
                if val.indexValue == 0:
                    willremoveIndex.append(i)
        res = cls.remove_indexs(res, willremoveIndex)
        return res

    @staticmethod
    def remove_indexs(csd: List, willremoveIndex: List) -> List:
        res = [val for i, val in enumerate(csd) if i not in willremoveIndex]
        return res

    # 自定义变量
    UnknowActionType = 0            # 未知操作
    AddCategoryActionType = 1       # 添加category操作(1)
    AddPannelActionType = 2         # 添加pannel操作(2)
    AddActionActionType = 3         # 添加action操作(3)
    RemoveCategoryActionType = 4    # 删除category操作(4)
    RemovePannelActionType = 5      # 删除pannel操作(5)
    RemoveActionActionType = 6      # 删除action操作(6)
    ChangeCategoryOrderActionType = 7   # 改变category顺序的操作(7)
    ChangePannelOrderActionType = 8     # 改变pannel顺序的操作(8)
    ChangeActionOrderActionType = 9     # 改变action顺序的操作(9)
    RenameCategoryActionType = 10   # 对category更名操作(10)
    RenamePannelActionType = 11     # 对Pannel更名操作(11)
    VisibleCategoryActionType = 12  # 对category执行隐藏/显示操作(12)
