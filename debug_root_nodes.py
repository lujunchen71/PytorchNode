"""
诊断脚本 - 检查根节点创建和显示问题
"""

import sys
import logging
from pathlib import Path

# 确保项目根目录在 Python 路径中
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def test_root_node_creation():
    """测试根节点创建"""
    logger.info("=" * 60)
    logger.info("测试 1: 根节点类导入和注册")
    logger.info("=" * 60)
    
    # 导入根节点类
    from core.nodes.context.root_nodes import ObjRootNode, VisRootNode, TrainRootNode, RootNode
    logger.info(f"✓ ObjRootNode: {ObjRootNode.node_type}")
    logger.info(f"✓ VisRootNode: {VisRootNode.node_type}")
    logger.info(f"✓ TrainRootNode: {TrainRootNode.node_type}")
    
    # 检查注册表
    from core.base.node_registry import get_registry
    registry = get_registry()
    logger.info(f"✓ 注册表中的节点类型数量: {len(registry._node_types)}")
    
    # 检查根节点是否已注册
    for node_type in ["root.obj", "root.vis", "root.train"]:
        node_class = registry.get_node_class(node_type)
        if node_class:
            logger.info(f"  ✓ {node_type} 已注册: {node_class}")
        else:
            logger.error(f"  ✗ {node_type} 未注册!")
    
    return True

def test_node_graph_creation():
    """测试节点图创建"""
    logger.info("=" * 60)
    logger.info("测试 2: 节点图和根节点创建")
    logger.info("=" * 60)
    
    from core.base import NodeGraph
    from core.nodes.context.root_nodes import ObjRootNode, VisRootNode, TrainRootNode
    
    # 创建根图
    root_graph = NodeGraph("root")
    logger.info(f"✓ 创建根图: {root_graph.name}")
    
    # 创建三个子图
    obj_graph = NodeGraph("obj", parent=root_graph)
    vis_graph = NodeGraph("vis", parent=root_graph)
    train_graph = NodeGraph("train", parent=root_graph)
    
    root_graph.subgraphs["obj"] = obj_graph
    root_graph.subgraphs["vis"] = vis_graph
    root_graph.subgraphs["train"] = train_graph
    
    logger.info(f"✓ 创建子图: obj, vis, train")
    logger.info(f"  根图路径: {root_graph.path}")
    logger.info(f"  obj图路径: {obj_graph.path}")
    logger.info(f"  vis图路径: {vis_graph.path}")
    logger.info(f"  train图路径: {train_graph.path}")
    
    # 创建根节点
    obj_root = ObjRootNode(name="obj", node_graph=obj_graph)
    vis_root = VisRootNode(name="vis", node_graph=vis_graph)
    train_root = TrainRootNode(name="train", node_graph=train_graph)
    
    logger.info(f"✓ 创建根节点:")
    logger.info(f"  obj_root: name={obj_root.name}, type={obj_root.node_type}")
    logger.info(f"  vis_root: name={vis_root.name}, type={vis_root.node_type}")
    logger.info(f"  train_root: name={train_root.name}, type={train_root.node_type}")
    
    # 添加到子图
    obj_graph.add_node(obj_root)
    vis_graph.add_node(vis_root)
    train_graph.add_node(train_root)
    
    logger.info(f"✓ 添加根节点到子图:")
    logger.info(f"  obj_graph 节点数: {len(obj_graph.nodes)}")
    logger.info(f"  vis_graph 节点数: {len(vis_graph.nodes)}")
    logger.info(f"  train_graph 节点数: {len(train_graph.nodes)}")
    
    # 验证节点是否正确添加
    logger.info(f"验证:")
    logger.info(f"  obj_graph.nodes.keys(): {list(obj_graph.nodes.keys())}")
    logger.info(f"  'obj' in obj_graph.nodes: {'obj' in obj_graph.nodes}")
    
    return True

def test_graphics_item_creation():
    """测试图形项创建"""
    logger.info("=" * 60)
    logger.info("测试 3: 图形项创建")
    logger.info("=" * 60)
    
    try:
        from PyQt6.QtWidgets import QApplication
        from core.base import NodeGraph
        from core.nodes.context.root_nodes import ObjRootNode
        from ui.graphics.node_graphics_item_v2 import NodeGraphicsItemV2
        
        # 创建 Qt 应用（不需要显示）
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        # 创建节点图和根节点
        obj_graph = NodeGraph("obj")
        obj_root = ObjRootNode(name="obj", node_graph=obj_graph)
        obj_graph.add_node(obj_root)
        
        # 创建图形项
        graphics_item = NodeGraphicsItemV2(obj_root)
        logger.info(f"✓ 创建图形项: {graphics_item}")
        logger.info(f"  节点名称: {graphics_item.node.name}")
        logger.info(f"  节点类型: {graphics_item.node.node_type}")
        
        return True
    except Exception as e:
        logger.error(f"✗ 图形项创建失败: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

def test_breadcrumb_navigation():
    """测试面包屑导航"""
    logger.info("=" * 60)
    logger.info("测试 4: 面包屑导航")
    logger.info("=" * 60)
    
    try:
        from PyQt6.QtWidgets import QApplication
        from ui.widgets.breadcrumb_path_bar import BreadcrumbPathBar
        
        # 创建 Qt 应用
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        # 创建面包屑导航栏
        breadcrumb = BreadcrumbPathBar()
        logger.info(f"✓ 创建面包屑导航栏")
        logger.info(f"  初始路径: {breadcrumb.current_path}")
        
        # 测试路径切换
        breadcrumb.set_path("/vis")
        logger.info(f"  切换到 /vis: {breadcrumb.current_path}")
        
        breadcrumb.set_path("/train")
        logger.info(f"  切换到 /train: {breadcrumb.current_path}")
        
        return True
    except Exception as e:
        logger.error(f"✗ 面包屑导航测试失败: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

def test_double_click_logic():
    """测试双击逻辑"""
    logger.info("=" * 60)
    logger.info("测试 5: 双击进入节点逻辑")
    logger.info("=" * 60)
    
    from core.base.node import NodeCategory
    from core.nodes.context.root_nodes import ObjRootNode, VisRootNode, TrainRootNode
    from core.base import NodeGraph
    
    # 创建节点图
    obj_graph = NodeGraph("obj")
    obj_root = ObjRootNode(name="obj", node_graph=obj_graph)
    
    logger.info(f"✓ 创建根节点:")
    logger.info(f"  node_category: {obj_root.node_category}")
    logger.info(f"  node_type: {obj_root.node_type}")
    logger.info(f"  is CONTEXT: {obj_root.node_category == NodeCategory.CONTEXT}")
    
    # 模拟双击逻辑
    if obj_root.node_category == NodeCategory.CONTEXT:
        new_path = None
        if obj_root.node_type == "root.obj":
            new_path = "/obj"
        elif obj_root.node_type == "root.vis":
            new_path = "/vis"
        elif obj_root.node_type == "root.train":
            new_path = "/train"
        
        if new_path:
            logger.info(f"  ✓ 双击将切换到: {new_path}")
        else:
            logger.error(f"  ✗ 未知根节点类型: {obj_root.node_type}")
    
    return True

def main():
    """运行所有诊断测试"""
    logger.info("开始诊断根节点问题...")
    logger.info("")
    
    results = {}
    
    # 测试 1: 根节点类导入和注册
    try:
        results["root_node_creation"] = test_root_node_creation()
    except Exception as e:
        logger.error(f"测试 1 失败: {e}")
        results["root_node_creation"] = False
    
    logger.info("")
    
    # 测试 2: 节点图创建
    try:
        results["node_graph_creation"] = test_node_graph_creation()
    except Exception as e:
        logger.error(f"测试 2 失败: {e}")
        results["node_graph_creation"] = False
    
    logger.info("")
    
    # 测试 3: 图形项创建
    try:
        results["graphics_item_creation"] = test_graphics_item_creation()
    except Exception as e:
        logger.error(f"测试 3 失败: {e}")
        results["graphics_item_creation"] = False
    
    logger.info("")
    
    # 测试 4: 面包屑导航
    try:
        results["breadcrumb_navigation"] = test_breadcrumb_navigation()
    except Exception as e:
        logger.error(f"测试 4 失败: {e}")
        results["breadcrumb_navigation"] = False
    
    logger.info("")
    
    # 测试 5: 双击逻辑
    try:
        results["double_click_logic"] = test_double_click_logic()
    except Exception as e:
        logger.error(f"测试 5 失败: {e}")
        results["double_click_logic"] = False
    
    # 总结
    logger.info("=" * 60)
    logger.info("诊断结果总结")
    logger.info("=" * 60)
    
    for test_name, passed in results.items():
        status = "✓ 通过" if passed else "✗ 失败"
        logger.info(f"  {test_name}: {status}")
    
    all_passed = all(results.values())
    if all_passed:
        logger.info("")
        logger.info("所有测试通过！问题可能在其他地方。")
    else:
        logger.info("")
        logger.info("有测试失败，请检查相关代码。")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
