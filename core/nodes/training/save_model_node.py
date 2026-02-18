"""
SaveModel节点 (Phase 5 T074)
"""

import os
import torch
from pathlib import Path
from typing import Optional, Dict, List
from core.base.node import Node, NodeCategory
from core.base.pin import PinType
from core.base import register_node
from core.base.pack import TorchPack


@register_node
class SaveModelNode(Node):
    """保存模型检查点节点"""
    
    node_type = "SaveModelNode"
    node_category = NodeCategory.TRAINING
    display_name = "Save Model"
    
    def init_pins(self):
        """初始化引脚"""
        self.add_input_pin("model", PinType.TENSOR, label="Model Parameters")
        self.add_input_pin("loss", PinType.TENSOR, label="Loss (可选)", optional=True)
        self.add_output_pin("saved_path", PinType.STRING, label="Saved Path")
    
    def init_properties(self):
        """初始化属性"""
        self.properties = {
            "model_name": "model",
            "max_saves": 5,
            "save_best": True,
            "checkpoint_dir": "./checkpoints",
        }
    
    def execute(self, input_packs: Dict[str, List[TorchPack]]) -> Dict[str, List[TorchPack]]:
        """执行模型保存
        
        Args:
            input_packs: 输入包字典，键为引脚名，值为TorchPack列表
        
        Returns:
            输出包字典
        """
        # 获取模型参数包
        model_packs = input_packs.get("model", [])
        if not model_packs:
            # 无输入，返回空路径
            return {"saved_path": [TorchPack("")]}
        model_pack = model_packs[0]
        model_params = model_pack.tensor  # 应为状态字典
        
        # 获取损失（如果存在）
        loss_packs = input_packs.get("loss", [])
        current_loss = None
        if loss_packs:
            current_loss = loss_packs[0].tensor.item()
        
        # 读取属性
        model_name = self.get_property("model_name")
        max_saves = int(self.get_property("max_saves"))
        save_best = self.get_property("save_best")
        checkpoint_dir = Path(self.get_property("checkpoint_dir"))
        
        # 创建目录
        checkpoint_dir.mkdir(parents=True, exist_ok=True)
        
        # 确定文件名
        if save_best and current_loss is not None:
            # 检查最佳损失
            best_loss_path = checkpoint_dir / f"{model_name}_best.pt"
            if best_loss_path.exists():
                try:
                    best_state = torch.load(best_loss_path, map_location='cpu')
                    best_loss = best_state.get('loss', float('inf'))
                except:
                    best_loss = float('inf')
            else:
                best_loss = float('inf')
            
            if current_loss < best_loss:
                # 保存最佳模型
                torch.save({
                    'model_state_dict': model_params,
                    'loss': current_loss,
                    'epoch': self._get_epoch()
                }, best_loss_path)
                saved_path = str(best_loss_path)
            else:
                # 不保存，返回空路径
                saved_path = ""
        else:
            # 常规保存，按时间戳命名
            import time
            timestamp = int(time.time())
            filename = checkpoint_dir / f"{model_name}_{timestamp}.pt"
            torch.save({
                'model_state_dict': model_params,
                'loss': current_loss if current_loss is not None else 0.0,
                'epoch': self._get_epoch()
            }, filename)
            saved_path = str(filename)
        
        # 清理旧检查点
        self._cleanup_old_checkpoints(checkpoint_dir, model_name, max_saves)
        
        # 返回保存的路径
        return {"saved_path": [TorchPack(saved_path)]}
    
    def _get_epoch(self) -> int:
        """获取当前训练轮次（模拟）"""
        # 可以从TrainingPipeline获取，此处返回默认值
        return 0
    
    def _cleanup_old_checkpoints(self, checkpoint_dir: Path, model_name: str, max_saves: int):
        """删除多余的检查点文件"""
        pattern = f"{model_name}_*.pt"
        files = list(checkpoint_dir.glob(pattern))
        files.sort(key=os.path.getmtime)  # 按修改时间排序
        
        if len(files) > max_saves:
            for f in files[:-max_saves]:  # 保留最新的max_saves个文件
                try:
                    f.unlink()
                except:
                    pass