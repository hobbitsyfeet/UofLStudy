# coding:utf-8
#from tracktor_ui import dialog
#from video import VideoCapture

from video_process.video import VideoCapture
from tracktor_ui import tracktorOptions
from tracktor_ui.dialog import Dialog

import PIL.Image, PIL.ImageTk
import math

import numpy.matrixlib as np
import time
import cv2
import tkinter
from tkinter import ttk
import tkinter.filedialog as fileDialog


class App:
    def __init__(self, window, window_title):
        self.window = window
        self.window.title(window_title)

        self.window_width = 1080
        self.window_height = 720
        self.number_of_trackers = 1

        self.working_number = 0

        self.play_state = False

        self.menu = tkinter.Menu(window)
        window.config(menu= self.menu)


        #set min window size to the videocapture size
        self.load_file()


        self.file_menu = tkinter.Menu(self.menu, tearoff = 0)
        self.menu.add_cascade(label = "File", menu = self.file_menu)

        self.file_menu.add_command(label="New", command=self.donothing)
        self.file_menu.add_command(label="Open", command=self.load_file)
        self.file_menu.add_command(label="Save", command=self.donothing)
        self.file_menu.add_command(label="Save as...", command=self.donothing)
        self.file_menu.add_command(label="Export All", command=self.vid.export_all)
        self.file_menu.add_command(label="Close", command=self.donothing)

        self.edit_menu = tkinter.Menu(self.menu, tearoff = 0)
        self.menu.add_cascade(label = "Edit", menu = self.edit_menu)
        self.edit_menu.add_command(label="New Trackers", command=self.create_tracker)
        self.edit_menu.add_command(label="Delete Trackers", command = self.donothing)

        #buttons for videos
        self.play = ttk.Button(self.window,text = "Play", command = self.play)
        self.play.grid(row = 2,column = 0,sticky = "E")

        self.pause = ttk.Button(self.window,text = "Pause", command = self.pause)
        self.pause.grid(row = 2,column = 1,sticky = "W")



        #self.vid.TRACK_ALL = -1

        #self.nudge_left_btn = ttk.Button(window, text = "<-" ,command = self.previous_frame )

        # After it is called once, the update method will be automatically called every delay milliseconds
        self.delay = 15
        #loads file and sets up canvases from the new file

        self.window.mainloop()

    def setup_canvas(self):
        # Create a canvas that can fit the above video source size, and inside the canvas change to crosshair
        canvas = tkinter.Canvas(self.window, width = self.window_width, height = self.window_height , cursor = "crosshair")
        canvas.bind("<Button-1>", self.callback1)
        canvas.grid(column = 0, columnspan = 6,row=1,ipady = 1)
        return canvas

    def setup_video_functions(self):

        #For choosing current frame
        self.frame_label = ttk.Label( text = "frame:")
        self.frame_label.grid(row=3,column = 2, sticky = "W")

        #frame_bar is a scale to the length of the video, controlling which frame the video shows
        self.frame_bar  = ttk.Scale(from_=0, to = self.vid.length - 1,command = self.set_frame_pos)
        self.frame_bar.config(length = self.window_width)
        self.frame_bar.grid(row=3,column = 1)

        self.nudge_left = ttk.Button(self.window,text = "<", command = self.previous_frame,width = 2)
        self.nudge_left.grid(row = 3,column = 0,sticky = "E")

        self.nudge_left = ttk.Button(self.window,text = ">", command = self.next_frame, width = 2)
        self.nudge_left.grid(row = 3,column = 3,sticky = "W")

        # Add a grid for dropdown
        self.mainframe = tkinter.Frame(self.window)
        self.mainframe.grid(row=0,column=0, sticky="NW" )
        self.mainframe.columnconfigure(5, weight = 1)
        self.mainframe.rowconfigure(5, weight = 1)

        # Create a Tkinter variable
        self.tkvar = tkinter.StringVar(self.window)

        self.choices = []
        self.choices.append("NONE")
        self.choices.append("All")
        #add trackers to set number
        for i in range(self.number_of_trackers):
            self.create_tracker()

        #setup the menu
        self.popupMenu = ttk.OptionMenu(self.mainframe, self.tkvar, *self.choices)
        tkinter.Label(self.mainframe, text="Tracked Individual").grid(row = 1, column = 1)
        self.popupMenu.grid(row = 2, column =1)

        offset_bar = tracktorOptions.data_bar(self.window, self.vid, "Offset",
                                self.working_number,
                                min= 5, max= 100,
                                row= 4, column= 1
                                )

        block_size_bar = tracktorOptions.data_bar(self.window, self.vid, "Blocksize",
                                self.working_number,
                                min= 1, max= 100,
                                row= 5, column= 1
                                )
        min_area_bar = tracktorOptions.data_bar(self.window, self.vid, "MinArea",
                                self.working_number,
                                min= 1, max= 5000,
                                row= 6, column= 1
                                )
        max_area_bar = tracktorOptions.data_bar(self.window, self.vid, "MaxArea",
                                self.working_number,
                                min= 1, max= 5000,
                                row= 7, column= 1
                                )
    # on change dropdown value
    def change_dropdown(*args):
        pass
        # link function to change dropdown
        self.tkvar.trace(change_dropdown)

    def update(self):
        self.vid.working_number = self.vid.find_tracker_index_by_id(self.tkvar.get())
        # Get a frame from the video source
        self.frame_label.config(text = "Frame:"+str(int(self.vid.current_frame)))

        #check if we are not the last frame, if we are, stop
        if self.vid.current_frame < self.vid.length:
            #track individual
            ret, frame = self.vid.get_frame(self.vid.working_number)
            frame = cv2.resize(frame,(int(1080),(int(720))),cv2.INTER_CUBIC)

            #update framenumber
            self.frame_label.config(text ="Frame:" + str(int(self.vid.current_frame)))

                #if the return for a frame is true
            if ret:
                #set the canvas to the frame image
                self.photo = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(frame))
                self.canvas.create_image(0, 0, image = self.photo, anchor = tkinter.NW)

                #after a certain time, update to the next frame if play is true
            if self.play_state is True:
                self.window.after(self.delay, self.update)
                self.set_frame_bar()

    def play(self):
        if self.play_state is False:
            self.play_state = True
            self.update()

    def pause(self):
        #pause only if play is set
        if self.play_state is True:
            print("Pausing")
            self.play_state = False
            self.update()

    def previous_frame(self):
        self.set_frame_pos(self.vid.current_frame-3)
        self.update()
        self.set_frame_bar()

    def next_frame(self):
        self.update()
        self.set_frame_bar()


    def callback1(self,event):
        if self.play_state is True:
            print("Pausing")
            self.play_state = False
        self.set_frame_pos(self.vid.current_frame-2)

        #ratio is calculated between incomming frame to the output
        ratio_x = self.vid.width / self.window_width
        ratio_y = self.vid.height / self.window_height
        print("ratio X " +str(ratio_x) )
        print("ratio X " +str(ratio_y) )

        pos_x = round(event.x * ratio_x)
        pos_y = round(event.y * ratio_y)


        print ("one clicked at", pos_x, pos_y)
        self.vid.trackers[self.working_number].clicked = (pos_x, pos_y)
        self.update()
        return event.x, event.y

    def set_frame_bar(self):
        self.frame_bar.config(value = self.vid.current_frame)


    def create_tracker(self):
        #add a tracker in the video
        self.vid.add_tracker()
        index = len(self.vid.trackers)-1
        #add value to NO_ID
        self.vid.trackers[index].s_id += str(index)
        self.choices.append(self.vid.trackers[index].s_id)
        #set the initial value
        self.tkvar.set(self.vid.trackers[0].s_id) # set the default option
        self.popupMenu = ttk.OptionMenu(self.mainframe, self.tkvar, *self.choices)
        self.popupMenu.grid(row = 2, column =1)



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
            self.vid = VideoCapture(file)
            self.play_state = False
            self.vid.play_state = False
            self.canvas = self.setup_canvas()
            self.setup_video_functions()
            self.update()

    def donothing(self):
        pass
