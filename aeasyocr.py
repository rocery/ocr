import easyocr
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont

reader = easyocr.Reader(['en'])
plat = []

def predict(frame):
    result = reader.readtext(frame)
    global plat
    reject = [" ", ".", ",", ":", "-", "/"]
    
    # Extract bounding boxes, texts, and confidence scores
    boxes = [line[0] for line in result]
    txts = [line[1] for line in result]
    scores = [line[2] for line in result]
    
    plat = []
    for data in txts:
        if any(char in data for char in reject):
            continue  # Skip this data if it contains any of the reject characters
        else:
            plat.append(data)
    
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

if __name__ == '__main__':
    process_this_frame = 29
    cap = cv2.VideoCapture(0)
    predictions = []
    
    while 1 > 0:
        ret, frame = cap.read()
        if ret:
            process_this_frame = process_this_frame + 1
            if process_this_frame % 30 == 0:
                predictions = predict(frame)
            frame = show_labels(frame, predictions)
            print(plat)
            cv2.imshow('Face Recognition', frame)
            print(plat)
            if ord('q') == cv2.waitKey(10):
                cap.release()
                cv2.destroyAllWindows()
                exit(0)