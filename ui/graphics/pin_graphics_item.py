"""
引脚图形项 - 引脚的可视化表示
"""

from PyQt6.QtWidgets import QGraphicsItem, QGraphicsEllipseItem
from PyQt6.QtCore import Qt, QRectF, QPointF, pyqtSignal as Signal
from PyQt6.QtGui import QPen, QBrush, QColor, QPainter

from core.base import PinType

import logging


logger = logging.getLogger(__name__)


# 引脚类型颜色映射
PIN_TYPE_COLORS = {
    PinType.EXEC: QColor(255, 255, 255),      # 白色 - 执行流
    PinType.TENSOR: QColor(100, 150, 255),    # 蓝色 - 张量
    PinType.INT: QColor(100, 255, 100),       # 绿色 - 整数
    PinType.FLOAT: QColor(255, 165, 0),       # 橙色 - 浮点数
    PinType.STRING: QColor(255, 100, 255),    # 紫色 - 字符串
    PinType.BOOL: QColor(255, 100, 100),      # 红色 - 布尔值
    PinType.ANY: QColor(200, 200, 200),       # 灰色 - 任意类型
    PinType.DATASET: QColor(150, 200, 100),   # 青绿色 - 数据集
    PinType.OPTIMIZER: QColor(255, 200, 100), # 橘色 - 优化器
    PinType.LOSS: QColor(255, 150, 150),      # 淡红色 - 损失函数
}


class PinGraphicsItem(QGraphicsEllipseItem):
    """引脚图形项"""

    def __init__(self, pin, parent=None):
        """
        初始化引脚图形项
        
        Args:
            pin: 核心引脚对象
            parent: 父图形项（通常是 NodeGraphicsItem）
        """
        # 引脚圆形的大小
        radius = 6
        super().__init__(-radius, -radius, radius * 2, radius * 2, parent)

        self.pin = pin
        self.radius = radius

        # 设置标志
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, False)
        self.setAcceptHoverEvents(True)

        # 状态
        self._is_hovered = False

        # 设置颜色
        self.update_appearance()

        logger.debug(f"Created pin graphics item: {pin.name} ({pin.pin_type.value})")

    def update_appearance(self):
        """更新外观"""
        # 获取引脚类型颜色
        color = PIN_TYPE_COLORS.get(self.pin.pin_type, QColor(150, 150, 150))

        # 设置边框
        pen = QPen(color.darker(150))
        pen.setWidth(2)
        self.setPen(pen)

        # 设置填充
        if self.pin.is_connected:
            # 已连接：实心
            self.setBrush(QBrush(color))
        else:
            # 未连接：半透明
            color.setAlpha(150)
            self.setBrush(QBrush(color))

    def hoverEnterEvent(self, event):
        """鼠标进入事件"""
        self._is_hovered = True
        # 高亮显示
        pen = self.pen()
        pen.setWidth(3)
        self.setPen(pen)
        
        # TODO: 显示工具提示
        tooltip = f"{self.pin.label}\n类型: {self.pin.pin_type.value}"
        if self.pin.is_connected:
            tooltip += f"\n连接数: {len(self.pin.connections)}"
        self.setToolTip(tooltip)
        
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        """鼠标离开事件"""
        self._is_hovered = False
        # 恢复正常
        pen = self.pen()
        pen.setWidth(2)
        self.setPen(pen)
        super().hoverLeaveEvent(event)

    def mousePressEvent(self, event):
        """鼠标按下事件 - 开始拖拽连接"""
        if event.button() == Qt.MouseButton.LeftButton:
            logger.info(f"[PIN DRAG] 开始拖拽引脚: {self.pin.full_path}")
            logger.info(f"[PIN DRAG] 引脚类型: {'输入' if self.pin.is_input else '输出'}")
            logger.info(f"[PIN DRAG] 是否已连接: {self.pin.is_connected}")
            if self.pin.is_connected:
                logger.info(f"[PIN DRAG] 当前连接数: {len(self.pin.connections)}")
                for conn in self.pin.connections:
                    logger.info(f"[PIN DRAG]   - 连接: {conn.source_pin.full_path} -> {conn.target_pin.full_path}")
            
            # 通知场景开始拖拽连接
            scene = self.scene()
            if scene and hasattr(scene, 'start_connection_drag'):
                scene.start_connection_drag(self)
            event.accept()
        else:
            super().mousePressEvent(event)
    
    def mouseReleaseEvent(self, event):
        """鼠标释放事件 - 完成连接"""
        if event.button() == Qt.MouseButton.LeftButton:
            # 通知场景完成连接
            scene = self.scene()
            if scene and hasattr(scene, 'finish_connection_drag'):
                scene.finish_connection_drag(self)
            event.accept()
        else:
            super().mouseReleaseEvent(event)

    def get_center_scene_pos(self) -> QPointF:
        """获取引脚中心的场景坐标"""
        return self.scenePos()
