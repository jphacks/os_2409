from edge.config import MOTOR_TURNS
from .motion_detector import MotionDetector
from .motor_controller import MotorController
import time

def main():
    try:
        # モーション検知の実行
        detector = MotionDetector()
        motion_completed = detector.monitor()

        if motion_completed:
            # モーター制御の実行
            motor = MotorController()
            motor.setup()
            
            # 時計回りに回転
            print("Rotating clockwise...")
            motor.rotate(MOTOR_TURNS, clockwise=True)
            
            # 1秒待機
            time.sleep(1)
            
            # 反時計回りに回転
            print("Rotating counter-clockwise...")
            motor.rotate(MOTOR_TURNS, clockwise=False)
            
            motor.cleanup()
            print("Motor sequence completed")

    except KeyboardInterrupt:
        print("\nProgram terminated by user")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()