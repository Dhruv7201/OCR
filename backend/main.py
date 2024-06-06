import os
from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from PIL import Image
import pymongo
import io
import base64
import re
import easyocr
import cv2
import numpy as np
import time
import spacy
from datetime import datetime
from ultralytics import YOLO

model = YOLO('./model/best.pt')


# Load Spacy NLP model once at startup
nlp = spacy.load('en_core_web_md')

app = FastAPI()

# Allow CORS for all origins
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

class VideoFrame(BaseModel):
    frame: str

# Initialize the EasyOCR reader once at startup with GPU enabled and use downloaded model
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


def filter_text(results, min_text_length=5, confidence_threshold=0.40):
    filtered_results = []
    text = ''
    for result in results:
        text = result[1]
        confidence = result[2]
        if confidence > confidence_threshold:
            filtered_results.append(result)
    return filtered_results

def extract_text(image_data):
    image = image_data
    image_np = cv2.cvtColor(np.array(image), cv2.COLOR_BGR2GRAY)
    recognition_results = reader.readtext(image_np)
    print(recognition_results)
    return recognition_results

import re
from datetime import datetime

def extract_batch_number(text):
    with open('text.txt', 'a') as f:
        f.write(text + '\n')
    # Initialize variables
    batch_no = None
    mfg = None
    exp = None

    return batch_no, mfg, exp
    
    # Patterns to identify dates in different formats
    date_patterns = [
        r'\b\d{2}/\d{4}\b',  # Matches MM/YYYY
        r'\b\d{2}-\d{4}\b',  # Matches MM-YYYY
        r'\b\d{2}.\d{4}\b',  # Matches MM.YYYY or any other separator
        r'\b\d{4}\b',         # Matches YYYY
        r'\b\w{3}-\d{2}\b',   # Matches MMM-YY
        r'\b\w{3} \d{2}\b',   # Matches MMM YY
    ]
    

    # Extract dates
    date_matches = []
    for pattern in date_patterns:
        date_matches.extend(re.findall(pattern, text))
    
    # Parse dates using datetime to determine MFG and EXP
    parsed_dates = []
    for date_str in date_matches:
        try:
            # Try different date formats
            if '/' in date_str:
                date_obj = datetime.strptime(date_str, '%m/%Y')
            elif '-' in date_str:
                date_obj = datetime.strptime(date_str, '%m-%Y')
            elif '.' in date_str:
                date_obj = datetime.strptime(date_str, '%m.%Y')
            else:
                date_obj = datetime.strptime(date_str, '%Y')
            
            parsed_dates.append(date_obj)
        except ValueError:
            # If parsing fails, skip this date
            continue

    # Remove duplicates from parsed dates
    unique_dates = []
    for date in parsed_dates:
        if date not in unique_dates:
            unique_dates.append(date)

    # Assign MFG and EXP based on unique dates
    if unique_dates:
        mfg = unique_dates[0].strftime('%m/%Y')
        if len(unique_dates) > 1:
            exp = unique_dates[1].strftime('%m/%Y')

    # Extract batch number
    batch_no = text.split(' ')[0]

    
    return batch_no, mfg, exp

@app.post("/api/send-frame", response_model=dict)
async def send_frame(frame: VideoFrame, background_tasks: BackgroundTasks):
    start = time.time()
    image_data = frame.frame.split(",")[1]
    img = Image.open(io.BytesIO(base64.b64decode(image_data)))
    model_results = model.predict(source=img, conf=0.5)

    for result in model_results:
        if result:
            if result.names:
                # Access the bounding box coordinates in xyxy format
                boxes = result.boxes
                for box in boxes:
                    cv2.imwrite('image.jpg', result.plot())
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    # Crop the image using the bounding box coordinates
                    cropped_img = img.crop((x1, y1, x2, y2))
                    # Save the cropped image
                    cropped_img.save('cropped_img.jpg')
                    # Extract text from the cropped image
                    text = extract_text(cropped_img)
                    # Filter the text
                    filtered_text = filter_text(text)
                    # cv2.imwrite('image.jpg', result.plot())
                    # Convert filtered text to a single string
                    filtered_text_str = ' '.join([t[1] for t in filtered_text])
                    # Extract the batch number from the filtered text
                    batch_no, mfg, exp = extract_batch_number(filtered_text_str)
                    print('--------------------------------Time taken:', time.time() - start)
                    return {'productName': '', 'batchNumber': batch_no, 'mfgDate': mfg, 'expDate': exp}



@app.post("/api/save-data")
async def save_data(request: Request):
    response = await request.json()
    response = response['data']
    connection = pymongo.MongoClient("mongodb://192.168.0.156:27017/")
    db = connection["productData"]
    collection = db["productData"]
    for item in response:
        collection.insert_one(item)

    return {"status": "success"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run('main:app', host='0.0.0.0', port=3001, reload=True, workers=5)


