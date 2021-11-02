import numpy as np
import cv2
import gopro_calib as calib
from copy import deepcopy


# import matplotlib.pyplot as plt
# from mpl_toolkits.mplot3d import Axes3D
# from matplotlib import cm

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# https://stackoverflow.com/questions/12299870/computing-x-y-coordinate-3d-from-image-point
def plot_points(event,x,y,flags,params):
    global mouseX,mouseY
    # print(params)
    mapped_points = params
    p_list = []
    x_list = []
    y_list = []
    z_list = []
    if event == cv2.EVENT_LBUTTONDBLCLK:
        if (x,y) in mapped_points.keys():
            p_list = mapped_points[(x,y)]
            
            
            for p in p_list:
                print(p)
                x_list.append(p[0])
                y_list.append(p[2])
                z_list.append(p[1])



            fig = plt.figure(figsize=(4,4))
            ax = fig.add_subplot(111, projection='3d')
            ax.scatter(xs = x_list, ys = y_list, zs = z_list)

            ax.set_title("3D Point position in room")

            ax.set_xlabel("X (Width")
            ax.set_ylabel("Y (Height)")
            ax.set_zlabel("Z (Depth")

            plt.show()


def map_2d_to_3d( rvec, tvec, camera_matrix, distortion_coefficients, room_dimensions = (1000,1000,1000),):
    '''
    Maps the entire image to depth points with defined room
    '''
    print("Mapping points...")
    # Room dimensions is 1m (width) x 1m (height) x 1m(depth)
    w = room_dimensions[0]
    h = room_dimensions[1]
    d = room_dimensions[2]

    # axis = np.float32([
    #     [0,0,0], # center
    #     [0,3000,0],
    #     [3000,3000,0],
    #     [3000,0,0],
    #                 [0,0,3000],[0,3000,3000],[3000,3000,3000],[3000,0,3000] ])
    img = cv2.imread(img_path)
    mapped = {}
    for i in range(0,w,25):
        print(i)
        for j in range(0,1000,25):
            for k in range(0,d,25):
                
                point = np.float32([[i, k, j]])
                
                mapped_point, jac = cv2.projectPoints(point, rvecs, tvecs, calib.GOPRO_HERO3_BLACK_NARROW_MTX, dist)
                mapped_point = (int(mapped_point[0][0][0]),int(mapped_point[0][0][1]))

                # cv2.putText(img,str(mapped_point),mapped_point,fontFace=cv2.FONT_HERSHEY_PLAIN,fontScale=2, color=(255,0,0))
                
                cv2.imshow('img', img) 
                cv2.waitKey(1) 
                
                # print(mapped_point)
                if mapped_point not in mapped.keys():
                    # cv2.circle(img,mapped_point,1,color=(255,0,255))
                    mapped[mapped_point] = list()
                    mapped[mapped_point].append((i,k,j))
                else:
                    cv2.circle(img,mapped_point,2,color=(0,0,0), thickness=-1)
                    mapped[mapped_point].append((i,k,j))
                    
                
    print("Finished mapping points")
    return mapped

def get_3d_point(pixel, camera_matrix, rotation_matrix, tvec, height=1500):
    uv_point = np.array([pixel[0], pixel[1], 1])
    left_side = np.linalg.inv(rotation_matrix * np.identity(3) ) * np.linalg.inv(camera_matrix * np.identity(3) ) * uv_point

    # print("Lside:", left_side)
    right_side = np.linalg.inv(rotation_matrix * np.identity(3)) * tvec
    # print("Rside:", right_side)

    s = height + right_side[2][2]/left_side[2][2]

    return np.linalg.inv(rotation_matrix* np.identity(3)) * (s*np.linalg.inv(camera_matrix* np.identity(3)) * uv_point - tvec)

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
    cv2.putText(img,"y",corner4,fontFace=cv2.FONT_HERSHEY_PLAIN,fontScale=2, color=(0,255,0))
    cv2.putText(img,"z",corner3,fontFace=cv2.FONT_HERSHEY_PLAIN,fontScale=2, color=(0,0,255))

    img = cv2.arrowedLine(img, corner, corner2, (255,0,0), 2)
    img = cv2.arrowedLine(img, corner, corner4, (0,255,0), 2)
    img = cv2.arrowedLine(img, corner, corner3, (0,0,255), 2)

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
    # img_path = "C:/Users/legom/Pictures/checker.png"
    # img_path = "C:/Users/legom/Pictures/Cat_ear.PNG"
    img_path = "C:/Users/legom/Pictures/testing.jpg"
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
    axis = np.float32([[3000,0,0], [0,3000,0], [0,0,1700]]).reshape(-1,3)
    # axis = np.float32([[3000,0,0], [0,3000,0], [0,0,3000]])
    
    print("AXIS", axis)

    objectPoints = get_room_points(3000,3000)
    mtx = np.array(
        [
            [465.53318908,0,259.21780444],
            [0,451.42964787,218.82569672],
            [0,0,1],
        ]
    )
    # dist = np.array([[ 0.1465351,-0.03129233,-0.00449818,-0.01571948,-0.10592451]])
    dist = np.zeros((5,1))

    retval, rvecs, tvecs = cv2.solvePnP(objectPoints, corner_np.astype(np.float64), calib.GOPRO_HERO3_BLACK_NARROW_MTX, dist)
    print("RVEC",rvecs,"\nTVEC",tvecs)

    # rotation_mat = cv2.Rodrigues(rvecs)

    # project 3D points to image plane
    imgpts, jac = cv2.projectPoints(axis, rvecs, tvecs, calib.GOPRO_HERO3_BLACK_NARROW_MTX, dist)

    box_pts = np.float32([[0,0,0], [0,3,0], [3,3,0], [3,0,0],
                    [0,0,3],[0,3,3],[3,3,3],[3,0,3]])

    projected_box, jac = cv2.projectPoints(box_pts, rvecs, tvecs, calib.GOPRO_HERO3_BLACK_NARROW_MTX, dist)
    image = draw(img,corner_np, imgpts)
    image = draw_box(image,corner_np,projected_box)
    cv2.imshow('img', image) 
    cv2.waitKey(0) 

    height = 0
    width = 0
    depth = 0
    init = deepcopy(image)

    # print(tvecs, rvecs)
    # rotation_matrx = cv2.Rodrigues(rvecs)

    mapped = map_2d_to_3d(rvecs,tvecs,calib.GOPRO_HERO3_BLACK_NARROW_MTX, dist, room_dimensions=(3000,3000,1000))
    cv2.setMouseCallback('img', plot_points, param=mapped)
    # plot_points(params=mapped)

    Lcam = calib.GOPRO_HERO3_BLACK_NARROW_MTX.dot(np.hstack((cv2.Rodrigues(rvecs)[0],tvecs)))
    # print(Lcam)
    shown = False
    img = cv2.imread(img_path)
    while True:
        key = cv2.waitKey(50) 
        if key == ord('w'):
            height += 10
        elif key == ord('s'):
            height -= 10
        elif key == ord('a'):
            width -= 10
        elif key == ord('d'):
            width += 10
        elif key == ord('x'):
            depth += 10
        elif key == ord('z'):
            depth -= 10
        

        axis = np.float32([[0,0,0], [0,3000,0], [3000,3000,0], [3000,0,0],
                    [0,0,3000],[0,3000,3000],[3000,3000,3000],[3000,0,3000] ])

        imgpts, jac = cv2.projectPoints(axis, rvecs, tvecs, calib.GOPRO_HERO3_BLACK_NARROW_MTX, dist)
        init = deepcopy(image)

        # mapped = get_3d_point((500,500), calib.GOPRO_HERO3_BLACK_NARROW_MTX, rvecs, tvecs)
        floater_point = np.float32([[width, depth, height]])
        floater, jac = cv2.projectPoints(floater_point, rvecs, tvecs, calib.GOPRO_HERO3_BLACK_NARROW_MTX, dist)
        # print("MAPPED", mapped, "\n| floater", floater, "\nFP: ", floater_point)
        # print(width, height, depth)
        # mapped = map_2d_to_3d(rvecs, tvecs, calib.GOPRO_HERO3_BLACK_NARROW_MTX, dist, room_dimensions=(4000,1000,3000))
        # print(width, height)
        # print(mapped)
        # Lcam=mtx.dot(np.hstack((cv2.Rodrigues(rvecs[0])[0],tvecs[0])))


        # cv::Mat uvPoint = (cv::Mat_<double>(3,1) << 363, 222, 1); // u = 363, v = 222, got this point using mouse callback

        # cv::Mat leftSideMat  = rotationMatrix.inv() * cameraMatrix.inv() * uvPoint;
        # cv::Mat rightSideMat = rotationMatrix.inv() * tvec;

        # double s = (285 + rightSideMat.at<double>(2,0))/leftSideMat.at<double>(2,0)); 
        # //285 represents the height Zconst

        # std::cout << "P = " << rotationMatrix.inv() * (s * cameraMatrix.inv() * uvPoint - tvec) << std::endl;
        # print(imgpts)
        # image = draw_box(img, corner_np, imgpts)

        # inv_mtx = np.invert(mtx)
        # print(inv_mtx)
        
        # print(mtx.inv())

        # point = np.float32([
        #     [width,0,height],
        #     [width,3000,height]
        #     ])
        # point_px = (width,height,0)
        # # print(point_px)

        # uv_point = np.float32([width, height, 1]) #Z is constant
        # print()

        # left_side_matrix = np.dot(
        #                         np.dot(np.linalg.inv(rotation_matrx[0]), np.linalg.inv(calib.GOPRO_HERO3_BLACK_NARROW_MTX)),
        #                         uv_point)
        
        # right_side_matrix = np.dot(np.linalg.inv(rotation_matrx[0]), tvecs)
        # print("RightSideMatrix", right_side_matrix)

        # s_matrix = 1750 + right_side_matrix[2]/ left_side_matrix[2]
        # # s_matrix = 
        # print("S", s_matrix)

        # print("Point = ", np.dot(np.linalg.inv(rotation_matrx[0]), (np.dot(np.dot(s_matrix, calib.GOPRO_HERO3_BLACK_NARROW_MTX), (uv_point-tvecs) ))))

        # front_point_px = (width,height,3)
        # back_point_px = (width,height,3)
        # hom_pt = point_px
        # print("HOM_PT",hom_pt)
        # np.float32([[width,0,height],[width,3,height]])
        # print()
        # print(hom_pt[1][1])

        # hom_pt = np.float32([[front_point_px[0],front_point_px[1],0],[front_point_px[0],front_point_px[1],3]])
        # hom_pt = np.float32([[front_point_px[0],front_point_px[1],0],[front_point_px[0],front_point_px[1],3]])
        # # point = np.float32([[hom_pt[0],hom_pt[1],0],[hom_pt[0],hom_pt[1],0]])
        # # print(hom_pt)
        
        back_point = np.float32([[width,height,0]])
        # # print(point)
        # # point = ()
        # # print(width, height)
        # px=100
        # py=100
        # Z=0
        # X=np.linalg.inv(np.hstack((Lcam[:,0:2],np.array([[-1*px],[-1*py],[-1]])))).dot((-Z*Lcam[:,2]-Lcam[:,3]))
        # print(X)
        X = np.linalg.inv(np.hstack((Lcam[:,0:2],np.array([[-1*width],[-1*height],[-1]])))).dot((-depth*Lcam[:,2]-Lcam[:,3]))
        # print("LOCATION", X)


        # front_face_pts, jac = cv2.projectPoints(point, rvecs, tvecs, calib.GOPRO_HERO3_BLACK_NARROW_MTX, dist)
        front_point = np.float32([[width,0,height]])
        front, jac = cv2.projectPoints(front_point, rvecs, tvecs, calib.GOPRO_HERO3_BLACK_NARROW_MTX, dist)

        back_point = np.float32([[width,3000,height]])
        back, jac = cv2.projectPoints(back_point, rvecs, tvecs, calib.GOPRO_HERO3_BLACK_NARROW_MTX, dist)

        floater_point = np.float32([[width, depth, height]])
        floater, jac = cv2.projectPoints(floater_point, rvecs, tvecs, calib.GOPRO_HERO3_BLACK_NARROW_MTX, dist)
        # print(front_and_back)
        # imgpts, jac = cv2.projectPoints(X, rvecs, tvecs, calib.GOPRO_HERO3_BLACK_NARROW_MTX, dist)
        # imgpts, jac = cv2.projectPoints(axis, rvecs, tvecs, calib.GOPRO_HERO3_BLACK_NARROW_MTX, dist)
        # print(imgpts)
        # point
        # print(imgpts)
        # display_3D_Plot(X, shown)
        # print()
        # show once then update
        if not shown:
            shown = True
        # print("FRONT/BACK",front_and_back)
        front_point = (front[0][0][0],front[0][0][1])
        back_point = (back[0][0][0],back[0][0][1])
        floater_point = (floater[0][0][0],floater[0][0][1])
        # print(front_point)
        # print(front_and_back[1][0][1])
        

        # cv2.circle(img,front_point,5,color=(255,255,255))
        # cv2.circle(img,back_point,10,color=(0,255,255))
        
        # cv2.circle(img, (100,100),5,color=(255,255,255))
        img = draw_point(init, front_point, back_point)
        # cv2.circle(img,floater_point,4,color=(0,0,255), thickness=4)

        test = (X)
        # cv2.putText()
        # cv2.imshow('img', img) 
        cv2.waitKey(0) 


