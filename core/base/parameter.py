"""
Parameter系统 - 节点参数管理

支持:
- 多种参数类型(float, int, string, vector等)
- 条件显示/禁用表达式
- 代码定义参数 vs 实例参数
- 参数分类(用于属性面板组织)
"""

from typing import Any, Dict, Optional
from enum import Enum


class ParameterType(Enum):
    """参数类型枚举"""
    FLOAT = "float"
    INT = "int"
    BOOL = "checkbox"
    STRING = "string"
    PATH = "path"
    FLOAT_RAMP = "float_ramp"  # 曲线/渐变
    VECTOR2 = "vector2"  # (x, y)
    VECTOR3 = "vector3"  # (x, y, z)
    INT2 = "int2"
    INT3 = "int3"
    BUTTON = "button"
    COLOR = "color"
    ENUM = "enum"  # 下拉选择
    
    # Phase 3.5: 文件夹和组织类型 (T138A)
    FOLDER_TAB = "folder_tab"  # Tab式文件夹
    FOLDER_EXPAND = "folder_expand"  # 可展开文件夹
    SEPARATOR = "separator"  # 分隔线


class Parameter:
    """参数类 - 节点的可配置属性"""
    
    def __init__(
        self,
        name: str,
        label: str,
        param_type: ParameterType,
        default_value: Any,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        初始化参数
        
        Args:
            name: 参数唯一标识(用于代码引用)
            label: 显示标签(用于UI显示)
            param_type: 参数类型
            default_value: 默认值
            metadata: 元数据(min/max/options等)
        """
        self.name = name
        self.label = label
        self.type = param_type
        self.value = default_value
        self.metadata = metadata or {}
        
        # 条件控制表达式
        self.hide_expression = ""  # 隐藏条件
        self.disable_expression = ""  # 禁用条件
        
        # 参数来源
        self.is_code_defined = True  # 代码中定义的参数(不可删除)
        self.is_instance_param = False  # 实例参数(可删除)
        
        # 分类(用于属性面板标签页)
        self.category = "基础"
    
    def set_value(self, value: Any) -> None:
        """设置参数值"""
        self.value = value
    
    def get_value(self) -> Any:
        """获取参数值"""
        return self.value
    
    def to_dict(self) -> Dict[str, Any]:
        """序列化为字典"""
        return {
            "name": self.name,
            "label": self.label,
            "type": self.type.value,
            "value": self.value,
            "metadata": self.metadata.copy(),
            "hide_expression": self.hide_expression,
            "disable_expression": self.disable_expression,
            "is_instance_param": self.is_instance_param,
            "category": self.category
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Parameter':
        """从字典反序列化"""
        param = cls(
            name=data["name"],
            label=data["label"],
            param_type=ParameterType(data["type"]),
            default_value=data["value"],
            metadata=data.get("metadata", {})
        )
        param.hide_expression = data.get("hide_expression", "")
        param.disable_expression = data.get("disable_expression", "")
        param.is_instance_param = data.get("is_instance_param", False)
        param.category = data.get("category", "基础")
        return param
    
    def __repr__(self) -> str:
        return f"Parameter('{self.name}', {self.type.value}, value={self.value})"


class FolderParameter(Parameter):
    """
    文件夹参数类 - Phase 3.5 T138B
    
    支持参数分组和嵌套：
    - children: 子参数列表（可以是Parameter或FolderParameter）
    - folder_type: 文件夹类型（TAB或EXPAND）
    - expanded: 展开状态（仅用于EXPAND类型）
    """
    
    def __init__(
        self,
        name: str,
        label: str,
        folder_type: ParameterType = ParameterType.FOLDER_EXPAND,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        初始化文件夹参数
        
        Args:
            name: 参数标识
            label: 显示标签
            folder_type: 文件夹类型（FOLDER_TAB或FOLDER_EXPAND）
            metadata: 元数据
        """
        # 文件夹参数没有值，使用None
        super().__init__(name, label, folder_type, None, metadata)
        
        # 子参数列表
        self.children: list[Parameter | FolderParameter] = []
        
        # 展开状态（仅用于EXPAND类型）
        self.expanded = metadata.get("expanded", True) if metadata else True
        
        # 默认分类
        self.category = "组织"
    
    def add_child(self, param: 'Parameter | FolderParameter') -> None:
        """
        添加子参数
        
        Args:
            param: 子参数（可以是Parameter或FolderParameter）
        """
        if param not in self.children:
            self.children.append(param)
    
    def remove_child(self, param: 'Parameter | FolderParameter') -> None:
        """
        移除子参数
        
        Args:
            param: 要移除的子参数
        """
        if param in self.children:
            self.children.remove(param)
    
    def get_child(self, name: str) -> Optional['Parameter | FolderParameter']:
        """
        根据名称获取子参数
        
        Args:
            name: 参数名称
            
        Returns:
            子参数，如果不存在返回None
        """
        for child in self.children:
            if child.name == name:
                return child
        return None
    
    def get_all_children_recursive(self) -> list['Parameter | FolderParameter']:
        """
        递归获取所有子参数（包括嵌套文件夹中的参数）
        
        Returns:
            所有子参数的扁平列表
        """
        all_children = []
        for child in self.children:
            all_children.append(child)
            if isinstance(child, FolderParameter):
                all_children.extend(child.get_all_children_recursive())
        return all_children
    
    def to_dict(self) -> Dict[str, Any]:
        """序列化为字典"""
        data = super().to_dict()
        data["children"] = [child.to_dict() for child in self.children]
        data["expanded"] = self.expanded
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FolderParameter':
        """从字典反序列化"""
        folder_type = ParameterType(data["type"])
        folder = cls(
            name=data["name"],
            label=data["label"],
            folder_type=folder_type,
            metadata=data.get("metadata", {})
        )
        folder.expanded = data.get("expanded", True)
        folder.hide_expression = data.get("hide_expression", "")
        folder.disable_expression = data.get("disable_expression", "")
        folder.is_instance_param = data.get("is_instance_param", False)
        folder.category = data.get("category", "组织")
        
        # 递归反序列化子参数
        for child_data in data.get("children", []):
            child_type = ParameterType(child_data["type"])
            if child_type in (ParameterType.FOLDER_TAB, ParameterType.FOLDER_EXPAND):
                child = FolderParameter.from_dict(child_data)
            else:
                child = Parameter.from_dict(child_data)
            folder.add_child(child)
        
        return folder
    
    def __repr__(self) -> str:
        return f"FolderParameter('{self.name}', {self.type.value}, {len(self.children)} children)"
