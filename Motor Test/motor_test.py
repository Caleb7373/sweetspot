import RPi.GPIO as GPIO
import time

# --- Pins ---
STEP_PIN   = 23
DIR_PIN    = 24
ENABLE_PIN = 25
LIMIT_PIN  = 8    # NC: HIGH=clear, LOW=pause

# --- Constants ---
FULL_STEPS_PER_REV  = 200
GEAR_RATIO          = 18
OUTPUT_STEPS_PER_REV = FULL_STEPS_PER_REV * GEAR_RATIO # 3600
MICROSTEP_MULTIPLIER = 1 

def setup():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(STEP_PIN, GPIO.OUT, initial=GPIO.LOW)
    GPIO.setup(DIR_PIN, GPIO.OUT, initial=GPIO.LOW)
    GPIO.setup(ENABLE_PIN, GPIO.OUT, initial=GPIO.HIGH)
    GPIO.setup(LIMIT_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def step(steps, direction=1, delay=0.005): # Slowed default delay
    GPIO.output(DIR_PIN, GPIO.HIGH if direction > 0 else GPIO.LOW)
    for _ in range(abs(steps)):
        while GPIO.input(LIMIT_PIN) == GPIO.LOW:
            time.sleep(0.01) # Pause while button is held
        
        GPIO.output(STEP_PIN, GPIO.HIGH)
        time.sleep(delay)
        GPIO.output(STEP_PIN, GPIO.LOW)
        time.sleep(delay)

def rotate_degrees(degrees, rpm=2.0, direction=1): # Lowered default RPM
    steps_per_rev = OUTPUT_STEPS_PER_REV * MICROSTEP_MULTIPLIER
    total_steps = int((degrees / 360.0) * steps_per_rev)
    # At 2 RPM, delay will be roughly 0.004s per pulse
    steps_per_sec = (rpm / 60.0) * steps_per_rev
    pulse_delay = 1.0 / (2.0 * steps_per_sec) 
    step(total_steps, direction, pulse_delay)

if __name__ == "__main__":
    try:
        setup()
        GPIO.output(ENABLE_PIN, GPIO.LOW) # Enable
        print("Testing motor at slow speed (2 RPM)...")
        rotate_degrees(90, rpm=2.0, direction=1)
    except KeyboardInterrupt:
        pass
    finally:
        GPIO.output(ENABLE_PIN, GPIO.HIGH)
        GPIO.cleanup()
