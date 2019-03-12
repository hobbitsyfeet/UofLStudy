"""
This file contains a class to locate and assign coordinates onto a stitched frame
This class will keep track of all points and manage them, for each frame that's
passed in with a point, we will extract the GPS coordinate from it.
"""
from video_process.image import StitchImage
import tkinter
from PIL import Image, ImageTk
import cv2
class Locate():
    def __init__(self, parent, video_source):
        """
        The parent window is the program that originally calls it. 
        """
        coordinates = []
        self.video_source = video_source
        
    def add_coordinate(self, lon, lat):
        """
        We add coordinates based on longitude , latitude
        """
        pass

    def format_coordinate(self, type):
        """
        converts format ?Needed?
        """
        pass

    def load_coords(self, file):
        """
        loads_coords from csv
        """
        pass

    def assign_coord(self, id):
        """
        Uses the ID of the coordinates to assign them on the image
        This function should be called by clicking 
        """
        pass
    def remove_assigned_coord(self, id):
        """
        removes the location of an assigned coordinate
        """
        pass

    def start(self, current_frame, current_frame_number):
        scan = self.stitch_and_reference(self.video_source, current_frame, current_frame_number)
        h,w = scan.shape[:2]

        # displayed in a separate, top-level window. Such windows usually have title bars, borders, and other “window decorations”
        locate_window = tkinter.Toplevel()
        locate_window.title("Stitch and Locate")

        #create a frame inside the window which will contain the canvas
        frame=tkinter.Frame(locate_window,width=w,height=h)
        frame.pack(side=tkinter.LEFT)

        #Create a canvas, the area where the image is shown. Scroll region is the size of the image
        canvas=tkinter.Canvas(frame,width=w,height=h, scrollregion=(0,0,w,h),cursor="crosshair")

        #create the structual scrollbars
        hbar=tkinter.Scrollbar(frame,orient=tkinter.HORIZONTAL)
        hbar.pack(side=tkinter.BOTTOM,fill=tkinter.X)
        hbar.config(command=canvas.xview)
        vbar=tkinter.Scrollbar(frame,orient=tkinter.VERTICAL)
        vbar.pack(side=tkinter.RIGHT,fill=tkinter.Y)
        vbar.config(command=canvas.yview)

        #link the scrollregion to the structural scrollbars
        canvas.config(xscrollcommand=hbar.set, yscrollcommand=vbar.set)
        canvas.pack(side=tkinter.LEFT, expand=True,fill=tkinter.BOTH)
        
        #set the image inside of the region
        photo = ImageTk.PhotoImage(image=Image.fromarray(scan))
        canvas.create_image(0,0,image=photo,anchor="nw")
        
        canvas.bind(self.assign_coord)
        locate_window.mainloop()

    
    def stitch_and_reference(self, video_source, query_frame, start_frame, skip_step=100, total_frames=10 ):
        """
        stitches the video together
        """
        print("Stitching image")
        img_process = StitchImage()

        frames = img_process.collect_frames(video_source, start_frame, skip_step, total_frames)

        status, scan = img_process.stitch(frames)
        
        print("Finding reference")

        coordinates = img_process.find_reference(query_frame, scan)

        cover_img = cv2.polylines(scan, coordinates, True, (0, 0, 255), 5, cv2.LINE_AA)
        cv2.imwrite("./output/scan.jpg", cover_img)
        return scan

