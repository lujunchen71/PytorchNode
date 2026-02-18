"""
Executor测试 (Phase 5 T066)
"""

import pytest
import sys
sys.path.insert(0, '.')

import torch
from core.base.node_graph import NodeGraph
from core.base.node import Node
from core.base.pin import InputPin, OutputPin
from core.base.pack import TorchPack
from core.engine.executor import Executor


class MockNode(Node):
    """模拟节点用于测试"""
    def __init__(self, name, output_value=None):
        super().__init__(name=name)
        self.output_value = output_value
        self.executed = False
    
    def init_pins(self):
        self.add_input_pin("in", data_type="any")
        self.add_output_pin("out", data_type="any")
    
    def execute(self, input_packs):
        self.executed = True
        if self.output_value is not None:
            return {"out": [self.output_value]}
        # 默认返回一个张量包
        return {"out": [TorchPack(torch.tensor([1.0]))]}


class AddNode(Node):
    """模拟加法节点：输入两个数，输出和"""
    def __init__(self, name):
        super().__init__(name=name)
        self.executed = False
    
    def init_pins(self):
        self.add_input_pin("a", data_type="any")
        self.add_input_pin("b", data_type="any")
        self.add_output_pin("sum", data_type="any")
    
    def execute(self, input_packs):
        self.executed = True
        a_packs = input_packs.get("a", [])
        b_packs = input_packs.get("b", [])
        if not a_packs or not b_packs:
            return {"sum": [TorchPack(torch.tensor(0.0))]}
        a_val = a_packs[0].tensor
        b_val = b_packs[0].tensor
        return {"sum": [TorchPack(a_val + b_val)]}


def test_executor_creation():
    """测试Executor实例化"""
    graph = NodeGraph()
    executor = Executor(graph)
    assert executor is not None
    assert executor.node_graph == graph


def test_topological_sort():
    """测试Executor的拓扑排序"""
    graph = NodeGraph()
    node_a = MockNode("A")
    node_b = MockNode("B")
    node_c = MockNode("C")
    graph.add_node(node_a)
    graph.add_node(node_b)
    graph.add_node(node_c)
    
    # 创建连接 A -> B -> C
    graph.create_connection("A", "out", "B", "in")
    graph.create_connection("B", "out", "C", "in")
    
    executor = Executor(graph)
    executor.prepare()
    
    # 检查执行顺序
    order = executor.execution_order
    assert len(order) == 3
    assert order[0].name == "A"
    assert order[1].name == "B"
    assert order[2].name == "C"


def test_execute_simple_graph():
    """测试简单图执行"""
    graph = NodeGraph()
    node_a = MockNode("A", output_value=TorchPack(torch.tensor([2.0])))
    node_b = MockNode("B")
    graph.add_node(node_a)
    graph.add_node(node_b)
    
    # 连接 A -> B
    graph.create_connection("A", "out", "B", "in")
    
    executor = Executor(graph)
    outputs = executor.execute()
    
    # 验证节点执行
    assert node_a.executed
    assert node_b.executed
    
    # 验证输出
    # 最终输出应为B的输出（因为没有下游连接）
    # 预期输出为默认值 [1.0]
    assert len(outputs) == 1
    key = list(outputs.keys())[0]
    assert key == "B.out"
    assert torch.allclose(outputs[key].tensor, torch.tensor([1.0]))


def test_execute_add_node():
    """测试加法节点执行"""
    graph = NodeGraph()
    node_a = MockNode("A", output_value=TorchPack(torch.tensor([3.0])))
    node_b = MockNode("B", output_value=TorchPack(torch.tensor([4.0])))
    add = AddNode("Add")
    
    graph.add_node(node_a)
    graph.add_node(node_b)
    graph.add_node(add)
    
    # 连接 A -> Add.a, B -> Add.b
    graph.create_connection("A", "out", "Add", "a")
    graph.create_connection("B", "out", "Add", "b")
    
    executor = Executor(graph)
    outputs = executor.execute()
    
    assert add.executed
    # 加法结果应为 3 + 4 = 7
    key = list(outputs.keys())[0]
    assert key == "Add.sum"
    assert torch.allclose(outputs[key].tensor, torch.tensor([7.0]))


def test_graph_with_cycle():
    """测试有环图引发异常"""
    graph = NodeGraph()
    node_a = MockNode("A")
    node_b = MockNode("B")
    graph.add_node(node_a)
    graph.add_node(node_b)
    
    # 创建循环 A -> B -> A
    graph.create_connection("A", "out", "B", "in")
    graph.create_connection("B", "out", "A", "in")
    
    executor = Executor(graph)
    with pytest.raises(ValueError, match="cycle"):
        executor.prepare()


if __name__ == "__main__":
    pytest.main([__file__, '-v', '-s'])