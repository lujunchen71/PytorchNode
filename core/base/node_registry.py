"""
节点注册表（NodeRegistry）- 管理所有可用的节点类型

职责:
- 节点类注册
- 节点类型查找
- 节点分类管理
"""

from typing import Dict, List, Type, Optional
from .node import Node, NodeCategory


class NodeRegistry:
    """节点注册表 - 单例模式管理所有节点类型"""

    _instance: Optional['NodeRegistry'] = None

    def __new__(cls):
        """确保单例"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """初始化注册表"""
        if self._initialized:
            return

        # 节点类型映射 {node_type: Node类}
        self._node_types: Dict[str, Type[Node]] = {}

        # 分类映射 {category: [node_types]}
        self._categories: Dict[str, List[str]] = {}

        self._initialized = True

    def register(self, node_class: Type[Node]) -> None:
        """
        注册节点类

        Args:
            node_class: 节点类

        Raises:
            ValueError: 如果节点类型已注册
        """
        node_type = node_class.node_type

        if node_type in self._node_types:
            raise ValueError(f"Node type '{node_type}' is already registered")

        # 注册节点类
        self._node_types[node_type] = node_class

        # 添加到分类
        category = node_class.node_category
        if category not in self._categories:
            self._categories[category] = []
        self._categories[category].append(node_type)

    def unregister(self, node_type: str) -> None:
        """
        取消注册节点类

        Args:
            node_type: 节点类型
        """
        if node_type in self._node_types:
            node_class = self._node_types[node_type]
            category = node_class.node_category

            # 从分类中移除
            if category in self._categories:
                self._categories[category].remove(node_type)
                if not self._categories[category]:
                    del self._categories[category]

            # 移除节点类
            del self._node_types[node_type]

    def get_node_class(self, node_type: str) -> Optional[Type[Node]]:
        """
        获取节点类

        Args:
            node_type: 节点类型

        Returns:
            节点类，如果不存在则返回 None
        """
        return self._node_types.get(node_type)

    def get_all_node_types(self) -> List[str]:
        """
        获取所有已注册的节点类型

        Returns:
            节点类型列表
        """
        return list(self._node_types.keys())

    def get_categories(self) -> List[str]:
        """
        获取所有分类

        Returns:
            分类列表
        """
        return list(self._categories.keys())

    def get_nodes_in_category(self, category: str) -> List[str]:
        """
        获取指定分类下的所有节点类型

        Args:
            category: 分类名称

        Returns:
            节点类型列表
        """
        return self._categories.get(category, []).copy()

    def search_nodes(self, query: str) -> List[str]:
        """
        搜索节点类型

        Args:
            query: 搜索关键词

        Returns:
            匹配的节点类型列表
        """
        query_lower = query.lower()
        results = []

        for node_type, node_class in self._node_types.items():
            # 搜索节点类型、显示名称
            if (query_lower in node_type.lower() or
                query_lower in node_class.display_name.lower()):
                results.append(node_type)

        return results

    def is_registered(self, node_type: str) -> bool:
        """
        检查节点类型是否已注册

        Args:
            node_type: 节点类型

        Returns:
            是否已注册
        """
        return node_type in self._node_types

    def clear(self) -> None:
        """清空所有注册的节点类型"""
        self._node_types.clear()
        self._categories.clear()

    def get_node_info(self, node_type: str) -> Optional[dict]:
        """
        获取节点信息

        Args:
            node_type: 节点类型

        Returns:
            节点信息字典
        """
        node_class = self.get_node_class(node_type)
        if node_class is None:
            return None

        return {
            "type": node_type,
            "display_name": node_class.display_name,
            "category": node_class.node_category,
            "class": node_class.__name__
        }

    def __repr__(self) -> str:
        """字符串表示"""
        return f"NodeRegistry(types={len(self._node_types)})"


# 全局注册表实例
_registry = NodeRegistry()


def register_node(node_class: Type[Node]) -> Type[Node]:
    """
    装饰器：注册节点类

    Args:
        node_class: 节点类

    Returns:
        原节点类（用于装饰器）

    Example:
        @register_node
        class MyNode(Node):
            node_type = "MyNode"
            ...
    """
    _registry.register(node_class)
    return node_class


def get_registry() -> NodeRegistry:
    """
    获取全局节点注册表

    Returns:
        节点注册表实例
    """
    return _registry
