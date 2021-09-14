# -*- coding: utf-8 -*-
"""
@Module     SARibbonElementManager
@Author     ROOT

@brief 此类是一个全局单例，用于管理SARibbonElementCreateDelegate
"""

from .SARibbonElementCreateDelegate import SARibbonElementCreateDelegate


class SARibbonElementManager:
    def __init__(self):
        self.m_delegate: SARibbonElementCreateDelegate = SARibbonElementCreateDelegate()

    def delegate(self) -> SARibbonElementCreateDelegate:
        return self.m_delegate

    def setupDelegate(self, delegate: SARibbonElementCreateDelegate):
        self.m_delegate = delegate


# 定义全局单例

RibbonSubElementMgr = SARibbonElementManager()

RibbonSubElementDelegate = RibbonSubElementMgr.delegate()

RibbonSubElementStyleOpt = RibbonSubElementDelegate.getRibbonStyleOption()
