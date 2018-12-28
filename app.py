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
        self.number_of_trackers = 3


        self.working_number = 0

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

        #For choosing current frame
        self.frame_label = ttk.Label( text = "frame:", font = ('Helvetica', '16') )
        self.frame_label.grid(column = 6,row=3,columnspan = 2, sticky = "NW")

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

        # Add a grid for dropdown
        mainframe = tkinter.Frame(self.window)
        mainframe.grid(column=0,row=0, sticky="NW" )
        mainframe.columnconfigure(5, weight = 1)
        mainframe.rowconfigure(5, weight = 1)
        #add trackers to set number
        for i in range(self.number_of_trackers):
            self.vid.add_tracker()

        # Create a Tkinter variable
        self.tkvar = tkinter.StringVar(self.window)

        # Dictionary with options
        choices = []
        for i in range(len(self.vid.trackers)):
            if i == 0:
                choices.append(self.vid.trackers[i].s_id + str(i))
            #add value to NO_ID
            self.vid.trackers[i].s_id += str(i)
            choices.append(self.vid.trackers[i].s_id)
        choices.append("All")


        #set the initial value
        self.tkvar.set(self.vid.trackers[0].s_id) # set the default option

        #setup the menu
        popupMenu = ttk.OptionMenu(mainframe, self.tkvar, *choices)
        tkinter.Label(mainframe, text="Tracked Individual").grid(row = 1, column = 1)
        popupMenu.grid(row = 2, column =1)

        self.offset_bar  = ttk.Scale(from_=0, to = 100,command = self.set_offset)
        self.offset_bar.config(length = self.vid.width)
        self.offset_bar.config(value = self.vid.trackers[self.working_number].offset)
        self.offset_bar.grid(column = 2,row=4,columnspan = 2, sticky = "SW")
        self.offset_label = ttk.Label(font = ('Helvetica', '16') )
        self.offset_label.grid(column = 6,row=4,columnspan = 2, sticky = "NW")
        self.offset_label.config(text = "Offset:" + str(self.vid.trackers[self.working_number].offset))

        self.block_size_bar  = ttk.Scale(from_=0, to = 100,command = self.set_blocksize)
        self.block_size_bar.config(length = self.vid.width)
        self.block_size_bar.config(value = self.vid.trackers[self.working_number].block_size)
        self.block_size_bar.grid(column = 2,row=5,columnspan = 2, sticky = "SW")
        self.block_size_label = ttk.Label(font = ('Helvetica', '16') )
        self.block_size_label.grid(column = 6,row=5,columnspan = 2, sticky = "NW")
        self.block_size_label.config(text = "Block_size:" + str(self.vid.trackers[self.working_number].block_size))

        self.min_area_bar  = ttk.Scale(from_=0, to = 100000,command = self.set_min_area)
        self.min_area_bar.config(length = self.vid.width)
        self.min_area_bar.config(value = self.vid.trackers[self.working_number].min_area)
        self.min_area_bar.grid(column = 2,row=6,columnspan = 2, sticky = "SW")
        self.min_area_label = ttk.Label(font = ('Helvetica', '16') )
        self.min_area_label.grid(column = 6,row=6,columnspan = 2, sticky = "NW")
        self.min_area_label.config(text = "Min_area:" + str(self.vid.trackers[self.working_number].min_area))

        self.max_area_bar  = ttk.Scale(from_=0, to = 100000,command = self.set_max_area)
        self.max_area_bar.config(length = self.vid.width)
        self.max_area_bar.grid(column = 2,row=7,columnspan = 2, sticky = "SW")
        self.max_area_label = ttk.Label(font = ('Helvetica', '16') )
        self.max_area_label.grid(column = 6,row=7,columnspan = 2, sticky = "NW")
        self.max_area_label.config(text = "Max_area:" + str(self.vid.trackers[self.working_number].max_area))

        # on change dropdown value
    def change_dropdown(*args):
        pass
        # link function to change dropdown
        #self.tkvar.trace(find_tracker_index_by_id,change_dropdown)

    def find_tracker_index_by_id(self,name):
        if name == "All":
            self.working_number = self.vid.TRACK_ALL
        for i in range(len(self.vid.trackers)):
            if name == self.vid.trackers[i].s_id:
                self.working_number = i
                return i




    def update(self):
        self.find_tracker_index_by_id(self.tkvar.get())
        # Get a frame from the video source
        self.frame_label.config(text = "Frame:"+str(int(self.vid.current_frame)))

        #check if we are not the last frame, if we are, stop
        if self.vid.current_frame < self.vid.length:
            #track individual
            ret, frame = self.vid.get_frame(self.working_number)

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

    def set_offset(self,value):
        #set local for ease of use
        offset = math.floor(float(value))
        self.vid.trackers[self.working_number].offset = offset

        #get the config value for the current viewed tracker
        self.offset_bar.config(value = offset)
        self.offset_label.config(text = "Offset:" + str(offset))

    def set_blocksize(self,value):
        block_size = math.floor(float(value))
        self.vid.trackers[self.working_number].block_size = block_size

        #get the config value for the current viewed tracker
        self.block_size_bar.config(value = block_size)
        self.block_size_bar.config(text = "Block_size:" + str(block_size))


    def set_min_area(self,value):
        #set local for ease of use
        min_area = math.floor(float(value))
        self.vid.trackers[self.working_number].min_area = min_area

        #get the config value for the current viewed tracker
        self.min_area_bar.config(value = min_area)
        self.min_area_label.config(text = "Min_area:" + str(min_area))


    def set_max_area(self,value):
        #set local for ease of use
        max_area = math.floor(float(value))
        self.vid.trackers[self.working_number].max_area = max_area

        #get the config value for the current viewed tracker
        self.max_area_bar.config(value = max_area)
        self.max_area_label.config(text = "Max_area:" + str(max_area))

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
