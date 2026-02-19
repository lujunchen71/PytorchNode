"""
MenuMixin - 菜单栏构建混入类

职责:
- 创建菜单栏
- 添加菜单项
- 连接菜单信号
"""

from PyQt6.QtWidgets import QMenuBar, QMenu
from PyQt6.QtGui import QAction, QKeySequence
from PyQt6.QtCore import pyqtSlot as Slot

import logging

logger = logging.getLogger(__name__)


class MenuMixin:
    """菜单栏构建混入类"""

    def _create_menus(self: 'MainWindow'):
        """创建菜单栏"""
        menubar = self.menuBar()

        # 文件菜单
        self._create_file_menu(menubar)

        # 编辑菜单
        self._create_edit_menu(menubar)

        # 视图菜单
        self._create_view_menu(menubar)

        # 调试菜单
        self._create_debug_menu(menubar)

        # 帮助菜单
        self._create_help_menu(menubar)

    def _create_file_menu(self: 'MainWindow', menubar: QMenuBar):
        """创建文件菜单"""
        file_menu = menubar.addMenu("文件(&F)")

        # 新建项目
        new_action = QAction("新建项目(&N)", self)
        new_action.setShortcut(QKeySequence.StandardKey.New)
        new_action.triggered.connect(self._on_new_project)
        file_menu.addAction(new_action)

        # 打开项目
        open_action = QAction("打开项目(&O)", self)
        open_action.setShortcut(QKeySequence.StandardKey.Open)
        open_action.triggered.connect(self._on_open_project)
        file_menu.addAction(open_action)

        file_menu.addSeparator()

        # 保存项目
        save_action = QAction("保存(&S)", self)
        save_action.setShortcut(QKeySequence.StandardKey.Save)
        save_action.triggered.connect(self._on_save_project)
        file_menu.addAction(save_action)

        # 另存为
        save_as_action = QAction("另存为(&A)...", self)
        save_as_action.setShortcut(QKeySequence.StandardKey.SaveAs)
        save_as_action.triggered.connect(self._on_save_project_as)
        file_menu.addAction(save_as_action)

        file_menu.addSeparator()

        # 退出
        exit_action = QAction("退出(&X)", self)
        exit_action.setShortcut(QKeySequence.StandardKey.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

    def _create_edit_menu(self: 'MainWindow', menubar: QMenuBar):
        """创建编辑菜单"""
        edit_menu = menubar.addMenu("编辑(&E)")

        # 撤销/重做动作连接到UndoStack
        self.undo_action = QAction("撤销(&U)", self)
        self.undo_action.setShortcut(QKeySequence.StandardKey.Undo)
        self.undo_action.setEnabled(False)
        self.undo_action.triggered.connect(self._on_undo)
        edit_menu.addAction(self.undo_action)

        self.redo_action = QAction("重做(&R)", self)
        self.redo_action.setShortcut(QKeySequence.StandardKey.Redo)
        self.redo_action.setEnabled(False)
        self.redo_action.triggered.connect(self._on_redo)
        edit_menu.addAction(self.redo_action)

        edit_menu.addSeparator()

        cut_action = QAction("剪切(&T)", self)
        cut_action.setShortcut(QKeySequence.StandardKey.Cut)
        cut_action.setEnabled(False)
        edit_menu.addAction(cut_action)

        copy_action = QAction("复制(&C)", self)
        copy_action.setShortcut(QKeySequence.StandardKey.Copy)
        copy_action.setEnabled(False)
        edit_menu.addAction(copy_action)

        paste_action = QAction("粘贴(&P)", self)
        paste_action.setShortcut(QKeySequence.StandardKey.Paste)
        paste_action.setEnabled(False)
        edit_menu.addAction(paste_action)

    def _create_view_menu(self: 'MainWindow', menubar: QMenuBar):
        """创建视图菜单"""
        view_menu = menubar.addMenu("视图(&V)")
        
        # 注意：P键切换属性面板由PropertiesPanel的全局事件过滤器处理（T146C）
        # 这里不再设置快捷键，避免冲突
        self.toggle_properties_action = QAction("切换属性面板", self)
        self.toggle_properties_action.triggered.connect(self._on_toggle_properties)
        view_menu.addAction(self.toggle_properties_action)
        
        view_menu.addSeparator()

        # 保存菜单引用（用于在 _create_dock_widgets 中添加停靠窗口的切换动作）
        self.view_menu = view_menu

    def _create_debug_menu(self: 'MainWindow', menubar: QMenuBar):
        """创建调试菜单"""
        debug_menu = menubar.addMenu("调试(&D)")
        
        debug_settings_action = QAction("调试设置(&S)...", self)
        debug_settings_action.triggered.connect(self._on_debug_settings)
        debug_menu.addAction(debug_settings_action)
        
        debug_menu.addSeparator()
        
        # 快速启用/禁用节点调试
        self.node_debug_action = QAction("节点调试", self)
        self.node_debug_action.setCheckable(True)
        self.node_debug_action.setChecked(False)
        self.node_debug_action.triggered.connect(self._on_toggle_node_debug)
        debug_menu.addAction(self.node_debug_action)
        
        # 快速启用/禁用打包调试
        self.pack_debug_action = QAction("打包调试", self)
        self.pack_debug_action.setCheckable(True)
        self.pack_debug_action.setChecked(False)
        self.pack_debug_action.triggered.connect(self._on_toggle_pack_debug)
        debug_menu.addAction(self.pack_debug_action)
        
        # 快速启用/禁用序列化调试
        self.serial_debug_action = QAction("序列化调试", self)
        self.serial_debug_action.setCheckable(True)
        self.serial_debug_action.setChecked(False)
        self.serial_debug_action.triggered.connect(self._on_toggle_serial_debug)
        debug_menu.addAction(self.serial_debug_action)

        # 保存菜单引用
        self.debug_menu = debug_menu

    def _create_help_menu(self: 'MainWindow', menubar: QMenuBar):
        """创建帮助菜单"""
        help_menu = menubar.addMenu("帮助(&H)")

        about_action = QAction("关于(&A)", self)
        about_action.triggered.connect(self._on_about)
        help_menu.addAction(about_action)
