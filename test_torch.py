#!/usr/bin/env python3
"""测试Torch导入"""
import sys
import os
sys.path.insert(0, '.')

# 设置环境变量
os.environ['PYTORCH_NO_CUDA'] = '1'
os.environ['CUDA_VISIBLE_DEVICES'] = ''

try:
    import torch
    print(f"Torch 版本: {torch.__version__}")
    print(f"CUDA 可用: {torch.cuda.is_available()}")
except Exception as e:
    print(f"导入 torch 失败: {e}")
    import traceback
    traceback.print_exc()

# 尝试导入核心节点
try:
    import core.nodes
    print("成功导入 core.nodes")
except Exception as e:
    print(f"导入 core.nodes 失败: {e}")
    import traceback
    traceback.print_exc()