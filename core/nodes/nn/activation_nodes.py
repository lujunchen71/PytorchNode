"""
激活函数节点
"""

import torch
import torch.nn as nn
from typing import Optional

from core.base import Node, NodeCategory, PinType, register_node


@register_node
class ReLUNode(Node):
    """ReLU激活函数节点"""

    node_type = "ReLU"
    node_category = NodeCategory.NN
    display_name = "ReLU"

    def init_pins(self) -> None:
        """初始化引脚"""
        self.add_input_pin("input", PinType.TENSOR, label="输入")
        self.add_output_pin("output", PinType.TENSOR, label="输出")

    def init_properties(self) -> None:
        """初始化属性"""
        self.properties = {
            "inplace": False,  # 是否原地操作
        }
        self._module: Optional[nn.ReLU] = None

    def get_module(self) -> nn.ReLU:
        """获取或创建PyTorch模块"""
        if self._module is None:
            self._module = nn.ReLU(inplace=self.get_property("inplace"))
        return self._module

    def execute(self) -> None:
        """执行节点计算"""
        input_tensor = self.get_input_value("input")
        
        if input_tensor is None:
            input_tensor = torch.randn(1, 10)
        
        module = self.get_module()
        output_tensor = module(input_tensor)
        
        self._output_cache["output"] = output_tensor
        self._is_dirty = False


@register_node
class SigmoidNode(Node):
    """Sigmoid激活函数节点"""

    node_type = "Sigmoid"
    node_category = NodeCategory.NN
    display_name = "Sigmoid"

    def init_pins(self) -> None:
        """初始化引脚"""
        self.add_input_pin("input", PinType.TENSOR, label="输入")
        self.add_output_pin("output", PinType.TENSOR, label="输出")

    def init_properties(self) -> None:
        """初始化属性"""
        self.properties = {}
        self._module: Optional[nn.Sigmoid] = None

    def get_module(self) -> nn.Sigmoid:
        """获取或创建PyTorch模块"""
        if self._module is None:
            self._module = nn.Sigmoid()
        return self._module

    def execute(self) -> None:
        """执行节点计算"""
        input_tensor = self.get_input_value("input")
        
        if input_tensor is None:
            input_tensor = torch.randn(1, 10)
        
        module = self.get_module()
        output_tensor = module(input_tensor)
        
        self._output_cache["output"] = output_tensor
        self._is_dirty = False


@register_node
class TanhNode(Node):
    """Tanh激活函数节点"""

    node_type = "Tanh"
    node_category = NodeCategory.NN
    display_name = "Tanh"

    def init_pins(self) -> None:
        """初始化引脚"""
        self.add_input_pin("input", PinType.TENSOR, label="输入")
        self.add_output_pin("output", PinType.TENSOR, label="输出")

    def init_properties(self) -> None:
        """初始化属性"""
        self.properties = {}
        self._module: Optional[nn.Tanh] = None

    def get_module(self) -> nn.Tanh:
        """获取或创建PyTorch模块"""
        if self._module is None:
            self._module = nn.Tanh()
        return self._module

    def execute(self) -> None:
        """执行节点计算"""
        input_tensor = self.get_input_value("input")
        
        if input_tensor is None:
            input_tensor = torch.randn(1, 10)
        
        module = self.get_module()
        output_tensor = module(input_tensor)
        
        self._output_cache["output"] = output_tensor
        self._is_dirty = False
