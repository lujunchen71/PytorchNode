"""
子网络接口引脚节点 - 用于子网络的输入/输出接口

SubnetInputPinNode:
- 子网络内部的输入接口节点
- 接收来自子网络外部的数据
- 不可手动创建（由打包时自动创建）
- 不可手动删除（随子网络删除）
- 没有参数

SubnetOutputPinNode:
- 子网络内部的输出接口节点
- 将数据输出到子网络外部
- 可以手动创建以增加输出端口
- 有index参数（从0开始）
"""

from typing import Dict, List, Optional, Any
from core.base.node import Node, NodeCategory
from core.base.pin import Pin, PinType
from core.base.node_registry import register_node

import logging

logger = logging.getLogger(__name__)


@register_node
class SubnetInputPinNode(Node):
    """
    子网络输入引脚节点
    
    功能：
    - 作为子网络的输入接口
    - 从子网络外部接收数据
    - 将数据传递给子网络内部的节点
    
    特点：
    - 不可手动创建
    - 不可手动删除
    - 没有参数
    """
    
    node_type = "subnet.input_pin"
    display_name = "Input"
    node_category = NodeCategory.SUBNET
    
    # 标记为系统节点，不可手动创建/删除
    is_system_node = True
    
    def init_pins(self) -> None:
        """初始化引脚"""
        # 输出引脚 - 将数据传递给子网络内部
        self.add_output_pin("output", PinType.ANY, label="输出")
    
    def init_properties(self) -> None:
        """初始化属性 - 无参数"""
        pass
    
    def execute(self) -> None:
        """执行节点 - 数据由外部传入"""
        # 数据由 SubnetNode 的 execute 方法设置
        self._is_dirty = False


@register_node
class SubnetOutputPinNode(Node):
    """
    子网络输出引脚节点
    
    功能：
    - 作为子网络的输出接口
    - 收集子网络内部节点的输出
    - 将数据传递到子网络外部
    
    特点：
    - 可以手动创建以增加输出端口
    - 可以手动删除
    - 有index参数（从0开始）
    """
    
    node_type = "subnet.output_pin"
    display_name = "Output"
    node_category = NodeCategory.SUBNET
    
    # 可以手动创建
    is_system_node = False
    
    def __init__(self, name: str = None, node_graph=None, index: int = 0):
        """初始化输出引脚节点
        
        Args:
            name: 节点名称
            node_graph: 所属节点图
            index: 输出索引（从0开始）
        """
        self._index = index
        super().__init__(name, node_graph)
    
    def init_pins(self) -> None:
        """初始化引脚"""
        # 输入引脚 - 接收子网络内部节点的输出
        self.add_input_pin("input", PinType.ANY, label="输入")
    
    def init_properties(self) -> None:
        """初始化属性"""
        # 使用 properties 字典存储 index 参数
        self.properties["index"] = self._index
    
    @property
    def index(self) -> int:
        """获取输出索引"""
        return self.properties.get("index", self._index)
    
    @index.setter
    def index(self, value: int):
        """设置输出索引"""
        self._index = value
        self.properties["index"] = value
    
    def execute(self) -> None:
        """执行节点 - 数据透传"""
        # 获取输入值并设置到输出缓存
        input_value = self.get_input_value("input") if "input" in self.input_pins else None
        self._output_cache["input"] = input_value  # 透传到外部
        self._is_dirty = False
    
    def to_dict(self) -> dict:
        """序列化为字典"""
        data = super().to_dict()
        data["index"] = self._index
        return data
    
    @classmethod
    def from_dict(cls, data: dict, node_graph=None) -> 'SubnetOutputPinNode':
        """从字典反序列化"""
        index = data.get("index", 0)
        node = cls(
            name=data.get("name"),
            node_graph=node_graph,
            index=index
        )
        node.position = tuple(data.get("position", [0, 0]))
        return node
