"""
训练管线 (TrainingPipeline) - 管理训练循环 (Phase 5 T077)

职责：
1. 管理训练步骤（前向、损失、反向、优化）
2. 执行多epoch训练
3. 跟踪损失和指标
4. 保存检查点
5. 支持早停和调度器
"""

from typing import Dict, List, Optional, Callable
import time
import torch
from .executor import Executor
from core.base.node_graph import NodeGraph
from core.base.node import Node
from core.base.pack import TorchPack


class TrainingPipeline:
    """训练管线"""
    
    def __init__(self, graph: NodeGraph, 
                 loss_node_name: str = None,
                 optimizer_node_name: str = None,
                 data_node_name: str = None):
        """
        初始化训练管线
        
        Args:
            graph: 节点图
            loss_node_name: 损失节点名称
            optimizer_node_name: 优化器节点名称
            data_node_name: 数据节点名称
        """
        self.graph = graph
        self.loss_node_name = loss_node_name
        self.optimizer_node_name = optimizer_node_name
        self.data_node_name = data_node_name
        
        self.executor = Executor(graph)
        self.epochs_completed = 0
        self.loss_history = []
        self.metrics_history = []
        
        # 钩子函数
        self.on_epoch_start_callbacks = []
        self.on_epoch_end_callbacks = []
        self.on_batch_end_callbacks = []
    
    def add_epoch_start_callback(self, callback: Callable):
        """添加epoch开始回调"""
        self.on_epoch_start_callbacks.append(callback)
    
    def add_epoch_end_callback(self, callback: Callable):
        """添加epoch结束回调"""
        self.on_epoch_end_callbacks.append(callback)
    
    def run(self, epochs: int = 10, batch_size: int = 32) -> Dict:
        """
        运行训练循环
        
        Args:
            epochs: 训练轮数
            batch_size: 批大小（暂时未使用）
            
        Returns:
            训练结果字典
        """
        for epoch in range(epochs):
            # epoch开始回调
            for cb in self.on_epoch_start_callbacks:
                cb(epoch)
            
            # 执行整个图（一个epoch）
            try:
                outputs = self.executor.execute()
            except Exception as e:
                print(f"训练错误 epoch {epoch}: {e}")
                break
            
            # 提取损失值
            loss = self._extract_loss(outputs)
            if loss is not None:
                self.loss_history.append(loss)
            
            # epoch结束回调
            for cb in self.on_epoch_end_callbacks:
                cb(epoch, loss)
            
            self.epochs_completed += 1
        
        return {
            "epochs": self.epochs_completed,
            "loss_history": self.loss_history,
            "metrics": self.metrics_history
        }
    
    def _extract_loss(self, outputs: Dict[str, TorchPack]) -> Optional[float]:
        """
        从执行输出中提取损失值
        
        Args:
            outputs: Executor的输出
            
        Returns:
            损失值（浮点数）或None
        """
        # 如果有指定的损失节点，查找其输出
        if self.loss_node_name:
            key = f"{self.loss_node_name}.loss"
            if key in outputs:
                return outputs[key].tensor.item()
        
        # 否则查找任何包含"loss"的键
        for key, pack in outputs.items():
            if "loss" in key.lower():
                return pack.tensor.item()
        
        return None
    
    def step(self) -> Dict[str, TorchPack]:
        """
        执行单个训练步骤（一个batch）
        
        Returns:
            步骤输出
        """
        # 使用Executor执行一个步骤（需要图支持batch执行）
        # 暂时简单执行整个图
        outputs = self.executor.execute()
        return outputs
    
    def get_loss_history(self) -> List[float]:
        """获取损失历史"""
        return self.loss_history
    
    def get_metrics(self, metric_name: str) -> List:
        """获取指定指标历史"""
        # 简单实现
        return []
    
    def reset(self) -> None:
        """重置管线状态"""
        self.epochs_completed = 0
        self.loss_history.clear()
        self.metrics_history.clear()
        self.executor = Executor(self.graph)
    
    def save_checkpoint(self, path: str) -> None:
        """保存检查点（暂未实现）"""
        # 需要保存图状态、损失历史等
        pass
    
    def load_checkpoint(self, path: str) -> None:
        """加载检查点（暂未实现）"""
        pass