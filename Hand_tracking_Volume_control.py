import cv2   # Importing OpenCV module
import mediapipe as mp  # Importing Mediapipe module for hand tracking
import time  # Importing time module to calculate fps
import numpy as np
import Hand_tracking_module as htm
import math
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

 # Capture webcam
vid = cv2.VideoCapture(0)

# Initialize frame timing
prev_time = 0

# Create hand tracking object
detector = htm.HandTracking()

# Retrieve the default audio output device (speakers)
devices = AudioUtilities.GetSpeakers()

# Get the volume interface
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)

volume = cast(interface, POINTER(IAudioEndpointVolume))

# Get the volume range
min_volume, max_volume, _ = volume.GetVolumeRange()
volume.SetMasterVolumeLevel(-50, None)
vol = 0
volbar = 450
volper = 0
while True:
    ret, frame = vid.read()  # Capture frame
    if not ret:
        break

    # Find hands and positions in the frame
    frame = detector.find_hands(frame)
    frame, positions = detector.find_position(frame, True, [4, 8])  # Track specific landmarks

    if positions:
        # print(positions)  # Print landmark positions
        x1, y1 = positions[0][0], positions[0][1]
        x2, y2 = positions[1][0], positions[1][1]
        cx, cy = (x1 + x2) // 2 , (y1 + y2) // 2
        cv2.circle(frame, (cx, cy), 8, (0, 0, 255), -1)
        cv2.line(frame, (x1, y1), (x2, y2), (0,0,255), 3)
        
        length = math.hypot(x2 - x1, y2 - y1)
        # print(length)
        
        if length < 20:
            cv2.circle(frame, (cx, cy), 8, (0, 255, 0), -1)
    
        vol = np.interp(int(length), (30, 100), (-63.5, 0))
        volbar = np.interp(int(length), (30, 100), (450, 100))
        volper = np.interp(int(length), (30, 100), (0, 100))
        # print(int(length), vol)
        volume.SetMasterVolumeLevel(vol, None)
        
    cv2.rectangle(frame, (30, 450), (50, 100), (0,0,255), 2)
    cv2.rectangle(frame, (30, 450), (50, int(volbar)), (0,0,255), -1)
    cv2.putText(frame, f'{int(volper)}%', (25, 475), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    # Calculate FPS
    current_time = time.time()
    fps = 1 / max((current_time - prev_time), 1e-6)  # Avoid division by 0
    prev_time = current_time

    # Display FPS on frame
    cv2.putText(frame, f'FPS: {int(fps)}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    # Display the frame
    cv2.imshow('Hand Tracking', frame)

    # Break loop with 'q' key
    if cv2.waitKey(1) == ord('q'):
        break

# Release resources
vid.release()
cv2.destroyAllWindows()
