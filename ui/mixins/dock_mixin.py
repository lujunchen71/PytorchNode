"""
DockMixin - 停靠窗口构建混入类

职责:
- 创建停靠窗口
- 管理面板布局
"""

from PyQt6.QtWidgets import QDockWidget, QLabel
from PyQt6.QtCore import Qt

import logging

logger = logging.getLogger(__name__)


class DockMixin:
    """停靠窗口构建混入类"""

    def _create_dock_widgets(self: 'MainWindow'):
        """创建停靠窗口"""
        # 节点库面板（左侧）- T049: 使用NodePalettePanel
        self._create_node_library_dock()

        # 属性面板（浮动窗口，不再使用停靠窗口）
        self._create_properties_panel()

        # 控制台面板（底部）
        self._create_console_dock()

    def _create_node_library_dock(self: 'MainWindow'):
        """创建节点库停靠窗口"""
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

        # 添加到视图菜单
        self.view_menu.addAction(node_library_dock.toggleViewAction())

        # 保存引用
        self.dock_widgets = {'node_library': node_library_dock}

    def _create_properties_panel(self: 'MainWindow'):
        """创建属性面板（浮动窗口）"""
        from ui.panels.properties_panel import PropertiesPanel
        
        self.properties_panel = PropertiesPanel(self)
        # 默认隐藏，按P键显示
        self.properties_panel.hide()

    def _create_console_dock(self: 'MainWindow'):
        """创建控制台停靠窗口"""
        console_dock = QDockWidget("控制台", self)
        console_dock.setObjectName("ConsoleDock")
        console_widget = QLabel("Python 控制台\n(日志和输出将在此显示)")
        console_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
        console_widget.setStyleSheet("background-color: #333; color: #888;")
        console_dock.setWidget(console_widget)
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, console_dock)

        # 添加到视图菜单
        self.view_menu.addAction(console_dock.toggleViewAction())

        # 保存引用
        self.dock_widgets['console'] = console_dock
