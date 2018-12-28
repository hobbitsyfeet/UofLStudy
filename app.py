# coding:utf-8
from video import VideoCapture
import time
import cv2
import tkinter
from tkinter import ttk
import tkinter.filedialog as fileDialog
#from tkinter import ttk.Label, ttk.Button
import PIL.Image, PIL.ImageTk
import math

class App:
    def __init__(self, window, window_title):
        self.window = window
        self.window.title(window_title)


        self.border = 10
        self.number_of_trackers = 5


        self.working_number = 1

        self.play_state = False



        self.menu = tkinter.Menu(window)
        window.config(menu= self.menu)

        self.file_menu = tkinter.Menu(self.menu, tearoff = 0)
        self.menu.add_cascade(label = "File", menu = self.file_menu)

        self.file_menu.add_command(label="New", command=self.donothing)
        self.file_menu.add_command(label="Open", command=self.load_file)
        self.file_menu.add_command(label="Save", command=self.donothing)
        self.file_menu.add_command(label="Save as...", command=self.donothing)
        self.file_menu.add_command(label="Close", command=self.donothing)

        self.edit_menu = tkinter.Menu(self.menu, tearoff = 0)
        self.menu.add_cascade(label = "Edit", menu = self.edit_menu)



        #set min window size to the videocapture size
        self.load_file()
        self.vid.TRACK_ALL = self.number_of_trackers+1
        #window.minsize(int(self.vid.width* 2),int(self.vid.height))

        #self.nudge_left_btn = ttk.Button(window, text = "<-" ,command = self.previous_frame )

        # After it is called once, the update method will be automatically called every delay milliseconds
        self.delay = 20
        #loads file and sets up canvases from the new file

        self.window.mainloop()

    def setup_canvas(self):
        # Create a canvas that can fit the above video source size, and inside the canvas change to crosshair
        canvas = tkinter.Canvas(self.window, width = self.window_width, height = self.window_height , cursor = "crosshair")
        canvas.bind("<Button-1>", self.callback1)
        canvas.grid(column = 0, columnspan = 6,row=1,ipady = 1)
        #self.vid.resize_video(self.window_width/2,self.window_height)
        return canvas

    def setup_canvas_focused(self):
        canvas_focused = tkinter.Canvas(self.window, width = self.window_width, height = self.window_height, cursor = "crosshair")
        canvas_focused.bind("<Button-1>", self.callback1)
        canvas_focused.grid(column = 7,columnspan = 6,row=1)
        #self.vid.resize_video(self.window_width,self.window_height)
        return canvas_focused

    def setup_video_functions(self):
        self.frame_bar_label = ttk.Label( text = "frame:", font = ('Helvetica', '16') )
        self.frame_bar_label.grid(column = 6,row=3,columnspan = 2, sticky = "NW")

        #frame_bar is a scale to the length of the video, controlling which frame the video shows
        self.frame_bar  = ttk.Scale(from_=0, to = self.vid.length - 4,command = self.set_frame_pos)
        self.frame_bar.config(length = self.vid.width)
        self.frame_bar.grid(column = 2,row=2,columnspan = 9, sticky = "SW")

        self.nudge_left = ttk.Button(self.window,text = "<", command = self.previous_frame,width = 2)
        self.nudge_left.grid(row = 2,column = 1,sticky = "E")

        self.nudge_left = ttk.Button(self.window,text = ">", command = self.next_frame,width = 2)
        self.nudge_left.grid(row = 2,column = 10,sticky = "W")


        #buttons for videos
        self.play = ttk.Button(self.window,text = "Play", command = self.play)
        self.play.grid(row = 2,column = 0,sticky = "E")

        self.pause = ttk.Button(self.window,text = "Pause", command = self.pause)
        self.pause.grid(row = 2,column = 1,sticky = "W")

        # Add a grid
        mainframe = tkinter.Frame(self.window)
        mainframe.grid(column=0,row=0, sticky="NW" )
        mainframe.columnconfigure(5, weight = 1)
        mainframe.rowconfigure(5, weight = 1)


        for i in range(self.number_of_trackers):
            self.vid.add_tracker()

        # Create a Tkinter variable
        self.tkvar = tkinter.StringVar(self.window)

        # Dictionary with options
        choices = []
        for i in range(len(self.vid.trackers)):
            #add value to NO_ID
            self.vid.trackers[i].s_id += str(i)
            choices.append(self.vid.trackers[i].s_id)
        choices.append("All")


        self.tkvar.set(self.vid.trackers[1].s_id) # set the default option

        popupMenu = ttk.OptionMenu(mainframe, self.tkvar, *choices)
        tkinter.Label(mainframe, text="Tracked Individual").grid(row = 1, column = 1)
        popupMenu.grid(row = 2, column =1)


        # on change dropdown value
    def change_dropdown(*args):
        print( self.tkvar.get() )
        # link function to change dropdown
        #self.tkvar.trace(find_tracker_index_by_id,change_dropdown)

    def find_tracker_index_by_id(self,name):
        if name == "All":
            self.working_number = self.number_of_trackers + 1
        for i in range(len(self.vid.trackers)):
            if name == self.vid.trackers[i].s_id:
                self.working_number = i
                print(self.working_number)
                return i




    def update(self):
        self.find_tracker_index_by_id(self.tkvar.get())
        print(self.working_number)
        # Get a frame from the video source
        self.frame_bar_label.config(text = int(self.vid.current_frame))
        #ret, whole_frame = self.vid.get_frame(self.vid.NO_TRACKING)

        #check if we are not the last frame, if we are, stop
        if self.vid.current_frame < self.vid.length:
            #track individual
            ret, frame = self.vid.get_frame(self.working_number)

            #track all
            #ret, track_all_frame = self.vid.get_frame(self.vid.TRACK_ALL)
            #update framenumber
            self.frame_bar_label.config(text = int(self.vid.current_frame))

            #typically at the end of the video it cannot process, restart video
            #self.set_frame_pos(1)
            #self.set_frame_bar()
            #self.play_state = False
            #print("ERROR")

                #if the return for a frame is true
            if ret:
                #set the canvas to the frame image

                self.photo = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(frame))
                self.canvas.create_image(0, 0, image = self.photo, anchor = tkinter.NW)

                #self.photo_focused = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(frame))
                #self.canvas_focused.create_image(0, 0, image = self.photo_focused, anchor = tkinter.NW)


                #after a certain time, update to the next frame if play is true
            if self.play_state is True:
                self.window.after(self.delay, self.update)
                self.set_frame_bar()

    def play(self):
        if self.play_state is not True:
            self.play_state = True
            self.update()

    def pause(self):
        #pause only if play is set
        if self.play_state is True:
            print("Pausing")
            self.play_state = False
            self.update()

    #NOTE current_frame - 7 just works idk why....
    def previous_frame(self):
        self.set_frame_pos(self.vid.current_frame-7)
        self.set_frame_bar()
        self.update()

    #NOTE current_frame - 5 just works idk why....
    def next_frame(self):
        self.set_frame_pos(self.vid.current_frame-5)
        self.set_frame_bar()
        self.update()


    def callback1(self,event):
        print ("one clicked at", event.x, event.y)
        return event.x, event.y

    def set_frame_bar(self):
        self.frame_bar.config(value = self.vid.current_frame)



    def set_frame_pos(self,value):
        self.vid.current_frame = math.floor(float(value))
        self.vid.set_frame(self.vid.current_frame)
        if self.play_state is False:
            self.update()
            #self.window.after(self.delay, )
    def save_profile(self):
        pass

        #loadfile finds a file from dialog
    def load_file(self):
        print("loading file")
        file_types = [('Video files', '*.mp4'), ('All files', '*')]
        dlg = fileDialog.Open()
        file = dlg.show()

        print(file)
        if file != '':
            try:
                del self.vid
            except: pass
            self.vid = VideoCapture(file)
            self.window_width = self.vid.width
            self.window_height = self.vid.height
            self.canvas = self.setup_canvas()
            #self.canvas_focused = self.setup_canvas_focused()

            self.setup_video_functions()

            self.update()

    def donothing(self):
        pass
