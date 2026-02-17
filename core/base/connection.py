"""
连接（Connection）类 - 节点之间的数据连接

职责:
- 连接验证
- 数据传递
- 状态管理
"""

from typing import Any, TYPE_CHECKING
import uuid

if TYPE_CHECKING:
    from .pin import Pin


class Connection:
    """连接类 - 表示两个引脚之间的连接"""

    def __init__(self, source_pin: 'Pin', target_pin: 'Pin'):
        """
        初始化连接

        Args:
            source_pin: 源引脚（输出）
            target_pin: 目标引脚（输入）

        Raises:
            ValueError: 如果连接无效
        """
        # 验证连接有效性
        if not source_pin.is_output:
            raise ValueError("Source pin must be an output pin")
        
        if not target_pin.is_input:
            raise ValueError("Target pin must be an input pin")

        if not source_pin.can_connect_to(target_pin):
            raise ValueError(
                f"Cannot connect {source_pin.full_path} to {target_pin.full_path}"
            )

        self.id = str(uuid.uuid4())
        self.source_pin = source_pin
        self.target_pin = target_pin

        # 添加连接到引脚
        self.source_pin.add_connection(self)
        self.target_pin.add_connection(self)

        # 数据缓存
        self._cached_value: Any = None
        self._cache_valid = False

    @property
    def source_node(self):
        """源节点"""
        return self.source_pin.node

    @property
    def target_node(self):
        """目标节点"""
        return self.target_pin.node

    def get_value(self) -> Any:
        """
        获取连接传递的值

        Returns:
            从源引脚传递的值
        """
        # 简单实现：直接从源引脚获取值
        # 在更复杂的实现中，可以在这里添加缓存逻辑
        return self.source_pin.get_value()

    def disconnect(self) -> None:
        """断开连接"""
        # 从引脚移除连接
        self.source_pin.remove_connection(self)
        self.target_pin.remove_connection(self)

    def is_valid(self) -> bool:
        """
        检查连接是否有效

        Returns:
            连接是否有效
        """
        # 检查引脚是否仍然存在
        if self.source_pin is None or self.target_pin is None:
            return False

        # 检查节点是否仍然存在
        if self.source_node is None or self.target_node is None:
            return False

        # 检查类型兼容性
        return self.source_pin.can_connect_to(self.target_pin)

    def to_dict(self) -> dict:
        """
        序列化为字典

        Returns:
            连接数据字典
        """
        return {
            "id": self.id,
            "source_node": self.source_node.path,
            "source_pin": self.source_pin.name,
            "target_node": self.target_node.path,
            "target_pin": self.target_pin.name
        }

    @classmethod
    def from_dict(cls, data: dict, node_graph) -> 'Connection':
        """
        从字典反序列化

        Args:
            data: 连接数据字典
            node_graph: 节点图管理器

        Returns:
            连接对象

        Raises:
            ValueError: 如果引用的节点或引脚不存在
        """
        # 查找节点
        source_node = node_graph.get_node(data["source_node"])
        target_node = node_graph.get_node(data["target_node"])

        if source_node is None:
            raise ValueError(f"Source node not found: {data['source_node']}")
        if target_node is None:
            raise ValueError(f"Target node not found: {data['target_node']}")

        # 查找引脚
        source_pin = source_node.get_output_pin(data["source_pin"])
        target_pin = target_node.get_input_pin(data["target_pin"])

        if source_pin is None:
            raise ValueError(
                f"Source pin not found: {data['source_node']}.{data['source_pin']}"
            )
        if target_pin is None:
            raise ValueError(
                f"Target pin not found: {data['target_node']}.{data['target_pin']}"
            )

        # 创建连接
        connection = cls(source_pin, target_pin)
        connection.id = data.get("id", connection.id)
        
        return connection

    def __repr__(self) -> str:
        """字符串表示"""
        return (
            f"Connection({self.source_pin.full_path} -> "
            f"{self.target_pin.full_path})"
        )

    def __eq__(self, other) -> bool:
        """相等性比较"""
        if not isinstance(other, Connection):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        """哈希值"""
        return hash(self.id)
