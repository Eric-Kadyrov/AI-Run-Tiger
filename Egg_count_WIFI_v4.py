import cv2
from tkinter import *
from tkinter.font import Font
from PIL import Image, ImageTk, ImageDraw
import time
import requests

# Set your D-Link IP camera details
USERNAME = "Admin"
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

# Roboflow API details
API_URL = "https://detect.roboflow.com"
API_KEY = "mPb0XMaWxTCOE15TbtbX"  # Replace with your actual API key
MODEL_ID = "new-batch/1"  # Replace with your model ID

# Function to detect eggs using Roboflow API
def detect_eggs_with_roboflow(image_path, output_path="labeled_eggs.jpg"):
    api_url = f"{API_URL}/{MODEL_ID}?api_key={API_KEY}"

    with open(image_path, "rb") as image_file:
        response = requests.post(api_url, files={"file": image_file})

    if response.status_code != 200:
        raise Exception(f"Error: Unable to connect to Roboflow API. Status Code: {response.status_code}, Response: {response.text}")

    result = response.json()
    predictions = result.get("predictions", [])
    egg_count = len(predictions)

    image = Image.open(image_path)
    draw = ImageDraw.Draw(image)

    for prediction in predictions:
        x, y, w, h = prediction["x"], prediction["y"], prediction["width"], prediction["height"]
        confidence = prediction["confidence"]

        x_min = int(x - w / 2)
        y_min = int(y - h / 2)
        x_max = int(x + w / 2)
        y_max = int(y + h / 2)

        draw.rectangle([x_min, y_min, x_max, y_max], outline="green", width=3)
        label = f"Egg {confidence:.2f}"
        draw.text((x_min, y_min - 10), label, fill="green")

    image.save(output_path)
    return egg_count, output_path

class VideoApp:
    def __init__(self, window, window_title):
        self.window = window
        self.window.title(window_title)
        self.video_source = None
        self.vid = None

        # Set a bold font for UI elements
        bold_font = Font(family="Helvetica", size=10, weight="bold")

        # Create UI Elements Before opening the video stream
        self.button_frame = Frame(window)
        self.button_frame.pack(side=BOTTOM, fill=X)

        self.btn_pause = Button(self.button_frame, text="Pause", width=10, command=self.pause_video, font=bold_font)
        self.btn_pause.pack(side=LEFT, padx=5, pady=5)

        self.btn_play = Button(self.button_frame, text="Play", width=10, command=self.play_video, font=bold_font)
        self.btn_play.pack(side=LEFT, padx=5, pady=5)

        self.btn_stop = Button(self.button_frame, text="Stop", width=10, command=self.exit_video, font=bold_font)
        self.btn_stop.pack(side=LEFT, padx=5, pady=5)

        # Placeholder Label while video loads
        self.canvas = Label(window, text="Connecting to Camera...", font=("Helvetica", 12))
        self.canvas.pack()

        # Try multiple RTSP URLs
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
            self.canvas.config(text="Error: Unable to load video stream.")
            return

        self.width = int(self.vid.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT))

        # Replace placeholder label with the actual video feed
        self.canvas.destroy()
        self.canvas = Canvas(window, width=self.width, height=self.height)
        self.canvas.pack()

        # Second window for still images
        self.photo_window = Toplevel(window)
        self.photo_window.title("30 sec Capture")
        self.photo_canvas = Canvas(self.photo_window, width=self.width, height=self.height)
        self.photo_canvas.pack()

        self.egg_count_label = Label(self.photo_window, text="Egg count: 0", font=("Helvetica", 14, "bold"))
        self.egg_count_label.pack()

        # Control variables
        self.pause = False
        self.running = True
        self.last_capture_time = time.time()

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
                    # Convert frame for Tkinter display
                    live_photo = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                    self.live_photo_tk = ImageTk.PhotoImage(image=live_photo)
                    self.canvas.create_image(0, 0, image=self.live_photo_tk, anchor=NW)

                    # Capture still image every 30 seconds
                    if time.time() - self.last_capture_time >= 30:
                        self.last_capture_time = time.time()
                        still_image_path = "temp_still_image.jpg"
                        cv2.imwrite(still_image_path, frame, [int(cv2.IMWRITE_JPEG_QUALITY), 95])

                        try:
                            egg_count, annotated_path = detect_eggs_with_roboflow(still_image_path)
                            annotated_image = Image.open(annotated_path)
                            annotated_image = annotated_image.resize((int(self.width), int(self.height)), Image.Resampling.LANCZOS)
                            self.annotated_photo_tk = ImageTk.PhotoImage(image=annotated_image)
                            self.photo_canvas.create_image(0, 0, image=self.annotated_photo_tk, anchor=NW)
                            self.egg_count_label.config(text=f"Egg count: {egg_count}")
                        except Exception as e:
                            print(f"Error in egg detection: {e}")

            self.window.after(10, self.update)

# Run the app
root = Tk()
app = VideoApp(root, "Egg Count - IP Camera Stream")
root.mainloop()
