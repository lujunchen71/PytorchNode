"""
Tab文件夹控件 - 横向Tab切换

设计：
- 同一层级的Tab文件夹横向排列
- 选哪个显示哪个（QTabWidget）
- Tab内可嵌套Expand文件夹或普通参数
- 支持递归嵌套
Phase 3.5 修复：每个参数不应分裂为一个Tab，而应按照横向文件夹分组
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTabWidget

from .folder_style import SPACING, get_tab_widget_style

import logging


logger = logging.getLogger(__name__)


class TabFolderWidget(QWidget):
    """Tab文件夹控件 - 横向Tab切换"""
    
    def __init__(self, folder_info: dict, nesting_level: int = 0, node=None, parent=None):
        """
        初始化Tab文件夹
        
        Args:
            folder_info: 文件夹参数信息字典（包含name, label, children等）
            nesting_level: 嵌套层级
            node: 节点引用（用于表达式求值）
            parent: 父控件
        """
        super().__init__(parent)
        self.folder_info = folder_info
        self.nesting_level = nesting_level
        self.node = node
        
        # 垂直布局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, SPACING['folder_spacing'], 0, 0)
        layout.setSpacing(0)
        
        # 创建Tab控件
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet(get_tab_widget_style())
        
        # 处理children - 分为文件夹和普通参数
        children = folder_info.get('children', [])
        folder_children = []  # 类型为 FOLDER_TAB 或 FOLDER_EXPAND
        param_children = []   # 普通参数
        
        for child in children:
            if isinstance(child, dict) and 'name' in child:
                child_type = child.get('type', '')
                if child_type in ('FOLDER_TAB', 'FOLDER_EXPAND'):
                    folder_children.append(child)
                else:
                    param_children.append(child)
        
        # 如果有文件夹子项，每个文件夹作为一个Tab页
        if folder_children:
            for child in folder_children:
                child_label = child.get('label', child.get('name', 'Tab'))
                tab_content = self._create_tab_content(child, nesting_level + 1)
                self.tab_widget.addTab(tab_content, child_label)
            
            # 如果有普通参数，额外增加一个“参数”Tab页
            if param_children:
                param_tab_content = self._create_param_tab_content(param_children, nesting_level + 1)
                self.tab_widget.addTab(param_tab_content, "参数")
        else:
            # 没有文件夹子项，整个文件夹作为一个Tab页，内部包含所有参数
            folder_label = folder_info.get('label', folder_info.get('name', 'Tab'))
            tab_content = self._create_param_tab_content(param_children, nesting_level + 1)
            self.tab_widget.addTab(tab_content, folder_label)
        
        layout.addWidget(self.tab_widget)
        
        logger.debug(f"Created TabFolderWidget with {self.tab_widget.count()} tabs")
    
    def _create_tab_content(self, child: dict, nesting_level: int) -> QWidget:
        """
        创建Tab页内容（用于文件夹子项）
        
        Args:
            child: 子参数信息字典
            nesting_level: 嵌套层级
            
        Returns:
            Tab页内容widget
        """
        child_type = child.get('type', '')
        
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(SPACING['param_vertical'])
        
        if child_type == 'FOLDER_EXPAND':
            # 嵌套的Expand文件夹
            from .expand_folder_widget import ExpandFolderWidget
            folder_widget = ExpandFolderWidget(child, nesting_level, self.node)
            layout.addWidget(folder_widget)
        elif child_type == 'FOLDER_TAB':
            # 嵌套的Tab文件夹
            tab_widget = TabFolderWidget(child, nesting_level, self.node)
            layout.addWidget(tab_widget)
        else:
            # 不应出现，但作为后备
            from .parameter_row_widget import ParameterRowWidget
            param_value = child.get('current_value', child.get('default', ''))
            row = ParameterRowWidget(child['name'], param_value, child, self.node)
            layout.addWidget(row)
        
        # 如果child本身有children（例如一个文件夹作为Tab页），递归处理
        sub_children = child.get('children', [])
        if sub_children and child_type not in ('FOLDER_EXPAND', 'FOLDER_TAB'):
            for sub_child in sub_children:
                if isinstance(sub_child, dict) and 'name' in sub_child:
                    sub_widget = self._create_sub_widget(sub_child, nesting_level + 1)
                    if sub_widget:
                        layout.addWidget(sub_widget)
        
        layout.addStretch()
        return content
    
    def _create_param_tab_content(self, param_children: list, nesting_level: int) -> QWidget:
        """
        创建参数Tab页内容（用于普通参数）
        
        Args:
            param_children: 普通参数子项列表
            nesting_level: 嵌套层级
            
        Returns:
            Tab页内容widget
        """
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(SPACING['param_vertical'])
        
        for child in param_children:
            child_type = child.get('type', '')
            if child_type in ('FOLDER_TAB', 'FOLDER_EXPAND'):
                # 不应该发生，但安全处理
                from .expand_folder_widget import ExpandFolderWidget
                folder_widget = ExpandFolderWidget(child, nesting_level, self.node)
                layout.addWidget(folder_widget)
            else:
                from .parameter_row_widget import ParameterRowWidget
                param_value = child.get('current_value', child.get('default', ''))
                row = ParameterRowWidget(child['name'], param_value, child, self.node)
                layout.addWidget(row)
        
        layout.addStretch()
        return content
    
    def _create_sub_widget(self, child: dict, nesting_level: int):
        """
        创建子控件（递归）
        
        Args:
            child: 子参数信息字典
            nesting_level: 嵌套层级
            
        Returns:
            子控件widget
        """
        child_type = child.get('type', '')
        
        if child_type == 'FOLDER_TAB':
            return TabFolderWidget(child, nesting_level, self.node)
        elif child_type == 'FOLDER_EXPAND':
            from .expand_folder_widget import ExpandFolderWidget
            return ExpandFolderWidget(child, nesting_level, self.node)
        else:
            from .parameter_row_widget import ParameterRowWidget
            param_value = child.get('current_value', child.get('default', ''))
            return ParameterRowWidget(child['name'], param_value, child, self.node)
