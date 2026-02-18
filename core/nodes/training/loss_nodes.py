"""
损失节点 (Phase 5 T072)
"""

from core.base.node import Node, NodeCategory
from core.base.pin import PinType
from core.base import register_node
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import torch
    import torch.nn.functional as F
    from core.base.pack import TorchPack


class LossNode(Node):
    """损失节点基类"""
    
    def init_pins(self):
        self.add_input_pin("predictions", PinType.TENSOR, label="Predictions")
        self.add_input_pin("targets", PinType.TENSOR, label="Targets")
        self.add_output_pin("loss", PinType.TENSOR, label="Loss")


@register_node
class CrossEntropyLossNode(LossNode):
    """交叉熵损失节点"""
    
    node_type = "CrossEntropyLossNode"
    node_category = NodeCategory.TRAINING
    display_name = "Cross‑Entropy Loss"
    
    def execute(self, input_packs):
        import torch
        import torch.nn.functional as F
        from core.base.pack import TorchPack
        
        pred_pack = input_packs.get("predictions", [TorchPack(torch.zeros(1, 10))])[0]
        target_pack = input_packs.get("targets", [TorchPack(torch.zeros(1, dtype=torch.long))])[0]
        
        pred = pred_pack.tensor
        target = target_pack.tensor
        
        # 确保 target 是长整型
        if target.dtype != torch.long:
            target = target.long()
        
        loss = F.cross_entropy(pred, target)
        return {"loss": [TorchPack(loss.unsqueeze(0))]}


@register_node
class MSELossNode(LossNode):
    """均方误差损失节点"""
    
    node_type = "MSELossNode"
    node_category = NodeCategory.TRAINING
    display_name = "MSE Loss"
    
    def execute(self, input_packs):
        import torch
        import torch.nn.functional as F
        from core.base.pack import TorchPack
        
        pred_pack = input_packs.get("predictions", [TorchPack(torch.zeros(1, 10))])[0]
        target_pack = input_packs.get("targets", [TorchPack(torch.zeros(1, 10))])[0]
        
        pred = pred_pack.tensor
        target = target_pack.tensor
        
        loss = F.mse_loss(pred, target)
        return {"loss": [TorchPack(loss.unsqueeze(0))]}