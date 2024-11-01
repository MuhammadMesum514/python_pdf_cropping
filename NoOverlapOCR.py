import datetime
import cv2
import numpy as np
import pytesseract
from PIL import Image
import re
import os

def detect_questions(image_path, x_threshold=50):
    """
    Detect questions in an image using question numbers as breakpoints,
    only recognizing numbers that start within a specific x-coordinate range.

    Args:
        image_path: Path to the image file.
        x_threshold: Maximum x-coordinate from the left for a number to be considered a question number.
    Returns:
        List of (x, y, w, h) coordinates for each question and question number sequence.
    """
    # Read the image
    image = cv2.imread(image_path)
    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Get text and bounding boxes using Tesseract
    custom_config = r'--oem 3 --psm 6'
    data = pytesseract.image_to_data(gray, config=custom_config, output_type=pytesseract.Output.DICT)
    
    questions = []
    question_start_indices = []
    question_number_sequence = []
    
    # Find question numbers
    question_pattern = r'\b([1-9]|[1-3][0-9]|40)\.?\b'
    print(data['text'])
    print(data['left'])
    
    for i, text in enumerate(data['text']):
        text = text.strip()
        if re.match(question_pattern, text):
            # Check if x-coordinate is within the threshold
            if data['left'][i] < x_threshold:
                # Remove period and convert to integer
                number_text = re.sub(r'\.', '', text)
                if number_text.isdigit():
                    number = int(number_text)
                    if not question_number_sequence or question_number_sequence[-1] + 1 == number:
                        question_number_sequence.append(number)
                        question_start_indices.append(i)
    
    # Create bounding boxes based on question positions
    for idx, start_idx in enumerate(question_start_indices):
        x = data['left'][start_idx]
        y = data['top'][start_idx]
        
        # Determine the end of the current question block
        end_idx = question_start_indices[idx + 1] if idx + 1 < len(question_start_indices) else len(data['text'])
        
        # Initialize bounding box for the question
        current_question = {
            'x': max(0, x - 10),
            'y': max(0, y - 10),
            'max_x': x + data['width'][start_idx] + 10,
            'max_y': y + data['height'][start_idx] + 10
        }
        
        # Expand the bounding box up to the next question start
        for i in range(start_idx + 1, end_idx):
            if data['conf'][i] > 0:  # Consider only valid text detections
                curr_x = data['left'][i]
                curr_y = data['top'][i]
                curr_w = data['width'][i]
                curr_h = data['height'][i]
                
                current_question['max_x'] = max(current_question['max_x'], curr_x + curr_w + 10)
                current_question['max_y'] = max(current_question['max_y'], curr_y + curr_h + 10)
        
        questions.append(current_question)
    
    # Convert to (x, y, w, h) format and return question number sequence as well
    question_boxes = [(q['x'], q['y'], q['max_x'] - q['x'], q['max_y'] - q['y']) for q in questions]
    return question_boxes, question_number_sequence

def draw_question_boxes(image_path, output_path):
    """
    Draw rectangles around detected questions and save the result.
    """
    image = cv2.imread(image_path)
    questions, question_number_sequence = detect_questions(image_path)
    
    # Draw rectangles with question numbers
    for i, ((x, y, w, h), question_number) in enumerate(zip(questions, question_number_sequence), 1):
        cv2.rectangle(image, (x, y), (x+w, y+h), (0, 255, 0), 2)
        # cv2.putText(image, f"Q{question_number}", (x+5, y+25), 
        #             cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
    
    cv2.imwrite(output_path, image)


def crop_questions(image_path, output_dir):
    """
    Crop individual questions and save them as separate images.
    """
    image = cv2.imread(image_path)
    questions, question_number_sequence = detect_questions(image_path)
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Save each question crop
    for ((x, y, w, h), question_number) in zip(questions, question_number_sequence):
        # Crop question
        x+=45
        question_crop = image[y:y+h, x:x+w]
        
        # Save cropped image
        output_path = f"{output_dir}/question_{question_number}.png"
        cv2.imwrite(output_path, question_crop)
        print(f"Saved question {question_number} with dimensions: {w}x{h}")      
# draw_question_boxes('output_cropped_images/page_15.png', 'output_with_boxes.png')
# crop_questions('output_cropped_images/page_15.png', 'output_cropped_images')

def images_to_pdf(images_folder, output_pdf_path):
    # Generate a timestamp for a unique filename
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    output_pdf_path = f"{output_pdf_path}_{timestamp}.pdf"
    
    # Sort and load images
    images = [Image.open(os.path.join(images_folder, f)) for f in sorted(os.listdir(images_folder)) if f.endswith('.png')]
    
    # Convert images to a single PDF
    if images:
        images[0].save(output_pdf_path, save_all=True, append_images=images[1:])
    print(f"PDF created: {output_pdf_path}")


# loop over the images in the output_cropped_images directory
def processAllImages():
    for filename in os.listdir('output_cropped_images'):
        if filename.endswith('.png'):
            draw_question_boxes(f'output_cropped_images/{filename}', f'marked-image/output_with_boxes_{filename}')
            # crop_questions(f'output_cropped_images/{filename}', 'final-results')
            print(f'Processed: {filename}')
          
    images_to_pdf('marked-image', 'input/9700_s19_12.pdf')  
processAllImages()