"""
GraphController - 图操作控制器

职责:
- 节点创建/删除
- 连接创建/删除
- 路径切换
- 子网操作
- 图显示管理
"""

from typing import Optional, List, Tuple
from PyQt6.QtCore import QObject, pyqtSignal

from core.base import NodeGraph, NodeFactory
from core.base.connection import Connection
from core.base.node import Node

import logging

logger = logging.getLogger(__name__)


class GraphController(QObject):
    """图操作控制器"""

    # 信号
    node_created = pyqtSignal(object)  # Node
    node_deleted = pyqtSignal(object)  # Node
    connection_created = pyqtSignal(object)  # Connection
    connection_deleted = pyqtSignal(object)  # Connection
    path_changed = pyqtSignal(str)  # 新路径
    subnet_entered = pyqtSignal(object)  # SubnetNode
    status_message = pyqtSignal(str)  # 状态消息

    def __init__(self, main_window):
        """
        初始化图控制器
        
        Args:
            main_window: MainWindow 实例
        """
        super().__init__(main_window)
        self.main_window = main_window

    @property
    def current_graph(self) -> NodeGraph:
        """获取当前图"""
        return self.main_window.current_graph

    @property
    def current_path(self) -> str:
        """获取当前路径"""
        return self.main_window.current_path

    # ==================== 节点操作 ====================

    def create_node(self, node_type: str, position: Tuple[float, float]) -> Optional[Node]:
        """
        创建节点
        
        Args:
            node_type: 节点类型
            position: 节点位置
            
        Returns:
            创建的节点，如果失败则返回 None
        """
        try:
            from core.undo.commands import AddNodeCommand
            from ui.graphics.node_graphics_item_v2 import NodeGraphicsItemV2
            
            # 在当前活动图中创建节点
            node = NodeFactory.create_node(node_type, node_graph=self.current_graph)
            node.position = position
            
            # 创建图形项
            graphics_item = NodeGraphicsItemV2(node)
            graphics_item.setPos(position[0], position[1])
            
            # 保存映射
            self.main_window.node_graphics_items[node] = graphics_item
            
            # 使用Command模式（支持撤销/重做）
            command = AddNodeCommand(
                self.current_graph,
                node,
                self.main_window.graphics_scene,
                graphics_item
            )
            self.main_window.undo_stack.push(command)
            
            # 更新撤销/重做菜单
            self.main_window._update_undo_redo_actions()
            
            logger.info(f"Created node: {node.name} ({node_type}) at {self.current_path}")
            self.status_message.emit(f"创建节点: {node.display_name} ({node.name}) @ {self.current_path}")
            self.node_created.emit(node)
            
            return node
            
        except Exception as e:
            logger.error(f"Failed to create node: {e}")
            self.status_message.emit(f"创建节点失败: {e}")
            return None

    def create_node_from_palette(self, node_type: str):
        """
        从面板双击创建节点（在画布中心创建）
        
        Args:
            node_type: 节点类型
        """
        from PyQt6.QtCore import QPointF
        
        # 获取视图中心的场景坐标
        view_center = self.main_window.graphics_view.viewport().rect().center()
        scene_pos = self.main_window.graphics_view.mapToScene(view_center)
        
        logger.info(f"Creating node from palette: {node_type} at view center")
        
        # 调用统一的创建节点方法
        self.create_node(node_type, (scene_pos.x(), scene_pos.y()))

    def delete_nodes(self, nodes: List[Node]) -> int:
        """
        删除多个节点
        
        Args:
            nodes: 要删除的节点列表
            
        Returns:
            成功删除的节点数
        """
        from core.undo.commands import DeleteNodeCommand
        
        deleted_count = 0
        logger.info(f"[GRAPH] 删除 {len(nodes)} 个节点")
        
        for node in nodes:
            try:
                node_item = self.main_window.node_graphics_items.get(node)
                
                if node_item:
                    command = DeleteNodeCommand(
                        self.current_graph,
                        node,
                        self.main_window.graphics_scene,
                        node_item
                    )
                    self.main_window.undo_stack.push(command)
                    
                    if node in self.main_window.node_graphics_items:
                        del self.main_window.node_graphics_items[node]
                    
                    deleted_count += 1
                    logger.info(f"[GRAPH] ✅ 节点已删除: {node.name}")
                    self.node_deleted.emit(node)
            
            except Exception as e:
                logger.error(f"[GRAPH] ❌ 删除节点失败: {node.name} - {e}")
        
        # 更新撤销/重做菜单
        self.main_window._update_undo_redo_actions()
        self.status_message.emit(f"已删除 {deleted_count} 个节点")
        
        return deleted_count

    # ==================== 连接操作 ====================

    def create_connection(self, source_pin, target_pin) -> Optional[Connection]:
        """
        创建连接
        
        Args:
            source_pin: 源引脚
            target_pin: 目标引脚
            
        Returns:
            创建的连接，如果失败则返回 None
        """
        try:
            from core.undo.commands import ConnectCommand
            from ui.graphics.connection_graphics_item import ConnectionGraphicsItem
            
            logger.info(f"[GRAPH] 创建连接: {source_pin.full_path} → {target_pin.full_path}")
            
            connection = Connection(source_pin, target_pin)
            
            source_node_item = self.main_window.node_graphics_items.get(source_pin.node)
            target_node_item = self.main_window.node_graphics_items.get(target_pin.node)
            
            if source_node_item and target_node_item:
                source_pin_item = source_node_item.output_pin_items.get(source_pin.name)
                target_pin_item = target_node_item.input_pin_items.get(target_pin.name)
                
                if source_pin_item and target_pin_item:
                    connection_item = ConnectionGraphicsItem(connection, source_pin_item, target_pin_item)
                    self.main_window.connection_graphics_items[connection] = connection_item
                    
                    command = ConnectCommand(
                        self.current_graph,
                        connection,
                        self.main_window.graphics_scene,
                        connection_item
                    )
                    self.main_window.undo_stack.push(command)
                    
                    self.main_window._update_undo_redo_actions()
                    
                    logger.info(f"[GRAPH] ✅ 连接创建成功: {source_pin.full_path} → {target_pin.full_path}")
                    self.status_message.emit(f"创建连接: {source_pin.node.name}.{source_pin.name} → {target_pin.node.name}.{target_pin.name}")
                    self.connection_created.emit(connection)
                    return connection
            
            logger.error("[GRAPH] ❌ 找不到节点图形项")
            return None
            
        except Exception as e:
            logger.error(f"[GRAPH] ❌ 创建连接失败: {e}")
            import traceback
            logger.error(traceback.format_exc())
            self.status_message.emit(f"创建连接失败: {e}")
            return None

    def delete_connection(self, connection: Connection) -> bool:
        """
        删除连接
        
        Args:
            connection: 要删除的连接
            
        Returns:
            是否成功
        """
        try:
            from core.undo.commands import DisconnectCommand
            
            logger.info(f"[GRAPH] 删除连接: {connection.source_pin.full_path} → {connection.target_pin.full_path}")
            
            connection_item = self.main_window.connection_graphics_items.get(connection)
            
            if connection_item:
                command = DisconnectCommand(
                    self.current_graph,
                    connection,
                    self.main_window.graphics_scene,
                    connection_item
                )
                self.main_window.undo_stack.push(command)
                
                del self.main_window.connection_graphics_items[connection]
                
                # 更新引脚外观
                source_node_item = self.main_window.node_graphics_items.get(connection.source_pin.node)
                target_node_item = self.main_window.node_graphics_items.get(connection.target_pin.node)
                
                if source_node_item:
                    source_pin_item = source_node_item.output_pin_items.get(connection.source_pin.name)
                    if source_pin_item:
                        source_pin_item.update_appearance()
                
                if target_node_item:
                    target_pin_item = target_node_item.input_pin_items.get(connection.target_pin.name)
                    if target_pin_item:
                        target_pin_item.update_appearance()
                
                self.main_window._update_undo_redo_actions()
                
                logger.info(f"[GRAPH] ✅ 连接删除成功")
                self.status_message.emit(f"删除连接: {connection.source_pin.node.name}.{connection.source_pin.name} → {connection.target_pin.node.name}.{connection.target_pin.name}")
                self.connection_deleted.emit(connection)
                return True
            
            logger.warning("[GRAPH] ⚠️ 未找到连接图形项")
            return False
            
        except Exception as e:
            logger.error(f"[GRAPH] ❌ 删除连接失败: {e}")
            import traceback
            logger.error(traceback.format_exc())
            self.status_message.emit(f"删除连接失败: {e}")
            return False

    # ==================== 路径操作 ====================

    def switch_path(self, new_path: str) -> bool:
        """
        切换路径
        
        Args:
            new_path: 新路径
            
        Returns:
            是否成功
        """
        if new_path == self.current_path:
            return False
        
        logger.info(f"Switching path: {self.current_path} -> {new_path}")
        
        # 获取对应的节点图
        if new_path == "/obj":
            new_graph = self.main_window.obj_graph
        elif new_path == "/vis":
            new_graph = self.main_window.vis_graph
        elif new_path == "/train":
            new_graph = self.main_window.train_graph
        else:
            logger.warning(f"Unknown path: {new_path}")
            return False
        
        # 清空当前场景显示的节点
        self._clear_scene_display()
        
        # 更新当前图和路径
        self.main_window.current_graph = new_graph
        self.main_window.current_path = new_path
        
        # 更新视图的路径上下文
        self.main_window.graphics_view.current_path = new_path
        
        # 更新节点面板的上下文路径
        if hasattr(self.main_window, 'node_palette_panel'):
            self.main_window.node_palette_panel.set_context_path(new_path)
        
        # 显示新图中的所有节点
        self._display_graph_nodes()
        
        logger.info(f"Path switched to: {new_path}, 节点数: {len(new_graph.nodes)}")
        self.status_message.emit(f"切换到路径: {new_path}")
        self.path_changed.emit(new_path)
        
        return True

    def handle_node_double_click(self, node):
        """
        处理节点双击事件
        
        Args:
            node: 被双击的节点
        """
        from core.base.node import NodeCategory
        
        logger.info(f"[DOUBLE CLICK] Node: {node.name}, type: {node.node_type}")
        
        # 根节点可以进入
        if node.node_category == NodeCategory.CONTEXT:
            new_path = None
            if node.node_type == "root.obj":
                new_path = "/obj"
            elif node.node_type == "root.vis":
                new_path = "/vis"
            elif node.node_type == "root.train":
                new_path = "/train"
            
            if new_path:
                if new_path == self.current_path:
                    self.status_message.emit(f"已在路径: {node.display_name}")
                else:
                    self.switch_path(new_path)
                    self.status_message.emit(f"进入: {node.display_name}")
        
        # SubnetNode 也可以进入
        elif node.node_type == "subnet":
            self.enter_subnet(node)
        
        else:
            logger.info(f"Node {node.name} is not a container node")

    def enter_subnet(self, subnet_node):
        """
        进入子网络
        
        Args:
            subnet_node: SubnetNode 实例
        """
        from ui.graphics.node_graphics_item_v2 import NodeGraphicsItemV2
        from ui.graphics.connection_graphics_item import ConnectionGraphicsItem
        
        logger.info(f"Entering subnet: {subnet_node.name}")
        
        # 保存当前路径状态（用于返回）
        self.main_window._parent_path = self.current_path
        self.main_window._parent_graph = self.current_graph
        
        # 清空当前场景显示
        self._clear_scene_display()
        
        # 切换到子图
        self.main_window.current_graph = subnet_node.subgraph
        self.main_window.current_path = f"{self.current_path}/{subnet_node.name}"
        
        # 更新面包屑导航栏
        self.main_window.path_nav_bar.set_path(self.main_window.current_path)
        
        # 更新视图的路径上下文
        self.main_window.graphics_view.current_path = self.main_window.current_path
        
        # 更新节点面板的上下文路径
        if hasattr(self.main_window, 'node_palette_panel'):
            self.main_window.node_palette_panel.set_context_path(self.main_window.current_path)
        
        # 显示子图中的节点
        self._display_subnet_nodes(subnet_node)
        
        logger.info(f"Entered subnet: {subnet_node.name}, nodes: {len(subnet_node.subgraph.nodes)}")
        self.status_message.emit(f"进入子网络: {subnet_node.name}")
        self.subnet_entered.emit(subnet_node)

    # ==================== 子网打包 ====================

    def pack_subnet(self, nodes: List[Node]) -> bool:
        """
        打包节点为子网络
        
        Args:
            nodes: 要打包的节点列表
            
        Returns:
            是否成功
        """
        from core.nodes.subnet.subnet_node import SubnetNode
        from core.nodes.subnet.subnet_pins import SubnetInputPinNode, SubnetOutputPinNode
        from ui.graphics.node_graphics_item_v2 import NodeGraphicsItemV2
        from ui.graphics.connection_graphics_item import ConnectionGraphicsItem
        from core.serialization.subnet_restorer import restore_subnet_subgraph
        
        logger.info(f"[GRAPH] 打包 {len(nodes)} 个节点为子网络")
        
        if len(nodes) < 1:
            self.status_message.emit("需要选中至少1个节点才能打包")
            return False
        
        try:
            # 1. 计算选中节点的边界和中心位置
            min_x = min(n.position[0] for n in nodes)
            max_x = max(n.position[0] for n in nodes)
            min_y = min(n.position[1] for n in nodes)
            max_y = max(n.position[1] for n in nodes)
            center_x = (min_x + max_x) / 2
            center_y = (min_y + max_y) / 2
            
            # 2. 识别头节点和尾节点
            head_nodes, tail_nodes, internal_connections, all_connections_to_remove = \
                self._identify_head_tail_nodes(nodes)
            
            logger.info(f"[GRAPH] 头节点数: {len(head_nodes)}")
            logger.info(f"[GRAPH] 尾节点数: {len(tail_nodes)}")
            
            # 3. 序列化选中的节点和内部连接
            nodes_data, connections_data = self._serialize_nodes_and_connections(
                nodes, internal_connections
            )
            
            # 4. 创建SubnetNode
            input_count = max(len(head_nodes), 1)
            output_count = max(len(tail_nodes), 1)
            
            subnet_name = f"Subnet_{nodes[0].name.split('_')[0] if '_' in nodes[0].name else 'group'}"
            subnet_node = SubnetNode(
                name=subnet_name,
                node_graph=self.current_graph,
                input_count=input_count,
                output_count=output_count
            )
            subnet_node.position = (center_x, center_y)
            
            # 5. 深拷贝：反序列化节点到子图中
            node_name_mapping = self._deep_copy_nodes_to_subnet(
                nodes_data, subnet_node, connections_data
            )
            
            # 6. 深拷贝：反序列化内部连接
            self._deep_copy_connections_to_subnet(connections_data, node_name_mapping, subnet_node)
            
            # 7. 连接InputPin到头节点
            self._connect_input_pins(subnet_node, head_nodes, node_name_mapping)
            
            # 8. 创建OutputPin并连接到尾节点
            self._connect_output_pins(subnet_node, tail_nodes, node_name_mapping)
            
            # 9. 保存外部连接信息
            external_input_connections, external_output_connections = \
                self._save_external_connections(head_nodes, tail_nodes)
            
            # 10. 删除原图中的节点和连接
            self._remove_original_items(
                nodes, all_connections_to_remove, internal_connections
            )
            
            # 11. 添加SubnetNode到当前图
            self.current_graph.add_node(subnet_node)
            self.current_graph.subgraphs[subnet_name] = subnet_node.subgraph
            
            # 12. 创建SubnetNode的图形项
            subnet_graphics = NodeGraphicsItemV2(subnet_node)
            subnet_graphics.setPos(center_x, center_y)
            self.main_window.node_graphics_items[subnet_node] = subnet_graphics
            self.main_window.graphics_scene.addItem(subnet_graphics)
            
            # 13. 重建外部连接
            self._rebuild_external_connections(
                subnet_node, subnet_graphics,
                external_input_connections, external_output_connections
            )
            
            logger.info(f"[GRAPH] ✅ 子网络创建成功: {subnet_name}")
            self.status_message.emit(f"已创建子网络: {subnet_name} (输入: {len(head_nodes)}, 输出: {len(tail_nodes)})")
            
            return True
            
        except Exception as e:
            logger.error(f"[GRAPH] ❌ 打包子网络失败: {e}")
            import traceback
            logger.error(traceback.format_exc())
            self.status_message.emit(f"打包子网络失败: {e}")
            return False

    def _identify_head_tail_nodes(self, nodes: List[Node]):
        """识别头节点和尾节点"""
        head_nodes = []
        tail_nodes = []
        internal_connections = []
        all_connections_to_remove = []
        
        for node in nodes:
            # 检查输入引脚
            for pin_name, pin in node.input_pins.items():
                external_conns = []
                internal_conns = []
                for conn in pin.connections:
                    source_node = conn.source_pin.node
                    if source_node not in nodes:
                        external_conns.append(conn)
                    else:
                        internal_conns.append(conn)
                
                if external_conns:
                    head_nodes.append((node, pin, external_conns))
                    all_connections_to_remove.extend(external_conns)
                internal_connections.extend(internal_conns)
            
            # 检查输出引脚
            for pin_name, pin in node.output_pins.items():
                external_conns = []
                for conn in pin.connections:
                    target_node = conn.target_pin.node
                    if target_node not in nodes:
                        external_conns.append(conn)
                
                if external_conns:
                    tail_nodes.append((node, pin, external_conns))
                    all_connections_to_remove.extend(external_conns)
        
        return head_nodes, tail_nodes, internal_connections, all_connections_to_remove

    def _serialize_nodes_and_connections(self, nodes: List[Node], internal_connections: List):
        """序列化节点和连接"""
        nodes_data = []
        for node in nodes:
            nodes_data.append(node.to_dict())
        
        connections_data = []
        for conn in internal_connections:
            connections_data.append({
                "id": conn.id,
                "source_node_id": conn.source_pin.node.id,
                "target_node_id": conn.target_pin.node.id,
                "source_node": conn.source_pin.node.name,
                "source_pin": conn.source_pin.name,
                "target_node": conn.target_pin.node.name,
                "target_pin": conn.target_pin.name
            })
        
        return nodes_data, connections_data

    def _deep_copy_nodes_to_subnet(self, nodes_data: list, subnet_node, connections_data: list):
        """深拷贝节点到子图"""
        from core.serialization.subnet_restorer import restore_subnet_subgraph
        
        node_name_mapping = {}
        
        for node_data in nodes_data:
            try:
                node_type = node_data.get("type")
                old_name = node_data.get("name")
                
                new_node = NodeFactory.create_node(
                    node_type=node_type,
                    node_graph=subnet_node.subgraph
                )
                
                # 恢复原始名称
                if new_node.name != old_name:
                    new_node._name = old_name
                
                new_node.id = node_data.get("id")
                new_node.position = tuple(node_data.get("position", [0, 0]))
                
                for key, value in node_data.get("properties", {}).items():
                    new_node.set_property(key, value)
                
                if "instance_parameters" in node_data:
                    new_node.instance_parameters = node_data["instance_parameters"].copy()
                
                # 特殊处理SubnetNode
                if node_type == "subnet":
                    new_node._subgraph.parent = subnet_node.subgraph
                    new_node._subgraph.name = new_node.name
                    restore_subnet_subgraph(new_node, node_data, logger)
                
                subnet_node.subgraph.add_node(new_node)
                node_name_mapping[old_name] = new_node
                
                logger.info(f"[GRAPH] 深拷贝节点: {old_name}")
                
            except Exception as e:
                logger.error(f"[GRAPH] 深拷贝节点失败: {e}")
        
        return node_name_mapping

    def _deep_copy_connections_to_subnet(self, connections_data: list, node_name_mapping: dict, subnet_node):
        """深拷贝连接到子图"""
        # 构建节点ID映射
        node_id_mapping = {}
        for old_name, new_node in node_name_mapping.items():
            for node_data in connections_data:
                # 从原始数据获取ID（需要从nodes_data获取）
                pass
        
        for conn_data in connections_data:
            try:
                source_node = node_name_mapping.get(conn_data.get("source_node"))
                target_node = node_name_mapping.get(conn_data.get("target_node"))
                
                if source_node and target_node:
                    source_pin = source_node.get_output_pin(conn_data["source_pin"])
                    target_pin = target_node.get_input_pin(conn_data["target_pin"])
                    
                    if source_pin and target_pin:
                        conn = Connection(source_pin, target_pin)
                        conn.id = conn_data["id"]
                        subnet_node.subgraph.add_connection(conn)
                        logger.info(f"[GRAPH] 深拷贝连接: {source_node.name}.{conn_data['source_pin']} -> {target_node.name}.{conn_data['target_pin']}")
            
            except Exception as e:
                logger.error(f"[GRAPH] 深拷贝连接失败: {e}")

    def _connect_input_pins(self, subnet_node, head_nodes: list, node_name_mapping: dict):
        """连接InputPin到头节点"""
        from core.nodes.subnet.subnet_pins import SubnetInputPinNode
        
        input_pin_y_offset = -100
        existing_input_pins = [n for n in subnet_node.subgraph.nodes.values() if n.node_type == "subnet.input_pin"]
        existing_input_pins.sort(key=lambda n: n.name)
        
        for i, (old_node, old_pin, ext_conns) in enumerate(head_nodes):
            new_node = node_name_mapping.get(old_node.name)
            if not new_node:
                continue
            
            new_pin = new_node.get_input_pin(old_pin.name)
            if not new_pin:
                continue
            
            if i < len(existing_input_pins):
                input_pin_node = existing_input_pins[i]
            else:
                input_pin_node = SubnetInputPinNode(
                    name=f"Input_{i+1}",
                    node_graph=subnet_node.subgraph
                )
                input_pin_node.position = (new_node.position[0], new_node.position[1] + input_pin_y_offset)
                subnet_node.add_internal_node(input_pin_node)
            
            conn = Connection(input_pin_node.output_pins["output"], new_pin)
            subnet_node.subgraph.add_connection(conn)
            
            external_pin_name = f"input_{i}"
            subnet_node.map_input_pin_node(input_pin_node.name, external_pin_name)

    def _connect_output_pins(self, subnet_node, tail_nodes: list, node_name_mapping: dict):
        """创建OutputPin并连接到尾节点"""
        from core.nodes.subnet.subnet_pins import SubnetOutputPinNode
        
        output_pin_y_offset = 100
        for i, (old_node, old_pin, ext_conns) in enumerate(tail_nodes):
            new_node = node_name_mapping.get(old_node.name)
            if not new_node:
                continue
            
            new_pin = new_node.get_output_pin(old_pin.name)
            if not new_pin:
                continue
            
            output_pin_node = SubnetOutputPinNode(
                name=f"Output_{i+1}",
                node_graph=subnet_node.subgraph,
                index=i
            )
            output_pin_node.position = (new_node.position[0], new_node.position[1] + output_pin_y_offset)
            
            subnet_node.add_internal_node(output_pin_node)
            
            conn = Connection(new_pin, output_pin_node.input_pins["input"])
            subnet_node.subgraph.add_connection(conn)
            
            external_pin_name = f"output_{i}"
            subnet_node.map_output_pin_node(output_pin_node.name, external_pin_name)

    def _save_external_connections(self, head_nodes: list, tail_nodes: list):
        """保存外部连接信息"""
        external_input_connections = []
        for i, (old_node, old_pin, ext_conns) in enumerate(head_nodes):
            for ext_conn in ext_conns:
                external_input_connections.append(
                    (ext_conn.source_pin.node, ext_conn.source_pin, i)
                )
        
        external_output_connections = []
        for i, (old_node, old_pin, ext_conns) in enumerate(tail_nodes):
            for ext_conn in ext_conns:
                external_output_connections.append(
                    (i, ext_conn.target_pin.node, ext_conn.target_pin)
                )
        
        return external_input_connections, external_output_connections

    def _remove_original_items(self, nodes: list, all_connections_to_remove: list, internal_connections: list):
        """删除原图中的节点和连接"""
        for conn in all_connections_to_remove:
            if conn in self.main_window.connection_graphics_items:
                old_conn_item = self.main_window.connection_graphics_items[conn]
                if old_conn_item.scene() == self.main_window.graphics_scene:
                    self.main_window.graphics_scene.removeItem(old_conn_item)
                del self.main_window.connection_graphics_items[conn]
            self.current_graph.remove_connection(conn)
        
        for conn in internal_connections:
            if conn in self.main_window.connection_graphics_items:
                old_conn_item = self.main_window.connection_graphics_items[conn]
                if old_conn_item.scene() == self.main_window.graphics_scene:
                    self.main_window.graphics_scene.removeItem(old_conn_item)
                del self.main_window.connection_graphics_items[conn]
            if conn in self.current_graph.connections:
                self.current_graph.connections.remove(conn)
        
        for node in nodes:
            if node in self.main_window.node_graphics_items:
                old_item = self.main_window.node_graphics_items[node]
                if old_item.scene() == self.main_window.graphics_scene:
                    self.main_window.graphics_scene.removeItem(old_item)
                del self.main_window.node_graphics_items[node]
            if node.name in self.current_graph.nodes:
                del self.current_graph.nodes[node.name]

    def _rebuild_external_connections(self, subnet_node, subnet_graphics, external_input_connections: list, external_output_connections: list):
        """重建外部连接"""
        from ui.graphics.connection_graphics_item import ConnectionGraphicsItem
        
        # 外部输入连接
        for external_source_node, external_source_pin, subnet_input_index in external_input_connections:
            try:
                source_node_item = self.main_window.node_graphics_items.get(external_source_node)
                if not source_node_item:
                    continue
                
                subnet_input_pin_name = f"input_{subnet_input_index}"
                subnet_input_pin = subnet_node.input_pins.get(subnet_input_pin_name)
                if not subnet_input_pin:
                    continue
                
                conn = Connection(external_source_pin, subnet_input_pin)
                self.current_graph.add_connection(conn)
                
                source_pin_item = source_node_item.output_pin_items.get(external_source_pin.name)
                subnet_pin_item = subnet_graphics.input_pin_items.get(subnet_input_pin_name)
                
                if source_pin_item and subnet_pin_item:
                    conn_item = ConnectionGraphicsItem(conn, source_pin_item, subnet_pin_item)
                    self.main_window.connection_graphics_items[conn] = conn_item
                    self.main_window.graphics_scene.addItem(conn_item)
            
            except Exception as e:
                logger.error(f"[GRAPH] 重建外部输入连接失败: {e}")
        
        # 外部输出连接
        for subnet_output_index, external_target_node, external_target_pin in external_output_connections:
            try:
                target_node_item = self.main_window.node_graphics_items.get(external_target_node)
                if not target_node_item:
                    continue
                
                subnet_output_pin_name = f"output_{subnet_output_index}"
                subnet_output_pin = subnet_node.output_pins.get(subnet_output_pin_name)
                if not subnet_output_pin:
                    continue
                
                conn = Connection(subnet_output_pin, external_target_pin)
                self.current_graph.add_connection(conn)
                
                subnet_pin_item = subnet_graphics.output_pin_items.get(subnet_output_pin_name)
                target_pin_item = target_node_item.input_pin_items.get(external_target_pin.name)
                
                if subnet_pin_item and target_pin_item:
                    conn_item = ConnectionGraphicsItem(conn, subnet_pin_item, target_pin_item)
                    self.main_window.connection_graphics_items[conn] = conn_item
                    self.main_window.graphics_scene.addItem(conn_item)
            
            except Exception as e:
                logger.error(f"[GRAPH] 重建外部输出连接失败: {e}")

    # ==================== 显示管理 ====================

    def _clear_scene_display(self):
        """清空场景显示（但不删除节点图的数据）"""
        logger.info("Clearing scene display...")
        
        # 移除所有连接图形项
        for connection_item in list(self.main_window.connection_graphics_items.values()):
            if connection_item.scene() == self.main_window.graphics_scene:
                self.main_window.graphics_scene.removeItem(connection_item)
        
        # 移除所有节点图形项
        for node_item in list(self.main_window.node_graphics_items.values()):
            if node_item.scene() == self.main_window.graphics_scene:
                self.main_window.graphics_scene.removeItem(node_item)
        
        # 清空映射字典
        self.main_window.connection_graphics_items.clear()
        self.main_window.node_graphics_items.clear()
        
        logger.info("Scene display cleared")

    def _display_graph_nodes(self):
        """显示当前图中的所有节点"""
        from ui.graphics.node_graphics_item_v2 import NodeGraphicsItemV2
        from ui.graphics.connection_graphics_item import ConnectionGraphicsItem
        from core.base.node import NodeCategory
        
        logger.info(f"Displaying nodes from: {self.current_path}")
        logger.info(f"Nodes in current graph: {len(self.current_graph.nodes)}")
        
        # 显示节点
        for node in self.current_graph.nodes.values():
            # 跳过当前路径对应的根节点
            if node.node_category == NodeCategory.CONTEXT:
                if self.current_path == "/obj" and node.node_type == "root.obj":
                    continue
                elif self.current_path == "/vis" and node.node_type == "root.vis":
                    continue
                elif self.current_path == "/train" and node.node_type == "root.train":
                    continue
            
            if node not in self.main_window.node_graphics_items:
                graphics_item = NodeGraphicsItemV2(node)
                graphics_item.setPos(node.position[0], node.position[1])
                self.main_window.node_graphics_items[node] = graphics_item
            
            graphics_item = self.main_window.node_graphics_items[node]
            
            if graphics_item.scene() != self.main_window.graphics_scene:
                self.main_window.graphics_scene.addItem(graphics_item)
        
        # 显示连接
        for connection in self.current_graph.connections:
            if connection not in self.main_window.connection_graphics_items:
                source_node_item = self.main_window.node_graphics_items.get(connection.source_node)
                target_node_item = self.main_window.node_graphics_items.get(connection.target_node)
                
                if source_node_item and target_node_item:
                    source_pin_item = source_node_item.output_pin_items.get(connection.source_pin.name)
                    target_pin_item = target_node_item.input_pin_items.get(connection.target_pin.name)
                    
                    if source_pin_item and target_pin_item:
                        connection_item = ConnectionGraphicsItem(
                            connection, source_pin_item, target_pin_item
                        )
                        self.main_window.connection_graphics_items[connection] = connection_item
            
            connection_item = self.main_window.connection_graphics_items.get(connection)
            
            if connection_item and connection_item.scene() != self.main_window.graphics_scene:
                self.main_window.graphics_scene.addItem(connection_item)
        
        logger.info(f"Displayed {len(self.current_graph.nodes)} nodes and {len(self.current_graph.connections)} connections")

    def _display_subnet_nodes(self, subnet_node):
        """显示子图中的节点"""
        from ui.graphics.node_graphics_item_v2 import NodeGraphicsItemV2
        from ui.graphics.connection_graphics_item import ConnectionGraphicsItem
        
        logger.info(f"[ENTER_SUBNET] 子图中的节点数: {len(subnet_node.subgraph.nodes)}")
        
        for node in subnet_node.subgraph.nodes.values():
            if node not in self.main_window.node_graphics_items:
                graphics_item = NodeGraphicsItemV2(node)
                graphics_item.setPos(node.position[0], node.position[1])
                self.main_window.node_graphics_items[node] = graphics_item
            
            graphics_item = self.main_window.node_graphics_items[node]
            if graphics_item.scene() != self.main_window.graphics_scene:
                self.main_window.graphics_scene.addItem(graphics_item)
        
        for connection in subnet_node.subgraph.connections:
            if connection not in self.main_window.connection_graphics_items:
                source_node_item = self.main_window.node_graphics_items.get(connection.source_node)
                target_node_item = self.main_window.node_graphics_items.get(connection.target_node)
                
                if source_node_item and target_node_item:
                    source_pin_item = source_node_item.output_pin_items.get(connection.source_pin.name)
                    target_pin_item = target_node_item.input_pin_items.get(connection.target_pin.name)
                    
                    if source_pin_item and target_pin_item:
                        connection_item = ConnectionGraphicsItem(
                            connection, source_pin_item, target_pin_item
                        )
                        self.main_window.connection_graphics_items[connection] = connection_item
            
            connection_item = self.main_window.connection_graphics_items.get(connection)
            if connection_item and connection_item.scene() != self.main_window.graphics_scene:
                self.main_window.graphics_scene.addItem(connection_item)
