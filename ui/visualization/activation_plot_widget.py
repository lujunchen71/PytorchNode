"""
激活值可视化部件
"""

from typing import List, Dict, Optional, Tuple
import numpy as np
import pyqtgraph as pg
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QPushButton, QComboBox, QCheckBox, QSpinBox
from PyQt6.QtGui import QColor, QFont


class ActivationPlotWidget(QWidget):
    """激活值可视化部件"""
    
    # 信号：显示设置改变
    display_changed = pyqtSignal(dict)
    
    def __init__(self, parent=None, title: str = "激活值可视化"):
        """
        初始化激活值可视化部件
        
        Args:
            parent: 父部件
            title: 图表标题
        """
        super().__init__(parent)
        
        self.activation_data: Dict[str, np.ndarray] = {}  # 层名称 -> 激活值
        self.current_layer: str = ""
        self.plot_type: str = "line"  # "line", "scatter", "histogram"
        self.max_samples: int = 1000  # 最大显示样本数
        
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
        
        # 绘图类型选择器
        self.plot_type_label = QLabel("类型:")
        header_layout.addWidget(self.plot_type_label)
        
        self.plot_type_combo = QComboBox()
        self.plot_type_combo.addItems(["折线图", "散点图", "直方图", "箱线图"])
        self.plot_type_combo.setCurrentText("折线图")
        self.plot_type_combo.setFixedWidth(100)
        self.plot_type_combo.currentTextChanged.connect(self._on_plot_type_changed)
        header_layout.addWidget(self.plot_type_combo)
        
        # 样本数限制
        self.samples_label = QLabel("样本:")
        header_layout.addWidget(self.samples_label)
        
        self.samples_spin = QSpinBox()
        self.samples_spin.setRange(100, 10000)
        self.samples_spin.setValue(1000)
        self.samples_spin.setFixedWidth(80)
        self.samples_spin.valueChanged.connect(self._on_samples_changed)
        header_layout.addWidget(self.samples_spin)
        
        layout.addLayout(header_layout)
        
        # 绘图区域
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground('w')
        self.plot_widget.showGrid(x=True, y=True, alpha=0.3)
        self.plot_widget.setLabel('left', '激活值')
        self.plot_widget.setLabel('bottom', '神经元索引')
        
        layout.addWidget(self.plot_widget)
        
        # 控制栏
        control_layout = QHBoxLayout()
        
        # 清除按钮
        self.clear_btn = QPushButton("清除")
        self.clear_btn.setFixedSize(60, 24)
        self.clear_btn.clicked.connect(self.clear)
        control_layout.addWidget(self.clear_btn)
        
        # 刷新按钮
        self.refresh_btn = QPushButton("刷新")
        self.refresh_btn.setFixedSize(60, 24)
        self.refresh_btn.clicked.connect(self._on_refresh)
        control_layout.addWidget(self.refresh_btn)
        
        control_layout.addStretch()
        
        # 统计信息
        self.stats_label = QLabel("神经元: -, 均值: -, 标准差: -, 范围: - ~ -")
        self.stats_label.setStyleSheet("color: gray; font-size: 12px;")
        control_layout.addWidget(self.stats_label)
        
        layout.addLayout(control_layout)
        
        self.setLayout(layout)
        
    def _init_plot(self):
        """初始化绘图"""
        # 创建绘图项
        self.plot_item = pg.PlotCurveItem()
        self.plot_widget.addItem(self.plot_item)
        
        # 创建散点项
        self.scatter_item = pg.ScatterPlotItem(size=5, pen=pg.mkPen('r'), brush=pg.mkBrush('r'))
        self.plot_widget.addItem(self.scatter_item)
        
        # 创建直方图项
        self.histogram_item = pg.PlotCurveItem()
        
        # 创建箱线图项（稍后实现）
        
        # 初始化所有项为隐藏
        self.scatter_item.hide()
        self.histogram_item.hide()
        
    def add_activations(self, layer_name: str, activations: np.ndarray):
        """
        添加激活值数据
        
        Args:
            layer_name: 层名称
            activations: 激活值数组 (1D或2D)
        """
        if activations.ndim > 2:
            # 如果是3D或更高维，展平
            activations = activations.flatten()
        elif activations.ndim == 2:
            # 如果是2D，取第一个样本或展平
            activations = activations.flatten()
        
        # 限制样本数量
        if len(activations) > self.max_samples:
            # 随机采样
            indices = np.random.choice(len(activations), self.max_samples, replace=False)
            activations = activations[indices]
        
        self.activation_data[layer_name] = activations
        
        # 更新层选择器
        if self.layer_combo.findText(layer_name) == -1:
            self.layer_combo.addItem(layer_name)
        
        # 如果当前没有选择层，设置为这个层
        if not self.current_layer:
            self.layer_combo.setCurrentText(layer_name)
            self.current_layer = layer_name
            self._update_plot()
        
    def _update_plot(self):
        """更新绘图显示"""
        if self.current_layer not in self.activation_data:
            return
            
        activations = self.activation_data[self.current_layer]
        
        if len(activations) == 0:
            return
            
        # 隐藏所有项
        self.plot_item.hide()
        self.scatter_item.hide()
        self.histogram_item.hide()
        
        plot_type = self.plot_type_combo.currentText()
        
        if plot_type == "折线图":
            # 显示折线图
            indices = np.arange(len(activations))
            self.plot_item.setData(indices, activations, pen=pg.mkPen('b', width=1))
            self.plot_item.show()
            
        elif plot_type == "散点图":
            # 显示散点图
            indices = np.arange(len(activations))
            self.scatter_item.setData(indices, activations)
            self.scatter_item.show()
            
        elif plot_type == "直方图":
            # 显示直方图
            bins = 50
            counts, bin_edges = np.histogram(activations, bins=bins)
            bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
            
            self.histogram_item.setData(bin_centers, counts, stepMode=True, fillLevel=0, brush=(0, 0, 255, 100))
            self.histogram_item.show()
            self.plot_widget.setLabel('bottom', '激活值')
            self.plot_widget.setLabel('left', '频率')
        else:  # 箱线图
            # 简单箱线图实现
            # 使用误差线表示
            q1 = np.percentile(activations, 25)
            q3 = np.percentile(activations, 75)
            median = np.median(activations)
            iqr = q3 - q1
            lower = q1 - 1.5 * iqr
            upper = q3 + 1.5 * iqr
            
            # 绘制箱线图
            self.plot_widget.clear()
            # 创建箱线图项
            box_item = pg.BarGraphItem(x=[0], height=[iqr], width=0.5, brush='y')
            self.plot_widget.addItem(box_item)
            # 中位线
            median_line = pg.InfiniteLine(pos=median, angle=0, movable=False, pen=pg.mkPen('r', width=2))
            self.plot_widget.addItem(median_line)
            # 须线
            whisker_item = pg.ErrorBarItem(x=np.array([0]), y=np.array([(lower + upper) / 2]), 
                                          height=np.array([upper - lower]), beam=0.2)
            self.plot_widget.addItem(whisker_item)
            # 离群点
            outliers = activations[(activations < lower) | (activations > upper)]
            if len(outliers) > 0:
                outlier_item = pg.ScatterPlotItem(x=np.zeros(len(outliers)), y=outliers, 
                                                 size=5, pen=pg.mkPen('r'), brush=pg.mkBrush('r'))
                self.plot_widget.addItem(outlier_item)
            
            self.plot_widget.setLabel('bottom', '')
            self.plot_widget.setLabel('left', '激活值')
            return
        
        # 更新统计信息
        n_neurons = len(activations)
        mean_val = np.mean(activations)
        std_val = np.std(activations)
        min_val = np.min(activations)
        max_val = np.max(activations)
        
        self.stats_label.setText(
            f"神经元: {n_neurons}, 均值: {mean_val:.6f}, "
            f"标准差: {std_val:.6f}, 范围: {min_val:.6f} ~ {max_val:.6f}"
        )
        
        # 自动调整范围
        self.plot_widget.autoRange()
        
    def _on_layer_changed(self, layer_name: str):
        """层选择改变事件"""
        self.current_layer = layer_name
        self._update_plot()
        
    def _on_plot_type_changed(self, plot_type: str):
        """绘图类型改变事件"""
        self.plot_type = plot_type
        self._update_plot()
        
    def _on_samples_changed(self, value: int):
        """样本数改变事件"""
        self.max_samples = value
        
    def _on_refresh(self):
        """刷新按钮点击事件"""
        self._update_plot()
        
    def set_layer(self, layer_name: str):
        """设置当前显示的层"""
        if layer_name in self.activation_data:
            self.layer_combo.setCurrentText(layer_name)
            
    def set_plot_type(self, plot_type: str):
        """设置绘图类型"""
        if plot_type in ["折线图", "散点图", "直方图", "箱线图"]:
            self.plot_type_combo.setCurrentText(plot_type)
            
    def set_max_samples(self, max_samples: int):
        """设置最大样本数"""
        self.max_samples = max_samples
        self.samples_spin.setValue(max_samples)
        
    def clear(self):
        """清除所有数据"""
        self.activation_data.clear()
        self.current_layer = ""
        self.layer_combo.clear()
        self.plot_widget.clear()
        self._init_plot()
        self.stats_label.setText("神经元: -, 均值: -, 标准差: -, 范围: - ~ -")
        
    def get_current_statistics(self) -> Optional[dict]:
        """获取当前层的统计信息"""
        if self.current_layer in self.activation_data:
            activations = self.activation_data[self.current_layer]
            return {
                "layer": self.current_layer,
                "count": len(activations),
                "mean": float(np.mean(activations)),
                "std": float(np.std(activations)),
                "min": float(np.min(activations)),
                "max": float(np.max(activations)),
                "plot_type": self.plot_type_combo.currentText()
            }
        return None
        
    def get_all_layers(self) -> List[str]:
        """获取所有层名称"""
        return list(self.activation_data.keys())
        
    def export_data(self) -> Optional[Tuple[np.ndarray, np.ndarray]]:
        """导出当前层数据"""
        if self.current_layer in self.activation_data:
            activations = self.activation_data[self.current_layer]
            indices = np.arange(len(activations))
            return indices, activations
        return None