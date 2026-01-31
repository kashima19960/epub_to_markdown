"""EPUB 到 Markdown 命令行接口模块。

提供命令行方式使用转换功能。

Usage:
    python -m epub_converter.cli input.epub [-o output.md] [--no-images] [--gui]

Example:
    $ python -m epub_converter.cli book.epub
    $ python -m epub_converter.cli book.epub -o my_book.md --no-images
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Optional
from typing import Sequence

from epub_converter.converter import ConversionOptions
from epub_converter.converter import EpubToMarkdownConverter
from epub_converter.utils import get_default_output_path


def create_parser() -> argparse.ArgumentParser:
    """创建命令行参数解析器。

    Returns:
        配置好的 ArgumentParser 实例。
    """
    parser = argparse.ArgumentParser(
        prog='epub2md',
        description='将 EPUB 电子书转换为 Markdown 格式',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
示例:
    epub2md book.epub
    epub2md book.epub -o output.md
    epub2md book.epub --no-images
    epub2md --gui

更多信息请访问: https://github.com/kashima19960/epub_to_markdown
        '''
    )

    parser.add_argument(
        'epub_file',
        nargs='?',
        type=str,
        help='EPUB 文件路径'
    )

    parser.add_argument(
        '-o', '--output',
        type=str,
        dest='output_file',
        help='输出 Markdown 文件路径（默认与输入文件同名）'
    )

    parser.add_argument(
        '--no-images',
        action='store_true',
        dest='no_images',
        help='不提取图片'
    )

    parser.add_argument(
        '--no-toc',
        action='store_true',
        dest='no_toc',
        help='不生成目录'
    )

    parser.add_argument(
        '--gui',
        action='store_true',
        help='启动图形界面'
    )

    parser.add_argument(
        '-v', '--version',
        action='version',
        version='%(prog)s 2.0.0'
    )

    return parser


def print_progress(percentage: int, message: str) -> None:
    """打印进度信息。

    Args:
        percentage: 进度百分比。
        message: 状态消息。
    """
    bar_length = 30
    filled = int(bar_length * percentage / 100)
    bar = '█' * filled + '░' * (bar_length - filled)
    print(f'\r[{bar}] {percentage:3d}% {message}', end='', flush=True)
    if percentage == 100:
        print()


def run_cli(args: argparse.Namespace) -> int:
    """执行 CLI 转换。

    Args:
        args: 解析后的命令行参数。

    Returns:
        退出码，0 表示成功。
    """
    # 检查是否启动 GUI
    if args.gui:
        return launch_gui()

    # 检查输入文件
    if not args.epub_file:
        print('错误: 请指定 EPUB 文件路径，或使用 --gui 启动图形界面')
        print('使用 --help 查看帮助信息')
        return 1

    epub_path = Path(args.epub_file)

    if not epub_path.exists():
        print(f'错误: 文件不存在 - {epub_path}')
        return 1

    if epub_path.suffix.lower() != '.epub':
        print(f'错误: 不是有效的 EPUB 文件 - {epub_path}')
        return 1

    # 确定输出路径
    if args.output_file:
        output_path = Path(args.output_file)
    else:
        output_path = get_default_output_path(epub_path)

    # 配置选项
    options = ConversionOptions(
        extract_images=not args.no_images,
        generate_toc=not args.no_toc
    )

    print(f'正在转换: {epub_path.name}')
    print(f'输出文件: {output_path}')
    print()

    try:
        converter = EpubToMarkdownConverter(epub_path, options)
        result = converter.save(output_path, progress_callback=print_progress)

        print()
        if result.success:
            print(f'✓ 转换成功！')
            print(f'  Markdown 文件: {result.markdown_path}')
            if result.image_count > 0:
                print(f'  提取图片: {result.image_count} 张')
            return 0
        else:
            print(f'✗ 转换失败: {result.error_message}')
            return 1

    except FileNotFoundError as e:
        print(f'错误: {e}')
        return 1
    except Exception as e:
        print(f'错误: 转换过程中发生异常 - {e}')
        return 1


def launch_gui() -> int:
    """启动图形界面。

    Returns:
        退出码。
    """
    try:
        from epub_converter.gui import main as gui_main
        return gui_main()
    except ImportError as e:
        print('错误: 无法启动图形界面')
        print('请确保已安装 PySide6: pip install PySide6')
        print(f'详细信息: {e}')
        return 1


def main(argv: Optional[Sequence[str]] = None) -> int:
    """CLI 主入口函数。

    Args:
        argv: 命令行参数列表，None 表示使用 sys.argv[1:]。

    Returns:
        退出码。
    """
    parser = create_parser()
    args = parser.parse_args(argv)
    return run_cli(args)


if __name__ == '__main__':
    sys.exit(main())
