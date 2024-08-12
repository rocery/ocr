import easyocr
import numpy as np
import cv2
from PIL import Image, ImageDraw
import re
import os

reader = easyocr.Reader(['en'])
plat = []
os.environ["QT_QPA_PLATFORM"] = "xcb"

def predict(frame):
    result = reader.readtext(frame)
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

def for_image(img):
    image = cv2.imread(img)
    
    predictions = []
    predictions = predict(image)
    frame = show_labels(image, predictions)
    
    cv2.namedWindow('OCR', cv2.WINDOW_NORMAL)
    cv2.imshow('OCR', frame)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    
def for_video():
    process_this_frame = 29
    cap = cv2.VideoCapture(0)
    # cap.open('rtsp://admin:admin123@192.168.10.245:554/Streaming/channels/301', cv2.CAP_FFMPEG)
    predictions = []
    
    while 1 > 0:
        ret, frame = cap.read()
        if ret:
            process_this_frame = process_this_frame + 1
            if process_this_frame % 30 == 0:
                predictions = predict(frame)
            frame = show_labels(frame, predictions)
            # print(plat)
            cv2.namedWindow('OCR', cv2.WINDOW_NORMAL)
            cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
            cv2.imshow('OCR', frame)
            if ord('q') == cv2.waitKey(10):
                cap.release()
                cv2.destroyAllWindows()
                exit(0)

if __name__ == '__main__':
    img_dir = 'pic/6.png'
    for_image(img_dir)
    
    for_video()