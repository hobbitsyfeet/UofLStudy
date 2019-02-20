"""
This takes the camera's details and uses it to calculate and adjust settings
"""
import cv2

class camera():
    """
    Initializes the the camera had.
    """
    def __init__(self, name,
                focal_length,
                sensor_width, sensor_height,
                dist_from_ground=0):
        self.name = name
        self.focal_length = focal_length
        self.sensor_width = sensor_width
        self.sensor_height = sensor_height
        self.dist_from_ground = dist_from_ground

        #calibrate will be a numpy matrix of intrinsic parameters of the camera
        self.calibrated = []

    def calibrate(self, vid_dir):
        """
        This will call a reference to a video taken, based on ?camera information?
        and will calibrate the camera and save the results in self.calibrated
        Probably calibrate to default video link

        With the calibration we get the distortion coefficients.
        NOTE We use a 5x6 grid
        
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
        pass

    def print_info(self):
        """
        Print's the information of the camera loaded
        """
        pass
