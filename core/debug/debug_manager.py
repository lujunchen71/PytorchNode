"""
调试管理器 - 管理调试类别和日志输出

功能：
- 分类调试（节点、连接、序列化等）
- 调试文件输出
- 全局开关控制
"""

import os
import json
from datetime import datetime
from enum import Enum, auto
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)


class DebugCategory(Enum):
    """调试类别"""
    NODE = auto()           # 节点操作
    CONNECTION = auto()     # 连接操作
    SERIALIZATION = auto()  # 序列化/反序列化
    PACK = auto()           # 打包操作
    UI = auto()             # UI操作
    PATH = auto()           # 路径导航


class DebugManager:
    """调试管理器"""
    
    def __init__(self):
        self._enabled_categories: Dict[DebugCategory, bool] = {
            category: False for category in DebugCategory
        }
        self._debug_dir = "debug_logs"
        self._session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self._operation_counter = 0
        
    def is_enabled(self, category: DebugCategory) -> bool:
        """检查调试类别是否启用"""
        return self._enabled_categories.get(category, False)
    
    def set_enabled(self, category: DebugCategory, enabled: bool):
        """设置调试类别启用状态"""
        self._enabled_categories[category] = enabled
        logger.info(f"调试类别 {category.name} {'启用' if enabled else '禁用'}")
    
    def toggle_category(self, category: DebugCategory) -> bool:
        """切换调试类别状态，返回新状态"""
        new_state = not self._enabled_categories.get(category, False)
        self.set_enabled(category, new_state)
        return new_state
    
    def get_all_categories_status(self) -> Dict[str, bool]:
        """获取所有类别状态"""
        return {category.name: self._enabled_categories[category] for category in DebugCategory}
    
    def _ensure_debug_dir(self):
        """确保调试目录存在"""
        if not os.path.exists(self._debug_dir):
            os.makedirs(self._debug_dir)
    
    def _get_debug_file_path(self, operation_type: str) -> str:
        """获取调试文件路径"""
        self._ensure_debug_dir()
        self._operation_counter += 1
        filename = f"{self._session_id}_{self._operation_counter:03d}_{operation_type}.json"
        return os.path.join(self._debug_dir, filename)
    
    def log_pack_operation(
        self,
        operation_phase: str,
        nodes_before: List[Dict],
        nodes_after: List[Dict],
        connections_before: List[Dict],
        connections_after: List[Dict],
        subnet_data: Optional[Dict] = None,
        nested_subnet_data: Optional[Dict] = None,
        metadata: Optional[Dict] = None
    ):
        """
        记录打包操作的详细信息
        
        Args:
            operation_phase: 操作阶段（before/after/pack/restore）
            nodes_before: 操作前的节点列表
            nodes_after: 操作后的节点列表
            connections_before: 操作前的连接列表
            connections_after: 操作后的连接列表
            subnet_data: 子网络数据
            nested_subnet_data: 嵌套子网络数据
            metadata: 额外元数据
        """
        if not self.is_enabled(DebugCategory.PACK):
            return
        
        debug_data = {
            "timestamp": datetime.now().isoformat(),
            "phase": operation_phase,
            "nodes_before": nodes_before,
            "nodes_after": nodes_after,
            "connections_before": connections_before,
            "connections_after": connections_after,
            "subnet_data": subnet_data,
            "nested_subnet_data": nested_subnet_data,
            "metadata": metadata or {}
        }
        
        file_path = self._get_debug_file_path(f"pack_{operation_phase}")
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(debug_data, f, indent=2, ensure_ascii=False, default=str)
            logger.info(f"[DEBUG] 打包操作日志已保存: {file_path}")
        except Exception as e:
            logger.error(f"[DEBUG] 保存调试日志失败: {e}")
    
    def log_node_mapping(
        self,
        operation: str,
        name_mapping: Dict[str, str],
        pin_mapping: Dict[str, str],
        failed_mappings: List[Dict]
    ):
        """
        记录节点映射信息
        
        Args:
            operation: 操作名称
            name_mapping: 名称映射 {old_name: new_name}
            pin_mapping: 引脚映射
            failed_mappings: 失败的映射
        """
        if not self.is_enabled(DebugCategory.NODE):
            return
        
        debug_data = {
            "timestamp": datetime.now().isoformat(),
            "operation": operation,
            "name_mapping": name_mapping,
            "pin_mapping": pin_mapping,
            "failed_mappings": failed_mappings
        }
        
        file_path = self._get_debug_file_path(f"mapping_{operation}")
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(debug_data, f, indent=2, ensure_ascii=False, default=str)
            logger.info(f"[DEBUG] 节点映射日志已保存: {file_path}")
        except Exception as e:
            logger.error(f"[DEBUG] 保存映射日志失败: {e}")
    
    def log_serialization(
        self,
        operation: str,
        data_before: Optional[Dict],
        data_after: Optional[Dict],
        errors: List[Dict]
    ):
        """
        记录序列化/反序列化信息
        
        Args:
            operation: 操作名称
            data_before: 操作前数据
            data_after: 操作后数据
            errors: 错误列表
        """
        if not self.is_enabled(DebugCategory.SERIALIZATION):
            return
        
        debug_data = {
            "timestamp": datetime.now().isoformat(),
            "operation": operation,
            "data_before": data_before,
            "data_after": data_after,
            "errors": errors
        }
        
        file_path = self._get_debug_file_path(f"serial_{operation}")
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(debug_data, f, indent=2, ensure_ascii=False, default=str)
            logger.info(f"[DEBUG] 序列化日志已保存: {file_path}")
        except Exception as e:
            logger.error(f"[DEBUG] 保存序列化日志失败: {e}")


# 便捷函数
def log_pack_operation(**kwargs):
    """便捷函数：记录打包操作"""
    from core.debug import get_debug_manager
    get_debug_manager().log_pack_operation(**kwargs)


def log_node_mapping(**kwargs):
    """便捷函数：记录节点映射"""
    from core.debug import get_debug_manager
    get_debug_manager().log_node_mapping(**kwargs)


def log_serialization(**kwargs):
    """便捷函数：记录序列化操作"""
    from core.debug import get_debug_manager
    get_debug_manager().log_serialization(**kwargs)
