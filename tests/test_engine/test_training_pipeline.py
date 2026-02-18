"""
TrainingPipeline测试 (Phase 5 T067)
"""

import pytest
import sys
sys.path.insert(0, '.')

from core.base.node_graph import NodeGraph
from core.base.node import Node
from core.base.pin import InputPin, OutputPin
from core.base.pack import TorchPack
from core.engine.training_pipeline import TrainingPipeline
import torch


class MockTrainingNode(Node):
    """模拟训练节点用于测试"""
    def __init__(self, name):
        super().__init__(name=name)
        self.epochs_completed = 0
    
    def init_pins(self):
        self.add_input_pin("model", data_type="any")
        self.add_input_pin("data", data_type="any")
        self.add_output_pin("trained_model", data_type="any")
        self.add_output_pin("loss", data_type="any")
    
    def execute(self, input_packs):
        # 模拟训练逻辑
        self.epochs_completed += 1
        model_pack = input_packs.get("model", [TorchPack(torch.tensor([0.]))])[0]
        return {
            "trained_model": [model_pack],
            "loss": [TorchPack(torch.tensor([0.1]))]
        }


def test_training_pipeline_creation():
    """测试TrainingPipeline实例化"""
    graph = NodeGraph()
    pipeline = TrainingPipeline(graph)
    assert pipeline is not None
    assert pipeline.graph == graph
    assert pipeline.epochs_completed == 0
    assert len(pipeline.loss_history) == 0


def test_add_training_step():
    """测试添加训练步骤"""
    graph = NodeGraph()
    node = MockTrainingNode("Trainer")
    graph.add_node(node)
    
    pipeline = TrainingPipeline(graph, loss_node_name="Trainer")
    # 添加回调
    epoch_start_called = []
    epoch_end_called = []
    
    def on_start(epoch):
        epoch_start_called.append(epoch)
    
    def on_end(epoch, loss):
        epoch_end_called.append((epoch, loss))
    
    pipeline.add_epoch_start_callback(on_start)
    pipeline.add_epoch_end_callback(on_end)
    
    # 运行1个epoch
    result = pipeline.run(epochs=1)
    
    assert pipeline.epochs_completed == 1
    assert len(pipeline.loss_history) == 1
    assert pipeline.loss_history[0] == 0.1  # 来自MockTrainingNode
    assert epoch_start_called == [0]
    assert len(epoch_end_called) == 1
    assert epoch_end_called[0][0] == 0
    assert epoch_end_called[0][1] == 0.1


def test_execute_single_epoch():
    """测试执行单个训练周期"""
    graph = NodeGraph()
    node = MockTrainingNode("Trainer")
    graph.add_node(node)
    
    pipeline = TrainingPipeline(graph, loss_node_name="Trainer")
    result = pipeline.run(epochs=1)
    
    assert result["epochs"] == 1
    assert result["loss_history"] == [0.1]
    assert node.epochs_completed == 1


def test_loss_tracking():
    """测试损失跟踪"""
    graph = NodeGraph()
    node = MockTrainingNode("Trainer")
    graph.add_node(node)
    
    pipeline = TrainingPipeline(graph, loss_node_name="Trainer")
    pipeline.run(epochs=3)
    
    assert len(pipeline.loss_history) == 3
    assert pipeline.loss_history == [0.1, 0.1, 0.1]
    assert pipeline.get_loss_history() == [0.1, 0.1, 0.1]


def test_early_stopping():
    """测试早停机制（简单模拟）"""
    graph = NodeGraph()
    node = MockTrainingNode("Trainer")
    graph.add_node(node)
    
    pipeline = TrainingPipeline(graph, loss_node_name="Trainer")
    
    # 模拟早停：如果损失没有改善则停止
    stop_after = []
    def stop_callback(epoch, loss):
        if epoch >= 2:
            # 抛出一个特殊异常来停止？这里仅作记录
            stop_after.append(epoch)
    
    pipeline.add_epoch_end_callback(stop_callback)
    result = pipeline.run(epochs=5)
    
    # 由于没有实现真正的早停，所有epoch都会执行
    assert pipeline.epochs_completed == 5


def test_reset():
    """测试重置管线状态"""
    graph = NodeGraph()
    node = MockTrainingNode("Trainer")
    graph.add_node(node)
    
    pipeline = TrainingPipeline(graph, loss_node_name="Trainer")
    pipeline.run(epochs=2)
    
    assert pipeline.epochs_completed == 2
    assert len(pipeline.loss_history) == 2
    
    pipeline.reset()
    
    assert pipeline.epochs_completed == 0
    assert len(pipeline.loss_history) == 0


if __name__ == "__main__":
    pytest.main([__file__, '-v', '-s'])