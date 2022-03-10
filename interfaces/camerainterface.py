#https://www.hackster.io/ruchir1674/video-streaming-on-flask-server-using-rpi-ef3d75-----------------------#

import time
import io
import threading
import picamera
import picamera.array
import cv2
import numpy
import logging
from PIL import Image
class CameraInterface(object):

    def __init__(self, logger=logging.getLogger(), resolution = (320,240), framerate=32):
        self.frame = None  # current frame is stored here by background thread
        self.logger=logger
        self.camera = picamera.PiCamera()
        self.camera.resolution = resolution
        self.camera.framerate = framerate
        self.camera.hflip = True; self.camera.vflip = True #not sure what this does
        self.rawCapture = io.BytesIO()
        self.stream = None
        self.thread = None
        self.stopped = False
        self.h_cascade = cv2.CascadeClassifier("haarcascade_custom/h_cascade.xml")
        self.u_cascade = cv2.CascadeClassifier("haarcascade_custom/u_cascade.xml")
        return

    def start(self):
        self.thread = threading.Thread(target=self.update, args=())
        self.thread.daemon = True
        self.thread.start()
        self.log("CAMERA INTERFACE: Started Camera Thread")
        return
        
    def log(self, message):
        self.logger.info(message)
        return

    def get_frame(self):
        return self.frame

    def stop(self):
        self.stopped = True
        return

    # Thread reads frames from the stream
    def update(self):
        self.camera.start_preview()
        time.sleep(2)
        self.stream = self.camera.capture_continuous(self.rawCapture, 'jpeg', use_video_port=True)
        for f in self.stream:
            self.rawCapture.seek(0)
            self.frame = self.rawCapture.read()
            self.data = numpy.fromstring(self.frame, dtype=numpy.uint8)
            cv2.imwrite('interfaces/image_target/frame.jpg', self.data)
            self.rawCapture.truncate(0)
            self.rawCapture.seek(0)

            # stop the thread
            if self.stopped:
                self.camera.stop_preview()
                time.sleep(2)
                self.rawCapture.close()
                self.stream.close()
                self.camera.close()
                self.log("CAMERA INTERFACE: Exiting Camera Thread")
                return
        return
    

    def convert_for_jpg(self):
        #cv2.imwrite('interfaces/image_target/frame.jpg', self.data)
        #print(self.JPEG)
        #f = open("demofile2.txt", "x")
        #print(self.JPEG[0][0].nbytes*8)
        #f.write
        #f.close()
        #self.frame = io.BytesIO(self.JPEG)
        return self.frame

    def find_h(self, frame):
        return self.h_cascade.detectMultiScale(self.data, 1.3, 5)

    def find_u(self, frame):
        return self.u_cascade.detectMultiScale(self.data, 1.3, 5)

    def apply_colour_filter(self, frame1, frame2, colour_lower, colour_upper):
        hsv = cv2.cvtColor(frame1, cv2.COLOR_BGR2HSV)
        lower_col = np.array(colour_lower)
        upper_col = np.array(colour_upper)

        mask = cv2.inRange(hsv, lower_col, upper_col)

        result = cv2.bitwise_and(frame1, frame2, mask=mask)
        return result

    def draw_box_label(self, val,frame, colour, label):
        #print(val)
        for (x, y, width, height) in val:
            print(x,y)
            cv2.rectangle(frame, (x, y), (x + width, y + height), colour, 3)
            cv2.putText(frame, label, (x,y), cv2.FONT_HERSHEY_COMPLEX, 2, colour)
        return frame

    def collect_live_frame(self):
        self.get_frame()
        #print(self.data.nbytes*8)
        h = self.find_h(self.data)
        u = self.find_u(self.data)
        self.draw_box_label(h, self.data, (255,0,0), 'Harmed')
        self.draw_box_label(u, self.data, (255,0,0), 'Harmed')
        #print(self.data.nbytes*8)
        self.frame = self.convert_for_jpg()
        return self.frame


    #detect if there is a colour in the image
    def get_camera_colour(self):
        if not self.frame: #hasnt read a frame from camera
            return "camera is not running yet"
        img = cv2.imdecode(numpy.fromstring(self.frame, dtype=numpy.uint8), 1)
        # set red range
        lowcolor = (50,50,150)
        highcolor = (128,128,255)

        # threshold
        thresh = cv2.inRange(img, lowcolor, highcolor)

        cv2.imwrite("threshold.jpg", thresh)

        count = numpy.sum(numpy.nonzero(thresh))
        self.log("RED PIXELS: " + str(count))
        if count > 300: #more than 300 pixels are between the low and high color
            return "red"
        return "no colour"
