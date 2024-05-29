import cv2


cam = cv2.VideoCapture(0)
# display the running video images
while True:
    ret, img = cam.read()
    cv2.imshow('img', img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break