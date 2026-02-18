"""
面包屑路径导航栏（BreadcrumbPathBar）- 显示和导航路径层次

职责:
- 显示完整路径（如 path: /obj/subnet1/node1）
- 每个路径部分可点击跳转
- 根路径支持下拉菜单切换（obj/vis/train）
"""

from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QLabel, QPushButton,
    QMenu
)
from PyQt6.QtCore import Qt, pyqtSignal as Signal, pyqtSlot as Slot
from PyQt6.QtGui import QFont, QCursor
import logging

logger = logging.getLogger(__name__)


class PathSegmentButton(QPushButton):
    """路径片段按钮 - 可点击跳转到该级路径"""
    
    def __init__(self, segment_name: str, full_path: str, is_root: bool = False, parent=None):
        """
        初始化路径片段按钮
        
        Args:
            segment_name: 片段显示名称（如 "obj", "subnet1"）
            full_path: 该片段对应的完整路径（如 "/obj", "/obj/subnet1"）
            is_root: 是否为根路径（支持下拉菜单）
            parent: 父控件
        """
        super().__init__(segment_name, parent)
        
        self.segment_name = segment_name
        self.full_path = full_path
        self.is_root = is_root
        
        # 设置样式
        self.setFlat(True)
        self.setStyleSheet("""
            PathSegmentButton {
                background-color: transparent;
                color: #aaa;
                border: none;
                padding: 3px 8px;
                font-size: 11px;
            }
            PathSegmentButton:hover {
                background-color: #3a3a3a;
                color: #fff;
                border-radius: 3px;
            }
            PathSegmentButton:pressed {
                background-color: #2a2a2a;
            }
        """)
        
        # 如果是根路径，设置粗体
        if is_root:
            font = self.font()
            font.setBold(True)
            self.setFont(font)


class BreadcrumbPathBar(QWidget):
    """面包屑路径导航栏组件"""
    
    # 信号
    path_changed = Signal(str)  # 路径切换信号，参数为新路径
    
    def __init__(self, parent=None):
        """
        初始化面包屑路径导航栏
        
        Args:
            parent: 父控件
        """
        super().__init__(parent)
        
        # 当前路径
        self.current_path = ""
        
        # 根路径选项
        self.root_options = ["obj", "vis", "train"]
        
        # 初始化UI
        self._init_ui()
        
        # 初始化路径显示 - 直接调用 _rebuild_breadcrumb 避免set_path的相等检查
        self.current_path = "/obj"
        self._rebuild_breadcrumb()
        
        logger.info(f"Breadcrumb path bar initialized with path: {self.current_path}")
    
    def _init_ui(self):
        """初始化UI"""
        # 主布局
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(10, 5, 10, 5)
        self.layout.setSpacing(0)
        
        # "Path:" 标签
        path_label = QLabel("Path:")
        path_label.setStyleSheet("""
            color: #888;
            font-size: 11px;
            padding-right: 5px;
        """)
        self.layout.addWidget(path_label)
        
        # 路径按钮容器（动态添加）
        self.path_buttons_layout = QHBoxLayout()
        self.path_buttons_layout.setSpacing(0)
        self.layout.addLayout(self.path_buttons_layout)
        
        # 弹簧（将内容推到左侧）
        self.layout.addStretch()
        
        # 整体样式
        self.setStyleSheet("""
            BreadcrumbPathBar {
                background-color: #252525;
                border-bottom: 1px solid #333;
            }
        """)
        
        self.setFixedHeight(35)
    
    def set_path(self, path: str):
        """
        设置当前路径
        
        Args:
            path: 新路径（如 "/obj/subnet1/node1"）
        """
        if path == self.current_path:
            return
        
        self.current_path = path
        self._rebuild_breadcrumb()
    
    def _rebuild_breadcrumb(self):
        """重建面包屑路径"""
        # 清空现有按钮
        while self.path_buttons_layout.count():
            item = self.path_buttons_layout.takeAt(0)
            if item and item.widget():
                item.widget().deleteLater()
        
        # 解析路径
        if not self.current_path or self.current_path == "/":
            # 空路径，显示根
            self._add_root_button("obj")
            return
        
        # 分割路径
        parts = self.current_path.strip("/").split("/")
        if not parts:
            self._add_root_button("obj")
            return
        
        # 第一部分是根路径（obj/vis/train）
        root = parts[0]
        self._add_root_button(root)
        
        # 添加后续路径部分
        current_full_path = f"/{root}"
        for i, part in enumerate(parts[1:], 1):
            # 添加分隔符
            separator = QLabel("/")
            separator.setStyleSheet("color: #555; padding: 0 2px;")
            self.path_buttons_layout.addWidget(separator)
            
            # 构建到此为止的完整路径
            current_full_path += f"/{part}"
            
            # 添加路径按钮
            btn = PathSegmentButton(part, current_full_path, is_root=False, parent=self)
            btn.clicked.connect(lambda checked, p=current_full_path: self._on_segment_clicked(p))
            
            # 如果是最后一个部分，高亮显示
            if i == len(parts) - 1:
                btn.setStyleSheet("""
                    PathSegmentButton {
                        background-color: transparent;
                        color: #fff;
                        border: none;
                        padding: 3px 8px;
                        font-size: 11px;
                        font-weight: bold;
                    }
                    PathSegmentButton:hover {
                        background-color: #3a3a3a;
                        border-radius: 3px;
                    }
                """)
            
            self.path_buttons_layout.addWidget(btn)
    
    def _add_root_button(self, root: str):
        """
        添加根路径按钮（点击跳转到根路径，右键显示下拉菜单）
        
        Args:
            root: 根路径名称（obj/vis/train）
        """
        # 添加斜杠（可点击，显示下拉菜单）
        slash = QLabel("/")
        slash.setStyleSheet("color: #666; padding: 0 2px;")
        self.path_buttons_layout.addWidget(slash)
        
        # 创建根路径按钮（点击跳转）
        root_btn = PathSegmentButton(root, f"/{root}", is_root=True, parent=self)
        
        # 左键点击：跳转到该路径
        root_btn.clicked.connect(lambda: self._on_segment_clicked(f"/{root}"))
        
        # 右键菜单：显示所有根路径选项
        def show_context_menu(pos):
            menu = QMenu(self)
            menu.setStyleSheet("""
                QMenu {
                    background-color: #2a2a2a;
                    color: #fff;
                    border: 1px solid #444;
                }
                QMenu::item {
                    padding: 5px 20px;
                }
                QMenu::item:selected {
                    background-color: #3a3a3a;
                }
            """)
            
            for option in self.root_options:
                action = menu.addAction(option)
                action.triggered.connect(lambda checked, o=option: self._on_root_changed(o))
            
            menu.exec(root_btn.mapToGlobal(pos))
        
        root_btn.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        root_btn.customContextMenuRequested.connect(show_context_menu)
        
        self.path_buttons_layout.addWidget(root_btn)
    
    @Slot(str)
    def _on_root_changed(self, new_root: str):
        """
        处理根路径切换
        
        Args:
            new_root: 新的根路径（obj/vis/train）
        """
        new_path = f"/{new_root}"
        logger.info(f"Root changed: {self.current_path} -> {new_path}")
        
        if new_path != self.current_path:
            self.current_path = new_path
            self._rebuild_breadcrumb()
            self.path_changed.emit(new_path)
    
    @Slot(str)
    def _on_segment_clicked(self, path: str):
        """
        处理路径片段点击
        
        Args:
            path: 被点击的路径
        """
        logger.info(f"Path segment clicked: {path}")
        
        if path != self.current_path:
            self.current_path = path
            self._rebuild_breadcrumb()
            self.path_changed.emit(path)
    
    def get_current_path(self) -> str:
        """
        获取当前路径
        
        Returns:
            当前路径
        """
        return self.current_path


if __name__ == "__main__":
    """测试面包屑路径导航栏"""
    import sys
    from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout
    
    app = QApplication(sys.argv)
    
    # 创建主窗口
    window = QMainWindow()
    window.setWindowTitle("面包屑路径导航栏测试")
    window.setGeometry(100, 100, 900, 600)
    
    # 设置暗色主题
    app.setStyle("Fusion")
    palette = app.palette()
    from PyQt6.QtGui import QColor
    palette.setColor(palette.ColorRole.Window, QColor(30, 30, 30))
    palette.setColor(palette.ColorRole.WindowText, Qt.GlobalColor.white)
    palette.setColor(palette.ColorRole.Base, QColor(25, 25, 25))
    palette.setColor(palette.ColorRole.AlternateBase, QColor(53, 53, 53))
    palette.setColor(palette.ColorRole.ToolTipBase, Qt.GlobalColor.white)
    palette.setColor(palette.ColorRole.ToolTipText, Qt.GlobalColor.white)
    palette.setColor(palette.ColorRole.Text, Qt.GlobalColor.white)
    palette.setColor(palette.ColorRole.Button, QColor(53, 53, 53))
    palette.setColor(palette.ColorRole.ButtonText, Qt.GlobalColor.white)
    palette.setColor(palette.ColorRole.BrightText, Qt.GlobalColor.red)
    palette.setColor(palette.ColorRole.Link, QColor(42, 130, 218))
    palette.setColor(palette.ColorRole.Highlight, QColor(42, 130, 218))
    palette.setColor(palette.ColorRole.HighlightedText, Qt.GlobalColor.black)
    app.setPalette(palette)
    
    # 创建中央控件
    central_widget = QWidget()
    layout = QVBoxLayout(central_widget)
    layout.setContentsMargins(0, 0, 0, 0)
    
    # 添加面包屑路径导航栏
    breadcrumb_bar = BreadcrumbPathBar()
    breadcrumb_bar.path_changed.connect(lambda path: print(f"Path changed to: {path}"))
    layout.addWidget(breadcrumb_bar)
    
    # 添加占位内容
    content = QLabel("内容区域\n点击路径部分跳转")
    content.setAlignment(Qt.AlignmentFlag.AlignCenter)
    content.setStyleSheet("background-color: #1a1a1a; color: #888;")
    layout.addWidget(content)
    
    window.setCentralWidget(central_widget)
    window.show()
    
    # 测试：模拟路径变化
    from PyQt6.QtCore import QTimer
    
    def test_path_1():
        print("\n=== Test 1: Switch to /obj/subnet1 ===")
        breadcrumb_bar.set_path("/obj/subnet1")
    
    def test_path_2():
        print("\n=== Test 2: Switch to /obj/subnet1/conv1 ===")
        breadcrumb_bar.set_path("/obj/subnet1/conv1")
    
    def test_path_3():
        print("\n=== Test 3: Switch to /vis ===")
        breadcrumb_bar.set_path("/vis")
    
    def test_path_4():
        print("\n=== Test 4: Switch to /train/dataset ===")
        breadcrumb_bar.set_path("/train/dataset")
    
    QTimer.singleShot(2000, test_path_1)
    QTimer.singleShot(4000, test_path_2)
    QTimer.singleShot(6000, test_path_3)
    QTimer.singleShot(8000, test_path_4)
    
    sys.exit(app.exec())
