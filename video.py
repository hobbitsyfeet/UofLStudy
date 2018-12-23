from tracktor import tracktor
import cv2
import numpy as np
from math import floor
import random
class VideoCapture:
    def __init__(self, video_source=0):
        # Open the video source
        self.vid = cv2.VideoCapture(video_source)
        if not self.vid.isOpened():
            raise ValueError("Unable to open video source", video_source)

        # Get video source width, height and length in frames
        self.width = self.vid.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.height = self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT)
        self.length = self.vid.get(cv2.CAP_PROP_FRAME_COUNT)
        self.current_frame = 0
        self.last_frame = self.current_frame

        self.trackers = [tracktor()]*1

        #randomize colour
        for i in range(len(self.trackers)):
            self.trackers[i].colour = (random.randrange(0,255,1),random.randrange(0,255,1),random.randrange(0,255,1))

        #constants for interaction
        self.DISPLAY_FINAL = 0
        self.DISPLAY_THRESH = 1
        self.PAUSE_VIDEO = 3

        #tracking constants for getting frame types
        self.NO_TRACKING = 0
        self.TRACK_ALL = len(self.trackers)+1

        #assignment we use to choose different processes
        self.display_type = self.DISPLAY_FINAL

        #zoom variable for setting focused frame
        self.zoom = 4

    def set_frame(self, value):
        self.vid.set(cv2.CAP_PROP_POS_FRAMES,value)

    def get_focused_frame(self,frame,individual):
        if self.vid.isOpened():
            ret, frame = self.vid.read()
            # Apply mask to aarea of interest\n",
            ret,frame = self.process(self.trackers[individual],frame,self.current_frame)
            x = int(floor(self.trackers[individual].meas_now[0][0]))
            y = int(floor(self.trackers[individual].meas_now[0][1]))
            try:
                roi = frame[int(y- (self.height + self.height/self.zoom)):y + int(self.height/self.zoom),
                            int(x -(self.width + self.width/self.zoom)):x + int(self.width/self.zoom)]
            except:
                print("Cannot focus frame")

            roi = cv2.resize(roi, (int(self.width), int(self.height)))


            if ret:
                return (roi)
            else:
                return (None)
        else:
            return (None)

    def show_all(self,frame):
        for i in range(len(self.trackers)):
            cv2.circle(frame, tuple([int(x) for x in self.trackers[i].meas_now[0]]), 5, self.trackers[i].colour, -1, cv2.LINE_AA)
            return frame
            #frame = self.process(self.trackers[i],frame,self.current_frame)

    def get_frame(self,tracking = 0):
        if self.vid.isOpened():
            ret, frame = self.vid.read()
            self.current_frame = self.vid.get(cv2.CAP_PROP_POS_FRAMES)

            if tracking == len(self.trackers)+1:
                frame = self.show_all(frame)

            if tracking > 0 and tracking != self.TRACK_ALL:
                frame = self.get_focused_frame(frame,tracking-1)

            if ret:
                return (ret,frame)
            else:
                return (ret, None)
        else:
            return (ret, None)

    def initVideo(self):

        return ret,frame


    def pause_frame(self):
        pass
    def resume_frames(self):
        pass
    def process(self,tracktor,frame,this):
        #preprocess the frames, adding a threshold, erode and dialing to
        try:
            #eliminate small noise
            thresh = tracktor.colour_to_thresh(frame)
            thresh = cv2.erode(thresh, tracktor.kernel, iterations = 1)
            thresh = cv2.dilate(thresh, tracktor.kernel, iterations = 1)
        except:
            print("Cannot create threshold")
            pass

        #from our current frame, draw contours and display it on final frame
        try:
            final, contours = tracktor.detect_and_draw_contours(frame, thresh)
        except:
            print("Cannot detect and draw contours (Nothing to draw?)")
            pass
        #calculate cost of previous to currentmouse_video
        try:    row_ind, col_ind = tracktor.hungarian_algorithm()
        except:
            print("Cannot calculate cost")
            pass
        #try to re-draw, separate try-except block allows redraw of min_area/max_area
        try:
            final = tracktor.reorder_and_draw(final, col_ind, this)
        except:
            print("Can't draw")
            pass

        # Display the resulting frame
        if self.display_type is self.DISPLAY_FINAL:
            self.display_frame = final
        elif self.display_type is self.DISPLAY_THRESH:
            self.display_frame = thresh
        elif self.display_type is self.PAUSE_VIDEO:
            self.display_frame = final
        return (True,self.display_frame)

    # Release the video source when the object is destroyed
    def __del__(self):
        if self.vid.isOpened():
            self.vid.release()
