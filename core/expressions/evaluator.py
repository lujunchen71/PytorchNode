"""
ExpressionEvaluator - 表达式求值器

支持:
- 参数引用函数(chf, chs, chi, chv等)
- Pack数据引用(pack_shape, pack_value)
- Detail数据引用(detail)
- 数学运算和条件表达式
"""

from typing import Any, Dict, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from core.base.node_graph import NodeGraph


class ExpressionError(Exception):
    """表达式求值错误"""
    pass


class ExpressionEvaluator:
    """表达式求值器"""
    
    def __init__(self, node_graph: 'NodeGraph'):
        """
        初始化求值器
        
        Args:
            node_graph: 节点图(用于路径解析和参数查找)
        """
        self.graph = node_graph
        self.context: Dict[str, Any] = {}  # 上下文变量
    
    def evaluate(self, expression: str, current_node_path: str) -> Any:
        """
        求值表达式
        
        Args:
            expression: 表达式字符串
            current_node_path: 当前节点路径(用于相对路径解析)
            
        Returns:
            求值结果
            
        Raises:
            ExpressionError: 求值失败
        """
        # 构建安全的执行上下文
        safe_context = self._build_context(current_node_path)
        
        try:
            # 使用eval求值,但限制命名空间
            result = eval(expression, {"__builtins__": {}}, safe_context)
            return result
        except Exception as e:
            raise ExpressionError(f"表达式求值失败: {expression}, 错误: {str(e)}")
    
    def _build_context(self, current_node_path: str) -> Dict[str, Any]:
        """构建求值上下文"""
        return {
            # 参数引用函数
            "chf": lambda path: self.get_float_param(path, current_node_path),
            "chs": lambda path: self.get_string_param(path, current_node_path),
            "chi": lambda path: self.get_int_param(path, current_node_path),
            "chv": lambda path: self.get_bool_param(path, current_node_path),
            "chv2": lambda path: self.get_vector2_param(path, current_node_path),
            "chi2": lambda path: self.get_int2_param(path, current_node_path),
            "chi3": lambda path: self.get_int3_param(path, current_node_path),
            
            # Pack数据引用
            "pack_shape": lambda node_path, pin: self.get_pack_shape(node_path, pin),
            "pack_value": lambda node_path, pin, idx: self.get_pack_value(node_path, pin, idx),
            
            # Detail数据引用
            "detail": lambda node_path, key: self.get_node_detail(node_path, key),
            
            # Python内置函数(受限)
            "abs": abs,
            "min": min,
            "max": max,
            "round": round,
            "len": len,
            "sum": sum,
            
            # 上下文变量
            **self.context
        }
    
    def resolve_path(self, path: str, current_path: str) -> str:
        """
        解析相对路径为绝对路径
        
        Args:
            path: 相对或绝对路径
            current_path: 当前节点路径
            
        Returns:
            绝对路径
        """
        if path.startswith("/"):
            return path  # 绝对路径
        
        # 解析相对路径
        parts = current_path.split("/")[:-1]  # 去掉当前节点名
        rel_parts = path.split("/")
        
        for part in rel_parts:
            if part == "..":
                if parts:
                    parts.pop()  # 向上一级
            elif part == ".":
                pass  # 当前级
            elif part:
                parts.append(part)
        
        return "/".join(parts) if parts else "/"
    
    def get_float_param(self, path: str, current_path: str) -> float:
        """获取浮点参数值"""
        abs_path = self.resolve_path(path, current_path)
        # TODO: 实现从graph获取节点参数
        return 0.0
    
    def get_string_param(self, path: str, current_path: str) -> str:
        """获取字符串参数值"""
        abs_path = self.resolve_path(path, current_path)
        return ""
    
    def get_int_param(self, path: str, current_path: str) -> int:
        """获取整数参数值"""
        abs_path = self.resolve_path(path, current_path)
        return 0
    
    def get_bool_param(self, path: str, current_path: str) -> bool:
        """获取布尔参数值"""
        abs_path = self.resolve_path(path, current_path)
        return False
    
    def get_vector2_param(self, path: str, current_path: str) -> tuple:
        """获取Vector2参数值"""
        abs_path = self.resolve_path(path, current_path)
        return (0.0, 0.0)
    
    def get_int2_param(self, path: str, current_path: str) -> tuple:
        """获取Int2参数值"""
        abs_path = self.resolve_path(path, current_path)
        return (0, 0)
    
    def get_int3_param(self, path: str, current_path: str) -> tuple:
        """获取Int3参数值"""
        abs_path = self.resolve_path(path, current_path)
        return (0, 0, 0)
    
    def get_pack_shape(self, node_path: str, pin_name: str) -> tuple:
        """获取Pack形状"""
        # TODO: 实现Pack形状获取
        return ()
    
    def get_pack_value(self, node_path: str, pin_name: str, index: int) -> Any:
        """获取Pack中的值"""
        # TODO: 实现Pack值获取
        return None
    
    def get_node_detail(self, node_path: str, key: str) -> Any:
        """获取节点Detail数据"""
        # TODO: 实现Detail数据获取
        return None
