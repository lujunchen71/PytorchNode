"""
优化器节点 (Phase 5 T073)
"""

from core.base.node import Node, NodeCategory
from core.base.pin import PinType
from core.base import register_node
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import torch
    from core.base.pack import TorchPack


class OptimizerNode(Node):
    """优化器节点基类"""
    
    def init_pins(self):
        self.add_input_pin("parameters", PinType.TENSOR, label="Parameters")
        self.add_input_pin("gradients", PinType.TENSOR, label="Gradients")
        self.add_output_pin("updated_parameters", PinType.TENSOR, label="Updated Parameters")
    
    def create_optimizer(self, parameters):
        """子类应重写此方法以创建具体的优化器"""
        raise NotImplementedError


@register_node
class SGDNode(OptimizerNode):
    """随机梯度下降节点"""
    
    node_type = "SGDNode"
    node_category = NodeCategory.TRAINING
    display_name = "SGD Optimizer"
    
    def __init__(self, name: str, **kwargs):
        super().__init__(name, **kwargs)
        self.instance_parameters = {
            "lr": {"current_value": 0.01},
            "momentum": {"current_value": 0.0}
        }
    
    def create_optimizer(self, parameters):
        import torch
        lr = self.instance_parameters["lr"]["current_value"]
        momentum = self.instance_parameters["momentum"]["current_value"]
        return torch.optim.SGD(parameters, lr=lr, momentum=momentum)
    
    def execute(self, input_packs):
        import torch
        from core.base.pack import TorchPack
        
        param_pack = input_packs.get("parameters", [TorchPack(torch.zeros(1, 10))])[0]
        grad_pack = input_packs.get("gradients", [TorchPack(torch.zeros(1, 10))])[0]
        
        params = param_pack.tensor
        grads = grad_pack.tensor
        
        # 模拟 SGD 更新: param = param - lr * grad
        lr = self.instance_parameters["lr"]["current_value"]
        updated = params - lr * grads
        
        return {"updated_parameters": [TorchPack(updated)]}


@register_node
class AdamNode(OptimizerNode):
    """Adam 优化器节点"""
    
    node_type = "AdamNode"
    node_category = NodeCategory.TRAINING
    display_name = "Adam Optimizer"
    
    def __init__(self, name: str, **kwargs):
        super().__init__(name, **kwargs)
        self.instance_parameters = {
            "lr": {"current_value": 0.001},
            "beta1": {"current_value": 0.9},
            "beta2": {"current_value": 0.999}
        }
    
    def create_optimizer(self, parameters):
        import torch
        lr = self.instance_parameters["lr"]["current_value"]
        beta1 = self.instance_parameters["beta1"]["current_value"]
        beta2 = self.instance_parameters["beta2"]["current_value"]
        return torch.optim.Adam(parameters, lr=lr, betas=(beta1, beta2))
    
    def execute(self, input_packs):
        import torch
        from core.base.pack import TorchPack
        
        # 简化实现：仅返回参数减去梯度乘以学习率
        param_pack = input_packs.get("parameters", [TorchPack(torch.zeros(1, 10))])[0]
        grad_pack = input_packs.get("gradients", [TorchPack(torch.zeros(1, 10))])[0]
        
        params = param_pack.tensor
        grads = grad_pack.tensor
        lr = self.instance_parameters["lr"]["current_value"]
        updated = params - lr * grads
        
        return {"updated_parameters": [TorchPack(updated)]}