"""
可视化面板 (VisualizationPanel) - 训练监控与数据可视化面板

职责:
- 展示训练过程中的损失曲线、权重热图、梯度直方图、激活值图等
- 提供实时训练监控界面
- 支持多图表布局和自定义配置

参考: T079-T083, T083 (Phase 5)
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
    QLabel, QPushButton, QGroupBox, QGridLayout
)
from PyQt6.QtCore import Qt, pyqtSignal as Signal, pyqtSlot as Slot
import logging

logger = logging.getLogger(__name__)


class VisualizationPanel(QWidget):
    """可视化面板窗口（独立窗口）"""

    # 信号定义
    panel_closed = Signal()

    def __init__(self, parent=None):
        """初始化可视化面板"""
        super().__init__(parent)

        # 窗口设置
        self.setWindowTitle("训练监控 - PNNE")
        self.setGeometry(100, 100, 1000, 700)

        # 初始化UI
        self._init_ui()

        logger.info("VisualizationPanel initialized")

    def _init_ui(self):
        """初始化UI布局"""
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(8)

        # 顶部控制栏
        control_layout = QHBoxLayout()
        self.start_button = QPushButton("开始监控")
        self.start_button.clicked.connect(self._on_start_monitoring)
        control_layout.addWidget(self.start_button)

        self.pause_button = QPushButton("暂停")
        self.pause_button.setEnabled(False)
        self.pause_button.clicked.connect(self._on_pause_monitoring)
        control_layout.addWidget(self.pause_button)

        control_layout.addStretch()

        self.export_button = QPushButton("导出图表")
        self.export_button.clicked.connect(self._on_export_charts)
        control_layout.addWidget(self.export_button)

        main_layout.addLayout(control_layout)

        # 标签页容器
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabPosition(QTabWidget.TabPosition.North)

        # 标签页1: 损失曲线
        self.loss_tab = self._create_loss_tab()
        self.tab_widget.addTab(self.loss_tab, "损失曲线")

        # 标签页2: 权重热图
        self.weights_tab = self._create_weights_tab()
        self.tab_widget.addTab(self.weights_tab, "权重热图")

        # 标签页3: 梯度直方图
        self.gradients_tab = self._create_gradients_tab()
        self.tab_widget.addTab(self.gradients_tab, "梯度分布")

        # 标签页4: 激活值
        self.activations_tab = self._create_activations_tab()
        self.tab_widget.addTab(self.activations_tab, "激活值")

        main_layout.addWidget(self.tab_widget)

        # 底部状态栏
        status_layout = QHBoxLayout()
        self.status_label = QLabel("就绪")
        status_layout.addWidget(self.status_label)

        status_layout.addStretch()

        self.epoch_label = QLabel("轮次: -")
        status_layout.addWidget(self.epoch_label)

        self.loss_label = QLabel("损失: -")
        status_layout.addWidget(self.loss_label)

        main_layout.addLayout(status_layout)

        self.setLayout(main_layout)

    def _create_loss_tab(self):
        """创建损失曲线标签页"""
        tab = QWidget()
        layout = QVBoxLayout()

        # 图表占位符
        chart_placeholder = QLabel("<h3>损失曲线图表</h3>"
                                   "<p>训练过程中的损失变化将显示在此处</p>"
                                   "<p>实现组件: <code>LossCurveWidget</code> (T079)</p>")
        chart_placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        chart_placeholder.setStyleSheet("""
            QLabel {
                background-color: #222;
                color: #ccc;
                border: 2px dashed #555;
                border-radius: 8px;
                padding: 40px;
            }
        """)
        layout.addWidget(chart_placeholder)

        # 控制组
        control_group = QGroupBox("控制")
        control_layout = QHBoxLayout()
        self.smooth_checkbox = QLabel("平滑: 未实现")
        control_layout.addWidget(self.smooth_checkbox)
        control_layout.addStretch()
        self.refresh_button = QPushButton("手动刷新")
        self.refresh_button.clicked.connect(self._on_refresh_loss)
        control_layout.addWidget(self.refresh_button)
        control_group.setLayout(control_layout)
        layout.addWidget(control_group)

        tab.setLayout(layout)
        return tab

    def _create_weights_tab(self):
        """创建权重热图标签页"""
        tab = QWidget()
        layout = QVBoxLayout()

        placeholder = QLabel("<h3>权重热图</h3>"
                             "<p>网络层权重分布的热图可视化</p>"
                             "<p>实现组件: <code>WeightHeatmapWidget</code> (T080)</p>")
        placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        placeholder.setStyleSheet("""
            QLabel {
                background-color: #222;
                color: #ccc;
                border: 2px dashed #555;
                border-radius: 8px;
                padding: 40px;
            }
        """)
        layout.addWidget(placeholder)

        # 层选择
        layer_group = QGroupBox("选择层")
        layer_layout = QHBoxLayout()
        layer_layout.addWidget(QLabel("层: "))
        self.layer_combo = QLabel("未实现")
        layer_layout.addWidget(self.layer_combo)
        layer_layout.addStretch()
        layer_group.setLayout(layer_layout)
        layout.addWidget(layer_group)

        tab.setLayout(layout)
        return tab

    def _create_gradients_tab(self):
        """创建梯度直方图标签页"""
        tab = QWidget()
        layout = QVBoxLayout()

        placeholder = QLabel("<h3>梯度分布直方图</h3>"
                             "<p>梯度值的分布统计</p>"
                             "<p>实现组件: <code>GradientHistogramWidget</code> (T081)</p>")
        placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        placeholder.setStyleSheet("""
            QLabel {
                background-color: #222;
                color: #ccc;
                border: 2px dashed #555;
                border-radius: 8px;
                padding: 40px;
            }
        """)
        layout.addWidget(placeholder)

        tab.setLayout(layout)
        return tab

    def _create_activations_tab(self):
        """创建激活值标签页"""
        tab = QWidget()
        layout = QVBoxLayout()

        placeholder = QLabel("<h3>激活值可视化</h3>"
                             "<p>网络各层的激活值分布图</p>"
                             "<p>实现组件: <code>ActivationPlotWidget</code> (T082)</p>")
        placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        placeholder.setStyleSheet("""
            QLabel {
                background-color: #222;
                color: #ccc;
                border: 2px dashed #555;
                border-radius: 8px;
                padding: 40px;
            }
        """)
        layout.addWidget(placeholder)

        tab.setLayout(layout)
        return tab

    # ========== 槽函数 ==========

    @Slot()
    def _on_start_monitoring(self):
        """开始监控"""
        logger.info("Starting visualization monitoring")
        self.status_label.setText("监控中...")
        self.start_button.setEnabled(False)
        self.pause_button.setEnabled(True)

    @Slot()
    def _on_pause_monitoring(self):
        """暂停/继续监控"""
        logger.info("Pausing/resuming visualization monitoring")
        if self.pause_button.text() == "暂停":
            self.status_label.setText("已暂停")
            self.pause_button.setText("继续")
        else:
            self.status_label.setText("监控中...")
            self.pause_button.setText("暂停")

    @Slot()
    def _on_refresh_loss(self):
        """手动刷新损失曲线"""
        logger.info("Refreshing loss curve")
        self.status_label.setText("刷新损失曲线...")

    @Slot()
    def _on_export_charts(self):
        """导出图表"""
        logger.info("Exporting charts")
        self.status_label.setText("导出图表...")
        # 实现导出功能

    # ========== 公共接口 ==========

    def update_training_progress(self, epoch: int, total_epochs: int, loss: float):
        """更新训练进度"""
        self.epoch_label.setText(f"轮次: {epoch}/{total_epochs}")
        self.loss_label.setText(f"损失: {loss:.6f}")
        # TODO: 更新各个图表

    def update_loss_curve(self, epoch_losses):
        """更新损失曲线数据"""
        # TODO: 传递给LossCurveWidget
        pass

    def update_weight_heatmap(self, layer_name, weight_matrix):
        """更新权重热图"""
        # TODO: 传递给WeightHeatmapWidget
        pass

    def update_gradient_histogram(self, gradients):
        """更新梯度直方图"""
        # TODO: 传递给GradientHistogramWidget
        pass

    def update_activation_plot(self, activations):
        """更新激活值图"""
        # TODO: 传递给ActivationPlotWidget
        pass

    def closeEvent(self, event):
        """窗口关闭事件"""
        logger.info("Closing visualization panel")
        self.panel_closed.emit()
        super().closeEvent(event)


if __name__ == "__main__":
    # 测试代码
    from PyQt6.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)
    panel = VisualizationPanel()
    panel.show()
    sys.exit(app.exec())