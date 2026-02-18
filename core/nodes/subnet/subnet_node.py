"""
子网络节点 - 封装一组节点为可复用模块

SubnetNode是一个容器节点，包含：
- 内部节点图（subgraph）
- 输入/输出映射接口
- 默认4个输入端和1个输出端
- 与SubnetInputPin/SubnetOutputPin配合使用
"""

from typing import Dict, List, Optional, Any
from core.base.node import Node, NodeCategory
from core.base.node_graph import NodeGraph
from core.base.pin import Pin, PinType
from core.base.pack import Pack
from core.base.node_registry import register_node

import logging

logger = logging.getLogger(__name__)


# 默认输入端口数量
DEFAULT_INPUT_COUNT = 4
# 默认输出端口数量
DEFAULT_OUTPUT_COUNT = 1


@register_node
class SubnetNode(Node):
    """
    子网络节点 - 封装一组节点
    
    功能：
    - 包含内部节点图
    - 默认4个输入端，1个输出端
    - 输入端对应内部的SubnetInputPin节点
    - 输出端对应内部的SubnetOutputPin节点
    - 可嵌套（子网络中可包含子网络）
    """
    
    node_type = "subnet"
    display_name = "Subnet"
    node_category = NodeCategory.SUBNET
    allowed_contexts = ["/obj", "/train"]  # 子网络可以在obj和train下创建
    
    def __init__(self, name: str = None, node_graph=None, input_count: int = DEFAULT_INPUT_COUNT, output_count: int = DEFAULT_OUTPUT_COUNT):
        """初始化子网络节点"""
        self._input_count = input_count
        self._output_count = output_count
        
        # 输入/输出映射（内部Pin节点名称 -> 外部引脚名称）
        self._input_pin_nodes: Dict[str, str] = {}  # {internal_input_pin_node_name: external_pin_name}
        self._output_pin_nodes: Dict[str, str] = {}  # {internal_output_pin_node_name: external_pin_name}
        
        # 先调用父类初始化
        super().__init__(name, node_graph)
        
        # 创建内部节点图（在 super().__init__ 之后，因为需要 self.name）
        self._subgraph = NodeGraph(name=self.name, parent=node_graph)
        
        # 创建默认的SubnetInputPin节点（4个）
        self._create_default_input_pins()
    
    def _create_default_input_pins(self):
        """创建默认的SubnetInputPin节点"""
        from core.nodes.subnet.subnet_pins import SubnetInputPinNode
        
        for i in range(self._input_count):
            pin_name = f"Input_{i+1}"
            input_pin_node = SubnetInputPinNode(
                name=pin_name,
                node_graph=self._subgraph
            )
            # 设置位置（从上到下排列）
            input_pin_node.position = (i * 80 - 120, -100)
            
            # 添加到子图
            self._subgraph.add_node(input_pin_node)
            input_pin_node.node_graph = self._subgraph
            
            # 建立映射
            external_pin_name = f"input_{i}"
            self._input_pin_nodes[pin_name] = external_pin_name
            
            logger.info(f"Subnet '{self.name}': 创建默认InputPin {pin_name} -> {external_pin_name}")
    
    @property
    def subgraph(self) -> NodeGraph:
        """获取内部节点图"""
        return self._subgraph
    
    @property
    def input_count(self) -> int:
        """获取输入端口数量"""
        return self._input_count
    
    @property
    def output_count(self) -> int:
        """获取输出端口数量"""
        return self._output_count
    
    def init_pins(self) -> None:
        """初始化引脚 - 创建默认的输入/输出端口"""
        # 创建默认输入引脚
        for i in range(self._input_count):
            pin_name = f"input_{i}"
            self.add_input_pin(pin_name, PinType.ANY, label=f"In {i+1}")
        
        # 创建默认输出引脚
        for i in range(self._output_count):
            pin_name = f"output_{i}"
            self.add_output_pin(pin_name, PinType.ANY, label=f"Out {i+1}")
    
    def init_properties(self) -> None:
        """初始化属性"""
        self.properties["subnet_name"] = self.name
    
    def add_input_pin_external(self, index: int = None) -> str:
        """
        添加外部输入引脚
        
        Args:
            index: 引脚索引（可选，默认添加到最后）
        
        Returns:
            创建的引脚名称
        """
        if index is None:
            index = self._input_count
        
        pin_name = f"input_{index}"
        if pin_name not in self.input_pins:
            self.add_input_pin(pin_name, PinType.ANY, label=f"In {index+1}")
            self._input_count += 1
            logger.info(f"Subnet '{self.name}': 添加外部输入引脚 {pin_name}")
        
        return pin_name
    
    def remove_input_pin_external(self, index: int) -> bool:
        """
        删除外部输入引脚及其对应的内部SubnetInputPinNode
        
        Args:
            index: 引脚索引
        
        Returns:
            是否成功删除
        """
        from core.nodes.subnet.subnet_pins import SubnetInputPinNode
        
        # 至少保留一个输入引脚
        if self._input_count <= 1:
            logger.warning(f"Subnet '{self.name}': 无法删除最后一个输入引脚")
            return False
        
        pin_name = f"input_{index}"
        
        # 检查引脚是否存在
        if pin_name not in self.input_pins:
            logger.warning(f"Subnet '{self.name}': 输入引脚 {pin_name} 不存在")
            return False
        
        # 查找对应的内部InputPin节点
        internal_node_name = None
        for node_name, ext_pin in self._input_pin_nodes.items():
            if ext_pin == pin_name:
                internal_node_name = node_name
                break
        
        # 删除内部InputPin节点
        if internal_node_name:
            internal_node = self.get_internal_node(internal_node_name)
            if internal_node:
                # 删除内部节点的所有连接
                for pin in list(internal_node.output_pins.values()):
                    for conn in list(pin.connections):
                        self._subgraph.remove_connection(conn)
                
                # 从子图中移除节点
                self._subgraph.remove_node(internal_node)
                logger.info(f"Subnet '{self.name}': 删除内部InputPin节点 {internal_node_name}")
            
            # 删除映射
            del self._input_pin_nodes[internal_node_name]
        
        # 删除外部引脚
        if pin_name in self._pins:
            del self._pins[pin_name]
        
        # 更新计数
        self._input_count -= 1
        
        logger.info(f"Subnet '{self.name}': 删除外部输入引脚 {pin_name}")
        return True
    
    def add_output_pin_external(self, index: int = None) -> str:
        """
        添加外部输出引脚
        
        Args:
            index: 引脚索引（可选，默认添加到最后）
        
        Returns:
            创建的引脚名称
        """
        if index is None:
            index = self._output_count
        
        pin_name = f"output_{index}"
        if pin_name not in self.output_pins:
            self.add_output_pin(pin_name, PinType.ANY, label=f"Out {index+1}")
            self._output_count += 1
            logger.info(f"Subnet '{self.name}': 添加外部输出引脚 {pin_name}")
        
        return pin_name
    
    def register_output_pin_node(self, internal_node_name: str, index: int) -> tuple:
        """
        注册内部SubnetOutputPinNode并动态更新外部输出端口
        
        Args:
            internal_node_name: 内部SubnetOutputPinNode名称
            index: 输出索引
        
        Returns:
            (success: bool, external_pin_name: str, error_message: str)
        """
        # 检查index是否已被使用
        for node_name, ext_pin in self._output_pin_nodes.items():
            if ext_pin == f"output_{index}":
                return (False, None, f"输出索引 {index} 已被节点 '{node_name}' 使用")
        
        # 确保外部引脚存在
        external_pin_name = f"output_{index}"
        if external_pin_name not in self.output_pins:
            self.add_output_pin(external_pin_name, PinType.ANY, label=f"Out {index+1}")
            # 更新输出计数（取最大值）
            self._output_count = max(self._output_count, index + 1)
            logger.info(f"Subnet '{self.name}': 动态创建外部输出引脚 {external_pin_name}")
        
        # 建立映射
        self._output_pin_nodes[internal_node_name] = external_pin_name
        logger.info(f"Subnet '{self.name}': 注册OutputPin {internal_node_name} -> {external_pin_name}")
        
        return (True, external_pin_name, None)
    
    def unregister_output_pin_node(self, internal_node_name: str) -> bool:
        """
        取消注册内部SubnetOutputPinNode
        
        Args:
            internal_node_name: 内部SubnetOutputPinNode名称
        
        Returns:
            是否成功取消注册
        """
        if internal_node_name not in self._output_pin_nodes:
            return False
        
        external_pin_name = self._output_pin_nodes[internal_node_name]
        del self._output_pin_nodes[internal_node_name]
        
        logger.info(f"Subnet '{self.name}': 取消注册OutputPin {internal_node_name} -> {external_pin_name}")
        return True
    
    def get_used_output_indices(self) -> List[int]:
        """
        获取已使用的输出索引列表
        
        Returns:
            已使用的索引列表
        """
        indices = []
        for node_name, ext_pin in self._output_pin_nodes.items():
            # 从 "output_X" 提取 X
            try:
                index = int(ext_pin.split("_")[1])
                indices.append(index)
            except (IndexError, ValueError):
                continue
        return sorted(indices)
    
    def map_input_pin_node(self, internal_node_name: str, external_pin_name: str):
        """
        映射内部InputPin节点到外部引脚
        
        Args:
            internal_node_name: 内部SubnetInputPin节点名称
            external_pin_name: 外部引脚名称
        """
        self._input_pin_nodes[internal_node_name] = external_pin_name
        logger.info(f"Subnet '{self.name}': 映射输入 {internal_node_name} -> {external_pin_name}")
    
    def map_output_pin_node(self, internal_node_name: str, external_pin_name: str):
        """
        映射内部OutputPin节点到外部引脚
        
        Args:
            internal_node_name: 内部SubnetOutputPin节点名称
            external_pin_name: 外部引脚名称
        """
        self._output_pin_nodes[internal_node_name] = external_pin_name
        logger.info(f"Subnet '{self.name}': 映射输出 {internal_node_name} -> {external_pin_name}")
    
    def get_internal_node(self, node_name: str) -> Optional[Node]:
        """获取内部节点"""
        return self._subgraph.get_node(node_name)
    
    def add_internal_node(self, node: Node):
        """添加节点到子网络内部"""
        self._subgraph.add_node(node)
        node.node_graph = self._subgraph
        logger.info(f"Subnet '{self.name}': 添加内部节点 {node.name}")
    
    def remove_internal_node(self, node: Node):
        """从子网络内部移除节点"""
        self._subgraph.remove_node(node)
        logger.info(f"Subnet '{self.name}': 移除内部节点 {node.name}")
    
    def get_external_pin_for_input_node(self, internal_node_name: str) -> Optional[str]:
        """获取内部InputPin节点对应的外部引脚名称"""
        return self._input_pin_nodes.get(internal_node_name)
    
    def get_external_pin_for_output_node(self, internal_node_name: str) -> Optional[str]:
        """获取内部OutputPin节点对应的外部引脚名称"""
        return self._output_pin_nodes.get(internal_node_name)
    
    def execute(self) -> None:
        """
        执行子网络
        
        执行流程：
        1. 将外部输入传递到内部InputPin节点
        2. 执行内部节点图
        3. 从内部OutputPin节点收集输出
        4. 如果没有OutputPin节点，将第一个输入直接作为输出
        """
        logger.info(f"Subnet '{self.name}': 开始执行")
        
        # 1. 将外部输入传递到内部InputPin节点
        for internal_node_name, external_pin_name in self._input_pin_nodes.items():
            internal_node = self.get_internal_node(internal_node_name)
            if internal_node:
                # 获取外部输入值
                external_value = self.get_input_value(external_pin_name) if external_pin_name in self.input_pins else None
                # 设置到内部节点的输出缓存（InputPin节点直接输出外部数据）
                internal_node._output_cache["output"] = external_value
                logger.debug(f"  传递输入: {external_pin_name} -> {internal_node_name}")
        
        # 2. 执行内部节点图（由执行引擎处理）
        # TODO: 调用执行引擎执行子图
        
        # 3. 从内部OutputPin节点收集输出
        has_output_pins = len(self._output_pin_nodes) > 0
        for internal_node_name, external_pin_name in self._output_pin_nodes.items():
            internal_node = self.get_internal_node(internal_node_name)
            if internal_node:
                # 获取内部节点的输入值（OutputPin节点透传输入）
                internal_value = internal_node.get_input_value("input") if "input" in internal_node.input_pins else None
                # 设置到外部输出缓存
                self._output_cache[external_pin_name] = internal_value
                logger.debug(f"  收集输出: {internal_node_name} -> {external_pin_name}")
        
        # 4. 如果没有OutputPin节点，将第一个输入直接作为输出
        if not has_output_pins:
            first_input_pin = "input_0"
            if first_input_pin in self.input_pins:
                first_input_value = self.get_input_value(first_input_pin)
                self._output_cache["output_0"] = first_input_value
                logger.debug(f"  无OutputPin节点，将第一个输入直接作为输出: {first_input_pin} -> output_0")
        
        self._is_dirty = False
        logger.info(f"Subnet '{self.name}': 执行完成")
    
    def to_dict(self) -> dict:
        """序列化为字典"""
        data = super().to_dict()
        data.update({
            "subgraph": self._subgraph.to_dict(),
            "input_pin_nodes": self._input_pin_nodes,
            "output_pin_nodes": self._output_pin_nodes,
            "input_count": self._input_count,
            "output_count": self._output_count,
        })
        return data
    
    @classmethod
    def from_dict(cls, data: dict, node_graph=None) -> 'SubnetNode':
        """从字典反序列化"""
        input_count = data.get("input_count", DEFAULT_INPUT_COUNT)
        output_count = data.get("output_count", DEFAULT_OUTPUT_COUNT)
        
        node = cls(
            name=data.get("name"), 
            node_graph=node_graph,
            input_count=input_count,
            output_count=output_count
        )
        
        # 恢复基本属性
        node.position = tuple(data.get("position", [0, 0]))
        
        # 恢复映射
        node._input_pin_nodes = data.get("input_pin_nodes", {})
        node._output_pin_nodes = data.get("output_pin_nodes", {})
        
        # TODO: 恢复子图节点
        
        return node
