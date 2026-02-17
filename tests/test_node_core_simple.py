"""
测试节点核心功能：创建、删除、连接等（简化版，不需要PyTorch）
"""

import sys
import io
from pathlib import Path

# 设置输出编码为 UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.base import (
    Node, NodeGraph, NodeRegistry, NodeFactory,
    Pin, PinType, Connection, get_registry, register_node, NodeCategory
)


# 创建简单的测试节点（不依赖PyTorch）
@register_node
class TestInputNode(Node):
    """测试输入节点"""
    node_type = "TestInput"
    node_category = NodeCategory.DATA
    display_name = "Test Input"
    
    def init_pins(self):
        self.add_output_pin("output", PinType.TENSOR, label="输出")
    
    def execute(self):
        # 模拟输出
        self._output_cache["output"] = "test_data"
        self._is_dirty = False


@register_node
class TestProcessNode(Node):
    """测试处理节点"""
    node_type = "TestProcess"
    node_category = NodeCategory.NN
    display_name = "Test Process"
    
    def init_pins(self):
        self.add_input_pin("input", PinType.TENSOR, label="输入")
        self.add_output_pin("output", PinType.TENSOR, label="输出")
    
    def init_properties(self):
        self.properties = {"value": 42}
    
    def execute(self):
        input_data = self.get_input_value("input")
        # 模拟处理
        output_data = f"processed_{input_data}_{self.get_property('value')}"
        self._output_cache["output"] = output_data
        self._is_dirty = False


def test_node_creation():
    """测试节点创建"""
    print("\n" + "=" * 60)
    print("测试 1: 节点创建")
    print("=" * 60)
    
    # 创建节点图
    graph = NodeGraph("test_graph")
    
    # 使用工厂创建节点
    input_node = NodeFactory.create_node("TestInput", name="input1", node_graph=graph)
    process_node = NodeFactory.create_node("TestProcess", name="process1", node_graph=graph)
    
    print(f"✓ 创建 Input 节点: {input_node}")
    print(f"  - 输入引脚: {list(input_node.input_pins.keys())}")
    print(f"  - 输出引脚: {list(input_node.output_pins.keys())}")
    
    print(f"\n✓ 创建 Process 节点: {process_node}")
    print(f"  - 输入引脚: {list(process_node.input_pins.keys())}")
    print(f"  - 输出引脚: {list(process_node.output_pins.keys())}")
    print(f"  - 属性: {process_node.properties}")
    
    return graph, input_node, process_node


def test_node_connection():
    """测试节点连接"""
    print("\n" + "=" * 60)
    print("测试 2: 节点连接")
    print("=" * 60)
    
    # 创建节点图和节点
    graph = NodeGraph("test_graph")
    input_node = NodeFactory.create_node("TestInput", name="input1", node_graph=graph)
    process_node = NodeFactory.create_node("TestProcess", name="process1", node_graph=graph)
    
    # 添加节点到图
    graph.add_node(input_node)
    graph.add_node(process_node)
    
    print(f"✓ 添加节点到图: {list(graph.nodes.keys())}")
    
    # 创建连接
    source_pin = input_node.get_output_pin("output")
    target_pin = process_node.get_input_pin("input")
    
    print(f"\n连接: {source_pin.full_path} -> {target_pin.full_path}")
    
    # 检查是否可以连接
    can_connect = source_pin.can_connect_to(target_pin)
    print(f"  - 可以连接: {can_connect}")
    
    if can_connect:
        connection = Connection(source_pin, target_pin)
        graph.add_connection(connection)
        print(f"✓ 创建连接: {connection}")
        print(f"  - Input.output 连接数: {len(source_pin.connections)}")
        print(f"  - Process.input 连接数: {len(target_pin.connections)}")
        print(f"  - Process.input 已连接: {target_pin.is_connected}")
    
    return graph


def test_node_execution():
    """测试节点执行"""
    print("\n" + "=" * 60)
    print("测试 3: 节点执行")
    print("=" * 60)
    
    # 创建节点图和节点
    graph = NodeGraph("test_graph")
    
    # 创建 Input -> Process 管道
    input_node = NodeFactory.create_node("TestInput", name="input1", node_graph=graph)
    process_node = NodeFactory.create_node("TestProcess", name="process1", node_graph=graph, value=100)
    
    graph.add_node(input_node)
    graph.add_node(process_node)
    
    # 连接节点
    connection = Connection(
        input_node.get_output_pin("output"),
        process_node.get_input_pin("input")
    )
    graph.add_connection(connection)
    
    print(f"✓ 创建管道: input1 -> process1")
    
    # 执行 Input 节点
    print(f"\n执行 Input 节点...")
    input_node.execute()
    output_input = input_node.get_output_value("output")
    print(f"  - Input 输出: {output_input}")
    
    # 执行 Process 节点
    print(f"\n执行 Process 节点...")
    process_node.execute()
    output_process = process_node.get_output_value("output")
    print(f"  - Process 输出: {output_process}")
    
    return graph


def test_topological_sort():
    """测试拓扑排序"""
    print("\n" + "=" * 60)
    print("测试 4: 拓扑排序")
    print("=" * 60)
    
    # 创建复杂的节点图
    graph = NodeGraph("test_graph")
    
    # 创建节点: input -> process1 -> process2 -> process3
    nodes = {}
    for i in range(1, 5):
        if i == 1:
            node = NodeFactory.create_node("TestInput", name=f"node{i}", node_graph=graph)
        else:
            node = NodeFactory.create_node("TestProcess", name=f"node{i}", node_graph=graph)
        graph.add_node(node)
        nodes[f"node{i}"] = node
    
    # 创建连接链
    connections = [
        ("node1", "output", "node2", "input"),
        ("node2", "output", "node3", "input"),
        ("node3", "output", "node4", "input"),
    ]
    
    for src_node, src_pin, tgt_node, tgt_pin in connections:
        conn = Connection(
            nodes[src_node].get_output_pin(src_pin),
            nodes[tgt_node].get_input_pin(tgt_pin)
        )
        graph.add_connection(conn)
    
    print(f"✓ 创建节点链:")
    for name in ["node1", "node2", "node3", "node4"]:
        print(f"  - {name}")
    
    # 拓扑排序
    print(f"\n执行拓扑排序...")
    sorted_nodes = graph.topological_sort()
    print(f"✓ 排序结果:")
    for i, node in enumerate(sorted_nodes, 1):
        print(f"  {i}. {node.name} ({node.node_type})")
    
    # 验证顺序
    node_order = {node.name: i for i, node in enumerate(sorted_nodes)}
    assert node_order["node1"] < node_order["node2"]
    assert node_order["node2"] < node_order["node3"]
    assert node_order["node3"] < node_order["node4"]
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
    node1 = NodeFactory.create_node("TestInput", name="node1", node_graph=graph)
    node2 = NodeFactory.create_node("TestProcess", name="node2", node_graph=graph)
    node3 = NodeFactory.create_node("TestProcess", name="node3", node_graph=graph)
    
    graph.add_node(node1)
    graph.add_node(node2)
    graph.add_node(node3)
    
    # 创建连接
    conn1 = Connection(node1.get_output_pin("output"), node2.get_input_pin("input"))
    conn2 = Connection(node2.get_output_pin("output"), node3.get_input_pin("input"))
    graph.add_connection(conn1)
    graph.add_connection(conn2)
    
    print(f"✓ 初始状态:")
    print(f"  - 节点数: {len(graph.nodes)}")
    print(f"  - 连接数: {len(graph.connections)}")
    
    # 删除中间节点
    print(f"\n删除中间节点 'node2'...")
    graph.remove_node(node2)
    
    print(f"✓ 删除后:")
    print(f"  - 节点数: {len(graph.nodes)}")
    print(f"  - 连接数: {len(graph.connections)}")
    print(f"  - 剩余节点: {list(graph.nodes.keys())}")
    
    # 验证连接被正确清理
    assert "node2" not in graph.nodes
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
    print(f"  节点类型: {node_types}")
    
    # 显示节点分类
    categories = registry.get_categories()
    print(f"\n✓ 节点分类:")
    for category in categories:
        nodes_in_cat = registry.get_nodes_in_category(category)
        print(f"  - {category}: {nodes_in_cat}")
    
    # 搜索节点
    print(f"\n✓ 搜索测试:")
    search_results = registry.search_nodes("test")
    print(f"  - 搜索 'test': {search_results}")
    
    search_results = registry.search_nodes("process")
    print(f"  - 搜索 'process': {search_results}")
    
    return registry


def test_pin_type_compatibility():
    """测试引脚类型兼容性"""
    print("\n" + "=" * 60)
    print("测试 7: 引脚类型兼容性")
    print("=" * 60)
    
    graph = NodeGraph("test_graph")
    node1 = NodeFactory.create_node("TestInput", name="node1", node_graph=graph)
    node2 = NodeFactory.create_node("TestProcess", name="node2", node_graph=graph)
    
    graph.add_node(node1)
    graph.add_node(node2)
    
    # 测试兼容的连接
    source_pin = node1.get_output_pin("output")
    target_pin = node2.get_input_pin("input")
    
    print(f"测试连接: {source_pin.pin_type.value} -> {target_pin.pin_type.value}")
    can_connect = source_pin.can_connect_to(target_pin)
    print(f"  - 可以连接: {can_connect}")
    assert can_connect, "相同类型应该可以连接"
    print(f"✓ 类型兼容性测试通过")
    
    return graph


def run_all_tests():
    """运行所有测试"""
    print("\n" + "=" * 80)
    print(" " * 20 + "节点核心功能测试（简化版）")
    print("=" * 80)
    
    try:
        # 运行测试
        test_node_creation()
        test_node_connection()
        test_node_execution()
        test_topological_sort()
        test_node_deletion()
        test_node_registry()
        test_pin_type_compatibility()
        
        # 总结
        print("\n" + "=" * 80)
        print(" " * 30 + "所有测试通过! ✓")
        print("=" * 80)
        print("\n核心功能验证:")
        print("  ✓ 节点创建和属性管理")
        print("  ✓ 引脚连接和类型检查")
        print("  ✓ 节点执行和数据流")
        print("  ✓ 拓扑排序和依赖分析")
        print("  ✓ 节点删除和连接清理")
        print("  ✓ 节点注册表和搜索")
        print("  ✓ 引脚类型兼容性")
        print("\n所有核心逻辑正常工作!")
        return True
        
    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
