import cv2
import pytesseract
import json
from PIL import Image
import fitz  # PyMuPDF

def extract_mcq_coordinates(image_path):
    # Read the image
    image = cv2.imread(image_path)
    
    # Perform OCR
    ocr_data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
    
    questions = []
    current_question = None
    
    # Iterate through the OCR results
    for i, text in enumerate(ocr_data['text']):
        if text.strip() and text[0].isdigit() and text[-1] == '.':
            # This looks like the start of a new question
            if current_question:
                questions.append(current_question)
            
            current_question = {
                'number': text,
                'top': ocr_data['top'][i],
                'left': ocr_data['left'][i],
                'bottom': ocr_data['top'][i] + ocr_data['height'][i],
                'right': ocr_data['left'][i] + ocr_data['width'][i]
            }
        elif current_question:
            # Update the bounding box of the current question
            current_question['bottom'] = max(current_question['bottom'], ocr_data['top'][i] + ocr_data['height'][i])
            current_question['right'] = max(current_question['right'], ocr_data['left'][i] + ocr_data['width'][i])
    
    # Add the last question
    if current_question:
        questions.append(current_question)
    
    return questions

def crop_pdf(input_pdf_path, output_pdf_path, page_number, crop_rect):
    """
    Crop a specific area from a PDF based on provided coordinates.

    :param input_pdf_path: Path to the input PDF file.
    :param output_pdf_path: Path to save the cropped PDF file.
    :param page_number: Page number to crop (0-indexed).
    :param crop_rect: Tuple of coordinates (x0, y0, x1, y1) defining the crop area.
    """
    # Open the PDF file
    pdf_document = fitz.open(input_pdf_path)
    
    # Select the page
    page = pdf_document.load_page(page_number)
    
    # Define the crop area
    rect = fitz.Rect(crop_rect)
    
    # Crop the page
    page.set_cropbox(rect)
    
    # Save the cropped PDF to a new file
    pdf_document.save(output_pdf_path)
    pdf_document.close()

# Example usage for extracting MCQ coordinates
image_path = 'path/to/your/document/image.png'
mcq_coordinates = extract_mcq_coordinates(image_path)

# Save coordinates to a JSON file
with open('mcq_coordinates.json', 'w') as f:
    json.dump(mcq_coordinates, f, indent=2)

print(f"Coordinates for {len(mcq_coordinates)} questions have been extracted and saved.")

# Example usage for cropping PDF
input_pdf_path = "input.pdf"
output_pdf_path = "cropped_output.pdf"
page_number = 0  # First page
crop_rect = (100, 100, 400, 400)  # Coordinates (x0, y0, x1, y1)

crop_pdf(input_pdf_path, output_pdf_path, page_number, crop_rect)