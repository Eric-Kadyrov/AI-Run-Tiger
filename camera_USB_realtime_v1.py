import cv2

def display_camera_feed():
    # Initialize the video capture object. The argument '0' accesses the default camera.
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: Camera could not be accessed.")
        return

    # Set the window name
    window_name = "ATLAS Egg Count Camera Feed"

    # Create a named window
    cv2.namedWindow(window_name)

    while True:
        # Capture frame-by-frame
        ret, frame = cap.read()

        if not ret:
            print("Failed to grab frame")
            break

        # Display the resulting frame
        cv2.imshow(window_name, frame)

        # Press 'q' on the keyboard to quit the program
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # When everything is done, release the capture
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    display_camera_feed()
