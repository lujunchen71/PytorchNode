#!/usr/bin/env python3
"""调试启动脚本"""
import sys
import os
sys.path.insert(0, '.')

# 设置环境变量
os.environ['PYTORCH_NO_CUDA'] = '1'
os.environ['CUDA_VISIBLE_DEVICES'] = ''

import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

from PyQt6.QtWidgets import QApplication
from ui.main_window import MainWindow

app = QApplication(sys.argv)
window = MainWindow()
window.show()

# 打印状态
print("=== 启动状态 ===")
print(f"当前路径: {window.current_path}")
print(f"面包屑路径: {window.path_nav_bar.current_path}")
print(f"obj 根节点: {window.obj_root_node.name}")
print(f"vis 根节点: {window.vis_root_node.name}")
print(f"train 根节点: {window.train_root_node.name}")
print(f"obj 图节点数: {len(window.obj_graph.nodes)}")
print(f"vis 图节点数: {len(window.vis_graph.nodes)}")
print(f"train 图节点数: {len(window.train_graph.nodes)}")
print(f"当前图节点数: {len(window.current_graph.nodes)}")

# 模拟双击 obj 根节点
print("=== 模拟双击 obj 根节点 ===")
from ui.graphics.node_graphics_item_v2 import NodeGraphicsItemV2
# 获取 obj 根节点的图形项
obj_graphics_item = None
for node, graphics_item in window.node_graphics_items.items():
    if node == window.obj_root_node:
        obj_graphics_item = graphics_item
        break
if obj_graphics_item:
    print(f"找到图形项，触发双击事件")
    # 手动调用 mouseDoubleClickEvent（需要事件对象）
    from PyQt6.QtCore import QPointF
    from PyQt6.QtGui import QMouseEvent
    from PyQt6.QtCore import Qt
    # 创建一个虚拟事件
    event = QMouseEvent(QMouseEvent.Type.MouseButtonDblClick, QPointF(0, 0), Qt.MouseButton.LeftButton, Qt.MouseButton.LeftButton, Qt.KeyboardModifier.NoModifier)
    obj_graphics_item.mouseDoubleClickEvent(event)
else:
    print("未找到 obj 根节点的图形项")

# 等待短暂时间后退出
from PyQt6.QtCore import QTimer
QTimer.singleShot(1000, app.quit)
sys.exit(app.exec())