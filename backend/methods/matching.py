import pandas as pd
from fuzzywuzzy import process, fuzz
import os
import cv2
import numpy as np
from skimage.metrics import structural_similarity as ssim
import time
from methods.redis import MyRedis
import json


def find_matches(batch_no, mfg_date, exp_date, price, picknote, threshold=60):
    # Check if batch_no, mfg_date, exp_date, and price are valid
    if not batch_no:
        print('Invalid input:', batch_no)
        return None, None, None, None, None, None
    
    
    # load data from redis
    redis = MyRedis()
    data = redis.get(picknote)

    # data is list of json containing batch
    if data is not None:
        data = json.loads(data)
        Batch = [item['batch'] for item in data]
        mfg = []
        exp = []
        price_list = []
        product_name = [item['product_name'] for item in data]
        product_code = [item['product_code'] for item in data]

    

    # Find the 5 best matches for the batch_no
    matches = process.extract(batch_no, Batch, limit=5)


    print('matches:', matches)

    for match in matches:
        index = Batch.index(match[0])

        # Extract corresponding row values
        # matched_mfg = mfg[index]
        # matched_exp = exp[index]
        # matched_price = price_list[index]

        # Calculate similarity scores
        batch_score = match[1]
        # mfg_score = fuzz.ratio(mfg_date, matched_mfg)
        # exp_score = fuzz.ratio(exp_date, matched_exp)
        # price_score = fuzz.ratio(str(price), str(matched_price))

        # Calculate average score based on available data
        # scores = [batch_score, mfg_score, exp_score, price_score]
        scores = [batch_score]
        num_scores = sum(1 for score in scores if score is not None)
        average_score = sum(score for score in scores if score is not None) / num_scores if num_scores > 0 else 0

        print('average_score:', average_score)
        # Check if the average score is above the threshold
        if average_score >= threshold:
            mfg_date = None
            exp_date = None
            price = None
            return Batch[index], mfg_date, exp_date, price, product_name[index], product_code[index]

    return None, None, None, None, None, None


def check_same_image(image_data):
    saved_image_list = os.listdir('prev_image')

    if not saved_image_list:
        # If the directory is empty, return False since there's no image to compare with.
        return False

    saved_image_list = [image.split('.')[0] for image in saved_image_list]

    # Take the latest image saved with time.time() name
    latest_image = max(saved_image_list, key=float)


    # if image time is not more than 5 seconds, return True
    if float(latest_image) + 5 > float(time.time()):
        return True

    # Load the latest saved image
    image1 = cv2.imread('prev_image/' + latest_image + '.jpg')

    # Convert image_data to OpenCV format
    image_data = cv2.cvtColor(np.array(image_data), cv2.COLOR_BGR2RGB)
    image2 = image_data

    # Convert both images to grayscale
    image1_gray = cv2.cvtColor(image1, cv2.COLOR_BGR2GRAY)
    if len(image2.shape) == 3 and image2.shape[2] == 3:
        image2_gray = cv2.cvtColor(image2, cv2.COLOR_BGR2GRAY)
    elif len(image2.shape) == 3 and image2.shape[2] == 4:
        image2_gray = cv2.cvtColor(image2, cv2.COLOR_BGRA2GRAY)
    elif len(image2.shape) == 2:
        image2_gray = image2
    else:
        raise ValueError("Unexpected number of channels in input image.")

    # Compute SSIM between the two images
    score, diff = ssim(image1_gray, image2_gray, full=True)
    print('SSIM:', score)
    # Return True if SSIM score is close to 1 (indicating images are very similar), else False
    if score >= 0.10:
        print('--------------------------------Same Image Detected')
        os.remove('prev_image/' + latest_image + '.jpg')
        return True
    else:
        print('--------------------------------Different Image Detected')
        os.remove('prev_image/' + latest_image + '.jpg')
        return False