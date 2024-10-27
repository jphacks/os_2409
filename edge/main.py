import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from edge import PIRMotionDetector, MotorController
from edge.config import MOTOR_TURNS, MOTION_SENSOR_PIN, PIR_SETTINGS
import time

def handle_detection_start():
    """検知開始時の処理"""
    print("\n=== 人を検知しました ===")
    print(f"検知時刻: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    # ここに検知開始時の追加処理を記述

def handle_detection_end(duration):
    """検知終了時の処理"""
    print("\n=== 検知を終了します ===")
    print(f"終了時刻: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"滞在時間: {duration}秒")
    # ここに検知終了時の追加処理を記述

def main():
    try:
        print("\n=== PIRモーションセンサー監視システム ===")
        print(f"センサーピン: {MOTION_SENSOR_PIN}")
        print(f"タイムアウト時間: {PIR_SETTINGS}秒")
        print("=====================================\n")

        monitor = PIRMotionDetector()
        monitor.start_monitoring()
        
        print("メインループを開始します...")
        while True:
            try:
                # 検知開始の判定
                if monitor.is_detection_started():
                    handle_detection_start()
                
                # 検知終了の判定
                if monitor.is_detection_ended():
                    handle_detection_end(monitor.get_current_duration())
                
                time.sleep(0.1)  # CPU負荷軽減のための短い待機
                
            except Exception as e:
                print(f"処理中にエラーが発生しました: {e}")
                time.sleep(1)  # エラー時は少し長めに待機
            
    except KeyboardInterrupt:
        print("\n\n=== プログラムを終了します ===")
    except Exception as e:
        print(f"\n予期せぬエラーが発生しました: {e}")
    finally:
        if 'monitor' in locals():
            monitor.cleanup()
            print("クリーンアップが完了しました")
            print("===============================")

if __name__ == "__main__":
    main()