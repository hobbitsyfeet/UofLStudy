import numpy as np
from tracktor import tracktor
import cv2
import sys
import time

DISPLAY_FINAL = 0
DISPLAY_THRESH = 1
DISPLAY_CROP = 2
PAUSE_VIDEO = 3

CAPTURE_INPUT = None
CAPTURE_INPUT_LIVE = 0
CAPTURE_INPUT_VIDEO = 1

CHANGE_POS_FLAG = False
def load_capture():
    print("Enter 'live' or name of video in video folder (include extention)")
    usr_input = input()
    if usr_input == "live" or usr_input == '0':
        CAPTURE_INPUT = CAPTURE_INPUT_LIVE
        return cv2.VideoCapture(0), CAPTURE_INPUT
    else:
        CAPTURE_INPUT = CAPTURE_INPUT_VIDEO
        return cv2.VideoCapture("./videos/" + usr_input), CAPTURE_INPUT

def change_flag(x):
    CHANGE_POS_FLAG = True



if __name__ == '__main__':

    #create a generic instance of tractor
    tr = tracktor()

    ## Start time
    start = time.time()

    #loads cap as either live or from video, and returns a variable flag
    cap, CAPTURE_INPUT = load_capture()

    if cap.isOpened() == False:
        sys.exit('Video file cannot be read! Please check input_vidpath to ensure it is correctly pointing to the video file')


    #set default display type to final processed frame
    display_type = DISPLAY_FINAL
    #flag used to invert threshold (on/off)
    invert_flag = False
    #assign a window name for further assignment to it
    cv2.namedWindow('frame',1)
    #create trackbar from start to one before last (so that it does't crash)
    cv2.createTrackbar("frame number","frame",0,int(cap.get(cv2.CAP_PROP_FRAME_COUNT)-1),change_flag)

    #Start Running
    while(True):
        key = cv2.waitKey(1)

        #set the capture to the frame set by the trackbar
        cap.set(cv2.CAP_PROP_POS_FRAMES,cv2.getTrackbarPos(trackbarname="frame number",winname="frame"))

        #display frame is a variable to choose between filters to display
        if display_type == PAUSE_VIDEO:

            if key ==ord(','):
                #set the trackbar to the next frame
                cv2.setTrackbarPos(trackbarname="frame number",winname="frame",pos=int(tr.last-1))
                this = tr.last - 1
                print("nudge Left")
            elif key == ord('.'):
                #set the Trackbar to previous frame
                cv2.setTrackbarPos(trackbarname="frame number",winname="frame",pos=int(tr.last+1))
                this = tr.last + 1
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

        #tr.crop(500,500,frame)
        if ret == True:
            #preprocess the frames, adding a threshold, erode and dialing to
            #eliminate small noise
            thresh = tr.colour_to_thresh(frame)
            thresh = cv2.erode(thresh, tr.kernel, iterations = 1)
            thresh = cv2.dilate(thresh, tr.kernel, iterations = 1)

            #test inverting the threshold
            if invert_flag:
                thresh = cv2.bitwise_not(thresh)

            #from our current frame, draw contours and display it on final frame
            final, contours = tr.detect_and_draw_contours(frame, thresh)

            #calculate cost of previous to currentmouse_video
            try:    row_ind, col_ind = tr.hungarian_algorithm()
            except:
                print("Cannot calculate cost")
                pass
            #try to re-draw, separate try-except block allows redraw of min_area/max_area
            try:
                final = tr.reorder_and_draw(final, col_ind, this)
            except:
                print("Can't draw")
                pass

            # Create output dataframe
            #for i in range(n_inds):
            #    df.append([this, meas_now[i][0], meas_now[i][1], s_id[i]])

            # Display the resulting frame
            if display_type is DISPLAY_FINAL:
                display_frame = final
            elif display_type is DISPLAY_THRESH:
                display_frame = thresh
            elif display_type is PAUSE_VIDEO:
                display_frame = final

            #out.write(final)
            cv2.imshow('frame', display_frame)


            #one '1'
            if key == ord('1'):
                display_type = DISPLAY_FINAL
                print("Final")
            #two '2
            elif key == ord('2'):
                display_type = DISPLAY_THRESH
                print("Thresh")


            if key == ord(' '):
                if display_type is not PAUSE_VIDEO:
                    display_type = PAUSE_VIDEO
                    print("PAUSING")
                else:
                    display_type = DISPLAY_FINAL
                    print("UNPAUSING")

        #this frame is last frame, stop
        #if this ==  and CAPTURE_INPUT == CAPTURE_INPUT_VIDEO:
        #    break


        #last frame is now this frame
        tr.last = this


    ## Write positions to file
    #df = pd.DataFrame(np.matrix(df), columns = ['frame','pos_x','pos_y','id'])
    #df.to_csv(output_filepath, sep=',')

    ## When everything done, release the capture
    cap.release()
    #out.release()
    cv2.destroyAllWindows()
    cv2.waitKey(1)

    ## End time and duration
    end = time.time()
    duration = end - start
    print("--- %s seconds ---" %duration)
