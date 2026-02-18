# Feature Specification: 可视化深度学习模型编辑器

**Feature Branch**: `1-visual-node-editor`  
**Created**: 2026-02-15  
**Status**: Draft  
**Input**: Build a visual deep learning model editor that makes model training accessible to learners, students, and enthusiasts without programming background, while also allowing data scientists to design, train, and debug PyTorch models through an intuitive node‑based interface. Users can construct neural networks by dragging and connecting nodes representing layers, data loaders, and training operations. The application should support hierarchical organization with a path system (/obj/, /vis/, /train/) and allow nesting of subnetworks. It must include real‑time visualization of weights, activations, and gradients during training. The interface should provide an expression language for dynamic parameters and a training pipeline with loop constructs. Users should be able to extend functionality with custom Python nodes and plugins.

## Clarifications

### Session 2026-02-15

- Q: 系统应支持哪些自定义数据导入方式？ → A: 支持文件系统路径 + CSV/JSON 元数据文件
- Q: 系统应如何实现训练状态的检查点和恢复？ → A: 通过 SaveModel 和 LoadModel 节点实现。SaveModel节点可配置参数：模型名称、最多保存轮数、是否保存最佳模型（默认勾选）。LoadModel节点在训练前加载检查点
- Q: 循环结构如何实现？连接验证规则是什么？ → A: 循环通过三节点组实现（ForEach Begin、ForEach Data、ForEach End），成对出现。Begin和Data节点通过路径参数指向End节点。循环块用凸包线框围起来（默认黄色背景）。连接验证规则：输出只能连接输入，输入只能连接输入，连接时实时验证。可选实时编译开关（右下角总开关）
- Q: 节点间数据传递如何设计？ → A: 采用Pack系统，分为NumpyPack（元数据、字符串、标签）和TorchPack（PyTorch张量）。一个节点可同时输入/输出多个Pack（通常1个TorchPack + 多个NumpyPack）。节点算法对多个Pack分别应用处理
- Q: 参数系统如何设计？ → A: 支持10+种参数类型（float、int、checkbox、string、path、vector2/3、color等）。参数分name（唯一标识）和label（显示标签）。支持代码定义参数（不可删除）和实例参数（用户可添加删除）。参数面板按分类组织成多标签页。支持条件显示/禁用表达式（如"layer == 1"）
- Q: Subnet参数如何与内部节点关联？ → A: 内部节点参数使用表达式引用父级Subnet参数（如"chf('../layer_num')"）。Subnet维护参数依赖映射，参数变更时自动通知依赖节点重新求值。表达式引擎提供chf、chs、chi、chv、chv2/chi2/chi3函数获取不同类型参数值

## User Scenarios & Testing *(mandatory)*

### User Story 1 - 基础神经网络构建 (Priority: P1)

**目标用户**: 初学者、学生，无编程背景的用户

用户可以通过拖拽节点的方式构建简单的神经网络模型（如多层感知器），将输入层、隐藏层、激活函数和输出层连接起来，并可视化查看网络结构。

**Why this priority**: 这是系统的核心功能，是MVP的基础。没有这个功能，其他所有功能都无法使用。它为非编程用户提供了最基本的模型构建能力。

**Independent Test**: 用户可以创建一个包含输入层、一个隐藏层（带ReLU激活）和输出层的简单网络，通过可视化界面验证连接是否正确，并能保存/加载该网络结构。

**Acceptance Scenarios**:

1. **Given** 用户打开空白画布，**When** 从节点面板拖拽"Linear层"、"ReLU激活"、"输出层"到画布并连接，**Then** 系统显示正确的网络拓扑图，所有连接有效
2. **Given** 用户创建了一个简单网络，**When** 点击保存按钮，**Then** 系统将网络结构序列化为.pnne文件
3. **Given** 用户保存了网络文件，**When** 重新打开应用并加载该文件，**Then** 网络结构完整恢复到画布上

---

### User Story 2 - 数据加载与预处理 (Priority: P2)

**目标用户**: 学生、数据科学家

用户可以通过数据加载节点导入常见数据集（MNIST、CIFAR-10等）或自定义数据（通过文件系统路径指定数据文件夹，配合CSV/JSON元数据文件描述数据结构），并通过预处理节点进行数据归一化、增强等操作。

**Why this priority**: 有了网络结构后，需要数据才能训练模型。这是从静态模型到可训练模型的关键一步。

**Independent Test**: 用户创建数据加载节点（MNIST），连接到数据预处理节点（归一化），验证数据流通过可视化工具查看数据样本和统计信息。

**Acceptance Scenarios**:

1. **Given** 用户在画布上放置MNIST数据加载节点，**When** 配置batch size和数据路径，**Then** 节点显示数据集信息（样本数、形状、类别数）
2. **Given** 用户放置自定义数据加载节点，**When** 指定图像文件夹路径和CSV标签文件（格式：filename, label），**Then** 系统加载自定义数据集并显示数据集信息
3. **Given** 数据加载节点已配置，**When** 连接到归一化预处理节点，**Then** 系统验证数据维度兼容性，提示任何不匹配
4. **Given** 数据管道配置完成，**When** 点击"预览数据"按钮，**Then** 在可视化面板显示前10个样本及其标签

---

### User Story 3 - 模型训练与实时监控 (Priority: P3)

**目标用户**: 数据科学家、研究人员

用户可以配置训练参数（学习率、优化器、损失函数），启动训练过程，并实时查看训练损失、准确率、权重分布、梯度流动等可视化指标。

**Why this priority**: 这是从静态模型到动态训练的核心功能，让用户能够实际使用深度学习模型，并理解训练过程。

**Independent Test**: 用户连接完整的训练管线（数据→模型→损失→优化器），点击"开始训练"，在可视化面板实时查看loss曲线、权重热图、梯度直方图。

**Acceptance Scenarios**:

1. **Given** 用户配置了完整的训练管线（包含数据、模型、损失函数、优化器），**When** 点击"开始训练"按钮，**Then** 训练进程启动，实时更新loss曲线
2. **Given** 训练正在进行，**When** 用户选择某一层节点，**Then** 可视化面板显示该层的权重分布热图和梯度统计
3. **Given** 训练进行到第10个epoch，**When** 用户点击"暂停"按钮，**Then** 训练暂停，当前模型状态被保存，用户可以继续或修改参数

---

### User Story 4 - 子网络与模块化设计 (Priority: P4)

**目标用户**: 高级用户、数据科学家

用户可以将一组节点封装为子网络模块（子图），通过层次化路径系统（/obj/、/vis/、/train/）组织复杂模型结构，并支持子网络嵌套。

**Why this priority**: 对于复杂模型（如ResNet、Transformer），模块化和层次化组织是必需的，但这不是MVP的核心。

**Independent Test**: 用户创建一个包含多层卷积和池化的模块，将其封装为"ConvBlock"子网络，并在主图中多次复用该模块。

**Acceptance Scenarios**:

1. **Given** 用户选中3个节点（Conv2D、BatchNorm、ReLU），**When** 右键选择"创建子网络"，**Then** 这些节点被封装为一个可折叠的子网络节点
2. **Given** 子网络已创建，**When** 用户拖拽该子网络到画布其他位置，**Then** 创建该子网络的实例，内部结构保持一致
3. **Given** 用户在路径面板切换到/train/目录，**When** 放置训练相关节点，**Then** 这些节点在层次视图中归类到/train/路径下

---

### User Story 5 - 表达式引擎与动态参数 (Priority: P5)

**目标用户**: 高级用户、研究人员

用户可以使用表达式语言为节点参数设置动态值（如学习率衰减schedule、条件分支），并支持变量引用和数学运算。

**Why this priority**: 这是高级功能，为高级用户提供更大的灵活性，但对基础用户不是必需的。

**Independent Test**: 用户为学习率参数设置表达式"0.001 * (0.95 ^ epoch)"，训练过程中验证学习率按指数衰减变化。

**Acceptance Scenarios**:

1. **Given** 用户选中优化器节点的学习率参数，**When** 输入表达式"0.001 * decay_factor"，**Then** 系统验证表达式语法，提示未定义变量
2. **Given** 用户定义了变量decay_factor=0.95，**When** 训练开始，**Then** 学习率根据表达式动态计算并显示在训练日志中
3. **Given** 用户为数据增强设置条件表达式"if epoch > 10 then rotate else none"，**When** 训练进行到epoch 11，**Then** 数据增强策略自动切换

---

### User Story 6 - 插件系统与自定义节点 (Priority: P6)

**目标用户**: 开发者、高级用户

用户可以通过Python编写自定义节点（自定义层、自定义损失函数），并以插件形式加载到系统中，扩展系统功能。

**Why this priority**: 这是可扩展性功能，允许社区贡献，但不是核心使用场景。

**Independent Test**: 用户编写一个自定义激活函数插件（Mish激活），加载到系统后，该激活函数出现在节点面板中，可以像内置节点一样使用。

**Acceptance Scenarios**:

1. **Given** 用户按插件模板编写了CustomLayerPlugin.py，**When** 将插件文件放入plugins目录并重启应用，**Then** 自定义节点出现在节点面板的"自定义"分类下
2. **Given** 自定义节点已加载，**When** 用户拖拽该节点到画布并连接，**Then** 节点正常运行，输入输出验证通过
3. **Given** 插件包含文档字符串，**When** 用户鼠标悬停在自定义节点上，**Then** 显示插件的描述和参数说明

---

### Edge Cases

- **空连接处理**: 当用户创建节点但没有连接输入时，系统如何提示错误？
- **类型不匹配**: 当用户尝试连接不兼容的节点类型（如将图像输出连接到音频输入）时，系统如何处理？
- **非法循环连接**: 当用户尝试创建非法循环连接（A→B→C→A）时，系统实时检测并阻止。合法的循环结构通过ForEach节点组实现
- **大规模图性能**: 当画布上有1000+节点时，渲染性能如何保证？
- **训练中断**: 当训练过程中应用崩溃或电源断开时，用户可通过LoadModel节点加载最近的检查点继续训练
- **GPU内存不足**: 当模型大小超过GPU内存时，系统如何提示并建议降低batch size或切换到CPU？
- **文件格式兼容性**: 旧版本保存的.pnne文件在新版本中能否正常加载？
- **并发编辑**: 多个用户（或同一用户多个窗口）同时编辑同一个模型文件时如何处理？

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: 系统必须提供基于画布的可视化编辑界面，用户可以通过拖拽添加节点
- **FR-002**: 系统必须支持节点间的连接操作，通过拖拽输出针脚到输入针脚创建连接
- **FR-003**: 系统必须提供预定义的PyTorch层节点（Linear、Conv2D、ReLU、Softmax、BatchNorm等）
- **FR-004**: 系统必须提供数据加载节点，支持常见数据集（MNIST、CIFAR-10、ImageNet等）以及自定义数据集（通过文件系统路径 + CSV/JSON元数据文件）
- **FR-005**: 系统必须验证节点连接的类型兼容性（张量形状、数据类型）
- **FR-006**: 系统必须支持训练管线配置（损失函数、优化器、学习率、epoch数量）
- **FR-007**: 系统必须在训练过程中实时更新损失曲线、准确率曲线
- **FR-008**: 系统必须提供权重可视化工具（热图、直方图、3D分布）
- **FR-009**: 系统必须提供梯度流可视化，帮助用户诊断梯度消失/爆炸问题
- **FR-010**: 系统必须支持模型序列化和反序列化，使用.pnne文件格式
- **FR-011**: 系统必须支持撤销/重做操作，记录用户的编辑历史
- **FR-012**: 系统必须提供节点属性面板，用户可以配置节点参数（层大小、激活函数等）
- **FR-013**: 系统必须支持多层级路径系统（/obj/、/vis/、/train/），组织节点层次结构
- **FR-014**: 系统必须支持子网络创建，将多个节点封装为可复用模块
- **FR-015**: 系统必须支持子网络嵌套，允许子网络内部包含其他子网络
- **FR-016**: 系统必须提供表达式语言解析器，支持动态参数计算
- **FR-017**: 系统必须支持表达式中的变量引用、数学运算、条件分支
- **FR-018**: 系统必须提供插件接口，允许用户加载自定义Python节点
- **FR-019**: 系统必须验证插件的安全性和接口兼容性
- **FR-020**: 系统必须支持GPU和CPU两种计算模式，自动检测可用设备
- **FR-021**: 系统必须提供训练暂停/继续/停止控制
- **FR-022**: 系统必须支持模型导出为标准PyTorch格式（.pt或.pth文件）
- **FR-023**: 系统必须提供错误提示和诊断信息（连接错误、类型不匹配、内存不足等）
- **FR-024**: 系统必须支持快捷键操作（复制、粘贴、删除、保存、撤销等）
- **FR-025**: 系统必须提供SaveModel节点，支持配置模型名称、最多保存轮数、是否保存最佳模型等参数
- **FR-026**: 系统必须提供LoadModel节点，允许用户在训练前加载已保存的检查点
- **FR-027**: 系统必须支持ForEach循环结构，由ForEach Begin、ForEach Data、ForEach End三个节点组成，Begin和Data节点通过路径参数指向End节点
- **FR-028**: 系统必须对ForEach循环块进行视觉标识，用凸包线框围起循环内的所有节点，默认使用黄色背景（可自定义颜色）
- **FR-029**: 系统必须实时验证连接合法性：输出针脚只能连接到输入针脚，输入针脚只能连接到输出针脚，阻止非法连接
- **FR-030**: 系统必须提供可选的实时编译开关（右下角），用户可控制是否实时将节点图编译为执行代码
- **FR-031**: 系统必须支持NumpyPack和TorchPack两种数据包类型，分别用于元数据和张量数据传递
- **FR-032**: 系统必须支持节点多输入多输出，每个Pin可同时传递多个Pack（通常一个TorchPack + 多个NumpyPack）
- **FR-033**: 系统必须支持多种参数类型：float、int、checkbox、string、path、float_ramp、vector2/3、int2/3、button、color、enum
- **FR-034**: 系统必须支持参数条件显示/禁用，通过表达式控制（如"layer == 1"隐藏参数）
- **FR-035**: 系统必须区分代码定义参数（不可删除）和实例参数（可删除，用户自定义添加）
- **FR-036**: 系统必须支持参数分组，在属性面板中以多标签页形式组织（基础、高级、优化、自定义等）
- **FR-037**: 系统必须支持表达式引擎函数：chf、chs、chi、chv、chv2、chi2、chi3（获取其他节点的参数值）
- **FR-038**: 系统必须支持Subnet参数提升，内部节点通过表达式引用父级Subnet参数（如"chf('../layer_num')"）
- **FR-039**: 系统必须提供参数变更通知机制，当Subnet参数改变时自动通知依赖的内部节点
- **FR-040**: 系统必须支持pack_shape、pack_value、detail等表达式函数，引用节点的Pack数据和Detail信息

### Non-Functional Requirements

- **NFR-001**: 系统界面响应时间必须小于100ms（100个节点以内）
- **NFR-002**: 系统必须支持至少1000个节点的画布，保持30 FPS渲染性能
- **NFR-003**: 系统启动时间必须小于3秒
- **NFR-004**: 项目文件加载时间必须小于5秒（中等规模项目，50-100个节点）
- **NFR-005**: 系统必须兼容Python 3.8+和PyTorch 1.13+
- **NFR-006**: 系统必须提供完整的用户文档和API参考
- **NFR-007**: 系统必须通过单元测试，核心模块代码覆盖率≥80%
- **NFR-008**: 系统必须支持主题切换（深色/浅色模式）
- **NFR-009**: 系统必须支持中文和英文两种界面语言
- **NFR-010**: 系统必须提供插件开发文档和示例代码

### Key Entities

- **节点 (Node)**: 代表神经网络中的一个操作单元（层、激活函数、数据加载器等），包含输入针脚、输出针脚、参数配置。节点可以有多个输入和多个输出，支持多Pack同时处理
- **针脚 (Pin)**: 节点的输入/输出接口，定义数据类型（张量形状、数据类型）。每个Pin可以传递多个Pack（NumpyPack和/或TorchPack）
- **数据包 (Pack)**: 节点间数据传递的容器，分为NumpyPack（字符串、元数据、标签）和TorchPack（PyTorch张量）。一个Pin可以同时传递多个Pack
- **参数 (Parameter)**: 节点的可配置属性，支持多种类型（float、int、checkbox、string、path、vector2/3、color等）。参数有name（唯一标识）和label（显示标签）的区别，支持条件显示/禁用表达式
- **连接 (Connection)**: 连接两个针脚的边，表示数据流向。连接遵循严格验证规则：输出只能连输入，需类型兼容，不能形成非法循环
- **节点图 (NodeGraph)**: 整个网络的拓扑结构，包含所有节点和连接
- **子网络 (Subnetwork)**: 封装的节点组，可以作为单个节点使用。内部参数可通过表达式提升到Subnet节点上，实现参数传递
- **训练管线 (TrainingPipeline)**: 包含数据加载、模型、损失函数、优化器的完整训练配置
- **ForEach循环组 (ForEachGroup)**: 由ForEach Begin、ForEach Data、ForEach End三节点组成，实现循环控制结构。Begin和Data节点持有指向End节点的路径参数
- **循环块 (LoopBlock)**: ForEach循环组包围的节点区域，用凸包线框和背景色可视化标识
- **实例参数 (Instance Parameter)**: 用户自定义添加到节点实例的参数，不改变类定义，仅影响当前实例。主要用于Subnet参数提升和数据存储
- **项目文件 (.pnne)**: 序列化的节点图，包含所有节点、连接、参数配置（含实例参数）
- **插件 (Plugin)**: 扩展系统功能的Python模块，提供自定义节点或功能

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 无编程背景的用户能够在15分钟内完成第一个简单神经网络的构建（输入→隐藏层→输出）
- **SC-002**: 用户可以在30分钟内完成MNIST数据集的加载、模型训练和可视化监控
- **SC-003**: 系统支持至少100个并发节点的实时编辑，界面响应时间<100ms
- **SC-004**: 训练可视化延迟<500ms，即用户在训练过程中看到的loss曲线与实际训练进度的延迟
- **SC-005**: 90%的常见PyTorch层（Linear、Conv、ReLU、Dropout等）都有对应的预定义节点
- **SC-006**: 用户可以在5分钟内理解如何创建和使用子网络模块
- **SC-007**: 插件开发者可以在30分钟内按文档完成第一个自定义节点插件
- **SC-008**: 系统在GPU模式下训练速度与纯PyTorch代码相比，性能损失<10%
- **SC-009**: 模型文件(.pnne)大小合理，100个节点的模型文件<1MB（不包含权重数据）
- **SC-010**: 用户满意度调查中，至少80%的用户认为系统"易于使用"且"有助于理解深度学习"
