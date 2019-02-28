"on the input of the video"
from __future__ import print_function
import cv2 as cv2
import numpy as np
import argparse
import sys
 
class StitchImage():
    def __init__(self):
        pass

    def stitch(self, video_source):
        """
        This function takes in the video
        """
        modes = (cv2.Stitcher_PANORAMA, cv2.Stitcher_SCANS)


        cap = cv2.VideoCapture(video_source)
        if not cap.isOpened():
            raise ValueError("Unable to open video source", video_source)
        print("Collecting Frames...")

        cap = cv2.VideoCapture(video_source)
        frames = []
        frame_skip = 100
        while len(frames) < 10:
            cap.set(cv2.CAP_PROP_POS_FRAMES, cap.get(cv2.CAP_PROP_POS_FRAMES) + frame_skip)
            print(cap.get(cv2.CAP_PROP_POS_FRAMES))
            ret, frame = cap.read()
            if ret:
                if cv2.waitKey(30) & 0xFF == ord('q'):
                    break
                cv2.imshow('frame', frame)
                frames.append(frame)
        print("Stitching Frames...")

        stitcher = cv2.createStitcher(True)
        status, pano = stitcher.stitch(frames)

        if status != cv2.Stitcher_OK:
            print("Can't stitch images, error code = %d" % status)
            sys.exit(-1)
        
        print("Stitching Successful.")
        cv2.imwrite("stitched_image3.jpg", pano);

    def reference_frame(self, current_frame):
        """
        This function takes the current frame number and finds it's reference to the stitched image
        """
        pass

if __name__ == "__main__":
    Image = StitchImage()
    Image.stitch("./videos/Cap2_2k_Trim.mp4")
