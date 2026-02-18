# 参数编辑器文件夹修复总结

## 修复日期
2026-02-16

## 修复的问题（全部完成）

### 1. 文件夹子参数未保存
**问题描述**: `_on_accept()` 方法未递归处理文件夹内的子参数，导致文件夹内参数在关闭对话框后丢失。

**解决方案**: 
- 实现 `_collect_parameter()` 递归方法
- 该方法递归遍历树结构，收集所有参数（包括文件夹内的子参数）
- 返回 `(param_name, param_def)` 元组，子参数保留 `name` 字段在 `children` 列表中

**代码位置**: [`ui/dialogs/parameter_editor_dialog.py:938-993`](ui/dialogs/parameter_editor_dialog.py:938)

```python
def _collect_parameter(self, item, old_params):
    """递归收集参数及其子参数"""
    # ... 收集参数数据 ...
    
    # 递归收集子参数（文件夹）
    if item.childCount() > 0:
        children = []
        for i in range(item.childCount()):
            child_item = item.child(i)
            child_result = self._collect_parameter(child_item, old_params)
            if child_result:
                child_name, child_def = child_result
                child_def_with_name = {'name': child_name, **child_def}
                children.append(child_def_with_name)
        
        if children:
            param_def['children'] = children
    
    return (param_name, param_def)
```

### 2. 文件夹不应该显示值
**问题描述**: 文件夹参数在树中显示默认值列，文件夹类型不应该有默认值。

**解决方案**: 
- 在 `_load_parameters()` 中，文件夹类型不显示默认值（显示为空字符串）
- 在 `set_parameter()` 中，文件夹类型禁用默认值编辑框
- 在 `_on_detail_changed()` 中，文件夹类型保存 `None` 作为默认值

**代码位置**: 
- [`_load_parameters()`](ui/dialogs/parameter_editor_dialog.py:166): 加载时不显示默认值
- [`set_parameter()`](ui/dialogs/parameter_editor_dialog.py:645): 禁用默认值编辑
- [`_on_detail_changed()`](ui/dialogs/parameter_editor_dialog.py:747): 保存时设置为 `None`

```python
# 在 _load_parameters() 中
is_folder = param_type in ('FOLDER_TAB', 'FOLDER_EXPAND')
display_value = '' if is_folder else str(default_value)

# 在 set_parameter() 中
if is_folder:
    self.default_edit.setText('')
    self.default_edit.setEnabled(False)
    self.default_edit.setPlaceholderText("文件夹无默认值")

# 在 _on_detail_changed() 中
if is_folder:
    param_data['default'] = None
else:
    param_data['default'] = self.default_edit.text()
```

### 3. 文件夹加载未实现
**问题描述**: `_load_parameters()` 未递归加载子参数，导致文件夹结构无法正确恢复。

**解决方案**: 
- 实现递归加载函数 `load_param_recursive()`
- 该函数处理参数的 `children` 字段，递归创建子树项
- 自动展开包含子参数的文件夹

**代码位置**: [`ui/dialogs/parameter_editor_dialog.py:166-236`](ui/dialogs/parameter_editor_dialog.py:166)

```python
def _load_parameters(self):
    """加载节点的动态参数（支持递归加载文件夹子参数）"""
    # ...
    
    # 递归加载参数函数
    def load_param_recursive(param_name, param_info, parent_item=None):
        """递归加载参数及其子参数"""
        # ... 创建树项 ...
        
        # 递归加载子参数
        children = param_info.get('children', [])
        if children and isinstance(children, list):
            for child_param in children:
                if isinstance(child_param, dict) and 'name' in child_param:
                    load_param_recursive(child_param['name'], child_param, item)
            # 展开文件夹
            item.setExpanded(True)
        
        return item
    
    # 加载所有顶级参数
    for param_name, param_info in instance_params.items():
        load_param_recursive(param_name, param_info)
```

## 测试验证

创建了全面的测试套件 [`tests/test_ui/test_parameter_folder_fix.py`](tests/test_ui/test_parameter_folder_fix.py)：

### 测试用例

1. **test_folder_children_save_and_load**: 
   - 验证文件夹子参数的保存和加载
   - 确认子参数结构正确
   - 检查文件夹不显示默认值

2. **test_folder_no_default_value_in_editor**:
   - 验证文件夹在编辑器中不显示默认值编辑
   - 确认默认值编辑框被禁用
   - 检查正确的占位符文本

3. **test_nested_folder_structure**:
   - 验证嵌套文件夹结构
   - 测试多层级文件夹和参数
   - 确认递归保存和加载正确

### 测试结果
```
tests/test_ui/test_parameter_folder_fix.py::test_folder_children_save_and_load PASSED
tests/test_ui/test_parameter_folder_fix.py::test_folder_no_default_value_in_editor PASSED
tests/test_ui/test_parameter_folder_fix.py::test_nested_folder_structure PASSED
======================== 3 passed, 1 warning in 0.44s =========================
```

## 数据结构

### 参数序列化格式

#### 顶级参数（字典键值对）
```python
{
    'folder1': {
        'type': 'FOLDER_TAB',
        'default': None,  # 文件夹无默认值
        'label': 'Folder 1',
        'metadata': {},
        'hide': '',
        'disable': '',
        'children': [...]  # 子参数列表
    },
    'regular_param': {
        'type': 'FLOAT',
        'default': 3.14,
        'label': 'Regular Param',
        'metadata': {'min': 0, 'max': 10},
        'hide': '',
        'disable': ''
    }
}
```

#### 子参数（列表元素）
```python
'children': [
    {
        'name': 'child1',  # 子参数必须包含 name 字段
        'type': 'INT',
        'default': 10,
        'label': 'Child 1',
        'metadata': {'min': 0, 'max': 100},
        'hide': '',
        'disable': '',
        'children': [...]  # 支持嵌套
    },
    {
        'name': 'child2',
        'type': 'STRING',
        'default': 'test',
        'label': 'Child 2',
        'metadata': {},
        'hide': '',
        'disable': ''
    }
]
```

## 影响范围

### 修改的文件
1. [`ui/dialogs/parameter_editor_dialog.py`](ui/dialogs/parameter_editor_dialog.py)
   - `_load_parameters()`: 递归加载
   - `set_parameter()`: 禁用文件夹默认值编辑
   - `_on_detail_changed()`: 文件夹默认值处理
   - `_collect_parameter()`: 递归收集（新方法）
   - `_on_accept()`: 使用递归收集

2. [`ui/panels/properties_panel.py`](ui/panels/properties_panel.py)
   - `_load_parameters()`: 修改为调用扁平化方法
   - `_flatten_parameters()`: 递归扁平化（新方法）

### 新增的文件
1. [`tests/test_ui/test_parameter_folder_fix.py`](tests/test_ui/test_parameter_folder_fix.py)
   - 参数编辑器测试套件
   - 3个测试用例覆盖编辑器修复

2. [`tests/test_ui/test_properties_panel_folder.py`](tests/test_ui/test_properties_panel_folder.py)
   - 属性面板测试套件
   - 3个测试用例覆盖面板修复

## 向后兼容性

所有修改都向后兼容：
- 没有 `children` 字段的参数仍然正常工作
- 旧的序列化数据可以正常加载
- 新的数据结构是旧结构的扩展

## 新增修复（属性面板）

### 4. 属性面板文件夹显示
**问题描述**: 文件夹参数在属性面板中显示为参数控件，但文件夹只是布局容器，不应该显示。

**解决方案**:
- 实现 [`_flatten_parameters()`](ui/panels/properties_panel.py:509) 递归方法
- 该方法遍历参数树，跳过文件夹类型，只提取文件夹内的实际参数
- 文件夹作为组织结构，其子参数扁平化显示在属性面板中

**代码位置**: [`ui/panels/properties_panel.py:459-533`](ui/panels/properties_panel.py:459)

```python
def _flatten_parameters(self, params_dict, output_dict):
    """递归展开参数（跳过文件夹，提取子参数）"""
    for param_name, param_info in params_dict.items():
        if isinstance(param_info, dict):
            param_type = param_info.get('type', '')
            is_folder = param_type in ('FOLDER_TAB', 'FOLDER_EXPAND')
            
            if is_folder:
                # 文件夹：递归处理子参数
                children = param_info.get('children', [])
                if children and isinstance(children, list):
                    children_dict = {}
                    for child in children:
                        if isinstance(child, dict) and 'name' in child:
                            children_dict[child['name']] = child
                    self._flatten_parameters(children_dict, output_dict)
            else:
                # 普通参数：添加到输出
                current_value = param_info.get('current_value', param_info.get('default', ''))
                output_dict[param_name] = current_value
```

### 测试验证（属性面板）

创建了属性面板测试套件 [`tests/test_ui/test_properties_panel_folder.py`](tests/test_ui/test_properties_panel_folder.py)：

```
✅ test_folder_not_displayed_in_properties_panel - 验证文件夹不显示，只显示子参数
✅ test_nested_folder_flattening - 验证嵌套文件夹的参数扁平化
✅ test_folder_with_no_children - 验证空文件夹的情况

======================== 3 passed, 1 warning in 1.21s =========================
```

## 文件夹设计理念

文件夹参数 (`FOLDER_TAB` / `FOLDER_EXPAND`) 是**纯UI布局容器**，类似于 Houdini 的参数文件夹：

- **参数编辑器中**: 文件夹显示为可折叠的树节点，用于组织参数层级
- **属性面板中**: 文件夹不显示，只显示其内部的实际参数（扁平化）
- **序列化**: 文件夹保存完整的树结构（包含 `children` 字段）
- **用途**: 提供参数的逻辑分组和视觉组织，不参与实际的数据存储和计算

## 后续建议

1. **Tab文件夹UI**: 考虑为 `FOLDER_TAB` 类型实现真正的Tab界面
2. **拖拽优化**: 改进文件夹内参数的拖拽体验
3. **验证增强**: 添加文件夹嵌套深度限制（建议最大3层）
4. **性能优化**: 对于大量参数，考虑延迟加载子树
5. **视觉增强**: 在参数编辑器中为文件夹添加更明显的视觉区分

## 相关文档

- [参数系统设计](docs/03_核心节点系统.md)
- [序列化系统](docs/10_序列化系统.md)
- [UI框架设计](docs/04_UI框架设计.md)
