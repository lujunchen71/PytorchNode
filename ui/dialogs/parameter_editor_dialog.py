"""
参数编辑器对话框 - Phase 3.5 参数系统

功能:
- T150A: 三栏布局框架
- T150B: 左栏 - 参数类型库（14种类型）
- T150C: 中栏 - 参数树（动态参数管理）
- T150D: 右栏 - 参数详情编辑
- T150E: 参数拖拽到中栏添加
- T150F: 参数拖入/拖出文件夹
- T150G: 参数多选删除
- T150H: 文件夹嵌套验证

设计参考: Houdini参数编辑器
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QSplitter,
    QListWidget, QTreeWidget, QTreeWidgetItem, QWidget,
    QLabel, QGroupBox, QFormLayout, QPushButton,
    QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox,
    QCheckBox, QTextEdit, QDialogButtonBox, QMessageBox,
    QListWidgetItem
)
from PyQt6.QtCore import Qt, QMimeData, pyqtSignal as Signal
from PyQt6.QtGui import QDrag, QIcon, QFont

import logging
import copy


logger = logging.getLogger(__name__)


# 参数类型定义 - 对应 core.base.parameter.ParameterType
PARAMETER_TYPES = [
    ("INT", "整数", "🔢"),
    ("FLOAT", "浮点数", "📊"),
    ("STRING", "字符串", "📝"),
    ("BOOL", "布尔值", "☑"),
    ("VECTOR2", "二维向量", "⬌"),
    ("VECTOR3", "三维向量", "⬍"),
    ("COLOR", "颜色", "🎨"),
    ("PATH", "路径", "📁"),
    ("ENUM", "枚举", "📋"),
    ("FLOAT_RAMP", "浮点曲线", "📈"),
    ("SEPARATOR", "分隔符", "━"),
    ("FOLDER_TAB", "Tab文件夹", "📂"),
    ("FOLDER_EXPAND", "展开文件夹", "📁"),
    ("LABEL", "标签", "🏷"),
]


class ParameterTypeListItem(QListWidgetItem):
    """参数类型列表项 - 支持拖拽"""
    
    def __init__(self, param_type: str, param_label: str, icon_text: str):
        super().__init__(f"{icon_text}  {param_label}")
        self.param_type = param_type
        self.param_label = param_label
        
        # 设置用户数据
        self.setData(Qt.ItemDataRole.UserRole, param_type)
        
        # 设置提示
        self.setToolTip(f"拖拽创建 {param_label} 参数")


class ParameterTypeLibrary(QListWidget):
    """左栏：参数类型库 - T150B"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # 启用拖拽
        self.setDragEnabled(True)
        self.setDragDropMode(QListWidget.DragDropMode.DragOnly)
        
        # 初始化类型列表
        self._init_types()
    
    def mimeData(self, items):
        """创建MIME数据用于拖拽"""
        mime_data = QMimeData()
        if items:
            # 传递参数类型
            param_type = items[0].param_type
            mime_data.setText(param_type)
            logger.debug(f"Drag started: {param_type}")
        return mime_data
        
        # 设置样式
        self.setStyleSheet("""
            QListWidget {
                background-color: #2b2b2b;
                color: #ddd;
                border: 1px solid #555;
                border-radius: 3px;
            }
            QListWidget::item {
                padding: 5px;
                border-radius: 2px;
            }
            QListWidget::item:hover {
                background-color: #3a3a3a;
            }
            QListWidget::item:selected {
                background-color: #0078d4;
            }
        """)
    
    def _init_types(self):
        """初始化参数类型列表"""
        for param_type, param_label, icon_text in PARAMETER_TYPES:
            item = ParameterTypeListItem(param_type, param_label, icon_text)
            self.addItem(item)


class ParameterTreeWidget(QTreeWidget):
    """中栏：参数树 - T150C"""
    
    parameter_selected = Signal(object)  # 参数被选中
    parameters_changed = Signal()  # 参数结构改变
    
    def __init__(self, node, parent=None):
        super().__init__(parent)
        
        self.node = node
        
        # 设置列
        self.setHeaderLabels(["参数名称", "类型", "默认值"])
        self.setColumnWidth(0, 150)
        self.setColumnWidth(1, 80)
        
        # 启用拖放
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDragDropMode(QTreeWidget.DragDropMode.InternalMove)
        self.setSelectionMode(QTreeWidget.SelectionMode.ExtendedSelection)  # 支持多选
        
        # 连接信号
        self.itemSelectionChanged.connect(self._on_selection_changed)
        
        # 加载节点参数
        self._load_parameters()
        
        # 设置样式
        self.setStyleSheet("""
            QTreeWidget {
                background-color: #2b2b2b;
                color: #ddd;
                border: 1px solid #555;
                border-radius: 3px;
            }
            QTreeWidget::item {
                padding: 3px;
            }
            QTreeWidget::item:hover {
                background-color: #3a3a3a;
            }
            QTreeWidget::item:selected {
                background-color: #0078d4;
            }
        """)
    
    def _load_parameters(self):
        """加载节点的动态参数（支持递归加载文件夹子参数）"""
        self.clear()
        
        # 从节点加载 instance_parameters
        instance_params = getattr(self.node, 'instance_parameters', {})
        
        logger.info(f"Loading instance_parameters: {len(instance_params)} params, keys={list(instance_params.keys())}")
        
        if not instance_params:
            # 没有动态参数，显示占位信息
            info_item = QTreeWidgetItem(["暂无动态参数", "", ""])
            info_item.setFlags(Qt.ItemFlag.ItemIsEnabled)  # 不可选择
            self.addTopLevelItem(info_item)
            return
        
        # 根据类型获取图标
        type_icons = {
            'INT': "🔢", 'FLOAT': "📊", 'STRING': "📝", 'BOOL': "☑",
            'VECTOR2': "⬌", 'VECTOR3': "⬍", 'COLOR': "🎨", 'PATH': "📁",
            'ENUM': "📋", 'FLOAT_RAMP': "📈", 'SEPARATOR': "━",
            'FOLDER_TAB': "📂", 'FOLDER_EXPAND': "📁", 'LABEL': "🏷"
        }
        
        # 递归加载参数函数
        def load_param_recursive(param_name, param_info, parent_item=None):
            """递归加载参数及其子参数"""
            param_type = param_info.get('type', 'STRING')
            default_value = param_info.get('default', '')
            icon = type_icons.get(param_type, "❓")
            
            # 深拷贝参数数据
            param_info_copy = copy.deepcopy(param_info)
            
            # 添加name到数据中
            param_info_copy['name'] = param_name
            
            # 确保metadata存在
            if 'metadata' not in param_info_copy:
                param_info_copy['metadata'] = {}
            
            # 文件夹类型不显示默认值（修复问题2）
            is_folder = param_type in ('FOLDER_TAB', 'FOLDER_EXPAND')
            display_value = '' if is_folder else str(default_value)
            
            # 创建树项
            item = QTreeWidgetItem([f"{icon} {param_name}", param_type, display_value])
            item.setData(0, Qt.ItemDataRole.UserRole, param_info_copy)
            
            # 添加到父级或顶级
            if parent_item:
                parent_item.addChild(item)
            else:
                self.addTopLevelItem(item)
            
            # 递归加载子参数（修复问题3）
            children = param_info.get('children', [])
            if children and isinstance(children, list):
                for child_param in children:
                    if isinstance(child_param, dict) and 'name' in child_param:
                        load_param_recursive(child_param['name'], child_param, item)
                # 展开文件夹
                item.setExpanded(True)
            
            return item
        
        # 加载所有顶级参数
        for param_name, param_info in instance_params.items():
            load_param_recursive(param_name, param_info)
        
        logger.info(f"Loaded {len(instance_params)} instance parameters from node (with children)")
    
    def _on_selection_changed(self):
        """选中项改变"""
        selected_items = self.selectedItems()
        if selected_items:
            self.parameter_selected.emit(selected_items[0])
        else:
            self.parameter_selected.emit(None)
    
    def dragEnterEvent(self, event):
        """拖拽进入事件 - T150E"""
        if event.mimeData().hasText():
            event.acceptProposedAction()
            logger.debug("Drag enter accepted")
        else:
            super().dragEnterEvent(event)
    
    def dragMoveEvent(self, event):
        """拖拽移动事件"""
        if event.mimeData().hasText():
            event.acceptProposedAction()
        else:
            super().dragMoveEvent(event)
    
    def dropEvent(self, event):
        """
        放置事件 - T150E + T150F + T150H
        
        - T150E: 从类型库拖拽创建参数
        - T150F: 参数拖入/拖出文件夹
        - T150H: 文件夹嵌套验证
        """
        mime_data = event.mimeData()
        
        if mime_data.hasText() and event.source() != self:
            # 从类型库拖拽创建
            param_type = mime_data.text()
            logger.info(f"Creating parameter of type: {param_type}")
            
            # T150F: 获取放置目标（可能是文件夹）
            drop_pos = event.position().toPoint()
            target_item = self.itemAt(drop_pos)
            
            if target_item:
                # T150H: 验证是否可以放置到目标
                if self._is_folder_type(target_item):
                    # 放到文件夹内
                    self._create_parameter_in_folder(param_type, target_item)
                else:
                    # 普通参数不能包含子参数，放到根级别
                    self._create_parameter(param_type)
            else:
                # 放到根级别
                self._create_parameter(param_type)
            
            event.acceptProposedAction()
            self.parameters_changed.emit()
        else:
            # T150F + T150H: 内部拖拽（排序或移入/移出文件夹）
            drop_pos = event.position().toPoint()
            target_item = self.itemAt(drop_pos)
            dragged_items = self.selectedItems()
            
            if dragged_items and target_item:
                # T150H: 验证拖拽目标
                if not self._validate_drop_target(dragged_items, target_item):
                    logger.warning("Invalid drop target - validation failed")
                    event.ignore()
                    return
            
            # 允许Qt默认的拖拽处理（排序）
            super().dropEvent(event)
            self.parameters_changed.emit()
    
    def _create_parameter(self, param_type: str):
        """创建新参数（根级别）"""
        # 生成默认参数名
        count = self.topLevelItemCount()
        param_name = f"param_{param_type.lower()}_{count + 1}"
        
        # 根据类型设置默认值和图标
        type_info = {
            'INT': (0, "🔢"),
            'FLOAT': (0.0, "📊"),
            'STRING': ('', "📝"),
            'BOOL': (False, "☑"),
            'VECTOR2': ((0.0, 0.0), "⬌"),
            'VECTOR3': ((0.0, 0.0, 0.0), "⬍"),
            'COLOR': ('#888888', "🎨"),
            'PATH': ('', "📁"),
            'ENUM': ('Option1', "📋"),
            'FLOAT_RAMP': ('', "📈"),
            'SEPARATOR': ('', "━"),
            'FOLDER_TAB': (None, "📂"),  # T150H: 文件夹无默认值
            'FOLDER_EXPAND': (None, "📁"),  # T150H: 文件夹无默认值
            'LABEL': ('Label', "🏷")
        }
        
        default_value, icon_text = type_info.get(param_type, ('', "❓"))
        
        # T150H: 文件夹类型默认值显示为空
        display_value = '' if default_value is None else str(default_value)
        
        # 创建树项，添加图标
        item = QTreeWidgetItem([f"{icon_text} {param_name}", param_type, display_value])
        item.setData(0, Qt.ItemDataRole.UserRole, {
            'name': param_name,
            'type': param_type,
            'default': default_value,
            'label': param_name.replace('_', ' ').title(),
            'metadata': {},
            'hide': '',
            'disable': ''
        })
        
        # 如果已有"暂无动态参数"的占位项，先移除
        if count == 1:
            first_item = self.topLevelItem(0)
            if first_item and first_item.text(0) == "暂无动态参数":
                self.takeTopLevelItem(0)
        
        self.addTopLevelItem(item)
        
        # T150F: 文件夹默认展开
        if param_type in ('FOLDER_TAB', 'FOLDER_EXPAND'):
            item.setExpanded(True)
        
        self.setCurrentItem(item)  # 选中新创建的参数
        logger.info(f"✅ Created parameter: {param_name} ({param_type})")
    
    def get_selected_parameters(self):
        """获取选中的参数 - T150G"""
        return self.selectedItems()
    
    def delete_selected_parameters(self):
        """删除选中的参数 - T150G"""
        selected_items = self.get_selected_parameters()
        
        if not selected_items:
            return
        
        # 确认对话框
        reply = QMessageBox.question(
            self,
            "删除参数",
            f"确定要删除 {len(selected_items)} 个参数吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            for item in selected_items:
                index = self.indexOfTopLevelItem(item)
                if index >= 0:
                    self.takeTopLevelItem(index)
            
            self.parameters_changed.emit()
            logger.info(f"Deleted {len(selected_items)} parameters")
    
    def _is_folder_type(self, item: QTreeWidgetItem) -> bool:
        """
        T150H: 判断参数项是否为文件夹类型
        
        Args:
            item: 树项
            
        Returns:
            是否为文件夹
        """
        param_data = item.data(0, Qt.ItemDataRole.UserRole)
        if not param_data or not isinstance(param_data, dict):
            return False
        
        param_type = param_data.get('type', '')
        return param_type in ('FOLDER_TAB', 'FOLDER_EXPAND')
    
    def _validate_drop_target(self, dragged_items: list, target_item: QTreeWidgetItem) -> bool:
        """
        T150H: 验证拖拽目标是否有效
        
        规则:
        1. 文件夹可以嵌套文件夹
        2. 参数可以放到文件夹内
        3. 参数不能放到参数内（普通参数不能嵌套）
        4. 不能拖拽到自己
        5. 不能形成循环嵌套
        
        Args:
            dragged_items: 被拖拽的项列表
            target_item: 目标项
            
        Returns:
            是否可以放置
        """
        # 规则 4: 不能拖拽到自己
        for dragged in dragged_items:
            if dragged == target_item:
                logger.warning("Cannot drop on self")
                return False
        
        # 获取目标类型
        is_target_folder = self._is_folder_type(target_item)
        
        # 检查每个被拖拽的项
        for dragged in dragged_items:
            is_dragged_folder = self._is_folder_type(dragged)
            
            # 规则 3: 如果目标不是文件夹，且不是排序操作（同级），则拒绝
            if not is_target_folder:
                # 检查是否是同级排序（目标的父级==拖拽项的父级）
                target_parent = target_item.parent()
                dragged_parent = dragged.parent()
                if target_parent != dragged_parent:
                    logger.warning("Cannot drop parameter into another parameter")
                    return False
            
            # 规则 5: 防止循环嵌套（如果拖拽文件夹A到文件夹B，B不能是A的子孙）
            if is_dragged_folder and is_target_folder:
                if self._is_ancestor(dragged, target_item):
                    logger.warning("Cannot create circular nesting")
                    return False
        
        # 规则 1 & 2: 文件夹可以接受任何项，参数只能排序
        return True
    
    def _is_ancestor(self, ancestor: QTreeWidgetItem, descendant: QTreeWidgetItem) -> bool:
        """
        T150H: 检查ancestor是否是descendant的祖先（防止循环嵌套）
        
        Args:
            ancestor: 可能的祖先项
            descendant: 后代项
            
        Returns:
            是否为祖先关系
        """
        current = descendant.parent()
        while current:
            if current == ancestor:
                return True
            current = current.parent()
        return False
    
    def _create_parameter_in_folder(self, param_type: str, folder_item: QTreeWidgetItem):
        """
        T150F: 在文件夹内创建参数
        
        Args:
            param_type: 参数类型
            folder_item: 文件夹项
        """
        # 生成默认参数名
        count = folder_item.childCount()
        param_name = f"param_{param_type.lower()}_{count + 1}"
        
        # 根据类型设置默认值和图标
        type_info = {
            'INT': (0, "🔢"),
            'FLOAT': (0.0, "📊"),
            'STRING': ('', "📝"),
            'BOOL': (False, "☑"),
            'VECTOR2': ((0.0, 0.0), "⬌"),
            'VECTOR3': ((0.0, 0.0, 0.0), "⬍"),
            'COLOR': ('#888888', "🎨"),
            'PATH': ('', "📁"),
            'ENUM': ('Option1', "📋"),
            'FLOAT_RAMP': ('', "📈"),
            'SEPARATOR': ('', "━"),
            'FOLDER_TAB': ('', "📂"),
            'FOLDER_EXPAND': ('', "📁"),
            'LABEL': ('Label', "🏷")
        }
        
        default_value, icon_text = type_info.get(param_type, ('', "❓"))
        
        # 创建树项，添加图标
        item = QTreeWidgetItem([f"{icon_text} {param_name}", param_type, str(default_value)])
        item.setData(0, Qt.ItemDataRole.UserRole, {
            'name': param_name,
            'type': param_type,
            'default': default_value,
            'label': param_name.replace('_', ' ').title(),
            'metadata': {},
            'hide': '',
            'disable': ''
        })
        
        # 添加到文件夹
        folder_item.addChild(item)
        
        # T150F要求: 文件夹默认展开
        folder_item.setExpanded(True)
        
        # 选中新创建的参数
        self.setCurrentItem(item)
        logger.info(f"✅ Created parameter '{param_name}' in folder: {folder_item.text(0)}")


class ParameterDetailPanel(QWidget):
    """右栏：参数详情编辑 - T150D (修复版)"""
    
    parameter_modified = Signal(object)  # 参数被修改
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.current_parameter = None
        self._updating = False  # 防止递归更新
        
        self._init_ui()
    
    def _init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # 标题
        title_label = QLabel("参数详情")
        title_font = QFont()
        title_font.setPointSize(10)
        title_font.setBold(True)
        title_label.setFont(title_font)
        layout.addWidget(title_label)
        
        # 详情表单
        detail_group = QGroupBox("基本信息")
        detail_layout = QFormLayout(detail_group)
        
        # 参数名称
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("参数名称（内部标识符）")
        self.name_edit.textChanged.connect(self._on_detail_changed)
        detail_layout.addRow("名称:", self.name_edit)
        
        # 参数标签
        self.label_edit = QLineEdit()
        self.label_edit.setPlaceholderText("参数标签（UI显示）")
        self.label_edit.textChanged.connect(self._on_detail_changed)
        detail_layout.addRow("标签:", self.label_edit)
        
        # 参数类型（只读）
        self.type_label = QLabel("-")
        detail_layout.addRow("类型:", self.type_label)
        
        # 默认值
        self.default_edit = QLineEdit()
        self.default_edit.setPlaceholderText("默认值")
        self.default_edit.textChanged.connect(self._on_detail_changed)
        detail_layout.addRow("默认值:", self.default_edit)
        
        layout.addWidget(detail_group)
        
        # 元数据组
        meta_group = QGroupBox("元数据")
        meta_layout = QFormLayout(meta_group)
        
        # 最小值
        self.min_edit = QDoubleSpinBox()
        self.min_edit.setRange(-999999, 999999)
        self.min_edit.setValue(0)
        self.min_edit.valueChanged.connect(self._on_detail_changed)
        meta_layout.addRow("最小值:", self.min_edit)
        
        # 最大值
        self.max_edit = QDoubleSpinBox()
        self.max_edit.setRange(-999999, 999999)
        self.max_edit.setValue(100)
        self.max_edit.valueChanged.connect(self._on_detail_changed)
        meta_layout.addRow("最大值:", self.max_edit)
        
        # 行数（用于多行字符串）
        self.rows_spin = QSpinBox()
        self.rows_spin.setRange(1, 20)
        self.rows_spin.setValue(1)
        self.rows_spin.valueChanged.connect(self._on_detail_changed)
        meta_layout.addRow("行数:", self.rows_spin)
        
        layout.addWidget(meta_group)
        
        # 条件表达式组 - T147
        condition_group = QGroupBox("条件控制")
        condition_layout = QFormLayout(condition_group)
        
        # 隐藏条件
        self.hide_expr_edit = QLineEdit()
        self.hide_expr_edit.setPlaceholderText("例如: ch('enable') == 0")
        self.hide_expr_edit.textChanged.connect(self._on_detail_changed)
        condition_layout.addRow("隐藏条件:", self.hide_expr_edit)
        
        # 禁用条件
        self.disable_expr_edit = QLineEdit()
        self.disable_expr_edit.setPlaceholderText("例如: ch('readonly') == 1")
        self.disable_expr_edit.textChanged.connect(self._on_detail_changed)
        condition_layout.addRow("禁用条件:", self.disable_expr_edit)
        
        layout.addWidget(condition_group)
        
        layout.addStretch()
        
        # 提示信息
        self.info_label = QLabel("← 从左侧选择参数以编辑")
        self.info_label.setStyleSheet("color: #888; font-style: italic;")
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.info_label)
        
        # 设置样式
        self.setStyleSheet("""
            QWidget {
                background-color: #2b2b2b;
            }
            QLabel {
                color: #ddd;
            }
            QGroupBox {
                color: #ddd;
                border: 1px solid #555;
                border-radius: 3px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
            QLineEdit, QSpinBox, QDoubleSpinBox {
                background-color: #3d3d3d;
                color: #ddd;
                border: 1px solid #505050;
                border-radius: 2px;
                padding: 3px;
            }
        """)
    
    def set_parameter(self, parameter_item):
        """设置要编辑的参数"""
        self.current_parameter = parameter_item
        
        if parameter_item is None:
            self._clear_form()
            self.info_label.show()
            return
        
        self.info_label.hide()
        
        # 获取参数数据
        param_data = parameter_item.data(0, Qt.ItemDataRole.UserRole)
        if not param_data:
            return
        
        # 确保metadata存在
        if 'metadata' not in param_data:
            param_data['metadata'] = {}
        
        # 日志：检查加载的数据
        logger.info(f"Loading parameter: name={param_data.get('name')}, type={param_data.get('type')}")
        
        # 阻止信号触发
        self._updating = True
        
        # 填充表单
        self.name_edit.setText(param_data.get('name', ''))
        self.label_edit.setText(param_data.get('label', param_data.get('name', '')))
        self.type_label.setText(param_data.get('type', '-'))
        
        # 检查是否为文件夹类型（修复问题2：文件夹不显示默认值）
        param_type = param_data.get('type', 'STRING')
        is_folder = param_type in ('FOLDER_TAB', 'FOLDER_EXPAND')
        
        # 文件夹类型：禁用默认值编辑
        if is_folder:
            self.default_edit.setText('')
            self.default_edit.setEnabled(False)
            self.default_edit.setPlaceholderText("文件夹无默认值")
        else:
            # 默认值转换
            default_value = param_data.get('default', '')
            if isinstance(default_value, (tuple, list)):
                default_value = str(default_value)
            self.default_edit.setText(str(default_value))
            self.default_edit.setEnabled(True)
            self.default_edit.setPlaceholderText("默认值")
        
        # 元数据
        metadata = param_data['metadata']
        self.min_edit.setValue(float(metadata.get('min', 0)))
        self.max_edit.setValue(float(metadata.get('max', 100)))
        self.rows_spin.setValue(int(metadata.get('rows', 1)))
        
        # 条件表达式
        self.hide_expr_edit.setText(param_data.get('hide', ''))
        self.disable_expr_edit.setText(param_data.get('disable', ''))
        
        # 恢复信号
        self._updating = False
        
        # 不要在这里保存，set_parameter只是加载数据
        logger.debug(f"Loaded parameter details: {param_data.get('name', 'unknown')}")
    
    def _on_detail_changed(self):
        """详情字段改变时实时保存"""
        if self._updating or not self.current_parameter:
            return
        
        param_data = self.current_parameter.data(0, Qt.ItemDataRole.UserRole)
        if not param_data or not isinstance(param_data, dict):
            logger.warning("Invalid param_data in _on_detail_changed")
            return
        
        # 日志：检查当前数据
        logger.debug(f"Before update: {param_data.keys()}")
        
        # 实时更新数据
        param_data['name'] = self.name_edit.text()
        param_data['label'] = self.label_edit.text()
        
        # 文件夹类型不保存默认值（修复问题2）
        param_type = param_data.get('type', 'STRING')
        is_folder = param_type in ('FOLDER_TAB', 'FOLDER_EXPAND')
        if is_folder:
            param_data['default'] = None
        else:
            param_data['default'] = self.default_edit.text()
        
        # 确保metadata存在
        if 'metadata' not in param_data:
            param_data['metadata'] = {}
        
        param_data['metadata']['min'] = self.min_edit.value()
        param_data['metadata']['max'] = self.max_edit.value()
        param_data['metadata']['rows'] = self.rows_spin.value()
        param_data['hide'] = self.hide_expr_edit.text()
        param_data['disable'] = self.disable_expr_edit.text()
        
        # 保存回树项
        self.current_parameter.setData(0, Qt.ItemDataRole.UserRole, param_data)
        
        # 日志：验证保存
        saved_data = self.current_parameter.data(0, Qt.ItemDataRole.UserRole)
        logger.debug(f"After save: {saved_data.keys() if saved_data else 'None'}")
        
        # 更新树项显示
        type_icons = {
            'INT': "🔢", 'FLOAT': "📊", 'STRING': "📝", 'BOOL': "☑",
            'VECTOR2': "⬌", 'VECTOR3': "⬍", 'COLOR': "🎨", 'PATH': "📁",
            'ENUM': "📋", 'FLOAT_RAMP': "📈", 'SEPARATOR': "━",
            'FOLDER_TAB': "📂", 'FOLDER_EXPAND': "📁", 'LABEL': "🏷"
        }
        icon = type_icons.get(param_type, "❓")
        self.current_parameter.setText(0, f"{icon} {param_data['name']}")
        # 文件夹类型不显示默认值
        display_value = '' if is_folder else str(param_data['default'])
        self.current_parameter.setText(2, display_value)
        
        logger.debug(f"Detail changed, updated parameter: {param_data['name']}")
    
    def _clear_form(self):
        """清空表单"""
        self._updating = True  # 防止触发更新
        
        self.name_edit.clear()
        self.label_edit.clear()
        self.type_label.setText("-")
        self.default_edit.clear()
        self.min_edit.setValue(0)
        self.max_edit.setValue(100)
        self.rows_spin.setValue(1)
        self.hide_expr_edit.clear()
        self.disable_expr_edit.clear()
        
        self._updating = False


class ParameterEditorDialog(QDialog):
    """参数编辑器对话框 - T150A"""
    
    def __init__(self, node, parent=None):
        super().__init__(parent)
        
        self.node = node
        
        self.setWindowTitle(f"参数编辑器 - {node.display_name}")
        self.resize(900, 600)
        
        self._init_ui()
        
        logger.info(f"Parameter editor opened for node: {node.name}")
    
    def _init_ui(self):
        """初始化三栏布局 - T150A"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # 标题
        title_label = QLabel(f"参数编辑器 - {self.node.display_name}")
        title_font = QFont()
        title_font.setPointSize(12)
        title_font.setBold(True)
        title_label.setFont(title_font)
        layout.addWidget(title_label)
        
        # 三栏分割器
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # 左栏：参数类型库 - T150B
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        left_title = QLabel("参数类型库")
        left_title.setStyleSheet("font-weight: bold; color: #ddd; padding: 5px;")
        left_layout.addWidget(left_title)
        
        self.type_library = ParameterTypeLibrary()
        left_layout.addWidget(self.type_library)
        
        splitter.addWidget(left_panel)
        
        # 中栏：参数树 - T150C
        middle_panel = QWidget()
        middle_layout = QVBoxLayout(middle_panel)
        middle_layout.setContentsMargins(0, 0, 0, 0)
        
        middle_title = QLabel("动态参数")
        middle_title.setStyleSheet("font-weight: bold; color: #ddd; padding: 5px;")
        middle_layout.addWidget(middle_title)
        
        self.param_tree = ParameterTreeWidget(self.node)
        self.param_tree.parameter_selected.connect(self._on_parameter_selected)
        middle_layout.addWidget(self.param_tree)
        
        # 删除按钮 - T150G
        delete_btn = QPushButton("删除选中参数 (Del)")
        delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #c42b1c;
                color: white;
                border: none;
                padding: 5px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #a52315;
            }
        """)
        delete_btn.clicked.connect(self.param_tree.delete_selected_parameters)
        middle_layout.addWidget(delete_btn)
        
        splitter.addWidget(middle_panel)
        
        # 右栏：参数详情 - T150D
        self.detail_panel = ParameterDetailPanel()
        splitter.addWidget(self.detail_panel)
        
        # 设置分割比例 (1:2:1.5)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)
        splitter.setStretchFactor(2, 1)
        
        layout.addWidget(splitter)
        
        # 按钮栏
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self._on_accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        # 设置窗口样式
        self.setStyleSheet("""
            QDialog {
                background-color: #2b2b2b;
            }
            QLabel {
                color: #ddd;
            }
            QSplitter::handle {
                background-color: #555;
            }
        """)
    
    def _on_parameter_selected(self, parameter_item):
        """参数被选中 - 更新详情面板"""
        self.detail_panel.set_parameter(parameter_item)
    
    def _collect_parameter(self, item, old_params):
        """
        递归收集参数及其子参数（修复问题1）
        
        Args:
            item: 树项
            old_params: 旧的参数数据（用于保留current_value）
            
        Returns:
            (param_name, param_def) 元组，如果无效则返回None
        """
        param_data = item.data(0, Qt.ItemDataRole.UserRole)
        
        # 跳过占位项或无效数据
        if not param_data or not isinstance(param_data, dict):
            return None
        
        # 确保必要的键存在
        if 'name' not in param_data or 'type' not in param_data:
            logger.warning(f"Skipping invalid parameter data: {param_data}")
            return None
        
        param_name = param_data['name']
        param_type = param_data['type']
        
        # 构建参数定义
        param_def = {
            'type': param_type,
            'default': param_data.get('default', ''),
            'label': param_data.get('label', param_name),
            'metadata': param_data.get('metadata', {}),
            'hide': param_data.get('hide', ''),
            'disable': param_data.get('disable', '')
        }
        
        # 保留current_value（参数编辑器只修改定义，不修改当前值）
        if param_name in old_params and 'current_value' in old_params[param_name]:
            param_def['current_value'] = old_params[param_name]['current_value']
            logger.debug(f"Preserved current_value for {param_name}: {param_def['current_value']}")
        
        # 递归收集子参数（文件夹）
        if item.childCount() > 0:
            children = []
            for i in range(item.childCount()):
                child_item = item.child(i)
                child_result = self._collect_parameter(child_item, old_params)
                if child_result:
                    # 子参数需要保留name字段（因为children是列表，不是字典）
                    child_name, child_def = child_result
                    child_def_with_name = {'name': child_name, **child_def}
                    children.append(child_def_with_name)
            
            if children:
                param_def['children'] = children
                logger.debug(f"Folder '{param_name}' has {len(children)} children")
        
        return (param_name, param_def)
    
    def _on_accept(self):
        """确定按钮 - 保存参数定义到节点实例（保留current_value，递归处理文件夹）"""
        # 获取旧的instance_parameters以保留current_value
        old_params = getattr(self.node, 'instance_parameters', {})
        
        # 收集所有顶级参数（递归处理）
        instance_params = {}
        
        for i in range(self.param_tree.topLevelItemCount()):
            item = self.param_tree.topLevelItem(i)
            result = self._collect_parameter(item, old_params)
            
            if result:
                param_name, param_def = result
                instance_params[param_name] = param_def
        
        # 保存到节点的instance_parameters
        if not hasattr(self.node, 'instance_parameters'):
            self.node.instance_parameters = {}
        
        self.node.instance_parameters = instance_params
        
        logger.info(f"Saved {len(instance_params)} instance parameter definitions to node: {self.node.name}")
        
        # 日志：输出结构
        for param_name, param_def in instance_params.items():
            child_count = len(param_def.get('children', []))
            if child_count > 0:
                logger.info(f"  - {param_name} ({param_def['type']}) with {child_count} children")
            else:
                logger.info(f"  - {param_name} ({param_def['type']})")
        
        self.accept()
    
    def keyPressEvent(self, event):
        """键盘事件 - T150G: Del键删除参数"""
        if event.key() == Qt.Key.Key_Delete:
            self.param_tree.delete_selected_parameters()
            event.accept()
        else:
            super().keyPressEvent(event)
