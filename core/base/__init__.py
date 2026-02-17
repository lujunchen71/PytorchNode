"""
核心基础模块 - 导出所有基础类和枚举

包含:
- Node: 节点基类
- Pin: 引脚类
- Connection: 连接类
- NodeGraph: 节点图管理器
- NodeRegistry: 节点注册表
- NodeFactory: 节点工厂
- PathManager: 路径管理器
"""

from .node import Node, NodeCategory
from .pin import Pin, PinDirection, PinType
from .connection import Connection
from .node_graph import NodeGraph
from .node_registry import NodeRegistry, register_node, get_registry
from .node_factory import NodeFactory
from .path_manager import PathManager

__all__ = [
    # 核心类
    'Node',
    'Pin',
    'Connection',
    'NodeGraph',
    'NodeRegistry',
    'NodeFactory',
    'PathManager',
    
    # 枚举
    'NodeCategory',
    'PinDirection',
    'PinType',
    
    # 函数和装饰器
    'register_node',
    'get_registry',
]
