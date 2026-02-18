"""
Command基类 - 命令模式实现

支持撤销/重做功能
"""

from abc import ABC, abstractmethod
from typing import Any


class Command(ABC):
    """命令抽象基类"""
    
    def __init__(self, description: str = ""):
        """
        初始化命令
        
        Args:
            description: 命令描述(用于UI显示)
        """
        self.description = description
        self._executed = False
    
    @abstractmethod
    def execute(self) -> bool:
        """
        执行命令
        
        Returns:
            执行是否成功
        """
        pass
    
    @abstractmethod
    def undo(self) -> bool:
        """
        撤销命令
        
        Returns:
            撤销是否成功
        """
        pass
    
    def redo(self) -> bool:
        """
        重做命令(默认调用execute)
        
        Returns:
            重做是否成功
        """
        return self.execute()
    
    @property
    def is_executed(self) -> bool:
        """命令是否已执行"""
        return self._executed
    
    def __repr__(self) -> str:
        """字符串表示"""
        return f"{self.__class__.__name__}('{self.description}')"
