"""
表达式上下文 (Phase 2 T031)
管理表达式求值时的变量和作用域。
TODO: 实现完整上下文管理。
"""

from typing import Any, Dict, Optional


class ExpressionContext:
    """表达式上下文，存储变量和引用"""
    
    def __init__(self):
        self.variables: Dict[str, Any] = {}
        self.references: Dict[str, Any] = {}  # 路径引用，如 chf('path')
    
    def set_variable(self, name: str, value: Any) -> None:
        """设置变量"""
        self.variables[name] = value
    
    def get_variable(self, name: str) -> Optional[Any]:
        """获取变量"""
        return self.variables.get(name)
    
    def set_reference(self, path: str, value: Any) -> None:
        """设置路径引用"""
        self.references[path] = value
    
    def get_reference(self, path: str) -> Optional[Any]:
        """获取路径引用"""
        return self.references.get(path)
    
    def clear(self) -> None:
        """清空上下文"""
        self.variables.clear()
        self.references.clear()


# 全局默认上下文
global_context = ExpressionContext()