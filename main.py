import numpy as np
from tracktor import tracktor
import cv2
import sys
import time

DISPLAY_FINAL = 0
DISPLAY_THRESH = 1
DISPLAY_CROP = 2

CAPTURE_INPUT = None
CAPTURE_INPUT_LIVE = 0
CAPTURE_INPUT_VIDEO = 1

def load_capture():
    print("Enter 'live' or name of video in video folder (include extention)")
    usr_input = input()
    if usr_input == "live" or usr_input == '0':
        CAPTURE_INPUT = CAPTURE_INPUT_LIVE
        return cv2.VideoCapture(0), CAPTURE_INPUT
    else:
        CAPTURE_INPUT = CAPTURE_INPUT_VIDEO
        return cv2.VideoCapture("./videos/" + usr_input), CAPTURE_INPUT

if __name__ == '__main__':
    #create a generic instance of tractor
    tr = tracktor()
    #input_vidpath = "./videos/mouse_video.mp4"
    ## Start time
    start = time.time()

    #loads cap as either live or from video, and returns a variable flag
    cap, CAPTURE_INPUT = load_capture()

    #cap = cv2.VideoCapture(0)
    #cap = cv2.VideoCapture(input_vidpath)
    #cap = cv2.imread("./fallot.png",cv2.IMREAD_COLOR)

    if cap.isOpened() == False:
        sys.exit('Video file cannot be read! Please check input_vidpath to ensure it is correctly pointing to the video file')

    #set default display type to final processed frame
    display_type = DISPLAY_FINAL
    #flag used to invert threshold (on/off)
    invert_flag = False

    #Start Running
    while(True):
        # Capture frame-by-frame
        ret, frame = cap.read()

        #display frame is a variable to choose between filters to display
        this = cap.get(1)
        cv2.namedWindow('frame')

        if ret == True:
            #preprocess the frames, adding a threshold, erode and dialing to
            #eliminate small noise
            thresh = tr.colour_to_thresh(frame)
            thresh = cv2.erode(thresh, tr.kernel, iterations = 1)
            thresh = cv2.dilate(thresh, tr.kernel, iterations = 1)

            #test by inverting the threshold
            if invert_flag:
                thresh = cv2.bitwise_not(thresh)


            final, contours = tr.detect_and_draw_contours(frame, thresh)
            #try:
            #from our current frame, draw contours and display it on final frame

            #calculate cost of previous to current
            try:    row_ind, col_ind = tr.hungarian_algorithm()
            except:
                pass
            #try to re-draw, separate try-except block allows redraw of min_area/max_area
            try:
                final = tr.reorder_and_draw(final, col_ind, this)
            except:
                pass
            #except:
                #individual was lost, prevent crashing with pass
            #    pass
            # Create output dataframe
            #for i in range(n_inds):
            #    df.append([this, meas_now[i][0], meas_now[i][1], s_id[i]])

            # Display the resulting frame
            if display_type is DISPLAY_FINAL:
                display_frame = final
            elif display_type is DISPLAY_THRESH:
                display_frame = thresh

            #out.write(final)
            cv2.imshow('frame', display_frame)
            key = cv2.waitKey(1)
            tr.get_input(key)

            #one '1'
            if key == ord('1'):
                    display_type = DISPLAY_FINAL
                    print("Final")
            #two '2'
            elif key == ord('2'):
                    display_type = DISPLAY_THRESH
                    print("Thresh")

        #this frame is last frame, stop
        if tr.last == this and CAPTURE_INPUT == CAPTURE_INPUT_VIDEO:
            break


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
