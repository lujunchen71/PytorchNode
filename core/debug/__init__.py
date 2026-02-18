"""
调试系统 - 用于记录和分析节点操作

功能：
- 记录打包操作的节点关系
- 支持分类调试（节点、连接、序列化等）
- 调试文件输出到 debug_logs/ 目录
"""

from core.debug.debug_manager import DebugManager, DebugCategory

# 全局调试管理器实例
_debug_manager = None

def get_debug_manager() -> DebugManager:
    """获取全局调试管理器实例"""
    global _debug_manager
    if _debug_manager is None:
        _debug_manager = DebugManager()
    return _debug_manager
