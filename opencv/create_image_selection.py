import cv2
cap = cv2.VideoCapture(0)
for i in range(100):
    run = True
    while run:
        ret, image = cap.read()
        cv2.imshow('Test', image)
        if cv2.waitKey(1) == 32:
            run = False
    cv2.imwrite("images/p-frame%d.jpg" % i, image) # save frame as JPEG file.
    