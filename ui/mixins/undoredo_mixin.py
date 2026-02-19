"""
UndoRedoMixin - 撤销/重做操作Mixin

职责:
- 撤销操作
- 重做操作
- 菜单状态更新
"""

from PyQt6.QtCore import pyqtSlot as Slot

import logging

logger = logging.getLogger(__name__)


class UndoRedoMixin:
    """撤销/重做操作Mixin"""

    @Slot()
    def _on_undo(self):
        """撤销操作"""
        if self.undo_stack.can_undo():
            success = self.undo_stack.undo()
            if success:
                self.status_label.setText(f"↶ 撤销: {self.undo_stack.get_undo_text() or '上一操作'}")
                self._update_undo_redo_actions()

    @Slot()
    def _on_redo(self):
        """重做操作"""
        if self.undo_stack.can_redo():
            success = self.undo_stack.redo()
            if success:
                self.status_label.setText(f"↷ 重做: {self.undo_stack.get_redo_text() or '下一操作'}")
                self._update_undo_redo_actions()

    def _update_undo_redo_actions(self):
        """更新撤销/重做菜单项的启用状态"""
        if self.undo_stack.can_undo():
            self.undo_action.setEnabled(True)
            undo_text = self.undo_stack.get_undo_text()
            self.undo_action.setText(f"撤销 {undo_text}" if undo_text else "撤销(&U)")
        else:
            self.undo_action.setEnabled(False)
            self.undo_action.setText("撤销(&U)")
        
        if self.undo_stack.can_redo():
            self.redo_action.setEnabled(True)
            redo_text = self.undo_stack.get_redo_text()
            self.redo_action.setText(f"重做 {redo_text}" if redo_text else "重做(&R)")
        else:
            self.redo_action.setEnabled(False)
            self.redo_action.setText("重做(&R)")
