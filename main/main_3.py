import time
import RPi.GPIO as GPIO
import numpy as np
import cv2
from picamera2 import Picamera2 as picam

# --- PIN CONFIGURATION ---
STEP_PIN = 23
DIR_PIN = 24
ENA_PIN = 25
SHOOT_PIN = 18
SWITCH_PIN = 6 
LET_USER_SHOOT = 1
LEFT_LIMIT_PIN = 17   
RIGHT_LIMIT_PIN = 12

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(STEP_PIN, GPIO.OUT)
GPIO.setup(DIR_PIN, GPIO.OUT)
GPIO.setup(ENA_PIN, GPIO.OUT)
GPIO.setup(SHOOT_PIN, GPIO.OUT, initial=GPIO.LOW)

# Inputs with Pull-Up Resistors
GPIO.setup(SWITCH_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP) 
GPIO.setup(LEFT_LIMIT_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(RIGHT_LIMIT_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

GPIO.output(SHOOT_PIN, GPIO.LOW)
GPIO.output(ENA_PIN, GPIO.LOW)  

# --- THE LOGIC FIX ---
# If your code prints 'Limit Reached' when it shouldn't, change these to GPIO.LOW
LIMIT_TRIGGER = GPIO.HIGH  # Changed to HIGH assuming Normally Closed wiring

# --- HELPER FUNCTIONS ---
def move(direction):
    """
    Checks the limit pin before and during motor steps.
    """
    limit_pin = LEFT_LIMIT_PIN if direction else RIGHT_LIMIT_PIN
    
    # Pre-check: Is the limit already hit?
    if GPIO.input(limit_pin) == LIMIT_TRIGGER:
        print(f"{'Left' if direction else 'Right'} Limit Reached! (Blocked)")
        return
        
    GPIO.output(DIR_PIN, direction)
    
    for _ in range(5000):
        # Continuous check during movement
        if GPIO.input(limit_pin) == LIMIT_TRIGGER:
            print("Limit hit during movement!")
            break
            
        GPIO.output(STEP_PIN, GPIO.HIGH)
        time.sleep(0.0001)
        GPIO.output(STEP_PIN, GPIO.LOW)
        time.sleep(0.0001)
    time.sleep(0.01)

def trigger_action():
    print("Launch ball!")
    GPIO.output(SHOOT_PIN, GPIO.HIGH)   
    time.sleep(1)  
    GPIO.output(SHOOT_PIN, GPIO.LOW)    
    time.sleep(LET_USER_SHOOT)

# --- CAMERA SETUP ---
cam = picam()
cam.configure(cam.create_preview_configuration(main={"format": "RGB888", "size": (640, 480)}))
cam.start()

# --- HSV VALUES (Fill these in with yours) ---
lower = np.array([15, 249, 183])
upper = np.array([18, 255, 212])

# --- STATE MANAGEMENT ---
system_active = False  
still_time = time.perf_counter()

# INITIAL SENSOR CHECK
print("\n--- INITIAL SENSOR STATES ---")
print(f"Left Pin (17):  {'HIGH' if GPIO.input(LEFT_LIMIT_PIN) else 'LOW'}")
print(f"Right Pin (12): {'HIGH' if GPIO.input(RIGHT_LIMIT_PIN) else 'LOW'}")
print(f"Trigger Logic is set to: {'HIGH' if LIMIT_TRIGGER == GPIO.HIGH else 'LOW'}")
print("-----------------------------\n")

try:
    while True:
        if not system_active:
            if GPIO.input(SWITCH_PIN) == GPIO.LOW:
                print("Start Button Pressed!")
                system_active = True
                still_time = time.perf_counter()
                time.sleep(0.5) 

        if system_active:
            frame = cam.capture_array()
            hsv = cv2.cvtColor(frame, cv2.COLOR_RGB2HSV)
            mask = cv2.inRange(hsv, lower, upper)
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            if contours:
                largest_cnt = max(contours, key=cv2.contourArea)
                bx, by, bw, bh = cv2.boundingRect(largest_cnt)
                obj_center_x = bx + (bw // 2)

                if obj_center_x <= 220:
                    move(True)  # Left
                    still_time = time.perf_counter() 
                elif obj_center_x >= 420:
                    move(False) # Right
                    still_time = time.perf_counter()
                else:
                    # Centered
                    if time.perf_counter() - still_time > 3:
                        trigger_action()
                        still_time = time.perf_counter() 
            else:
                still_time = time.perf_counter()

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

except KeyboardInterrupt:
    print("\nStopping...")
finally:
    GPIO.output(SHOOT_PIN, GPIO.LOW)
    GPIO.cleanup()
    cam.stop()
    cv2.destroyAllWindows()
