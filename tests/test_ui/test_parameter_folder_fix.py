"""
测试参数编辑器文件夹修复
验证三个问题：
1. 文件夹子参数保存和加载
2. 文件夹不显示默认值
3. 递归加载文件夹结构
"""

import pytest
import sys
from PyQt6.QtWidgets import QApplication

# 确保导入路径正确
sys.path.insert(0, '.')

from core.base.node import Node, PinType
from ui.dialogs.parameter_editor_dialog import ParameterEditorDialog


class TestNode(Node):
    """测试用的具体节点类"""
    
    display_name = "Test Node"
    node_type = "TestNode"
    
    def init_pins(self):
        """初始化引脚（测试用空实现）"""
        pass
    
    def execute(self):
        """执行节点（测试用空实现）"""
        pass


@pytest.fixture(scope="module")
def qapp():
    """创建QApplication实例"""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app


def test_folder_children_save_and_load(qapp, qtbot):
    """测试文件夹子参数的保存和加载"""
    
    # 创建测试节点
    node = TestNode(name="test_node")
    
    # 创建带子参数的文件夹结构
    node.instance_parameters = {
        'folder1': {
            'type': 'FOLDER_TAB',
            'default': None,
            'label': 'Folder 1',
            'metadata': {},
            'hide': '',
            'disable': '',
            'children': [
                {
                    'name': 'child1',
                    'type': 'INT',
                    'default': 10,
                    'label': 'Child 1',
                    'metadata': {'min': 0, 'max': 100},
                    'hide': '',
                    'disable': ''
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
    
    # 打开参数编辑器
    dialog = ParameterEditorDialog(node)
    qtbot.addWidget(dialog)
    
    # 验证加载
    tree = dialog.param_tree
    
    # 应该有2个顶级项
    assert tree.topLevelItemCount() == 2, "应该有2个顶级参数"
    
    # 查找文件夹项
    folder_item = None
    for i in range(tree.topLevelItemCount()):
        item = tree.topLevelItem(i)
        param_data = item.data(0, 0x0100)  # Qt.ItemDataRole.UserRole
        if param_data and param_data.get('name') == 'folder1':
            folder_item = item
            break
    
    assert folder_item is not None, "应该找到folder1"
    
    # 验证文件夹有2个子项
    assert folder_item.childCount() == 2, f"文件夹应该有2个子参数，实际有 {folder_item.childCount()}"
    
    # 验证文件夹不显示默认值（问题2）
    folder_default_value = folder_item.text(2)
    assert folder_default_value == '', f"文件夹默认值应该为空，实际为 '{folder_default_value}'"
    
    # 验证子参数
    child1 = folder_item.child(0)
    child1_data = child1.data(0, 0x0100)
    assert child1_data['name'] == 'child1', "子参数1名称不正确"
    assert child1_data['type'] == 'INT', "子参数1类型不正确"
    assert child1_data['default'] == 10, "子参数1默认值不正确"
    
    # 模拟保存（点击OK）
    dialog._on_accept()
    
    # 验证保存后的结构
    saved_params = node.instance_parameters
    
    assert 'folder1' in saved_params, "folder1应该被保存"
    assert 'children' in saved_params['folder1'], "folder1应该有children字段"
    assert len(saved_params['folder1']['children']) == 2, "folder1应该有2个子参数"
    
    # 验证子参数被正确保存
    children = saved_params['folder1']['children']
    child1_saved = next((c for c in children if c['name'] == 'child1'), None)
    assert child1_saved is not None, "child1应该被保存"
    assert child1_saved['type'] == 'INT', "child1类型应该保存正确"
    assert child1_saved['default'] == 10, "child1默认值应该保存正确"
    
    print("✅ 文件夹子参数保存和加载测试通过")


def test_folder_no_default_value_in_editor(qapp, qtbot):
    """测试文件夹在编辑器中不显示默认值编辑"""
    
    # 创建测试节点
    node = TestNode(name="test_node")
    
    node.instance_parameters = {
        'folder1': {
            'type': 'FOLDER_TAB',
            'default': None,
            'label': 'Folder 1',
            'metadata': {},
            'hide': '',
            'disable': ''
        }
    }
    
    # 打开参数编辑器
    dialog = ParameterEditorDialog(node)
    qtbot.addWidget(dialog)
    
    # 选择文件夹参数
    tree = dialog.param_tree
    folder_item = tree.topLevelItem(0)
    tree.setCurrentItem(folder_item)
    
    # 验证详情面板中默认值编辑被禁用
    default_edit = dialog.detail_panel.default_edit
    assert not default_edit.isEnabled(), "文件夹的默认值编辑应该被禁用"
    assert default_edit.placeholderText() == "文件夹无默认值", "应该显示正确的占位符"
    
    print("✅ 文件夹不显示默认值编辑测试通过")


def test_nested_folder_structure(qapp, qtbot):
    """测试嵌套文件夹结构"""
    
    # 创建测试节点
    node = TestNode(name="test_node")
    
    # 创建嵌套文件夹结构
    node.instance_parameters = {
        'root_folder': {
            'type': 'FOLDER_EXPAND',
            'default': None,
            'label': 'Root Folder',
            'metadata': {},
            'hide': '',
            'disable': '',
            'children': [
                {
                    'name': 'nested_folder',
                    'type': 'FOLDER_TAB',
                    'default': None,
                    'label': 'Nested Folder',
                    'metadata': {},
                    'hide': '',
                    'disable': '',
                    'children': [
                        {
                            'name': 'deep_param',
                            'type': 'BOOL',
                            'default': True,
                            'label': 'Deep Param',
                            'metadata': {},
                            'hide': '',
                            'disable': ''
                        }
                    ]
                },
                {
                    'name': 'sibling_param',
                    'type': 'FLOAT',
                    'default': 1.5,
                    'label': 'Sibling Param',
                    'metadata': {},
                    'hide': '',
                    'disable': ''
                }
            ]
        }
    }
    
    # 打开参数编辑器
    dialog = ParameterEditorDialog(node)
    qtbot.addWidget(dialog)
    
    # 验证加载
    tree = dialog.param_tree
    root_folder = tree.topLevelItem(0)
    
    assert root_folder.childCount() == 2, "根文件夹应该有2个子项"
    
    # 获取嵌套文件夹
    nested_folder = root_folder.child(0)
    nested_data = nested_folder.data(0, 0x0100)
    assert nested_data['name'] == 'nested_folder', "应该找到嵌套文件夹"
    assert nested_folder.childCount() == 1, "嵌套文件夹应该有1个子项"
    
    # 获取深层参数
    deep_param = nested_folder.child(0)
    deep_data = deep_param.data(0, 0x0100)
    assert deep_data['name'] == 'deep_param', "应该找到深层参数"
    assert deep_data['type'] == 'BOOL', "深层参数类型正确"
    
    # 模拟保存
    dialog._on_accept()
    
    # 验证嵌套结构被正确保存
    saved_params = node.instance_parameters
    assert 'root_folder' in saved_params
    root_children = saved_params['root_folder']['children']
    assert len(root_children) == 2
    
    nested_saved = next((c for c in root_children if c['name'] == 'nested_folder'), None)
    assert nested_saved is not None, "嵌套文件夹应该被保存"
    assert 'children' in nested_saved, "嵌套文件夹应该有children"
    assert len(nested_saved['children']) == 1, "嵌套文件夹应该有1个子项"
    
    deep_saved = nested_saved['children'][0]
    assert deep_saved['name'] == 'deep_param', "深层参数应该被保存"
    assert deep_saved['type'] == 'BOOL', "深层参数类型正确"
    
    print("✅ 嵌套文件夹结构测试通过")


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])
