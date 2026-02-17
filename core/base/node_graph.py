"""
节点图管理器（NodeGraph）- 管理节点和连接的图结构

职责:
- 节点增删
- 拓扑排序
- 子图支持
- 节点查找
"""

from typing import Dict, List, Optional, Set
from collections import deque

from .node import Node
from .connection import Connection


class NodeGraph:
    """节点图管理器 - 管理节点集合和它们之间的连接"""

    def __init__(self, name: str = "root", parent: 'NodeGraph' = None):
        """
        初始化节点图

        Args:
            name: 图名称
            parent: 父图（用于子图）
        """
        self.name = name
        self.parent = parent

        # 节点存储 - 使用路径作为键
        self.nodes: Dict[str, Node] = {}

        # 连接存储
        self.connections: List[Connection] = []

        # 子图
        self.subgraphs: Dict[str, 'NodeGraph'] = {}

    @property
    def path(self) -> str:
        """
        获取图的完整路径

        Returns:
            图的路径
        """
        if self.parent is None:
            return ""
        parent_path = self.parent.path
        if parent_path:
            return f"{parent_path}/{self.name}"
        return f"/{self.name}"

    def add_node(self, node: Node) -> None:
        """
        添加节点

        Args:
            node: 要添加的节点

        Raises:
            ValueError: 如果节点名称已存在
        """
        if node.name in self.nodes:
            raise ValueError(f"Node with name '{node.name}' already exists")

        self.nodes[node.name] = node
        node.node_graph = self

    def remove_node(self, node: Node) -> None:
        """
        移除节点

        Args:
            node: 要移除的节点
        """
        # 先断开所有连接
        self._disconnect_node(node)

        # 从字典中移除
        if node.name in self.nodes:
            del self.nodes[node.name]
            node.node_graph = None

    def _disconnect_node(self, node: Node) -> None:
        """
        断开节点的所有连接

        Args:
            node: 要断开的节点
        """
        # 收集与此节点相关的所有连接
        connections_to_remove = []
        for conn in self.connections:
            if conn.source_node == node or conn.target_node == node:
                connections_to_remove.append(conn)

        # 断开连接
        for conn in connections_to_remove:
            self.remove_connection(conn)

    def get_node(self, path: str) -> Optional[Node]:
        """
        根据路径获取节点

        Args:
            path: 节点路径（可以是相对路径或完整路径）

        Returns:
            节点对象，如果不存在则返回 None
        """
        # 简单实现：只支持当前图中的节点名称
        # 复杂的路径解析可以在 PathManager 中实现
        if path.startswith('/'):
            # 绝对路径
            path = path[1:]  # 移除开头的 '/'
        
        # 检查是否包含子图路径
        if '/' in path:
            parts = path.split('/', 1)
            subgraph_name = parts[0]
            remaining_path = parts[1]
            
            if subgraph_name in self.subgraphs:
                return self.subgraphs[subgraph_name].get_node(remaining_path)
            return None
        
        # 当前图中的节点
        return self.nodes.get(path)

    def get_node_by_id(self, node_id: str) -> Optional[Node]:
        """
        根据ID获取节点

        Args:
            node_id: 节点ID

        Returns:
            节点对象，如果不存在则返回 None
        """
        for node in self.nodes.values():
            if node.id == node_id:
                return node
        
        # 在子图中查找
        for subgraph in self.subgraphs.values():
            node = subgraph.get_node_by_id(node_id)
            if node:
                return node
        
        return None

    def add_connection(self, connection: Connection) -> None:
        """
        添加连接

        Args:
            connection: 要添加的连接

        Raises:
            ValueError: 如果连接无效
        """
        # 验证连接的节点都在此图中
        if connection.source_node not in self.nodes.values():
            raise ValueError("Source node not in this graph")
        if connection.target_node not in self.nodes.values():
            raise ValueError("Target node not in this graph")

        if connection not in self.connections:
            self.connections.append(connection)

    def remove_connection(self, connection: Connection) -> None:
        """
        移除连接

        Args:
            connection: 要移除的连接
        """
        if connection in self.connections:
            connection.disconnect()
            self.connections.remove(connection)

    def create_connection(self, source_path: str, source_pin: str,
                         target_path: str, target_pin: str) -> Connection:
        """
        创建新连接

        Args:
            source_path: 源节点路径
            source_pin: 源引脚名称
            target_path: 目标节点路径
            target_pin: 目标引脚名称

        Returns:
            创建的连接对象

        Raises:
            ValueError: 如果节点或引脚不存在，或连接无效
        """
        # 查找节点
        source_node = self.get_node(source_path)
        target_node = self.get_node(target_path)

        if source_node is None:
            raise ValueError(f"Source node not found: {source_path}")
        if target_node is None:
            raise ValueError(f"Target node not found: {target_path}")

        # 查找引脚
        source_pin_obj = source_node.get_output_pin(source_pin)
        target_pin_obj = target_node.get_input_pin(target_pin)

        if source_pin_obj is None:
            raise ValueError(f"Source pin not found: {source_path}.{source_pin}")
        if target_pin_obj is None:
            raise ValueError(f"Target pin not found: {target_path}.{target_pin}")

        # 创建连接
        connection = Connection(source_pin_obj, target_pin_obj)
        self.add_connection(connection)

        return connection

    def get_all_nodes(self, include_subgraphs: bool = False) -> List[Node]:
        """
        获取所有节点

        Args:
            include_subgraphs: 是否包含子图中的节点

        Returns:
            节点列表
        """
        nodes = list(self.nodes.values())

        if include_subgraphs:
            for subgraph in self.subgraphs.values():
                nodes.extend(subgraph.get_all_nodes(include_subgraphs=True))

        return nodes

    def topological_sort(self) -> List[Node]:
        """
        对节点进行拓扑排序

        Returns:
            排序后的节点列表

        Raises:
            ValueError: 如果图中存在环
        """
        # 计算每个节点的入度
        in_degree = {node: 0 for node in self.nodes.values()}
        
        for conn in self.connections:
            if conn.target_node in in_degree:
                in_degree[conn.target_node] += 1

        # 找到所有入度为0的节点
        queue = deque([node for node, degree in in_degree.items() if degree == 0])
        sorted_nodes = []

        while queue:
            node = queue.popleft()
            sorted_nodes.append(node)

            # 减少后继节点的入度
            for pin in node.output_pins.values():
                for conn in pin.connections:
                    target = conn.target_node
                    if target in in_degree:
                        in_degree[target] -= 1
                        if in_degree[target] == 0:
                            queue.append(target)

        # 检查是否所有节点都被访问（检测环）
        if len(sorted_nodes) != len(self.nodes):
            raise ValueError("Graph contains a cycle")

        return sorted_nodes

    def find_dependencies(self, node: Node) -> Set[Node]:
        """
        查找节点的所有依赖

        Args:
            node: 目标节点

        Returns:
            依赖节点集合
        """
        dependencies = set()
        visited = set()

        def dfs(n: Node):
            if n in visited:
                return
            visited.add(n)

            # 遍历所有输入引脚
            for pin in n.input_pins.values():
                for conn in pin.connections:
                    source_node = conn.source_node
                    dependencies.add(source_node)
                    dfs(source_node)

        dfs(node)
        return dependencies

    def find_dependents(self, node: Node) -> Set[Node]:
        """
        查找依赖于指定节点的所有节点

        Args:
            node: 目标节点

        Returns:
            依赖节点集合
        """
        dependents = set()
        visited = set()

        def dfs(n: Node):
            if n in visited:
                return
            visited.add(n)

            # 遍历所有输出引脚
            for pin in n.output_pins.values():
                for conn in pin.connections:
                    target_node = conn.target_node
                    dependents.add(target_node)
                    dfs(target_node)

        dfs(node)
        return dependents

    def clear(self) -> None:
        """清空图中的所有节点和连接"""
        # 断开所有连接
        connections_copy = self.connections.copy()
        for conn in connections_copy:
            self.remove_connection(conn)

        # 移除所有节点
        nodes_copy = list(self.nodes.values())
        for node in nodes_copy:
            self.remove_node(node)

        # 清空子图
        self.subgraphs.clear()

    def validate(self) -> List[str]:
        """
        验证图的完整性

        Returns:
            错误信息列表
        """
        errors = []

        # 验证每个节点
        for node in self.nodes.values():
            node_errors = node.validate()
            if node_errors:
                errors.extend([f"[{node.name}] {err}" for err in node_errors])

        # 验证连接
        for conn in self.connections:
            if not conn.is_valid():
                errors.append(f"Invalid connection: {conn}")

        # 检查循环依赖
        try:
            self.topological_sort()
        except ValueError as e:
            errors.append(str(e))

        return errors

    def to_dict(self) -> dict:
        """
        序列化为字典

        Returns:
            图数据字典
        """
        return {
            "name": self.name,
            "nodes": [node.to_dict() for node in self.nodes.values()],
            "connections": [conn.to_dict() for conn in self.connections],
            "subgraphs": {
                name: subgraph.to_dict()
                for name, subgraph in self.subgraphs.items()
            }
        }

    def __repr__(self) -> str:
        """字符串表示"""
        return (
            f"NodeGraph('{self.name}', "
            f"nodes={len(self.nodes)}, "
            f"connections={len(self.connections)})"
        )
