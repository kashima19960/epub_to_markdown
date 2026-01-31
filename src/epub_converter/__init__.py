"""EPUB to Markdown 转换器包。

该包提供将 EPUB 电子书转换为 Markdown 格式的功能，
支持命令行和图形界面两种使用方式。

Typical usage example:

    from epub_converter import EpubToMarkdownConverter

    converter = EpubToMarkdownConverter('book.epub')
    converter.save('output.md')
"""

from epub_converter.converter import BookMetadata
from epub_converter.converter import ConversionOptions
from epub_converter.converter import ConversionResult
from epub_converter.converter import EpubToMarkdownConverter

__version__ = '2.0.0'
__author__ = 'kashima19960'
__all__ = [
    'EpubToMarkdownConverter',
    'ConversionResult',
    'ConversionOptions',
    'BookMetadata',
]
