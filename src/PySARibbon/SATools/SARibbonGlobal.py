# -*- coding: utf-8 -*-
"""
@Module     SARibbonGlobal
@Author     ROOT
"""

# ribbon的数字版本
SA_RIBBON_BAR_VERSION = 0.1

# ribbon 的文字版本
SA_RIBBON_BAR_VERSION_STR = '0.1'

"""
@def 属性，用于标记是否可以进行自定义，用于动态设置到@ref SARibbonCategory 和@ref SARibbonPannel
值为bool，在为true时，可以通过@ref SARibbonCustomizeWidget 改变这个SARibbonCategory和SARibbonPannel的布局，
默认不会有此属性，仅在有此属性且为true时才会在SARibbonCustomizeWidget中能显示为可设置
"""
SA_RIBBON_BAR_PROP_CAN_CUSTOMIZE = '_sa_isCanCustomize'
