import time
from datetime import datetime
import lgpio # type: ignore
import threading
from edge.config import MOTION_SENSOR_PIN, PIR_SETTINGS

class PIRMotionDetector:
    def __init__(self):
        # 設定値の確認を追加
        print("\n=== 設定値の確認 ===")
        print(f"MOTION_SENSOR_PIN: {MOTION_SENSOR_PIN}")
        print(f"PIR_SETTINGS: {PIR_SETTINGS}")
        print("==================\n")

        self.pir_pin = MOTION_SENSOR_PIN
        self.presence_timeout = PIR_SETTINGS
        self.h = lgpio.gpiochip_open(0)
        lgpio.gpio_claim_input(self.h, self.pir_pin)
        
        # デバッグ情報を出力
        print(f"初期化: PIN={self.pir_pin}, TIMEOUT={self.presence_timeout}")
        
        self.person_present = False
        self.last_detection_time = 0
        
        self.current_session_start = None
        self.detection_started = False
        self.detection_ended = False
        self.current_duration = 0
        
        self.monitoring = False
        self.monitor_thread = None

    def start_monitoring(self):
        """監視を開始する"""
        if not self.monitoring:
            self.monitoring = True
            self.monitor_thread = threading.Thread(target=self.monitor_presence)
            self.monitor_thread.daemon = True
            self.monitor_thread.start()
            print("モニタリングスレッドを開始しました")

    def stop_monitoring(self):
        """監視を停止する"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join()
            print("モニタリングスレッドを停止しました")

    def monitor_presence(self):
        try:
            print("\n=== モニタリング開始 ===")
            print("PIRセンサーの監視を開始します...")
            print(f"PIRセンサーピン: {self.pir_pin}")
            print(f"不在判定時間: {self.presence_timeout}秒")
            print("=====================\n")
            
            # センサーの初期化と初期状態の確認
            time.sleep(2)
            initial_state = lgpio.gpio_read(self.h, self.pir_pin)
            print(f"センサーの初期状態: {initial_state}")
            
            while self.monitoring:
                current_time = time.time()
                try:
                    pir_state = lgpio.gpio_read(self.h, self.pir_pin)
                    # センサーの値の変化をデバッグ出力
                    if pir_state:
                        print(f"センサー状態: HIGH ({pir_state})")
                    
                    # フラグのリセット
                    self.detection_started = False
                    self.detection_ended = False
                    
                    if pir_state == 1:  # 人を検知
                        self.last_detection_time = current_time
                        if not self.person_present:
                            print("動きを検知しました")
                            self.person_present = True
                            self.detection_started = True
                            self.current_session_start = datetime.now()
                    
                    # 一定時間検知がない場合
                    elif (current_time - self.last_detection_time > self.presence_timeout 
                          and self.person_present):
                        print("タイムアウトによる検知終了")
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
                    print(f"センサー読み取りエラー: {e}")
                    time.sleep(1)  # エラー時は少し待機
                
        except Exception as e:
            print(f"監視中にエラーが発生しました: {e}")
        finally:
            self.monitoring = False
            print("監視を終了します")

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
            print("GPIOをクリーンアップしました")
        except:
            pass