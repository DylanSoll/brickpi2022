import cv2
import numpy as np
class CVInterface():
    def __init__(self):
        self.h_cascade = cv2.CascadeClassifier("haarcascade_custom/h_cascade.xml")
        self.u_cascade = cv2.CascadeClassifier("haarcascade_custom/u_cascade.xml")
        self.eye_cascade = cv2.CascadeClassifier("haarcascade_custom/eye_cascade.xml")

        return
    def find_h(self, frame):
        return self.h_cascade.detectMultiScale(frame, 1.3, 5)
    
    def find_eye(self, frame):
        return self.eye_cascade.detectMultiScale(frame, 1.3, 5)

    def find_u(self, frame):
        return self.u_cascade.detectMultiScale(frame, 1.3, 5)

    def apply_colour_filter(self, frame1, frame2, colour_lower, colour_upper):
        hsv = cv2.cvtColor(frame1, cv2.COLOR_BGR2HSV)
        lower_col = np.array(colour_lower)
        upper_col = np.array(colour_upper)

        mask = cv2.inRange(hsv, lower_col, upper_col)

        result = cv2.bitwise_and(frame1, frame2, mask=mask)
        return result
if __name__ == '__main__':
    cap = cv2.VideoCapture(0)
    while True:
        var, frame = cap.read()
        cv_helper = CVInterface()
        #frame = apply_colour_mask(frame, frame, [90, 50, 50], [130, 255, 255])
        #frame = apply_colour_filter(frame, frame, [0, 0, 0], [255, 255, 255])
        for (x, y, width, height) in cv_helper.find_h(frame):
            cv2.rectangle(frame, (x, y), (x + width, y + height), (255, 0, 0), 3)
            cv2.putText(frame,'Harmed Victim', (x,y), cv2.FONT_HERSHEY_COMPLEX, 2, (255,0,0))
            #break
        for (x, y, width, height) in cv_helper.find_u(frame):
            cv2.rectangle(frame, (x, y), (x + width, y + height), (0, 255, 0), 3)
            cv2.putText(frame,'Unharmed Victim', (x,y), cv2.FONT_HERSHEY_COMPLEX, 2, (0,255,0))
            #break
        for (x, y, width, height) in cv_helper.find_eye(frame):
            cv2.rectangle(frame, (x, y), (x + width, y + height), (0, 255, 0), 3)
            #cv2.putText(frame,'Unharmed Victim', (x,y), cv2.FONT_HERSHEY_COMPLEX, 2, (0,255,0))
            #break
        cv2.imshow('img', frame)
        if cv2.waitKey(1) == ord('q'):
            break 