# EPUB to Markdown Converter

一个将 EPUB 电子书转换为 Markdown 格式的 Python 工具，支持提取图片、保留文档结构和元数据。  
提供 **命令行 (CLI)** 和 **图形界面 (GUI)** 两种使用方式。

## 功能特性

### 核心功能

- ✅ **元数据提取** - 自动提取书籍标题、作者、出版商、语言、描述等信息，生成 YAML 前置数据
- ✅ **目录生成** - 自动从 EPUB 的 TOC（Table of Contents）生成 Markdown 目录，支持多级嵌套
- ✅ **大纲识别** - 智能识别章节标题，包括：
  - 标准 HTML 标题标签 (`<h1>` - `<h6>`)
  - Calibre 生成的带 bold 类的 span 标题
  - 中文小节标题（如（一）（二）等）
- ✅ **图片提取** - 自动提取 EPUB 中的所有图片并保存到独立目录
- ✅ **HTML 到 Markdown 转换** - 支持多种 HTML 元素转换
- ✅ **保持阅读顺序** - 按 EPUB 的 spine 顺序处理章节
- ✅ **自动清理** - 移除多余空行，跳过目录页，优化输出格式

### 使用方式

- 🖥️ **命令行模式 (CLI)** - 适合开发者和批量处理
- 🎨 **图形界面 (GUI)** - 适合普通用户，支持拖拽文件、一键转换

### 支持的HTML元素

| 元素类型 | HTML标签                         | Markdown输出       |
| -------- | -------------------------------- | ------------------ |
| 标题     | `<h1>` - `<h6>`              | `#` - `######` |
| 段落     | `<p>`                          | 普通段落           |
| 粗体     | `<strong>`, `<b>`            | `**文本**`       |
| 斜体     | `<em>`, `<i>`                | `*文本*`         |
| 删除线   | `<s>`, `<del>`, `<strike>` | `~~文本~~`       |
| 下划线   | `<u>`                          | `<u>文本</u>`    |
| 链接     | `<a>`                          | `[文本](链接)`   |
| 图片     | `<img>`                        | `![描述](路径)`  |
| 无序列表 | `<ul>`, `<li>`               | `- 项目`         |
| 有序列表 | `<ol>`, `<li>`               | `1. 项目`        |
| 引用     | `<blockquote>`                 | `> 引用文本`     |
| 代码块   | `<pre>`, `<code>`            | ` ```代码``` `   |
| 行内代码 | `<code>`                       | `` `代码` ``       |
| 表格     | `<table>`                      | Markdown表格       |
| 分隔线   | `<hr>`                         | `---`            |
| 上标     | `<sup>`                        | `^文本^`         |
| 下标     | `<sub>`                        | `~文本~`         |

## 环境要求

### Python 版本

- **Python 3.8+** （推荐 Python 3.10 或更高版本）

### 依赖包

#### 基础依赖（CLI 模式）

| 包名           | 版本    | 用途               |
| -------------- | ------- | ------------------ |
| ebooklib       | ≥0.18  | 读取和解析 EPUB 文件 |
| beautifulsoup4 | ≥4.9.0 | 解析 HTML 内容       |
| lxml           | ≥4.6.0 | HTML/XML 解析器     |

#### GUI 依赖（可选）

| 包名    | 版本   | 用途           |
| ------- | ------ | -------------- |
| PySide6 | ≥6.5.0 | 图形用户界面   |

## 安装指南

### 1. 克隆项目

```bash
git clone git@github.com:kashima19960/epub_to_markdown.git
cd epub_to_markdown
```

### 2. 创建虚拟环境（推荐）

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Linux / macOS
python3 -m venv .venv
source .venv/bin/activate
```

### 3. 安装依赖

**仅 CLI 模式：**

```bash
pip install -r requirements.txt
```

**包含 GUI 模式：**

```bash
pip install -r requirements.txt
pip install -r requirements-gui.txt
```

### 4. 验证安装

```bash
python -c "import ebooklib; from bs4 import BeautifulSoup; import lxml; print('CLI 依赖安装成功！')"

# 如果需要 GUI
python -c "from PySide6 import QtWidgets; print('GUI 依赖安装成功！')"
```

## 使用方法

### 方式一：图形界面（推荐普通用户）

**Windows：**

双击 `scripts/epub2md_gui.pyw` 文件即可启动。

**命令行启动：**

```bash
python scripts/epub2md.py --gui
```

**GUI 功能：**

- 📁 拖拽文件到窗口
- ⚙️ 选择转换选项（提取图片、生成目录）
- 📊 实时显示转换进度
- 📂 转换完成后自动打开文件夹

### 方式二：命令行

```bash
# 基本转换
python scripts/epub2md.py book.epub

# 指定输出路径
python scripts/epub2md.py book.epub -o /path/to/output.md

# 不提取图片
python scripts/epub2md.py book.epub --no-images

# 不生成目录
python scripts/epub2md.py book.epub --no-toc

# 查看帮助
python scripts/epub2md.py --help
```

### 输出结构

转换后会生成以下文件结构：

```
输出目录/
├── output.md           # Markdown文件
└── images/             # 图片目录（如果EPUB包含图片）
    ├── cover.jpg
    ├── image1.png
    └── ...
```

## 输出格式示例

转换后的Markdown文件包含以下内容：

```markdown
---
title: "书籍标题"
author: "作者名"
language: "en"
publisher: "出版商"
description: "书籍描述..."
---

# 书籍标题

![cover](images/cover.jpg)

---

## 第一章

正文内容...

---

## 第二章

正文内容...
```

## 作为 Python 模块使用

```python
from epub_converter import EpubToMarkdownConverter, ConversionOptions

# 创建转换器实例
converter = EpubToMarkdownConverter('book.epub')

# 方式1：直接保存（包含图片提取）
result = converter.save('output.md')
print(f"转换完成！共 {result.image_count} 张图片")

# 方式2：带选项的转换
options = ConversionOptions(
    extract_images=True,
    generate_toc=True
)
converter = EpubToMarkdownConverter('book.epub', options)
result = converter.save('output.md')

# 方式3：只获取 Markdown 内容（不保存文件）
converter = EpubToMarkdownConverter('book.epub')
markdown_content = converter.convert()
print(markdown_content)

# 方式4：获取书籍元数据
converter = EpubToMarkdownConverter('book.epub')
_ = converter.convert()
metadata = converter.metadata
print(f"标题: {metadata.title}")
print(f"作者: {metadata.author}")
```

## 常见问题

### Q1: 转换后图片不显示？

**原因**：Markdown预览器可能不支持相对路径，或者图片目录位置不对。

**解决方案**：

1. 确保 `images/` 目录与 `.md` 文件在同一目录下
2. 使用支持相对路径的Markdown编辑器（如VS Code、Typora）

### Q2: 中文乱码？

**原因**：文件编码问题。

**解决方案**：

1. 确保使用UTF-8编码打开Markdown文件
2. 在编辑器中设置默认编码为UTF-8

### Q3: 某些格式丢失？

**原因**：EPUB使用了复杂的CSS样式，而不是语义化HTML标签。

**解决方案**：

- 这是HTML到Markdown转换的固有限制
- 可以手动调整转换后的Markdown文件

### Q4: 安装依赖失败？

**解决方案**：

```bash
# 升级pip
python -m pip install --upgrade pip

# 使用国内镜像源
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple ebooklib beautifulsoup4 lxml
```

### Q5: 提示找不到Python？

**解决方案**：

1. 确保Python已添加到系统PATH
2. Windows用户可以使用 `py` 命令代替 `python`
3. 使用完整路径运行Python

## 技术说明

### 工作原理

1. **加载EPUB** - 使用 `ebooklib` 读取EPUB文件
2. **提取元数据** - 从Dublin Core元数据中获取书籍信息
3. **提取目录** - 解析EPUB的TOC结构，建立章节映射
4. **提取图片** - 遍历所有媒体项，保存图片文件
5. **解析HTML** - 使用 `BeautifulSoup` 解析每个章节的HTML内容
6. **识别标题** - 智能识别章节标题（包括非标准HTML标签的标题）
7. **转换Markdown** - 递归处理HTML元素，转换为对应的Markdown语法
8. **输出文件** - 保存Markdown文件和图片

### 项目结构

```
epub_to_markdown/
├── src/
│   └── epub_converter/
│       ├── __init__.py      # 包初始化，导出公共 API
│       ├── converter.py     # 核心转换器类
│       ├── utils.py         # 工具函数
│       ├── cli.py           # 命令行接口
│       └── gui/
│           ├── __init__.py  # GUI 包初始化
│           └── main_window.py  # 主窗口
├── scripts/
│   ├── epub2md.py           # CLI 入口脚本
│   └── epub2md_gui.pyw      # GUI 入口脚本 (Windows)
├── requirements.txt         # 基础依赖
├── requirements-gui.txt     # GUI 依赖
├── .gitignore               # Git 忽略配置
└── README.md                # 说明文档
```

## 许可证

MIT License

## 更新日志

### v2.0.0 (2025-01-31)

- 新增：图形用户界面 (GUI)，支持拖拽文件
- 新增：模块化项目结构
- 新增：进度回调支持
- 改进：代码重构，遵循 Google Python Style Guide
- 改进：命令行参数设计

### v1.1.0 (2025-01-31)

- 新增：自动生成目录 (TOC)
- 新增：智能识别章节标题（支持 Calibre 生成的 EPUB）
- 新增：识别中文小节标题（如（一）（二））
- 优化：自动跳过目录页面
- 优化：排除非标题内容的误识别

### v1.0.0 (2025-01-31)

- 初始版本发布
- 支持基本的 EPUB 到 Markdown 转换
- 支持图片提取
- 支持元数据提取
- 支持多种 HTML 元素转换
