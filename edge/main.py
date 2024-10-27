import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from edge import PIRMotionDetector, MotorController
from edge.config import MOTOR_TURNS
import time

def main():
    try:
        monitor = PIRMotionDetector()
        monitor.start_monitoring()
        print("PIRセンサーの監視を開始します...")

        while True:
            # 検知開始の判定
            if monitor.is_detection_started():
                print("検知を開始しました")
                
            # 検知終了の判定
            if monitor.is_detection_ended():
                print(f"検知を終了しました - 滞在時間: {monitor.get_current_duration()}秒")
                
            time.sleep(1)  # 1秒ごとにチェック


        # if monitor.detection_ended:
        #     motor = MotorController()
        #     motor.setup()
            
        #     print("Rotating clockwise...")
        #     motor.rotate(MOTOR_TURNS, clockwise=True)
            
        #     time.sleep(1)
            
        #     print("Rotating counter-clockwise...")
        #     motor.rotate(MOTOR_TURNS, clockwise=False)
            
        #     motor.cleanup()
        #     print("Motor sequence completed")

    except KeyboardInterrupt:
        print("\nプログラムを終了します")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()