# -*- coding: utf-8 -*-
"""
@Module     SARibbonGalleryGroup
@Author     ROOT

@brief Gallery的组
组负责显示管理Gallery Item
"""
from typing import List, Union
from PyQt5.QtCore import Qt, QModelIndex, QSize, pyqtSignal, QAbstractListModel, QItemSelectionModel
from PyQt5.QtGui import QIcon, QPainter
from PyQt5.QtWidgets import QAction, QStyledItemDelegate, QStyleOptionViewItem, QStyle, QListView


class SARibbonGalleryItem:
    def __init__(self, *_args):
        """
        __init__()
        __init__(str, QIcon)
        __init__(QAction)
        """
        self.m_datas = dict()   # 存储不同role对应的数据
        self.m_flags = Qt.ItemIsEnabled | Qt.ItemIsSelectable
        self.m_action: QAction = None
        if len(_args) > 1:
            self.setText(_args[0])
            self.setIcon(_args[1])
        elif len(_args) > 0 and isinstance(_args[0], QAction):
            self.setAction(_args[0])

    def setData(self, role: int, data):
        self.m_datas[role] = data

    def data(self, role) -> any:
        if self.m_action:
            if role == Qt.DisplayRole:
                return self.m_action.text()
            elif role == Qt.ToolTipRole:
                return self.m_action.toolTip()
            elif role == Qt.DecorationRole:
                return self.m_action.icon()
        return self.m_datas.get(role)

    def setText(self, text: str):
        self.setData(Qt.DisplayRole, text)

    def text(self) -> str:
        if self.m_action:
            return self.m_action.text()
        return self.data(Qt.DisplayRole)

    def setToolTip(self, text: str):
        self.setData(Qt.ToolTipRole, text)

    def toolTip(self) -> str:
        if self.m_action:
            return self.m_action.toolTip()
        return self.data(Qt.ToolTipRole)

    def setIcon(self, icon: QIcon):
        self.setData(Qt.DecorationRole, icon)

    def icon(self) -> QIcon:
        if self.m_action:
            return self.m_action.icon()
        return self.data(Qt.DecorationRole)

    def setAction(self, act: QAction):
        self.m_action = act
        if act.isEnabled():
            self.m_flags |= Qt.ItemIsEnabled
        else:
            self.m_flags &= ~Qt.ItemIsEnabled

    def action(self) -> QAction:
        return self.m_action

    def setSelectable(self, isSelectable: bool):
        if isSelectable:
            self.m_flags |= Qt.ItemIsSelectable
        else:
            self.m_flags &= ~Qt.ItemIsSelectable

    def isSelectable(self) -> bool:
        return bool(self.m_flags & Qt.ItemIsSelectable)

    def setEnable(self, isEnable: bool):
        if self.m_action:
            self.m_action.setEnabled(isEnable)
        if isEnable:
            self.m_flags |= Qt.ItemIsEnabled
        else:
            self.m_flags &= ~Qt.ItemIsEnabled

    def isEnable(self) -> bool:
        if self.m_action:
            return self.m_action.isEnabled()
        return bool(self.m_flags & Qt.ItemIsEnabled)

    def setFlags(self, flag: int):
        self.m_flags = flag
        if self.m_flags:
            self.m_action.setEnabled(flag & Qt.ItemIsEnabled)

    def flags(self) -> int:
        return self.m_flags


class SARibbonGalleryGroupItemDelegate(QStyledItemDelegate):
    """@brief SARibbonGalleryGroup对应的显示代理"""
    def __init__(self, group, parent):
        super().__init__(parent)
        self.m_group: SARibbonGalleryGroup = group

    def sizeHint(self, option, index) -> QSize:
        return QSize(option.rect.width(), option.rect.height())

    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex):
        if self.m_group.enableIconText():
            self.paintIconWithText(painter, option, index)
        else:
            self.paintIconOnly(painter, option, index)

    def paintIconOnly(self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex):
        painter.save()
        painter.setClipRect(option.rect)
        style = self.m_group.style()
        style.drawPrimitive(QStyle.PE_PanelItemViewItem, option, painter, self.m_group)
        iconRect = option.rect
        iconRect.adjust(3, 3, -3, -3)
        ico: QIcon = index.data(Qt.DecorationRole)
        ico.paint(painter, iconRect, Qt.AlignCenter, QIcon.Normal, QIcon.On)
        painter.restore()

    def paintIconWithText(self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex):
        super().paint(painter, option, index)


class SARibbonGalleryGroupModel(QAbstractListModel):
    """@brief SARibbonGalleryGroup对应的model"""
    def __init__(self, parent):
        super().__init__(parent)
        self.m_items: List[SARibbonGalleryItem] = list()

    def rowCount(self, parent=QModelIndex()) -> int:
        ret = 0 if parent.isValid() else len(self.m_items)
        return ret

    def flags(self, index: QModelIndex) -> int:
        if not index.isValid() or index.row() >= len(self.m_items):
            return Qt.NoItemFlags
        i = index.row()
        return self.m_items[i].flags()

    def data(self, index: QModelIndex=None, role: int=0):
        if not index.isValid() or index.row() >= len(self.m_items):
            return None
        i = index.row()
        return self.m_items[i].data(role)

    def index(self, row: int, column: int=0, parent: QModelIndex=None):
        if self.hasIndex(row, column, parent):
            return self.createIndex(row, column, self.m_items[row])
        return QModelIndex()

    def setData(self, index: QModelIndex, value, role: int=0):
        if not index.isValid() or index.row() >= len(self.m_items):
            return False
        i = index.row()
        self.m_items[i].setData(role, value)
        return True

    def clear(self):
        self.beginResetModel()
        self.m_items.clear()
        self.endResetModel()

    def at(self, row: int) -> SARibbonGalleryItem:
        return self.m_items[row]

    def insert(self, row: int, item: SARibbonGalleryItem):
        self.beginInsertRows(QModelIndex(), row, row)
        self.m_items.insert(row, item)
        self.endInsertRows()

    def take(self, row: int) -> Union[None, SARibbonGalleryItem]:
        if row < 0 or row >= len(self.m_items):
            return None
        self.beginRemoveRows(QModelIndex(), row, row)
        item = self.m_items[row]
        del self.m_items[row]
        self.endRemoveRows()
        return item

    def append(self, item: SARibbonGalleryItem):
        row = len(self.m_items)
        self.beginInsertRows(QModelIndex(), row, row+1)
        self.m_items.append(item)
        self.endInsertRows()


class SARibbonGalleryGroup(QListView):
    def __init__(self, parent):
        super().__init__(parent)
        self.enableIconText_ = False
        self.groupTitle = ''

        self.setupGroupModel()
        self.setViewMode(QListView.IconMode)
        self.setResizeMode(QListView.Adjust)
        self.setSelectionRectVisible(True)
        self.setUniformItemSizes(True)
        self.setPreinstallStyle(SARibbonGalleryGroup.LargeIconWithText)
        self.setItemDelegate(SARibbonGalleryGroupItemDelegate(self, self))
        self.clicked.connect(self.onItemClicked)

    def setPreinstallStyle(self, style: int):
        """设置默认的样式"""
        if style == SARibbonGalleryGroup.LargeIconOnly:
            self.setIconSize(QSize(72, 56))
            self.setGridSize(QSize(72, 56))
            self.setEnableIconText(False)
        else:
            self.setIconSize(QSize(72, 36))
            self.setGridSize(QSize(72, 56))
            self.setEnableIconText(True)

    def addItem(self, *_args):
        """
        addItem(QAction)
        addItem(SARibbonGalleryItem)
        addItem(str, QIcon)
        """
        if len(_args) < 1:
            raise Exception('parameter length < 1')

        if not self.groupModel():
            return
        if len(_args) >= 2:
            self.groupModel().append(SARibbonGalleryItem(_args[0], _args[1]))
        elif isinstance(_args[0], QAction):
            self.groupModel().append(SARibbonGalleryItem(_args[0]))
        else:
            self.groupModel().append(_args[0])

    def addActionItem(self, act: QAction):
        if not self.groupModel():
            return
        self.groupModel().append(SARibbonGalleryItem(act))

    def addActionItemList(self, acts: List[QAction]):
        if not self.groupModel():
            return
        for act in acts:
            self.groupModel().append(SARibbonGalleryItem(act))

    def setupGroupModel(self):
        """构建一个model，这个model的父类是SARibbonGalleryGroup"""
        self.setModel(SARibbonGalleryGroupModel(self.parent()))

    def groupModel(self) -> SARibbonGalleryGroupModel:
        return self.model()

    def setEnableIconText(self, enable: bool):
        self.enableIconText_ = enable

    def enableIconText(self) -> bool:
        return self.enableIconText_

    def setGroupTitle(self, title: str):
        self.groupTitle = title
        self.groupTitleChanged.emit(self.groupTitle)

    def groupTitle(self) -> str:
        return self.groupTitle

    def selectByIndex(self, i: int):
        if not self.groupModel():
            return
        ind = self.groupModel().index(i, 0, QModelIndex())
        selmodel: QItemSelectionModel = self.selectionModel()
        if selmodel:
            selmodel.select(ind, QItemSelectionModel.SelectCurrent)

    # 槽函数
    def onItemClicked(self, index: QModelIndex):
        if not index.isValid():
            return
        item: SARibbonGalleryItem = index.internalPointer()
        act = item.action()
        if act:
            act.activate(QAction.Trigger)

    # 信号
    groupTitleChanged = pyqtSignal(str)

    # 枚举
    LargeIconWithText = 0
    LargeIconOnly = 1
