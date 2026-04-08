import time
import numpy as np
import cv2
from picamera2 import Picamera2 as picam
cam = picam()

cam.configure(cam.create_preview_configuration(main={"format": "RGB888", "size": (640, 480)}))

cam.start()

def prepHSV():
    # Initialize with extreme values
    lowHSV = np.array([255, 255, 255])
    highHSV = np.array([0, 0, 0])
    
    print("Calibrating... Press 'q' to finish.")
    
    while True:
        frame = cam.capture_array()
        hsv_frame = cv2.cvtColor(frame, cv2.COLOR_RGB2HSV)
        
        # Define ROI (Center 20x20 pixels)
        x, y, w, h = 310, 230, 20, 20
        roi = hsv_frame[y:y+h, x:x+w]
        
        # Update min/max from the entire box at once
        lowHSV = np.minimum(lowHSV, roi.min(axis=(0, 1)))
        highHSV = np.maximum(highHSV, roi.max(axis=(0, 1)))
        
        # Draw the box on the RGB frame for the user
        # Note: cv2 uses BGR for colors, so (0, 255, 0) is green
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
        cv2.imshow("Calibrating - Center Object", frame)
        
        # Break loop on 'q' key
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
            
    print(f"Calibration Done! lowHSV: {lowHSV}, highHSV: {highHSV}")
    cv2.destroyAllWindows()
    return lowHSV, highHSV

lower = upper = []
lower, upper = prepHSV()

while True:
    frame = cam.capture_array()
    cv2.imwrite("Camera.jpg", frame)
    hsv = cv2.cvtColor(frame, cv2.COLOR_RGB2HSV)
    mask  = cv2.inRange(hsv, lower, upper)
    cv2.imwrite("mask.jpg", mask)
    result = cv2.bitwise_and(frame, frame, mask=mask)
    cv2.imwrite("final_img.jpg", result)
    cv2.imshow("Calibrating - Center Object", result)
    
    # Break loop on 'q' key
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
cv2.destroyAllWindows()
