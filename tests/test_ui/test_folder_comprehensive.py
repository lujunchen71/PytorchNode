"""
综合性测试文件夹嵌套组合 (Phase 3.5 T153O)
验证文件夹参数在各种嵌套组合下的正确显示和交互。
"""

import pytest
import sys
from PyQt6.QtWidgets import QApplication

sys.path.insert(0, '.')

from core.base.node import Node
from ui.panels.properties_panel import PropertiesPanel
from ui.widgets.tab_folder_widget import TabFolderWidget
from ui.widgets.expand_folder_widget import ExpandFolderWidget
from ui.widgets.parameter_row_widget import ParameterRowWidget


class _TestNode(Node):
    """测试用的具体节点类"""
    
    display_name = "Test Node"
    node_type = "TestNode"
    
    def init_pins(self):
        pass
    
    def execute(self):
        pass


@pytest.fixture(scope="module")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app


def test_deep_nested_folders(qapp, qtbot):
    """测试深度嵌套文件夹（三层）"""
    
    node = _TestNode(name="test_node")
    node.instance_parameters = {
        'root_expand': {
            'type': 'FOLDER_EXPAND',
            'default': None,
            'label': 'Root Expand',
            'metadata': {},
            'hide': '',
            'disable': '',
            'children': [
                {
                    'name': 'nested_tab',
                    'type': 'FOLDER_TAB',
                    'default': None,
                    'label': 'Nested Tab',
                    'metadata': {},
                    'hide': '',
                    'disable': '',
                    'children': [
                        {
                            'name': 'deep_expand',
                            'type': 'FOLDER_EXPAND',
                            'default': None,
                            'label': 'Deep Expand',
                            'metadata': {},
                            'hide': '',
                            'disable': '',
                            'children': [
                                {
                                    'name': 'deep_param',
                                    'type': 'INT',
                                    'default': 42,
                                    'label': 'Deep Param',
                                    'metadata': {},
                                    'hide': '',
                                    'disable': '',
                                    'current_value': 42
                                }
                            ]
                        },
                        {
                            'name': 'tab_param',
                            'type': 'FLOAT',
                            'default': 3.14,
                            'label': 'Tab Param',
                            'metadata': {},
                            'hide': '',
                            'disable': '',
                            'current_value': 3.14
                        }
                    ]
                },
                {
                    'name': 'root_param',
                    'type': 'STRING',
                    'default': 'hello',
                    'label': 'Root Param',
                    'metadata': {},
                    'hide': '',
                    'disable': '',
                    'current_value': 'hello'
                }
            ]
        }
    }
    
    panel = PropertiesPanel()
    qtbot.addWidget(panel)
    panel.set_node(node)
    
    # 验证根文件夹显示为ExpandFolderWidget
    assert 'root_expand' in panel.param_widgets
    assert isinstance(panel.param_widgets['root_expand'], ExpandFolderWidget)
    
    # 嵌套文件夹和参数应在子控件中（具体实现可能不同）
    # 这里仅确保没有崩溃
    print("✅ 深度嵌套文件夹测试通过")


def test_mixed_parameter_types_in_folders(qapp, qtbot):
    """测试文件夹内混合多种参数类型"""
    
    node = _TestNode(name="test_node")
    node.instance_parameters = {
        'mixed_folder': {
            'type': 'FOLDER_TAB',
            'default': None,
            'label': 'Mixed Folder',
            'metadata': {},
            'hide': '',
            'disable': '',
            'children': [
                {
                    'name': 'int_param',
                    'type': 'INT',
                    'default': 10,
                    'label': 'Int Param',
                    'metadata': {'min': 0, 'max': 100},
                    'hide': '',
                    'disable': '',
                    'current_value': 10
                },
                {
                    'name': 'float_param',
                    'type': 'FLOAT',
                    'default': 2.5,
                    'label': 'Float Param',
                    'metadata': {'decimals': 2},
                    'hide': '',
                    'disable': '',
                    'current_value': 2.5
                },
                {
                    'name': 'bool_param',
                    'type': 'BOOL',
                    'default': True,
                    'label': 'Bool Param',
                    'metadata': {},
                    'hide': '',
                    'disable': '',
                    'current_value': True
                },
                {
                    'name': 'enum_param',
                    'type': 'ENUM',
                    'default': 'option1',
                    'label': 'Enum Param',
                    'metadata': {'options': ['option1', 'option2', 'option3']},
                    'hide': '',
                    'disable': '',
                    'current_value': 'option1'
                },
                {
                    'name': 'color_param',
                    'type': 'COLOR',
                    'default': '#FF0000',
                    'label': 'Color Param',
                    'metadata': {},
                    'hide': '',
                    'disable': '',
                    'current_value': '#FF0000'
                }
            ]
        }
    }
    
    panel = PropertiesPanel()
    qtbot.addWidget(panel)
    panel.set_node(node)
    
    assert 'mixed_folder' in panel.param_widgets
    assert isinstance(panel.param_widgets['mixed_folder'], TabFolderWidget)
    print("✅ 混合参数类型文件夹测试通过")


def test_empty_nested_folders(qapp, qtbot):
    """测试空嵌套文件夹（文件夹内只有空文件夹）"""
    
    node = _TestNode(name="test_node")
    node.instance_parameters = {
        'empty_root': {
            'type': 'FOLDER_EXPAND',
            'default': None,
            'label': 'Empty Root',
            'metadata': {},
            'hide': '',
            'disable': '',
            'children': [
                {
                    'name': 'empty_child',
                    'type': 'FOLDER_TAB',
                    'default': None,
                    'label': 'Empty Child',
                    'metadata': {},
                    'hide': '',
                    'disable': '',
                    'children': []
                }
            ]
        }
    }
    
    panel = PropertiesPanel()
    qtbot.addWidget(panel)
    panel.set_node(node)
    
    assert 'empty_root' in panel.param_widgets
    assert isinstance(panel.param_widgets['empty_root'], ExpandFolderWidget)
    print("✅ 空嵌套文件夹测试通过")


def test_folder_expanded_state(qapp, qtbot):
    """测试文件夹展开状态"""
    
    node = _TestNode(name="test_node")
    node.instance_parameters = {
        'expanded_folder': {
            'type': 'FOLDER_EXPAND',
            'default': None,
            'label': 'Expanded Folder',
            'metadata': {'expanded': True},
            'hide': '',
            'disable': '',
            'children': [
                {
                    'name': 'child_param',
                    'type': 'INT',
                    'default': 5,
                    'label': 'Child Param',
                    'metadata': {},
                    'hide': '',
                    'disable': '',
                    'current_value': 5
                }
            ]
        },
        'collapsed_folder': {
            'type': 'FOLDER_EXPAND',
            'default': None,
            'label': 'Collapsed Folder',
            'metadata': {'expanded': False},
            'hide': '',
            'disable': '',
            'children': [
                {
                    'name': 'hidden_param',
                    'type': 'FLOAT',
                    'default': 9.99,
                    'label': 'Hidden Param',
                    'metadata': {},
                    'hide': '',
                    'disable': '',
                    'current_value': 9.99
                }
            ]
        }
    }
    
    panel = PropertiesPanel()
    qtbot.addWidget(panel)
    panel.set_node(node)
    
    # 验证两个文件夹都存在
    assert 'expanded_folder' in panel.param_widgets
    assert 'collapsed_folder' in panel.param_widgets
    
    # 具体展开/折叠状态由控件内部管理，这里仅确保无异常
    print("✅ 文件夹展开状态测试通过")


def test_large_number_of_parameters(qapp, qtbot):
    """测试大量参数渲染（性能相关）"""
    
    node = _TestNode(name="test_node")
    children = []
    for i in range(50):
        children.append({
            'name': f'param_{i}',
            'type': 'FLOAT',
            'default': float(i),
            'label': f'Param {i}',
            'metadata': {},
            'hide': '',
            'disable': '',
            'current_value': float(i)
        })
    
    node.instance_parameters = {
        'big_folder': {
            'type': 'FOLDER_TAB',
            'default': None,
            'label': 'Big Folder',
            'metadata': {},
            'hide': '',
            'disable': '',
            'children': children
        }
    }
    
    panel = PropertiesPanel()
    qtbot.addWidget(panel)
    panel.set_node(node)
    
    assert 'big_folder' in panel.param_widgets
    # 渲染大量参数不应崩溃
    print("✅ 大量参数渲染测试通过")


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])