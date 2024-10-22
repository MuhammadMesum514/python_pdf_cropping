import fitz  # PyMuPDF

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

# Example usage
input_pdf_path = "input.pdf"
output_pdf_path = "cropped_output.pdf"
page_number = 0  # First page
crop_rect = (100, 100, 400, 400)  # Coordinates (x0, y0, x1, y1)

crop_pdf(input_pdf_path, output_pdf_path, page_number, crop_rect)