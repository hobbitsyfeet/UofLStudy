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
     - SIFT and SURF are patented and if you want to use it in a real-world application, you need to pay a licensing fee.
     - ORB is not.
    2) Compute the distances between every descriptor
    3) Select the best matches to align (Knn - 2 best matches for each descriptor {k=2})
    - finds two best matches for each feature and leaves the best one only if the ratio between descriptor distances is greater than the threshold
    4) Estimate Homography (Homography Estimator)
    5) Warp the images (translate and rotate) to align
        - NOTE this is where we will extract the top left of each frame for reference on the stitched image
        locations of each frame (hopefully)
    6) Stitch the images (Stitch and blend)
    """
    def __init__(self):
        pass
    
    def registration(self, images):
        """
        1) resize to medium resolution
        2) Find Features
        3) Match Features
        4) Select images and matches subset to build pano?
        5) Esimate Camera parameters rough initial guess?
        6) refine camera parameters globally
        7) Wave correction and Final scale estimation
        Return Registration Data.?
        """
        pass
    def resize(self, percent):
        pass

    def find_features(self):
        pass
    def match_features(self):
        pass
    def camera_estimation(self):
        pass
    def refine_estimation(self):
        pass
    def wave_correction(self):
        pass

    def composit(self, images, regist_data):
        """
        1)Resize original image to small resolution
        2)Warp the image (with regist_data)
        3)Estimate exposure errors
        4)Find seam masks
        5)Resize mask to original resolution
        
        6)Warp original image
        7)Compensate exposure errors with results in step 3
        8)Using results from step 5 and 7, blend images

        """
        pass

    def warp_resized(self):
        pass
    def exposure_estimation(self):
        pass
    def find_seam_mask(self):
        pass
    def warp_original(self):
        pass
    def compensate_exposure(self):
        pass
    def blend_images(self):
        pass
    

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
        frame_skip = 100

        while len(frames) < 20:
            #set current frame to the next n-skipped frames
            cap.set(cv2.CAP_PROP_POS_FRAMES, cap.get(cv2.CAP_PROP_POS_FRAMES) + frame_skip)
            print(cap.get(cv2.CAP_PROP_POS_FRAMES))

            #read the image from that skipped frame
            ret, frame = cap.read()
            if ret:
                if cv2.waitKey(30) & 0xFF == ord('q'):
                    break
                # cv2.imshow('frame', frame)
                #append the frames to be processed
                frames.append(frame)
        
        return frames

if __name__ == "__main__":
    Image = StitchImage()
