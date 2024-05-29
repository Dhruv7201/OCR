import cv2
from pyzbar.pyzbar import decode
import time

def read_barcode(image):
    # Convert the image to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Use OpenCV to find barcodes in the image
    barcodes = decode(gray)

    # If barcodes are found, decode them
    for barcode in barcodes:
        # Extract barcode data and format
        barcode_data = barcode.data.decode('utf-8')
        barcode_type = barcode.type

        # Draw a rectangle around the barcode area
        x, y, w, h = barcode.rect
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)

        # Put the barcode data and type on the image
        text = f"{barcode_data}"
        cv2.putText(image, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        print(f"Found {barcode_type} barcode: {barcode_data}")
    return image

# Capture video from the default camera
cap = cv2.VideoCapture(0)

while True:
    # Read frame from the camera
    ret, frame = cap.read()

    # Stop the loop if no frame is captured
    if not ret:
        break

    # Call the function to read barcodes in the frame
    frame = read_barcode(frame)

    # Display the frame
    cv2.imshow('Barcode Reader', frame)

    # Break the loop if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the video capture object and close the OpenCV window
cap.release()
cv2.destroyAllWindows()
