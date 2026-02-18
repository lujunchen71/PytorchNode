"""
连接命令 - 支持撤销/重做
T054 [P] [US1] 实现ConnectCommand
"""

from typing import Optional
from core.undo.command import Command
import logging


logger = logging.getLogger(__name__)


class ConnectCommand(Command):
    """创建连接命令"""

    def __init__(self, node_graph, connection, graphics_scene=None, graphics_item=None):
        """
        初始化连接命令

        Args:
            node_graph: 节点图对象
            connection: 要创建的连接对象
            graphics_scene: 图形场景（可选）
            graphics_item: 连接图形项（可选）
        """
        source_name = connection.source_pin.node.name
        target_name = connection.target_pin.node.name
        super().__init__(f"连接: {source_name} → {target_name}")
        
        self.node_graph = node_graph
        self.connection = connection
        self.graphics_scene = graphics_scene
        self.graphics_item = graphics_item

    def execute(self) -> bool:
        """执行创建连接"""
        try:
            # 添加到节点图
            self.node_graph.add_connection(self.connection)

            # 如果有图形场景，添加图形项
            if self.graphics_scene and self.graphics_item:
                self.graphics_scene.addItem(self.graphics_item)
                
                # 更新引脚外观（显示为已连接状态）
                if hasattr(self.graphics_item, 'source_pin_item'):
                    self.graphics_item.source_pin_item.update_appearance()
                if hasattr(self.graphics_item, 'target_pin_item'):
                    self.graphics_item.target_pin_item.update_appearance()

            self._executed = True
            logger.info(f"✅ 创建连接: {self.connection.source_pin.full_path} → {self.connection.target_pin.full_path}")
            return True

        except Exception as e:
            logger.error(f"❌ 创建连接失败: {e}")
            import traceback
            logger.error(traceback.format_exc())
            self._executed = False
            return False

    def undo(self) -> bool:
        """撤销创建连接"""
        try:
            # 从节点图移除
            self.node_graph.remove_connection(self.connection)

            # 如果有图形场景，移除图形项
            if self.graphics_scene and self.graphics_item:
                self.graphics_scene.removeItem(self.graphics_item)
                
                # 更新引脚外观（显示为未连接状态）
                if hasattr(self.graphics_item, 'source_pin_item'):
                    self.graphics_item.source_pin_item.update_appearance()
                if hasattr(self.graphics_item, 'target_pin_item'):
                    self.graphics_item.target_pin_item.update_appearance()

            self._executed = False
            logger.info(f"↶ 撤销创建连接: {self.connection.source_pin.full_path} → {self.connection.target_pin.full_path}")
            return True

        except Exception as e:
            logger.error(f"❌ 撤销创建连接失败: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return False


class DisconnectCommand(Command):
    """断开连接命令"""

    def __init__(self, node_graph, connection, graphics_scene=None, graphics_item=None):
        """
        初始化断开连接命令

        Args:
            node_graph: 节点图对象
            connection: 要断开的连接对象
            graphics_scene: 图形场景（可选）
            graphics_item: 连接图形项（可选）
        """
        source_name = connection.source_pin.node.name
        target_name = connection.target_pin.node.name
        super().__init__(f"断开连接: {source_name} → {target_name}")
        
        self.node_graph = node_graph
        self.connection = connection
        self.graphics_scene = graphics_scene
        self.graphics_item = graphics_item

    def execute(self) -> bool:
        """执行断开连接"""
        try:
            # 从节点图移除
            self.node_graph.remove_connection(self.connection)

            # 如果有图形场景，移除图形项
            if self.graphics_scene and self.graphics_item:
                self.graphics_scene.removeItem(self.graphics_item)
                
                # 更新引脚外观
                if hasattr(self.graphics_item, 'source_pin_item'):
                    self.graphics_item.source_pin_item.update_appearance()
                if hasattr(self.graphics_item, 'target_pin_item'):
                    self.graphics_item.target_pin_item.update_appearance()

            self._executed = True
            logger.info(f"✅ 断开连接: {self.connection.source_pin.full_path} → {self.connection.target_pin.full_path}")
            return True

        except Exception as e:
            logger.error(f"❌ 断开连接失败: {e}")
            self._executed = False
            return False

    def undo(self) -> bool:
        """撤销断开连接（重新连接）"""
        try:
            # 重新添加到节点图
            self.node_graph.add_connection(self.connection)

            # 如果有图形场景，重新添加图形项
            if self.graphics_scene and self.graphics_item:
                self.graphics_scene.addItem(self.graphics_item)
                
                # 更新引脚外观
                if hasattr(self.graphics_item, 'source_pin_item'):
                    self.graphics_item.source_pin_item.update_appearance()
                if hasattr(self.graphics_item, 'target_pin_item'):
                    self.graphics_item.target_pin_item.update_appearance()

            self._executed = False
            logger.info(f"↶ 撤销断开连接: {self.connection.source_pin.full_path} → {self.connection.target_pin.full_path}")
            return True

        except Exception as e:
            logger.error(f"❌ 撤销断开连接失败: {e}")
            return False
