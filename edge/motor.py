import lgpio # type: ignore
import time

# GPIOチップハンドルを開く
h = lgpio.gpiochip_open(4)

# ULN2003のピン定義
IN1 = 23  # GPIO23
IN2 = 24  # GPIO24
IN3 = 25  # GPIO25
IN4 = 17  # GPIO17に変更（以前のGPIO8から変更）

# ステッピングシーケンス（半ステップ駆動）
SEQUENCE = [
    [1, 0, 0, 0],
    [1, 1, 0, 0],
    [0, 1, 0, 0],
    [0, 1, 1, 0],
    [0, 0, 1, 0],
    [0, 0, 1, 1],
    [0, 0, 0, 1],
    [1, 0, 0, 1]
]

def setup():
    # 出力ピンとして設定
    lgpio.gpio_claim_output(h, IN1)
    lgpio.gpio_claim_output(h, IN2)
    lgpio.gpio_claim_output(h, IN3)
    lgpio.gpio_claim_output(h, IN4)

def rotate(turns, clockwise=True, delay=0.001):
    """
    指定した回転数だけモーターを回転
    :param turns: 回転数
    :param clockwise: True=時計回り、False=反時計回り
    :param delay: ステップ間の待機時間（秒）
    """
    # 1回転 = 8ステップ/周期 * 64周期 = 512ステップ
    steps = int(512 * turns)
    
    # 回転方向に応じてシーケンスを設定
    sequence = SEQUENCE if clockwise else SEQUENCE[::-1]
    
    # モーター回転
    for _ in range(steps):
        for step in sequence:
            lgpio.gpio_write(h, IN1, step[0])
            lgpio.gpio_write(h, IN2, step[1])
            lgpio.gpio_write(h, IN3, step[2])
            lgpio.gpio_write(h, IN4, step[3])
            time.sleep(delay)

def cleanup():
    # すべてのピンをLOWに設定
    lgpio.gpio_write(h, IN1, 0)
    lgpio.gpio_write(h, IN2, 0)
    lgpio.gpio_write(h, IN3, 0)
    lgpio.gpio_write(h, IN4, 0)
    
    # ピンを解放
    lgpio.gpio_free(h, IN1)
    lgpio.gpio_free(h, IN2)
    lgpio.gpio_free(h, IN3)
    lgpio.gpio_free(h, IN4)
    
    # GPIOチップを閉じる
    lgpio.gpiochip_close(h)

if __name__ == '__main__':
    try:
        setup()
        # 2回転（時計回り）
        rotate(2, clockwise=True)
        time.sleep(1)  # 1秒待機
        cleanup()
    except KeyboardInterrupt:
        cleanup()