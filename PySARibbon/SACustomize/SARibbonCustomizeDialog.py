# -*- coding: utf-8 -*-
"""
@Module     SARibbonCustomizeDialog
@Author     ROOT

@brief SARibbonCustomizeWidget的对话框封装
此功能依赖于@ref SARibbonActionsManager ，SARibbonActionsManager建议作为mianwindow的成员变量，
SARibbonActionsManager可以快速绑定所有QAction，详细见SARibbonActionsManager的说明

@note SARibbon的自定义是基于步骤的，如果在窗口生成前调用了@ref sa_apply_customize_from_xml_file 类似函数
那么在对话框生成前为了保证同步需要调用@ref SARibbonCustomizeDialog::fromXml 同步配置文件，这样再次修改后的配置文件就一致
"""

from PyQt5.QtCore import Qt, QXmlStreamWriter, QXmlStreamReader
from PyQt5.QtWidgets import QDialog, QWidget, QVBoxLayout, QHBoxLayout, QSpacerItem, QSizePolicy, QPushButton, \
    QApplication

from .SARibbonCustomizeWidget import SARibbonCustomizeWidget


class SARibbonCustomizeDialog(QDialog):
    def __init__(self, ribbonWindow, parent=None, f=Qt.WindowFlags()):
        super().__init__(parent, f)

        self.ui = SARibbonCustomizeDialogUi()
        self.ui.setupUi(ribbonWindow, self)
        self.initConnection()

    def setupActionsManager(self, mgr: QWidget):
        """设置action管理器"""
        self.ui.customWidget.setupActionsManager(mgr)

    def applys(self) -> bool:
        """等同SARibbonCustomizeWidget::applys"""
        return self.ui.customWidget.applys()

    def clear(self):
        """清除所有动作"""
        self.ui.customWidget.clear()

    def toXml(self, *_args) -> bool:
        """转换为xml
        toXml(xml: QXmlStreamWriter) -> bool
        toXml(xmlpath: str) -> bool
        """
        if len(_args) < 1:
            return False

        xml = _args[0]
        if isinstance(xml, QXmlStreamWriter) or isinstance(xml, str):
            return self.ui.customWidget.toXml(xml)
        else:
            print('Unknow type of xml:', type(xml))

        return False

    def fromXml(self, *_args):
        """等同SARibbonCustomizeWidget::fromXml
        fromXml(xml: QXmlStreamReader) -> None
        fromXml(xmlpath: str) -> None
        """
        if len(_args) < 1:
            return

        xml = _args[0]
        if isinstance(xml, QXmlStreamReader) or isinstance(xml, str):
            self.ui.customWidget.fromXml(xml)
        else:
            print('Unknow type of xml:', type(xml))

    def customizeWidget(self) -> SARibbonCustomizeWidget:
        """返回SARibbonCustomizeWidget窗口指针"""
        return self.ui.customWidget

    def initConnection(self):
        self.ui.pushButtonOk.clicked.connect(self.accept)
        self.ui.pushButtonCancel.clicked.connect(self.reject)


class SARibbonCustomizeDialogUi:
    def __init__(self):
        self.customWidget = None
        self.verticalLayoutMain = None
        self.horizontalLayoutButtonGroup = None
        self.pushButtonCancel: QPushButton = None
        self.pushButtonOk: QPushButton = None
        self.spacerItemleft = None

    def setupUi(self, ribbonWindow, customizeDialog: QWidget):
        if not customizeDialog.objectName():
            customizeDialog.setObjectName('SARibbonCustomizeDialog')
        customizeDialog.resize(800, 600)

        self.verticalLayoutMain = QVBoxLayout(customizeDialog)
        self.verticalLayoutMain.setObjectName('verticalLayoutMain')
        self.customWidget = SARibbonCustomizeWidget(ribbonWindow, customizeDialog)
        self.customWidget.setObjectName('customWidget')
        self.verticalLayoutMain.addWidget(self.customWidget)

        self.horizontalLayoutButtonGroup = QHBoxLayout()
        self.horizontalLayoutButtonGroup.setObjectName('horizontalLayoutButtonGroup')
        self.spacerItemleft = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.horizontalLayoutButtonGroup.addItem(self.spacerItemleft)

        self.pushButtonCancel = QPushButton(customizeDialog)
        self.pushButtonCancel.setObjectName('pushButtonCancel')
        self.horizontalLayoutButtonGroup.addWidget(self.pushButtonCancel)
        self.pushButtonOk = QPushButton(customizeDialog)
        self.pushButtonOk.setObjectName('pushButtonOk')
        self.horizontalLayoutButtonGroup.addWidget(self.pushButtonOk)

        self.verticalLayoutMain.addItem(self.horizontalLayoutButtonGroup)
        self.retranslateUi(customizeDialog)

    def retranslateUi(self, customizeDialog: QWidget):
        """国际化文本"""
        customizeDialog.setWindowTitle(QApplication.translate('SARibbonCustomizeDialog', 'Customize Dialog'))
        self.pushButtonCancel.setText(QApplication.translate('SARibbonCustomizeDialog', 'Cancel'))
        self.pushButtonOk.setText(QApplication.translate('SARibbonCustomizeDialog', 'OK'))
