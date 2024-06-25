from PIL import Image
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
from pydantic import BaseModel
import os

model = YOLO('./model/best.pt')


# Load Spacy NLP model once at startup
nlp = spacy.load('en_core_web_md')

class VideoFrame(BaseModel):
    frame: str

counter = 0

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



def extract_batch_number(text):
    with open('text.txt', 'a') as f:
        f.write(text + '\n')

    # Initialize variables
    batch_no = None
    mfg = None
    exp = None

    # Patterns to identify dates in different formats
    date_patterns = [
        r'\b\d{2}/\d{4}\b',
        r'\b\d{2}-\d{4}\b',
        r'\b\d{2}.\d{4}\b',
        r'\b\w{3}-\d{2}\b',
        r'\b\w{3} \d{2}\b',
        r'\b\w{3}.\d{2}\b',
        r'\b\w{3}.\d{4}\b',
    ]

    # Extract dates
    date_matches = []
    for pattern in date_patterns:
        matches = re.findall(pattern, text)
        date_matches.extend(matches)

    # Parse dates using datetime to determine MFG and EXP
    parsed_dates = []
    for date_str in date_matches:
        try:
            # Handle different date formats
            if re.match(r'\b\d{2}/\d{4}\b', date_str):
                date = datetime.strptime(date_str, '%m/%Y')
            elif re.match(r'\b\d{2}-\d{4}\b', date_str):
                date = datetime.strptime(date_str, '%m-%Y')
            elif re.match(r'\b\d{2}.\d{4}\b', date_str):
                date = datetime.strptime(date_str, '%m.%Y')
            elif re.match(r'\b\w{3}-\d{2}\b', date_str):
                date = datetime.strptime(date_str, '%b-%y')
            elif re.match(r'\b\w{3} \d{2}\b', date_str):
                date = datetime.strptime(date_str, '%b %y')
            elif re.match(r'\b\w{3}.\d{2}\b', date_str):
                date = datetime.strptime(date_str, '%b.%y')
            elif re.match(r'\b\w{3}.\d{4}\b', date_str):
                date = datetime.strptime(date_str, '%b.%Y')
            else:
                # Use spaCy to parse the date
                doc = nlp(date_str)
                for ent in doc.ents:
                    if ent.label_ == 'DATE':
                        date = ent.text
                        break
            parsed_dates.append(date)
        except ValueError:
            continue

    # Remove duplicates from parsed dates
    unique_dates = list(set(parsed_dates))
    unique_dates.sort()

    # Assign MFG and EXP based on unique dates
    if unique_dates:
        mfg = unique_dates[0].strftime('%m/%Y')
        if len(unique_dates) > 1:
            exp = unique_dates[1].strftime('%m/%Y')

    # Extract batch number
    batch_no_match = re.search(r'[a-zA-Z]+[0-9]+', text)
    if batch_no_match:
        batch_no = batch_no_match.group()

    return batch_no, mfg, exp

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
    return recognition_results


def send_frame(frame: VideoFrame):
    start = time.time()
    image_data = frame['frame']
    img = Image.open(io.BytesIO(base64.b64decode(image_data)))
    model_results = model.predict(source=img, conf=0.5)
    global counter
    for result in model_results:
        if result:
            if result.names:
                # Access the bounding box coordinates in xyxy format
                boxes = result.boxes
                if boxes:
                    counter = counter + 1
                    box = max(boxes, key=lambda box: box.conf.item())
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
                    
                    # make rectangle on the image on original image
                    plt_img = img.copy()
                    plt_img = np.array(plt_img)
                    cv2.rectangle(plt_img, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    # display text on the image
                    font = cv2.FONT_HERSHEY_SIMPLEX
                    cv2.putText(plt_img, f'Batch No: {batch_no}', (x1, y1 - 10), font, 0.5, (0, 255, 0), 2)
                    # display time took to process the image
                    cv2.putText(plt_img, f'Time taken: {time.time() - start:.2f} seconds', (10, 20), font, 0.5, (0, 255, 0), 2)
                    plt_img = Image.fromarray(plt_img)
                    buffered = io.BytesIO()
                    plt_img.save(buffered, format="JPEG")
                    img_str = base64.b64encode(buffered.getvalue()).decode()
                    return img_str
    # return original image
    buffered = io.BytesIO()
    img.save(buffered, format="JPEG")
    img_str = base64.b64encode(buffered.getvalue()).decode()

    return img_str
    

img_list = os.listdir('/home/ethics/workspace/medicine/')
print('***************************************length:', len(img_list))
for image in img_list:
    img = Image.open(f'/home/ethics/workspace/medicine/{image}')
    frame = np.array(img)
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    frame = Image.fromarray(frame)
    frame = frame.resize((640, 480))
    buffered = io.BytesIO()
    frame.save(buffered, format="JPEG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    frame = {'frame': img_str}
    img = send_frame(frame)
    img = base64.b64decode(img)
    # display the image with opencv
    cv2.waitKey(0)
print('***************************************counter:', counter)