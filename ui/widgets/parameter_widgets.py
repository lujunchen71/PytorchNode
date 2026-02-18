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


class Vector2Widget(BaseParameterWidget):
    """二维向量编辑控件 - Phase 3.5 T140"""
    
    def __init__(self, param_name: str, initial_value: tuple = (0.0, 0.0),
                 min_val: float = -999999.0, max_val: float = 999999.0,
                 decimals: int = 4, parent=None):
        super().__init__(param_name, parent)
        
        h_layout = QHBoxLayout()
        h_layout.setSpacing(3)
        
        self.x_spinbox = QDoubleSpinBox()
        self.x_spinbox.setRange(min_val, max_val)
        self.x_spinbox.setDecimals(decimals)
        self.x_spinbox.setValue(initial_value[0])
        self.x_spinbox.setPrefix("X: ")
        self._style_spinbox(self.x_spinbox)
        
        self.y_spinbox = QDoubleSpinBox()
        self.y_spinbox.setRange(min_val, max_val)
        self.y_spinbox.setDecimals(decimals)
        self.y_spinbox.setValue(initial_value[1])
        self.y_spinbox.setPrefix("Y: ")
        self._style_spinbox(self.y_spinbox)
        
        self.x_spinbox.valueChanged.connect(self._on_value_changed)
        self.y_spinbox.valueChanged.connect(self._on_value_changed)
        
        h_layout.addWidget(self.x_spinbox)
        h_layout.addWidget(self.y_spinbox)
        self.main_layout.addLayout(h_layout)
    
    def _style_spinbox(self, spinbox):
        spinbox.setStyleSheet("""
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
    
    def _on_value_changed(self):
        self.value_changed.emit(self.get_value())
    
    def get_value(self):
        return (self.x_spinbox.value(), self.y_spinbox.value())
    
    def set_value(self, value):
        if isinstance(value, (list, tuple)) and len(value) >= 2:
            self.x_spinbox.setValue(float(value[0]))
            self.y_spinbox.setValue(float(value[1]))


class Vector3Widget(BaseParameterWidget):
    """三维向量编辑控件 - Phase 3.5 T141"""
    
    def __init__(self, param_name: str, initial_value: tuple = (0.0, 0.0, 0.0),
                 min_val: float = -999999.0, max_val: float = 999999.0,
                 decimals: int = 4, parent=None):
        super().__init__(param_name, parent)
        
        h_layout = QHBoxLayout()
        h_layout.setSpacing(3)
        
        self.x_spinbox = QDoubleSpinBox()
        self.x_spinbox.setRange(min_val, max_val)
        self.x_spinbox.setDecimals(decimals)
        self.x_spinbox.setValue(initial_value[0])
        self.x_spinbox.setPrefix("X: ")
        self._style_spinbox(self.x_spinbox)
        
        self.y_spinbox = QDoubleSpinBox()
        self.y_spinbox.setRange(min_val, max_val)
        self.y_spinbox.setDecimals(decimals)
        self.y_spinbox.setValue(initial_value[1])
        self.y_spinbox.setPrefix("Y: ")
        self._style_spinbox(self.y_spinbox)
        
        self.z_spinbox = QDoubleSpinBox()
        self.z_spinbox.setRange(min_val, max_val)
        self.z_spinbox.setDecimals(decimals)
        self.z_spinbox.setValue(initial_value[2])
        self.z_spinbox.setPrefix("Z: ")
        self._style_spinbox(self.z_spinbox)
        
        self.x_spinbox.valueChanged.connect(self._on_value_changed)
        self.y_spinbox.valueChanged.connect(self._on_value_changed)
        self.z_spinbox.valueChanged.connect(self._on_value_changed)
        
        h_layout.addWidget(self.x_spinbox)
        h_layout.addWidget(self.y_spinbox)
        h_layout.addWidget(self.z_spinbox)
        self.main_layout.addLayout(h_layout)
    
    def _style_spinbox(self, spinbox):
        spinbox.setStyleSheet("""
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
    
    def _on_value_changed(self):
        self.value_changed.emit(self.get_value())
    
    def get_value(self):
        return (self.x_spinbox.value(), self.y_spinbox.value(), self.z_spinbox.value())
    
    def set_value(self, value):
        if isinstance(value, (list, tuple)) and len(value) >= 3:
            self.x_spinbox.setValue(float(value[0]))
            self.y_spinbox.setValue(float(value[1]))
            self.z_spinbox.setValue(float(value[2]))


class ColorWidget(BaseParameterWidget):
    """颜色选择控件 - Phase 3.5 T142"""
    
    def __init__(self, param_name: str, initial_value: str = "#888888", parent=None):
        from PyQt6.QtWidgets import QPushButton
        from PyQt6.QtGui import QColor
        from PyQt6.QtWidgets import QColorDialog
        
        super().__init__(param_name, parent)
        
        self.color_button = QPushButton()
        self.color_button.setFixedHeight(30)
        self.color_button.clicked.connect(self._choose_color)
        
        self.current_color = QColor(initial_value)
        self._update_button_color()
        
        self.main_layout.addWidget(self.color_button)
    
    def _update_button_color(self):
        self.color_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.current_color.name()};
                border: 2px solid #505050;
                border-radius: 3px;
            }}
        """)
        self.color_button.setText(self.current_color.name())
    
    def _choose_color(self):
        from PyQt6.QtWidgets import QColorDialog
        
        color = QColorDialog.getColor(self.current_color, self)
        if color.isValid():
            self.current_color = color
            self._update_button_color()
            self.value_changed.emit(self.get_value())
    
    def get_value(self):
        return self.current_color.name()
    
    def set_value(self, value):
        from PyQt6.QtGui import QColor
        self.current_color = QColor(value)
        self._update_button_color()


class PathWidget(BaseParameterWidget):
    """文件路径选择控件 - Phase 3.5 T143"""
    
    def __init__(self, param_name: str, initial_value: str = "", parent=None):
        from PyQt6.QtWidgets import QPushButton
        
        super().__init__(param_name, parent)
        
        h_layout = QHBoxLayout()
        h_layout.setSpacing(3)
        
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
        self.lineedit.textChanged.connect(self._on_value_changed)
        
        self.browse_button = QPushButton("...")
        self.browse_button.setFixedWidth(30)
        self.browse_button.setStyleSheet("""
            QPushButton {
                background-color: #4d4d4d;
                color: #ddd;
                border: 1px solid #505050;
                border-radius: 2px;
            }
            QPushButton:hover {
                background-color: #5d5d5d;
            }
        """)
        self.browse_button.clicked.connect(self._browse_file)
        
        h_layout.addWidget(self.lineedit)
        h_layout.addWidget(self.browse_button)
        self.main_layout.addLayout(h_layout)
    
    def _browse_file(self):
        from PyQt6.QtWidgets import QFileDialog
        
        file_path, _ = QFileDialog.getOpenFileName(self, "选择文件", self.lineedit.text())
        if file_path:
            self.lineedit.setText(file_path)
    
    def _on_value_changed(self, value):
        self.value_changed.emit(value)
    
    def get_value(self):
        return self.lineedit.text()
    
    def set_value(self, value):
        self.lineedit.setText(str(value))


class FolderTabWidget(BaseParameterWidget):
    """Tab式文件夹控件 - Phase 3.5 T145A"""
    
    def __init__(self, param_name: str, parent=None):
        from PyQt6.QtWidgets import QTabWidget as QTab
        
        super().__init__(param_name, parent)
        
        # 创建Tab控件
        self.tab_widget = QTab()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #505050;
                border-radius: 3px;
                background-color: #2d2d2d;
            }
            QTabBar::tab {
                background-color: #3d3d3d;
                color: #aaa;
                padding: 5px 10px;
                border-top-left-radius: 3px;
                border-top-right-radius: 3px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: #2d2d2d;
                color: #fff;
            }
            QTabBar::tab:hover {
                background-color: #4d4d4d;
            }
        """)
        
        self.main_layout.addWidget(self.tab_widget)
        
        # 子参数字典 {param_name: widget}
        self.child_widgets = {}
    
    def add_child_parameter(self, param_name: str, param_widget: QWidget):
        """
        添加子参数到Tab中
        
        Args:
            param_name: 参数名称
            param_widget: 参数控件
        """
        # 创建容器
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.addWidget(param_widget)
        layout.addStretch()
        
        # 添加到Tab
        self.tab_widget.addTab(container, param_name)
        self.child_widgets[param_name] = param_widget
    
    def get_value(self):
        """文件夹没有值，返回None"""
        return None
    
    def set_value(self, value):
        """文件夹不支持set_value"""
        pass


class FolderExpandWidget(BaseParameterWidget):
    """可展开文件夹控件 - Phase 3.5 T145B"""
    
    def __init__(self, param_name: str, expanded: bool = True, parent=None):
        from PyQt6.QtWidgets import QToolButton, QVBoxLayout as QVBox
        from PyQt6.QtCore import Qt
        
        super().__init__(param_name, parent)
        
        # 设置样式
        self.setStyleSheet("""
            QFrame {
                background-color: #2d2d2d;
                border: 1px solid #505050;
                border-radius: 3px;
                padding: 3px;
            }
        """)
        
        # 顶部：标题 + 展开/折叠按钮
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        # 展开/折叠按钮
        self.toggle_btn = QToolButton()
        self.toggle_btn.setText("▼" if expanded else "▶")
        self.toggle_btn.setFixedSize(16, 16)
        self.toggle_btn.setStyleSheet("""
            QToolButton {
                background: transparent;
                color: #aaa;
                border: none;
                font-size: 10px;
            }
            QToolButton:hover {
                color: #fff;
            }
        """)
        self.toggle_btn.clicked.connect(self.toggle_expanded)
        header_layout.addWidget(self.toggle_btn)
        
        # 标题标签（替换父类的标签）
        # 移除父类添加的标签
        if self.main_layout.count() > 0:
            old_label = self.main_layout.itemAt(0).widget()
            if old_label:
                old_label.setParent(None)
        
        folder_label = QLabel(param_name)
        folder_font = QFont()
        folder_font.setPointSize(9)
        folder_font.setBold(True)
        folder_label.setFont(folder_font)
        folder_label.setStyleSheet("color: #ddd; border: none; background: transparent;")
        header_layout.addWidget(folder_label)
        header_layout.addStretch()
        
        self.main_layout.insertLayout(0, header_layout)
        
        # 子参数容器（可展开/折叠）
        self.children_container = QWidget()
        self.children_layout = QVBox(self.children_container)
        self.children_layout.setContentsMargins(15, 5, 5, 5)  # 左侧缩进
        self.children_layout.setSpacing(5)
        
        self.main_layout.addWidget(self.children_container)
        
        # 设置初始展开状态
        self.expanded = expanded
        self.children_container.setVisible(expanded)
        
        # 子参数字典
        self.child_widgets = {}
    
    def toggle_expanded(self):
        """切换展开/折叠状态"""
        self.expanded = not self.expanded
        self.children_container.setVisible(self.expanded)
        self.toggle_btn.setText("▼" if self.expanded else "▶")
    
    def add_child_parameter(self, param_name: str, param_widget: QWidget):
        """
        添加子参数到文件夹中
        
        Args:
            param_name: 参数名称
            param_widget: 参数控件
        """
        self.children_layout.addWidget(param_widget)
        self.child_widgets[param_name] = param_widget
    
    def get_value(self):
        """文件夹没有值，返回None"""
        return None
    
    def set_value(self, value):
        """文件夹不支持set_value"""
        pass


class FloatRampWidget(BaseParameterWidget):
    """浮点渐变编辑器控件 - Phase 3.5 T144"""

    def __init__(self, param_name: str, initial_value: tuple = (0.0, 1.0),
                 min_val: float = 0.0, max_val: float = 1.0,
                 decimals: int = 4, parent=None):
        super().__init__(param_name, parent)

        h_layout = QHBoxLayout()
        h_layout.setSpacing(3)

        self.start_spinbox = QDoubleSpinBox()
        self.start_spinbox.setRange(min_val, max_val)
        self.start_spinbox.setDecimals(decimals)
        self.start_spinbox.setValue(initial_value[0] if isinstance(initial_value, (list, tuple)) and len(initial_value) > 0 else 0.0)
        self.start_spinbox.setPrefix("起点: ")
        self._style_spinbox(self.start_spinbox)

        self.end_spinbox = QDoubleSpinBox()
        self.end_spinbox.setRange(min_val, max_val)
        self.end_spinbox.setDecimals(decimals)
        self.end_spinbox.setValue(initial_value[1] if isinstance(initial_value, (list, tuple)) and len(initial_value) > 1 else 1.0)
        self.end_spinbox.setPrefix("终点: ")
        self._style_spinbox(self.end_spinbox)

        self.start_spinbox.valueChanged.connect(self._on_value_changed)
        self.end_spinbox.valueChanged.connect(self._on_value_changed)

        h_layout.addWidget(self.start_spinbox)
        h_layout.addWidget(self.end_spinbox)
        self.main_layout.addLayout(h_layout)

    def _style_spinbox(self, spinbox):
        spinbox.setStyleSheet("""
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

    def _on_value_changed(self):
        self.value_changed.emit(self.get_value())

    def get_value(self):
        return (self.start_spinbox.value(), self.end_spinbox.value())

    def set_value(self, value):
        if isinstance(value, (list, tuple)) and len(value) >= 2:
            self.start_spinbox.setValue(float(value[0]))
            self.end_spinbox.setValue(float(value[1]))


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
    
    elif isinstance(param_value, (list, tuple)):
        # 向量类型
        if len(param_value) == 2:
            return Vector2Widget(param_name, param_value)
        elif len(param_value) == 3:
            return Vector3Widget(param_name, param_value)
    
    else:
        # 未知类型，返回字符串编辑器
        logger.warning(f"Unknown parameter type for {param_name}: {type(param_value)}")
        return StringWidget(param_name, str(param_value))
