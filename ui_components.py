import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.gridspec as gridspec
from matplotlib.widgets import Slider
from typing import Callable, Dict, Any
import numpy as np

from config import UI_CONFIG, DISPLAY_CONFIG, GRID_CONFIG

class ControlPanel:
    def __init__(self, parent: tk.Frame, on_file_select: Callable, on_load: Callable, on_label_change: Callable):
        self.frame = ttk.Frame(parent, width=UI_CONFIG['control_panel_width'])
        self.frame.pack(side=tk.LEFT, fill=tk.Y, padx=UI_CONFIG['padding'])
        
        # File selection
        self.file_button = ttk.Button(
            self.frame,
            text='选择文件',
            command=on_file_select,
            width=20
        )
        self.file_button.pack(pady=UI_CONFIG['padding'])
        
        # Load button
        self.load_button = ttk.Button(
            self.frame,
            text='加载数据',
            command=on_load,
            width=20
        )
        self.load_button.pack(pady=UI_CONFIG['padding'])
        
        # Label selection
        label_frame = ttk.LabelFrame(self.frame, text="标签选择")
        label_frame.pack(fill=tk.X, padx=UI_CONFIG['padding'], pady=UI_CONFIG['padding'])
        
        self.label_var = tk.StringVar()
        self.label_combo = ttk.Combobox(
            label_frame,
            textvariable=self.label_var,
            state='readonly',
            width=15
        )
        self.label_combo.pack(pady=UI_CONFIG['padding'])
        self.label_var.trace('w', lambda *args: on_label_change(self.label_var.get()))

    def update_file_button(self, filename: str):
        self.file_button.config(text=f"已选择: {filename}")

    def update_labels(self, labels: list):
        self.label_combo['values'] = labels
        if labels:
            self.label_combo.set(labels[0])

class ViewPanel:
    def __init__(self, parent: tk.Frame, on_slice_change: Callable):
        self.frame = ttk.Frame(parent)
        self.frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.fig = Figure(figsize=DISPLAY_CONFIG['figure_size'], dpi=DISPLAY_CONFIG['dpi'])
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        self.views: Dict[str, Any] = {}
        self.sliders: Dict[str, Slider] = {}
        self.slice_texts: Dict[str, Any] = {}
        
        self.on_slice_change = on_slice_change
        
        # Create initial empty layout
        self.create_empty_layout()

    def create_empty_layout(self):
        """Create initial empty layout with placeholder text."""
        self.fig.clear()
        gs = gridspec.GridSpec(3, 3, figure=self.fig,
                             height_ratios=GRID_CONFIG['height_ratios'],
                             width_ratios=GRID_CONFIG['width_ratios'])

        # Create placeholder views
        for i, view in enumerate(GRID_CONFIG['views']):
            # Main view
            ax = self.fig.add_subplot(gs[1, i])
            ax.text(0.5, 0.5, f'{view.title()}视图\n请加载数据',
                   ha='center', va='center', fontsize=12)
            ax.set_xticks([])
            ax.set_yticks([])
            self.views[view] = ax
            
            # Slider
            ax_slider = self.fig.add_subplot(gs[2, i])
            ax_slider.text(0.5, 0.5, '切片控制',
                         ha='center', va='center', fontsize=10)
            ax_slider.set_xticks([])
            ax_slider.set_yticks([])
            
            # Create empty slider
            slider = Slider(ax_slider, '', 0, 1, valinit=0, valstep=1,
                          color=DISPLAY_CONFIG['slider_color'])
            self.sliders[view] = slider
            slider.set_active(False)  # Disable slider until data is loaded
            
            # Slice text
            slice_text = ax_slider.text(
                0.5, DISPLAY_CONFIG['text_pad'],
                '切片 0',
                transform=ax_slider.transAxes,
                ha='center'
            )
            self.slice_texts[view] = slice_text

        self.canvas.draw()

    def create_views(self, shape: tuple):
        """Create views with actual data dimensions."""
        self.fig.clear()
        gs = gridspec.GridSpec(3, 3, figure=self.fig,
                             height_ratios=GRID_CONFIG['height_ratios'],
                             width_ratios=GRID_CONFIG['width_ratios'])

        # Create views
        for i, view in enumerate(GRID_CONFIG['views']):
            # Main view
            ax = self.fig.add_subplot(gs[1, i])
            ax.set_title(f'{view.title()}视图 [切片 0]')
            self.views[view] = ax
            
            # Slider
            ax_slider = self.fig.add_subplot(gs[2, i])
            slider = Slider(ax_slider, '', 0, shape[i] - 1,
                          valinit=0, valstep=1,
                          color=DISPLAY_CONFIG['slider_color'])
            ax_slider.set_title(f'{view.title()}切片', pad=DISPLAY_CONFIG['title_pad'])
            
            # Slice text
            slice_text = ax_slider.text(
                0.5, DISPLAY_CONFIG['text_pad'],
                f'切片 0',
                transform=ax_slider.transAxes,
                ha='center'
            )
            
            self.sliders[view] = slider
            self.slice_texts[view] = slice_text
            slider.on_changed(lambda val, v=view: self.on_slice_change(v, val))

        self.canvas.draw()

    def update_view(self, view: str, data: np.ndarray, mask: np.ndarray, slice_idx: int):
        ax = self.views[view]
        ax.clear()
        
        # Display data
        ax.imshow(data.T, cmap=DISPLAY_CONFIG['cmap'],
                 norm=plt.Normalize(*DISPLAY_CONFIG['normalize_range']),
                 origin=DISPLAY_CONFIG['origin'],
                 interpolation=DISPLAY_CONFIG['interpolation'])
        
        # Add contour
        ax.contour(mask.T, levels=[0.5],
                  colors=DISPLAY_CONFIG['contour_color'],
                  linewidths=DISPLAY_CONFIG['contour_width'])
        
        # Update title and remove ticks
        ax.set_title(f'{view.title()}视图 [切片 {slice_idx}]')
        ax.set_xticks([])
        ax.set_yticks([])
        
        # Update slice text
        self.slice_texts[view].set_text(f'切片 {slice_idx}')
        
        self.canvas.draw()

    def update_slider(self, view: str, value: int):
        self.sliders[view].set_val(value) 