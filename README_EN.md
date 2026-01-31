# EPUB to Markdown Converter

A Python tool that converts EPUB e-books to Markdown format, supporting image extraction, document structure preservation, and metadata extraction.  
Available in both **Command Line (CLI)** and **Graphical User Interface (GUI)** modes.

## Features

### Core Features

- ✅ **Metadata Extraction** - Automatically extracts book title, author, publisher, language, description, and generates YAML front matter
- ✅ **Table of Contents Generation** - Automatically generates Markdown TOC from EPUB's Table of Contents, supporting multi-level nesting
- ✅ **Outline Recognition** - Intelligently identifies chapter headings, including:
  - Standard HTML heading tags (`<h1>` - `<h6>`)
  - Calibre-generated span headings with bold class
  - Chinese section titles (e.g., (一), (二), etc.)
- ✅ **Image Extraction** - Automatically extracts all images from EPUB and saves them to a separate directory
- ✅ **HTML to Markdown Conversion** - Supports various HTML element conversions
- ✅ **Reading Order Preservation** - Processes chapters according to EPUB's spine order
- ✅ **Auto Cleanup** - Removes excessive blank lines, skips TOC pages, optimizes output format

### Usage Modes

- 🖥️ **Command Line Mode (CLI)** - Suitable for developers and batch processing
- 🎨 **Graphical User Interface (GUI)** - Suitable for general users, supports drag-and-drop files, one-click conversion

### Supported HTML Elements

| Element Type | HTML Tags | Markdown Output |
| --- | --- | --- |
| Headings | `<h1>` - `<h6>` | `#` - `######` |
| Paragraphs | `<p>` | Normal paragraphs |
| Bold | `<strong>`, `<b>` | `**text**` |
| Italic | `<em>`, `<i>` | `*text*` |
| Strikethrough | `<s>`, `<del>`, `<strike>` | `~~text~~` |
| Underline | `<u>` | `<u>text</u>` |
| Links | `<a>` | `[text](url)` |
| Images | `<img>` | `![alt](path)` |
| Unordered Lists | `<ul>`, `<li>` | `- item` |
| Ordered Lists | `<ol>`, `<li>` | `1. item` |
| Blockquotes | `<blockquote>` | `> quoted text` |
| Code Blocks | `<pre>`, `<code>` | ` ```code``` ` |
| Inline Code | `<code>` | `` `code` `` |
| Tables | `<table>` | Markdown tables |
| Horizontal Rules | `<hr>` | `---` |
| Superscript | `<sup>` | `^text^` |
| Subscript | `<sub>` | `~text~` |

## Requirements

### Python Version

- **Python 3.8+** (Python 3.10 or higher recommended)

### Dependencies

#### Basic Dependencies (CLI Mode)

| Package | Version | Purpose |
| --- | --- | --- |
| ebooklib | ≥0.18 | Read and parse EPUB files |
| beautifulsoup4 | ≥4.9.0 | Parse HTML content |
| lxml | ≥4.6.0 | HTML/XML parser |

#### GUI Dependencies (Optional)

| Package | Version | Purpose |
| --- | --- | --- |
| PySide6 | ≥6.5.0 | Graphical user interface |

## Installation Guide

### 1. Clone the Project

```bash
git clone git@github.com:kashima19960/epub_to_markdown.git
cd epub_to_markdown
```

### 2. Create Virtual Environment (Recommended)

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Linux / macOS
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

**CLI Mode Only:**

```bash
pip install -r requirements.txt
```

**Including GUI Mode:**

```bash
pip install -r requirements.txt
pip install -r requirements-gui.txt
```

### 4. Verify Installation

```bash
python -c "import ebooklib; from bs4 import BeautifulSoup; import lxml; print('CLI dependencies installed successfully!')"

# If GUI is needed
python -c "from PySide6 import QtWidgets; print('GUI dependencies installed successfully!')"
```

## Usage

### Method 1: Graphical User Interface (Recommended for General Users)

**Windows:**

Double-click `scripts/epub2md_gui.pyw` to launch.

**Command Line Launch:**

```bash
python scripts/epub2md.py --gui
```

**GUI Features:**

- 📁 Drag and drop files to the window
- ⚙️ Select conversion options (extract images, generate TOC)
- 📊 Real-time conversion progress display
- 📂 Automatically open folder after conversion

### Method 2: Command Line

```bash
# Basic conversion
python scripts/epub2md.py book.epub

# Specify output path
python scripts/epub2md.py book.epub -o /path/to/output.md

# Without image extraction
python scripts/epub2md.py book.epub --no-images

# Without TOC generation
python scripts/epub2md.py book.epub --no-toc

# View help
python scripts/epub2md.py --help
```

### Output Structure

After conversion, the following file structure will be generated:

```
output_directory/
├── output.md           # Markdown file
└── images/             # Image directory (if EPUB contains images)
    ├── cover.jpg
    ├── image1.png
    └── ...
```

## Output Format Example

The converted Markdown file contains the following:

```markdown
---
title: "Book Title"
author: "Author Name"
language: "en"
publisher: "Publisher"
description: "Book description..."
---

# Book Title

![cover](images/cover.jpg)

---

## Chapter 1

Content...

---

## Chapter 2

Content...
```

## Using as a Python Module

```python
from epub_converter import EpubToMarkdownConverter, ConversionOptions

# Create converter instance
converter = EpubToMarkdownConverter('book.epub')

# Method 1: Save directly (including image extraction)
result = converter.save('output.md')
print(f"Conversion complete! {result.image_count} images")

# Method 2: Conversion with options
options = ConversionOptions(
    extract_images=True,
    generate_toc=True
)
converter = EpubToMarkdownConverter('book.epub', options)
result = converter.save('output.md')

# Method 3: Get Markdown content only (without saving file)
converter = EpubToMarkdownConverter('book.epub')
markdown_content = converter.convert()
print(markdown_content)

# Method 4: Get book metadata
converter = EpubToMarkdownConverter('book.epub')
_ = converter.convert()
metadata = converter.metadata
print(f"Title: {metadata.title}")
print(f"Author: {metadata.author}")
```

## FAQ

### Q1: Images not displaying after conversion?

**Cause**: The Markdown previewer may not support relative paths, or the image directory location is incorrect.

**Solution**:

1. Ensure the `images/` directory is in the same directory as the `.md` file
2. Use a Markdown editor that supports relative paths (e.g., VS Code, Typora)

### Q2: Chinese characters garbled?

**Cause**: File encoding issue.

**Solution**:

1. Ensure you open the Markdown file with UTF-8 encoding
2. Set the default encoding to UTF-8 in your editor

### Q3: Some formatting lost?

**Cause**: EPUB uses complex CSS styles instead of semantic HTML tags.

**Solution**:

- This is an inherent limitation of HTML to Markdown conversion
- You can manually adjust the converted Markdown file

### Q4: Failed to install dependencies?

**Solution**:

```bash
# Upgrade pip
python -m pip install --upgrade pip

# Use alternative mirror (for users in China)
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple ebooklib beautifulsoup4 lxml
```

### Q5: Python not found?

**Solution**:

1. Ensure Python is added to system PATH
2. Windows users can use the `py` command instead of `python`
3. Use the full path to run Python

## Technical Details

### How It Works

1. **Load EPUB** - Use `ebooklib` to read EPUB files
2. **Extract Metadata** - Get book information from Dublin Core metadata
3. **Extract TOC** - Parse EPUB's TOC structure, build chapter mapping
4. **Extract Images** - Iterate through all media items, save image files
5. **Parse HTML** - Use `BeautifulSoup` to parse each chapter's HTML content
6. **Identify Headings** - Intelligently identify chapter headings (including non-standard HTML tag headings)
7. **Convert to Markdown** - Recursively process HTML elements, convert to corresponding Markdown syntax
8. **Output Files** - Save Markdown file and images

### Project Structure

```
epub_to_markdown/
├── src/
│   └── epub_converter/
│       ├── __init__.py      # Package initialization, export public API
│       ├── converter.py     # Core converter class
│       ├── utils.py         # Utility functions
│       ├── cli.py           # Command line interface
│       └── gui/
│           ├── __init__.py  # GUI package initialization
│           └── main_window.py  # Main window
├── scripts/
│   ├── epub2md.py           # CLI entry script
│   └── epub2md_gui.pyw      # GUI entry script (Windows)
├── requirements.txt         # Basic dependencies
├── requirements-gui.txt     # GUI dependencies
├── .gitignore               # Git ignore configuration
└── README.md                # Documentation
```

## License

MIT License

## Changelog

### v2.0.0 (2025-01-31)

- Added: Graphical User Interface (GUI) with drag-and-drop support
- Added: Modular project structure
- Added: Progress callback support
- Improved: Code refactoring following Google Python Style Guide
- Improved: Command line argument design

### v1.1.0 (2025-01-31)

- Added: Auto-generate Table of Contents (TOC)
- Added: Smart chapter heading recognition (supports Calibre-generated EPUBs)
- Added: Chinese section title recognition (e.g., (一), (二))
- Optimized: Auto-skip TOC pages
- Optimized: Exclude non-heading content misidentification

### v1.0.0 (2025-01-31)

- Initial release
- Support basic EPUB to Markdown conversion
- Support image extraction
- Support metadata extraction
- Support various HTML element conversions
