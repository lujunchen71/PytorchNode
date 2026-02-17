"""
Linear节点 - 全连接层（nn.Linear）
"""

import torch
import torch.nn as nn
from typing import Optional

from core.base import Node, NodeCategory, PinType, register_node


@register_node
class LinearNode(Node):
    """全连接层节点"""

    node_type = "Linear"
    node_category = NodeCategory.NN
    display_name = "Linear (全连接层)"

    def init_pins(self) -> None:
        """初始化引脚"""
        # 输入引脚
        self.add_input_pin("input", PinType.TENSOR, label="输入")

        # 输出引脚
        self.add_output_pin("output", PinType.TENSOR, label="输出")

    def init_properties(self) -> None:
        """初始化属性"""
        self.properties = {
            "in_features": 128,  # 输入特征数
            "out_features": 64,  # 输出特征数
            "bias": True,  # 是否使用偏置
        }

        # PyTorch模块（延迟初始化）
        self._module: Optional[nn.Linear] = None

    def get_module(self) -> nn.Linear:
        """获取或创建PyTorch模块"""
        if self._module is None:
            self._module = nn.Linear(
                in_features=self.get_property("in_features"),
                out_features=self.get_property("out_features"),
                bias=self.get_property("bias")
            )
        return self._module

    def execute(self) -> None:
        """执行节点计算"""
        # 获取输入
        input_tensor = self.get_input_value("input")

        if input_tensor is None:
            # 如果没有输入，创建一个示例张量用于测试
            in_features = self.get_property("in_features")
            input_tensor = torch.randn(1, in_features)

        # 执行前向传播
        module = self.get_module()
        output_tensor = module(input_tensor)

        # 保存输出
        self._output_cache["output"] = output_tensor
        self._is_dirty = False

    def __repr__(self) -> str:
        """字符串表示"""
        in_feat = self.get_property("in_features")
        out_feat = self.get_property("out_features")
        return f"LinearNode('{self.name}', {in_feat}->{out_feat})"
