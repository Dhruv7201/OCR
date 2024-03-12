import cv2
import numpy as np
import time

def detect_biggest_box(frame, canny_threshold_low, canny_threshold_high):
    # Convert the frame to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Use edge detection (e.g., Canny) to highlight edges
    edges = cv2.Canny(gray, canny_threshold_low, canny_threshold_high)

    # Find contours in the edged image
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Find the contour with the maximum area
    max_contour = max(contours, key=cv2.contourArea, default=None)

    if max_contour is not None:
        # Extract bounding box from the largest contour
        x, y, w, h = cv2.boundingRect(max_contour)
        return [(x, y, w, h)]
    else:
        return []

def draw_boxes(frame, boxes):
    for (x, y, w, h) in boxes:
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

# Open a connection to the webcam (assuming the first webcam, index 0)
cap = cv2.VideoCapture(0)

# Set Canny edge detection thresholds
canny_threshold_low = 100
canny_threshold_high = 150

# Capture a frame every 5 seconds
capture_interval = 0.1  # seconds
last_capture_time = time.time()

while True:
    # Calculate time since the last capture
    current_time = time.time()
    elapsed_time = current_time - last_capture_time

    # Capture frame if the elapsed time is greater than the interval
    if elapsed_time >= capture_interval:
        # Capture frame
        ret, frame = cap.read()

        # Detect the biggest box in the frame with specified Canny thresholds
        boxes = detect_biggest_box(frame, canny_threshold_low, canny_threshold_high)

        # Draw boxes on the frame
        draw_boxes(frame, boxes)

        # Display the resulting frame
        cv2.imshow('Webcam Feed with Biggest Box', frame)

        # Crop and save the detected biggest box
        if boxes:
            x, y, w, h = boxes[0]
            roi = frame[y:y + h, x:x + w]
            cv2.imshow('Biggest Box ROI', roi)
            cv2.imwrite('biggest_box_roi.png', roi)

        # Update the last capture time
        last_capture_time = current_time

    # Break the loop if 'q' key is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the webcam and close all OpenCV windows
cap.release()
cv2.destroyAllWindows()
