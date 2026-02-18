"""
测试参数控件 - Phase 3.5 T135

测试内容:
- FloatWidget: 浮点数输入控件
- IntWidget: 整数输入控件  
- Vector2Widget: 二维向量控件
- Vector3Widget: 三维向量控件
- ColorWidget: 颜色选择器
- PathWidget: 文件路径选择器
- FloatRampWidget: 曲线编辑器
- EnumWidget: 枚举下拉选择
- FolderTabWidget: Tab文件夹控件
- FolderExpandWidget: 展开文件夹控件
"""

import pytest
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
import sys

# 确保应用实例存在
@pytest.fixture(scope="session")
def qapp():
    """创建QApplication实例"""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app


class TestIntWidget:
    """测试整数控件"""
    
    def test_int_widget_creation(self, qapp):
        """测试IntWidget创建"""
        from ui.widgets.parameter_widgets import IntWidget
        
        widget = IntWidget("test_int", initial_value=10, min_val=0, max_val=100)
        assert widget.get_value() == 10
    
    def test_int_widget_set_value(self, qapp):
        """测试设置值"""
        from ui.widgets.parameter_widgets import IntWidget
        
        widget = IntWidget("test_int", initial_value=10)
        widget.set_value(25)
        assert widget.get_value() == 25
    
    def test_int_widget_value_changed_signal(self, qapp, qtbot):
        """测试值改变信号"""
        from ui.widgets.parameter_widgets import IntWidget
        
        widget = IntWidget("test_int", initial_value=10)
        
        # 监听信号
        with qtbot.waitSignal(widget.value_changed, timeout=1000) as blocker:
            widget.spinbox.setValue(20)
        
        assert blocker.args[0] == 20


class TestFloatWidget:
    """测试浮点数控件"""
    
    def test_float_widget_creation(self, qapp):
        """测试FloatWidget创建"""
        from ui.widgets.parameter_widgets import FloatWidget
        
        widget = FloatWidget("test_float", initial_value=1.5, min_val=0.0, max_val=10.0, decimals=2)
        assert widget.get_value() == 1.5
    
    def test_float_widget_set_value(self, qapp):
        """测试设置值"""
        from ui.widgets.parameter_widgets import FloatWidget
        
        widget = FloatWidget("test_float", initial_value=1.5)
        widget.set_value(3.14)
        assert abs(widget.get_value() - 3.14) < 0.0001
    
    def test_float_widget_decimals(self, qapp):
        """测试小数位数"""
        from ui.widgets.parameter_widgets import FloatWidget
        
        widget = FloatWidget("test_float", initial_value=0.0, decimals=4)
        widget.set_value(1.23456789)
        # 检查显示精度
        assert widget.spinbox.decimals() == 4


class TestBoolWidget:
    """测试布尔值控件"""
    
    def test_bool_widget_creation(self, qapp):
        """测试BoolWidget创建"""
        from ui.widgets.parameter_widgets import BoolWidget
        
        widget = BoolWidget("test_bool", initial_value=True)
        assert widget.get_value() is True
    
    def test_bool_widget_toggle(self, qapp):
        """测试切换值"""
        from ui.widgets.parameter_widgets import BoolWidget
        
        widget = BoolWidget("test_bool", initial_value=False)
        widget.set_value(True)
        assert widget.get_value() is True


class TestStringWidget:
    """测试字符串控件"""
    
    def test_string_widget_creation(self, qapp):
        """测试StringWidget创建"""
        from ui.widgets.parameter_widgets import StringWidget
        
        widget = StringWidget("test_string", initial_value="hello")
        assert widget.get_value() == "hello"
    
    def test_string_widget_set_value(self, qapp):
        """测试设置值"""
        from ui.widgets.parameter_widgets import StringWidget
        
        widget = StringWidget("test_string", initial_value="")
        widget.set_value("world")
        assert widget.get_value() == "world"


class TestEnumWidget:
    """测试枚举控件"""
    
    def test_enum_widget_creation(self, qapp):
        """测试EnumWidget创建"""
        from ui.widgets.parameter_widgets import EnumWidget
        
        options = ["Option1", "Option2", "Option3"]
        widget = EnumWidget("test_enum", options, initial_value="Option2")
        assert widget.get_value() == "Option2"
    
    def test_enum_widget_change_selection(self, qapp):
        """测试修改选择"""
        from ui.widgets.parameter_widgets import EnumWidget
        
        options = ["Red", "Green", "Blue"]
        widget = EnumWidget("test_enum", options, initial_value="Red")
        widget.set_value("Blue")
        assert widget.get_value() == "Blue"


class TestVector2Widget:
    """测试二维向量控件 - 待实现"""
    
    def test_vector2_widget_creation(self, qapp):
        """测试Vector2Widget创建"""
        pytest.skip("Vector2Widget尚未实现 - 任务T140")


class TestVector3Widget:
    """测试三维向量控件 - 待实现"""
    
    def test_vector3_widget_creation(self, qapp):
        """测试Vector3Widget创建"""
        pytest.skip("Vector3Widget尚未实现 - 任务T141")


class TestColorWidget:
    """测试颜色选择器 - 待实现"""
    
    def test_color_widget_creation(self, qapp):
        """测试ColorWidget创建"""
        pytest.skip("ColorWidget尚未实现 - 任务T142")


class TestPathWidget:
    """测试路径选择器 - 待实现"""
    
    def test_path_widget_creation(self, qapp):
        """测试PathWidget创建"""
        pytest.skip("PathWidget尚未实现 - 任务T143")


class TestFloatRampWidget:
    """测试曲线编辑器 - 待实现"""
    
    def test_float_ramp_widget_creation(self, qapp):
        """测试FloatRampWidget创建"""
        pytest.skip("FloatRampWidget尚未实现 - 任务T144")


class TestFolderWidgets:
    """测试文件夹控件 - 待实现"""
    
    def test_folder_tab_widget(self, qapp):
        """测试FolderTabWidget"""
        pytest.skip("FolderTabWidget尚未实现 - 任务T145A")
    
    def test_folder_expand_widget(self, qapp):
        """测试FolderExpandWidget"""
        pytest.skip("FolderExpandWidget尚未实现 - 任务T145B")


class TestParameterWidgetFactory:
    """测试参数控件工厂函数"""
    
    def test_create_int_widget(self, qapp):
        """测试创建整数控件"""
        from ui.widgets.parameter_widgets import create_parameter_widget
        
        widget = create_parameter_widget("test", 42)
        from ui.widgets.parameter_widgets import IntWidget
        assert isinstance(widget, IntWidget)
    
    def test_create_float_widget(self, qapp):
        """测试创建浮点数控件"""
        from ui.widgets.parameter_widgets import create_parameter_widget
        
        widget = create_parameter_widget("test", 3.14)
        from ui.widgets.parameter_widgets import FloatWidget
        assert isinstance(widget, FloatWidget)
    
    def test_create_bool_widget(self, qapp):
        """测试创建布尔控件"""
        from ui.widgets.parameter_widgets import create_parameter_widget
        
        widget = create_parameter_widget("test", True)
        from ui.widgets.parameter_widgets import BoolWidget
        assert isinstance(widget, BoolWidget)
    
    def test_create_string_widget(self, qapp):
        """测试创建字符串控件"""
        from ui.widgets.parameter_widgets import create_parameter_widget
        
        widget = create_parameter_widget("test", "hello")
        from ui.widgets.parameter_widgets import StringWidget
        assert isinstance(widget, StringWidget)
