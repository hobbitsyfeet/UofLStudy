"""
This file contains a class to locate and assign coordinates onto a stitched frame
This class will keep track of all points and manage them, for each frame that's
passed in with a point, we will extract the GPS coordinate from it.
"""
from video_process.image import StitchImage
import tkinter
from tkinter import ttk, filedialog
from PIL import Image, ImageTk
import cv2
import pandas as pd
class Locate():
    def __init__(self, parent, video_source):
        """
        The parent window is the program that originally calls it.
        """
        self.window = parent
        # self.data = data
        self.coordinates = []
        self.assigned = []
        self.data = None
        self.video_source = video_source
        self.vid_length = None
        self.img_processor = StitchImage()
        self.process_image = None

        self.step = 100
        self.stitched_frames=10
        self.delay = 15
        
    def update(self):
        self.id_coordinates.config(text=self.get_data_by_id(int(self.tkvar.get())))
            # print(self.assigned[0][0])
        display = self.process_image.copy()
        # gray = cv2.cvtColor(display, cv2.COLOR_BGR2GRAY)
        current_coord = self.get_data_by_id(int(self.tkvar.get()))
        for points in range(len(self.assigned)):
            colour = (255,0,0)
            if current_coord == self.assigned[points][1]:
                colour = (0,255,0)

                
            cv2.circle(display, tuple(self.assigned[points][0]), 10, colour, -1, cv2.LINE_AA)
        self.photo = ImageTk.PhotoImage(image=Image.fromarray(display))
        self.canvas.create_image(0,0,image=self.photo, anchor="nw")

        self.window.after(self.delay, self.update)

    def add_coordinate(self, lon, lat):
        """
        We add coordinates based on longitude , latitude
        """

    def format_coordinate(self, type):
        """
        converts format ?Needed?
        """
        pass

    def load_coords(self, ):
        """
        loads_coords from csv.
        """
        print("loading file")
        #if there is no passed variable, open dialog to select
        file_types = [('Microsoft Excel', '*.csv'), ('All files', '*')]
        dlg = filedialog.Open(filetypes=file_types)
        file = dlg.show()
        print(file)

        #if file is selected, read the data
        if file != '':
            data = pd.read_csv(file)
            self.coordinates = data
            print(data)
            return data

    def assign_coord(self, event):
        """
        Uses the ID of the coordinates to assign them on the image
        This function should be called by clicking.
        """

        if len(self.assigned) == 0:
            self.assigned.append( ( (event.x, event.y), (self.get_data_by_id(int(self.tkvar.get()))) ) )

        else:
            found = False
            current_coord = self.get_data_by_id(int(self.tkvar.get()))
            for points in range(len(self.assigned)):
                
                if current_coord == self.assigned[points][1]:
                    found = True
                    self.assigned[points] = ( ((event.x, event.y), current_coord) )
                    break
            if not found:
                self.assigned.append( ( (event.x, event.y), (self.get_data_by_id(int(self.tkvar.get()))) ) )
    
        return event.x, event.y
    
    def remove_assigned_coord(self):
        """
        removes the location of an assigned coordinate
        """
        current_coord = self.get_data_by_id(int(self.tkvar.get()))
        for points in range(len(self.assigned)):
            if current_coord == self.assigned[points][1]:
                self.assigned.pop(points)


    def start(self, finish_frame):
        stitched_number = 0
        cap = cv2.VideoCapture(self.video_source)
        self.vid_length = cap.get(cv2.CAP_PROP_FRAME_COUNT)
        finish_frame = self.vid_length/3

        for num_stitch in range(1, int(finish_frame), int(self.step*self.stitched_frames)):
            if num_stitch + self.step*self.stitched_frames - finish_frame < 0:
        #         print()

                scan = self.stitch_and_reference(self.video_source, num_stitch)
        #         print("Finding reference...")
        #         for frames in range(num_stitch):
        #             ret, frame = cap.read()
        #             # print(frames)
        #             if ret:
        #                 points = self.reference(frame, scan)
        #                 self.coordinates.append(points)

        #         print("Number of coordinates: "+str(len(self.coordinates)))
        #         # print(num_stitch)
        #         stitched_number +=1
        #         cv2.imwrite("./output/stitched/stitched"+ str(stitched_number) +".jpg", scan)

        
        h,w = scan.shape[:2]
        self.process_image = scan
        self.data = self.load_coords()

        # option_panel=tkinter.Frame(self.window,width=200, height=200)
        # option_panel.pack(side=tkinter.LEFT)

        self.setup_dropdown(self.window, self.data)
        #create a frame inside the window which will contain the canvas
        frame=tkinter.Frame(self.window,width=w,height=h)
        frame.pack(side=tkinter.LEFT)

        
        #Create a canvas, the area where the image is shown. Scroll region is the size of the image
        self.canvas=tkinter.Canvas(frame,width=w,height=h, scrollregion=(0,0,w,h),cursor="crosshair")

        #create the structual scrollbars
        hbar=tkinter.Scrollbar(frame,orient=tkinter.HORIZONTAL)
        hbar.pack(side=tkinter.BOTTOM,fill=tkinter.X)
        hbar.config(command=self.canvas.xview)
        vbar=tkinter.Scrollbar(frame,orient=tkinter.VERTICAL)
        vbar.pack(side=tkinter.RIGHT,fill=tkinter.Y)
        vbar.config(command=self.canvas.yview)

        #link the scrollregion to the structural scrollbars
        self.canvas.config(xscrollcommand=hbar.set, yscrollcommand=vbar.set)
        self.canvas.pack(side=tkinter.LEFT, expand=True,fill=tkinter.BOTH)
        
        #set the image inside of the region
        self.photo = ImageTk.PhotoImage(image=Image.fromarray(self.process_image))
        #0,0 is the image location we anchor, anchor is how. If not anchored to nw, it sets the center of the image to top left corner 
        self.canvas.create_image(0,0,image=self.photo, anchor="nw")
        
        self.canvas.bind("<Button-1>", self.assign_coord)

        
        self.update()
        self.window.mainloop()

    def setup_dropdown(self, window, data):
        print("Setting up dropdown")
        # Create a Tkinter variable
        self.tkvar = tkinter.StringVar(window)
        all_id = self.data.loc[:,'ID'].tolist()
        
        #duplicate first index
        all_id.insert(0, all_id[0])
        self.tkvar.set(all_id[0])

        #assign all id's to the option menu
        popup_menu = ttk.OptionMenu(window, self.tkvar, *all_id)
        popup_lable = tkinter.Label(window, text="GPS Coordinates")
        self.id_coordinates = tkinter.Label(window, text=self.get_data_by_id(int(self.tkvar.get())))
        remove = tkinter.Button(window, text="Remove", command=self.remove_assigned_coord)
        #set the option menu
        popup_lable.pack(side=tkinter.TOP)
        popup_menu.pack(side=tkinter.TOP)
        self.id_coordinates.pack(side=tkinter.TOP)
        remove.pack(side=tkinter.TOP)
        

    def get_data_by_id(self, id):
        id_type = self.data.ID.dtype

        #get the row which the id matches
        id_loc = self.data.loc[self.data['ID'] == id]
        #get the coordinates of that id
        x_coord = id_loc.iloc[0]['X']
        y_coord = id_loc.iloc[0]['Y']
        return x_coord, y_coord


    def show_reference(self, points, ref_image):
        for points in range(len(points)):
            copy = ref_image
            cover_img = cv2.polylines(copy, points, True, (0, 0, 255),5, cv2.LINE_AA)
            cv2.imshow("show", cover_img)

    def reference(self, query_frame, stitched_img):
        coordinates = self.img_processor.find_reference(query_frame, stitched_img)
        return coordinates

    def stitch_and_reference(self, video_source, start_frame, skip_step=100, total_frames=10):
        """
        stitches the video together
        """
        print("Stitching image")

        frames = self.img_processor.collect_frames(video_source, start_frame, skip_step, total_frames)

        status, scan = self.img_processor.stitch(frames)
        print("Stitching Complete.")
        return scan

if __name__ == "__main__":
    
        # displayed in a separate, top-level window. Such windows usually have title bars, borders, and other “window decorations”
        locate_window = tkinter.Toplevel()
        locate_window.title("Stitch and Locate")

        locate_tool = Locate(locate_window, "./videos/GH010018.mp4")
        # cv2.imshow("FRAME", frame)
        #first is the frame itself the other is the frame number
        locate_tool.start(locate_tool.vid_length)