"""
表达式求值器测试

测试参数引用、Pack引用、Detail引用等
"""

import pytest


# from core.expressions.evaluator import ExpressionEvaluator


class TestExpressionEvaluator:
    """测试表达式求值"""
    
    def test_evaluate_simple_math(self):
        """测试简单数学表达式求值"""
        pytest.skip("ExpressionEvaluator not implemented yet")
        # evaluator = ExpressionEvaluator(node_graph)
        # result = evaluator.evaluate("2 + 3 * 4", "/test/node")
        # assert result == 14
        
    def test_evaluate_chf_function(self):
        """测试chf()函数求值"""
        pytest.skip("ExpressionEvaluator not implemented yet")
        
    def test_evaluate_relative_path_reference(self):
        """测试相对路径参数引用"""
        pytest.skip("ExpressionEvaluator not implemented yet")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
