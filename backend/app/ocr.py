# PDF / text extraction with fallback to OCR for images
import pdfplumber
from PIL import Image
import pytesseract
import io

def extract_text_from_pdf(path_or_bytes):
    """
    path_or_bytes: local file path or bytes (if you load the upload)
    returns concatenated text
    """
    text = ""
    if isinstance(path_or_bytes, bytes):
        # open from bytes
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=True) as tmp:
            tmp.write(path_or_bytes)
            tmp.flush()
            with pdfplumber.open(tmp.name) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text() or ""
                    text += page_text + "\n"
    else:
        with pdfplumber.open(path_or_bytes) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text() or ""
                text += page_text + "\n"
    # If text seems empty, try OCR fallback: render pages to images and OCR them
    if len(text.strip()) < 40:
        # OCR fallback
        try:
            with pdfplumber.open(path_or_bytes) as pdf:
                for page in pdf.pages:
                    pil = page.to_image(resolution=150).original
                    text += "\n" + pytesseract.image_to_string(pil)
        except Exception as e:
            # gzip / non-pdf etc.
            print("OCR fallback error:", e)
    return text
