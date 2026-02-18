"""
MNIST加载节点测试 (Phase 4 T056)
"""

import pytest
import sys
sys.path.insert(0, '.')

from core.nodes.data.dataset_nodes import MNISTNode


def test_mnist_node_creation():
    """测试MNIST节点创建"""
    node = MNISTNode(name="mnist_test")
    assert node.name == "mnist_test"
    assert node.display_name == "MNIST Dataset"
    assert node.node_type == "MNISTNode"
    # 检查参数
    assert "data_dir" in node.instance_parameters
    assert "train" in node.instance_parameters
    assert "download" in node.instance_parameters
    print("✅ MNIST节点创建测试通过")


def test_mnist_node_pins():
    """测试MNIST节点针脚"""
    node = MNISTNode(name="mnist_test")
    node.init_pins()
    assert "images" in node.output_pins
    assert "labels" in node.output_pins
    print("✅ MNIST节点针脚测试通过")


# 注意：实际数据加载测试需要torchvision和数据集，可能跳过
if __name__ == "__main__":
    pytest.main([__file__, '-v', '-s'])