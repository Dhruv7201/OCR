import numpy as np
import cv2 as cv
import matplotlib.pyplot as plt
import base64



def base64_to_cv2(base64_string):
    decoded_data = base64.b64decode(base64_string)
    np_data = np.frombuffer(decoded_data, np.uint8)
    img = cv.imdecode(np_data, cv.IMREAD_COLOR)
    return img

def detect_box(frame, product_img, batch_img):
    # Convert base64 image to OpenCV format
    img1 = base64_to_cv2(frame)
    product_img = cv.imread(product_img)
    
    # Initiate SIFT detector
    sift = cv.SIFT_create()

    # Convert frame to grayscale
    gray_frame = cv.cvtColor(img1, cv.COLOR_BGR2GRAY)

    # find the keypoints and descriptors with SIFT
    kp1, des1 = sift.detectAndCompute(gray_frame, None)
    kp2, des2 = sift.detectAndCompute(product_img, None)

    # FLANN parameters
    FLANN_INDEX_KDTREE = 1
    index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
    search_params = dict(checks=50)  # or pass empty dictionary

    flann = cv.FlannBasedMatcher(index_params, search_params)

    matches = flann.knnMatch(des1, des2, k=2)

    # Need to draw only good matches, so create a mask
    matchesMask = [[0, 0] for _ in range(len(matches))]

    # ratio test as per Lowe's paper
    for i, (m, n) in enumerate(matches):
        if m.distance < 0.7 * n.distance:
            matchesMask[i] = [1, 0]

    # Count the number of matches that pass the ratio test
    num_good_matches = sum(mask[0] for mask in matchesMask)
    
    # If the number of good matches exceeds a certain threshold
    if num_good_matches / len(matches) > 0.04:
        print('Box detected')
        return 1
    else:
        batch_img = cv.imread(batch_img)
        kp3, des3 = sift.detectAndCompute(gray_frame, None)
        kp4, des4 = sift.detectAndCompute(batch_img, None)
        matches = flann.knnMatch(des3, des4, k=2)
        matchesMask = [[0, 0] for _ in range(len(matches))]
        for i, (m, n) in enumerate(matches):
            if m.distance < 0.7 * n.distance:
                matchesMask[i] = [1, 0]
        num_good_matches = sum(mask[0] for mask in matchesMask)
        if num_good_matches / len(matches) > 0.04:
            print('Batch detected')
            return 2
        else:
            print('No box or batch detected')

        return 0
