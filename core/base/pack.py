"""
Pack系统 - 节点间数据传递的容器

支持两种Pack类型:
- NumpyPack: 用于字符串、元数据、标签等
- TorchPack: 用于PyTorch张量
"""

from typing import Any, Dict, Union
import numpy as np
import torch


class Pack:
    """数据包基类"""
    
    def __init__(self, data: Any, metadata: Dict[str, Any] = None):
        """
        初始化数据包
        
        Args:
            data: 数据内容
            metadata: 元数据字典
        """
        self.data = data
        self.metadata = metadata or {}
    
    def get_shape(self):
        """获取数据形状 - 由子类实现"""
        raise NotImplementedError("Subclass must implement get_shape()")


class NumpyPack(Pack):
    """NumPy数据包 - 用于字符串、元数据、标签"""
    
    def __init__(self, data: np.ndarray, metadata: Dict[str, Any] = None):
        """
        初始化NumpyPack
        
        Args:
            data: NumPy数组
            metadata: 元数据
        """
        assert isinstance(data, np.ndarray), f"NumpyPack requires np.ndarray, got {type(data)}"
        super().__init__(data, metadata)
    
    def get_shape(self) -> tuple:
        """
        获取数组形状
        
        Returns:
            形状元组
        """
        return self.data.shape
    
    def __repr__(self) -> str:
        return f"NumpyPack(shape={self.get_shape()}, dtype={self.data.dtype})"


class TorchPack(Pack):
    """Torch数据包 - 用于PyTorch张量"""
    
    def __init__(self, data: torch.Tensor, metadata: Dict[str, Any] = None):
        """
        初始化TorchPack
        
        Args:
            data: PyTorch张量
            metadata: 元数据
        """
        assert isinstance(data, torch.Tensor), f"TorchPack requires torch.Tensor, got {type(data)}"
        super().__init__(data, metadata)
    
    def get_shape(self) -> tuple:
        """
        获取张量形状
        
        Returns:
            形状元组
        """
        return tuple(self.data.shape)
    
    def to_device(self, device: Union[str, torch.device]) -> None:
        """
        移动数据到指定设备(CPU/GPU)
        
        Args:
            device: 目标设备('cpu', 'cuda', torch.device对象)
        """
        self.data = self.data.to(device)
    
    @property
    def device(self) -> torch.device:
        """获取当前设备"""
        return self.data.device
    
    def __repr__(self) -> str:
        return f"TorchPack(shape={self.get_shape()}, dtype={self.data.dtype}, device={self.device})"
