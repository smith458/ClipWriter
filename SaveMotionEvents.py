from PyImageSearch.KeyClipWriter import KeyClipWriter
from imutils.video import VideoStream
import argparse
import datetime
import imutils
import time
import cv2

ap = argparse.ArgumentParser()
ap.add_argument("-o",  "--output", type=str, default="output", help="path to output directory")
ap.add_argument("-ca", "--camera", type=int, default=1, help="which camera should be used")
ap.add_argument("-f",  "--fps", type=int, default=20, help="FPS of output video")
ap.add_argument("-co", "--codec", type=str, default="MJPG")
ap.add_argument("-b",  "--buffer_size", type=int, default=32, help="buffer size of video clip writer")
ap.add_argument("-a", "--min_area", type=int, default=500, help="minimum area size of motion")
args = vars(ap.parse_args())

print("[INFO] warming up camera...")
cap = cv2.VideoCapture(args["camera"])
time.sleep(1.0)

#initialize key clip writer
kcw = KeyClipWriter(bufSize=args["buffer_size"])
consecFrames = 0

firstFrame = None

while True:
    (grabbed, frame) = cap.read()
    text = "Unoccupied"
     
    if not grabbed:
        break
    
    frame = imutils.resize(frame, width=500)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (21, 21), 0)
    
    if firstFrame is None:
        if  cv2.countNonZero(gray) > 1:
            firstFrame = gray
            kcw.frames.append(gray)
        continue
    
    # Absolute diff between current and first frame
    frameDelta = cv2.absdiff(firstFrame, gray)
    thresh = cv2.threshold(frameDelta, 25, 255, cv2.THRESH_BINARY)[1]

    # Dialate the thresholded image to fill holes and find contours
    thresh = cv2.dilate(thresh, None, iterations=2)
    (img, cnts, _) = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    motionDetected = False

    # Loop over contours
    for c in cnts:
        # Ignore if contour is big enough
        if cv2.contourArea(c) >= args["min_area"]:
            # Find and draw rectangle
            (x, y, w, h) = cv2.boundingRect(c)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            text = "Occupied"
    
            consecFrames = 0
            
            
            if not kcw.recording:
                timeStamp = datetime.datetime.now()
                p = "{}/{}.avi".format(args["output"], timeStamp.strftime("%Y%m%d-%H%M%S"))
                kcw.start(p, cv2.VideoWriter_fourcc(*args["codec"]), args["fps"])
            
            motionDetected = True
        else:
            motionDetected = False
    
    if not motionDetected:
        consecFrames += 1
    
    kcw.update(frame)

    if kcw.recording and consecFrames == args["buffer_size"]:
        kcw.finish()
    
    # Draw text and timestamp on the frame
    cv2.putText(frame, "Room Status: {}".format(text), (10, 10), cv2.FONT_HERSHEY_SIMPLEX, .35, (0, 0, 255), 2)
    cv2.putText(frame, datetime.datetime.now().strftime("%A %d %B %Y %I :%M:%S%p"), (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, .35, (0, 0, 255), 1)

    # Show the frame and record if the user presses a key
    cv2.imshow("Security Feed", frame)
    cv2.imshow("Thresh", thresh)
    cv2.imshow("Frame Delta", frameDelta)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    
if kcw.recording:
    kcw.finish()

cap.release()
cv2.destroyAllWindows()

#https://www.pyimagesearch.com/2016/02/29/saving-key-event-video-clips-with-opencv/