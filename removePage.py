from PyPDF2 import PdfReader, PdfWriter

def remove_pages(input_path, output_path, pages_to_remove):
    reader = PdfReader(input_path)
    writer = PdfWriter()

    for page_num in range(len(reader.pages)):
        if page_num + 1 not in pages_to_remove:
            writer.add_page(reader.pages[page_num])

    with open(output_path, 'wb') as output_file:
        writer.write(output_file)

# Example usage
input_pdf = "5054_s22_qp_11.pdf"
output_pdf = "output.pdf"
pages_to_remove = [1]  # Remove pages 2, 4, and 6

remove_pages(input_pdf, output_pdf, pages_to_remove)