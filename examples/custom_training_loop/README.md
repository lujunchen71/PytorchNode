# 自定义训练循环示例

这个示例展示如何使用PytorchNode的ForEach节点组创建自定义训练循环。

## 特性

- 使用ForEach Begin/Data/End节点组
- 自定义学习率衰减
- 动态参数调整
- 训练过程可视化

## 文件说明

- `model.pnne`: 节点图文件(包含ForEach循环)
- `train.py`: 训练脚本
