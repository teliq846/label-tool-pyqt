import matplotlib.colors as colors

# UI Configuration
UI_CONFIG = {
    'window_title': 'NIfTI Image Viewer',
    'window_size': (1000, 650),
    'control_panel_width': 200,
    'padding': 5,
    'font_family': 'Arial',
    'font_size': 9,
    'title_font_size': 11,
    'button_width': 20,
    'combobox_width': 15,
    'button_height': 30,
    'label_frame_text': "标签选择",
    'file_button_text': "选择文件",
    'load_button_text': "加载数据",
    'theme': 'cosmo',
    'style': {
        'button': {
            'width': 20,
            'padding': 5
        },
        'combobox': {
            'width': 15,
            'padding': 5
        },
        'labelframe': {
            'padding': 10
        }
    },
    'dark_mode': {
        'background': '#0A1929',  # Darker blue background
        'foreground': '#FFFFFF',
        'button_background': '#132F4C',  # Dark blue button
        'button_hover': '#173A5E',  # Slightly lighter blue for hover
        'frame_background': '#0D2339',  # Slightly lighter than background
        'accent_color': '#0288D1',  # Modern blue accent
        'accent_hover': '#029BE5',  # Lighter blue for hover
        'border_color': '#1E4976',  # Subtle blue border
        'separator_color': '#1E4976',
        'highlight_text': '#66B2FF',  # Light blue for highlighted text
    }
}

# Display Configuration
DISPLAY_CONFIG = {
    'figure_size': (3.5, 3.5),
    'dpi': 100,
    'cmap': colors.ListedColormap(['#0A1929', '#132F4C', '#FF9800']),  # Background, unlabeled, labeled
    'bounds': [0, 1, 2, 3],
    'contour_color': '#FF9800',  # Orange contour for labels
    'contour_width': 2.0,  # Slightly thicker for better visibility
    'slider_color': '#0288D1',
    'title_pad': 8,
    'text_pad': -0.2,
    'normalize_range': (0, 2),
    'interpolation': 'none',
    'origin': 'lower',
    'figure_facecolor': '#0A1929',
    'axes_facecolor': '#0A1929',
    'text_color': '#FFFFFF',
    'title_weight': 'bold',
    'title_size': 11,
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