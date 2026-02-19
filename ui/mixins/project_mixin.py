"""
ProjectMixin - 项目操作Mixin

职责:
- 项目新建/打开/保存
- 项目状态更新
"""

from PyQt6.QtCore import pyqtSlot as Slot
from PyQt6.QtWidgets import QMessageBox, QFileDialog

import logging

logger = logging.getLogger(__name__)


class ProjectMixin:
    """项目操作Mixin"""

    def _on_new_project(self):
        """新建项目"""
        logger.info("Creating new project")
        self._project_controller.new_project()
        self.status_label.setText("新建项目")

    def _on_open_project(self):
        """打开项目"""
        logger.info("Opening project")
        file_path, _ = QFileDialog.getOpenFileName(
            self, "打开项目", "", "PNNE 项目文件 (*.pnne);;所有文件 (*)"
        )

        if file_path:
            logger.info(f"Selected file: {file_path}")
            self._load_project(file_path)

    def _load_project(self, file_path: str):
        """加载项目"""
        if self._project_controller.load_from_file(file_path):
            self.current_project_path = file_path
            total_nodes, total_conns = self._project_controller._count_all_nodes()
            QMessageBox.information(
                self, "加载成功",
                f"项目已成功加载:\n{file_path}\n\n"
                f"总节点数: {total_nodes}\n总连接数: {total_conns}"
            )

    def _on_save_project(self):
        """保存项目"""
        if self.current_project_path:
            self._save_project(self.current_project_path)
        else:
            self._on_save_project_as()

    def _on_save_project_as(self):
        """另存为项目"""
        logger.info("Save project as")
        file_path, _ = QFileDialog.getSaveFileName(
            self, "另存为", "", "PNNE 项目文件 (*.pnne);;所有文件 (*)"
        )

        if file_path:
            logger.info(f"Save to: {file_path}")
            self._save_project(file_path)

    def _save_project(self, file_path: str):
        """保存项目"""
        if self._project_controller.save_to_file(file_path):
            self.current_project_path = file_path
            total_nodes, total_conns = self._project_controller._count_all_nodes()
            QMessageBox.information(
                self, "保存成功",
                f"项目已成功保存到:\n{file_path}\n\n"
                f"节点数: {total_nodes}\n连接数: {total_conns}"
            )

    @Slot(str)
    def _on_project_saved(self, file_path: str):
        """项目保存完成"""
        self.status_label.setText(f"✅ 项目已保存: {file_path}")
        self.project_saved.emit(file_path)

    @Slot(str)
    def _on_project_loaded(self, file_path: str):
        """项目加载完成"""
        self.status_label.setText(f"✅ 项目已加载: {file_path}")
        self.project_opened.emit(file_path)

    @Slot(str)
    def _on_load_error(self, error: str):
        """加载错误"""
        self.status_label.setText("❌ 加载失败")
        QMessageBox.warning(self, "加载失败", error)

    @Slot(str)
    def _on_save_error(self, error: str):
        """保存错误"""
        self.status_label.setText("❌ 保存失败")
        QMessageBox.warning(self, "保存失败", error)
