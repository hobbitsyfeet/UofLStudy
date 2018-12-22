from app import App
import tkinter

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
