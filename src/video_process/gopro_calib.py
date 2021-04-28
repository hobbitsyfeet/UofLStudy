import numpy as np
"""
xdistorted=x(1+k1r2+k2r4+k3r6)
ydistorted=y(1+k1r2+k2r4+k3r6)


xdistorted=x+[2p1xy+p2(r2+2x2)]
ydistorted=y+[p1(r2+2y2)+2p2xy]

Distortioncoefficients=(k1k2p1p2k3)

CameraMatrix = [fx, 0, cx]
               [0, fy, cy]
               [0,  0,  1]

Distortion Coefficients = (k1, k2, p1, p2, k3)
"""      
# Results from: http://argus.web.unc.edu/camera-calibration-database/ 
# MTX                                         f       w       h   cx     cy      a      k1    k2     t1
# GoPro Hero4 Silver	720p-120fps-narrow	1150	1280	720	640	    360	    1	-0.31	0.17	0	
# GoPro Hero3 Black	720p-120fps-narrow  	1101	1280	720	639.5	359.5	1	-0.359	0.279	0

# DST                                   FC   W       H          C                   D
# GoPro Hero3 Black	720p-60fps-wide	    4	1280	720	1.038962477337479	0.011039937655688	

GOPRO_HERO4_SILVER_NARROW_MTX = np.array([
                                    [1150, 0, 640],
                                    [0 ,1150, 360],
                                    [0,    0,   1],
                                ])
# GOPRO_HERO4_SILVER_NARROW_DST = np.array([-0.31,0.17, ,])


GOPRO_HERO3_BLACK_NARROW_MTX = np.array([
                       [1101, 0, 639.5],
                       [0 ,1150, 359.5],
                       [0,    0,   1],
                                ])


GOPRO_HERO3_SILVER ={"Resolution_x":720, "FOV":None}


    