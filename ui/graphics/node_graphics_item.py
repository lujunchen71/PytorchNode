"""
节点图形项 - 节点的可视化表示
"""

from PyQt6.QtWidgets import QGraphicsItem, QGraphicsTextItem
from PyQt6.QtCore import Qt, QRectF, QPointF
from PyQt6.QtGui import QPen, QBrush, QColor, QFont, QPainter, QPainterPath

from .pin_graphics_item import PinGraphicsItem

import logging


logger = logging.getLogger(__name__)


class NodeGraphicsItem(QGraphicsItem):
    """节点图形项"""

    def __init__(self, node, parent=None):
        """
        初始化节点图形项
        
        Args:
            node: 核心节点对象
        """
        super().__init__(parent)

        self.node = node

        # 图形属性
        self.width = 180
        self.height = 100
        self.edge_size = 10
        self.title_height = 30

        # 颜色
        self._title_color = QColor(40, 40, 40)
        self._body_color = QColor(60, 60, 60)
        self._selected_color = QColor(255, 165, 0)

        # 设置标志
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)

        # 创建标题文本
        self.title_item = QGraphicsTextItem(self)
        self.title_item.setDefaultTextColor(Qt.GlobalColor.white)
        self.title_item.setPlainText(self.node.display_name)
        self.title_item.setPos(10, 5)
        
        # 设置字体
        font = QFont("Arial", 10, QFont.Weight.Bold)
        self.title_item.setFont(font)

        # 创建节点名称文本
        self.name_item = QGraphicsTextItem(self)
        self.name_item.setDefaultTextColor(QColor(200, 200, 200))
        self.name_item.setPlainText(self.node.name)
        self.name_item.setPos(10, self.title_height + 5)

        # 设置字体
        name_font = QFont("Arial", 9)
        self.name_item.setFont(name_font)

        # 创建引脚图形项
        self.input_pin_items = {}
        self.output_pin_items = {}
        self._create_pin_graphics()
        
        # 更新节点高度以适应引脚
        self._update_height()

        logger.debug(f"Created graphics item for node: {node.name}")

    def boundingRect(self) -> QRectF:
        """返回边界矩形"""
        return QRectF(0, 0, self.width, self.height)

    def paint(self, painter: QPainter, option, widget=None):
        """绘制节点"""
        # 绘制标题栏
        title_path = QPainterPath()
        title_path.addRoundedRect(
            0, 0, self.width, self.title_height, 
            self.edge_size, self.edge_size
        )
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(self._title_color))
        painter.drawPath(title_path.simplified())

        # 绘制主体
        body_path = QPainterPath()
        body_path.addRoundedRect(
            0, self.title_height, self.width, self.height - self.title_height,
            self.edge_size, self.edge_size
        )
        painter.setBrush(QBrush(self._body_color))
        painter.drawPath(body_path.simplified())

        # 绘制完整的外框
        outline_path = QPainterPath()
        outline_path.addRoundedRect(
            0, 0, self.width, self.height,
            self.edge_size, self.edge_size
        )
        
        # 如果被选中，使用高亮颜色
        if self.isSelected():
            painter.setPen(QPen(self._selected_color, 2))
        else:
            painter.setPen(QPen(QColor(30, 30, 30), 1))
        
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawPath(outline_path)

    def _create_pin_graphics(self):
        """创建引脚图形项"""
        pin_spacing = 20  # 引脚之间的间距
        start_y = self.title_height + 10  # 引脚开始的Y坐标
        
        # 创建输入引脚
        for i, (pin_name, pin) in enumerate(self.node.input_pins.items()):
            pin_item = PinGraphicsItem(pin, self)
            y_pos = start_y + i * pin_spacing
            pin_item.setPos(0, y_pos)  # 左侧
            self.input_pin_items[pin_name] = pin_item
        
        # 创建输出引脚
        for i, (pin_name, pin) in enumerate(self.node.output_pins.items()):
            pin_item = PinGraphicsItem(pin, self)
            y_pos = start_y + i * pin_spacing
            pin_item.setPos(self.width, y_pos)  # 右侧
            self.output_pin_items[pin_name] = pin_item

    def _update_height(self):
        """根据引脚数量更新节点高度"""
        # 计算需要的最小高度
        max_pins = max(len(self.node.input_pins), len(self.node.output_pins))
        if max_pins > 0:
            pin_spacing = 20
            min_height = self.title_height + 20 + max_pins * pin_spacing + 10
            self.height = max(self.height, min_height)

    def itemChange(self, change, value):
        """项目变化事件"""
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionChange:
            # 更新节点模型的位置
            self.node.position = (value.x(), value.y())
            logger.debug(f"Node {self.node.name} moved to ({value.x():.1f}, {value.y():.1f})")
        
        return super().itemChange(change, value)
