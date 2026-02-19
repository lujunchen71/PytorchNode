"""
DebugMixin - 调试功能Mixin

职责:
- 调试菜单操作
- 调试设置对话框
- 调试状态管理
"""

from PyQt6.QtCore import pyqtSlot as Slot
from PyQt6.QtWidgets import QDialog

import logging

logger = logging.getLogger(__name__)


class DebugMixin:
    """调试功能Mixin"""

    @Slot()
    def _on_debug_settings(self):
        """打开调试设置对话框"""
        from ui.dialogs.debug_settings_dialog import DebugSettingsDialog
        
        dialog = DebugSettingsDialog(self)
        result = dialog.exec()
        
        if result == QDialog.DialogCode.Accepted:
            self._update_debug_menu_states()

    def _update_debug_menu_states(self):
        """更新调试菜单项状态"""
        from core.debug import get_debug_manager, DebugCategory
        
        manager = get_debug_manager()
        self.node_debug_action.setChecked(manager.is_enabled(DebugCategory.NODE))
        self.pack_debug_action.setChecked(manager.is_enabled(DebugCategory.PACK))
        self.serial_debug_action.setChecked(manager.is_enabled(DebugCategory.SERIALIZATION))

    @Slot()
    def _on_toggle_node_debug(self):
        """切换节点调试"""
        from core.debug import get_debug_manager, DebugCategory
        
        manager = get_debug_manager()
        new_state = manager.toggle_category(DebugCategory.NODE)
        self.node_debug_action.setChecked(new_state)
        self.status_label.setText(f"节点调试: {'启用' if new_state else '禁用'}")

    @Slot()
    def _on_toggle_pack_debug(self):
        """切换打包调试"""
        from core.debug import get_debug_manager, DebugCategory
        
        manager = get_debug_manager()
        new_state = manager.toggle_category(DebugCategory.PACK)
        self.pack_debug_action.setChecked(new_state)
        self.status_label.setText(f"打包调试: {'启用' if new_state else '禁用'}")

    @Slot()
    def _on_toggle_serial_debug(self):
        """切换序列化调试"""
        from core.debug import get_debug_manager, DebugCategory
        
        manager = get_debug_manager()
        new_state = manager.toggle_category(DebugCategory.SERIALIZATION)
        self.serial_debug_action.setChecked(new_state)
        self.status_label.setText(f"序列化调试: {'启用' if new_state else '禁用'}")
