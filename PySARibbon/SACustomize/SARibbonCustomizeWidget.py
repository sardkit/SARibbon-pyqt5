# -*- coding: utf-8 -*-
"""
@Module     SARibbonCustomizeWidget
@Author     ROOT

@brief 自定义界面窗口

@note SARibbon的自定义是基于步骤的，如果在窗口生成前调用了@ref sa_apply_customize_from_xml_file 类似函数
那么在对话框生成前为了保证同步需要调用@ref SARibbonCustomizeWidget::fromXml 同步配置文件，这样再次修改后的配置文件就一致
"""
from typing import List

from PyQt5.QtCore import Qt, QXmlStreamReader, QModelIndex, QDateTime, QXmlStreamWriter, QXmlStreamAttributes, \
    QIODevice, QFile, QItemSelectionModel
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QWidget, QAction, QHBoxLayout, QVBoxLayout, QLabel, QComboBox, QLineEdit, QListView, \
    QSpacerItem, QPushButton, QRadioButton, QButtonGroup, QTreeView, QToolButton, QSizePolicy, QAbstractItemView, \
    QApplication, QMessageBox, QInputDialog

from PySARibbon.SAWidgets import SARibbonPannelItem
from .SARibbonActionsManager import SARibbonActionsManager, SARibbonActionsManagerModel
from .SARibbonCustomizeData import SARibbonCustomizeData


class SARibbonCustomizeWidget(QWidget):
    def __init__(self, ribbonWindow, parent=None, f=Qt.WindowFlags()):
        super().__init__(parent, f)

        self.ui = SARibbonCustomizeWidgetUi()
        self.m_d = SARibbonCustomizeWidgetPrivate(self)

        self.m_d.mRibbonWindow = ribbonWindow
        self.ui.setupUi(self)
        self.ui.listViewSelect.setModel(self.m_d.mAcionModel)
        self.ui.treeViewResult.setModel(self.m_d.mRibbonModel)

        self.initConnection()
        self.updateModel()

    def initConnection(self):
        self.ui.comboBoxActionIndex.currentIndexChanged.connect(self.onComboBoxActionIndexCurrentIndexChanged)
        self.ui.radioButtonGroup.buttonClicked.connect(self.onRadioButtonGroupButtonClicked)
        self.ui.pushButtonNewCategory.clicked.connect(self.onPushButtonNewCategoryClicked)
        self.ui.pushButtonNewPannel.clicked.connect(self.onPushButtonNewPannelClicked)
        self.ui.pushButtonRename.clicked.connect(self.onPushButtonRenameClicked)
        self.ui.pushButtonAdd.clicked.connect(self.onPushButtonAddClicked)
        self.ui.pushButtonDelete.clicked.connect(self.onPushButtonDeleteClicked)
        self.ui.listViewSelect.clicked.connect(self.onListViewSelectClicked)
        self.ui.treeViewResult.clicked.connect(self.onTreeViewResultClicked)
        self.ui.toolButtonUp.clicked.connect(self.onToolButtonUpClicked)
        self.ui.toolButtonDown.clicked.connect(self.onToolButtonDownClicked)
        self.m_d.mRibbonModel.itemChanged.connect(self.onItemChanged)
        self.ui.lineEditSearchAction.textEdited.connect(self.onLineEditSearchActionTextEdited)
        self.ui.pushButtonReset.clicked.connect(self.onPushButtonResetClicked)

    def setupActionsManager(self, mgr: QWidget):
        """设置action管理器"""
        self.m_d.mActionMgr = mgr
        if (self.m_d.mActionMgr):
            self.m_d.mAcionModel.uninstallActionsManager()
        self.m_d.mAcionModel.setupActionsManager(mgr)
        # 更新左边复选框
        tags = mgr.actionTags()

        self.ui.comboBoxActionIndex.clear()
        for tag in tags:
            self.ui.comboBoxActionIndex.addItem(mgr.tagName(tag), tag)

    def isChanged(self) -> bool:
        return len(self.m_d.mCustomizeDatas) > 0

    def model(self) -> QStandardItemModel:
        """获取model"""
        return self.m_d.mRibbonModel

    def updateModel(self, tp: int = -1):
        """根据当前的radiobutton选项来更新model"""
        if tp >= 0:
            self.m_d.mShowType = tp
            self.m_d.updateModel()
        else:
            tp = self.ShowAllCategory if self.ui.radioButtonAllCategory.isChecked() else self.ShowMainCategory
            self.updateModel(tp)
            if self.m_d.mRibbonWindow:
                bar = self.m_d.mRibbonWindow.ribbonBar()
                if bar:
                    self.ui.comboBoxActionProportion.clear()
                    if bar.isTwoRowStyle():
                        self.ui.comboBoxActionProportion.addItem('large', SARibbonPannelItem.RPLarge)
                        self.ui.comboBoxActionProportion.addItem('small', SARibbonPannelItem.RPSmall)
                    else:
                        self.ui.comboBoxActionProportion.addItem('large', SARibbonPannelItem.RPLarge)
                        self.ui.comboBoxActionProportion.addItem('medium', SARibbonPannelItem.RPMedium)
                        self.ui.comboBoxActionProportion.addItem('small', SARibbonPannelItem.RPSmall)

    def applys(self) -> bool:
        """应用所有设定"""
        self.simplify()
        return self.sa_customize_datas_apply(self.m_d.mCustomizeDatas, self.m_d.mRibbonWindow) > 0

    def toXml(self, *_args) -> bool:
        """转换为xml
        此函数仅会写element，不会写document相关内容，因此如果需要写document，
        需要在此函数前调用QXmlStreamWriter::writeStartDocument(),在此函数后调用QXmlStreamWriter::writeEndDocument()
        :return 如果出现异常，返回false，如果没有自定义数据也会返回false
        """
        if len(_args) == 0:
            return  False
        xml = _args[0]
        if isinstance(xml, QXmlStreamWriter):
            res = self.m_d.mOldCustomizeDatas + self.m_d.mCustomizeDatas
            res = SARibbonCustomizeData.simplify(res)
            return self.sa_customize_datas_to_xml(xml, res)
        elif isinstance(xml, str):
            f = QFile(xml)
            if not f.open(QIODevice.ReadWrite | QIODevice.Truncate | QIODevice.Text):
                return False
            xml = QXmlStreamWriter(f)
            xml.setAutoFormatting(True)
            xml.setAutoFormattingIndent(2)
            # 在writeStartDocument之前指定编码
            xml.setCodec('utf-8')
            xml.writeStartDocument()
            isOK = self.toXml(xml)
            xml.writeEndDocument()
            f.close()
            return isOK
        return False

    def fromXml(self, *_args):
        """从xml中加载QList<SARibbonCustomizeData>
        对于基于配置文件的设置，对话框显示前建议调用此函数，保证叠加设置的正确记录
        """
        if len(_args) == 0:
            return
        xml = _args[0]

        if isinstance(xml, str):
            f = QFile(xml)
            if not f.open(QIODevice.ReadOnly | QIODevice.Text):
                return
            f.seek(0)
            xml = QXmlStreamReader(f)
            self.fromXml(xml)
        elif isinstance(xml, QXmlStreamReader):
            cds = self.sa_customize_datas_from_xml(xml, self.m_d.mActionMgr)
            self.m_d.mOldCustomizeDatas = cds

    def clear(self):
        """清除所有动作
        在执行applys函数后，如果要继续调用，应该clear，否则会导致异常
        """
        self.m_d.mCustomizeDatas.clear()

    def simplify(self):
        """精简"""
        self.m_d.mCustomizeDatas = SARibbonCustomizeData.simplify(self.m_d.mCustomizeDatas)

    def selectedRowProportion(self) -> int:
        """获取当前界面选中的行属性"""
        return self.ui.comboBoxActionProportion.currentData()

    def selectedAction(self) -> QAction:
        """获取listview中选中的action"""
        m = self.ui.listViewSelect.selectionModel()
        if not m or not m.hasSelection():
            return None

        i = m.currentIndex()
        return self.m_d.mAcionModel.indexToAction(i)

    def itemToAction(self, item: QStandardItem) -> QAction:
        """把item转换为action"""
        return self.m_d.itemToAction(item)

    def selectedItem(self) -> QStandardItem:
        """获取ribbon tree选中的item"""
        m = self.ui.treeViewResult.selectionModel()
        if not m or not m.hasSelection():
            return None

        i = m.currentIndex()
        return self.m_d.mRibbonModel.itemFromIndex(i)

    def selectedRibbonLevel(self) -> int:
        """获取选中的ribbon tree 的level
        :return: -1为选中异常，0代表选中了category 1代表选中了pannel 2代表选中了action
        """
        item = self.selectedItem()
        if item:
            return self.itemLevel(item)

        return -1

    def itemLevel(self, item: QStandardItem) -> int:
        """获取StandardItem 的level"""
        return self.m_d.itemLevel(item)

    def setSelectItem(self, item: QStandardItem, ensureVisible=False):
        """设置某个item被选中"""
        m = self.ui.treeViewResult.selectionModel()
        if not m:
            return

        m.clearSelection()
        m.select(item.index(), QItemSelectionModel.Select)
        if ensureVisible:
            self.ui.treeViewResult.scrollTo(item.index())

    def isItemCanCustomize(self, item: QStandardItem) -> bool:
        """判断itemn能否改动，可以改动返回true"""
        return self.m_d.isItemCanCustomize(item)

    def isSelectedItemCanCustomize(self) -> bool:
        return self.isItemCanCustomize(self.selectedItem())

    def isCustomizeItem(self, item: QStandardItem) -> bool:
        """判断itemn能否改动，可以改动返回true"""
        return self.m_d.isCustomizeItem(item)

    def isSelectedItemIsCustomize(self) -> bool:
        return self.isCustomizeItem(self.selectedItem())

    def removeItem(self, item: QStandardItem):
        if item.parent():
            item.parent().removeRow(item.row())
        else:
            self.m_d.mRibbonModel.removeRow(item.row())

    # slots
    def onComboBoxActionIndexCurrentIndexChanged(self, index: int):
        tag: int = self.ui.comboBoxActionIndex.itemData(index)
        self.m_d.mAcionModel.setFilter(tag)

    def onRadioButtonGroupButtonClicked(self, b):
        categoryType = self.ShowAllCategory if (b == self.ui.radioButtonAllCategory) else self.ShowMainCategory
        self.updateModel(categoryType)

    def onPushButtonNewCategoryClicked(self):
        row: int = self.m_d.mRibbonModel.rowCount()
        m: QItemSelectionModel = self.ui.treeViewResult.selectionModel()

        if m and m.hasSelection():
            i: QModelIndex = m.currentIndex()
            while i.parent().isValid():
                i = i.parent()
            # 获取选中的最顶层item
            row = i.row() + 1

        self.m_d.mCustomizeCategoryCount += 1
        ni: QStandardItem = QStandardItem("category[customize]{0}".format(self.m_d.mCustomizeCategoryCount))
        ni.setData(0, SARibbonCustomizeWidget.LevelRole)
        self.m_d.mRibbonModel.insertRow(row, ni)
        # 设置新增的为选中
        self.setSelectItem(ni)
        # 把动作插入动作列表中
        d = SARibbonCustomizeData.makeAddCategoryCustomizeData(ni.text(), ni.row(), SARibbonCustomizeWidgetPrivate.makeRandomObjName("category"))

        self.m_d.mCustomizeDatas.append(d)
        ni.setData(True, SARibbonCustomizeWidget.CanCustomizeRole)  # 有CustomizeRole，必有CanCustomizeRole
        ni.setData(True, SARibbonCustomizeWidget.CustomizeRole)
        ni.setData(d.categoryObjNameValue, SARibbonCustomizeWidget.CustomizeObjNameRole)

    def onPushButtonNewPannelClicked(self):
        item: QStandardItem = self.selectedItem()
        if not item:
            return

        level: int = self.selectedRibbonLevel()
        self.m_d.mCustomizePannelCount += 1
        ni: QStandardItem = QStandardItem("pannel[customize]{0}".format(self.m_d.mCustomizePannelCount))
        ni.setData(1, SARibbonCustomizeWidget.LevelRole)

        if 0 == level:
            # 说明是category,插入到最后
            item.appendRow(ni)
        elif 1 == level:
            # 说明选择的是pannel，插入到此pannel之后
            categoryItem: QStandardItem = item.parent()
            if categoryItem is None:
                return
            categoryItem.insertRow(item.row() + 1, ni)
        else:
            # 不符合就删除退出
            return

        # 查找category的object name
        categoryItem: QStandardItem = ni.parent()
        categoryObjName = self.m_d.itemObjectName(categoryItem)
        d = SARibbonCustomizeData.makeAddPannelCustomizeData(ni.text(), ni.row(),
                                                             categoryObjName, SARibbonCustomizeWidgetPrivate.makeRandomObjName("pannel"))

        self.m_d.mCustomizeDatas.append(d)
        ni.setData(True, SARibbonCustomizeWidget.CanCustomizeRole)  # 有CustomizeRole，必有CanCustomizeRole
        ni.setData(True, SARibbonCustomizeWidget.CustomizeRole)
        ni.setData(d.pannelObjNameValue, SARibbonCustomizeWidget.CustomizeObjNameRole)
        self.setSelectItem(ni)

    def onPushButtonRenameClicked(self):
        item: QStandardItem = self.selectedItem()
        if item is None:
            return

        text, ok = QInputDialog.getText(self, "rename", "name:", QLineEdit.Normal, item.text())
        if not ok or not text:
            return

        level: int = self.itemLevel(item)
        if 0 == level:
            # 改Category名
            cateObjName: str = self.m_d.itemObjectName(item)
            d = SARibbonCustomizeData.makeRenameCategoryCustomizeData(text, cateObjName)
            self.m_d.mCustomizeDatas.append(d)
        elif 1 == level:
            cateObjName: str = self.m_d.itemObjectName(item.parent())
            pannelObjName: str = self.m_d.itemObjectName(item)
            d = SARibbonCustomizeData.makeRenamePannelCustomizeData(text, cateObjName,  pannelObjName)
            self.m_d.mCustomizeDatas.append(d)
        else:
            # action 不允许改名
            return

        item.setText(text)

    def onPushButtonAddClicked(self):
        act: QAction = self.selectedAction()
        item: QStandardItem = self.selectedItem()
        if act is None or item is None:
            return

        level: int = self.itemLevel(item)
        if 0 == level:
            # 选中category不进行操作
            return
        elif 2 == level:
            # 选中action，添加到这个action之后,把item设置为pannel
            item = item.parent()

        pannelObjName: str = self.m_d.itemObjectName(item)
        categoryObjName: str = self.m_d.itemObjectName(item.parent())
        key: str = self.m_d.mActionMgr.key(act)

        d = SARibbonCustomizeData.makeAddActionCustomizeData(key, self.m_d.mActionMgr, self.selectedRowProportion(),
                                                             categoryObjName, pannelObjName)
        self.m_d.mCustomizeDatas.append(d)

        actItem: QStandardItem = QStandardItem(act.icon(), act.text())

        actItem.setData(2, SARibbonCustomizeWidget.LevelRole)
        actItem.setData(True, SARibbonCustomizeWidget.CanCustomizeRole)  # 有CustomizeRole，必有CanCustomizeRole
        actItem.setData(True, SARibbonCustomizeWidget.CustomizeRole)
        actItem.setData(act.objectName(), SARibbonCustomizeWidget.CustomizeObjNameRole)
        actItem.setData(act, SARibbonCustomizeWidget.PointerRole)  # 把action指针传入
        item.appendRow(actItem)

    def onPushButtonDeleteClicked(self):
        item: QStandardItem = self.selectedItem()
        if item is None:
            return
        if not self.isItemCanCustomize(item):
            return

        level: int = self.itemLevel(item)
        if 0 == level:
            # 删除category
            d = SARibbonCustomizeData.makeRemoveCategoryCustomizeData(self.m_d.itemObjectName(item))
            self.m_d.mCustomizeDatas.append(d)
        elif 1 == level:
            # 删除pannel
            catObjName: str = self.m_d.itemObjectName(item.parent())
            pannelObjName: str = self.m_d.itemObjectName(item)
            d = SARibbonCustomizeData.makeRemovePannelCustomizeData(catObjName, pannelObjName)
            self.m_d.mCustomizeDatas.append(d)
        elif 2 == level:
            # 删除Action
            catObjName: str = self.m_d.itemObjectName(item.parent().parent())
            pannelObjName: str = self.m_d.itemObjectName(item.parent())
            act: QAction = self.itemToAction(item)
            key: str = self.m_d.mActionMgr.key(act)
            if not key or not catObjName or not pannelObjName:
                return

            d = SARibbonCustomizeData.makeRemoveActionCustomizeData(catObjName, pannelObjName,
                                                                    key, self.m_d.mActionMgr)
            self.m_d.mCustomizeDatas.append(d)

        # 执行删除操作
        self.removeItem(item)
        # 删除后重新识别
        self.ui.pushButtonAdd.setEnabled(self.selectedAction() and self.isSelectedItemIsCustomize() and self.selectedRibbonLevel() > 0)
        self.ui.pushButtonDelete.setEnabled(self.isSelectedItemIsCustomize())

    def onListViewSelectClicked(self, index: QModelIndex):
        # 每次点击，判断是否可以进行操作，决定pushButtonAdd和pushButtonDelete的显示状态
        # 点击了listview，判断treeview的状态
        self.ui.pushButtonAdd.setEnabled(self.isSelectedItemCanCustomize() and self.selectedRibbonLevel() > 0)
        self.ui.pushButtonDelete.setEnabled(self.isSelectedItemCanCustomize())

    def onTreeViewResultClicked(self, index: QModelIndex):
        # 每次点击，判断是否可以进行操作，决定pushButtonAdd和pushButtonDelete的显示状态
        item: QStandardItem = self.selectedItem()
        if item is None:
            return

        level: int = self.itemLevel(item)
        self.ui.pushButtonAdd.setEnabled(self.selectedAction() and (level > 0) and self.isItemCanCustomize(item))
        self.ui.pushButtonDelete.setEnabled(self.isItemCanCustomize(item))  # 有CustomizeRole，必有CanCustomizeRole
        self.ui.pushButtonRename.setEnabled(
            level != 2 or self.isItemCanCustomize(item))  # QAction 不能改名 ， 有CustomizeRole，必有CanCustomizeRole

    def onToolButtonUpClicked(self):
        item: QStandardItem = self.selectedItem()
        if item is None or 0 == item.row():
            return

        level: int = self.itemLevel(item)
        if 0 == level:
            # 移动category
            d = SARibbonCustomizeData.makeChangeCategoryOrderCustomizeData(self.m_d.itemObjectName(item), -1)
            self.m_d.mCustomizeDatas.append(d)
            r: int = item.row()
            item = self.m_d.mRibbonModel.takeItem(r)
            self.m_d.mRibbonModel.removeRow(r)
            self.m_d.mRibbonModel.insertRow(r - 1, item)
        elif 1 == level:
            paritem: QStandardItem = item.parent()
            d = SARibbonCustomizeData.makeChangePannelOrderCustomizeData(self.m_d.itemObjectName(paritem), self.m_d.itemObjectName(item), -1)
            self.m_d.mCustomizeDatas.append(d)
            r: int = item.row()
            item = paritem.takeChild(r)
            paritem.removeRow(r)
            paritem.insertRow(r - 1, item)
        elif 2 == level:
            pannelItem: QStandardItem = item.parent()
            categoryItem: QStandardItem = pannelItem.parent()
            act: QAction = self.itemToAction(item)
            if not act:
                return

            key: str = self.m_d.mActionMgr.key(act)
            d = SARibbonCustomizeData.makeChangeActionOrderCustomizeData(self.m_d.itemObjectName(categoryItem),
                                                                         self.m_d.itemObjectName(pannelItem), key, self.m_d.mActionMgr, -1)
            self.m_d.mCustomizeDatas.append(d)
            r: int = item.row()
            item = pannelItem.takeChild(r)
            pannelItem.removeRow(r)
            pannelItem.insertRow(r - 1, item)

    def onToolButtonDownClicked(self):
        item: QStandardItem = self.selectedItem()
        if item is None:
            return

        if item.parent():
            count = item.parent().rowCount()
        else:
            count = self.m_d.mRibbonModel.rowCount()
        if not item or count - 1 == item.row():
            return

        level: int = self.itemLevel(item)
        if 0 == level:
            # 移动category
            d = SARibbonCustomizeData.makeChangeCategoryOrderCustomizeData(self.m_d.itemObjectName(item), 1)
            self.m_d.mCustomizeDatas.append(d)
            r: int = item.row()
            item = self.m_d.mRibbonModel.takeItem(item.row())
            self.m_d.mRibbonModel.removeRow(r)
            self.m_d.mRibbonModel.insertRow(r + 1, item)
        elif 1 == level:
            paritem: QStandardItem = item.parent()
            d = SARibbonCustomizeData.makeChangePannelOrderCustomizeData(self.m_d.itemObjectName(paritem), self.m_d.itemObjectName(item), 1)
            self.m_d.mCustomizeDatas.append(d)
            r: int = item.row()
            item = paritem.takeChild(r)
            paritem.removeRow(r)
            paritem.insertRow(r + 1, item)
        elif 2 == level:
            pannelItem: QStandardItem = item.parent()
            categoryItem: QStandardItem = pannelItem.parent()
            act: QAction = self.itemToAction(item)
            if not act:
                return

            key: str = self.m_d.mActionMgr.key(act)
            d = SARibbonCustomizeData.makeChangeActionOrderCustomizeData(self.m_d.itemObjectName(categoryItem),
                                                                         self.m_d.itemObjectName(pannelItem), key, self.m_d.mActionMgr, -1)
            self.m_d.mCustomizeDatas.append(d)
            r: int = item.row()
            item = pannelItem.takeChild(r)
            pannelItem.removeRow(r)
            pannelItem.insertRow(r + 1, item)

    def onItemChanged(self, item: QStandardItem):
        if item is None:
            return

        level: int = self.itemLevel(item)
        if 0 == level:
            if item.isCheckable():
                objname: str = self.m_d.itemObjectName(item)
                d = SARibbonCustomizeData.makeVisibleCategoryCustomizeData(objname, item.checkState() == Qt.Checked)
                self.m_d.mCustomizeDatas.append(d)

    def onLineEditSearchActionTextEdited(self, text: str):
        self.m_d.mAcionModel.search(text)

    def onPushButtonResetClicked(self):
        btn: int = QMessageBox.warning(self, "Warning", "Are you sure reset all customize setting?",
                                       QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if btn == QMessageBox.Yes:
            self.clear()

    @classmethod
    def sFromXml(cls, xml: QXmlStreamReader, ribbonWindow, mgr: QWidget):
        """应用xml配置
        可以结合customize_datas_from_xml和customize_datas_apply函数
        """
        # 先找到sa-ribbon-customize标签
        cds = cls.sa_customize_datas_from_xml(xml, mgr)
        return cls.sa_customize_datas_apply(cds, ribbonWindow) > 0

    @staticmethod
    def sa_customize_datas_to_xml(xml: QXmlStreamWriter, cds: List) -> bool:
        """  转换为xml
        此函数仅会写element，不会写document相关内容，因此如果需要写document，
        需要在此函数前调用QXmlStreamWriter.writeStartDocument(),在此函数后调用QXmlStreamWriter.writeEndDocument()
        :param xml: QXmlStreamWriter指针
        注意，在传入QXmlStreamWriter之前，需要设置编码为utf-8:xml.setCodec("utf-8");
        由于QXmlStreamWriter在string作为io时，是不支持编码的，而此又无法保证自定义过程不出现中文字符，
        因此，QXmlStreamWriter不应该通过string进行构造，如果需要用到string，也需要通过QByteArray构造，如：
        :param cds: 基于List<SARibbonCustomizeData>生成的步骤
        :return: 如果出现异常，返回False,如果没有自定义数据也会返回False
        """
        if len(cds) <= 0:
            return False

        xml.writeStartElement('sa-ribbon-customize')
        for d in cds:
            xml.writeStartElement('customize-data')
            xml.writeAttribute('type', str(d.actionType()))
            xml.writeAttribute('index', str(d.indexValue))
            xml.writeAttribute('key', d.keyValue)
            xml.writeAttribute('category', d.categoryObjNameValue)
            xml.writeAttribute('pannel', d.pannelObjNameValue)
            xml.writeAttribute('row-prop', str(d.actionRowProportionValue))
            xml.writeEndElement()
        xml.writeEndElement()
        if xml.hasError():
            print('write has error')

        return True

    @staticmethod
    def sa_customize_datas_from_xml(xml: QXmlStreamWriter, mgr: SARibbonActionsManager) -> List:
        """  通过xml获取List<SARibbonCustomizeData>
        :param xml:
        :param mgr:
        :return: List<SARibbonCustomizeData>
        """
        # 先找到'sa-ribbon-customize'
        while not xml.atEnd():
            print('name:', xml.name(), ' qualifiedName:', xml.qualifiedName())
            if xml.isStartElement() and xml.name() == 'sa-ribbon-customize':
                break

            xml.readNext()

        res = list()
        # 开始遍历'customize-data'
        while not xml.atEnd():
            if xml.isStartElement() and xml.name() == 'customize-data':
                # 首先读取属性type
                d = SARibbonCustomizeData()
                attrs: QXmlStreamAttributes = xml.attributes()
                if not attrs.hasAttribute('type'):
                    # 说明异常，跳过这个
                    xml.readNextStartElement()
                    continue

                d.setActionType(int(attrs.value('type')))
                # 开始读取子对象
                if attrs.hasAttribute('index'):
                    d.indexValue = int(xml.attributes().value('index'))

                if attrs.hasAttribute('key'):
                    d.keyValue = str(attrs.value('key'))
                if attrs.hasAttribute('category'):
                    d.categoryObjNameValue = str(attrs.value('category'))
                if attrs.hasAttribute('pannel'):
                    d.pannelObjNameValue = str(attrs.value('pannel'))
                if attrs.hasAttribute('row-prop'):
                    d.actionRowProportionValue = int(attrs.value('row-prop'))

                d.setActionsManager(mgr)
                res.append(d)

            xml.readNext()

        if xml.hasError():
            print(xml.errorString())
        return res

    @staticmethod
    def sa_customize_datas_apply(cds: List, w: QWidget) -> int:
        """  应用QList<SARibbonCustomizeData>
        :param cds:
        :param w: SARibbonMainWindow指针
        :return: 成功应用的个数
        """
        c = 0
        for d in cds:
            if d.apply(w):
                c += 1
        return c

    @staticmethod
    def sa_apply_customize_from_xml_file(filePath: str, w: QWidget, mgr: SARibbonActionsManager) -> bool:
        """  直接加载xml自定义ribbon配置文件用于ribbon的自定义显示
        :param filePath: xml配置文件
        :param w: 主窗体
        :param mgr: action管理器
        :return: 成功返回True
        """
        f = QFile(filePath)
        if not f.open(QIODevice.ReadOnly | QIODevice.Text):
            return False

        f.seek(0)
        xml = QXmlStreamReader(f)
        return SARibbonCustomizeWidget.sFromXml(xml, w, mgr)

    # RibbonTreeShowType, 定义ribbon树的显示类型
    ShowAllCategory = 0     # 显示所有Category，包括contextcategory
    ShowMainCategory = 1    # 显示主要的category，不包含上下文
    # ItemRole, QStandardItem对应的role
    LevelRole = Qt.UserRole + 1             # 代表这是层级，有0：category 1：pannel 2：item
    PointerRole = Qt.UserRole + 2           # 代表这是存放指针。根据LevelRole来进行转
    CanCustomizeRole = Qt.UserRole + 3      # 代表个item是可以自定义的.bool
    CustomizeRole = Qt.UserRole + 4         # 代表这个是自定义的item,bool,主要用于那些自己添加的标签和pannel，有此角色必有CanCustomizeRole
    CustomizeObjNameRole = Qt.UserRole + 5  # 记录了临时的自定义内容的obj名 QString


class SARibbonCustomizeWidgetUi:
    """构建SARibbonCustomizeWidget的Ui"""
    def __init__(self):
        self.horizontalLayoutMain: QHBoxLayout = None
        self.verticalLayoutSelect: QVBoxLayout = None
        self.labelSelectAction: QLabel = None
        self.horizontalLayoutSearch: QHBoxLayout = None
        self.comboBoxActionIndex: QComboBox = None
        self.lineEditSearchAction: QLineEdit = None
        self.listViewSelect: QListView = None
        self.verticalLayoutMidButtons: QVBoxLayout = None
        self.verticalSpacerUp: QSpacerItem = None
        self.pushButtonAdd: QPushButton = None
        self.pushButtonDelete: QPushButton = None
        self.pushButtonReset: QPushButton = None
        self.verticalSpacerDown: QSpacerItem = None
        self.labelProportion: QLabel = None
        self.comboBoxActionProportion: QComboBox = None
        self.verticalLayoutResult: QVBoxLayout = None
        self.labelCustomize: QLabel = None
        self.horizontalLayoutCategorySelect: QHBoxLayout = None
        self.radioButtonMainCategory: QRadioButton = None
        self.radioButtonAllCategory: QRadioButton = None
        self.radioButtonGroup: QButtonGroup = None
        self.treeViewResult: QTreeView = None
        self.horizontalLayoutActionOptBtns: QHBoxLayout = None
        self.pushButtonNewCategory: QPushButton = None
        self.pushButtonNewPannel: QPushButton = None
        self.pushButtonRename: QPushButton = None
        self.verticalLayoutRightButtons: QVBoxLayout = None
        self.verticalSpacerUp2: QSpacerItem = None
        self.toolButtonUp: QToolButton = None
        self.toolButtonDown: QToolButton = None
        self.verticalSpacerDown2: QSpacerItem = None

    def setupUi(self, customizeWidget: QWidget):
        if not customizeWidget.objectName():
            customizeWidget.setObjectName('SARibbonCustomizeWidget')
        customizeWidget.resize(800, 600)

        self.horizontalLayoutMain = QHBoxLayout(customizeWidget)
        self.horizontalLayoutMain.setObjectName('horizontalLayoutMain')
        self.verticalLayoutSelect = QVBoxLayout()
        self.verticalLayoutSelect.setObjectName('verticalLayoutSelect')
        self.labelSelectAction = QLabel(customizeWidget)
        self.labelSelectAction.setObjectName('labelSelectAction')
        self.verticalLayoutSelect.addWidget(self.labelSelectAction)

        self.horizontalLayoutSearch = QHBoxLayout()
        self.horizontalLayoutSearch.setObjectName('horizontalLayoutSearch')
        self.comboBoxActionIndex = QComboBox(customizeWidget)
        self.comboBoxActionIndex.setObjectName('comboBoxActionIndex')
        self.comboBoxActionIndex.setEditable(False)
        self.horizontalLayoutSearch.addWidget(self.comboBoxActionIndex)
        self.lineEditSearchAction = QLineEdit(customizeWidget)
        self.lineEditSearchAction.setObjectName('lineEditSearchAction')
        self.horizontalLayoutSearch.addWidget(self.lineEditSearchAction)

        self.verticalLayoutSelect.addLayout(self.horizontalLayoutSearch)
        self.listViewSelect = QListView(customizeWidget)
        self.listViewSelect.setObjectName('listViewSelect')
        self.verticalLayoutSelect.addWidget(self.listViewSelect)

        self.horizontalLayoutMain.addLayout(self.verticalLayoutSelect)

        self.verticalLayoutMidButtons = QVBoxLayout()
        self.verticalLayoutMidButtons.setObjectName('verticalLayoutMidButtons')
        self.verticalSpacerUp = QSpacerItem(20, 40,  QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.verticalLayoutMidButtons.addItem(self.verticalSpacerUp)
        self.pushButtonAdd = QPushButton(customizeWidget)
        self.pushButtonAdd.setObjectName('pushButtonAdd')
        self.pushButtonAdd.setEnabled(False)
        self.verticalLayoutMidButtons.addWidget(self.pushButtonAdd)
        self.pushButtonDelete = QPushButton(customizeWidget)
        self.pushButtonDelete.setObjectName('pushButtonDelete')
        self.pushButtonDelete.setEnabled(False)
        self.verticalLayoutMidButtons.addWidget(self.pushButtonDelete)
        self.verticalSpacerDown = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.verticalLayoutMidButtons.addItem(self.verticalSpacerDown)
        self.labelProportion = QLabel(customizeWidget)
        self.labelProportion.setObjectName('labelProportion')
        self.verticalLayoutMidButtons.addWidget(self.labelProportion)
        self.comboBoxActionProportion = QComboBox(customizeWidget)
        self.comboBoxActionProportion.setObjectName('comboBoxActionProportion')
        self.comboBoxActionProportion.setEnabled(False)
        self.verticalLayoutMidButtons.addWidget(self.comboBoxActionProportion)

        self.horizontalLayoutMain.addLayout(self.verticalLayoutMidButtons)

        self.verticalLayoutResult = QVBoxLayout()
        self.verticalLayoutResult.setObjectName('verticalLayoutResult')
        self.labelCustomize = QLabel(customizeWidget)
        self.labelCustomize.setObjectName('labelCustomize')
        self.verticalLayoutResult.addWidget(self.labelCustomize)

        self.horizontalLayoutCategorySelect = QHBoxLayout()
        self.horizontalLayoutCategorySelect.setObjectName('horizontalLayoutCategorySelect')
        self.radioButtonMainCategory = QRadioButton(customizeWidget)
        self.radioButtonMainCategory.setObjectName('radioButtonMainCategory')
        self.radioButtonMainCategory.setChecked(False)
        self.horizontalLayoutCategorySelect.addWidget(self.radioButtonMainCategory)
        self.radioButtonAllCategory = QRadioButton(customizeWidget)
        self.radioButtonAllCategory.setObjectName('radioButtonAllCategory')
        self.radioButtonAllCategory.setChecked(True)
        self.horizontalLayoutCategorySelect.addWidget(self.radioButtonAllCategory)

        self.radioButtonGroup = QButtonGroup(customizeWidget)
        self.radioButtonGroup.addButton(self.radioButtonMainCategory)
        self.radioButtonGroup.addButton(self.radioButtonAllCategory)
        self.verticalLayoutResult.addLayout(self.horizontalLayoutCategorySelect)

        self.treeViewResult = QTreeView(customizeWidget)
        self.treeViewResult.setObjectName('treeViewResult')
        self.treeViewResult.setHeaderHidden(True)
        self.treeViewResult.setSelectionMode(QAbstractItemView.SingleSelection)
        self.treeViewResult.setAnimated(True)   # 支持动画
        self.treeViewResult.setEditTriggers(QAbstractItemView.NoEditTriggers)  # 不允许直接在item上重命名
        self.verticalLayoutResult.addWidget(self.treeViewResult)

        self.horizontalLayoutActionOptBtns = QHBoxLayout()
        self.horizontalLayoutActionOptBtns.setObjectName('horizontalLayoutActionOptBtns')
        self.pushButtonNewCategory = QPushButton(customizeWidget)
        self.pushButtonNewCategory.setObjectName('pushButtonNewCategory')
        self.horizontalLayoutActionOptBtns.addWidget(self.pushButtonNewCategory)
        self.pushButtonNewPannel = QPushButton(customizeWidget)
        self.pushButtonNewPannel.setObjectName('pushButtonNewPannel')
        self.horizontalLayoutActionOptBtns.addWidget(self.pushButtonNewPannel)
        self.pushButtonRename = QPushButton(customizeWidget)
        self.pushButtonRename.setObjectName('pushButtonRename')
        self.horizontalLayoutActionOptBtns.addWidget(self.pushButtonRename)
        self.pushButtonReset = QPushButton(customizeWidget)
        self.pushButtonReset.setObjectName('pushButtonReset')
        self.horizontalLayoutActionOptBtns.addWidget(self.pushButtonReset)
        self.verticalLayoutResult.addLayout(self.horizontalLayoutActionOptBtns)

        self.horizontalLayoutMain.addLayout(self.verticalLayoutResult)

        self.verticalLayoutRightButtons = QVBoxLayout()
        self.verticalLayoutRightButtons.setObjectName('verticalLayoutRightButtons')
        self.verticalSpacerUp2 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.verticalLayoutRightButtons.addItem(self.verticalSpacerUp2)
        self.toolButtonUp = QToolButton(customizeWidget)
        self.toolButtonUp.setObjectName('toolButtonUp')
        self.toolButtonUp.setArrowType(Qt.UpArrow)
        self.toolButtonUp.setAutoRaise(True)
        self.verticalLayoutRightButtons.addWidget(self.toolButtonUp)
        self.toolButtonDown = QToolButton(customizeWidget)
        self.toolButtonDown.setObjectName('toolButtonDown')
        self.toolButtonDown.setArrowType(Qt.DownArrow)
        self.toolButtonDown.setAutoRaise(True)
        self.verticalLayoutRightButtons.addWidget(self.toolButtonDown)
        self.verticalSpacerDown2 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.verticalLayoutRightButtons.addItem(self.verticalSpacerDown2)

        self.horizontalLayoutMain.addLayout(self.verticalLayoutRightButtons)

        self.retranslateUi(customizeWidget)

    def retranslateUi(self, customizeWidget: QWidget):
        customizeWidget.setWindowTitle(QApplication.translate('SARibbonCustomizeWidget', 'Customize Widget'))
        self.labelSelectAction.setText(QApplication.translate('SARibbonCustomizeWidget', '\344\273\216\344\270\213\345\210\227\351\200\211\351\241\271\345\215\241\351\200\211\346\213\251\345\221\275\344\273\244\357\274\232'))
        self.lineEditSearchAction.setInputMask('')
        self.lineEditSearchAction.setText('')
        self.lineEditSearchAction.setPlaceholderText(QApplication.translate('SARibbonCustomizeWidget', '\346\237\245\346\211\276\345\221\275\344\273\244'))
        self.pushButtonAdd.setText(QApplication.translate('SARibbonCustomizeWidget', '\346\267\273\345\212\240 >>'))
        self.pushButtonDelete.setText(QApplication.translate('SARibbonCustomizeWidget', '<< \345\210\240\351\231\244'))
        self.labelCustomize.setText(QApplication.translate('SARibbonCustomizeWidget', '\350\207\252\345\256\232\344\271\211\345\212\237\350\203\275\345\214\272\357\274\232'))
        self.radioButtonMainCategory.setText(QApplication.translate('SARibbonCustomizeWidget', '\344\270\273\351\200\211\351\241\271\345\215\241'))
        self.radioButtonAllCategory.setText(QApplication.translate('SARibbonCustomizeWidget', '\346\211\200\346\234\211\351\200\211\351\241\271\345\215\241'))
        self.pushButtonNewCategory.setText(QApplication.translate('SARibbonCustomizeWidget', '\346\226\260\345\273\272\351\200\211\351\241\271\345\215\241'))
        self.pushButtonNewPannel.setText(QApplication.translate('SARibbonCustomizeWidget', '\346\226\260\345\273\272\347\273\204'))
        self.pushButtonRename.setText(QApplication.translate('SARibbonCustomizeWidget', '\351\207\215\345\221\275\345\220\215'))
        self.pushButtonReset.setText(QApplication.translate('SARibbonCustomizeWidget', 'reset'))
        self.labelProportion.setText(QApplication.translate('SARibbonCustomizeWidget', 'proportion:'))


class SARibbonCustomizeWidgetPrivate:
    """管理SARibbonCustomizeWidget的业务逻辑"""
    def __init__(self, w):
        self.mParent: SARibbonCustomizeWidget = w
        self.mShowType = SARibbonCustomizeWidget.ShowAllCategory  # 显示类型
        self.mRibbonWindow: QWidget = None  # 保存SARibbonMainWindow的指针
        self.mActionMgr = None  # action管理器
        self.mAcionModel = SARibbonActionsManagerModel(w)  # action管理器对应的model
        self.mRibbonModel = QStandardItemModel(w)  # 用于很成ribbon的树
        self.mCustomizeCategoryCount = 0  # 记录自定义Category的个数
        self.mCustomizePannelCount = 0  # 记录自定义Pannel的个数
        self.mCustomizeDatas: List = list()  # 记录所有的自定义动作
        self.mOldCustomizeDatas: List = list()  # 记录旧的自定义动作

    def updateModel(self):
        if not self.mRibbonWindow:
            return

        self.mRibbonModel.clear()
        ribbonbar = self.mRibbonWindow.ribbonBar()

        for c in ribbonbar.categoryPages():
            if (self.mShowType == SARibbonCustomizeWidget.ShowMainCategory) and c.isContextCategory():
                # 如果是只显示主内容，如果是上下文标签就忽略
                continue

            ci = QStandardItem()
            if c.isContextCategory():
                ci.setText("[{}]".format(c.windowTitle()))
            else:
                ci.setText(c.windowTitle())

            if c.isCanCustomize() and not c.isContextCategory():
                # 上下文标签不做显示隐藏处理
                ci.setCheckable(True)
                st = Qt.Checked if ribbonbar.isCategoryVisible(c) else Qt.Unchecked
                ci.setCheckState(st)
                # 标记这个是可以自定义的
                ci.setData(True, SARibbonCustomizeWidget.CanCustomizeRole)

            ci.setData(0, SARibbonCustomizeWidget.LevelRole)
            ci.setData(c, SARibbonCustomizeWidget.PointerRole)
            for p in c.pannelList():
                pi = QStandardItem(p.windowTitle())
                pi.setData(1, SARibbonCustomizeWidget.LevelRole)
                pi.setData(p, SARibbonCustomizeWidget.PointerRole)
                if p.isCanCustomize():
                    # 标记这个是可以自定义的
                    pi.setData(True, SARibbonCustomizeWidget.CanCustomizeRole)

                ci.appendRow(pi)
                for i in p.ribbonPannelItem():
                    act = i.action
                    if act.isSeparator():
                        continue

                    ii = QStandardItem()
                    if i.customWidget:
                        # 如果是自定义窗口
                        if not i.widget().windowTitle() and not i.widget().windowIcon():
                            continue  # 如果窗口啥也没有，就跳过

                        ii.setText(i.widget().windowTitle())
                        ii.setIcon(i.widget().windowIcon())
                        if SARibbonCustomizeData.isCanCustomize(i.widget()):
                            # 标记这个是可以自定义的
                            ii.setData(True, SARibbonCustomizeWidget.CanCustomizeRole)
                    else:
                        # 不是自定义，说明是action
                        ii.setText(i.action.text())
                        ii.setIcon(i.action.icon())
                        if SARibbonCustomizeData.isCanCustomize(i.action):
                            # 标记这个是可以自定义的
                            ii.setData(True, SARibbonCustomizeWidget.CanCustomizeRole)

                    ii.setData(2, SARibbonCustomizeWidget.LevelRole)
                    ii.setData(i, SARibbonCustomizeWidget.PointerRole)
                    pi.appendRow(ii)

            self.mRibbonModel.appendRow(ci)

    def itemLevel(self, item: QStandardItem) -> int:
        return item.data(SARibbonCustomizeWidget.LevelRole)

    def isCustomizeItem(self, item: QStandardItem) -> bool:
        if not item:
            return False
        return item.data(SARibbonCustomizeWidget.CustomizeRole) == None

    def itemToCategory(self, item: QStandardItem) -> QWidget:
        """把item转换为category"""
        level = item.data(SARibbonCustomizeWidget.LevelRole)
        if level != 0:
            return None

        p = item.data(SARibbonCustomizeWidget.PointerRole)
        return p

    def itemToPannel(self, item: QStandardItem) -> QWidget:
        """把item转换为SARibbonPannel"""
        level = item.data(SARibbonCustomizeWidget.LevelRole)
        if level != 1:
            return None

        p = item.data(SARibbonCustomizeWidget.PointerRole)
        return p

    def itemToAction(self, item: QStandardItem) -> QAction:
        """从item转为action"""
        if 2 != self.itemLevel(item):
            return None

        # 这里要非常注意，SARibbonCustomizeWidget.CustomizeRole为true时，说明这个是自定义的内容，
        # 这时PointerRole里存放的是action指针，不是SARibbonPannelItem
        act: QAction = None

        if item.data(SARibbonCustomizeWidget.CustomizeRole):
            act = item.data(SARibbonCustomizeWidget.PointerRole)
        else:
            pi = item.data(SARibbonCustomizeWidget.PointerRole)
            act = pi.action

        return act

    def itemObjectName(self, item: QStandardItem) -> str:
        """获取item对应的object name"""
        if (self.isCustomizeItem(item)):
            # 说明是自定义的
            objName = item.data(SARibbonCustomizeWidget.CustomizeObjNameRole)
        else:
            # 说明这个是非自定义的
            level = self.itemLevel(item)
            if 0 == level:
                category = self.itemToCategory(item)
                if category:
                    objName = category.objectName()

            elif 1 == level:
                pannel = self.itemToPannel(item)
                if pannel:
                    objName = pannel.objectName()

        return (objName)

    def isItemCanCustomize(self, item: QStandardItem) -> bool:
        """判断是否可以自定义"""
        if not item:
            return False

        v = item.data(SARibbonCustomizeWidget.CanCustomizeRole)
        return bool(v)

    @staticmethod
    def makeRandomObjName(pre: str) -> str:
        """创建一个随机id，形如：pre_QDateTime::currentMSecsSinceEpoch_suf"""
        return '{}_{}'.format(pre, QDateTime.currentMSecsSinceEpoch())
