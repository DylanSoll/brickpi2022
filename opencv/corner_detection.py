import numpy as np
import cv2

cap = cv2.VideoCapture(0)
while True:
    ret, img = cap.read()#cv2.imread('opencv\chessboard.png')
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    corners = cv2.goodFeaturesToTrack(gray, 100, 0.01, 100)
    corners = np.int0(corners)

    for corner in corners:
        x, y = corner.ravel()
        cv2.circle(img, (x, y), 5, (255, 0, 0), -1)

    '''for i in range(len(corners)):
        for j in range(i + 1, len(corners)):
            corner1 = tuple(corners[i][0])
            corner2 = tuple(corners[j][0])
            color = tuple(map(lambda x: int(x), np.random.randint(0, 255, size=3)))
            cv2.line(img, corner1, corner2, color, 1)'''

    cv2.imshow('Frame', img)
    if cv2.waitKey(1) == ord('q'):
        cv2.destroyAllWindows()
        cap.release()
        break