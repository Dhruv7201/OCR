
import cv2
import easyocr
import numpy as np
import io
import base64
from PIL import Image
from ultralytics import YOLO

img = cv2.imread("./image.png")

# encode image in base64
_, img_encoded = cv2.imencode('.png', img)
img_encoded = base64.b64encode(img_encoded).decode('utf-8')


img = Image.open(io.BytesIO(base64.b64decode(img_encoded)))


model = YOLO('./model/best.pt')
reader = easyocr.Reader(
    ['en'], 
    gpu=True, 
    model_storage_directory='model',
    download_enabled=False,
    detector=True,
    recognizer=True,
    verbose=False,
    cudnn_benchmark=True,
    quantize=True
)

model_results = model.predict(source=img, conf=0.5)

for result in model_results:
        if result:
            if result.names:
                # Access the bounding box coordinates in xyxy format
                boxes = result.boxes
                for box in boxes:
                    cv2.imwrite("plot.png", result.plot())
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    # Crop the image using the bounding box coordinates
                    cropped_img = img.crop((x1, y1, x2, y2))
                    cv2.imwrite("cropped.png", np.array(cropped_img))
                    # cv2.imshow("cropped", cropped_img)
                    recognition_results = reader.readtext(np.array(cropped_img))
                    for text in recognition_results:
                        print(text[1])
                        print(text[2])