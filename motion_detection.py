import argparse
import datetime
import imutils
import time
import cv2

ap = argparse.ArgumentParser()
ap.add_argument("-p", "--camera", default=1, help="which camera should be used")
ap.add_argument("-a", "--min_area", type=int, default=500, help="minimum area size of motion")
args = vars(ap.parse_args())

cap = cv2.VideoCapture(args["camera"])
time.sleep(2)

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
        firstFrame = gray
        continue
    
    # Absolute diff between current and first frame
    frameDelta = cv2.absdiff(firstFrame, gray)
    thresh = cv2.threshold(frameDelta, 25, 255, cv2.THRESH_BINARY)[1]

    # Dialate the thresholded image to fill holes and find contours
    thresh = cv2.dilate(thresh, None, iterations=2)
    (img, cnts, _) = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Loop over contours
    for c in cnts:
        # Ignore if contour is big enough
        if cv2.contourArea(c) >= args["min_area"]:
            # Find and draw rectangle
            (x, y, w, h) = cv2.boundingRect(c)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            text = "Occupied"

    # Draw text and timestamp on the frame
    cv2.putText(frame, "Room Status: {}".format(text), (10, 10), cv2.FONT_HERSHEY_SIMPLEX, .05, (0, 0, 255), 2)
    cv2.putText(frame, datetime.datetime.now().strftime("%A %d %B %Y %I :%M:%S%p"), (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, .35, (0, 0, 255), 1)
    
    # Show the frame and record if the user presses a key
    cv2.imshow("Security Feed", frame)
    cv2.imshow("Thresh", thresh)
    cv2.imshow("Frame Delta", frameDelta)
    key = cv2.waitKey(1) & 0xFF

    # Break if 'q' is pressed
    if key == ord("q"):
        break

# Cleanup
cap.release()
cv2.destroyAllWindows()