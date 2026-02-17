"""
节点图形视图 - 显示和交互节点图形场景
"""

from PyQt6.QtWidgets import QGraphicsView, QMenu, QRubberBand, QApplication
from PyQt6.QtCore import Qt, pyqtSignal as Signal, QPointF, QPoint, QRect
from PyQt6.QtGui import QPainter, QWheelEvent, QMouseEvent, QKeyEvent

from core.base import get_registry

import logging


logger = logging.getLogger(__name__)


class NodeGraphicsView(QGraphicsView):
    """节点图形视图"""

    # 自定义信号
    node_create_requested = Signal(str, QPointF)  # 节点类型, 场景坐标

    def __init__(self, scene, parent=None):
        """初始化视图"""
        super().__init__(scene, parent)

        # 视图设置
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setRenderHint(QPainter.RenderHint.TextAntialiasing)
        self.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.FullViewportUpdate)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        # 禁用默认拖拽模式，避免左键拖拽背景
        self.setDragMode(QGraphicsView.DragMode.NoDrag)

        # 缩放设置
        self._zoom = 1.0
        self._zoom_step = 1.15
        self._zoom_range = (0.1, 3.0)

        # 平移设置
        self._is_panning = False
        self._pan_start = QPointF()

        # 框选设置
        self._is_selecting = False
        self._selection_start = QPoint()
        self._rubber_band = None

        logger.info("Node graphics view initialized")

    def mousePressEvent(self, event: QMouseEvent):
        """鼠标按下事件"""
        # 中键平移
        if event.button() == Qt.MouseButton.MiddleButton:
            self._is_panning = True
            self._pan_start = event.pos()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            event.accept()
            return

        # 左键 - 检查是否在空白处按下
        if event.button() == Qt.MouseButton.LeftButton:
            scene_pos = self.mapToScene(event.pos())
            items = self.scene().items(scene_pos)
            
            # 如果点击在空白处，准备框选
            if not items:
                self._is_selecting = True
                self._selection_start = event.pos()
                
                # 创建橡皮筋选择框
                if not self._rubber_band:
                    self._rubber_band = QRubberBand(QRubberBand.Shape.Rectangle, self)
                self._rubber_band.setGeometry(QRect(self._selection_start, self._selection_start))
                self._rubber_band.show()
                
                event.accept()
                return

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        """鼠标移动事件"""
        # 中键平移
        if self._is_panning:
            delta = event.pos() - self._pan_start
            self._pan_start = event.pos()
            self.horizontalScrollBar().setValue(
                self.horizontalScrollBar().value() - delta.x()
            )
            self.verticalScrollBar().setValue(
                self.verticalScrollBar().value() - delta.y()
            )
            event.accept()
            return
        
        # 框选拖拽
        if self._is_selecting:
            if self._rubber_band:
                # 更新橡皮筋选择框
                self._rubber_band.setGeometry(QRect(self._selection_start, event.pos()).normalized())
            event.accept()
            return
        
        # 更新连接拖拽
        scene = self.scene()
        if scene and hasattr(scene, 'is_dragging_connection') and scene.is_dragging_connection():
            scene_pos = self.mapToScene(event.pos())
            scene.update_connection_drag(scene_pos)
            # logger.debug(f"[VIEW] 更新拖拽位置: ({scene_pos.x():.1f}, {scene_pos.y():.1f})")
            event.accept()
            return

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        """鼠标释放事件"""
        # 中键平移结束
        if event.button() == Qt.MouseButton.MiddleButton:
            self._is_panning = False
            self.setCursor(Qt.CursorShape.ArrowCursor)
            event.accept()
            return

        # 右键菜单
        if event.button() == Qt.MouseButton.RightButton:
            self._show_context_menu(event.pos())
            event.accept()
            return
        
        # 左键释放 - 检查是否正在框选
        if event.button() == Qt.MouseButton.LeftButton:
            if self._is_selecting:
                # 完成框选
                self._finish_selection()
                event.accept()
                return
            
            # 检查是否正在拖拽连接
            scene = self.scene()
            if scene and hasattr(scene, 'is_dragging_connection') and scene.is_dragging_connection():
                # 获取释放位置的场景坐标
                scene_pos = self.mapToScene(event.pos())
                logger.info(f"[VIEW] 检测到鼠标释放，场景坐标: ({scene_pos.x():.1f}, {scene_pos.y():.1f})")
                
                # 查找释放位置下的引脚
                from .pin_graphics_item import PinGraphicsItem
                items = scene.items(scene_pos)
                logger.info(f"[VIEW] 释放位置下的图形项数量: {len(items)}")
                
                target_pin = None
                for item in items:
                    logger.info(f"[VIEW]   - 图形项类型: {type(item).__name__}")
                    if isinstance(item, PinGraphicsItem):
                        target_pin = item
                        logger.info(f"[VIEW] ✅ 找到目标引脚: {target_pin.pin.full_path}")
                        break
                
                if not target_pin:
                    logger.info(f"[VIEW] ℹ️ 未找到目标引脚，将在空白处释放")
                
                # 完成连接拖拽
                scene.finish_connection_drag(target_pin)
                event.accept()
                return

        super().mouseReleaseEvent(event)
    
    def _finish_selection(self):
        """完成框选"""
        if not self._rubber_band:
            return
        
        # 隐藏橡皮筋
        self._rubber_band.hide()
        self._is_selecting = False
        
        # 获取选择区域（视图坐标转换为场景坐标）
        selection_rect_view = self._rubber_band.geometry()
        selection_rect_scene = self.mapToScene(selection_rect_view).boundingRect()
        
        # 选择框内的所有项
        from .node_graphics_item_v2 import NodeGraphicsItemV2
        
        # 清除当前选择（如果没有按Ctrl/Shift）
        modifiers = QApplication.keyboardModifiers()
        if not (modifiers & (Qt.KeyboardModifier.ControlModifier | Qt.KeyboardModifier.ShiftModifier)):
            self.scene().clearSelection()
        
        # 选择框内的节点
        selected_count = 0
        for item in self.scene().items(selection_rect_scene, Qt.ItemSelectionMode.IntersectsItemShape):
            if isinstance(item, NodeGraphicsItemV2):
                item.setSelected(True)
                selected_count += 1
        
        logger.info(f"框选了 {selected_count} 个节点")

    def wheelEvent(self, event: QWheelEvent):
        """鼠标滚轮事件 - 缩放"""
        # 计算缩放因子
        if event.angleDelta().y() > 0:
            zoom_factor = self._zoom_step
        else:
            zoom_factor = 1 / self._zoom_step

        # 应用缩放
        new_zoom = self._zoom * zoom_factor

        # 限制缩放范围
        if self._zoom_range[0] <= new_zoom <= self._zoom_range[1]:
            self.scale(zoom_factor, zoom_factor)
            self._zoom = new_zoom

        event.accept()

    def keyPressEvent(self, event: QKeyEvent):
        """键盘按下事件"""
        # Delete 键删除选中的节点
        if event.key() == Qt.Key.Key_Delete:
            selected_items = self.scene().selectedItems()
            if selected_items:
                logger.info(f"Deleting {len(selected_items)} selected items")
                # TODO: 实现删除逻辑
            event.accept()
            return

        # F 键适应视图
        if event.key() == Qt.Key.Key_F:
            self._fit_in_view()
            event.accept()
            return

        super().keyPressEvent(event)

    def _show_context_menu(self, pos):
        """显示右键菜单"""
        # 获取场景坐标
        scene_pos = self.mapToScene(pos)

        logger.info(f"Showing context menu at scene position: ({scene_pos.x():.1f}, {scene_pos.y():.1f})")

        # 创建菜单
        menu = QMenu(self)
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

        # 获取节点注册表
        registry = get_registry()
        categories = registry.get_categories()

        if not categories:
            # 如果没有注册的节点，显示提示
            no_nodes_action = menu.addAction("(没有可用的节点)")
            no_nodes_action.setEnabled(False)
        else:
            # 按分类添加节点
            for category in sorted(categories):
                # 创建子菜单
                category_menu = menu.addMenu(category)
                
                # 获取该分类下的所有节点
                node_types = registry.get_nodes_in_category(category)
                
                for node_type in sorted(node_types):
                    # 获取节点信息
                    node_info = registry.get_node_info(node_type)
                    display_name = node_info.get("display_name", node_type)
                    
                    # 创建动作
                    action = category_menu.addAction(display_name)
                    # 使用lambda捕获参数
                    action.triggered.connect(
                        lambda checked, nt=node_type, sp=scene_pos: self._on_create_node(nt, sp)
                    )

        # 显示菜单
        menu.exec(self.mapToGlobal(pos))

    def _on_create_node(self, node_type: str, scene_pos: QPointF):
        """创建节点"""
        logger.info(f"Creating node: {node_type} at ({scene_pos.x():.1f}, {scene_pos.y():.1f})")
        self.node_create_requested.emit(node_type, scene_pos)

    def _fit_in_view(self):
        """适应视图"""
        items = self.scene().items()
        if items:
            rect = self.scene().itemsBoundingRect()
            self.fitInView(rect, Qt.AspectRatioMode.KeepAspectRatio)
            self._zoom = 1.0
        else:
            # 如果没有项目，重置视图
            self.resetTransform()
            self._zoom = 1.0

    def reset_zoom(self):
        """重置缩放"""
        self.resetTransform()
        self._zoom = 1.0
