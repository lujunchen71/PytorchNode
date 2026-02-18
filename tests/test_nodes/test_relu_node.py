"""
测试ReLU激活函数节点
T036 [P] [US1] 编写ReLU节点测试
"""

import pytest
import torch
from core.nodes.nn.activation_nodes import ReLUNode, SigmoidNode, TanhNode


class TestReLUNode:
    """测试ReLU激活函数节点"""

    def test_relu_node_creation(self):
        """测试ReLU节点创建"""
        node = ReLUNode()
        assert node.node_type == "ReLU"
        assert node.display_name == "ReLU"
        assert "input" in node.input_pins
        assert "output" in node.output_pins

    def test_relu_node_properties(self):
        """测试ReLU节点属性"""
        node = ReLUNode()
        assert node.get_property("inplace") is False

    def test_relu_node_module_creation(self):
        """测试PyTorch模块创建"""
        node = ReLUNode()
        module = node.get_module()
        assert isinstance(module, torch.nn.ReLU)

    def test_relu_node_execute_without_input(self):
        """测试无输入时的执行"""
        node = ReLUNode()
        node.execute()
        
        output = node.get_output_value("output")
        assert output is not None
        assert isinstance(output, torch.Tensor)

    def test_relu_node_execute_with_input(self):
        """测试有输入时的执行"""
        node = ReLUNode()
        
        # 创建包含正负值的输入
        input_tensor = torch.tensor([[-1.0, 0.0, 1.0, 2.0]])
        node.set_input_value("input", input_tensor)
        
        # 执行节点
        node.execute()
        
        # 验证输出（负值应变为0）
        output = node.get_output_value("output")
        expected = torch.tensor([[0.0, 0.0, 1.0, 2.0]])
        assert torch.allclose(output, expected)

    def test_relu_node_negative_values(self):
        """测试ReLU对负值的处理"""
        node = ReLUNode()
        
        input_tensor = torch.tensor([[-5.0, -3.0, -1.0]])
        node.set_input_value("input", input_tensor)
        node.execute()
        
        output = node.get_output_value("output")
        expected = torch.tensor([[0.0, 0.0, 0.0]])
        assert torch.allclose(output, expected)

    def test_relu_node_positive_values(self):
        """测试ReLU对正值的处理"""
        node = ReLUNode()
        
        input_tensor = torch.tensor([[1.0, 2.0, 3.0]])
        node.set_input_value("input", input_tensor)
        node.execute()
        
        output = node.get_output_value("output")
        assert torch.allclose(output, input_tensor)  # 正值不变

    def test_relu_node_inplace_operation(self):
        """测试inplace选项"""
        node = ReLUNode()
        node.set_property("inplace", True)
        
        module = node.get_module()
        assert module.inplace is True


class TestSigmoidNode:
    """测试Sigmoid激活函数节点"""

    def test_sigmoid_node_creation(self):
        """测试Sigmoid节点创建"""
        node = SigmoidNode()
        assert node.node_type == "Sigmoid"
        assert node.display_name == "Sigmoid"

    def test_sigmoid_node_execute(self):
        """测试Sigmoid节点执行"""
        node = SigmoidNode()
        
        input_tensor = torch.tensor([[0.0]])
        node.set_input_value("input", input_tensor)
        node.execute()
        
        output = node.get_output_value("output")
        # sigmoid(0) = 0.5
        assert torch.allclose(output, torch.tensor([[0.5]]))

    def test_sigmoid_node_range(self):
        """测试Sigmoid输出范围在(0, 1)之间"""
        node = SigmoidNode()
        
        input_tensor = torch.tensor([[-100.0, -1.0, 0.0, 1.0, 100.0]])
        node.set_input_value("input", input_tensor)
        node.execute()
        
        output = node.get_output_value("output")
        assert torch.all(output > 0)
        assert torch.all(output < 1)


class TestTanhNode:
    """测试Tanh激活函数节点"""

    def test_tanh_node_creation(self):
        """测试Tanh节点创建"""
        node = TanhNode()
        assert node.node_type == "Tanh"
        assert node.display_name == "Tanh"

    def test_tanh_node_execute(self):
        """测试Tanh节点执行"""
        node = TanhNode()
        
        input_tensor = torch.tensor([[0.0]])
        node.set_input_value("input", input_tensor)
        node.execute()
        
        output = node.get_output_value("output")
        # tanh(0) = 0
        assert torch.allclose(output, torch.tensor([[0.0]]))

    def test_tanh_node_range(self):
        """测试Tanh输出范围在(-1, 1)之间"""
        node = TanhNode()
        
        input_tensor = torch.tensor([[-100.0, -1.0, 0.0, 1.0, 100.0]])
        node.set_input_value("input", input_tensor)
        node.execute()
        
        output = node.get_output_value("output")
        assert torch.all(output > -1)
        assert torch.all(output < 1)

    def test_tanh_node_symmetry(self):
        """测试Tanh的对称性: tanh(-x) = -tanh(x)"""
        node = TanhNode()
        
        x = 2.0
        input_pos = torch.tensor([[x]])
        input_neg = torch.tensor([[-x]])
        
        # 计算tanh(x)
        node.set_input_value("input", input_pos)
        node.execute()
        output_pos = node.get_output_value("output")
        
        # 计算tanh(-x)
        node.set_input_value("input", input_neg)
        node.execute()
        output_neg = node.get_output_value("output")
        
        # 验证对称性
        assert torch.allclose(output_neg, -output_pos)
