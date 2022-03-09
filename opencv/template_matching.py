import numpy as np
import cv2



methods = [cv2.TM_CCOEFF, cv2.TM_CCOEFF_NORMED, cv2.TM_CCORR,
            cv2.TM_CCORR_NORMED, cv2.TM_SQDIFF, cv2.TM_SQDIFF_NORMED]
cap = cv2.VideoCapture(0)

while True:
    ret, col = cap.read()
    img = (cv2.cvtColor(col,0)/256).astype('uint8')
    lines = cv2.Canny(img, 200, 100, 3, False)
    cv2.imshow('Test', lines)
    cv2.waitKey(0)
    for method in methods:
        template = cv2.resize(cv2.imread('opencv/h_template.jpg', 0), (0, 0), fx=0.8, fy=0.8)
        for i in range(10):
            template = cv2.resize(template, (0, 0), fx=1/(i+1), fy=1/(i+1))
            template = cv2.Canny(np.uint8(template), 200, 100, 3, False)
            h, w = template.shape
            img2 = img.copy()
            col2 = col.copy()
            '''result = cv2.matchTemplate(img2, template, method)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            if method in [cv2.TM_SQDIFF, cv2.TM_SQDIFF_NORMED]:
                location = min_loc
            else:
                location = max_loc

            bottom_right = (location[0] + w, location[1] + h)    
            cv2.rectangle(col2, location, bottom_right, 255, 5)'''
            cv2.imshow('Match', col2)
            cv2.waitKey(0)
            cv2.destroyAllWindows()