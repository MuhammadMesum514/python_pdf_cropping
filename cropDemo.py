import pdfplumber
from pdf2image import convert_from_path
from PIL import Image

# Open the PDF
pdf_path = "output.pdf"
output_dir = "./results"  # Output directory for cropped images

# Iterate over each page
with pdfplumber.open(pdf_path) as pdf:
    for page_num, page in enumerate(pdf.pages, start=1):
        # Extract text with bounding boxes
        text = page.extract_text()
        question_positions = []
        for word in page.extract_words():
            # Assume question numbers are isolated numbers
            if word['text'].isdigit():
                question_positions.append((int(word['text']), word['x0'], word['top'], word['x1'], word['bottom']))

        # Process each question and its bounding box
        for i, (question_num, x0, y0, x1, y1) in enumerate(question_positions):
            # Determine the bottom boundary by the start of the next question or end of page
            if i < len(question_positions) - 1:
                _, _, _, _, y1_next = question_positions[i + 1]
            else:
                y1_next = page.height  # Use page height if it’s the last question

            # Convert the PDF page to an image
            images = convert_from_path(pdf_path, first_page=page_num, last_page=page_num, dpi=300)
            page_image = images[0]

            # Calculate the crop box and crop the image
            crop_box = (x0, y0, x1, y1_next)
            cropped_image = page_image.crop(crop_box)

            # Save the cropped image
            cropped_image.save(f"{output_dir}/page_{page_num}_question_{question_num}.png")
            print(f"Cropped image saved: page_{page_num}_question_{question_num}.png")
