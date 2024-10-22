from pdf2image import convert_from_path
import pytesseract
from PIL import Image

# Retry loading the PDF and converting to images
pdf_path = "5054_s22_qp_11.pdf"
images = convert_from_path(pdf_path, dpi=300)

# Initialize list to hold paths of cropped question images
cropped_question_paths = []

# Define function to save image and add to paths
def save_cropped_image(img, index):
    save_path = f"./output/question_{index}.png"
    img.save(save_path)
    cropped_question_paths.append(save_path)

# Process each page to crop each question
for page_num, image in enumerate(images, start=1):
    # Convert to grayscale for OCR
    gray_image = image.convert("L")
    
    # Use OCR to find question text
    text = pytesseract.image_to_string(gray_image)
    print(text)
    
    # Split by questions (assuming questions start with numbers)
    questions = text.split("\n\n")
    question_starts = [i for i, q in enumerate(questions) if q.strip().startswith(tuple(str(n) for n in range(1, 41)))]

    # Crop each question based on approximate location
    for idx, start in enumerate(question_starts):
        question_image = image.crop((0, idx*100, image.width, (idx+1)*100))  # Simplified crop for demo purposes
        save_cropped_image(question_image, page_num * 10 + idx)

cropped_question_paths
