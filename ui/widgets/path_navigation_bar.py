"""
路径导航栏（PathNavigationBar）- 显示和切换当前路径

职责:
- 显示当前所在路径
- 提供路径切换按钮
- 显示路径面包屑
"""

from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QPushButton, QLabel,
    QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal as Signal, pyqtSlot as Slot
from PyQt6.QtGui import QFont
import logging

logger = logging.getLogger(__name__)


class PathButton(QPushButton):
    """路径按钮 - 可点击切换到对应路径"""
    
    def __init__(self, path: str, display_name: str, is_current: bool = False, parent=None):
        """
        初始化路径按钮
        
        Args:
            path: 完整路径（如 "/obj"）
            display_name: 显示名称（如 "obj"）
            is_current: 是否为当前路径
            parent: 父控件
        """
        super().__init__(display_name, parent)
        
        self.path = path
        self.is_current = is_current
        
        # 设置样式
        self.setFlat(True)
        self.setMinimumHeight(30)
        self.setFont(QFont("Segoe UI", 10, QFont.Weight.Normal if not is_current else QFont.Weight.Bold))
        self._update_style()
        
        # 鼠标悬停效果
        self.setStyleSheet(self._get_stylesheet())
    
    def _get_stylesheet(self) -> str:
        """获取样式表"""
        if self.is_current:
            return """
                PathButton {
                    background-color: #3a3a3a;
                    color: #ffffff;
                    border: none;
                    border-radius: 4px;
                    padding: 5px 15px;
                    font-weight: bold;
                }
                PathButton:hover {
                    background-color: #4a4a4a;
                }
            """
        else:
            return """
                PathButton {
                    background-color: transparent;
                    color: #aaaaaa;
                    border: none;
                    border-radius: 4px;
                    padding: 5px 15px;
                }
                PathButton:hover {
                    background-color: #2a2a2a;
                    color: #ffffff;
                }
                PathButton:pressed {
                    background-color: #1a1a1a;
                }
            """
    
    def _update_style(self):
        """更新样式"""
        self.setStyleSheet(self._get_stylesheet())
    
    def set_current(self, is_current: bool):
        """设置是否为当前路径"""
        if self.is_current != is_current:
            self.is_current = is_current
            self.setFont(QFont("Segoe UI", 10, QFont.Weight.Normal if not is_current else QFont.Weight.Bold))
            self._update_style()


class PathNavigationBar(QWidget):
    """路径导航栏组件"""
    
    # 信号
    path_changed = Signal(str)  # 路径切换信号，参数为新路径
    
    def __init__(self, parent=None):
        """
        初始化路径导航栏
        
        Args:
            parent: 父控件
        """
        super().__init__(parent)
        
        # 当前路径
        self.current_path = "/obj"
        
        # 根路径定义
        self.root_paths = {
            "/obj": {"name": "obj", "description": "模型空间"},
            "/vis": {"name": "vis", "description": "可视化空间"},
            "/train": {"name": "train", "description": "训练空间"}
        }
        
        # 路径按钮映射
        self.path_buttons = {}
        
        # 初始化UI
        self._init_ui()
        
        logger.info("Path navigation bar initialized")
    
    def _init_ui(self):
        """初始化UI"""
        # 主布局
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(5)
        
        # 左侧标签
        path_label = QLabel("路径:")
        path_label.setStyleSheet("""
            color: #888;
            font-size: 11px;
        """)
        layout.addWidget(path_label)
        
        # 根路径按钮
        for path, info in self.root_paths.items():
            is_current = (path == self.current_path)
            btn = PathButton(path, info["name"], is_current, self)
            btn.setToolTip(info["description"])
            btn.clicked.connect(lambda checked, p=path: self._on_path_clicked(p))
            
            layout.addWidget(btn)
            self.path_buttons[path] = btn
        
        # 分隔符
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.VLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        separator.setStyleSheet("QFrame { color: #444; }")
        layout.addWidget(separator)
        
        # 面包屑路径显示（当前路径下的子路径）
        self.breadcrumb_label = QLabel("")
        self.breadcrumb_label.setStyleSheet("""
            color: #aaa;
            font-size: 10px;
        """)
        layout.addWidget(self.breadcrumb_label)
        
        # 弹簧（将按钮推到左侧）
        layout.addStretch()
        
        # 整体样式
        self.setStyleSheet("""
            PathNavigationBar {
                background-color: #252525;
                border-bottom: 1px solid #333;
            }
        """)
        
        self.setFixedHeight(40)
    
    @Slot(str)
    def _on_path_clicked(self, path: str):
        """
        处理路径按钮点击
        
        Args:
            path: 被点击的路径
        """
        if path != self.current_path:
            logger.info(f"Path changed: {self.current_path} -> {path}")
            
            # 更新当前路径
            old_path = self.current_path
            self.current_path = path
            
            # 更新按钮状态
            for btn_path, btn in self.path_buttons.items():
                btn.set_current(btn_path == path)
            
            # 清空面包屑
            self.breadcrumb_label.setText("")
            
            # 发送信号
            self.path_changed.emit(path)
            
            logger.info(f"Path navigation: {old_path} -> {path}")
    
    def get_current_path(self) -> str:
        """
        获取当前路径
        
        Returns:
            当前路径
        """
        return self.current_path
    
    def set_current_path(self, path: str, update_ui: bool = True):
        """
        设置当前路径
        
        Args:
            path: 新路径
            update_ui: 是否更新UI
        """
        if path in self.root_paths:
            if update_ui:
                self._on_path_clicked(path)
            else:
                self.current_path = path
                # 仅更新按钮状态，不发送信号
                for btn_path, btn in self.path_buttons.items():
                    btn.set_current(btn_path == path)
    
    def set_breadcrumb(self, breadcrumb: str):
        """
        设置面包屑路径（子路径）
        
        Args:
            breadcrumb: 面包屑文本（如 "subnet1/conv1"）
        """
        if breadcrumb:
            self.breadcrumb_label.setText(f"/ {breadcrumb}")
        else:
            self.breadcrumb_label.setText("")


if __name__ == "__main__":
    """测试路径导航栏"""
    import sys
    from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout
    
    app = QApplication(sys.argv)
    
    # 创建主窗口
    window = QMainWindow()
    window.setWindowTitle("路径导航栏测试")
    window.setGeometry(100, 100, 800, 600)
    
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
    
    # 添加路径导航栏
    nav_bar = PathNavigationBar()
    nav_bar.path_changed.connect(lambda path: print(f"Path changed to: {path}"))
    layout.addWidget(nav_bar)
    
    # 添加占位内容
    content = QLabel("内容区域\n点击上方路径按钮切换路径")
    content.setAlignment(Qt.AlignmentFlag.AlignCenter)
    content.setStyleSheet("background-color: #1a1a1a; color: #888;")
    layout.addWidget(content)
    
    window.setCentralWidget(central_widget)
    window.show()
    
    # 测试：3秒后切换到 vis 路径
    from PyQt6.QtCore import QTimer
    def test_path_change():
        print("Auto switching to /vis")
        nav_bar.set_current_path("/vis")
        nav_bar.set_breadcrumb("monitor/loss_plot")
    
    timer = QTimer()
    timer.singleShot(3000, test_path_change)
    
    sys.exit(app.exec())
