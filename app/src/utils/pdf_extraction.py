import pdfplumber
import pytesseract
from pdf2image import convert_from_path

def extract_pdf_text(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        text = ""
        for page in pdf.pages:
            # Extract text from page
            text += page.extract_text() or ""
            # Extract tables
            tables = page.extract_tables()
            for table in tables:
                for row in table:
                    # Convert None to empty string in each cell
                    cleaned_row = [str(cell) if cell is not None else "" for cell in row]
                    text += "\t".join(cleaned_row) + "\n"
    return text


def extract_text_from_scanned_pdf(pdf_path):
    images = convert_from_path(pdf_path)
    text = ""
    for image in images:
        text += pytesseract.image_to_string(image)
    return text