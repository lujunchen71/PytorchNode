"""
Pin基类测试 (Phase 2 T012)
"""

import pytest
import sys
sys.path.insert(0, '.')

from core.base.pin import Pin
from core.base.pack import TorchPack


def test_pin_creation():
    """测试针脚创建"""
    pin = Pin("test_pin", "float", multiple=False)
    assert pin.name == "test_pin"
    assert pin.data_type == "float"
    assert not pin.multiple
    print("✅ 针脚创建测试通过")


def test_pin_multiple():
    """测试多Pack针脚"""
    pin = Pin("multi_pin", "int", multiple=True)
    assert pin.multiple
    # 多Pack针脚应能存储列表
    pack1 = TorchPack(tensor=1)
    pack2 = TorchPack(tensor=2)
    pin.set_pack([pack1, pack2])
    packs = pin.get_pack()
    assert isinstance(packs, list)
    assert len(packs) == 2
    print("✅ 多Pack针脚测试通过")


def test_pin_set_get():
    """测试针脚设置和获取Pack"""
    pin = Pin("test_pin", "float")
    pack = TorchPack(tensor=3.14)
    pin.set_pack(pack)
    retrieved = pin.get_pack()
    assert retrieved is pack
    print("✅ 针脚设置获取测试通过")


def test_pin_clear():
    """测试针脚清除"""
    pin = Pin("test_pin", "float")
    pack = TorchPack(tensor=1.0)
    pin.set_pack(pack)
    pin.clear()
    assert pin.get_pack() is None
    print("✅ 针脚清除测试通过")


if __name__ == "__main__":
    pytest.main([__file__, '-v', '-s'])