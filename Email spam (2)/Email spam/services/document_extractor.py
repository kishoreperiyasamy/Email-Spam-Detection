import os
import io
import re

try:
    import pdfplumber
except ImportError:
    pdfplumber = None

from PIL import Image

def extract_text_from_file(file_storage) -> dict:
    """
    Extracts text and metadata from uploaded brochures (PDF), documents (TXT, EML),
    and photo/image attachments.
    """
    filename = file_storage.filename or "uploaded_file"
    ext = os.path.splitext(filename)[1].lower()
    
    # Read file bytes
    file_bytes = file_storage.read()
    file_storage.seek(0)  # Reset pointer
    
    file_size_kb = round(len(file_bytes) / 1024, 1)

    result = {
        "success": True,
        "filename": filename,
        "extension": ext,
        "file_size_kb": file_size_kb,
        "file_type": "unknown",
        "extracted_text": "",
        "page_count": 1,
        "urls_detected": [],
        "notes": []
    }

    # 1. PDF Brochures & Invoices
    if ext == '.pdf':
        result["file_type"] = "PDF Brochure / Document"
        if not pdfplumber:
            result["success"] = False
            result["error"] = "PDF extraction module (pdfplumber) is not available. Please install it using 'pip install pdfplumber'."
            return result
        try:
            with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
                pages_text = []
                urls = set()
                result["page_count"] = len(pdf.pages)

                for page_num, page in enumerate(pdf.pages, 1):
                    # Extract page text
                    text = page.extract_text()
                    if text:
                        pages_text.append(text)
                    
                    # Extract hyperlink annotations if present
                    if hasattr(page, 'hyperlinks') and page.hyperlinks:
                        for link in page.hyperlinks:
                            uri = link.get('uri')
                            if uri:
                                urls.add(uri)

                full_text = "\n\n".join(pages_text).strip()
                result["extracted_text"] = full_text

                # Find any raw URLs in extracted text
                raw_urls = re.findall(r'https?://[^\s<>"]+|www\.[^\s<>"]+', full_text)
                for u in raw_urls:
                    urls.add(u)

                result["urls_detected"] = list(urls)
                result["notes"].append(f"Successfully extracted {len(pages_text)} page(s) from PDF brochure.")
        except Exception as e:
            result["success"] = False
            result["error"] = f"Failed to extract PDF content: {str(e)}"
            return result

    # 2. Photos, Ad Banners, & Flyers (Image inspection)
    elif ext in ['.png', '.jpg', '.jpeg', '.webp', '.bmp', '.gif']:
        result["file_type"] = "Photo / Image Ad"
        try:
            image = Image.open(io.BytesIO(file_bytes))
            width, height = image.size
            img_format = image.format or ext.replace('.', '').upper()
            result["notes"].append(f"Image format: {img_format}, dimensions: {width}x{height}px.")
            result["extracted_text"] = ""  # Client-side Tesseract.js handles high-speed OCR
        except Exception as e:
            result["notes"].append(f"Basic image validation note: {str(e)}")

    # 3. Plain Text, EML, Markdown, or HTML files
    elif ext in ['.txt', '.eml', '.html', '.htm', '.md']:
        result["file_type"] = "Text / EML Document"
        try:
            decoded_text = file_bytes.decode('utf-8', errors='replace').strip()
            result["extracted_text"] = decoded_text
            raw_urls = re.findall(r'https?://[^\s<>"]+|www\.[^\s<>"]+', decoded_text)
            result["urls_detected"] = list(set(raw_urls))
            result["notes"].append("Extracted plain text content.")
        except Exception as e:
            result["success"] = False
            result["error"] = f"Failed to read document: {str(e)}"
            return result

    else:
        result["file_type"] = "Attachment"
        result["notes"].append("Binary attachment detected.")

    return result
