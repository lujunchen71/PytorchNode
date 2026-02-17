"""
参数编辑控件 - 各种类型参数的编辑器

提供:
- IntWidget: 整数编辑
- FloatWidget: 浮点数编辑  
- StringWidget: 字符串编辑
- BoolWidget: 布尔值编辑
- EnumWidget: 枚举选择
"""

from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, 
    QSpinBox, QDoubleSpinBox, QLineEdit, QCheckBox,
    QComboBox, QSlider, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal as Signal
from PyQt6.QtGui import QFont

import logging


logger = logging.getLogger(__name__)


class BaseParameterWidget(QFrame):
    """参数控件基类"""
    
    value_changed = Signal(object)  # 值改变信号
    
    def __init__(self, param_name: str, parent=None):
        """
        初始化参数控件
        
        Args:
            param_name: 参数名称
            parent: 父控件
        """
        super().__init__(parent)
        
        self.param_name = param_name
        
        # 设置框架样式
        self.setFrameStyle(QFrame.Shape.StyledPanel)
        self.setStyleSheet("""
            QFrame {
                background-color: #2d2d2d;
                border: 1px solid #404040;
                border-radius: 3px;
                padding: 3px;
            }
        """)
        
        # 主布局
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(5, 5, 5, 5)
        self.main_layout.setSpacing(3)
        
        # 标签
        label = QLabel(param_name)
        label_font = QFont()
        label_font.setPointSize(8)
        label.setFont(label_font)
        label.setStyleSheet("color: #aaa; border: none; background: transparent;")
        self.main_layout.addWidget(label)
    
    def get_value(self):
        """获取当前值（子类实现）"""
        raise NotImplementedError
    
    def set_value(self, value):
        """设置值（子类实现）"""
        raise NotImplementedError


class IntWidget(BaseParameterWidget):
    """整数编辑控件"""
    
    def __init__(self, param_name: str, initial_value: int = 0, 
                 min_val: int = -999999, max_val: int = 999999, parent=None):
        """
        初始化整数控件
        
        Args:
            param_name: 参数名称
            initial_value: 初始值
            min_val: 最小值
            max_val: 最大值
            parent: 父控件
        """
        super().__init__(param_name, parent)
        
        # 创建SpinBox
        self.spinbox = QSpinBox()
        self.spinbox.setRange(min_val, max_val)
        self.spinbox.setValue(initial_value)
        self.spinbox.setStyleSheet("""
            QSpinBox {
                background-color: #3d3d3d;
                color: #ddd;
                border: 1px solid #505050;
                border-radius: 2px;
                padding: 2px;
            }
            QSpinBox::up-button, QSpinBox::down-button {
                background-color: #4d4d4d;
                border: none;
            }
        """)
        
        # 连接信号
        self.spinbox.valueChanged.connect(self._on_value_changed)
        
        self.main_layout.addWidget(self.spinbox)
    
    def _on_value_changed(self, value):
        """值改变时触发信号"""
        self.value_changed.emit(value)
    
    def get_value(self):
        """获取当前值"""
        return self.spinbox.value()
    
    def set_value(self, value):
        """设置值"""
        self.spinbox.setValue(int(value))


class FloatWidget(BaseParameterWidget):
    """浮点数编辑控件"""
    
    def __init__(self, param_name: str, initial_value: float = 0.0,
                 min_val: float = -999999.0, max_val: float = 999999.0,
                 decimals: int = 4, parent=None):
        """
        初始化浮点数控件
        
        Args:
            param_name: 参数名称
            initial_value: 初始值
            min_val: 最小值
            max_val: 最大值
            decimals: 小数位数
            parent: 父控件
        """
        super().__init__(param_name, parent)
        
        # 创建DoubleSpinBox
        self.spinbox = QDoubleSpinBox()
        self.spinbox.setRange(min_val, max_val)
        self.spinbox.setDecimals(decimals)
        self.spinbox.setValue(initial_value)
        self.spinbox.setStyleSheet("""
            QDoubleSpinBox {
                background-color: #3d3d3d;
                color: #ddd;
                border: 1px solid #505050;
                border-radius: 2px;
                padding: 2px;
            }
            QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {
                background-color: #4d4d4d;
                border: none;
            }
        """)
        
        # 连接信号
        self.spinbox.valueChanged.connect(self._on_value_changed)
        
        self.main_layout.addWidget(self.spinbox)
    
    def _on_value_changed(self, value):
        """值改变时触发信号"""
        self.value_changed.emit(value)
    
    def get_value(self):
        """获取当前值"""
        return self.spinbox.value()
    
    def set_value(self, value):
        """设置值"""
        self.spinbox.setValue(float(value))


class StringWidget(BaseParameterWidget):
    """字符串编辑控件"""
    
    def __init__(self, param_name: str, initial_value: str = "", parent=None):
        """
        初始化字符串控件
        
        Args:
            param_name: 参数名称
            initial_value: 初始值
            parent: 父控件
        """
        super().__init__(param_name, parent)
        
        # 创建LineEdit
        self.lineedit = QLineEdit()
        self.lineedit.setText(initial_value)
        self.lineedit.setStyleSheet("""
            QLineEdit {
                background-color: #3d3d3d;
                color: #ddd;
                border: 1px solid #505050;
                border-radius: 2px;
                padding: 3px;
            }
        """)
        
        # 连接信号
        self.lineedit.textChanged.connect(self._on_value_changed)
        
        self.main_layout.addWidget(self.lineedit)
    
    def _on_value_changed(self, value):
        """值改变时触发信号"""
        self.value_changed.emit(value)
    
    def get_value(self):
        """获取当前值"""
        return self.lineedit.text()
    
    def set_value(self, value):
        """设置值"""
        self.lineedit.setText(str(value))


class BoolWidget(BaseParameterWidget):
    """布尔值编辑控件"""
    
    def __init__(self, param_name: str, initial_value: bool = False, parent=None):
        """
        初始化布尔值控件
        
        Args:
            param_name: 参数名称
            initial_value: 初始值
            parent: 父控件
        """
        super().__init__(param_name, parent)
        
        # 创建CheckBox
        self.checkbox = QCheckBox()
        self.checkbox.setChecked(initial_value)
        self.checkbox.setStyleSheet("""
            QCheckBox {
                color: #ddd;
                background: transparent;
                border: none;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border: 1px solid #505050;
                border-radius: 3px;
                background-color: #3d3d3d;
            }
            QCheckBox::indicator:checked {
                background-color: #0078d4;
                border-color: #0078d4;
            }
        """)
        
        # 连接信号
        self.checkbox.stateChanged.connect(self._on_value_changed)
        
        self.main_layout.addWidget(self.checkbox)
    
    def _on_value_changed(self, state):
        """值改变时触发信号"""
        value = (state == Qt.CheckState.Checked.value)
        self.value_changed.emit(value)
    
    def get_value(self):
        """获取当前值"""
        return self.checkbox.isChecked()
    
    def set_value(self, value):
        """设置值"""
        self.checkbox.setChecked(bool(value))


class EnumWidget(BaseParameterWidget):
    """枚举选择控件"""
    
    def __init__(self, param_name: str, options: list, initial_value=None, parent=None):
        """
        初始化枚举控件
        
        Args:
            param_name: 参数名称
            options: 选项列表
            initial_value: 初始值
            parent: 父控件
        """
        super().__init__(param_name, parent)
        
        # 创建ComboBox
        self.combobox = QComboBox()
        
        # 添加选项
        for option in options:
            self.combobox.addItem(str(option))
        
        # 设置初始值
        if initial_value is not None:
            index = self.combobox.findText(str(initial_value))
            if index >= 0:
                self.combobox.setCurrentIndex(index)
        
        self.combobox.setStyleSheet("""
            QComboBox {
                background-color: #3d3d3d;
                color: #ddd;
                border: 1px solid #505050;
                border-radius: 2px;
                padding: 3px;
            }
            QComboBox::drop-down {
                border: none;
                background-color: #4d4d4d;
            }
            QComboBox QAbstractItemView {
                background-color: #3d3d3d;
                color: #ddd;
                selection-background-color: #0078d4;
            }
        """)
        
        # 连接信号
        self.combobox.currentTextChanged.connect(self._on_value_changed)
        
        self.main_layout.addWidget(self.combobox)
    
    def _on_value_changed(self, value):
        """值改变时触发信号"""
        self.value_changed.emit(value)
    
    def get_value(self):
        """获取当前值"""
        return self.combobox.currentText()
    
    def set_value(self, value):
        """设置值"""
        index = self.combobox.findText(str(value))
        if index >= 0:
            self.combobox.setCurrentIndex(index)


def create_parameter_widget(param_name: str, param_value, node=None):
    """
    根据参数类型创建相应的编辑控件
    
    Args:
        param_name: 参数名称
        param_value: 参数值
        node: 节点对象（可选，用于获取额外信息）
        
    Returns:
        参数控件widget
    """
    # 根据值类型判断
    if isinstance(param_value, bool):
        return BoolWidget(param_name, param_value)
    
    elif isinstance(param_value, int):
        # 尝试从节点获取范围信息
        min_val = -999999
        max_val = 999999
        if node and hasattr(node, 'get_parameter_meta'):
            meta = node.get_parameter_meta(param_name)
            if meta:
                min_val = meta.get('min', min_val)
                max_val = meta.get('max', max_val)
        
        return IntWidget(param_name, param_value, min_val, max_val)
    
    elif isinstance(param_value, float):
        # 尝试从节点获取范围信息
        min_val = -999999.0
        max_val = 999999.0
        decimals = 4
        if node and hasattr(node, 'get_parameter_meta'):
            meta = node.get_parameter_meta(param_name)
            if meta:
                min_val = meta.get('min', min_val)
                max_val = meta.get('max', max_val)
                decimals = meta.get('decimals', decimals)
        
        return FloatWidget(param_name, param_value, min_val, max_val, decimals)
    
    elif isinstance(param_value, str):
        # 检查是否是枚举类型
        if node and hasattr(node, 'get_parameter_meta'):
            meta = node.get_parameter_meta(param_name)
            if meta and 'options' in meta:
                return EnumWidget(param_name, meta['options'], param_value)
        
        return StringWidget(param_name, param_value)
    
    else:
        # 未知类型，返回字符串编辑器
        logger.warning(f"Unknown parameter type for {param_name}: {type(param_value)}")
        return StringWidget(param_name, str(param_value))
