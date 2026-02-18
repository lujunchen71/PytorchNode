"""
PathManager 单元测试

测试路径解析、验证、查找等功能
"""

import pytest
from core.base.path_manager import PathManager
from core.base.node_graph import NodeGraph
from core.base.node import Node


class TestPathParsing:
    """测试路径解析功能"""
    
    def test_parse_path_with_pin(self):
        """测试解析带引脚的路径"""
        node_path, pin_name = PathManager.parse_path("/obj/conv1.output")
        assert node_path == "/obj/conv1"
        assert pin_name == "output"
    
    def test_parse_path_without_pin(self):
        """测试解析不带引脚的路径"""
        node_path, pin_name = PathManager.parse_path("/obj/conv1")
        assert node_path == "/obj/conv1"
        assert pin_name is None
    
    def test_parse_path_with_multiple_dots(self):
        """测试解析包含多个点的路径（只有最后一个点被视为引脚分隔符）"""
        node_path, pin_name = PathManager.parse_path("/obj/subnet.1/conv.2.output")
        assert node_path == "/obj/subnet.1/conv.2"
        assert pin_name == "output"


class TestPathNormalization:
    """测试路径规范化功能"""
    
    def test_normalize_path_add_leading_slash(self):
        """测试添加开头的斜杠"""
        assert PathManager.normalize_path("obj/conv1") == "/obj/conv1"
    
    def test_normalize_path_remove_duplicate_slashes(self):
        """测试移除重复的斜杠"""
        assert PathManager.normalize_path("//obj//conv1//") == "/obj/conv1"
    
    def test_normalize_path_remove_trailing_slash(self):
        """测试移除末尾的斜杠"""
        assert PathManager.normalize_path("/obj/conv1/") == "/obj/conv1"
    
    def test_normalize_path_root(self):
        """测试根路径"""
        assert PathManager.normalize_path("/") == "/"
        assert PathManager.normalize_path("//") == "/"
    
    def test_normalize_path_already_normalized(self):
        """测试已经规范化的路径"""
        assert PathManager.normalize_path("/obj/conv1") == "/obj/conv1"


class TestPathJoining:
    """测试路径连接功能"""
    
    def test_join_path_simple(self):
        """测试简单路径连接"""
        assert PathManager.join_path("/obj", "subnet1", "conv1") == "/obj/subnet1/conv1"
    
    def test_join_path_with_empty_parts(self):
        """测试包含空字符串的路径连接"""
        assert PathManager.join_path("/obj", "", "conv1") == "/obj/conv1"
    
    def test_join_path_no_parts(self):
        """测试没有路径部分的连接"""
        assert PathManager.join_path() == "/"
    
    def test_join_path_only_empty_parts(self):
        """测试只有空字符串的路径连接"""
        assert PathManager.join_path("", "", "") == "/"


class TestPathHierarchy:
    """测试路径层级功能"""
    
    def test_get_parent_path_nested(self):
        """测试获取嵌套路径的父路径"""
        assert PathManager.get_parent_path("/obj/subnet1/conv1") == "/obj/subnet1"
    
    def test_get_parent_path_top_level(self):
        """测试获取顶级路径的父路径"""
        assert PathManager.get_parent_path("/obj") == "/"
    
    def test_get_parent_path_root(self):
        """测试获取根路径的父路径"""
        assert PathManager.get_parent_path("/") is None
    
    def test_get_node_name(self):
        """测试从路径提取节点名称"""
        assert PathManager.get_node_name("/obj/subnet1/conv1") == "conv1"
        assert PathManager.get_node_name("/obj") == "obj"
        assert PathManager.get_node_name("/") == ""
    
    def test_is_descendant_true(self):
        """测试检查后代关系 - 正确的后代"""
        assert PathManager.is_descendant("/obj", "/obj/subnet1/conv1") is True
        assert PathManager.is_descendant("/obj/subnet1", "/obj/subnet1/conv1") is True
    
    def test_is_descendant_false_sibling(self):
        """测试检查后代关系 - 兄弟节点"""
        assert PathManager.is_descendant("/obj/subnet1", "/obj/subnet2/conv1") is False
    
    def test_is_descendant_false_same_path(self):
        """测试检查后代关系 - 相同路径"""
        assert PathManager.is_descendant("/obj/subnet1", "/obj/subnet1") is False
    
    def test_is_descendant_false_ancestor(self):
        """测试检查后代关系 - 祖先关系颠倒"""
        assert PathManager.is_descendant("/obj/subnet1/conv1", "/obj/subnet1") is False


class TestPathValidation:
    """测试路径验证功能"""
    
    def test_validate_path_valid(self):
        """测试验证有效路径"""
        assert PathManager.validate_path("/obj/conv1") is True
        assert PathManager.validate_path("/obj/subnet1/conv1") is True
        assert PathManager.validate_path("/") is True
    
    def test_validate_path_invalid_empty(self):
        """测试验证空路径"""
        assert PathManager.validate_path("") is False
    
    def test_validate_path_invalid_no_leading_slash(self):
        """测试验证无开头斜杠的路径"""
        assert PathManager.validate_path("obj/conv1") is False
    
    def test_validate_path_invalid_illegal_chars(self):
        """测试验证包含非法字符的路径"""
        assert PathManager.validate_path("/obj\\conv1") is False
        assert PathManager.validate_path("/obj?conv1") is False
        assert PathManager.validate_path("/obj*conv1") is False
        assert PathManager.validate_path("/obj|conv1") is False
        assert PathManager.validate_path("/obj<conv1") is False
        assert PathManager.validate_path("/obj>conv1") is False
        assert PathManager.validate_path('/obj"conv1') is False
        assert PathManager.validate_path("/obj:conv1") is False
    
    def test_validate_path_invalid_double_slash(self):
        """测试验证包含双斜杠的路径"""
        assert PathManager.validate_path("/obj//conv1") is False
    
    def test_is_absolute_path(self):
        """测试检查是否为绝对路径"""
        assert PathManager.is_absolute_path("/obj/conv1") is True
        assert PathManager.is_absolute_path("obj/conv1") is False
        assert PathManager.is_absolute_path("./obj/conv1") is False
        assert PathManager.is_absolute_path("../obj/conv1") is False


class TestRelativePathResolution:
    """测试相对路径解析功能"""
    
    def test_resolve_relative_path_parent(self):
        """测试解析父目录相对路径"""
        result = PathManager.resolve_relative_path("/obj/subnet1", "../conv1")
        assert result == "/obj/conv1"
    
    def test_resolve_relative_path_current(self):
        """测试解析当前目录相对路径"""
        result = PathManager.resolve_relative_path("/obj", "./subnet1/conv1")
        assert result == "/obj/subnet1/conv1"
    
    def test_resolve_relative_path_absolute(self):
        """测试解析绝对路径（应直接返回）"""
        result = PathManager.resolve_relative_path("/obj", "/train/dataset")
        assert result == "/train/dataset"
    
    def test_resolve_relative_path_multiple_parent(self):
        """测试解析多级父目录"""
        result = PathManager.resolve_relative_path("/obj/subnet1/subnet2", "../../conv1")
        assert result == "/obj/conv1"
    
    def test_resolve_relative_path_to_root(self):
        """测试解析到根目录"""
        result = PathManager.resolve_relative_path("/obj", "..")
        assert result == "/"
    
    def test_resolve_relative_path_beyond_root(self):
        """测试解析超出根目录（应停留在根目录）"""
        result = PathManager.resolve_relative_path("/obj", "../..")
        assert result == "/"


class SimpleNode(Node):
    """用于测试的简单节点"""
    
    def init_pins(self):
        """初始化引脚"""
        pass
    
    def execute(self):
        """执行节点逻辑"""
        pass


class TestNodeFinding:
    """测试节点查找功能"""
    
    def test_find_node_simple(self):
        """测试查找简单节点"""
        graph = NodeGraph("test_graph")
        
        # 创建节点（使用简单测试节点）
        node1 = SimpleNode(name="test_node1")
        graph.add_node(node1)
        
        # 通过路径查找节点
        found_node = PathManager.find_node(graph, "/test_node1")
        assert found_node is not None
        assert found_node.name == "test_node1"
    
    def test_find_node_not_found(self):
        """测试查找不存在的节点"""
        graph = NodeGraph("test_graph")
        
        # 查找不存在的节点
        found_node = PathManager.find_node(graph, "/nonexistent")
        assert found_node is None
    
    def test_find_node_normalized_path(self):
        """测试使用未规范化的路径查找节点"""
        graph = NodeGraph("test_graph")
        
        # 创建节点（使用简单测试节点）
        node1 = SimpleNode(name="test_node1")
        graph.add_node(node1)
        
        # 使用未规范化的路径查找节点
        found_node = PathManager.find_node(graph, "//test_node1//")
        assert found_node is not None
        assert found_node.name == "test_node1"


class TestEdgeCases:
    """测试边界情况"""
    
    def test_parse_path_only_dot(self):
        """测试解析只有点的路径"""
        node_path, pin_name = PathManager.parse_path("/obj/conv1.")
        assert node_path == "/obj/conv1"
        assert pin_name == ""
    
    def test_normalize_path_only_slashes(self):
        """测试规范化只有斜杠的路径"""
        assert PathManager.normalize_path("///") == "/"
    
    def test_join_path_with_leading_slashes(self):
        """测试连接带有开头斜杠的路径部分"""
        # join_path 会自动规范化，所以不会产生重复斜杠
        result = PathManager.join_path("/obj", "/subnet1", "/conv1")
        # 由于自动规范化，结果应该是干净的路径
        assert result == "/obj/subnet1/conv1"
    
    def test_get_parent_path_with_unnormalized_input(self):
        """测试使用未规范化路径获取父路径"""
        assert PathManager.get_parent_path("//obj//subnet1//") == "/obj"
    
    def test_resolve_relative_path_empty_relative(self):
        """测试解析空相对路径"""
        result = PathManager.resolve_relative_path("/obj/subnet1", "")
        assert result == "/obj/subnet1"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
