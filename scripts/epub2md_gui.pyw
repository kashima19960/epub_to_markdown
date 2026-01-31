#!/usr/bin/env pythonw
"""EPUB 转 Markdown 图形界面工具入口脚本。

Windows 下使用 .pyw 扩展名以隐藏控制台窗口。
这是专为普通用户设计的图形界面入口。

Usage:
    双击此文件即可启动图形界面。
"""

import sys
from pathlib import Path

# 将 src 目录添加到 Python 路径
src_dir = Path(__file__).parent.parent / 'src'
sys.path.insert(0, str(src_dir))

from epub_converter.gui import main


if __name__ == '__main__':
    sys.exit(main())
