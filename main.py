# coding:utf-8
from video import video
import time
import cv2
import tkinter
from tkinter import ttk
import PIL.Image, PIL.ImageTk
from tracktor import tracktor
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

        #



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


class VideoCapture:
    def __init__(self, video_source=0):
        # Open the video source
        self.vid = cv2.VideoCapture(video_source)
        if not self.vid.isOpened():
            raise ValueError("Unable to open video source", video_source)

        # Get video source width, height and length in frames
        self.width = self.vid.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.height = self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT)
        self.length = self.vid.get(cv2.CAP_PROP_FRAME_COUNT)
        self.current_frame = 0
        self.last_frame = self.current_frame

        self.trackers = [tracktor()]*1

        #constants for interaction
        self.DISPLAY_FINAL = 0
        self.DISPLAY_THRESH = 1
        self.PAUSE_VIDEO = 3

        #assignment we use to choose different processes
        self.display_type = self.DISPLAY_FINAL

    def set_frame(self, value):
        self.vid.set(cv2.CAP_PROP_POS_FRAMES,value)

    def get_frame(self):
        if self.vid.isOpened():
            ret, frame = self.vid.read()

            self.current_frame = self.vid.get(cv2.CAP_PROP_POS_FRAMES)

            if ret:

                # Return a boolean success flag and the current frame converted to BGR
                #return (ret, cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                return (ret, self.process(self.trackers[0],frame,self.current_frame))
            else:
                return (ret, None)
        else:
            return (ret, None)

    def pause_frame(self):
        pass
    def resume_frames(self):
        pass
    def process(self,tracktor,frame,this):
        #preprocess the frames, adding a threshold, erode and dialing to
        #eliminate small noise
        thresh = tracktor.colour_to_thresh(frame)
        thresh = cv2.erode(thresh, tracktor.kernel, iterations = 1)
        thresh = cv2.dilate(thresh, tracktor.kernel, iterations = 1)

        #from our current frame, draw contours and display it on final frame
        final, contours = tracktor.detect_and_draw_contours(frame, thresh)

        #calculate cost of previous to currentmouse_video
        try:    row_ind, col_ind = tracktor.hungarian_algorithm()
        except:
            print("Cannot calculate cost")
            pass
        #try to re-draw, separate try-except block allows redraw of min_area/max_area
        try:
            final = tracktor.reorder_and_draw(final, col_ind, this)
        except:
            print("Can't draw")
            pass

        # Display the resulting frame
        if self.display_type is self.DISPLAY_FINAL:
            self.display_frame = final
        elif self.display_type is self.DISPLAY_THRESH:
            self.display_frame = thresh
        elif self.display_type is self.PAUSE_VIDEO:
            self.display_frame = final
        return self.display_frame

    # Release the video source when the object is destroyed
    def __del__(self):
        if self.vid.isOpened():
            self.vid.release()

if __name__ == "__main__":
 # Create a window and pass it to the Application object
    App(tkinter.Tk(), "Tkinter and OpenCV", "./videos/mouse_video.mp4")
    ## Start time
    #start = time.time()

    #program = video("Tracking")
    #program.load("0")
    #program.load("./videos/mouse_video.mp4")

    ## End time and duration
    #end = time.time()
    #duration = end - start
    #print("--- %s seconds ---" %duration)
