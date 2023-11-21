# -*- coding: utf-8 -*-
"""
@Module     SARibbonToolButton
@Author     ROOT
"""
from PyQt5.QtCore import Qt, QSize, QRect, QEvent, QPoint
from PyQt5.QtGui import QPixmap, QPainter, QIcon, QCursor, QPalette
from PyQt5.QtWidgets import QToolButton, QAction, QStyleOptionToolButton, QWidget, QStyle, QSizePolicy, QStylePainter, QStyleOption

LITE_LARGE_BUTTON_ICON_HIGHT_RATE = 0.52
ARROW_WIDTH = 10


class SARibbonToolButton(QToolButton):
    """
    Ribbon界面适用的toolButton
    相对于普通toolbutton，主要多了两个类型设置，setButtonType 和 setLargeButtonType
    """
    def __init__(self, *_args):
        """
        __init__(parent=None)
        __init__(QAction, parent=None)
        """
        parent = None
        act: QAction = None
        arg_len = len(_args)
        if arg_len > 0 and isinstance(_args[0], QAction):
            parent = _args[1] if arg_len >= 2 else None
            act = _args[0]
        elif arg_len > 0:
            parent = _args[0]
        super().__init__(parent)

        self.m_buttonType = SARibbonToolButton.LargeButton
        self.m_largeButtonType = SARibbonToolButton.Normal
        self.m_mouseOnSubControl = False     # 用于标记MenuButtonPopup模式下，鼠标在文本区域
        self.m_menuButtonPressed = False
        self.m_iconRect = QRect()
        self.m_isWordWrap = False            # 标记是否文字换行 @default false

        if act:
            self.setDefaultAction(act)
        self.setAutoRaise(True)
        self.setButtonType(SARibbonToolButton.SmallButton)

    def buttonType(self) -> int:
        return self.m_buttonType

    def setButtonType(self, buttonType):
        self.m_buttonType = buttonType
        if SARibbonToolButton.LargeButton == buttonType:
            self.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
            self.setIconSize(QSize(32, 32))
            self.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Expanding)
        else:
            self.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
            self.setIconSize(QSize(18, 18))
            self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)

        self.setMouseTracking(True)

    def minimumSizeHint(self) -> QSize:
        return self.sizeHint()

    def setLargeButtonType(self, largeType):
        self.m_largeButtonType = largeType

    def largeButtonType(self) -> int:
        return self.m_largeButtonType

    def liteLargeButtonIconHeight(self, buttonHeight: int) -> int:
        return int(buttonHeight * LITE_LARGE_BUTTON_ICON_HIGHT_RATE)

    def calcIconRect(self, opt: QStyleOptionToolButton):
        """根据设定计算图标的绘制区域"""
        if self.LargeButton == self.m_buttonType:
            self.m_iconRect = QRect(opt.rect)   # 不能直接等于，否则m_iconRect修改会修改opt的尺寸
            if opt.toolButtonStyle != Qt.ToolButtonIconOnly:
                if self.Normal == self.m_largeButtonType:
                    self.m_iconRect.setHeight(int(opt.rect.height()/2))
                else:
                    self.m_iconRect.setHeight(self.liteLargeButtonIconHeight(opt.rect.height()))
        else:
            if opt.toolButtonStyle == Qt.ToolButtonIconOnly:
                # InstantPopup在qtoolbutton不会添加控件来放下箭头，在仅有图标的小模式显示时，预留一个下拉箭头位置
                self.m_iconRect = QRect(self.rect())
                if (opt.features & QStyleOptionToolButton.Menu) or (opt.features & QStyleOptionToolButton.HasMenu):
                    self.m_iconRect.adjust(0, 0, -ARROW_WIDTH, 0)
            else:
                self.m_iconRect = QRect(0, 0, max(opt.rect.height(), opt.iconSize.width()), opt.rect.height())

    def calcTextRect(self, *_args) -> QRect:
        """根据设定计算文本显示区域
        calcTextRect(QStyleOptionToolButton) -> QRect
        calcTextRect(QRect, hasMenu: bool=False) -> QRect
        """
        if len(_args) < 1:
            raise Exception('calcTextRect parameter len < 1')

        if len(_args) == 1 and isinstance(_args[0], QStyleOptionToolButton):
            x, y = 0, 0
            opt: QStyleOptionToolButton = _args[0]
            if opt.state & (QStyle.State_Sunken | QStyle.State_On):
                x = self.style().pixelMetric(QStyle.PM_ButtonShiftHorizontal, opt, self)
                y = self.style().pixelMetric(QStyle.PM_ButtonShiftVertical, opt, self)
            rect = self.calcTextRect(opt.rect, (opt.features & QStyleOptionToolButton.Menu) or (
                                                 opt.features & QStyleOptionToolButton.HasMenu))
            rect.translate(x, y)
            return rect

        # calcTextRect(QRect, hasMenu: bool=False) -> QRect
        buttonRect: QRect = _args[0]
        hasMenu: bool = _args[1] if len(_args) >= 2 else False
        rect = QRect(buttonRect)
        if Qt.ToolButtonTextOnly == self.toolButtonStyle() or self.icon().isNull():
            return rect

        if SARibbonToolButton.LargeButton == self.m_buttonType:
            if SARibbonToolButton.Normal == self.m_largeButtonType:
                if hasMenu and self.m_isWordWrap:
                    # 预留ARROW_WIDTH绘制箭头，1px的上下边界
                    rect.adjust(1, int(buttonRect.height()/2), -ARROW_WIDTH, -1)
                elif hasMenu:
                    # 预留ARROW_WIDTH绘制箭头，1px的上下边界
                    rect.adjust(1, int(buttonRect.height()/2), -1, -ARROW_WIDTH)
                else:
                    # 没有菜单不用预留箭头，1px的上下边界
                    rect.adjust(1, int(buttonRect.height()/2), -1, -1)
            elif self.Lite == self.m_largeButtonType:
                p2d = -ARROW_WIDTH if hasMenu else -1
                rect.adjust(1, self.liteLargeButtonIconHeight(buttonRect.height()), p2d, -1)
                # if hasMenu:
                #     rect.adjust(1, self.liteLargeButtonIconHeight(buttonRect.height()), -ARROW_WIDTH, -1)
                # else:
                #     rect.adjust(1, self.liteLargeButtonIconHeight(buttonRect.height()), -1, -1)
        else:
            if Qt.ToolButtonTextOnly != self.toolButtonStyle():
                if hasMenu:
                    rect = buttonRect.adjusted(self.m_iconRect.width(), 0, -ARROW_WIDTH, 0)
                else:
                    rect = buttonRect.adjusted(self.m_iconRect.width(), 0, -1, 0)
        return rect

    def calcIndicatorArrowDownRect(self, opt: QStyleOptionToolButton) -> QRect:
        """sub control 的下拉箭头的位置"""
        rect = opt.rect
        if SARibbonToolButton.LargeButton == self.m_buttonType:
            if SARibbonToolButton.Normal == self.m_largeButtonType and self.m_isWordWrap:
                rect.adjust(rect.width()-ARROW_WIDTH, int(rect.height()/2), 1, 1)
            elif SARibbonToolButton.Normal == self.m_largeButtonType:
                rect.adjust(1, rect.height()-ARROW_WIDTH, 1, 1)
            else:
                rect.adjust(rect.width()-ARROW_WIDTH, self.liteLargeButtonIconHeight(opt.rect.height()), 1, 1)
        else:
            rect.adjust(rect.width()-ARROW_WIDTH, 1, 1, 1)
        return rect

    def createIconPixmap(self, opt: QStyleOptionToolButton) -> QPixmap:
        if not opt.icon.isNull():  # 有图标
            state = QIcon.On if opt.state & QStyle.State_On else QIcon.Off
            if not (opt.state & QStyle.State_Enabled):
                mode = QIcon.Disabled
            elif (opt.state & QStyle.State_MouseOver) and (opt.state & QStyle.State_AutoRaise):
                mode = QIcon.Active
            else:
                mode = QIcon.Normal
            return opt.icon.pixmap(self.window().windowHandle(), opt.rect.size().boundedTo(opt.iconSize), mode, state)
        return QPixmap()

    def paintLargeButton(self, e: QEvent):
        p = QStylePainter(self)
        opt = QStyleOptionToolButton()
        self.initStyleOption(opt)
        if (opt.features & QStyleOptionToolButton.MenuButtonPopup) or (opt.features & QStyleOptionToolButton.HasMenu):
            if not self.rect().contains(self.mapFromGlobal(QCursor.pos())):
                opt.state = opt.state & ~QStyle.State_MouseOver

        autoRaise = opt.state & QStyle.State_AutoRaise
        bflags = opt.state & ~QStyle.State_Sunken
        mflags = bflags
        if autoRaise and (not (bflags & QStyle.State_MouseOver) or not (bflags & QStyle.State_Enabled)):
            bflags = bflags & ~QStyle.State_Raised
        if opt.state & QStyle.State_Sunken:
            if opt.activeSubControls & QStyle.SC_ToolButton:
                bflags |= QStyle.State_Sunken
                mflags |= QStyle.State_Sunken | QStyle.State_MouseOver
            elif opt.activeSubControls & QStyle.SC_ToolButtonMenu:
                bflags |= QStyle.State_Sunken
                mflags |= QStyle.State_MouseOver
        # 绘制背景
        tool = QStyleOption(0)
        tool.palette = opt.palette
        if (opt.subControls & QStyle.SC_ToolButton) and (opt.features & QStyleOptionToolButton.MenuButtonPopup):
            tool.rect = opt.rect
            tool.state = opt.state
            opt.activeSubControls &= QStyle.SC_ToolButtonMenu
            if opt.activeSubControls:
                # 菜单激活
                self.style().drawPrimitive(QStyle.PE_PanelButtonTool, tool, p, self)
                tool.rect = self.m_iconRect.adjusted(1, 1, -1, -1)
                tool.state = QStyle.State_Raised    # 把图标区域显示为正常
                drawStyle = QStyle.PE_PanelButtonTool if autoRaise else QStyle.PE_PanelButtonBevel
                self.style().drawPrimitive(drawStyle, tool, p, self)
            else:
                self.style().drawPrimitive(QStyle.PE_PanelButtonTool, tool, p, self)
                if tool.state & QStyle.State_MouseOver:
                    if self.m_mouseOnSubControl:
                        # 鼠标在文字区，把图标显示为正常
                        tool.rect = self.m_iconRect.adjusted(1, 1, -1, -1)
                        tool.state = QStyle.State_Raised  # 把图标区域显示为正常
                        drawStyle = QStyle.PE_PanelButtonTool if autoRaise else QStyle.PE_PanelButtonBevel
                        self.style().drawPrimitive(drawStyle, tool, p, self)
                    else:
                        # 鼠标在图标区，把文字显示为正常
                        tool.rect = self.m_iconRect.adjusted(self.m_iconRect.width()+1, 1, -1, -1)
                        tool.state = QStyle.State_Raised  # 把图标区域显示为正常
                        drawStyle = QStyle.PE_PanelButtonTool if autoRaise else QStyle.PE_PanelButtonBevel
                        self.style().drawPrimitive(drawStyle, tool, p, self)
        elif (opt.subControls & QStyle.SC_ToolButton) and (opt.features & QStyleOptionToolButton.HasMenu):
            tool.rect = QRect(opt.rect)
            tool.state = bflags
            drawStyle = QStyle.PE_PanelButtonTool if autoRaise else QStyle.PE_PanelButtonBevel
            self.style().drawPrimitive(drawStyle, tool, p, self)
        elif opt.subControls & QStyle.SC_ToolButton:
            tool.rect = QRect(opt.rect)
            tool.state = bflags
            if opt.state & QStyle.State_Sunken:
                tool.state = tool.state & ~QStyle.State_MouseOver
            drawStyle = QStyle.PE_PanelButtonTool if autoRaise else QStyle.PE_PanelButtonBevel
            self.style().drawPrimitive(drawStyle, tool, p, self)

        self.drawIconAndLabel(p, opt)

    def paintSmallButton(self, e: QEvent):
        p = QStylePainter(self)
        opt = QStyleOptionToolButton()
        self.initStyleOption(opt)
        if (opt.features & QStyleOptionToolButton.MenuButtonPopup) or (opt.features & QStyleOptionToolButton.HasMenu):
            if not self.rect().contains(self.mapFromGlobal(QCursor.pos())):
                opt.state = opt.state & ~QStyle.State_MouseOver

        autoRaise = bool(opt.state & QStyle.State_AutoRaise)
        bflags = opt.state & ~QStyle.State_Sunken
        if autoRaise and (not (bflags & QStyle.State_MouseOver) or not (bflags & QStyle.State_Enabled)):
            bflags = bflags & ~QStyle.State_Raised
        if opt.state & QStyle.State_Sunken:
            if opt.activeSubControls & QStyle.SC_ToolButton:
                bflags = bflags | QStyle.State_Sunken
            elif opt.activeSubControls & QStyle.SC_ToolButtonMenu:
                bflags = bflags | QStyle.State_MouseOver
        # 绘制背景
        tool = QStyleOption(0)
        tool.palette = opt.palette
        if (opt.subControls & QStyle.SC_ToolButton) and (opt.features & QStyleOptionToolButton.MenuButtonPopup):
            tool.rect = QRect(opt.rect)
            tool.state = bflags
            opt.activeSubControls = QStyle.SC_ToolButtonMenu & opt.activeSubControls
            if opt.activeSubControls:
                # 菜单激活
                self.style().drawPrimitive(QStyle.PE_PanelButtonTool, tool, p, self)
                tool.rect = self.m_iconRect.adjusted(1, 1, -1, -1)
                tool.state = QStyle.State_Raised  # 把图标区域显示为正常
                drawStyle = QStyle.PE_PanelButtonTool if autoRaise else QStyle.PE_PanelButtonBevel
                self.style().drawPrimitive(drawStyle, tool, p, self)
            else:
                self.style().drawPrimitive(QStyle.PE_PanelButtonTool, tool, p, self)
                if tool.state & QStyle.State_MouseOver:
                    if self.m_mouseOnSubControl:
                        # 鼠标在文字区，把图标显示为正常
                        tool.rect = self.m_iconRect.adjusted(1, 1, -1, -1)
                        tool.state = QStyle.State_Raised  # 把图标区域显示为正常
                        drawStyle = QStyle.PE_PanelButtonTool if autoRaise else QStyle.PE_PanelButtonBevel
                        self.style().drawPrimitive(drawStyle, tool, p, self)
                    else:
                        # 鼠标在图标区，把文字显示为正常
                        tool.rect = self.m_iconRect.adjusted(self.m_iconRect.width()+1, 1, -1, -1)
                        tool.state = QStyle.State_Raised  # 把图标区域显示为正常
                        drawStyle = QStyle.PE_PanelButtonTool if autoRaise else QStyle.PE_PanelButtonBevel
                        self.style().drawPrimitive(drawStyle, tool, p, self)
        elif (opt.subControls & QStyle.SC_ToolButton) and (opt.features & QStyleOptionToolButton.HasMenu):
            tool.rect = QRect(opt.rect)
            tool.state = bflags
            drawStyle = QStyle.PE_PanelButtonTool if autoRaise else QStyle.PE_PanelButtonBevel
            self.style().drawPrimitive(drawStyle, tool, p, self)
        elif opt.subControls & QStyle.SC_ToolButton:
            tool.rect = QRect(opt.rect)
            tool.state = bflags
            if opt.state & QStyle.State_Sunken:
                tool.state = tool.state & ~QStyle.State_MouseOver
            drawStyle = QStyle.PE_PanelButtonTool if autoRaise else QStyle.PE_PanelButtonBevel
            self.style().drawPrimitive(drawStyle, tool, p, self)

        self.drawIconAndLabel(p, opt)

    def drawIconAndLabel(self, p: QPainter, opt: QStyleOptionToolButton):
        """
        在LargeButtonType == Normal模式下，icon占大按钮的一半区域，
        在wps模式下，icon占大按钮的60%，文字占40%，且文字不换行
        """
        self.calcIconRect(opt)
        pm = self.createIconPixmap(opt)
        if self.m_buttonType == SARibbonToolButton.LargeButton:
            # 绘制图标和文字
            textRect = self.calcTextRect(opt)
            hasArrow = opt.features & QStyleOptionToolButton.Arrow
            if ((not hasArrow) and opt.icon.isNull() and opt.text) or opt.toolButtonStyle == Qt.ToolButtonTextOnly:
                # 只有文字模式
                p.setFont(opt.font)
                alignment = Qt.AlignCenter | Qt.TextShowMnemonic | Qt.TextWordWrap  # 纯文本下，居中对齐,换行
                if not self.style().styleHint(QStyle.SH_UnderlineShortcut, opt, self):
                    alignment |= Qt.TextHideMnemonic
                self.style().drawItemText(p, textRect, alignment, opt.palette,
                                          opt.state & QStyle.State_Enabled, opt.text, QPalette.ButtonText)
                return
            if opt.toolButtonStyle != Qt.ToolButtonIconOnly:
                # 文本加图标情况
                p.setFont(opt.font)
                alignment = Qt.TextShowMnemonic | Qt.TextWordWrap   # 换行
                if not self.style().styleHint(QStyle.SH_UnderlineShortcut, opt, self):
                    alignment |= Qt.TextHideMnemonic
                # 文字在icon下，先绘制图标
                if not hasArrow:
                    self.style().drawItemPixmap(p, self.m_iconRect, Qt.AlignCenter, pm)
                else:
                    self.drawArrow(self.style(), opt, self.m_iconRect, p, self)
                if self.m_largeButtonType == SARibbonToolButton.Normal:
                    alignment = (Qt.AlignHCenter | Qt.AlignTop) | alignment
                else:
                    alignment |= Qt.AlignCenter
                # 再绘制文本，对于Normal模式下的Largebutton，如果有菜单，箭头将在文本旁边
                self.style().drawItemText(p, QStyle.visualRect(opt.direction, opt.rect, textRect), alignment, opt.palette,
                                          opt.state & QStyle.State_Enabled, opt.text, QPalette.ButtonText)
            else:
                # 只有图标情况
                if not hasArrow:
                    self.style().drawItemPixmap(p, self.m_iconRect, Qt.AlignCenter, pm)
                else:
                    self.drawArrow(self.style(), opt, opt.rect, p, self)
            # 绘制sub control 的下拉箭头
            if opt.features & QStyleOptionToolButton.HasMenu:
                opt.rect = self.calcIndicatorArrowDownRect(opt)
                self.style().drawPrimitive(QStyle.PE_IndicatorArrowDown, opt, p, self)
        else:
            if opt.icon.isNull():
                # 只有文字
                alignment = Qt.TextShowMnemonic
                if not self.style().styleHint(QStyle.SH_UnderlineShortcut, opt, self):
                    alignment |= Qt.TextHideMnemonic
                self.style().drawItemText(p, QStyle.visualRect(opt.direction, opt.rect, opt.rect.adjusted(2, 1, -2, -1)),
                                          alignment, opt.palette, opt.state & QStyle.State_Enabled,
                                          opt.text, QPalette.ButtonText)
            elif opt.toolButtonStyle != Qt.ToolButtonIconOnly:
                # 文本加图标情况
                # pmSize = pm.size() / pm.devicePixelRatio()
                p.save()
                p.setFont(opt.font)
                pr = self.m_iconRect    # 图标区域
                tr = opt.rect.adjusted(pr.width()+2, 0, -1, 0)  # 文本区域

                alignment = Qt.TextShowMnemonic
                if not self.style().styleHint(QStyle.SH_UnderlineShortcut, opt, self):
                    alignment |= Qt.TextHideMnemonic
                # ribbonbutton在小图标下，不支持ToolButtonTextUnderIcon
                if opt.toolButtonStyle != Qt.ToolButtonTextUnderIcon:
                    self.style().drawItemPixmap(p, QStyle.visualRect(opt.direction, opt.rect, pr), Qt.AlignCenter, pm)
                    alignment = (Qt.AlignLeft | Qt.AlignVCenter) | alignment
                # 绘制文本
                self.style().drawItemText(p, QStyle.visualRect(opt.direction, opt.rect, tr), alignment, opt.palette,
                                          opt.state & QStyle.State_Enabled, opt.text, QPalette.ButtonText)
                p.restore()
            else:
                # 只有图标情况
                self.style().drawItemPixmap(p, self.m_iconRect, Qt.AlignCenter, pm)

            # 绘制sub control 的下拉箭头
            if opt.features & QStyleOptionToolButton.HasMenu:
                opt.rect = self.calcIndicatorArrowDownRect(opt)
                self.style().drawPrimitive(QStyle.PE_IndicatorArrowDown, opt, p, self)

    def hitButton(self, pos: QPoint) -> bool:
        if super().hitButton(pos):
            return not self.m_menuButtonPressed
        return False

    def sizeHint(self) -> QSize:
        s = super().sizeHint()
        opt = QStyleOptionToolButton()
        self.initStyleOption(opt)
        if self.LargeButton == self.buttonType():
            # 计算最佳大小
            if s.width() > s.height() * 1.4:
                alignment = Qt.TextShowMnemonic | Qt.TextWordWrap
                fm = self.fontMetrics()
                textRange = self.calcTextRect(QRect(0, 0, int(s.width() / 2), s.height()))
                textRange.moveTo(0, 0)
                textRange = fm.boundingRect(textRange, alignment, self.text())
                s.setWidth(textRange.width()+4)
                self.m_isWordWrap = textRange.height() > fm.lineSpacing()
                if (opt.features & QStyleOptionToolButton.Menu) or (opt.features & QStyleOptionToolButton.HasMenu):
                    # 如果有菜单
                    if self.largeButtonType() == self.Lite or self.m_isWordWrap:
                        s.setWidth(s.width()+ARROW_WIDTH)
            else:
                self.m_isWordWrap = '\n' in self.text()
                if (opt.features & QStyleOptionToolButton.Menu) or (opt.features & QStyleOptionToolButton.HasMenu):
                    # 如果有菜单
                    if self.largeButtonType() == self.Normal and self.m_isWordWrap:
                        s.setWidth(s.width()+ARROW_WIDTH)
        else:
            # 在仅有图标的小模式显示时，预留一个下拉箭头位置
            if self.toolButtonStyle() == Qt.ToolButtonIconOnly:
                if (opt.features & QStyleOptionToolButton.Menu) or (opt.features & QStyleOptionToolButton.HasMenu):
                    s.setWidth(s.width()+ARROW_WIDTH)
            else:
                if not ((opt.features & QStyleOptionToolButton.Menu) or (opt.features & QStyleOptionToolButton.HasMenu)):
                    s.setWidth(s.width()-4)
        # print(__file__, 'size hint', s)
        return s

    # 事件
    def event(self, e: QEvent) -> bool:
        eList = [
            QEvent.WindowDeactivate,
            QEvent.ActionChanged,
            QEvent.ActionRemoved,
            QEvent.ActionAdded,
        ]
        if e.type() in eList:
            self.m_mouseOnSubControl = False
        return super().event(e)

    def paintEvent(self, e: QEvent):
        if self.m_buttonType == self.LargeButton:
            self.paintLargeButton(e)
        elif self.m_buttonType == self.SmallButton:
            self.paintSmallButton(e)

    def resizeEvent(self, e):
        super().resizeEvent(e)

    def mouseMoveEvent(self, e):
        if self.m_buttonType == self.LargeButton:
            isMouseOnSubControl = e.pos().y() > (self.height() / 2)
        else:
            isMouseOnSubControl = not self.m_iconRect.contains(e.pos())
        if self.m_mouseOnSubControl != isMouseOnSubControl:
            self.m_mouseOnSubControl = isMouseOnSubControl
            self.update()
        super().mouseMoveEvent(e)

    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton and self.popupMode() == QToolButton.MenuButtonPopup:
            if self.m_buttonType == self.LargeButton:
                popupr = self.rect().adjusted(0, int(self.height() / 2), 0, 0)
                if popupr.isValid() and popupr.contains(e.pos()):
                    self.m_menuButtonPressed = True
                    self.showMenu()
                    return
            elif self.m_iconRect.isValid() and not self.m_iconRect.contains(e.pos()):
                self.m_menuButtonPressed = True
                self.showMenu()
                return

        self.m_menuButtonPressed = False
        super().mousePressEvent(e)

    def mouseReleaseEvent(self, e):
        self.m_menuButtonPressed = False
        super().mouseReleaseEvent(e)

    def focusOutEvent(self, e):
        self.m_mouseOnSubControl = False
        super().focusOutEvent(e)

    def leaveEvent(self, e):
        self.m_mouseOnSubControl = False
        super().leaveEvent(e)

    @staticmethod
    def drawArrow(style: QStyle, opt: QStyleOptionToolButton, rect: QRect,
                  painter: QPainter, widget: QWidget = None):
        if opt.arrowType == Qt.LeftArrow:
            pe = QStyle.PE_IndicatorArrowLeft
        elif opt.arrowType == Qt.RightArrow:
            pe = QStyle.PE_IndicatorArrowRight
        elif opt.arrowType == Qt.UpArrow:
            pe = QStyle.PE_IndicatorArrowUp
        elif opt.arrowType == Qt.DownArrow:
            pe = QStyle.PE_IndicatorArrowDown
        else:
            return
        opt.rect = rect
        style.drawPrimitive(pe, opt, painter, widget)

    LargeButton = 0     # 按钮样式
    SmallButton = 1     # 按钮样式
    Normal = 0          # LargeButton的显示样式，仅在LargeButton模式下，有mean的情况生效
    Lite = 1            # LargeButton的显示样式，仅在LargeButton模式下，有mean的情况生效


if __name__ == '__main__':
    from PyQt5.QtWidgets import QApplication
    from SAWidgets.SARibbonMenu import SARibbonMenu

    app = QApplication([])
    mainWindow = QWidget()

    menu = SARibbonMenu(mainWindow)
    menu.addAction(QIcon("../resource/icon/folder.png"), '1')
    menu.addAction(QIcon("../resource/icon/folder.png"), '2')
    menu.addAction(QIcon("../resource/icon/folder.png"), '3')

    # act = QAction('Test', mainWindow)
    btn = SARibbonToolButton(mainWindow)
    btn.setFocusPolicy(Qt.NoFocus)
    # btn.setButtonType(SARibbonToolButton.SmallButton)
    btn.setButtonType(SARibbonToolButton.LargeButton)
    btn.setLargeButtonType(SARibbonToolButton.Normal)
    # btn.setDefaultAction(act)
    btn.setMenu(menu)

    btn.setText('un format icon')
    btn.setIcon(QIcon('../resource/icon/folder.png'))
    btn.setFixedHeight(78)
    btn.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
    btn.setPopupMode(QToolButton.MenuButtonPopup)

    mainWindow.setMinimumWidth(50)
    mainWindow.show()
    app.exec()
