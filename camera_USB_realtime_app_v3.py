import cv2
from tkinter import *
from tkinter.font import Font
from PIL import Image, ImageTk

class VideoApp:
    def __init__(self, window, window_title):
        self.window = window
        self.window.title(window_title)
        self.video_source = 0

        # Set a bold font for the titles and buttons
        bold_font = Font(family="Helvetica", size=10, weight="bold")

        # Open the video source
        self.vid = cv2.VideoCapture(self.video_source)
        if not self.vid.isOpened():
            raise ValueError("Unable to open video source", self.video_source)

        self.width = self.vid.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.height = self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT)

        # Create a canvas that can fit the above video source size
        self.canvas = Canvas(window, width=self.width, height=self.height)
        self.canvas.pack()

        # Frame for buttons
        button_frame = Frame(window)
        button_frame.pack(side=BOTTOM, fill=X)

        # Button that lets the user pause the video
        self.btn_pause = Button(button_frame, text="Pause", width=10, command=self.pause_video, font=bold_font)
        self.btn_pause.pack(side=LEFT, padx=5, pady=5)

        # Button that lets the user play the video
        self.btn_play = Button(button_frame, text="Play", width=10, command=self.play_video, font=bold_font)
        self.btn_play.pack(side=LEFT, padx=5, pady=5)

        # Button that lets the user exit the program
        self.btn_stop = Button(button_frame, text="Stop", width=10, command=self.exit_video, font=bold_font)
        self.btn_stop.pack(side=LEFT, padx=5, pady=5)

        # Control variable for pausing the stream
        self.pause = False
        self.running = True
        self.update()

        self.window.mainloop()

    def pause_video(self):
        self.pause = True

    def play_video(self):
        self.pause = False

    def exit_video(self):
        self.running = False
        self.vid.release()
        self.window.quit()

    def update(self):
        if self.running:
            if not self.pause:
                # Get a frame from the video source
                ret, frame = self.vid.read()
                if ret:
                    self.photo = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                    self.photo = ImageTk.PhotoImage(image=self.photo)
                    self.canvas.create_image(0, 0, image=self.photo, anchor=NW)
            self.window.after(10, self.update)

# Create a window and pass it to the VideoApp class
root = Tk()
app = VideoApp(root, "ATLAS Egg Count Camera Feed")
root.mainloop()
