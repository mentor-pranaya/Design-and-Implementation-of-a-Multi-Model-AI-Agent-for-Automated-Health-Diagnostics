import pytesseract
from PIL import Image
import cv2
import numpy as np
import os

# Tesseract paths
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
os.environ["TESSDATA_PREFIX"] = r"C:\Program Files\Tesseract-OCR\tessdata"

# Load image
img = Image.open("test.png")

# Convert PIL → OpenCV
img_cv = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

# Preprocessing (VERY IMPORTANT)
gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

# OCR with config
custom_config = r"--oem 3 --psm 6"
text = pytesseract.image_to_string(gray, lang="eng", config=custom_config)

print("Extracted Text:")
print(text)
