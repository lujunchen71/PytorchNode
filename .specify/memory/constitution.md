<!--
=== SYNC IMPACT REPORT ===
Version Change: 1.0.0 → 1.0.1 (PATCH: Constitution structure standardization + sync report addition)

Modified Principles:
- No principle content changes, only formatting standardization

Added Sections:
- Sync Impact Report (this comment block)

Removed Sections:
- None

Templates Status:
✅ plan-template.md - Verified: Constitution Check section aligns with all principles
✅ spec-template.md - Verified: User scenarios and requirements align with testing and quality standards
✅ tasks-template.md - Verified: Task categorization reflects principle-driven development
✅ All workflow commands - No updates needed

Follow-up TODOs:
- None - All placeholders resolved, all templates verified

Ratification Date: 2026-02-15 (Initial adoption)
Last Amended: 2026-02-16 (Structure standardization)
Amendment Rationale: Added formal sync impact tracking and standardized governance metadata format per speckit.constitution workflow requirements
=== END SYNC IMPACT REPORT ===
-->

# PytorchNode Constitution

## Core Principles

### I. 代码质量至上 (Code Quality First)
代码质量是项目的基石，所有代码必须符合以下标准：
- **可读性优先**：代码应清晰表达意图，使用有意义的变量和函数名
- **模块化设计**：每个模块、类和函数应有单一明确的职责
- **类型注解强制**：所有 Python 代码必须使用类型注解（Type Hints）
- **文档化要求**：所有公共 API、类和复杂函数必须有清晰的文档字符串
- **代码复用**：避免重复代码，通过抽象和继承实现功能复用
- **遵循 PEP8**：严格遵循 Python 编码规范，使用 `black` 和 `pylint` 进行代码格式化和检查

**Rationale**: 高质量的代码是长期可维护性和团队协作的基础，类型注解和文档能显著降低认知负担和错误率。

### II. 测试驱动开发 (Test-First - NON-NEGOTIABLE)
测试是确保代码质量和系统稳定性的关键：
- **TDD 强制执行**：新功能开发必须先写测试，后写实现（Red-Green-Refactor）
- **测试覆盖率要求**：核心模块（`core/`）测试覆盖率必须 ≥ 80%，UI 模块（`ui/`）≥ 60%
- **测试分层**：
  - **单元测试**：测试单个类、函数的功能（`tests/test_core/`, `tests/test_nodes/`）
  - **集成测试**：测试模块间交互（节点连接、图执行、序列化等）
  - **UI 测试**：测试用户界面交互和视觉一致性（`tests/test_ui/`）
- **测试命名规范**：`test_[feature]_[scenario]_[expected_result]`
- **持续集成**：所有 PR 必须通过全部测试才能合并

**Rationale**: TDD 确保代码从设计之初就是可测试的，防止技术债务累积，测试即文档说明预期行为。

### III. 用户体验一致性 (UX Consistency)
保持统一的用户体验，确保可用性和学习曲线平滑：
- **视觉一致性**：
  - 统一的配色方案和主题系统（`config/themes/`）
  - 一致的图标风格和大小（`resources/icons/`）
  - 标准化的节点视觉表现（颜色、形状、字体）
- **交互一致性**：
  - 拖拽操作行为统一（节点、连接、参数）
  - 快捷键体系完整且不冲突
  - 右键菜单结构标准化
  - 撤销/重做机制贯穿所有操作
- **反馈机制**：
  - 操作即时反馈（高亮、动画、状态变化）
  - 错误提示清晰具体，提供解决方案
  - 长时间操作显示进度指示器
- **可访问性**：
  - 支持键盘导航
  - 适当的对比度和可读性
  - 工具提示和帮助文档完善

**Rationale**: 一致性降低用户认知负担，可预测的交互模式提升效率和用户满意度。

### IV. 性能要求 (Performance Standards)
确保系统在各种场景下的性能表现：
- **图渲染性能**：
  - 100 节点以内渲染时间 < 100ms
  - 1000 节点以内保持 30 FPS 交互
  - 使用场景剔除和 LOD 技术优化大规模图
- **计算性能**：
  - 节点执行延迟 < 10ms（非深度学习计算）
  - PyTorch 模型执行优先使用 GPU
  - 图执行使用拓扑排序和并行执行优化
- **内存管理**：
  - 避免内存泄漏，及时释放不用的张量和对象
  - 大数据使用流式处理或分块加载
  - 监控内存使用，提供内存优化建议
- **启动和加载**：
  - 应用启动时间 < 3 秒
  - 项目文件加载时间 < 5 秒（中等规模项目）
  - 延迟加载插件和非必要模块

**Rationale**: 性能直接影响用户体验和生产力，明确的性能指标使优化工作有的放矢。

### V. 架构清晰性 (Architectural Clarity)
保持清晰的架构层次和模块边界：
- **核心-UI 分离**：核心逻辑（`core/`）与界面（`ui/`）严格分离，核心不依赖 UI
- **插件系统独立**：插件接口明确，插件与核心系统松耦合
- **序列化标准化**：所有数据结构可序列化，格式统一（`.pnne` 文件）
- **依赖管理**：最小化外部依赖，核心功能不依赖可选库
- **向后兼容**：文件格式和 API 变更遵循语义化版本控制

**Rationale**: 清晰的架构边界使系统更易理解、测试和维护，降低修改风险和技术债务。

## 质量保证标准

### 代码审查要求
- **强制审查**：所有代码合并前必须经过至少一人审查
- **审查清单**：
  - [ ] 符合编码规范（`docs/11_编码规范.md`）
  - [ ] 有对应的单元测试，测试通过
  - [ ] 有必要的文档和注释
  - [ ] 无明显性能问题
  - [ ] 向后兼容或有迁移方案
- **审查响应时间**：24 小时内给出反馈

### 质量门禁
在每个 PR 合并前自动检查：
1. **静态分析**：`pylint` 评分 ≥ 8.0/10
2. **类型检查**：`mypy` 无错误
3. **测试通过**：所有测试套件通过，覆盖率达标
4. **文档完整**：API 变更必须更新文档
5. **性能基准**：关键路径性能不劣化 > 10%

### 技术栈约束
- **Python 版本**：≥ 3.8，使用现代 Python 特性
- **PyTorch 版本**：≥ 1.13，支持最新 API
- **UI 框架**：PyQt5/PySide2，保持一致性
- **序列化格式**：JSON 为主，支持二进制格式优化

## 开发流程规范

### 功能开发流程
1. **需求分析**：明确功能需求和验收标准
2. **架构设计**：设计模块接口和交互流程
3. **编写测试**：根据验收标准编写测试用例
4. **实现功能**：按照 TDD 循环实现功能
5. **文档更新**：更新相关文档和 API 参考
6. **代码审查**：提交 PR 并通过审查
7. **集成测试**：验证与现有系统的集成

### Bug 修复流程
1. **重现问题**：编写失败的测试用例重现 Bug
2. **定位原因**：分析日志和调试信息
3. **修复实现**：修复代码使测试通过
4. **回归测试**：确保修复不引入新问题
5. **文档记录**：在 `docs/` 目录记录关键修复

### 重构流程
1. **确保测试覆盖**：重构前确保有足够的测试
2. **小步重构**：每次只重构一小部分，保持测试通过
3. **性能验证**：确保重构不降低性能
4. **文档同步**：更新受影响的文档

## 性能监控与优化

### 性能基准测试
定期执行性能基准测试（benchmark）：
- **图渲染性能**：不同节点数量下的渲染时间和帧率
- **图执行性能**：不同复杂度图的执行时间
- **内存占用**：各模块的内存使用情况
- **启动性能**：应用和项目加载时间

### 性能优化原则
- **先测量后优化**：使用 profiler 定位瓶颈
- **优先优化热点**：聚焦 80/20 原则
- **权衡取舍**：在性能和代码复杂度间平衡
- **文档化优化**：记录优化思路和权衡决策

## 安全性要求

### 代码执行安全
- **脚本节点沙箱**：限制脚本节点的文件和网络访问
- **输入验证**：严格验证用户输入和文件格式
- **依赖安全**：定期更新依赖，修复已知漏洞

### 数据安全
- **用户数据保护**：不收集或上传用户项目数据
- **本地存储**：所有数据默认本地存储
- **插件隔离**：插件不能访问系统敏感资源

## Governance（治理）

### 宪法地位
- 本宪法是 PytorchNode 项目的最高开发准则
- 所有设计决策和代码审查必须符合本宪法
- 违反宪法原则的代码不予合并

### 修订流程
1. 宪法修订需经核心开发者讨论和批准
2. 修订必须有充分的理由和文档支持
3. 修订需要制定迁移计划（如适用）
4. 版本控制遵循语义化版本规范：
   - **MAJOR**: 向后不兼容的治理/原则移除或重新定义
   - **MINOR**: 新增原则/章节或实质性扩展指导
   - **PATCH**: 澄清、措辞、错别字修复、非语义优化

### 例外处理
- 特殊情况下可申请例外（需充分论证）
- 例外必须文档化，并制定后续改进计划
- 临时性例外应在下一版本中修正

### 持续改进
- 定期回顾本宪法的有效性（每季度）
- 根据项目发展调整标准和流程
- 收集开发者反馈，优化开发体验

### 合规性审查
- 所有 PR 和代码审查必须验证对本宪法的合规性
- 复杂性和架构偏离必须充分论证
- 参考 `docs/11_编码规范.md` 获取运行时开发指导

---

**Version**: 1.0.1  
**Ratified**: 2026-02-15  
**Last Amended**: 2026-02-16  
**Project**: PytorchNode - Visual PyTorch Node Editor  
**Repository**: https://github.com/yourorg/PytorchNode
