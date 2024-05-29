import os
from fastapi import FastAPI, Request
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
from test import detect_box
import time
import spacy


nlp = spacy.load('en_core_web_md') 

app = FastAPI()

# Allow CORS for all origins
origins = [
    "*"
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

class VideoFrame(BaseModel):
    frame: str


def filter_text(results, min_text_length=5, confidence_threshold=0.75):
    filtered_results = []
    for result in results:
        print(result)
        text = result[1]
        confidence = result[2]
        # Adjust the criteria as needed
        if len(text) >= min_text_length and confidence > confidence_threshold:
            filtered_results.append(result)
    return filtered_results


def extract_text(image_data):
    
    # Convert the bytes to an image
    image = Image.open(io.BytesIO(base64.b64decode(image_data)))

    image_np = cv2.cvtColor(np.array(image), cv2.COLOR_BGR2GRAY)

    # Initialize the EasyOCR reader
    reader = easyocr.Reader(
        ['en'], 
        gpu=True, 
        download_enabled=True, 
    )
    recognition_results = reader.readtext(image_np)
    return recognition_results


def extract_batch_number(text):
    # check for batch number with nlp
    tokens = nlp(text)
    batch_no = None
    for ent in tokens.ents:
        text = text.replace(ent.text, '')
    
    print(text)

    pattern = r"B\.*No\.*\s*([A-Z0-9\-]*)"
    pattern1 = r"Batch\s*\,*No\.*:*;*\s*:*\s*([A-Z0-9\-]*)"
    match = re.search(pattern, text)
    match1 = re.search(pattern1, text)
    if match:
        batch_no = match.group(1)
    elif match1:
        batch_no = match1.group(1)
    else:
        batch_no = None

    dates = r'\d{2}[/-]\d{4}'

    # get all dates from the text and put 1st in mfg and 2nd in exp
    found_dates = re.findall(dates, text)
    mfg = None
    exp = None
    if found_dates and len(found_dates) > 1:
        mfg = found_dates[0]
        exp = found_dates[1]
    else:
        mfg = None
        exp = None
    print(batch_no, mfg, exp)
    return batch_no, mfg, exp


@app.post("/api/send-frame", response_model=dict)
async def send_frame(frame: VideoFrame):
    start = time.time()
    product_img = 'product.png'
    batch_img = 'batch.png'
    flag = detect_box(frame.frame.split(',')[1].encode('utf-8'), product_img, batch_img)
    if flag == 1:
        recognition_results = extract_text(frame.frame.split(',')[1].encode('utf-8'))
        product_text = filter_text(recognition_results)
        text = ''

        product_text = text.join([result[1] for result in product_text])
        product_text = re.search(r'\b[A-Za-z]+\s*[A-Za-z0-9&\s,()]+\s[A-Za-z]+\b', product_text).group(0)
        product_text = re.sub(r'\n', '', product_text)
        product_text = re.sub(',', '', product_text)
        print("---------------------------time---------------------------", time.time()-start)
        return {'productName': product_text, 'batchNumber': '', 'mfgDate': "", 'expDate': ""}
    elif flag == 2:
        recognition_results = extract_text(frame.frame.split(',')[1].encode('utf-8'))
        text = ''
        if recognition_results:
            for result in recognition_results:
                text = text + ' ' + result[1]
        batch_number, mfg, exp = extract_batch_number(text)
        print("---------------------------time---------------------------", time.time()-start)
        return {'productName': '', 'batchNumber': batch_number, 'mfgDate': mfg, 'expDate': exp}
    else:
        print("---------------------------time---------------------------", time.time()-start)
        return {'productName': '', 'batchNumber': '', 'mfgDate': "", 'expDate': ""}
        




@app.post("/api/save-data")
async def save_data(request: Request):
    response = await request.json()
    response = response['data']
    connection = pymongo.MongoClient("mongodb://192.168.0.156:27017/")
    db = connection["productData"]
    collection = db["productData"]
    for i in response:
        collection.insert_one(i)

    return {"status": "success"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run('main:app', host='0.0.0.0', port=3001, reload=True, workers=5)