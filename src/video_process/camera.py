"""
This takes the camera's details and uses it to calculate and adjust settings
"""
import numpy as np
import cv2

class Camera():
    """
    Initializes the the camera had.
    """
    def __init__(self, name,
                focal_length,
                #sensor_width, sensor_height, these are determined from resolution?
                dist_from_ground=0):
        self.name = name
        self.focal_length = focal_length
        # self.sensor_width = sensor_width
        # self.sensor_height = sensor_height
        self.dist_from_ground = dist_from_ground

        #calibrate will be a numpy matrix of intrinsic parameters of the camera
        self.calibrated = []

    def calibrate(self, video_source="./", dim_x=7, dim_y=7):
        """
        This will call a reference to a video taken, based on ?camera information?
        and will calibrate the camera and save the results in self.calibrated
        Probably calibrate to default video link

        With the calibration we get the distortion coefficients.
        NOTE We use a 7x7 grid
        
        Returns
        -------
            Camera matrix, distortion coefficients, rotation and translation vectors

        Distortion Coefficients = (k1, k2, p1, p2, k3)

        Camera Matrix:
            focal length (fx,fy), optical centers (cx, cy)
            [fx, 0 , cx]
            [0 , fy, cy]
            [0 , 0 , 1 ]
        
        """
        cap = cv2.VideoCapture(video_source)
        if not cap.isOpened():
            raise ValueError("Unable to open video source", video_source)
        print("Calibrating Camera...")

        cap = cv2.VideoCapture(video_source)
        while True:
            corners_found = 0
            # termination criteria
            criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

            # prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
            objp = np.zeros((dim_x*dim_y, 3), np.float32)
            objp[:, :2] = np.mgrid[0:dim_x, 0:dim_y].T.reshape(-1, 2)

            # Arrays to store object points and image points from all the images.
            objpoints = [] # 3d point in real world space
            framepoints = [] # 2d points in image plane.
            ret, frame = cap.read()
            if ret:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

                if cv2.waitKey(30) & 0xFF == ord('q'):
                    break

                # print("Finding Corners... ", end ="")
                # Find the chess board corners
                ret, corners = cv2.findChessboardCorners(gray, (dim_x, dim_y), None)
                # print(ret)
                # If found, add object points, image points (after refining them)
                if ret:
                    corners_found += 1
                    objpoints.append(objp)

                    corners2 = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
                    framepoints.append(corners2)

                    # Draw and display the corners
                    frame = cv2.drawChessboardCorners(frame, (dim_x, dim_y), corners2, ret)

                    cv2.imshow('frame', frame)

                    ret, cam_mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, framepoints, gray.shape[::-1], None,None)
        
                    w = np.size(frame, 1)
                    h = np.size(frame, 0)
                    newcameramtx, roi=cv2.getOptimalNewCameraMatrix(cam_mtx, dist, (w, h), 1, (w, h))

                    # undistort
                    dst = cv2.undistort(frame, cam_mtx, dist, None, newcameramtx)
                    # crop the image
                    x,y,w,h = roi
                    dst = dst[y:y+h, x:x+w]
                    if x+w == 0:
                        print(cam_mtx)
                        print("Bad export. Trying next frame")
                        continue

                    # crop the image
                    x,y,w,h = roi
                    dst = dst[y:y+h, x:x+w]
                    cv2.imwrite('calibresult.png',dst)

                    mean_error = 0
                    tot_error = 0
                    for i in range(len(objpoints)):
                        framepoints2, _ = cv2.projectPoints(objpoints[i], rvecs[i], tvecs[i], cam_mtx, dist)
                        error = cv2.norm(framepoints[i], framepoints2, cv2.NORM_L2)/len(framepoints2)
                        tot_error += error

                    print("Mean Error: " + str(mean_error/len(objpoints)))
                    
                #we found a valid frame so we can use it to calculate
                    break
                else:
                    print("Cannot find corners")
            else:
                break
        cap.release()
        cv2.destroyAllWindows()
        return cam_mtx, newcameramtx

    def print_info(self):
        """
        Print's the information of the camera loaded
        """
        pass

if __name__ == "__main__":
    cam = Camera("Gopro Hero 7 Black", 15)
    cam.calibrate("./videos/Checkerboards/board_1280x960.MP4")
