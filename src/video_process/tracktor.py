import numpy as np
import pandas as pd
import cv2
import sys
from sklearn.cluster import KMeans
from scipy.optimize import linear_sum_assignment
from scipy.spatial.distance import cdist
from random import randrange

class tracktor():
    def __init__(self,
        s_id ="NO_ID",
        colour = (randrange(0,255,1),randrange(0,255,1),randrange(0,255,1)),
        block_size = 51, offset = 20,
        min_area = 100, max_area = 5000,
        scaling = 1.0
        ):

        # colours is a vector of BGR values which are used to identify individuals in the video
        # s_id is spider id and is also used for individual identification
        # since we only have two individuals, the program will only use the first two elements from these arrays (s_id and colours)
        # number of elements in colours should be greater than n_inds (THIS IS NECESSARY FOR VISUALISATION ONLY)
        # number of elements in s_id should be greater than n_inds (THIS IS NECESSARY TO GET INDIVIDUAL-SPECIFIC DATA)

        #where each tracktor takes care of one individual, we do not need this.
        #self.n_inds = n_inds
        self.s_id = s_id
        self.colour = colour

        # this is the block_size and offset used for adaptive thresholding (block_size should always be odd)
        # these values are critical for tracking performance
        if block_size % 2 != 1:
            self.block_size = block_size + 1
        else:
            self.block_size = block_size
        self.offset = offset

        # minimum area and maximum area occupied by the animal in number of pixels
        # this parameter is used to get rid of other objects in view that might be hard to threshold out but are differently sized
        # in this case, the range is wide because males vastly smaller than females
        self.min_area = min_area
        self.max_area = max_area

        # the scaling parameter can be used to speed up tracking if video resolution is too high (use value 0-1)
        self.scaling = scaling

        # kernel for erosion and dilation
        # useful since thin spider limbs are sometimes detected as separate objects
        self.kernel = np.ones((5,5),np.uint8)

        # mot determines whether the tracker is being used in noisy conditions to track a single object or for multi-object
        # using this will enable k-means clustering to force n_inds number of animals
        self.mot = False

        df = []

        codec = 'DIVX' # try other codecs if the default doesn't work ('DIVX', 'avc1', 'XVID') note: this list is non-exhaustive

        ## Video writer class to output video with contour and centroid of tracked object(s)
        # make sure the frame size matches size of array 'final'
        fourcc = cv2.VideoWriter_fourcc(*codec)
        #output_framesize = (int(cap.read()[1].shape[1]*scaling),int(cap.read()[1].shape[0]*scaling))
        #out = cv2.VideoWriter(filename = output_vidpath, fourcc = fourcc, fps = 60.0, frameSize = output_framesize, isColor = True)

        ## Individual location(s) measured in the last and current step
        self.meas_last = list(np.zeros((1,2)))
        self.meas_now = list(np.zeros((1,2)))

        #data frame?
        self.df = []


    def colour_to_thresh(self,frame):
        """
        This function retrieves a video frame and preprocesses it for object tracking.
        The code blurs image to reduce noise, converts it to greyscale and then returns a
        thresholded version of the original image.

        Parameters
        ----------
        frame: ndarray, shape(n_rows, n_cols, 3)
            source image containing all three colour channels
        block_size: int(optional), default = 31
            block_size determines the width of the kernel used for adaptive thresholding.
            Note: block_size must be odd. If even integer is used, the programme will add
            1 to the block_size to make it odd.
        offset: int(optional), default = 25
            constant subtracted from the mean value within the block

        Returns
        -------
        thresh: ndarray, shape(n_rows, n_cols, 1)
            binarised(0,255) image
        """
        blur = cv2.blur(frame, (5,5))
        gray = cv2.cvtColor(blur, cv2.COLOR_BGR2GRAY)
        thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, self.block_size, self.offset)
        return thresh

    def detect_and_draw_contours(self,frame, thresh):
        """
        This function detects contours, thresholds them based on area and draws them.

        Parameters
        ----------
        frame: ndarray, shape(n_rows, n_cols, 3)
            source image containing all three colour channels
        thresh: ndarray, shape(n_rows, n_cols, 1)
            binarised(0,255) image
        meas_last: array_like, dtype=float
            individual's location on previous frame
        meas_now: array_like, dtype=float
            individual's location on current frame
        min_area: int
            minimum area threhold used to detect the object of interest
        max_area: int
            maximum area threhold used to detect the object of interest

        Returns
        -------
        final: ndarray, shape(n_rows, n_cols, 3)
            final output image composed of the input frame with object contours
            and centroids overlaid on it
        contours: list
            a list of all detected contours that pass the area based threhold criterion
        meas_last: array_like, dtype=float
            individual's location on previous frame
        meas_now: array_like, dtype=float
            individual's location on current frame
        """
        # Detect contours and draw them based on specified area thresholds
        img, contours, hierarchy = cv2.findContours(thresh.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)

        final = frame.copy()

        i = 0
        self.meas_last = self.meas_now.copy()
        #del self.meas_now[:]
        #assigning to empty doesn't crash, less efficient but a size of 2 wont make a difference
        self.meas_now = []
        while i < len(contours):
            area = cv2.contourArea(contours[i])
            if area < self.min_area or area > self.max_area:
                del contours[i]
            else:
                cv2.drawContours(final, contours, i, (0,0,255), 1)
                M = cv2.moments(contours[i])
                if M['m00'] != 0:
                	cx = M['m10']/M['m00']
                	cy = M['m01']/M['m00']
                else:
                	cx = 0
                	cy = 0
                self.meas_now.append([cx,cy])
                i += 1
        return final, contours

    def apply_k_means(self,contours):
        """
        This function applies the k-means clustering algorithm to separate merged
        contours. The algorithm is applied when detected contours are fewer than
        expected objects(number of animals) in the scene.

        Parameters
        ----------
        contours: list
            a list of all detected contours that pass the area based threhold criterion
        n_inds: int
            total number of individuals being tracked
        meas_now: array_like, dtype=float
            individual's location on current frame

        Returns
        -------
        contours: list
            a list of all detected contours that pass the area based threhold criterion
        meas_now: array_like, dtype=float
            individual's location on current frame
        """

        #del self.meas_now[:]
        self.meas_now = []
        # Clustering contours to separate individuals
        myarray = np.vstack(contours)
        myarray = myarray.reshape(myarray.shape[0], myarray.shape[2])

        kmeans = KMeans(n_clusters=1, random_state=0, n_init = 50).fit(myarray)
        l = len(kmeans.cluster_centers_)

        for i in range(l):
            x = int(tuple(kmeans.cluster_centers_[i])[0])
            y = int(tuple(kmeans.cluster_centers_[i])[1])
            self.meas_now.append([x,y])
        return contours

    def hungarian_algorithm(self):
        """
        The hungarian algorithm is a combinatorial optimisation algorithm used
        to solve assignment problems. Here, we use the algorithm to reduce noise
        due to ripples and to maintain individual identity. This is accomplished
        by minimising a cost function; in this case, euclidean distances between
        points measured in previous and current step. The algorithm here is written
        to be flexible as the number of contours detected between successive frames
        changes. However, an error will be returned if zero contours are detected.

        Parameters
        ----------
       self.meas_last: array_like, dtype=float
            individual's location on previous frame
        meas_now: array_like, dtype=float
            individual's location on current frame

        Returns
        -------
        row_ind: array, dtype=int64
            individual identites arranged according to input ``meas_last``
        col_ind: array, dtype=int64
            individual identities rearranged based on matching locations from
            ``meas_last`` to ``meas_now`` by minimising the cost function
        """
        self.meas_last = np.array(self.meas_last)
        self.meas_now = np.array(self.meas_now)
        if self.meas_now.shape !=self.meas_last.shape:
            if self.meas_now.shape[0] <self.meas_last.shape[0]:
                while self.meas_now.shape[0] !=self.meas_last.shape[0]:
                   self.meas_last = np.delete(self.meas_last,self.meas_last.shape[0]-1, 0)
            else:
                result = np.zeros(self.meas_now.shape)
                result[:self.meas_last.shape[0],:self.meas_last.shape[1]] = self.meas_last
                self.meas_last = result

        self.meas_last = list(self.meas_last)
        self.meas_now = list(self.meas_now)
        cost = cdist(self.meas_last, self.meas_now)
        row_ind, col_ind = linear_sum_assignment(cost)
        return row_ind, col_ind

    def reorder_and_draw(self,final, col_ind, fr_no):
        """
        This function reorders the measurements in the current frame to match
        identity from previous frame. This is done by using the results of the
        hungarian algorithm from the array col_inds.

        Parameters
        ----------
        final: ndarray, shape(n_rows, n_cols, 3)
            final output image composed of the input frame with object contours
            and centroids overlaid on it
        colours: list, tuple
            list of tuples that represent colours used to assign individual identities
        n_inds: int
            total number of individuals being tracked
        col_ind: array, dtype=int64
            individual identities rearranged based on matching locations from
            ``meas_last`` to ``meas_now`` by minimising the cost function
        meas_now: array_like, dtype=float
            individual's location on current frame
        df: pandas.core.frame.DataFrame
            this dataframe holds tracked coordinates i.e. the tracking results
        mot: bool
            this boolean determines if we apply the alogrithm to a multi-object
            tracking problem

        Returns
        -------
        final: ndarray, shape(n_rows, n_cols, 3)
            final output image composed of the input frame with object contours
            and centroids overlaid on it
        meas_now: array_like, dtype=float
            individual's location on current frame
        df: pandas.DataFrame
            this dataframe holds tracked coordinates i.e. the tracking results
        """
        # Reorder contours based on results of the hungarian algorithm
        equal = np.array_equal(col_ind, list(range(len(col_ind))))
        if equal == False:
            current_ids = col_ind.copy()
            reordered = [i[0] for i in sorted(enumerate(current_ids), key=lambda x:x[1])]
            self.meas_now = [x for (y,x) in sorted(zip(reordered,self.meas_now))]

        for i in range(1):
            cv2.circle(final, tuple([int(x) for x in self.meas_now[i]]), 5, self.colour, -1, cv2.LINE_AA)


            #circle for min_area (A = pi*r^2) => r = sqrt(A/pi)
            min_radius = int(np.sqrt(self.min_area/np.pi))
            cv2.circle(final, tuple([int(x) for x in self.meas_now[i]]), min_radius, (255,255,255), 1, cv2.LINE_AA)

            max_radius = int(np.sqrt(self.max_area/np.pi))
            cv2.circle(final, tuple([int(x) for x in self.meas_now[i]]), max_radius, (0,0,255), 1, cv2.LINE_AA)

        # add frame number
        font = cv2.FONT_HERSHEY_SCRIPT_SIMPLEX
        #cv2.putText(final, str(int(fr_no)), (5,30), font, 1, (255,255,255), 2)

        return final

    def reject_outliers(data, m):
        """
        This function removes any outliers from presented data.

        Parameters
        ----------
        data: pandas.Series
            a column from a pandas dataframe that needs smoothing
        m: float
            standard deviation cutoff beyond which, datapoint is considered as an outlier

        Returns
        -------
        index: ndarray
            an array of indices of points that are not outliers
        """
        d = np.abs(data - np.nanmedian(data))
        mdev = np.nanmedian(d)
        s = d/mdev if mdev else 0.
        return np.where(s < m)
