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
        self.object = self.vid.trackers[self.vid.working_number]

        #assign value to
        self.min = min
        self.max = max
        self.scale = tkinter.ttk.Scale(from_= min, to = max,command = self.set)
        self.scale.config (length = 480)
        self.scale.grid(row = row, column = column,sticky = "W")

        self.scale_name = tkinter.ttk.Label(text = name)
        self.scale_name.grid(row = row, column = column - 1, sticky = "E")

        self.scale_data = tkinter.ttk.Label()
        self.scale_data.grid(row = row, column = column+1, sticky = "E")

        self.update()


    def set(self, value):
        #check the name if we are tracking a new individual, if so set our object
        if self.object.s_id != self.vid.trackers[self.vid.working_number].s_id:

            self.object = self.vid.trackers[self.vid.working_number]
            print (self.object.s_id)

        #floor the value to suit the numbers being used
        value = floor(float(value))

        if self.name == "Offset":
            self.vid.set_tracker_offset(value)
            print("Offset:"+str(value))
        elif self.name == "Blocksize":
            self.vid.set_tracker_blocksize(value)
            print("Blocksize:"+str(value))
        elif self.name == "MinArea":
            self.vid.set_tracker_minarea(value)
            print("MinArea:"+str(value))
        elif self.name == "MaxArea":
            self.vid.set_tracker_maxarea(value)
            print("MaxArea:"+str(value))
        #display it's value
        self.scale_data.config(text = value)

    def get(self):
        if self.name == "Offset":
            value = self.object.offset
        elif self.name == "Blocksize":
            value = self.object.block_size
        elif self.name == "MinArea":
            value = self.object.min_area
        elif self.name == "MaxArea":
            return self.object.max_area
        return value

    def update(self):
        self.scale.set(value=self.get())
        self.scale_data.config(text = self.get())
