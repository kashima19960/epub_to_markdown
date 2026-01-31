"""工具函数模块。

提供文件操作、路径处理等通用工具函数。
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from typing import Optional


def get_default_output_path(epub_path: Path) -> Path:
    """根据 EPUB 文件路径生成默认的输出路径。

    Args:
        epub_path: EPUB 文件路径。

    Returns:
        输出 Markdown 文件路径。
    """
    return epub_path.with_suffix('.md')


def open_file_location(file_path: Path) -> bool:
    """在系统文件管理器中打开文件所在位置。

    Args:
        file_path: 文件路径。

    Returns:
        是否成功打开。
    """
    try:
        folder_path = file_path.parent if file_path.is_file() else file_path

        if sys.platform == 'win32':
            # Windows: 使用 explorer 并选中文件
            if file_path.is_file():
                subprocess.run(['explorer', '/select,', str(file_path)])
            else:
                os.startfile(str(folder_path))
        elif sys.platform == 'darwin':
            # macOS
            subprocess.run(['open', str(folder_path)])
        else:
            # Linux
            subprocess.run(['xdg-open', str(folder_path)])
        return True
    except Exception:
        return False


def open_file(file_path: Path) -> bool:
    """使用系统默认程序打开文件。

    Args:
        file_path: 文件路径。

    Returns:
        是否成功打开。
    """
    try:
        if sys.platform == 'win32':
            os.startfile(str(file_path))
        elif sys.platform == 'darwin':
            subprocess.run(['open', str(file_path)])
        else:
            subprocess.run(['xdg-open', str(file_path)])
        return True
    except Exception:
        return False


def format_file_size(size_bytes: int) -> str:
    """格式化文件大小为人类可读格式。

    Args:
        size_bytes: 文件大小（字节）。

    Returns:
        格式化后的字符串。
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f'{size_bytes:.1f} {unit}'
        size_bytes /= 1024
    return f'{size_bytes:.1f} TB'


def is_valid_epub(file_path: Path) -> bool:
    """检查文件是否是有效的 EPUB 文件。

    Args:
        file_path: 文件路径。

    Returns:
        是否是有效的 EPUB 文件。
    """
    if not file_path.exists():
        return False
    if not file_path.is_file():
        return False
    if file_path.suffix.lower() != '.epub':
        return False
    return True


def ensure_unique_path(file_path: Path) -> Path:
    """确保文件路径唯一，如果存在则添加数字后缀。

    Args:
        file_path: 原始文件路径。

    Returns:
        唯一的文件路径。
    """
    if not file_path.exists():
        return file_path

    stem = file_path.stem
    suffix = file_path.suffix
    parent = file_path.parent

    counter = 1
    while True:
        new_path = parent / f'{stem}_{counter}{suffix}'
        if not new_path.exists():
            return new_path
        counter += 1
