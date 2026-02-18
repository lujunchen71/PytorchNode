"""
PNNE - PyTorch Neural Network Editor
主程序入口

启动应用程序的主窗口
"""

import sys
import argparse
from pathlib import Path

# 确保项目根目录在 Python 路径中
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description="PNNE - PyTorch Neural Network Editor",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python main.py                    # 启动应用
  python main.py --file project.pnne # 打开指定项目
  python main.py --debug            # 启用调试模式
        """
    )

    parser.add_argument(
        '--file', '-f',
        type=str,
        metavar='FILE',
        help='启动时打开的项目文件'
    )

    parser.add_argument(
        '--debug', '-d',
        action='store_true',
        help='启用调试模式'
    )

    parser.add_argument(
        '--version', '-v',
        action='version',
        version='PNNE v0.1.0'
    )

    parser.add_argument(
        '--log-level',
        type=str,
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        default='INFO',
        help='设置日志级别'
    )

    return parser.parse_args()


def setup_logging(level='INFO'):
    """配置日志系统"""
    import logging
    
    # 配置基础日志
    logging.basicConfig(
        level=getattr(logging, level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


def main():
    """主函数"""
    # 解析命令行参数
    args = parse_arguments()

    # 设置日志
    setup_logging(args.log_level)

    # 日志记录
    import logging
    import os
    logger = logging.getLogger(__name__)
    logger.info("Starting PNNE - PyTorch Neural Network Editor")

    # 重要：在导入 PyQt6 之前先导入 torch，避免 DLL 加载冲突
    logger.info("Pre-loading PyTorch to avoid DLL conflicts...")
    try:
        os.environ['PYTORCH_NO_CUDA'] = '1'
        os.environ['CUDA_VISIBLE_DEVICES'] = ''
        import torch
        logger.info(f"PyTorch {torch.__version__} loaded successfully")
    except Exception as e:
        logger.warning(f"Failed to pre-load PyTorch: {e}")

    try:
        # 导入 Qt 应用
        from PyQt6.QtWidgets import QApplication
        from PyQt6.QtCore import Qt
        
        # 设置高DPI缩放
        QApplication.setHighDpiScaleFactorRoundingPolicy(
            Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
        )

        # 创建应用实例
        app = QApplication(sys.argv)
        app.setApplicationName("PNNE")
        app.setOrganizationName("PNNE")
        app.setApplicationVersion("0.1.0")

        # 导入节点类型（触发注册）
        logger.info("Registering node types...")
        try:
            # 导入核心节点模块以触发装饰器注册
            import core.nodes
            logger.info(f"Registered {len(core.nodes.__all__)} node types")
        except Exception as e:
            logger.warning(f"Failed to import core nodes: {e}")
            # 尝试单独导入节点模块（不依赖 PyTorch DLL）
            logger.info("Attempting to import node modules individually...")
            try:
                # 先导入基类和注册表
                from core.base.node import Node, NodeCategory
                from core.base.node_registry import register_node
                
                # 导入根节点（不依赖 PyTorch）
                from core.nodes.context.root_nodes import ObjRootNode, VisRootNode, TrainRootNode
                logger.info("Registered root nodes")
                
                # 尝试导入 NN 节点
                try:
                    from core.nodes.nn.linear_node import LinearNode
                    from core.nodes.nn.activation_nodes import ReLUNode, SigmoidNode, TanhNode
                    logger.info("Registered NN nodes")
                except Exception as nn_e:
                    logger.warning(f"Failed to import NN nodes: {nn_e}")
                
                # 尝试导入训练节点
                try:
                    from core.nodes.training.loss_nodes import CrossEntropyLossNode, MSELossNode
                    from core.nodes.training.optimizer_nodes import SGDNode, AdamNode
                    from core.nodes.training.save_model_node import SaveModelNode
                    from core.nodes.training.load_model_node import LoadModelNode
                    logger.info("Registered training nodes")
                except Exception as train_e:
                    logger.warning(f"Failed to import training nodes: {train_e}")
                
                # 尝试导入控制流节点
                try:
                    from core.nodes.control.foreach_nodes import ForEachBeginNode, ForEachDataNode, ForEachEndNode
                    logger.info("Registered control flow nodes (ForEach)")
                except Exception as ctrl_e:
                    logger.warning(f"Failed to import control nodes: {ctrl_e}")
                
                # 尝试导入子网络节点
                try:
                    from core.nodes.subnet.subnet_node import SubnetNode
                    logger.info("Registered subnet node")
                except Exception as subnet_e:
                    logger.warning(f"Failed to import subnet node: {subnet_e}")
                
                # 尝试导入数据节点
                try:
                    from core.nodes.data.dataset_nodes import MNISTNode, CIFAR10Node
                    logger.info("Registered data nodes")
                except Exception as data_e:
                    logger.warning(f"Failed to import data nodes: {data_e}")
                    
            except Exception as fallback_e:
                logger.error(f"Failed to import any node modules: {fallback_e}")

        # 导入主窗口（延迟导入以加快启动速度）
        logger.info("Loading main window...")
        try:
            from ui.main_window import MainWindow
            
            # 创建主窗口
            window = MainWindow()
            
            # 如果指定了文件，打开它
            if args.file:
                file_path = Path(args.file)
                if file_path.exists():
                    logger.info(f"Opening file: {file_path}")
                    # TODO: 实现文件加载逻辑
                    # window.open_project(file_path)
                else:
                    logger.warning(f"File not found: {file_path}")
            
            # 显示主窗口
            window.show()
            
            logger.info("Application started successfully")
            
            # 进入事件循环
            sys.exit(app.exec())
            
        except ImportError as e:
            logger.error(f"Failed to import main window: {e}")
            logger.info("UI module not yet implemented. Running in headless mode.")
            
            # 无头模式 - 用于测试核心功能
            logger.info("=" * 60)
            logger.info("PNNE Core System Test")
            logger.info("=" * 60)
            
            # 测试核心模块
            from core.base import (
                Node, NodeGraph, NodeRegistry, NodeFactory,
                Pin, PinType, Connection
            )
            
            logger.info("✓ Successfully imported core modules")
            logger.info("✓ Core base system is operational")
            
            # 显示注册的节点类型
            registry = NodeRegistry()
            node_types = registry.get_all_node_types()
            logger.info(f"Registered node types: {len(node_types)}")
            
            logger.info("=" * 60)
            logger.info("UI module will be available in the next phase.")
            logger.info("=" * 60)
            
            return 0

    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
        return 0

    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
