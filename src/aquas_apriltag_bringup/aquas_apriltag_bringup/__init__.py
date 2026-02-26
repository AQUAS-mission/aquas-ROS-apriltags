#!/usr/bin/env python3
import cv2
import numpy as np
from apriltag import apriltag

def main():
    capture = cv2.VideoCapture(0)
    if not capture.isOpened():
        print("Error: Could not open camera")
        return

    # INITIALIZE ONCE OUTSIDE THE LOOP
    detector = apriltag("tag36h11") 

    while True:
        ret, frame = capture.read()
        if not ret:
            break
            
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # USE THE PRE-INITIALIZED DETECTOR
        detections = detector.detect(gray)
        
        # Optional: Overlay detections on frame to see them
        for d in detections:
            print(f"Detected Tag ID: {d}")


    capture.release()
if __name__ == "__main__":
    main()



