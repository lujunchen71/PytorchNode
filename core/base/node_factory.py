"""
节点工厂（NodeFactory）- 创建节点实例

职责:
- 节点创建
- 类型查找
- 默认参数设置
"""

from typing import Optional, TYPE_CHECKING
from .node import Node
from .node_registry import get_registry

if TYPE_CHECKING:
    from .node_graph import NodeGraph


class NodeFactory:
    """节点工厂 - 负责创建节点实例"""

    @staticmethod
    def create_node(
        node_type: str,
        name: str = None,
        node_graph: Optional['NodeGraph'] = None,
        **properties
    ) -> Node:
        """
        创建节点实例

        Args:
            node_type: 节点类型
            name: 节点名称（可选）
            node_graph: 所属节点图
            **properties: 节点属性

        Returns:
            创建的节点实例

        Raises:
            ValueError: 如果节点类型未注册
        """
        registry = get_registry()
        node_class = registry.get_node_class(node_type)

        if node_class is None:
            raise ValueError(f"Unknown node type: {node_type}")

        # 创建节点实例
        node = node_class(name=name, node_graph=node_graph)

        # 设置属性
        for key, value in properties.items():
            node.set_property(key, value)

        return node

    @staticmethod
    def create_node_with_defaults(
        node_type: str,
        node_graph: Optional['NodeGraph'] = None
    ) -> Node:
        """
        创建带默认配置的节点

        Args:
            node_type: 节点类型
            node_graph: 所属节点图

        Returns:
            创建的节点实例

        Raises:
            ValueError: 如果节点类型未注册
        """
        return NodeFactory.create_node(node_type, node_graph=node_graph)

    @staticmethod
    def is_valid_type(node_type: str) -> bool:
        """
        检查节点类型是否有效

        Args:
            node_type: 节点类型

        Returns:
            是否为有效的节点类型
        """
        registry = get_registry()
        return registry.is_registered(node_type)

    @staticmethod
    def get_available_types() -> list:
        """
        获取所有可用的节点类型

        Returns:
            节点类型列表
        """
        registry = get_registry()
        return registry.get_all_node_types()

    @staticmethod
    def get_node_info(node_type: str) -> Optional[dict]:
        """
        获取节点类型信息

        Args:
            node_type: 节点类型

        Returns:
            节点信息字典
        """
        registry = get_registry()
        return registry.get_node_info(node_type)
