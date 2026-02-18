"""
可视化面板 - 集成所有训练可视化部件
"""

from typing import Optional, Dict, Any
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, 
                             QPushButton, QLabel, QSplitter, QFrame, QGridLayout)
from PyQt6.QtGui import QFont, QColor

from .loss_curve_widget import LossCurveWidget
from .weight_heatmap_widget import WeightHeatmapWidget
from .gradient_histogram_widget import GradientHistogramWidget
from .activation_plot_widget import ActivationPlotWidget


class VisualizationPanel(QWidget):
    """可视化面板 - 集成所有训练可视化部件"""
    
    # 信号：面板关闭
    closed = pyqtSignal()
    
    def __init__(self, parent=None):
        """
        初始化可视化面板
        
        Args:
            parent: 父部件
        """
        super().__init__(parent)
        
        # 设置窗口属性
        self.setWindowTitle("训练可视化")
        self.setMinimumSize(800, 600)
        
        # 创建UI
        self._setup_ui()
        
        # 连接信号
        self._connect_signals()
        
        # 自动刷新定时器
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self._on_timer_refresh)
        self.refresh_interval = 1000  # 1秒
        
    def _setup_ui(self):
        """设置UI布局"""
        layout = QVBoxLayout()
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)
        
        # 标题栏
        header_layout = QHBoxLayout()
        
        self.title_label = QLabel("训练可视化")
        self.title_label.setStyleSheet("font-weight: bold; font-size: 16px;")
        header_layout.addWidget(self.title_label)
        
        header_layout.addStretch()
        
        # 控制按钮
        self.start_btn = QPushButton("开始监控")
        self.start_btn.setFixedSize(100, 28)
        self.start_btn.clicked.connect(self._on_start_monitoring)
        header_layout.addWidget(self.start_btn)
        
        self.stop_btn = QPushButton("停止监控")
        self.stop_btn.setFixedSize(100, 28)
        self.stop_btn.clicked.connect(self._on_stop_monitoring)
        self.stop_btn.setEnabled(False)
        header_layout.addWidget(self.stop_btn)
        
        self.refresh_btn = QPushButton("手动刷新")
        self.refresh_btn.setFixedSize(100, 28)
        self.refresh_btn.clicked.connect(self._on_manual_refresh)
        header_layout.addWidget(self.refresh_btn)
        
        self.close_btn = QPushButton("关闭")
        self.close_btn.setFixedSize(80, 28)
        self.close_btn.clicked.connect(self._on_close)
        header_layout.addWidget(self.close_btn)
        
        layout.addLayout(header_layout)
        
        # 分隔线
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(separator)
        
        # 主内容区域 - 选项卡
        self.tab_widget = QTabWidget()
        
        # 损失曲线标签页
        self.loss_tab = LossCurveWidget(title="训练损失曲线")
        self.tab_widget.addTab(self.loss_tab, "损失曲线")
        
        # 权重热图标签页
        self.heatmap_tab = WeightHeatmapWidget(title="权重热图")
        self.tab_widget.addTab(self.heatmap_tab, "权重热图")
        
        # 梯度直方图标签页
        self.gradient_tab = GradientHistogramWidget(title="梯度直方图")
        self.tab_widget.addTab(self.gradient_tab, "梯度直方图")
        
        # 激活值可视化标签页
        self.activation_tab = ActivationPlotWidget(title="激活值可视化")
        self.tab_widget.addTab(self.activation_tab, "激活值")
        
        # 网格布局标签页（可选）
        self.grid_tab = QWidget()
        self._setup_grid_tab()
        self.tab_widget.addTab(self.grid_tab, "综合视图")
        
        layout.addWidget(self.tab_widget)
        
        # 状态栏
        self.status_label = QLabel("就绪")
        self.status_label.setStyleSheet("color: gray; font-size: 12px;")
        layout.addWidget(self.status_label)
        
        self.setLayout(layout)
        
    def _setup_grid_tab(self):
        """设置网格布局标签页"""
        layout = QGridLayout()
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)
        
        # 第一行：损失曲线和权重热图
        self.grid_loss = LossCurveWidget(title="损失曲线 (网格)")
        self.grid_loss.setMinimumHeight(300)
        layout.addWidget(self.grid_loss, 0, 0)
        
        self.grid_heatmap = WeightHeatmapWidget(title="权重热图 (网格)")
        self.grid_heatmap.setMinimumHeight(300)
        layout.addWidget(self.grid_heatmap, 0, 1)
        
        # 第二行：梯度直方图和激活值
        self.grid_gradient = GradientHistogramWidget(title="梯度直方图 (网格)")
        self.grid_gradient.setMinimumHeight(300)
        layout.addWidget(self.grid_gradient, 1, 0)
        
        self.grid_activation = ActivationPlotWidget(title="激活值 (网格)")
        self.grid_activation.setMinimumHeight(300)
        layout.addWidget(self.grid_activation, 1, 1)
        
        self.grid_tab.setLayout(layout)
        
    def _connect_signals(self):
        """连接信号"""
        # 损失曲线清除信号
        self.loss_tab.clear_requested.connect(lambda: self.status_label.setText("损失曲线已清除"))
        
        # 权重热图颜色映射改变信号
        self.heatmap_tab.colormap_changed.connect(
            lambda cmap: self.status_label.setText(f"颜色映射改为: {cmap}")
        )
        
        # 梯度直方图显示设置改变信号
        self.gradient_tab.display_changed.connect(
            lambda settings: self.status_label.setText("梯度显示设置已更新")
        )
        
    def _on_start_monitoring(self):
        """开始监控按钮点击事件"""
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.refresh_timer.start(self.refresh_interval)
        self.status_label.setText("监控已启动")
        
    def _on_stop_monitoring(self):
        """停止监控按钮点击事件"""
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.refresh_timer.stop()
        self.status_label.setText("监控已停止")
        
    def _on_manual_refresh(self):
        """手动刷新按钮点击事件"""
        self._update_all_visualizations()
        self.status_label.setText("手动刷新完成")
        
    def _on_timer_refresh(self):
        """定时器刷新事件"""
        self._update_all_visualizations()
        
    def _update_all_visualizations(self):
        """更新所有可视化部件"""
        # 这里应该从训练引擎获取最新数据
        # 目前只是占位
        pass
        
    def _on_close(self):
        """关闭按钮点击事件"""
        self.refresh_timer.stop()
        self.closed.emit()
        self.hide()
        
    def add_loss_point(self, epoch: int, loss: float):
        """
        添加损失点
        
        Args:
            epoch: 迭代次数
            loss: 损失值
        """
        self.loss_tab.add_point(epoch, loss)
        self.grid_loss.add_point(epoch, loss)
        
    def add_weight_data(self, layer_name: str, weight_matrix: Any):
        """
        添加权重数据
        
        Args:
            layer_name: 层名称
            weight_matrix: 权重矩阵（numpy数组）
        """
        import numpy as np
        
        if isinstance(weight_matrix, np.ndarray):
            self.heatmap_tab.set_data(layer_name, weight_matrix)
            self.grid_heatmap.set_data(layer_name, weight_matrix)
        
    def add_gradient_data(self, layer_name: str, gradients: Any):
        """
        添加梯度数据
        
        Args:
            layer_name: 层名称
            gradients: 梯度值（numpy数组）
        """
        import numpy as np
        
        if isinstance(gradients, np.ndarray):
            self.gradient_tab.add_gradients(layer_name, gradients)
            self.grid_gradient.add_gradients(layer_name, gradients)
            
    def add_activation_data(self, layer_name: str, activations: Any):
        """
        添加激活值数据
        
        Args:
            layer_name: 层名称
            activations: 激活值（numpy数组）
        """
        import numpy as np
        
        if isinstance(activations, np.ndarray):
            self.activation_tab.add_activations(layer_name, activations)
            self.grid_activation.add_activations(layer_name, activations)
            
    def set_refresh_interval(self, interval_ms: int):
        """
        设置刷新间隔
        
        Args:
            interval_ms: 间隔毫秒数
        """
        self.refresh_interval = interval_ms
        if self.refresh_timer.isActive():
            self.refresh_timer.stop()
            self.refresh_timer.start(interval_ms)
            
    def get_current_tab_name(self) -> str:
        """获取当前标签页名称"""
        return self.tab_widget.tabText(self.tab_widget.currentIndex())
        
    def clear_all(self):
        """清除所有数据"""
        self.loss_tab.clear()
        self.heatmap_tab.clear()
        self.gradient_tab.clear()
        self.activation_tab.clear()
        self.grid_loss.clear()
        self.grid_heatmap.clear()
        self.grid_gradient.clear()
        self.grid_activation.clear()
        self.status_label.setText("所有数据已清除")
        
    def showEvent(self, event):
        """显示事件"""
        super().showEvent(event)
        self.status_label.setText("可视化面板已显示")
        
    def closeEvent(self, event):
        """关闭事件"""
        self.refresh_timer.stop()
        self.closed.emit()
        event.accept()