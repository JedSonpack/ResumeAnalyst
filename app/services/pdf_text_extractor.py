from io import BytesIO

import pdfplumber


class PdfTextExtractor:
    def extract(self, content: BytesIO) -> str:
        try:
            with pdfplumber.open(content) as pdf:
                texts = [page.extract_text() or "" for page in pdf.pages]
        except Exception as exc:  # noqa: BLE001
            raise ValueError("PDF 文本提取失败") from exc

        text = "\n".join(texts).strip()
        if not text:
            raise ValueError("PDF 中未提取到有效文本")

        return text
