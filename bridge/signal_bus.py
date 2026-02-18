"""
SignalBus - 全局信号总线

用于UI和Core层之间的解耦通信,实现发布-订阅模式
"""

from typing import Callable, Dict, List, Any
from PyQt6.QtCore import QObject, pyqtSignal


class SignalBus(QObject):
    """全局信号总线 - 单例模式"""
    
    _instance = None
    
    # 节点相关信号
    node_added = pyqtSignal(object)  # (node)
    node_removed = pyqtSignal(str)  # (node_id)
    node_selected = pyqtSignal(object)  # (node)
    node_property_changed = pyqtSignal(str, str, object)  # (node_id, prop_name, value)
    
    # 连接相关信号
    connection_created = pyqtSignal(object)  # (connection)
    connection_removed = pyqtSignal(str)  # (connection_id)
    
    # 图相关信号
    graph_loaded = pyqtSignal()
    graph_saved = pyqtSignal(str)  # (file_path)
    graph_cleared = pyqtSignal()
    
    # 训练相关信号
    training_started = pyqtSignal()
    training_paused = pyqtSignal()
    training_stopped = pyqtSignal()
    training_step_completed = pyqtSignal(int, float, dict)  # (step, loss, metrics)
    
    # 执行相关信号
    execution_started = pyqtSignal()
    execution_completed = pyqtSignal()
    execution_error = pyqtSignal(str)  # (error_message)
    
    def __new__(cls):
        """单例实现"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            super(SignalBus, cls._instance).__init__()
        return cls._instance
    
    @classmethod
    def get_instance(cls) -> 'SignalBus':
        """获取单例实例"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def reset(self) -> None:
        """重置信号总线(主要用于测试)"""
        # 断开所有连接
        self.disconnect()


# 全局信号总线实例
signal_bus = SignalBus.get_instance()
