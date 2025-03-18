import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QPushButton,
                           QVBoxLayout, QHBoxLayout, QComboBox, QFileDialog,
                           QLabel, QFrame, QMessageBox, QSlider)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QIcon, QPalette, QColor
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np

from config import UI_CONFIG, FILE_CONFIG, DISPLAY_CONFIG, GRID_CONFIG, LABELS, ERROR_MESSAGES
from nifti_utils import NiftiDataManager

class DarkPalette(QPalette):
    def __init__(self):
        super().__init__()
        self.setColor(QPalette.ColorRole.Window, QColor(UI_CONFIG['dark_mode']['background']))
        self.setColor(QPalette.ColorRole.WindowText, QColor(UI_CONFIG['dark_mode']['foreground']))
        self.setColor(QPalette.ColorRole.Base, QColor(UI_CONFIG['dark_mode']['background']))
        self.setColor(QPalette.ColorRole.Text, QColor(UI_CONFIG['dark_mode']['foreground']))
        self.setColor(QPalette.ColorRole.Button, QColor(UI_CONFIG['dark_mode']['button_background']))
        self.setColor(QPalette.ColorRole.ButtonText, QColor(UI_CONFIG['dark_mode']['foreground']))

class SliceWidget(QFrame):
    slice_changed = pyqtSignal(str, int)

    def __init__(self, view: str, parent=None):
        super().__init__(parent)
        self.view = view
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 12)
        layout.setSpacing(8)
        self.setFrameStyle(QFrame.Shape.NoFrame)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {UI_CONFIG['dark_mode']['frame_background']};
                border-radius: 8px;
                margin-bottom: 4px;
            }}
        """)

        # Create matplotlib figure with tight layout
        self.figure = Figure(figsize=DISPLAY_CONFIG['figure_size'])
        self.figure.patch.set_facecolor(DISPLAY_CONFIG['figure_facecolor'])
        
        # Create subplot with specific spacing
        self.ax = self.figure.add_subplot(111)
        self.ax.set_facecolor(DISPLAY_CONFIG['axes_facecolor'])
        
        # Remove axes completely
        self.ax.set_axis_off()
        
        # Adjust subplot parameters to remove white lines
        self.figure.subplots_adjust(left=0, right=1, bottom=0, top=0.9, wspace=0, hspace=0)
        
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setStyleSheet(f"""
            background-color: {UI_CONFIG['dark_mode']['frame_background']};
            border: none;
        """)
        layout.addWidget(self.canvas)

        # Create slider
        slider_layout = QVBoxLayout()
        slider_layout.setSpacing(6)
        slider_layout.setContentsMargins(4, 0, 4, 0)

        self.slice_label = QLabel(f"{LABELS['slice']}: 0")
        self.slice_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.slice_label.setStyleSheet(f"""
            color: {UI_CONFIG['dark_mode']['highlight_text']};
            font-size: {UI_CONFIG['font_size']}pt;
            padding: 2px;
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
                background: {UI_CONFIG['dark_mode']['button_background']};
                height: 6px;
                border-radius: 3px;
            }}
            QSlider::handle:horizontal {{
                background: {UI_CONFIG['dark_mode']['accent_color']};
                width: 18px;
                margin: -6px 0;
                border-radius: 9px;
            }}
            QSlider::handle:horizontal:hover {{
                background: {UI_CONFIG['dark_mode']['accent_hover']};
            }}
        """)
        slider_layout.addWidget(self.slider)

        layout.addLayout(slider_layout)

        # Initialize empty plot
        self.ax = self.figure.add_subplot(111)
        self.ax.set_facecolor(DISPLAY_CONFIG['axes_facecolor'])
        
        # Set title with bold font
        self.ax.set_title(f"{self.view} {LABELS['view']}", 
                         color=DISPLAY_CONFIG['text_color'],
                         fontweight=DISPLAY_CONFIG['title_weight'],
                         fontsize=DISPLAY_CONFIG['title_size'],
                         pad=DISPLAY_CONFIG['title_pad'])
        
        self.ax.text(0.5, 0.5, LABELS['please_load'],
                    ha='center', va='center', 
                    fontsize=UI_CONFIG['font_size'],
                    color=DISPLAY_CONFIG['text_color'])
        self.ax.set_xticks([])
        self.ax.set_yticks([])
        self.canvas.draw()

    def _on_slice_changed(self, value):
        self.slice_changed.emit(self.view.lower(), value)
        self.slice_label.setText(f"{LABELS['slice']}: {value}")

    def update_view(self, data: np.ndarray, mask: np.ndarray, slice_idx: int):
        self.ax.clear()
        
        # Ensure dark background
        self.ax.set_facecolor(DISPLAY_CONFIG['axes_facecolor'])
        
        # Remove axes completely
        self.ax.set_axis_off()
        
        # Display data with exact extent
        height, width = data.T.shape
        # Create a colored mask for visualization
        colored_data = np.zeros_like(data)  # Set all data to 0 (background)
        colored_data[data > 0] = 1  # Set brain tissue to 1 (unlabeled/blue)
        colored_data[mask > 0.5] = 2  # Set labeled regions to 2 (orange)
        
        self.ax.imshow(colored_data.T, 
                      extent=(-0.5, width-0.5, -0.5, height-0.5),
                      cmap=DISPLAY_CONFIG['cmap'],
                      norm=plt.Normalize(0, 2),  # Explicitly set range from 0 to 2
                      origin=DISPLAY_CONFIG['origin'],
                      interpolation=DISPLAY_CONFIG['interpolation'])
        
        # Add contour with same extent
        self.ax.contour(np.arange(width), np.arange(height), mask.T,
                       levels=[0.5],
                       colors=DISPLAY_CONFIG['contour_color'],
                       linewidths=DISPLAY_CONFIG['contour_width'])
        
        # Update title with bold font
        self.ax.set_title(f"{self.view} {LABELS['view']}", 
                         color=DISPLAY_CONFIG['text_color'],
                         fontweight=DISPLAY_CONFIG['title_weight'],
                         fontsize=DISPLAY_CONFIG['title_size'],
                         pad=DISPLAY_CONFIG['title_pad'])
        
        # Remove ticks and ensure axes don't expand
        self.ax.set_axis_off()
        self.ax.set_xlim(-0.5, width-0.5)
        self.ax.set_ylim(-0.5, height-0.5)
        
        # Update slider
        if self.slider.maximum() == 0:
            self.slider.setMaximum(data.shape[0] - 1)
        self.slider.setValue(slice_idx)
        
        # Ensure tight layout and redraw
        self.figure.tight_layout()
        self.canvas.draw()

class ControlPanel(QFrame):
    file_selected = pyqtSignal()
    load_clicked = pyqtSignal()
    label_changed = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(12)
        self.setFixedWidth(UI_CONFIG['control_panel_width'])
        self.setFrameStyle(QFrame.Shape.NoFrame)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {UI_CONFIG['dark_mode']['frame_background']};
                border-radius: 8px;
            }}
        """)

        # File selection button
        self.file_button = QPushButton(LABELS['select_file'])
        self.file_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {UI_CONFIG['dark_mode']['button_background']};
                color: {UI_CONFIG['dark_mode']['foreground']};
                padding: 10px;
                border-radius: 6px;
                font-size: {UI_CONFIG['font_size']}pt;
            }}
            QPushButton:hover {{
                background-color: {UI_CONFIG['dark_mode']['button_hover']};
            }}
        """)
        self.file_button.clicked.connect(self.file_selected.emit)
        layout.addWidget(self.file_button)

        # Load button
        self.load_button = QPushButton(LABELS['load_data'])
        self.load_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {UI_CONFIG['dark_mode']['accent_color']};
                color: {UI_CONFIG['dark_mode']['foreground']};
                padding: 10px;
                border-radius: 6px;
                font-size: {UI_CONFIG['font_size']}pt;
            }}
            QPushButton:hover {{
                background-color: {UI_CONFIG['dark_mode']['accent_hover']};
            }}
        """)
        self.load_button.clicked.connect(self.load_clicked.emit)
        layout.addWidget(self.load_button)

        # Label selection frame
        label_frame = QFrame()
        label_frame.setFrameStyle(QFrame.Shape.NoFrame)
        label_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {UI_CONFIG['dark_mode']['button_background']};
                border-radius: 6px;
                padding: 2px;
            }}
        """)
        label_layout = QVBoxLayout(label_frame)
        label_layout.setContentsMargins(12, 12, 12, 12)
        label_layout.setSpacing(8)
        
        label_title = QLabel(LABELS['label_selection'])
        label_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label_title.setStyleSheet(f"""
            color: {UI_CONFIG['dark_mode']['highlight_text']};
            font-weight: bold;
            font-size: {UI_CONFIG['title_font_size']}pt;
        """)
        label_layout.addWidget(label_title)
        
        self.label_combo = QComboBox()
        self.label_combo.setStyleSheet(f"""
            QComboBox {{
                background-color: {UI_CONFIG['dark_mode']['background']};
                color: {UI_CONFIG['dark_mode']['foreground']};
                border-radius: 4px;
                padding: 6px;
                min-height: 24px;
            }}
            QComboBox:hover {{
                background-color: {UI_CONFIG['dark_mode']['button_hover']};
            }}
            QComboBox::drop-down {{
                border: none;
                width: 20px;
            }}
            QComboBox::down-arrow {{
                image: none;
                border: none;
            }}
            QComboBox QAbstractItemView {{
                background-color: {UI_CONFIG['dark_mode']['background']};
                color: {UI_CONFIG['dark_mode']['foreground']};
                selection-background-color: {UI_CONFIG['dark_mode']['accent_color']};
                selection-color: {UI_CONFIG['dark_mode']['foreground']};
                border-radius: 4px;
                outline: none;
            }}
            QComboBox QAbstractItemView::item {{
                padding: 4px 6px;
                border-radius: 2px;
                margin: 2px;
            }}
            QComboBox QAbstractItemView::item:hover {{
                background-color: {UI_CONFIG['dark_mode']['highlight_text']};
                color: {UI_CONFIG['dark_mode']['background']};
            }}
            QComboBox QAbstractItemView::item:selected {{
                background-color: {UI_CONFIG['dark_mode']['accent_color']};
                color: {UI_CONFIG['dark_mode']['foreground']};
            }}
        """)
        self.label_combo.currentIndexChanged.connect(self._on_label_changed)
        label_layout.addWidget(self.label_combo)
        
        layout.addWidget(label_frame)

        # Description text
        desc_frame = QFrame()
        desc_frame.setFrameStyle(QFrame.Shape.NoFrame)
        desc_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {UI_CONFIG['dark_mode']['button_background']};
                border-radius: 6px;
                padding: 2px;
            }}
        """)
        desc_layout = QVBoxLayout(desc_frame)
        desc_layout.setContentsMargins(12, 12, 12, 12)
        
        desc_label = QLabel(LABELS['description'])
        desc_label.setWordWrap(True)
        desc_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        desc_label.setStyleSheet(f"""
            color: {UI_CONFIG['dark_mode']['foreground']};
            font-size: {UI_CONFIG['font_size']}pt;
        """)
        desc_layout.addWidget(desc_label)
        
        layout.addWidget(desc_frame)
        layout.addStretch()

    def _on_label_changed(self, index):
        if index >= 0:  # Ensure valid index
            label = self.label_combo.itemData(index)
            if label is not None:
                self.label_changed.emit(label)

    def update_file_button(self, filename: str):
        self.file_button.setText(LABELS['file_selected'].format(filename))

    def update_labels(self, labels: list):
        self.label_combo.clear()
        for label in sorted(labels):  # Sort labels numerically
            self.label_combo.addItem(str(label), label)  # Just show the number

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.data_manager = NiftiDataManager()
        self.current_file = None
        self.setup_ui()
        
        # Set window icon
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), FILE_CONFIG['icon_path'])
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

    def setup_ui(self):
        self.setWindowTitle(UI_CONFIG['window_title'])
        self.resize(*UI_CONFIG['window_size'])

        # Create main widget
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        # Set background color for main window
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {UI_CONFIG['dark_mode']['background']};
            }}
        """)

        # Main layout
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # Create control panel
        self.control_panel = ControlPanel()
        self.control_panel.file_selected.connect(self.open_file)
        self.control_panel.load_clicked.connect(self.load_data)
        self.control_panel.label_changed.connect(self.update_label)
        main_layout.addWidget(self.control_panel)

        # Create view layout
        view_container = QFrame()
        view_container.setFrameStyle(QFrame.Shape.NoFrame)
        view_container.setStyleSheet(f"""
            QFrame {{
                background-color: {UI_CONFIG['dark_mode']['frame_background']};
                border-radius: 8px;
            }}
        """)
        view_layout = QHBoxLayout(view_container)
        view_layout.setSpacing(10)
        view_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.addWidget(view_container)

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
            QMessageBox.critical(self, "Error", f"Failed to update views: {str(e)}")

if __name__ == '__main__':
    try:
        app = QApplication(sys.argv)
        
        # Set application icon
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), FILE_CONFIG['icon_path'])
        if os.path.exists(icon_path):
            app.setWindowIcon(QIcon(icon_path))
        
        # Apply dark theme
        app.setStyle('Fusion')
        app.setPalette(DarkPalette())
        
        window = MainWindow()
        window.show()
        sys.exit(app.exec())
    except Exception as e:
        QMessageBox.critical(None, "Error", f"Failed to start application: {str(e)}")