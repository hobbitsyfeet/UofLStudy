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

        # open video source (by default this will try to open the computer webcam)
        self.vid = VideoCapture(self.video_source)

        #set min window size to the videocapture size
        window.minsize(int(self.vid.width),int(self.vid.height))

        # Create a canvas that can fit the above video source size, and inside the canvas change to crosshair
        self.canvas = tkinter.Canvas(window, width = self.vid.width, height = self.vid.height, cursor = "crosshair")
        self.canvas.bind("<Button-1>", self.callback1)
        self.canvas.pack()

        self.frame_bar_label = ttk.Label( text = "frame:")
        self.frame_bar_label.pack()

        self.frame_bar  = ttk.Scale(from_=0, to = self.vid.length,command = self.set_frame_pos)
        self.frame_bar.pack()

        # After it is called once, the update method will be automatically called every delay milliseconds
        self.delay = 15
        self.update()

        self.window.mainloop()

    def update(self):
        # Get a frame from the video source
        ret, frame = self.vid.get_frame()
        self.frame_bar_label.config(text = self.vid.current_frame)
        self.set_frame_bar()
        if ret:
            self.photo = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(frame))
            self.canvas.create_image(0, 0, image = self.photo, anchor = tkinter.NW)

        self.window.after(self.delay, self.update)

    def callback1(self,event):
        print ("one clicked at", event.x, event.y)
        return event.x, event.y

    def set_frame_bar(self):
        self.frame_bar.config(value = self.vid.current_frame)

    def set_frame_pos(self,value):
        self.vid.current_frame = math.floor(float(value))
        self.vid.set_frame(self.vid.current_frame)
