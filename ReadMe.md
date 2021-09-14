# 简介

 本项目是基于[尘中远](https://gitee.com/czyt1988)的一个轻量级的Ribbon控件([SARibbon](https://gitee.com/czyt1988/SARibbon))移植的pyqt版本，功能与原版本基本保持一致
 
 界面截图也基本相似：

![](https://cdn.jsdelivr.net/gh/czyt1988/SARibbon/doc/screenshot/001.gif)

MIT协议，欢迎大家使用并提出意见

[gitee(码云) - https://gitee.com/sardkit/saribbon-pyqt5](https://gitee.com/sardkit/saribbon-pyqt5)

 它理论支持4种目前常见的ribbon样式在线切换（目前只测试了3行office模式，其余未进行测试）

 包括2种office模式，office模式是最常见的ribbon模式了，就是我们经常看到的word模式，office模式的tab和标题栏占用位置较多。

![](https://cdn.jsdelivr.net/gh/czyt1988/SARibbon/doc/screenshot/office-mode.png)

 另两种参考wps设计的wps模式，wps模式是office模式的改良版，它为了减小ribbon的高度，把标签和标题栏设置在一起
 
![](https://cdn.jsdelivr.net/gh/czyt1988/SARibbon/doc/screenshot/wps-mode.png)

 office模式和wps模式都支持两行和3行设计，满足不同界面需求。

# 使用方法

可以把整个目录移动到需要的工程目录下，然后在项目的文件中`import PySARibbonBar`或`from PySARibbonBar import *`即可，
引用实用类示例如下：

```Python
from PySARibbonBar import SARibbonMainWindow
```


# 更多截图(copy自原Qt项目，有些暂未实现)

![](https://cdn.jsdelivr.net/gh/czyt1988/SARibbon/doc/screenshot/SARibbonBar-screenshot-01.gif)

- 支持quickAccessBar（word快速菜单），在wps模式和office模式下会有不同的显示效果

![](https://cdn.jsdelivr.net/gh/czyt1988/SARibbon/doc/screenshot/SARibbonBar-screenshot-quickAccessBar.gif)

- 支持4种不同的ribbon button，普通按钮，延迟弹出菜单按钮，菜单按钮，action菜单按钮（action菜单按钮是此ribbon控件最主要解决的问题之一）

![](https://cdn.jsdelivr.net/gh/czyt1988/SARibbon/doc/screenshot/SARibbonBar-screenshot-ribbonbutton.gif)

- 支持qss对ribbon进行设置

![](https://cdn.jsdelivr.net/gh/czyt1988/SARibbon/doc/screenshot/SARibbonBar-screenshot-useqss.gif)


# 题外

大部分代码是根据C++进行移植的，也有少部分对代码结构进行了更改；

更多相关功能可看Qt原作者相关其他项目，欢迎有兴趣的朋友一起完善本项目

# 计划及进度

## 计划

- 实现C++ Qt版本定制化功能

## 已知bug

- 暂未完全测试

## 已解决

- 略

# 其他

> 无