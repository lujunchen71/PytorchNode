"""
节点（Node）基类 - 所有节点的基类

职责:
- 属性管理
- 引脚管理
- 前向/反向传播接口
- 序列化
"""

from typing import Dict, List, Any, Optional, TYPE_CHECKING
import uuid
from abc import ABC, abstractmethod

from .pin import Pin, PinDirection, PinType

if TYPE_CHECKING:
    from .node_graph import NodeGraph


class NodeCategory:
    """节点分类常量"""
    NN = "Neural Network"  # 神经网络层
    DATA = "Data"  # 数据处理
    TRAINING = "Training"  # 训练相关（损失、优化器、检查点）
    LOGIC = "Logic"  # 逻辑控制
    SUBNET = "Subnet"  # 子网
    SCRIPT = "Script"  # 脚本
    CONTEXT = "Context"  # 上下文根节点
    MATH = "Math"  # 数学运算
    TRANSFORM = "Transform"  # 变换
    VISUALIZATION = "Visualization"  # 可视化


class Node(ABC):
    """节点基类 - 所有节点类型的抽象基类"""

    # 类属性 - 由子类覆盖
    node_type: str = "BaseNode"
    node_category: str = NodeCategory.NN
    display_name: str = "Base Node"
    
    def __init__(self, name: str = None, node_graph: 'NodeGraph' = None):
        """
        初始化节点

        Args:
            name: 节点名称（可选，如果未提供则自动生成）
            node_graph: 所属节点图
        """
        self.id = str(uuid.uuid4())
        self.name = name or self._generate_default_name()
        self.node_graph = node_graph

        # 引脚
        self.input_pins: Dict[str, Pin] = {}
        self.output_pins: Dict[str, Pin] = {}

        # 属性/参数
        self.properties: Dict[str, Any] = {}

        # 图形位置（用于UI）
        self.position = (0.0, 0.0)

        # 执行状态
        self._is_dirty = True
        self._output_cache: Dict[str, Any] = {}

        # 初始化引脚和属性
        self.init_pins()
        self.init_properties()

    def _generate_default_name(self) -> str:
        """生成默认节点名称"""
        return f"{self.node_type}_{self.id[:8]}"

    @abstractmethod
    def init_pins(self) -> None:
        """初始化引脚 - 由子类实现"""
        pass

    def init_properties(self) -> None:
        """初始化属性 - 可由子类覆盖"""
        pass

    def add_input_pin(
        self,
        name: str,
        pin_type: PinType,
        default_value: Any = None,
        is_list: bool = False,
        label: str = None
    ) -> Pin:
        """
        添加输入引脚

        Args:
            name: 引脚名称
            pin_type: 数据类型
            default_value: 默认值
            is_list: 是否为列表类型
            label: 显示标签

        Returns:
            创建的引脚对象
        """
        pin = Pin(
            node=self,
            name=name,
            direction=PinDirection.INPUT,
            pin_type=pin_type,
            default_value=default_value,
            is_list=is_list,
            label=label
        )
        self.input_pins[name] = pin
        return pin

    def add_output_pin(
        self,
        name: str,
        pin_type: PinType,
        label: str = None
    ) -> Pin:
        """
        添加输出引脚

        Args:
            name: 引脚名称
            pin_type: 数据类型
            label: 显示标签

        Returns:
            创建的引脚对象
        """
        pin = Pin(
            node=self,
            name=name,
            direction=PinDirection.OUTPUT,
            pin_type=pin_type,
            label=label
        )
        self.output_pins[name] = pin
        return pin

    def get_input_pin(self, name: str) -> Optional[Pin]:
        """获取输入引脚"""
        return self.input_pins.get(name)

    def get_output_pin(self, name: str) -> Optional[Pin]:
        """获取输出引脚"""
        return self.output_pins.get(name)

    def get_input_value(self, pin_name: str) -> Any:
        """
        获取输入引脚的值

        Args:
            pin_name: 引脚名称

        Returns:
            引脚的值
        """
        pin = self.get_input_pin(pin_name)
        if pin is None:
            raise ValueError(f"Input pin '{pin_name}' not found")
        return pin.get_value()

    def get_output_value(self, pin_name: str) -> Any:
        """
        获取输出引脚的值（触发计算）

        Args:
            pin_name: 引脚名称

        Returns:
            计算后的输出值
        """
        # 检查缓存
        if not self._is_dirty and pin_name in self._output_cache:
            return self._output_cache[pin_name]

        # 执行计算
        self.execute()

        # 返回缓存的输出
        if pin_name not in self._output_cache:
            raise ValueError(f"Output pin '{pin_name}' was not computed")
        
        return self._output_cache[pin_name]

    def set_property(self, name: str, value: Any) -> None:
        """
        设置属性值

        Args:
            name: 属性名称
            value: 属性值
        """
        self.properties[name] = value
        self.mark_dirty()

    def get_property(self, name: str, default: Any = None) -> Any:
        """
        获取属性值

        Args:
            name: 属性名称
            default: 默认值

        Returns:
            属性值
        """
        return self.properties.get(name, default)

    def mark_dirty(self) -> None:
        """标记节点需要重新计算"""
        self._is_dirty = True
        self._output_cache.clear()
        
        # 传播到下游节点
        for pin in self.output_pins.values():
            pin.mark_dirty()

    @abstractmethod
    def execute(self) -> None:
        """
        执行节点计算 - 由子类实现

        子类应该:
        1. 从输入引脚获取值
        2. 执行计算
        3. 将结果写入 self._output_cache
        4. 设置 self._is_dirty = False
        """
        pass

    def validate(self) -> List[str]:
        """
        验证节点配置

        Returns:
            错误信息列表（空列表表示无错误）
        """
        errors = []

        # 检查必需的输入是否连接
        for pin in self.input_pins.values():
            if not pin.is_connected and pin.default_value is None:
                if pin.pin_type != PinType.EXEC:  # EXEC引脚可以不连接
                    errors.append(f"Input pin '{pin.name}' is not connected")

        return errors

    @property
    def path(self) -> str:
        """
        获取节点路径

        Returns:
            节点的完整路径
        """
        if self.node_graph is None:
            return f"/{self.name}"
        
        # 如果节点图有父路径，则构建完整路径
        parent_path = getattr(self.node_graph, 'path', '')
        if parent_path:
            return f"{parent_path}/{self.name}"
        return f"/{self.name}"

    @property
    def is_dirty(self) -> bool:
        """节点是否需要重新计算"""
        return self._is_dirty

    def to_dict(self) -> dict:
        """
        序列化为字典

        Returns:
            节点数据字典
        """
        result = {
            "id": self.id,
            "type": self.node_type,
            "name": self.name,
            "position": self.position,
            "properties": self.properties.copy(),
            "input_pins": [pin.to_dict() for pin in self.input_pins.values()],
            "output_pins": [pin.to_dict() for pin in self.output_pins.values()]
        }
        
        # Phase 3.5: 序列化实例参数（动态参数）
        if hasattr(self, 'instance_parameters') and self.instance_parameters:
            result["instance_parameters"] = self.instance_parameters.copy()
        
        return result

    @classmethod
    def from_dict(cls, data: dict, node_graph: 'NodeGraph' = None) -> 'Node':
        """
        从字典反序列化

        Args:
            data: 节点数据字典
            node_graph: 所属节点图

        Returns:
            节点对象
        """
        # 创建节点实例
        node = cls(name=data["name"], node_graph=node_graph)
        node.id = data["id"]
        node.position = tuple(data.get("position", (0, 0)))
        
        # 恢复属性
        for key, value in data.get("properties", {}).items():
            node.set_property(key, value)

        # Phase 3.5: 恢复实例参数（动态参数）
        if "instance_parameters" in data:
            node.instance_parameters = data["instance_parameters"].copy()

        # 引脚在 init_pins 中已创建，这里只需要恢复默认值
        for pin_data in data.get("input_pins", []):
            pin = node.get_input_pin(pin_data["name"])
            if pin and "default_value" in pin_data:
                pin.default_value = pin_data["default_value"]

        return node

    def __repr__(self) -> str:
        """字符串表示"""
        return f"{self.__class__.__name__}('{self.name}', path='{self.path}')"

    def __str__(self) -> str:
        """可读字符串表示"""
        return f"{self.display_name} ({self.name})"
