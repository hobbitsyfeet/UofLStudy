from tkinter import simpledialog

class Dialog:
    def __init__(self, title, message):
        self.messagebox.showinfo(title, message)
        self.answer = simpledialog.askstring("Input", "What is your first name?", 
                                parent=window)
