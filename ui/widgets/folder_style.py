"""
文件夹参数UI样式常量

定义文件夹和参数显示的颜色、间距、圆角等样式规范
"""

# 颜色方案
COLORS = {
    'background': '#2b2b2b',        # 主背景（深灰）
    'folder_bg': '#333333',         # 文件夹背景（稍亮）
    'border': '#555555',            # 边框
    'text': '#dddddd',              # 文本
    'text_dim': '#aaaaaa',          # 次要文本
    'tab_active': '#2b2b2b',        # 活动Tab
    'tab_inactive': '#3a3a3a',      # 非活动Tab
    'tab_hover': '#4a4a4a',         # Tab悬停
}

# 间距规范
SPACING = {
    'param_vertical': 3,            # 参数间垂直间距
    'folder_top': 10,               # 文件夹上边距
    'folder_padding': (10, 5, 5, 5),# 文件夹内边距 (top, right, bottom, left)
    'nesting_indent': 15,           # 每层嵌套缩进
    'folder_spacing': 8,            # 文件夹之间的间距
}

# 圆角规范
RADIUS = {
    'folder_box': 5,                # 文件夹框圆角
    'tab_corner': 3,                # Tab圆角
}

# 尺寸规范
SIZES = {
    'name_min_width': 80,           # 参数名最小宽度
    'value_min_width': 100,         # 参数值最小宽度
    'row_height': 24,               # 参数行高度
}


def get_folder_groupbox_style(nesting_level: int = 0) -> str:
    """
    获取文件夹GroupBox的样式表
    
    Args:
        nesting_level: 嵌套层级（用于计算缩进）
        
    Returns:
        CSS样式字符串
    """
    indent = nesting_level * SPACING['nesting_indent']
    top, right, bottom, left = SPACING['folder_padding']
    
    return f"""
        QGroupBox {{
            background-color: {COLORS['folder_bg']};
            border: 1px solid {COLORS['border']};
            border-radius: {RADIUS['folder_box']}px;
            margin-top: {SPACING['folder_top']}px;
            margin-left: {indent}px;
            padding: {top}px {right}px {bottom}px {left}px;
            font-weight: bold;
            color: {COLORS['text']};
        }}
        QGroupBox::title {{
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px;
            color: {COLORS['text']};
        }}
    """


def get_tab_widget_style() -> str:
    """
    获取TabWidget的样式表
    
    Returns:
        CSS样式字符串
    """
    return f"""
        QTabWidget::pane {{
            border: 1px solid {COLORS['border']};
            border-radius: {RADIUS['tab_corner']}px;
            background-color: {COLORS['background']};
            margin-top: -1px;
        }}
        QTabBar::tab {{
            background-color: {COLORS['tab_inactive']};
            color: {COLORS['text_dim']};
            padding: 5px 10px;
            border-top-left-radius: {RADIUS['tab_corner']}px;
            border-top-right-radius: {RADIUS['tab_corner']}px;
            margin-right: 2px;
            border: 1px solid {COLORS['border']};
            border-bottom: none;
        }}
        QTabBar::tab:selected {{
            background-color: {COLORS['tab_active']};
            color: {COLORS['text']};
        }}
        QTabBar::tab:hover {{
            background-color: {COLORS['tab_hover']};
        }}
    """


def get_parameter_row_style() -> str:
    """
    获取参数行的样式表
    
    Returns:
        CSS样式字符串
    """
    return f"""
        QWidget {{
            background-color: transparent;
        }}
        QLabel {{
            color: {COLORS['text']};
            background-color: transparent;
        }}
    """
