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
    
    def stitch(self, images):
        print("Stitching images")
        stitcher = cv2.Stitcher_create(cv2.Stitcher_SCANS)
        image = stitcher.stitch(images)
        print(image)
        return image

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

    def find_features(self, img1, img2):
        """
        This function finds features between 2 images using ORB
        Desribes keypoints using "steer" BRIEF
        """
        orb = cv2.ORB_create()
        kp1, des1 = orb.detectAndCompute(img1, None)
        kp2, des2 = orb.detectAndCompute(img2, None)
        return kp1, kp2, des1, des2

    def match_features(self, des1, des2, mode=0):
        # 0 = BRUTE FORCE
        # 1 = BRUTE FORCE HAMMING
        if mode == 0:
            # BFMatcher with default params
            bf = cv2.BFMatcher()
            matches = bf.knnMatch(des1, des2, k=2)
            # Apply ratio test
            good = []
            for m,n in matches:
                if m.distance < 0.75*n.distance:
                    good.append([m])
            matches = good

        elif mode == 1:
            # create BFMatcher object with NORM_HAMMING
            bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
            # Match descriptors.
            matches = bf.match(des1, des2)
            # Sort them in the order of their distance.
            matches = sorted(matches, key=lambda x:x.distance)
            
            matches = matches[:20]

        return matches

    def find_homography(self, img1, img2, kp1, kp2, matches):
        ## extract the matched keypoints
        # 
        src_pts  = np.array([kp1[m.queryIdx].pt for m in matches], dtype=np.float32).reshape(-1, 1, 2)
        dst_pts  = np.array([kp2[m.trainIdx].pt for m in matches], dtype=np.float32).reshape(-1, 1, 2)

        ## find homography matrix and do perspective transform
        M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC,5.0)
        h,w = img1.shape[:2]
        pts = np.array([ [0,0],[0,h-1],[w-1,h-1],[w-1,0] ], dtype=np.float32).reshape(-1, 1, 2)
        dst = cv2.perspectiveTransform(pts, M)
        # dst = cv2.getAffineTransform(pts, M)
        return dst


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
        frame_skip = 300

        while len(frames) < 10:
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

if __name__ == "__main__":
    processor = StitchImage()

    frames = processor.collect_frames("./videos/GH010018_Trim.mp4")
    stitcher = cv2.Stitcher_create(cv2.Stitcher_SCANS)
    status, scan = stitcher.stitch(frames)

    if status != cv2.Stitcher_OK:
         print("Stitching Successful.")
    cv2.imwrite("./output/stitched.jpg", scan);

    img2 = scan
    img1 = frames[2]
    kp1, kp2, des1, des2 = processor.find_features(img1, img2)
    
    matches = processor.match_features(des1, des2, mode=1)
    print(matches)

    try:
        match_img = cv2.drawMatchesKnn(img1, kp1, img2, kp2, matches, None, flags=2)
    except:
        print("draw matches (non-knn)")
        match_img = cv2.drawMatches(img1, kp1, img2, kp2, matches, None, flags=2)

    dst = processor.find_homography(img1, img2, kp1, kp2, matches)
    cover_img = cv2.polylines(img2, [np.int32(dst)], True, (0, 0, 255),5, cv2.LINE_AA)

    cv2.imwrite("./output/cover_img2.jpg", cover_img)
    cv2.imwrite("./output/cover_query.jpg", img1)