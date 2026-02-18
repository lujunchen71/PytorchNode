"""
表达式解析器测试

测试ch*函数、路径解析等
"""

import pytest


# from core.expressions.parser import ExpressionParser


class TestExpressionParser:
    """测试表达式解析"""
    
    def test_parse_chf_function(self):
        """测试解析chf()函数"""
        pytest.skip("ExpressionParser not implemented yet")
        
    def test_parse_relative_path(self):
        """测试相对路径解析"""
        pytest.skip("ExpressionParser not implemented yet")
        
    def test_parse_math_expression(self):
        """测试数学表达式"""
        pytest.skip("ExpressionParser not implemented yet")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
