import numpy as np
import cv2
from PIL import ImageGrab
cap = cv2.VideoCapture(0)
def find_h(frame):
    h_cascade = cv2.CascadeClassifier("C:/Users/22dyl\OneDrive\Desktop/h_training_data_cropped\classifier\cascade.xml")
    h = h_cascade.detectMultiScale(frame, 1.3, 5)
    return h


while True:
    var, frame = cap.read()
    h = find_h(frame)
    print(h)
    for (x, y, width, height) in h:
        #temp_img = np.array(ImageGrab.grab(bbox=(x,y,x+width, y+height)))
        #cv2.imshow('Frame', temp_img)
        #cv2.waitKey(0)
        cv2.rectangle(frame, (x, y), (x + width, y + height), (255, 0, 0), 3)
    cv2.imshow('img', frame)
    
    if cv2.waitKey(1) == ord('q'):
        break 

