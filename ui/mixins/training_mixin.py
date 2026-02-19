"""
TrainingMixin - 训练操作Mixin

职责:
- 训练开始/暂停/停止
- 训练进度更新
- 可视化面板
"""

from PyQt6.QtCore import pyqtSlot as Slot

import logging

logger = logging.getLogger(__name__)


class TrainingMixin:
    """训练操作Mixin"""

    @Slot()
    def _on_train_start(self):
        """开始训练"""
        self._training_controller.start_training()
        self.train_start_action.setEnabled(False)
        self.train_pause_action.setEnabled(True)
        self.train_stop_action.setEnabled(True)

    @Slot()
    def _on_train_pause(self):
        """暂停/继续训练"""
        self._training_controller.toggle_pause()
        self.train_pause_action.setText(self._training_controller.get_pause_button_text())

    @Slot()
    def _on_train_stop(self):
        """停止训练"""
        self._training_controller.stop_training()
        self.train_start_action.setEnabled(True)
        self.train_pause_action.setEnabled(False)
        self.train_stop_action.setEnabled(False)
        self.train_pause_action.setText("暂停训练")

    @Slot()
    def _on_show_visualization(self):
        """显示可视化面板"""
        self._training_controller.show_visualization()

    @Slot(float, str)
    def _on_training_progress_updated(self, progress: float, status: str):
        """更新训练进度"""
        if progress >= 0:
            self.train_progress_label.setText(f"训练: {int(progress * 100)}% - {status}")
        else:
            self.train_progress_label.setText(f"训练: {status}")
