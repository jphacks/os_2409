import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from edge import PIRMotionDetector, MotorController
from edge.config import MOTOR_TURNS, MOTION_SENSOR_PIN, PIR_SETTINGS
import time

def main():
    try:
        print("\n=== プログラム開始 ===")
        print(f"設定値確認:")
        print(f"MOTION_SENSOR_PIN: {MOTION_SENSOR_PIN}")
        print(f"PIR_SETTINGS: {PIR_SETTINGS}")
        print("===================\n")

        monitor = PIRMotionDetector()
        print("PIRMotionDetectorを初期化しました")
        
        monitor.start_monitoring()
        print("モニタリングを開始しました")

        while True:
            # 検知開始の判定
            if monitor.is_detection_started():
                print("検知を開始しました")
                
            # 検知終了の判定
            if monitor.is_detection_ended():
                print(f"検知を終了しました - 滞在時間: {monitor.get_current_duration()}秒")
                
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nプログラムを終了します")
    except Exception as e:
        print(f"予期せぬエラーが発生しました: {e}")
    finally:
        if 'monitor' in locals():
            monitor.cleanup()
            print("クリーンアップ完了")

if __name__ == "__main__":
    main()