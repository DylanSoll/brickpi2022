import cv2
import time
def create_im_from_cam(iterations):
    cap = cv2.VideoCapture(0)
    for i in range(iterations):
        run = True
        while run:
            ret, image = cap.read()
            cv2.imshow('Test', image)
            if cv2.waitKey(1) == 32:
                run = False
        cv2.imwrite("n/no_eye_frame%d.jpg" % time.time(), image) # save frame as JPEG file.
    cap.release()
    return

def create_video():
    run= True
    cap = cv2.VideoCapture(0)
    frame_size = (int(cap.get(3)), int(cap.get(4)))
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(f"{time.time()}.mp4", fourcc, 20, frame_size)
    while run:
        ret, image = cap.read()
        cv2.imshow('Test', image)
        if cv2.waitKey(1) == 32:
            run = False
            out.release()
    cap.release()

#create_im_from_cam(30)