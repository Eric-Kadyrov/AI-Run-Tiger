import cv2
import requests
from PIL import Image, ImageDraw

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
        y_max = int(y + h / 2)

        # Draw the bounding box
        draw.rectangle([x_min, y_min, x_max, y_max], outline="green", width=3)

        # Add a label
        label = f"Egg {confidence:.2f}"
        draw.text((x_min, y_min - 10), label, fill="green")

    # Save the labeled image
    image.save(output_path)

    return egg_count, output_path

# Input image path
input_image_path = r"C:\Users\User\Downloads\egg4.jfif"  # Replace with your image path
output_image_path = r"C:\Users\User\Downloads\labeled_eggs.jpg"  # Replace with your desired output path

# Detect eggs and count
try:
    egg_count, labeled_image_path = detect_eggs_with_roboflow(input_image_path, output_path=output_image_path)

    # Output results
    print(f"Number of eggs detected: {egg_count}")
    print(f"Labeled image saved at: {labeled_image_path}")
except Exception as e:
    print(str(e))
