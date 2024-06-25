from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from PIL import Image
import io
import base64
import easyocr
import cv2
import numpy as np
import time
from ultralytics import YOLO
from methods import extract_details, check_same_image
from methods import extract_text, filter_text
from methods import picknote_saving_logic



model = YOLO('./model/best.pt')



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
    picknote: str
    token: str

# Initialize the EasyOCR reader once at startup with GPU enabled and use downloaded model
reader = easyocr.Reader(
    ['en'],
    gpu=True,
    model_storage_directory='./model',
)


@app.post("/api/send-frame", response_model=dict)
async def send_frame(data: VideoFrame):
    start = time.time()
    image_data = data.frame.split(",")[1] if data.frame.startswith('data:image') else data.frame
    img = Image.open(io.BytesIO(base64.b64decode(image_data)))


    picknote = data.picknote
    token = data.token

    # picknote logic for saving and validating
    picknote_flag = picknote_saving_logic(picknote, token)
    if not picknote_flag:
        print("Picknote not found")
        return {
            'batchNumber': None,
            'mfgDate': None,
            'expDate': None,
            'image': None,
            'original': None,
            'price': None,
            'productName': None,
            'productCode': None
        }

    model_results = model.predict(source=img, conf=0.5)


    for result in model_results:
        if result:
            if result.names:
                # Access the bounding box coordinates in xyxy format
                boxes = result.boxes
                if boxes:
                    time_str = str(time.time())
                    time_str = time_str.replace('.', '')
                    # img.save('prev_image/' + time_str + '.jpg')
                    # same_img_flag = check_same_image(img)
                    # if same_img_flag:
                    #     return {'batchNumber': None, 'mfgDate': None, 'expDate': None, 'image': None, 'original': None, 'price': None, 'productName': None, 'productCode': None}
                    
                    box = max(boxes, key=lambda box: box.conf.item())
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    # Crop the image using the bounding box coordinates
                    cropped_img = img.crop((x1, y1, x2, y2))
                    # Extract text from the cropped image
                    text = extract_text(cropped_img, reader)
                    filtered_text, price = filter_text(text)
                    # Convert filtered text to a single string
                    filtered_text_str = ' '.join([t[1] for t in filtered_text])
                    # Extract the batch number from the filtered text
                    org_batch_no, batch_no, mfg, exp, price, product_name, product_code = extract_details(filtered_text_str, price, picknote)
                    
                    
                    # make rectangle on the image on original image
                    plt_img = img.copy()
                    plt_img = np.array(plt_img)
                    cv2.rectangle(plt_img, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    font = cv2.FONT_HERSHEY_SIMPLEX
                    font_scale = 2  # Increase the font scale to make the text bigger
                    font_color = (0, 255, 0)
                    thickness = 2

                    # Add batch number text
                    cv2.putText(plt_img, f'Batch No: {org_batch_no}', (x1, y1 - 10), font, font_scale, font_color, thickness)

                    # Display time taken to process the image
                    cv2.putText(plt_img, f'Time taken: {time.time() - start:.2f} seconds', (10, 50), font, font_scale, font_color, thickness)

                    plt_img = Image.fromarray(plt_img)
                    buffered = io.BytesIO()
                    plt_img.save(buffered, format="JPEG")
                    img_str = base64.b64encode(buffered.getvalue()).decode()
                    if batch_no:
                        data = {
                            'batchNumber': batch_no,
                            'mfgDate': mfg,
                            'expDate': exp,
                            'image': img_str,
                            'original': org_batch_no,
                            'price': price,
                            'productName': product_name,
                            'productCode': product_code
                        }

                        return data
                    else:
                        data = {
                            'batchNumber': None,
                            'mfgDate': None,
                            'expDate': None,
                            'image': img_str,
                            'original': None,
                            'price': None,
                            'productName': None,
                            'productCode': None
                        }
                        return data
    # return original image
    buffered = io.BytesIO()
    img.save(buffered, format="JPEG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    data = {
        'batchNumber': None,
        'mfgDate': None,
        'expDate': None,
        'image': None,
        'original': None,
        'price': None,
        'productName': None,
        'productCode': None
    }
    
    return data


if __name__ == "__main__":
    import uvicorn
    uvicorn.run('main:app', host='0.0.0.0', port=3000, reload=True)