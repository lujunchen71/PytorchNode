"""
执行器 (Executor) - 节点图执行引擎 (Phase 5 T076)

负责：
1. 对节点图进行拓扑排序
2. 执行节点顺序
3. 管理节点间的Pack传递
4. 处理多Pack场景
"""

from typing import Dict, List, Optional
from collections import defaultdict

from core.base.node_graph import NodeGraph
from core.base.node import Node
from core.base.pin import InputPin, OutputPin
from core.base.pack import Pack, TorchPack


class Executor:
    """节点图执行器"""
    
    def __init__(self, node_graph: NodeGraph):
        """
        初始化执行器
        
        Args:
            node_graph: 要执行的节点图
        """
        self.node_graph = node_graph
        self.execution_order: List[Node] = []
        self.node_outputs: Dict[Node, Dict[str, List[Pack]]] = {}  # 缓存节点输出
        
    def prepare(self) -> None:
        """准备执行：拓扑排序、验证图"""
        # 验证图
        errors = self.node_graph.validate()
        if errors:
            raise ValueError(f"Graph validation failed: {errors}")
        
        # 拓扑排序
        self.execution_order = self.node_graph.topological_sort()
        
        # 清空输出缓存
        self.node_outputs.clear()
        
    def execute(self) -> Dict[str, Pack]:
        """
        执行整个图
        
        Returns:
            最终输出包的字典（键为节点名？实际上返回根节点的输出？）
            暂时返回一个空字典，未来可扩展返回输出节点的结果
        """
        self.prepare()
        
        # 为每个引脚收集输入包
        pin_inputs: Dict[InputPin, List[Pack]] = defaultdict(list)
        
        for node in self.execution_order:
            # 构建当前节点的输入包字典
            input_packs: Dict[str, List[Pack]] = {}
            
            # 遍历每个输入引脚，从上游收集包
            for pin_name, pin in node.input_pins.items():
                # 获取连接到该引脚的所有连接
                connections = pin.connections
                packs_for_pin = []
                
                for conn in connections:
                    source_pin = conn.source_pin
                    source_node = conn.source_node
                    
                    # 从缓存中获取源节点的输出
                    if source_node in self.node_outputs:
                        source_outputs = self.node_outputs[source_node]
                        # 源引脚名对应源节点的输出引脚名
                        source_pin_name = source_pin.name
                        if source_pin_name in source_outputs:
                            packs_for_pin.extend(source_outputs[source_pin_name])
                
                input_packs[pin_name] = packs_for_pin
            
            # 执行节点
            try:
                output_packs = node.execute(input_packs)
            except Exception as e:
                raise RuntimeError(f"Node '{node.name}' execution failed: {e}")
            
            # 缓存输出
            self.node_outputs[node] = output_packs
        
        # 收集最终输出（所有没有下游连接的输出引脚）
        final_outputs = {}
        for node, outputs in self.node_outputs.items():
            for pin_name, packs in outputs.items():
                # 查找输出引脚是否有下游连接
                pin = node.get_output_pin(pin_name)
                if pin and not pin.connections:
                    # 这是一个终端输出，添加到最终结果
                    key = f"{node.name}.{pin_name}"
                    if packs:
                        final_outputs[key] = packs[0]  # 暂时只返回第一个包
        
        return final_outputs
    
    def execute_node(self, node: Node, input_packs: Dict[str, List[Pack]]) -> Dict[str, List[Pack]]:
        """
        执行单个节点（外部调用）
        
        Args:
            node: 要执行的节点
            input_packs: 输入包字典
            
        Returns:
            输出包字典
        """
        return node.execute(input_packs)
    
    def get_node_outputs(self, node: Node) -> Optional[Dict[str, List[Pack]]]:
        """
        获取节点的输出缓存
        
        Args:
            node: 节点对象
            
        Returns:
            节点的输出包字典，如果未执行则返回None
        """
        return self.node_outputs.get(node)