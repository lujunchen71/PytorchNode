"""
节点面板 - 显示可用节点列表，支持拖拽创建节点
T049 [US1] 实现NodePalettePanel
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTreeWidget, QTreeWidgetItem,
    QLineEdit, QLabel
)
from PyQt6.QtCore import Qt, pyqtSignal as Signal, QMimeData
from PyQt6.QtGui import QDrag

from core.base import get_registry
import logging


logger = logging.getLogger(__name__)


class NodePalettePanel(QWidget):
    """节点面板 - 左侧节点库"""

    # 自定义信号
    node_create_requested = Signal(str)  # 节点类型

    def __init__(self, parent=None):
        """初始化节点面板"""
        super().__init__(parent)

        self.setWindowTitle("节点库")
        self.setMinimumWidth(200)
        
        # 当前上下文路径
        self._context_path = "/obj"

        # 创建布局
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        # 搜索框
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("搜索节点...")
        self.search_box.textChanged.connect(self._on_search_changed)
        layout.addWidget(self.search_box)

        # 节点树
        self.node_tree = QTreeWidget()
        self.node_tree.setHeaderHidden(True)
        self.node_tree.setDragEnabled(True)
        self.node_tree.itemDoubleClicked.connect(self._on_item_double_clicked)
        layout.addWidget(self.node_tree)

        # 设置布局
        self.setLayout(layout)

        # 填充节点树
        self._populate_node_tree()

        logger.info("Node palette panel initialized")
    
    def set_context_path(self, path: str, force_refresh: bool = False):
        """
        设置当前上下文路径并刷新节点列表
        
        Args:
            path: 上下文路径（如 /obj, /vis, /train）
            force_refresh: 是否强制刷新（即使路径相同）
        """
        if path != self._context_path or force_refresh:
            self._context_path = path
            logger.info(f"Context path set to: {path}, force_refresh={force_refresh}")
            self._populate_node_tree()

    def _populate_node_tree(self):
        """填充节点树 - 根据当前上下文路径过滤可用节点"""
        from core.base.node import NodeCategory
        
        self.node_tree.clear()

        # 获取节点注册表
        registry = get_registry()
        
        # 根据上下文路径获取可用的节点类型
        available_node_types = registry.get_nodes_for_context(self._context_path)
        
        logger.info(f"Context path: {self._context_path}, available nodes: {len(available_node_types)}")

        if not available_node_types:
            # 如果没有可用的节点，显示提示
            no_nodes_item = QTreeWidgetItem([f"(在 {self._context_path} 路径下没有可用的节点)"])
            no_nodes_item.setFlags(Qt.ItemFlag.NoItemFlags)
            self.node_tree.addTopLevelItem(no_nodes_item)
            return

        # 按分类组织可用节点
        category_nodes = {}  # {category: [node_types]}
        for node_type in available_node_types:
            node_info = registry.get_node_info(node_type)
            if node_info:
                category = node_info.get("category", "Other")
                if category not in category_nodes:
                    category_nodes[category] = []
                category_nodes[category].append(node_type)

        # 按分类添加节点
        for category in sorted(category_nodes.keys()):
            # 创建分类项
            category_item = QTreeWidgetItem([category])
            category_item.setExpanded(True)  # 默认展开

            # 获取该分类下的所有节点
            node_types = category_nodes[category]

            for node_type in sorted(node_types):
                # 获取节点信息
                node_info = registry.get_node_info(node_type)
                display_name = node_info.get("display_name", node_type)

                # 创建节点项
                node_item = QTreeWidgetItem([display_name])
                node_item.setData(0, Qt.ItemDataRole.UserRole, node_type)  # 保存节点类型
                node_item.setToolTip(0, f"双击或拖拽创建 {display_name} 节点")

                category_item.addChild(node_item)

            self.node_tree.addTopLevelItem(category_item)

        logger.info(f"Populated {len(category_nodes)} categories for path {self._context_path}")

    def _on_search_changed(self, text: str):
        """搜索框文本改变"""
        text = text.lower()

        # 遍历所有项，隐藏不匹配的
        for i in range(self.node_tree.topLevelItemCount()):
            category_item = self.node_tree.topLevelItem(i)
            category_visible = False

            for j in range(category_item.childCount()):
                node_item = category_item.child(j)
                node_name = node_item.text(0).lower()

                # 检查是否匹配
                if text in node_name:
                    node_item.setHidden(False)
                    category_visible = True
                else:
                    node_item.setHidden(True)

            # 如果分类下有可见项，显示分类
            category_item.setHidden(not category_visible)

    def _on_item_double_clicked(self, item: QTreeWidgetItem, column: int):
        """双击节点项 - 在画布中心创建节点"""
        # 获取节点类型
        node_type = item.data(0, Qt.ItemDataRole.UserRole)

        if node_type:
            logger.info(f"Double-clicked node type: {node_type}")
            self.node_create_requested.emit(node_type)

    def startDrag(self, supportedActions):
        """开始拖拽（支持拖拽到画布创建节点）"""
        # 获取当前选中项
        current_item = self.node_tree.currentItem()

        if current_item:
            # 获取节点类型
            node_type = current_item.data(0, Qt.ItemDataRole.UserRole)

            if node_type:
                # 创建拖拽对象
                drag = QDrag(self)

                # 创建MIME数据
                mime_data = QMimeData()
                mime_data.setText(node_type)
                drag.setMimeData(mime_data)

                # 执行拖拽
                logger.info(f"Starting drag for node type: {node_type}")
                drag.exec(Qt.DropAction.CopyAction)

    def refresh(self):
        """刷新节点树（重新加载节点注册表）"""
        logger.info("Refreshing node palette")
        self._populate_node_tree()
