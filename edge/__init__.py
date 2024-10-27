__version__ = '1.0.0'

# 主要なクラスとモジュールを直接インポートできるようにする
from .rip_motion_detector import PIRMotionDetector
from .motor_controller import MotorController
from . import config

# 全てのパブリックインターフェースを定義
__all__ = [
    'MotionDetector',
    'MotorController',
    'config'
]