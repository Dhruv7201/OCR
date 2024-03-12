import easyocr
import cv2
import time

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

reader = easyocr.Reader(['en'], gpu=False, download_enabled=True, model_storage_directory='./models', user_network_directory='./user_network', recognizer='lite')

image = './Screenshot from 2024-02-05 17-46-26.png'

recognition_results = reader.readtext(image)

# Filter and print the desired results
filtered_results = filter_text(recognition_results)

if filtered_results:
    print("Filtered Text:")
    for result in filtered_results:
        print('111111111111111111111111111111', result[1])

