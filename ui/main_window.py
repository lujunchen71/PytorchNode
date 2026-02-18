"""
主窗口（MainWindow）- 应用程序的主界面

职责:
- 布局管理
- 菜单/工具栏
- 信号连接
- 面板管理
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QMenuBar, QMenu, QToolBar, QStatusBar, QDockWidget,
    QLabel, QMessageBox, QFileDialog, QDialog
)
from PyQt6.QtCore import Qt, pyqtSignal as Signal, pyqtSlot as Slot
from PyQt6.QtGui import QAction, QKeySequence, QIcon

import logging


logger = logging.getLogger(__name__)


def _restore_subnet_subgraph(subnet_node, node_data, logger):
    """
    递归恢复SubnetNode的子图内容
    
    Args:
        subnet_node: SubnetNode实例
        node_data: 序列化的节点数据（包含subgraph字段）
        logger: 日志记录器
    """
    from core.base.connection import Connection
    from core.base import NodeFactory
    from core.base.pin import Pin, PinType
    from core.nodes.subnet.subnet_pins import SubnetInputPinNode, SubnetOutputPinNode
    from core.debug import get_debug_manager, DebugCategory
    
    debug_manager = get_debug_manager()
    debug_enabled = debug_manager.is_enabled(DebugCategory.PACK)
    
    subgraph_data = node_data.get("subgraph", {})
    if not subgraph_data:
        logger.info(f"[RESTORE] SubnetNode {subnet_node.name} 没有子图数据")
        return
    
    # 重要：确保 _subgraph.name 与 subnet_node.name 同步
    # 这是修复三层嵌套子网连接显示问题的关键
    if subnet_node._subgraph.name != subnet_node.name:
        logger.info(f"[RESTORE] 同步 subgraph 名称: {subnet_node._subgraph.name} -> {subnet_node.name}")
        subnet_node._subgraph.name = subnet_node.name
    
    logger.info(f"[RESTORE] ===== 开始恢复SubnetNode {subnet_node.name} =====")
    logger.info(f"[RESTORE] 子图数据: {len(subgraph_data.get('nodes', []))} 节点, {len(subgraph_data.get('connections', []))} 连接")
    
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
    
    logger.info(f"[RESTORE] 找到 {len(default_input_pins)} 个默认InputPin节点")
    
    # 删除默认InputPin节点
    for pin_node in default_input_pins:
        # 删除该节点的所有连接
        for pin in list(pin_node.output_pins.values()):
            for conn in list(pin.connections):
                subnet_node.subgraph.remove_connection(conn)
        # 从子图中移除节点
        if pin_node.name in subnet_node.subgraph.nodes:
            del subnet_node.subgraph.nodes[pin_node.name]
        logger.info(f"[RESTORE] 删除默认InputPin: {pin_node.name}")
    
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
            
            logger.info(f"[RESTORE] 创建节点: type={inner_node_type}, old_name={inner_old_name}")
            
            # 创建内部节点
            inner_node = NodeFactory.create_node(
                node_type=inner_node_type,
                node_graph=subnet_node.subgraph
            )
            
            # 重要：恢复原始名称（打包不应改变内部节点名称）
            # NodeFactory.create_node 会自动生成新名称，我们需要强制恢复原始名称
            if inner_node.name != inner_old_name:
                logger.info(f"[RESTORE] 恢复节点名称: {inner_node.name} -> {inner_old_name}")
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
                logger.info(f"[RESTORE] 检测到嵌套SubnetNode: {inner_old_name}")
                # 重要：更新嵌套SubnetNode的subgraph的parent引用
                # 确保路径计算正确
                inner_node._subgraph.parent = subnet_node.subgraph
                inner_node._subgraph.name = inner_node.name  # 更新subgraph名称
                _restore_subnet_subgraph(inner_node, inner_node_data, logger)
            
            # 添加到子图
            subnet_node.subgraph.add_node(inner_node)
            inner_name_mapping[inner_old_name] = inner_node
            
            logger.info(f"[RESTORE] 恢复内部节点成功: {inner_old_name}")
            
        except Exception as e:
            logger.error(f"[RESTORE] 恢复内部节点失败: {e}")
            import traceback
            logger.error(traceback.format_exc())
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
                logger.info(f"[RESTORE] 连接查找(ID): source_id={conn_data['source_node_id']} -> source_node={source_node}")
                logger.info(f"[RESTORE] 连接查找(ID): target_id={conn_data['target_node_id']} -> target_node={target_node}")
            
            if source_node is None or target_node is None:
                # 回退到名称查找（兼容旧格式）
                source_path = conn_data.get("source_node", "")
                target_path = conn_data.get("target_node", "")
                
                # 提取简单名称（取路径的最后一段）
                source_name = source_path.split("/")[-1] if "/" in source_path else source_path
                target_name = target_path.split("/")[-1] if "/" in target_path else target_path
                
                logger.info(f"[RESTORE] 连接查找(名称): source_path={source_path} -> source_name={source_name}")
                logger.info(f"[RESTORE] 连接查找(名称): target_path={target_path} -> target_name={target_name}")
                
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
                    logger.info(f"[RESTORE] 恢复内部连接: {source_name}.{conn_data['source_pin']} -> {target_name}.{conn_data['target_pin']}")
                else:
                    error_msg = f"找不到引脚: source_pin={source_pin}, target_pin={target_pin}"
                    logger.warning(f"[RESTORE] {error_msg}")
                    failed_connections.append({
                        "connection": f"{source_name}.{conn_data['source_pin']} -> {target_name}.{conn_data['target_pin']}",
                        "error": error_msg
                    })
            else:
                error_msg = f"找不到节点: source_node={source_node}, target_node={target_node}"
                logger.warning(f"[RESTORE] {error_msg}")
                failed_connections.append({
                    "connection": f"{source_name or 'Unknown'} -> {target_name or 'Unknown'}",
                    "error": error_msg
                })
        
        except Exception as e:
            logger.error(f"[RESTORE] 恢复内部连接失败: {e}")
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
        logger.info(f"[RESTORE] 创建外部输入引脚: {pin_name}")
    
    # 6. 恢复外部输出引脚
    for i in range(output_count):
        pin_name = f"output_{i}"
        subnet_node.add_output_pin(pin_name, PinType.ANY, label=f"Out {i+1}")
        logger.info(f"[RESTORE] 创建外部输出引脚: {pin_name}")
    
    # 7. 恢复映射关系
    input_pin_nodes = node_data.get("input_pin_nodes", {})
    output_pin_nodes = node_data.get("output_pin_nodes", {})
    
    logger.info(f"[RESTORE] 原始输入映射: {input_pin_nodes}")
    logger.info(f"[RESTORE] 原始输出映射: {output_pin_nodes}")
    
    # 更新_input_pin_nodes映射（使用新的节点名称）
    for old_internal_name, external_pin_name in input_pin_nodes.items():
        # 查找对应的内部节点（可能是新名称）
        new_internal_node = inner_name_mapping.get(old_internal_name)
        if new_internal_node:
            subnet_node._input_pin_nodes[new_internal_node.name] = external_pin_name
            logger.info(f"[RESTORE] 恢复输入映射: {new_internal_node.name} -> {external_pin_name}")
        else:
            # 如果找不到，可能是InputPin节点，尝试按原名查找
            subnet_node._input_pin_nodes[old_internal_name] = external_pin_name
            logger.info(f"[RESTORE] 保留原输入映射: {old_internal_name} -> {external_pin_name}")
    
    # 更新_output_pin_nodes映射
    for old_internal_name, external_pin_name in output_pin_nodes.items():
        new_internal_node = inner_name_mapping.get(old_internal_name)
        if new_internal_node:
            subnet_node._output_pin_nodes[new_internal_node.name] = external_pin_name
            logger.info(f"[RESTORE] 恢复输出映射: {new_internal_node.name} -> {external_pin_name}")
        else:
            subnet_node._output_pin_nodes[old_internal_name] = external_pin_name
            logger.info(f"[RESTORE] 保留原输出映射: {old_internal_name} -> {external_pin_name}")
    
    logger.info(f"[RESTORE] ===== SubnetNode {subnet_node.name} 恢复完成 =====")
    logger.info(f"[RESTORE] 节点: {len(inner_name_mapping)} 成功, {len(failed_nodes)} 失败")
    logger.info(f"[RESTORE] 连接: {len(subgraph_data.get('connections', [])) - len(failed_connections)} 成功, {len(failed_connections)} 失败")
    logger.info(f"[RESTORE] 输入: {input_count}, 输出: {output_count}")
    
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


class MainWindow(QMainWindow):
    """主窗口类"""

    # 自定义信号
    project_opened = Signal(str)
    project_saved = Signal(str)
    project_closed = Signal()

    def __init__(self, parent=None):
        """初始化主窗口"""
        super().__init__(parent)

        # 窗口设置
        self.setWindowTitle("PNNE - PyTorch Neural Network Editor")
        self.setGeometry(100, 100, 1400, 900)

        # 当前项目
        self.current_project_path = None

        # 初始化UI
        self._init_ui()
        self._create_menus()
        self._create_toolbars()
        self._create_status_bar()
        self._create_dock_widgets()
        
        # 显示初始路径的根节点
        self._display_graph_nodes()

        logger.info(f"启动完成 - 当前路径: {self.current_path}, 面包屑路径: {self.path_nav_bar.current_path if hasattr(self, 'path_nav_bar') else 'N/A'}")
        logger.info("Main window initialized")

    def _init_ui(self):
        """初始化UI布局"""
        # 导入图形组件
        from ui.graphics.node_graphics_scene import NodeGraphicsScene
        from ui.graphics.node_graphics_view import NodeGraphicsView
        from ui.graphics.node_graphics_item_v2 import NodeGraphicsItemV2
        from core.base import NodeGraph, NodeFactory
        from core.undo.undo_stack import UndoStack
        from ui.widgets.breadcrumb_path_bar import BreadcrumbPathBar

        # 创建核心节点图（根图和三个子图）
        self.node_graph = NodeGraph("root")
        
        # 创建三个主要路径的子图
        self.obj_graph = NodeGraph("obj", parent=self.node_graph)
        self.vis_graph = NodeGraph("vis", parent=self.node_graph)
        self.train_graph = NodeGraph("train", parent=self.node_graph)
        
        # 添加到根图的子图字典
        self.node_graph.subgraphs["obj"] = self.obj_graph
        self.node_graph.subgraphs["vis"] = self.vis_graph
        self.node_graph.subgraphs["train"] = self.train_graph
        
        # 创建三个根节点（/obj, /vis, /train）
        from core.nodes.context.root_nodes import ObjRootNode, VisRootNode, TrainRootNode
        
        self.obj_root_node = ObjRootNode(name="obj", node_graph=self.obj_graph)
        self.vis_root_node = VisRootNode(name="vis", node_graph=self.vis_graph)
        self.train_root_node = TrainRootNode(name="train", node_graph=self.train_graph)
        
        # 添加根节点到各自的图中
        self.obj_graph.add_node(self.obj_root_node)
        self.vis_graph.add_node(self.vis_root_node)
        self.train_graph.add_node(self.train_root_node)
        
        # 设置根节点位置（居中显示）
        self.obj_root_node.position = (0, 0)
        self.vis_root_node.position = (0, 0)
        self.train_root_node.position = (0, 0)
        
        # 日志记录根节点创建
        logger.info(f"根节点创建完成 - obj: {self.obj_root_node.name}, vis: {self.vis_root_node.name}, train: {self.train_root_node.name}")
        logger.info(f"obj 图节点数: {len(self.obj_graph.nodes)}, vis 图节点数: {len(self.vis_graph.nodes)}, train 图节点数: {len(self.train_graph.nodes)}")
        
        # 当前活动图（默认为 obj）
        self.current_graph = self.obj_graph
        self.current_path = "/obj"

        # 创建撤销栈（T055: 集成UndoStack到MainWindow）
        self.undo_stack = UndoStack(max_size=100)

        # 创建图形场景和视图
        self.graphics_scene = NodeGraphicsScene(self)
        self.graphics_view = NodeGraphicsView(self.graphics_scene, self)

        # 连接信号
        self.graphics_view.node_create_requested.connect(self._on_node_create_requested)
        self.graphics_scene.connection_created.connect(self._on_connection_created)
        self.graphics_scene.connection_deleted.connect(self._on_connection_deleted)
        self.graphics_scene.node_double_clicked.connect(self._on_node_double_clicked)
        self.graphics_scene.selectionChanged.connect(self._on_selection_changed)
        # 新增：节点删除和打包信号
        self.graphics_scene.node_delete_requested.connect(self._on_nodes_delete_requested)
        self.graphics_scene.pack_subnet_requested.connect(self._on_pack_subnet_requested)

        # 创建面包屑路径导航栏
        self.path_nav_bar = BreadcrumbPathBar(self)
        self.path_nav_bar.path_changed.connect(self._on_path_changed)
        # 同步面包屑导航栏的初始路径
        self.path_nav_bar.current_path = self.current_path
        self.path_nav_bar._rebuild_breadcrumb()

        # 创建中央控件布局
        central_widget = QWidget()
        central_layout = QVBoxLayout(central_widget)
        central_layout.setContentsMargins(0, 0, 0, 0)
        central_layout.setSpacing(0)
        
        # 添加路径导航栏
        central_layout.addWidget(self.path_nav_bar)
        
        # 添加图形视图
        central_layout.addWidget(self.graphics_view)
        
        # 设置中央控件
        self.setCentralWidget(central_widget)

        # 保存节点图形项的映射（按路径分组）
        self.node_graphics_items = {}  # {node: graphics_item}
        # 保存连接图形项的映射
        self.connection_graphics_items = {}  # {connection: graphics_item}
        
        # 同步视图的路径上下文
        self.graphics_view.current_path = self.current_path

        # 训练桥接器（延迟初始化）
        self.training_bridge = None
        self.visualization_panel = None

    def _create_menus(self):
        """创建菜单栏"""
        menubar = self.menuBar()

        # 文件菜单
        file_menu = menubar.addMenu("文件(&F)")

        # 新建项目
        new_action = QAction("新建项目(&N)", self)
        new_action.setShortcut(QKeySequence.StandardKey.New)
        new_action.triggered.connect(self._on_new_project)
        file_menu.addAction(new_action)

        # 打开项目
        open_action = QAction("打开项目(&O)", self)
        open_action.setShortcut(QKeySequence.StandardKey.Open)
        open_action.triggered.connect(self._on_open_project)
        file_menu.addAction(open_action)

        file_menu.addSeparator()

        # 保存项目
        save_action = QAction("保存(&S)", self)
        save_action.setShortcut(QKeySequence.StandardKey.Save)
        save_action.triggered.connect(self._on_save_project)
        file_menu.addAction(save_action)

        # 另存为
        save_as_action = QAction("另存为(&A)...", self)
        save_as_action.setShortcut(QKeySequence.StandardKey.SaveAs)
        save_as_action.triggered.connect(self._on_save_project_as)
        file_menu.addAction(save_as_action)

        file_menu.addSeparator()

        # 退出
        exit_action = QAction("退出(&X)", self)
        exit_action.setShortcut(QKeySequence.StandardKey.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # 编辑菜单
        edit_menu = menubar.addMenu("编辑(&E)")

        # T055: 撤销/重做动作连接到UndoStack
        self.undo_action = QAction("撤销(&U)", self)
        self.undo_action.setShortcut(QKeySequence.StandardKey.Undo)
        self.undo_action.setEnabled(False)
        self.undo_action.triggered.connect(self._on_undo)
        edit_menu.addAction(self.undo_action)

        self.redo_action = QAction("重做(&R)", self)
        self.redo_action.setShortcut(QKeySequence.StandardKey.Redo)
        self.redo_action.setEnabled(False)
        self.redo_action.triggered.connect(self._on_redo)
        edit_menu.addAction(self.redo_action)

        edit_menu.addSeparator()

        cut_action = QAction("剪切(&T)", self)
        cut_action.setShortcut(QKeySequence.StandardKey.Cut)
        cut_action.setEnabled(False)
        edit_menu.addAction(cut_action)

        copy_action = QAction("复制(&C)", self)
        copy_action.setShortcut(QKeySequence.StandardKey.Copy)
        copy_action.setEnabled(False)
        edit_menu.addAction(copy_action)

        paste_action = QAction("粘贴(&P)", self)
        paste_action.setShortcut(QKeySequence.StandardKey.Paste)
        paste_action.setEnabled(False)
        edit_menu.addAction(paste_action)

        # 视图菜单
        view_menu = menubar.addMenu("视图(&V)")
        
        # 注意：P键切换属性面板由PropertiesPanel的全局事件过滤器处理（T146C）
        # 这里不再设置快捷键，避免冲突
        self.toggle_properties_action = QAction("切换属性面板", self)
        self.toggle_properties_action.triggered.connect(self._on_toggle_properties)
        view_menu.addAction(self.toggle_properties_action)
        
        view_menu.addSeparator()

        # 将在 _create_dock_widgets 后填充

        # 调试菜单
        debug_menu = menubar.addMenu("调试(&D)")
        
        debug_settings_action = QAction("调试设置(&S)...", self)
        debug_settings_action.triggered.connect(self._on_debug_settings)
        debug_menu.addAction(debug_settings_action)
        
        debug_menu.addSeparator()
        
        # 快速启用/禁用节点调试
        self.node_debug_action = QAction("节点调试", self)
        self.node_debug_action.setCheckable(True)
        self.node_debug_action.setChecked(False)
        self.node_debug_action.triggered.connect(self._on_toggle_node_debug)
        debug_menu.addAction(self.node_debug_action)
        
        # 快速启用/禁用打包调试
        self.pack_debug_action = QAction("打包调试", self)
        self.pack_debug_action.setCheckable(True)
        self.pack_debug_action.setChecked(False)
        self.pack_debug_action.triggered.connect(self._on_toggle_pack_debug)
        debug_menu.addAction(self.pack_debug_action)
        
        # 快速启用/禁用序列化调试
        self.serial_debug_action = QAction("序列化调试", self)
        self.serial_debug_action.setCheckable(True)
        self.serial_debug_action.setChecked(False)
        self.serial_debug_action.triggered.connect(self._on_toggle_serial_debug)
        debug_menu.addAction(self.serial_debug_action)

        # 帮助菜单
        help_menu = menubar.addMenu("帮助(&H)")

        about_action = QAction("关于(&A)", self)
        about_action.triggered.connect(self._on_about)
        help_menu.addAction(about_action)

        # 保存菜单引用
        self.view_menu = view_menu
        self.debug_menu = debug_menu

    def _create_toolbars(self):
        """创建工具栏"""
        # 主工具栏
        main_toolbar = QToolBar("主工具栏")
        main_toolbar.setObjectName("MainToolBar")
        self.addToolBar(main_toolbar)

        # 添加工具按钮（占位）
        new_action = QAction("新建", self)
        new_action.triggered.connect(self._on_new_project)
        main_toolbar.addAction(new_action)

        open_action = QAction("打开", self)
        open_action.triggered.connect(self._on_open_project)
        main_toolbar.addAction(open_action)

        save_action = QAction("保存", self)
        save_action.triggered.connect(self._on_save_project)
        main_toolbar.addAction(save_action)

        main_toolbar.addSeparator()

        run_action = QAction("运行", self)
        run_action.triggered.connect(self._on_run_graph)
        main_toolbar.addAction(run_action)

        main_toolbar.addSeparator()

        # 训练控制按钮 (T085)
        self.train_start_action = QAction("开始训练", self)
        self.train_start_action.triggered.connect(self._on_train_start)
        main_toolbar.addAction(self.train_start_action)

        self.train_pause_action = QAction("暂停训练", self)
        self.train_pause_action.triggered.connect(self._on_train_pause)
        self.train_pause_action.setEnabled(False)
        main_toolbar.addAction(self.train_pause_action)

        self.train_stop_action = QAction("停止训练", self)
        self.train_stop_action.triggered.connect(self._on_train_stop)
        self.train_stop_action.setEnabled(False)
        main_toolbar.addAction(self.train_stop_action)

        main_toolbar.addSeparator()

        # 可视化面板按钮
        self.viz_action = QAction("可视化面板", self)
        self.viz_action.triggered.connect(self._on_show_visualization)
        main_toolbar.addAction(self.viz_action)

    def _create_status_bar(self):
        """创建状态栏"""
        statusbar = QStatusBar()
        self.setStatusBar(statusbar)

        # 状态标签
        self.status_label = QLabel("就绪")
        statusbar.addWidget(self.status_label)

        # 训练进度标签 (T086)
        self.train_progress_label = QLabel("训练: 未开始")
        self.train_progress_label.setStyleSheet("color: #888; font-size: 12px;")
        statusbar.addPermanentWidget(self.train_progress_label)

        # 右侧信息
        self.info_label = QLabel("")
        statusbar.addPermanentWidget(self.info_label)

    def _create_dock_widgets(self):
        """创建停靠窗口"""
        # 节点库面板（左侧）- T049: 使用NodePalettePanel
        from ui.panels.node_palette_panel import NodePalettePanel
        
        node_library_dock = QDockWidget("节点库", self)
        node_library_dock.setObjectName("NodeLibraryDock")
        
        # 创建节点面板
        self.node_palette_panel = NodePalettePanel(self)
        # 设置初始上下文路径（过滤可用节点）- 强制刷新以确保节点已注册
        self.node_palette_panel.set_context_path(self.current_path, force_refresh=True)
        # 连接双击创建信号（在画布中心创建）
        self.node_palette_panel.node_create_requested.connect(self._on_node_create_from_palette)
        
        node_library_dock.setWidget(self.node_palette_panel)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, node_library_dock)

        # 属性面板（浮动窗口，不再使用停靠窗口）
        from ui.panels.properties_panel import PropertiesPanel
        self.properties_panel = PropertiesPanel(self)
        # 默认隐藏，按P键显示
        self.properties_panel.hide()

        # 控制台面板（底部）
        console_dock = QDockWidget("控制台", self)
        console_dock.setObjectName("ConsoleDock")
        console_widget = QLabel("Python 控制台\n(日志和输出将在此显示)")
        console_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
        console_widget.setStyleSheet("background-color: #333; color: #888;")
        console_dock.setWidget(console_widget)
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, console_dock)

        # 添加到视图菜单
        self.view_menu.addAction(node_library_dock.toggleViewAction())
        self.view_menu.addAction(console_dock.toggleViewAction())

        # 保存引用
        self.dock_widgets = {
            'node_library': node_library_dock,
            'console': console_dock
        }
    
    @Slot()
    def _on_toggle_properties(self):
        """切换属性面板显示/隐藏 - T146: 使用属性面板自己的toggle方法"""
        self.properties_panel.toggle_visibility()

    @Slot()
    def _on_new_project(self):
        """新建项目"""
        logger.info("Creating new project")
        self.status_label.setText("新建项目")
        QMessageBox.information(
            self,
            "新建项目",
            "新建项目功能将在后续实现"
        )

    @Slot()
    def _on_open_project(self):
        """打开项目"""
        logger.info("Opening project")
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "打开项目",
            "",
            "PNNE 项目文件 (*.pnne);;所有文件 (*)"
        )

        if file_path:
            logger.info(f"Selected file: {file_path}")
            self._load_from_file(file_path)

    @Slot()
    def _on_save_project(self):
        """保存项目"""
        if self.current_project_path:
            self._save_to_file(self.current_project_path)
        else:
            self._on_save_project_as()

    @Slot()
    def _on_save_project_as(self):
        """另存为项目"""
        logger.info("Save project as")
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "另存为",
            "",
            "PNNE 项目文件 (*.pnne);;所有文件 (*)"
        )

        if file_path:
            logger.info(f"Save to: {file_path}")
            self.current_project_path = file_path
            self._save_to_file(file_path)
    
    def _save_to_file(self, file_path: str):
        """
        保存项目到文件
        
        Args:
            file_path: 文件路径
        """
        from core.serialization.serializer import Serializer
        
        try:
            # 保存项目
            success = Serializer.save_to_file(self.node_graph, file_path)
            
            if success:
                self.status_label.setText(f"✅ 项目已保存: {file_path}")
                self.project_saved.emit(file_path)
                QMessageBox.information(
                    self,
                    "保存成功",
                    f"项目已成功保存到:\n{file_path}\n\n"
                    f"节点数: {len(self.node_graph.nodes)}\n"
                    f"连接数: {len(self.node_graph.connections)}"
                )
            else:
                self.status_label.setText(f"❌ 保存失败")
                QMessageBox.warning(
                    self,
                    "保存失败",
                    f"无法保存项目到:\n{file_path}"
                )
                
        except Exception as e:
            logger.error(f"Save error: {e}")
            self.status_label.setText(f"❌ 保存错误: {e}")
            QMessageBox.critical(
                self,
                "保存错误",
                f"保存项目时发生错误:\n{e}"
            )
    
    def _load_from_file(self, file_path: str):
        """
        从文件加载项目
        
        Args:
            file_path: 文件路径
        """
        from core.serialization.serializer import Serializer
        from core.base import NodeFactory, NodeGraph
        from ui.graphics.node_graphics_item_v2 import NodeGraphicsItemV2
        from ui.graphics.connection_graphics_item import ConnectionGraphicsItem
        from core.base.connection import Connection
        
        try:
            logger.info(f"Loading project from: {file_path}")
            self.status_label.setText(f"加载项目: {file_path}")
            
            # 从文件加载数据
            project_data = Serializer.load_from_file(file_path)
            
            if project_data is None:
                self.status_label.setText("❌ 加载失败")
                QMessageBox.warning(
                    self,
                    "加载失败",
                    f"无法加载项目文件:\n{file_path}"
                )
                return
            
            graph_data = project_data["graph"]
            
            # 第一步：清空当前场景和节点图
            logger.info("Clearing current graph...")
            self._clear_scene()
            
            # 第二步：递归反序列化节点图（包括子图）
            logger.info("Deserializing graph with subgraphs...")
            self._deserialize_graph_recursive(graph_data, self.node_graph)
            
            # 第三步：重新初始化子图引用
            self._reinitialize_subgraphs()
            
            # 第四步：创建当前图的节点图形项
            logger.info(f"Creating graphics items for current graph: {self.current_path}")
            self._display_graph_nodes()
            
            # 更新状态
            self.current_project_path = file_path
            self.status_label.setText(f"✅ 项目已加载: {file_path}")
            self.project_opened.emit(file_path)
            
            logger.info("Project loaded successfully!")
            
            # 统计总节点数和连接数
            total_nodes, total_conns = self._count_all_nodes()
            
            # 显示成功消息
            QMessageBox.information(
                self,
                "加载成功",
                f"项目已成功加载:\n{file_path}\n\n"
                f"总节点数: {total_nodes}\n"
                f"总连接数: {total_conns}"
            )
            
        except Exception as e:
            logger.error(f"Load error: {e}")
            import traceback
            logger.error(traceback.format_exc())
            self.status_label.setText(f"❌ 加载错误: {e}")
            QMessageBox.critical(
                self,
                "加载错误",
                f"加载项目时发生错误:\n{e}"
            )
    
    def _deserialize_graph_recursive(self, graph_data: dict, node_graph):
        """
        递归反序列化节点图（包括所有子图）
        
        Args:
            graph_data: 图数据字典
            node_graph: 目标节点图对象
        """
        from core.base import NodeFactory, NodeGraph
        from core.base.connection import Connection
        from core.nodes.subnet.subnet_node import SubnetNode
        
        logger.info(f"[DESERIALIZE] Deserializing graph: {graph_data.get('name', 'unknown')}")
        
        # 1. 反序列化当前层的节点
        for node_data in graph_data.get("nodes", []):
            try:
                node_type = node_data.get("type")
                node_name = node_data.get("name")
                node_id = node_data.get("id")
                position = node_data.get("position", [0.0, 0.0])
                properties = node_data.get("properties", {})
                instance_parameters = node_data.get("instance_parameters", {})
                
                logger.info(f"[DESERIALIZE] Creating node: {node_name} (type={node_type})")
                
                # 创建节点
                node = NodeFactory.create_node(
                    node_type=node_type,
                    name=node_name,
                    node_graph=node_graph
                )
                
                # 恢复ID和位置
                node.id = node_id
                node.position = tuple(position)
                
                # 恢复属性
                for key, value in properties.items():
                    node.set_property(key, value)
                
                # 恢复实例参数
                if instance_parameters:
                    node.instance_parameters = instance_parameters.copy()
                
                # 添加到节点图
                node_graph.add_node(node)
                
                logger.info(f"[DESERIALIZE]   ✓ Node created: {node_name}")
                
            except Exception as e:
                logger.error(f"[DESERIALIZE]   ✗ Failed to create node: {e}")
                import traceback
                logger.error(traceback.format_exc())
        
        # 2. 反序列化当前层的连接
        for conn_data in graph_data.get("connections", []):
            try:
                source_node_id = conn_data.get("source_node_id")
                target_node_id = conn_data.get("target_node_id")
                source_pin_name = conn_data.get("source_pin")
                target_pin_name = conn_data.get("target_pin")
                conn_id = conn_data.get("id")
                
                # 使用ID查找节点
                source_node = node_graph.get_node_by_id(source_node_id) if source_node_id else None
                target_node = node_graph.get_node_by_id(target_node_id) if target_node_id else None
                
                # 回退到名称查找
                if source_node is None:
                    source_path = conn_data.get("source_node", "")
                    source_name = source_path.split('/')[-1] if '/' in source_path else source_path
                    source_node = node_graph.get_node(source_name)
                
                if target_node is None:
                    target_path = conn_data.get("target_node", "")
                    target_name = target_path.split('/')[-1] if '/' in target_path else target_path
                    target_node = node_graph.get_node(target_name)
                
                if source_node and target_node:
                    source_pin = source_node.get_output_pin(source_pin_name)
                    target_pin = target_node.get_input_pin(target_pin_name)
                    
                    if source_pin and target_pin:
                        conn = Connection(source_pin, target_pin)
                        conn.id = conn_id
                        node_graph.add_connection(conn)
                        logger.info(f"[DESERIALIZE]   ✓ Connection: {source_node.name}.{source_pin_name} -> {target_node.name}.{target_pin_name}")
                    else:
                        logger.warning(f"[DESERIALIZE]   ✗ Pins not found: {source_pin_name}, {target_pin_name}")
                else:
                    logger.warning(f"[DESERIALIZE]   ✗ Nodes not found: source={source_node}, target={target_node}")
                    
            except Exception as e:
                logger.error(f"[DESERIALIZE]   ✗ Failed to create connection: {e}")
        
        # 3. 递归反序列化子图
        for subgraph_name, subgraph_data in graph_data.get("subgraphs", {}).items():
            try:
                logger.info(f"[DESERIALIZE] Creating subgraph: {subgraph_name}")
                
                # 创建子图对象
                subgraph = NodeGraph(subgraph_name, parent=node_graph)
                
                # 递归反序列化子图
                self._deserialize_graph_recursive(subgraph_data, subgraph)
                
                # 添加到父图
                node_graph.subgraphs[subgraph_name] = subgraph
                
                logger.info(f"[DESERIALIZE]   ✓ Subgraph created: {subgraph_name} with {len(subgraph.nodes)} nodes")
                
            except Exception as e:
                logger.error(f"[DESERIALIZE]   ✗ Failed to create subgraph {subgraph_name}: {e}")
                import traceback
                logger.error(traceback.format_exc())
        
        # 4. 恢复SubnetNode的内部子图引用
        for node in node_graph.nodes.values():
            if node.node_type == "subnet":
                # 检查是否有对应的子图
                if node.name in node_graph.subgraphs:
                    # 恢复子图引用
                    node._subgraph = node_graph.subgraphs[node.name]
                    node._subgraph.parent = node_graph
                    logger.info(f"[DESERIALIZE]   ✓ Restored subnet '{node.name}' subgraph reference")
    
    def _count_all_nodes(self):
        """统计所有节点和连接数量（包括子图）"""
        def count_recursive(node_graph):
            total_nodes = len(node_graph.nodes)
            total_conns = len(node_graph.connections)
            for subgraph in node_graph.subgraphs.values():
                sub_nodes, sub_conns = count_recursive(subgraph)
                total_nodes += sub_nodes
                total_conns += sub_conns
            return total_nodes, total_conns
        
        return count_recursive(self.node_graph)
    
    def _clear_scene(self):
        """清空当前场景和节点图"""
        logger.info("Clearing scene...")
        
        try:
            # 清空连接图形项
            for connection_item in list(self.connection_graphics_items.values()):
                self.graphics_scene.removeItem(connection_item)
            self.connection_graphics_items.clear()
            
            # 清空节点图形项
            for node_item in list(self.node_graphics_items.values()):
                self.graphics_scene.removeItem(node_item)
            self.node_graphics_items.clear()
            
            # 清空节点图
            self.node_graph.clear()
            
            logger.info("Scene cleared successfully")
            
        except Exception as e:
            logger.error(f"Error clearing scene: {e}")
            import traceback
            logger.error(traceback.format_exc())
    
    def _reinitialize_subgraphs(self):
        """
        重新初始化子图引用
        
        在加载项目后调用，确保 obj, vis, train 三个主要子图的引用正确
        """
        from core.base import NodeGraph
        
        logger.info("Reinitializing subgraphs...")
        
        # 检查 subgraphs 中是否有 obj, vis, train
        if "obj" in self.node_graph.subgraphs:
            self.obj_graph = self.node_graph.subgraphs["obj"]
            logger.info(f"  obj_graph: {len(self.obj_graph.nodes)} nodes")
        else:
            # 如果没有，创建新的子图
            self.obj_graph = NodeGraph("obj", parent=self.node_graph)
            self.node_graph.subgraphs["obj"] = self.obj_graph
            logger.info("  Created new obj_graph")
        
        if "vis" in self.node_graph.subgraphs:
            self.vis_graph = self.node_graph.subgraphs["vis"]
            logger.info(f"  vis_graph: {len(self.vis_graph.nodes)} nodes")
        else:
            self.vis_graph = NodeGraph("vis", parent=self.node_graph)
            self.node_graph.subgraphs["vis"] = self.vis_graph
            logger.info("  Created new vis_graph")
        
        if "train" in self.node_graph.subgraphs:
            self.train_graph = self.node_graph.subgraphs["train"]
            logger.info(f"  train_graph: {len(self.train_graph.nodes)} nodes")
        else:
            self.train_graph = NodeGraph("train", parent=self.node_graph)
            self.node_graph.subgraphs["train"] = self.train_graph
            logger.info("  Created new train_graph")
        
        # 确保当前图指向有效的子图
        if self.current_path == "/obj":
            self.current_graph = self.obj_graph
        elif self.current_path == "/vis":
            self.current_graph = self.vis_graph
        elif self.current_path == "/train":
            self.current_graph = self.train_graph
        else:
            # 默认使用 obj
            self.current_graph = self.obj_graph
            self.current_path = "/obj"
        
        # 更新面包屑导航栏
        self.path_nav_bar.set_path(self.current_path)
        
        logger.info(f"Subgraphs reinitialized. Current path: {self.current_path}")

    @Slot()
    def _on_run_graph(self):
        """运行图"""
        logger.info("Running graph")
        self.status_label.setText("执行节点图...")
        QMessageBox.information(
            self,
            "运行",
            "图执行功能将在后续实现"
        )

    @Slot()
    def _on_about(self):
        """关于对话框"""
        QMessageBox.about(
            self,
            "关于 PNNE",
            "<h3>PNNE - PyTorch Neural Network Editor</h3>"
            "<p>版本: 0.1.0</p>"
            "<p>一个基于节点的可视化深度学习模型编辑器</p>"
            "<p>灵感来自 Houdini</p>"
            "<p><a href='https://github.com/yourusername/pytorch-node-editor'>"
            "GitHub 仓库</a></p>"
        )
    
    @Slot()
    def _on_debug_settings(self):
        """打开调试设置对话框"""
        from ui.dialogs.debug_settings_dialog import DebugSettingsDialog
        
        dialog = DebugSettingsDialog(self)
        result = dialog.exec()
        
        # 更新菜单项状态
        if result == QDialog.DialogCode.Accepted:
            self._update_debug_menu_states()
    
    def _update_debug_menu_states(self):
        """更新调试菜单项状态"""
        from core.debug import get_debug_manager, DebugCategory
        
        manager = get_debug_manager()
        self.node_debug_action.setChecked(manager.is_enabled(DebugCategory.NODE))
        self.pack_debug_action.setChecked(manager.is_enabled(DebugCategory.PACK))
        self.serial_debug_action.setChecked(manager.is_enabled(DebugCategory.SERIALIZATION))
    
    @Slot()
    def _on_toggle_node_debug(self):
        """切换节点调试"""
        from core.debug import get_debug_manager, DebugCategory
        
        manager = get_debug_manager()
        new_state = manager.toggle_category(DebugCategory.NODE)
        self.node_debug_action.setChecked(new_state)
        self.status_label.setText(f"节点调试: {'启用' if new_state else '禁用'}")
    
    @Slot()
    def _on_toggle_pack_debug(self):
        """切换打包调试"""
        from core.debug import get_debug_manager, DebugCategory
        
        manager = get_debug_manager()
        new_state = manager.toggle_category(DebugCategory.PACK)
        self.pack_debug_action.setChecked(new_state)
        self.status_label.setText(f"打包调试: {'启用' if new_state else '禁用'}")
    
    @Slot()
    def _on_toggle_serial_debug(self):
        """切换序列化调试"""
        from core.debug import get_debug_manager, DebugCategory
        
        manager = get_debug_manager()
        new_state = manager.toggle_category(DebugCategory.SERIALIZATION)
        self.serial_debug_action.setChecked(new_state)
        self.status_label.setText(f"序列化调试: {'启用' if new_state else '禁用'}")
    
    @Slot()
    def _on_undo(self):
        """撤销操作（T055: UndoStack集成）"""
        if self.undo_stack.can_undo():
            success = self.undo_stack.undo()
            if success:
                undo_text = self.undo_stack.get_undo_text()
                logger.info(f"↶ 撤销: {undo_text}")
                self.status_label.setText(f"↶ 撤销: {undo_text or '上一操作'}")
                self._update_undo_redo_actions()
            else:
                logger.error("撤销失败")
                self.status_label.setText("❌ 撤销失败")
        else:
            logger.info("无可撤销的操作")
    
    @Slot()
    def _on_redo(self):
        """重做操作（T055: UndoStack集成）"""
        if self.undo_stack.can_redo():
            success = self.undo_stack.redo()
            if success:
                redo_text = self.undo_stack.get_redo_text()
                logger.info(f"↷ 重做: {redo_text}")
                self.status_label.setText(f"↷ 重做: {redo_text or '下一操作'}")
                self._update_undo_redo_actions()
            else:
                logger.error("重做失败")
                self.status_label.setText("❌ 重做失败")
        else:
            logger.info("无可重做的操作")
    
    def _update_undo_redo_actions(self):
        """更新撤销/重做菜单项的启用状态（T055）"""
        # 更新撤销动作
        if self.undo_stack.can_undo():
            self.undo_action.setEnabled(True)
            undo_text = self.undo_stack.get_undo_text()
            self.undo_action.setText(f"撤销 {undo_text}" if undo_text else "撤销(&U)")
        else:
            self.undo_action.setEnabled(False)
            self.undo_action.setText("撤销(&U)")
        
        # 更新重做动作
        if self.undo_stack.can_redo():
            self.redo_action.setEnabled(True)
            redo_text = self.undo_stack.get_redo_text()
            self.redo_action.setText(f"重做 {redo_text}" if redo_text else "重做(&R)")
        else:
            self.redo_action.setEnabled(False)
            self.redo_action.setText("重做(&R)")

    @Slot(str)
    def _on_path_changed(self, path: str):
        """
        处理路径切换
        
        Args:
            path: 新路径（/obj, /vis, /train）
        """
        logger.info(f"Switching path: {self.current_path} -> {path}")
        
        # 获取对应的节点图
        if path == "/obj":
            new_graph = self.obj_graph
        elif path == "/vis":
            new_graph = self.vis_graph
        elif path == "/train":
            new_graph = self.train_graph
        else:
            logger.warning(f"Unknown path: {path}")
            return
        
        # 如果路径没有变化，直接返回
        if new_graph == self.current_graph:
            return
        
        # 清空当前场景显示的节点
        self._clear_scene_display()
        
        # 更新当前图和路径
        self.current_graph = new_graph
        self.current_path = path
        
        # 更新视图的路径上下文（用于右键菜单过滤）
        self.graphics_view.current_path = path
        
        # 更新节点面板的上下文路径（过滤可用节点）
        if hasattr(self, 'node_palette_panel'):
            self.node_palette_panel.set_context_path(path)
        
        # 显示新图中的所有节点
        self._display_graph_nodes()
        logger.info(f"Path switched to: {path}, 节点数: {len(self.current_graph.nodes)}")
        self.status_label.setText(f"切换到路径: {path}")
    
    @Slot(object)
    def _on_node_double_clicked(self, node):
        """
        处理节点双击事件 - 进入容器节点
        
        Args:
            node: 被双击的节点对象
        """
        from core.base.node import NodeCategory
        
        logger.info(f"[DOUBLE CLICK] Node: {node.name}, type: {node.node_type}, category: {node.node_category}")
        logger.info(f"[DOUBLE CLICK] Current path: {self.current_path}")
        
        # 根节点可以进入
        if node.node_category == NodeCategory.CONTEXT:
            # 根据根节点类型确定新路径
            new_path = None
            if node.node_type == "root.obj":
                new_path = "/obj"
            elif node.node_type == "root.vis":
                new_path = "/vis"
            elif node.node_type == "root.train":
                new_path = "/train"
            
            if new_path:
                if new_path == self.current_path:
                    logger.info(f"已在路径 {new_path} 中")
                    self.status_label.setText(f"已在路径: {node.display_name}")
                else:
                    logger.info(f"Entering root node: {node.name} → {new_path}")
                    # 更新路径导航栏（会触发 _on_path_changed）
                    self.path_nav_bar.set_path(new_path)
                    self.status_label.setText(f"进入: {node.display_name}")
            else:
                logger.warning(f"Unknown root node type: {node.node_type}")
        
        # SubnetNode 也可以进入
        elif node.node_type == "subnet":
            logger.info(f"Entering subnet: {node.name}")
            self._enter_subnet(node)
        
        else:
            logger.info(f"Node {node.name} is not a container node, cannot enter")
    
    def _enter_subnet(self, subnet_node):
        """
        进入子网络
        
        Args:
            subnet_node: SubnetNode 实例
        """
        from ui.graphics.node_graphics_item_v2 import NodeGraphicsItemV2
        from ui.graphics.connection_graphics_item import ConnectionGraphicsItem
        
        logger.info(f"Entering subnet: {subnet_node.name}")
        
        # 保存当前路径状态（用于返回）
        self._parent_path = self.current_path
        self._parent_graph = self.current_graph
        
        # 清空当前场景显示
        self._clear_scene_display()
        
        # 切换到子图
        self.current_graph = subnet_node.subgraph
        self.current_path = f"{self.current_path}/{subnet_node.name}"
        
        # 更新面包屑导航栏
        self.path_nav_bar.set_path(self.current_path)
        
        # 更新视图的路径上下文
        self.graphics_view.current_path = self.current_path
        
        # 更新节点面板的上下文路径
        if hasattr(self, 'node_palette_panel'):
            self.node_palette_panel.set_context_path(self.current_path)
        
        # 显示子图中的节点
        logger.info(f"[ENTER_SUBNET] 子图中的节点数: {len(subnet_node.subgraph.nodes)}")
        logger.info(f"[ENTER_SUBNET] 子图中的连接数: {len(subnet_node.subgraph.connections)}")
        
        # 先记录子图中所有节点的信息
        for node in subnet_node.subgraph.nodes.values():
            logger.info(f"[ENTER_SUBNET] 子图节点: name={node.name}, type={node.node_type}, id={id(node)}")
        
        for node in subnet_node.subgraph.nodes.values():
            if node not in self.node_graphics_items:
                graphics_item = NodeGraphicsItemV2(node)
                graphics_item.setPos(node.position[0], node.position[1])
                self.node_graphics_items[node] = graphics_item
                logger.info(f"[ENTER_SUBNET] 创建节点图形项: {node.name}, id={id(node)}")
            else:
                logger.info(f"[ENTER_SUBNET] 节点图形项已存在: {node.name}, id={id(node)}")
            
            graphics_item = self.node_graphics_items[node]
            if graphics_item.scene() != self.graphics_scene:
                self.graphics_scene.addItem(graphics_item)
                logger.info(f"Added subnet node to scene: {node.name}")
        
        # 显示子图中的连接
        logger.info(f"[ENTER_SUBNET] {subnet_node.name}: 处理 {len(subnet_node.subgraph.connections)} 条连接")
        for connection in subnet_node.subgraph.connections:
            if connection not in self.connection_graphics_items:
                source_node = connection.source_node
                target_node = connection.target_node
                
                logger.info(f"[ENTER_SUBNET] 连接: {source_node.name}.{connection.source_pin.name} -> {target_node.name}.{connection.target_pin.name}")
                logger.info(f"[ENTER_SUBNET] source_node in node_graphics_items: {source_node in self.node_graphics_items}")
                logger.info(f"[ENTER_SUBNET] target_node in node_graphics_items: {target_node in self.node_graphics_items}")
                
                source_node_item = self.node_graphics_items.get(source_node)
                target_node_item = self.node_graphics_items.get(target_node)
                
                if source_node_item and target_node_item:
                    source_pin_item = source_node_item.output_pin_items.get(connection.source_pin.name)
                    target_pin_item = target_node_item.input_pin_items.get(connection.target_pin.name)
                    
                    logger.info(f"[ENTER_SUBNET] source_pin_item: {source_pin_item}, target_pin_item: {target_pin_item}")
                    
                    if source_pin_item and target_pin_item:
                        connection_item = ConnectionGraphicsItem(
                            connection,
                            source_pin_item,
                            target_pin_item
                        )
                        self.connection_graphics_items[connection] = connection_item
                        logger.info(f"[ENTER_SUBNET] 连接图形项创建成功")
                    else:
                        logger.warning(f"[ENTER_SUBNET] 无法找到引脚图形项: source_pin={connection.source_pin.name}, target_pin={connection.target_pin.name}")
                        logger.warning(f"[ENTER_SUBNET] 可用输出引脚: {list(source_node_item.output_pin_items.keys())}")
                        logger.warning(f"[ENTER_SUBNET] 可用输入引脚: {list(target_node_item.input_pin_items.keys())}")
                else:
                    logger.warning(f"[ENTER_SUBNET] 无法找到节点图形项: source={source_node_item}, target={target_node_item}")
                    logger.warning(f"[ENTER_SUBNET] 当前node_graphics_items中的节点: {[n.name for n in self.node_graphics_items.keys()]}")
            else:
                logger.info(f"[ENTER_SUBNET] 连接已有图形项，跳过创建")
            
            connection_item = self.connection_graphics_items.get(connection)
            if connection_item and connection_item.scene() != self.graphics_scene:
                self.graphics_scene.addItem(connection_item)
        
        logger.info(f"Entered subnet: {subnet_node.name}, nodes: {len(subnet_node.subgraph.nodes)}")
        self.status_label.setText(f"进入子网络: {subnet_node.name}")
    
    
    def _clear_scene_display(self):
        """清空场景显示（但不删除节点图的数据）"""
        logger.info("Clearing scene display...")
        
        # 移除所有连接图形项
        for connection_item in list(self.connection_graphics_items.values()):
            if connection_item.scene() == self.graphics_scene:
                self.graphics_scene.removeItem(connection_item)
        
        # 移除所有节点图形项
        for node_item in list(self.node_graphics_items.values()):
            if node_item.scene() == self.graphics_scene:
                self.graphics_scene.removeItem(node_item)
        
        # 重要：清空映射字典，确保下次进入时创建新的图形项
        # 这避免了旧的图形项引用不正确的节点/引脚
        self.connection_graphics_items.clear()
        self.node_graphics_items.clear()
        
        logger.info("Scene display cleared (graphics items cleared)")
    
    def _display_graph_nodes(self):
        """显示当前图中的所有节点"""
        from ui.graphics.node_graphics_item_v2 import NodeGraphicsItemV2
        from ui.graphics.connection_graphics_item import ConnectionGraphicsItem
        from core.base.node import NodeCategory
        
        logger.info(f"Displaying nodes from: {self.current_path}")
        logger.info(f"Breadcrumb path: {self.path_nav_bar.current_path if hasattr(self, 'path_nav_bar') else 'N/A'}")
        logger.info(f"Nodes in current graph: {len(self.current_graph.nodes)}")
        
        # 显示节点
        for node in self.current_graph.nodes.values():
            # 跳过当前路径对应的根节点（根节点不应在其自己的路径下显示）
            if node.node_category == NodeCategory.CONTEXT:
                # 根据当前路径跳过对应的根节点
                if self.current_path == "/obj" and node.node_type == "root.obj":
                    logger.info(f"Skipping root node {node.name} in its own path /obj")
                    continue
                elif self.current_path == "/vis" and node.node_type == "root.vis":
                    logger.info(f"Skipping root node {node.name} in its own path /vis")
                    continue
                elif self.current_path == "/train" and node.node_type == "root.train":
                    logger.info(f"Skipping root node {node.name} in its own path /train")
                    continue
            
            # 检查是否已有图形项
            if node not in self.node_graphics_items:
                # 创建新的图形项
                graphics_item = NodeGraphicsItemV2(node)
                graphics_item.setPos(node.position[0], node.position[1])
                self.node_graphics_items[node] = graphics_item
            
            graphics_item = self.node_graphics_items[node]
            
            # 添加到场景（如果还没有）
            if graphics_item.scene() != self.graphics_scene:
                self.graphics_scene.addItem(graphics_item)
                logger.info(f"Added node to scene: {node.name}")
        
        # 显示连接
        for connection in self.current_graph.connections:
            # 检查是否已有图形项
            if connection not in self.connection_graphics_items:
                source_node_item = self.node_graphics_items.get(connection.source_node)
                target_node_item = self.node_graphics_items.get(connection.target_node)
                
                if source_node_item and target_node_item:
                    source_pin_item = source_node_item.output_pin_items.get(connection.source_pin.name)
                    target_pin_item = target_node_item.input_pin_items.get(connection.target_pin.name)
                    
                    if source_pin_item and target_pin_item:
                        connection_item = ConnectionGraphicsItem(
                            connection,
                            source_pin_item,
                            target_pin_item
                        )
                        self.connection_graphics_items[connection] = connection_item
            
            connection_item = self.connection_graphics_items.get(connection)
            
            # 添加到场景（如果还没有）
            if connection_item and connection_item.scene() != self.graphics_scene:
                self.graphics_scene.addItem(connection_item)
                logger.info("Added connection to scene")
        
        logger.info(f"Displayed {len(self.current_graph.nodes)} nodes and {len(self.current_graph.connections)} connections")

    def _on_node_create_requested(self, node_type: str, scene_pos):
        """处理创建节点请求（T055: 使用Command模式）"""
        from ui.graphics.node_graphics_item_v2 import NodeGraphicsItemV2
        from core.base import NodeFactory
        from core.undo.commands import AddNodeCommand
        
        try:
            # 在当前活动图中创建节点
            node = NodeFactory.create_node(node_type, node_graph=self.current_graph)
            
            # 设置节点位置
            node.position = (scene_pos.x(), scene_pos.y())
            
            # 创建图形项（使用V2版本）
            graphics_item = NodeGraphicsItemV2(node)
            graphics_item.setPos(scene_pos.x(), scene_pos.y())
            
            # 保存映射
            self.node_graphics_items[node] = graphics_item
            
            # 使用Command模式（支持撤销/重做）
            command = AddNodeCommand(
                self.current_graph,  # 使用当前图而不是根图
                node,
                self.graphics_scene,
                graphics_item
            )
            self.undo_stack.push(command)
            
            # 更新撤销/重做菜单
            self._update_undo_redo_actions()
            
            logger.info(f"Created node: {node.name} ({node_type}) at {self.current_path} ({scene_pos.x():.1f}, {scene_pos.y():.1f})")
            self.status_label.setText(f"创建节点: {node.display_name} ({node.name}) @ {self.current_path}")
            
        except Exception as e:
            logger.error(f"Failed to create node: {e}")
            self.status_label.setText(f"创建节点失败: {e}")
    
    @Slot(str)
    def _on_node_create_from_palette(self, node_type: str):
        """处理从面板双击创建节点（T049）- 在画布中心创建"""
        from PyQt6.QtCore import QPointF
        
        # 获取视图中心的场景坐标
        view_center = self.graphics_view.viewport().rect().center()
        scene_pos = self.graphics_view.mapToScene(view_center)
        
        logger.info(f"Creating node from palette: {node_type} at view center")
        
        # 调用统一的创建节点方法
        self._on_node_create_requested(node_type, scene_pos)
    
    def _on_connection_created(self, source_pin, target_pin):
        """处理创建连接请求（T055: 使用Command模式）"""
        from ui.graphics.connection_graphics_item import ConnectionGraphicsItem
        from core.base.connection import Connection
        from core.undo.commands import ConnectCommand
        
        logger.info(f"[MAIN] 收到创建连接信号")
        logger.info(f"[MAIN] 源引脚: {source_pin.full_path}")
        logger.info(f"[MAIN] 目标引脚: {target_pin.full_path}")
        
        try:
            # 创建核心连接
            connection = Connection(source_pin, target_pin)
            logger.info(f"[MAIN] 核心连接对象已创建")
            
            # 获取引脚图形项
            source_node_item = self.node_graphics_items.get(source_pin.node)
            target_node_item = self.node_graphics_items.get(target_pin.node)
            
            if source_node_item and target_node_item:
                # 找到对应的引脚图形项
                source_pin_item = source_node_item.output_pin_items.get(source_pin.name)
                target_pin_item = target_node_item.input_pin_items.get(target_pin.name)
                
                if source_pin_item and target_pin_item:
                    # 创建连接图形项
                    connection_item = ConnectionGraphicsItem(connection, source_pin_item, target_pin_item)
                    logger.info(f"[MAIN] 连接图形项已创建")
                    
                    # 保存映射
                    self.connection_graphics_items[connection] = connection_item
                    
                    # 使用Command模式（支持撤销/重做）
                    command = ConnectCommand(
                        self.current_graph,  # 使用当前图而不是根图
                        connection,
                        self.graphics_scene,
                        connection_item
                    )
                    self.undo_stack.push(command)
                    
                    # 更新撤销/重做菜单
                    self._update_undo_redo_actions()
                    
                    logger.info(f"[MAIN] ✅ 连接创建成功: {source_pin.full_path} → {target_pin.full_path}")
                    self.status_label.setText(f"创建连接: {source_pin.node.name}.{source_pin.name} → {target_pin.node.name}.{target_pin.name}")
                else:
                    logger.error("[MAIN] ❌ 找不到引脚图形项")
            else:
                logger.error("[MAIN] ❌ 找不到节点图形项")
                
        except Exception as e:
            logger.error(f"[MAIN] ❌ 创建连接失败: {e}")
            import traceback
            logger.error(traceback.format_exc())
            self.status_label.setText(f"创建连接失败: {e}")
    
    def _on_connection_deleted(self, connection):
        """处理删除连接请求（T055: 使用Command模式）"""
        from core.undo.commands import DisconnectCommand
        
        logger.info(f"[MAIN] 收到删除连接信号")
        logger.info(f"[MAIN] 连接: {connection.source_pin.full_path} → {connection.target_pin.full_path}")
        
        try:
            # 获取连接图形项
            connection_item = self.connection_graphics_items.get(connection)
            
            if connection_item:
                # 使用Command模式（支持撤销/重做）
                command = DisconnectCommand(
                    self.current_graph,  # 使用当前图而不是根图
                    connection,
                    self.graphics_scene,
                    connection_item
                )
                self.undo_stack.push(command)
                
                # 从映射中移除
                del self.connection_graphics_items[connection]
                
                # 更新引脚外观
                source_node_item = self.node_graphics_items.get(connection.source_pin.node)
                target_node_item = self.node_graphics_items.get(connection.target_pin.node)
                
                if source_node_item:
                    source_pin_item = source_node_item.output_pin_items.get(connection.source_pin.name)
                    if source_pin_item:
                        source_pin_item.update_appearance()
                        logger.info(f"[MAIN] 源引脚外观已更新")
                
                if target_node_item:
                    target_pin_item = target_node_item.input_pin_items.get(connection.target_pin.name)
                    if target_pin_item:
                        target_pin_item.update_appearance()
                        logger.info(f"[MAIN] 目标引脚外观已更新")
                
                # 更新撤销/重做菜单
                self._update_undo_redo_actions()
                
                logger.info(f"[MAIN] ✅ 连接删除成功")
                self.status_label.setText(f"删除连接: {connection.source_pin.node.name}.{connection.source_pin.name} → {connection.target_pin.node.name}.{connection.target_pin.name}")
            else:
                logger.warning("[MAIN] ⚠️ 未找到连接图形项")
                
        except Exception as e:
            logger.error(f"[MAIN] ❌ 删除连接失败: {e}")
            import traceback
            logger.error(traceback.format_exc())
            self.status_label.setText(f"删除连接失败: {e}")
    
    def _on_selection_changed(self):
        """处理选中项变化"""
        selected_items = self.graphics_scene.selectedItems()
        
        # 查找选中的节点图形项
        from ui.graphics.node_graphics_item_v2 import NodeGraphicsItemV2
        
        selected_node = None
        for item in selected_items:
            if isinstance(item, NodeGraphicsItemV2):
                selected_node = item.node
                break
        
        # 更新属性面板
        if hasattr(self, 'properties_panel'):
            self.properties_panel.set_node(selected_node)

    def closeEvent(self, event):
        """窗口关闭事件"""
        logger.info("Closing main window")
        # TODO: 检查未保存的更改
        event.accept()

    @Slot()
    def _on_train_start(self):
        """开始训练"""
        logger.info("Starting training")
        self.status_label.setText("训练开始...")
        # 延迟初始化训练桥接器
        if self.training_bridge is None:
            from bridge.training_bridge import TrainingBridge
            self.training_bridge = TrainingBridge(self.node_graph, self)
            self.training_bridge.progress_updated.connect(self._on_training_progress_updated)
        # 启动训练
        self.training_bridge.start_training()
        # 更新按钮状态
        self.train_start_action.setEnabled(False)
        self.train_pause_action.setEnabled(True)
        self.train_stop_action.setEnabled(True)

    @Slot()
    def _on_train_pause(self):
        """暂停/继续训练"""
        if self.training_bridge is None:
            return
        # 切换暂停状态
        if self.training_bridge.is_paused():
            logger.info("Resuming training")
            self.training_bridge.resume_training()
            self.train_pause_action.setText("暂停训练")
            self.status_label.setText("训练继续...")
        else:
            logger.info("Pausing training")
            self.training_bridge.pause_training()
            self.train_pause_action.setText("继续训练")
            self.status_label.setText("训练暂停...")

    @Slot()
    def _on_train_stop(self):
        """停止训练"""
        logger.info("Stopping training")
        if self.training_bridge is not None:
            self.training_bridge.stop_training()
        # 重置按钮状态
        self.train_start_action.setEnabled(True)
        self.train_pause_action.setEnabled(False)
        self.train_stop_action.setEnabled(False)
        self.train_pause_action.setText("暂停训练")
        self.status_label.setText("训练已停止")

    @Slot()
    def _on_show_visualization(self):
        """显示可视化面板"""
        logger.info("Showing visualization panel")
        # 延迟初始化可视化面板
        if self.visualization_panel is None:
            from ui.panels.visualization_panel import VisualizationPanel
            self.visualization_panel = VisualizationPanel(self)
        # 显示面板
        self.visualization_panel.show()
        self.visualization_panel.raise_()
        self.visualization_panel.activateWindow()

    @Slot(float, str)
    def _on_training_progress_updated(self, progress: float, status: str):
        """更新训练进度"""
        # 更新状态栏标签
        if progress >= 0:
            self.train_progress_label.setText(f"训练: {int(progress * 100)}% - {status}")
        else:
            self.train_progress_label.setText(f"训练: {status}")
        # 可以在这里更新进度条（如果有的话）
    
    @Slot(list)
    def _on_nodes_delete_requested(self, nodes):
        """
        处理节点删除请求
        
        Args:
            nodes: 要删除的节点列表
        """
        from core.undo.commands import DeleteNodeCommand
        
        logger.info(f"[MAIN] 删除 {len(nodes)} 个节点")
        
        for node in nodes:
            try:
                # 获取节点图形项
                node_item = self.node_graphics_items.get(node)
                
                if node_item:
                    # 创建删除命令
                    command = DeleteNodeCommand(
                        self.current_graph,
                        node,
                        self.graphics_scene,
                        node_item
                    )
                    self.undo_stack.push(command)
                    
                    # 从映射中移除
                    if node in self.node_graphics_items:
                        del self.node_graphics_items[node]
                    
                    logger.info(f"[MAIN] ✅ 节点已删除: {node.name}")
            
            except Exception as e:
                logger.error(f"[MAIN] ❌ 删除节点失败: {node.name} - {e}")
        
        # 更新撤销/重做菜单
        self._update_undo_redo_actions()
        self.status_label.setText(f"已删除 {len(nodes)} 个节点")
    
    @Slot(list)
    def _on_pack_subnet_requested(self, nodes):
        """
        处理打包为子网络请求
        
        使用JSON序列化/反序列化实现深拷贝，确保连接和表达式引用正确处理
        
        Args:
            nodes: 要打包的节点列表
        """
        from core.nodes.subnet.subnet_node import SubnetNode
        from core.nodes.subnet.subnet_pins import SubnetInputPinNode, SubnetOutputPinNode
        from ui.graphics.node_graphics_item_v2 import NodeGraphicsItemV2
        from ui.graphics.connection_graphics_item import ConnectionGraphicsItem
        from core.base.connection import Connection
        from core.base import NodeFactory
        import json
        import copy
        
        logger.info(f"[MAIN] 打包 {len(nodes)} 个节点为子网络（深拷贝模式）")
        
        if len(nodes) < 1:
            self.status_label.setText("需要选中至少1个节点才能打包")
            return
        
        try:
            # 1. 计算选中节点的边界和中心位置
            min_x = min(n.position[0] for n in nodes)
            max_x = max(n.position[0] for n in nodes)
            min_y = min(n.position[1] for n in nodes)
            max_y = max(n.position[1] for n in nodes)
            center_x = (min_x + max_x) / 2
            center_y = (min_y + max_y) / 2
            
            # 2. 识别头节点和尾节点
            head_nodes = []  # [(internal_node, internal_pin, external_connections)]
            tail_nodes = []  # [(internal_node, internal_pin, external_connections)]
            internal_connections = []
            all_connections_to_remove = []
            
            for node in nodes:
                # 检查输入引脚
                for pin_name, pin in node.input_pins.items():
                    external_conns = []
                    internal_conns = []
                    for conn in pin.connections:
                        source_node = conn.source_pin.node
                        if source_node not in nodes:
                            external_conns.append(conn)
                        else:
                            internal_conns.append(conn)
                    
                    if external_conns:
                        head_nodes.append((node, pin, external_conns))
                        all_connections_to_remove.extend(external_conns)
                    internal_connections.extend(internal_conns)
                
                # 检查输出引脚
                for pin_name, pin in node.output_pins.items():
                    external_conns = []
                    for conn in pin.connections:
                        target_node = conn.target_pin.node
                        if target_node not in nodes:
                            external_conns.append(conn)
                    
                    if external_conns:
                        tail_nodes.append((node, pin, external_conns))
                        all_connections_to_remove.extend(external_conns)
            
            logger.info(f"[MAIN] 头节点数: {len(head_nodes)}")
            logger.info(f"[MAIN] 尾节点数: {len(tail_nodes)}")
            logger.info(f"[MAIN] 内部连接: {len(internal_connections)}")
            
            # 3. 序列化选中的节点和内部连接（深拷贝）
            nodes_data = []
            for node in nodes:
                node_dict = node.to_dict()
                nodes_data.append(node_dict)
            
            # 序列化内部连接（使用节点ID，ID是稳定的不会因打包而改变）
            connections_data = []
            for conn in internal_connections:
                conn_dict = {
                    "id": conn.id,
                    "source_node_id": conn.source_pin.node.id,  # 使用ID（推荐）
                    "target_node_id": conn.target_pin.node.id,  # 使用ID（推荐）
                    "source_node": conn.source_pin.node.name,   # 保留名称作为备用（兼容）
                    "source_pin": conn.source_pin.name,
                    "target_node": conn.target_pin.node.name,   # 保留名称作为备用（兼容）
                    "target_pin": conn.target_pin.name
                }
                connections_data.append(conn_dict)
            
            graph_data = {"nodes": nodes_data, "connections": connections_data}
            logger.info(f"[MAIN] 序列化完成: {len(nodes_data)} 节点, {len(connections_data)} 连接")
            
            # 4. 创建SubnetNode
            input_count = max(len(head_nodes), 1)
            output_count = max(len(tail_nodes), 1)
            
            subnet_name = f"Subnet_{nodes[0].name.split('_')[0] if '_' in nodes[0].name else 'group'}"
            subnet_node = SubnetNode(
                name=subnet_name,
                node_graph=self.current_graph,
                input_count=input_count,
                output_count=output_count
            )
            subnet_node.position = (center_x, center_y)
            
            # 5. 深拷贝：反序列化节点到子图中
            node_name_mapping = {}  # old_name -> new_node
            
            for node_data in nodes_data:
                try:
                    node_type = node_data.get("type")
                    old_name = node_data.get("name")
                    
                    # 创建新节点（深拷贝）
                    new_node = NodeFactory.create_node(
                        node_type=node_type,
                        node_graph=subnet_node.subgraph
                    )
                    
                    # 重要：恢复原始名称（打包不应改变内部节点名称）
                    # NodeFactory.create_node 会自动生成新名称，我们需要强制恢复原始名称
                    if new_node.name != old_name:
                        logger.info(f"[MAIN] 恢复节点名称: {new_node.name} -> {old_name}")
                        new_node._name = old_name  # 直接设置内部属性
                    
                    # 恢复属性
                    new_node.id = node_data.get("id")
                    new_node.position = tuple(node_data.get("position", [0, 0]))
                    for key, value in node_data.get("properties", {}).items():
                        new_node.set_property(key, value)
                    
                    # 恢复实例参数
                    if "instance_parameters" in node_data:
                        new_node.instance_parameters = node_data["instance_parameters"].copy()
                    
                    # 特殊处理：SubnetNode 需要递归恢复子图
                    if node_type == "subnet":
                        # 重要：更新嵌套SubnetNode的subgraph的parent引用
                        # 确保路径计算正确
                        logger.info(f"[MAIN] 恢复前: new_node.name={new_node.name}, _subgraph.name={new_node._subgraph.name}")
                        new_node._subgraph.parent = subnet_node.subgraph
                        new_node._subgraph.name = new_node.name
                        logger.info(f"[MAIN] 恢复后: new_node.name={new_node.name}, _subgraph.name={new_node._subgraph.name}")
                        _restore_subnet_subgraph(new_node, node_data, logger)
                    
                    # 添加到子图
                    subnet_node.subgraph.add_node(new_node)
                    node_name_mapping[old_name] = new_node
                    
                    logger.info(f"[MAIN] 深拷贝节点: {old_name}")
                    
                except Exception as e:
                    logger.error(f"[MAIN] 深拷贝节点失败: {e}")
            
            # 6. 深拷贝：反序列化内部连接
            # 构建节点ID到新节点的映射（优先使用ID查找）
            node_id_mapping = {}  # old_id -> new_node
            for old_name, new_node in node_name_mapping.items():
                # 从原始节点数据中获取ID
                for node_data in nodes_data:
                    if node_data.get("name") == old_name:
                        old_id = node_data.get("id")
                        if old_id:
                            node_id_mapping[old_id] = new_node
                        break
            
            for conn_data in connections_data:
                try:
                    # 优先使用节点ID查找（推荐方式，ID是稳定的）
                    source_node = None
                    target_node = None
                    
                    if "source_node_id" in conn_data:
                        source_node = node_id_mapping.get(conn_data["source_node_id"])
                        target_node = node_id_mapping.get(conn_data["target_node_id"])
                    
                    # 回退到名称查找（兼容旧格式）
                    if source_node is None or target_node is None:
                        source_name = conn_data.get("source_node")
                        target_name = conn_data.get("target_node")
                        
                        if source_node is None:
                            source_node = node_name_mapping.get(source_name)
                        if target_node is None:
                            target_node = node_name_mapping.get(target_name)
                    
                    if source_node and target_node:
                        source_pin = source_node.get_output_pin(conn_data["source_pin"])
                        target_pin = target_node.get_input_pin(conn_data["target_pin"])
                        
                        if source_pin and target_pin:
                            conn = Connection(source_pin, target_pin)
                            conn.id = conn_data["id"]
                            subnet_node.subgraph.add_connection(conn)
                            logger.info(f"[MAIN] 深拷贝连接: {source_node.name}.{conn_data['source_pin']} -> {target_node.name}.{conn_data['target_pin']}")
                
                except Exception as e:
                    logger.error(f"[MAIN] 深拷贝连接失败: {e}")
            
            # 7. 使用已存在的SubnetInputPin节点并连接到头节点
            # SubnetNode在初始化时已创建默认的InputPin节点，直接使用它们
            input_pin_y_offset = -100
            existing_input_pins = [n for n in subnet_node.subgraph.nodes.values() if n.node_type == "subnet.input_pin"]
            existing_input_pins.sort(key=lambda n: n.name)  # 按名称排序: Input_1, Input_2, ...
            
            for i, (old_node, old_pin, ext_conns) in enumerate(head_nodes):
                # 找到深拷贝后的新节点
                new_node = node_name_mapping.get(old_node.name)
                if not new_node:
                    continue
                
                new_pin = new_node.get_input_pin(old_pin.name)
                if not new_pin:
                    continue
                
                # 使用已存在的InputPin节点（如果有的话），否则创建新的
                if i < len(existing_input_pins):
                    input_pin_node = existing_input_pins[i]
                    logger.info(f"[MAIN] 使用已存在的InputPin: {input_pin_node.name}")
                else:
                    # 创建新的InputPin节点（超过默认数量时）
                    input_pin_node = SubnetInputPinNode(
                        name=f"Input_{i+1}",
                        node_graph=subnet_node.subgraph
                    )
                    input_pin_node.position = (new_node.position[0], new_node.position[1] + input_pin_y_offset)
                    subnet_node.add_internal_node(input_pin_node)
                    logger.info(f"[MAIN] 创建新InputPin: {input_pin_node.name}")
                
                # 连接InputPin到头节点
                conn = Connection(
                    input_pin_node.output_pins["output"],
                    new_pin
                )
                subnet_node.subgraph.add_connection(conn)
                
                # 建立映射
                external_pin_name = f"input_{i}"
                subnet_node.map_input_pin_node(input_pin_node.name, external_pin_name)
                
                logger.info(f"[MAIN] 连接InputPin: {input_pin_node.name} -> {new_node.name}.{new_pin.name}")
            
            # 8. 创建SubnetOutputPin节点并连接到尾节点
            output_pin_y_offset = 100
            for i, (old_node, old_pin, ext_conns) in enumerate(tail_nodes):
                # 找到深拷贝后的新节点
                new_node = node_name_mapping.get(old_node.name)
                if not new_node:
                    continue
                
                new_pin = new_node.get_output_pin(old_pin.name)
                if not new_pin:
                    continue
                
                # 创建OutputPin节点
                output_pin_node = SubnetOutputPinNode(
                    name=f"Output_{i+1}",
                    node_graph=subnet_node.subgraph,
                    index=i
                )
                output_pin_node.position = (new_node.position[0], new_node.position[1] + output_pin_y_offset)
                
                # 添加到子图
                subnet_node.add_internal_node(output_pin_node)
                
                # 连接尾节点到OutputPin
                conn = Connection(
                    new_pin,
                    output_pin_node.input_pins["input"]
                )
                subnet_node.subgraph.add_connection(conn)
                
                # 建立映射
                external_pin_name = f"output_{i}"
                subnet_node.map_output_pin_node(output_pin_node.name, external_pin_name)
                
                logger.info(f"[MAIN] 创建OutputPin: {new_node.name}.{new_pin.name} -> {output_pin_node.name}")
            
            # 9. 保存外部连接信息（用于重建外部连接）
            # 头节点的外部连接：外部源节点 -> SubnetNode输入
            external_input_connections = []  # [(external_source_node, external_source_pin, subnet_input_index)]
            for i, (old_node, old_pin, ext_conns) in enumerate(head_nodes):
                for ext_conn in ext_conns:
                    external_source_node = ext_conn.source_pin.node
                    external_source_pin = ext_conn.source_pin
                    external_input_connections.append((external_source_node, external_source_pin, i))
                    logger.info(f"[MAIN] 记录外部输入连接: {external_source_node.name}.{external_source_pin.name} -> Subnet.input_{i}")
            
            # 尾节点的外部连接：SubnetNode输出 -> 外部目标节点
            external_output_connections = []  # [(subnet_output_index, external_target_node, external_target_pin)]
            for i, (old_node, old_pin, ext_conns) in enumerate(tail_nodes):
                for ext_conn in ext_conns:
                    external_target_node = ext_conn.target_pin.node
                    external_target_pin = ext_conn.target_pin
                    external_output_connections.append((i, external_target_node, external_target_pin))
                    logger.info(f"[MAIN] 记录外部输出连接: Subnet.output_{i} -> {external_target_node.name}.{external_target_pin.name}")
            
            # 10. 删除原图中的节点和连接
            for conn in all_connections_to_remove:
                if conn in self.connection_graphics_items:
                    old_conn_item = self.connection_graphics_items[conn]
                    if old_conn_item.scene() == self.graphics_scene:
                        self.graphics_scene.removeItem(old_conn_item)
                    del self.connection_graphics_items[conn]
                self.current_graph.remove_connection(conn)
            
            for conn in internal_connections:
                if conn in self.connection_graphics_items:
                    old_conn_item = self.connection_graphics_items[conn]
                    if old_conn_item.scene() == self.graphics_scene:
                        self.graphics_scene.removeItem(old_conn_item)
                    del self.connection_graphics_items[conn]
                if conn in self.current_graph.connections:
                    self.current_graph.connections.remove(conn)
            
            for node in nodes:
                if node in self.node_graphics_items:
                    old_item = self.node_graphics_items[node]
                    if old_item.scene() == self.graphics_scene:
                        self.graphics_scene.removeItem(old_item)
                    del self.node_graphics_items[node]
                if node.name in self.current_graph.nodes:
                    del self.current_graph.nodes[node.name]
            
            # 11. 添加SubnetNode到当前图
            self.current_graph.add_node(subnet_node)
            self.current_graph.subgraphs[subnet_name] = subnet_node.subgraph
            
            # 12. 创建SubnetNode的图形项
            subnet_graphics = NodeGraphicsItemV2(subnet_node)
            subnet_graphics.setPos(center_x, center_y)
            self.node_graphics_items[subnet_node] = subnet_graphics
            self.graphics_scene.addItem(subnet_graphics)
            
            # 13. 重建外部连接
            # 外部输入连接：外部源节点 -> SubnetNode输入
            for external_source_node, external_source_pin, subnet_input_index in external_input_connections:
                try:
                    # 获取外部源节点的图形项
                    source_node_item = self.node_graphics_items.get(external_source_node)
                    if not source_node_item:
                        logger.warning(f"[MAIN] 找不到外部源节点图形项: {external_source_node.name}")
                        continue
                    
                    # 获取SubnetNode的输入引脚
                    subnet_input_pin_name = f"input_{subnet_input_index}"
                    subnet_input_pin = subnet_node.input_pins.get(subnet_input_pin_name)
                    if not subnet_input_pin:
                        logger.warning(f"[MAIN] SubnetNode没有输入引脚: {subnet_input_pin_name}")
                        continue
                    
                    # 获取源引脚
                    source_pin = external_source_pin
                    
                    # 创建连接
                    conn = Connection(source_pin, subnet_input_pin)
                    self.current_graph.add_connection(conn)
                    
                    # 创建连接图形项
                    source_pin_item = source_node_item.output_pin_items.get(source_pin.name)
                    subnet_pin_item = subnet_graphics.input_pin_items.get(subnet_input_pin_name)
                    
                    if source_pin_item and subnet_pin_item:
                        conn_item = ConnectionGraphicsItem(conn, source_pin_item, subnet_pin_item)
                        self.connection_graphics_items[conn] = conn_item
                        self.graphics_scene.addItem(conn_item)
                        logger.info(f"[MAIN] 重建外部输入连接: {external_source_node.name}.{source_pin.name} -> Subnet.{subnet_input_pin_name}")
                
                except Exception as e:
                    logger.error(f"[MAIN] 重建外部输入连接失败: {e}")
            
            # 外部输出连接：SubnetNode输出 -> 外部目标节点
            for subnet_output_index, external_target_node, external_target_pin in external_output_connections:
                try:
                    # 获取外部目标节点的图形项
                    target_node_item = self.node_graphics_items.get(external_target_node)
                    if not target_node_item:
                        logger.warning(f"[MAIN] 找不到外部目标节点图形项: {external_target_node.name}")
                        continue
                    
                    # 获取SubnetNode的输出引脚
                    subnet_output_pin_name = f"output_{subnet_output_index}"
                    subnet_output_pin = subnet_node.output_pins.get(subnet_output_pin_name)
                    if not subnet_output_pin:
                        logger.warning(f"[MAIN] SubnetNode没有输出引脚: {subnet_output_pin_name}")
                        continue
                    
                    # 获取目标引脚
                    target_pin = external_target_pin
                    
                    # 创建连接
                    conn = Connection(subnet_output_pin, target_pin)
                    self.current_graph.add_connection(conn)
                    
                    # 创建连接图形项
                    subnet_pin_item = subnet_graphics.output_pin_items.get(subnet_output_pin_name)
                    target_pin_item = target_node_item.input_pin_items.get(target_pin.name)
                    
                    if subnet_pin_item and target_pin_item:
                        conn_item = ConnectionGraphicsItem(conn, subnet_pin_item, target_pin_item)
                        self.connection_graphics_items[conn] = conn_item
                        self.graphics_scene.addItem(conn_item)
                        logger.info(f"[MAIN] 重建外部输出连接: Subnet.{subnet_output_pin_name} -> {external_target_node.name}.{target_pin.name}")
                
                except Exception as e:
                    logger.error(f"[MAIN] 重建外部输出连接失败: {e}")
            
            logger.info(f"[MAIN] ✅ 子网络创建成功（深拷贝+外部连接重建）: {subnet_name}")
            self.status_label.setText(f"已创建子网络: {subnet_name} (输入: {len(head_nodes)}, 输出: {len(tail_nodes)})")
            
        except Exception as e:
            logger.error(f"[MAIN] ❌ 打包子网络失败: {e}")
            import traceback
            logger.error(traceback.format_exc())
            self.status_label.setText(f"打包子网络失败: {e}")
    
    def keyPressEvent(self, event):
        """处理键盘事件"""
        from PyQt6.QtCore import Qt
        
        # Delete键删除选中节点
        if event.key() == Qt.Key.Key_Delete:
            selected_items = self.graphics_scene.selectedItems()
            from ui.graphics.node_graphics_item_v2 import NodeGraphicsItemV2
            
            selected_nodes = []
            for item in selected_items:
                if isinstance(item, NodeGraphicsItemV2):
                    selected_nodes.append(item.node)
            
            if selected_nodes:
                logger.info(f"[MAIN] Delete键: 删除 {len(selected_nodes)} 个选中节点")
                self._on_nodes_delete_requested(selected_nodes)
            else:
                # 如果没有选中节点，检查是否有选中的连接
                from ui.graphics.connection_graphics_item import ConnectionGraphicsItem
                for item in selected_items:
                    if isinstance(item, ConnectionGraphicsItem):
                        # 删除连接
                        self._on_connection_deleted(item.connection)
                        break
        else:
            super().keyPressEvent(event)
