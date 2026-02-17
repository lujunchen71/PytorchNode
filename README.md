# PNNE - PyTorch Neural Network Editor

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.0%2B-orange.svg)](https://pytorch.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

一个基于节点的可视化深度学习模型编辑器，灵感来自 Houdini。通过直观的节点编辑器界面，轻松构建、训练和调试 PyTorch 神经网络模型。

> [!TIP]
> 该项目已通过 Git 版本控制，可使用 `git` 命令进行备份和协作。

## ✨ 主要特性

### 🎨 可视化节点编辑
- **直观的图形界面**: 拖拽式节点连接，所见即所得
- **丰富的节点库**: 涵盖常用的 PyTorch 层和操作
- **实时预览**: 即时查看模型结构和数据流
- **子网支持**: 将复杂网络封装为可复用的子网节点

### 🔧 强大的表达式系统
- **参数表达式**: 使用表达式动态计算参数值
- **引用机制**: 引用其他节点的输出和属性
- **内置函数库**: 数学、张量、字符串等函数支持

### 🚀 完整的训练流程
- **内置训练引擎**: 支持标准训练循环
- **实时监控**: 损失曲线、准确率等指标可视化
- **检查点管理**: 自动保存和恢复训练状态
- **分布式训练**: 支持多GPU和分布式训练（计划中）

### 📊 数据可视化
- **张量查看器**: 查看中间层的输出和梯度
- **权重分布**: 可视化模型参数分布
- **特征图可视化**: 查看卷积层的特征图
- **训练曲线**: 实时绘制训练和验证指标

### 🔌 可扩展插件系统
- **插件架构**: 支持自定义节点和功能
- **热插拔**: 动态加载和卸载插件
- **API文档**: 完整的插件开发文档

### 💾 灵活的序列化
- **项目保存**: JSON格式保存整个项目
- **版本兼容**: 向后兼容的版本管理
- **导出支持**: 导出为标准 PyTorch 模型

## 📦 安装

### 前置要求
- Python 3.8 或更高版本
- PyTorch 2.0 或更高版本
- PyQt6 6.5 或更高版本

### 使用 pip 安装

```bash
# 克隆仓库
git clone https://github.com/lujunchen71/PytorchNode.git
cd PytorchNode

# 安装依赖
pip install -r requirements.txt

# 运行应用
python main.py
```

### 使用 conda 安装

```bash
# 创建虚拟环境
conda create -n pnne python=3.10
conda activate pnne

# 安装 PyTorch
conda install pytorch torchvision torchaudio pytorch-cuda=11.8 -c pytorch -c nvidia

# 安装其他依赖
pip install -r requirements.txt

# 运行应用
python main.py
```

## 🚀 快速开始

### 创建第一个神经网络

1. **启动应用**: 运行 `python main.py`

2. **创建输入节点**: 
   - 按 `Tab` 键打开节点搜索菜单
   - 搜索 "Input" 并创建

3. **添加网络层**:
   - 创建 `Linear` 节点
   - 创建 `ReLU` 激活节点
   - 创建输出层

4. **连接节点**:
   - 从一个节点的输出引脚拖动到另一个节点的输入引脚

5. **配置参数**:
   - 在属性面板中设置层的参数（如输入/输出维度）

6. **运行模型**:
   - 点击工具栏的"编译"按钮生成 PyTorch 模型
   - 点击"运行"执行前向传播

### 训练模型

1. **设置数据加载器**:
   - 创建 `DataLoader` 节点
   - 配置数据集路径和批次大小

2. **配置训练循环**:
   - 创建 `Loss` 节点（如 `CrossEntropyLoss`）
   - 创建 `Optimizer` 节点（如 `Adam`）
   - 创建 `TrainingLoop` 节点

3. **开始训练**:
   - 连接所有节点
   - 点击"开始训练"按钮
   - 在训练监控面板查看实时指标

## 📚 文档

完整文档请查看 `doc/` 目录：

- [项目总览](doc/00_项目总览.md)
- [架构设计](doc/01_架构设计.md)
- [开发路线图](doc/02_开发路线图_完善版.md)
- [核心节点系统](doc/03_核心节点系统.md)
- [UI框架设计](doc/04_UI框架设计.md)
- [PyTorch集成](doc/05_PyTorch集成.md)
- [表达式引擎](doc/06_表达式引擎.md)
- [训练管线](doc/07_训练管线.md)
- [可视化系统](doc/08_可视化系统.md)
- [插件系统](doc/09_插件系统.md)
- [序列化系统](doc/10_序列化系统.md)
- [编码规范](doc/11_编码规范.md)
- [API参考](doc/12_API参考.md)
- [文件清单](doc/13_文件清单.md)

## 🎯 项目结构

```
PytorchNode/
├── core/                   # 核心功能模块
│   ├── base/              # 基础类（Node, Pin, Connection等）
│   ├── nodes/             # 节点实现
│   ├── engine/            # 执行引擎
│   ├── expressions/       # 表达式引擎
│   ├── serialization/     # 序列化系统
│   └── undo/              # 撤销/重做系统
├── ui/                    # 用户界面模块
│   ├── graphics/          # 图形系统
│   ├── panels/            # 面板组件
│   ├── widgets/           # 自定义控件
│   ├── dialogs/           # 对话框
│   └── themes/            # 主题系统
├── utils/                 # 工具模块
├── plugins/               # 插件系统
├── config/                # 配置文件
├── examples/              # 示例项目
├── doc/                   # 文档
├── tests/                 # 测试
├── main.py                # 程序入口
└── requirements.txt       # 依赖清单
```

## 🤝 贡献

欢迎贡献！请查看 [贡献指南](CONTRIBUTING.md) 了解详情。

### 开发设置

```bash
# 安装开发依赖
pip install -r requirements-dev.txt

# 运行测试
pytest tests/

# 代码格式化
black .

# 类型检查
mypy core/
```

## 📝 许可证

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。

## 🙏 致谢

- [PyTorch](https://pytorch.org/) - 深度学习框架
- [PySide6](https://www.qt.io/qt-for-python) - GUI框架
- [Houdini](https://www.sidefx.com/) - 节点编辑器灵感来源

## 📧 联系

- 问题反馈: [GitHub Issues](https://github.com/lujunchen71/PytorchNode/issues)
- 邮箱: your.email@example.com

## 🗺️ 路线图

### v0.1.0 (当前开发中)
- [x] 核心节点系统
- [x] 基础UI框架
- [ ] 常用PyTorch节点实现
- [ ] 表达式引擎
- [ ] 基础训练功能

### v0.2.0 (计划中)
- [ ] 完整的可视化系统
- [ ] 插件系统
- [ ] 更多节点类型
- [ ] 性能优化

### v0.3.0 (计划中)
- [ ] 分布式训练支持
- [ ] 模型导出
- [ ] 在线文档

### v1.0.0 (长期目标)
- [ ] 稳定的API
- [ ] 完整的测试覆盖
- [ ] 丰富的示例项目
- [ ] 社区插件生态

---

**注意**: 本项目仍在早期开发阶段，API可能会有较大变动。
