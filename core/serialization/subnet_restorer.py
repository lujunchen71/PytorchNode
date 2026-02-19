"""
子网恢复器 - 递归恢复SubnetNode的子图内容

从 ui/main_window.py 移出的独立模块，负责子网的序列化恢复
"""

import logging
from typing import Dict, List, Any, Optional


logger = logging.getLogger(__name__)


def restore_subnet_subgraph(subnet_node, node_data: dict, custom_logger=None):
    """
    递归恢复SubnetNode的子图内容
    
    Args:
        subnet_node: SubnetNode实例
        node_data: 序列化的节点数据（包含subgraph字段）
        custom_logger: 可选的自定义日志记录器
    """
    from core.base.connection import Connection
    from core.base import NodeFactory
    from core.base.pin import Pin, PinType
    from core.nodes.subnet.subnet_pins import SubnetInputPinNode, SubnetOutputPinNode
    from core.debug import get_debug_manager, DebugCategory
    
    log = custom_logger or logger
    
    debug_manager = get_debug_manager()
    debug_enabled = debug_manager.is_enabled(DebugCategory.PACK)
    
    subgraph_data = node_data.get("subgraph", {})
    if not subgraph_data:
        log.info(f"[RESTORE] SubnetNode {subnet_node.name} 没有子图数据")
        return
    
    # 重要：确保 _subgraph.name 与 subnet_node.name 同步
    # 这是修复三层嵌套子网连接显示问题的关键
    if subnet_node._subgraph.name != subnet_node.name:
        log.info(f"[RESTORE] 同步 subgraph 名称: {subnet_node._subgraph.name} -> {subnet_node.name}")
        subnet_node._subgraph.name = subnet_node.name
    
    log.info(f"[RESTORE] ===== 开始恢复SubnetNode {subnet_node.name} =====")
    log.info(f"[RESTORE] 子图数据: {len(subgraph_data.get('nodes', []))} 节点, {len(subgraph_data.get('connections', []))} 连接")
    
    # 记录调试信息
    if debug_enabled:
        debug_manager.log_serialization(
            operation=f"restore_start_{subnet_node.name}",
            data_before=node_data,
            data_after=None,
            errors=[]
        )
    
    # 1. 清空默认创建的InputPin节点
    default_input_pins = [n for n in list(subnet_node.subgraph.nodes.values())
                          if n.node_type == "subnet.input_pin"]
    
    log.info(f"[RESTORE] 找到 {len(default_input_pins)} 个默认InputPin节点")
    
    # 删除默认InputPin节点
    for pin_node in default_input_pins:
        # 删除该节点的所有连接
        for pin in list(pin_node.output_pins.values()):
            for conn in list(pin.connections):
                subnet_node.subgraph.remove_connection(conn)
        # 从子图中移除节点
        if pin_node.name in subnet_node.subgraph.nodes:
            del subnet_node.subgraph.nodes[pin_node.name]
        log.info(f"[RESTORE] 删除默认InputPin: {pin_node.name}")
    
    # 清空默认外部引脚（使用正确的属性名）
    subnet_node.input_pins.clear()
    subnet_node.output_pins.clear()
    subnet_node._input_pin_nodes.clear()
    subnet_node._output_pin_nodes.clear()
    
    # 2. 恢复子图中的节点
    inner_name_mapping = {}  # old_name -> new_node
    failed_nodes = []
    
    for inner_node_data in subgraph_data.get("nodes", []):
        try:
            inner_node_type = inner_node_data.get("type")
            inner_old_name = inner_node_data.get("name")
            
            log.info(f"[RESTORE] 创建节点: type={inner_node_type}, old_name={inner_old_name}")
            
            # 创建内部节点
            inner_node = NodeFactory.create_node(
                node_type=inner_node_type,
                node_graph=subnet_node.subgraph
            )
            
            # 重要：恢复原始名称（打包不应改变内部节点名称）
            # NodeFactory.create_node 会自动生成新名称，我们需要强制恢复原始名称
            if inner_node.name != inner_old_name:
                log.info(f"[RESTORE] 恢复节点名称: {inner_node.name} -> {inner_old_name}")
                inner_node._name = inner_old_name  # 直接设置内部属性
            
            # 恢复属性
            inner_node.id = inner_node_data.get("id")
            inner_node.position = tuple(inner_node_data.get("position", [0, 0]))
            for key, value in inner_node_data.get("properties", {}).items():
                inner_node.set_property(key, value)
            
            # 恢复实例参数
            if "instance_parameters" in inner_node_data:
                inner_node.instance_parameters = inner_node_data["instance_parameters"].copy()
            
            # 递归处理嵌套的SubnetNode
            if inner_node_type == "subnet":
                log.info(f"[RESTORE] 检测到嵌套SubnetNode: {inner_old_name}")
                # 重要：更新嵌套SubnetNode的subgraph的parent引用
                # 确保路径计算正确
                inner_node._subgraph.parent = subnet_node.subgraph
                inner_node._subgraph.name = inner_node.name  # 更新subgraph名称
                restore_subnet_subgraph(inner_node, inner_node_data, log)
            
            # 添加到子图
            subnet_node.subgraph.add_node(inner_node)
            inner_name_mapping[inner_old_name] = inner_node
            
            log.info(f"[RESTORE] 恢复内部节点成功: {inner_old_name}")
            
        except Exception as e:
            log.error(f"[RESTORE] 恢复内部节点失败: {e}")
            import traceback
            log.error(traceback.format_exc())
            failed_nodes.append({
                "type": inner_node_data.get("type"),
                "name": inner_node_data.get("name"),
                "error": str(e)
            })
    
    # 记录节点映射调试信息
    if debug_enabled:
        debug_manager.log_node_mapping(
            operation=f"restore_nodes_{subnet_node.name}",
            name_mapping={old: new.name for old, new in inner_name_mapping.items()},
            pin_mapping={},
            failed_mappings=failed_nodes
        )
    
    # 3. 恢复子图中的连接
    # 构建节点ID到新节点的映射（优先使用ID查找）
    node_id_mapping = {}  # old_id -> new_node
    for old_name, new_node in inner_name_mapping.items():
        # 从原始节点数据中获取ID
        for inner_node_data in subgraph_data.get("nodes", []):
            if inner_node_data.get("name") == old_name:
                old_id = inner_node_data.get("id")
                if old_id:
                    node_id_mapping[old_id] = new_node
                break
    
    failed_connections = []
    
    for conn_data in subgraph_data.get("connections", []):
        try:
            # 优先使用节点ID查找（推荐方式，ID是稳定的）
            source_node = None
            target_node = None
            source_name = None  # 提前初始化，避免后续引用错误
            target_name = None
            
            if "source_node_id" in conn_data:
                # 使用节点ID查找
                source_node = node_id_mapping.get(conn_data["source_node_id"])
                target_node = node_id_mapping.get(conn_data["target_node_id"])
                log.info(f"[RESTORE] 连接查找(ID): source_id={conn_data['source_node_id']} -> source_node={source_node}")
                log.info(f"[RESTORE] 连接查找(ID): target_id={conn_data['target_node_id']} -> target_node={target_node}")
            
            if source_node is None or target_node is None:
                # 回退到名称查找（兼容旧格式）
                source_path = conn_data.get("source_node", "")
                target_path = conn_data.get("target_node", "")
                
                # 提取简单名称（取路径的最后一段）
                source_name = source_path.split("/")[-1] if "/" in source_path else source_path
                target_name = target_path.split("/")[-1] if "/" in target_path else target_path
                
                log.info(f"[RESTORE] 连接查找(名称): source_path={source_path} -> source_name={source_name}")
                log.info(f"[RESTORE] 连接查找(名称): target_path={target_path} -> target_name={target_name}")
                
                if source_node is None:
                    source_node = inner_name_mapping.get(source_name)
                if target_node is None:
                    target_node = inner_name_mapping.get(target_name)
            
            # 获取节点名称用于日志和错误信息
            if source_node:
                source_name = source_node.name
            if target_node:
                target_name = target_node.name
            
            if source_node and target_node:
                source_pin = source_node.get_output_pin(conn_data["source_pin"])
                target_pin = target_node.get_input_pin(conn_data["target_pin"])
                
                if source_pin and target_pin:
                    conn = Connection(source_pin, target_pin)
                    conn.id = conn_data.get("id")
                    subnet_node.subgraph.add_connection(conn)
                    log.info(f"[RESTORE] 恢复内部连接: {source_name}.{conn_data['source_pin']} -> {target_name}.{conn_data['target_pin']}")
                else:
                    error_msg = f"找不到引脚: source_pin={source_pin}, target_pin={target_pin}"
                    log.warning(f"[RESTORE] {error_msg}")
                    failed_connections.append({
                        "connection": f"{source_name}.{conn_data['source_pin']} -> {target_name}.{conn_data['target_pin']}",
                        "error": error_msg
                    })
            else:
                error_msg = f"找不到节点: source_node={source_node}, target_node={target_node}"
                log.warning(f"[RESTORE] {error_msg}")
                failed_connections.append({
                    "connection": f"{source_name or 'Unknown'} -> {target_name or 'Unknown'}",
                    "error": error_msg
                })
        
        except Exception as e:
            log.error(f"[RESTORE] 恢复内部连接失败: {e}")
            failed_connections.append({
                "connection": f"{conn_data.get('source_node', 'Unknown')} -> {conn_data.get('target_node', 'Unknown')}",
                "error": str(e)
            })
    
    # 4. 恢复input_count和output_count
    input_count = node_data.get("input_count", 4)
    output_count = node_data.get("output_count", 1)
    subnet_node._input_count = input_count
    subnet_node._output_count = output_count
    
    # 5. 恢复外部输入引脚
    for i in range(input_count):
        pin_name = f"input_{i}"
        subnet_node.add_input_pin(pin_name, PinType.ANY, label=f"In {i+1}")
        log.info(f"[RESTORE] 创建外部输入引脚: {pin_name}")
    
    # 6. 恢复外部输出引脚
    for i in range(output_count):
        pin_name = f"output_{i}"
        subnet_node.add_output_pin(pin_name, PinType.ANY, label=f"Out {i+1}")
        log.info(f"[RESTORE] 创建外部输出引脚: {pin_name}")
    
    # 7. 恢复映射关系
    input_pin_nodes = node_data.get("input_pin_nodes", {})
    output_pin_nodes = node_data.get("output_pin_nodes", {})
    
    log.info(f"[RESTORE] 原始输入映射: {input_pin_nodes}")
    log.info(f"[RESTORE] 原始输出映射: {output_pin_nodes}")
    
    # 更新_input_pin_nodes映射（使用新的节点名称）
    for old_internal_name, external_pin_name in input_pin_nodes.items():
        # 查找对应的内部节点（可能是新名称）
        new_internal_node = inner_name_mapping.get(old_internal_name)
        if new_internal_node:
            subnet_node._input_pin_nodes[new_internal_node.name] = external_pin_name
            log.info(f"[RESTORE] 恢复输入映射: {new_internal_node.name} -> {external_pin_name}")
        else:
            # 如果找不到，可能是InputPin节点，尝试按原名查找
            subnet_node._input_pin_nodes[old_internal_name] = external_pin_name
            log.info(f"[RESTORE] 保留原输入映射: {old_internal_name} -> {external_pin_name}")
    
    # 更新_output_pin_nodes映射
    for old_internal_name, external_pin_name in output_pin_nodes.items():
        new_internal_node = inner_name_mapping.get(old_internal_name)
        if new_internal_node:
            subnet_node._output_pin_nodes[new_internal_node.name] = external_pin_name
            log.info(f"[RESTORE] 恢复输出映射: {new_internal_node.name} -> {external_pin_name}")
        else:
            subnet_node._output_pin_nodes[old_internal_name] = external_pin_name
            log.info(f"[RESTORE] 保留原输出映射: {old_internal_name} -> {external_pin_name}")
    
    log.info(f"[RESTORE] ===== SubnetNode {subnet_node.name} 恢复完成 =====")
    log.info(f"[RESTORE] 节点: {len(inner_name_mapping)} 成功, {len(failed_nodes)} 失败")
    log.info(f"[RESTORE] 连接: {len(subgraph_data.get('connections', [])) - len(failed_connections)} 成功, {len(failed_connections)} 失败")
    log.info(f"[RESTORE] 输入: {input_count}, 输出: {output_count}")
    
    # 记录最终调试信息
    if debug_enabled:
        # 构建恢复后的子图数据
        restored_data = {
            "nodes": [{"name": n.name, "type": n.node_type} for n in subnet_node.subgraph.nodes.values()],
            "connections": [{"source": c.source_pin.full_path, "target": c.target_pin.full_path} for c in subnet_node.subgraph.connections],
            "input_pin_nodes": subnet_node._input_pin_nodes,
            "output_pin_nodes": subnet_node._output_pin_nodes
        }
        
        debug_manager.log_serialization(
            operation=f"restore_end_{subnet_node.name}",
            data_before=node_data,
            data_after=restored_data,
            errors=failed_nodes + failed_connections
        )
