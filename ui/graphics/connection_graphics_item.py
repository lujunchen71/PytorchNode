"""
连接线图形项 - 贝塞尔曲线渲染

职责:
- 绘制两个引脚之间的贝塞尔曲线
- 处理连接线的交互（选中、高亮）
- 动态更新连接线位置
"""

from PyQt6.QtWidgets import QGraphicsPathItem
from PyQt6.QtCore import Qt, QPointF
from PyQt6.QtGui import QPen, QColor, QPainterPath, QPainter

from core.base.connection import Connection
from .pin_graphics_item import PinGraphicsItem

import logging
import math


logger = logging.getLogger(__name__)


class ConnectionGraphicsItem(QGraphicsPathItem):
    """连接线图形项 - 使用贝塞尔曲线绘制"""

    def __init__(self, connection: Connection, source_pin_item: PinGraphicsItem, 
                 target_pin_item: PinGraphicsItem, parent=None):
        """
        初始化连接线图形项
        
        Args:
            connection: 核心连接对象
            source_pin_item: 源引脚图形项
            target_pin_item: 目标引脚图形项
            parent: 父图形项
        """
        super().__init__(parent)
        
        self.connection = connection
        self.source_pin_item = source_pin_item
        self.target_pin_item = target_pin_item
        
        # 样式设置
        self.line_width = 2
        self.selected_line_width = 3
        self._is_hovered = False
        
        # 设置标志
        self.setFlag(QGraphicsPathItem.GraphicsItemFlag.ItemIsSelectable)
        self.setAcceptHoverEvents(True)
        
        # 设置Z值（使连接线在节点下方）
        self.setZValue(-1)
        
        # 初始化外观
        self.update_appearance()
        
        # 更新路径
        self.update_path()
        
        logger.debug(f"Created connection graphics item: {connection}")

    def update_appearance(self):
        """更新连接线外观"""
        # 获取源引脚颜色
        source_color = self.source_pin_item.brush().color()
        
        # 设置画笔
        pen = QPen(source_color)
        
        if self.isSelected():
            pen.setWidth(self.selected_line_width)
        else:
            pen.setWidth(self.line_width)
        
        # 如果节点被禁用，使用虚线
        if hasattr(self.source_pin_item.pin.node, '_disabled') and \
           self.source_pin_item.pin.node._disabled:
            pen.setStyle(Qt.PenStyle.DashLine)
        else:
            pen.setStyle(Qt.PenStyle.SolidLine)
        
        self.setPen(pen)

    def update_path(self):
        """更新连接线路径（贝塞尔曲线）"""
        # 获取引脚的场景坐标
        source_pos = self.source_pin_item.get_center_scene_pos()
        target_pos = self.target_pin_item.get_center_scene_pos()
        
        # 计算贝塞尔曲线路径
        path = self.calculate_bezier_path(source_pos, target_pos)
        self.setPath(path)

    def calculate_bezier_path(self, start: QPointF, end: QPointF) -> QPainterPath:
        """
        计算贝塞尔曲线路径
        
        Args:
            start: 起点（源引脚位置）
            end: 终点（目标引脚位置）
            
        Returns:
            贝塞尔曲线路径
        """
        path = QPainterPath(start)
        
        # 计算水平距离
        dx = end.x() - start.x()
        dy = end.y() - start.y()
        
        # 计算控制点偏移量
        # 根据距离调整控制点，使曲线更自然
        control_offset = min(abs(dx) * 0.5, 150)  # 限制最大偏移
        
        # 判断是上下连接还是左右连接
        # 如果垂直距离大于水平距离，使用垂直控制点
        if abs(dy) > abs(dx):
            # 垂直方向控制点
            control1 = QPointF(start.x(), start.y() + control_offset)
            control2 = QPointF(end.x(), end.y() - control_offset)
        else:
            # 水平方向控制点（适用于左右布局）
            control1 = QPointF(start.x() + control_offset, start.y())
            control2 = QPointF(end.x() - control_offset, end.y())
        
        # 创建三次贝塞尔曲线
        path.cubicTo(control1, control2, end)
        
        return path

    def hoverEnterEvent(self, event):
        """鼠标进入事件"""
        self._is_hovered = True
        # 高亮显示
        pen = self.pen()
        pen.setWidth(self.selected_line_width)
        self.setPen(pen)
        
        # 显示工具提示
        source_node = self.connection.source_node
        target_node = self.connection.target_node
        tooltip = (
            f"连接: {source_node.name}.{self.connection.source_pin.name}\n"
            f"  → {target_node.name}.{self.connection.target_pin.name}"
        )
        self.setToolTip(tooltip)
        
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        """鼠标离开事件"""
        self._is_hovered = False
        # 恢复正常
        if not self.isSelected():
            pen = self.pen()
            pen.setWidth(self.line_width)
            self.setPen(pen)
        super().hoverLeaveEvent(event)

    def itemChange(self, change, value):
        """项目变化事件"""
        if change == QGraphicsPathItem.GraphicsItemChange.ItemSelectedChange:
            self.update_appearance()
        return super().itemChange(change, value)

    def paint(self, painter: QPainter, option, widget=None):
        """自定义绘制"""
        # 更新路径（确保位置同步）
        self.update_path()
        # 调用父类绘制
        super().paint(painter, option, widget)


class TempConnectionGraphicsItem(QGraphicsPathItem):
    """临时连接线 - 用于拖拽创建连接时的视觉反馈"""

    def __init__(self, source_pin_item: PinGraphicsItem, parent=None):
        """
        初始化临时连接线
        
        Args:
            source_pin_item: 源引脚图形项
            parent: 父图形项
        """
        super().__init__(parent)
        
        self.source_pin_item = source_pin_item
        self.end_pos = source_pin_item.get_center_scene_pos()
        
        # 样式设置
        source_color = source_pin_item.brush().color()
        pen = QPen(source_color)
        pen.setWidth(2)
        pen.setStyle(Qt.PenStyle.DashLine)
        self.setPen(pen)
        
        # 设置Z值
        self.setZValue(-1)
        
        # 初始化路径
        self.update_path()
        
        logger.debug("Created temp connection graphics item")

    def update_end_pos(self, pos: QPointF):
        """
        更新终点位置
        
        Args:
            pos: 新的终点位置（场景坐标）
        """
        self.end_pos = pos
        self.update_path()

    def update_path(self):
        """更新连接线路径"""
        start_pos = self.source_pin_item.get_center_scene_pos()
        
        path = QPainterPath(start_pos)
        
        # 计算控制点
        dx = self.end_pos.x() - start_pos.x()
        dy = self.end_pos.y() - start_pos.y()
        
        control_offset = min(abs(dx) * 0.5, 150)
        
        if abs(dy) > abs(dx):
            control1 = QPointF(start_pos.x(), start_pos.y() + control_offset)
            control2 = QPointF(self.end_pos.x(), self.end_pos.y() - control_offset)
        else:
            control1 = QPointF(start_pos.x() + control_offset, start_pos.y())
            control2 = QPointF(self.end_pos.x() - control_offset, self.end_pos.y())
        
        path.cubicTo(control1, control2, self.end_pos)
        self.setPath(path)
