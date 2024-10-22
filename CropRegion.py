# import pytesseract
# from pytesseract import Output
# from PIL import Image
# import cv2
# import re

# # Load image using OpenCV
# image_path = 'testImg.jpg'  # Update to your image path
# image = cv2.imread(image_path)

# # Convert to RGB (OpenCV uses BGR format by default)
# image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

# # Perform OCR with bounding box output
# d = pytesseract.image_to_data(image_rgb, output_type=Output.DICT)

# # find question number using regex pattern such that
#     # it start wit a number and dont have an characters before it on same line
#     # it has a string after around a tab space or more
#     # it shouldn't be confused with page number which is in center of page  at the header
#     # and question number should not be in the middle of the page
# pattern = r'\b\d+\b\s+(?:(?=\t)|(?<=\s))(?:[^\t\s]+\s+){2,}'
# question_numbers = [text for text in d['text'] if re.match(pattern, text)]
# print(question_numbers)
    
    

# # Extract bounding box and text data
# n_boxes = len(d['text'])

# # Function to crop a portion of the image
# def crop_image(image, x, y, w, h, output_name):
#     cropped_img = image[y:y+h, x:x+w]
#     cv2.imwrite(output_name, cropped_img)

# # Variables to track question areas
# question_areas = []

# # Iterate through detected text
# for i in range(n_boxes):
#     if int(d['conf'][i]) > 60:  # Confidence threshold for accurate text
#         text = d['text'][i]
#         if text.strip().isdigit():  # Check if it's a question number (like "3", "4", "5")
#             x, y, w, h = d['left'][i], d['top'][i], d['width'][i], d['height'][i]
#             question_areas.append((x, y, w, h))

# # Now that we have the bounding boxes for question numbers, let's crop the regions
# for i in range(len(question_areas) - 1):
#     x1, y1, w1, h1 = question_areas[i]  # Start of the current question
#     x2, y2, w2, h2 = question_areas[i + 1]  # Start of the next question

#     # Crop between the current question and the next one
#     crop_image(image, 0, y1, image.shape[1], y2 - y1, f'question_{i + 1}.jpg')

# # For the last question, crop till the bottom of the image
# x_last, y_last, w_last, h_last = question_areas[-1]
# crop_image(image, 0, y_last, image.shape[1], image.shape[0] - y_last, f'question_{len(question_areas)}.jpg')

# print("Questions cropped and saved successfully!")



import pytesseract
from pytesseract import Output
from PIL import Image
import cv2
import re

# Load image using OpenCV
image_path = 'testImg.jpg'  # Update to your image path
image = cv2.imread(image_path)

# Convert to RGB (OpenCV uses BGR format by default)
image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

# Perform OCR with bounding box output
d = pytesseract.image_to_data(image_rgb, output_type=Output.DICT)

print (d['text'])
# Variables to store detected question numbers
question_numbers = []
min_question_line_height = 0.05 * image.shape[0]  # Set a threshold for vertical position to ignore headers

# Iterate through detected text and check for potential question numbers
for i in range(len(d['text'])):
    if int(d['conf'][i]) > 60:  # Only consider text with confidence above 60
        text = d['text'][i].strip()
        x, y, w, h = d['left'][i], d['top'][i], d['width'][i], d['height'][i]
        
        # Skip page numbers based on position (usually found at the top)
        if y < min_question_line_height:
            continue
        
        # Match a digit at the start of the line followed by a sentence (likely a question number)
        if re.match(r'^\d+\s+.+', text):
            question_numbers.append((text, (x, y, w, h)))

# Print the detected question numbers
for q_number, (x, y, w, h) in question_numbers:
    print(f"Detected question: '{q_number}' at position (x={x}, y={y}, w={w}, h={h})")

