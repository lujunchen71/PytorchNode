"""
ProjectController - 项目操作控制器

职责:
- 项目保存/加载
- 序列化/反序列化
- 项目状态管理
"""

from typing import Optional, Tuple
from PyQt6.QtCore import QObject, pyqtSignal
from pathlib import Path

import logging

logger = logging.getLogger(__name__)


class ProjectController(QObject):
    """项目操作控制器"""

    # 信号
    project_saved = pyqtSignal(str)  # 文件路径
    project_loaded = pyqtSignal(str)  # 文件路径
    project_closed = pyqtSignal()
    load_error = pyqtSignal(str)  # 错误信息
    save_error = pyqtSignal(str)  # 错误信息

    def __init__(self, main_window):
        """
        初始化项目控制器
        
        Args:
            main_window: MainWindow 实例
        """
        super().__init__(main_window)
        self.main_window = main_window
        self._current_project_path: Optional[str] = None

    @property
    def current_project_path(self) -> Optional[str]:
        """获取当前项目路径"""
        return self._current_project_path

    @current_project_path.setter
    def current_project_path(self, value: Optional[str]):
        """设置当前项目路径"""
        self._current_project_path = value

    def save_to_file(self, file_path: str) -> bool:
        """
        保存项目到文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            是否成功
        """
        from core.serialization.serializer import Serializer
        
        try:
            success = Serializer.save_to_file(self.main_window.node_graph, file_path)
            
            if success:
                self._current_project_path = file_path
                total_nodes, total_conns = self._count_all_nodes()
                logger.info(f"Project saved to: {file_path}")
                logger.info(f"  - Nodes: {total_nodes}, Connections: {total_conns}")
                self.project_saved.emit(file_path)
                return True
            else:
                error_msg = f"无法保存项目到: {file_path}"
                logger.error(f"Failed to save project to: {file_path}")
                self.save_error.emit(error_msg)
                return False
                
        except Exception as e:
            error_msg = f"保存项目时发生错误: {e}"
            logger.error(f"Save error: {e}")
            import traceback
            logger.error(traceback.format_exc())
            self.save_error.emit(error_msg)
            return False

    def load_from_file(self, file_path: str) -> bool:
        """
        从文件加载项目
        
        Args:
            file_path: 文件路径
            
        Returns:
            是否成功
        """
        from core.serialization.serializer import Serializer
        
        try:
            logger.info(f"Loading project from: {file_path}")
            
            # 从文件加载数据
            project_data = Serializer.load_from_file(file_path)
            
            if project_data is None:
                error_msg = f"无法加载项目文件: {file_path}"
                logger.error(f"Failed to load project file: {file_path}")
                self.load_error.emit(error_msg)
                return False
            
            graph_data = project_data["graph"]
            
            # 第一步：清空当前场景和节点图
            logger.info("Clearing current graph...")
            self._clear_scene()
            
            # 第二步：递归反序列化节点图（包括子图）
            logger.info("Deserializing graph with subgraphs...")
            self._deserialize_graph_recursive(graph_data, self.main_window.node_graph)
            
            # 第三步：重新初始化子图引用
            self._reinitialize_subgraphs()
            
            # 第四步：创建当前图的节点图形项
            logger.info(f"Creating graphics items for current graph: {self.main_window.current_path}")
            self.main_window._display_graph_nodes()
            
            # 更新状态
            self._current_project_path = file_path
            
            total_nodes, total_conns = self._count_all_nodes()
            logger.info(f"Project loaded from: {file_path}")
            logger.info(f"  - Nodes: {total_nodes}, Connections: {total_conns}")
            self.project_loaded.emit(file_path)
            
            return True
                
        except Exception as e:
            error_msg = f"加载项目时发生错误: {e}"
            logger.error(f"Load error: {e}")
            import traceback
            logger.error(traceback.format_exc())
            self.load_error.emit(error_msg)
            return False

    def new_project(self) -> bool:
        """
        创建新项目
        
        Returns:
            是否成功
        """
        try:
            # 清空当前场景和节点图
            self._clear_scene()
            
            # 重新初始化节点图
            self.main_window._init_node_graph()
            
            # 重新初始化子图
            self._reinitialize_subgraphs()
            
            # 显示当前图
            self.main_window._display_graph_nodes()
            
            # 清除项目路径
            self._current_project_path = None
            
            logger.info("Created new project")
            self.project_closed.emit()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to create new project: {e}")
            return False

    def _deserialize_graph_recursive(self, graph_data: dict, node_graph):
        """
        递归反序列化节点图（包括所有子图）
        
        Args:
            graph_data: 图数据字典
            node_graph: 目标节点图对象
        """
        from core.base import NodeFactory, NodeGraph
        from core.base.connection import Connection
        from core.nodes.subnet.subnet_node import SubnetNode
        
        logger.info(f"[DESERIALIZE] Deserializing graph: {graph_data.get('name', 'unknown')}")
        
        # 1. 反序列化当前层的节点
        for node_data in graph_data.get("nodes", []):
            try:
                node_type = node_data.get("type")
                node_name = node_data.get("name")
                node_id = node_data.get("id")
                position = node_data.get("position", [0.0, 0.0])
                properties = node_data.get("properties", {})
                instance_parameters = node_data.get("instance_parameters", {})
                
                logger.info(f"[DESERIALIZE] Creating node: {node_name} (type={node_type})")
                
                # 创建节点
                node = NodeFactory.create_node(
                    node_type=node_type,
                    name=node_name,
                    node_graph=node_graph
                )
                
                # 恢复ID和位置
                node.id = node_id
                node.position = tuple(position)
                
                # 恢复属性
                for key, value in properties.items():
                    node.set_property(key, value)
                
                # 恢复实例参数
                if instance_parameters:
                    node.instance_parameters = instance_parameters.copy()
                
                # 添加到节点图
                node_graph.add_node(node)
                
                logger.info(f"[DESERIALIZE]   ✓ Node created: {node_name}")
                
            except Exception as e:
                logger.error(f"[DESERIALIZE]   ✗ Failed to create node: {e}")
                import traceback
                logger.error(traceback.format_exc())
        
        # 2. 反序列化当前层的连接
        for conn_data in graph_data.get("connections", []):
            try:
                source_node_id = conn_data.get("source_node_id")
                target_node_id = conn_data.get("target_node_id")
                source_pin_name = conn_data.get("source_pin")
                target_pin_name = conn_data.get("target_pin")
                conn_id = conn_data.get("id")
                
                # 使用ID查找节点
                source_node = node_graph.get_node_by_id(source_node_id) if source_node_id else None
                target_node = node_graph.get_node_by_id(target_node_id) if target_node_id else None
                
                # 回退到名称查找
                if source_node is None:
                    source_path = conn_data.get("source_node", "")
                    source_name = source_path.split('/')[-1] if '/' in source_path else source_path
                    source_node = node_graph.get_node(source_name)
                
                if target_node is None:
                    target_path = conn_data.get("target_node", "")
                    target_name = target_path.split('/')[-1] if '/' in target_path else target_path
                    target_node = node_graph.get_node(target_name)
                
                if source_node and target_node:
                    source_pin = source_node.get_output_pin(source_pin_name)
                    target_pin = target_node.get_input_pin(target_pin_name)
                    
                    if source_pin and target_pin:
                        conn = Connection(source_pin, target_pin)
                        conn.id = conn_id
                        node_graph.add_connection(conn)
                        logger.info(f"[DESERIALIZE]   ✓ Connection: {source_node.name}.{source_pin_name} -> {target_node.name}.{target_pin_name}")
                    else:
                        logger.warning(f"[DESERIALIZE]   ✗ Pins not found: {source_pin_name}, {target_pin_name}")
                else:
                    logger.warning(f"[DESERIALIZE]   ✗ Nodes not found: source={source_node}, target={target_node}")
                    
            except Exception as e:
                logger.error(f"[DESERIALIZE]   ✗ Failed to create connection: {e}")
        
        # 3. 递归反序列化子图
        for subgraph_name, subgraph_data in graph_data.get("subgraphs", {}).items():
            try:
                logger.info(f"[DESERIALIZE] Creating subgraph: {subgraph_name}")
                
                # 创建子图对象
                subgraph = NodeGraph(subgraph_name, parent=node_graph)
                
                # 递归反序列化子图
                self._deserialize_graph_recursive(subgraph_data, subgraph)
                
                # 添加到父图
                node_graph.subgraphs[subgraph_name] = subgraph
                
                logger.info(f"[DESERIALIZE]   ✓ Subgraph created: {subgraph_name} with {len(subgraph.nodes)} nodes")
                
            except Exception as e:
                logger.error(f"[DESERIALIZE]   ✗ Failed to create subgraph {subgraph_name}: {e}")
                import traceback
                logger.error(traceback.format_exc())
        
        # 4. 恢复SubnetNode的内部子图引用
        for node in node_graph.nodes.values():
            if node.node_type == "subnet":
                # 检查是否有对应的子图
                if node.name in node_graph.subgraphs:
                    # 恢复子图引用
                    node._subgraph = node_graph.subgraphs[node.name]
                    node._subgraph.parent = node_graph
                    logger.info(f"[DESERIALIZE]   ✓ Restored subnet '{node.name}' subgraph reference")

    def _count_all_nodes(self) -> Tuple[int, int]:
        """
        统计所有节点和连接数量（包括子图）
        
        Returns:
            (总节点数, 总连接数)
        """
        def count_recursive(node_graph):
            total_nodes = len(node_graph.nodes)
            total_conns = len(node_graph.connections)
            for subgraph in node_graph.subgraphs.values():
                sub_nodes, sub_conns = count_recursive(subgraph)
                total_nodes += sub_nodes
                total_conns += sub_conns
            return total_nodes, total_conns
        
        return count_recursive(self.main_window.node_graph)

    def _clear_scene(self):
        """清空当前场景和节点图"""
        logger.info("Clearing scene...")
        
        try:
            # 清空连接图形项
            for connection_item in list(self.main_window.connection_graphics_items.values()):
                self.main_window.graphics_scene.removeItem(connection_item)
            self.main_window.connection_graphics_items.clear()
            
            # 清空节点图形项
            for node_item in list(self.main_window.node_graphics_items.values()):
                self.main_window.graphics_scene.removeItem(node_item)
            self.main_window.node_graphics_items.clear()
            
            # 清空节点图
            self.main_window.node_graph.clear()
            
            logger.info("Scene cleared successfully")
            
        except Exception as e:
            logger.error(f"Error clearing scene: {e}")
            import traceback
            logger.error(traceback.format_exc())

    def _reinitialize_subgraphs(self):
        """
        重新初始化子图引用
        
        在加载项目后调用，确保 obj, vis, train 三个主要子图的引用正确
        """
        from core.base import NodeGraph
        
        logger.info("Reinitializing subgraphs...")
        
        # 检查 subgraphs 中是否有 obj, vis, train
        if "obj" in self.main_window.node_graph.subgraphs:
            self.main_window.obj_graph = self.main_window.node_graph.subgraphs["obj"]
            logger.info(f"  obj_graph: {len(self.main_window.obj_graph.nodes)} nodes")
        else:
            # 如果没有，创建新的子图
            self.main_window.obj_graph = NodeGraph("obj", parent=self.main_window.node_graph)
            self.main_window.node_graph.subgraphs["obj"] = self.main_window.obj_graph
            logger.info("  Created new obj_graph")
        
        if "vis" in self.main_window.node_graph.subgraphs:
            self.main_window.vis_graph = self.main_window.node_graph.subgraphs["vis"]
            logger.info(f"  vis_graph: {len(self.main_window.vis_graph.nodes)} nodes")
        else:
            self.main_window.vis_graph = NodeGraph("vis", parent=self.main_window.node_graph)
            self.main_window.node_graph.subgraphs["vis"] = self.main_window.vis_graph
            logger.info("  Created new vis_graph")
        
        if "train" in self.main_window.node_graph.subgraphs:
            self.main_window.train_graph = self.main_window.node_graph.subgraphs["train"]
            logger.info(f"  train_graph: {len(self.main_window.train_graph.nodes)} nodes")
        else:
            self.main_window.train_graph = NodeGraph("train", parent=self.main_window.node_graph)
            self.main_window.node_graph.subgraphs["train"] = self.main_window.train_graph
            logger.info("  Created new train_graph")
        
        # 确保当前图指向有效的子图
        if self.main_window.current_path == "/obj":
            self.main_window.current_graph = self.main_window.obj_graph
        elif self.main_window.current_path == "/vis":
            self.main_window.current_graph = self.main_window.vis_graph
        elif self.main_window.current_path == "/train":
            self.main_window.current_graph = self.main_window.train_graph
        else:
            # 默认使用 obj
            self.main_window.current_graph = self.main_window.obj_graph
            self.main_window.current_path = "/obj"
        
        # 更新面包屑导航栏
        self.main_window.path_nav_bar.set_path(self.main_window.current_path)
        
        logger.info(f"Subgraphs reinitialized. Current path: {self.main_window.current_path}")

    def has_unsaved_changes(self) -> bool:
        """
        检查是否有未保存的更改
        
        Returns:
            是否有未保存的更改
        """
        # TODO: 实现更改跟踪
        return False

    def get_project_name(self) -> str:
        """
        获取项目名称
        
        Returns:
            项目名称
        """
        if self._current_project_path:
            return Path(self._current_project_path).stem
        return "未命名项目"
