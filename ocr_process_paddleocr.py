import numpy as np
import cv2
from PIL import Image, ImageDraw, ExifTags
import csv
import os
import base64
from io import BytesIO
from paddleocr import PaddleOCR
from script.char_prosess import character_cleaning, character_process
from datetime import datetime

ocr = PaddleOCR(enable_mkldnn=False, use_tensorrt=False, use_angle_cls=False, use_gpu=False, lang="en", use_direction_classify=True)
plat = []
filename = []
csv_data_photo_uploaded = 'pic/photo_uploaded.csv'
folder_upload = 'pic/upload/'
folder_ocr = 'pic/ocr/'
csv_all_data_ocr = 'pic/ocr/all_data_ocr.csv'

def image_preprocess(image, category, time_str, quality=100, compress_level=9):
    # Define the original path to save the image
    global folder_upload
    if not os.path.exists(folder_upload):
        os.makedirs(folder_upload)
    
    # Extract the file extension
    file_extension = os.path.splitext(image.filename)[1]
    
    # Construct the new filename with time_str
    global filename
    filename = f"{os.path.splitext(image.filename)[0]}-{time_str}{file_extension}"
    
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
    # image = resize_image(image, 1500)
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
        
def data_photo_ocr(csv_file_path, photo_path, time_ocr, text_ocr, category):
    # Check if the file exists; if not, create it and write the header
    if not os.path.exists(csv_file_path):
        with open(csv_file_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['photo_path', 'ocr', 'category', 'time_ocr'])
    # Append the new row to the CSV file
    with open(csv_file_path, mode='a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([photo_path, text_ocr, category, time_ocr])
    
    # Check if the file exists; if not, create it and write the header
    if not os.path.exists(csv_all_data_ocr):
        with open(csv_all_data_ocr, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['ocr', 'category', 'time_ocr'])
    # Append the new row to the CSV file
    with open(csv_all_data_ocr, mode='a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([text_ocr, category, time_ocr])

def data_photo_failed(photo_path, ocr, time_upload, category):
    # Check if the file exists; if not, create it and write the header
    if not os.path.exists('pic/photo_failed.csv'):
        with open('pic/photo_failed.csv', mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['photo_path', 'ocr', 'category', 'time_ocr'])
    
    # Append the new row to the CSV file
    with open('pic/photo_failed.csv', mode='a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([photo_path, ocr, time_upload, category])
        
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
        # Perform OCR using PaddleOCR
        try:
            result = OCR.ocr(frame, cls=True) 
        except:
            OCR = PaddleOCR(enable_mkldnn=False, use_tensorrt=False, use_angle_cls=False, use_gpu=False, lang="en", use_direction_classify=True)
            result = OCR.ocr(frame, cls=False)
        
        # Check if result is None
        if result is None:
            raise ValueError("OCR result is None. Please check the input image and OCR settings.")

        # Sort the OCR results based on the x-coordinate of the top-left corner (left to right)
        sorted_result = sorted(result[0], key=lambda x: x[0][0][0])

        # Extract the bounding boxes, texts, and confidence scores from the sorted result
        boxes = [line[0] for line in sorted_result]
        txts = [line[1][0] for line in sorted_result]
        scores = [line[1][1] for line in sorted_result]

        reject = []
        global plat
        plat = []
        for data in txts:
            if any(char in data for char in reject) or data[0] == '0':
                continue
            else:
                cleaned_string = character_cleaning(data)
                plat.append(cleaned_string)
            print(f"Data: {data}, cleaned string: {cleaned_string}")

        print(f"Plat: {plat}")
        plat = character_process(plat)
        print(f"OCR: {plat}")

        # Convert boxes to the required format
        boxes = [np.array(box, dtype=np.int32).reshape((-1, 1, 2)) for box in boxes]

        return [(box, txt, score) for box, txt, score in zip(boxes, txts, scores)]

    except Exception as e:
        print(f"Error during OCR: {e}")
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
    # global plat
    return opencvimage, plat

def save_image_ocr(image, file_name, folder_date, time_input, label, action):
    csv = f"{folder_date}.csv"
    folder_path = os.path.join(folder_ocr, folder_date)
    csv_path = os.path.join(folder_ocr, csv)
    
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        
    file_path = os.path.join(folder_path, file_name)
    
    data_photo_ocr(csv_path, file_path, time_input, label, action)
    
    cv2.imwrite(file_path, image)

def ocr_enhancement(image):
    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Apply Gaussian Blur
    blurred = cv2.GaussianBlur(gray, (3, 3), 0)

    # Enhance the image
    enhanced = cv2.equalizeHist(blurred)

    return enhanced

def read_data_csv():
    data = []
    file_path = 'pic/ocr/all_data_ocr.csv'

    # Membaca data dari file ocr.csv
    with open(file_path, newline='') as csvfile:
        csvreader = csv.reader(csvfile, delimiter=',')
        header = next(csvreader)  # Skip the header row
        for row in csvreader:
            data.append(row)
            
    # Ambil 100 data terbaru
    recent_data = data[-100:]
    
    # Tambahkan nomor urut secara menurun
    numbered_data = [[i + 1, *row] for i, row in enumerate(recent_data[::-1])]

    return numbered_data