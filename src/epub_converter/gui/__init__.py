"""EPUB 转换器图形用户界面包。

使用 PySide6 实现的现代化图形界面，面向普通用户设计。
"""

from __future__ import annotations

import sys


def main() -> int:
    """GUI 主入口函数。

    Returns:
        应用程序退出码。
    """
    try:
        from PySide6.QtWidgets import QApplication

        from epub_converter.gui.main_window import MainWindow

        app = QApplication(sys.argv)
        app.setApplicationName('EPUB to Markdown')
        app.setApplicationVersion('2.0.0')

        window = MainWindow()
        window.show()

        return app.exec()
    except ImportError as e:
        print(f'错误: 无法导入 PySide6 - {e}')
        print('请安装 PySide6: pip install PySide6')
        return 1


if __name__ == '__main__':
    sys.exit(main())
