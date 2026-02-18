"""
测试Phase 1基础组件
- ParameterRowWidget
- FolderGroupBox
"""

import pytest
import sys
from PyQt6.QtWidgets import QApplication, QLabel

sys.path.insert(0, '.')

from ui.widgets.parameter_row_widget import ParameterRowWidget
from ui.widgets.folder_group_box import FolderGroupBox


@pytest.fixture(scope="module")
def qapp():
    """创建QApplication实例"""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app


def test_parameter_row_widget_creation(qapp, qtbot):
    """测试ParameterRowWidget创建"""
    
    param_info = {
        'type': 'FLOAT',
        'label': 'Learning Rate',
        'metadata': {'min': 0.0, 'max': 1.0}
    }
    
    row = ParameterRowWidget(
        param_name='learning_rate',
        param_value=0.001,
        param_info=param_info
    )
    qtbot.addWidget(row)
    
    # 验证name label存在
    assert row.name_label is not None
    assert row.name_label.text() == 'Learning Rate'
    
    # 验证value widget存在
    assert row.value_widget is not None
    
    # 验证布局（现在包含分隔条）
    layout = row.layout()
    assert layout is not None
    assert layout.count() == 3  # name + splitter + value
    
    print("PASS ParameterRowWidget创建测试通过")


def test_parameter_row_widget_ratio(qapp, qtbot):
    """测试参数行比例调整"""
    
    param_info = {'type': 'INT', 'label': 'Size'}
    row = ParameterRowWidget('size', 10, param_info)
    qtbot.addWidget(row)
    
    # 默认比例1:1 (0.5)
    layout = row.layout()
    # 名称拉伸因子 = 50, 值拉伸因子 = 50 (因为比例0.5)
    assert layout.stretch(0) == 50  # name
    assert layout.stretch(2) == 50  # value (索引2因为分隔条在索引1)
    
    # 调整为4:6
    row.set_ratio(0.4)
    assert layout.stretch(0) == 40
    assert layout.stretch(2) == 60
    
    # 调整为3:7
    row.set_ratio(0.3)
    assert layout.stretch(0) == 30
    assert layout.stretch(2) == 70
    
    print("PASS ParameterRowWidget比例调整测试通过")


def test_folder_group_box_creation(qapp, qtbot):
    """测试FolderGroupBox创建"""
    
    # 顶级文件夹
    folder = FolderGroupBox(
        folder_name='Basic Settings',
        folder_type='FOLDER_EXPAND',
        nesting_level=0
    )
    qtbot.addWidget(folder)
    
    assert folder.title() == 'Basic Settings'
    assert folder.folder_type == 'FOLDER_EXPAND'
    assert folder.nesting_level == 0
    
    # 嵌套文件夹
    nested_folder = FolderGroupBox(
        folder_name='Advanced',
        folder_type='FOLDER_TAB',
        nesting_level=1
    )
    qtbot.addWidget(nested_folder)
    
    assert nested_folder.nesting_level == 1
    
    print("PASS FolderGroupBox创建测试通过")


def test_folder_group_box_nesting_style(qapp, qtbot):
    """测试文件夹嵌套层级样式"""
    
    # 测试不同嵌套层级
    folders = []
    for level in range(3):
        folder = FolderGroupBox(
            folder_name=f'Level {level}',
            folder_type='FOLDER_EXPAND',
            nesting_level=level
        )
        qtbot.addWidget(folder)
        folders.append(folder)
        
        # 验证样式表包含正确的margin-left
        style = folder.styleSheet()
        expected_indent = level * 15
        assert f'margin-left: {expected_indent}px' in style, f"Level {level} should have {expected_indent}px indent"
    
    print("PASS FolderGroupBox嵌套样式测试通过")


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])
