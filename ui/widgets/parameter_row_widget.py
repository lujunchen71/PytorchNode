"""
参数行控件 - name左value右的单行布局

设计：
- 水平布局，name和value左对齐
- name最小宽度80px，value最小宽度100px
- 支持伸展因子（默认1:1，可通过父级文件夹统一调整）
- 减小上下间距（3px）
- Phase 4: 可拖动分隔条调整name/value比例
"""

from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QSizePolicy
from PyQt6.QtCore import Qt, pyqtSignal as Signal
from PyQt6.QtGui import QMouseEvent, QPainter, QPen, QColor

from .folder_style import SIZES, SPACING, get_parameter_row_style

import logging


logger = logging.getLogger(__name__)


class RatioSplitter(QWidget):
    """可拖动的比例分隔条"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(5)
        self.setCursor(Qt.CursorShape.SizeHorCursor)
        self.dragging = False
        self.drag_start_pos = None
        self.drag_start_ratio = 0.5
        
        # 设置样式
        self.setStyleSheet("background: transparent;")
    
    def paintEvent(self, event):
        """绘制分隔条"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        pen = QPen(QColor("#888888"), 1)
        painter.setPen(pen)
        # 绘制一条垂直线
        center_x = self.width() // 2
        painter.drawLine(center_x, 2, center_x, self.height() - 2)
    
    def mousePressEvent(self, event: QMouseEvent):
        """鼠标按下开始拖拽"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = True
            self.drag_start_pos = event.globalPosition().toPoint()
            # 获取当前比例
            parent = self.parent()
            if isinstance(parent, ParameterRowWidget):
                self.drag_start_ratio = parent.get_ratio()
            event.accept()
    
    def mouseMoveEvent(self, event: QMouseEvent):
        """鼠标移动调整比例"""
        if self.dragging:
            parent = self.parent()
            if isinstance(parent, ParameterRowWidget):
                delta = event.globalPosition().toPoint().x() - self.drag_start_pos.x()
                # 将像素delta转换为比例变化（每100像素变化0.1比例）
                ratio_delta = delta / 500.0  # 可调整灵敏度
                new_ratio = max(0.2, min(0.8, self.drag_start_ratio + ratio_delta))
                parent.set_ratio(new_ratio)
                parent.ratio_changed.emit(new_ratio)
            event.accept()
    
    def mouseReleaseEvent(self, event: QMouseEvent):
        """鼠标释放结束拖拽"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = False
            event.accept()


class ParameterRowWidget(QWidget):
    """参数行控件 - name左value右单行布局"""
    
    value_changed = Signal(str, object)  # (param_name, value)
    ratio_changed = Signal(float)  # 比例变化信号
    
    def __init__(self, param_name: str, param_value, param_info: dict, node=None, parent=None):
        """
        初始化参数行
        
        Args:
            param_name: 参数名称
            param_value: 参数值
            param_info: 参数信息字典（type, label, metadata等）
            node: 节点引用（用于表达式求值）
            parent: 父控件
        """
        super().__init__(parent)
        self.param_name = param_name
        self.param_info = param_info
        self.node = node
        self.current_ratio = 0.5  # 默认比例
        
        self._init_ui(param_value)
        self.setStyleSheet(get_parameter_row_style())
    
    def _init_ui(self, param_value):
        """初始化UI"""
        # 水平布局
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, SPACING['param_vertical'], 0, SPACING['param_vertical'])
        layout.setSpacing(5)
        
        # 参数名称标签（左对齐）
        label_text = self.param_info.get('label', self.param_name)
        self.name_label = QLabel(label_text)
        self.name_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.name_label.setMinimumWidth(SIZES['name_min_width'])
        self.name_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        
        layout.addWidget(self.name_label)
        
        # 可拖动分隔条
        self.splitter = RatioSplitter(self)
        layout.addWidget(self.splitter)
        
        # 参数值控件（左对齐）
        self.value_widget = self._create_value_widget(param_value)
        if self.value_widget:
            self.value_widget.setMinimumWidth(SIZES['value_min_width'])
            self.value_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            layout.addWidget(self.value_widget)
        
        # 设置伸展因子（默认1:1，可通过set_ratio调整）
        layout.setStretch(0, 1)  # name
        layout.setStretch(1, 0)  # splitter不拉伸
        layout.setStretch(2, 1)  # value
        
        # 设置初始比例（0.5）
        self.set_ratio(0.5)
    
    def _create_value_widget(self, param_value):
        """
        创建参数值编辑控件
        
        Args:
            param_value: 参数当前值
            
        Returns:
            参数编辑控件
        """
        from ui.widgets.parameter_widgets import create_parameter_widget
        
        try:
            widget = create_parameter_widget(self.param_name, param_value, self.node)
            
            # 连接信号
            if hasattr(widget, 'value_changed'):
                widget.value_changed.connect(
                    lambda value: self.value_changed.emit(self.param_name, value)
                )
            
            return widget
        except Exception as e:
            logger.error(f"Failed to create widget for parameter {self.param_name}: {e}")
            # 返回一个简单的标签
            fallback_label = QLabel(str(param_value))
            return fallback_label
    
    def get_value(self):
        """
        获取当前值
        
        Returns:
            参数当前值
        """
        if hasattr(self.value_widget, 'get_value'):
            return self.value_widget.get_value()
        return None
    
    def set_value(self, value):
        """
        设置值
        
        Args:
            value: 新值
        """
        if hasattr(self.value_widget, 'set_value'):
            self.value_widget.set_value(value)
    
    def get_ratio(self) -> float:
        """
        获取当前比例
        
        Returns:
            name所占比例（0.0-1.0）
        """
        return self.current_ratio
    
    def set_ratio(self, ratio: float):
        """
        设置name/value比例
        
        Args:
            ratio: name占用的比例（0.0-1.0），例如0.4表示name占40%，value占60%
        """
        ratio = max(0.2, min(0.8, ratio))  # 限制在合理范围
        self.current_ratio = ratio
        
        layout = self.layout()
        if layout:
            # 将比例转换为整数stretch因子（避免浮点精度问题）
            name_stretch = int(ratio * 100)
            value_stretch = int((1 - ratio) * 100)
            
            layout.setStretch(0, name_stretch)
            layout.setStretch(2, value_stretch)
            
            logger.debug(f"Set ratio for {self.param_name}: {ratio} (stretch {name_stretch}:{value_stretch})")
