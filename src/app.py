from video_process.video import VideoCapture
from tracktor_ui import tracktorOptions
import PIL.Image, PIL.ImageTk

import numpy.matrixlib as np
import cv2
import tkinter
from tkinter import ttk
import tkinter.filedialog as fileDialog

class App:
    def __init__(self, window, window_title):
        self.window = window
        self.window.title(window_title)

        self.window_width = 720
        self.window_height = 480
        self.number_of_trackers = 1

        self.menu = tkinter.Menu(window)
        window.config(menu= self.menu)

        self.load_file()

        self.setup_menu()

        self.canvas = self.setup_canvas()
        self.setup_video_functions()

        # After it is called once, the update method will be automatically called every delay milliseconds
        self.delay = 15

        self.update()
        self.window.mainloop()

    def setup_canvas(self):
        # Create a canvas that can fit the above video source size, and inside the canvas change to crosshair
        canvas = tkinter.Canvas(self.window, width=self.window_width, height=self.window_height, cursor="crosshair")
        canvas.bind("<Button-1>", self.callback1)
        canvas.grid(column=0, columnspan=5, row=1, ipady=1)
        return canvas

    def setup_menu(self):
        self.file_menu = tkinter.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="File", menu=self.file_menu)

        self.file_menu.add_command(label="New", command=self.donothing)
        self.file_menu.add_command(label="Open", command=self.load_file)
        self.file_menu.add_command(label="Save", command=self.donothing)
        self.file_menu.add_command(label="Save as...", command=self.donothing)
        self.file_menu.add_command(label="Export All", command=self.vid.export_all)
        self.file_menu.add_command(label="Close", command=self.donothing)

        self.edit_menu = tkinter.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="Edit", menu=self.edit_menu)
        self.edit_menu.add_command(label="New Trackers", command=self.create_tracker)
        self.edit_menu.add_command(label="Delete Trackers", command=self.donothing)

    def setup_video_functions(self):
        #For choosing current frame
        self.frame_label = ttk.Label(text="frame:", width=15)
        self.frame_label.grid(row=3, column=6, sticky="W")

        #frame_bar is a scale to the length of the video, controlling which frame the video shows
        self.frame_bar  = ttk.Scale(from_=0, to=self.vid.length - 1, command=self.vid.set_frame)
        self.frame_bar.config(length=self.window_width)
        self.frame_bar.grid(row=3, column=1, columnspan=3)

        self.zoom_label = ttk.Label(text="Zoom")
        self.zoom_label.grid(row=0, column=5,sticky="S")
        self.zoom_bar = ttk.Scale(from_=10, to=1, command=self.vid.set_zoom, orient=tkinter.VERTICAL)
        self.zoom_bar.config(length=self.window_height)
        self.zoom_bar.grid(row=1, column=5)

        #buttons for videos
        self.play = ttk.Button(self.window, text="Play", command=self.vid.play)
        self.play.grid(row = 2, column=0, sticky="E")

        self.pause_btn = ttk.Button(self.window, text="Pause", command=self.vid.pause)
        self.pause_btn.grid(row=2, column=1, sticky="W")

        self.nudge_left = ttk.Button(self.window, text="<", command=self.vid.previous_frame, width=2)
        self.nudge_left.grid(row=3, column=0, sticky="E")

        self.nudge_right = ttk.Button(self.window, text=">", command=self.vid.next_frame, width=2)
        self.nudge_right.grid(row=3, column=5, sticky="W")

        # Add a grid for dropdown
        self.mainframe = tkinter.Frame(self.window)
        self.mainframe.grid(row=0, column=0, sticky="NW" )
        self.mainframe.columnconfigure(5)
        self.mainframe.rowconfigure(5)

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
        tkinter.Label(self.mainframe, text="Tracked Individual").grid(row=0, column=0)
        self.popupMenu.grid(row=1, column=0)

        self.offset_bar = tracktorOptions.Databar(self.window, self.vid, "Offset",
                                                  min_value=5, max_value=100,
                                                  row=4, column=1
                                                  )
        self.block_size_bar = tracktorOptions.Databar(self.window, self.vid, "Blocksize",
                                                      min_value=1, max_value=100,
                                                      row=5, column=1
                                                      )
        self.min_area_bar = tracktorOptions.Databar(self.window, self.vid, "MinArea",
                                                    min_value=1, max_value=5000,
                                                    row=6, column=1
                                                    )
        self.max_area_bar = tracktorOptions.Databar(self.window, self.vid, "MaxArea",
                                                    min_value=1, max_value=5000,
                                                    row=7, column=1
                                                    )
    # on change dropdown value
    # def change_dropdown(*args):
    #     pass
    #     # link function to change dropdown
    #     self.tkvar.trace(change_dropdown)

    def update(self):
        #set working number to the selected individual from the dropdown menu
        self.vid.working_number = self.vid.find_tracker_index_by_id(self.tkvar.get())
        #self.offset_bar.scale.config(value = self.vid.trackers[self.vid.working_number].offset)
        self.offset_bar.update()
        self.block_size_bar.update()
        self.min_area_bar.update()
        self.max_area_bar.update()
        #updata the data according to the selected user
        self.frame_label.config(text="Frame:"+str(int(self.vid.current_frame)))

        #check if we are not the last frame, if we are, stop
        if self.vid.current_frame < self.vid.length:
            #track individual
            ret, frame = self.vid.get_frame(self.vid.working_number)
            frame = cv2.resize(frame, (self.window_width, self.window_height), cv2.INTER_CUBIC)

            #update framenumber
            self.frame_label.config(text="Frame:" + str(int(self.vid.current_frame)))

            #if the return for a frame is true
            if ret:
                #set the canvas to the frame image
                self.photo=PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(frame))
                self.canvas.create_image(0, 0, image=self.photo, anchor=tkinter.NW)

        #after a certain time, update to the next frame if play is true
        self.update_frame_bar()
        self.window.after(self.delay, self.update)

    def callback1(self, event):
        self.vid.pause()

        #ratio is calculated between incomming frame to the output
        ratio_x = self.vid.width / self.window_width
        ratio_y = self.vid.height / self.window_height

        #calculate the position to the ratio
        pos_x = round(event.x * ratio_x)
        pos_y = round(event.y * ratio_y)

        #self.working_number = self.vid.find_tracker_index_by_id(self.tkvar.get())
        self.vid.trackers[self.vid.working_number].clicked = (pos_x, pos_y)
        return event.x, event.y

    def update_frame_bar(self):
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
        self.popupMenu.grid(row=1, column =0)

    def save_profile(self):
        pass

        #loadfile finds a file from dialog
    def load_file(self):
        print("loading file")
        file_types = [('Video files', '*.mp4'), ('All files', '*')]
        dlg = fileDialog.Open(filetypes = file_types)
        file = dlg.show()

        print(file)
        if file != '':
            self.vid = VideoCapture(file)
            self.vid.play_state = False
            #self.vid.vid.play_state = False

    def donothing(self):
        pass
