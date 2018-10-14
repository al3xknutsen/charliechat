import cv, cv2
from numpy import array, asarray

from thread import MultiThread
from time import sleep


class WebcamManager:
    def init_webcam(self):
        self.capturing = False
    
    def send_camstream(self):
        self.camera = cv.CaptureFromCAM(0)
        
        while self.capturing:
            img = cv.QueryFrame(self.camera)
            self.datastream.put(("send", {"datatype": "webcam", "data": asarray(cv.GetMat(img)).tostring()}))
            sleep(10)
#             cv.ShowImage("CharlieChat Webcam", img)
#             cv.WaitKey(10)
    
    
    def recv_camstream(self, imgdata):
        with open(appdata + "webcam-img.jpg") as webcamimg:
            webcamimg.write(imgdata)
        cv.NamedWindow("CharlieChat Webcam")
        cv.ShowImage("CharlieChat Webcam", cv2.imgread(appdata + "webcam-img.jpg", cv2.IMREAD_COLOR))
        cv.WaitKey(10)
    
    
    def toggle_webcam(self, event):
        if event.GetEventObject().GetValue():
            self.capturing = True
            MultiThread(self.send_camstream).start()
        else:
            self.capturing = False
            cv.DestroyWindow("CharlieChat Webcam")
            del self.camera
#             MultiThread(self.grab_img).start()