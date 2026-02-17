"""
测试连接拖拽和断开功能 - 带详细日志
"""

import sys
import os
import logging

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QPointF, QTimer

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def test_connection_drag():
    """测试连接拖拽功能"""
    from ui.main_window import MainWindow
    
    # 创建应用
    app = QApplication(sys.argv)
    
    # 创建主窗口
    window = MainWindow()
    window.show()
    
    logger.info("="*60)
    logger.info("连接拖拽测试 - 请按照以下步骤操作:")
    logger.info("="*60)
    logger.info("1. 右键点击画布，创建两个节点（例如：nn/Linear 和 nn/ReLU）")
    logger.info("2. 从第一个节点的输出引脚（底部）拖拽到第二个节点的输入引脚（顶部）")
    logger.info("3. 观察控制台日志，查看连接创建过程")
    logger.info("4. 再次从已连接的输入引脚拖拽并在空白处释放")
    logger.info("5. 观察是否断开连接（目前应该不会断开，这是需要修复的问题）")
    logger.info("="*60)
    logger.info("")
    
    # 定时器输出提示
    def show_reminder():
        logger.info("\n[提示] 如果拖拽连接时没有日志输出，可能是:")
        logger.info("  1. 引脚事件被父节点拦截")
        logger.info("  2. 引脚未正确设置为可接收鼠标事件")
        logger.info("  3. 引脚被其他图形项遮挡\n")
    
    timer = QTimer()
    timer.timeout.connect(show_reminder)
    timer.start(5000)  # 5秒后显示提示
    
    # 运行应用
    return app.exec()

if __name__ == '__main__':
    sys.exit(test_connection_drag())
