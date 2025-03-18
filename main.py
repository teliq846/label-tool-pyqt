import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QPushButton,
                           QVBoxLayout, QHBoxLayout, QComboBox, QFileDialog,
                           QLabel, QFrame, QMessageBox, QSlider)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QIcon, QPalette, QColor
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

# 用于调试 - 打印当前文件信息
print(f"运行文件: {__file__}")
print(f"文件修改时间: {os.path.getmtime(__file__)}")
print(f"Python版本: {sys.version}")

import numpy as np
import matplotlib.font_manager as fm

from config import UI_CONFIG, FILE_CONFIG, DISPLAY_CONFIG, GRID_CONFIG, LABELS, ERROR_MESSAGES
from nifti_utils import NiftiDataManager

class DarkPalette(QPalette):
    def __init__(self):
        super().__init__()
        # 设置更透明的背景色以增强毛玻璃效果
        self.setColor(QPalette.ColorRole.Window, QColor(25, 25, 35, 220))  # 半透明背景
        self.setColor(QPalette.ColorRole.WindowText, QColor(230, 230, 230, 250))  # 更亮的文本颜色
        self.setColor(QPalette.ColorRole.Base, QColor(30, 30, 40, 200))  # 半透明基础色
        self.setColor(QPalette.ColorRole.Text, QColor(230, 230, 230, 250))
        self.setColor(QPalette.ColorRole.Button, QColor(40, 40, 50, 200))  # 半透明按钮背景
        self.setColor(QPalette.ColorRole.ButtonText, QColor(230, 230, 230, 250))

class SliceWidget(QFrame):
    slice_changed = pyqtSignal(str, int)

    def __init__(self, view: str, parent=None):
        super().__init__(parent)
        self.view = view
        self.setup_ui()
        # 设置毛玻璃效果
        self.setStyleSheet(f"""
            QFrame#slice_{self.view.lower()} {{
                background-color: rgba(35, 35, 45, 180);
                border: 1px solid rgba(255, 255, 255, 30);
                border-radius: 12px;
            }}
        """)
        self.setObjectName(f"slice_{self.view.lower()}")

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 12)
        layout.setSpacing(8)
        self.setFrameStyle(QFrame.Shape.NoFrame)

        # 添加顶部标题标签
        self.title_label = QLabel(f"{self.view} {LABELS['view']}")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setStyleSheet(f"""
            color: rgba(255, 255, 255, 240);
            font-weight: bold;
            font-size: {UI_CONFIG['title_font_size']}pt;
            padding: 6px;
            background-color: rgba(60, 60, 80, 180);
            border: 1px solid rgba(255, 255, 255, 30);
            border-radius: 6px;
            margin: 0px 4px;
        """)
        layout.addWidget(self.title_label)

        # 创建带透明背景的matplotlib图形
        self.figure = Figure(figsize=DISPLAY_CONFIG['figure_size'])
        self.figure.patch.set_facecolor((0, 0, 0, 0))  # 完全透明背景
        
        # 设置matplotlib字体属性以避免非英文文本的警告
        self.font_prop = fm.FontProperties(family='Arial')
        
        # 创建子图
        self.ax = self.figure.add_subplot(111)
        self.ax.set_facecolor((0.12, 0.12, 0.15, 0.6))  # 半透明背景
        
        # 完全移除坐标轴
        self.ax.set_axis_off()
        
        # 调整子图参数
        self.figure.subplots_adjust(left=0, right=1, bottom=0, top=1, wspace=0, hspace=0)
        
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setStyleSheet(f"""
            background-color: transparent;
            border: none;
        """)
        layout.addWidget(self.canvas)

        # 创建滑块
        slider_layout = QVBoxLayout()
        slider_layout.setSpacing(6)
        slider_layout.setContentsMargins(4, 0, 4, 0)

        self.slice_label = QLabel(f"{LABELS['slice']}: 0")
        self.slice_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.slice_label.setStyleSheet(f"""
            color: rgba(255, 255, 255, 240);
            font-size: {UI_CONFIG['font_size']}pt;
            padding: 4px;
            background-color: rgba(60, 60, 80, 180);
            border: 1px solid rgba(255, 255, 255, 30);
            border-radius: 6px;
        """)
        slider_layout.addWidget(self.slice_label)

        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setMinimum(0)
        self.slider.setMaximum(0)
        self.slider.valueChanged.connect(self._on_slice_changed)
        self.slider.setStyleSheet(f"""
            QSlider {{
                margin: 4px 0px;
            }}
            QSlider::groove:horizontal {{
                background: rgba(60, 60, 80, 180);
                height: 6px;
                border-radius: 3px;
            }}
            QSlider::handle:horizontal {{
                background: rgba(70, 130, 180, 220);
                width: 18px;
                margin: -6px 0;
                border-radius: 9px;
                border: 1px solid rgba(255, 255, 255, 50);
            }}
            QSlider::handle:horizontal:hover {{
                background: rgba(90, 150, 200, 220);
                border: 1px solid rgba(255, 255, 255, 70);
            }}
        """)
        slider_layout.addWidget(self.slider)

        layout.addLayout(slider_layout)

        # 初始化空图表 - 使用fontproperties避免缺失字形警告
        self.ax.text(0.5, 0.5, LABELS['please_load'],
                    ha='center', va='center', 
                    fontsize=UI_CONFIG['font_size'],
                    color=(1, 1, 1, 0.8),  # 使用matplotlib支持的元组格式(r,g,b,a)
                    fontproperties=self.font_prop)
        self.ax.set_xticks([])
        self.ax.set_yticks([])
        self.canvas.draw()

    def _on_slice_changed(self, value):
        self.slice_changed.emit(self.view.lower(), value)
        self.slice_label.setText(f"{LABELS['slice']}: {value}")

    def update_view(self, data: np.ndarray, mask: np.ndarray, slice_idx: int):
        self.ax.clear()
        
        # 确保深色背景
        self.ax.set_facecolor((0.12, 0.12, 0.15, 0.6))
        
        # 完全移除坐标轴
        self.ax.set_axis_off()
        
        # 使用精确范围显示数据
        height, width = data.T.shape
        # 创建用于可视化的彩色遮罩
        colored_data = np.zeros_like(data)  # 将所有数据设置为0（背景）
        colored_data[data > 0] = 1  # 将脑组织设置为1（未标记/蓝色）
        colored_data[mask > 0.5] = 2  # 将标记区域设置为2（橙色）
        
        # 使用更明亮的渐变色彩图，搭配毛玻璃效果
        custom_cmap = plt.cm.get_cmap('cool', 3)
        # 修改第一个颜色为透明黑色（背景）
        colors = custom_cmap(np.arange(3))
        colors[0] = [0, 0, 0, 0.3]  # 半透明黑色背景
        colors[1] = [0.2, 0.4, 0.8, 0.8]  # 半透明蓝色（脑组织）
        colors[2] = [1, 0.5, 0, 0.9]  # 橙色（标记区域）
        custom_cmap = plt.matplotlib.colors.ListedColormap(colors)
        
        self.ax.imshow(colored_data.T, 
                      extent=(-0.5, width-0.5, -0.5, height-0.5),
                      cmap=custom_cmap,
                      norm=plt.Normalize(0, 2),  # 明确设置范围从0到2
                      origin=DISPLAY_CONFIG['origin'],
                      interpolation='bilinear')  # 使用双线性插值使图像更平滑
        
        # 添加具有相同范围的轮廓
        self.ax.contour(np.arange(width), np.arange(height), mask.T,
                       levels=[0.5],
                       colors=[(1, 1, 1, 0.7)],  # 半透明白色轮廓 - 已经是正确的元组格式
                       linewidths=1.5)
        
        # 更新Qt标签中的切片文本（不是在matplotlib中）
        self.slice_label.setText(f"{LABELS['slice']}: {slice_idx}")
        
        # 移除刻度并确保坐标轴不扩展
        self.ax.set_axis_off()
        self.ax.set_xlim(-0.5, width-0.5)
        self.ax.set_ylim(-0.5, height-0.5)
        
        # 更新滑块
        if self.slider.maximum() == 0:
            self.slider.setMaximum(data.shape[0] - 1)
        self.slider.setValue(slice_idx)
        
        # 确保紧凑布局并重绘
        self.figure.tight_layout()
        self.canvas.draw()

class ControlPanel(QFrame):
    file_selected = pyqtSignal()
    load_clicked = pyqtSignal()
    label_changed = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumWidth(UI_CONFIG['control_panel_width'])
        self.setMaximumWidth(UI_CONFIG['control_panel_width'])
        self.setup_ui()
        # 设置毛玻璃效果
        self.setStyleSheet(f"""
            QFrame#controlPanel {{
                background-color: rgba(30, 30, 40, 180);
                border: 1px solid rgba(255, 255, 255, 30);
                border-radius: 12px;
            }}
        """)
        self.setObjectName("controlPanel")

    def setup_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)  # 保留无内容边距
        self.main_layout.setSpacing(0)  # 保留无间距
        self.setFrameStyle(QFrame.Shape.NoFrame)
        
        # 内容容器
        self.content_widget = QWidget()
        self.content_widget.setContentsMargins(10, 10, 10, 10)
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(10)
        
        # 顶部布局 - 保留固定高度以保持对齐
        top_layout = QHBoxLayout()
        top_layout.setContentsMargins(10, 8, 10, 0)  # 固定顶部边距为8px
        top_layout.setSpacing(6)
        
        # 只保留标题
        panel_title = QLabel("Control Panel")
        panel_title.setStyleSheet(f"""
            color: rgba(255, 255, 255, 240);
            font-weight: bold;
            font-size: {UI_CONFIG['title_font_size']}pt;
            padding: 4px;
        """)
        
        top_layout.addWidget(panel_title)
        top_layout.addStretch()
        
        self.content_layout.addLayout(top_layout)
        
        # 创建分隔线
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFixedHeight(1)
        separator.setStyleSheet(f"""
            background-color: rgba(255, 255, 255, 50);
            margin: 8px 0px;
        """)
        self.content_layout.addWidget(separator)
        
        # 毛玻璃按钮样式
        button_style = f"""
            QPushButton {{
                background-color: rgba(60, 60, 80, 180);
                color: rgba(255, 255, 255, 240);
                padding: 10px;
                border-radius: 8px;
                font-size: {UI_CONFIG['font_size']}pt;
                border: 1px solid rgba(255, 255, 255, 30);
            }}
            QPushButton:hover {{
                background-color: rgba(80, 80, 100, 200);
                border: 1px solid rgba(255, 255, 255, 50);
            }}
        """
        
        accent_button_style = f"""
            QPushButton {{
                background-color: rgba(70, 130, 180, 200);
                color: rgba(255, 255, 255, 240);
                padding: 10px;
                border-radius: 8px;
                font-size: {UI_CONFIG['font_size']}pt;
                border: 1px solid rgba(255, 255, 255, 50);
            }}
            QPushButton:hover {{
                background-color: rgba(90, 150, 200, 220);
                border: 1px solid rgba(255, 255, 255, 70);
            }}
        """
        
        self.file_button = QPushButton(LABELS['select_file'])
        self.file_button.setStyleSheet(button_style)
        self.file_button.clicked.connect(self.file_selected.emit)
        self.file_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.content_layout.addWidget(self.file_button)

        self.load_button = QPushButton(LABELS['load_data'])
        self.load_button.setStyleSheet(accent_button_style)
        self.load_button.clicked.connect(self.load_clicked.emit)
        self.load_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.content_layout.addWidget(self.load_button)

        # 标签选择带毛玻璃效果
        frame_style = f"""
            QFrame {{
                background-color: rgba(50, 50, 70, 180);
                border-radius: 12px;
                border: 1px solid rgba(255, 255, 255, 40);
                padding: 8px;
            }}
            QFrame:hover {{
                border: 1px solid rgba(255, 255, 255, 60);
                background-color: rgba(55, 55, 75, 200);
            }}
        """
        
        label_frame = QFrame()
        label_frame.setFrameStyle(QFrame.Shape.NoFrame)
        label_frame.setStyleSheet(frame_style)
        label_layout = QVBoxLayout(label_frame)
        label_layout.setContentsMargins(12, 12, 12, 15)
        label_layout.setSpacing(12)
        
        # 添加标题容器，带图标效果
        title_container = QHBoxLayout()
        title_container.setContentsMargins(0, 0, 0, 0)
        title_container.setSpacing(8)
        
        # 模拟标签图标
        label_icon = QLabel("🏷️")
        label_icon.setStyleSheet(f"""
            font-size: {UI_CONFIG['title_font_size'] + 2}pt;
            color: rgba(255, 255, 255, 240);
        """)
        title_container.addWidget(label_icon)
        
        # 标题文本
        label_title = QLabel(LABELS['label_selection'])
        label_title.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        label_title.setStyleSheet(f"""
            color: rgba(255, 255, 255, 240);
            font-weight: bold;
            font-size: {UI_CONFIG['title_font_size']}pt;
        """)
        title_container.addWidget(label_title)
        title_container.addStretch()
        
        label_layout.addLayout(title_container)
        
        # 添加说明标签
        hint_label = QLabel(f"选择要查看的标签类别")
        hint_label.setWordWrap(True)
        hint_label.setStyleSheet(f"""
            color: rgba(255, 255, 255, 180);
            font-size: {UI_CONFIG['font_size'] - 1}pt;
            padding-left: 2px;
            font-style: italic;
        """)
        label_layout.addWidget(hint_label)
        
        # 改进的毛玻璃组合框样式
        self.label_combo = QComboBox()
        self.label_combo.setStyleSheet(f"""
            QComboBox {{
                background-color: rgba(40, 40, 60, 180);
                color: rgba(255, 255, 255, 240);
                border-radius: 8px;
                padding: 10px 12px;
                border: 1px solid rgba(255, 255, 255, 40);
                font-size: {UI_CONFIG['font_size']}pt;
                font-weight: bold;
                selection-background-color: rgba(70, 130, 180, 150);
                min-height: 30px;
            }}
            QComboBox:hover {{
                background-color: rgba(60, 60, 80, 220);
                border: 1px solid rgba(255, 255, 255, 60);
            }}
            QComboBox:focus {{
                border: 1px solid rgba(100, 170, 255, 160);
            }}
            QComboBox::drop-down {{
                subcontrol-origin: padding;
                subcontrol-position: right center;
                width: 30px;
                border-left: none;
                border-top-right-radius: 8px;
                border-bottom-right-radius: 8px;
            }}
            QComboBox::down-arrow {{
                image: none;
                width: 20px;
                height: 20px;
                background-color: rgba(255, 255, 255, 160);
                mask: url(down_arrow.png);
                -qt-mask: url(down_arrow.png);
            }}
            QComboBox QAbstractItemView {{
                background-color: rgba(45, 45, 65, 245);
                color: rgba(255, 255, 255, 240);
                selection-background-color: rgba(70, 130, 180, 200);
                border: 1px solid rgba(255, 255, 255, 60);
                border-radius: 8px;
                padding: 4px;
            }}
            QComboBox QAbstractItemView::item {{
                min-height: 24px;
                padding: 4px 8px;
                border-radius: 4px;
            }}
            QComboBox QAbstractItemView::item:hover {{
                background-color: rgba(80, 140, 200, 100);
            }}
            QComboBox QAbstractItemView::item:selected {{
                background-color: rgba(70, 130, 180, 200);
            }}
        """)
        self.label_combo.currentIndexChanged.connect(self._on_label_changed)
        self.label_combo.setCursor(Qt.CursorShape.PointingHandCursor)
        
        # 添加组合框下方的标签计数显示
        self.label_count = QLabel("当前暂无标签")
        self.label_count.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_count.setStyleSheet(f"""
            color: rgba(255, 255, 255, 180);
            font-size: {UI_CONFIG['font_size'] - 1}pt;
            padding: 4px;
            margin-top: 2px;
        """)
        
        # 创建标签选择容器
        combo_container = QVBoxLayout()
        combo_container.setSpacing(4)
        combo_container.addWidget(self.label_combo)
        combo_container.addWidget(self.label_count)
        
        label_layout.addLayout(combo_container)
        
        # 添加额外的标签选项按钮区域
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(8)
        
        # 可以添加排序按钮等功能扩展
        self.sort_button = QPushButton("排序")
        self.sort_button.setStyleSheet(f"""
            QPushButton {{
                background-color: rgba(60, 60, 90, 150);
                color: rgba(255, 255, 255, 220);
                padding: 6px 10px;
                border-radius: 6px;
                font-size: {UI_CONFIG['font_size'] - 1}pt;
                border: 1px solid rgba(255, 255, 255, 30);
                min-width: 60px;
            }}
            QPushButton:hover {{
                background-color: rgba(70, 70, 100, 180);
                border: 1px solid rgba(255, 255, 255, 50);
            }}
            QPushButton:pressed {{
                background-color: rgba(50, 50, 80, 180);
            }}
        """)
        self.sort_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.sort_button.clicked.connect(self._toggle_sort_order)
        self.sort_ascending = True  # 默认升序排序
        buttons_layout.addWidget(self.sort_button)
        
        self.refresh_button = QPushButton("刷新")
        self.refresh_button.setStyleSheet(f"""
            QPushButton {{
                background-color: rgba(60, 60, 90, 150);
                color: rgba(255, 255, 255, 220);
                padding: 6px 10px;
                border-radius: 6px;
                font-size: {UI_CONFIG['font_size'] - 1}pt;
                border: 1px solid rgba(255, 255, 255, 30);
                min-width: 60px;
            }}
            QPushButton:hover {{
                background-color: rgba(70, 70, 100, 180);
                border: 1px solid rgba(255, 255, 255, 50);
            }}
            QPushButton:pressed {{
                background-color: rgba(50, 50, 80, 180);
            }}
        """)
        self.refresh_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.refresh_button.clicked.connect(self._refresh_labels)
        buttons_layout.addWidget(self.refresh_button)
        
        label_layout.addLayout(buttons_layout)
        
        self.content_layout.addWidget(label_frame)
        
        # 描述部分
        desc_frame = QFrame()
        desc_frame.setFrameStyle(QFrame.Shape.NoFrame)
        desc_frame.setStyleSheet(frame_style)
        desc_layout = QVBoxLayout(desc_frame)
        desc_layout.setContentsMargins(12, 12, 12, 12)
        
        # 添加描述标题和图标
        desc_title_layout = QHBoxLayout()
        desc_title_layout.setSpacing(8)
        
        desc_icon = QLabel("ℹ️")
        desc_icon.setStyleSheet(f"""
            font-size: {UI_CONFIG['title_font_size'] + 2}pt;
            color: rgba(255, 255, 255, 240);
        """)
        desc_title_layout.addWidget(desc_icon)
        
        desc_title = QLabel("详细信息")
        desc_title.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        desc_title.setStyleSheet(f"""
            color: rgba(255, 255, 255, 240);
            font-weight: bold;
            font-size: {UI_CONFIG['title_font_size']}pt;
        """)
        desc_title_layout.addWidget(desc_title)
        desc_title_layout.addStretch()
        
        desc_layout.addLayout(desc_title_layout)
        
        # 更美观的描述标签
        desc_label = QLabel(LABELS['description'])
        desc_label.setWordWrap(True)
        desc_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        desc_label.setStyleSheet(f"""
            color: rgba(255, 255, 255, 230);
            font-size: {UI_CONFIG['font_size']}pt;
            line-height: 150%;
            padding: 8px 4px;
            background-color: rgba(40, 40, 60, 80);
            border-radius: 6px;
        """)
        desc_layout.addWidget(desc_label)
        
        self.content_layout.addWidget(desc_frame)
        self.content_layout.addStretch()
        
        # 将内容添加到主布局
        self.main_layout.addWidget(self.content_widget)

    def _on_label_changed(self, index):
        if index >= 0:
            label = self.label_combo.itemData(index)
            if label is not None:
                self.label_changed.emit(label)

    def update_file_button(self, filename: str):
        self.file_button.setText(LABELS['file_selected'].format(filename))

    def update_labels(self, labels: list):
        # 保存当前标签列表用于排序和刷新
        self.current_labels = labels if labels else []
        self.label_combo.clear()
        
        # 根据排序顺序排序标签
        sorted_labels = sorted(self.current_labels, reverse=not self.sort_ascending)
        
        for label in sorted_labels:
            self.label_combo.addItem(str(label), label)
        
        # 更新标签计数显示
        if len(self.current_labels) > 0:
            self.label_count.setText(f"共 {len(self.current_labels)} 个标签")
            # 更新排序按钮文本，显示当前排序顺序
            self.sort_button.setText("↑ 升序" if self.sort_ascending else "↓ 降序")
        else:
            self.label_count.setText("当前暂无标签")
            self.sort_button.setText("排序")
            
    def _toggle_sort_order(self):
        # 切换排序顺序
        self.sort_ascending = not self.sort_ascending
        
        # 如果有标签，则重新排序
        if hasattr(self, 'current_labels') and self.current_labels:
            # 保存当前选中的标签
            current_label = self.label_combo.currentData()
            
            # 更新标签列表（会根据self.sort_ascending重新排序）
            self.update_labels(self.current_labels)
            
            # 如果之前有选中的标签，尝试恢复选中状态
            if current_label is not None:
                for i in range(self.label_combo.count()):
                    if self.label_combo.itemData(i) == current_label:
                        self.label_combo.setCurrentIndex(i)
                        break
        
    def _refresh_labels(self):
        # 触发刷新事件
        self.file_selected.emit()  # 这将触发MainWindow重新加载文件并更新标签

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.data_manager = NiftiDataManager()
        self.current_file = None
        self.setup_ui()
        
        # 设置窗口图标
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), FILE_CONFIG['icon_path'])
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

    def setup_ui(self):
        self.setWindowTitle(UI_CONFIG['window_title'])
        self.resize(*UI_CONFIG['window_size'])

        # 创建主部件
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        # 设置主窗口的背景色，使毛玻璃效果更明显
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                                stop:0 #1a1a2a, 
                                                stop:0.5 #252540, 
                                                stop:1 #1a1a2a);
            }}
        """)

        # 主布局
        self.main_layout = QHBoxLayout(main_widget)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(10)

        # 创建控制面板
        self.control_panel = ControlPanel()
        self.control_panel.file_selected.connect(self.open_file)
        self.control_panel.load_clicked.connect(self.load_data)
        self.control_panel.label_changed.connect(self.update_label)
        self.main_layout.addWidget(self.control_panel)

        # 创建视图布局
        self.view_container = QFrame()
        self.view_container.setFrameStyle(QFrame.Shape.NoFrame)
        self.view_container.setStyleSheet(f"""
            QFrame#viewContainer {{
                background-color: rgba(35, 35, 45, 160);
                border: 1px solid rgba(255, 255, 255, 30);
                border-radius: 12px;
            }}
        """)
        self.view_container.setObjectName("viewContainer")
        view_layout = QHBoxLayout(self.view_container)
        view_layout.setSpacing(10)
        view_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.addWidget(self.view_container)

        # Create slice views
        self.views = {}
        for view in GRID_CONFIG['views']:
            slice_widget = SliceWidget(view)
            slice_widget.slice_changed.connect(self.update_slice)
            view_layout.addWidget(slice_widget)
            self.views[view] = slice_widget

    def open_file(self):
        try:
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                LABELS['select_file'],
                FILE_CONFIG['initial_dir'],
                "NIfTI files (*.nii.gz)"
            )
            if file_path:
                self.current_file = file_path
                self.control_panel.update_file_button(os.path.basename(file_path))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open file: {str(e)}")

    def load_data(self):
        if not self.current_file:
            QMessageBox.warning(self, "Warning", ERROR_MESSAGES['no_file'])
            return

        try:
            if self.data_manager.load_file(self.current_file):
                # Convert labels to integers and sort them
                labels = sorted([int(label) for label in self.data_manager.unique_labels])
                self.control_panel.update_labels(labels)
                self.update_all_views()
            else:
                QMessageBox.critical(self, "Error", ERROR_MESSAGES['load_failed'])
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load data: {str(e)}")

    def update_label(self, label: int):
        try:
            self.data_manager.set_current_label(label)
            self.update_all_views()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to update label: {str(e)}")

    def update_slice(self, view: str, value: int):
        try:
            if not hasattr(self.data_manager, '_data_cache') or self.data_manager._data_cache is None:
                QMessageBox.warning(self, "Warning", ERROR_MESSAGES['no_data'])
                return

            self.data_manager.current_slices[view] = int(value)
            self.update_view(view)
        except Exception as e:
            print(f"Error updating slice: {e}")
            QMessageBox.critical(self, "Error", f"Failed to update slice: {str(e)}")

    def update_view(self, view: str):
        try:
            if not hasattr(self.data_manager, '_data_cache') or self.data_manager._data_cache is None:
                QMessageBox.warning(self, "Warning", ERROR_MESSAGES['no_data'])
                return

            slice_data, mask = self.data_manager.get_slice_data(
                view,
                self.data_manager.current_slices[view]
            )
            self.views[view.title()].update_view(
                slice_data,
                mask,
                self.data_manager.current_slices[view]
            )
        except Exception as e:
            print(f"Error updating view: {e}")
            QMessageBox.critical(self, "Error", f"Failed to update view: {str(e)}")

    def update_all_views(self):
        try:
            if not hasattr(self.data_manager, '_data_cache') or self.data_manager._data_cache is None:
                QMessageBox.warning(self, "Warning", ERROR_MESSAGES['no_data'])
                return

            for view in [v.lower() for v in GRID_CONFIG['views']]:
                try:
                    self.update_view(view)
                except Exception as e:
                    print(f"Error updating {view} view: {e}")
                    continue
        except Exception as e:
            print(f"Error updating all views: {e}")
            QMessageBox.critical(self, "Error", f"Failed to update all views: {str(e)}")

if __name__ == '__main__':
    try:
        app = QApplication(sys.argv)
        
        # 设置应用程序图标
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), FILE_CONFIG['icon_path'])
        if os.path.exists(icon_path):
            app.setWindowIcon(QIcon(icon_path))
        
        # 应用暗色主题
        app.setStyle('Fusion')
        app.setPalette(DarkPalette())
        
        # 设置应用程序样式表增强毛玻璃效果
        app.setStyleSheet("""
            QToolTip {
                background-color: rgba(40, 40, 60, 220);
                color: white;
                border: 1px solid rgba(255, 255, 255, 40);
                border-radius: 4px;
                padding: 4px;
            }
            
            QScrollBar:vertical {
                background: rgba(30, 30, 40, 120);
                width: 12px;
                border-radius: 6px;
            }
            
            QScrollBar::handle:vertical {
                background: rgba(80, 80, 120, 180);
                min-height: 20px;
                border-radius: 6px;
            }
            
            QScrollBar::handle:vertical:hover {
                background: rgba(100, 100, 150, 200);
            }
            
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            
            QScrollBar:horizontal {
                background: rgba(30, 30, 40, 120);
                height: 12px;
                border-radius: 6px;
            }
            
            QScrollBar::handle:horizontal {
                background: rgba(80, 80, 120, 180);
                min-width: 20px;
                border-radius: 6px;
            }
            
            QScrollBar::handle:horizontal:hover {
                background: rgba(100, 100, 150, 200);
            }
            
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                width: 0px;
            }
        """)
        
        window = MainWindow()
        
        # 使用淡入效果显示窗口
        window.setWindowOpacity(0)
        window.show()
        
        # 动画效果淡入
        for i in range(1, 11):
            window.setWindowOpacity(i/10)
            app.processEvents()
            QTimer.singleShot(20, app.processEvents)
        
        sys.exit(app.exec())
    except Exception as e:
        QMessageBox.critical(None, "Error", f"Failed to start application: {str(e)}")