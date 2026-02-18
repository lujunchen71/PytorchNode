"""
文件夹容器基类 - 带圆角框和标题的GroupBox

设计：
- 使用QGroupBox实现
- 圆角框（5px）+ 标题
- 根据嵌套层级自动缩进（每层15px）
- 文件夹背景色略亮于主背景
"""

from PyQt6.QtWidgets import QGroupBox

from .folder_style import get_folder_groupbox_style

import logging


logger = logging.getLogger(__name__)


class FolderGroupBox(QGroupBox):
    """文件夹参数容器基类"""
    
    def __init__(self, folder_name: str, folder_type: str, nesting_level: int = 0, parent=None):
        """
        初始化文件夹容器
        
        Args:
            folder_name: 文件夹名称（显示为标题）
            folder_type: 文件夹类型（'FOLDER_TAB' or 'FOLDER_EXPAND'）
            nesting_level: 嵌套层级（0=顶级，1=一级嵌套，用于计算缩进）
            parent: 父控件
        """
        super().__init__(folder_name, parent)
        self.folder_type = folder_type
        self.nesting_level = nesting_level
        
        # 应用样式
        self.setStyleSheet(get_folder_groupbox_style(nesting_level))
        
        logger.debug(f"Created FolderGroupBox: {folder_name} (type={folder_type}, level={nesting_level})")
