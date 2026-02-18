"""
Node基类测试 (Phase 2 T011)
"""

import pytest
import sys
sys.path.insert(0, '.')

from core.base.node import Node
from core.base.pin import Pin
from core.base.pack import TorchPack


class ConcreteNode(Node):
    """用于测试的具体节点类"""
    
    display_name = "Concrete Node"
    node_type = "ConcreteNode"
    
    def init_pins(self):
        self.add_input_pin(Pin("input", "float", multiple=True))
        self.add_output_pin(Pin("output", "float"))
    
    def execute(self):
        # 简单传递输入
        input_pack = self.input_pins["input"].get_pack()
        if input_pack:
            self.output_pins["output"].set_pack(input_pack)
        return {}


def test_node_creation():
    """测试节点创建"""
    node = ConcreteNode(name="test_node")
    assert node.name == "test_node"
    assert node.display_name == "Concrete Node"
    assert node.node_type == "ConcreteNode"
    print("✅ 节点创建测试通过")


def test_node_pins():
    """测试节点针脚初始化"""
    node = ConcreteNode(name="test_node")
    node.init_pins()
    
    assert "input" in node.input_pins
    assert "output" in node.output_pins
    assert isinstance(node.input_pins["input"], Pin)
    assert isinstance(node.output_pins["output"], Pin)
    print("✅ 节点针脚测试通过")


def test_node_parameters():
    """测试节点参数管理"""
    node = ConcreteNode(name="test_node")
    # 添加实例参数
    node.add_instance_parameter("test_param", "float", 1.0, label="Test Param")
    assert "test_param" in node.instance_parameters
    param = node.instance_parameters["test_param"]
    assert param["type"] == "float"
    assert param["default"] == 1.0
    print("✅ 节点参数测试通过")


def test_node_execute():
    """测试节点执行（简单场景）"""
    node = ConcreteNode(name="test_node")
    node.init_pins()
    
    # 模拟输入数据
    input_pack = TorchPack(tensor=1.0)
    node.input_pins["input"].set_pack(input_pack)
    
    # 执行节点
    result = node.execute()
    assert isinstance(result, dict)
    # 输出针脚应有数据
    output_pack = node.output_pins["output"].get_pack()
    assert output_pack is not None
    print("✅ 节点执行测试通过")


if __name__ == "__main__":
    pytest.main([__file__, '-v', '-s'])