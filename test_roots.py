#!/usr/bin/env python3
"""测试根节点是否存在"""
import sys
sys.path.insert(0, '.')

from ui.main_window import MainWindow
from PyQt6.QtWidgets import QApplication

app = QApplication(sys.argv)
window = MainWindow()
print("当前路径:", window.current_path)
print("obj 根节点:", window.obj_root_node.name if hasattr(window, 'obj_root_node') else '未找到')
print("vis 根节点:", window.vis_root_node.name if hasattr(window, 'vis_root_node') else '未找到')
print("train 根节点:", window.train_root_node.name if hasattr(window, 'train_root_node') else '未找到')
print("obj 图节点数:", len(window.obj_graph.nodes))
print("vis 图节点数:", len(window.vis_graph.nodes))
print("train 图节点数:", len(window.train_graph.nodes))

# 切换到 vis 路径
window._on_path_changed("/vis")
print("切换到 /vis 后当前路径:", window.current_path)
print("vis 图中节点数:", len(window.current_graph.nodes))

# 切换回 obj
window._on_path_changed("/obj")
print("切回 /obj 后当前路径:", window.current_path)
print("obj 图中节点数:", len(window.current_graph.nodes))

print("测试通过")