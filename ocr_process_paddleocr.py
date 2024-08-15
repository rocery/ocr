import numpy as np
import cv2
from PIL import Image, ImageDraw, ExifTags
import csv
import os
import base64
from io import BytesIO
from paddleocr import PaddleOCR
from script.char_prosess import character_cleaning, character_process

# Initialize PaddleOCR
ocr = PaddleOCR(use_angle_cls=True, lang='en')

# reader = easyocr.Reader(['en', 'id'], gpu=False)
plat = []
filename = []
csv_data_photo_uploaded = 'pic/photo_uploaded.csv'
folder_upload = 'pic/upload/'
folder_ocr = 'pic/ocr/'

def image_preprocess(image, category, time_str, quality=100, compress_level=9):
    # Define the original path to save the image
    global folder_upload
    if not os.path.exists(folder_upload):
        os.makedirs(folder_upload)
    
    global filename
    filename = image.filename
    
    # Open the image with PIL to handle EXIF data and save later
    pil_image = Image.open(image.stream)
    
    # Rotate image if needed based on EXIF orientation
    try:
        for orientation in ExifTags.TAGS.keys():
            if ExifTags.TAGS[orientation] == 'Orientation':
                break
        exif = pil_image._getexif()
        if exif is not None:
            orientation = exif.get(orientation, 1)
            if orientation == 3:
                pil_image = pil_image.rotate(180, expand=True)
            elif orientation == 6:
                pil_image = pil_image.rotate(270, expand=True)
            elif orientation == 8:
                pil_image = pil_image.rotate(90, expand=True)
    except (AttributeError, KeyError, IndexError):
        # Handle cases where the image doesn't have EXIF data
        pass
    
    original_path = os.path.join(folder_upload, filename)
    # Save the image in the appropriate format
    if filename.lower().endswith(('.jpg', '.jpeg')):
        pil_image.save(original_path)
        # pil_image.save(original_path, quality=quality, optimize=True, progressive=True)
    elif filename.lower().endswith('.png'):
        pil_image.save(original_path)
        # pil_image.save(original_path, compress_level=compress_level, optimize=True)

    image = cv2.imread(original_path)
    # image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image = resize_image(image, 700)
    # image = ocr_enhancement(image)
    cv2.imwrite(original_path, image)
    
    # Call to data_photo_uploaded (assuming it's defined elsewhere)
    data_photo_uploaded(csv_data_photo_uploaded, original_path, time_str, category)
    
    return image
        
def data_photo_uploaded(csv_file_path, photo_path, time_upload, category):
    # Check if the file exists; if not, create it and write the header
    if not os.path.exists(csv_file_path):
        with open(csv_file_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['photo_path', 'time_upload', 'category'])
    
    # Append the new row to the CSV file
    with open(csv_file_path, mode='a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([photo_path, time_upload, category])
        
def numpy_to_base64(image_np):
    # Convert NumPy array to PIL Image
    pil_image = Image.fromarray(cv2.cvtColor(image_np, cv2.COLOR_BGR2RGB))
    
    # Save the PIL image to a BytesIO buffer
    buffer = BytesIO()
    pil_image.save(buffer, format="JPEG")
    
    # Encode the image to base64
    img_str = base64.b64encode(buffer.getvalue()).decode()
    
    return f"data:image/jpeg;base64,{img_str}"

def resize_image(image, max_width):
    # Get the current dimensions
    height, width = image.shape[:2]
    
    # Calculate the scaling factor
    scaling_factor = max_width / width
    
    # Calculate the new dimensions while maintaining the aspect ratio
    new_width = max_width
    new_height = int(height * scaling_factor)
    
    # Resize the image
    resized_image = cv2.resize(image, (new_width, new_height))
    
    return resized_image

def predict(frame):
    try:
        # Convert PIL image to numpy array
        open_cv_image = np.array(frame)
        
        # Perform OCR using PaddleOCR
        result = ocr.ocr(open_cv_image, cls=True)
        
        # Check if result is None
        if result is None:
            raise ValueError("OCR result is None. Please check the input image and OCR settings.")

        # Extract the bounding boxes, texts, and confidence scores
        boxes = [line[0] for line in result[0]]
        txts = [line[1][0] for line in result[0]]
        scores = [line[1][1] for line in result[0]]

        reject = [".", ",", "'", "*", "-"]
        global plat
        plat = []
        for data in txts:
            if any(char in data for char in reject) or data[0] == '0':
                continue
            else:
                cleaned_string = character_cleaning(data)
                plat.append(cleaned_string)
            print(f"Data: {data}, cleaned string: {cleaned_string}")

        print(f"Pla: {plat}")
        plat = character_process(plat)
        print(f"OCR: {plat}")

        # Convert boxes to the required format
        boxes = [np.array(box, dtype=np.int32).reshape((-1, 1, 2)) for box in boxes]

        return [(box, txt, score) for box, txt, score in zip(boxes, txts, scores)]
    
    except Exception as e:
        # Handle the error (e.g., log it, return a default value, etc.)
        print(f"Error in OCR prediction: {e}")
        # Return empty results or handle according to your needs
        return False

def fixed_colors():
    """Return a fixed set of colors."""
    return [(0, 0, 255), (255, 0, 0), (0, 0, 127), (63, 0, 127), (4, 38, 82)]

def show_labels(frame, predictions):
    pil_image = Image.fromarray(frame)
    draw = ImageDraw.Draw(pil_image)
    
    colors = fixed_colors()
    
    for box, txt, score in predictions:
        color = colors[np.random.randint(0, len(colors))]
        
        # Draw bounding box (using the points from PaddleOCR)
        cv2.polylines(frame, [box], isClosed=True, color=color, thickness=2)
        
        # Calculate the position to put the text (top-left corner of the bounding box)
        x, y = box[0][0]
        
        # Overlay text and score on the image
        text = f'{txt} ({score:.2f})'
        cv2.putText(frame, text, (x - 3, y - 3), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)
        cv2.putText(frame, text, (x - 3, y - 3), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1, cv2.LINE_AA)
    
    del draw
    opencvimage = np.array(frame)
    global plat
    return opencvimage, plat

def save_image_ocr(image, label, action, time_str, image_format):
    global folder_ocr
    if not os.path.exists(folder_ocr):
        os.makedirs(folder_ocr)
        
    global filename
    folder_path = os.path.join(folder_ocr, filename)
    
    cv2.imwrite(folder_path, image)

def ocr_enhancement(image):
    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Apply Gaussian Blur
    blurred = cv2.GaussianBlur(gray, (3, 3), 0)

    # Enhance the image
    enhanced = cv2.equalizeHist(blurred)

    return enhanced