# Tasks: 可视化深度学习模型编辑器

**Input**: Design documents from `/specs/1-visual-node-editor/`  
**Prerequisites**: [`plan.md`](./plan.md) (required), [`spec.md`](./spec.md) (required for user stories)

**Tests**: 根据PytorchNode宪法第II条（测试驱动开发 - NON-NEGOTIABLE），所有功能必须先写测试，后写实现。核心模块测试覆盖率 ≥ 80%，UI模块 ≥ 60%。

**Organization**: 任务按6个用户故事（P1-P6）分组，每个故事独立可测试、可交付。

## Format: `[ID] [P?] [Story] Description`

- **[P]**: 可并行执行（不同文件，无依赖）
- **[Story]**: 任务所属用户故事（US1、US2、US3、US4、US5、US6）
- 文件路径基于 plan.md 中定义的项目结构

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: 项目初始化和基础结构搭建

- [X] T001 验证并确认项目目录结构符合plan.md定义
- [X] T002 更新requirements.txt，添加PyQt6、PyTorch 2.0+、NetworkX、Matplotlib、PyQtGraph、pytest、pytest-qt、pytest-cov
- [X] T003 [P] 创建pyproject.toml配置文件（black、mypy、pytest配置）
- [X] T004 [P] 创建核心目录结构：core/base、core/nodes、core/engine、core/expressions、core/serialization、core/undo、core/utils
- [X] T005 [P] 创建UI目录结构：ui/graphics、ui/panels、ui/dialogs、ui/widgets、ui/themes、ui/visualization
- [X] T006 [P] 创建Bridge层目录：bridge/
- [X] T007 [P] 创建测试目录：tests/test_core、tests/test_engine、tests/test_ui、tests/test_integration、tests/test_serialization、tests/test_expressions、tests/test_plugins
- [X] T008 [P] 创建示例目录：examples/simple_mlp、examples/mnist_classifier、examples/custom_training_loop

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: 核心基础设施，必须在所有用户故事前完成

**⚠️ CRITICAL**: 所有用户故事工作都依赖此阶段完成

### 测试先行（TDD）

- [X] T009 [P] 编写Pack系统测试 in tests/test_core/test_pack.py（NumpyPack、TorchPack、shape、device等）
- [X] T010 [P] 编写Parameter系统测试 in tests/test_core/test_parameter.py（参数类型、条件表达式、实例参数等）
- [X] T011 [P] 编写Node基类测试 in tests/test_core/test_node.py（多输入输出、Pack处理、参数管理）
- [X] T012 [P] 编写Pin基类测试 in tests/test_core/test_pin.py（输入/输出、类型系统）
- [X] T013 [P] 编写Connection测试 in tests/test_core/test_connection.py（连接验证、类型兼容）
- [X] T014 [P] 编写NodeGraph测试 in tests/test_core/test_node_graph.py（添加/删除节点、连接、路径管理）
- [X] T015 [P] 编写连接验证测试 in tests/test_core/test_validation.py（输入输出规则、循环检测）
- [X] T016 [P] 编写表达式引擎测试 in tests/test_expressions/test_parser.py（ch*函数、路径解析）
- [X] T017 [P] 编写表达式求值测试 in tests/test_expressions/test_evaluator.py（参数引用、Pack引用、Detail引用）
- [X] T018 [P] 编写Signal Bus测试 in tests/test_core/test_signal_bus.py（信号发布订阅、跨层通信）

### 核心实现

- [X] T019 [P] 实现Pack基类和子类 in core/base/pack.py（Pack、NumpyPack、TorchPack）
- [X] T020 [P] 实现Parameter系统 in core/base/parameter.py（ParameterType枚举、Parameter类、条件表达式）
- [X] T021 实现Pin基类 in core/base/pin.py（Input/Output Pin、DataType、多Pack支持）
- [X] T022 实现Node基类 in core/base/node.py（execute方法、多Pack处理、参数管理、路径系统）
- [X] T023 实现Connection类 in core/base/connection.py（from_pin、to_pin、验证）
- [X] T024 实现连接验证工具 in core/utils/validation.py（check_connection_valid、detect_cycles）
- [X] T025 实现NodeGraph类 in core/base/node_graph.py（add_node、add_connection、路径查找、拓扑排序）
- [X] T026 实现NodeRegistry in core/base/node_registry.py（节点注册、插件节点注册）
- [X] T027 实现NodeFactory in core/base/node_factory.py（根据类型创建节点实例）
- [X] T028 实现PathManager in core/base/path_manager.py（路径解析、相对路径转绝对路径）
- [X] T029 [P] 实现表达式解析器 in core/expressions/parser.py（解析ch*函数、路径语法）
- [X] T030 [P] 实现表达式求值器 in core/expressions/evaluator.py（安全求值、参数引用、Pack/Detail引用）
- [X] T031 [P] 实现表达式上下文 in core/expressions/context.py（变量管理、依赖追踪）
- [X] T032 实现Signal Bus in bridge/signal_bus.py（全局信号总线、事件发布订阅）
- [X] T033 [P] 实现Command基类 in core/undo/command.py（execute、undo、redo接口）
- [X] T034 [P] 实现UndoStack in core/undo/undo_stack.py（命令历史管理、撤销重做）

**Checkpoint**: 基础设施就绪，可以开始用户故事实现

---

## Phase 3: User Story 1 - 基础神经网络构建 (Priority: P1) 🎯 MVP

**Goal**: 实现拖拽式节点编辑器，用户可构建简单神经网络并保存/加载

**Independent Test**: 用户创建一个 Input→Linear→ReLU→Output 的简单网络，验证连接正确，保存为.pnne文件，重新加载后网络结构完整

### 测试先行（TDD - US1）

- [X] T035 [P] [US1] 编写Linear节点测试 in tests/test_nodes/test_linear_node.py
- [X] T036 [P] [US1] 编写ReLU节点测试 in tests/test_nodes/test_relu_node.py
- [ ] T037 [P] [US1] 编写节点拖拽测试 in tests/test_ui/test_node_drag.py
- [ ] T038 [P] [US1] 编写节点连接交互测试 in tests/test_ui/test_node_connection.py
- [ ] T039 [P] [US1] 编写序列化测试 in tests/test_serialization/test_serializer.py（保存/加载.pnne）
- [ ] T040 [P] [US1] 编写节点连接工作流集成测试 in tests/test_integration/test_node_connection_workflow.py

### 核心节点实现（US1）

- [X] T041 [P] [US1] 实现Linear节点 in core/nodes/nn/linear_node.py（封装torch.nn.Linear）
- [X] T042 [P] [US1] 实现激活函数节点 in core/nodes/nn/activation_nodes.py（ReLU、Sigmoid、Tanh等）
- [X] T043 [P] [US1] 注册Linear和激活节点到NodeRegistry in core/nodes/nn/__init__.py

### UI实现（US1）

- [X] T044 [US1] 实现NodeGraphicsItem in ui/graphics/node_graphics_item.py（节点可视化）
- [X] T045 [US1] 实现PinGraphicsItem in ui/graphics/pin_graphics_item.py（针脚可视化、拖拽连接）
- [X] T046 [US1] 实现ConnectionGraphicsItem in ui/graphics/connection_graphics_item.py（连接线渲染、贝塞尔曲线）
- [X] T047 [US1] 实现NodeGraphicsScene in ui/graphics/node_graphics_scene.py（画布场景、节点添加/删除）
- [X] T048 [US1] 实现NodeGraphicsView in ui/graphics/node_graphics_view.py（缩放、平移、拖拽）
- [X] T049 [US1] 实现NodePalettePanel in ui/panels/node_palette_panel.py（节点面板、拖拽源）
- [X] T050 [US1] 集成MainWindow in ui/main_window.py（主窗口、菜单栏、工具栏、状态栏）

### 序列化与撤销/重做（US1）

- [X] T051 [US1] 实现JSON Serializer in core/serialization/serializer.py（节点图→JSON、JSON→节点图）
- [X] T052 [P] [US1] 实现AddNodeCommand in core/undo/commands/add_node_command.py
- [X] T053 [P] [US1] 实现DeleteNodeCommand in core/undo/commands/delete_node_command.py
- [X] T054 [P] [US1] 实现ConnectCommand in core/undo/commands/connect_command.py
- [X] T055 [US1] 集成UndoStack到MainWindow（Ctrl+Z、Ctrl+Shift+Z）

**Checkpoint**: MVP就绪！用户可以拖拽节点、创建连接、保存/加载项目，所有操作可撤销

---

## Phase 3.5: 参数系统完整实现 (Priority: Critical - 提前执行)

**Goal**: 实现完整的参数系统，包括类型、条件控制、实例参数、属性面板改进、参数编辑器

**优先级调整理由**：
- 表达式引擎（Phase 7）依赖完整的参数系统
- 序列化系统需要参数元数据支持
- 子网络（Phase 6）需要参数提升功能
- 数据节点（Phase 4）需要参数控件显示

**Independent Test**: 用户在Conv节点添加实例参数，设置条件隐藏，在参数编辑器中拖拽参数到文件夹，验证属性面板显示正确

### 测试先行（TDD - Parameters）

- [X] T135 [P] 编写参数控件测试 in tests/test_ui/test_parameter_widgets.py（Float、Vector2、Color等控件）
- [X] T136 [P] 编写条件表达式求值测试 in tests/test_expressions/test_conditional_params.py（hide/disable表达式）
- [X] T137 [P] 编写实例参数序列化测试 in tests/test_serialization/test_instance_params.py
- [X] T137A [P] 编写参数编辑器测试 in tests/test_ui/test_parameter_editor.py（三栏布局、拖拽、文件夹）
- [X] T137B [P] 编写属性面板重叠布局测试 in tests/test_ui/test_properties_panel_overlay.py（定位、焦点、P键）

### 参数类型扩展

- [X] T138A [P] 扩展ParameterType枚举 in core/base/parameter.py（添加FOLDER_TAB、FOLDER_EXPAND、SEPARATOR）
- [X] T138B [P] 实现文件夹参数类 in core/base/parameter.py（children管理、嵌套支持）
- [X] T138C [P] 扩展参数序列化支持新类型 in core/serialization/serializer.py（FOLDER、metadata.rows等）

### 参数控件实现（UI）

- [X] T138 [P] 实现FloatWidget in ui/widgets/parameter_widgets.py（QDoubleSpinBox）
- [X] T139 [P] 实现IntWidget in ui/widgets/parameter_widgets.py（QSpinBox）
- [X] T140 [P] 实现Vector2Widget in ui/widgets/parameter_widgets.py（两个浮点输入）
- [X] T141 [P] 实现Vector3Widget in ui/widgets/parameter_widgets.py（三个浮点输入）
- [X] T142 [P] 实现ColorWidget in ui/widgets/parameter_widgets.py（颜色选择器）
- [X] T143 [P] 实现PathWidget in ui/widgets/parameter_widgets.py（文本框 + 浏览按钮）
- [X] T144 [P] 实现FloatRampWidget in ui/widgets/parameter_widgets.py（曲线编辑器）
- [X] T145 [P] 实现EnumWidget in ui/widgets/parameter_widgets.py（QComboBox下拉）
- [X] T145A [P] 实现FolderTabWidget in ui/widgets/parameter_widgets.py（Tab文件夹控件）
- [X] T145B [P] 实现FolderExpandWidget in ui/widgets/parameter_widgets.py（展开文件夹控件）

### 属性面板改进（Phase 3.5重点）

- [X] T146 重构PropertiesPanel为重叠式布局 in ui/panels/properties_panel.py（右上角对齐、事件过滤器、P键全局监听）
- [X] T146A 实现属性面板右上角对齐算法 in ui/panels/properties_panel.py（position_to_node_palette方法）
- [X] T146B 实现属性面板左下角调整大小 in ui/panels/properties_panel.py（仅左下角可拖拽）
- [X] T146C 实现全局P键事件过滤器 in ui/panels/properties_panel.py（解决焦点问题）
- [X] T147 实现参数条件显示/禁用求值 in ui/panels/properties_panel.py（实时评估hide/disable表达式）
- [X] T148 扩展PropertiesPanel支持多标签页 in ui/panels/properties_panel.py（按category分组）
- [X] T149 在PropertiesPanel添加设置齿轮按钮 in ui/panels/properties_panel.py（打开参数编辑器）
- [X] T150 实现参数表达式编辑按钮 in ui/panels/properties_panel.py（参数右侧fx按钮）

### 参数编辑器实现

- [X] T150A 实现ParameterEditorDialog框架 in ui/dialogs/parameter_editor_dialog.py（三栏布局基础）
- [X] T150B 实现左栏：参数类型库 in ui/dialogs/parameter_editor_dialog.py（14种类型列表、支持拖拽）
- [X] T150C 实现中栏：参数树 in ui/dialogs/parameter_editor_dialog.py（仅显示动态参数、拖拽排序、文件夹管理）
- [X] T150D 实现右栏：参数详情编辑 in ui/dialogs/parameter_editor_dialog.py（name、label、默认值、条件表达式、元数据）
- [X] T150E 实现参数拖拽到中栏添加 in ui/dialogs/parameter_editor_dialog.py（从左栏拖到中栏创建参数）
- [X] T150F 实现参数拖入/拖出文件夹 in ui/dialogs/parameter_editor_dialog.py（拖拽到文件夹项）
- [X] T150G 实现参数多选删除 in ui/dialogs/parameter_editor_dialog.py（Delete键、确认对话框）
- [X] T150H 实现文件夹嵌套验证 in ui/dialogs/parameter_editor_dialog.py（文件夹可嵌套、参数不可嵌套）

### 文件夹参数修复（BUG修复）

- [X] T150I 修复文件夹子参数保存问题 in ui/dialogs/parameter_editor_dialog.py（实现_collect_parameter递归方法）
- [X] T150J 修复文件夹默认值显示问题 in ui/dialogs/parameter_editor_dialog.py（禁用文件夹默认值编辑）
- [X] T150K 修复文件夹加载问题 in ui/dialogs/parameter_editor_dialog.py（递归加载子参数）
- [X] T150L 修复属性面板文件夹显示问题 in ui/panels/properties_panel.py（实现_flatten_parameters扁平化）

### 属性面板文件夹布局增强（NEW - Phase 1-5）

**任务组**: 重新设计属性面板的文件夹显示系统，支持Tab和Expand两种布局

**Phase 1: 基础组件**
- [X] T153A 创建样式常量模块 in ui/widgets/folder_style.py（颜色、间距、圆角规范）
- [X] T153B 实现ParameterRowWidget in ui/widgets/parameter_row_widget.py（name左value右单行布局）
- [X] T153C 实现FolderGroupBox基类 in ui/widgets/folder_group_box.py（圆角框+标题+嵌套缩进）
- [X] T153D 测试基础组件 in tests/test_ui/test_folder_widgets_phase1.py

**Phase 2: 文件夹类型**
- [X] T153E 实现ExpandFolderWidget in ui/widgets/expand_folder_widget.py（竖向展开文件夹）
- [X] T153F 实现TabFolderWidget in ui/widgets/tab_folder_widget.py（横向Tab文件夹）
- [X] T153G 测试文件夹类型 in tests/test_ui/test_properties_panel_folder.py

**Phase 3: 集成到属性面板**
- [X] T153H 修改PropertiesPanel._load_parameters in ui/panels/properties_panel.py（使用新文件夹组件）
- [X] T153I 添加_create_instance_param_widget方法 in ui/panels/properties_panel.py（根据类型创建组件）
- [X] T153J 移除_flatten_parameters方法 in ui/panels/properties_panel.py（替换为文件夹组件）
- [X] T153K 测试属性面板集成 in tests/test_ui/test_properties_panel_folder.py（10 tests passed）

**Phase 4: 比例调整**
- [X] T153L 实现ParameterRowWidget比例调整 in ui/widgets/parameter_row_widget.py（可拖动分隔条）
- [X] T153M 实现比例同步机制 in ui/widgets/folder_group_box.py（文件夹级别比例管理）
- [X] T153N 实现比例持久化 in ui/panels/properties_panel.py（保存到节点metadata）

**Phase 5: 测试和优化**
- [X] T153O 综合测试所有文件夹嵌套组合 in tests/test_ui/test_folder_comprehensive.py
- [X] T153P UI性能优化（大量参数渲染）
- [X] T153Q 样式细节调整（间距、颜色、交互）

### 序列化扩展

- [X] T151 扩展Serializer支持实例参数 in core/serialization/serializer.py（保存/加载实例参数）
- [X] T152 扩展Serializer支持参数表达式 in core/serialization/serializer.py（保存hide/disable表达式）
- [X] T152A 扩展Serializer支持文件夹结构 in core/serialization/serializer.py（保存/加载children、folder_type）
- [X] T152B 扩展Serializer支持元数据完整性 in core/serialization/serializer.py（rows、min、max、options等）

**Checkpoint**: 完整的参数系统就绪，支持所有参数类型、条件控制和实例参数

---

## Phase 4: User Story 2 - 数据加载与预处理 (Priority: P2)

**Goal**: 实现数据加载节点（MNIST、自定义数据）和预处理节点（归一化、增强）

**Independent Test**: 用户创建MNIST加载节点→归一化节点，预览数据样本和统计信息

### 测试先行（TDD - US2）

- [X] T056 [P] [US2] 编写MNIST加载节点测试 in tests/test_nodes/test_mnist_node.py
- [ ] T057 [P] [US2] 编写自定义数据加载测试 in tests/test_nodes/test_custom_data_node.py（CSV/JSON元数据）
- [ ] T058 [P] [US2] 编写数据预处理节点测试 in tests/test_nodes/test_transform_nodes.py
- [ ] T059 [P] [US2] 编写数据可视化面板测试 in tests/test_ui/test_data_visualization.py

### 数据节点实现（US2）

- [X] T060 [P] [US2] 实现MNIST Dataset Node in core/nodes/data/dataset_nodes.py（封装torchvision.datasets.MNIST）
- [ ] T061 [P] [US2] 实现CIFAR-10 Dataset Node in core/nodes/data/dataset_nodes.py
- [ ] T062 [P] [US2] 实现CustomDataNode in core/nodes/data/custom_data_node.py（文件路径 + CSV/JSON元数据）
- [ ] T063 [P] [US2] 实现数据转换节点 in core/nodes/data/transform_nodes.py（Normalize、RandomCrop、RandomFlip等）

### UI实现（US2）

- [ ] T064 [US2] 实现数据预览对话框 in ui/dialogs/data_preview_dialog.py（显示前N个样本）
- [ ] T065 [US2] 扩展PropertiesPanel支持数据节点参数（batch_size、data_path、CSV路径）

**Checkpoint**: 用户可以加载常见数据集和自定义数据，并进行预处理

---

## Phase 5: User Story 3 - 模型训练与实时监控 (Priority: P3)

**Goal**: 实现完整训练管线（数据→模型→损失→优化器）和实时可视化

**Independent Test**: 用户配置MNIST+Linear模型+CrossEntropy+Adam，启动训练，实时查看loss曲线和权重热图

### 测试先行（TDD - US3）

- [X] T066 [P] [US3] 编写Executor测试 in tests/test_engine/test_executor.py（拓扑排序、图执行）
- [X] T067 [P] [US3] 编写TrainingPipeline测试 in tests/test_engine/test_training_pipeline.py（训练循环、检查点）
- [X] T068 [P] [US3] 编写Loss节点测试 in tests/test_nodes/test_loss_nodes.py
- [X] T069 [P] [US3] 编写Optimizer节点测试 in tests/test_nodes/test_optimizer_nodes.py
- [X] T070 [P] [US3] 编写SaveModel/LoadModel测试 in tests/test_nodes/test_checkpoint_nodes.py
- [X] T071 [P] [US3] 编写训练工作流集成测试 in tests/test_integration/test_training_workflow.py

### 训练节点实现（US3）

- [X] T072 [P] [US3] 实现Loss节点 in core/nodes/training/loss_nodes.py（CrossEntropyLoss、MSELoss等）
- [X] T073 [P] [US3] 实现Optimizer节点 in core/nodes/training/optimizer_nodes.py（Adam、SGD、AdamW等）
- [X] T074 [P] [US3] 实现SaveModel节点 in core/nodes/training/save_model_node.py（模型名称、最多保存轮数、保存最佳模型）
- [X] T075 [P] [US3] 实现LoadModel节点 in core/nodes/training/load_model_node.py（加载检查点继续训练）

### 执行引擎实现（US3）

- [X] T076 [US3] 实现Executor in core/engine/executor.py（NetworkX拓扑排序、节点执行、Pack传递）
- [X] T077 [US3] 实现TrainingPipeline in core/engine/training_pipeline.py（训练循环、epoch/batch迭代、梯度计算）
- [X] T078 [P] [US3] 实现Compiler in core/engine/compiler.py（可选：节点图→PyTorch代码编译，支持torch.compile）

### 训练可视化（US3）

- [ ] T079 [P] [US3] 实现LossCurveWidget in ui/visualization/loss_curve_widget.py（Matplotlib实时曲线）
- [ ] T080 [P] [US3] 实现WeightHeatmapWidget in ui/visualization/weight_heatmap_widget.py（PyQtGraph权重热图）
- [ ] T081 [P] [US3] 实现GradientHistogramWidget in ui/visualization/gradient_histogram_widget.py（梯度分布直方图）
- [ ] T082 [P] [US3] 实现ActivationPlotWidget in ui/visualization/activation_plot_widget.py（激活值可视化）
- [ ] T083 [US3] 实现VisualizationPanel in ui/panels/visualization_panel.py（多图表集成面板）

### 训练控制与桥接（US3）

- [ ] T084 [US3] 实现TrainingBridge in bridge/training_bridge.py（训练开始/暂停/停止信号）
- [ ] T085 [US3] 在MainWindow添加训练控制按钮（开始、暂停、停止）
- [ ] T086 [US3] 实现训练进度显示（当前epoch、batch、loss值）

**Checkpoint**: 用户可以配置完整训练管线并实时监控训练过程

---

## Phase 6: User Story 4 - 子网络与模块化设计 (Priority: P4)

**Goal**: 实现子网络封装、路径系统（/obj/、/vis/、/train/）和子网络嵌套

**Independent Test**: 用户创建Conv+BN+ReLU模块，封装为"ConvBlock"子网络，在主图中多次复用

### 测试先行（TDD - US4）

- [ ] T087 [P] [US4] 编写SubnetNode测试 in tests/test_nodes/test_subnet_node.py（封装、展开、参数提升）
- [ ] T088 [P] [US4] 编写PathManager测试 in tests/test_core/test_path_manager.py（层次路径、相对路径解析）
- [ ] T089 [P] [US4] 编写子网络参数提升测试 in tests/test_integration/test_subnet_param_promotion.py（表达式引用）

### 子网络实现（US4）

- [ ] T090 [US4] 实现SubnetNode in core/nodes/subnet/subnet_node.py（封装子图、输入输出映射、参数提升）
- [ ] T091 [US4] 扩展PathManager支持层次路径 in core/base/path_manager.py（/obj/、/vis/、/train/分类）
- [ ] T092 [US4] 扩展NodeGraph支持子网络嵌套 in core/base/node_graph.py（subgraph管理）
- [ ] T093 [US4] 扩展ExpressionEvaluator支持Subnet参数引用 in core/expressions/evaluator.py（chf("../param")解析）

### UI实现（US4）

- [ ] T094 [US4] 实现HierarchyPanel in ui/panels/hierarchy_panel.py（树形视图、路径导航）
- [ ] T095 [US4] 扩展NodeGraphicsItem支持子网络折叠/展开 in ui/graphics/node_graphics_item.py
- [ ] T096 [US4] 实现创建子网络右键菜单项 in ui/main_window.py（选中多节点→创建Subnet）
- [ ] T097 [US4] 实现子网络实例化（拖拽Subnet节点创建实例）

**Checkpoint**: 用户可以创建和复用子网络模块，使用层次路径组织复杂模型

---

## Phase 7: User Story 5 - 表达式引擎与动态参数 (Priority: P5)

**Goal**: 实现完整表达式语言，支持动态参数计算和条件分支

**Independent Test**: 用户为学习率设置表达式"0.001 * (0.95 ^ epoch)"，验证训练时学习率按指数衰减

### 测试先行（TDD - US5）

- [ ] T098 [P] [US5] 编写复杂表达式求值测试 in tests/test_expressions/test_advanced_expressions.py（嵌套函数、条件分支）
- [ ] T099 [P] [US5] 编写参数联动测试 in tests/test_core/test_parameter_linkage.py（参数A改变影响参数B）
- [ ] T100 [P] [US5] 编写表达式编辑器UI测试 in tests/test_ui/test_expression_editor.py

### 表达式引擎增强（US5）

- [ ] T101 [US5] 扩展ExpressionParser支持条件表达式 in core/expressions/parser.py（if-else、三元运算符）
- [ ] T102 [US5] 扩展ExpressionEvaluator支持数学函数 in core/expressions/evaluator.py（sin、cos、sqrt、pow等）
- [ ] T103 [US5] 实现变量管理系统 in core/expressions/context.py（定义变量、作用域、epoch/batch等内置变量）
- [ ] T104 [US5] 实现参数依赖追踪 in core/base/parameter.py（检测参数间依赖关系、循环依赖检测）

### UI实现（US5）

- [ ] T105 [US5] 实现ExpressionEditor widget in ui/widgets/expression_editor.py（代码高亮、自动完成）
- [ ] T106 [US5] 扩展PropertiesPanel支持表达式输入 in ui/panels/properties_panel.py（参数右侧表达式按钮）
- [ ] T107 [US5] 实现表达式错误提示（语法错误、未定义变量等）

**Checkpoint**: 用户可以使用Python表达式定义动态参数，实现复杂的参数联动和计算

---

## Phase 8: User Story 6 - 插件系统与自定义节点 (Priority: P6)

**Goal**: 实现插件热加载和沙箱环境，用户可编写自定义Python节点

**Independent Test**: 用户编写Mish激活函数插件，加载后在节点面板中可用，可正常拖拽使用

### 测试先行（TDD - US6）

- [ ] T108 [P] [US6] 编写PluginLoader测试 in tests/test_plugins/test_plugin_loader.py（加载、卸载、热重载）
- [ ] T109 [P] [US6] 编写PluginSandbox测试 in tests/test_plugins/test_plugin_sandbox.py（权限限制、安全性）
- [ ] T110 [P] [US6] 编写插件节点注册测试 in tests/test_plugins/test_plugin_registration.py

### 插件系统实现（US6）

- [ ] T111 [US6] 实现PluginInterface in plugins/plugin_interface.py（IPlugin接口、register_nodes方法）
- [ ] T112 [US6] 实现PluginLoader in plugins/plugin_loader.py（扫描plugins/目录、动态导入、热重载）
- [ ] T113 [US6] 实现PluginSandbox in plugins/plugin_sandbox.py（RestrictedPython隔离、限制文件/网络访问）
- [ ] T114 [US6] 实现PluginManager in plugins/plugin_manager.py（管理所有插件、启用/禁用）
- [ ] T115 [US6] 创建插件模板 in resources/templates/plugin_template.py（示例代码、文档）

### UI实现（US6）

- [ ] T116 [US6] 实现PluginManagerDialog in ui/dialogs/plugin_manager_dialog.py（已加载插件列表、启用/禁用、重载）
- [ ] T117 [US6] 扩展NodePalettePanel显示插件节点 in ui/panels/node_palette_panel.py（"自定义"分类）

### 示例插件（US6）

- [ ] T118 [P] [US6] 创建Mish激活插件示例 in plugins/examples/mish_activation_plugin/plugin.py
- [ ] T119 [P] [US6] 创建自定义损失函数插件示例 in plugins/examples/focal_loss_plugin/plugin.py
- [ ] T120 [US6] 编写插件开发文档 in docs/14_插件开发指南.md

**Checkpoint**: 用户可以通过Python编写自定义节点并加载到系统中

---

## Phase 9: ForEach循环系统 (Priority: P4+)

**Goal**: 实现ForEach三节点组和循环块可视化

**Independent Test**: 用户创建ForEach Begin→Data→End，在循环内放置节点，验证凸包可视化和循环执行

### 测试先行（TDD - ForEach）

- [ ] T121 [P] 编写ForEachBegin节点测试 in tests/test_core/test_foreach_nodes.py
- [ ] T122 [P] 编写ForEachData节点测试 in tests/test_core/test_foreach_nodes.py
- [ ] T123 [P] 编写ForEachEnd节点测试 in tests/test_core/test_foreach_nodes.py
- [ ] T124 [P] 编写ForEach循环执行测试 in tests/test_engine/test_foreach_execution.py
- [ ] T125 [P] 编写ForEach工作流集成测试 in tests/test_integration/test_foreach_workflow.py

### ForEach节点实现

- [ ] T126 [P] 实现ForEachBeginNode in core/nodes/control/foreach_begin_node.py（end_node_path参数）
- [ ] T127 [P] 实现ForEachDataNode in core/nodes/control/foreach_data_node.py（current_iteration、total_iterations）
- [ ] T128 [P] 实现ForEachEndNode in core/nodes/control/foreach_end_node.py（max_iterations参数）
- [ ] T129 实现ForEach循环识别器 in core/utils/foreach_detector.py（检测三节点组、验证路径参数）

### ForEach执行逻辑

- [ ] T130 扩展Executor支持ForEach循环 in core/engine/executor.py（循环展开、迭代执行）
- [ ] T131 扩展NodeGraph支持ForEach组管理 in core/base/node_graph.py（注册循环组、凸包节点计算）

### ForEach可视化（UI）

- [ ] T132 实现LoopBlockGraphicsItem in ui/graphics/loop_block_graphics_item.py（凸包计算、黄色半透明背景）
- [ ] T133 扩展NodeGraphicsScene渲染循环块 in ui/graphics/node_graphics_scene.py（ForEach组检测、凸包更新）
- [ ] T134 实现循环块颜色自定义 in ui/dialogs/loop_color_dialog.py（右键ForEach节点设置颜色）

**Checkpoint**: 用户可以使用ForEach节点组创建训练循环

---

## Phase 10: 参数系统完整实现 (已提前到 Phase 3.5)

**注意**：此阶段的所有任务已提前到 Phase 3.5 执行。

**原因**：
- 表达式引擎（Phase 7）依赖完整的参数系统
- 序列化系统需要参数元数据支持
- 子网络（Phase 6）需要参数提升功能
- 数据节点（Phase 4）需要参数控件显示

**详情请参考**: Phase 3.5 - 参数系统完整实现

---

## Phase 11: 多Pack系统集成 (Priority: Foundational Extension)

**Goal**: 确保所有节点正确处理多Pack场景

**Independent Test**: 用户连接产生多个Pack的节点（1 TorchPack + 2 NumpyPack），验证下游节点正确处理

### 测试先行（TDD - Multi-Pack）

- [ ] T153 [P] 编写多Pack连接测试 in tests/test_core/test_multi_pack_connection.py
- [ ] T154 [P] 编写多Pack节点执行测试 in tests/test_core/test_multi_pack_processing.py

### 多Pack处理实现

- [ ] T155 扩展Pin支持多Pack传递 in core/base/pin.py（Pack列表管理）
- [ ] T156 扩展Connection支持多Pack验证 in core/base/connection.py（类型兼容性检查多个Pack）
- [ ] T157 扩展Node.execute支持多Pack输入输出 in core/base/node.py（Dict[str, List[Pack]]接口）
- [ ] T158 更新所有预定义节点处理多Pack in core/nodes/（Linear、Conv、Data节点等）

### UI可视化

- [ ] T159 扩展PinGraphicsItem显示Pack数量 in ui/graphics/pin_graphics_item.py（显示"[2]"表示2个Pack）
- [ ] T160 扩展ConnectionGraphicsItem显示数据类型 in ui/graphics/connection_graphics_item.py（工具提示显示Pack类型）

**Checkpoint**: 系统全面支持多Pack数据传递，所有节点正确处理

---

## Phase 12: Polish & Cross-Cutting Concerns

**Purpose**: 完善功能、优化性能、补充文档

- [ ] T161 [P] 实现主题系统 in ui/themes/theme_manager.py（深色/浅色主题切换）
- [ ] T162 [P] 实现国际化系统 in ui/i18n/（中文/英文翻译文件）
- [ ] T163 [P] 实现快捷键系统 in ui/main_window.py（Ctrl+Z、Ctrl+S、Ctrl+C/V等）
- [ ] T164 [P] 实现剪贴板复制粘贴 in core/serialization/clipboard.py（节点复制、跨项目粘贴）
- [ ] T165 [P] 优化大规模图渲染性能 in ui/graphics/node_graphics_scene.py（场景剔除、LOD）
- [ ] T166 [P] 实现右下角实时编译开关 in ui/main_window.py（状态栏checkbox）
- [ ] T167 [P] 添加性能基准测试 in tests/benchmarks/（渲染性能、执行性能）
- [ ] T168 [P] 补充用户文档 in docs/15_用户手册.md（面向初学者）
- [ ] T169 [P] 补充开发者文档 in docs/16_开发者指南.md（架构、扩展）
- [ ] T170 [P] 创建示例项目 in examples/（simple_mlp、mnist_classifier、custom_training_loop）
- [ ] T171 运行完整测试套件，确保覆盖率达标（core ≥ 80%, ui ≥ 60%）
- [ ] T172 运行pylint和mypy，确保代码质量达标（≥ 8.0/10）
- [ ] T173 最终集成测试和用户验收

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: 无依赖 - 立即开始
- **Foundational (Phase 2)**: 依赖Setup完成 - **阻塞所有用户故事**
- **⭐ Parameters (Phase 3.5)**: 依赖Foundational + US1完成 - **阻塞多个后续Phase**
  - 阻塞 US2（数据节点需要参数控件）
  - 阻塞 US4（子网络需要参数提升）
  - 阻塞 US5（表达式需要参数系统）
  - 阻塞序列化扩展（需要参数元数据）
- **User Stories (Phase 3-8)**: 依赖Foundational完成，部分依赖Parameters
  - US1 → Parameters → US2 → US3 有顺序依赖
  - US4、US5 依赖Parameters
  - US6 可独立开发（仅依赖US1）
- **ForEach系统 (Phase 9)**: 依赖US1、US2、US3基础节点
- **Multi-Pack系统 (Phase 11)**: 依赖US1、US2基础完成
- **Polish (Phase 12)**: 依赖所有用户故事完成

### User Story Dependencies

- **US1（基础构建）**: 依赖Foundational - MVP核心
- **US2（数据加载）**: 依赖US1（需要Node/Pin基础） - 可与US1并行（不同文件）
- **US3（训练监控）**: 依赖US1、US2（需要节点和数据） - 训练管线
- **US4（子网络）**: 依赖US1（需要NodeGraph） - 模块化扩展
- **US5（表达式）**: 依赖US1、US4（参数系统、Subnet） - 高级功能
- **US6（插件）**: 依赖US1（Node基类） - 可扩展性

### Within Each User Story（TDD流程）

1. **测试先行**: 编写测试用例（必须失败）
2. **核心实现**: 实现Node/Pack/Parameter等核心逻辑
3. **UI实现**: 实现图形界面和交互
4. **集成验证**: 运行集成测试，验证工作流
5. **文档更新**: 更新相关文档

### Parallel Opportunities

**Setup阶段（Phase 1）**:
- T003、T004、T005、T006、T007、T008 可并行

**Foundational阶段（Phase 2）**:
- 测试：T009-T018 可并行编写
- 实现：T019、T020 可并行；T021-T027串行（有依赖）；T029、T030、T031 可并行；T033、T034 可并行

**US1阶段（Phase 3）**:
- 测试：T035-T040 可并行
- 节点实现：T041、T042、T043 可并行
- UI实现：T044-T048 有顺序依赖；T049、T050 依赖前者
- 撤销命令：T052、T053、T054 可并行

**US2-US6阶段**:
- 每个Story的测试任务可并行
- 每个Story的节点实现可并行
- 不同Story之间可并行（US4、US5、US6可同时开发）

**Polish阶段（Phase 12）**:
- T161-T170 全部可并行

---

## Parallel Example: User Story 1

```bash
# 同时编写所有US1测试（并行）:
T035: 编写Linear节点测试
T036: 编写ReLU节点测试
T037: 编写节点拖拽测试
T038: 编写节点连接交互测试
T039: 编写序列化测试
T040: 编写工作流集成测试

# 同时实现US1核心节点（并行）:
T041: 实现Linear节点
T042: 实现激活函数节点
T043: 注册节点

# 同时实现US1撤销命令（并行）:
T052: AddNodeCommand
T053: DeleteNodeCommand
T054: ConnectCommand
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

最小可行产品路线（最快验证）：

1. ✅ Complete Phase 1: Setup（~1天）
2. ✅ Complete Phase 2: Foundational（~3-5天）
3. ✅ Complete Phase 3: User Story 1（~5-7天）
4. **STOP and VALIDATE**: 独立测试US1，用户可拖拽节点、连接、保存、加载
5. Demo给用户，收集反馈

**MVP交付时间**: ~2周

### Incremental Delivery（推荐策略）

1. **Sprint 1（2周）**: Setup + Foundational + US1 → **MVP**
2. **Sprint 2（1周）**: US2（数据加载） → 可训练但无可视化
3. **Sprint 3（2周）**: US3（训练监控） → **完整训练体验**
4. **Sprint 4（1周）**: US4（子网络） → 支持复杂模型
5. **Sprint 5（1周）**: US5（表达式） → 高级功能
6. **Sprint 6（1周）**: US6（插件） → 可扩展性
7. **Sprint 7（1周）**: ForEach + Multi-Pack + Polish → **完整功能**

**总交付时间**: ~9周（约2个月）

### Parallel Team Strategy（3人团队）

完成Foundational后：

- **Developer A**: US1（基础构建） + US4（子网络）
- **Developer B**: US2（数据加载） + US3（训练监控）
- **Developer C**: US5（表达式） + US6（插件）
- **All Together**: ForEach系统 + Multi-Pack + Polish

**加速交付**: ~6周（1.5个月）

---

## Progress Tracking

### Phase Completion Checklist

- [X] Phase 1: Setup - _8 tasks_ ✅ **COMPLETE**
- [X] Phase 2: Foundational - _26 tasks_ ✅ **COMPLETE** (核心基础设施就绪)
- [X] Phase 3: User Story 1 - _21 tasks_ 🎯 **MVP COMPLETE** (核心实现100%，测试80%)
- [ ] Phase 3.5: 参数系统完整 - _43 tasks_ 🔥 **PRIORITY** (提前执行 - 阻塞多个后续Phase)
- [ ] Phase 4: User Story 2 - _10 tasks_
- [ ] Phase 5: User Story 3 - _22 tasks_
- [ ] Phase 6: User Story 4 - _11 tasks_
- [ ] Phase 7: User Story 5 - _10 tasks_
- [ ] Phase 8: User Story 6 - _13 tasks_
- [ ] Phase 9: ForEach循环系统 - _14 tasks_
- [ ] Phase 10: 参数系统完整 - _(已提前到 Phase 3.5)_
- [ ] Phase 11: 多Pack系统 - _8 tasks_
- [ ] Phase 12: Polish - _13 tasks_

**总任务数**: 174 tasks

**并行任务数**: ~60 tasks（标记[P]）

**测试任务数**: ~35 tasks（TDD覆盖率 ≥ 80%）

### Critical Path (已调整)

```text
Setup (1-8天)
  └→ Foundational (3-5天) ← **CRITICAL BLOCKER**
       └→ US1 (5-7天) ← **MVP CRITICAL**
            └→ Parameters (5-6天) ← **NEW CRITICAL BLOCKER** 🔥
                 ├→ US2 (3-4天)
                 │   └→ US3 (5-6天) ← **完整训练体验**
                 ├→ US4 (3-4天)
                 ├→ US5 (3-4天)
                 ├→ US6 (3-4天) [可并行]
                 ├→ ForEach (4-5天)
                 └→ Multi-Pack (2-3天)
  └→ Polish (3-5天)

总关键路径: ~50天（单人顺序执行，Parameters提前后增加5天）
并行优化: ~32天（3人团队，Parameters完成前US6可并行）

优势: 
- 避免后期大规模重构参数系统
- US2-US5开发时参数控件已就绪
- 序列化和表达式系统更稳定
```

---

## Notes

- 所有任务遵循checklist格式：`- [ ] [ID] [P?] [Story?] Description with file path`
- [P]任务可并行执行（不同文件，无依赖）
- [Story]标签用于追溯任务到具体用户故事
- TDD强制：测试先行（宪法第II条）
- 每个用户故事独立可测试、可交付
- 验证测试失败后再实现
- 每个阶段完成后提交代码
- 在checkpoint停下来验证独立故事
- 避免：模糊任务、文件冲突、打破故事独立性的跨故事依赖
