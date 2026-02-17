# 12 — API参考文档

---

## 1. 概述

本文档提供 PNNE 所有公开类和方法的完整API签名，供开发者参考。

---

## 2. core.base 模块

### 2.1 Node (节点基类)

```python
class Node(ABC):
    """节点基类"""
    
    def __init__(self):
        self.id: str
        self.node_name: str
        self.node_label: str
        self.node_type: str
        self.category: str
        self.position: QPointF
        self.pins: Dict[str, Pin]
        self.properties: Dict[str, Property]
        self.details: Dict[str, Any]
        self.module: Optional[nn.Module]
        self.enabled: bool
        self.visible: bool
    
    def add_pin(self, name: str, direction: PinDirection, data_type: PinDataType) -> Pin:
        """添加引脚"""
    
    def remove_pin(self, name: str) -> None:
        """移除引脚"""
    
    def get_pin(self, name: str) -> Pin:
        """获取引脚"""
    
    @abstractmethod
    def forward(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """前向传播"""
    
    def backward(self, grad_outputs: Dict[str, torch.Tensor]) -> Dict[str, torch.Tensor]:
        """反向传播"""
    
    def get_path(self) -> str:
        """获取节点路径"""
    
    def to_dict(self) -> dict:
        """序列化为字典"""
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Node':
        """从字典反序列化"""
```

### 2.2 Pin (引脚)

```python
class Pin:
    """引脚类"""
    
    def __init__(self, name: str, direction: PinDirection, data_type: PinDataType):
        self.id: str
        self.name: str
        self.direction: PinDirection
        self.data_type: PinDataType
        self.default_value: Any
        self.connections: List[Connection]
        self.owner_node: Node
        self.cached_data: Any
    
    def connect(self, other: 'Pin') -> Connection:
        """连接到另一个引脚"""
    
    def disconnect(self, connection: Connection) -> None:
        """断开连接"""
    
    def get_data(self) -> Any:
        """获取数据"""
    
    def set_data(self, data: Any) -> None:
        """设置数据"""
    
    def get_shape(self) -> Optional[Tuple[int, ...]]:
        """获取张量形状"""
    
    def is_connected(self) -> bool:
        """是否已连接"""
```

### 2.3 Connection (连接)

```python
class Connection:
    """连接类"""
    
    def __init__(self, source_pin: Pin, target_pin: Pin):
        self.id: str
        self.source_node: Node
        self.source_pin: Pin
        self.target_node: Node
        self.target_pin: Pin
        self.enabled: bool
    
    def validate(self) -> bool:
        """验证连接合法性"""
    
    def execute(self) -> None:
        """执行数据传递"""
    
    def to_dict(self) -> dict:
        """序列化"""
```

### 2.4 NodeGraph (节点图)

```python
class NodeGraph:
    """节点图管理器"""
    
    def __init__(self):
        self.name: str
        self.nodes: Dict[str, Node]
        self.connections: List[Connection]
        self.path: str
        self.context: Dict[str, Any]
    
    def add_node(self, node: Node) -> None:
        """添加节点"""
    
    def remove_node(self, node_id: str) -> None:
        """移除节点"""
    
    def get_node(self, node_id: str) -> Node:
        """获取节点"""
    
    def connect(self, source_pin: Pin, target_pin: Pin) -> Connection:
        """建立连接"""
    
    def disconnect(self, connection: Connection) -> None:
        """断开连接"""
    
    def execute(self) -> Dict[str, Any]:
        """执行图"""
    
    def topological_sort(self) -> List[Node]:
        """拓扑排序"""
    
    def find_by_path(self, path: str) -> Optional[Node]:
        """通过路径查找节点"""
    
    def to_dict(self) -> dict:
        """序列化"""
    
    @classmethod
    def from_dict(cls, data: dict) -> 'NodeGraph':
        """反序列化"""
```

---

## 3. core.nodes 模块

### 3.1 LinearNode

```python
class LinearNode(NNLayerNode):
    """线性层节点"""
    
    def __init__(self):
        super().__init__()
        self.node_type = "nn.Linear"
        
    properties = {
        "in_features": IntProperty(default=128, min=1),
        "out_features": IntProperty(default=64, min=1),
        "bias": BoolProperty(default=True)
    }
    
    def forward(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """前向传播"""
```

### 3.2 Conv2dNode

```python
class Conv2dNode(NNLayerNode):
    """2D卷积层节点"""
    
    properties = {
        "in_channels": IntProperty(default=3, min=1),
        "out_channels": IntProperty(default=64, min=1),
        "kernel_size": IntProperty(default=3, min=1),
        "stride": IntProperty(default=1, min=1),
        "padding": IntProperty(default=0, min=0),
        "bias": BoolProperty(default=True)
    }
```

---

## 4. core.engine 模块

### 4.1 GraphExecutor

```python
class GraphExecutor:
    """图执行器"""
    
    def __init__(self, graph: NodeGraph):
        self.graph: NodeGraph
        self.execution_order: List[Node]
    
    def execute(self) -> Dict[str, Any]:
        """执行图"""
    
    def execute_node(self, node: Node, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """执行单个节点"""
    
    def collect_node_inputs(self, node: Node) -> Dict[str, Any]:
        """收集节点输入"""
```

### 4.2 TorchCompiler

```python
class TorchCompiler:
    """PyTorch模型编译器"""
    
    def compile(self, graph: NodeGraph) -> nn.Module:
        """编译节点图为nn.Module"""
    
    def export_pt(self, module: nn.Module, path: str) -> None:
        """导出.pt文件"""
    
    def export_onnx(self, module: nn.Module, path: str, dummy_input: torch.Tensor) -> None:
        """导出ONNX模型"""
    
    def export_torchscript(self, module: nn.Module, path: str) -> None:
        """导出TorchScript"""
```

### 4.3 TrainingEngine

```python
class TrainingEngine(QThread):
    """训练引擎"""
    
    # 信号
    training_started = Signal()
    training_stopped = Signal()
    epoch_started = Signal(int)
    epoch_finished = Signal(int, dict)
    batch_finished = Signal(int, dict)
    
    def __init__(self, graph: NodeGraph):
        super().__init__()
        self.graph: NodeGraph
        self.context: TrainContext
    
    def run(self) -> None:
        """主训练循环"""
    
    def pause(self) -> None:
        """暂停训练"""
    
    def resume(self) -> None:
        """恢复训练"""
    
    def stop(self) -> None:
        """停止训练"""
```

---

## 5. core.expressions 模块

### 5.1 ExpressionEngine

```python
class ExpressionEngine:
    """表达式引擎"""
    
    @staticmethod
    def evaluate(expression: str, context: Dict[str, Any]) -> Any:
        """求值表达式"""
    
    @staticmethod
    def parse(expression: str) -> ASTNode:
        """解析表达式为AST"""
    
    @staticmethod
    def register_function(name: str, func: Callable) -> None:
        """注册自定义函数"""
    
    @staticmethod
    def unregister_function(name: str) -> None:
        """注销函数"""
```

---

## 6. ui.main_window 模块

### 6.1 MainWindow

```python
class MainWindow(QMainWindow):
    """主窗口"""
    
    def __init__(self):
        super().__init__()
        self.graph_view: NodeGraphicsView
        self.data_viewer_panel: DataViewerPanel
        self.properties_panel: PropertiesPanel
        self.training_monitor_panel: TrainingMonitorPanel
    
    def new_project(self) -> None:
        """新建项目"""
    
    def open_project(self, path: str) -> None:
        """打开项目"""
    
    def save_project(self, path: str) -> None:
        """保存项目"""
    
    def run_graph(self) -> None:
        """执行图"""
    
    def start_training(self) -> None:
        """开始训练"""
```

---

## 7. ui.graphics 模块

### 7.1 NodeGraphicsView

```python
class NodeGraphicsView(QGraphicsView):
    """节点图形视图"""
    
    def __init__(self, scene: NodeGraphicsScene):
        super().__init__(scene)
        self.zoom_factor: float = 1.0
    
    def zoom_in(self) -> None:
        """放大"""
    
    def zoom_out(self) -> None:
        """缩小"""
    
    def fit_in_view(self) -> None:
        """适应窗口"""
    
    def center_on_node(self, node: Node) -> None:
        """居中到节点"""
```

### 7.2 NodeGraphicsItem

```python
class NodeGraphicsItem(QGraphicsItem):
    """节点图形项"""
    
    def __init__(self, node: Node):
        super().__init__()
        self.node: Node
        self.width: float = 180
        self.height: float = 52
    
    def boundingRect(self) -> QRectF:
        """边界矩形"""
    
    def paint(self, painter: QPainter, option, widget) -> None:
        """绘制节点"""
    
    def mousePressEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        """鼠标按下事件"""
```

---

## 8. plugins 模块

### 8.1 Plugin

```python
class Plugin(ABC):
    """插件基类"""
    
    name: str
    version: str
    author: str
    description: str
    
    @abstractmethod
    def activate(self) -> None:
        """激活插件"""
    
    @abstractmethod
    def deactivate(self) -> None:
        """停用插件"""
    
    def configure(self, config: dict) -> None:
        """配置插件"""
```

### 8.2 PluginManager

```python
class PluginManager:
    """插件管理器"""
    
    def discover_plugins(self) -> List[Plugin]:
        """发现插件"""
    
    def enable_plugin(self, plugin_name: str) -> None:
        """启用插件"""
    
    def disable_plugin(self, plugin_name: str) -> None:
        """禁用插件"""
    
    def get_all_plugins(self) -> List[Plugin]:
        """获取所有插件"""
```

---

## 9. utils 模块

### 9.1 GlobalSignalBus

```python
class GlobalSignalBus(QObject):
    """全局信号总线"""
    
    # 节点事件
    node_created = Signal(str)
    node_deleted = Signal(str)
    node_selected = Signal(str)
    
    # 训练事件
    training_started = Signal()
    training_stopped = Signal()
    training_epoch = Signal(int, dict)
    
    # 项目事件
    project_opened = Signal(str)
    project_saved = Signal(str)
```

---

*文档版本: v1.0*  
*最后更新: 2026-02-14*  
*文档状态: 已完成*