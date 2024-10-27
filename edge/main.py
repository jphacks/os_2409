import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from edge import PIRMotionDetector, MotorController
from edge.config import MOTOR_TURNS
import time

def main():
    try:
        detector = PIRMotionDetector()
        motion_completed = detector.monitor()
        print(f"Monitoring completed: {'Successfully' if motion_completed else 'Interrupted'}")

        if motion_completed:
            motor = MotorController()
            motor.setup()
            
            print("Rotating clockwise...")
            motor.rotate(MOTOR_TURNS, clockwise=True)
            
            time.sleep(1)
            
            print("Rotating counter-clockwise...")
            motor.rotate(MOTOR_TURNS, clockwise=False)
            
            motor.cleanup()
            print("Motor sequence completed")

    except KeyboardInterrupt:
        print("\nProgram terminated by user")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()