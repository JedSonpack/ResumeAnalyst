from io import BytesIO

import pdfplumber


class PdfTextExtractor:
    def extract(self, content: BytesIO) -> str:
        with pdfplumber.open(content) as pdf:
            texts = [page.extract_text() or "" for page in pdf.pages]
        return "\n".join(texts).strip()
