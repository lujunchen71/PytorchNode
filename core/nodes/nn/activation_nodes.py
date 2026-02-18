"""
激活函数节点
"""

from typing import Optional, TYPE_CHECKING

from core.base import Node, NodeCategory, PinType, register_node

# 延迟导入 PyTorch，只在类型检查时导入
if TYPE_CHECKING:
    import torch
    import torch.nn as nn


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
        self._module = None  # 延迟初始化

    def get_module(self):
        """获取或创建PyTorch模块"""
        if self._module is None:
            import torch.nn as nn
            self._module = nn.ReLU(inplace=self.get_property("inplace"))
        return self._module

    def execute(self) -> None:
        """执行节点计算"""
        import torch
        
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
        self._module = None  # 延迟初始化

    def get_module(self):
        """获取或创建PyTorch模块"""
        if self._module is None:
            import torch.nn as nn
            self._module = nn.Sigmoid()
        return self._module

    def execute(self) -> None:
        """执行节点计算"""
        import torch
        
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
        self._module = None  # 延迟初始化

    def get_module(self):
        """获取或创建PyTorch模块"""
        if self._module is None:
            import torch.nn as nn
            self._module = nn.Tanh()
        return self._module

    def execute(self) -> None:
        """执行节点计算"""
        import torch
        
        input_tensor = self.get_input_value("input")
        
        if input_tensor is None:
            input_tensor = torch.randn(1, 10)
        
        module = self.get_module()
        output_tensor = module(input_tensor)
        
        self._output_cache["output"] = output_tensor
        self._is_dirty = False
