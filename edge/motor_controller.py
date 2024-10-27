import lgpio # type: ignore
import time
from .config import *

class MotorController:
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

    def __init__(self):
        self.h = lgpio.gpiochip_open(4)
        self.pins = [
            MOTOR_PINS["IN1"],
            MOTOR_PINS["IN2"],
            MOTOR_PINS["IN3"],
            MOTOR_PINS["IN4"]
        ]

    def setup(self):
        for pin in self.pins:
            lgpio.gpio_claim_output(self.h, pin)

    def rotate(self, turns, clockwise=True, delay=MOTOR_DELAY):
        steps = int(512 * turns)
        sequence = self.SEQUENCE if clockwise else self.SEQUENCE[::-1]
        
        for _ in range(steps):
            for step in sequence:
                for pin, value in zip(self.pins, step):
                    lgpio.gpio_write(self.h, pin, value)
                time.sleep(delay)

    def cleanup(self):
        for pin in self.pins:
            lgpio.gpio_write(self.h, pin, 0)
            lgpio.gpio_free(self.h, pin)
        lgpio.gpiochip_close(self.h)