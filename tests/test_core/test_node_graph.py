"""
NodeGraph测试 (Phase 2 T014)
"""

import pytest
import sys
sys.path.insert(0, '.')

from core.base.node_graph import NodeGraph
from core.base.node import Node
from core.base.pin import Pin
from core.base.connection import Connection


class SimpleNode(Node):
    """简单测试节点"""
    
    display_name = "Simple Node"
    node_type = "SimpleNode"
    
    def init_pins(self):
        self.add_input_pin(Pin("input", "float"))
        self.add_output_pin(Pin("output", "float"))
    
    def execute(self):
        input_pack = self.input_pins["input"].get_pack()
        self.output_pins["output"].set_pack(input_pack)
        return {}


def test_node_graph_creation():
    """测试节点图创建"""
    graph = NodeGraph()
    assert graph.nodes == {}
    assert graph.connections == []
    print("✅ 节点图创建测试通过")


def test_add_node():
    """测试添加节点"""
    graph = NodeGraph()
    node = SimpleNode(name="node1")
    graph.add_node(node)
    assert "node1" in graph.nodes
    assert graph.nodes["node1"] is node
    print("✅ 添加节点测试通过")


def test_remove_node():
    """测试移除节点"""
    graph = NodeGraph()
    node = SimpleNode(name="node1")
    graph.add_node(node)
    graph.remove_node(node)
    assert "node1" not in graph.nodes
    print("✅ 移除节点测试通过")


def test_add_connection():
    """测试添加连接"""
    graph = NodeGraph()
    node1 = SimpleNode(name="node1")
    node2 = SimpleNode(name="node2")
    graph.add_node(node1)
    graph.add_node(node2)
    
    from_pin = node1.output_pins["output"]
    to_pin = node2.input_pins["input"]
    conn = Connection(from_pin, to_pin)
    graph.add_connection(conn)
    
    assert len(graph.connections) == 1
    assert graph.connections[0] is conn
    print("✅ 添加连接测试通过")


def test_find_path():
    """测试查找路径"""
    graph = NodeGraph()
    node1 = SimpleNode(name="node1")
    node2 = SimpleNode(name="node2")
    graph.add_node(node1)
    graph.add_node(node2)
    
    from_pin = node1.output_pins["output"]
    to_pin = node2.input_pins["input"]
    conn = Connection(from_pin, to_pin)
    graph.add_connection(conn)
    
    # 查找从node1到node2的路径
    path = graph.find_path(node1, node2)
    assert path is not None
    print("✅ 查找路径测试通过")


if __name__ == "__main__":
    pytest.main([__file__, '-v', '-s'])