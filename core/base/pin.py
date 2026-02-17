"""
引脚（Pin）类 - 节点的输入输出端口

职责:
- 数据类型检查
- 连接管理
- 形状推导
- 数据传递
"""

from typing import Optional, Any, List, TYPE_CHECKING
from enum import Enum

if TYPE_CHECKING:
    from .node import Node
    from .connection import Connection


class PinDirection(Enum):
    """引脚方向"""
    INPUT = "input"
    OUTPUT = "output"


class PinType(Enum):
    """引脚数据类型"""
    EXEC = "exec"  # 执行流
    TENSOR = "tensor"  # 张量
    INT = "int"  # 整数
    FLOAT = "float"  # 浮点数
    STRING = "string"  # 字符串
    BOOL = "bool"  # 布尔值
    ANY = "any"  # 任意类型
    DATASET = "dataset"  # 数据集
    OPTIMIZER = "optimizer"  # 优化器
    LOSS = "loss"  # 损失函数


class Pin:
    """引脚类 - 表示节点的输入/输出端口"""

    def __init__(
        self,
        node: 'Node',
        name: str,
        direction: PinDirection,
        pin_type: PinType,
        default_value: Any = None,
        is_list: bool = False,
        label: str = None
    ):
        """
        初始化引脚

        Args:
            node: 所属节点
            name: 引脚名称
            direction: 引脚方向 (INPUT/OUTPUT)
            pin_type: 数据类型
            default_value: 默认值
            is_list: 是否为列表类型（支持多个输入）
            label: 显示标签（可选）
        """
        self.node = node
        self.name = name
        self.direction = direction
        self.pin_type = pin_type
        self.default_value = default_value
        self.is_list = is_list
        self.label = label or name

        # 连接管理
        self.connections: List['Connection'] = []

        # 缓存的数据值
        self._cached_value: Any = None
        self._value_dirty = True

    @property
    def is_input(self) -> bool:
        """是否为输入引脚"""
        return self.direction == PinDirection.INPUT

    @property
    def is_output(self) -> bool:
        """是否为输出引脚"""
        return self.direction == PinDirection.OUTPUT

    @property
    def is_connected(self) -> bool:
        """是否有连接"""
        return len(self.connections) > 0

    @property
    def full_path(self) -> str:
        """获取完整路径"""
        return f"{self.node.path}.{self.name}"

    def can_connect_to(self, other_pin: 'Pin') -> bool:
        """
        检查是否可以连接到另一个引脚

        Args:
            other_pin: 目标引脚

        Returns:
            是否可以连接
        """
        # 不能连接到自己
        if other_pin is self:
            return False

        # 不能连接到同一节点的其他引脚
        if other_pin.node is self.node:
            return False

        # 必须是不同方向
        if other_pin.direction == self.direction:
            return False

        # 类型兼容性检查
        if not self._is_type_compatible(other_pin):
            return False

        # 输入引脚已有连接且不支持列表
        if self.is_input and not self.is_list and self.is_connected:
            return False

        if other_pin.is_input and not other_pin.is_list and other_pin.is_connected:
            return False

        return True

    def _is_type_compatible(self, other_pin: 'Pin') -> bool:
        """
        检查类型兼容性

        Args:
            other_pin: 目标引脚

        Returns:
            是否类型兼容
        """
        # ANY类型兼容所有类型
        if self.pin_type == PinType.ANY or other_pin.pin_type == PinType.ANY:
            return True

        # 相同类型兼容
        if self.pin_type == other_pin.pin_type:
            return True

        # EXEC类型只能与EXEC连接
        if self.pin_type == PinType.EXEC or other_pin.pin_type == PinType.EXEC:
            return False

        # 数值类型的隐式转换
        numeric_types = {PinType.INT, PinType.FLOAT}
        if self.pin_type in numeric_types and other_pin.pin_type in numeric_types:
            return True

        return False

    def add_connection(self, connection: 'Connection') -> None:
        """
        添加连接

        Args:
            connection: 连接对象
        """
        if connection not in self.connections:
            self.connections.append(connection)
            self.mark_dirty()

    def remove_connection(self, connection: 'Connection') -> None:
        """
        移除连接

        Args:
            connection: 连接对象
        """
        if connection in self.connections:
            self.connections.remove(connection)
            self.mark_dirty()

    def disconnect_all(self) -> None:
        """断开所有连接"""
        # 复制列表以避免迭代时修改
        connections_copy = self.connections.copy()
        for conn in connections_copy:
            conn.disconnect()

    def mark_dirty(self) -> None:
        """标记数据需要重新计算"""
        self._value_dirty = True
        
        # 如果是输出引脚，传播dirty标记到下游
        if self.is_output:
            for conn in self.connections:
                conn.target_pin.mark_dirty()

    def get_value(self) -> Any:
        """
        获取引脚当前值

        Returns:
            引脚的值
        """
        if self.is_output:
            # 输出引脚从节点获取计算结果
            return self.node.get_output_value(self.name)
        else:
            # 输入引脚
            if self.is_connected:
                if self.is_list:
                    # 列表类型：收集所有连接的值
                    return [conn.get_value() for conn in self.connections]
                else:
                    # 单一连接
                    return self.connections[0].get_value()
            else:
                # 无连接时返回默认值
                return self.default_value

    def set_value(self, value: Any) -> None:
        """
        设置引脚值（仅用于未连接的输入引脚）

        Args:
            value: 要设置的值
        """
        if self.is_output:
            raise ValueError("Cannot set value on output pin")
        
        if self.is_connected:
            raise ValueError("Cannot set value on connected pin")

        self.default_value = value
        self.mark_dirty()

    def to_dict(self) -> dict:
        """
        序列化为字典

        Returns:
            引脚数据字典
        """
        return {
            "name": self.name,
            "direction": self.direction.value,
            "type": self.pin_type.value,
            "default_value": self.default_value,
            "is_list": self.is_list,
            "label": self.label
        }

    @classmethod
    def from_dict(cls, data: dict, node: 'Node') -> 'Pin':
        """
        从字典反序列化

        Args:
            data: 引脚数据字典
            node: 所属节点

        Returns:
            引脚对象
        """
        return cls(
            node=node,
            name=data["name"],
            direction=PinDirection(data["direction"]),
            pin_type=PinType(data["type"]),
            default_value=data.get("default_value"),
            is_list=data.get("is_list", False),
            label=data.get("label")
        )

    def __repr__(self) -> str:
        """字符串表示"""
        return (
            f"Pin('{self.name}', {self.direction.value}, "
            f"{self.pin_type.value}, node='{self.node.name}')"
        )
