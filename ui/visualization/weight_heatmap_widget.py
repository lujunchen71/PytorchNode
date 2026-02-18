"""
权重热图可视化部件
"""

from typing import Optional, Tuple
import numpy as np
import pyqtgraph as pg
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QPushButton, QComboBox, QSlider
from PyQt6.QtGui import QColor, QFont


class WeightHeatmapWidget(QWidget):
    """权重矩阵热图可视化部件"""
    
    # 信号：颜色映射改变
    colormap_changed = pyqtSignal(str)
    
    def __init__(self, parent=None, title: str = "权重热图"):
        """
        初始化权重热图部件
        
        Args:
            parent: 父部件
            title: 图表标题
        """
        super().__init__(parent)
        
        self.data: Optional[np.ndarray] = None
        self.current_layer: str = ""
        
        # 创建UI
        self._setup_ui(title)
        
        # 初始化绘图
        self._init_plot()
        
    def _setup_ui(self, title: str):
        """设置UI布局"""
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        
        # 标题栏
        header_layout = QHBoxLayout()
        self.title_label = QLabel(title)
        self.title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        header_layout.addWidget(self.title_label)
        
        header_layout.addStretch()
        
        # 层选择器
        self.layer_label = QLabel("层:")
        header_layout.addWidget(self.layer_label)
        
        self.layer_combo = QComboBox()
        self.layer_combo.setFixedWidth(150)
        self.layer_combo.currentTextChanged.connect(self._on_layer_changed)
        header_layout.addWidget(self.layer_combo)
        
        # 颜色映射选择器
        self.cmap_label = QLabel("颜色:")
        header_layout.addWidget(self.cmap_label)
        
        self.cmap_combo = QComboBox()
        self.cmap_combo.addItems(["viridis", "plasma", "hot", "cool", "gray", "jet"])
        self.cmap_combo.setCurrentText("viridis")
        self.cmap_combo.setFixedWidth(100)
        self.cmap_combo.currentTextChanged.connect(self._on_cmap_changed)
        header_layout.addWidget(self.cmap_combo)
        
        layout.addLayout(header_layout)
        
        # 绘图区域
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground('w')
        self.plot_widget.setLabel('left', '行')
        self.plot_widget.setLabel('bottom', '列')
        
        layout.addWidget(self.plot_widget)
        
        # 控制栏
        control_layout = QHBoxLayout()
        
        # 缩放滑块
        self.scale_label = QLabel("缩放:")
        control_layout.addWidget(self.scale_label)
        
        self.scale_slider = QSlider(Qt.Orientation.Horizontal)
        self.scale_slider.setRange(1, 20)
        self.scale_slider.setValue(10)
        self.scale_slider.setFixedWidth(100)
        self.scale_slider.valueChanged.connect(self._on_scale_changed)
        control_layout.addWidget(self.scale_slider)
        
        control_layout.addStretch()
        
        # 统计信息
        self.stats_label = QLabel("尺寸: - x -, 范围: - ~ -")
        self.stats_label.setStyleSheet("color: gray; font-size: 12px;")
        control_layout.addWidget(self.stats_label)
        
        layout.addLayout(control_layout)
        
        self.setLayout(layout)
        
    def _init_plot(self):
        """初始化绘图"""
        # 创建图像项
        self.image_item = pg.ImageItem()
        self.plot_widget.addItem(self.image_item)
        
        # 创建颜色条
        self.color_bar = pg.ColorBarItem(
            values=(0, 1),
            colorMap=pg.colormap.get('viridis'),
            label='权重值'
        )
        self.color_bar.setImageItem(self.image_item, insert_in=self.plot_widget)
        
        # 设置视图范围
        self.plot_widget.setAspectLocked(False)
        
    def set_data(self, layer_name: str, weight_matrix: np.ndarray):
        """
        设置权重数据
        
        Args:
            layer_name: 层名称
            weight_matrix: 权重矩阵 (2D)
        """
        if weight_matrix.ndim != 2:
            # 尝试重塑
            if weight_matrix.ndim == 1:
                # 重塑为行向量
                weight_matrix = weight_matrix.reshape(1, -1)
            elif weight_matrix.ndim == 3:
                # 3D张量，取第一个通道
                weight_matrix = weight_matrix[0]
            elif weight_matrix.ndim == 4:
                # 卷积权重 [out_channels, in_channels, h, w]
                # 展平为2D
                out_c, in_c, h, w = weight_matrix.shape
                weight_matrix = weight_matrix.reshape(out_c * h, in_c * w)
            else:
                raise ValueError(f"不支持的权重维度: {weight_matrix.ndim}")
        
        self.data = weight_matrix
        self.current_layer = layer_name
        
        # 更新层选择器
        if self.layer_combo.findText(layer_name) == -1:
            self.layer_combo.addItem(layer_name)
        self.layer_combo.setCurrentText(layer_name)
        
        # 更新热图
        self._update_heatmap()
        
        # 更新统计信息
        rows, cols = weight_matrix.shape
        min_val = np.min(weight_matrix)
        max_val = np.max(weight_matrix)
        mean_val = np.mean(weight_matrix)
        std_val = np.std(weight_matrix)
        
        self.stats_label.setText(
            f"尺寸: {rows} x {cols}, 范围: {min_val:.4f} ~ {max_val:.4f}, "
            f"均值: {mean_val:.4f}, 标准差: {std_val:.4f}"
        )
        
    def _update_heatmap(self):
        """更新热图显示"""
        if self.data is None:
            return
            
        # 获取当前颜色映射
        cmap_name = self.cmap_combo.currentText()
        cmap = pg.colormap.get(cmap_name)
        
        # 设置图像数据
        self.image_item.setImage(self.data.T)  # 转置以匹配坐标
        
        # 更新颜色条
        self.color_bar.setColorMap(cmap)
        
        # 自动调整范围
        self.plot_widget.autoRange()
        
    def add_layer(self, layer_name: str, weight_matrix: np.ndarray):
        """
        添加一个新层的数据
        
        Args:
            layer_name: 层名称
            weight_matrix: 权重矩阵
        """
        self.set_data(layer_name, weight_matrix)
        
    def set_colormap(self, cmap_name: str):
        """设置颜色映射"""
        if cmap_name in ["viridis", "plasma", "hot", "cool", "gray", "jet"]:
            self.cmap_combo.setCurrentText(cmap_name)
            self._update_heatmap()
            
    def set_scale(self, scale: float):
        """设置显示缩放"""
        # 缩放范围 0.1-2.0
        scale = max(0.1, min(2.0, scale))
        slider_value = int(scale * 10)
        self.scale_slider.setValue(slider_value)
        
    def _on_layer_changed(self, layer_name: str):
        """层选择改变事件"""
        # 如果有多个层数据，可以切换显示
        # 目前只显示当前层
        pass
        
    def _on_cmap_changed(self, cmap_name: str):
        """颜色映射改变事件"""
        self._update_heatmap()
        self.colormap_changed.emit(cmap_name)
        
    def _on_scale_changed(self, value: int):
        """缩放滑块改变事件"""
        scale = value / 10.0
        # 调整图像显示比例
        if self.data is not None:
            rows, cols = self.data.shape
            self.plot_widget.setXRange(0, cols * scale)
            self.plot_widget.setYRange(0, rows * scale)
            
    def clear(self):
        """清除所有数据"""
        self.data = None
        self.current_layer = ""
        self.layer_combo.clear()
        self.image_item.clear()
        self.stats_label.setText("尺寸: - x -, 范围: - ~ -")
        
    def get_current_data(self) -> Optional[Tuple[str, np.ndarray]]:
        """获取当前显示的数据"""
        if self.data is not None:
            return self.current_layer, self.data
        return None
        
    def get_color_range(self) -> Tuple[float, float]:
        """获取颜色范围"""
        if self.data is not None:
            return float(np.min(self.data)), float(np.max(self.data))
        return 0.0, 1.0
        
    def get_layer_names(self) -> list:
        """获取所有层名称"""
        return [self.layer_combo.itemText(i) for i in range(self.layer_combo.count())]