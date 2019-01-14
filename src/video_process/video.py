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

        #print(cv2.getBuildInformation())
        #print(cv2.ocl.haveOpenCL())
        #cv2.ocl.setUseOpenCL(True)

        # Get video source width, height and length in frames
        self.width = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.height = self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        self.length = self.cap.get(cv2.CAP_PROP_FRAME_COUNT)
        self.FPS = 60
        self.cap.set(cv2.CAP_PROP_FPS, self.FPS)


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


    def play(self):
        if self.play_state is False:
            self.play_state = True

    def pause(self):
        #pause only if play is set
        if self.play_state is True:
            print("Pausing")
            self.play_state = False

    def set_frame(self, value):
        value = floor(float(value))
        self.current_frame = value
        self.cap.set(cv2.CAP_PROP_POS_FRAMES,value)

    def previous_frame(self):
        self.set_frame(self.current_frame-1)

    def next_frame(self):
        self.set_frame(self.current_frame+1)

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

    def set_tracker_offset(self,value):
        self.trackers[self.working_number].offset = value
        #go to the previous frame to update to current
        if self.play_state is False:
            self.set_frame(self.current_frame -1)

    def set_tracker_blocksize(self,value):
        if value % 2 == 0:
            value += 1
        self.trackers[self.working_number].block_size = value
        #go to the previous frame to update to current
        if self.play_state is False:
            self.set_frame(self.current_frame -1)

    def set_tracker_minarea(self,value):
        self.trackers[self.working_number].min_area = value
        #go to the previous frame to update to current
        if self.play_state is False:
            self.set_frame(self.current_frame -1)

    def set_tracker_maxarea(self,value):
        self.trackers[self.working_number].max_area = value
        #go to the previous frame to update to current
        if self.play_state is False:
            self.set_frame(self.current_frame -1)

    def get_frame(self,tracking = 0):
        """
        Description: get frame gets the tracking number, and depending on the
        tracking, we determine what to track (-2: NONE, -1 ALL, 1...n tracking index)
        """
        if self.cap.isOpened():

            #initialize ret to false so we enter the while loop
            ret = False

            #if we cannot retreive the frame, continue onto the next one
            while ret is False:
                if self.play_state is False:
                    self.set_frame(self.current_frame - 1)
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
            #when we retreive a new frame, we can assume we updated values with it
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
            ret,final = self.process(self.trackers[i],frame,self.current_frame,detail = False)

            if ret is True:
                cv2.circle(frame, tuple([int(x) for x in self.trackers[i].meas_now[0]]), 5, self.trackers[i].colour, -1, cv2.LINE_AA)
        if ret:
            return final
        else:
            return frame

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

            #x,y coordinates of previous tracktor
            if len(tracktor.meas_now) > 0:
                pos_x = tracktor.meas_now[0][0]
                pos_y = tracktor.meas_now[0][1]
            else:
                print("Unable to track " + tracktor.s_id)

            #from our current frame, draw contours and display it on final frame
            final, contours = tracktor.detect_and_draw_contours(frame, thresh)

            #detect if the tracker is changed
            changed = self.tracker_changed(pos_x,pos_y,contours)
            if changed is True:
                print(tracktor.s_id + "has changed")

            row_ind, col_ind = tracktor.hungarian_algorithm()

            #try to re-draw, separate try-except block allows redraw of min_area/max_area
            final = tracktor.reorder_and_draw(final, col_ind, this)

            ret = True
        except:
            ret = False
            return ret,frame

        return (True,final)

    def tracker_changed(self, x, y, contours):
        #assign default flag to True (assume changed until proven not)
        changed_tracker_flag = True

        #if there exist no contours, nothing is being tracked
        if len(contours) > 0:
            #we look at all the contours
            for contour in contours:
                #check if previous position exists in updated contour (1= Yes, -1= No)
                dist = cv2.pointPolygonTest(contour,(x,y), False)
                #print(dist)
                #if previous point exists in the same contour, set changed flag to false
                if dist != -1.0:
                    changed_tracker_flag = False

            if changed_tracker_flag is True:
                #print("changed contours")
                return changed_tracker_flag

        # if no contours exist, we cannot process anything
        else:
            #print("Unable to track ")
            return changed_tracker_flag

    def export_all(self):
        #self.set_frame_pos(1)
        #print("setting fame to start:" + str(self.current_frame))
        #sets the process to process ALL
        self.working_number = self.find_tracker_index_by_id("ALL")
        ret = True
        #we want to process as fast as we can(1000 fps should be good)
        self.cap.set(cv2.CAP_PROP_FPS, 1000)
        #we want playstate to be true so get_frame will work
        self.play_state = True

        #reset all tracktor's data
        for i in range(len(self.trackers)):
            self.trackers[i].df = []

        while(self.current_frame < self.length):
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
                    print("Could not get location from " + self.trackers[i].s_id +
                                " at frame " + str(self.current_frame)
                                )
                    self.trackers[i].df.append([self.current_frame,-1,-1])

        self.cap.set(cv2.CAP_PROP_FPS, self.FPS)
        print("Starting to export....")
        #once done processing the video (last frame complete), export to file
        for i in range(len(self.trackers)):
            print("Exporting: " + self.trackers[i].s_id)
            #load our data into a pandas dataframe
            self.trackers[i].df = pd.DataFrame(np.matrix(self.trackers[i].df), columns = ['frame','pos_x','pos_y'])
            #export the data into a csv file
            self.trackers[i].df.to_csv(self.output_path + "csv/" + self.trackers[i].s_id + ".csv")

    # Release the video source when the object is destroyed
    def __del__(self):
        if self.cap.isOpened():
            self.cap.release()
