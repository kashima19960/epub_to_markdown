"""EPUB 转换器图形用户界面主窗口。

使用 PySide6 实现的现代化图形界面，面向普通用户设计。
提供拖拽文件、一键转换等便捷操作。
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtCore import QThread
from PySide6.QtCore import Signal
from PySide6.QtCore import Slot
from PySide6.QtGui import QDragEnterEvent
from PySide6.QtGui import QDropEvent
from PySide6.QtGui import QFont
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication
from PySide6.QtWidgets import QCheckBox
from PySide6.QtWidgets import QFileDialog
from PySide6.QtWidgets import QFrame
from PySide6.QtWidgets import QGroupBox
from PySide6.QtWidgets import QHBoxLayout
from PySide6.QtWidgets import QLabel
from PySide6.QtWidgets import QMainWindow
from PySide6.QtWidgets import QMessageBox
from PySide6.QtWidgets import QProgressBar
from PySide6.QtWidgets import QPushButton
from PySide6.QtWidgets import QSizePolicy
from PySide6.QtWidgets import QVBoxLayout
from PySide6.QtWidgets import QWidget

from epub_converter.converter import ConversionOptions
from epub_converter.converter import ConversionResult
from epub_converter.converter import EpubToMarkdownConverter
from epub_converter.utils import get_default_output_path
from epub_converter.utils import open_file
from epub_converter.utils import open_file_location


class ConversionWorker(QThread):
    """后台转换工作线程。

    在后台线程中执行转换任务，避免阻塞 UI。

    Signals:
        progress: 进度更新信号 (百分比, 消息)。
        finished: 转换完成信号 (ConversionResult)。
        error: 错误信号 (错误消息)。
    """

    progress = Signal(int, str)
    finished = Signal(object)
    error = Signal(str)

    def __init__(
        self,
        epub_path: Path,
        output_path: Path,
        options: ConversionOptions
    ) -> None:
        """初始化工作线程。

        Args:
            epub_path: EPUB 文件路径。
            output_path: 输出文件路径。
            options: 转换选项。
        """
        super().__init__()
        self._epub_path = epub_path
        self._output_path = output_path
        self._options = options

    def run(self) -> None:
        """执行转换任务。"""
        try:
            converter = EpubToMarkdownConverter(self._epub_path, self._options)
            result = converter.save(
                self._output_path,
                progress_callback=self._on_progress
            )
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))

    def _on_progress(self, percentage: int, message: str) -> None:
        """进度回调。"""
        self.progress.emit(percentage, message)


class DropArea(QFrame):
    """文件拖放区域组件。

    支持拖拽 EPUB 文件到此区域，或点击选择文件。

    Signals:
        file_dropped: 文件拖放信号，携带文件路径。
        clicked: 点击信号。
    """

    file_dropped = Signal(str)
    clicked = Signal()

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """初始化拖放区域。"""
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._setup_ui()

    def _setup_ui(self) -> None:
        """设置界面。"""
        self.setMinimumHeight(200)
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setStyleSheet('''
            DropArea {
                background-color: #f8fafc;
                border: 2px dashed #cbd5e1;
                border-radius: 12px;
            }
            DropArea:hover {
                background-color: #f1f5f9;
                border-color: #94a3b8;
            }
        ''')

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(16)

        # 图标标签
        icon_label = QLabel('📁')
        icon_label.setStyleSheet('font-size: 48px; border: none;')
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(icon_label)

        # 主提示文字
        main_text = QLabel('将 EPUB 文件拖拽到此处')
        main_text.setStyleSheet('''
            font-size: 18px;
            font-weight: 600;
            color: #334155;
            border: none;
        ''')
        main_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(main_text)

        # 分隔文字
        or_text = QLabel('或')
        or_text.setStyleSheet('font-size: 14px; color: #94a3b8; border: none;')
        or_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(or_text)

        # 选择文件按钮
        select_btn = QPushButton('选择文件')
        select_btn.setStyleSheet('''
            QPushButton {
                background-color: #3b82f6;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 32px;
                font-size: 14px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #2563eb;
            }
            QPushButton:pressed {
                background-color: #1d4ed8;
            }
        ''')
        select_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        select_btn.clicked.connect(self.clicked.emit)
        layout.addWidget(select_btn, alignment=Qt.AlignmentFlag.AlignCenter)

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        """处理拖入事件。"""
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if urls and urls[0].toLocalFile().lower().endswith('.epub'):
                event.acceptProposedAction()
                self.setStyleSheet('''
                    DropArea {
                        background-color: #dbeafe;
                        border: 2px dashed #3b82f6;
                        border-radius: 12px;
                    }
                ''')

    def dragLeaveEvent(self, event) -> None:
        """处理拖离事件。"""
        self.setStyleSheet('''
            DropArea {
                background-color: #f8fafc;
                border: 2px dashed #cbd5e1;
                border-radius: 12px;
            }
            DropArea:hover {
                background-color: #f1f5f9;
                border-color: #94a3b8;
            }
        ''')

    def dropEvent(self, event: QDropEvent) -> None:
        """处理放下事件。"""
        self.setStyleSheet('''
            DropArea {
                background-color: #f8fafc;
                border: 2px dashed #cbd5e1;
                border-radius: 12px;
            }
            DropArea:hover {
                background-color: #f1f5f9;
                border-color: #94a3b8;
            }
        ''')

        urls = event.mimeData().urls()
        if urls:
            file_path = urls[0].toLocalFile()
            if file_path.lower().endswith('.epub'):
                self.file_dropped.emit(file_path)

    def mousePressEvent(self, event) -> None:
        """处理鼠标点击事件。"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()


class MainWindow(QMainWindow):
    """主窗口类。

    提供 EPUB 转 Markdown 的图形界面操作。
    面向普通用户设计，操作简单直观。
    """

    def __init__(self) -> None:
        """初始化主窗口。"""
        super().__init__()
        self._current_file: Optional[Path] = None
        self._worker: Optional[ConversionWorker] = None

        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self) -> None:
        """设置用户界面。"""
        self.setWindowTitle('EPUB 转 Markdown 工具')
        self.setMinimumSize(500, 600)
        self.resize(520, 680)

        # 设置窗口样式
        self.setStyleSheet('''
            QMainWindow {
                background-color: #ffffff;
            }
            QLabel {
                color: #334155;
            }
            QGroupBox {
                font-weight: 600;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                margin-top: 12px;
                padding-top: 8px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 8px;
                color: #475569;
            }
            QCheckBox {
                color: #475569;
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
            }
        ''')

        # 主容器
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(20)

        # 标题
        title_label = QLabel('EPUB 转 Markdown')
        title_label.setStyleSheet('''
            font-size: 24px;
            font-weight: 700;
            color: #1e293b;
        ''')
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)

        # 副标题
        subtitle_label = QLabel('轻松将电子书转换为 Markdown 格式')
        subtitle_label.setStyleSheet('''
            font-size: 14px;
            color: #64748b;
        ''')
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(subtitle_label)

        main_layout.addSpacing(8)

        # 拖放区域
        self._drop_area = DropArea()
        main_layout.addWidget(self._drop_area)

        # 文件信息标签
        self._file_info_label = QLabel('未选择文件')
        self._file_info_label.setStyleSheet('''
            font-size: 13px;
            color: #64748b;
            padding: 8px;
        ''')
        self._file_info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self._file_info_label)

        # 选项组
        options_group = QGroupBox('转换选项')
        options_layout = QVBoxLayout(options_group)
        options_layout.setSpacing(12)
        options_layout.setContentsMargins(16, 20, 16, 16)

        self._extract_images_cb = QCheckBox('提取书中的图片')
        self._extract_images_cb.setChecked(True)
        self._extract_images_cb.setCursor(Qt.CursorShape.PointingHandCursor)
        options_layout.addWidget(self._extract_images_cb)

        self._generate_toc_cb = QCheckBox('生成目录导航')
        self._generate_toc_cb.setChecked(True)
        self._generate_toc_cb.setCursor(Qt.CursorShape.PointingHandCursor)
        options_layout.addWidget(self._generate_toc_cb)

        self._open_folder_cb = QCheckBox('转换完成后打开文件夹')
        self._open_folder_cb.setChecked(True)
        self._open_folder_cb.setCursor(Qt.CursorShape.PointingHandCursor)
        options_layout.addWidget(self._open_folder_cb)

        main_layout.addWidget(options_group)

        # 转换按钮
        self._convert_btn = QPushButton('开始转换')
        self._convert_btn.setEnabled(False)
        self._convert_btn.setMinimumHeight(50)
        self._convert_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._convert_btn.setStyleSheet('''
            QPushButton {
                background-color: #10b981;
                color: white;
                border: none;
                border-radius: 10px;
                font-size: 16px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #059669;
            }
            QPushButton:pressed {
                background-color: #047857;
            }
            QPushButton:disabled {
                background-color: #d1d5db;
                color: #9ca3af;
            }
        ''')
        main_layout.addWidget(self._convert_btn)

        # 进度条
        self._progress_bar = QProgressBar()
        self._progress_bar.setVisible(False)
        self._progress_bar.setMinimumHeight(8)
        self._progress_bar.setTextVisible(False)
        self._progress_bar.setStyleSheet('''
            QProgressBar {
                background-color: #e2e8f0;
                border: none;
                border-radius: 4px;
            }
            QProgressBar::chunk {
                background-color: #3b82f6;
                border-radius: 4px;
            }
        ''')
        main_layout.addWidget(self._progress_bar)

        # 状态标签
        self._status_label = QLabel('')
        self._status_label.setStyleSheet('''
            font-size: 13px;
            color: #64748b;
        ''')
        self._status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._status_label.setVisible(False)
        main_layout.addWidget(self._status_label)

        # 弹簧
        main_layout.addStretch()

        # 版本信息
        version_label = QLabel('v2.0.0 | 开源项目')
        version_label.setStyleSheet('''
            font-size: 12px;
            color: #94a3b8;
        ''')
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(version_label)

    def _connect_signals(self) -> None:
        """连接信号和槽。"""
        self._drop_area.file_dropped.connect(self._on_file_selected)
        self._drop_area.clicked.connect(self._on_select_file_clicked)
        self._convert_btn.clicked.connect(self._on_convert_clicked)

    @Slot()
    def _on_select_file_clicked(self) -> None:
        """处理选择文件按钮点击。"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            '选择 EPUB 文件',
            '',
            'EPUB 文件 (*.epub);;所有文件 (*.*)'
        )
        if file_path:
            self._on_file_selected(file_path)

    @Slot(str)
    def _on_file_selected(self, file_path: str) -> None:
        """处理文件选择。

        Args:
            file_path: 选择的文件路径。
        """
        self._current_file = Path(file_path)
        file_name = self._current_file.name
        file_size = self._current_file.stat().st_size
        size_str = self._format_size(file_size)

        self._file_info_label.setText(f'📖 {file_name} ({size_str})')
        self._file_info_label.setStyleSheet('''
            font-size: 13px;
            color: #059669;
            padding: 8px;
            background-color: #ecfdf5;
            border-radius: 6px;
        ''')

        self._convert_btn.setEnabled(True)

    @staticmethod
    def _format_size(size_bytes: int) -> str:
        """格式化文件大小。"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024:
                return f'{size_bytes:.1f} {unit}'
            size_bytes /= 1024
        return f'{size_bytes:.1f} TB'

    @Slot()
    def _on_convert_clicked(self) -> None:
        """处理转换按钮点击。"""
        if not self._current_file:
            return

        # 获取输出路径
        output_path = get_default_output_path(self._current_file)

        # 询问用户保存位置
        save_path, _ = QFileDialog.getSaveFileName(
            self,
            '保存 Markdown 文件',
            str(output_path),
            'Markdown 文件 (*.md);;所有文件 (*.*)'
        )

        if not save_path:
            return

        output_path = Path(save_path)

        # 配置选项
        options = ConversionOptions(
            extract_images=self._extract_images_cb.isChecked(),
            generate_toc=self._generate_toc_cb.isChecked()
        )

        # 禁用界面
        self._convert_btn.setEnabled(False)
        self._convert_btn.setText('转换中...')
        self._progress_bar.setVisible(True)
        self._progress_bar.setValue(0)
        self._status_label.setVisible(True)

        # 启动工作线程
        self._worker = ConversionWorker(
            self._current_file,
            output_path,
            options
        )
        self._worker.progress.connect(self._on_progress)
        self._worker.finished.connect(self._on_conversion_finished)
        self._worker.error.connect(self._on_conversion_error)
        self._worker.start()

    @Slot(int, str)
    def _on_progress(self, percentage: int, message: str) -> None:
        """处理进度更新。

        Args:
            percentage: 进度百分比。
            message: 状态消息。
        """
        self._progress_bar.setValue(percentage)
        self._status_label.setText(message)

    @Slot(object)
    def _on_conversion_finished(self, result: ConversionResult) -> None:
        """处理转换完成。

        Args:
            result: 转换结果。
        """
        self._convert_btn.setEnabled(True)
        self._convert_btn.setText('开始转换')

        if result.success:
            self._progress_bar.setValue(100)
            self._status_label.setText('转换完成！')

            # 显示成功对话框
            self._show_success_dialog(result)
        else:
            self._progress_bar.setVisible(False)
            self._status_label.setText(f'转换失败: {result.error_message}')
            self._status_label.setStyleSheet('''
                font-size: 13px;
                color: #dc2626;
            ''')

            QMessageBox.warning(
                self,
                '转换失败',
                f'转换过程中发生错误:\n{result.error_message}'
            )

    @Slot(str)
    def _on_conversion_error(self, error_message: str) -> None:
        """处理转换错误。

        Args:
            error_message: 错误消息。
        """
        self._convert_btn.setEnabled(True)
        self._convert_btn.setText('开始转换')
        self._progress_bar.setVisible(False)
        self._status_label.setText(f'错误: {error_message}')
        self._status_label.setStyleSheet('''
            font-size: 13px;
            color: #dc2626;
        ''')

        QMessageBox.critical(
            self,
            '错误',
            f'转换过程中发生错误:\n{error_message}'
        )

    def _show_success_dialog(self, result: ConversionResult) -> None:
        """显示转换成功对话框。

        Args:
            result: 转换结果。
        """
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle('转换成功')
        msg_box.setIcon(QMessageBox.Icon.Information)

        text = f'✅ 转换完成！\n\n'
        text += f'📄 文件: {result.markdown_path.name}\n'
        if result.image_count > 0:
            text += f'🖼️ 图片: {result.image_count} 张\n'
        text += f'📁 位置: {result.markdown_path.parent}'

        msg_box.setText(text)

        open_folder_btn = msg_box.addButton(
            '打开文件夹',
            QMessageBox.ButtonRole.ActionRole
        )
        open_file_btn = msg_box.addButton(
            '打开文件',
            QMessageBox.ButtonRole.ActionRole
        )
        close_btn = msg_box.addButton(
            '关闭',
            QMessageBox.ButtonRole.RejectRole
        )

        msg_box.exec()

        clicked = msg_box.clickedButton()
        if clicked == open_folder_btn:
            open_file_location(result.markdown_path)
        elif clicked == open_file_btn:
            open_file(result.markdown_path)

        # 如果勾选了自动打开文件夹
        if (self._open_folder_cb.isChecked() and
                clicked == close_btn):
            open_file_location(result.markdown_path)

        # 重置状态
        self._progress_bar.setVisible(False)
        self._status_label.setVisible(False)
