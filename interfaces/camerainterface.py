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
        self.upper_col = (255, 255, 255)
        self.lower_col = (0, 0, 0)
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






    def convert_to_CV2(self, frame):
        """Converts IOBytes stream to CV2 object

        Args:
            frame (str): Frame from IOBytes stream

        Returns:
            UMat: cv2 object of image
        """        
        numpy_array = numpy.fromstring(frame, dtype=numpy.uint8) #converts image to numpy array
        cv2_object = cv2.imdecode(numpy_array, 1) #decodes numpy array into cv2 object
        return cv2_object #retuns altered object

    def convert_to_bytes(self, frame, image_type = '.jpg'):
        """Converts cv2 object to bytes

        Args:
            frame (UMat): Converts 
            image_type (str, optional): _description_. Defaults to '.jpg'.

        Returns:
            _type_: _description_
        """           
        in_bytes = cv2.imencode(image_type, frame)[1].tobytes() #encodes frame object in bytes, typically in jpg format
        return in_bytes #retuns bytes form


    # Thread reads frames from the stream
    def update(self):
        self.camera.start_preview()
        time.sleep(2)
        self.stream = self.camera.capture_continuous(self.rawCapture, 'jpeg', use_video_port=True)
        for f in self.stream:
            self.rawCapture.seek(0)
            self.frame = self.rawCapture.read()
            self.data = self.convert_to_CV2(self.frame)
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
    

    def find_h(self, frame):
        """Finds position of any H in frame

        Args:
            frame (UMat): Current frame, as a cv2 object

        Returns:
            list: Returns a list of 'H' found, tuple of ( x,y, width, height)
        """        
        #Uses custom trained haar cascade to detect H position
        return self.h_cascade.detectMultiScale(frame, 1.3, 5)

    def find_u(self, frame):
        """Finds position of any U in frame

        Args:
            frame (UMat): Current frame, as a cv2 object

        Returns:
            list: Returns a list of 'U' found, tuple of ( x,y, width, height)
        """        
        #Uses custom trained haar cascade to detect U position
        return self.u_cascade.detectMultiScale(frame, 1.3, 5)

    def apply_colour_mask(self, frame1, frame2):
        """Applies a colour mask to a CV2 object

        Args:
            frame1 (UMat): Frame to match
            frame2 (Umat): _description_

        Returns:
            UMAT: CV2 object with colour mask applied
        """        
        hsv = cv2.cvtColor(frame1, cv2.COLOR_BGR2HSV) #converts to HSV
        lower_col = numpy.array(self.lower_col)
        upper_col = numpy.array(self.upper_col)
        mask = cv2.inRange(hsv, lower_col, upper_col)
        result = cv2.bitwise_and(frame1, frame2, mask=mask)
        return result

    def draw_box_label(self, val,frame, colour, label):
        """Draws a box on the screen

        Args:
            val (list): List of tuples of (x, y, width, height)
            frame (UMat): CV2 object 
            colour (tuple): colour of label and box (BGR)
            label (str): Label to be displayed across the box

        Returns:
            UMat: frame with box and label
        """        
        for (x, y, width, height) in val: #runs through all values provided
            #retreives coordinates and dimensions
            cv2.rectangle(frame, (x, y), (x + width, y + height), colour, 3)
            #draws rectangle and label in same colour, in same position
            cv2.putText(frame, label, (x-width,y), cv2.FONT_HERSHEY_COMPLEX, 1, colour)
            break
        return frame

    def collect_live_frame(self):
        """Collects and alters current frame of camera 

        Returns:
            str: Returns image from camera (with overlays)
        """        
        try:
            h = self.find_h(self.data)
            u = self.find_u(self.data)
            self.data = self.draw_box_label(h, self.data, (255,0,0), 'Harmed')
            self.data = self.draw_box_label(u, self.data, (0,255,0), 'Unharmed')
            self.data = self.apply_colour_mask(self.data, self.data)
            return self.convert_to_bytes(self.data)
        except:
            self.log('Error with frame manipulation in collect_live_frame')
            return self.frame

    def take_photo(self):
        alt_image = self.collect_live_frame()
        time_taken = time.time()
        raw_image = self.get_frame()
        
        #cv2.imwrite('robot_cam_photos/'+str(int(time.time()))+".jpg", self.data)
        data = {'image': alt_image, 'time_taken':time_taken, 'raw_image': raw_image,
        'lower_col': self.lower_col, 'upper_col': self.upper_col}
        return data

    #detect if there is a colour in the image
    def sir_get_camera_colour(self):
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

    def invert_colour(self):

        return

def check_colour(frame, low, high):
    thresh = cv2.inRange(frame, low, high)
    count = numpy.sum(numpy.nonzero(thresh))
    if count > 1000: #more than 300 pixels are between the low and high color
        return True
    else:
        return False


def check_for_colours(frame):
    img = cv2.imdecode(numpy.fromstring(frame, dtype=numpy.uint8), 1)
    colours_found = {'red':check_colour(img, (50,50,150), (128,128,255)),
    'yellow': check_colour(img, (0,115,115), (153,255,235)), 
    'green':check_colour(img, (0,133,0), (255,255,255)) }

    return colours_found