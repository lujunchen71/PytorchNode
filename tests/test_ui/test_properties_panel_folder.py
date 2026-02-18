"""
测试属性面板文件夹参数处理
验证文件夹参数显示为文件夹控件（Tab/Expand），子参数在文件夹内显示
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


def test_folder_displayed_as_tab_widget(qapp, qtbot):
    """测试FOLDER_TAB参数显示为TabFolderWidget"""
    
    node = _TestNode(name="test_node")
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
                    'disable': '',
                    'current_value': 10
                },
                {
                    'name': 'child2',
                    'type': 'STRING',
                    'default': 'test',
                    'label': 'Child 2',
                    'metadata': {},
                    'hide': '',
                    'disable': '',
                    'current_value': 'test'
                }
            ]
        },
        'regular_param': {
            'type': 'FLOAT',
            'default': 3.14,
            'label': 'Regular Param',
            'metadata': {'min': 0, 'max': 10},
            'hide': '',
            'disable': '',
            'current_value': 3.14
        }
    }
    
    panel = PropertiesPanel()
    qtbot.addWidget(panel)
    panel.set_node(node)
    
    # 文件夹应该显示为TabFolderWidget
    assert 'folder1' in panel.param_widgets
    assert isinstance(panel.param_widgets['folder1'], TabFolderWidget)
    
    # 普通参数应该显示为ParameterRowWidget
    assert 'regular_param' in panel.param_widgets
    assert isinstance(panel.param_widgets['regular_param'], ParameterRowWidget)
    
    print("✅ FOLDER_TAB显示为TabFolderWidget测试通过")


def test_folder_displayed_as_expand_widget(qapp, qtbot):
    """测试FOLDER_EXPAND参数显示为ExpandFolderWidget"""
    
    node = _TestNode(name="test_node")
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
                            'disable': '',
                            'current_value': True
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
                    'disable': '',
                    'current_value': 1.5
                }
            ]
        }
    }
    
    panel = PropertiesPanel()
    qtbot.addWidget(panel)
    panel.set_node(node)
    
    # 文件夹应该显示为ExpandFolderWidget
    assert 'root_folder' in panel.param_widgets
    assert isinstance(panel.param_widgets['root_folder'], ExpandFolderWidget)
    
    print("✅ FOLDER_EXPAND显示为ExpandFolderWidget测试通过")


def test_empty_folder_still_displayed(qapp, qtbot):
    """测试空文件夹仍然显示为文件夹控件"""
    
    node = _TestNode(name="test_node")
    node.instance_parameters = {
        'empty_folder': {
            'type': 'FOLDER_TAB',
            'default': None,
            'label': 'Empty Folder',
            'metadata': {},
            'hide': '',
            'disable': '',
            'children': []
        },
        'some_param': {
            'type': 'STRING',
            'default': 'value',
            'label': 'Some Param',
            'metadata': {},
            'hide': '',
            'disable': '',
            'current_value': 'value'
        }
    }
    
    panel = PropertiesPanel()
    qtbot.addWidget(panel)
    panel.set_node(node)
    
    # 空文件夹仍然显示为TabFolderWidget
    assert 'empty_folder' in panel.param_widgets
    assert isinstance(panel.param_widgets['empty_folder'], TabFolderWidget)
    
    # 普通参数显示为ParameterRowWidget
    assert 'some_param' in panel.param_widgets
    assert isinstance(panel.param_widgets['some_param'], ParameterRowWidget)
    
    print("✅ 空文件夹显示测试通过")


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])
