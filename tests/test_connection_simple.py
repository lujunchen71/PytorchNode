"""
简单连接拖拽测试 - 不依赖PyTorch

使用基本节点测试连接功能
"""

import sys
import os

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

import logging
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QPointF

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def register_test_nodes():
    """注册测试用的简单节点"""
    from core.base import Node, Pin, PinType, get_registry
    
    class TestSourceNode(Node):
        """测试源节点 - 有输出引脚"""
        node_type = "test.source"
        node_category = "Test"
        display_name = "测试源"
        
        def init_pins(self):
            """初始化引脚"""
            self.add_output_pin("output", PinType.TENSOR)
        
        def execute(self):
            """执行节点"""
            self._output_cache["output"] = "test_output"
            self._is_dirty = False
    
    class TestTargetNode(Node):
        """测试目标节点 - 有输入引脚"""
        node_type = "test.target"
        node_category = "Test"
        display_name = "测试目标"
        
        def init_pins(self):
            """初始化引脚"""
            self.add_input_pin("input", PinType.TENSOR)
        
        def execute(self):
            """执行节点"""
            pass
    
    # 注册节点
    registry = get_registry()
    registry.register(TestSourceNode)
    registry.register(TestTargetNode)
    
    logger.info("Test nodes registered")


def main():
    """主测试函数"""
    from ui.main_window import MainWindow
    from core.base import get_registry
    
    # 创建应用
    app = QApplication(sys.argv)
    
    # 注册测试节点
    register_test_nodes()
    
    # 创建主窗口
    window = MainWindow()
    window.show()
    
    logger.info("=" * 60)
    logger.info("连接拖拽功能测试")
    logger.info("=" * 60)
    
    # 验证节点注册
    registry = get_registry()
    categories = registry.get_categories()
    logger.info(f"可用分类: {categories}")
    
    # 创建两个测试节点
    logger.info("\n步骤 1: 创建源节点和目标节点")
    
    # 创建源节点
    pos1 = QPointF(100, 200)
    window._on_node_create_requested("test.source", pos1)
    logger.info(f"✓ 创建源节点在位置 {pos1}")
    
    # 创建目标节点
    pos2 = QPointF(400, 200)
    window._on_node_create_requested("test.target", pos2)
    logger.info(f"✓ 创建目标节点在位置 {pos2}")
    
    # 获取创建的节点
    nodes = list(window.node_graph.nodes.values())
    logger.info(f"当前节点数: {len(nodes)}")
    
    if len(nodes) >= 2:
        source_node = nodes[0]
        target_node = nodes[1]
        
        logger.info(f"\n源节点: {source_node.name}")
        logger.info(f"  输出引脚: {list(source_node.output_pins.keys())}")
        
        logger.info(f"目标节点: {target_node.name}")
        logger.info(f"  输入引脚: {list(target_node.input_pins.keys())}")
        
        # 获取引脚
        source_pin = list(source_node.output_pins.values())[0]
        target_pin = list(target_node.input_pins.values())[0]
        
        logger.info(f"\n步骤 2: 测试连接兼容性")
        if source_pin.can_connect_to(target_pin):
            logger.info(f"✓ 引脚可以连接")
            logger.info(f"  源: {source_pin.full_path} ({source_pin.pin_type.value})")
            logger.info(f"  目标: {target_pin.full_path} ({target_pin.pin_type.value})")
            
            # 通过信号创建连接
            logger.info(f"\n步骤 3: 创建连接")
            window.graphics_scene.connection_created.emit(source_pin, target_pin)
            
            # 验证连接 - connections可能是list或dict
            connections = window.node_graph.connections
            if isinstance(connections, dict):
                connections = list(connections.values())
            elif not isinstance(connections, list):
                connections = []
            
            logger.info(f"当前连接数: {len(connections)}")
            
            if connections:
                logger.info(f"✓ 连接创建成功!")
                conn = connections[0]
                logger.info(f"  {conn.source_node.name}.{conn.source_pin.name} → {conn.target_node.name}.{conn.target_pin.name}")
                
                # 验证图形项
                if conn in window.connection_graphics_items:
                    logger.info(f"✓ 连接图形项已创建")
                    conn_item = window.connection_graphics_items[conn]
                    logger.info(f"  类型: {type(conn_item).__name__}")
                else:
                    logger.error(f"✗ 连接图形项未找到")
            else:
                logger.error(f"✗ 连接未创建")
        else:
            logger.error(f"✗ 引脚无法连接")
    else:
        logger.error(f"✗ 节点创建失败，只有 {len(nodes)} 个节点")
    
    # 测试拖拽功能
    logger.info(f"\n步骤 4: 测试拖拽状态管理")
    
    if len(nodes) >= 2:
        source_node = nodes[0]
        node_item = window.node_graphics_items.get(source_node)
        
        if node_item:
            pin_name = list(source_node.output_pins.keys())[0]
            if pin_name in node_item.output_pin_items:
                pin_item = node_item.output_pin_items[pin_name]
                
                # 测试开始拖拽
                window.graphics_scene.start_connection_drag(pin_item)
                
                if window.graphics_scene.is_dragging_connection():
                    logger.info(f"✓ 开始拖拽连接")
                    
                    # 更新位置
                    test_pos = QPointF(250, 250)
                    window.graphics_scene.update_connection_drag(test_pos)
                    logger.info(f"✓ 更新拖拽位置到 {test_pos}")
                    
                    # 取消拖拽
                    window.graphics_scene.cancel_connection_drag()
                    
                    if not window.graphics_scene.is_dragging_connection():
                        logger.info(f"✓ 取消拖拽成功")
                    else:
                        logger.error(f"✗ 取消拖拽失败")
                else:
                    logger.error(f"✗ 未能开始拖拽")
    
    logger.info("\n" + "=" * 60)
    logger.info("测试完成！")
    logger.info("=" * 60)
    logger.info("\n手动测试说明:")
    logger.info("1. 将鼠标移到源节点底部的蓝色圆点（输出引脚）")
    logger.info("2. 按住鼠标左键并拖拽")
    logger.info("3. 拖拽到目标节点顶部的蓝色圆点（输入引脚）")
    logger.info("4. 释放鼠标完成连接")
    logger.info("\n窗口保持打开，可以手动测试拖拽功能...")
    
    # 运行应用
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
