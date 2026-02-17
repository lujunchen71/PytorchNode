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
    QLabel, QMessageBox, QFileDialog
)
from PyQt6.QtCore import Qt, pyqtSignal as Signal, pyqtSlot as Slot
from PyQt6.QtGui import QAction, QKeySequence, QIcon

import logging


logger = logging.getLogger(__name__)


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

        logger.info("Main window initialized")

    def _init_ui(self):
        """初始化UI布局"""
        # 导入图形组件
        from ui.graphics.node_graphics_scene import NodeGraphicsScene
        from ui.graphics.node_graphics_view import NodeGraphicsView
        from ui.graphics.node_graphics_item_v2 import NodeGraphicsItemV2
        from core.base import NodeGraph, NodeFactory

        # 创建核心节点图
        self.node_graph = NodeGraph("main_graph")

        # 创建图形场景和视图
        self.graphics_scene = NodeGraphicsScene(self)
        self.graphics_view = NodeGraphicsView(self.graphics_scene, self)

        # 连接信号
        self.graphics_view.node_create_requested.connect(self._on_node_create_requested)
        self.graphics_scene.connection_created.connect(self._on_connection_created)
        self.graphics_scene.connection_deleted.connect(self._on_connection_deleted)
        self.graphics_scene.selectionChanged.connect(self._on_selection_changed)

        # 设置中央控件
        self.setCentralWidget(self.graphics_view)

        # 保存节点图形项的映射
        self.node_graphics_items = {}  # {node: graphics_item}
        # 保存连接图形项的映射
        self.connection_graphics_items = {}  # {connection: graphics_item}

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

        undo_action = QAction("撤销(&U)", self)
        undo_action.setShortcut(QKeySequence.StandardKey.Undo)
        undo_action.setEnabled(False)
        edit_menu.addAction(undo_action)

        redo_action = QAction("重做(&R)", self)
        redo_action.setShortcut(QKeySequence.StandardKey.Redo)
        redo_action.setEnabled(False)
        edit_menu.addAction(redo_action)

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
        
        # 属性面板切换动作 (P键)
        self.toggle_properties_action = QAction("切换属性面板(&P)", self)
        self.toggle_properties_action.setShortcut(Qt.Key.Key_P)
        self.toggle_properties_action.triggered.connect(self._on_toggle_properties)
        view_menu.addAction(self.toggle_properties_action)
        
        view_menu.addSeparator()

        # 将在 _create_dock_widgets 后填充

        # 帮助菜单
        help_menu = menubar.addMenu("帮助(&H)")

        about_action = QAction("关于(&A)", self)
        about_action.triggered.connect(self._on_about)
        help_menu.addAction(about_action)

        # 保存菜单引用
        self.view_menu = view_menu

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

    def _create_status_bar(self):
        """创建状态栏"""
        statusbar = QStatusBar()
        self.setStatusBar(statusbar)

        # 状态标签
        self.status_label = QLabel("就绪")
        statusbar.addWidget(self.status_label)

        # 右侧信息
        self.info_label = QLabel("")
        statusbar.addPermanentWidget(self.info_label)

    def _create_dock_widgets(self):
        """创建停靠窗口"""
        # 节点库面板（左侧）
        node_library_dock = QDockWidget("节点库", self)
        node_library_dock.setObjectName("NodeLibraryDock")
        node_library_widget = QLabel("节点库面板\n(节点列表将在此显示)")
        node_library_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
        node_library_widget.setStyleSheet("background-color: #333; color: #888;")
        node_library_dock.setWidget(node_library_widget)
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
        """切换属性面板显示/隐藏"""
        if self.properties_panel.isVisible():
            self.properties_panel.hide()
            logger.info("Properties panel hidden")
        else:
            self.properties_panel.show()
            # 如果是第一次显示，将窗口放置在主窗口右侧
            if not hasattr(self, '_properties_panel_positioned'):
                main_geo = self.geometry()
                panel_geo = self.properties_panel.geometry()
                self.properties_panel.move(
                    main_geo.right() + 10,
                    main_geo.top()
                )
                self._properties_panel_positioned = True
            logger.info("Properties panel shown")

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
        from core.base import NodeFactory
        from ui.graphics.node_graphics_item_v2 import NodeGraphicsItemV2
        from ui.graphics.connection_graphics_item import ConnectionGraphicsItem
        
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
            
            # 第二步：反序列化节点图
            logger.info("Deserializing graph...")
            created_nodes = Serializer.deserialize_graph(
                graph_data, 
                self.node_graph, 
                NodeFactory
            )
            
            # 第三步：创建节点图形项
            logger.info("Creating node graphics items...")
            for node in created_nodes:
                try:
                    # 创建图形项
                    graphics_item = NodeGraphicsItemV2(node)
                    graphics_item.setPos(node.position[0], node.position[1])
                    
                    # 添加到场景
                    self.graphics_scene.addItem(graphics_item)
                    
                    # 保存映射
                    self.node_graphics_items[node] = graphics_item
                    
                    logger.info(f"  ✓ Graphics item created for: {node.name}")
                    
                except Exception as e:
                    logger.error(f"Failed to create graphics item for {node.name}: {e}")
                    import traceback
                    logger.error(traceback.format_exc())
            
            # 第四步：创建连接图形项
            logger.info("Creating connection graphics items...")
            for connection in self.node_graph.connections:
                try:
                    source_node_item = self.node_graphics_items.get(connection.source_node)
                    target_node_item = self.node_graphics_items.get(connection.target_node)
                    
                    if source_node_item and target_node_item:
                        # 找到对应的引脚图形项
                        source_pin_item = source_node_item.output_pin_items.get(connection.source_pin.name)
                        target_pin_item = target_node_item.input_pin_items.get(connection.target_pin.name)
                        
                        if source_pin_item and target_pin_item:
                            # 创建连接图形项
                            connection_item = ConnectionGraphicsItem(
                                connection, 
                                source_pin_item, 
                                target_pin_item
                            )
                            
                            # 添加到场景
                            self.graphics_scene.addItem(connection_item)
                            
                            # 保存映射
                            self.connection_graphics_items[connection] = connection_item
                            
                            logger.info(f"  ✓ Connection graphics item created")
                        else:
                            logger.error(f"  ✗ Pin graphics items not found")
                    else:
                        logger.error(f"  ✗ Node graphics items not found")
                        
                except Exception as e:
                    logger.error(f"Failed to create connection graphics item: {e}")
                    import traceback
                    logger.error(traceback.format_exc())
            
            # 更新状态
            self.current_project_path = file_path
            self.status_label.setText(f"✅ 项目已加载: {file_path}")
            self.project_opened.emit(file_path)
            
            logger.info("Project loaded successfully!")
            
            # 显示成功消息
            QMessageBox.information(
                self,
                "加载成功",
                f"项目已成功加载:\n{file_path}\n\n"
                f"节点数: {len(self.node_graph.nodes)}\n"
                f"连接数: {len(self.node_graph.connections)}"
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

    def _on_node_create_requested(self, node_type: str, scene_pos):
        """处理创建节点请求"""
        from ui.graphics.node_graphics_item_v2 import NodeGraphicsItemV2
        from core.base import NodeFactory
        
        try:
            # 创建核心节点
            node = NodeFactory.create_node(node_type, node_graph=self.node_graph)
            
            # 设置节点位置
            node.position = (scene_pos.x(), scene_pos.y())
            
            # 添加到节点图
            self.node_graph.add_node(node)
            
            # 创建图形项（使用V2版本）
            graphics_item = NodeGraphicsItemV2(node)
            graphics_item.setPos(scene_pos.x(), scene_pos.y())
            
            # 添加到场景
            self.graphics_scene.addItem(graphics_item)
            
            # 保存映射
            self.node_graphics_items[node] = graphics_item
            
            logger.info(f"Created node: {node.name} ({node_type}) at ({scene_pos.x():.1f}, {scene_pos.y():.1f})")
            self.status_label.setText(f"创建节点: {node.display_name} ({node.name})")
            
        except Exception as e:
            logger.error(f"Failed to create node: {e}")
            self.status_label.setText(f"创建节点失败: {e}")
    
    def _on_connection_created(self, source_pin, target_pin):
        """处理创建连接请求"""
        from ui.graphics.connection_graphics_item import ConnectionGraphicsItem
        from core.base.connection import Connection
        
        logger.info(f"[MAIN] 收到创建连接信号")
        logger.info(f"[MAIN] 源引脚: {source_pin.full_path}")
        logger.info(f"[MAIN] 目标引脚: {target_pin.full_path}")
        
        try:
            # 创建核心连接
            connection = Connection(source_pin, target_pin)
            logger.info(f"[MAIN] 核心连接对象已创建")
            
            # 添加到节点图
            self.node_graph.add_connection(connection)
            logger.info(f"[MAIN] 连接已添加到节点图")
            
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
                    
                    # 添加到场景
                    self.graphics_scene.addItem(connection_item)
                    logger.info(f"[MAIN] 连接图形项已添加到场景")
                    
                    # 保存映射
                    self.connection_graphics_items[connection] = connection_item
                    
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
        """处理删除连接请求"""
        logger.info(f"[MAIN] 收到删除连接信号")
        logger.info(f"[MAIN] 连接: {connection.source_pin.full_path} → {connection.target_pin.full_path}")
        
        try:
            # 从节点图移除连接
            self.node_graph.remove_connection(connection)
            logger.info(f"[MAIN] 连接已从节点图移除")
            
            # 获取并移除连接图形项
            connection_item = self.connection_graphics_items.get(connection)
            if connection_item:
                self.graphics_scene.removeItem(connection_item)
                logger.info(f"[MAIN] 连接图形项已从场景移除")
                
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
