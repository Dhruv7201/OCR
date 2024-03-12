from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from PIL import Image
import pymongo
import io
import base64
import re
import easyocr

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




@app.post("/api/send-frame", response_model=dict)
async def send_frame(frame: VideoFrame, background_tasks: BackgroundTasks):
    # Decode the base64 image data to bytes
    image_data = frame.frame.split(',')[1].encode('utf-8')
    image = Image.open(io.BytesIO(base64.b64decode(image_data)))

        # Perform OCR on the image
    reader = easyocr.Reader(['en'], gpu=True, model_storage_directory='./models', user_network_directory='./user_network', recognizer='lite')
    recognition_results = reader.readtext(image)

    # logic to find batch number from list of text
    batch_text = ''
    if recognition_results:
        for result in recognition_results:
            batch_text = batch_text + result[1]
    pattern = r"B\.*No\.*\s*([A-Z0-9\-]*)"
    pattern1 = r"Batch\s*\,*No\.*:*;*\s*:*\s*([A-Z0-9\-]*)"
    match = re.search(pattern, batch_text)
    match1 = re.search(pattern1, batch_text)

    if match or match1:
        # if batch number is found then return the batch number
        filtered_results = recognition_results
    else:
        # if not batch number then filter the text for product name
        filtered_results = filter_text(recognition_results)
    text1 = ''
    if filtered_results:
        for result in filtered_results:
            text1 = text1 + result[1]
    try:
        filtered_text1 = re.search(r'\b[A-Za-z]+\s*[A-Za-z0-9&\s,()]+\s[A-Za-z]+\b', text1).group()
        filtered_text1 = re.sub(r'\n', '', filtered_text1)
        filtered_text1 = re.sub(',', '', filtered_text1)
        pattern = r"B\.*No\.*\s*([A-Z0-9\-]*[0-9])"
        pattern1 = r"Batch\s*\,*No\.*:*;*\s*:*\s*([0-9\-]*)"
        match = re.search(pattern, text1)
        match1 = re.search(pattern1, text1)

        if match or match1:
            if match:
                BatchNumber = match.group(1)
                if BatchNumber == '':
                    result = text1
                    result = result.split()
                    batch_no_index = result.index('B.No.' or 'B.No' or 'B.No.:' or 'B.No:' or 'B.No')
                    # Print the next four-list members
                    next_four_members = result[batch_no_index + 1:batch_no_index + 5]
                    next_four_members = ' '.join(next_four_members)
                    for i in next_four_members:
                        next_four_members = next_four_members.replace(',', '')
                        next_four_members = re.sub(r'[\u0900-\u097F]+', '', next_four_members)
                        next_four_members = re.search(r'\b([A-Za-z]+\d+)\b', next_four_members).group()
                    return {'productName': '', 'batchNumber': next_four_members}
                return {'productName': '', 'batchNumber': BatchNumber}
            elif match1:
                BatchNumber = match1.group(1)
                if BatchNumber == '':
                    result = text1
                    result = result.split()
                    batch_no_index = result.index('Batch' or 'BatchNo' or 'BatchNo.' or 'BatchNo:' or 'BatchNo,' or
                                                'BatchNo: ' or 'BatchNo;')
                    next_four_members = result[batch_no_index + 1:batch_no_index + 5]
                    next_four_members = ' '.join(next_four_members)
                    print('0000000000000000000000000000',next_four_members)
                    for i in next_four_members:
                        next_four_members = next_four_members.replace(',', '')
                        next_four_members = re.sub(r'[\u0900-\u097F]+', '', next_four_members)
                        print(next_four_members)
                        next_four_members = re.search(r'\b([A-Za-z]+-\d+)\b', next_four_members).group()
                    print('111111111111111111',next_four_members)
                    return {'productName': '', 'batchNumber': next_four_members}
                return {'productName': '', 'batchNumber': BatchNumber}
        else:
            return {'productName': filtered_text1, 'batchNumber': ''}
    except AttributeError as e:
        return {'productName': '', 'batchNumber': ''}




@app.post("/api/save-data")
async def save_data(request: Request):
    response = await request.json()
    response = response['data']
    connection = pymongo.MongoClient("mongodb://localhost:27017/")
    db = connection["productData"]
    collection = db["productData"]
    for i in response:
        collection.insert_one(i)

    return {"status": "success"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run('main:app', host='0.0.0.0', port=3001, reload=True)