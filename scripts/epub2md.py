#!/usr/bin/env python3
"""EPUB 转 Markdown 命令行工具入口脚本。

这是命令行工具的主入口点。支持直接转换 EPUB 文件，
也可以通过 --gui 参数启动图形界面。

Usage:
    python epub2md.py <epub_file> [-o output.md] [options]
    python epub2md.py --gui

Example:
    # 转换文件
    python epub2md.py book.epub

    # 指定输出路径
    python epub2md.py book.epub -o /path/to/output.md

    # 不提取图片
    python epub2md.py book.epub --no-images

    # 启动图形界面
    python epub2md.py --gui
"""

import sys
from pathlib import Path

# 将 src 目录添加到 Python 路径
src_dir = Path(__file__).parent.parent / 'src'
sys.path.insert(0, str(src_dir))

from epub_converter.cli import main


if __name__ == '__main__':
    sys.exit(main())
