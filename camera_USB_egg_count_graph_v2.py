import cv2
from tkinter import *
from tkinter.font import Font
from PIL import Image, ImageTk, ImageDraw
import time
import requests
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Roboflow API details
API_URL = "https://detect.roboflow.com"
API_KEY = "mPb0XMaWxTCOE15TbtbX"  # Replace with your actual API key
MODEL_ID = "new-batch/1"  # Replace with your model ID

# Function to detect eggs using the Roboflow API
def detect_eggs_with_roboflow(image_path, output_path="labeled_eggs.jpg"):
    # Prepare the API URL
    api_url = f"{API_URL}/{MODEL_ID}?api_key={API_KEY}"

    # Open the image
    with open(image_path, "rb") as image_file:
        # Send the image to the Roboflow API
        response = requests.post(api_url, files={"file": image_file})

    # Check for a valid response
    if response.status_code != 200:
        raise Exception(f"Error: Unable to connect to Roboflow API. Status Code: {response.status_code}, Response: {response.text}")

    # Parse the response
    result = response.json()
    predictions = result.get("predictions", [])
    egg_count = len(predictions)

    # Load the image using PIL
    image = Image.open(image_path)
    draw = ImageDraw.Draw(image)

    # Draw bounding boxes and labels
    for prediction in predictions:
        x, y, w, h = prediction["x"], prediction["y"], prediction["width"], prediction["height"]
        confidence = prediction["confidence"]

        # Calculate the bounding box coordinates
        x_min = int(x - w / 2)
        y_min = int(y - h / 2)
        x_max = int(x + w / 2)
        y_max = int(y + w / 2)

        # Draw the bounding box
        draw.rectangle([x_min, y_min, x_max, y_max], outline="green", width=3)

        # Add a label
        label = f"Egg {confidence:.2f}"
        draw.text((x_min, y_min - 10), label, fill="green")

    # Save the labeled image
    image.save(output_path)

    return egg_count, output_path

class VideoApp:
    def __init__(self, window, window_title):
        self.window = window
        self.window.title(window_title)
        self.video_source = 0

        # Open the video source
        self.vid = cv2.VideoCapture(self.video_source)
        if not self.vid.isOpened():
            raise ValueError("Unable to open video source", self.video_source)

        self.width = self.vid.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.height = self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT)

        # Create a canvas that can fit the above video source size
        self.canvas = Canvas(window, width=self.width, height=self.height)
        self.canvas.pack()

        # Create a second window for the still photo
        self.photo_window = Toplevel(window)
        self.photo_window.title("30 sec Capture")
        self.photo_canvas = Canvas(self.photo_window, width=self.width, height=self.height)
        self.photo_canvas.pack()

        # Egg count label
        self.egg_count_label = Label(self.photo_window, text="Egg count: 0", font=("Helvetica", 14, "bold"))
        self.egg_count_label.pack()

        # Create a third window for the egg count plot
        self.plot_window = Toplevel(window)
        self.plot_window.title("Egg Count Plot")

        self.fig, self.ax = plt.subplots()
        self.ax.set_title("Egg Count Over Time")
        self.ax.set_xlabel("Time (s)")
        self.ax.set_ylabel("Egg Count")

        self.times = []
        self.egg_counts = []

        self.canvas_plot = FigureCanvasTkAgg(self.fig, master=self.plot_window)
        self.canvas_plot.get_tk_widget().pack()

        # Frame for buttons
        button_frame = Frame(window)
        button_frame.pack(side=BOTTOM, fill=X)

        # Button that lets the user pause the video
        self.btn_pause = Button(button_frame, text="Pause", width=10, command=self.pause_video, font=Font(family="Helvetica", size=10, weight="bold"))
        self.btn_pause.pack(side=LEFT, padx=5, pady=5)

        # Button that lets the user play the video
        self.btn_play = Button(button_frame, text="Play", width=10, command=self.play_video, font=Font(family="Helvetica", size=10, weight="bold"))
        self.btn_play.pack(side=LEFT, padx=5, pady=5)

        # Button that lets the user exit the program
        self.btn_stop = Button(button_frame, text="Stop", width=10, command=self.exit_video, font=Font(family="Helvetica", size=10, weight="bold"))
        self.btn_stop.pack(side=LEFT, padx=5, pady=5)

        # Control variables
        self.pause = False
        self.running = True
        self.last_capture_time = time.time()
        self.start_time = time.time()

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

    def update_plot(self):
        self.ax.clear()
        self.ax.plot(self.times, self.egg_counts, marker="o")
        self.ax.set_title("Egg Count Over Time")
        self.ax.set_xlabel("Time (s)")
        self.ax.set_ylabel("Egg Count")
        self.ax.set_xticks(self.times)
        self.ax.set_xticklabels([f"{t} sec" for t in self.times])
        self.canvas_plot.draw()

    def update(self):
        if self.running:
            if not self.pause:
                # Get a frame from the video source
                ret, frame = self.vid.read()
                if ret:
                    # Display the live video frame
                    live_photo = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                    self.live_photo_tk = ImageTk.PhotoImage(image=live_photo)
                    self.canvas.create_image(0, 0, image=self.live_photo_tk, anchor=NW)

                    # Check if 30 seconds have passed to update the second window
                    if time.time() - self.last_capture_time >= 30:
                        self.last_capture_time = time.time()

                        # Save the current frame as a still image in JPG format
                        still_image_path = "temp_still_image.jpg"
                        cv2.imwrite(still_image_path, frame, [int(cv2.IMWRITE_JPEG_QUALITY), 95])

                        # Detect eggs and annotate the image
                        try:
                            egg_count, annotated_path = detect_eggs_with_roboflow(still_image_path)
                            annotated_image = Image.open(annotated_path)
                            annotated_image = annotated_image.resize((int(self.width), int(self.height)), Image.Resampling.LANCZOS)
                            self.annotated_photo_tk = ImageTk.PhotoImage(image=annotated_image)
                            self.photo_canvas.create_image(0, 0, image=self.annotated_photo_tk, anchor=NW)
                            self.egg_count_label.config(text=f"Egg count: {egg_count}")

                            # Update plot data
                            elapsed_time = int((time.time() - self.start_time) // 30 * 30)  # Increment in 30s intervals
                            self.times.append(elapsed_time)
                            self.egg_counts.append(egg_count)
                            self.update_plot()

                        except Exception as e:
                            print(f"Error in egg detection: {e}")

            self.window.after(10, self.update)

    def __del__(self):
        if self.vid.isOpened():
            self.vid.release()

# Create a window and pass it to the VideoApp class
root = Tk()
app = VideoApp(root, "ATLAS Egg Count Camera Feed")
