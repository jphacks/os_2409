import lgpio # type: ignore
from time import sleep, time
import requests # type: ignore
from datetime import datetime
from .config import *

class MotionDetector:
    def __init__(self):
        self.h = lgpio.gpiochip_open(4)
        lgpio.gpio_claim_input(self.h, MOTION_SENSOR_PIN)
        self.detection_count = 0
        self.no_detection_count = 0
        self.timer_running = False
        self.start_time = 0

    def send_post_notification(self, message):
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

    def monitor(self):
        try:
            while True:
                sleep(SENSOR_INTERVAL)
                
                if lgpio.gpio_read(self.h, MOTION_SENSOR_PIN) == 1:
                    self.detection_count += 1
                    self.no_detection_count = 0
                    print("Motion detected!", self.detection_count)
                    
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
        lgpio.gpiochip_close(self.h)