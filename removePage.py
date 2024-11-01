from PyPDF2 import PdfReader, PdfWriter

def remove_pages(input_path, output_path, pages_to_remove):
    reader = PdfReader(input_path)
    writer = PdfWriter()
    print(len(reader.pages))
    for page_num in range(len(reader.pages)):
        if page_num + 1 not in pages_to_remove:
            writer.add_page(reader.pages[page_num])

    with open(output_path, 'wb') as output_file:
        writer.write(output_file)

# Example usage
input_pdf = "input/9700_s19_12.pdf"
output_pdf = "output-bio.pdf"
pages_to_remove = [1,16,17,18,19,20]  # Remove pages 2, 4, and 6

remove_pages(input_pdf, output_pdf, pages_to_remove)