"""
LoadModel节点 (Phase 5 T075)
"""

import torch
from pathlib import Path
from typing import Dict, List, Optional
from core.base.node import Node, NodeCategory
from core.base.pin import PinType
from core.base import register_node
from core.base.pack import TorchPack


@register_node
class LoadModelNode(Node):
    """加载模型检查点节点"""
    
    node_type = "LoadModelNode"
    node_category = NodeCategory.TRAINING
    display_name = "Load Model"
    
    def init_pins(self):
        """初始化引脚"""
        self.add_input_pin("path", PinType.STRING, label="Checkpoint Path", optional=True)
        self.add_output_pin("model", PinType.TENSOR, label="Model Parameters")
        self.add_output_pin("loss", PinType.TENSOR, label="Loss (可选)", optional=True)
        self.add_output_pin("epoch", PinType.INT, label="Epoch (可选)", optional=True)
    
    def init_properties(self):
        """初始化属性"""
        self.properties = {
            "checkpoint_path": "",
            "load_best": False,
            "model_name": "model",
        }
    
    def execute(self, input_packs: Dict[str, List[TorchPack]]) -> Dict[str, List[TorchPack]]:
        """执行模型加载
        
        Args:
            input_packs: 输入包字典，键为引脚名，值为TorchPack列表
        
        Returns:
            输出包字典
        """
        # 确定检查点路径
        path_packs = input_packs.get("path", [])
        if path_packs:
            checkpoint_path = path_packs[0].tensor  # 字符串包
        else:
            checkpoint_path = self.get_property("checkpoint_path")
        
        load_best = self.get_property("load_best")
        model_name = self.get_property("model_name")
        
        # 如果load_best为True，查找最佳模型
        if load_best:
            checkpoint_dir = Path(checkpoint_path).parent if checkpoint_path else Path("./checkpoints")
            best_path = checkpoint_dir / f"{model_name}_best.pt"
            if best_path.exists():
                checkpoint_path = str(best_path)
            else:
                # 没有最佳模型，返回空
                return {
                    "model": [TorchPack(torch.zeros(0))],
                    "loss": [TorchPack(torch.tensor(0.0))],
                    "epoch": [TorchPack(torch.tensor(0))]
                }
        
        # 加载检查点
        if not checkpoint_path:
            # 无路径，返回空
            return {
                "model": [TorchPack(torch.zeros(0))],
                "loss": [TorchPack(torch.tensor(0.0))],
                "epoch": [TorchPack(torch.tensor(0))]
            }
        
        try:
            checkpoint = torch.load(checkpoint_path, map_location='cpu')
        except Exception as e:
            # 加载失败，返回空
            print(f"LoadModelNode: 加载失败 {e}")
            return {
                "model": [TorchPack(torch.zeros(0))],
                "loss": [TorchPack(torch.tensor(0.0))],
                "epoch": [TorchPack(torch.tensor(0))]
            }
        
        # 提取数据
        model_state_dict = checkpoint.get('model_state_dict', {})
        loss = checkpoint.get('loss', 0.0)
        epoch = checkpoint.get('epoch', 0)
        
        # 转换为张量（状态字典可能不是张量，我们将其包装为字典包？）
        # 暂时将状态字典作为张量返回（占位）
        model_tensor = torch.tensor(list(model_state_dict.values())[0]) if model_state_dict else torch.zeros(0)
        
        return {
            "model": [TorchPack(model_tensor)],
            "loss": [TorchPack(torch.tensor(loss))],
            "epoch": [TorchPack(torch.tensor(epoch))]
        }