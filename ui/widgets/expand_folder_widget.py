"""
展开文件夹控件 - 竖向展开显示所有子参数

设计：
- 继承自FolderGroupBox
- 竖向展开，全部内容可见
- 递归创建子组件（参数行、嵌套文件夹）
- 支持嵌套Tab和Expand文件夹
- Phase 4: 文件夹级别比例同步（拖动一个参数行，同步所有子参数行）
"""

from PyQt6.QtWidgets import QVBoxLayout
from PyQt6.QtCore import pyqtSignal as Signal

from .folder_group_box import FolderGroupBox
from .folder_style import SPACING

import logging


logger = logging.getLogger(__name__)


class ExpandFolderWidget(FolderGroupBox):
    """展开文件夹控件 - 竖向展开显示所有内容"""
    
    def __init__(self, folder_info: dict, nesting_level: int = 0, node=None, parent=None):
        """
        初始化展开文件夹
        
        Args:
            folder_info: 文件夹参数信息字典（包含name, label, children等）
            nesting_level: 嵌套层级
            node: 节点引用（用于表达式求值）
            parent: 父控件
        """
        folder_name = folder_info.get('label', folder_info.get('name', 'Folder'))
        super().__init__(folder_name, 'FOLDER_EXPAND', nesting_level, parent)
        
        self.folder_info = folder_info
        self.node = node
        self.param_rows = []  # 跟踪所有参数行（用于比例同步）
        # 从元数据读取比例，默认为0.5
        metadata = folder_info.get('metadata', {})
        self.folder_ratio = metadata.get('ratio', 0.5)
        
        # 内容布局
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(5, 5, 5, 5)
        content_layout.setSpacing(SPACING['param_vertical'])
        
        # 递归加载子参数
        children = folder_info.get('children', [])
        for child in children:
            if isinstance(child, dict) and 'name' in child:
                child_widget = self._create_child_widget(child, nesting_level + 1)
                if child_widget:
                    content_layout.addWidget(child_widget)
        
        content_layout.addStretch()
        self.setLayout(content_layout)
        
        logger.debug(f"Created ExpandFolderWidget: {folder_name} with {len(children)} children")
    
    def _create_child_widget(self, child: dict, nesting_level: int):
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
            # 嵌套的Tab文件夹 - 延迟导入避免循环
            from .tab_folder_widget import TabFolderWidget
            tab_widget = TabFolderWidget(child, nesting_level, self.node)
            # 为Tab文件夹也设置比例（可选）
            return tab_widget
        elif child_type == 'FOLDER_EXPAND':
            # 嵌套的Expand文件夹
            return ExpandFolderWidget(child, nesting_level, self.node)
        else:
            # 普通参数行
            from .parameter_row_widget import ParameterRowWidget
            param_value = child.get('current_value', child.get('default', ''))
            row = ParameterRowWidget(child['name'], param_value, child, self.node)
            # 连接比例变化信号
            row.ratio_changed.connect(self._on_child_ratio_changed)
            self.param_rows.append(row)
            # 设置初始比例
            row.set_ratio(self.folder_ratio)
            return row
    
    def _on_child_ratio_changed(self, ratio: float):
        """
        当子参数行比例变化时的处理
        
        Args:
            ratio: 新比例
        """
        # 更新文件夹比例
        self.folder_ratio = ratio
        # 同步到所有参数行（除了触发变化的那个）
        for row in self.param_rows:
            # 为了避免无限循环，暂时断开连接，设置后再连接？但我们使用块信号
            row.blockSignals(True)
            row.set_ratio(ratio)
            row.blockSignals(False)
        # 更新文件夹信息的元数据，以便持久化
        self._update_folder_metadata('ratio', ratio)
        logger.debug(f"Folder ratio synced to {ratio} across {len(self.param_rows)} rows")
    
    def _update_folder_metadata(self, key: str, value):
        """
        更新文件夹元数据
        
        Args:
            key: 元数据键
            value: 值
        """
        if 'metadata' not in self.folder_info:
            self.folder_info['metadata'] = {}
        self.folder_info['metadata'][key] = value
        logger.debug(f"Updated folder metadata: {key}={value}")
    
    def set_folder_ratio(self, ratio: float):
        """
        设置文件夹级别比例（手动调用）
        
        Args:
            ratio: 新比例
        """
        self.folder_ratio = ratio
        for row in self.param_rows:
            row.set_ratio(ratio)
        logger.debug(f"Folder ratio set to {ratio}")
