# Implementation Plan: 可视化深度学习模型编辑器

**Branch**: `1-visual-node-editor` | **Date**: 2026-02-15 | **Spec**: [spec.md](./spec.md)  
**Input**: Feature specification from `/specs/1-visual-node-editor/spec.md`

## Summary

构建一个跨平台的可视化深度学习模型编辑器，使用Python 3.10+、PyQt6和PyTorch 2.0+作为核心技术栈。系统采用严格的分层架构（UI、Bridge、Core、Engine），通过全局信号总线实现解耦通信。支持节点拖拽、实时训练可视化、ForEach循环结构、子网络封装、插件系统和完整的撤销/重做功能。项目文件使用JSON格式序列化，支持增量保存、版本迁移和剪贴板操作。测试使用pytest，代码遵循PEP 8和类型提示。

## Technical Context

**Language/Version**: Python 3.10+（使用现代Python特性，支持类型注解和match-case语句）  
**Primary Dependencies**:  
- **UI**: PyQt6（跨平台GUI框架）
- **Deep Learning**: PyTorch 2.0+（深度学习后端，torch.compile支持）
- **Graph Management**: NetworkX（图管理、拓扑排序）
- **Visualization**: Matplotlib + PyQtGraph（实时权重、激活、梯度可视化）
- **Testing**: pytest（单元测试和集成测试）
- **Code Quality**: black（格式化）、pylint（静态分析）、mypy（类型检查）

**Storage**: 本地文件系统（JSON格式的.pnne项目文件）  
**Testing**: pytest + pytest-qt（UI测试），覆盖率目标：core/ ≥ 80%, ui/ ≥ 60%  
**Target Platform**: 跨平台（Windows、Linux、macOS），支持CPU和CUDA GPU  
**Project Type**: 单项目桌面应用（Python单仓库，UI + Core分离）  
**Performance Goals**:  
- 图渲染：100节点内渲染<100ms，1000节点保持30 FPS
- 节点执行延迟<10ms（非DL计算）
- 启动时间<3秒，项目加载<5秒（50-100节点）
- 训练可视化延迟<500ms

**Constraints**:  
- 核心层（core/）严格禁止依赖UI框架
- 插件沙箱环境，限制文件和网络访问
- 内存管理：及时释放PyTorch张量，避免泄漏
- 向后兼容：文件格式变更需要版本迁移机制

**Scale/Scope**:  
- 目标用户：初学者到数据科学家（3个用户层级）
- 预定义节点：90%常见PyTorch层（Linear、Conv、ReLU等）
- 支持图规模：最多1000个节点
- 插件接口：标准化Python模块接口
- 6个优先级分明的用户故事（P1-P6）

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### 代码质量检查
- ✅ **类型注解**: 所有Python代码必须使用Type Hints（mypy验证）
- ✅ **PEP8遵守**: 使用black格式化，pylint评分≥8.0/10
- ✅ **文档化**: 所有公共API有文档字符串
- ✅ **模块化**: UI-Core严格分离，核心不依赖PyQt6

### 测试驱动开发
- ✅ **TDD强制**: 先写测试（pytest），后写实现
- ✅ **覆盖率**: core/ ≥ 80%, ui/ ≥ 60%
- ✅ **测试分层**: 单元测试（test_core/）、集成测试（test_integration/）、UI测试（test_ui/）
- ✅ **命名规范**: `test_[feature]_[scenario]_[expected_result]`

### 用户体验一致性
- ✅ **主题系统**: 深色/浅色模式切换
- ✅ **撤销/重做**: Command模式实现所有操作可撤销
- ✅ **快捷键**: 完整的快捷键体系（Ctrl+Z、Ctrl+S等）
- ✅ **国际化**: 支持中文和英文界面

### 性能标准
- ✅ **渲染性能**: 100节点<100ms，1000节点30FPS（使用场景剔除）
- ✅ **GPU优先**: PyTorch计算优先使用CUDA
- ✅ **内存管理**: 及时释放张量，监控内存使用
- ✅ **启动优化**: 延迟加载插件和非必要模块

### 架构清晰性
- ✅ **分层架构**: UI → Bridge → Core → Engine（严格依赖方向）
- ✅ **信号总线**: 全局信号总线解耦模块通信
- ✅ **插件独立**: 插件接口明确，沙箱环境运行
- ✅ **序列化标准**: JSON格式.pnne文件，支持版本迁移

**Gate Status**: ✅ **PASS** - 所有宪法要求已在架构设计中体现

## Project Structure

### Documentation (this feature)

```text
specs/1-visual-node-editor/
├── spec.md              # 功能规范（已完成）
├── plan.md              # 本文件 - 技术实施计划
├── data-model.md        # Phase 1 - 数据模型设计
├── quickstart.md        # Phase 1 - 快速开始指南
├── contracts/           # Phase 1 - 节点接口契约
│   ├── node_interface.md
│   ├── pin_interface.md
│   └── plugin_interface.md
├── checklists/          # 质量检查清单
│   └── requirements.md  # 规范质量检查（已完成）
└── tasks.md             # Phase 2 - 任务分解（需/speckit.tasks生成）
```

### Source Code (repository root)

```text
PytorchNode/
├── core/                          # 核心逻辑层（无UI依赖）
│   ├── base/                      # 基础类和抽象接口
│   │   ├── __init__.py
│   │   ├── node.py                # Node基类
│   │   ├── pin.py                 # Pin基类（输入/输出针脚）
│   │   ├── pack.py                # Pack类（NumpyPack、TorchPack数据包）
│   │   ├── parameter.py           # Parameter类（参数系统）
│   │   ├── connection.py          # Connection类（节点连接）
│   │   ├── node_graph.py          # NodeGraph类（图管理）
│   │   ├── node_registry.py       # 节点注册表
│   │   ├── node_factory.py        # 节点工厂
│   │   └── path_manager.py        # 层次路径管理器
│   ├── nodes/                     # 预定义节点实现
│   │   ├── __init__.py
│   │   ├── nn/                    # PyTorch神经网络层节点
│   │   │   ├── __init__.py
│   │   │   ├── linear_node.py
│   │   │   ├── conv_nodes.py
│   │   │   ├── activation_nodes.py
│   │   │   └── normalization_nodes.py
│   │   ├── data/                  # 数据加载和处理节点
│   │   │   ├── __init__.py
│   │   │   ├── dataset_nodes.py   # MNIST、CIFAR-10加载节点
│   │   │   ├── custom_data_node.py # 自定义数据加载（CSV/JSON元数据）
│   │   │   └── transform_nodes.py # 数据预处理节点
│   │   ├── training/              # 训练相关节点
│   │   │   ├── __init__.py
│   │   │   ├── optimizer_nodes.py
│   │   │   ├── loss_nodes.py
│   │   │   ├── save_model_node.py  # SaveModel节点
│   │   │   └── load_model_node.py  # LoadModel节点
│   │   ├── control/               # 控制流节点
│   │   │   ├── __init__.py
│   │   │   ├── foreach_begin_node.py
│   │   │   ├── foreach_data_node.py
│   │   │   └── foreach_end_node.py
│   │   └── subnet/                # 子网络节点
│   │       ├── __init__.py
│   │       └── subnet_node.py
│   ├── engine/                    # 执行引擎
│   │   ├── __init__.py
│   │   ├── executor.py            # 图执行器（拓扑排序）
│   │   ├── compiler.py            # 实时编译器（节点图→PyTorch代码）
│   │   └── training_pipeline.py  # 训练管线管理
│   ├── expressions/               # 表达式引擎
│   │   ├── __init__.py
│   │   ├── parser.py              # 表达式解析器
│   │   ├── evaluator.py           # 表达式求值器
│   │   └── context.py             # 表达式上下文（变量管理）
│   ├── serialization/             # 序列化系统
│   │   ├── __init__.py
│   │   ├── serializer.py          # JSON序列化器
│   │   ├── migrator.py            # 版本迁移器
│   │   └── clipboard.py           # 剪贴板序列化
│   ├── undo/                      # 撤销/重做系统
│   │   ├── __init__.py
│   │   ├── command.py             # Command抽象基类
│   │   ├── undo_stack.py          # 撤销栈管理器
│   │   └── commands/              # 具体命令实现
│   │       ├── __init__.py
│   │       ├── add_node_command.py
│   │       ├── delete_node_command.py
│   │       ├── connect_command.py
│   │       └── modify_param_command.py
│   └── utils/                     # 核心工具函数
│       ├── __init__.py
│       ├── validation.py          # 连接验证、循环检测
│       ├── graph_algorithms.py    # 图算法（拓扑排序）
│       └── type_inference.py      # 类型推断

├── ui/                            # UI层（PyQt6）
│   ├── __init__.py
│   ├── main_window.py             # 主窗口
│   ├── graphics/                  # 图形视图组件
│   │   ├── __init__.py
│   │   ├── node_graphics_scene.py # 节点画布场景
│   │   ├── node_graphics_view.py  # 节点画布视图
│   │   ├── node_graphics_item.py  # 节点图形项
│   │   ├── pin_graphics_item.py   # 针脚图形项
│   │   ├── connection_graphics_item.py # 连接线图形项
│   │   └── loop_block_graphics_item.py # ForEach循环块凸包
│   ├── panels/                    # 面板组件
│   │   ├── __init__.py
│   │   ├── node_palette_panel.py  # 节点面板（拖拽）
│   │   ├── properties_panel.py    # 属性面板（参数配置）
│   │   ├── hierarchy_panel.py     # 层次面板（/obj/、/vis/、/train/）
│   │   └── visualization_panel.py # 可视化面板（训练监控）
│   ├── dialogs/                   # 对话框
│   │   ├── __init__.py
│   │   ├── settings_dialog.py     # 设置对话框
│   │   └── plugin_manager_dialog.py # 插件管理对话框
│   ├── widgets/                   # 自定义控件
│   │   ├── __init__.py
│   │   ├── parameter_widgets.py   # 参数编辑控件
│   │   └── expression_editor.py   # 表达式编辑器
│   ├── themes/                    # 主题系统
│   │   ├── __init__.py
│   │   ├── theme_manager.py
│   │   ├── dark_theme.py
│   │   └── light_theme.py
│   └── visualization/             # 训练可视化
│       ├── __init__.py
│       ├── loss_curve_widget.py   # 损失曲线（Matplotlib）
│       ├── weight_heatmap_widget.py # 权重热图
│       ├── gradient_histogram_widget.py # 梯度直方图
│       └── activation_plot_widget.py # 激活值分布

├── bridge/                        # 桥接层（连接UI和Core）
│   ├── __init__.py
│   ├── signal_bus.py              # 全局信号总线
│   ├── node_bridge.py             # 节点桥接
│   ├── graph_bridge.py            # 图桥接
│   └── training_bridge.py         # 训练桥接

├── plugins/                       # 插件系统
│   ├── __init__.py
│   ├── plugin_manager.py          # 插件管理器
│   ├── plugin_loader.py           # 插件加载器（热加载）
│   ├── plugin_sandbox.py          # 沙箱环境
│   ├── plugin_interface.py        # 插件接口定义
│   └── examples/                  # 示例插件
│       └── custom_layer_plugin/
│           ├── __init__.py
│           ├── plugin.py
│           └── README.md

├── config/                        # 配置文件
│   ├── __init__.py
│   ├── settings.py                # 应用设置
│   └── themes/                    # 主题配置文件
│       ├── dark.json
│       └── light.json

├── resources/                     # 资源文件
│   ├── icons/                     # 图标资源
│   │   ├── node_icons/
│   │   └── toolbar_icons/
│   ├── fonts/                     # 字体资源
│   └── templates/                 # 模板文件
│       └── plugin_template.py

├── tests/                         # 测试套件
│   ├── __init__.py
│   ├── conftest.py                # pytest配置
│   ├── test_core/                 # 核心层单元测试
│   │   ├── __init__.py
│   │   ├── test_node.py
│   │   ├── test_pin.py
│   │   ├── test_pack.py           # Pack系统测试（NumpyPack、TorchPack）
│   │   ├── test_parameter.py      # 参数系统测试
│   │   ├── test_connection.py
│   │   ├── test_node_graph.py
│   │   ├── test_validation.py     # 连接验证、循环检测测试
│   │   ├── test_foreach_nodes.py  # ForEach节点测试
│   │   └── test_multi_pack_processing.py  # 多Pack处理测试
│   ├── test_engine/               # 引擎测试
│   │   ├── __init__.py
│   │   ├── test_executor.py
│   │   ├── test_compiler.py
│   │   └── test_training_pipeline.py
│   ├── test_serialization/        # 序列化测试
│   │   ├── __init__.py
│   │   ├── test_serializer.py
│   │   └── test_migrator.py
│   ├── test_expressions/          # 表达式引擎测试
│   │   ├── __init__.py
│   │   ├── test_parser.py
│   │   └── test_evaluator.py
│   ├── test_plugins/              # 插件系统测试
│   │   ├── __init__.py
│   │   ├── test_plugin_loader.py
│   │   └── test_plugin_sandbox.py
│   ├── test_ui/                   # UI测试（pytest-qt）
│   │   ├── __init__.py
│   │   ├── test_main_window.py
│   │   ├── test_node_graphics.py
│   │   └── test_visualization.py
│   └── test_integration/          # 集成测试
│       ├── __init__.py
│       ├── test_node_connection_workflow.py
│       ├── test_training_workflow.py
│       ├── test_save_load_workflow.py
│       └── test_foreach_workflow.py

├── docs/                          # 项目文档（已存在）
│   ├── 00_项目总览.md
│   ├── 01_架构设计.md
│   ├── 03_核心节点系统.md
│   ├── 04_UI框架设计.md
│   ├── 05_PyTorch集成.md
│   ├── 06_表达式引擎.md
│   ├── 07_训练管线.md
│   ├── 08_可视化系统.md
│   ├── 09_插件系统.md
│   ├── 10_序列化系统.md
│   ├── 11_编码规范.md
│   ├── 12_API参考.md
│   └── 13_文件清单.md

├── examples/                      # 示例项目
│   ├── simple_mlp/                # 简单多层感知器示例
│   ├── mnist_classifier/          # MNIST分类器示例
│   └── custom_training_loop/      # 自定义训练循环示例

├── main.py                        # 应用入口
├── setup.py                       # 安装脚本
├── requirements.txt               # 依赖列表
├── pyproject.toml                 # 项目配置（black、mypy、pytest）
├── .gitignore
├── README.md
└── LICENSE
```

**Structure Decision**: 
采用单项目结构（Option 1），因为这是桌面应用而非Web应用。核心设计原则：
1. **严格分层**: UI → Bridge → Core → Engine，依赖方向单向，核心层完全独立于UI
2. **信号总线**: 使用全局信号总线（SignalBus）实现跨层通信，避免直接依赖
3. **插件隔离**: 插件系统独立目录，通过接口和沙箱环境与核心交互
4. **测试驱动**: tests/目录按功能模块组织，对应core/、ui/、engine/等结构

## Architecture Overview

### 分层架构

```text
┌─────────────────────────────────────────────────────────────────┐
│                          UI Layer (PyQt6)                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │ Main Window  │  │ Graphics View│  │ Panels & Dialogs     │  │
│  │              │  │ (节点画布)    │  │ (属性、层次、可视化)   │  │
│  └──────────────┘  └──────────────┘  └──────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              ↓↑
┌─────────────────────────────────────────────────────────────────┐
│                       Bridge Layer (Signal Bus)                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │ Node Bridge  │  │ Graph Bridge │  │ Training Bridge      │  │
│  │              │  │              │  │                      │  │
│  └──────────────┘  └──────────────┘  └──────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              ↓↑
┌─────────────────────────────────────────────────────────────────┐
│                      Core Layer (Pure Python)                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │ Node System  │  │ Node Graph   │  │ Expressions Engine   │  │
│  │ (Node, Pin)  │  │ (Graph Mgmt) │  │ (Dynamic Params)     │  │
│  └──────────────┘  └──────────────┘  └──────────────────────┘  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │ Serialization│  │ Undo/Redo    │  │ Plugin System        │  │
│  │ (JSON .pnne) │  │ (Command)    │  │ (Sandbox)            │  │
│  └──────────────┘  └──────────────┘  └──────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              ↓↑
┌─────────────────────────────────────────────────────────────────┐
│                    Engine Layer (PyTorch)                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │ Executor     │  │ Compiler     │  │ Training Pipeline    │  │
│  │ (Topo Sort)  │  │ (Graph→Code) │  │ (Train Loop)         │  │
│  └──────────────┘  └──────────────┘  └──────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

### 关键设计模式

1. **Command Pattern** (撤销/重做)
   - 所有用户操作封装为Command对象
   - UndoStack管理命令历史
   - 支持宏命令（复合操作）

2. **Factory Pattern** (节点创建)
   - NodeFactory根据节点类型创建实例
   - NodeRegistry注册所有可用节点
   - 支持插件动态注册新节点类型

3. **Observer Pattern** (信号总线)
   - 全局SignalBus实现发布-订阅
   - UI层订阅Core层事件（节点添加、参数变更等）
   - 解耦UI和Core，支持多视图同步

4. **Strategy Pattern** (表达式求值)
   - 不同类型表达式使用不同求值策略
   - 支持数学运算、条件分支、变量引用
   - 可扩展自定义函数

5. **Visitor Pattern** (图遍历)
   - Executor使用Visitor模式遍历节点图
   - 支持多种遍历策略（拓扑排序、深度优先等）
   - 便于添加新的图分析功能

## Key Technologies

### PyQt6（UI框架）
- **Graphics View Framework**: 用于节点画布，支持高性能2D图形渲染
- **Signal/Slot机制**: 实现UI事件处理和跨模块通信
- **Model/View架构**: 属性面板使用Model/View分离数据和视图
- **QUndoStack**: 集成Qt的撤销/重做框架

### PyTorch 2.0+（深度学习后端）
- **torch.nn模块**: 预定义层节点直接封装torch.nn类
- **torch.optim**: 优化器节点封装
- **torch.compile**: 可选的JIT编译加速（实时编译开关）
- **CUDA支持**: 自动检测GPU，优先使用CUDA

### NetworkX（图管理）
- **拓扑排序**: 使用`nx.topological_sort`确定节点执行顺序
- **循环检测**: 使用`nx.is_directed_acyclic_graph`检测非法循环
- **路径查找**: ForEach节点路径查找使用NetworkX算法

### Matplotlib + PyQtGraph（可视化）
- **Matplotlib**: 静态图表（loss曲线、混淆矩阵）
- **PyQtGraph**: 实时动态图表（权重热图、梯度直方图）
- **集成PyQt6**: 使用`FigureCanvasQTAgg`嵌入Matplotlib到PyQt

### pytest + pytest-qt（测试）
- **pytest**: 单元测试和集成测试框架
- **pytest-qt**: Qt应用测试支持（qtbot fixture）
- **pytest-cov**: 代码覆盖率分析
- **pytest-mock**: Mock对象支持（隔离依赖）

## Data Flow

### 节点执行流程
```text
1. User Action (UI)
   └→ SignalBus.node_added / connection_created
      └→ Core: NodeGraph.add_node() / NodeGraph.add_connection()
         └→ Validation: check_connection_valid() / detect_cycles()
            └→ Engine: Executor.execute_graph()
               └→ NetworkX: topological_sort(graph)
                  └→ For each node in sorted order:
                     └→ node.execute(inputs) → outputs
                        └→ PyTorch: forward pass
                           └→ Return results to UI for visualization
```

### 训练流程
```text
1. User clicks "Start Training" (UI)
   └→ TrainingBridge.start_training_requested
      └→ TrainingPipeline.start(data_node, model_node, loss_node, optimizer_node)
         └→ For each epoch:
            └→ For each batch:
               ├→ Execute data_node → batch_data
               ├→ Execute model_node(batch_data) → predictions
               ├→ Execute loss_node(predictions, labels) → loss
               ├→ loss.backward() → gradients
               ├→ Execute optimizer_node.step() → update weights
               └→ SignalBus.training_step_completed(loss, metrics)
                  └→ UI: update loss curve, weight heatmap, gradient histogram
         └→ Execute save_model_node (if configured)
```

### 序列化流程
```text
Save:
1. User: Ctrl+S / File→Save
   └→ Serializer.serialize(node_graph) → JSON dict
      ├→ nodes: [{id, type, params, position}, ...]
      ├→ connections: [{from_node, from_pin, to_node, to_pin}, ...]
      ├→ foreach_groups: [{begin_id, data_id, end_id}, ...]
      └→ metadata: {version, created_at, modified_at}
   └→ Write to .pnne file (JSON format)

Load:
1. User: File→Open .pnne
   └→ Read JSON from file
      └→ Migrator.migrate(json, from_version, to_version) → updated JSON
         └→ Serializer.deserialize(json) → node_graph
            ├→ Create nodes from json['nodes']
            ├→ Create connections from json['connections']
            ├→ Restore ForEach groups
            └→ Restore metadata
         └→ UI: render node_graph
```

## ForEach循环结构设计

### 三节点组设计
```python
# ForEach Begin Node
class ForEachBeginNode(Node):
    def __init__(self):
        super().__init__()
        self.add_input_pin("input", DataType.TENSOR)
        self.add_output_pin("loop_value", DataType.TENSOR)
        self.add_parameter("end_node_path", "/train/loop_1/end")  # 指向End节点路径
        
# ForEach Data Node
class ForEachDataNode(Node):
    def __init__(self):
        super().__init__()
        self.add_output_pin("current_iteration", DataType.INT)
        self.add_output_pin("total_iterations", DataType.INT)
        self.add_parameter("end_node_path", "/train/loop_1/end")  # 指向End节点路径
        self.current_iter = 0
        self.total_iter = 0
        
# ForEach End Node
class ForEachEndNode(Node):
    def __init__(self):
        super().__init__()
        self.add_input_pin("loop_value", DataType.TENSOR)
        self.add_output_pin("output", DataType.TENSOR)
        self.add_parameter("max_iterations", 10)  # 循环次数
```

### 凸包可视化
```python
# LoopBlockGraphicsItem (UI层)
class LoopBlockGraphicsItem(QGraphicsPathItem):
    def __init__(self, begin_node, data_node, end_node, nodes_in_loop):
        # 计算凸包路径
        self.convex_hull = self.compute_convex_hull(nodes_in_loop)
        # 设置背景色（默认黄色，可自定义）
        self.setBrush(QColor(255, 255, 0, 50))  # 半透明黄色
        self.setPen(QPen(QColor(255, 200, 0), 2, Qt.DashLine))
```

### 连接验证规则
```python
# Validation (Core层)
def check_connection_valid(from_pin, to_pin) -> bool:
    # 规则1: 输出只能连接输入
    if from_pin.is_input() and to_pin.is_input():
        return False  # 输入不能连输入
    if from_pin.is_output() and to_pin.is_output():
        return False  # 输出不能连输出
    
    # 规则2: 类型兼容性
    if not are_types_compatible(from_pin.data_type, to_pin.data_type):
        return False
    
    # 规则3: 循环检测（使用NetworkX）
    temp_graph = graph.copy()
    temp_graph.add_edge(from_node, to_node)
    if not nx.is_directed_acyclic_graph(temp_graph):
        return False  # 非法循环
    
    return True
```

## 数据包系统设计（Pack System）

### Pack类型

系统支持两种数据包类型，用于节点间数据传递：

1. **NumPy Pack**: 主要用于字符串、元数据、标签等非张量数据存储
   - 类型标识：`NumpyPack`
   - 数据格式：`np.ndarray`（通常是1D或2D数组）
   - 使用场景：数据集标签、文件名列表、配置信息、中间计算结果（非张量）

2. **Torch Pack**: 主要用于PyTorch张量数据
   - 类型标识：`TorchPack`
   - 数据格式：`torch.Tensor`
   - 使用场景：图像数据、特征图、权重、梯度、网络输出

### 多Pack处理规则

```python
# 节点执行示例 - 处理多个Pack
class GenericNode(Node):
    def execute(self, inputs: Dict[str, List[Pack]]) -> Dict[str, List[Pack]]:
        """
        inputs = {
            "input_1": [NumpyPack(labels), TorchPack(images)],
            "input_2": [TorchPack(features)]
        }
        """
        numpy_packs = []
        torch_packs = []
        
        # 分离不同类型的Pack
        for pin_name, pack_list in inputs.items():
            for pack in pack_list:
                if isinstance(pack, NumpyPack):
                    numpy_packs.append(pack)
                elif isinstance(pack, TorchPack):
                    torch_packs.append(pack)
        
        # 通常只有一个TorchPack，多个NumpyPack
        # 对每个Pack分别应用节点算法（除非特殊节点有特殊逻辑）
        output_torch_packs = []
        for torch_pack in torch_packs:
            result = self.process_torch(torch_pack.data)  # 应用算法
            output_torch_packs.append(TorchPack(result))
        
        output_numpy_packs = []
        for numpy_pack in numpy_packs:
            result = self.process_numpy(numpy_pack.data)
            output_numpy_packs.append(NumpyPack(result))
        
        return {"output": output_torch_packs + output_numpy_packs}
```

### Pack类定义

```python
# core/base/pack.py
from typing import Union
import numpy as np
import torch

class Pack:
    """数据包基类"""
    def __init__(self, data, metadata: dict = None):
        self.data = data
        self.metadata = metadata or {}
        
class NumpyPack(Pack):
    """NumPy数据包 - 用于字符串、元数据、标签"""
    def __init__(self, data: np.ndarray, metadata: dict = None):
        super().__init__(data, metadata)
        assert isinstance(data, np.ndarray)
        
    def get_shape(self):
        return self.data.shape
        
class TorchPack(Pack):
    """Torch数据包 - 用于PyTorch张量"""
    def __init__(self, data: torch.Tensor, metadata: dict = None):
        super().__init__(data, metadata)
        assert isinstance(data, torch.Tensor)
        
    def get_shape(self):
        return tuple(self.data.shape)
    
    def to_device(self, device):
        """移动到指定设备（CPU/GPU）"""
        self.data = self.data.to(device)
```

### Pin多输入输出设计

```python
# 节点可以有多个输入针脚和输出针脚
class ConvNode(Node):
    def __init__(self):
        super().__init__()
        # 多个输入
        self.add_input_pin("input", DataType.TENSOR)  # 主输入（图像）
        self.add_input_pin("labels", DataType.NUMPY)  # 可选标签（NumpyPack）
        
        # 多个输出
        self.add_output_pin("output", DataType.TENSOR)  # 卷积输出（TorchPack）
        self.add_output_pin("shape_info", DataType.NUMPY)  # 形状信息（NumpyPack）
```

## 参数系统设计（Parameter System）

### 参数类型

节点支持以下参数类型，所有参数在属性面板中可编辑：

```python
# core/base/parameter.py
class ParameterType(Enum):
    FLOAT = "float"                 # 浮点数
    INT = "int"                     # 整数
    BOOL = "checkbox"               # 复选框
    STRING = "string"               # 字符串
    PATH = "path"                   # 文件/目录路径
    FLOAT_RAMP = "float_ramp"       # 浮点曲线/渐变
    VECTOR2 = "vector2"             # 二维向量 (x, y)
    VECTOR3 = "vector3"             # 三维向量 (x, y, z)
    INT2 = "int2"                   # 整数二维向量
    INT3 = "int3"                   # 整数三维向量
    BUTTON = "button"               # 按钮（触发操作）
    COLOR = "color"                 # 颜色选择器
    ENUM = "enum"                   # 下拉选择（枚举）
```

### 参数定义结构

```python
class Parameter:
    def __init__(self, name: str, label: str, param_type: ParameterType,
                 default_value, metadata: dict = None):
        self.name = name           # 唯一标识（用于代码引用）
        self.label = label         # 显示标签（用于UI显示）
        self.type = param_type     # 参数类型
        self.value = default_value # 当前值
        self.metadata = metadata or {}  # 额外元数据
        
        # 条件显示/编辑控制（表达式）
        self.hide_expression = ""   # 隐藏条件：如 "layer == 1"
        self.disable_expression = "" # 禁用条件：如 "mode == 'auto'"
        
        # 参数来源标记
        self.is_code_defined = True  # 是否在代码中定义（不可删除）
        self.is_instance_param = False  # 是否为实例参数（可删除，仅此实例有效）

# 使用示例
class ConvNode(Node):
    def __init__(self):
        super().__init__()
        # 代码定义的参数（不可删除）
        self.add_parameter(Parameter(
            name="in_channels",
            label="输入通道数",
            param_type=ParameterType.INT,
            default_value=3,
            metadata={"min": 1, "max": 1024}
        ))
        
        self.add_parameter(Parameter(
            name="kernel_size",
            label="卷积核大小",
            param_type=ParameterType.INT,
            default_value=3,
            metadata={"min": 1, "max": 11}
        ))
        
        # 带条件显示的参数
        self.add_parameter(Parameter(
            name="padding",
            label="填充大小",
            param_type=ParameterType.INT,
            default_value=1,
            metadata={"hide_expression": "kernel_size == 1"}  # 当kernel_size=1时隐藏
        ))
```

### 实例参数（Instance Parameters）

用户可以右键节点添加自定义参数，这些参数：
- 只影响当前节点实例，不改变类定义
- 可以删除和修改
- 主要用于子网络参数提升和数据存储
- 保存到.pnne文件中

```python
# 实例参数添加示例
conv_node_instance = ConvNode()

# 用户右键添加实例参数（用于subnet参数传递）
conv_node_instance.add_instance_parameter(Parameter(
    name="custom_scale",
    label="自定义缩放",
    param_type=ParameterType.FLOAT,
    default_value=1.0,
    metadata={"is_instance_param": True}  # 标记为实例参数
))
```

### 参数分组与标签页

属性面板使用多标签页组织参数：

```python
class Parameter:
    def __init__(self, ...):
        ...
        self.category = "基础"  # 参数分类（决定所属标签页）
        
# 分类示例：
# - "基础" 标签页：in_channels, out_channels, kernel_size
# - "高级" 标签页：padding, stride, dilation
# - "优化" 标签页：bias, weight_init
# - "自定义" 标签页：用户添加的实例参数
```

### 条件显示/禁用表达式

参数的显示和编辑权限可以通过表达式动态控制：

```python
# 隐藏条件示例
parameter.hide_expression = "layer == 1"  # 当layer参数值为1时隐藏此参数

# 禁用条件示例
parameter.disable_expression = "mode == 'auto'"  # 当mode为'auto'时禁用编辑

# 复杂条件
parameter.hide_expression = "layer > 3 and use_bn == True"  # 支持逻辑运算
```

## 表达式引擎设计（Expression System）

### 表达式语法

表达式引擎基于Python语法，支持以下功能：

1. **参数引用函数** - 通过路径引用其他节点的参数：
   - `chf("path/to/node/param")` - 获取浮点参数（Channel Float）
   - `chs("path/to/node/param")` - 获取字符串参数（Channel String）
   - `chi("path/to/node/param")` - 获取整数参数（Channel Integer）
   - `chv("path/to/node/param")` - 获取布尔参数（Channel booleaN/Value）
   - `chv2("path/to/node/param")` - 获取Vector2参数
   - `chi2("path/to/node/param")` - 获取Int2参数
   - `chi3("path/to/node/param")` - 获取Int3参数

2. **Pack数据引用**：
   - `pack_shape("path/to/node", "output_pin")` - 获取某节点某Pin的Pack形状
   - `pack_value("path/to/node", "output_pin", index)` - 获取Pack中某个值

3. **Detail数据引用**：
   - Detail数据是节点内部存储的元数据（float、int、string、list）
   - `detail("path/to/node", "detail_key")` - 获取节点的detail数据

### Subnet参数提升机制

子网络内部节点的参数可以通过表达式提升到Subnet节点上：

```python
# Subnet内部结构
Subnet "MyConvBlock":
  ├─ Conv2D (path: /subnet/conv1)
  │   ├─ in_channels = chf("../layer_num")  # 引用父级Subnet的layer_num参数
  │   └─ out_channels = 64
  ├─ ReLU (path: /subnet/relu)
  └─ Conv2D (path: /subnet/conv2)
      ├─ in_channels = chi("../layer_num") * 2  # 表达式计算
      └─ out_channels = 128

# Subnet节点参数定义
Subnet节点参数：
  - layer_num: INT = 32  # 被内部节点引用
  - 参数变更通知机制：
      当layer_num改变时 → 通知/subnet/conv1和/subnet/conv2重新求值参数
```

### 路径语法

```text
绝对路径: "/obj/model/conv1/in_channels"  # 从根节点开始
相对路径: "../layer_num"                 # 相对于当前节点的父级
         "./sibling_node/param"          # 相对于当前节点的同级
         "../../parent_subnet/param"     # 向上两级
```

### 表达式求值流程

```python
# core/expressions/evaluator.py
class ExpressionEvaluator:
    def __init__(self, node_graph: NodeGraph):
        self.graph = node_graph
        self.context = {}  # 表达式上下文（变量存储）
        
    def evaluate(self, expression: str, current_node_path: str):
        """
        求值表达式，支持：
        1. Python基本运算：+、-、*、/、**、%
        2. 逻辑运算：==、!=、<、>、<=、>=、and、or、not
        3. 条件表达式：a if condition else b
        4. 函数调用：chf()、chs()、chi()等
        """
        # 构建安全的执行上下文
        safe_context = {
            # 参数引用函数
            "chf": lambda path: self.get_float_param(path, current_node_path),
            "chs": lambda path: self.get_string_param(path, current_node_path),
            "chi": lambda path: self.get_int_param(path, current_node_path),
            "chv": lambda path: self.get_bool_param(path, current_node_path),
            "chv2": lambda path: self.get_vector2_param(path, current_node_path),
            "chi2": lambda path: self.get_int2_param(path, current_node_path),
            "chi3": lambda path: self.get_int3_param(path, current_node_path),
            
            # Pack数据引用
            "pack_shape": lambda node_path, pin: self.get_pack_shape(node_path, pin),
            "pack_value": lambda node_path, pin, idx: self.get_pack_value(node_path, pin, idx),
            
            # Detail数据引用
            "detail": lambda node_path, key: self.get_node_detail(node_path, key),
            
            # Python内置函数（受限）
            "abs": abs, "min": min, "max": max, "round": round,
            "len": len, "sum": sum,
        }
        
        # 安全求值（使用eval，但限制命名空间）
        try:
            result = eval(expression, {"__builtins__": {}}, safe_context)
            return result
        except Exception as e:
            raise ExpressionError(f"表达式求值失败: {expression}, 错误: {str(e)}")
    
    def get_float_param(self, path: str, current_path: str) -> float:
        """解析路径并获取浮点参数值"""
        abs_path = self.resolve_path(path, current_path)
        node = self.graph.get_node_by_path(abs_path)
        param_name = abs_path.split("/")[-1]
        return float(node.get_parameter(param_name).value)
    
    def resolve_path(self, path: str, current_path: str) -> str:
        """解析相对路径为绝对路径"""
        if path.startswith("/"):
            return path  # 绝对路径
        elif path.startswith("../"):
            # 相对路径：向上一级
            parts = current_path.split("/")[:-1]  # 去掉当前节点名
            rel_parts = path.split("/")
            for part in rel_parts:
                if part == "..":
                    parts.pop()  # 向上一级
                elif part != ".":
                    parts.append(part)
            return "/".join(parts)
        else:
            # 相对路径：同级或子级
            base = "/".join(current_path.split("/")[:-1])
            return f"{base}/{path}"
```

### 参数变更通知机制

当Subnet参数改变时，需要通知内部引用了该参数的子节点：

```python
class SubnetNode(Node):
    def __init__(self):
        super().__init__()
        self.param_dependency_map = {}  # {param_name: [dependent_node_paths]}
        
    def set_parameter_value(self, param_name: str, value):
        """设置参数值并通知依赖节点"""
        old_value = self.get_parameter(param_name).value
        self.get_parameter(param_name).value = value
        
        # 通知依赖此参数的内部节点
        if param_name in self.param_dependency_map:
            for dependent_path in self.param_dependency_map[param_name]:
                dependent_node = self.graph.get_node_by_path(dependent_path)
                dependent_node.on_parent_param_changed(param_name, value)
                
    def register_param_dependency(self, param_name: str, dependent_node_path: str):
        """注册参数依赖关系"""
        if param_name not in self.param_dependency_map:
            self.param_dependency_map[param_name] = []
        self.param_dependency_map[param_name].append(dependent_node_path)
```

### 参数表达式示例

#### 示例1：子网络参数传递
```python
# Subnet节点定义
subnet = SubnetNode("MyResBlock")
subnet.add_parameter("num_layers", ParameterType.INT, 3)  # Subnet参数
subnet.add_parameter("hidden_dim", ParameterType.INT, 256)

# 内部节点使用表达式引用Subnet参数
internal_conv = ConvNode()
internal_conv.path = "/subnet/layer_1/conv"
internal_conv.set_parameter_expression(
    "out_channels",
    "chi('../hidden_dim')"  # 引用父级Subnet的hidden_dim参数
)

# 当用户修改subnet.hidden_dim = 512时
# → 自动触发internal_conv重新求值out_channels = 512
```

#### 示例2：条件显示
```python
# Conv节点参数
conv_node.add_parameter("use_bias", ParameterType.BOOL, True)
conv_node.add_parameter("bias_initializer", ParameterType.ENUM, "zeros")

# bias_initializer仅当use_bias=True时显示
conv_node.get_parameter("bias_initializer").hide_expression = "use_bias == False"
```

#### 示例3：参数联动
```python
# 优化器节点
optimizer_node.add_parameter("learning_rate", ParameterType.FLOAT, 0.001)
optimizer_node.add_parameter("use_scheduler", ParameterType.BOOL, False)
optimizer_node.add_parameter("scheduler_gamma", ParameterType.FLOAT, 0.95)

# scheduler_gamma仅当use_scheduler=True时可编辑
optimizer_node.get_parameter("scheduler_gamma").disable_expression = "use_scheduler == False"
```

### 属性面板详细设计（Phase 3改进）

#### 面板定位与行为规范

**面板类型**：非停靠窗口，重叠式面板（类似Houdini Parameter Editor）

**定位规则**：
```python
# ui/panels/properties_panel.py 设计规范
class PropertiesPanel(QWidget):
    """
    属性面板 - 重叠在节点面板之上的浮动面板
    
    定位规范:
    1. 右上角与节点面板（node_palette_panel）右上角对齐重合
    2. 覆盖在节点面板之上（更高的Z-order）
    3. 调整大小：仅允许拖拽左下角（保持右上角固定）
    4. 焦点行为：鼠标在节点面板区域时，P键总是能开关属性面板
    5. 默认隐藏，按P键显示/隐藏
    """
    def __init__(self, parent_window):
        super().__init__(parent_window, Qt.WindowType.Tool | Qt.WindowType.FramelessWindowHint)
        
        # 窗口设置
        self.setWindowTitle("属性")
        self.setMinimumSize(300, 400)
        self.resize(350, 600)
        
        # 安装事件过滤器（全局监听P键）
        parent_window.installEventFilter(self)
        
        # 保存父窗口和节点面板引用
        self.parent_window = parent_window
        self.node_palette_panel = None  # 将在_position_panel()中查找
    
    def position_to_node_palette(self):
        """定位到节点面板右上角"""
        if not self.node_palette_panel:
            # 查找节点面板
            for dock in self.parent_window.findChildren(QDockWidget):
                widget = dock.widget()
                if widget and isinstance(widget, NodePalettePanel):
                    self.node_palette_panel = widget
                    self.node_palette_dock = dock
                    break
        
        if self.node_palette_panel:
            # 获取停靠窗口的全局坐标
            dock_geometry = self.node_palette_dock.geometry()
            dock_global_pos = self.parent_window.mapToGlobal(dock_geometry.topRight())
            
            # 计算属性面板位置（右上角对齐）
            panel_width = self.width()
            target_x = dock_global_pos.x() - panel_width
            target_y = dock_global_pos.y()
            
            self.move(target_x, target_y)
    
    def eventFilter(self, obj, event):
        """全局事件过滤器 - 监听P键"""
        if event.type() == QEvent.Type.KeyPress:
            if event.key() == Qt.Key.Key_P:
                # 检查鼠标是否在节点面板区域或属性面板自身
                cursor_pos = QCursor.pos()
                in_node_palette = self.is_cursor_in_node_palette(cursor_pos)
                in_properties = self.geometry().contains(self.mapFromGlobal(cursor_pos))
                
                if in_node_palette or in_properties or self.isVisible():
                    self.toggle_visibility()
                    return True
        
        return super().eventFilter(obj, event)
    
    def toggle_visibility(self):
        """切换显示/隐藏"""
        if self.isVisible():
            self.hide()
        else:
            self.position_to_node_palette()  # 重新定位
            self.show()
            self.raise_()  # 提到最前面
            self.activateWindow()
```

#### 参数编辑面板设计（Phase 10扩展）

**右上角设置按钮**：
```python
# ui/panels/properties_panel.py
def _create_header(self):
    """创建面板标题栏"""
    header = QWidget()
    header_layout = QHBoxLayout()
    
    title_label = QLabel("属性")
    title_label.setStyleSheet("font-weight: bold; font-size: 12pt;")
    header_layout.addWidget(title_label)
    
    header_layout.addStretch()
    
    # 设置齿轮按钮（打开参数编辑面板）
    settings_btn = QPushButton("⚙")
    settings_btn.setToolTip("编辑参数定义")
    settings_btn.setFixedSize(24, 24)
    settings_btn.clicked.connect(self._open_parameter_editor)
    header_layout.addWidget(settings_btn)
    
    header.setLayout(header_layout)
    return header

def _open_parameter_editor(self):
    """打开参数编辑面板"""
    from ui.dialogs.parameter_editor_dialog import ParameterEditorDialog
    
    if self.current_node:
        dialog = ParameterEditorDialog(self.current_node, self)
        dialog.exec()
```

#### 参数编辑器对话框设计（三栏布局）

```python
# ui/dialogs/parameter_editor_dialog.py
class ParameterEditorDialog(QDialog):
    """
    参数编辑器对话框 - 对当前节点的参数进行增删改查
    
    布局：左中右三栏
    - 左栏：可用参数类型列表
    - 中栏：当前节点参数列表（仅显示动态参数，可增删改、拖拽排序、文件夹组织）
    - 右栏：选中参数的详细属性编辑
    """
    
    def __init__(self, node, parent=None):
        super().__init__(parent)
        self.node = node
        self.setWindowTitle(f"参数编辑器 - {node.name}")
        self.setMinimumSize(900, 600)
        
        # 创建三栏布局
        main_layout = QHBoxLayout()
        
        # 左栏：参数类型库
        self.type_list = self._create_type_list()
        main_layout.addWidget(self.type_list, 1)
        
        # 中栏：参数列表
        self.param_list = self._create_param_list()
        main_layout.addWidget(self.param_list, 2)
        
        # 右栏：参数属性
        self.param_detail = self._create_param_detail()
        main_layout.addWidget(self.param_detail, 2)
        
        self.setLayout(main_layout)
    
    def _create_type_list(self) -> QWidget:
        """
        创建左栏：可用参数类型列表
        
        支持的类型:
        - INT（整数）
        - FLOAT（浮点数）
        - STRING（字符串）
        - BOOL（复选框）
        - BUTTON（按钮）
        - PATH（文件/文件夹路径）
        - COLOR（颜色选择器）
        - VECTOR2（二维向量）
        - VECTOR3（三维向量）
        - ENUM（下拉选择）
        - FLOAT_RAMP（浮点曲线）
        - FOLDER（参数分组文件夹）
        """
        widget = QWidget()
        layout = QVBoxLayout()
        
        title = QLabel("参数类型")
        title.setStyleSheet("font-weight: bold;")
        layout.addWidget(title)
        
        # 参数类型列表（支持拖拽）
        type_list = QListWidget()
        type_list.setDragEnabled(True)
        
        # 添加参数类型
        param_types = [
            ("INT", "整数"),
            ("FLOAT", "浮点数"),
            ("STRING", "字符串"),
            ("BOOL", "复选框"),
            ("BUTTON", "按钮"),
            ("PATH", "文件路径"),
            ("COLOR", "颜色"),
            ("VECTOR2", "向量2D"),
            ("VECTOR3", "向量3D"),
            ("ENUM", "下拉选择"),
            ("FLOAT_RAMP", "浮点曲线"),
            ("---", "分隔符"),
            ("FOLDER_TAB", "文件夹(Tab)"),
            ("FOLDER_EXPAND", "文件夹(展开)"),
        ]
        
        for type_id, display_name in param_types:
            item = QListWidgetItem(display_name)
            item.setData(Qt.ItemDataRole.UserRole, type_id)
            type_list.addItem(item)
        
        layout.addWidget(type_list)
        widget.setLayout(layout)
        return widget
    
    def _create_param_list(self) -> QWidget:
        """
        创建中栏：当前节点参数列表
        
        规则:
        1. 固定参数（代码定义）不显示，无法修改
        2. 仅显示动态参数（用户添加的实例参数）
        3. 支持拖拽左栏类型添加新参数
        4. 支持拖拽排序参数顺序
        5. 支持多选删除（Delete键）
        6. 支持文件夹组织（拖入/拖出文件夹）
        7. 文件夹类型：Tab布局（左右标签页）、Expand布局（上下展开）
        8. 文件夹可嵌套，参数不能嵌套
        """
        widget = QWidget()
        layout = QVBoxLayout()
        
        title = QLabel("动态参数")
        title.setStyleSheet("font-weight: bold;")
        layout.addWidget(title)
        
        # 参数树（支持拖放、多选、文件夹）
        param_tree = QTreeWidget()
        param_tree.setHeaderHidden(True)
        param_tree.setDragEnabled(True)
        param_tree.setAcceptDrops(True)
        param_tree.setDropIndicatorShown(True)
        param_tree.setSelectionMode(QTreeWidget.SelectionMode.ExtendedSelection)
        param_tree.setDragDropMode(QTreeWidget.DragDropMode.InternalMove)
        
        # 填充动态参数
        self._populate_dynamic_params(param_tree)
        
        # 连接信号
        param_tree.itemSelectionChanged.connect(self._on_param_selection_changed)
        param_tree.itemChanged.connect(self._on_param_item_changed)
        
        layout.addWidget(param_tree)
        
        # 操作按钮
        button_layout = QHBoxLayout()
        
        add_folder_btn = QPushButton("+ 文件夹")
        add_folder_btn.clicked.connect(self._add_folder)
        button_layout.addWidget(add_folder_btn)
        
        delete_btn = QPushButton("删除选中")
        delete_btn.clicked.connect(self._delete_selected)
        button_layout.addWidget(delete_btn)
        
        layout.addLayout(button_layout)
        
        widget.setLayout(layout)
        self.param_tree = param_tree
        return widget
    
    def _create_param_detail(self) -> QWidget:
        """
        创建右栏：参数详细属性编辑
        
        可编辑属性:
        - name: 参数名称（唯一标识）
        - label: 显示标签
        - type: 参数类型（不可改）
        - default_value: 默认值
        - help: 帮助文本
        - hide_expression: 隐藏条件表达式
        - disable_expression: 禁用条件表达式
        - metadata: 类型特定元数据
          - 对于STRING: rows（文本框高度）
          - 对于INT/FLOAT: min, max, step
          - 对于ENUM: options（选项列表）
          - 对于FOLDER: folder_type（tab/expand）
        
        注意:
        - 多选时只显示第一个参数的属性
        - 修改只应用到第一个参数
        """
        widget = QWidget()
        layout = QFormLayout()
        
        title = QLabel("参数属性")
        title.setStyleSheet("font-weight: bold;")
        layout.addRow(title)
        
        layout.addRow("", QLabel(""))  # 空行
        
        # 基础属性
        self.name_edit = QLineEdit()
        layout.addRow("名称:", self.name_edit)
        
        self.label_edit = QLineEdit()
        layout.addRow("标签:", self.label_edit)
        
        self.type_label = QLabel("")
        layout.addRow("类型:", self.type_label)
        
        self.default_edit = QLineEdit()
        layout.addRow("默认值:", self.default_edit)
        
        self.help_edit = QTextEdit()
        self.help_edit.setMaximumHeight(60)
        layout.addRow("帮助:", self.help_edit)
        
        layout.addRow("", QLabel(""))  # 空行
        layout.addRow("", QLabel("条件控制"))
        
        # 条件表达式
        self.hide_expr_edit = QLineEdit()
        self.hide_expr_edit.setPlaceholderText("例如: layer == 1")
        layout.addRow("隐藏条件:", self.hide_expr_edit)
        
        self.disable_expr_edit = QLineEdit()
        self.disable_expr_edit.setPlaceholderText("例如: mode == 'auto'")
        layout.addRow("禁用条件:", self.disable_expr_edit)
        
        layout.addRow("", QLabel(""))  # 空行
        layout.addRow("", QLabel("类型特定"))
        
        # 类型特定元数据（动态显示）
        self.metadata_widget = QWidget()
        self.metadata_layout = QFormLayout()
        self.metadata_widget.setLayout(self.metadata_layout)
        layout.addRow(self.metadata_widget)
        
        layout.addStretch()
        
        widget.setLayout(layout)
        return widget
    
    def _populate_dynamic_params(self, tree: QTreeWidget):
        """填充动态参数列表（不显示固定参数）"""
        tree.clear()
        
        # 遍历节点的所有参数
        for param_name, param in self.node.parameters.items():
            # 跳过固定参数（代码定义的参数）
            if param.is_code_defined and not param.is_instance_param:
                continue
            
            # 创建参数项
            param_item = QTreeWidgetItem([param.label])
            param_item.setData(0, Qt.ItemDataRole.UserRole, param)
            
            # 如果是文件夹，递归添加子参数
            if param.type == ParameterType.FOLDER:
                self._add_folder_children(param_item, param)
            
            tree.addTopLevelItem(param_item)
    
    def _add_folder_children(self, parent_item: QTreeWidgetItem, folder_param):
        """添加文件夹子参数"""
        children = folder_param.metadata.get("children", [])
        for child_param in children:
            child_item = QTreeWidgetItem([child_param.label])
            child_item.setData(0, Qt.ItemDataRole.UserRole, child_param)
            
            # 递归处理子文件夹
            if child_param.type == ParameterType.FOLDER:
                self._add_folder_children(child_item, child_param)
            
            parent_item.addChild(child_item)
```

#### 参数类型系统扩展

```python
# core/base/parameter.py 扩展
class ParameterType(Enum):
    # 基础类型
    FLOAT = "float"
    INT = "int"
    BOOL = "checkbox"
    STRING = "string"
    
    # 高级类型
    PATH = "path"
    FLOAT_RAMP = "float_ramp"
    VECTOR2 = "vector2"
    VECTOR3 = "vector3"
    INT2 = "int2"
    INT3 = "int3"
    BUTTON = "button"
    COLOR = "color"
    ENUM = "enum"
    
    # 组织类型（新增）
    FOLDER_TAB = "folder_tab"      # 文件夹：左右Tab标签页布局
    FOLDER_EXPAND = "folder_expand" # 文件夹：上下全展开布局
    SEPARATOR = "separator"          # 分隔符

class Parameter:
    def __init__(self, name: str, label: str, param_type: ParameterType,
                 default_value, metadata: dict = None):
        self.name = name
        self.label = label
        self.type = param_type
        self.value = default_value
        self.metadata = metadata or {}
        
        # 条件控制
        self.hide_expression = ""
        self.disable_expression = ""
        
        # 参数来源标记
        self.is_code_defined = True      # 代码定义（不可删除，不在编辑器显示）
        self.is_instance_param = False   # 实例参数（可删除，在编辑器显示）
        
        # 文件夹特定（仅当type为FOLDER时有效）
        if param_type in (ParameterType.FOLDER_TAB, ParameterType.FOLDER_EXPAND):
            self.metadata.setdefault("children", [])  # 子参数列表
            self.metadata.setdefault("folder_type", param_type.value)
        
        # STRING特定
        if param_type == ParameterType.STRING:
            self.metadata.setdefault("rows", 1)  # 文本框行数（默认单行）
        
        # INT/FLOAT特定
        if param_type in (ParameterType.INT, ParameterType.FLOAT):
            self.metadata.setdefault("min", None)
            self.metadata.setdefault("max", None)
            self.metadata.setdefault("step", None)
        
        # ENUM特定
        if param_type == ParameterType.ENUM:
            self.metadata.setdefault("options", [])
```

#### 参数序列化完整支持

```python
# core/serialization/serializer.py 扩展
def serialize_parameter(param: Parameter) -> dict:
    """
    序列化参数（完整类型支持）
    
    返回:
    {
        "name": "learning_rate",
        "label": "学习率",
        "type": "float",
        "value": 0.001,
        "default_value": 0.001,
        "is_code_defined": False,
        "is_instance_param": True,
        "hide_expression": "",
        "disable_expression": "",
        "metadata": {
            "min": 0.0,
            "max": 1.0,
            "step": 0.0001
        }
    }
    """
    return {
        "name": param.name,
        "label": param.label,
        "type": param.type.value,
        "value": param.value,
        "default_value": param.default_value,
        "is_code_defined": param.is_code_defined,
        "is_instance_param": param.is_instance_param,
        "hide_expression": param.hide_expression,
        "disable_expression": param.disable_expression,
        "metadata": param.metadata  # 包含类型特定信息
    }

def deserialize_parameter(param_data: dict) -> Parameter:
    """从字典恢复参数（完整类型支持）"""
    param_type = ParameterType(param_data["type"])
    
    param = Parameter(
        name=param_data["name"],
        label=param_data["label"],
        param_type=param_type,
        default_value=param_data.get("default_value"),
        metadata=param_data.get("metadata", {})
    )
    
    param.value = param_data.get("value", param_data.get("default_value"))
    param.is_code_defined = param_data.get("is_code_defined", True)
    param.is_instance_param = param_data.get("is_instance_param", False)
    param.hide_expression = param_data.get("hide_expression", "")
    param.disable_expression = param_data.get("disable_expression", "")
    
    return param
```

#### 属性面板UI结构（原方案保留）

```python
# ui/panels/properties_panel.py - 主面板内容区域
class PropertiesPanel(QWidget):
    def __init__(self):
        self.tab_widget = QTabWidget()  # 多标签页
        self.param_widgets = {}  # {param_name: widget}
        
    def show_node_properties(self, node: Node):
        """显示节点属性，按分类组织到标签页"""
        self.tab_widget.clear()
        
        # 按分类组织参数（包括固定参数和动态参数）
        params_by_category = self.group_parameters_by_category(node.parameters)
        
        for category, params in params_by_category.items():
            tab_content = QWidget()
            layout = QFormLayout()
            
            for param in params:
                # 根据参数类型创建对应控件
                widget = self.create_parameter_widget(param)
                
                # 评估隐藏/禁用表达式
                if param.hide_expression:
                    is_hidden = self.evaluate_expression(param.hide_expression, node)
                    widget.setVisible(not is_hidden)
                    
                if param.disable_expression:
                    is_disabled = self.evaluate_expression(param.disable_expression, node)
                    widget.setEnabled(not is_disabled)
                
                # 添加到布局
                layout.addRow(param.label + ":", widget)
                self.param_widgets[param.name] = widget
            
            tab_content.setLayout(layout)
            self.tab_widget.addTab(tab_content, category)
    
    def create_parameter_widget(self, param: Parameter) -> QWidget:
        """根据参数类型创建对应控件"""
        if param.type == ParameterType.FLOAT:
            return QDoubleSpinBox()
        elif param.type == ParameterType.INT:
            return QSpinBox()
        elif param.type == ParameterType.BOOL:
            return QCheckBox()
        elif param.type == ParameterType.STRING:
            # 支持多行文本框
            rows = param.metadata.get("rows", 1)
            if rows > 1:
                text_edit = QTextEdit()
                text_edit.setMaximumHeight(rows * 20)
                return text_edit
            else:
                return QLineEdit()
        elif param.type == ParameterType.PATH:
            return PathEdit()  # 自定义控件：文本框 + 浏览按钮
        elif param.type == ParameterType.COLOR:
            return ColorPicker()  # 自定义颜色选择器
        elif param.type == ParameterType.VECTOR2:
            return Vector2Widget()  # (x, y) 双浮点输入
        elif param.type == ParameterType.VECTOR3:
            return Vector3Widget()  # (x, y, z) 三浮点输入
        elif param.type == ParameterType.FLOAT_RAMP:
            return RampWidget()  # 曲线编辑器
        elif param.type == ParameterType.BUTTON:
            return QPushButton(param.label)
        elif param.type == ParameterType.ENUM:
            combo = QComboBox()
            combo.addItems(param.metadata.get("options", []))
            return combo
        elif param.type in (ParameterType.FOLDER_TAB, ParameterType.FOLDER_EXPAND):
            # 文件夹类型：创建容器控件
            if param.type == ParameterType.FOLDER_TAB:
                return QTabWidget()  # Tab布局
            else:
                return QGroupBox(param.label)  # 展开布局
```

### 表达式求值上下文

```python
# 求值上下文示例
# 假设当前节点路径：/subnet/layer_1/conv
# Subnet参数：layer_num = 32

# 表达式: "chi('../layer_num') * 2"
# 求值过程:
# 1. 解析路径 "../layer_num" → "/subnet/layer_num"
# 2. 获取节点 /subnet (SubnetNode)
# 3. 获取参数值 layer_num = 32
# 4. 计算表达式 32 * 2 = 64
# 结果: 64
```

### 实时编译开关

用户界面右下角提供实时编译开关：

```python
# ui/main_window.py
class MainWindow(QMainWindow):
    def __init__(self):
        # 右下角状态栏
        self.status_bar = self.statusBar()
        
        # 实时编译开关
        self.compile_switch = QCheckBox("实时编译")
        self.compile_switch.setChecked(False)  # 默认关闭
        self.compile_switch.stateChanged.connect(self.on_compile_switch_changed)
        self.status_bar.addPermanentWidget(self.compile_switch)
    
    def on_compile_switch_changed(self, state):
        """实时编译开关状态改变"""
        if state == Qt.Checked:
            # 启用实时编译：节点图变更时自动编译为PyTorch代码
            self.enable_realtime_compilation()
        else:
            # 禁用实时编译：仅在执行/训练时编译
            self.disable_realtime_compilation()
```

## Complexity Tracking

**无宪法违规需要辩护**

本计划严格遵守PytorchNode宪法的所有原则：
- ✅ 代码质量：类型注解、PEP8、模块化设计
- ✅ 测试驱动：TDD流程、覆盖率要求、测试分层
- ✅ UX一致性：主题系统、撤销重做、快捷键、国际化
- ✅ 性能标准：渲染性能、GPU优先、内存管理、启动优化
- ✅ 架构清晰：分层架构、信号总线、插件独立、序列化标准

所有技术选型和架构决策都符合宪法约束，无需例外审批。

## Phase 0 Deliverables (Planned)

本阶段将研究和确认技术细节，输出以下文档：

1. **research.md**: 
   - PyQt6 Graphics View最佳实践
   - NetworkX拓扑排序性能分析
   - PyTorch 2.0 torch.compile使用指南
   - 插件沙箱隔离方案（RestrictedPython vs subprocess）
   - 实时可视化性能优化（PyQtGraph vs Matplotlib）

2. **技术风险评估**:
   - ForEach循环嵌套深度限制
   - 大规模图（1000+节点）性能瓶颈
   - PyQt6线程模型与PyTorch GPU计算协调
   - 跨平台兼容性（Windows/Linux/macOS差异）

## Phase 1 Deliverables (Planned)

1. **data-model.md**: 定义核心数据结构
   - Node、Pin、Connection、NodeGraph类设计
   - ForEachGroup、SubnetworkNode结构
   - 序列化格式规范（.pnne JSON schema）

2. **contracts/**: 定义接口契约
   - `node_interface.md`: Node基类接口（execute、validate等）
   - `pin_interface.md`: Pin接口（类型系统、连接规则）
   - `plugin_interface.md`: 插件接口（IPlugin、register_nodes等）

3. **quickstart.md**: 开发快速开始指南
   - 环境搭建（Python 3.10+、依赖安装）
   - 运行示例（simple_mlp、mnist_classifier）
   - 插件开发示例

## Next Steps

1. ✅ **已完成**: 规范澄清 (`/speckit.clarify`)
2. ✅ **已完成**: 技术计划 (`/speckit.plan`) ← 当前阶段
3. **下一步**: 任务分解 (`/speckit.tasks`)
   - 将6个用户故事分解为可执行任务
   - 按优先级组织（P1→P2→P3→P4→P5→P6）
   - 标记可并行任务
   - 定义测试策略（TDD）

4. **后续**: 实施阶段
   - Phase 0: 研究和技术验证（research.md）
   - Phase 1: 数据模型和接口设计（data-model.md, contracts/）
   - Phase 2: 核心开发（按tasks.md执行）
   - Phase 3: UI开发和集成
   - Phase 4: 测试和优化
   - Phase 5: 文档和发布

---

**计划版本**: 1.0.0  
**创建日期**: 2026-02-15  
**宪法版本**: 1.0.0  
**审核状态**: ✅ 通过宪法检查
