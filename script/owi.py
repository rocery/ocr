import torch
from PIL import Image
import numpy as np
import cv2
from transformers import OwlViTProcessor, OwlViTForObjectDetection

# Load the OWL-ViT-2 model and processor
model_name = "google/owlvit-base-patch32"
model = OwlViTForObjectDetection.from_pretrained(model_name)
processor = OwlViTProcessor.from_pretrained(model_name)

# Load the image and convert it to RGB if needed
image_path = "pic/upload/WhatsApp Image 2024-08-14 at 1.30.57 PM.jpeg"
image = Image.open(image_path).convert("RGB")  # Ensure the image is in RGB format

# Define the text prompt with a more specific query
text_queries = ["car license plate", "vehicle registration plate"]

# Preprocess the image and text queries
inputs = processor(images=image, text=text_queries, return_tensors="pt")

# Perform inference
with torch.no_grad():
    outputs = model(**inputs)

# Extract bounding boxes and scores
target_sizes = torch.tensor([image.size[::-1]])
results = processor.post_process(outputs, target_sizes=target_sizes)

# Get the bounding boxes and labels
boxes = results[0]["boxes"]
scores = results[0]["scores"]
labels = results[0]["labels"]

# Filter boxes by a lower score threshold (e.g., 0.3 for more boxes)
threshold = 0.3
filtered_boxes = boxes[scores > threshold]
filtered_labels = labels[scores > threshold]

# Check if any boxes are detected
if len(filtered_boxes) == 0:
    print("No boxes detected with the given threshold.")

# Convert the PIL image to a NumPy array
image_np = np.array(image)

# Draw bounding boxes using OpenCV
for i, box in enumerate(filtered_boxes):
    xmin, ymin, xmax, ymax = map(int, box)
    color = (0, 0, 255)  # Red color in BGR
    thickness = 2
    cv2.rectangle(image_np, (xmin, ymin), (xmax, ymax), color, thickness)

    # Crop the image based on the bounding box
    cropped_image_np = image_np[ymin:ymax, xmin:xmax]

    # Convert cropped image to PIL for saving
    cropped_image_pil = Image.fromarray(cv2.cvtColor(cropped_image_np, cv2.COLOR_BGR2RGB))

    # Save the cropped image
    cropped_image_path = f"cropped_image_{i}.png"
    cropped_image_pil.save(cropped_image_path)
    print(f"Cropped image saved to {cropped_image_path}")

# Save the image with the bounding boxes
output_image_path = "output_image_with_bounding_box.png"
cv2.imwrite(output_image_path, cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR))

print(f"Image with bounding boxes saved to {output_image_path}")
