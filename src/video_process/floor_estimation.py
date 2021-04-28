import numpy as np
import cv2
import gopro_calib as calib
from copy import deepcopy

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm

def display_3D_Plot(points, shown):
    fig = plt.figure()
    ax = plt.axes(projection='3d')
    x_data = points[0]
    y_data = points[1]
    z_data = points[2]
    scatter = ax.scatter3D(x_data, y_data,z_data, cmap='Greens')
    
    if shown:
        fig.canvas.draw()
        fig.canvas.flush_events()
    else:
        fig.show()
    

    # cv2.line(img,corners[0],corners[1])
criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 2, 0.001)
objp = np.zeros((6*7,3), np.float32)
objp[:,:2] = np.mgrid[0:7,0:6].T.reshape(-1,2)
axis = np.asarray([[3,0,0], [0,3,0], [0,0,-3]]).reshape(-1,3)
corner_np = np.zeros((4,2,1))
print(corner_np)
corner_count = 0
corners = []
img = None

def get_calibration(img):
        # Define the dimensions of checkerboard 
    CHECKERBOARD = (6, 9) 
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
    # prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
    objp = np.zeros((6*9,3), np.float32)
    objp[:,:2] = np.mgrid[0:6,0:9].T.reshape(-1,2)
    axis = np.float32([[3,0,0], [0,3,0], [0,0,-3]]).reshape(-1,3)
    # Arrays to store object points and image points from all the images.
    objpoints = [] # 3d point in real world space
    imgpoints = [] # 2d points in image plane.

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # Find the chess board corners
    ret, corners = cv2.findChessboardCorners( 
                gray, CHECKERBOARD,  
                cv2.CALIB_CB_ADAPTIVE_THRESH  
                + cv2.CALIB_CB_FAST_CHECK + 
                cv2.CALIB_CB_NORMALIZE_IMAGE)
    # If found, add object points, image points (after refining them)
    if ret == True:
        objpoints.append(objp)
        corners2 = cv2.cornerSubPix(gray,corners, (11,11), (-1,-1), criteria)
        imgpoints.append(corners)
    #     # Draw and display the corners
    #     cv2.drawChessboardCorners(img, (6,9), corners2, ret)
    #     cv2.imshow('img', img)
    #     cv2.waitKey(500)
    # cv2.destroyAllWindows()
    ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)

    print("Mtx",mtx)
    print("dist",dist)

    ret, rvecs, tvecs = cv2.solvePnP(objp, corners2, mtx, dist)
    imgpts, jac = cv2.projectPoints(axis, rvecs, tvecs, mtx, dist)

    img = draw(img,corners2,imgpts)
    cv2.imshow('img',img)

    print("CalibRVEC:", rvecs, "CALIBTVEC", tvecs)
    # print(mtx,dist,rvecs,tvecs)
    return ret, mtx, dist, rvecs, tvecs

def draw_normals(img, corners, imgpts):
    # corner = tuple(corners[0].ravel())
    # print(corners[1][1])
    corn = (int(corners[0][0]), int(corners[0][1]))
    # print(imgpts)

    # print(corn)
    # print(imgpts[0].ravel())
    # print(tuple(imgpts[0].ravel()))
    # print(tuple(imgpts[1].ravel()))
    # print(tuple(imgpts[2].ravel()))
    # img = cv2.line(img, corn, tuple(imgpts[0].ravel()), (255,0,0), 5)
    # img = cv2.line(img, corn, tuple(imgpts[1].ravel()), (0,255,0), 5)
    # img = cv2.line(img, corn, tuple(imgpts[2].ravel()), (0,0,255), 5)

    img = cv2.arrowedLine(img, corn, tuple(imgpts[0].ravel()), (255,0,0), 2)
    img = cv2.arrowedLine(img, corn, tuple(imgpts[1].ravel()), (0,255,0), 2)
    img = cv2.arrowedLine(img, corn, tuple(imgpts[2].ravel()), (0,0,255), 2)

    return img

def draw(img, corners, imgpts):
    corner = tuple(corners[0].ravel())
    corner2 = tuple(imgpts[0].ravel())
    corner3 = tuple(imgpts[1].ravel())
    corner4 = tuple(imgpts[2].ravel())
    
    cv2.putText(img,"x",corner2,fontFace=cv2.FONT_HERSHEY_PLAIN,fontScale=2, color=(255,0,0))
    cv2.putText(img,"y",corner3,fontFace=cv2.FONT_HERSHEY_PLAIN,fontScale=2, color=(0,255,0))
    cv2.putText(img,"z",corner4,fontFace=cv2.FONT_HERSHEY_PLAIN,fontScale=2, color=(0,0,255))

    img = cv2.arrowedLine(img, corner, corner2, (255,0,0), 2)
    img = cv2.arrowedLine(img, corner, corner3, (0,255,0), 2)
    img = cv2.arrowedLine(img, corner, corner4, (0,0,255), 2)

    return img

def draw_box(img, corners, imgpts):
    imgpts = np.int32(imgpts).reshape(-1,2)
    # draw ground floor in green
    img = cv2.drawContours(img, [imgpts[:4]],-1,(0,255,0),-3)
    # draw pillars in blue color

    for i,j in zip(range(4),range(4,8)):
        img = cv2.line(img, tuple(imgpts[i]), tuple(imgpts[j]),(255),3)
    # draw top layer in red color
    img = cv2.drawContours(img, [imgpts[4:]],-1,(0,0,255),3)
    return img

def draw_point(img, front_pt, back_pt):
    # print("IMPTS",imgpts)
    # imgpts = np.int32(imgpts).reshape(-1,2)
    # # print("IMPTS",imgpts)
    # impts_orig = tuple(imgpts[0].ravel())
    # # impts_final = tuple(imgpts[1].ravel())
    # # try:
    # impts_final = tuple(point[0].ravel())
    # print(impts_final)
    # except:
    #     impts_final = (point[0],point[1])
    # impts_final = (int(front_pt[0]),int(point[1]))


    img = cv2.circle(img, front_pt, 8,(125,0,125),2,0)
    img = cv2.drawMarker(img, back_pt, color=(255,255,0),markerType=1)
    img = cv2.line(img,front_pt, back_pt, (100,100,0), 2)
    img = cv2.circle(img, front_pt, 8,(255,255,0),2,0)
    return img

def estimate_plane(img, corners, points, calibration_matrix, distortion_matrix):

    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
    objp = np.zeros((6*7,3), np.float32)
    objp[:,:2] = np.mgrid[0:7,0:6].T.reshape(-1,2)
    
    axis = np.array([[3,0,0], [0,3,0], [0,0,-3]],dtype=np.float32).reshape(-1,3)
    
    corners2 = cv2.cornerSubPix(img,corners,(11,11),(-1,-1),criteria)
    # Find the rotation and translation vectors.
    ret,rvecs, tvecs = cv2.solvePnP(objp, corners2, calibration_matrix, distortion_matrix)

    print("CalibRVEC:", rvecs, "CALIBTVEC", tvecs)
    # project 3D points to image plane
    imgpts, jac = cv2.projectPoints(axis, rvecs, tvecs, calibration_matrix, distortion_matrix)

    return imgpts, jac
    
def get_corners(event, x, y, flags, param):
    # grab references to the global variables
    global refPt, cropping, corner_count, corner_np, corners
    # if the left mouse button was clicked, record the starting
    # (x, y) coordinates and indicate that cropping is being
    # performed
    if event == cv2.EVENT_LBUTTONDOWN:
        refPt = [(x, y)]
        cv2.circle(img, (x,y), 1,(0,0,255), 5, 0)
        # corners.append((x,y))
        corners.append((x,y))
        
        corner_np[corner_count][0][0] = x
        corner_np[corner_count][1][0] = y
        corner_count += 1
        # corner_np[0][0][0] = x
        # print(corner_np[0])
        # print((x,y))
        corner_np = corner_np.astype(np.int)
        print("CORNER !!!")
        # print(corner_np)
        
        # print(corners)
        

        getting_corners = True
    # check to see if the left mouse button was released
    # elif event == cv2.EVENT_LBUTTONUP:
    #     # record the ending (x, y) coordinates and indicate that
    #     # the cropping operation is finished
    #     refPt.append((x, y))
    #     cropping = False
    #     # draw a rectangle around the region of interest
    #     # cv2.rectangle(image, refPt[0], refPt[1], (0, 255, 0), 2)
    #     # cv2.circle(img, )

def connect_corners():
    for index, point in enumerate(corners):
        if index == 4:
            print("Last point")
            cv2.line(img, corners[-1], corners[0], (255,0,0))
        if len(corners) > 1 and index+1 < len(corners):
            cv2.line(img, corners[index], corners[index+1], (255,0,0))

def get_room_points(width,length,height=0):
    """
    Returns a matrix for real world points.
    These points start on the bottom left and are assigned as a rectangle in a clockwise direction
       
       (width)
      1------2 
      |      |
      |      | (length)
      0      3

    We may include Height, but this is not included.
    """

    objectPoints = np.array(
        [
            [[0.0],[0.0],[0.0]],
            [[0.0],[float(length)],[0.0]],
            [[float(width)],[float(length)],[0.0]],
            [[float(width)],[0.0],[0.0]],
            # [[5.0],[3.5],[0.0]],
        ]
    )

    return objectPoints


if __name__ == "__main__":
    # img_path = "C:/Users/legom/Pictures/idea.jpeg"
    img_path = "C:/Users/legom/Pictures/checker.png"
    # img_path = "C:/Users/legom/Pictures/Cat_ear.PNG"
    # img_path = "C:/Users/legom/Pictures/testing.jpg"
    img = cv2.imread(img_path)
    # gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)

    cv2.namedWindow("image")
    cv2.setMouseCallback("image", get_corners)
    # ret, mtx, dist, rvecs, tvecs = get_calibration(img)
    # identity = np.identity(4)

    while len(corners) < 4:
        # print(corners)
                # display the image and wait for a keypress
        cv2.imshow("image", img)
        key = cv2.waitKey(1) & 0xFF
        connect_corners()
        if key == ord("c"):
            break

    cv2.destroyAllWindows()
    # Define the dimensions of checkerboard 
    CHECKERBOARD = (6, 9) 
    
    selected_corners = corners
    print("CORNER_NP", corner_np)
    
    #  3D points real world coordinates 
    objectp3d = np.zeros((1, CHECKERBOARD[0]  
                        * CHECKERBOARD[1],  
                        3), np.float32) 

    objectp3d[0, :, :2] = np.mgrid[0:CHECKERBOARD[0], 
                                0:CHECKERBOARD[1]].T.reshape(-1, 2) 

    # object3d = np.asarray((0,0,0), (1,0,0), ())
    prev_img_shape = None

    image = img

    # distCoeffs = np.identity(4)
    axis = np.float32([[3,0,0], [0,3,0], [0,0,-3]]).reshape(-1,3)
    
    print("AXIS", axis)

    objectPoints = get_room_points(3,3)
    mtx = np.array(
        [
            [465.53318908,0,259.21780444],
            [0,451.42964787,218.82569672],
            [0,0,1],
        ]
    )
    # dist = np.array([[ 0.1465351,-0.03129233,-0.00449818,-0.01571948,-0.10592451]])
    dist = np.zeros((5,1))
    # mtx = np.identity(3)
    # dist = np.zeros
    # objp = np.zeros((3*4,3), np.float32)
    # objp[:,:2] = np.mgrid[0:3,0:4].T.reshape(-1,2)
    # print("OBJECT POINTS", objectPoints)
    # print(objectPoints.shape)
    # print()

    retval, rvecs, tvecs = cv2.solvePnP(objectPoints, corner_np.astype(np.float64), calib.GOPRO_HERO3_BLACK_NARROW_MTX, dist)
    print()
    Lcam = calib.GOPRO_HERO3_BLACK_NARROW_MTX.dot(np.hstack((cv2.Rodrigues(rvecs)[0],tvecs)))

    rotation_mat = cv2.Rodrigues(rvecs)

    print("Rotation Vector", rvecs)
    print("Rotation Matrix", rotation_mat)
    # invert_rvecs = np.zeros((3,3))
    print(type(rvecs))
    print(rvecs.shape)
    
    invert_rvecs = np.transpose(rvecs)
    print(invert_rvecs.shape)

    # invert_rvecs = cv2.invert(rvecs, invert_rvecs)
    # invert_tvecs = np.invert(tvecs)
    
    # retval, rvecs, tvecs = cv2.solveP3P(objectPoints, corner_np.astype(np.float64), calib.GOPRO_HERO3_BLACK_NARROW_MTX, dist)

    print("RVEC",rvecs,"\nTVEC",tvecs)
    # print("IRVEC",invert_rvecs,"\nITVEC",invert_tvecs)
    invert_rvecs = np.array([[0],[0],[0]])
    invert_tvecs = np.array([[0],[0],[0]])


    # cv2.invert(rvecs,invert_rvecs)
    # project 3D points to image plane
    imgpts, jac = cv2.projectPoints(axis, rvecs, tvecs, calib.GOPRO_HERO3_BLACK_NARROW_MTX, dist)

    box_pts = np.float32([[0,0,0], [0,3,0], [3,3,0], [3,0,0],
                    [0,0,3],[0,3,3],[3,3,3],[3,0,3] ])
    projected_box, jac = cv2.projectPoints(box_pts, rvecs, tvecs, calib.GOPRO_HERO3_BLACK_NARROW_MTX, dist)
    # print("Jacobian", jac)
    # print("PROJECTED_BOX",projected_box)

    # inverse_box, jac = cv2.projectPoints(box_pts, rvecs, tvecs, calib.GOPRO_HERO3_BLACK_NARROW_MTX, dist)
    # print("INVERSE_PROJECTED_BOX", )
    
    # image = draw_normals(img, corner_np, imgpts)
    image = draw(img,corner_np, imgpts)
    # image = draw_box(image,corner_np,projected_box)
    print(corner_np[:1])
    cv2.imshow('img', image) 
    cv2.waitKey(0) 

    height = 0
    width = 0
    depth = 3
    init = deepcopy(image)

    print(tvecs, rvecs)

    # invert_translate = cv2.invert(tvecs)
    
    # invert_rotate = cv2.invert(rvecs)


    print(mtx)
    # print(cv2.invert(calib.GOPRO_HERO3_BLACK_NARROW_MTX))
    # inv_mtx = cv2.invert(calib.GOPRO_HERO3_BLACK_NARROW_MTX)[1]
    # print(inv_mtx.shape)
    # print(inv_mtx)
    shown = False
    while True:
        key = cv2.waitKey(50) 
        if key == ord('w'):
            height += 0.1
        elif key == ord('s'):
            height -= 0.1
        elif key == ord('a'):
            width -= 0.1
        elif key == ord('d'):

            width += 0.1
        img = cv2.imread(img_path)

        axis = np.float32([[0,0,0], [0,3,0], [3,3,0], [3,0,0],
                    [0,0,3],[0,3,3],[3,3,3],[3,0,3] ])

        imgpts, jac = cv2.projectPoints(axis, rvecs, tvecs, calib.GOPRO_HERO3_BLACK_NARROW_MTX, dist)
        

        # image = draw_box(img, corner_np, imgpts)

        # inv_mtx = np.invert(mtx)
        # print(inv_mtx)
        
        # print(mtx.inv())

        point = np.float32([
            [width,0,height],
            [width,3,height]
            ])
        point_px = (width,height,0)
        print(point_px)




        # point_px = (width,height,3)
        # hom_pt = point_px
        # print("HOM_PT",hom_pt)
        # np.float32([[width,0,height],[width,3,height]])
        # print()
        # print(hom_pt[1][1])

        # hom_pt = np.float32([[hom_pt[0],hom_pt[1],0],[hom_pt[0],hom_pt[1],3]])
        # # point = np.float32([[hom_pt[0],hom_pt[1],0],[hom_pt[0],hom_pt[1],0]])
        # # print(hom_pt)
        # point = np.float32([[hom_pt[0][0],hom_pt[1][1],3]])
        # # print(point)
        # # point = ()
        # # print(width, height)
        X = np.linalg.inv(np.hstack((Lcam[:,0:2],np.array([[-1*width],[-1*height],[-1]])))).dot((-depth*Lcam[:,2]-Lcam[:,3]))
        print(X)


        # front_face_pts, jac = cv2.projectPoints(point, rvecs, tvecs, calib.GOPRO_HERO3_BLACK_NARROW_MTX, dist)
        front_and_back, jac = cv2.projectPoints(point, rvecs, tvecs, calib.GOPRO_HERO3_BLACK_NARROW_MTX, dist)
        print(front_and_back)
        # imgpts, jac = cv2.projectPoints(X, rvecs, tvecs, calib.GOPRO_HERO3_BLACK_NARROW_MTX, dist)
        # imgpts, jac = cv2.projectPoints(axis, rvecs, tvecs, calib.GOPRO_HERO3_BLACK_NARROW_MTX, dist)
        # print(imgpts)
        # point
        # print(imgpts)
        # display_3D_Plot(X, shown)
        
        # show once then update
        if not shown:
            shown = True
        # print("FRONT/BACK",front_and_back)
        front_point = (front_and_back[0][0][0],front_and_back[0][0][1])
        print(front_and_back[0])
        back_point = (front_and_back[1][0][0],front_and_back[1][0][1])

        cv2.circle(image,front_point,5,color=(255,255,255))
        image = draw_point(image, front_point, back_point )
        cv2.imshow('img', image) 


