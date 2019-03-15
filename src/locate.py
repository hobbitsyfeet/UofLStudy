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

        self.window_width = 1080
        self.window_height = 720
        # assigned records where the GPS data is linked to the pixel data
        self.assigned = []
        # referenced records where a particular frame find's its place on the working image
        self.referenced = []
        # data is the GPS coordinate data
        self.data = None
        # video source is the video which the interface works on
        self.video_source = video_source
        self.vid_length = None

        #image_processor is the image processing layer of this interface.
        self.img_processor = StitchImage()

        #process image is the image which is to be worked on. This is the largest stitched image.
        self.process_image = None

        #step is how many frames exists between stitched frames
        self.step = 100
        #stitched frames is the total number of frames per stitched image
        self.stitched_frames=10
        self.view_frame = 0

        #delay is the milisend delay between updating UI
        self.delay = 15
        
    def start(self, finish_frame):
        """
        You might think I know... but its just a collection of code to start things...
        """
        #counter for each stitched set
        stitched_number = 1


        cap = cv2.VideoCapture(self.video_source)
        self.vid_length = cap.get(cv2.CAP_PROP_FRAME_COUNT)
        
        #stop at the end of the video
        finish_frame = self.vid_length/2

        #iterate in large steps where each step is the range of frames stitched. Eg. stitch(frames[100,200,300]) each iteration is 300
        for num_stitch in range(0, int(finish_frame), int(self.step*self.stitched_frames)):
            # print(int(self.step*self.stitched_frames))
            # print(num_stitch)
            #if limit is not passed
            if num_stitch + self.step*self.stitched_frames - finish_frame < 0:
                #create a stitched image
                scan = self.stitch_from_video(self.video_source, num_stitch)
                #reference each frame in the video that exists in the range stitched Eg. every frame in range 100-300
                print("Finding reference...")

                for frames in range(int(self.step*self.stitched_frames)):
                    #read each frame and record their referenced locations. These are the corners of the frame
                    ret, frame = cap.read()
                    if ret:
                        if frames % 10 == 0:
                            print(str(frames) + "/" + str(self.step*self.stitched_frames*stitched_number))

                        try:
                            points = self.reference(frame, scan)
                            self.referenced.append(points)
                            # top_left =  points[0][0][0]
                            # top_right = points[0][1][0]
                            # bottom_right = points[0][2][0]
                            # bottom_left = points[0][3][0]
                            # self.referenced.append((frames,top_left, top_right,bottom_right,bottom_left))
                        except:
                            print("Could not reference frame" + str(frames))

                print("Number of coordinates: "+str(len(self.referenced)))
                stitched_number +=1
                cv2.imwrite("./output/stitched/stitched"+ str(stitched_number) +".jpg", scan)
                # reference_data = pd.DataFrame(self.referenced, columns=['frame','Top_Left', 'Top_Right'
                #                                                         ,'Bottom_Right', 'Bottom_Left'])
                # reference_data.to_csv("./output/csv/" + "Reference" + ".csv")

        self.process_image = scan
        self.data = self.load_coords()

        self.setup_dropdown(self.window, self.data)
        
        self.setup_frame_bar()
        #create a frame inside the window which will contain the canvas

        frame=tkinter.Frame(self.window,width=self.window_width,height=self.window_height)
        frame.pack(side=tkinter.LEFT)

        
        # #Create a canvas, the area where the image is shown. Scroll region is the size of the image
        # self.canvas=tkinter.Canvas(frame,width=w,height=h, scrollregion=(0,0,w,h),cursor="crosshair")

        # #create the structual scrollbars
        # hbar=tkinter.Scrollbar(frame,orient=tkinter.HORIZONTAL)
        # hbar.pack(side=tkinter.BOTTOM,fill=tkinter.X)
        # hbar.config(command=self.canvas.xview)
        # vbar=tkinter.Scrollbar(frame,orient=tkinter.VERTICAL)
        # vbar.pack(side=tkinter.RIGHT,fill=tkinter.Y)
        # vbar.config(command=self.canvas.yview)

        # #link the scrollregion to the structural scrollbars
        # self.canvas.config(xscrollcommand=hbar.set, yscrollcommand=vbar.set)

        self.canvas=tkinter.Canvas(frame,width=self.window_width,height=self.window_height,cursor="crosshair")

        self.canvas.pack(side=tkinter.LEFT, expand=True,fill=tkinter.BOTH)
        
        #set the image inside of the region
        resized = cv2.resize(self.process_image,(self.window_width, self.window_height),cv2.INTER_CUBIC)
        self.photo = ImageTk.PhotoImage(image=Image.fromarray(resized))
        #0,0 is the image location we anchor, anchor is how. If not anchored to nw, it sets the center of the image to top left corner 
        self.canvas.create_image(0,0,image=self.photo, anchor="nw")
        
        self.canvas.bind("<Button-1>", self.assign_coord)
        
        self.update()
        self.window.mainloop()

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
        try:
            cv2.polylines(display,self.referenced[self.view_frame], True, (0, 0, 255),5, cv2.LINE_AA)
        except:
            print("no references exist for that frame")

        

        resized = cv2.resize(display,(self.window_width, self.window_height),cv2.INTER_CUBIC)
        self.photo = ImageTk.PhotoImage(image=Image.fromarray(resized))
        self.canvas.create_image(0,0,image=self.photo, anchor="nw")

        self.window.after(self.delay, self.update)

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
        h,w = self.process_image.shape[:2]
        ratio_x = w / self.window_width
        ratio_y = h / self.window_height

        #calculate the position to the ratio
        event.x = round(event.x * ratio_x)
        event.y = round(event.y * ratio_y)

        
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
                break

    def convert_referenced(self, point):
        top_left =  point[0][0][0]
        top_right = point[0][1][0]
        bottom_right = point[0][2][0]
        bottom_left = point[0][3][0]
        return [top_left,top_right,bottom_right,bottom_left]

    def setup_dropdown(self, window, data):
        """
        This dropdown is what maps the data to the user interface to select
        GPS coordinate ID's and assigns the coordinates to pixel locations
        """
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
        
    def setup_frame_bar(self):
        self.frame_bar = ttk.Scale(self.window,from_=0, to=self.vid_length - 1, command=self.set_frame)
        self.frame_bar.config(length=self.window_width)
        self.frame_bar.pack(side=tkinter.BOTTOM)

    def set_frame(self, value):
        self.view_frame = int(float(value))

    def get_data_by_id(self, id):
        id_type = self.data.ID.dtype

        #get the row which the id matches
        id_loc = self.data.loc[self.data['ID'] == id]
        #get the coordinates of that id
        x_coord = id_loc.iloc[0]['X']
        y_coord = id_loc.iloc[0]['Y']
        return x_coord, y_coord
    
    def map_referenced(self):
        """
        This function will map the given points through the reference onto
        the stitched frame
        """
        pass

    def show_reference(self, points, ref_image):
        """
        Takes points and finds reference onto the frame
        """
        for points in range(len(points)):
            copy = ref_image
            cover_img = cv2.polylines(copy, points, True, (0, 0, 255),5, cv2.LINE_AA)
            cv2.imshow("show", cover_img)

    def reference(self, query_frame, stitched_img):
        """
        This takes a query frame and a larger-stitched frame to find where it exists.
        """
        coordinates = self.img_processor.find_reference(query_frame, stitched_img)
        return coordinates

    def stitch_from_video(self, video_source, start_frame, skip_step=100, total_frames=10):
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

        locate_tool = Locate(locate_window, "./videos/GH010018_Trim_Trim.mp4")
        # cv2.imshow("FRAME", frame)
        #first is the frame itself the other is the frame number
        locate_tool.start(locate_tool.vid_length)