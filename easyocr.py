import easyocr
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont

reader = easyocr.Reader(['en'])

def predict(frame):
    result = reader.readtext(frame)
    
    # Extract bounding boxes, texts, and confidence scores
    boxes = [line[0] for line in result]
    txts = [line[1] for line in result]
    scores = [line[2] for line in result]
    
    return [(box, txt, score) for box, txt, score in zip(boxes, txts, scores) if scores > 0.5]

def show_labels(frame, predictions):
    pil_image = Image.fromarray(frame)
    draw = ImageDraw.Draw(pil_image)
    font = ImageFont.truetype("Ubuntu.ttf", 16)
    
    for box, txt, score in predictions:
        draw.rectangle(((box[0], box[1]), (box[2], box[3])), outline = (0, 0, 255), width = 3)
        text = f'{txt} ({score:.2f})'
        draw.text((box[0] + 5, box[1] - 15), text, fill = (255, 255, 255), font = font)
    
    del draw
    opencvimage = np.array(pil_image)
    return opencvimage

if __name__ == '__main__':
    process_this_frame = 29
    cap = cv2.VideoCapture(1)
    predictions = []
    
    while 1 > 0:
        ret, frame = cap.read()
        if ret:
            process_this_frame = process_this_frame + 1
            if process_this_frame % 30 == 0:
                predictions = predict(frame)
            frame = show_labels(frame, predictions)
            cv2.imshow('Face Recognition', frame)
            if ord('q') == cv2.waitKey(10):
                cap.release()
                cv2.destroyAllWindows()
                exit(0)