"""
节点图形项 V2 - 上下引脚布局（按文档设计）

根据 docs/04_UI框架设计.md 设计：
- 输入引脚在顶部横排
- 输出引脚在底部横排
- 左侧1/9：禁用按钮
- 中间7/9：图标+名称
- 右侧1/9：显示按钮
"""

from PyQt6.QtWidgets import QGraphicsItem, QGraphicsTextItem, QGraphicsRectItem
from PyQt6.QtCore import Qt, QRectF, QPointF
from PyQt6.QtGui import QPen, QBrush, QColor, QFont, QPainter, QPainterPath

from .pin_graphics_item import PinGraphicsItem

import logging


logger = logging.getLogger(__name__)


class NodeGraphicsItemV2(QGraphicsItem):
    """节点图形项 - 上下引脚布局版本"""

    def __init__(self, node, parent=None):
        """初始化节点图形项"""
        super().__init__(parent)

        self.node = node

        # 基础尺寸
        self.width = 180
        self.header_height = 24  # 输入引脚区高度
        self.body_height = 60    # 主体高度
        self.footer_height = 24  # 输出引脚区高度
        self.edge_radius = 5

        # 颜色
        self._header_color = QColor(50, 50, 50)
        self._body_color = QColor(60, 60, 60)
        self._footer_color = QColor(50, 50, 50)
        self._border_color = QColor(80, 80, 80)
        self._selected_color = QColor(255, 165, 0)
        
        # 禁用状态
        self._is_disabled = False

        # 设置标志
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        self.setAcceptHoverEvents(True)

        # 创建子元素
        self._create_text_items()
        self._create_buttons()
        self._create_pin_items()

        logger.info(f"Created node graphics v2 for: {node.name}")

    def _create_text_items(self):
        """创建文本项"""
        # 节点类型名称（居中显示在主体）
        self.type_label = QGraphicsTextItem(self)
        self.type_label.setDefaultTextColor(Qt.GlobalColor.white)
        self.type_label.setPlainText(self.node.display_name)
        
        # 计算居中位置
        font = QFont("Arial", 10, QFont.Weight.Bold)
        self.type_label.setFont(font)
        text_width = self.type_label.boundingRect().width()
        text_x = (self.width - text_width) / 2
        text_y = self.header_height + 10
        self.type_label.setPos(text_x, text_y)

        # 节点名称（小字显示在类型下方）
        self.name_label = QGraphicsTextItem(self)
        self.name_label.setDefaultTextColor(QColor(180, 180, 180))
        self.name_label.setPlainText(self.node.name)
        
        name_font = QFont("Arial", 8)
        self.name_label.setFont(name_font)
        name_width = self.name_label.boundingRect().width()
        name_x = (self.width - name_width) / 2
        name_y = text_y + 18
        self.name_label.setPos(name_x, name_y)

    def _create_buttons(self):
        """创建按钮区域"""
        button_width = self.width / 9
        
        # 创建透明画笔
        no_pen = QPen(Qt.GlobalColor.transparent)
        no_pen.setWidth(0)
        
        # 左侧禁用按钮区域（可点击）
        self.disable_button = QGraphicsRectItem(0, self.header_height,
                                                button_width, self.body_height, self)
        self.disable_button.setBrush(QBrush(QColor(70, 70, 70, 100)))
        self.disable_button.setPen(no_pen)
        
        # 右侧显示按钮区域（可点击）
        self.show_button = QGraphicsRectItem(self.width - button_width, self.header_height,
                                            button_width, self.body_height, self)
        self.show_button.setBrush(QBrush(QColor(70, 70, 70, 100)))
        self.show_button.setPen(no_pen)

    def _create_pin_items(self):
        """创建引脚图形项"""
        self.input_pin_items = {}
        self.output_pin_items = {}

        # 输入引脚（顶部横排）
        input_count = len(self.node.input_pins)
        if input_count > 0:
            spacing = self.width / (input_count + 1)
            for i, (pin_name, pin) in enumerate(self.node.input_pins.items()):
                pin_item = PinGraphicsItem(pin, self)
                x_pos = spacing * (i + 1)
                y_pos = 0  # 顶部
                pin_item.setPos(x_pos, y_pos)
                self.input_pin_items[pin_name] = pin_item

        # 输出引脚（底部横排）
        output_count = len(self.node.output_pins)
        if output_count > 0:
            spacing = self.width / (output_count + 1)
            for i, (pin_name, pin) in enumerate(self.node.output_pins.items()):
                pin_item = PinGraphicsItem(pin, self)
                x_pos = spacing * (i + 1)
                y_pos = self.get_total_height()  # 底部
                pin_item.setPos(x_pos, y_pos)
                self.output_pin_items[pin_name] = pin_item

    def get_total_height(self) -> float:
        """获取节点总高度"""
        return self.header_height + self.body_height + self.footer_height

    def boundingRect(self) -> QRectF:
        """返回边界矩形"""
        return QRectF(0, 0, self.width, self.get_total_height())

    def paint(self, painter: QPainter, option, widget=None):
        """绘制节点"""
        total_height = self.get_total_height()

        # 如果禁用，整体半透明
        if self._is_disabled:
            painter.setOpacity(0.5)

        # 1. 绘制主体背景
        path = QPainterPath()
        path.addRoundedRect(0, 0, self.width, total_height,
                           self.edge_radius, self.edge_radius)
        
        # 填充背景 - 使用透明画笔
        no_pen = QPen(Qt.GlobalColor.transparent)
        no_pen.setWidth(0)
        painter.setPen(no_pen)
        
        # 顶部区域（输入引脚）
        painter.setBrush(QBrush(self._header_color))
        header_path = QPainterPath()
        header_path.addRoundedRect(0, 0, self.width, self.header_height,
                                  self.edge_radius, self.edge_radius)
        painter.drawPath(header_path)
        
        # 中间主体
        painter.setBrush(QBrush(self._body_color))
        body_rect = QRectF(0, self.header_height, self.width, self.body_height)
        painter.drawRect(body_rect)
        
        # 底部区域（输出引脚）
        painter.setBrush(QBrush(self._footer_color))
        footer_path = QPainterPath()
        footer_path.addRoundedRect(0, self.header_height + self.body_height,
                                  self.width, self.footer_height,
                                  self.edge_radius, self.edge_radius)
        painter.drawPath(footer_path)

        # 2. 绘制边框
        if self.isSelected():
            pen = QPen(self._selected_color, 2)
        else:
            pen = QPen(self._border_color, 1)
        
        painter.setPen(pen)
        painter.setBrush(QBrush(Qt.BrushStyle.NoBrush))
        painter.drawPath(path)

        # 3. 绘制禁用图标（如果禁用）
        if self._is_disabled:
            button_width = self.width / 9
            center_x = button_width / 2
            center_y = self.header_height + self.body_height / 2
            
            # 绘制禁用符号 ⊘
            painter.setPen(QPen(QColor(255, 100, 100), 2))
            radius = 8
            painter.drawEllipse(QPointF(center_x, center_y), radius, radius)
            painter.drawLine(int(center_x - radius * 0.7), int(center_y - radius * 0.7),
                           int(center_x + radius * 0.7), int(center_y + radius * 0.7))

    def mousePressEvent(self, event):
        """鼠标按下事件"""
        # 右键菜单
        if event.button() == Qt.MouseButton.RightButton:
            self._show_context_menu(event.screenPos())
            event.accept()
            return
        
        button_width = self.width / 9
        pos = event.pos()
        
        # 检查是否点击了禁用按钮
        if (0 <= pos.x() <= button_width and
            self.header_height <= pos.y() <= self.header_height + self.body_height):
            self.toggle_disabled()
            event.accept()
            return
        
        # 检查是否点击了显示按钮
        if (self.width - button_width <= pos.x() <= self.width and
            self.header_height <= pos.y() <= self.header_height + self.body_height):
            self.on_show_button_clicked()
            event.accept()
            return
        
        super().mousePressEvent(event)
    
    def mouseDoubleClickEvent(self, event):
        """鼠标双击事件 - 进入节点"""
        from core.base.node import NodeCategory
        logger.info(f"[DOUBLE CLICK] Node: {self.node.name}, category: {self.node.node_category}, type: {self.node.node_type}")
        # 检查节点是否有子图（容器节点）
        if self.node.node_category == NodeCategory.CONTEXT or hasattr(self.node.node_graph, 'subgraphs'):
            # 通知场景/主窗口进入此节点
            scene = self.scene()
            if scene and hasattr(scene, 'node_double_clicked'):
                scene.node_double_clicked.emit(self.node)
                logger.info(f"Double-clicked node to enter: {self.node.name}")
                event.accept()
                return
        
        super().mouseDoubleClickEvent(event)

    def toggle_disabled(self):
        """切换禁用状态"""
        self._is_disabled = not self._is_disabled
        self.update()
        logger.info(f"Node {self.node.name} disabled: {self._is_disabled}")

    def on_show_button_clicked(self):
        """点击显示按钮"""
        logger.info(f"Show button clicked for node: {self.node.name}")
        # TODO: 在左侧面板显示节点数据

    def itemChange(self, change, value):
        """项目变化事件"""
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionChange:
            self.node.position = (value.x(), value.y())
            # 更新连接线位置（如果有）
            # TODO: 通知连接线更新
        
        return super().itemChange(change, value)
    
    def _show_context_menu(self, screen_pos):
        """显示节点右键菜单"""
        from PyQt6.QtWidgets import QMenu
        
        menu = QMenu()
        menu.setStyleSheet("""
            QMenu {
                background-color: #2b2b2b;
                color: #ffffff;
                border: 1px solid #555;
                padding: 5px;
            }
            QMenu::item {
                padding: 5px 20px 5px 20px;
            }
            QMenu::item:selected {
                background-color: #3d8ec9;
            }
            QMenu::separator {
                height: 1px;
                background-color: #555;
                margin: 5px 0px;
            }
        """)
        
        # 获取场景中选中的节点数量
        selected_count = len(self.scene().selectedItems())
        
        # 删除动作
        delete_action = menu.addAction("删除 (Delete)")
        delete_action.triggered.connect(lambda: self._on_delete_requested())
        
        # 复制动作（TODO）
        copy_action = menu.addAction("复制 (Ctrl+C)")
        copy_action.setEnabled(False)  # 暂未实现
        copy_action.triggered.connect(lambda: self._on_copy_requested())
        
        menu.addSeparator()
        
        # 如果选中了多个节点，显示打包选项
        if selected_count > 1:
            pack_action = menu.addAction(f"打包为子网络 ({selected_count}个节点)")
            pack_action.triggered.connect(lambda: self._on_pack_subnet_requested())
        
        # 禁用/启用
        if self._is_disabled:
            enable_action = menu.addAction("启用节点")
            enable_action.triggered.connect(lambda: self.toggle_disabled())
        else:
            disable_action = menu.addAction("禁用节点")
            disable_action.triggered.connect(lambda: self.toggle_disabled())
        
        menu.addSeparator()
        
        # 属性编辑
        properties_action = menu.addAction("编辑参数...")
        properties_action.triggered.connect(lambda: self._on_edit_properties())
        
        # 显示菜单
        menu.exec(screen_pos)
    
    def _on_delete_requested(self):
        """删除节点请求"""
        scene = self.scene()
        if scene and hasattr(scene, 'node_delete_requested'):
            # 获取所有选中的节点
            from .node_graphics_item_v2 import NodeGraphicsItemV2
            selected_nodes = []
            for item in scene.selectedItems():
                if isinstance(item, NodeGraphicsItemV2):
                    selected_nodes.append(item.node)
            
            # 如果没有选中节点，删除当前节点
            if not selected_nodes:
                selected_nodes = [self.node]
            
            scene.node_delete_requested.emit(selected_nodes)
            logger.info(f"Delete requested for {len(selected_nodes)} nodes")
    
    def _on_copy_requested(self):
        """复制节点请求"""
        # TODO: 实现复制功能
        logger.info(f"Copy requested for node: {self.node.name}")
    
    def _on_pack_subnet_requested(self):
        """打包为子网络请求"""
        scene = self.scene()
        if scene and hasattr(scene, 'pack_subnet_requested'):
            # 获取所有选中的节点
            from .node_graphics_item_v2 import NodeGraphicsItemV2
            selected_nodes = []
            for item in scene.selectedItems():
                if isinstance(item, NodeGraphicsItemV2):
                    selected_nodes.append(item.node)
            
            scene.pack_subnet_requested.emit(selected_nodes)
            logger.info(f"Pack subnet requested for {len(selected_nodes)} nodes")
    
    def _on_edit_properties(self):
        """编辑属性"""
        scene = self.scene()
        if scene and hasattr(scene, 'node_double_clicked'):
            scene.node_double_clicked.emit(self.node)
