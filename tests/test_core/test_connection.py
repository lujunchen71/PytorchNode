"""
Connection测试 (Phase 2 T013)
"""

import pytest
import sys
sys.path.insert(0, '.')

from core.base.pin import Pin
from core.base.connection import Connection


def test_connection_creation():
    """测试连接创建"""
    from_pin = Pin("output", "float")
    to_pin = Pin("input", "float")
    conn = Connection(from_pin, to_pin)
    assert conn.from_pin is from_pin
    assert conn.to_pin is to_pin
    print("✅ 连接创建测试通过")


def test_connection_valid():
    """测试连接有效性验证"""
    from_pin = Pin("output", "float")
    to_pin = Pin("input", "float")
    conn = Connection(from_pin, to_pin)
    # 类型匹配，应有效
    assert conn.is_valid() == True
    print("✅ 连接有效性测试通过")


def test_connection_type_mismatch():
    """测试类型不匹配的连接"""
    from_pin = Pin("output", "float")
    to_pin = Pin("input", "int")  # 不同类型
    conn = Connection(from_pin, to_pin)
    # 类型不匹配，应无效
    assert conn.is_valid() == False
    print("✅ 连接类型不匹配测试通过")


def test_connection_multiple():
    """测试多Pack连接"""
    from_pin = Pin("output", "float", multiple=True)
    to_pin = Pin("input", "float", multiple=True)
    conn = Connection(from_pin, to_pin)
    # 多Pack针脚可以连接
    assert conn.is_valid() == True
    print("✅ 多Pack连接测试通过")


if __name__ == "__main__":
    pytest.main([__file__, '-v', '-s'])