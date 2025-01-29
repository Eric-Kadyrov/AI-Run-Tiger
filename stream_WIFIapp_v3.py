import cv2
from tkinter import *
from tkinter.font import Font
from PIL import Image, ImageTk

# Set your D-Link IP camera details
USERNAME = "Admin"  # Updated login
PASSWORD = "Atlas33"
IP_ADDRESS = "192.168.0.109"
RTSP_PORT = "554"

# Possible RTSP stream URLs for D-Link cameras
POSSIBLE_STREAMS = [
    f"rtsp://{USERNAME}:{PASSWORD}@{IP_ADDRESS}:{RTSP_PORT}/live1.sdp",
    f"rtsp://{USERNAME}:{PASSWORD}@{IP_ADDRESS}:{RTSP_PORT}/play1.sdp",
    f"rtsp://{USERNAME}:{PASSWORD}@{IP_ADDRESS}:{RTSP_PORT}/cam1",
    f"rtsp://{USERNAME}:{PASSWORD}@{IP_ADDRESS}:{RTSP_PORT}/live2.sdp"
]

class VideoApp:
    def __init__(self, window, window_title):
        self.window = window
        self.window.title(window_title)
        self.video_source = None
        self.vid = None

        # Set a bold font for UI elements
        bold_font = Font(family="Helvetica", size=10, weight="bold")

        # Try multiple RTSP URLs to find the correct one
        for url in POSSIBLE_STREAMS:
            print(f"Trying RTSP stream: {url}")
            self.vid = cv2.VideoCapture(url)
            if self.vid.isOpened():
                self.video_source = url
                print(f"Connected to: {url}")
                break
            else:
                print(f"Failed to connect: {url}")

        if not self.vid.isOpened():
            raise ValueError("Unable to open video stream from any RTSP source.")

        self.width = self.vid.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.height = self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT)

        # Create a canvas for video display
        self.canvas = Canvas(window, width=self.width, height=self.height)
        self.canvas.pack()

        # Frame for control buttons
        button_frame = Frame(window)
        button_frame.pack(side=BOTTOM, fill=X)

        # Pause button
        self.btn_pause = Button(button_frame, text="Pause", width=10, command=self.pause_video, font=bold_font)
        self.btn_pause.pack(side=LEFT, padx=5, pady=5)

        # Play button
        self.btn_play = Button(button_frame, text="Play", width=10, command=self.play_video, font=bold_font)
        self.btn_play.pack(side=LEFT, padx=5, pady=5)

        # Stop button
        self.btn_stop = Button(button_frame, text="Stop", width=10, command=self.exit_video, font=bold_font)
        self.btn_stop.pack(side=LEFT, padx=5, pady=5)

        # Control variables
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
                ret, frame = self.vid.read()
                if ret:
                    # Convert OpenCV frame to Tkinter format
                    self.photo = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                    self.photo = ImageTk.PhotoImage(image=self.photo)
                    self.canvas.create_image(0, 0, image=self.photo, anchor=NW)
                else:
                    print("Error: Unable to read video frame.")

            self.window.after(10, self.update)

# Start the GUI application
root = Tk()
app = VideoApp(root, "D-Link IP Camera Stream")
root.mainloop()
