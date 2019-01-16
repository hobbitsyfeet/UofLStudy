import tkinter
from math import floor

#OFFSET = 0
#BLOCKSIZE = 1
#MINAREA = 2
#MAXAREA = 3

class Databar:
    """
    A Tkinter Scale but with the name and data showing on either side
    """
    def __init__(self, root, vid, name,
                 min_value, max_value,
                 row, column):

        #assign variable to
        self.root = root
        self.vid = vid
        self.name = name
        self.object = self.vid.trackers[self.vid.working_number]

        #Tkinter scake with range from min to max, and an width(length)
        self.scale = tkinter.ttk.Scale(from_=min_value, to=max_value, command=self.set)
        self.scale.config(length=480)

        #place tkinter scale on the window grid
        self.scale.grid(row=row, column=column, sticky="W")

        #Apply name on the left hand side of the scale
        self.scale_name = tkinter.ttk.Label(text=name)
        self.scale_name.grid(row=row, column=column - 1, sticky="E")

        #Apply data on the Right hand side of the scale
        self.scale_data = tkinter.ttk.Label()
        self.scale_data.grid(row=row, column=column + 1, sticky="E")

        #according to the data's values, update the scales to match
        self.update()


    def set(self, value):
        """
        Assigns value from scale according to the name of the Databar 

        NOTE: REVISE HOW ITS DONE

        Parameters
        ----------
        value: float
            value to assign tracktor variables
        """
        #check the name if we are tracking a new individual, if so set our object
        if self.object.s_id != self.vid.trackers[self.vid.working_number].s_id:

            self.object = self.vid.trackers[self.vid.working_number]
            print (self.object.s_id)

        #floor the value to suit the numbers being used
        value = floor(float(value))

        if self.name == "Offset":
            self.vid.set_tracker_offset(value)
        elif self.name == "Blocksize":
            self.vid.set_tracker_blocksize(value)
        elif self.name == "MinArea":
            self.vid.set_tracker_minarea(value)
        elif self.name == "MaxArea":
            self.vid.set_tracker_maxarea(value)
        #display it's value
        self.scale_data.config(text=value)

    def get(self):
        """
        Returns a value according to the name of the Databar
        
        NOTE: REVISE HOW ITS DONE

        Returns
        -------
        value: float
        """
        current_tracktor = self.vid.trackers[self.vid.working_number]
        if self.name == "Offset":
            value = current_tracktor.offset
        elif self.name == "Blocksize":
            value = current_tracktor.block_size
        elif self.name == "MinArea":
            value = current_tracktor.min_area
        elif self.name == "MaxArea":
            return current_tracktor.max_area
        return value

    def update(self):
        self.scale.config(value = self.get())
        self.scale_data.config(text=self.get())
