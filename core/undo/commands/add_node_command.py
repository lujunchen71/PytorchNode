"""
添加节点命令 - 支持撤销/重做
T052 [P] [US1] 实现AddNodeCommand
"""

from typing import Optional
from core.undo.command import Command
import logging


logger = logging.getLogger(__name__)


class AddNodeCommand(Command):
    """添加节点命令"""

    def __init__(self, node_graph, node, graphics_scene=None, graphics_item=None):
        """
        初始化添加节点命令

        Args:
            node_graph: 节点图对象
            node: 要添加的节点
            graphics_scene: 图形场景（可选）
            graphics_item: 节点图形项（可选）
        """
        super().__init__(f"添加节点: {node.name}")
        self.node_graph = node_graph
        self.node = node
        self.graphics_scene = graphics_scene
        self.graphics_item = graphics_item

    def execute(self) -> bool:
        """执行添加节点"""
        try:
            # 添加到节点图
            self.node_graph.add_node(self.node)

            # 如果有图形场景，添加图形项
            if self.graphics_scene and self.graphics_item:
                self.graphics_scene.addItem(self.graphics_item)

            self._executed = True
            logger.info(f"✅ 添加节点: {self.node.name}")
            return True

        except Exception as e:
            logger.error(f"❌ 添加节点失败: {e}")
            self._executed = False
            return False

    def undo(self) -> bool:
        """撤销添加节点"""
        try:
            # 从节点图移除
            self.node_graph.remove_node(self.node)

            # 如果有图形场景，移除图形项
            if self.graphics_scene and self.graphics_item:
                self.graphics_scene.removeItem(self.graphics_item)

            self._executed = False
            logger.info(f"↶ 撤销添加节点: {self.node.name}")
            return True

        except Exception as e:
            logger.error(f"❌ 撤销添加节点失败: {e}")
            return False
