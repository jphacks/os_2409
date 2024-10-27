import lgpio # type: ignore
import time
from datetime import datetime

class PIRSensor:
    def __init__(self, pir_pin=18):
        # lgpioの初期化
        self.h = lgpio.gpiochip_open(0)
        
        # ピン設定
        self.pir_pin = pir_pin
      
        
        # ピンのモード設定
        lgpio.gpio_claim_input(self.h, self.pir_pin)
        
        # 検知状態の追跡用変数
        self.last_detection_time = 0
        self.person_present = False
        self.presence_timeout = 3.0  # 不在判定までの秒数（調整可能）

    def monitor_presence(self):
        try:
            print("PIRセンサーの監視を開始します...")
            print("Ctrl+Cで終了します")
            print(f"PIRセンサーピン: {self.pir_pin}")
            print(f"LEDピン: {self.led_pin}")
            
            # センサーの初期化待ち
            time.sleep(2)
            
            while True:
                current_time = time.time()
                # PIRセンサーの状態を読み取り
                pir_state = lgpio.gpio_read(self.h, self.pir_pin)
                
                if pir_state:  # 人を検知
                    self.last_detection_time = current_time
                    if not self.person_present:
                        self.person_present = True
                      
                        detection_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        print(f"人を検知しました - {detection_time}")             
                # 一定時間検知がない場合
                elif (current_time - self.last_detection_time > self.presence_timeout 
                      and self.person_present):
                    self.person_present = False
                    absence_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    print(f"人がいなくなりました - {absence_time}")
                
                time.sleep(0.1)  # CPU負荷軽減のための短い待機
                
        except KeyboardInterrupt:
            print("\nプログラムを終了します")
        finally:
            # クリーンアップ          
            lgpio.gpiochip_close(self.h)
    
    def set_timeout(self, seconds):
        """不在判定までの時間を設定"""
        self.presence_timeout = seconds
        print(f"不在判定までの時間を{seconds}秒に設定しました")

    def cleanup(self):
        """リソースの解放"""
        try:
            lgpio.gpiochip_close(self.h)
            print("GPIOをクリーンアップしました")
        except:
            pass

def main():
    # PIRセンサーのインスタンスを作成
    # ピン番号は実際の接続に合わせて変更してください
    pir = PIRSensor(pir_pin=17, led_pin=18)
    
    try:
        # 必要に応じて不在判定時間を調整（例: 5秒）
        pir.set_timeout(5.0)
        
        # モニタリング開始
        pir.monitor_presence()
    finally:
        pir.cleanup()

if __name__ == "__main__":
    main()