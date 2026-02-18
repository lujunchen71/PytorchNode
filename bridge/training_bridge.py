"""
训练桥接器 - 连接训练引擎和可视化UI
"""

from typing import Optional, Dict, Any, List
import numpy as np
import logging
from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot

from core.engine.training_pipeline import TrainingPipeline
from ui.visualization.visualization_panel import VisualizationPanel


class TrainingBridge(QObject):
    """训练桥接器 - 连接训练引擎和可视化UI"""
    
    # 信号：训练状态改变
    training_started = pyqtSignal()
    training_paused = pyqtSignal()
    training_stopped = pyqtSignal()
    training_finished = pyqtSignal()
    
    # 信号：训练进度更新（进度百分比，状态描述）
    progress_updated = pyqtSignal(float, str)  # progress (0-1), status
    
    # 信号：训练进度更新
    epoch_progress = pyqtSignal(int, int)  # current_epoch, total_epochs
    batch_progress = pyqtSignal(int, int)  # current_batch, total_batches
    
    # 信号：损失值更新
    loss_updated = pyqtSignal(float, int)  # loss, epoch
    
    # 信号：权重更新
    weights_updated = pyqtSignal(dict)  # {layer_name: weight_matrix}
    
    # 信号：梯度更新
    gradients_updated = pyqtSignal(dict)  # {layer_name: gradient_matrix}
    
    # 信号：激活值更新
    activations_updated = pyqtSignal(dict)  # {layer_name: activation_matrix}
    
    def __init__(self, node_graph=None, parent=None):
        """
        初始化训练桥接器
        
        Args:
            node_graph: 节点图（可选）
            parent: 父对象
        """
        super().__init__(parent)
        
        self.node_graph = node_graph
        self.training_pipeline: Optional[TrainingPipeline] = None
        self.visualization_panel: Optional[VisualizationPanel] = None
        
        self.is_monitoring = False
        self._paused = False
        self._running = False
        self.loss_history: List[float] = []
        self.epoch_history: List[int] = []
        
        # 连接内部信号
        self._connect_internal_signals()
        
    def _connect_internal_signals(self):
        """连接内部信号"""
        self.training_started.connect(self._on_training_started)
        self.training_stopped.connect(self._on_training_stopped)
        self.loss_updated.connect(self._on_loss_updated)
        self.weights_updated.connect(self._on_weights_updated)
        self.gradients_updated.connect(self._on_gradients_updated)
        self.activations_updated.connect(self._on_activations_updated)
        
    def set_training_pipeline(self, pipeline: TrainingPipeline):
        """
        设置训练管道
        
        Args:
            pipeline: 训练管道实例
        """
        self.training_pipeline = pipeline
        
        # 连接训练管道的信号
        # 注意：需要TrainingPipeline有相应的信号
        # 这里假设TrainingPipeline有这些信号
        try:
            pipeline.training_started.connect(self.training_started.emit)
            pipeline.training_stopped.connect(self.training_stopped.emit)
            pipeline.epoch_completed.connect(self._on_epoch_completed)
            pipeline.batch_completed.connect(self._on_batch_completed)
            pipeline.loss_computed.connect(self._on_loss_computed)
        except AttributeError:
            # 如果TrainingPipeline没有这些信号，使用轮询
            pass
            
    def set_visualization_panel(self, panel: VisualizationPanel):
        """
        设置可视化面板
        
        Args:
            panel: 可视化面板实例
        """
        self.visualization_panel = panel
        
    def start_monitoring(self):
        """开始监控训练过程"""
        self.is_monitoring = True
        self.loss_history.clear()
        self.epoch_history.clear()
        
    def stop_monitoring(self):
        """停止监控训练过程"""
        self.is_monitoring = False
        
    @pyqtSlot()
    def _on_training_started(self):
        """训练开始事件处理"""
        if self.visualization_panel:
            self.visualization_panel.clear_all()
            self.visualization_panel.status_label.setText("训练已开始")
            
    @pyqtSlot()
    def _on_training_stopped(self):
        """训练停止事件处理"""
        if self.visualization_panel:
            self.visualization_panel.status_label.setText("训练已停止")
            
    @pyqtSlot(float, int)
    def _on_loss_updated(self, loss: float, epoch: int):
        """损失更新事件处理"""
        if not self.is_monitoring or not self.visualization_panel:
            return
            
        self.loss_history.append(loss)
        self.epoch_history.append(epoch)
        
        # 更新可视化面板
        self.visualization_panel.add_loss_point(epoch, loss)
        
    @pyqtSlot(dict)
    def _on_weights_updated(self, weights: Dict[str, Any]):
        """权重更新事件处理"""
        if not self.is_monitoring or not self.visualization_panel:
            return
            
        for layer_name, weight_matrix in weights.items():
            if isinstance(weight_matrix, np.ndarray):
                self.visualization_panel.add_weight_data(layer_name, weight_matrix)
                
    @pyqtSlot(dict)
    def _on_gradients_updated(self, gradients: Dict[str, Any]):
        """梯度更新事件处理"""
        if not self.is_monitoring or not self.visualization_panel:
            return
            
        for layer_name, gradient_matrix in gradients.items():
            if isinstance(gradient_matrix, np.ndarray):
                self.visualization_panel.add_gradient_data(layer_name, gradient_matrix)
                
    @pyqtSlot(dict)
    def _on_activations_updated(self, activations: Dict[str, Any]):
        """激活值更新事件处理"""
        if not self.is_monitoring or not self.visualization_panel:
            return
            
        for layer_name, activation_matrix in activations.items():
            if isinstance(activation_matrix, np.ndarray):
                self.visualization_panel.add_activation_data(layer_name, activation_matrix)
                
    def _on_epoch_completed(self, epoch: int, total_epochs: int, loss: float):
        """epoch完成事件处理（从TrainingPipeline调用）"""
        self.epoch_progress.emit(epoch, total_epochs)
        self.loss_updated.emit(loss, epoch)
        
    def _on_batch_completed(self, batch: int, total_batches: int, batch_loss: float):
        """batch完成事件处理（从TrainingPipeline调用）"""
        self.batch_progress.emit(batch, total_batches)
        
    def _on_loss_computed(self, loss: float, epoch: int, batch: Optional[int] = None):
        """损失计算事件处理（从TrainingPipeline调用）"""
        self.loss_updated.emit(loss, epoch)
        
    def update_from_pipeline(self):
        """
        从训练管道更新数据（轮询模式）
        
        当TrainingPipeline没有信号时使用此方法
        """
        if not self.training_pipeline or not self.is_monitoring:
            return
            
        # 获取当前训练状态
        current_epoch = self.training_pipeline.current_epoch
        total_epochs = self.training_pipeline.total_epochs
        current_loss = self.training_pipeline.current_loss
        
        if current_loss is not None:
            self.loss_updated.emit(current_loss, current_epoch)
            
        # 获取权重和梯度数据
        # 这需要TrainingPipeline暴露模型访问方法
        # 暂时留空
        
    def export_training_data(self) -> Dict[str, Any]:
        """
        导出训练数据
        
        Returns:
            训练数据字典
        """
        return {
            "loss_history": self.loss_history.copy(),
            "epoch_history": self.epoch_history.copy(),
            "is_monitoring": self.is_monitoring
        }
        
    def clear_history(self):
        """清除历史数据"""
        self.loss_history.clear()
        self.epoch_history.clear()

    # ========== 训练控制方法 ==========
    
    def start_training(self):
        """开始训练"""
        if self._running:
            return
        self._running = True
        self._paused = False
        self.training_started.emit()
        self.progress_updated.emit(0.0, "训练开始")
        logger = logging.getLogger(__name__)
        logger.info("Training started via bridge")
        # TODO: 实际启动训练管道
    
    def pause_training(self):
        """暂停训练"""
        if not self._running or self._paused:
            return
        self._paused = True
        self.training_paused.emit()
        self.progress_updated.emit(-1.0, "训练暂停")
        logger = logging.getLogger(__name__)
        logger.info("Training paused")
    
    def resume_training(self):
        """继续训练"""
        if not self._running or not self._paused:
            return
        self._paused = False
        self.training_started.emit()  # 可能需要一个专门的 resumed 信号
        self.progress_updated.emit(-1.0, "训练继续")
        logger = logging.getLogger(__name__)
        logger.info("Training resumed")
    
    def stop_training(self):
        """停止训练"""
        if not self._running:
            return
        self._running = False
        self._paused = False
        self.training_stopped.emit()
        self.progress_updated.emit(1.0, "训练停止")
        logger = logging.getLogger(__name__)
        logger.info("Training stopped")
    
    def is_paused(self):
        """返回训练是否暂停"""
        return self._paused
    
    def is_running(self):
        """返回训练是否正在运行"""
        return self._running