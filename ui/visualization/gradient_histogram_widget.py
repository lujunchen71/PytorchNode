"""
梯度直方图可视化部件
"""

from typing import List, Optional, Dict
import numpy as np
import pyqtgraph as pg
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QPushButton, QComboBox, QCheckBox
from PyQt6.QtGui import QColor, QFont


class GradientHistogramWidget(QWidget):
    """梯度分布直方图可视化部件"""
    
    # 信号：显示设置改变
    display_changed = pyqtSignal(dict)
    
    def __init__(self, parent=None, title: str = "梯度直方图"):
        """
        初始化梯度直方图部件
        
        Args:
            parent: 父部件
            title: 图表标题
        """
        super().__init__(parent)
        
        self.grad_data: Dict[str, np.ndarray] = {}  # 层名称 -> 梯度值
        self.current_layer: str = ""
        self.bins: int = 50
        
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
        
        # 直方图箱数
        self.bins_label = QLabel("箱数:")
        header_layout.addWidget(self.bins_label)
        
        self.bins_combo = QComboBox()
        self.bins_combo.addItems(["20", "30", "50", "100", "200"])
        self.bins_combo.setCurrentText("50")
        self.bins_combo.setFixedWidth(80)
        self.bins_combo.currentTextChanged.connect(self._on_bins_changed)
        header_layout.addWidget(self.bins_combo)
        
        # 对数坐标复选框
        self.log_check = QCheckBox("对数Y轴")
        self.log_check.setChecked(False)
        self.log_check.toggled.connect(self._on_log_toggled)
        header_layout.addWidget(self.log_check)
        
        layout.addLayout(header_layout)
        
        # 绘图区域
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground('w')
        self.plot_widget.showGrid(x=True, y=True, alpha=0.3)
        self.plot_widget.setLabel('left', '频率')
        self.plot_widget.setLabel('bottom', '梯度值')
        
        layout.addWidget(self.plot_widget)
        
        # 控制栏
        control_layout = QHBoxLayout()
        
        # 清除按钮
        self.clear_btn = QPushButton("清除")
        self.clear_btn.setFixedSize(60, 24)
        self.clear_btn.clicked.connect(self.clear)
        control_layout.addWidget(self.clear_btn)
        
        control_layout.addStretch()
        
        # 统计信息
        self.stats_label = QLabel("数据点: -, 均值: -, 标准差: -, 范围: - ~ -")
        self.stats_label.setStyleSheet("color: gray; font-size: 12px;")
        control_layout.addWidget(self.stats_label)
        
        layout.addLayout(control_layout)
        
        self.setLayout(layout)
        
    def _init_plot(self):
        """初始化绘图"""
        # 创建直方图项
        self.histogram_item = pg.PlotCurveItem()
        self.plot_widget.addItem(self.histogram_item)
        
        # 创建垂直线表示均值
        self.mean_line = pg.InfiniteLine(angle=90, movable=False, pen=pg.mkPen('r', width=2))
        self.plot_widget.addItem(self.mean_line)
        
        # 创建零值线
        self.zero_line = pg.InfiniteLine(pos=0, angle=90, movable=False, pen=pg.mkPen('g', width=1, style=Qt.PenStyle.DashLine))
        self.plot_widget.addItem(self.zero_line)
        
    def add_gradients(self, layer_name: str, gradients: np.ndarray):
        """
        添加梯度数据
        
        Args:
            layer_name: 层名称
            gradients: 梯度值数组 (1D)
        """
        if gradients.ndim > 1:
            # 展平为1D
            gradients = gradients.flatten()
        
        self.grad_data[layer_name] = gradients
        
        # 更新层选择器
        if self.layer_combo.findText(layer_name) == -1:
            self.layer_combo.addItem(layer_name)
        
        # 如果当前没有选择层，设置为这个层
        if not self.current_layer:
            self.layer_combo.setCurrentText(layer_name)
            self.current_layer = layer_name
            self._update_histogram()
        
    def _update_histogram(self):
        """更新直方图显示"""
        if self.current_layer not in self.grad_data:
            return
            
        gradients = self.grad_data[self.current_layer]
        
        if len(gradients) == 0:
            return
            
        # 计算直方图
        self.bins = int(self.bins_combo.currentText())
        counts, bin_edges = np.histogram(gradients, bins=self.bins)
        
        # 计算bin中心
        bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
        
        # 更新曲线
        self.histogram_item.setData(bin_centers, counts, stepMode=True, fillLevel=0, brush=(0, 0, 255, 100))
        
        # 更新统计信息
        n_points = len(gradients)
        mean_val = np.mean(gradients)
        std_val = np.std(gradients)
        min_val = np.min(gradients)
        max_val = np.max(gradients)
        
        self.stats_label.setText(
            f"数据点: {n_points}, 均值: {mean_val:.6f}, "
            f"标准差: {std_val:.6f}, 范围: {min_val:.6f} ~ {max_val:.6f}"
        )
        
        # 更新均值线
        self.mean_line.setValue(mean_val)
        
        # 更新零值线（如果不在范围内）
        if min_val <= 0 <= max_val:
            self.zero_line.setVisible(True)
        else:
            self.zero_line.setVisible(False)
        
        # 自动调整范围
        self.plot_widget.autoRange()
        
        # 如果启用了对数Y轴
        if self.log_check.isChecked():
            self.plot_widget.setLogMode(y=True)
        else:
            self.plot_widget.setLogMode(y=False)
            
    def _on_layer_changed(self, layer_name: str):
        """层选择改变事件"""
        self.current_layer = layer_name
        self._update_histogram()
        
    def _on_bins_changed(self, bins_text: str):
        """箱数改变事件"""
        self.bins = int(bins_text)
        self._update_histogram()
        
    def _on_log_toggled(self, checked: bool):
        """对数坐标切换事件"""
        self.plot_widget.setLogMode(y=checked)
        
    def set_layer(self, layer_name: str):
        """设置当前显示的层"""
        if layer_name in self.grad_data:
            self.layer_combo.setCurrentText(layer_name)
            
    def set_bins(self, bins: int):
        """设置直方图箱数"""
        if bins in [20, 30, 50, 100, 200]:
            self.bins_combo.setCurrentText(str(bins))
            
    def set_log_scale(self, enabled: bool):
        """设置对数坐标"""
        self.log_check.setChecked(enabled)
        
    def clear(self):
        """清除所有数据"""
        self.grad_data.clear()
        self.current_layer = ""
        self.layer_combo.clear()
        self.histogram_item.clear()
        self.mean_line.setValue(0)
        self.stats_label.setText("数据点: -, 均值: -, 标准差: -, 范围: - ~ -")
        
    def get_current_statistics(self) -> Optional[dict]:
        """获取当前层的统计信息"""
        if self.current_layer in self.grad_data:
            gradients = self.grad_data[self.current_layer]
            return {
                "layer": self.current_layer,
                "count": len(gradients),
                "mean": float(np.mean(gradients)),
                "std": float(np.std(gradients)),
                "min": float(np.min(gradients)),
                "max": float(np.max(gradients)),
                "bins": self.bins
            }
        return None
        
    def get_all_layers(self) -> List[str]:
        """获取所有层名称"""
        return list(self.grad_data.keys())
        
    def export_histogram_data(self) -> Optional[tuple]:
        """导出当前直方图数据"""
        if self.current_layer in self.grad_data:
            gradients = self.grad_data[self.current_layer]
            counts, bin_edges = np.histogram(gradients, bins=self.bins)
            bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
            return bin_centers, counts, bin_edges
        return None