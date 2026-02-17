"""
测试节点核心功能：创建、删除、连接等
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import torch
from core.base import (
    Node, NodeGraph, NodeRegistry, NodeFactory,
    Pin, PinType, Connection, get_registry
)

# 导入节点以触发注册
from core.nodes.nn import LinearNode, ReLUNode, SigmoidNode


def test_node_creation():
    """测试节点创建"""
    print("\n" + "=" * 60)
    print("测试 1: 节点创建")
    print("=" * 60)
    
    # 创建节点图
    graph = NodeGraph("test_graph")
    
    # 使用工厂创建节点
    linear_node = NodeFactory.create_node("Linear", name="fc1", node_graph=graph)
    relu_node = NodeFactory.create_node("ReLU", name="relu1", node_graph=graph)
    
    print(f"✓ 创建 Linear 节点: {linear_node}")
    print(f"  - 输入引脚: {list(linear_node.input_pins.keys())}")
    print(f"  - 输出引脚: {list(linear_node.output_pins.keys())}")
    print(f"  - 属性: {linear_node.properties}")
    
    print(f"\n✓ 创建 ReLU 节点: {relu_node}")
    print(f"  - 输入引脚: {list(relu_node.input_pins.keys())}")
    print(f"  - 输出引脚: {list(relu_node.output_pins.keys())}")
    
    return graph, linear_node, relu_node


def test_node_connection():
    """测试节点连接"""
    print("\n" + "=" * 60)
    print("测试 2: 节点连接")
    print("=" * 60)
    
    # 创建节点图和节点
    graph = NodeGraph("test_graph")
    linear_node = NodeFactory.create_node("Linear", name="fc1", node_graph=graph)
    relu_node = NodeFactory.create_node("ReLU", name="relu1", node_graph=graph)
    
    # 添加节点到图
    graph.add_node(linear_node)
    graph.add_node(relu_node)
    
    print(f"✓ 添加节点到图: {graph.nodes.keys()}")
    
    # 创建连接
    source_pin = linear_node.get_output_pin("output")
    target_pin = relu_node.get_input_pin("input")
    
    print(f"\n连接: {source_pin.full_path} -> {target_pin.full_path}")
    
    # 检查是否可以连接
    can_connect = source_pin.can_connect_to(target_pin)
    print(f"  - 可以连接: {can_connect}")
    
    if can_connect:
        connection = Connection(source_pin, target_pin)
        graph.add_connection(connection)
        print(f"✓ 创建连接: {connection}")
        print(f"  - Linear.output 连接数: {len(source_pin.connections)}")
        print(f"  - ReLU.input 连接数: {len(target_pin.connections)}")
        print(f"  - ReLU.input 已连接: {target_pin.is_connected}")
    
    return graph


def test_node_execution():
    """测试节点执行"""
    print("\n" + "=" * 60)
    print("测试 3: 节点执行")
    print("=" * 60)
    
    # 创建节点图和节点
    graph = NodeGraph("test_graph")
    
    # 创建 Linear -> ReLU 管道
    linear_node = NodeFactory.create_node(
        "Linear",
        name="fc1",
        node_graph=graph,
        in_features=10,
        out_features=5
    )
    relu_node = NodeFactory.create_node("ReLU", name="relu1", node_graph=graph)
    
    graph.add_node(linear_node)
    graph.add_node(relu_node)
    
    # 连接节点
    connection = Connection(
        linear_node.get_output_pin("output"),
        relu_node.get_input_pin("input")
    )
    graph.add_connection(connection)
    
    print(f"✓ 创建管道: fc1(10->5) -> relu1")
    
    # 执行 Linear 节点
    print(f"\n执行 Linear 节点...")
    linear_node.execute()
    output_linear = linear_node.get_output_value("output")
    print(f"  - Linear 输出形状: {output_linear.shape}")
    print(f"  - Linear 输出样本: {output_linear[0, :3]}")
    
    # 执行 ReLU 节点
    print(f"\n执行 ReLU 节点...")
    relu_node.execute()
    output_relu = relu_node.get_output_value("output")
    print(f"  - ReLU 输出形状: {output_relu.shape}")
    print(f"  - ReLU 输出样本: {output_relu[0, :3]}")
    print(f"  - 所有值 >= 0: {torch.all(output_relu >= 0).item()}")
    
    return graph


def test_topological_sort():
    """测试拓扑排序"""
    print("\n" + "=" * 60)
    print("测试 4: 拓扑排序")
    print("=" * 60)
    
    # 创建复杂的节点图
    graph = NodeGraph("test_graph")
    
    # 创建节点: input -> fc1 -> relu1 -> fc2 -> sigmoid -> output
    nodes = {}
    node_configs = [
        ("Linear", "fc1", {"in_features": 10, "out_features": 20}),
        ("ReLU", "relu1", {}),
        ("Linear", "fc2", {"in_features": 20, "out_features": 5}),
        ("Sigmoid", "sigmoid1", {}),
    ]
    
    for node_type, name, props in node_configs:
        node = NodeFactory.create_node(node_type, name=name, node_graph=graph, **props)
        graph.add_node(node)
        nodes[name] = node
    
    # 创建连接链
    connections = [
        ("fc1", "output", "relu1", "input"),
        ("relu1", "output", "fc2", "input"),
        ("fc2", "output", "sigmoid1", "input"),
    ]
    
    for src_node, src_pin, tgt_node, tgt_pin in connections:
        conn = Connection(
            nodes[src_node].get_output_pin(src_pin),
            nodes[tgt_node].get_input_pin(tgt_pin)
        )
        graph.add_connection(conn)
    
    print(f"✓ 创建节点链:")
    for name in ["fc1", "relu1", "fc2", "sigmoid1"]:
        print(f"  - {name}")
    
    # 拓扑排序
    print(f"\n执行拓扑排序...")
    sorted_nodes = graph.topological_sort()
    print(f"✓ 排序结果:")
    for i, node in enumerate(sorted_nodes, 1):
        print(f"  {i}. {node.name} ({node.node_type})")
    
    # 验证顺序
    node_order = {node.name: i for i, node in enumerate(sorted_nodes)}
    assert node_order["fc1"] < node_order["relu1"]
    assert node_order["relu1"] < node_order["fc2"]
    assert node_order["fc2"] < node_order["sigmoid1"]
    print(f"\n✓ 顺序验证通过")
    
    return graph


def test_node_deletion():
    """测试节点删除"""
    print("\n" + "=" * 60)
    print("测试 5: 节点删除")
    print("=" * 60)
    
    # 创建节点图
    graph = NodeGraph("test_graph")
    
    # 创建节点
    fc1 = NodeFactory.create_node("Linear", name="fc1", node_graph=graph)
    relu = NodeFactory.create_node("ReLU", name="relu", node_graph=graph)
    fc2 = NodeFactory.create_node("Linear", name="fc2", node_graph=graph)
    
    graph.add_node(fc1)
    graph.add_node(relu)
    graph.add_node(fc2)
    
    # 创建连接
    conn1 = Connection(fc1.get_output_pin("output"), relu.get_input_pin("input"))
    conn2 = Connection(relu.get_output_pin("output"), fc2.get_input_pin("input"))
    graph.add_connection(conn1)
    graph.add_connection(conn2)
    
    print(f"✓ 初始状态:")
    print(f"  - 节点数: {len(graph.nodes)}")
    print(f"  - 连接数: {len(graph.connections)}")
    
    # 删除中间节点
    print(f"\n删除中间节点 'relu'...")
    graph.remove_node(relu)
    
    print(f"✓ 删除后:")
    print(f"  - 节点数: {len(graph.nodes)}")
    print(f"  - 连接数: {len(graph.connections)}")
    print(f"  - 剩余节点: {list(graph.nodes.keys())}")
    
    # 验证连接被正确清理
    assert "relu" not in graph.nodes
    assert len(graph.connections) == 0  # 所有相关连接都应被删除
    print(f"\n✓ 删除验证通过")
    
    return graph


def test_node_registry():
    """测试节点注册表"""
    print("\n" + "=" * 60)
    print("测试 6: 节点注册表")
    print("=" * 60)
    
    registry = get_registry()
    
    # 获取所有注册的节点类型
    node_types = registry.get_all_node_types()
    print(f"✓ 已注册的节点类型数: {len(node_types)}")
    
    # 显示节点分类
    categories = registry.get_categories()
    print(f"\n✓ 节点分类:")
    for category in categories:
        nodes_in_cat = registry.get_nodes_in_category(category)
        print(f"  - {category}: {nodes_in_cat}")
    
    # 搜索节点
    print(f"\n✓ 搜索测试:")
    search_results = registry.search_nodes("relu")
    print(f"  - 搜索 'relu': {search_results}")
    
    search_results = registry.search_nodes("linear")
    print(f"  - 搜索 'linear': {search_results}")
    
    return registry


def run_all_tests():
    """运行所有测试"""
    print("\n" + "=" * 80)
    print(" " * 20 + "节点核心功能测试")
    print("=" * 80)
    
    try:
        # 运行测试
        test_node_creation()
        test_node_connection()
        test_node_execution()
        test_topological_sort()
        test_node_deletion()
        test_node_registry()
        
        # 总结
        print("\n" + "=" * 80)
        print(" " * 30 + "所有测试通过! ✓")
        print("=" * 80)
        return True
        
    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
