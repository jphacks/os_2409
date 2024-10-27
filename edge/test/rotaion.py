import lgpio  # type: ignore
import time
from typing import Tuple

class RotaryEncoder:
    def __init__(self, chip_handle: int):
        self.h = chip_handle
        # GPIOピンの設定
        self.sia_pin = 16  # SIA
        self.sib_pin = 19  # SIB
        self.sw_pin = 26   # SW
        self.pulses_per_rev = 20
        self.counter = 0
        self.last_time = time.time()
        self.last_state: Tuple[int, int] = (0, 0)
        
        # ピンを入力として設定
        lgpio.gpio_claim_input(self.h, self.sia_pin)
        lgpio.gpio_claim_input(self.h, self.sib_pin)
        lgpio.gpio_claim_input(self.h, self.sw_pin)
        
        # プルアップ抵抗を設定
        lgpio.gpio_set_pull_up_down(self.h, self.sia_pin, lgpio.LGPIO_PULL_UP)
        lgpio.gpio_set_pull_up_down(self.h, self.sib_pin, lgpio.LGPIO_PULL_UP)
        lgpio.gpio_set_pull_up_down(self.h, self.sw_pin, lgpio.LGPIO_PULL_UP)
        
        # コールバックの設定
        self.cb_sia = lgpio.callback(self.h, self.sia_pin, lgpio.BOTH_EDGES, self._encoder_callback)
        self.cb_sib = lgpio.callback(self.h, self.sib_pin, lgpio.BOTH_EDGES, self._encoder_callback)
        self.cb_sw = lgpio.callback(self.h, self.sw_pin, lgpio.FALLING_EDGE, self._switch_callback)

    def _encoder_callback(self, chip: int, gpio: int, level: int, tick: int) -> None:
        # SIAとSIBの現在の状態を取得
        current_state = (
            lgpio.gpio_read(self.h, self.sia_pin),
            lgpio.gpio_read(self.h, self.sib_pin)
        )
        
        # 状態が変化した場合のみ処理
        if current_state != self.last_state:
            # 回転方向の判定
            if (self.last_state == (0, 0) and current_state == (0, 1)) or \
               (self.last_state == (0, 1) and current_state == (1, 1)) or \
               (self.last_state == (1, 1) and current_state == (1, 0)) or \
               (self.last_state == (1, 0) and current_state == (0, 0)):
                self.counter += 1
            else:
                self.counter -= 1

            # 1回転完了時の処理
            if abs(self.counter) % self.pulses_per_rev == 0:
                current_time = time.time()
                time_diff = current_time - self.last_time
                rpm = abs(60 / time_diff) if time_diff > 0 else 0
                direction = "CW" if self.counter > 0 else "CCW"
                print(f"Rotation: {abs(self.counter) // self.pulses_per_rev}, "
                      f"Direction: {direction}, RPM: {rpm:.2f}")
                self.last_time = current_time

            self.last_state = current_state

    def _switch_callback(self, chip: int, gpio: int, level: int, tick: int) -> None:
        print("Switch pressed - Reset counter")
        self.counter = 0

    def cleanup(self) -> None:
        """リソースの解放"""
        self.cb_sia.cancel()
        self.cb_sib.cancel()
        self.cb_sw.cancel()
        lgpio.gpio_free(self.h, self.sia_pin)
        lgpio.gpio_free(self.h, self.sib_pin)
        lgpio.gpio_free(self.h, self.sw_pin)

def main():
    # GPIOチップハンドルを開く
    h = lgpio.gpiochip_open(4)  # あなたの環境に合わせて4を使用

    # ロータリーエンコーダーの初期化
    encoder = RotaryEncoder(h)

    try:
        print("Monitoring rotation... Press Ctrl+C to exit")
        while True:
            time.sleep(0.1)

    except KeyboardInterrupt:
        print("\nProgram terminated by user")
    finally:
        encoder.cleanup()
        lgpio.gpiochip_close(h)

if __name__ == "__main__":
    main()
