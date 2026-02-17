"""
路径管理器（PathManager）- 管理节点路径解析

职责:
- 路径解析
- 节点查找
- 路径验证
"""

from typing import Optional, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from .node import Node
    from .node_graph import NodeGraph


class PathManager:
    """路径管理器 - 处理节点路径的解析和查找"""

    @staticmethod
    def parse_path(path: str) -> Tuple[str, Optional[str]]:
        """
        解析路径为节点路径和引脚名称

        Args:
            path: 完整路径，格式为 "/node_path" 或 "/node_path.pin_name"

        Returns:
            (节点路径, 引脚名称) 元组，如果没有引脚则引脚名称为 None

        Examples:
            parse_path("/obj/conv1") -> ("/obj/conv1", None)
            parse_path("/obj/conv1.output") -> ("/obj/conv1", "output")
        """
        if '.' in path:
            # 分割节点路径和引脚名称
            parts = path.rsplit('.', 1)
            return parts[0], parts[1]
        else:
            return path, None

    @staticmethod
    def normalize_path(path: str) -> str:
        """
        规范化路径

        Args:
            path: 原始路径

        Returns:
            规范化后的路径

        Examples:
            normalize_path("obj/conv1") -> "/obj/conv1"
            normalize_path("//obj//conv1") -> "/obj/conv1"
        """
        # 确保以 / 开头
        if not path.startswith('/'):
            path = '/' + path

        # 移除重复的 /
        while '//' in path:
            path = path.replace('//', '/')

        # 移除末尾的 /
        if path.endswith('/') and path != '/':
            path = path[:-1]

        return path

    @staticmethod
    def join_path(*parts: str) -> str:
        """
        连接路径部分

        Args:
            *parts: 路径部分

        Returns:
            连接后的路径

        Examples:
            join_path("/obj", "subnet1", "conv1") -> "/obj/subnet1/conv1"
        """
        # 过滤空字符串
        parts = [p for p in parts if p]
        
        if not parts:
            return "/"

        # 连接路径
        path = '/'.join(parts)
        return PathManager.normalize_path(path)

    @staticmethod
    def get_parent_path(path: str) -> Optional[str]:
        """
        获取父路径

        Args:
            path: 节点路径

        Returns:
            父路径，如果是根则返回 None

        Examples:
            get_parent_path("/obj/subnet1/conv1") -> "/obj/subnet1"
            get_parent_path("/obj") -> "/"
            get_parent_path("/") -> None
        """
        path = PathManager.normalize_path(path)
        
        if path == '/':
            return None

        parts = path.rsplit('/', 1)
        if len(parts) == 1:
            return '/'
        
        parent = parts[0]
        return parent if parent else '/'

    @staticmethod
    def get_node_name(path: str) -> str:
        """
        从路径中提取节点名称

        Args:
            path: 节点路径

        Returns:
            节点名称

        Examples:
            get_node_name("/obj/subnet1/conv1") -> "conv1"
        """
        path = PathManager.normalize_path(path)
        
        if path == '/':
            return ''

        return path.rsplit('/', 1)[-1]

    @staticmethod
    def is_absolute_path(path: str) -> bool:
        """
        检查是否为绝对路径

        Args:
            path: 路径

        Returns:
            是否为绝对路径
        """
        return path.startswith('/')

    @staticmethod
    def is_descendant(ancestor_path: str, descendant_path: str) -> bool:
        """
        检查一个路径是否是另一个路径的后代

        Args:
            ancestor_path: 祖先路径
            descendant_path: 后代路径

        Returns:
            是否为后代关系

        Examples:
            is_descendant("/obj", "/obj/subnet1/conv1") -> True
            is_descendant("/obj/subnet1", "/obj/subnet2/conv1") -> False
        """
        ancestor = PathManager.normalize_path(ancestor_path)
        descendant = PathManager.normalize_path(descendant_path)

        if ancestor == descendant:
            return False

        return descendant.startswith(ancestor + '/')

    @staticmethod
    def validate_path(path: str) -> bool:
        """
        验证路径格式是否正确

        Args:
            path: 要验证的路径

        Returns:
            路径是否有效
        """
        if not path:
            return False

        # 路径必须以 / 开头（绝对路径）
        if not path.startswith('/'):
            return False

        # 不能包含非法字符
        illegal_chars = ['\\', '?', '*', '|', '<', '>', '"', ':']
        if any(char in path for char in illegal_chars):
            return False

        # 不能有空节点名（连续的 //）
        if '//' in path:
            return False

        return True

    @staticmethod
    def resolve_relative_path(base_path: str, relative_path: str) -> str:
        """
        解析相对路径

        Args:
            base_path: 基础路径
            relative_path: 相对路径

        Returns:
            绝对路径

        Examples:
            resolve_relative_path("/obj/subnet1", "../conv1") -> "/obj/conv1"
            resolve_relative_path("/obj", "./subnet1/conv1") -> "/obj/subnet1/conv1"
        """
        # 如果是绝对路径，直接返回
        if relative_path.startswith('/'):
            return PathManager.normalize_path(relative_path)

        base_path = PathManager.normalize_path(base_path)
        parts = base_path.split('/')[1:]  # 移除开头的空字符串

        # 处理相对路径
        for part in relative_path.split('/'):
            if part == '..':
                if parts:
                    parts.pop()
            elif part == '.' or part == '':
                continue
            else:
                parts.append(part)

        return '/' + '/'.join(parts) if parts else '/'

    @staticmethod
    def find_node(root_graph: 'NodeGraph', path: str) -> Optional['Node']:
        """
        在节点图中查找节点

        Args:
            root_graph: 根节点图
            path: 节点路径

        Returns:
            找到的节点，如果不存在则返回 None
        """
        path = PathManager.normalize_path(path)
        
        # 简单实现：委托给 NodeGraph.get_node
        return root_graph.get_node(path)
