"""
UI Mixins - UI构建混入类

包含:
- MenuMixin: 菜单栏构建
- ToolbarMixin: 工具栏构建
- DockMixin: 停靠窗口构建
- DebugMixin: 调试功能
- ProjectMixin: 项目操作
- GraphMixin: 图操作
- TrainingMixin: 训练操作
- UndoRedoMixin: 撤销/重做操作
"""

from .menu_mixin import MenuMixin
from .toolbar_mixin import ToolbarMixin
from .dock_mixin import DockMixin
from .debug_mixin import DebugMixin
from .project_mixin import ProjectMixin
from .graph_mixin import GraphMixin
from .training_mixin import TrainingMixin
from .undoredo_mixin import UndoRedoMixin

__all__ = [
    'MenuMixin', 'ToolbarMixin', 'DockMixin', 'DebugMixin',
    'ProjectMixin', 'GraphMixin', 'TrainingMixin', 'UndoRedoMixin'
]
