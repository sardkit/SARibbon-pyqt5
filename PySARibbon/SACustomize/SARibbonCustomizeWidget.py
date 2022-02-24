# -*- coding: utf-8 -*-
"""
@Module     SARibbonCustomizeWidget
@Author     ROOT

@brief 自定义界面窗口

@note SARibbon的自定义是基于步骤的，如果在窗口生成前调用了@ref sa_apply_customize_from_xml_file 类似函数
那么在对话框生成前为了保证同步需要调用@ref SARibbonCustomizeWidget::fromXml 同步配置文件，这样再次修改后的配置文件就一致
"""
from PyQt5.QtCore import Qt, QXmlStreamReader, QModelIndex
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QWidget, QAction, QHBoxLayout, QVBoxLayout, QLabel, QComboBox, QLineEdit, QListView, \
    QSpacerItem, QPushButton, QRadioButton, QButtonGroup, QTreeView, QToolButton, QSizePolicy, QAbstractItemView, \
    QApplication


class SARibbonCustomizeWidget(QWidget):
    def __init__(self, ribbonWindow, parent=None, f=Qt.WindowFlags()):
        super().__init__(parent, f)

        self.ui = SARibbonCustomizeWidgetUi()
        self.m_d = SARibbonCustomizeWidgetPrivate()

    def setupActionsManager(self, mgr: QWidget):
        pass

    def isChanged(self) -> bool:
        pass

    def model(self) -> QStandardItemModel:
        pass

    def updateModel(self, tp: int):
        pass

    def applys(self) -> bool:
        pass

    def toXml(self, *_args) -> bool:
        pass

    def fromXml(self, *_args):
        pass

    def clear(self):
        pass

    @staticmethod
    def sFromXml(xml: QXmlStreamReader, ribbonWindow, mgr: QWidget) -> bool:
        pass

    def simplify(self):
        pass

    def selectedRowProportion(self) -> int:
        pass

    def selectedAction(self) -> QAction:
        pass

    def itemToAction(self, item: QStandardItem) -> QAction:
        pass

    def selectedItem(self) -> QStandardItem:
        pass

    def selectedRibbonLevel(self) -> int:
        pass

    def itemLevel(self, item: QStandardItem) -> int:
        pass

    def setSelectItem(self, item: QStandardItem, ensureVisible=False):
        pass

    def isItemCanCustomize(self, item: QStandardItem) -> bool:
        pass

    def isSelectedItemCanCustomize(self) -> bool:
        pass

    def removeItem(self, item: QStandardItem):
        pass

    def initConnection(self):
        pass

    # slots
    def onComboBoxActionIndexCurrentIndexChanged(self, index: int):
        pass

    def onRadioButtonGroupButtonClicked(self, b):
        pass

    def onPushButtonNewCategoryClicked(self):
        pass

    def onPushButtonNewPannelClicked(self):
        pass

    def onPushButtonRenameClicked(self):
        pass

    def onPushButtonAddClicked(self):
        pass

    def onPushButtonDeleteClicked(self):
        pass

    def onListViewSelectClicked(self, index: QModelIndex):
        pass

    def onTreeViewResultClicked(self, index: QModelIndex):
        pass

    def onToolButtonUpClicked(self):
        pass

    def onToolButtonDownClicked(self):
        pass

    def onItemChanged(self, item: QStandardItem):
        pass

    def onLineEditSearchActionTextEdited(self, text: str):
        pass

    def onPushButtonResetClicked(self):
        pass

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
        self.treeViewResult.setHeader(True)
        self.treeViewResult.setSelectionModel(QAbstractItemView.SingleSelection)
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
    def __init__(self):
        pass    # TODO
