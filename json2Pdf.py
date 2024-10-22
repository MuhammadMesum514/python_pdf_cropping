import json
from fpdf import FPDF

# Load JSON data
with open('document.json') as f:
    data = json.load(f)

# Initialize PDF
pdf = FPDF()
pdf.add_page()
pdf.set_font("Arial", size=12)

# Convert JSON to PDF
for key, value in data.items():
    pdf.cell(200, 10, txt=f"{key}: {value}", ln=True)

# Save PDF
pdf.output("output_json.pdf")
