"""
删除节点命令 - 支持撤销/重做
T053 [P] [US1] 实现DeleteNodeCommand
"""

from typing import List, Optional
from core.undo.command import Command
import logging


logger = logging.getLogger(__name__)


class DeleteNodeCommand(Command):
    """删除节点命令"""

    def __init__(self, node_graph, node, graphics_scene=None, graphics_item=None):
        """
        初始化删除节点命令

        Args:
            node_graph: 节点图对象
            node: 要删除的节点
            graphics_scene: 图形场景（可选）
            graphics_item: 节点图形项（可选）
        """
        super().__init__(f"删除节点: {node.name}")
        self.node_graph = node_graph
        self.node = node
        self.graphics_scene = graphics_scene
        self.graphics_item = graphics_item

        # 保存节点的连接（用于撤销时恢复）
        self.saved_connections = []
        self.saved_connection_items = []

    def execute(self) -> bool:
        """执行删除节点"""
        try:
            # 保存节点的所有连接
            self.saved_connections = []
            
            # 获取所有输入连接
            for input_pin in self.node.input_pins.values():
                if input_pin.is_connected:
                    self.saved_connections.extend(list(input_pin.connections))
            
            # 获取所有输出连接
            for output_pin in self.node.output_pins.values():
                if output_pin.is_connected:
                    self.saved_connections.extend(list(output_pin.connections))
            
            # 去重（避免重复保存）
            self.saved_connections = list(set(self.saved_connections))
            
            logger.info(f"保存了 {len(self.saved_connections)} 个连接")

            # 如果有图形场景，保存并移除连接图形项
            if self.graphics_scene:
                from ui.graphics.connection_graphics_item import ConnectionGraphicsItem
                
                self.saved_connection_items = []
                for item in self.graphics_scene.items():
                    if isinstance(item, ConnectionGraphicsItem):
                        if item.connection in self.saved_connections:
                            self.saved_connection_items.append(item)
                            self.graphics_scene.removeItem(item)

            # 删除节点（会自动删除连接）
            self.node_graph.remove_node(self.node)

            # 如果有图形场景，移除图形项
            if self.graphics_scene and self.graphics_item:
                self.graphics_scene.removeItem(self.graphics_item)

            self._executed = True
            logger.info(f"✅ 删除节点: {self.node.name}")
            return True

        except Exception as e:
            logger.error(f"❌ 删除节点失败: {e}")
            import traceback
            logger.error(traceback.format_exc())
            self._executed = False
            return False

    def undo(self) -> bool:
        """撤销删除节点"""
        try:
            # 恢复节点
            self.node_graph.add_node(self.node)

            # 如果有图形场景，恢复图形项
            if self.graphics_scene and self.graphics_item:
                self.graphics_scene.addItem(self.graphics_item)

            # 恢复连接
            for connection in self.saved_connections:
                self.node_graph.add_connection(connection)

            # 恢复连接图形项
            for connection_item in self.saved_connection_items:
                self.graphics_scene.addItem(connection_item)

            self._executed = False
            logger.info(f"↶ 撤销删除节点: {self.node.name}")
            return True

        except Exception as e:
            logger.error(f"❌ 撤销删除节点失败: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return False
