import matplotlib.colors as colors

# UI Configuration
UI_CONFIG = {
    'window_title': 'NIfTI Image Viewer',
    'window_size': (1200, 700),  # 更大的窗口尺寸
    'control_panel_width': 240,   # 更宽的控制面板
    'padding': 8,                 # 更大的内边距
    'font_family': 'SF Pro Text', # macOS默认字体
    'font_size': 13,              # 更大的字体
    'title_font_size': 14,        # 更大的标题字体
    'button_width': 20,
    'combobox_width': 15,
    'button_height': 32,          # 更高的按钮
    'label_frame_text': "标签选择",
    'file_button_text': "选择文件",
    'load_button_text': "加载数据",
    'theme': 'macOS',
    'style': {
        'button': {
            'width': 20,
            'padding': 8
        },
        'combobox': {
            'width': 15,
            'padding': 8
        },
        'labelframe': {
            'padding': 12
        }
    },
    'dark_mode': {
        'background': '#1E1E1E',           # 深色背景
        'foreground': '#FFFFFF',           # 白色文字
        'button_background': '#323232',    # 按钮背景
        'button_hover': '#404040',         # 按钮悬停
        'frame_background': '#252525',     # 框架背景
        'accent_color': '#007AFF',         # macOS蓝色
        'accent_hover': '#0063CC',         # 深蓝色悬停
        'border_color': '#323232',         # 边框颜色
        'separator_color': '#323232',      # 分隔线颜色
        'highlight_text': '#007AFF',       # 高亮文字
    }
}

# Display Configuration
DISPLAY_CONFIG = {
    'figure_size': (4, 4),        # 更大的图像尺寸
    'dpi': 100,
    'cmap': colors.ListedColormap(['#1E1E1E', '#323232', '#007AFF']),  # 更新颜色方案
    'bounds': [0, 1, 2, 3],
    'contour_color': '#007AFF',   # 使用macOS蓝色
    'contour_width': 1.5,         # 更细的轮廓线
    'slider_color': '#007AFF',    # macOS蓝色滑块
    'title_pad': 12,
    'text_pad': -0.2,
    'normalize_range': (0, 2),
    'interpolation': 'nearest',    # 更清晰的图像显示
    'origin': 'lower',
    'figure_facecolor': '#1E1E1E',
    'axes_facecolor': '#1E1E1E',
    'text_color': '#FFFFFF',
    'title_weight': 'medium',      # macOS风格的字重
    'title_size': 14,
}

# File Configuration
FILE_CONFIG = {
    'initial_dir': './data',
    'file_types': [("NIfTI files", "*.nii.gz")],
    'icon_path': 'icon/label-tool.ico',
    'file_dialog_title': "选择NIfTI文件",
}

# Grid Configuration
GRID_CONFIG = {
    'height_ratios': [1, 5, 1],
    'width_ratios': [1, 1, 1],
    'suptitle_y': 0.98,
    'views': ['Axial', 'Coronal', 'Sagittal'],
}

# Labels and Messages
LABELS = {
    'select_file': 'Select File',
    'load_data': 'Load Data',
    'label_selection': 'Label Selection',
    'slice': 'Slice',
    'view': 'View',
    'please_load': 'Please load data',
    'file_selected': 'Selected: {}',
    'description': 'This software is designed to visualize the correspondence between NIfTI file label numbers and their annotated regions.',
}

# Error Messages
ERROR_MESSAGES = {
    'no_file': "Please select a file first",
    'load_failed': "Failed to load data",
    'update_failed': "Failed to update",
    'invalid_view': "Invalid view",
    'no_data': "No data loaded",
} 