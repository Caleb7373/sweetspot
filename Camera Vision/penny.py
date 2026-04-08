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
    #cv2.imshow("Calibrating - Center Object", result)
        # 1. Find all contours in the mask
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if contours:
        # 2. Find the largest contour by area
        largest_cnt = max(contours, key=cv2.contourArea)
        
        # 3. Get the bounding box coordinates (x, y, width, height)
        bx, by, bw, bh = cv2.boundingRect(largest_cnt)
        
        # 4. Draw the rectangle on your BGR frame (Green, thickness 2)
        cv2.rectangle(frame, (bx, by), (bx + bw, by + bh), (0, 255, 0), 2)
        
        # Optional: Add text label
        cv2.putText(frame, "Target", (bx, by - 10), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        # 1. Calculate the horizontal center of the object
        obj_center_x = bx + (bw // 2)
        cam_midline = 320

        # 2. Check offsets (100 pixels left or right of 320)
        # Left: 320 - 100 = 220 | Right: 320 + 100 = 420
        if obj_center_x <= 220:
            # Flash Green Square in top-left
            cv2.rectangle(frame, (50, 50), (150, 150), (0, 255, 0), -1) 
        elif obj_center_x >= 420:
            # Flash Red Square in top-right
            cv2.rectangle(frame, (490, 50), (590, 150), (0, 0, 255), -1)
        
    cv2.imshow("Tracking", frame)
    
    # Break loop on 'q' key
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
cv2.destroyAllWindows()
