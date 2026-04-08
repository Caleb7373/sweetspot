import RPi.GPIO as GPIO
import time

PUL_PIN = 23
DIR_PIN = 24

def test_rotation():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(PUL_PIN, GPIO.OUT, initial=GPIO.HIGH)
    GPIO.setup(DIR_PIN, GPIO.OUT, initial=GPIO.HIGH)
    
    print("Testing slow rotation... Disconnect EN wires for this test.")
    
    # Send 1600 pulses (1 motor turn at microstep 8)
    for _ in range(1600):
        GPIO.output(PUL_PIN, GPIO.LOW)
        time.sleep(0.001)  # 1ms High
        GPIO.output(PUL_PIN, GPIO.HIGH)
        time.sleep(0.001)  # 1ms Low

if __name__ == "__main__":
    try:
        test_rotation()
    finally:
        GPIO.cleanup()
