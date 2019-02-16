
#pip packages
import tkinter
from tkinter import ttk, filedialog
from PIL import Image, ImageTk
from cv2 import resize, INTER_CUBIC
#local
from video_process.video import VideoCapture
from tracktor_ui import tracktorOptions


class App:
    """
    This is where the video meets the interface where the commands are called.
    App contains all the tkinter widgets (sliders, buttons, ect.)
    and the widgets are then mapped to functions called onto the video

    App contains the update loop where the changes are made, the video
    then sends the processed frame with the new changes. The app then
    takes the frame from the video, and displays it using a Pillow converted
    frame.
    """
    def __init__(self, window, window_title):
        self.window = window
        self.window.title(window_title)


        self.window_width = 1080
        self.window_height = 720
        self.number_of_trackers = 1

        self.menu = tkinter.Menu(window)
        window.config(menu=self.menu)

        self.load_file()

        # self.window_width = self.vid.width
        # self.window_height = self.vid.height

        self.setup_menu()

        self.canvas = self.setup_canvas()

        self.setup_video_functions()

        #delay between update in milliseconds
        self.delay = 15

        #initialize update, this keeps looping as mainloop is called
        self.update()
        self.window.mainloop()

    def setup_canvas(self):
        """
        This creates a tkinter canvas for the video to display in.
        It also defines the cursor and cursor function.
        """
        # Create a canvas that can fit the above video source size, assign crosshair
        canvas = tkinter.Canvas(self.window,
                                width=self.window_width, height=self.window_height,
                                cursor="crosshair"
                                )
        canvas.bind("<Button-1>", self.callback1)
        canvas.grid(column=0, columnspan=5, row=1, ipady=1)
        return canvas

    def setup_menu(self):
        """
        This creates tkinter dropdown menu at the top consisting of File, Edit,
        and their children.
        """
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
        """
        This creates the interface for all the buttons and scales(sliders) associated with
        changing the data in the video.
        """
        #For choosing current frame
        self.frame_label = ttk.Label(text="frame:", width=15)
        self.frame_label.grid(row=3, column=6, sticky="W")

        #frame_bar is a scale to the length of the video, controlling which frame the video shows
        self.frame_bar = ttk.Scale(from_=0, to=self.vid.length - 1, command=self.vid.set_frame)
        self.frame_bar.config(length=self.window_width)
        self.frame_bar.grid(row=3, column=1, columnspan=3)

        self.zoom_label = ttk.Label(text="Zoom")
        self.zoom_label.grid(row=0, column=5, sticky="S")
        #can zoom in 15 times
        self.zoom_bar = ttk.Scale(from_=15, to=1,
                                  command=self.vid.set_zoom, orient=tkinter.VERTICAL)
        self.zoom_bar.config(length=self.window_height)
        self.zoom_bar.config(value=self.vid.zoom)
        self.zoom_bar.grid(row=1, column=5)

        #buttons for videos
        self.play = ttk.Button(self.window, text="Play", command=self.vid.play)
        self.play.grid(row=2, column=0, sticky="E")

        self.pause_btn = ttk.Button(self.window, text="Pause", command=self.vid.pause)
        self.pause_btn.grid(row=2, column=1, sticky="W")

        self.nudge_left = ttk.Button(self.window, text="<",
                                     command=self.vid.previous_frame, width=2)
        self.nudge_left.grid(row=3, column=0, sticky="E")

        self.nudge_right = ttk.Button(self.window, text=">", command=self.vid.next_frame, width=2)
        self.nudge_right.grid(row=3, column=5, sticky="W")

        #START DROPDOWN
        # Add a grid for dropdown
        self.mainframe = tkinter.Frame(self.window)
        self.mainframe.grid(row=0, column=0, sticky="NW")
        self.mainframe.columnconfigure(5)
        self.mainframe.rowconfigure(5)

        # Create a Tkinter variable
        self.tkvar = tkinter.StringVar(self.window)

        self.choices = []
        #First value in the list is considered as default
        self.choices.append("ALL")

        #List of options of choice begins here
        self.choices.append("All")
        #add trackers to set number
        self.create_tracker()

        #setup the menu
        self.popup_menu = ttk.OptionMenu(self.mainframe, self.tkvar, *self.choices)
        tkinter.Label(self.mainframe, text="Tracked Individual").grid(row=0, column=0)
        self.popup_menu.grid(row=1, column=0)
        #END DROPDOWN

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


    def update(self):
        """
        Update presents the updated frame with the new data, and also updates
        the interface based on the data at hand. (IE sliders change data, and if
        the tracker is changed to another individual, change the sliders to match)

        It continually receives a processed frame and displays it, then
        calls itself after a delay. (This is the form Tkinter is designed for)
        """
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
            frame = resize(frame,
                               (int(self.window_width), int(self.window_height)),
                               INTER_CUBIC)

            #update framenumber
            self.frame_label.config(text="Frame:" + str(int(self.vid.current_frame)))

            #if the return for a frame is true
            if ret:
                #set the canvas to the frame image
                self.photo = ImageTk.PhotoImage(image=Image.fromarray(frame))
                self.canvas.create_image(0, 0, image=self.photo, anchor=tkinter.NW)

        #after a certain time, update to the next frame if play is true
        self.update_frame_bar()
        self.window.after(self.delay, self.update)

    def callback1(self, event):
        """
        This function calculates the x and y coordinates based on
        the location clicked on the canvas, and maps it according to
        the resolution of the video.

        It then assignes the location to the tracktor object, allowing it
        to detect and delete all contours but the one the point exists in.

        Ex. If the display is 720x480 and the video is 1080x720, it
        maps the pixel from one to another.
        """
        self.vid.pause()

        #ratio is calculated between incomming frame to the output
        ratio_x = self.vid.width / self.window_width
        ratio_y = self.vid.height / self.window_height

        #calculate the position to the ratio
        pos_x = round(event.x * ratio_x)
        pos_y = round(event.y * ratio_y)

        #self.working_number = self.vid.find_tracker_index_by_id(self.tkvar.get())
        #self.vid.trackers[self.vid.working_number].clicked = (pos_x, pos_y)
        self.vid.create_tracker_pos(pos_x, pos_y)
        self.vid.set_tracker_pos(self.vid.trackers[self.vid.working_number])
        return event.x, event.y

    def update_frame_bar(self):
        """
        A simple function that sets the position of the frame bar
        based on the current frame.
        """
        self.frame_bar.config(value=self.vid.current_frame)

    def create_tracker(self):
        """
        This function adds a tracktor object to the tracker list (appended).
        The name is displayed on the popup menu(NOID when initialized),
        and then creates a new popup menu with the new data.

        NOTE: THIS FUNCTION NEEDS TO BE ABLE TO CHANGE NAME,
        AND BE UPDATED WITHOUT CREATING A NEW MENU EVERY TIME
        """
        #add a tracker in the video
        self.vid.add_tracker()
        index = len(self.vid.trackers)-1
        #add value to NO_ID
        self.vid.trackers[index].id += " " + str(index)
        self.choices.append(self.vid.trackers[index].id)
        #set the initial value
        self.tkvar.set(self.vid.trackers[0].id) # set the default option
        self.popup_menu = ttk.OptionMenu(self.mainframe, self.tkvar, *self.choices)
        self.popup_menu.grid(row=1, column=0)

    def save_profile(self):
        """
        This function is intended to provide a save, exit and load up again experience.
        NOTE: NOT IMPLEMENTED
        """
        pass

        #loadfile finds a file from dialog
    def load_file(self):
        """
        This function opens a file selection, and loads up the video selected.
        """
        print("loading file")
        file_types = [('Video files', '*.mp4'), ('All files', '*')]
        dlg = filedialog.Open(filetypes=file_types)
        file = dlg.show()

        print(file)
        if file != '':
            self.vid = VideoCapture(file)

    def donothing(self):
        """
        This function, literally, does nothing.

        The intent is to provide buttons with no function attatched.
        A filler.
        """
        pass
