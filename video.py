import numpy as np
from tracktor import tracktor
import cv2
import sys


def nothing(x):
    return

class video():
    def __init__(self,
                    window_name ="NO_NAME",
                    number_of_trackers = 1
                    ):
        #name of project?
        self.window_name =""


        self.trackers = [tracktor()]*number_of_trackers

        #constants for interaction
        self.DISPLAY_FINAL = 0
        self.DISPLAY_THRESH = 1
        self.PAUSE_VIDEO = 3

        #assignment we use to choose different processes
        self.display_type = self.DISPLAY_FINAL


    def load(self,path = ""):
        """
        this loads a video up by retreiving it's path, if there is none it
        tries to load a video from default camera
        Intended use: if there is no path assigned initally, we can still retreive
        video path through 'path'

        Parameters
        ----------
        path : string
            This is a string to the path of the video
        """
        print(path)
        if path == "live" or path == '0':
            return self.run_live()
        else:
            return self.run_video(path)


    def run_video(self,path):
        print("Loading video...")
        print(path)
        cap = cv2.VideoCapture(path)

        if cap.isOpened() == False:
            sys.exit('Video file cannot be read! Please check input_vidpath to ensure it is correctly pointing to the video file')
        #assign a window name for further assignment to it
        cv2.namedWindow('frame',1)
        #create trackbar from start to one before last (so that it does't crash)
        cv2.createTrackbar("frame number","frame",0,int(cap.get(cv2.CAP_PROP_FRAME_COUNT)-1),nothing)

        last=0
        #Start Running
        while(True):
            key = cv2.waitKey(1)

            #set the capture to the frame set by the trackbar
            cap.set(cv2.CAP_PROP_POS_FRAMES,cv2.getTrackbarPos(trackbarname="frame number",winname="frame"))

            #display frame is a variable to choose between filters to display
            if self.display_type == self.PAUSE_VIDEO:

                if key ==ord(','):
                    #set the trackbar to the next frame
                    cv2.setTrackbarPos(trackbarname="frame number",winname="frame",pos=int(last-1))
                    this = last - 1
                    print("nudge Left")
                elif key == ord('.'):
                    #set the Trackbar to previous frame
                    cv2.setTrackbarPos(trackbarname="frame number",winname="frame",pos=int(last+1))
                    this = last + 1
                    print("nudge Right")
                else:
                    #we do not nudge, but if the Trackbar is moved, we update to that position
                    this = cv2.getTrackbarPos(trackbarname="frame number",winname="frame")

                #set the capture to frame assigned to 'this'
                cap.set(1,this)
                #read from frame which capture was set to
                ret, frame = cap.read()
            else:
                #read the next frame
                ret, frame = cap.read()
                this = cap.get(1)
                #set trackbar position to current frame
                cv2.setTrackbarPos(trackbarname="frame number",winname="frame",pos=int(this))

            #crop(500,500,frame)
            if ret == True:
                processed_frame = self.process(self.trackers[0],frame,this)
                # Create output dataframe
                #for i in range(n_inds):
                #    df.append([this, meas_now[i][0], meas_now[i][1], s_id[i]])

                #out.write(final)
                cv2.imshow('frame', processed_frame)

                if key == ord(' '):
                    if self.display_type is not self.PAUSE_VIDEO:
                        self.display_type = self.PAUSE_VIDEO
                        print("PAUSING")
                    else:
                        self.display_type = self.DISPLAY_FINAL
                        print("UNPAUSING")

            #this frame is last frame, stop
            #if this ==  and CAPTURE_INPUT == CAPTURE_INPUT_VIDEO:
            #    break

            #last frame is now this frame
            last = this


        ## Write positions to file
        #df = pd.DataFrame(np.matrix(df), columns = ['frame','pos_x','pos_y','id'])
        #df.to_csv(output_filepath, sep=',')

        ## When everything done, release the capture
        cap.release()
        #out.release()
        cv2.destroyAllWindows()


    def run_live(self):
        print("Streaming video...")
        #loads cap as either live or from video, and returns a variable flag
        cap = cv2.VideoCapture(0)

        if cap.isOpened() == False:
            sys.exit('Video file cannot be read! Please check input_vidpath to ensure it is correctly pointing to the video file')

        #Start Running
        while(True):
            ret, frame = cap.read()
            this = cap.get(1)
            key = cv2.waitKey(1)
            if ret == True:
                processed_frame = self.process(self.trackers[0],frame,this)
                # Create output dataframe
                #for i in range(n_inds):
                #    df.append([this, meas_now[i][0], meas_now[i][1], s_id[i]])
                #out.write(final)
                cv2.imshow('frame', processed_frame)

                #one '1'
                if key == ord('1'):
                    self.display_type = self.DISPLAY_FINAL
                    print("Final")
                #two '2
                elif key == ord('2'):
                    self.display_type = self.DISPLAY_THRESH
                    print("Thresh")

        ## Write positions to file
        #df = pd.DataFrame(np.matrix(df), columns = ['frame','pos_x','pos_y','id'])
        #df.to_csv(output_filepath, sep=',')

        ## When everything done, release the capture
        cap.release()
        #out.release()
        cv2.destroyAllWindows()

    def process(self,tracktor,frame,this):
        #preprocess the frames, adding a threshold, erode and dialing to
        #eliminate small noise
        thresh = tracktor.colour_to_thresh(frame)
        thresh = cv2.erode(thresh, tracktor.kernel, iterations = 1)
        thresh = cv2.dilate(thresh, tracktor.kernel, iterations = 1)

        #from our current frame, draw contours and display it on final frame
        final, contours = tracktor.detect_and_draw_contours(frame, thresh)

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
        return self.display_frame

    def close(self,capture):
        pass

    def export(self):
        pass
