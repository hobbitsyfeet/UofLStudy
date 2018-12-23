# coding:utf-8
from video import VideoCapture
import time
import cv2
import tkinter
from tkinter import ttk
import PIL.Image, PIL.ImageTk
import math

class App:
    def __init__(self, window, window_title, video_source=0):
        self.window = window
        self.window.title(window_title)
        self.border = 10
        self.video_source = video_source
        self.number_of_trackers = 1

        self.working_number = 1

        self.play_state = False

        # open video source (by default this will try to open the computer webcam)
        self.vid = VideoCapture(self.video_source)

        #set min window size to the videocapture size
        #window.minsize(int(self.vid.width),int(self.vid.height))

        # Create a canvas that can fit the above video source size, and inside the canvas change to crosshair

        self.canvas = tkinter.Canvas(window, width = self.vid.width, height = self.vid.height, cursor = "crosshair")
        self.canvas.bind("<Button-1>", self.callback1)
        self.canvas.grid(column = 0, columnspan = 5,row=0)
        #self.canvas.pack(side=tkinter.TOP)

        self.canvas_focused = tkinter.Canvas(window, width = self.vid.width, height = self.vid.height, cursor = "crosshair")
        self.canvas_focused.bind("<Button-1>", self.callback1)
        self.canvas_focused.grid(column = 6,columnspan = 5,row=0)
        #self.canvas_focused.pack(side=tkinter.LEFT)


        self.frame_bar_label = ttk.Label( text = "frame:", font = ('Helvetica', '16') )
        self.frame_bar_label.grid(column = 3,columnspan=7,row=3)
        #self.frame_bar_label.pack()

        #frame_bar is a scale to the length of the video, controlling which frame the video shows
        self.frame_bar  = ttk.Scale(from_=0, to = self.vid.length,command = self.set_frame_pos)
        self.frame_bar.config(length = self.vid.width)
        self.frame_bar.grid(column = 3,columnspan=7,row=2)
        #self.frame_bar.pack(side = tkinter.LEFT)

        #buttons for videos
        self.play = ttk.Button(window,text = "Play", command = self.play)
        self.play.grid(row = 2,column = 0)

        self.pause = ttk.Button(window,text = "Pause", command = self.pause)
        self.pause.grid(row = 2,column = 1)

        # After it is called once, the update method will be automatically called every delay milliseconds
        self.delay = 15
        self.update()

        self.window.mainloop()

    def update(self):

        # Get a frame from the video source
        self.set_frame_bar()
        try:

            ret, frame = self.vid.get_frame(1)
            ret, whole_frame = self.vid.get_frame(self.vid.NO_TRACKING)
            ret, track_all_frame = self.vid.get_frame(self.vid.TRACK_ALL)
            self.frame_bar_label.config(text = int(self.vid.current_frame))

        except:
            #typically at the end of the video it cannot process, restart video
            self.set_frame_pos(1)
            self.set_frame_bar()
            self.window.after(self.delay, self.update)
            #self.window.after(self.delay*10, )


            #if the return for a frame is true
        if ret:
            #set the canvas to the frame image
            self.photo = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(track_all_frame))
            self.canvas.create_image(0, 0, image = self.photo, anchor = tkinter.NW)

            self.photo_focused = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(frame))
            self.canvas_focused.create_image(0, 0, image = self.photo_focused, anchor = tkinter.NW)


        #after a certain time, update to the next frame if play is true
        if self.play_state is True:
            self.window.after(self.delay, self.update)


    def play(self):
        if self.play_state is not True:
            self.play_state = True
            self.update()

    def pause(self):
        print("Pausing")
        self.play_state = False


    def callback1(self,event):
        print ("one clicked at", event.x, event.y)
        return event.x, event.y

    def set_frame_bar(self):
        self.frame_bar.config(value = self.vid.current_frame)

    def set_frame_pos(self,value):
        self.vid.current_frame = math.floor(float(value))
        self.vid.set_frame(self.vid.current_frame)
