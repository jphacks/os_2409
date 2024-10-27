import time
from datetime import datetime
import lgpio # type: ignore

class PresenceMonitor:
    def __init__(self, pir_pin):
        self.pir_pin = pir_pin
        self.h = lgpio.gpiochip_open(0)
        lgpio.gpio_claim_input(self.h, self.pir_pin)
        
        self.presence_timeout = 30
        self.person_present = False
        self.last_detection_time = 0
        
        self.current_session_start = None
        self.detection_started = False
        self.detection_ended = False
        self.current_duration = 0

    def monitor_presence(self):
        try:
            print("PIRセンサーの監視を開始します...")
            print("Ctrl+Cで終了します")
            
            time.sleep(2)  # センサーの初期化待ち
            
            while True:
                current_time = time.time()
                pir_state = lgpio.gpio_read(self.h, self.pir_pin)
                
                # フラグのリセット
                self.detection_started = False
                self.detection_ended = False
                
                if pir_state:  # 人を検知
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
                
        except KeyboardInterrupt:
            print("\nプログラムを終了します")
            if self.person_present and self.current_session_start:
                self.current_duration = (datetime.now() - self.current_session_start).total_seconds()
            
        finally:
            self.cleanup()

    def is_detection_started(self):
        return self.detection_started

    def is_detection_ended(self):
        return self.detection_ended

    def get_current_duration(self):
        return int(self.current_duration)

    def set_timeout(self, seconds):
        self.presence_timeout = seconds

    def cleanup(self):
        """リソースの解放"""
        try:
            lgpio.gpiochip_close(self.h)
        except:
            pass