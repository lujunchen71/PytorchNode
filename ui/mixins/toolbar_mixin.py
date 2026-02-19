"""
ToolbarMixin - 工具栏构建混入类

职责:
- 创建工具栏
- 添加工具按钮
- 连接工具栏信号
"""

from PyQt6.QtWidgets import QToolBar
from PyQt6.QtGui import QAction

import logging

logger = logging.getLogger(__name__)


class ToolbarMixin:
    """工具栏构建混入类"""

    def _create_toolbars(self: 'MainWindow'):
        """创建工具栏"""
        # 主工具栏
        main_toolbar = QToolBar("主工具栏")
        main_toolbar.setObjectName("MainToolBar")
        self.addToolBar(main_toolbar)

        # 文件操作按钮
        self._create_file_toolbar_buttons(main_toolbar)

        main_toolbar.addSeparator()

        # 运行按钮
        self._create_run_toolbar_buttons(main_toolbar)

        main_toolbar.addSeparator()

        # 训练控制按钮
        self._create_training_toolbar_buttons(main_toolbar)

        main_toolbar.addSeparator()

        # 可视化面板按钮
        self._create_visualization_toolbar_buttons(main_toolbar)

    def _create_file_toolbar_buttons(self: 'MainWindow', toolbar: QToolBar):
        """创建文件操作工具按钮"""
        new_action = QAction("新建", self)
        new_action.triggered.connect(self._on_new_project)
        toolbar.addAction(new_action)

        open_action = QAction("打开", self)
        open_action.triggered.connect(self._on_open_project)
        toolbar.addAction(open_action)

        save_action = QAction("保存", self)
        save_action.triggered.connect(self._on_save_project)
        toolbar.addAction(save_action)

    def _create_run_toolbar_buttons(self: 'MainWindow', toolbar: QToolBar):
        """创建运行工具按钮"""
        run_action = QAction("运行", self)
        run_action.triggered.connect(self._on_run_graph)
        toolbar.addAction(run_action)

    def _create_training_toolbar_buttons(self: 'MainWindow', toolbar: QToolBar):
        """创建训练控制工具按钮 (T085)"""
        self.train_start_action = QAction("开始训练", self)
        self.train_start_action.triggered.connect(self._on_train_start)
        toolbar.addAction(self.train_start_action)

        self.train_pause_action = QAction("暂停训练", self)
        self.train_pause_action.triggered.connect(self._on_train_pause)
        self.train_pause_action.setEnabled(False)
        toolbar.addAction(self.train_pause_action)

        self.train_stop_action = QAction("停止训练", self)
        self.train_stop_action.triggered.connect(self._on_train_stop)
        self.train_stop_action.setEnabled(False)
        toolbar.addAction(self.train_stop_action)

    def _create_visualization_toolbar_buttons(self: 'MainWindow', toolbar: QToolBar):
        """创建可视化工具按钮"""
        self.viz_action = QAction("可视化面板", self)
        self.viz_action.triggered.connect(self._on_show_visualization)
        toolbar.addAction(self.viz_action)
