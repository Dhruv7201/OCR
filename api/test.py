import io
import base64
from PIL import Image
import cv2
import numpy as np
import easyocr

# get the image from the file
image = Image.open('image.jpg')
image_np = np.array(image)

# Perform OCR on the image
reader = easyocr.Reader(['en'], gpu=True, model_storage_directory='./models', user_network_directory='./user_network', recognizer='Transformer', verbose=False, download_enabled=False, detector='TextDetection')
recognition_results = reader.readtext(image_np)

# Print OCR results
for result in recognition_results:
    print(result)

# show image with bounding boxes
for result in recognition_results:
    # Extract coordinates
    box_coordinates = result[0]
    top_left = tuple(box_coordinates[0])
    bottom_right = tuple(box_coordinates[2])
    text = result[1]
    font = cv2.FONT_HERSHEY_SIMPLEX
    image_np = cv2.rectangle(image_np, top_left, bottom_right, (0, 255, 0), 5)

# save the image to disk
cv2.imwrite('image_with_bounding_boxes.jpg', image_np)
