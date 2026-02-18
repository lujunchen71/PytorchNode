"""
节点模块包 - 导入所有节点类型以触发注册
"""

# 导入上下文根节点（优先加载）
from .context.root_nodes import ObjRootNode, VisRootNode, TrainRootNode

# 导入神经网络层节点
from .nn.linear_node import LinearNode
from .nn.activation_nodes import ReLUNode, SigmoidNode, TanhNode

# 导入训练节点
from .training.loss_nodes import CrossEntropyLossNode, MSELossNode
from .training.optimizer_nodes import SGDNode, AdamNode
from .training.save_model_node import SaveModelNode
from .training.load_model_node import LoadModelNode

# 导入数据节点
from .data.dataset_nodes import MNISTNode, CIFAR10Node

# 导入控制流节点
from .control.foreach_nodes import ForEachBeginNode, ForEachDataNode, ForEachEndNode

# 导入子网络节点
from .subnet.subnet_node import SubnetNode
from .subnet.subnet_pins import SubnetInputPinNode, SubnetOutputPinNode

__all__ = [
    # 上下文根节点
    'ObjRootNode',
    'VisRootNode',
    'TrainRootNode',
    # 神经网络层
    'LinearNode',
    'ReLUNode',
    'SigmoidNode',
    'TanhNode',
    # 训练节点
    'CrossEntropyLossNode',
    'MSELossNode',
    'SGDNode',
    'AdamNode',
    'SaveModelNode',
    'LoadModelNode',
    # 数据节点
    'MNISTNode',
    'CIFAR10Node',
    # 控制流节点
    'ForEachBeginNode',
    'ForEachDataNode',
    'ForEachEndNode',
    # 子网络节点
    'SubnetNode',
    'SubnetInputPinNode',
    'SubnetOutputPinNode',
]