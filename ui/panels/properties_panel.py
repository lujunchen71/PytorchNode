"""
属性面板 - 显示和编辑选中节点的参数

职责:
- 显示节点参数
- 提供各种类型的编辑控件
- 实时更新节点属性

Phase 3.5 重构:
- T146: 重叠式布局（右上角对齐）
- T146A: 右上角对齐算法
- T146B: 左下角可调整大小
- T146C: 全局P键事件过滤器
- T147: 参数条件显示/禁用求值
- T148: 多标签页支持
- T149: 设置齿轮按钮
- T150: 参数表达式编辑按钮
"""

from typing import Any, Dict

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QScrollArea, QFrame, QSizePolicy, QPushButton,
    QTabWidget, QToolButton
)
from PyQt6.QtCore import Qt, pyqtSignal as Signal, QPoint, QSize, QRect
from PyQt6.QtGui import QFont, QCloseEvent, QIcon, QMouseEvent, QPainter, QPen, QColor
from PyQt6.QtWidgets import QApplication

import logging


logger = logging.getLogger(__name__)


class ResizeHandle(QWidget):
    """左下角调整大小手柄 - T146B"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.setFixedSize(15, 15)
        self.parent_widget = parent
        self.dragging = False
        self.drag_start_pos = QPoint()
        self.drag_start_size = QSize()
        self.setStyleSheet("background: transparent;")
        self.setCursor(Qt.CursorShape.SizeBDiagCursor)  # 左下角调整大小光标
    
    def paintEvent(self, event):
        """绘制调整大小手柄"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        pen = QPen(QColor("#888888"), 1)
        painter.setPen(pen)
        
        # 绘制三条斜线表示可调整大小
        for i in range(3):
            offset = i * 4
            painter.drawLine(0, 15 - offset, 15 - offset, 15)
    
    def mousePressEvent(self, event: QMouseEvent):
        """鼠标按下开始拖拽"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = True
            self.drag_start_pos = event.globalPosition().toPoint()
            self.drag_start_size = self.parent_widget.size()
            event.accept()
    
    def mouseMoveEvent(self, event: QMouseEvent):
        """鼠标移动调整大小"""
        if self.dragging:
            delta = event.globalPosition().toPoint() - self.drag_start_pos
            
            # 左下角调整：宽度反向增加，高度正向增加
            new_width = max(250, self.drag_start_size.width() - delta.x())
            new_height = max(300, self.drag_start_size.height() + delta.y())
            
            # 调整窗口大小和位置
            new_x = self.parent_widget.x() + delta.x()
            self.parent_widget.setGeometry(new_x, self.parent_widget.y(), new_width, new_height)
            event.accept()
    
    def mouseReleaseEvent(self, event: QMouseEvent):
        """鼠标释放结束拖拽"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = False
            event.accept()


class PropertiesPanel(QWidget):
    """属性面板类 - 重叠式浮动窗口"""
    
    # 自定义信号
    parameter_changed = Signal(object, str, object)  # node, param_name, value
    
    def __init__(self, parent=None):
        """初始化属性面板"""
        super().__init__(parent, Qt.WindowType.Tool)  # 使用Tool窗口类型
        
        # 设置窗口属性 - T146: 重叠式布局
        self.setWindowTitle("属性")
        self.setWindowFlags(
            Qt.WindowType.Tool |  # 工具窗口
            Qt.WindowType.FramelessWindowHint |  # 无边框
            Qt.WindowType.WindowStaysOnTopHint  # 保持在最上层
        )
        
        # 设置窗口大小（宽度增加1/3，高度为窗口的2/3，稍后根据实际窗口高度调整）
        self.resize(426, 600)
        
        self.current_node = None
        self.param_widgets = {}  # {param_name: widget}
        
        # 自定义标题栏拖拽
        self.dragging = False
        self.drag_start_pos = QPoint()
        
        self._init_ui()
        
        # 安装全局事件过滤器 - T146C
        self._install_global_event_filter()
        
        logger.info("Properties panel initialized (overlay floating window)")
    
    def _install_global_event_filter(self):
        """安装全局P键事件过滤器 - T146C"""
        app = QApplication.instance()
        if app:
            app.installEventFilter(self)
    
    def eventFilter(self, obj, event):
        """全局事件过滤器 - T146C: 捕获P键"""
        if event.type() == event.Type.KeyPress:
            if event.key() == Qt.Key.Key_P and not event.modifiers():
                self.toggle_visibility()
                return True
        return super().eventFilter(obj, event)
    
    def toggle_visibility(self):
        """切换显示/隐藏"""
        if self.isVisible():
            self.hide()
        else:
            self.show()
            self.position_to_node_palette()  # T146A: 右上角对齐
    
    def position_to_node_palette(self):
        """定位到节点面板停靠窗口的右上角 - T146A"""
        if not self.parent():
            return
        
        # 获取主窗口和节点面板停靠窗口
        main_window = self.parent()
        if not hasattr(main_window, 'dock_widgets') or 'node_library' not in main_window.dock_widgets:
            logger.warning("Node library dock not found, using default position")
            return
        
        # 获取节点面板的停靠窗口
        node_library_dock = main_window.dock_widgets['node_library']
        
        # 获取停靠窗口的右上角全局位置
        # 使用rect()的topRight()获取右上角的本地坐标，然后转换为全局坐标
        top_right_local = node_library_dock.rect().topRight()
        top_right_global = node_library_dock.mapToGlobal(top_right_local)
        
        # 属性面板放置在节点面板停靠窗口的右上角，稍微偏右5px
        x = top_right_global.x() + 5
        y = top_right_global.y()
        
        self.move(x, y)
        logger.info(f"Positioned properties panel at ({x}, {y}) - right-top of node palette dock")
    
    def _init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # 自定义标题栏 - T146: 无边框窗口需要自定义标题栏
        title_bar = QFrame()
        title_bar.setFixedHeight(30)
        title_bar.setStyleSheet("""
            QFrame {
                background-color: #3a3a3a;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
            }
        """)
        title_bar_layout = QHBoxLayout(title_bar)
        title_bar_layout.setContentsMargins(10, 0, 5, 0)
        
        # 标题文本
        title_label = QLabel("属性")
        title_font = QFont()
        title_font.setPointSize(10)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #ddd; background: transparent;")
        title_bar_layout.addWidget(title_label)
        
        title_bar_layout.addStretch()
        
        # 设置齿轮按钮 - T149
        settings_btn = QToolButton()
        settings_btn.setText("⚙")
        settings_btn.setToolTip("参数编辑器")
        settings_btn.setStyleSheet("""
            QToolButton {
                background: transparent;
                color: #aaa;
                border: none;
                font-size: 14px;
                padding: 2px;
            }
            QToolButton:hover {
                color: #fff;
                background-color: #4a4a4a;
                border-radius: 3px;
            }
        """)
        settings_btn.clicked.connect(self._open_parameter_editor)
        title_bar_layout.addWidget(settings_btn)
        
        # 关闭按钮
        close_btn = QToolButton()
        close_btn.setText("×")
        close_btn.setToolTip("关闭 (P)")
        close_btn.setStyleSheet("""
            QToolButton {
                background: transparent;
                color: #aaa;
                border: none;
                font-size: 18px;
                padding: 2px 5px;
            }
            QToolButton:hover {
                color: #fff;
                background-color: #e81123;
                border-radius: 3px;
            }
        """)
        close_btn.clicked.connect(self.hide)
        title_bar_layout.addWidget(close_btn)
        
        # 保存标题栏用于拖拽
        self.title_bar = title_bar
        
        layout.addWidget(title_bar)
        
        # 内容区域（带边框和圆角）
        content_widget = QFrame()
        content_widget.setStyleSheet("""
            QFrame {
                background-color: #2b2b2b;
                border: 1px solid #555;
                border-top: none;
                border-bottom-left-radius: 5px;
                border-bottom-right-radius: 5px;
            }
        """)
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(5, 5, 5, 5)
        content_layout.setSpacing(5)
        
        # 节点信息区域
        self.info_frame = QFrame()
        self.info_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        self.info_frame.setStyleSheet("""
            QFrame {
                background-color: #3a3a3a;
                border-radius: 3px;
                border: none;
            }
        """)
        info_layout = QVBoxLayout(self.info_frame)
        info_layout.setContentsMargins(5, 5, 5, 5)
        
        self.node_type_label = QLabel("未选择节点")
        self.node_type_label.setStyleSheet("color: #888; background: transparent;")
        info_layout.addWidget(self.node_type_label)
        
        self.node_name_label = QLabel("")
        node_name_font = QFont()
        node_name_font.setPointSize(9)
        self.node_name_label.setFont(node_name_font)
        self.node_name_label.setStyleSheet("color: #ddd; background: transparent;")
        info_layout.addWidget(self.node_name_label)
        
        content_layout.addWidget(self.info_frame)
        
        # 分隔线
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        separator.setStyleSheet("background-color: #555;")
        content_layout.addWidget(separator)
        
        # Tab控件 - T148: 支持多标签页
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: none;
                background-color: transparent;
            }
            QTabBar::tab {
                background-color: #3a3a3a;
                color: #aaa;
                padding: 5px 10px;
                border-top-left-radius: 3px;
                border-top-right-radius: 3px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: #2b2b2b;
                color: #fff;
            }
            QTabBar::tab:hover {
                background-color: #4a4a4a;
            }
        """)
        
        # 参数标签页
        params_tab = QWidget()
        params_tab_layout = QVBoxLayout(params_tab)
        params_tab_layout.setContentsMargins(0, 5, 0, 0)
        
        # 滚动区域 - 用于显示参数
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        scroll_area.setStyleSheet("""
            QScrollArea {
                background-color: transparent;
                border: none;
            }
        """)
        
        # 参数容器
        self.params_container = QWidget()
        self.params_layout = QVBoxLayout(self.params_container)
        self.params_layout.setContentsMargins(0, 0, 0, 0)
        self.params_layout.setSpacing(5)
        self.params_layout.addStretch()
        
        scroll_area.setWidget(self.params_container)
        params_tab_layout.addWidget(scroll_area)
        
        self.tab_widget.addTab(params_tab, "参数")
        
        # 可以添加其他标签页（例如：输入输出、统计等）
        # info_tab = QWidget()
        # self.tab_widget.addTab(info_tab, "信息")
        
        content_layout.addWidget(self.tab_widget)
        
        layout.addWidget(content_widget)
        
        # 添加左下角调整大小手柄 - T146B
        self.resize_handle = ResizeHandle(self)
        self.resize_handle.move(0, self.height() - 15)
        
        # 设置窗口阴影效果
        self.setStyleSheet("""
            PropertiesPanel {
                background-color: transparent;
            }
            QLabel {
                color: #ddd;
            }
        """)
    
    def resizeEvent(self, event):
        """窗口调整大小时更新手柄位置"""
        super().resizeEvent(event)
        if hasattr(self, 'resize_handle'):
            self.resize_handle.move(0, self.height() - 15)
    
    def mousePressEvent(self, event: QMouseEvent):
        """鼠标按下 - 用于拖拽标题栏"""
        if event.button() == Qt.MouseButton.LeftButton:
            # 检查是否点击在标题栏区域
            if hasattr(self, 'title_bar') and self.title_bar.geometry().contains(event.pos()):
                self.dragging = True
                self.drag_start_pos = event.globalPosition().toPoint() - self.pos()
                event.accept()
    
    def mouseMoveEvent(self, event: QMouseEvent):
        """鼠标移动 - 拖拽窗口"""
        if self.dragging:
            self.move(event.globalPosition().toPoint() - self.drag_start_pos)
            event.accept()
    
    def mouseReleaseEvent(self, event: QMouseEvent):
        """鼠标释放 - 停止拖拽"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = False
            event.accept()
    
    def _open_parameter_editor(self):
        """打开参数编辑器对话框 - T149"""
        if not self.current_node:
            logger.warning("No node selected, cannot open parameter editor")
            return
        
        try:
            from ui.dialogs.parameter_editor_dialog import ParameterEditorDialog
            
            dialog = ParameterEditorDialog(self.current_node, self)
            if dialog.exec():
                # 参数编辑完成后重新加载参数显示
                self._clear_params()
                self._load_parameters()
                logger.info("Parameter editor closed, parameters reloaded")
        except ImportError:
            logger.error("ParameterEditorDialog not yet implemented")
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.information(self, "提示", "参数编辑器功能即将推出")
    
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
        """加载并显示节点参数（支持文件夹层级布局）"""
        if not self.current_node:
            return
        
        # 先加载类级参数
        parameters = getattr(self.current_node, 'parameters', None)
        if parameters is None:
            parameters = getattr(self.current_node, 'properties', {})
        
        # 再加载实例参数（动态参数）
        instance_params = getattr(self.current_node, 'instance_parameters', {})
        
        has_any_params = bool(parameters) or bool(instance_params)
        
        if not has_any_params:
            # 没有参数，显示提示
            no_params_label = QLabel("此节点没有可编辑的参数\n点击齿轮⚙按钮添加动态参数")
            no_params_label.setStyleSheet("color: #888; font-style: italic;")
            no_params_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.params_layout.insertWidget(0, no_params_label)
            self.param_widgets['_no_params'] = no_params_label
            return
        
        # 添加类级参数（简单的key-value）
        if parameters:
            for param_name, param_value in parameters.items():
                widget = self._create_param_widget(param_name, param_value)
                if widget:
                    insert_index = self.params_layout.count() - 1
                    self.params_layout.insertWidget(insert_index, widget)
                    self.param_widgets[param_name] = widget
        
        # 添加实例参数（支持文件夹层级）
        if instance_params:
            for param_name, param_info in instance_params.items():
                widget = self._create_instance_param_widget(param_name, param_info, nesting_level=0)
                if widget:
                    insert_index = self.params_layout.count() - 1
                    self.params_layout.insertWidget(insert_index, widget)
                    self.param_widgets[param_name] = widget
        
        # T147: 初始求值所有参数的条件表达式
        self._evaluate_conditional_expressions()
    
    def _create_instance_param_widget(self, param_name: str, param_info: dict, nesting_level: int = 0):
        """
        创建实例参数控件（支持文件夹类型）
        
        Args:
            param_name: 参数名称
            param_info: 参数信息字典
            nesting_level: 嵌套层级
            
        Returns:
            参数控件widget
        """
        if not isinstance(param_info, dict):
            return self._create_param_widget(param_name, param_info)
        
        param_type = param_info.get('type', '')
        
        if param_type == 'FOLDER_TAB':
            # Tab文件夹
            from ui.widgets.tab_folder_widget import TabFolderWidget
            return TabFolderWidget(param_info, nesting_level, self.current_node)
        elif param_type == 'FOLDER_EXPAND':
            # 展开文件夹
            from ui.widgets.expand_folder_widget import ExpandFolderWidget
            return ExpandFolderWidget(param_info, nesting_level, self.current_node)
        else:
            # 普通参数 - 使用ParameterRowWidget
            from ui.widgets.parameter_row_widget import ParameterRowWidget
            param_value = param_info.get('current_value', param_info.get('default', ''))
            row = ParameterRowWidget(param_name, param_value, param_info, self.current_node)
            row.value_changed.connect(
                lambda name, value: self._on_parameter_changed(name, value)
            )
            return row
    
    def _create_param_widget(self, param_name: str, param_value):
        """
        创建参数编辑控件（包含表达式编辑按钮）
        
        Args:
            param_name: 参数名称
            param_value: 参数值
            
        Returns:
            参数控件widget（可能包装在容器中）
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
            
            # T150: 如果是实例参数，添加表达式编辑按钮
            if hasattr(self.current_node, 'instance_parameters') and param_name in self.current_node.instance_parameters:
                return self._wrap_widget_with_expression_button(widget, param_name)
            
            return widget
            
        except Exception as e:
            logger.error(f"Failed to create widget for parameter {param_name}: {e}")
            # 返回一个简单的标签
            label = QLabel(f"{param_name}: {param_value}")
            return label
    
    def _wrap_widget_with_expression_button(self, widget: QWidget, param_name: str) -> QWidget:
        """
        T150: 在参数控件旁边添加表达式编辑按钮
        
        Args:
            widget: 参数控件
            param_name: 参数名称
            
        Returns:
            包含控件和表达式按钮的容器
        """
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(3)
        
        # 添加参数控件
        layout.addWidget(widget)
        
        # 创建表达式按钮（fx图标）
        expr_btn = QToolButton()
        expr_btn.setText("fx")
        expr_btn.setToolTip(f"编辑 '{param_name}' 的条件表达式")
        expr_btn.setFixedSize(24, 24)
        expr_btn.setStyleSheet("""
            QToolButton {
                background: transparent;
                color: #888;
                border: 1px solid #505050;
                border-radius: 3px;
                font-size: 10px;
                font-weight: bold;
            }
            QToolButton:hover {
                color: #fff;
                background-color: #4a4a4a;
                border-color: #0078d4;
            }
            QToolButton:pressed {
                background-color: #0078d4;
            }
        """)
        expr_btn.clicked.connect(lambda: self._edit_parameter_expression(param_name))
        
        layout.addWidget(expr_btn)
        
        return container
    
    def _edit_parameter_expression(self, param_name: str):
        """
        T150: 编辑参数的条件表达式（hide/disable）
        
        Args:
            param_name: 参数名称
        """
        if not self.current_node:
            return
        
        instance_params = getattr(self.current_node, 'instance_parameters', {})
        if param_name not in instance_params:
            logger.warning(f"Parameter '{param_name}' not found in instance_parameters")
            return
        
        param_info = instance_params[param_name]
        
        # 打开表达式编辑对话框
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTextEdit
        
        dialog = QDialog(self)
        dialog.setWindowTitle(f"表达式: {param_name}")
        dialog.setMinimumWidth(400)
        dialog.setStyleSheet("""
            QDialog {
                background-color: #2b2b2b;
            }
            QLabel {
                color: #ddd;
            }
            QLineEdit, QTextEdit {
                background-color: #3d3d3d;
                color: #ddd;
                border: 1px solid #505050;
                border-radius: 2px;
                padding: 5px;
            }
            QPushButton {
                background-color: #4d4d4d;
                color: #ddd;
                border: 1px solid #505050;
                border-radius: 3px;
                padding: 5px 15px;
            }
            QPushButton:hover {
                background-color: #5d5d5d;
            }
        """)
        
        layout = QVBoxLayout(dialog)
        layout.setSpacing(10)
        
        # Hide表达式
        hide_label = QLabel("Hide Expression (隐藏条件):")
        hide_input = QLineEdit(param_info.get('hide_expression', ''))
        hide_input.setPlaceholderText("例如: mode == 'basic' (当mode为basic时隐藏此参数)")
        
        layout.addWidget(hide_label)
        layout.addWidget(hide_input)
        
        # Disable表达式
        disable_label = QLabel("Disable Expression (禁用条件):")
        disable_input = QLineEdit(param_info.get('disable_expression', ''))
        disable_input.setPlaceholderText("例如: not enable (当enable为False时禁用此参数)")
        
        layout.addWidget(disable_label)
        layout.addWidget(disable_input)
        
        # 说明文本
        help_text = QTextEdit()
        help_text.setReadOnly(True)
        help_text.setMaximumHeight(100)
        help_text.setPlainText(
            "可用的变量: 当前节点的所有参数名称\n"
            "可用的运算符: ==, !=, <, >, <=, >=, and, or, not\n"
            "示例:\n"
            "  - mode == 'advanced'  (当mode等于'advanced')\n"
            "  - value > 10 and value < 100  (当value在10到100之间)\n"
            "  - not enable  (当enable为False)"
        )
        layout.addWidget(help_text)
        
        # 按钮行
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(dialog.reject)
        btn_layout.addWidget(cancel_btn)
        
        ok_btn = QPushButton("确定")
        ok_btn.clicked.connect(dialog.accept)
        btn_layout.addWidget(ok_btn)
        
        layout.addLayout(btn_layout)
        
        # 显示对话框
        if dialog.exec():
            # 保存表达式
            param_info['hide_expression'] = hide_input.text().strip()
            param_info['disable_expression'] = disable_input.text().strip()
            
            logger.info(f"Updated expressions for '{param_name}': "
                       f"hide='{param_info['hide_expression']}', "
                       f"disable='{param_info['disable_expression']}'")
            
            # 重新求值条件表达式
            self._evaluate_conditional_expressions()
    
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
        
        # Phase 3.5: 如果是实例参数，也要更新instance_parameters中的current值
        if hasattr(self.current_node, 'instance_parameters') and param_name in self.current_node.instance_parameters:
            # 注意：这里不修改default，而是保存当前值（可以单独存储）
            # 为了简化，我们将当前值也存储在instance_parameters中
            if 'current_value' not in self.current_node.instance_parameters[param_name]:
                self.current_node.instance_parameters[param_name]['current_value'] = value
            else:
                self.current_node.instance_parameters[param_name]['current_value'] = value
            logger.debug(f"Updated instance parameter current_value: {param_name}")
        
        # 触发信号
        self.parameter_changed.emit(self.current_node, param_name, value)
    
    def _evaluate_conditional_expressions(self):
        """
        T147: 求值所有参数的条件表达式（hide/disable）
        
        根据表达式结果动态显示/隐藏和启用/禁用参数控件
        """
        if not self.current_node:
            return
        
        # 获取实例参数（包含hide/disable表达式）
        instance_params = getattr(self.current_node, 'instance_parameters', {})
        if not instance_params:
            return
        
        # 构建求值上下文（所有参数的当前值）
        context = self._build_expression_context()
        
        # 遍历所有参数，求值hide和disable表达式
        for param_name, param_info in instance_params.items():
            if param_name not in self.param_widgets:
                continue
            
            widget = self.param_widgets[param_name]
            
            # 求值hide表达式
            hide_expr = param_info.get('hide_expression', '')
            if hide_expr:
                should_hide = self._evaluate_expression(hide_expr, context)
                widget.setVisible(not should_hide)
                if should_hide:
                    logger.debug(f"Parameter '{param_name}' hidden by expression: {hide_expr}")
            else:
                # 没有hide表达式，确保可见
                widget.setVisible(True)
            
            # 求值disable表达式
            disable_expr = param_info.get('disable_expression', '')
            if disable_expr:
                should_disable = self._evaluate_expression(disable_expr, context)
                widget.setEnabled(not should_disable)
                if should_disable:
                    logger.debug(f"Parameter '{param_name}' disabled by expression: {disable_expr}")
            else:
                # 没有disable表达式，确保启用
                widget.setEnabled(True)
    
    def _build_expression_context(self) -> Dict[str, Any]:
        """
        构建表达式求值上下文
        
        Returns:
            包含所有参数名称和值的字典
        """
        context = {}
        
        if not self.current_node:
            return context
        
        # 添加类级参数
        parameters = getattr(self.current_node, 'parameters', None)
        if parameters is None:
            parameters = getattr(self.current_node, 'properties', {})
        
        if parameters:
            context.update(parameters)
        
        # 添加实例参数的当前值
        instance_params = getattr(self.current_node, 'instance_parameters', {})
        if instance_params:
            for param_name, param_info in instance_params.items():
                current_value = param_info.get('current_value', param_info.get('default', ''))
                context[param_name] = current_value
        
        return context
    
    def _evaluate_expression(self, expression: str, context: Dict[str, Any]) -> bool:
        """
        求值条件表达式
        
        Args:
            expression: 表达式字符串（例如："mode == 'advanced'" 或 "not enable"）
            context: 变量上下文（参数名称->值）
            
        Returns:
            表达式结果（布尔值），如果求值失败返回False
        """
        if not expression:
            return False
        
        try:
            # 使用安全的eval求值，只允许访问上下文变量和基本运算符
            # 限制__builtins__以防止恶意代码执行
            safe_globals = {
                "__builtins__": {
                    # 只允许基本的布尔和比较函数
                    "True": True,
                    "False": False,
                    "None": None,
                    "abs": abs,
                    "min": min,
                    "max": max,
                    "len": len,
                    "int": int,
                    "float": float,
                    "str": str,
                    "bool": bool,
                }
            }
            
            result = eval(expression, safe_globals, context)
            return bool(result)
            
        except Exception as e:
            logger.error(f"Failed to evaluate expression '{expression}': {e}")
            return False  # 求值失败时默认不隐藏/禁用
        
        # T147: 参数改变后重新求值条件表达式
        self._evaluate_conditional_expressions()
