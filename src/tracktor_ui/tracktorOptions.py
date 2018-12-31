import tkinter
from math import floor

#OFFSET = 0
#BLOCKSIZE = 1
#MINAREA = 2
#MAXAREA = 3

class data_bar:
    def __init__(self, root, vid, name,
                    working_number,
                    min, max,
                    row, column):

        self.OFFSET = 0
        #assign variable to
        self.root = root
        self.vid = vid
        self.name = name
        self.working_number = working_number
        self.object = self.vid.trackers[working_number]

        #assign value to
        self.min = min
        self.max = max
        self.scale = tkinter.ttk.Scale(from_= min, to = max,command = self.set)
        self.scale.config (length = 480)
        #self.scale.config(length = root.winfo_width())

        self.scale.grid(row = row, column = column,sticky = "W")
        self.scale_name = tkinter.ttk.Label(text = name)
        self.scale_name.grid(row = row, column = column - 1, sticky = "E")


    def set(self, value):
        value = floor(float(value))
        if self.name == "Offset":
            self.object.offset = value
            print("Offset:"+str(value))
        elif self.name == "Blocksize":
            self.object.block_size = value
            print("Blocksize:"+str(value))
        elif self.name == "MinArea":
            self.object.min_area = value
            print("MinArea:"+str(value))
        elif self.name == "MaxArea":
            self.object.max_area = value
            print("MaxArea:"+str(value))
        #if self.vid.play_state is False:
        #    set_frame_pos(-1)

    def get(self):
        if self.name == "Offset":
            self.value = object.offset
        elif self.name == "Blocksize":
            self.value = object.block_size
        elif self.name == "MinArea":
            self.value = object.min_area
        elif self.name == "MaxArea":
            self.value = object.max_area
        return self.value

    def update(self,video):
        #video.current_frame-1
        pass
