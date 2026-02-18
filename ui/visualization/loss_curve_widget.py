"""
损失曲线可视化部件
"""

from typing import List, Tuple, Optional
import numpy as np
import pyqtgraph as pg
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QPushButton
from PyQt6.QtGui import QColor


class LossCurveWidget(QWidget):
    """实时损失曲线可视化部件"""
    
    # 信号：清除曲线
    clear_requested = pyqtSignal()
    
    def __init__(self, parent=None, title: str = "损失曲线", max_points: int = 1000):
        """
        初始化损失曲线部件
        
        Args:
            parent: 父部件
            title: 图表标题
            max_points: 最大数据点数量（滚动窗口）
        """
        super().__init__(parent)
        
        self.max_points = max_points
        self.data: List[Tuple[int, float]] = []  # [(epoch, loss)]
        self.epochs: List[int] = []
        self.losses: List[float] = []
        
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
        
        # 控制按钮
        self.clear_btn = QPushButton("清除")
        self.clear_btn.setFixedSize(60, 24)
        self.clear_btn.clicked.connect(self._on_clear)
        header_layout.addWidget(self.clear_btn)
        
        layout.addLayout(header_layout)
        
        # 绘图区域
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground('w')
        self.plot_widget.showGrid(x=True, y=True, alpha=0.3)
        self.plot_widget.setLabel('left', '损失值')
        self.plot_widget.setLabel('bottom', '迭代')
        
        layout.addWidget(self.plot_widget)
        
        # 状态栏
        self.status_label = QLabel("等待数据...")
        self.status_label.setStyleSheet("color: gray; font-size: 12px;")
        layout.addWidget(self.status_label)
        
        self.setLayout(layout)
        
    def _init_plot(self):
        """初始化绘图"""
        # 创建曲线
        self.curve = self.plot_widget.plot(pen=pg.mkPen(color='r', width=2))
        self.scatter = pg.ScatterPlotItem(
            size=6, 
            pen=pg.mkPen(color='r'), 
            brush=pg.mkBrush(color='r')
        )
        self.plot_widget.addItem(self.scatter)
        
    def add_point(self, epoch: int, loss: float):
        """
        添加一个数据点
        
        Args:
            epoch: 迭代次数
            loss: 损失值
        """
        self.data.append((epoch, loss))
        self.epochs.append(epoch)
        self.losses.append(loss)
        
        # 限制数据点数量
        if len(self.data) > self.max_points:
            self.data = self.data[-self.max_points:]
            self.epochs = self.epochs[-self.max_points:]
            self.losses = self.losses[-self.max_points:]
        
        # 更新曲线
        self.curve.setData(self.epochs, self.losses)
        
        # 更新散点（只显示最后20个点）
        n_show = min(20, len(self.epochs))
        show_epochs = self.epochs[-n_show:]
        show_losses = self.losses[-n_show:]
        self.scatter.setData(show_epochs, show_losses)
        
        # 更新状态
        self.status_label.setText(f"Epoch {epoch}: loss = {loss:.6f}")
        
    def add_batch_points(self, epoch: int, batch_losses: List[float]):
        """
        添加一批数据点（每个batch的损失）
        
        Args:
            epoch: 当前epoch
            batch_losses: 每个batch的损失列表
        """
        if not batch_losses:
            return
            
        # 计算平均损失
        avg_loss = np.mean(batch_losses)
        self.add_point(epoch, avg_loss)
        
        # 可选：绘制每个batch的损失（浅色点）
        if len(batch_losses) <= 10:  # 如果batch数量不多，绘制所有点
            for i, loss in enumerate(batch_losses):
                batch_epoch = epoch + i / len(batch_losses)  # 在epoch内插值
                self._add_batch_point(batch_epoch, loss)
    
    def _add_batch_point(self, epoch: float, loss: float):
        """添加batch级别的点（浅色显示）"""
        batch_scatter = pg.ScatterPlotItem(
            size=4,
            pen=pg.mkPen(color=(255, 150, 150, 100)),
            brush=pg.mkBrush(color=(255, 150, 150, 100))
        )
        batch_scatter.setData([epoch], [loss])
        self.plot_widget.addItem(batch_scatter)
        # 自动清理（通过定时器移除）
        QTimer.singleShot(5000, lambda: self.plot_widget.removeItem(batch_scatter))
        
    def set_curve_color(self, color: QColor):
        """设置曲线颜色"""
        self.curve.setPen(pg.mkPen(color=color, width=2))
        self.scatter.setPen(pg.mkPen(color=color))
        self.scatter.setBrush(pg.mkBrush(color=color))
        
    def set_title(self, title: str):
        """设置标题"""
        self.title_label.setText(title)
        
    def clear(self):
        """清除所有数据"""
        self.data.clear()
        self.epochs.clear()
        self.losses.clear()
        self.curve.setData([], [])
        self.scatter.setData([], [])
        self.status_label.setText("等待数据...")
        
    def _on_clear(self):
        """清除按钮点击事件"""
        self.clear()
        self.clear_requested.emit()
        
    def get_latest_loss(self) -> Optional[float]:
        """获取最新的损失值"""
        if self.losses:
            return self.losses[-1]
        return None
        
    def get_min_loss(self) -> Optional[float]:
        """获取最小损失值"""
        if self.losses:
            return min(self.losses)
        return None
        
    def get_epoch_count(self) -> int:
        """获取数据点数量"""
        return len(self.data)