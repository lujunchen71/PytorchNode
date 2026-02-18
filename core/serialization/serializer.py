"""
序列化器 - 将节点图序列化为JSON

职责:
- 节点序列化
- 连接序列化
- 图序列化
"""

import json
import logging
from pathlib import Path


logger = logging.getLogger(__name__)


class Serializer:
    """序列化器类"""

    @staticmethod
    def serialize_graph(node_graph) -> dict:
        """
        序列化节点图为字典
        
        Args:
            node_graph: 节点图对象
            
        Returns:
            序列化的字典
        """
        return node_graph.to_dict()

    @staticmethod
    def _count_all_nodes_and_connections(node_graph) -> tuple:
        """
        递归统计节点图中所有节点和连接的数量（包括子图）
        
        Args:
            node_graph: 节点图对象
            
        Returns:
            (节点总数, 连接总数)
        """
        total_nodes = len(node_graph.nodes)
        total_connections = len(node_graph.connections)
        
        # 递归统计子图
        for subgraph in node_graph.subgraphs.values():
            sub_nodes, sub_conns = Serializer._count_all_nodes_and_connections(subgraph)
            total_nodes += sub_nodes
            total_connections += sub_conns
        
        return total_nodes, total_connections

    @staticmethod
    def save_to_file(node_graph, file_path: str) -> bool:
        """
        保存节点图到文件
        
        Args:
            node_graph: 节点图对象
            file_path: 文件路径
            
        Returns:
            是否成功
        """
        try:
            # 调试：检查 node_graph 状态
            logger.info(f"[SAVE DEBUG] node_graph.name: {node_graph.name}")
            logger.info(f"[SAVE DEBUG] node_graph.nodes: {list(node_graph.nodes.keys())}")
            logger.info(f"[SAVE DEBUG] node_graph.subgraphs: {list(node_graph.subgraphs.keys())}")
            for name, sg in node_graph.subgraphs.items():
                logger.info(f"[SAVE DEBUG]   subgraph '{name}': nodes={list(sg.nodes.keys())}")
            
            # 序列化
            data = Serializer.serialize_graph(node_graph)
            logger.info(f"[SAVE DEBUG] Serialized data subgraphs: {list(data.get('subgraphs', {}).keys())}")
            
            # 添加元数据
            project_data = {
                "version": "0.1.0",
                "type": "pnne_project",
                "graph": data
            }
            
            # 确保目录存在
            path = Path(file_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            
            # 保存JSON
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(project_data, f, indent=2, ensure_ascii=False)
            
            # 递归统计所有节点和连接（包括子图）
            total_nodes, total_connections = Serializer._count_all_nodes_and_connections(node_graph)
            
            logger.info(f"Project saved to: {file_path}")
            logger.info(f"  - Nodes: {total_nodes} (including subgraphs)")
            logger.info(f"  - Connections: {total_connections} (including subgraphs)")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to save project: {e}")
            return False

    @staticmethod
    def load_from_file(file_path: str):
        """
        从文件加载节点图
        
        Args:
            file_path: 文件路径
            
        Returns:
            节点图数据字典 (包含graph_data和metadata)
        """
        try:
            # 读取JSON
            with open(file_path, 'r', encoding='utf-8') as f:
                project_data = json.load(f)
            
            # 验证格式
            if project_data.get("type") != "pnne_project":
                raise ValueError("Invalid project file format")
            
            # 提取图数据
            graph_data = project_data.get("graph")
            if graph_data is None:
                raise ValueError("No graph data found in project file")
            
            logger.info(f"Project loaded from: {file_path}")
            logger.info(f"  - Nodes: {len(graph_data.get('nodes', []))}")
            logger.info(f"  - Connections: {len(graph_data.get('connections', []))}")
            
            return {
                "graph": graph_data,
                "version": project_data.get("version", "0.1.0"),
                "metadata": project_data.get("metadata", {})
            }
            
        except Exception as e:
            logger.error(f"Failed to load project: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return None
    
    @staticmethod
    def deserialize_graph(graph_data: dict, node_graph, node_factory):
        """
        从字典数据恢复节点图
        
        Args:
            graph_data: 图数据字典
            node_graph: 目标节点图对象
            node_factory: 节点工厂
            
        Returns:
            恢复的节点列表
        """
        from core.base.connection import Connection
        
        logger.info(f"Starting deserialization...")
        
        # 第一步：创建所有节点
        created_nodes = []
        for node_data in graph_data.get("nodes", []):
            try:
                node_type = node_data.get("type")
                node_name = node_data.get("name")
                node_id = node_data.get("id")
                position = node_data.get("position", [0.0, 0.0])
                properties = node_data.get("properties", {})
                instance_parameters = node_data.get("instance_parameters", {})
                
                logger.info(f"Creating node: {node_name} (type={node_type})")
                
                # 创建节点
                node = node_factory.create_node(
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
                
                # Phase 3.5: 恢复实例参数
                if instance_parameters:
                    node.instance_parameters = instance_parameters.copy()
                    logger.info(f"  ✓ Restored {len(instance_parameters)} instance parameters")
                
                # 添加到节点图
                node_graph.add_node(node)
                created_nodes.append(node)
                
                logger.info(f"  ✓ Node created: {node_name}")
                
            except Exception as e:
                logger.error(f"Failed to create node: {e}")
                import traceback
                logger.error(traceback.format_exc())
        
        logger.info(f"Created {len(created_nodes)} nodes")
        
        # 第二步：创建所有连接
        created_connections = []
        for conn_data in graph_data.get("connections", []):
            try:
                source_node_path = conn_data.get("source_node")
                source_pin_name = conn_data.get("source_pin")
                target_node_path = conn_data.get("target_node")
                target_pin_name = conn_data.get("target_pin")
                conn_id = conn_data.get("id")
                
                logger.info(f"Creating connection: {source_node_path}.{source_pin_name} -> {target_node_path}.{target_pin_name}")
                
                # 查找节点（使用节点名称，去除路径前缀）
                source_node_name = source_node_path.split('/')[-1]
                target_node_name = target_node_path.split('/')[-1]
                
                source_node = node_graph.get_node(source_node_name)
                target_node = node_graph.get_node(target_node_name)
                
                if source_node is None:
                    logger.error(f"  ✗ Source node not found: {source_node_name}")
                    continue
                
                if target_node is None:
                    logger.error(f"  ✗ Target node not found: {target_node_name}")
                    continue
                
                # 查找引脚
                source_pin = source_node.get_output_pin(source_pin_name)
                target_pin = target_node.get_input_pin(target_pin_name)
                
                if source_pin is None:
                    logger.error(f"  ✗ Source pin not found: {source_node_name}.{source_pin_name}")
                    continue
                
                if target_pin is None:
                    logger.error(f"  ✗ Target pin not found: {target_node_name}.{target_pin_name}")
                    continue
                
                # 创建连接
                connection = Connection(source_pin, target_pin)
                connection.id = conn_id
                
                # 添加到节点图
                node_graph.add_connection(connection)
                created_connections.append(connection)
                
                logger.info(f"  ✓ Connection created")
                
            except Exception as e:
                logger.error(f"Failed to create connection: {e}")
                import traceback
                logger.error(traceback.format_exc())
        
        logger.info(f"Created {len(created_connections)} connections")
        logger.info(f"Deserialization complete!")
        
        return created_nodes
