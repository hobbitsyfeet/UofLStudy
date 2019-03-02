"on the input of the video"
from __future__ import print_function
import cv2 as cv2
import numpy as np
import sys
# import matplotlib.pyplot as plt
# from random import randrange

class StitchImage():
    """
    Steps to stitching the images
    1) Find Keypoints between images (SIFT/SURF/ORB?)
    2) Compute the distances between every descriptor

    3) Select the best matches to align (Best of 2? feature matcher)
    - finds two best matches for each feature and leaves the best one only if the ratio between descriptor distances is greater than the threshold
    4) Estimate Homography (Homography Estimator)
    5) Warp the images (translate and rotate) to align
        - NOTE this is where we will extract the top left of each frame for reference on the stitched image
        locations of each frame (hopefully)
    6) Stitch the images (Stitch and blend)
    """
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

        frames = self.collect_frames("./videos/Cap2_2k_Trim.mp4")
        keypoints, descriptor = self.find_KeyPoints(frames)
        print(descriptor)
        # stitcher = cv2.createStitcherScans(True)
        # stitcher = cv2.Stitcher_create(cv2.Stitcher_SCANS)
        # status, pano = stitcher.stitch(frames)

        # if status != cv2.Stitcher_OK:
        #     print("Can't stitch images, error code = %d" % status)
        #     sys.exit(-1)
        
        print("Stitching Successful.")
        cv2.imwrite("stitched_linear.jpg", scan);

    def collect_frames(self, video_source):
        """
        Collects the images for stitching
        """
        print(video_source)
        cap = cv2.VideoCapture(video_source)
        if not cap.isOpened():
            raise ValueError("Unable to open video source", video_source)
        print("Collecting Frames...")

        #setup cv2 capture from video
        cap = cv2.VideoCapture(video_source)
        frames = []
        frame_skip = 105

        while len(frames) < 12:
            #set current frame to the next n-skipped frames
            cap.set(cv2.CAP_PROP_POS_FRAMES, cap.get(cv2.CAP_PROP_POS_FRAMES) + frame_skip)
            print(cap.get(cv2.CAP_PROP_POS_FRAMES))

            #read the image from that skipped frame
            ret, frame = cap.read()
            if ret:
                if cv2.waitKey(30) & 0xFF == ord('q'):
                    break
                cv2.imshow('frame', frame)
                #append the frames to be processed
                frames.append(frame)
        
        return frames
    
    def find_KeyPoints(self, frames):
        #ORB: An efficient alternative to SIFT or SURF
        #this creates the parameters to be used
        orb = cv2.ORB_create()
        for frame in frames:
            # find the keypoints with ORB
            keypoints = orb.detect(frame, None)
            #compute the descriptors with ORB
            keypoints, des = orb.compute(frame, keypoints)
        return keypoints, des
    
    def match_Keypoints(self):
        #cv2.estimateAffinePartial2D()
        pass

    def reference_frame(self, current_frame):
        """
        This function takes the current frame number and finds it's reference to the stitched image
        """
        pass

if __name__ == "__main__":
    Image = StitchImage()
    Image.stitch()
