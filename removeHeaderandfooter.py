import fitz  # PyMuPDF

def remove_header_footer(input_file, output_file, top_margin=0, bottom_margin=0):
    # Open the PDF
    doc = fitz.open(input_file)
    
    for page in doc:
        # Get the page dimensions
        page_rect = page.rect
        
        # Create rectangles for the areas to keep (effectively removing header and footer)
        keep_rect = fitz.Rect(
            page_rect.x0,  # left
            page_rect.y0 + top_margin,  # top (excluding top margin)
            page_rect.x1,  # right
            page_rect.y1 - bottom_margin  # bottom (excluding bottom margin)
        )
        
        # Remove all content outside of the keep_rect
        page.add_redact_annot(page_rect)
        page.add_redact_annot(keep_rect, "white")
        page.apply_redactions()
        
        # Optionally, you can add a white rectangle to cover any remaining artifacts
        page.draw_rect(page_rect, color=fitz.utils.getColor("white"), fill=fitz.utils.getColor("white"))
        page.draw_rect(keep_rect, color=fitz.utils.getColor("white"), fill=None)

    # Save the modified PDF
    doc.save(output_file)
    doc.close()

# Usage
input_file = 'output.pdf'
output_file = 'output_without_header_footer.pdf'
remove_header_footer(input_file, output_file)