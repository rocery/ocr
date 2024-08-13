import cv2
import numpy as np
import easyocr

reader = easyocr.Reader(['en'])
image = cv2.imread('pic/4.jpg')
# image = cv2.resize(image, None, fx=0.1, fy=0.1, interpolation=cv2.INTER_CUBIC)

# result = ocr.ocr(image, cls=True)
# Perform OCR on the image
result = reader.readtext(image)

# Extract bounding boxes, texts, and confidence scores
boxes = [line[0] for line in result]
txts = [line[1] for line in result]
scores = [line[2] for line in result]

print(len(txts))

plat = []
reject = [" ", "."]

for data in txts:
    # plat.append(data)
    if any(char in data for char in reject):
        continue  # Skip this data if it contains any of the reject characters
    else:
        plat.append(data)

print(plat)

# Convert the bounding boxes to a format suitable for cv2.polylines
boxes = [np.array(box, dtype=np.int32).reshape((-1, 1, 2)) for box in boxes]

# Draw the bounding boxes and text on the image
for box, txt, score in zip(boxes, txts, scores):
    # Draw bounding box
    img = cv2.polylines(image, [box], isClosed=True, color=(0, 255, 0), thickness=2)
    
    # Calculate the position to put the text (top-left corner of the bounding box)
    x, y = box[0][0]
    
    # Overlay text and score on the image
    text = f'{txt} ({score:.2f})'
    img = cv2.putText(image, text, (x + 5, y + 15), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 255), 1, cv2.LINE_AA)

# Display the image with bounding boxes and text
cv2.imshow('Detected Boxes and Text', image)
cv2.waitKey(0)
cv2.destroyAllWindows()