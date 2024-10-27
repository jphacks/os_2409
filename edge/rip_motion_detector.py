import time
from datetime import datetime
import lgpio # type: ignore
import threading
from edge.config import MOTION_SENSOR_PIN, PIR_SETTINGS

class PIRMotionDetector:
    def __init__(self):
        self.pir_pin = MOTION_SENSOR_PIN
        self.presence_timeout = PIR_SETTINGS
        self.h = lgpio.gpiochip_open(0)
        lgpio.gpio_claim_input(self.h, self.pir_pin)
        
        self.person_present = False
        self.last_detection_time = 0
        
        self.current_session_start = None
        self.detection_started = False
        self.detection_ended = False
        self.current_duration = 0
        
        # 監視スレッド制御用のフラグ
        self.monitoring = False
        self.monitor_thread = None

    def start_monitoring(self):
        """監視を開始する"""
        if not self.monitoring:
            self.monitoring = True
            self.monitor_thread = threading.Thread(target=self.monitor_presence)
            self.monitor_thread.daemon = True  # メインスレッド終了時に一緒に終了
            self.monitor_thread.start()

    def stop_monitoring(self):
        """監視を停止する"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join()

    def monitor_presence(self):
        try:
            print("PIRセンサーの監視を開始します...")
            print("Ctrl+Cで終了します")
            
            time.sleep(2)  # センサーの初期化待ち
            
            while self.monitoring:
                current_time = time.time()
                pir_state = lgpio.gpio_read(self.h, self.pir_pin)
                
                # フラグのリセット
                self.detection_started = False
                self.detection_ended = False
                
                if pir_state == 1:  # 人を検知
                    self.last_detection_time = current_time
                    if not self.person_present:
                        self.person_present = True
                        self.detection_started = True
                        self.current_session_start = datetime.now()
                
                # 一定時間検知がない場合
                elif (current_time - self.last_detection_time > self.presence_timeout 
                      and self.person_present):
                    self.person_present = False
                    self.detection_ended = True
                    
                    if self.current_session_start:
                        self.current_duration = (datetime.now() - self.current_session_start).total_seconds()
                        self.current_session_start = None
                
                # 現在進行中のセッションの滞在時間を更新
                if self.person_present and self.current_session_start:
                    self.current_duration = (datetime.now() - self.current_session_start).total_seconds()
                
                time.sleep(0.1)
                
        except Exception as e:
            print(f"監視中にエラーが発生しました: {e}")
        finally:
            self.monitoring = False

    def is_detection_started(self):
        """人の検知が開始されたかどうかを返す"""
        return self.detection_started

    def is_detection_ended(self):
        """人の検知が終了したかどうかを返す"""
        return self.detection_ended

    def get_current_duration(self):
        """現在の滞在時間（秒）を返す"""
        return int(self.current_duration)

    def cleanup(self):
        """リソースの解放"""
        self.stop_monitoring()
        try:
            lgpio.gpiochip_close(self.h)
        except:
            pass