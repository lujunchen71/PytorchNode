"""
TrainingController - 训练操作控制器

职责:
- 训练开始/暂停/停止
- 训练进度管理
- 训练状态管理
- 可视化面板管理
"""

from typing import Optional
from PyQt6.QtCore import QObject, pyqtSignal

import logging

logger = logging.getLogger(__name__)


class TrainingController(QObject):
    """训练操作控制器"""

    # 信号
    training_started = pyqtSignal()
    training_paused = pyqtSignal()
    training_resumed = pyqtSignal()
    training_stopped = pyqtSignal()
    progress_updated = pyqtSignal(float, str)  # 进度, 状态
    status_message = pyqtSignal(str)  # 状态消息

    def __init__(self, main_window):
        """
        初始化训练控制器
        
        Args:
            main_window: MainWindow 实例
        """
        super().__init__(main_window)
        self.main_window = main_window
        self._training_bridge = None
        self._visualization_panel = None
        self._is_training = False
        self._is_paused = False

    @property
    def training_bridge(self):
        """获取训练桥接器"""
        return self._training_bridge

    @property
    def is_training(self) -> bool:
        """是否正在训练"""
        return self._is_training

    @property
    def is_paused(self) -> bool:
        """是否暂停"""
        return self._is_paused

    def _ensure_training_bridge(self):
        """确保训练桥接器已初始化"""
        if self._training_bridge is None:
            from bridge.training_bridge import TrainingBridge
            self._training_bridge = TrainingBridge(self.main_window.node_graph, self.main_window)
            self._training_bridge.progress_updated.connect(self._on_progress_updated)

    def start_training(self) -> bool:
        """
        开始训练
        
        Returns:
            是否成功
        """
        try:
            logger.info("Starting training")
            self.status_message.emit("训练开始...")
            
            self._ensure_training_bridge()
            self._training_bridge.start_training()
            
            self._is_training = True
            self._is_paused = False
            
            self.training_started.emit()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to start training: {e}")
            self.status_message.emit(f"训练启动失败: {e}")
            return False

    def pause_training(self) -> bool:
        """
        暂停训练
        
        Returns:
            是否成功
        """
        if self._training_bridge is None:
            return False
        
        try:
            logger.info("Pausing training")
            self._training_bridge.pause_training()
            
            self._is_paused = True
            self.training_paused.emit()
            self.status_message.emit("训练暂停...")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to pause training: {e}")
            return False

    def resume_training(self) -> bool:
        """
        继续训练
        
        Returns:
            是否成功
        """
        if self._training_bridge is None:
            return False
        
        try:
            logger.info("Resuming training")
            self._training_bridge.resume_training()
            
            self._is_paused = False
            self.training_resumed.emit()
            self.status_message.emit("训练继续...")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to resume training: {e}")
            return False

    def stop_training(self) -> bool:
        """
        停止训练
        
        Returns:
            是否成功
        """
        if self._training_bridge is None:
            return False
        
        try:
            logger.info("Stopping training")
            self._training_bridge.stop_training()
            
            self._is_training = False
            self._is_paused = False
            self.training_stopped.emit()
            self.status_message.emit("训练已停止")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to stop training: {e}")
            return False

    def toggle_pause(self) -> bool:
        """
        切换暂停/继续状态
        
        Returns:
            切换后是否为暂停状态
        """
        if self._is_paused:
            self.resume_training()
            return False
        else:
            self.pause_training()
            return True

    def _on_progress_updated(self, progress: float, status: str):
        """
        处理训练进度更新
        
        Args:
            progress: 进度 (0.0 - 1.0)
            status: 状态文本
        """
        self.progress_updated.emit(progress, status)

    def show_visualization(self):
        """显示可视化面板"""
        logger.info("Showing visualization panel")
        
        # 延迟初始化可视化面板
        if self._visualization_panel is None:
            from ui.panels.visualization_panel import VisualizationPanel
            self._visualization_panel = VisualizationPanel(self.main_window)
        
        # 显示面板
        self._visualization_panel.show()
        self._visualization_panel.raise_()
        self._visualization_panel.activateWindow()

    def get_pause_button_text(self) -> str:
        """
        获取暂停按钮的文本
        
        Returns:
            按钮文本
        """
        return "继续训练" if self._is_paused else "暂停训练"
