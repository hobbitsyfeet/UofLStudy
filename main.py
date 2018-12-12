import numpy as np
import pandas as pd
import tracktor as tr
import cv2
import sys
import time
from scipy.optimize import linear_sum_assignment
from scipy.spatial.distance import cdist




if __name__ == '__main__':
    # colours is a vector of BGR values which are used to identify individuals in the video
    # s_id is spider id and is also used for individual identification
    # since we only have two individuals, the program will only use the first two elements from these arrays (s_id and colours)
    # number of elements in colours should be greater than n_inds (THIS IS NECESSARY FOR VISUALISATION ONLY)
    # number of elements in s_id should be greater than n_inds (THIS IS NECESSARY TO GET INDIVIDUAL-SPECIFIC DATA)
    n_inds = 1
    s_id = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
    colours = [(0,0,255),(0,255,255),(255,0,255),(0,0,0),(255,255,0),(255,0,0),(0,255,0),(255,255,255)]

    # this is the block_size and offset used for adaptive thresholding (block_size should always be odd)
    # these values are critical for tracking performance
    block_size = 7
    offset = 20

    # minimum area and maximum area occupied by the animal in number of pixels
    # this parameter is used to get rid of other objects in view that might be hard to threshold out but are differently sized
    # in this case, the range is wide because males vastly smaller than females
    min_area = 10
    max_area = 2000

    # the scaling parameter can be used to speed up tracking if video resolution is too high (use value 0-1)
    scaling = 1.0

    # kernel for erosion and dilation
    # useful since thin spider limbs are sometimes detected as separate objects
    kernel = np.ones((5,5),np.uint8)

    # mot determines whether the tracker is being used in noisy conditions to track a single object or for multi-object
    # using this will enable k-means clustering to force n_inds number of animals
    mot = True

    # name of source video and paths
    video = 'test'
    input_vidpath = '../videos/' + video + '.MP4'
    #output_vidpath = '../tracktor/output/' + video + '.avi'
    #output_filepath = '../tracktor/output/' + video + '.csv'
    codec = 'DIVX' # try other codecs if the default doesn't work ('DIVX', 'avc1', 'XVID') note: this list is non-exhaustive
    ## Start time
    start = time.time()

    ## Open video
    cap = cv2.VideoCapture(0)
    #cap = cv2.VideoCapture(input_vidpath)
    if cap.isOpened() == False:
        sys.exit('Video file cannot be read! Please check input_vidpath to ensure it is correctly pointing to the video file')

    ## Video writer class to output video with contour and centroid of tracked object(s)
    # make sure the frame size matches size of array 'final'
    fourcc = cv2.VideoWriter_fourcc(*codec)
    #output_framesize = (int(cap.read()[1].shape[1]*scaling),int(cap.read()[1].shape[0]*scaling))
    #out = cv2.VideoWriter(filename = output_vidpath, fourcc = fourcc, fps = 60.0, frameSize = output_framesize, isColor = True)

    ## Individual location(s) measured in the last and current step
    meas_last = list(np.zeros((n_inds,2)))
    meas_now = list(np.zeros((n_inds,2)))

    last = 0
    df = []

    while(True):
        # Capture frame-by-frame
        ret, frame = cap.read()

        this = cap.get(1)
        if ret == True:
            #frame = cv2.resize(frame, None, fx = scaling, fy = scaling, interpolation = cv2.INTER_LINEAR)

            # Apply mask to aarea of interest
            #mask = np.zeros(frame.shape)
            #mask = cv2.rectangle(mask, (100, 30), (2440,1080), (255,255,255), -1)
            #frame[mask ==  0] = 0

            thresh = tr.colour_to_thresh(frame, block_size, offset)
            thresh = cv2.erode(thresh, kernel, iterations = 1)
            thresh = cv2.dilate(thresh, kernel, iterations = 1)
            final, contours, meas_last, meas_now = tr.detect_and_draw_contours(frame, thresh, meas_last, meas_now, min_area, max_area)

            try:
                row_ind, col_ind = tr.hungarian_algorithm(meas_last, meas_now)

                final, meas_now, df = tr.reorder_and_draw(final, colours, n_inds, col_ind, meas_now, df, mot, this)
            except:
                pass
            # Create output dataframe
            #for i in range(n_inds):
            #    df.append([this, meas_now[i][0], meas_now[i][1], s_id[i]])

            # Display the resulting frame
            #out.write(final)
            cv2.imshow('frame', final)
            key = cv2.waitKey(1)
            #if key is not -1:
                #print(key)
            if key == 27:
                break
            elif key == 43:
                offset = offset + 1
                print("Offset:", end = "")
                print(offset)
            elif key == 45:
                offset = offset - 1
                print("Offset:", end = "")
                print(offset)
            elif key == 42:
                block_size = block_size + 2
                print("BlockSize:", end = "")
                print(block_size)
            elif key == 47:
                block_size = block_size - 2
                print("BlockSize:", end = "")
                print(block_size)
        if last == this:
            continue

        last = this

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
