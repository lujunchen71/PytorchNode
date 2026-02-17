"""
测试连接拖拽功能

验证：
1. 引脚拖拽能正确创建临时连接线
2. 拖拽到目标引脚时创建真实连接
3. 连接线正确显示和渲染
4. 连接创建、显示和删除功能
"""

import sys
import os
import logging

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QPointF, Qt

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def test_connection_creation():
    """测试连接创建功能"""
    from ui.main_window import MainWindow
    from core.base import get_registry
    
    # 创建应用
    app = QApplication(sys.argv)
    
    # 创建主窗口
    window = MainWindow()
    window.show()
    
    logger.info("=== 测试连接拖拽功能 ===")
    
    # 获取注册表并注册测试节点
    registry = get_registry()
    
    # 检查是否有可用的节点
    categories = registry.get_categories()
    logger.info(f"Available categories: {categories}")
    
    if not categories:
        logger.warning("No nodes registered! Loading default nodes...")
        # 尝试加载默认节点
        try:
            from core.nodes.nn import register_nn_nodes
            register_nn_nodes()
            categories = registry.get_categories()
            logger.info(f"After loading: {categories}")
        except Exception as e:
            logger.error(f"Failed to load nodes: {e}")
            return
    
    # 创建两个测试节点
    logger.info("\n--- 步骤 1: 创建两个节点 ---")
    
    # 获取第一个可用的节点类型
    first_category = sorted(categories)[0]
    node_types = registry.get_nodes_in_category(first_category)
    
    if len(node_types) < 1:
        logger.error("Not enough node types available for testing")
        return
    
    # 创建第一个节点
    node_type1 = sorted(node_types)[0]
    pos1 = QPointF(100, 100)
    logger.info(f"Creating node 1: {node_type1} at {pos1}")
    window._on_node_create_requested(node_type1, pos1)
    
    # 创建第二个节点
    node_type2 = sorted(node_types)[0]  # 可以是同一类型
    pos2 = QPointF(300, 100)
    logger.info(f"Creating node 2: {node_type2} at {pos2}")
    window._on_node_create_requested(node_type2, pos2)
    
    # 获取创建的节点
    nodes = list(window.node_graph.nodes.values())
    if len(nodes) < 2:
        logger.error(f"Failed to create 2 nodes, only got {len(nodes)}")
        return
    
    node1 = nodes[0]
    node2 = nodes[1]
    
    logger.info(f"Node 1: {node1.name}, outputs: {list(node1.output_pins.keys())}")
    logger.info(f"Node 2: {node2.name}, inputs: {list(node2.input_pins.keys())}")
    
    # 验证节点有输出和输入引脚
    if not node1.output_pins:
        logger.error(f"Node 1 ({node1.name}) has no output pins")
        return
    
    if not node2.input_pins:
        logger.error(f"Node 2 ({node2.name}) has no input pins")
        return
    
    # 获取引脚
    source_pin_name = list(node1.output_pins.keys())[0]
    target_pin_name = list(node2.input_pins.keys())[0]
    
    source_pin = node1.output_pins[source_pin_name]
    target_pin = node2.input_pins[target_pin_name]
    
    logger.info(f"Source pin: {source_pin.full_path}")
    logger.info(f"Target pin: {target_pin.full_path}")
    
    # 测试连接创建
    logger.info("\n--- 步骤 2: 测试连接创建 ---")
    
    # 检查是否可以连接
    if source_pin.can_connect_to(target_pin):
        logger.info("✓ Pins can be connected")
        
        # 通过信号创建连接
        logger.info("Creating connection through signal...")
        window.graphics_scene.connection_created.emit(source_pin, target_pin)
        
        # 验证连接是否创建
        connections = list(window.node_graph.connections.values())
        logger.info(f"Total connections in graph: {len(connections)}")
        
        if connections:
            logger.info("✓ Connection created successfully")
            conn = connections[0]
            logger.info(f"  Connection: {conn.source_node.name}.{conn.source_pin.name} → {conn.target_node.name}.{conn.target_pin.name}")
            
            # 验证图形项
            if conn in window.connection_graphics_items:
                logger.info("✓ Connection graphics item created")
                conn_item = window.connection_graphics_items[conn]
                logger.info(f"  Graphics item: {conn_item}")
            else:
                logger.error("✗ Connection graphics item NOT found")
        else:
            logger.error("✗ Connection NOT created")
    else:
        logger.warning(f"✗ Cannot connect {source_pin.pin_type} to {target_pin.pin_type}")
    
    # 测试场景的连接拖拽功能
    logger.info("\n--- 步骤 3: 测试拖拽状态管理 ---")
    
    # 获取引脚图形项
    node1_item = window.node_graphics_items.get(node1)
    if node1_item and source_pin_name in node1_item.output_pin_items:
        source_pin_item = node1_item.output_pin_items[source_pin_name]
        
        # 模拟开始拖拽
        logger.info("Simulating connection drag start...")
        window.graphics_scene.start_connection_drag(source_pin_item)
        
        if window.graphics_scene.is_dragging_connection():
            logger.info("✓ Connection drag started")
            
            # 模拟更新位置
            test_pos = QPointF(200, 150)
            window.graphics_scene.update_connection_drag(test_pos)
            logger.info(f"✓ Updated drag position to {test_pos}")
            
            # 取消拖拽
            window.graphics_scene.cancel_connection_drag()
            
            if not window.graphics_scene.is_dragging_connection():
                logger.info("✓ Connection drag cancelled")
            else:
                logger.error("✗ Failed to cancel drag")
        else:
            logger.error("✗ Connection drag NOT started")
    else:
        logger.error("✗ Could not find source pin graphics item")
    
    logger.info("\n=== 测试完成 ===")
    logger.info("窗口将保持打开状态，您可以手动测试拖拽连接功能：")
    logger.info("1. 在节点的输出引脚上按下鼠标左键")
    logger.info("2. 拖拽到目标节点的输入引脚")
    logger.info("3. 释放鼠标创建连接")
    
    # 运行应用
    sys.exit(app.exec())


if __name__ == '__main__':
    test_connection_creation()
