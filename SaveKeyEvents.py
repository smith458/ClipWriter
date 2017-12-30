from pyimagesearch.KeyClipWriter import KeyClipWriter
from imutils.video import VideoStream
import argparse
import datetime
import imutils
import time
import cv2

ap = argparse.ArgumentParser()
ap.add_argument("-o", "--output", required=True, help="path to output directory")
ap.add_argument("-p", "--picamera", type=int, default=-1, help="whether or not the Raspberry Pi camera should be used")
ap.add_argument("-f", "--fps", type=int, default=20, help="FPS of output video")
ap.add_argument("-c", "--codec", type=str, default="MJPG")
ap.add_argument("-b", "--buffer-size", type=int, default=32, help="buffer size of video clip writer")

print("[INFO] warming up camera...")
vs = VideoStream(usePiCamera=args["picamera"])
time.sleep(2.0)

#define lower and upper bounds of of "green" ball
greenLower = (29, 86, 6)
greenUpper = (64, 255, 255)

#initialize key clip writer
kcw = KeyClipWriter(bufsize=args["buffer-size"])
consecFrames = 0

#https://www.pyimagesearch.com/2016/02/29/saving-key-event-video-clips-with-opencv/