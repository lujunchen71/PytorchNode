"""
连接验证工具

提供连接合法性检查和循环检测功能
"""

from typing import TYPE_CHECKING
import networkx as nx

if TYPE_CHECKING:
    from core.base.pin import Pin
    from core.base.node_graph import NodeGraph


def check_connection_valid(from_pin: 'Pin', to_pin: 'Pin') -> tuple[bool, str]:
    """
    检查连接是否合法
    
    Args:
        from_pin: 源引脚
        to_pin: 目标引脚
        
    Returns:
        (是否合法, 错误信息)
    """
    # 规则1: 不能连接到自己
    if from_pin is to_pin:
        return False, "不能连接到自己"
    
    # 规则2: 不能连接到同一节点
    if from_pin.node is to_pin.node:
        return False, "不能连接到同一节点的其他引脚"
    
    # 规则3: 必须是不同方向(输出→输入)
    if from_pin.direction == to_pin.direction:
        if from_pin.is_input:
            return False, "输入引脚不能连接到输入引脚"
        else:
            return False, "输出引脚不能连接到输出引脚"
    
    # 规则4: 使用Pin的类型检查
    if not from_pin.can_connect_to(to_pin):
        return False, "类型不兼容"
    
    return True, ""


def detect_cycles(graph: 'NodeGraph', from_node_id: str, to_node_id: str) -> bool:
    """
    检测添加连接后是否会形成循环
    
    Args:
        graph: 节点图
        from_node_id: 源节点ID
        to_node_id: 目标节点ID
        
    Returns:
        是否会形成循环(True=有循环,False=无循环)
    """
    # 使用NetworkX构建有向图
    nx_graph = nx.DiGraph()
    
    # 添加现有连接
    for conn in graph.connections.values():
        nx_graph.add_edge(conn.source_pin.node.id, conn.target_pin.node.id)
    
    # 添加新连接
    nx_graph.add_edge(from_node_id, to_node_id)
    
    # 检测是否为DAG(有向无环图)
    is_dag = nx.is_directed_acyclic_graph(nx_graph)
    
    return not is_dag  # 如果不是DAG,则有循环
