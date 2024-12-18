import cv2
import requests
import os
import json
from PIL import Image, ImageDraw

# Roboflow API details
API_URL = "https://detect.roboflow.com"
API_KEY = "mPb0XMaWxTCOE15TbtbX"  # Replace with your actual API key
MODEL_ID = "new-batch/1"  # Replace with your model ID

# Function to detect eggs using the Roboflow API
def detect_eggs_with_roboflow(image_path, output_path):
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
    return egg_count

# Batch process images
def batch_process_images(directory):
    output_data = []
    valid_extensions = ('.jpg', '.jpeg', '.png', '.jfif')  # Supported file extensions
    for filename in os.listdir(directory):
        if filename.startswith("egg") and filename.lower().endswith(valid_extensions):
            input_path = os.path.join(directory, filename)
            output_path = os.path.join(directory, f"{os.path.splitext(filename)[0]}_labelled{os.path.splitext(filename)[1]}")
            try:
                egg_count = detect_eggs_with_roboflow(input_path, output_path)
                output_data.append({"output_file_name": output_path, "egg_count": egg_count})
                print(f"Processed {output_path}, Egg count: {egg_count}")
            except Exception as e:
                print(f"Failed to process {filename}: {str(e)}")
    return output_data

# Save output data to a JSON file
def save_output_data(output_data, output_file):
    with open(output_file, 'w') as f:
        json.dump(output_data, f, indent=4)

# Main execution
if __name__ == "__main__":
    directory = os.path.dirname(os.path.realpath(__file__))  # Use script's directory
    output_data = batch_process_images(directory)
    output_json_path = os.path.join(directory, "output_data.json")
    save_output_data(output_data, output_json_path)
    print("Batch processing complete. Output data saved to 'output_data.json'.")
