import lgpio # type: ignore
import time
from typing import List, Tuple

class RotaryEncoder:
    def __init__(self, chip_handle: int, sia_pin: int, sib_pin: int, sw_pin: int):
        self.h = chip_handle
        self.sia_pin = sia_pin
        self.sib_pin = sib_pin
        self.sw_pin = sw_pin
        self.pulses_per_rev = 20
        self.counter = 0
        self.last_time = time.time()
        self.last_state: Tuple[int, int] = (0, 0)
        
        # ピンの設定（プルアップ付きの入力として設定）
        for pin in [sia_pin, sib_pin, sw_pin]:
            lgpio.gpio_claim_input(self.h, pin)
            # プルアップ設定を gpio_set_pull_up_down に変更
            lgpio.gpio_set_pull_up_down(self.h, pin, lgpio.SET_PULL_UP)
        
        # コールバックの設定
        lgpio.gpio_set_edge(self.h, sia_pin, lgpio.BOTH_EDGES)
        lgpio.gpio_set_edge(self.h, sib_pin, lgpio.BOTH_EDGES)
        lgpio.gpio_set_edge(self.h, sw_pin, lgpio.FALLING_EDGE)
        
        self.cb_sia = lgpio.callback(self.h, sia_pin, lgpio.BOTH_EDGES, self._encoder_callback)
        self.cb_sib = lgpio.callback(self.h, sib_pin, lgpio.BOTH_EDGES, self._encoder_callback)
        self.cb_sw = lgpio.callback(self.h, sw_pin, lgpio.FALLING_EDGE, self._switch_callback)

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
        for pin in [self.sia_pin, self.sib_pin, self.sw_pin]:
            lgpio.gpio_free(self.h, pin)

def main():
    # GPIOチップハンドルを開く
    h = lgpio.gpiochip_open(4)
    
    # ロータリーエンコーダーの初期化
    encoder = RotaryEncoder(
        chip_handle=h,
        sia_pin=16,  # GPIO16
        sib_pin=19,  # GPIO19
        sw_pin=26    # GPIO26
    )
    
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