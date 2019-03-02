"on the input of the video"
from __future__ import print_function
import cv2 as cv2
import numpy as np
import sys
# import matplotlib.pyplot as plt
# from random import randrange

class StitchImage():
    def __init__(self):
        pass

    def stitch(self):
        """
        This function takes in the video
        
        ----------------
        Stitcher methods
        ----------------

        register resolution(0.6)
        estimation resolution(0.1)
        compsiting resolution (original resolution)
        Panorama confidence threshold(1) = certain?
        seam finder -> graphCutSeamFinder - detail COST COLOR?
        Blender -> Multiband blender(false)
        Feature finder (ORB)
        Interpolation flags -> INTER_LINEAR

        work scale = 1
        seam scale = 1
        seam work aspect = 1
        warped image scale = 1

        ---------------------
        SCANS stitcher modes.
        ---------------------
        estimator -> AffineBasedEstimator
        wave correction -> False
        Feature matcher ->best of 2 nearest matcher(false,false)
        Bundle adjuster -> BundleAdjusterAffinePartial
        warper -> affine
        exposureCompensator -> no compensation

        """
        print("Stitching Frames...")

        frames = self.collect_frames("./videos/GH010018_Trim.mp4")

        # stitcher = cv2.createStitcherScans(True)
        stitcher = cv2.Stitcher_create(cv2.Stitcher_SCANS)
        status, pano = stitcher.stitch(frames)

        if status != cv2.Stitcher_OK:
            print("Can't stitch images, error code = %d" % status)
            sys.exit(-1)
        
        print("Stitching Successful.")
        cv2.imwrite("stitched_linear.jpg", pano);

    def collect_frames(self, video_source):
        """
        Collects the images for stitching
        """
        print(video_source)
        cap = cv2.VideoCapture(video_source)
        if not cap.isOpened():
            raise ValueError("Unable to open video source", video_source)
        print("Collecting Frames...")

        cap = cv2.VideoCapture(video_source)
        frames = []
        frame_skip = 105

        while len(frames) < 12:
            cap.set(cv2.CAP_PROP_POS_FRAMES, cap.get(cv2.CAP_PROP_POS_FRAMES) + frame_skip)
            print(cap.get(cv2.CAP_PROP_POS_FRAMES))
            ret, frame = cap.read()
            if ret:
                if cv2.waitKey(30) & 0xFF == ord('q'):
                    break
                cv2.imshow('frame', frame)

                frames.append(frame)
        
        return frames
    
    def find_KeyPoints(self):
        pass
    
    def match_Keypoints(self):
        pass

    def reference_frame(self, current_frame):
        """
        This function takes the current frame number and finds it's reference to the stitched image
        """
        pass

if __name__ == "__main__":
    Image = StitchImage()
    Image.stitch()
