"""
根路径容器节点 - 代表 /obj, /vis, /train 三个主要路径

这些节点在系统启动时自动创建，作为整个节点层次结构的根节点。
"""

from typing import Optional, TYPE_CHECKING
from core.base.node import Node, NodeCategory
from core.base.pin import PinType

if TYPE_CHECKING:
    from core.base.node_graph import NodeGraph


class RootNode(Node):
    """根节点基类 - 不可删除的容器节点"""
    
    node_category = NodeCategory.CONTEXT
    
    # 允许的子节点类别（子类覆盖）
    allowed_child_categories = []
    
    def __init__(self, name: str = None, node_graph: 'NodeGraph' = None):
        """
        初始化根节点
        
        Args:
            name: 节点名称
            node_graph: 所属节点图
        """
        super().__init__(name=name, node_graph=node_graph)
    
    def init_pins(self) -> None:
        """根节点通常不需要引脚，但可以有执行流引脚"""
        # 可以添加执行流引脚用于触发子网络
        pass
    
    def init_properties(self) -> None:
        """初始化属性"""
        super().init_properties()
        # 标记为根节点，不可删除
        self.properties['is_root'] = True
        self.properties['deletable'] = False
    
    def execute(self) -> None:
        """根节点不执行计算，仅作为容器"""
        self._is_dirty = False
    
    def can_add_child_type(self, node_type: str) -> bool:
        """
        检查是否可以在此根节点下添加指定类型的节点
        
        Args:
            node_type: 节点类型
            
        Returns:
            是否允许添加
        """
        # 需要从注册表获取节点类别
        from core.base.node_registry import get_registry
        registry = get_registry()
        node_class = registry.get_node_class(node_type)
        
        if node_class is None:
            return False
        
        # 检查节点类别是否在允许列表中
        return node_class.node_category in self.allowed_child_categories


class ObjRootNode(RootNode):
    """
    /obj 根节点 - 对象/神经网络构建路径
    
    用于构建神经网络模型，包含所有NN层节点、子网络等
    """
    
    node_type = "root.obj"
    display_name = "Object Network Root"
    
    # obj 路径下允许的节点类别
    allowed_child_categories = [
        NodeCategory.NN,        # 神经网络层
        NodeCategory.SUBNET,    # 子网络
        NodeCategory.MATH,      # 数学运算
        NodeCategory.TRANSFORM, # 变换
    ]
    
    def __init__(self, name: str = "obj", node_graph: 'NodeGraph' = None):
        """初始化 obj 根节点"""
        super().__init__(name=name, node_graph=node_graph)
        self.properties['description'] = "神经网络对象构建路径"


class VisRootNode(RootNode):
    """
    /vis 根节点 - 可视化路径
    
    用于数据可视化、训练监控、模型分析等
    """
    
    node_type = "root.vis"
    display_name = "Visualization Root"
    
    # vis 路径下允许的节点类别
    allowed_child_categories = [
        NodeCategory.VISUALIZATION,  # 可视化节点
        NodeCategory.DATA,           # 数据处理
    ]
    
    def __init__(self, name: str = "vis", node_graph: 'NodeGraph' = None):
        """初始化 vis 根节点"""
        super().__init__(name=name, node_graph=node_graph)
        self.properties['description'] = "可视化与监控路径"


class TrainRootNode(RootNode):
    """
    /train 根节点 - 训练流程路径
    
    用于定义训练流程，包含损失函数、优化器、检查点等
    """
    
    node_type = "root.train"
    display_name = "Training Pipeline Root"
    
    # train 路径下允许的节点类别
    allowed_child_categories = [
        NodeCategory.TRAINING,  # 训练节点（损失、优化器、检查点）
        NodeCategory.DATA,      # 数据加载
        NodeCategory.LOGIC,     # 逻辑控制
    ]
    
    def __init__(self, name: str = "train", node_graph: 'NodeGraph' = None):
        """初始化 train 根节点"""
        super().__init__(name=name, node_graph=node_graph)
        self.properties['description'] = "训练流程定义路径"


# 注册根节点到注册表
from core.base.node_registry import register_node

register_node(ObjRootNode)
register_node(VisRootNode)
register_node(TrainRootNode)
