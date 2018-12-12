import numpy as np
from tracktor import tracktor
import cv2
import sys
import time

if __name__ == '__main__':
    #create a generic instance of tractor
    tr = tracktor()
    ## Start time
    start = time.time()

    ## Open video (0 == live camera)
    cap = cv2.VideoCapture(0)
    #cap = cv2.VideoCapture(input_vidpath)
    #cap = cv2.imread("./fallot.png",cv2.IMREAD_COLOR)
    if cap.isOpened() == False:
        sys.exit('Video file cannot be read! Please check input_vidpath to ensure it is correctly pointing to the video file')

    display_type = "Final"
    invert_flag = False
    #Start Running
    while(True):
        # Capture frame-by-frame
        ret, frame = cap.read()

        #display frame is a variable to choose between filters to display
        this = cap.get(1)

        if ret == True:

            thresh = tr.colour_to_thresh(frame)
            thresh = cv2.erode(thresh, tr.kernel, iterations = 1)
            thresh = cv2.dilate(thresh, tr.kernel, iterations = 1)
            if invert_flag:
                thresh = cv2.bitwise_not(thresh)
            final, contours = tr.detect_and_draw_contours(frame, thresh)

            try:
                row_ind, col_ind = tr.hungarian_algorithm()
                final = tr.reorder_and_draw(final, col_ind, this)
            except:
                #if these functions cannot compute, we ignore their failiure and continue
                pass

            # Create output dataframe
            #for i in range(n_inds):
            #    df.append([this, meas_now[i][0], meas_now[i][1], s_id[i]])

            # Display the resulting frame
            if display_type is "Final":
                display_frame = final
            elif display_type is "Thresh":
                display_frame = thresh
            #out.write(final)
            cv2.imshow('frame', display_frame)
            key = cv2.waitKey(1)
            tr.get_input(key)

            #one '1'
            if key == 49:
                display_type = "Frame"
                print("Frame")
            #two '2'
            elif key == 50:
                display_type = "Final"
                print("Final")
            #three '3'
            elif key == 51:
                display_type = "Thresh"
                print("Thresh")


        if tr.last == this:
            continue

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
