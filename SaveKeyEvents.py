from PyImageSearch.KeyClipWriter import KeyClipWriter
from imutils.video import VideoStream
import argparse
import datetime
import imutils
import time
import cv2

ap = argparse.ArgumentParser()
ap.add_argument("-o",  "--output", type=str, default="output", help="path to output directory")
ap.add_argument("-ca", "--camera", type=int, default=0, help="which camera should be used")
ap.add_argument("-f",  "--fps", type=int, default=20, help="FPS of output video")
ap.add_argument("-co", "--codec", type=str, default="MJPG")
ap.add_argument("-b",  "--buffer_size", type=int, default=32, help="buffer size of video clip writer")
args = vars(ap.parse_args())

print("[INFO] warming up camera...")
vs = cv2.VideoCapture(args["camera"] > 0)
time.sleep(2.0)

#define lower and upper bounds of of "green" ball
greenLower = (29, 86, 6)
greenUpper = (64, 255, 255)

#initialize key clip writer
kcw = KeyClipWriter(bufSize=args["buffer_size"])
consecFrames = 0

triggeringEvent = False

while True:
    ret, frame = vs.read()
    if triggeringEvent:
        consecFrames = 0
        if not kcw.recording:
            timeStamp = datetime.datetime.now()
            p = "{}/{}.avi".format(args["output"], timeStamp.strftime("%Y%m%d-%H%M%S"))
            kcw.start(p, cv2.VideoWriter_fourcc(*args["codec"]), args["fps"])
    else:
        updateConsecFrames = True
    
    if updateConsecFrames:
        consecFrames += 1
    
    kcw.update(frame)

    if kcw.recording and consecFrames == args["buffer_size"]:
        kcw.finish()
    
    cv2.imshow('Frame', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    
if kcw.recording:
    kcw.finish()

vs.release()
cv2.destroyAllWindows()

## ToDo
# Check to see if actually recording
# Check consecutive frames

#https://www.pyimagesearch.com/2016/02/29/saving-key-event-video-clips-with-opencv/