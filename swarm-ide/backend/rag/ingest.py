"""
ingest.py
Modular document ingestion pipeline for swarm-ide.
Wraps the existing PyMuPDF / Pandas / Tesseract logic from 6_builder_app.py
and exposes a single parse_document(name, b64_content) interface.
"""
import base64
import io


def parse_document(name: str, b64_content: str) -> str:
    """
    Decodes base64 file content and extracts text based on extension / magic bytes.
    Returns plain text (truncated at 25,000 chars) or an error string.
    """
    if "," in b64_content:
        b64_content = b64_content.split(",", 1)[1]

    try:
        raw_bytes = base64.b64decode(b64_content)
    except Exception as e:
        return f"[Error decoding base64 for {name}: {e}]"

    name_lower = name.lower()

    # --- PDF (extension or magic bytes) ---
    if name_lower.endswith(".pdf") or raw_bytes.startswith(b"%PDF"):
        try:
            import pymupdf as fitz
        except ImportError:
            import fitz
        try:
            doc = fitz.open(stream=raw_bytes, filetype="pdf")
            full_text = "\n".join(page.get_text() for page in doc)
            if len(full_text) > 25_000:
                return full_text[:25_000] + "\n\n[SYSTEM WARNING: PDF truncated at 25,000 chars.]"
            return full_text
        except Exception as e:
            return f"[Error parsing PDF: {e}]"

    # --- Excel / CSV ---
    if name_lower.endswith((".xlsx", ".xls", ".csv")):
        try:
            import pandas as pd
            if name_lower.endswith(".csv"):
                df = pd.read_csv(io.BytesIO(raw_bytes))
            else:
                df = pd.read_excel(io.BytesIO(raw_bytes))
            return df.to_markdown()
        except Exception as e:
            return f"[Error parsing spreadsheet: {e}]"

    # --- Images (OCR) ---
    if name_lower.endswith((".png", ".jpg", ".jpeg")):
        try:
            import pytesseract
            from PIL import Image
            img = Image.open(io.BytesIO(raw_bytes))
            text = pytesseract.image_to_string(img)
            return text if text.strip() else "[OCR found no text]"
        except Exception as e:
            return f"[OCR Error: {e}]"

    # --- Fallback: plain text ---
    try:
        return raw_bytes.decode("utf-8")
    except Exception:
        return "[Error: binary file unsupported or not text-decodable]"
