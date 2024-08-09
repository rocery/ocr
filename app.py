from flask import Flask, render_template, Response
import cv2
import numpy as np
from paddleocr import PaddleOCR, draw_ocr

app = Flask(__name__)

# Initialize PaddleOCR
ocr = PaddleOCR(use_angle_cls=True, lang='en')

def ocrProcess(img):
    result = ocr.ocr(img, cls=True)
    return result

def gen_frames():  
    cap = cv2.VideoCapture(1)  # Use 0 for the default webcam
    frame_count = 0
    last_ocr_result = None  # Store the last OCR result

    while True:
        success, frame = cap.read()
        if not success:
            break
        else:
            frame_count += 1
            
            if frame_count % 10 == 0:  # Perform OCR every 10th frame
                result = ocr.ocr(frame, cls=True)

                if result and len(result) > 0:
                    last_ocr_result = result  # Update the last OCR result

            # Draw the last OCR result on every frame
            if last_ocr_result:
                for line in last_ocr_result:
                    if line:  # Ensure that line is not None
                        for element in line:
                            box, (text, confidence) = element
                            # Extract the top-left and bottom-right points from the box
                            top_left = tuple(map(int, box[0]))
                            bottom_right = tuple(map(int, box[2]))

                            # Draw bounding boxes and text
                            cv2.rectangle(frame, top_left, bottom_right, (0, 255, 0), 2)
                            cv2.putText(frame, f'{text} ({confidence:.2f})', 
                                        (top_left[0], top_left[1] - 10), 
                                        cv2.FONT_HERSHEY_SIMPLEX, 
                                        0.5, (0, 255, 0), 2)

            # Encode the frame and prepare it for streaming
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run()
