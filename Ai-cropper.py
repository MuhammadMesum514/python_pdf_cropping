import datetime
from PyPDF2 import PdfReader, PdfWriter
from pdf2image import convert_from_path
import os
from PIL import Image
import cv2
import numpy as np
import pytesseract
import re



# VARIABLES

# INPUT_PDF_PATH = 'input.pdf'
INPUT_PDF_FILE = 'input/9700_s19_12.pdf'
OUTPUT_PDF_NAME = 'output-removed-pages.pdf' 
OUTPUT_IMAGES_PATH = 'output_images'
OUTPUT_CROPPED_IMAGES_PATH = 'output_cropped_images'
PAGES_TO_REMOVE = [1, 3, 5]
OUTPUT_IMAGES_DIR = 'output_images'
MARKED_IMAGES_DIR = 'marked-image'
FINAL_IMAGES_DIR = 'final-results'


# step 1
def remove_pages(input_path, output_path, pages_to_remove):
    reader = PdfReader(input_path)
    writer = PdfWriter()
    print(len(reader.pages))
    for page_num in range(len(reader.pages)):
        if page_num + 1 not in pages_to_remove:
            writer.add_page(reader.pages[page_num])

    with open(output_path, 'wb') as output_file:
        writer.write(output_file)

# step 2
def pdf_to_images(pdf_path, output_folder):
    # Convert PDF to a list of images
    images = convert_from_path(pdf_path)
    
    # Ensure the output folder exists
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    # Save each image to the output folder
    for i, image in enumerate(images):
        image_path = os.path.join(output_folder, f'page_{i + 1}.png')
        image.save(image_path, 'PNG')
        print(f'Saved: {image_path}')

# step 3
def crop_images(input_dir, output_dir):
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # get file count in the directory
    file_count = len([name for name in os.listdir(input_dir) if os.path.isfile(os.path.join(input_dir, name))])
    print(f"Total files in the directory: {file_count}")

    # Loop over the images in the input directory
    for filename in os.listdir(input_dir):
        if filename.endswith('.jpg') or filename.endswith('.png'):
            img_path = os.path.join(input_dir, filename)
            im = Image.open(img_path)
            
            left = 95
            top = 130   
            right = 1630
            bottom = 0
            if filename == f"page_{file_count}.png":
                bottom = 1750
            else:
                bottom = 2160
            print(f"Processing {filename} with dimensions: {left}, {top}, {right}, {bottom}")
            im1 = im.crop((left, top, right, bottom))
            
            # Save the cropped image to the output directory
            cropped_img_path = os.path.join(output_dir, filename)
            im1.save(cropped_img_path)
            
            
# step 4
def detect_questions(image_path):
    """
    Detect questions in an image using question numbers as breakpoints.
    
    Args:
        image_path: Path to the image file.
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
    
    for i, text in enumerate(data['text']):
        text = text.strip()
        if re.match(question_pattern, text):
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

# step 5
def processAllImages(cropped_images_directory,marked_images_directory, final_image_directory):
    for filename in os.listdir('output_cropped_images'):
        if filename.endswith('.png'):
            draw_question_boxes(f'{cropped_images_directory}/{filename}', f'{marked_images_directory}/output_with_boxes_{filename}')
            crop_questions(f'{cropped_images_directory}/{filename}', f'{final_image_directory}')
            print(f'Processed: {filename}')


# step 6: convert marked images back into pdf and save with timestamp 
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


# main function 

def processPDF():
    # step 1: remove pages
    remove_pages(INPUT_PDF_FILE, OUTPUT_PDF_NAME,PAGES_TO_REMOVE)
    
    # step 2: pdf to images
    pdf_to_images(OUTPUT_PDF_NAME, OUTPUT_IMAGES_PATH)
    
    # step 3: crop images
    crop_images(OUTPUT_IMAGES_PATH, OUTPUT_CROPPED_IMAGES_PATH)
    
    # step 4: process images
    processAllImages(OUTPUT_CROPPED_IMAGES_PATH, MARKED_IMAGES_DIR, FINAL_IMAGES_DIR)
    
    # step 5: convert images to pdf
    images_to_pdf(MARKED_IMAGES_DIR, INPUT_PDF_FILE)


processPDF()