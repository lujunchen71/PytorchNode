"""
属性面板 - 显示和编辑选中节点的参数

职责:
- 显示节点参数
- 提供各种类型的编辑控件
- 实时更新节点属性
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QScrollArea, QFrame, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal as Signal
from PyQt6.QtGui import QFont, QCloseEvent

import logging


logger = logging.getLogger(__name__)


class PropertiesPanel(QWidget):
    """属性面板类 - 浮动窗口"""
    
    # 自定义信号
    parameter_changed = Signal(object, str, object)  # node, param_name, value
    
    def __init__(self, parent=None):
        """初始化属性面板"""
        super().__init__(parent, Qt.WindowType.Window)  # 设置为独立窗口
        
        # 设置窗口属性
        self.setWindowTitle("属性")
        self.setWindowFlags(
            Qt.WindowType.Window |
            Qt.WindowType.WindowStaysOnTopHint |  # 保持在最上层
            Qt.WindowType.CustomizeWindowHint |
            Qt.WindowType.WindowTitleHint |
            Qt.WindowType.WindowCloseButtonHint
        )
        
        # 设置窗口大小
        self.resize(300, 500)
        
        self.current_node = None
        self.param_widgets = {}  # {param_name: widget}
        
        self._init_ui()
        
        logger.info("Properties panel initialized (floating window)")
    
    def _init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        # 标题
        title_label = QLabel("属性")
        title_font = QFont()
        title_font.setPointSize(12)
        title_font.setBold(True)
        title_label.setFont(title_font)
        layout.addWidget(title_label)
        
        # 节点信息区域
        self.info_frame = QFrame()
        self.info_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        info_layout = QVBoxLayout(self.info_frame)
        info_layout.setContentsMargins(5, 5, 5, 5)
        
        self.node_type_label = QLabel("未选择节点")
        self.node_type_label.setStyleSheet("color: #888;")
        info_layout.addWidget(self.node_type_label)
        
        self.node_name_label = QLabel("")
        node_name_font = QFont()
        node_name_font.setPointSize(9)
        self.node_name_label.setFont(node_name_font)
        info_layout.addWidget(self.node_name_label)
        
        layout.addWidget(self.info_frame)
        
        # 分隔线
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(separator)
        
        # 滚动区域 - 用于显示参数
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        
        # 参数容器
        self.params_container = QWidget()
        self.params_layout = QVBoxLayout(self.params_container)
        self.params_layout.setContentsMargins(0, 0, 0, 0)
        self.params_layout.setSpacing(5)
        self.params_layout.addStretch()
        
        scroll_area.setWidget(self.params_container)
        layout.addWidget(scroll_area)
        
        # 设置样式
        self.setStyleSheet("""
            QWidget {
                background-color: #2b2b2b;
            }
            QLabel {
                color: #ddd;
            }
            QFrame {
                background-color: #3a3a3a;
                border-radius: 3px;
            }
        """)
    
    def closeEvent(self, event: QCloseEvent):
        """关闭事件 - 隐藏而不是关闭"""
        event.ignore()
        self.hide()
    
    def set_node(self, node):
        """
        设置要显示属性的节点
        
        Args:
            node: 节点对象
        """
        self.current_node = node
        self._clear_params()
        
        if node is None:
            self.node_type_label.setText("未选择节点")
            self.node_name_label.setText("")
            return
        
        # 更新节点信息
        self.node_type_label.setText(node.display_name)
        self.node_name_label.setText(f"名称: {node.name}")
        
        # 显示参数
        self._load_parameters()
        
        logger.info(f"Displaying properties for node: {node.name}")
    
    def _clear_params(self):
        """清空参数显示"""
        # 移除所有参数控件
        for widget in self.param_widgets.values():
            widget.setParent(None)
            widget.deleteLater()
        
        self.param_widgets.clear()
    
    def _load_parameters(self):
        """加载并显示节点参数"""
        if not self.current_node:
            return
        
        # 获取节点参数（兼容properties和parameters属性）
        parameters = getattr(self.current_node, 'parameters', None)
        if parameters is None:
            parameters = getattr(self.current_node, 'properties', {})
        
        if not parameters:
            # 没有参数，显示提示
            no_params_label = QLabel("此节点没有可编辑的参数")
            no_params_label.setStyleSheet("color: #888; font-style: italic;")
            no_params_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            # 插入到stretch之前
            self.params_layout.insertWidget(0, no_params_label)
            self.param_widgets['_no_params'] = no_params_label
            return
        
        # 为每个参数创建编辑控件
        for param_name, param_value in parameters.items():
            widget = self._create_param_widget(param_name, param_value)
            if widget:
                # 插入到stretch之前
                insert_index = self.params_layout.count() - 1
                self.params_layout.insertWidget(insert_index, widget)
                self.param_widgets[param_name] = widget
    
    def _create_param_widget(self, param_name: str, param_value):
        """
        创建参数编辑控件
        
        Args:
            param_name: 参数名称
            param_value: 参数值
            
        Returns:
            参数控件widget
        """
        from ui.widgets.parameter_widgets import create_parameter_widget
        
        try:
            # 创建参数控件
            widget = create_parameter_widget(param_name, param_value, self.current_node)
            
            # 连接信号
            if hasattr(widget, 'value_changed'):
                widget.value_changed.connect(
                    lambda value, name=param_name: self._on_parameter_changed(name, value)
                )
            
            return widget
            
        except Exception as e:
            logger.error(f"Failed to create widget for parameter {param_name}: {e}")
            # 返回一个简单的标签
            label = QLabel(f"{param_name}: {param_value}")
            return label
    
    def _on_parameter_changed(self, param_name: str, value):
        """
        参数值改变时的处理
        
        Args:
            param_name: 参数名称
            value: 新值
        """
        if not self.current_node:
            return
        
        logger.info(f"Parameter changed: {self.current_node.name}.{param_name} = {value}")
        
        # 更新节点参数（兼容properties和parameters）
        if hasattr(self.current_node, 'parameters'):
            self.current_node.parameters[param_name] = value
        elif hasattr(self.current_node, 'properties'):
            self.current_node.properties[param_name] = value
        
        # 触发信号
        self.parameter_changed.emit(self.current_node, param_name, value)
