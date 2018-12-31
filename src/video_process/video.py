#from YourClassParentDir.YourClass import YourClass
from video_process.tracktor import tracktor
#import tracktor.tracktor
import cv2
import numpy as np
from math import floor
import pandas as pd


class VideoCapture:
    def __init__(self, video_source=""):
        # Open the video source
        self.cap = cv2.VideoCapture(video_source)
        if not self.cap.isOpened():
            raise ValueError("Unable to open video source", video_source)

        self.cap.set(cv2.CAP_PROP_FPS, 60)
        # Get video source width, height and length in frames
        self.width = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.height = self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        self.length = self.cap.get(cv2.CAP_PROP_FRAME_COUNT)-4

        self.current_frame = 0
        self.last_frame = self.current_frame
        self.play_state = False

        self.working_number = 0
        self.trackers = []

        self.output_path = "../output/"
        #tracking constants for getting frame types

        self.TRACK_ALL = -1
        self.NO_TRACKING = -2

        #zoom variable for setting focused frame
        self.zoom = 4

    def export_all(self):
        #self.set_frame_pos(1)
        #print("setting fame to start:" + str(self.current_frame))
        #sets the process to process ALL
        self.working_number = self.find_tracker_index_by_id("ALL")
        ret = True

        for i in range(len(self.trackers)):
            self.trackers[i].df = []

        while(self.current_frame <= self.length):

            # Get a frame from the video source, already processed
            ret, frame = self.get_frame(self.working_number)
            print("loading: " + str(int(self.current_frame)) + " of "+ str(int(self.length)))

            #frame already processed, retreive data from that frame, store it in each trackers
            for i in range(len(self.trackers)):
                #ignore duplicate frame
                if len(self.trackers[i].df) > 1:
                    last_frame = self.trackers[i].df[i-1][0]
                #it is the first frame and we can simulate the previous_frame
                else:
                    last_frame = self.current_frame-1

                #try to append data
                try:
                    #if we have a new frame, append it
                    if self.current_frame != last_frame:
                        self.trackers[i].df.append([self.current_frame,
                                                self.trackers[i].meas_now[0][0], #store X coord
                                                self.trackers[i].meas_now[0][1] #store Y coord
                                                ])
                #we received bad data and cannot process it. return -1
                except:
                    print("Could not get location from" + self.trackers[i].s_id +
                                "at frame " + str(self.current_frame)
                                )
                    self.trackers[i].df.append([self.current_frame,-1,-1])

        print("Starting to export....")
        #once done processing the video (last frame complete), export to file
        for i in range(len(self.trackers)):
            print("Exporting: " + self.trackers[i].s_id)
            #load our data into a pandas dataframe
            self.trackers[i].df = pd.DataFrame(np.matrix(self.trackers[i].df), columns = ['frame','pos_x','pos_y'])
            #export the data into a csv file
            self.trackers[i].df.to_csv(self.output_path + "csv/" + self.trackers[i].s_id + ".csv")


    def run(self):
        while(true):
            update()

    def set_frame(self, value):
        self.cap.set(cv2.CAP_PROP_POS_FRAMES,value)


    def get_frame(self,tracking = 0):
        """
        Description: get frame gets the tracking number, and depending on the
        tracking, we determine what to track (-2: NONE, -1 ALL, 1...n tracking index)
        """
        if self.cap.isOpened():
            #grab a frame
            ret, frame = self.cap.read()
            #set the current frame number to the frame we just received
            self.current_frame = self.cap.get(cv2.CAP_PROP_POS_FRAMES)
            if tracking == self.NO_TRACKING:
                return (ret,frame)
            elif tracking == self.TRACK_ALL:
                frame = self.show_all(frame)

            elif tracking != self.TRACK_ALL:
                frame = self.get_focused_frame(frame,tracking)
        if ret:
            return (ret,frame)

    def get_focused_frame(self,frame,individual):
        """
        Description: This function returns a frame centered and zoomed in on the
        individual being tracked.
        """
        if self.cap.isOpened():
            # Apply mask to aarea of interest\n",
            ret,frame = self.process(self.trackers[individual],frame,self.current_frame)
            if ret is True:
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
                return (frame)
        else:
            return (frame)

    def show_all(self,frame):
        """
        Description: this function returns a frame that shows all of the tracked individuals
        """
        #iterate through all
        for i in range(len(self.trackers)):
            ret,frame = self.process(self.trackers[i],frame,self.current_frame,detail = False)
            if ret is True:
                cv2.circle(frame, tuple([int(x) for x in self.trackers[i].meas_now[0]]), 5, self.trackers[i].colour, -1, cv2.LINE_AA)
        return frame

    def initVideo(self):
        return ret,frame

    def process(self,tracktor,frame,this,detail=True):
        """
        This function takes a frame, and a tracked individua and performs operations
        on the frame and applies information to the tracktor like x,y coordinates
        """
        try:
            #eliminate small noise
            thresh = tracktor.colour_to_thresh(frame)
            thresh = cv2.erode(thresh, tracktor.kernel, iterations = 1)
            thresh = cv2.dilate(thresh, tracktor.kernel, iterations = 1)


            #from our current frame, draw contours and display it on final frame
            final, contours = tracktor.detect_and_draw_contours(frame, thresh)
            #calculate cost of previous to currentmouse_video
            row_ind, col_ind = tracktor.hungarian_algorithm()

            #try to re-draw, separate try-except block allows redraw of min_area/max_area
            final = tracktor.reorder_and_draw(final, col_ind, this)
            ret = True
        except:
            ret = False
            return ret,frame

        return (True,final)

    def add_tracker(self):
        self.trackers.append(tracktor())

    def delete_tracker(self,index):
        del trackers[index]

    #search the list of trackers by name and return -1 if not fouond
    def find_tracker_index_by_id(self,name):
        for i in range(len(self.trackers)):
            if name == self.trackers[i].s_id:
                return i
        else:
            return -1

    # Release the video source when the object is destroyed
    def __del__(self):
        if self.cap.isOpened():
            self.cap.release()
