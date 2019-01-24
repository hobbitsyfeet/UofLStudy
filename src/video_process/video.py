#from YourClassParentDir.YourClass import YourClass
from math import floor
import cv2
import numpy as np
import pandas as pd
import multiprocessing as mp

from video_process.tracktor import Tracktor

class VideoCapture:
    """
    VideoCapture is a class that takes a video, processes it, and returns it.
    This means that VideoCapture is responsible for working with the data (Tracktor)
    managing the data, adding and removing tracktor objects from the video as well as
    retreiving and exporting data.
    It is also related for video related functions such as play and pause.
    Parameters
    ----------
    video_source: string
        This is the directory of the video that is to be processed.

    """
    def __init__(self, video_source=""):
        # Open the video source
        self.cap = cv2.VideoCapture(video_source)
        if not self.cap.isOpened():
            raise ValueError("Unable to open video source", video_source)

        #print(cv2.getBuildInformation())
        #print(cv2.ocl.haveOpenCL())
        #cv2.ocl.setUseOpenCL(True)

        # Get video source width, height (resolution) and video length in frames
        self.width = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.height = self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        self.length = self.cap.get(cv2.CAP_PROP_FRAME_COUNT)
        self.FPS = 60
        #set the video framerate
        self.cap.set(cv2.CAP_PROP_FPS, self.FPS)

        #current frame is used to know what frame it is, as well as assigning frames
        self.current_frame = 0
        self.last_frame = self.current_frame

        #playstate is used to play/pause the video
        self.play_state = False

        #working number is the index for which tracktor to process
        self.working_number = 0
        self.trackers = []

        #a list of tuples with position to track and frame to assign on.
        self.track_history = []


        #the path to export the data
        self.output_path = "../output/"

        #tracking constants for getting frame types
        self.TRACK_ALL = -1
        self.NO_TRACKING = -2

        #zoom variable for setting focused frame
        self.zoom = 1

    def create_tracker_pos(self, pos_x, pos_y):
        """
        This function creates a new coordinate in history according to current frame
        """
        if self.working_number >= 0:
            location = (pos_x, pos_y, self.working_number, self.current_frame)
            self.track_history.append(location)
            print("Adding clicked location to", end="")
            print(self.track_history[-1])


    def delete_tracker_pos(self, frame_number):
        """
        This function removes an assignment on a given frame
        """

    def set_tracker_pos(self, tracktor):
        """
        This function sets the tracker position at a given frame
        """
        for i in range(len(self.track_history)):
            #if frame number is equal to set frame ex: (x,y,working_number,frame)
            if self.current_frame == self.track_history[i][3]:
                tracktor_index = self.find_tracker_index_by_id(tracktor.id)
                #if the saved tracktor in the list matches the saved working_number
                if tracktor_index == self.track_history[i][2]:
                    #assign that tracktor's clicked to the saved coordinates(x,y)
                    self.trackers[tracktor_index].clicked = (self.track_history[i][0],
                                            self.track_history[i][1])
                    # print("Assigning point from history at:", end="")
                    # print(self.track_history[i])

    def play(self):
        """
         Sets the play_state of the video to play, if not already.
        """
        if self.play_state is False:
            self.play_state = True

    def pause(self):
        """
         Sets the play_state of the video to pause, if not already.
        """
        #pause only if play is set
        if self.play_state is True:
            print("Pausing")
            self.play_state = False

    def set_frame(self, value):
        """
        Sets the current frame to process to the value passed in.
        Parameters
        ----------
        Value: float
            Assigns the current_frame
        """
        value = floor(float(value))
        self.current_frame = value
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, value)

    def previous_frame(self):
        """
        Sets the current frame to process to the previous frame.
        """
        self.set_frame(self.current_frame-1)

    def next_frame(self):
        """
        Sets the current frame to process to the next frame.
        """
        self.set_frame(self.current_frame+1)

    def add_tracker(self):
        """
        Appends a Tracktor object to the trackers list.
        """
        self.trackers.append(Tracktor())

    def delete_tracker(self, index):
        """
        !NOT COMPLETE!
        Removes a tracktor object from the trackers list
        """
        del self.trackers[index]

    #search the list of trackers by name and return -1 if not fouond
    def find_tracker_index_by_id(self, name):
        """
        Finds the index in trackers where the name matches the tracktor's id.
        Parameters
        ----------
        name: string
            compared to the tracktor's id
        """
        for i in range(len(self.trackers)):
            if name == self.trackers[i].id:
                return i
        return -1

    def set_tracker_offset(self, value):
        """
        Sets the working_number tracktor's offset to the value passed in.

        Offset is the constant subtracted from the mean value within the block
        Parameters
        ----------
        value: float
        """
        self.trackers[self.working_number].offset = value

    def set_tracker_blocksize(self, value):
        """
        Sets the working_number tracktor's block_size to the value passed in.
        block_size determines the width of the kernel used for adaptive thresholding.

        Note: block_size must be odd. This is automatically handled.
        Parameters
        ----------
        value: float
        """
        if value % 2 == 0:
            value += 1
        self.trackers[self.working_number].block_size = value

    def set_tracker_minarea(self, value):
        """
        Sets the working_number tracktor's min_area to the value passed in.

        min_area is the minimum area threhold used to detect the object of interest.
        Parameters
        ----------
        value: float
        """
        self.trackers[self.working_number].min_area = value

    def set_tracker_maxarea(self, value):
        """
        Sets the working_number tracktor's max_area to the value passed in.

        max_area is the maximum area threhold used to detect the object of interest.
        Parameters
        ----------
        value: float
        """
        self.trackers[self.working_number].max_area = value

    def set_zoom(self, value):
        """
        Sets the zoom to adjust region of interest on a specific tracktor
        Parameters:
        value: float
            The zoom multiplier
        """
        self.zoom = float(value)

    def get_frame(self, tracking=0):
        """
        Returns a processed frame based on what tracking value is passed in
        Parameters
        ----------
        tracking: int
            determines what to track.
            (-2: NONE, -1 ALL, 0...n working_number tracking index)
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
                return (True, frame)
            elif tracking == self.TRACK_ALL:
                ret, final = self.show_all(frame)

            elif tracking != self.TRACK_ALL:
                ret, final = self.process(frame, self.trackers[tracking])
                ret, final = self.get_focused_frame(final, self.trackers[tracking], self.zoom)
        if ret:
            #when we retreive a new frame, we can assume we updated values with it
            return (ret, final)
        else:
            return(True, frame)

    def get_focused_frame(self, frame, tracktor, zoom):
        """
        Returns a frame centered and zoomed in on the
        individual being tracked.
        Parameters
        ----------
        frame: ndarray, shape(n_rows, n_cols, 3)
            source image containing all three colour channels
        tracktor: tracktor object
            Contains data and basic functions for tracked individual
        zoom: int
            The value in pixels to be zoomed in. 
            This is the number of pixels to be zoomed in on all sides;
            the original aspect ratio is adjusted.
        """
        try:
            #create point from tracked individual
            pos_x = int(floor(tracktor.meas_now[0][0]))
            pos_y = int(floor(tracktor.meas_now[0][1]))

            roi = frame[int(pos_y- (self.height + self.height/zoom)):
                        pos_y + int(self.height/zoom),
                        int(pos_x -(self.width + self.width/zoom)):
                        pos_x + int(self.width/zoom)]

            #roi = cv2.resize(roi, (int(self.width), int(self.height)))
            # # #calculate edges based on points
            # min_x = int(pos_x - zoom)
            # max_x = int(pos_x + zoom)
            # min_y = int(pos_y - zoom)
            # max_y = int(pos_y + zoom)

            # #keeping aspect ratio solves constant oblongness
            # original_aspect = self.width/self.height
            # zoomed_aspect = (max_x - min_x)/(max_y - min_y)

            # print(zoomed_aspect)
            # #difference between ratios needed to change
            # adjust_aspect = zoomed_aspect - original_aspect

            # #ratio is applied to current height
            # adjust_height = (max_y - min_y) * adjust_aspect
            # #ratio is applied to current width
            # adjust_width = (max_x - min_x) * adjust_aspect

            # #when height ratio is off
            # if original_aspect > zoomed_aspect:
            #     #subtract half the ammount needed to meet original aspect
            #     min_y = int(min_y - (adjust_height/2))
            #     #add half the ammount needed to meet original aspect
            #     max_y = int(max_y + (adjust_height/2))

            # #when width ratio is off
            # elif original_aspect < zoomed_aspect:
            #     #subtract half the ammount needed to meet original aspect
            #     min_x = int(min_x - (adjust_width/2))
            #     #add half the ammount needed to meet original aspect
            #     max_x = int(max_x + (adjust_width/2))
  
            # NOTE: CAUSE OF DISTORTION, we need the outer edge to stop moving as well
            # #limit zoom to video edge
            # if min_x < 0:
            #     min_x = 0
            # if max_x > self.width:
            #     max_x = int(self.width)
            # if min_y < 0:
            #     min_y = 0
            # if max_y > self.height:
            #     max_y = int(self.height)

            # # region of interest
            # roi = frame[min_y:max_y, min_x:max_x]
            cv2.imshow("resize", roi)
            return (True, roi)

        except:
            print("Cannot focus frame")
            return (True, frame)

    def show_all(self, frame, detail=True):
        """
         Returns a frame that shows all of the tracked individuals.
         Parameters
         ----------
        frame: ndarray, shape(n_rows, n_cols, 3)
            source image containing all three colour channels
        detail: bool
            determines whether or not to display contours,
            min_area circle and max_area circle.

        """
        #iterate through all
        final = frame
        ret = True
        for i in range(len(self.trackers)):
            #accumulate tracker's processes onto final frame
            ret, final = self.process(final, self.trackers[i])

            if ret is True and detail is False:
                cv2.circle(frame, tuple([int(x) for x in self.trackers[i].meas_now[0]]), 5,
                           self.trackers[i].colour, -1, cv2.LINE_AA)

        if detail is True:
            return (True, final)
        else:
            return (True, frame)

    def process(self, frame, tracktor):
        """
        This function takes a frame, and a tracked individua and performs operations
        on the frame and applies information to the tracktor such as x,y coordinates

        First it applies a threshold, erodes and dialates to reduce noise
        Before measuring contours, it records the previous coordinates of the tracker

        Second, it applies contours to each clustered individual

        Last, hungarian_algorithm calculates minimum cost between frames to continue tracking then
        Reorder_and_draw then draws the center dot, and min/max area circles

        Parameters
        ----------
        tracktor: Tracktor Object
            The object containing all the data to be processed
        frame: ndarray, shape(n_rows, n_cols, 3)
            source image containing all three colour channels
        """
        self.set_tracker_pos(tracktor)
        try:
            #eliminate small noise
            thresh = tracktor.colour_to_thresh(frame)
            thresh = cv2.erode(thresh, tracktor.kernel, iterations=1)
            thresh = cv2.dilate(thresh, tracktor.kernel, iterations=1)

            #x, y coordinates of previous tracktor if meas_now is not empty
            if tracktor.meas_now:
                pos_x = tracktor.meas_now[0][0]
                pos_y = tracktor.meas_now[0][1]
            else:
                self.pause()
                print("Unable to track " + tracktor.id)

            #from our current frame, draw contours and display it on final frame
            final, contours = tracktor.detect_and_draw_contours(frame, thresh)

            #detect if the tracker is changed
            changed = self.tracker_changed(pos_x, pos_y, contours)
            if changed is True:
                self.pause()
                print(tracktor.id + "has changed")

            row_ind, col_ind = tracktor.hungarian_algorithm()

            #try to re-draw, separate try-except block allows redraw of min_area/max_area
            final = tracktor.reorder_and_draw(final, col_ind, self.current_frame)
            return (True, final)
        except:
            return (False, frame)


    def tracker_changed(self, pos_x, pos_y, contours):
        """
        NOTE: Function name needs a change.

        This function checks if the (pos_x, pos_y) coordinate passed in exists
        within the contours that are passed in.

        This can either be used to select and assign contours to a tracker,
        or check if tracker has changed from it's last position to new contours.
        Parameters
        ----------
        pos_x: float
            x coordinate on frame
        pos_y: float
            y coordinate on frame
        contours: list
            a list of all detected contours that pass the area based threhold criterion
        """
        #assign default flag to True (assume changed until proven not)
        changed_tracker_flag = True

        #if contours exist (not empty)
        if contours:
            #we look at all the contours
            for contour in contours:
                #check if previous position exists in updated contour (1= Yes, -1= No)
                dist = cv2.pointPolygonTest(contour, (pos_x, pos_y), False)
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
        """
        Iterates through the video collecting the data of each tracktor in trackers the list.
        Once data is collected, it exports it in a Pandas dataframe with the frame number,
        x and y coordinates.

        Each individual exports it's own CSV file.
        """
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

        while self.current_frame < self.length:
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
                                                    self.trackers[i].meas_now[0][0],#store X coord
                                                    self.trackers[i].meas_now[0][1] #store Y coord
                                                    ])
                #we received bad data and cannot process it. return -1
                except:
                    print("Could not get location from " + self.trackers[i].id +
                          " at frame " + str(self.current_frame)
                         )
                    self.trackers[i].df.append([self.current_frame, -1, -1])

        self.cap.set(cv2.CAP_PROP_FPS, self.FPS)
        print("Starting to export....")
        #once done processing the video (last frame complete), export to file
        for i in range(len(self.trackers)):
            print("Exporting: " + self.trackers[i].id)
            #load our data into a pandas dataframe
            self.trackers[i].df = pd.DataFrame(np.matrix(self.trackers[i].df),
                                               columns=['frame', 'pos_x', 'pos_y'])
            #export the data into a csv file
            self.trackers[i].df.to_csv(self.output_path + "csv/" + self.trackers[i].id + ".csv")

    # Release the video source when the object is destroyed
    def __del__(self):
        if self.cap.isOpened():
            self.cap.release()
