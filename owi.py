import torch
from PIL import Image
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from transformers import OwlViTProcessor, OwlViTForObjectDetection

# Load the OWL-ViT-2 model and processor
model_name = "google/owlvit-base-patch32"
model = OwlViTForObjectDetection.from_pretrained(model_name)
processor = OwlViTProcessor.from_pretrained(model_name)

# Load the image and convert it to RGB if needed
image_path = "pic/upload/WhatsApp Image 2024-08-14 at 1.30.57 PM (2).jpeg"
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

# # For debugging: print the bounding boxes and scores
# for i, (box, score) in enumerate(zip(boxes, scores)):
#     print(f"Box {i}: {box.tolist()}, Score: {score.item()}")

# Filter boxes by a lower score threshold (e.g., 0.3 for more boxes)
threshold = 0.3
filtered_boxes = boxes[scores > threshold]
filtered_labels = labels[scores > threshold]

# Check if any boxes are detected
if len(filtered_boxes) == 0:
    print("No boxes detected with the given threshold.")

# Plot and save the image with bounding boxes
fig, ax = plt.subplots(1)
ax.imshow(image)

for box in filtered_boxes:
    xmin, ymin, xmax, ymax = box
    width, height = xmax - xmin, ymax - ymin

    # Create a rectangle patch
    rect = patches.Rectangle((xmin, ymin), width, height, linewidth=2, edgecolor='r', facecolor='none')
    ax.add_patch(rect)

# Save the image with the bounding box
output_image_path = "output_image_with_bounding_box.png"
plt.savefig(output_image_path)

print(f"Image saved to {output_image_path}")
