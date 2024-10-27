import lgpio # type: ignore
from time import sleep, time
import requests # type: ignore
from datetime import datetime
from .config import *

class PIRMotionDetector:
    def __init__(self, pir_pin=MOTION_SENSOR_PIN):
        # lgpioの初期化
        self.h = lgpio.gpiochip_open(4)
        self.pir_pin = pir_pin
        
        # ピンのモード設定
        lgpio.gpio_claim_input(self.h, self.pir_pin)
        
        # カウンターと状態変数
        self.detection_count = 0
        self.no_detection_count = 0
        self.timer_running = False
        self.start_time = 0

    def send_post_notification(self, message):
        """サーバーに通知を送信"""
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            payload = {
                "message": message,
                "timestamp": timestamp
            }
            response = requests.post(SERVER_URL, json=payload)
            print(f"POST notification sent: {message}")
            print(f"Server response: {response.status_code}")
        except Exception as e:
            print(f"Failed to send POST notification: {e}")

    def monitor(self) -> bool:
        """
        モーション検知を監視
        Returns:
            bool: モーション検知シーケンスが完了した場合True、
                 　ユーザーによる中断の場合False
        """
        try:
            print("Motion monitoring started...")
            
            while True:
                sleep(SENSOR_INTERVAL)
                
                # PIRセンサーの状態を読み取り
                if lgpio.gpio_read(self.h, self.pir_pin) == 1:
                    self.detection_count += 1
                    self.no_detection_count = 0
                    print("Motion detected!", self.detection_count)
                    
                    # 検知閾値に達し、タイマーが動いていない場合
                    if self.detection_count >= DETECTION_THRESHOLD and not self.timer_running:
                        start_message = "Motion detected: Timer started!"
                        print(start_message)
                        # TODO: エンドポイント完成後コメントアウト
                        # self.send_post_notification(start_message)
                        self.timer_running = True
                        self.start_time = time()
                        self.detection_count = 0
                
                else:
                    self.no_detection_count += 1
                    self.detection_count = 0
                    print("No motion", self.no_detection_count)
                    
                    # 不検知閾値に達し、タイマーが動いている場合
                    if self.no_detection_count >= NO_DETECTION_THRESHOLD and self.timer_running:
                        elapsed_time = time() - self.start_time
                        stop_message = f"Motion stopped: Timer ended after {elapsed_time:.2f} seconds"
                        print(stop_message)
                        self.send_post_notification(stop_message)
                        print("Sensor monitoring ended.")
                        return True  # モーション検知シーケンス完了
                
        except KeyboardInterrupt:
            print("\nProgram terminated by user")
            return False
        finally:
            self.cleanup()

    def cleanup(self):
        """リソースの解放"""
        try:
            lgpio.gpiochip_close(self.h)
            print("GPIO cleaned up")
        except:
            pass

