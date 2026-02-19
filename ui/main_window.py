"""
主窗口（MainWindow）- 应用程序的主界面

职责:
- UI 布局管理
- 组件组装
- 信号连接

重构说明:
- 使用 Mixin 模式分离所有功能代码
- 使用 Controller 模式分离业务逻辑
- MainWindow 只负责组装和协调
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QLabel, QMessageBox, QStatusBar
)
from PyQt6.QtCore import Qt, pyqtSignal as Signal, pyqtSlot as Slot

import logging

logger = logging.getLogger(__name__)

# 导入所有 Mixin 类
from ui.mixins import (
    MenuMixin, ToolbarMixin, DockMixin, DebugMixin,
    ProjectMixin, GraphMixin, TrainingMixin, UndoRedoMixin
)

# 导入 Controller 类
from ui.controllers import GraphController, ProjectController, TrainingController


class MainWindow(
    MenuMixin, ToolbarMixin, DockMixin, DebugMixin,
    ProjectMixin, GraphMixin, TrainingMixin, UndoRedoMixin,
    QMainWindow
):
    """主窗口类 - 纯 UI 组装者"""

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

        # 初始化 UI
        self._init_ui()
        self._create_menus()
        self._create_toolbars()
        self._create_status_bar()
        self._create_dock_widgets()
        
        # 连接控制器信号
        self._connect_controller_signals()

        # 显示初始路径的节点
        self.graph_controller._display_graph_nodes()

        logger.info(f"启动完成 - 当前路径: {self.current_path}")
        logger.info("Main window initialized")

    def _init_ui(self):
        """初始化 UI 布局"""
        from ui.graphics.node_graphics_scene import NodeGraphicsScene
        from ui.graphics.node_graphics_view import NodeGraphicsView
        from core.base import NodeGraph
        from core.undo.undo_stack import UndoStack
        from ui.widgets.breadcrumb_path_bar import BreadcrumbPathBar

        # 创建核心节点图
        self._init_node_graph()

        # 创建撤销栈
        self.undo_stack = UndoStack(max_size=100)

        # 创建图形场景和视图
        self.graphics_scene = NodeGraphicsScene(self)
        self.graphics_view = NodeGraphicsView(self.graphics_scene, self)

        # 连接图形场景信号
        self._connect_graphics_signals()

        # 创建面包屑路径导航栏
        self.path_nav_bar = BreadcrumbPathBar(self)
        self.path_nav_bar.path_changed.connect(self._on_path_changed)
        self.path_nav_bar.current_path = self.current_path
        self.path_nav_bar._rebuild_breadcrumb()

        # 创建中央控件布局
        central_widget = QWidget()
        central_layout = QVBoxLayout(central_widget)
        central_layout.setContentsMargins(0, 0, 0, 0)
        central_layout.setSpacing(0)
        
        central_layout.addWidget(self.path_nav_bar)
        central_layout.addWidget(self.graphics_view)
        
        self.setCentralWidget(central_widget)

        # 保存节点图形项的映射
        self.node_graphics_items = {}
        self.connection_graphics_items = {}
        
        # 同步视图的路径上下文
        self.graphics_view.current_path = self.current_path

        # 初始化控制器
        self._graph_controller = GraphController(self)
        self._project_controller = ProjectController(self)
        self._training_controller = TrainingController(self)

    def _init_node_graph(self):
        """初始化节点图"""
        from core.base import NodeGraph
        from core.nodes.context.root_nodes import ObjRootNode, VisRootNode, TrainRootNode

        # 创建根图和子图
        self.node_graph = NodeGraph("root")
        self.obj_graph = NodeGraph("obj", parent=self.node_graph)
        self.vis_graph = NodeGraph("vis", parent=self.node_graph)
        self.train_graph = NodeGraph("train", parent=self.node_graph)
        
        self.node_graph.subgraphs["obj"] = self.obj_graph
        self.node_graph.subgraphs["vis"] = self.vis_graph
        self.node_graph.subgraphs["train"] = self.train_graph
        
        # 创建根节点
        self.obj_root_node = ObjRootNode(name="obj", node_graph=self.obj_graph)
        self.vis_root_node = VisRootNode(name="vis", node_graph=self.vis_graph)
        self.train_root_node = TrainRootNode(name="train", node_graph=self.train_graph)
        
        self.obj_graph.add_node(self.obj_root_node)
        self.vis_graph.add_node(self.vis_root_node)
        self.train_graph.add_node(self.train_root_node)
        
        self.obj_root_node.position = (0, 0)
        self.vis_root_node.position = (0, 0)
        self.train_root_node.position = (0, 0)
        
        logger.info(f"根节点创建完成 - obj: {self.obj_root_node.name}, vis: {self.vis_root_node.name}, train: {self.train_root_node.name}")
        
        # 当前活动图
        self.current_graph = self.obj_graph
        self.current_path = "/obj"

    def _connect_graphics_signals(self):
        """连接图形场景信号"""
        self.graphics_view.node_create_requested.connect(self._on_node_create_requested)
        self.graphics_scene.connection_created.connect(self._on_connection_created)
        self.graphics_scene.connection_deleted.connect(self._on_connection_deleted)
        self.graphics_scene.node_double_clicked.connect(self._on_node_double_clicked)
        self.graphics_scene.selectionChanged.connect(self._on_selection_changed)
        self.graphics_scene.node_delete_requested.connect(self._on_nodes_delete_requested)
        self.graphics_scene.pack_subnet_requested.connect(self._on_pack_subnet_requested)

    def _connect_controller_signals(self):
        """连接控制器信号"""
        self._graph_controller.status_message.connect(self._update_status)
        self._project_controller.project_saved.connect(self._on_project_saved)
        self._project_controller.project_loaded.connect(self._on_project_loaded)
        self._project_controller.load_error.connect(self._on_load_error)
        self._project_controller.save_error.connect(self._on_save_error)
        self._training_controller.progress_updated.connect(self._on_training_progress_updated)
        self._training_controller.status_message.connect(self._update_status)

    # ==================== 属性访问器 ====================

    @property
    def graph_controller(self) -> GraphController:
        return self._graph_controller

    @property
    def project_controller(self) -> ProjectController:
        return self._project_controller

    @property
    def training_controller(self) -> TrainingController:
        return self._training_controller

    # ==================== 状态栏 ====================

    def _create_status_bar(self):
        """创建状态栏"""
        statusbar = QStatusBar()
        self.setStatusBar(statusbar)

        self.status_label = QLabel("就绪")
        statusbar.addWidget(self.status_label)

        self.train_progress_label = QLabel("训练: 未开始")
        self.train_progress_label.setStyleSheet("color: #888; font-size: 12px;")
        statusbar.addPermanentWidget(self.train_progress_label)

        self.info_label = QLabel("")
        statusbar.addPermanentWidget(self.info_label)

    def _update_status(self, message: str):
        """更新状态栏"""
        self.status_label.setText(message)

    # ==================== 属性面板 ====================

    @Slot()
    def _on_toggle_properties(self):
        self.properties_panel.toggle_visibility()

    @Slot()
    def _on_selection_changed(self):
        from ui.graphics.node_graphics_item_v2 import NodeGraphicsItemV2
        
        selected_items = self.graphics_scene.selectedItems()
        selected_node = None
        
        for item in selected_items:
            if isinstance(item, NodeGraphicsItemV2):
                selected_node = item.node
                break
        
        if hasattr(self, 'properties_panel'):
            self.properties_panel.set_node(selected_node)

    # ==================== 其他操作 ====================

    @Slot()
    def _on_run_graph(self):
        logger.info("Running graph")
        self.status_label.setText("执行节点图...")
        QMessageBox.information(self, "运行", "图执行功能将在后续实现")

    @Slot()
    def _on_about(self):
        QMessageBox.about(
            self, "关于 PNNE",
            "<h3>PNNE - PyTorch Neural Network Editor</h3>"
            "<p>版本: 0.1.0</p>"
            "<p>一个基于节点的可视化深度学习模型编辑器</p>"
        )

    # ==================== 键盘事件 ====================

    def keyPressEvent(self, event):
        from PyQt6.QtCore import Qt
        from ui.graphics.node_graphics_item_v2 import NodeGraphicsItemV2
        from ui.graphics.connection_graphics_item import ConnectionGraphicsItem
        
        if event.key() == Qt.Key.Key_Delete:
            selected_items = self.graphics_scene.selectedItems()
            
            selected_nodes = [
                item.node for item in selected_items
                if isinstance(item, NodeGraphicsItemV2)
            ]
            
            if selected_nodes:
                self._on_nodes_delete_requested(selected_nodes)
            else:
                for item in selected_items:
                    if isinstance(item, ConnectionGraphicsItem):
                        self._on_connection_deleted(item.connection)
                        break
        else:
            super().keyPressEvent(event)

    # ==================== 窗口事件 ====================

    def closeEvent(self, event):
        logger.info("Closing main window")
        event.accept()

    # ==================== 兼容性方法 ====================

    def _display_graph_nodes(self):
        self._graph_controller._display_graph_nodes()

    def _clear_scene_display(self):
        self._graph_controller._clear_scene_display()
