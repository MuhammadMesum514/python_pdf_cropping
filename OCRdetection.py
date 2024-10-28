# import cv2
# import numpy as np
# import pytesseract
# from PIL import Image
# import re

# def detect_questions(image_path):
#     """
#     Detect questions in an image and return their bounding boxes.
    
#     Args:
#         image_path: Path to the image file
#     Returns:
#         List of (x, y, w, h) coordinates for each question
#     """
#     # Read the image
#     image = cv2.imread(image_path)
#     # Convert to grayscale
#     gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
#     # Get text and bounding boxes using Tesseract
#     custom_config = r'--oem 3 --psm 6'
#     data = pytesseract.image_to_data(gray, config=custom_config, output_type=pytesseract.Output.DICT)
    
#     questions = []
#     current_question = None
#     previous_text = ""
#     text_buffer = []
    
#     # Process each detected text element
#     for i in range(len(data['text'])):
#         text = data['text'][i].strip()
#         print(text)
#         # Combine current text with previous text to handle split numbers
#         combined_text = f"{previous_text} {text}".strip()
        
#         # Check if text matches question number pattern (e.g., "1", "1.", "1 ", "1. ")
#         # followed by 2-3 spaces before actual question text
#         question_pattern = r'^(\d+\.?\s{0,3})$'
        
#         if re.match(question_pattern, text) or re.match(question_pattern, combined_text):
#             # If we found a new question number
#             if current_question is not None:
#                 questions.append(current_question)
            
#             # Start new question bounding box
#             x = data['left'][i]
#             y = data['top'][i]
#             current_question = {
#                 'number': int(re.match(r'^(\d+)', text or combined_text).group(1)),
#                 'x': x,
#                 'y': y,
#                 'max_x': x + data['width'][i],
#                 'max_y': y + data['height'][i]
#             }
#             text_buffer = []
#         elif current_question is not None:
#             # Update bounding box for current question
#             x = data['left'][i]
#             y = data['top'][i]
#             current_question['max_x'] = max(current_question['max_x'], x + data['width'][i])
#             current_question['max_y'] = max(current_question['max_y'], y + data['height'][i])
#             text_buffer.append(text)
            
#             # Check if we've found the next question number in the text
#             full_text = ' '.join(text_buffer)
#             if re.search(r'\s\d+\.?\s{0,3}$', full_text):
#                 questions.append(current_question)
#                 current_question = None
#                 text_buffer = []
        
#         previous_text = text
    
#     # Add the last question
#     if current_question is not None:
#         questions.append(current_question)
    
#     # Convert to list of (x, y, w, h) format
#     return [(q['x'], q['y'], 
#              q['max_x'] - q['x'], 
#              q['max_y'] - q['y']) for q in questions]

# def draw_question_boxes(image_path, output_path):
#     """
#     Draw rectangles around detected questions and save the result.
    
#     Args:
#         image_path: Path to input image
#         output_path: Path to save the output image
#     """
#     # Read image
#     image = cv2.imread(image_path)
    
#     # Detect questions
#     questions = detect_questions(image_path)
    
#     # Draw rectangles
#     for (x, y, w, h) in questions:
#         cv2.rectangle(image, (x-10, y-10), (x+w+10, y+h+10), (0, 255, 0), 2)
#         myImage = Image.open(image_path)
#         # crop image as per rectangle dimensions
#         cropped = myImage.crop((x+12, y-10, x+w+10, y+h+10))
#         # save image 
#         cropped.save('output_cropped_images/' + 'question_' + str(questions.index((x, y, w, h))) + '.png')
#     # Save result
#     cv2.imwrite(output_path, image)
    
# def crop_questions(image_path, output_dir):
#     """
#     Crop individual questions and save them as separate images.
    
#     Args:
#         image_path: Path to input image
#         output_dir: Directory to save cropped images
#     """
#     # Read image
#     image = cv2.imread(image_path)
    
#     # Detect questions
#     questions = detect_questions(image_path)
    
#     # Crop and save each question
#     for i, (x, y, w, h) in enumerate(questions, 1):
#         # Add padding
#         x, y = max(0, x-10), max(0, y-10)
#         w, h = w+20, h+20
        
#         # Crop question
#         question = image[y:y+h, x:x+w]
        
#         # Save cropped image
#         output_path = f"{output_dir}/question_{i}_boxed.png"
#         cv2.imwrite(output_path, question)
        
        
# # draw_question_boxes('output_cropped_images/page_2.png', 'output_with_boxes.png')
# crop_questions('output_cropped_images/page_2.png', 'output_cropped_images')



import cv2
import numpy as np
import pytesseract
from PIL import Image
import re

def detect_questions(image_path):
    """
    Detect questions in an image and return their non-overlapping bounding boxes.
    
    Args:
        image_path: Path to the image file
    Returns:
        List of (x, y, w, h) coordinates for each question
    """
    # Read the image
    image = cv2.imread(image_path)
    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Get text and bounding boxes using Tesseract
    custom_config = r'--oem 3 --psm 6'
    data = pytesseract.image_to_data(gray, config=custom_config, output_type=pytesseract.Output.DICT)
    
    questions = []
    current_question = None
    previous_text = ""
    text_buffer = []
    min_vertical_gap = 100  # Minimum vertical gap between questions
    
    # First pass: Detect question boundaries
    for i in range(len(data['text'])):
        text = data['text'][i].strip()
        combined_text = f"{previous_text} {text}".strip()
        
        # Check if text matches question number pattern
        question_pattern = r'^(\d+\.?\s{0,3})$'
        
        if re.match(question_pattern, text) or re.match(question_pattern, combined_text):
            # If we found a new question number
            if current_question is not None:
                # Ensure minimum height for the current question
                min_height = 50  # Minimum height in pixels
                if current_question['max_y'] - current_question['y'] < min_height:
                    current_question['max_y'] = current_question['y'] + min_height
                questions.append(current_question)
            
            # Start new question bounding box
            x = data['left'][i]
            y = data['top'][i]
            current_question = {
                'number': int(re.match(r'^(\d+)', text or combined_text).group(1)),
                'x': max(0, x - 10),  # Add padding and ensure non-negative
                'y': max(0, y - 10),
                'max_x': x + data['width'][i] + 10,
                'max_y': y + data['height'][i] + 10
            }
            text_buffer = []
        elif current_question is not None:
            # Update bounding box for current question
            x = data['left'][i]
            y = data['top'][i]
            current_question['max_x'] = max(current_question['max_x'], x + data['width'][i] + 10)
            current_question['max_y'] = max(current_question['max_y'], y + data['height'][i] + 10)
            
        previous_text = text
    
    # Add the last question
    if current_question is not None:
        questions.append(current_question)
    
    # Second pass: Adjust boundaries to prevent overlaps
    for i in range(len(questions)-1):
        current = questions[i]
        next_q = questions[i+1]
        
        # If there's overlap in vertical direction
        if current['max_y'] + min_vertical_gap > next_q['y']:
            # Calculate middle point between questions
            mid_point = (current['max_y'] + next_q['y']) // 2
            
            # Adjust boundaries
            current['max_y'] = mid_point - (min_vertical_gap // 2)
            next_q['y'] = mid_point + (min_vertical_gap // 2)
    
    # Convert to list of (x, y, w, h) format and ensure non-negative values
    return [(
        max(0, q['x']), 
        max(0, q['y']), 
        max(1, q['max_x'] - q['x']), 
        max(1, q['max_y'] - q['y'])
    ) for q in questions]

def draw_question_boxes(image_path, output_path):
    """
    Draw rectangles around detected questions and save the result.
    """
    image = cv2.imread(image_path)
    questions = detect_questions(image_path)
    
    # Draw rectangles
    for i, (x, y, w, h) in enumerate(questions, 1):
        cv2.rectangle(image, (x, y), (x+w, y+h), (0, 255, 0), 2)
        cv2.putText(image, f"Q{i}", (x+5, y+25), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
    
    cv2.imwrite(output_path, image)

def crop_questions(image_path, output_dir):
    """
    Crop individual questions and save them as separate images.
    """
    image = cv2.imread(image_path)
    questions = detect_questions(image_path)
    
    for i, (x, y, w, h) in enumerate(questions, 1):
        # Crop question
        question = image[y:y+h+40, x:x+w]
        
        # Save cropped image
        output_path = f"{output_dir}/question_{i}.png"
        cv2.imwrite(output_path, question)
        
        print(f"Saved question {i} with dimensions: {w}x{h}")
        
        
draw_question_boxes('output_cropped_images/page_1.png', 'output_with_boxes.png')
crop_questions('output_cropped_images/page_1.png', 'output_cropped_images')
