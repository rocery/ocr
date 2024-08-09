from paddleocr import PaddleOCR, draw_ocr
import cv2

ocr = PaddleOCR(use_angle_cls=True, lang='en')

image = cv2.imread('contoh.png')
def ocrProcess(img):
    result = ocr.ocr(img, cls=True)
    return result

a = ocrProcess('contoh.png')
# print(a)
print(len(a))
for item in a:
#     bbox, text_data = item
#     # Convert the coordinates to integers
#     bbox = [(int(point[0]), int(point[1])) for point in bbox]
    print(item[3])
#     # Draw a rectangle around the detected text
#     cv2.rectangle(image, bbox[0], bbox[2], color=(0, 255, 0), thickness=2)

# cv2.imshow('Detected Text', image)
# cv2.waitKey(0)
# cv2.destroyAllWindows()