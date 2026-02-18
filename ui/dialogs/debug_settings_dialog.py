"""
调试设置对话框 - 用于配置调试类别

功能：
- 显示所有调试类别
- 允许用户勾选启用/禁用
- 全局开关
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QCheckBox, QGroupBox, QScrollArea, QWidget
)
from PyQt6.QtCore import Qt
from typing import Dict

import logging

logger = logging.getLogger(__name__)


class DebugSettingsDialog(QDialog):
    """调试设置对话框"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("调试设置")
        self.setMinimumSize(400, 300)
        self._checkboxes: Dict[str, QCheckBox] = {}
        self._setup_ui()
        self._load_current_settings()
    
    def _setup_ui(self):
        """设置UI"""
        layout = QVBoxLayout(self)
        
        # 标题
        title_label = QLabel("选择要启用的调试类别")
        title_label.setStyleSheet("font-size: 14px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title_label)
        
        # 说明
        info_label = QLabel(
            "启用调试后，相关操作会记录到 debug_logs/ 目录下的文件中。\n"
            "这些日志可以帮助诊断问题，但在正式发布时建议关闭。"
        )
        info_label.setStyleSheet("color: #888; font-size: 11px; margin-bottom: 15px;")
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        # 调试类别组
        categories_group = QGroupBox("调试类别")
        categories_layout = QVBoxLayout(categories_group)
        
        # 调试类别描述
        category_descriptions = {
            "NODE": "节点操作 - 记录节点创建、删除、映射等操作",
            "CONNECTION": "连接操作 - 记录连接创建、删除等操作",
            "SERIALIZATION": "序列化 - 记录序列化/反序列化操作",
            "PACK": "打包操作 - 记录打包为子网络的详细过程",
            "UI": "UI操作 - 记录用户界面交互",
            "PATH": "路径导航 - 记录路径切换和导航操作"
        }
        
        from core.debug import DebugCategory
        
        for category in DebugCategory:
            checkbox = QCheckBox(category.name)
            description = category_descriptions.get(category.name, "")
            checkbox.setToolTip(description)
            checkbox.setStyleSheet("margin: 5px 0;")
            self._checkboxes[category.name] = checkbox
            categories_layout.addWidget(checkbox)
            
            # 添加描述标签
            desc_label = QLabel(f"  {description}")
            desc_label.setStyleSheet("color: #666; font-size: 10px; margin-left: 20px;")
            categories_layout.addWidget(desc_label)
        
        layout.addWidget(categories_group)
        
        # 全局按钮
        buttons_layout = QHBoxLayout()
        
        enable_all_btn = QPushButton("全部启用")
        enable_all_btn.clicked.connect(self._enable_all)
        buttons_layout.addWidget(enable_all_btn)
        
        disable_all_btn = QPushButton("全部禁用")
        disable_all_btn.clicked.connect(self._disable_all)
        buttons_layout.addWidget(disable_all_btn)
        
        layout.addLayout(buttons_layout)
        
        # 确定取消按钮
        dialog_buttons = QHBoxLayout()
        dialog_buttons.addStretch()
        
        ok_btn = QPushButton("确定")
        ok_btn.clicked.connect(self._on_ok)
        ok_btn.setDefault(True)
        dialog_buttons.addWidget(ok_btn)
        
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        dialog_buttons.addWidget(cancel_btn)
        
        layout.addLayout(dialog_buttons)
    
    def _load_current_settings(self):
        """加载当前设置"""
        from core.debug import get_debug_manager, DebugCategory
        
        manager = get_debug_manager()
        for category in DebugCategory:
            if category.name in self._checkboxes:
                is_enabled = manager.is_enabled(category)
                self._checkboxes[category.name].setChecked(is_enabled)
    
    def _enable_all(self):
        """启用所有类别"""
        for checkbox in self._checkboxes.values():
            checkbox.setChecked(True)
    
    def _disable_all(self):
        """禁用所有类别"""
        for checkbox in self._checkboxes.values():
            checkbox.setChecked(False)
    
    def _on_ok(self):
        """确定按钮点击"""
        from core.debug import get_debug_manager, DebugCategory
        
        manager = get_debug_manager()
        for category in DebugCategory:
            if category.name in self._checkboxes:
                is_checked = self._checkboxes[category.name].isChecked()
                manager.set_enabled(category, is_checked)
        
        logger.info(f"调试设置已更新: {manager.get_all_categories_status()}")
        self.accept()
