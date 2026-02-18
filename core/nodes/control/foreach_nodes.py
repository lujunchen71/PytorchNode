"""
ForEach循环节点组 - 实现训练循环等迭代逻辑

ForEach是三节点组：
1. ForEachBegin - 循环开始，设置迭代次数
2. ForEachData - 提供当前迭代索引和总迭代次数  
3. ForEachEnd - 循环结束，收集结果

使用方式：
- ForEachBegin连接到循环体内的第一个节点
- ForEachData提供iteration和total_iterations输出
- 循环体内的最后一个节点连接到ForEachEnd
"""

from typing import Dict, List, Optional, Any
from core.base.node import Node, NodeCategory
from core.base.pin import Pin, PinType
from core.base.pack import Pack

import logging

logger = logging.getLogger(__name__)


class ForEachBeginNode(Node):
    """
    ForEach循环开始节点
    
    功能：
    - 设置循环次数（iterations）
    - 输出循环开始信号
    - 连接到ForEachEnd节点完成循环闭环
    """
    
    node_type = "control.foreach_begin"
    display_name = "ForEach Begin"
    node_category = NodeCategory.LOGIC
    allowed_contexts = ["/obj", "/train"]  # 在obj和train路径下可用
    
    def init_pins(self) -> None:
        """初始化引脚 - 实现抽象方法"""
        # 输入引脚
        self.add_input_pin("input", PinType.ANY, label="输入")
        
        # 输出引脚
        self.add_output_pin("output", PinType.ANY, label="循环体")
        self.add_output_pin("end_signal", PinType.EXEC, label="结束信号")
    
    def init_properties(self) -> None:
        """初始化属性"""
        self.properties["iterations"] = 10
        self.properties["end_node_path"] = ""
    
    def execute(self) -> None:
        """执行节点"""
        iterations = self.properties.get("iterations", 10)
        
        # 传递输入到循环体
        input_value = self.get_input_value("input") if "input" in self.input_pins else None
        
        logger.info(f"ForEachBegin: 开始循环，迭代次数={iterations}")
        
        # 设置输出
        self._output_cache["output"] = input_value
        self._output_cache["end_signal"] = None
        self._is_dirty = False


class ForEachDataNode(Node):
    """
    ForEach数据节点
    
    功能：
    - 提供当前迭代索引（current_iteration）
    - 提供总迭代次数（total_iterations）
    - 可在循环体内使用这些数据进行条件判断
    """
    
    node_type = "control.foreach_data"
    display_name = "ForEach Data"
    node_category = NodeCategory.LOGIC
    allowed_contexts = ["/obj", "/train"]
    
    def __init__(self, name: str = None, node_graph=None):
        """初始化"""
        super().__init__(name, node_graph)
        self._current_iteration = 0
        self._total_iterations = 0
    
    def init_pins(self) -> None:
        """初始化引脚 - 实现抽象方法"""
        # 输入：从ForEachBegin或上游节点接收
        self.add_input_pin("input", PinType.ANY, label="输入")
        
        # 输出
        self.add_output_pin("current", PinType.INT, label="当前索引")
        self.add_output_pin("total", PinType.INT, label="总迭代数")
        self.add_output_pin("output", PinType.ANY, label="数据透传")
    
    def init_properties(self) -> None:
        """初始化属性"""
        self.properties["begin_node_path"] = ""
    
    def set_iteration_data(self, current: int, total: int):
        """设置迭代数据（由执行引擎调用）"""
        self._current_iteration = current
        self._total_iterations = total
    
    def execute(self) -> None:
        """执行节点"""
        logger.debug(f"ForEachData: iteration {self._current_iteration}/{self._total_iterations}")
        
        # 设置输出
        self._output_cache["current"] = self._current_iteration
        self._output_cache["total"] = self._total_iterations
        self._output_cache["output"] = self.get_input_value("input") if "input" in self.input_pins else None
        self._is_dirty = False


class ForEachEndNode(Node):
    """
    ForEach循环结束节点
    
    功能：
    - 收集循环体内所有迭代的结果
    - 输出聚合后的数据列表
    - 完成循环闭环
    """
    
    node_type = "control.foreach_end"
    display_name = "ForEach End"
    node_category = NodeCategory.LOGIC
    allowed_contexts = ["/obj", "/train"]
    
    def init_pins(self) -> None:
        """初始化引脚 - 实现抽象方法"""
        # 输入：从循环体最后一个节点接收
        self.add_input_pin("input", PinType.ANY, label="循环体输入")
        self.add_input_pin("begin_signal", PinType.EXEC, label="开始信号")
        
        # 输出：聚合后的结果
        self.add_output_pin("output", PinType.ANY, label="结果列表")
    
    def init_properties(self) -> None:
        """初始化属性"""
        self.properties["collect_mode"] = "list"  # list, stack, concat
    
    def execute(self) -> None:
        """执行节点"""
        input_value = self.get_input_value("input") if "input" in self.input_pins else []
        
        logger.info(f"ForEachEnd: 收集结果")
        
        # 收集结果（实际聚合由执行引擎处理）
        self._output_cache["output"] = input_value
        self._is_dirty = False
