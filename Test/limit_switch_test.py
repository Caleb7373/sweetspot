import time
import RPi.GPIO as GPIO

LEFT_LIMIT_PIN = 17   
RIGHT_LIMIT_PIN = 12

GPIO.setmode(GPIO.BCM)
GPIO.setup(LEFT_LIMIT_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(RIGHT_LIMIT_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
LIMIT_TRIGGER = GPIO.HIGH  # Changed to HIGH assuming Normally Closed wiring

print(f"Left Pin (17):  {'HIGH' if GPIO.input(LEFT_LIMIT_PIN) else 'LOW'}")
print(f"Right Pin (12): {'HIGH' if GPIO.input(RIGHT_LIMIT_PIN) else 'LOW'}")
print(f"Trigger Logic is set to: {'HIGH' if LIMIT_TRIGGER == GPIO.HIGH else 'LOW'}")

GPIO.cleanup()