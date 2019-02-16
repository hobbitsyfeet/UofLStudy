"""
This takes the camera's details and uses it to calculate and adjust settings
"""

class camera():
    """
    Initializes the the camera had.
    """
    def __init__(self, focal_length, 
                sensor_width, sensor_height,
                dist_from_ground=0):
        self.focal_length = focal_length
        self.sensor_width = sensor_width
        self.sensor_height = sensor_height
        self.dist_from_ground = dist_from_ground
