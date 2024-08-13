import easyocr
import numpy as np
import cv2
from PIL import Image, ImageDraw, ExifTags
import re
import csv
import os
import time
import base64
from io import BytesIO

reader = easyocr.Reader(['en', 'id'], gpu=False)
plat = []
csv_data_photo_uploaded = 'pic/photo_uploaded.csv'
folder_path = 'pic/upload/'

def image_preprocess(image, category, time_str, quality=50, compress_level=9):
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

    # Convert the PIL image to a NumPy array for OpenCV processing
    image = np.array(pil_image)
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    
    # Define the original path to save the image
    global folder_path
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    
    original_path = os.path.join(folder_path, filename)

    # Save the image in the appropriate format
    if filename.lower().endswith(('.jpg', '.jpeg')):
        pil_image.save(original_path, quality=quality, optimize=True, progressive=True)
    elif filename.lower().endswith('.png'):
        pil_image.save(original_path, compress_level=compress_level, optimize=True)
    
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


## OCR TIMEa




def save_image(images, folder_path, quality=40, compress_level=4):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    
    for image in images:
        img = Image.open(image)
        # Handle image rotation based on EXIF orientation
        try:
            for orientation in ExifTags.TAGS.keys():
                if ExifTags.TAGS[orientation] == 'Orientation':
                    break
            exif = img._getexif()
            if exif is not None:
                orientation = exif.get(orientation, 1)
                if orientation == 3:
                    img = img.rotate(180, expand=True)
                elif orientation == 6:
                    img = img.rotate(270, expand=True)
                elif orientation == 8:
                    img = img.rotate(90, expand=True)
        except (AttributeError, KeyError, IndexError):
            # Cases: image don't have getexif
            pass
        
        # Save original image with reduced quality
        original_path = os.path.join(folder_path, f"o_{image.filename}")
        if image.filename.lower().endswith(('.jpg', '.jpeg')):
            img.save(original_path, quality=quality, optimize=True)
        elif image.filename.lower().endswith('.png'):
            img.save(original_path, compress_level=compress_level, optimize=True)
        
        time_str = time.strftime("%d-%m-%Y %H:%M:%S", time.localtime())
        data_photo_uploaded(csv_data_photo_uploaded, original_path, time_str)
        
        # Create and save mirrored image with reduced quality
        mirrored_img = img.transpose(Image.FLIP_LEFT_RIGHT)
        mirrored_path = os.path.join(folder_path, f"m_{image.filename}")
        if image.filename.lower().endswith(('.jpg', '.jpeg')):
            mirrored_img.save(mirrored_path, quality=quality, optimize=True)
        elif image.filename.lower().endswith('.png'):
            mirrored_img.save(mirrored_path, compress_level=compress_level, optimize=True)
        
        time_str = time.strftime("%d-%m-%Y %H:%M:%S", time.localtime())
        data_photo_uploaded(csv_data_photo_uploaded, mirrored_path, time_str)




def preprocess_image(images, quality=10, compress_level=1):
    # if not os.path.exists(folder_path):
    #     os.makedirs(folder_path)
    
    img = Image.open(images)
    # Handle image rotation based on EXIF orientation
    try:
        for orientation in ExifTags.TAGS.keys():
            if ExifTags.TAGS[orientation] == 'Orientation':
                break
        exif = img._getexif()
        if exif is not None:
            orientation = exif.get(orientation, 1)
            if orientation == 3:
                img = img.rotate(180, expand=True)
            elif orientation == 6:
                img = img.rotate(270, expand=True)
            elif orientation == 8:
                img = img.rotate(90, expand=True)
    except (AttributeError, KeyError, IndexError):
        # Cases: image don't have getexif
        pass
    
    return img

def predict(frame):
    pil_image = Image.open(frame)

    # Konversi PIL image ke numpy array
    open_cv_image = np.array(pil_image)

    # Convert RGB to BGR (jika diperlukan oleh OpenCV, tetapi tidak perlu jika menggunakan EasyOCR)
    open_cv_image = open_cv_image[:, :, ::-1].copy()
    
    open_cv_image = cv2.resize(open_cv_image, None, fx=0.1, fy=0.1, interpolation=cv2.INTER_CUBIC)
    
    result = reader.readtext(open_cv_image)
    boxes = [line[0] for line in result]
    txts = [line[1] for line in result]
    scores = [line[2] for line in result]
    
    reject = [".", ","]
    global plat
    plat = []
    for data in txts:
        if any(char in data for char in reject):
            continue
        else:
            cleaned_string = re.sub(r'[^\w\s\n]', '', data)
            cleaned_string = cleaned_string.upper()
            plat.append(cleaned_string)
        print("Data: {}, cleaned string: {}".format(data, cleaned_string))
    
    print(plat)
        
    boxes = [np.array(box, dtype=np.int32).reshape((-1, 1, 2)) for box in boxes]
    
    return [(box, txt, score) for box, txt, score in zip(boxes, txts, scores)]

def show_labels(frame, predictions):
    pil_image = Image.fromarray(frame)
    draw = ImageDraw.Draw(pil_image)
    
    for box, txt, score in predictions:
        # Draw bounding box
        img = cv2.polylines(frame, [box], isClosed=True, color=(0, 255, 0), thickness=2)
        
        # Calculate the position to put the text (top-left corner of the bounding box)
        x, y = box[0][0]
        
        # Overlay text and score on the image
        text = f'{txt} ({score:.2f})'
        img = cv2.putText(frame, text, (x + 5, y + 15), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 255), 1, cv2.LINE_AA)
    
    del draw
    opencvimage = np.array(frame)
    return opencvimage

def show_label(frame, predictions):
    for box, txt, score in predictions:
        # Draw bounding box
        frame = cv2.polylines(frame, [np.array(box)], isClosed=True, color=(0, 255, 0), thickness=2)
        
        # Calculate the position to put the text (top-left corner of the bounding box)
        x, y = box[0]
        
        # Overlay text and score on the image
        text = f'{txt} ({score:.2f})'
        frame = cv2.putText(frame, text, (x + 5, y + 15), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 255), 1, cv2.LINE_AA)
    
    return frame

# def generate_image(frame):
#     predictions = predict(frame)
#     frame_with_labels = show_labels(frame, predictions)
#     # Konversi frame ke JPEG
#     _, jpeg = cv2.imencode('.jpg', frame_with_labels)

#     # Encode ke base64
#     jpeg_base64 = base64.b64encode(jpeg).decode('utf-8')

#     return jpeg_base64






# def for_image(img):
#     image = cv2.imread(img)
#     gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
#     predictions = []
#     predictions = predict(gray_image)
#     frame = show_labels(image, predictions)
    
#     cv2.namedWindow('OCR', cv2.WINDOW_NORMAL)
#     cv2.imshow('OCR', frame)
    
#     cv2.waitKey(0)
#     cv2.destroyAllWindows()
    
# def for_video():
#     process_this_frame = 29
#     cap = cv2.VideoCapture()
#     cap.open('rtsp://admin:admin123@192.168.10.245:554/Streaming/channels/301', cv2.CAP_FFMPEG)
#     predictions = []
    
#     while 1 > 0:
#         ret, frame = cap.read()
#         if ret:
#             process_this_frame = process_this_frame + 1
#             if process_this_frame % 30 == 0:
#                 predictions = predict(frame)
#             # frame = show_labels(frame, predictions)
#             # # print(plat)
#             cv2.namedWindow('OCR', cv2.WINDOW_NORMAL)
#             cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
#             cv2.imshow('OCR', frame)
#             if cv2.waitKey(1) & 0xFF == ord('q'):
#                 cap.release()
#                 cv2.destroyAllWindows()
#                 exit(0)