from video import video
import time



if __name__ == '__main__':
    ## Start time
    start = time.time()

    program = video("Tracking")
    #program.load("0")
    program.load("./videos/mouse_video.mp4")

    ## End time and duration
    end = time.time()
    duration = end - start
    print("--- %s seconds ---" %duration)
