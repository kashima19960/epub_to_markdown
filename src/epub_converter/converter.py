"""EPUB 到 Markdown 核心转换器模块。

本模块提供 EPUB 文件解析和 Markdown 格式转换的核心功能。
支持提取图片、生成目录、识别章节标题等功能。

Typical usage example:

    converter = EpubToMarkdownConverter('/path/to/book.epub')
    result = converter.save('/path/to/output.md')
    
    # 或者只获取 Markdown 内容
    markdown_content = converter.convert()
"""

from __future__ import annotations

import os
import re
import warnings
from dataclasses import dataclass
from dataclasses import field
from pathlib import Path
from typing import Callable
from typing import Optional
from typing import Union

import ebooklib
from bs4 import BeautifulSoup
from bs4 import NavigableString
from bs4 import Tag
from bs4 import XMLParsedAsHTMLWarning
from ebooklib import epub

# 忽略 XML 作为 HTML 解析的警告
warnings.filterwarnings('ignore', category=XMLParsedAsHTMLWarning)


@dataclass
class BookMetadata:
    """书籍元数据。

    Attributes:
        title: 书籍标题。
        author: 作者。
        language: 语言。
        publisher: 出版商。
        description: 描述。
    """

    title: Optional[str] = None
    author: Optional[str] = None
    language: Optional[str] = None
    publisher: Optional[str] = None
    description: Optional[str] = None

    def to_dict(self) -> dict[str, str]:
        """转换为字典格式。

        Returns:
            包含非空字段的字典。
        """
        result = {}
        if self.title:
            result['title'] = self.title
        if self.author:
            result['author'] = self.author
        if self.language:
            result['language'] = self.language
        if self.publisher:
            result['publisher'] = self.publisher
        if self.description:
            result['description'] = self.description
        return result


@dataclass
class ConversionOptions:
    """转换选项配置。

    Attributes:
        extract_images: 是否提取图片。
        generate_toc: 是否生成目录。
        image_dir: 图片输出目录名。
    """

    extract_images: bool = True
    generate_toc: bool = True
    image_dir: str = 'images'


@dataclass
class ConversionResult:
    """转换结果数据类。

    Attributes:
        success: 转换是否成功。
        markdown_path: 生成的 Markdown 文件路径。
        image_count: 提取的图片数量。
        error_message: 错误信息（如果失败）。
    """

    success: bool
    markdown_path: Optional[Path] = None
    image_count: int = 0
    error_message: Optional[str] = None


@dataclass
class TocItem:
    """目录项。

    Attributes:
        title: 标题。
        href: 链接地址。
        level: 层级（1 为顶级）。
    """

    title: str
    href: str
    level: int


class EpubToMarkdownConverter:
    """EPUB 到 Markdown 转换器。

    该类负责读取 EPUB 文件，解析其内容，并转换为 Markdown 格式。
    支持提取图片、生成目录、识别章节标题等功能。

    Attributes:
        epub_path: EPUB 文件路径。
        options: 转换选项。

    Example:
        >>> converter = EpubToMarkdownConverter('book.epub')
        >>> result = converter.save('output.md')
        >>> print(result.success)
        True
    """

    def __init__(
        self,
        epub_path: Union[str, Path],
        options: Optional[ConversionOptions] = None
    ) -> None:
        """初始化转换器。

        Args:
            epub_path: EPUB 文件的路径。
            options: 转换选项，为 None 时使用默认选项。

        Raises:
            FileNotFoundError: 如果 EPUB 文件不存在。
        """
        self.epub_path = Path(epub_path)
        if not self.epub_path.exists():
            raise FileNotFoundError(f'EPUB 文件不存在: {epub_path}')

        self.options = options or ConversionOptions()
        self._book: Optional[epub.EpubBook] = None
        self._markdown_content: list[str] = []
        self._images: dict[str, dict] = {}
        self._toc: list[TocItem] = []
        self._href_to_title: dict[str, dict] = {}
        self._output_dir: Path = Path('.')
        self._current_soup: Optional[BeautifulSoup] = None
        self._progress_callback: Optional[Callable[[int, str], None]] = None

    def _load_epub(self) -> bool:
        """加载 EPUB 文件。

        Returns:
            加载是否成功。
        """
        try:
            self._book = epub.read_epub(str(self.epub_path))
            return True
        except Exception as e:
            self._report_progress(0, f'加载 EPUB 失败: {e}')
            return False

    def _report_progress(self, percentage: int, message: str) -> None:
        """报告进度。

        Args:
            percentage: 进度百分比 (0-100)。
            message: 状态消息。
        """
        if self._progress_callback:
            self._progress_callback(percentage, message)

    def get_metadata(self) -> BookMetadata:
        """获取书籍元数据。

        Returns:
            包含书籍元数据的 BookMetadata 对象。
        """
        if not self._book:
            if not self._load_epub():
                return BookMetadata()

        metadata = BookMetadata()

        # 获取各项元数据
        title = self._book.get_metadata('DC', 'title')
        if title:
            metadata.title = title[0][0]

        creator = self._book.get_metadata('DC', 'creator')
        if creator:
            metadata.author = creator[0][0]

        language = self._book.get_metadata('DC', 'language')
        if language:
            metadata.language = language[0][0]

        publisher = self._book.get_metadata('DC', 'publisher')
        if publisher:
            metadata.publisher = publisher[0][0]

        description = self._book.get_metadata('DC', 'description')
        if description:
            metadata.description = description[0][0]

        return metadata

    @property
    def metadata(self) -> BookMetadata:
        """书籍元数据属性。

        Returns:
            包含书籍元数据的 BookMetadata 对象。
        """
        return self.get_metadata()

    def _extract_toc(self) -> list[TocItem]:
        """提取 EPUB 的目录结构。

        Returns:
            目录项列表。
        """
        if not self._book:
            return []

        toc_items: list[TocItem] = []

        def process_toc_item(item, level: int = 1) -> None:
            """递归处理目录项。"""
            if isinstance(item, tuple):
                section, children = item
                href = section.href.split('#')[0] if section.href else ''
                toc_items.append(TocItem(
                    title=section.title,
                    href=href,
                    level=level
                ))
                for child in children:
                    process_toc_item(child, level + 1)
            elif hasattr(item, 'title') and hasattr(item, 'href'):
                href = item.href.split('#')[0] if item.href else ''
                toc_items.append(TocItem(
                    title=item.title,
                    href=href,
                    level=level
                ))

        for item in self._book.toc:
            process_toc_item(item)

        # 建立 href 到标题的映射
        for toc_item in toc_items:
            if toc_item.href:
                self._href_to_title[toc_item.href] = {
                    'title': toc_item.title,
                    'level': toc_item.level
                }

        self._toc = toc_items
        return toc_items

    def _generate_toc_markdown(self) -> str:
        """生成 Markdown 格式的目录。

        Returns:
            Markdown 目录字符串。
        """
        if not self._toc:
            return ''

        lines = ['## 目录\n']
        for item in self._toc:
            indent = '  ' * (item.level - 1)
            anchor = self._generate_anchor(item.title)
            lines.append(f'{indent}- [{item.title}](#{anchor})')

        return '\n'.join(lines) + '\n'

    @staticmethod
    def _generate_anchor(text: str) -> str:
        """生成锚点链接。

        Args:
            text: 标题文本。

        Returns:
            锚点字符串。
        """
        anchor = text.lower()
        anchor = anchor.replace(' ', '-')
        anchor = re.sub(r'[（）()]', '', anchor)
        return anchor

    def _is_title_element(self, element: Tag) -> Optional[int]:
        """判断元素是否是标题，返回标题级别。

        Args:
            element: BeautifulSoup 元素。

        Returns:
            标题级别 (1-6)，如果不是标题返回 None。
        """
        if not isinstance(element, Tag):
            return None

        tag_name = element.name.lower() if element.name else ''

        # 标准 h1-h6 标签
        if tag_name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            return int(tag_name[1])

        # 检查是否是 p 标签包含 bold span 的模式
        if tag_name == 'p':
            bold_span = element.find(
                'span',
                class_=lambda x: x and 'bold' in str(x)
            )
            if bold_span:
                text = element.get_text().strip()
                if len(text) < 100 and text:
                    return self._determine_title_level(element, text)

        return None

    def _determine_title_level(self, element: Tag, text: str) -> Optional[int]:
        """确定标题级别。

        Args:
            element: HTML 元素。
            text: 文本内容。

        Returns:
            标题级别，不是标题返回 None。
        """
        # 检查是否在 TOC 中
        for item in self._toc:
            if item.title == text:
                return item.level + 1

        # 检查是否像小节标题
        if re.match(r'^[（\(][一二三四五六七八九十\d]+[）\)]$', text):
            return 3

        # 排除明显不是标题的内容
        if re.match(r'^\d{4}年\d{1,2}月\d{1,2}日', text):
            return None
        if re.match(r'^[\u4e00-\u9fa5]{2,4}$', text):
            toc_titles = [item.title for item in self._toc]
            if text not in toc_titles:
                return None
        if text in ['版权信息', '目录', '封面', '扉页']:
            return None

        # 检查是否是章节标题
        if len(text) <= 30:
            parent = element.parent
            if parent:
                all_bold_p = [
                    p for p in parent.find_all('p')
                    if p.find('span', class_=lambda x: x and 'bold' in str(x))
                ]
                if all_bold_p and element == all_bold_p[0]:
                    if self._has_content_after(parent, element):
                        return 2

        return None

    def _has_content_after(self, parent: Tag, element: Tag) -> bool:
        """检查元素后面是否有正文内容。

        Args:
            parent: 父元素。
            element: 当前元素。

        Returns:
            是否有后续内容。
        """
        all_p = parent.find_all('p')
        found_self = False
        for p in all_p:
            if p == element:
                found_self = True
                continue
            if found_self:
                p_text = p.get_text().strip()
                if len(p_text) > 50:
                    return True
        return False

    def _extract_images(self) -> dict[str, dict]:
        """提取 EPUB 中的所有图片。

        Returns:
            图片路径映射字典。
        """
        if not self._book:
            return {}

        image_map: dict[str, dict] = {}

        for item in self._book.get_items():
            if item.get_type() == ebooklib.ITEM_IMAGE:
                original_name = item.get_name()
                file_name = os.path.basename(original_name)

                # 确保文件名唯一
                existing_names = [v['new_name'] for v in image_map.values()]
                if file_name in existing_names:
                    name, ext = os.path.splitext(file_name)
                    counter = 1
                    while f'{name}_{counter}{ext}' in existing_names:
                        counter += 1
                    file_name = f'{name}_{counter}{ext}'

                image_map[original_name] = {
                    'new_name': file_name,
                    'data': item.get_content()
                }

                # 添加可能的引用路径变体
                base_name = os.path.basename(original_name)
                if base_name not in image_map:
                    image_map[base_name] = image_map[original_name]

        self._images = image_map
        return image_map

    def _save_images(self, output_dir: Path) -> int:
        """保存提取的图片到指定目录。

        Args:
            output_dir: 输出目录路径。

        Returns:
            保存的图片数量。
        """
        if not self._images:
            return 0

        image_output_dir = output_dir / self.options.image_dir
        image_output_dir.mkdir(parents=True, exist_ok=True)

        saved_count = 0
        saved_names: set[str] = set()

        for image_info in self._images.values():
            new_name = image_info['new_name']
            if new_name in saved_names:
                continue

            image_path = image_output_dir / new_name
            try:
                with open(image_path, 'wb') as f:
                    f.write(image_info['data'])
                saved_count += 1
                saved_names.add(new_name)
            except OSError:
                pass  # 忽略保存失败的图片

        return saved_count

    def _get_new_image_path(self, original_src: str) -> str:
        """获取图片的新路径。

        Args:
            original_src: 原始图片路径。

        Returns:
            新的相对路径。
        """
        if original_src in self._images:
            return f"{self.options.image_dir}/{self._images[original_src]['new_name']}"

        base_name = os.path.basename(original_src)
        if base_name in self._images:
            return f"{self.options.image_dir}/{self._images[base_name]['new_name']}"

        cleaned_src = re.sub(r'^(\.\./)+', '', original_src)
        cleaned_src = re.sub(r'^\./+', '', cleaned_src)

        for orig_path, image_info in self._images.items():
            if (orig_path.endswith(cleaned_src) or
                    cleaned_src.endswith(os.path.basename(orig_path))):
                return f"{self.options.image_dir}/{image_info['new_name']}"

        return original_src

    def _html_to_markdown(self, html_content: str) -> str:
        """将 HTML 内容转换为 Markdown。

        Args:
            html_content: HTML 内容字符串。

        Returns:
            Markdown 格式的字符串。
        """
        self._current_soup = BeautifulSoup(html_content, 'lxml')

        # 移除脚本和样式
        for tag in self._current_soup(['script', 'style', 'head', 'meta', 'link']):
            tag.decompose()

        body = self._current_soup.find('body')
        content = body if body else self._current_soup

        # 预处理标题
        self._preprocess_headings(content)

        markdown = self._process_element(content)
        markdown = re.sub(r'\n{3,}', '\n\n', markdown)

        return markdown.strip()

    def _preprocess_headings(self, soup_content: Tag) -> None:
        """预处理 HTML，将基于 CSS 的标题转换为标准标题标签。

        Args:
            soup_content: BeautifulSoup 内容元素。
        """
        for p in list(soup_content.find_all('p')):
            title_level = self._is_title_element(p)
            if title_level:
                text = p.get_text().strip()
                new_tag = self._current_soup.new_tag(f'h{min(title_level, 6)}')
                new_tag.string = text
                p.replace_with(new_tag)

    def _process_element(self, element) -> str:
        """递归处理 HTML 元素并转换为 Markdown。

        Args:
            element: BeautifulSoup 元素。

        Returns:
            Markdown 格式的字符串。
        """
        if isinstance(element, NavigableString):
            text = str(element)
            return re.sub(r'[ \t]+', ' ', text)

        if not isinstance(element, Tag):
            return ''

        tag_name = element.name.lower() if element.name else ''
        return self._convert_tag_to_markdown(element, tag_name)

    def _convert_tag_to_markdown(self, element: Tag, tag_name: str) -> str:
        """将 HTML 标签转换为 Markdown。

        Args:
            element: HTML 元素。
            tag_name: 标签名。

        Returns:
            Markdown 字符串。
        """
        # 标题标签
        if tag_name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            level = int(tag_name[1])
            text = element.get_text(separator=' ', strip=True)
            if text:
                return f"\n\n{'#' * level} {text}\n\n"
            return ''

        # 段落
        if tag_name == 'p':
            text = self._process_children(element).strip()
            if text:
                return f'\n\n{text}\n\n'
            return ''

        # 换行和分隔线
        if tag_name == 'br':
            return '  \n'
        if tag_name == 'hr':
            return '\n\n---\n\n'

        # 文本样式
        if tag_name in ['strong', 'b']:
            text = self._process_children(element).strip()
            return f'**{text}**' if text else ''

        if tag_name in ['em', 'i']:
            text = self._process_children(element).strip()
            return f'*{text}*' if text else ''

        if tag_name == 'u':
            text = self._process_children(element).strip()
            return f'<u>{text}</u>' if text else ''

        if tag_name in ['s', 'strike', 'del']:
            text = self._process_children(element).strip()
            return f'~~{text}~~' if text else ''

        # 链接
        if tag_name == 'a':
            href = element.get('href', '')
            text = self._process_children(element).strip()
            if text and href and not href.startswith('#'):
                return f'[{text}]({href})'
            return text

        # 图片
        if tag_name == 'img':
            src = element.get('src', '')
            alt = element.get('alt', 'image')
            if src:
                new_src = self._get_new_image_path(src)
                return f'![{alt}]({new_src})'
            return ''

        # 列表
        if tag_name == 'ul':
            return self._process_unordered_list(element)
        if tag_name == 'ol':
            return self._process_ordered_list(element)

        # 引用
        if tag_name == 'blockquote':
            text = self._process_children(element).strip()
            if text:
                lines = text.split('\n')
                quoted = '\n'.join(f'> {line}' for line in lines)
                return f'\n\n{quoted}\n\n'
            return ''

        # 代码
        if tag_name == 'pre':
            code = element.get_text()
            return f'\n\n```\n{code}\n```\n\n'

        if tag_name == 'code':
            if element.parent and element.parent.name == 'pre':
                return element.get_text()
            text = element.get_text().strip()
            return f'`{text}`' if text else ''

        # 表格
        if tag_name == 'table':
            return self._process_table(element)

        # 上下标
        if tag_name == 'sup':
            text = self._process_children(element).strip()
            return f'^{text}^' if text else ''

        if tag_name == 'sub':
            text = self._process_children(element).strip()
            return f'~{text}~' if text else ''

        # 容器标签，处理子元素
        return self._process_children(element)

    def _process_children(self, element: Tag) -> str:
        """处理元素的所有子元素。

        Args:
            element: BeautifulSoup 元素。

        Returns:
            子元素转换后的 Markdown 字符串。
        """
        result = []
        for child in element.children:
            result.append(self._process_element(child))
        return ''.join(result)

    def _process_unordered_list(self, element: Tag) -> str:
        """处理无序列表。

        Args:
            element: 列表元素。

        Returns:
            Markdown 列表字符串。
        """
        items = []
        for li in element.find_all('li', recursive=False):
            item_text = self._process_children(li).strip()
            if item_text:
                lines = item_text.split('\n')
                formatted = f'- {lines[0]}'
                for line in lines[1:]:
                    if line.strip():
                        formatted += f'\n  {line.strip()}'
                items.append(formatted)

        if items:
            return '\n\n' + '\n'.join(items) + '\n\n'
        return ''

    def _process_ordered_list(self, element: Tag) -> str:
        """处理有序列表。

        Args:
            element: 列表元素。

        Returns:
            Markdown 列表字符串。
        """
        items = []
        for i, li in enumerate(element.find_all('li', recursive=False), 1):
            item_text = self._process_children(li).strip()
            if item_text:
                lines = item_text.split('\n')
                formatted = f'{i}. {lines[0]}'
                for line in lines[1:]:
                    if line.strip():
                        formatted += f'\n   {line.strip()}'
                items.append(formatted)

        if items:
            return '\n\n' + '\n'.join(items) + '\n\n'
        return ''

    def _process_table(self, table_element: Tag) -> str:
        """处理表格元素。

        Args:
            table_element: 表格 BeautifulSoup 元素。

        Returns:
            Markdown 格式的表格。
        """
        rows = []
        for tr in table_element.find_all('tr'):
            cells = []
            for cell in tr.find_all(['th', 'td']):
                cell_text = cell.get_text(separator=' ', strip=True)
                cell_text = cell_text.replace('|', '\\|')
                cells.append(cell_text)
            if cells:
                rows.append(cells)

        if not rows:
            return ''

        md_table = []
        md_table.append('| ' + ' | '.join(rows[0]) + ' |')
        md_table.append('| ' + ' | '.join(['---'] * len(rows[0])) + ' |')

        for row in rows[1:]:
            while len(row) < len(rows[0]):
                row.append('')
            md_table.append('| ' + ' | '.join(row[:len(rows[0])]) + ' |')

        return '\n\n' + '\n'.join(md_table) + '\n\n'

    def _is_toc_page(self, html_content: str) -> bool:
        """检测是否是目录页。

        Args:
            html_content: HTML 内容。

        Returns:
            是否是目录页。
        """
        soup = BeautifulSoup(html_content, 'lxml')
        internal_links = soup.find_all(
            'a',
            href=lambda x: x and x.startswith('index_split_')
        )
        return len(internal_links) > 10

    def convert(
        self,
        progress_callback: Optional[Callable[[int, str], None]] = None
    ) -> str:
        """执行转换并返回 Markdown 内容。

        Args:
            progress_callback: 进度回调函数，接收 (进度百分比, 状态消息)。

        Returns:
            转换后的 Markdown 字符串。
        """
        self._progress_callback = progress_callback
        self._report_progress(0, '开始加载 EPUB 文件...')

        if not self._load_epub():
            return ''

        self._markdown_content = []
        self._report_progress(10, '提取图片...')

        # 提取图片和目录
        if self.options.extract_images:
            self._extract_images()

        self._report_progress(20, '解析目录结构...')
        self._extract_toc()

        # 添加 YAML 前置数据
        self._report_progress(30, '生成元数据...')
        metadata = self.get_metadata()
        if metadata.to_dict():
            self._add_yaml_front_matter(metadata)

        # 添加标题
        if metadata.title:
            self._markdown_content.append(f'# {metadata.title}\n')

        # 添加目录
        if self.options.generate_toc:
            toc_md = self._generate_toc_markdown()
            if toc_md:
                self._markdown_content.append(toc_md)
                self._markdown_content.append('\n---\n')

        # 获取并处理文档
        self._report_progress(40, '转换文档内容...')
        ordered_items = self._get_ordered_items()

        total_items = len(ordered_items)
        for i, item in enumerate(ordered_items):
            progress = 40 + int((i / total_items) * 50)
            self._report_progress(progress, f'正在转换: {item.get_name()}')

            content = item.get_content().decode('utf-8', errors='ignore')

            if self._is_toc_page(content):
                continue

            markdown = self._html_to_markdown(content)
            if markdown.strip():
                self._markdown_content.append(markdown)
                self._markdown_content.append('\n\n---\n\n')

        result = '\n'.join(self._markdown_content)
        result = re.sub(r'\n{3,}', '\n\n', result)
        result = re.sub(r'(\n---\n)+$', '', result)

        self._report_progress(100, '转换完成！')
        return result.strip()

    def _add_yaml_front_matter(self, metadata: BookMetadata) -> None:
        """添加 YAML 前置数据。

        Args:
            metadata: 书籍元数据。
        """
        self._markdown_content.append('---')
        for key, value in metadata.to_dict().items():
            if '\n' in str(value):
                self._markdown_content.append(f'{key}: |')
                for line in str(value).split('\n'):
                    self._markdown_content.append(f'  {line}')
            else:
                value_str = str(value).replace('"', '\\"')
                self._markdown_content.append(f'{key}: "{value_str}"')
        self._markdown_content.append('---\n')

    def _get_ordered_items(self) -> list:
        """获取按阅读顺序排列的文档项。

        Returns:
            文档项列表。
        """
        spine_items = []
        for item in self._book.get_items():
            if item.get_type() == ebooklib.ITEM_DOCUMENT:
                spine_items.append(item)

        spine_ids = [item_id for item_id, _ in self._book.spine]
        ordered_items = []

        id_to_item = {item.get_id(): item for item in spine_items}
        for item_id in spine_ids:
            if item_id in id_to_item:
                ordered_items.append(id_to_item[item_id])

        spine_id_set = set(spine_ids)
        for item in spine_items:
            if item.get_id() not in spine_id_set:
                ordered_items.append(item)

        return ordered_items

    def save(
        self,
        output_path: Union[str, Path],
        progress_callback: Optional[Callable[[int, str], None]] = None
    ) -> ConversionResult:
        """保存转换结果到文件。

        Args:
            output_path: 输出文件路径。
            progress_callback: 进度回调函数。

        Returns:
            ConversionResult 对象，包含转换结果信息。
        """
        output_path = Path(output_path)
        self._output_dir = output_path.parent
        self._output_dir.mkdir(parents=True, exist_ok=True)

        try:
            markdown = self.convert(progress_callback)
            if not markdown:
                return ConversionResult(
                    success=False,
                    error_message='转换结果为空'
                )

            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(markdown)

            image_count = 0
            if self.options.extract_images and self._images:
                image_count = self._save_images(self._output_dir)

            return ConversionResult(
                success=True,
                markdown_path=output_path,
                image_count=image_count
            )

        except Exception as e:
            return ConversionResult(
                success=False,
                error_message=str(e)
            )
