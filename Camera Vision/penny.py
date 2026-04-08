import time
import numpy as np
import cv2
from picamera2 import Picamera2 as picam
from gpiozero import Button # Requires: pip install gpiozero

# 1. Setup Camera and Button
cam = picam()
cam.configure(cam.create_preview_configuration(main={"format": "RGB888", "size": (640, 480)}))
cam.start()

# Initialize button on GPIO 17 with a 3-second hold time
# This replaces all 'q' key functionality
btn = Button(17, hold_time=3) 

def prepHSV():
    lowHSV = np.array([255, 255, 255])
    highHSV = np.array([0, 0, 0])
    
    print("Calibrating... Align object and click button to finish.")
    
    # Reset calibration loop
    while True:
        frame = cam.capture_array()
        hsv_frame = cv2.cvtColor(frame, cv2.COLOR_RGB2HSV)
        
        x, y, w, h = 310, 230, 20, 20
        roi = hsv_frame[y:y+h, x:x+w]
        
        lowHSV = np.minimum(lowHSV, roi.min(axis=(0, 1)))
        highHSV = np.maximum(highHSV, roi.max(axis=(0, 1)))
        
        cv2.rectangle(frame, (x, y), (x+h, y+w), (0, 255, 0), 2)
        cv2.imshow("Calibration", frame)
        cv2.waitKey(1) # Needed to update the window

        # Replace 'q' with a button press
        if btn.is_pressed:
            # Wait for release so it doesn't trigger the next loop immediately
            btn.wait_for_release() 
            break
            
    cv2.destroyAllWindows()
    return lowHSV, highHSV

# Initial Calibration
lower, upper = prepHSV()

print("Running... Hold button for 3s to recalibrate. Click to exit.")

try:
    while True:
        # 1. Handle Button Logic
        if btn.is_pressed:
            lower, upper = prepHSV()

        frame = cam.capture_array()
        hsv = cv2.cvtColor(frame, cv2.COLOR_RGB2HSV)
        mask = cv2.inRange(hsv, lower, upper)
        
        # Drawing & Logic
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if contours:
            largest_cnt = max(contours, key=cv2.contourArea)
            bx, by, bw, bh = cv2.boundingRect(largest_cnt)
            cv2.rectangle(frame, (bx, by), (bx + bw, by + bh), (0, 255, 0), 2)

            # Centerline Logic
            obj_x = bx + (bw // 2)
            if obj_x <= 220:
                cv2.rectangle(frame, (50, 50), (150, 150), (0, 255, 0), -1) 
            elif obj_x >= 420:
                cv2.rectangle(frame, (490, 50), (590, 150), (0, 0, 255), -1)

        cv2.imshow("Tracking", frame)
        cv2.waitKey(1)
        
        # Break loop on 'q' key
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

finally:
    cam.stop()
    cv2.destroyAllWindows()