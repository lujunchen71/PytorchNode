"""
测试Linear节点
T035 [P] [US1] 编写Linear节点测试
"""

import pytest
import torch
from core.nodes.nn.linear_node import LinearNode


class TestLinearNode:
    """测试LinearNode类"""

    def test_linear_node_creation(self):
        """测试Linear节点创建"""
        node = LinearNode()
        assert node.node_type == "Linear"
        assert node.display_name == "Linear (全连接层)"
        assert "input" in node.input_pins
        assert "output" in node.output_pins

    def test_linear_node_properties(self):
        """测试Linear节点属性"""
        node = LinearNode()
        assert node.get_property("in_features") == 128
        assert node.get_property("out_features") == 64
        assert node.get_property("bias") is True

    def test_linear_node_module_creation(self):
        """测试PyTorch模块创建"""
        node = LinearNode()
        module = node.get_module()
        assert isinstance(module, torch.nn.Linear)
        assert module.in_features == 128
        assert module.out_features == 64
        assert module.bias is not None  # bias=True

    def test_linear_node_execute_without_input(self):
        """测试无输入时的执行（应使用默认测试张量）"""
        node = LinearNode()
        node.execute()
        
        output = node.get_output_value("output")
        assert output is not None
        assert isinstance(output, torch.Tensor)
        assert output.shape == (1, 64)  # out_features=64

    def test_linear_node_execute_with_input(self):
        """测试有输入时的执行"""
        node = LinearNode()
        node.set_property("in_features", 32)
        node.set_property("out_features", 16)
        
        # 创建输入张量
        input_tensor = torch.randn(2, 32)  # batch_size=2, in_features=32
        node.set_input_value("input", input_tensor)
        
        # 执行节点
        node.execute()
        
        # 验证输出
        output = node.get_output_value("output")
        assert output is not None
        assert isinstance(output, torch.Tensor)
        assert output.shape == (2, 16)  # batch_size=2, out_features=16

    def test_linear_node_no_bias(self):
        """测试不使用偏置的Linear节点"""
        node = LinearNode()
        node.set_property("bias", False)
        node.set_property("in_features", 10)
        node.set_property("out_features", 5)
        
        module = node.get_module()
        assert module.bias is None  # bias=False

    def test_linear_node_forward_pass(self):
        """测试前向传播的正确性"""
        node = LinearNode()
        node.set_property("in_features", 3)
        node.set_property("out_features", 2)
        
        # 设置固定权重以便测试
        module = node.get_module()
        with torch.no_grad():
            module.weight.fill_(1.0)
            module.bias.fill_(0.0)
        
        # 创建输入
        input_tensor = torch.ones(1, 3)
        node.set_input_value("input", input_tensor)
        
        # 执行
        node.execute()
        
        # 验证输出（权重全为1，输入全为1，应输出[3.0, 3.0]）
        output = node.get_output_value("output")
        expected = torch.tensor([[3.0, 3.0]])
        assert torch.allclose(output, expected)

    def test_linear_node_caching(self):
        """测试输出缓存机制"""
        node = LinearNode()
        node.set_property("in_features", 4)
        node.set_property("out_features", 2)
        
        input_tensor = torch.randn(1, 4)
        node.set_input_value("input", input_tensor)
        
        # 第一次执行
        node.execute()
        output1 = node.get_output_value("output")
        
        # 不改变输入，再次获取输出应返回缓存结果
        output2 = node.get_output_value("output")
        assert torch.equal(output1, output2)

    def test_linear_node_repr(self):
        """测试字符串表示"""
        node = LinearNode()
        node.set_property("in_features", 128)
        node.set_property("out_features", 64)
        
        repr_str = repr(node)
        assert "LinearNode" in repr_str
        assert "128" in repr_str
        assert "64" in repr_str
