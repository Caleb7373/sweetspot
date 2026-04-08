import time
import numpy as np
import cv2
from picamera2 import Picamera2 as picam
cam = picam()

cam.configure(cam.create_preview_configuration(main={"format": "RGB888", "size": (640, 480)}))

cam.start()

low = high = []

'''takes 10 frames over 10s and determines upper and lower HSV values of the center pixel'''
def prepHSV(lowHSV, highHSV):
    lowHSV = [255,255,255]
    highHSV = [0,0,0]
    for i in range(10):
        frame = cam.capture_array()
        #at the center pixel 320, 240, but intputted as y, x
        hsv = cv2.cvtColor(frame, cv2.COLOR_RGB2HSV)[240,320]
        print(hsv)
        for i in range(3):
            if hsv[i] < lowHSV[i]:
                lowHSV[i] = hsv[i]
            if hsv[i] > highHSV[i]:
                highHSV[i] = hsv[i]
        time.sleep(1)
    print(f"lowHSV: {lowHSV} highHSV: {highHSV}")
#prepHSV(low, high)

#while True:
    #frame = cam.capture_array()
    #cv2.imshow("Camera", frame)
    
frame = cam.capture_array()
#height = frame.shape[0]
#width = frame.shape[1]
#print(f"Height: {height} Width: {width}")
cv2.imwrite("Camera.jpg", frame)

hsv = cv2.cvtColor(frame, cv2.COLOR_RGB2HSV)
#####################################################
lower = np.array([8,244,177])
upper = np.array([32,255,235])
'''failed to use value from prepHSV() to directly make lower and upper mask values
TODO next: implement direct lower/upper mask value thing - error: low and high arrays contain elements of: np.uint8(18).
TODO after: display live video feed from camera w annotated region in center and use that region to get lowHSV and highHSV. Could do this in the real thing too if a button is pressed to recalibrate it, but make sure to reset it to hard coded values when machine restarts.'''
#lower = np.array(low)
#upper = np.array(high)
#####################################################
mask  = cv2.inRange(hsv, lower, upper)

cv2.imwrite("mask.jpg", mask)

result = cv2.bitwise_and(frame, frame, mask=mask)

cv2.imwrite("final_img.jpg", result)

#cv2.imshow('frame',frame)
#cv2.imshow('mask',mask)
#time.sleep(5)

