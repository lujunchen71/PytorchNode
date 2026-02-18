"""
节点图形场景 - 管理节点图形项的场景
"""

from PyQt6.QtWidgets import QGraphicsScene, QMenu
from PyQt6.QtCore import Qt, pyqtSignal as Signal, QPointF
from PyQt6.QtGui import QPen, QColor, QBrush

import logging


logger = logging.getLogger(__name__)


class NodeGraphicsScene(QGraphicsScene):
    """节点图形场景"""

    # 自定义信号
    node_created = Signal(str, float, float)  # 节点类型, x, y
    node_selected = Signal(object)  # 节点对象
    node_double_clicked = Signal(object)  # 节点对象（双击进入）
    nodes_deleted = Signal(list)  # 节点列表
    connection_created = Signal(object, object)  # 源引脚, 目标引脚
    connection_deleted = Signal(object)  # 连接对象
    node_delete_requested = Signal(list)  # 删除节点请求（节点列表）
    pack_subnet_requested = Signal(list)  # 打包子网络请求（节点列表）

    def __init__(self, parent=None):
        """初始化场景"""
        super().__init__(parent)

        # 场景设置
        self.setSceneRect(-10000, -10000, 20000, 20000)

        # 背景网格颜色
        self._grid_color = QColor(60, 60, 60)
        self._bg_color = QColor(40, 40, 40)

        # 设置背景
        self.setBackgroundBrush(QBrush(self._bg_color))
        
        # 连接拖拽状态
        self._dragging_connection = False
        self._drag_start_pin = None
        self._temp_connection_item = None
        self._connections_to_delete = []  # 拖拽时要删除的连接列表

    def drawBackground(self, painter, rect):
        """绘制背景网格"""
        super().drawBackground(painter, rect)

        # 绘制网格
        pen = QPen(self._grid_color)
        pen.setWidth(1)
        painter.setPen(pen)

        # 网格大小
        grid_size = 20
        large_grid_size = 100

        # 获取可见区域
        left = int(rect.left()) - (int(rect.left()) % grid_size)
        top = int(rect.top()) - (int(rect.top()) % grid_size)
        right = int(rect.right())
        bottom = int(rect.bottom())

        # 绘制小网格
        for x in range(left, right, grid_size):
            painter.drawLine(x, top, x, bottom)
        for y in range(top, bottom, grid_size):
            painter.drawLine(left, y, right, y)

        # 绘制大网格
        pen.setColor(QColor(80, 80, 80))
        painter.setPen(pen)
        for x in range(left, right, large_grid_size):
            painter.drawLine(x, top, x, bottom)
        for y in range(top, bottom, large_grid_size):
            painter.drawLine(left, y, right, y)
    
    def start_connection_drag(self, pin_item):
        """
        开始拖拽连接
        
        Args:
            pin_item: 开始拖拽的引脚图形项
        """
        from .connection_graphics_item import TempConnectionGraphicsItem
        
        self._dragging_connection = True
        self._drag_start_pin = pin_item
        
        logger.info(f"[SCENE] 场景开始处理连接拖拽")
        logger.info(f"[SCENE] 源引脚: {pin_item.pin.full_path}")
        logger.info(f"[SCENE] 源引脚已连接: {pin_item.pin.is_connected}")
        
        # 检查引脚是否已有连接，如果有则标记为待删除
        self._connections_to_delete = []
        if pin_item.pin.is_connected:
            # 复制连接列表（避免在迭代时修改）
            self._connections_to_delete = list(pin_item.pin.connections)
            logger.info(f"[SCENE] 引脚已有 {len(self._connections_to_delete)} 个连接，标记为待删除")
            for conn in self._connections_to_delete:
                logger.info(f"[SCENE]   - 待删除连接: {conn.source_pin.full_path} -> {conn.target_pin.full_path}")
        
        # 创建临时连接线
        self._temp_connection_item = TempConnectionGraphicsItem(pin_item)
        self.addItem(self._temp_connection_item)
        logger.info(f"[SCENE] 临时连接线已创建")
    
    def update_connection_drag(self, scene_pos: QPointF):
        """
        更新连接拖拽位置
        
        Args:
            scene_pos: 当前鼠标场景坐标
        """
        if self._dragging_connection and self._temp_connection_item:
            self._temp_connection_item.update_end_pos(scene_pos)
    
    def finish_connection_drag(self, end_pin_item):
        """
        完成连接拖拽
        
        Args:
            end_pin_item: 结束拖拽的引脚图形项（如果在引脚上释放）
        """
        if not self._dragging_connection:
            return
        
        logger.info(f"[SCENE] 完成连接拖拽")
        logger.info(f"[SCENE] 释放位置: {'引脚上' if end_pin_item else '空白处'}")
        if end_pin_item:
            logger.info(f"[SCENE] 目标引脚: {end_pin_item.pin.full_path}")
        
        # 移除临时连接线
        if self._temp_connection_item:
            self.removeItem(self._temp_connection_item)
            self._temp_connection_item = None
            logger.info(f"[SCENE] 临时连接线已移除")
        
        # 如果在有效引脚上释放，创建连接
        if end_pin_item and end_pin_item != self._drag_start_pin:
            start_pin = self._drag_start_pin.pin
            end_pin = end_pin_item.pin
            
            logger.info(f"[SCENE] 尝试创建连接")
            logger.info(f"[SCENE] 起始引脚类型: {'输出' if start_pin.is_output else '输入'}")
            logger.info(f"[SCENE] 目标引脚类型: {'输出' if end_pin.is_output else '输入'}")
            
            # 判断连接方向（输出→输入）
            if start_pin.is_output and end_pin.is_input:
                source_pin = start_pin
                target_pin = end_pin
            elif start_pin.is_input and end_pin.is_output:
                source_pin = end_pin
                target_pin = start_pin
            else:
                logger.warning("[SCENE] ❌ 连接失败: 两个引脚方向相同")
                self._reset_drag_state()
                return
            
            # 检查是否可以连接
            if source_pin.can_connect_to(target_pin):
                # 先删除旧连接（从拖拽开始的引脚）
                self._delete_old_connections()
                
                # 如果目标引脚也已连接且不支持列表，也需要删除其连接
                if target_pin.is_connected and not target_pin.is_list:
                    logger.info(f"[SCENE] 目标引脚已连接，将替换连接")
                    for conn in list(target_pin.connections):
                        logger.info(f"[SCENE] 🗑️ 删除目标引脚的旧连接: {conn.source_pin.full_path} -> {conn.target_pin.full_path}")
                        self.connection_deleted.emit(conn)
                
                logger.info(f"[SCENE] ✅ 创建连接: {source_pin.full_path} → {target_pin.full_path}")
                self.connection_created.emit(source_pin, target_pin)
            else:
                logger.warning(f"[SCENE] ❌ 无法连接: {source_pin.full_path} → {target_pin.full_path}")
                # 无法连接，恢复旧连接（不删除）
                self._connections_to_delete.clear()
        else:
            logger.info(f"[SCENE] ℹ️ 在空白处释放")
            # 如果拖拽起始引脚已有连接，断开这些连接
            if self._connections_to_delete:
                logger.info(f"[SCENE] 将断开 {len(self._connections_to_delete)} 个旧连接")
                self._delete_old_connections()
            else:
                logger.info(f"[SCENE] 无旧连接需要断开")
        
        self._reset_drag_state()
        logger.info(f"[SCENE] 拖拽状态已重置")
    
    def cancel_connection_drag(self):
        """取消连接拖拽"""
        if self._temp_connection_item:
            self.removeItem(self._temp_connection_item)
            self._temp_connection_item = None
        self._reset_drag_state()
    
    def _delete_old_connections(self):
        """删除拖拽开始时标记的旧连接"""
        for conn in self._connections_to_delete:
            logger.info(f"[SCENE] 🗑️ 删除旧连接: {conn.source_pin.full_path} -> {conn.target_pin.full_path}")
            self.connection_deleted.emit(conn)
        self._connections_to_delete.clear()
    
    def _reset_drag_state(self):
        """重置拖拽状态"""
        self._dragging_connection = False
        self._drag_start_pin = None
        self._connections_to_delete.clear()
    
    def is_dragging_connection(self) -> bool:
        """是否正在拖拽连接"""
        return self._dragging_connection
