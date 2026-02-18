"""
UndoStack - 撤销/重做栈管理

管理命令历史,支持撤销/重做操作
"""

from typing import List, Optional
from .command import Command


class UndoStack:
    """撤销栈管理器"""
    
    def __init__(self, max_size: int = 100):
        """
        初始化撤销栈
        
        Args:
            max_size: 最大历史记录数
        """
        self._undo_stack: List[Command] = []
        self._redo_stack: List[Command] = []
        self._max_size = max_size
        self._current_index = -1
    
    def push(self, command: Command) -> bool:
        """
        执行并推入命令
        
        Args:
            command: 要执行的命令
            
        Returns:
            执行是否成功
        """
        # 执行命令
        if not command.execute():
            return False
        
        # 添加到撤销栈
        self._undo_stack.append(command)
        
        # 清空重做栈
        self._redo_stack.clear()
        
        # 限制栈大小
        if len(self._undo_stack) > self._max_size:
            self._undo_stack.pop(0)
        
        return True
    
    def undo(self) -> bool:
        """
        撤销上一个命令
        
        Returns:
            撤销是否成功
        """
        if not self.can_undo():
            return False
        
        # 弹出命令
        command = self._undo_stack.pop()
        
        # 执行撤销
        if command.undo():
            self._redo_stack.append(command)
            return True
        else:
            # 撤销失败,放回栈中
            self._undo_stack.append(command)
            return False
    
    def redo(self) -> bool:
        """
        重做上一个撤销的命令
        
        Returns:
            重做是否成功
        """
        if not self.can_redo():
            return False
        
        # 弹出命令
        command = self._redo_stack.pop()
        
        # 执行重做
        if command.redo():
            self._undo_stack.append(command)
            return True
        else:
            # 重做失败,放回栈中
            self._redo_stack.append(command)
            return False
    
    def can_undo(self) -> bool:
        """是否可以撤销"""
        return len(self._undo_stack) > 0
    
    def can_redo(self) -> bool:
        """是否可以重做"""
        return len(self._redo_stack) > 0
    
    def clear(self) -> None:
        """清空所有历史"""
        self._undo_stack.clear()
        self._redo_stack.clear()
    
    def get_undo_text(self) -> Optional[str]:
        """获取撤销命令描述"""
        if self.can_undo():
            return self._undo_stack[-1].description
        return None
    
    def get_redo_text(self) -> Optional[str]:
        """获取重做命令描述"""
        if self.can_redo():
            return self._redo_stack[-1].description
        return None
    
    @property
    def undo_count(self) -> int:
        """撤销栈大小"""
        return len(self._undo_stack)
    
    @property
    def redo_count(self) -> int:
        """重做栈大小"""
        return len(self._redo_stack)
