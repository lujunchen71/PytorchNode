"""
GraphMixin - 图操作Mixin

职责:
- 节点创建/删除
- 连接创建/删除
- 路径切换
- 子网操作
"""

import logging

logger = logging.getLogger(__name__)


class GraphMixin:
    """图操作Mixin"""

    def _on_node_create_requested(self, node_type: str, scene_pos):
        """处理创建节点请求"""
        self._graph_controller.create_node(node_type, (scene_pos.x(), scene_pos.y()))

    def _on_node_create_from_palette(self, node_type: str):
        """处理从面板双击创建节点"""
        self._graph_controller.create_node_from_palette(node_type)

    def _on_connection_created(self, source_pin, target_pin):
        """处理创建连接请求"""
        self._graph_controller.create_connection(source_pin, target_pin)

    def _on_connection_deleted(self, connection):
        """处理删除连接请求"""
        self._graph_controller.delete_connection(connection)

    def _on_nodes_delete_requested(self, nodes):
        """处理节点删除请求"""
        self._graph_controller.delete_nodes(nodes)

    def _on_pack_subnet_requested(self, nodes):
        """处理打包为子网络请求"""
        self._graph_controller.pack_subnet(nodes)

    def _on_path_changed(self, path: str):
        """处理路径切换"""
        self._graph_controller.switch_path(path)

    def _on_node_double_clicked(self, node):
        """处理节点双击事件"""
        self._graph_controller.handle_node_double_click(node)
