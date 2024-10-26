import lgpio # type: ignore
from time import sleep, time
import requests # type: ignore
from datetime import datetime

# POSTリクエストの設定
SERVER_URL = "http://your-server-url/api/endpoint"  # あなたのサーバーURLに変更してください

def send_post_notification(message):
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

# GPIOハンドルを開く
h = lgpio.gpiochip_open(4)
# GPIO 18を入力として設定
lgpio.gpio_claim_input(h, 18)

# カウンターの初期化
detection_count = 0    # 検出カウント
no_detection_count = 0 # 非検出カウント
timer_running = False  # タイマー状態
start_time = 0        # 開始時間

try:
    while True:
        sleep(0.1)  # センサーの読み取り間隔を0.1秒に設定
        
        # センサーの状態を読み取り
        if lgpio.gpio_read(h, 18) == 1:
            detection_count += 1
            no_detection_count = 0
            print("Motion detected!", detection_count)
            
            # 5回連続で検出された場合、タイマー開始
            if detection_count >= 5 and not timer_running:
                start_message = "Motion detected: Timer started!"
                print(start_message)
                send_post_notification(start_message)
                timer_running = True
                start_time = time()
                detection_count = 0  # カウントをリセット
        else:
            no_detection_count += 1
            detection_count = 0
            print("No motion", no_detection_count)
            
            # タイマー動作中に5回連続で非検出の場合、計測終了
            if no_detection_count >= 5 and timer_running:
                elapsed_time = time() - start_time
                stop_message = f"Motion stopped: Timer ended after {elapsed_time:.2f} seconds"
                print(stop_message)
                send_post_notification(stop_message)
                print("Sensor monitoring ended.")
                break

except KeyboardInterrupt:
    print("\nProgram terminated by user")
finally:
    # GPIOをクリーンアップ
    lgpio.gpiochip_close(h)