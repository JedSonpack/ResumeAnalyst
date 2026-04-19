from io import BytesIO

from app.services.pdf_text_extractor import PdfTextExtractor


def test_extract_pdf_text(monkeypatch):
    class FakePage:
        def extract_text(self):
            return "教育经历\n某大学 计算机科学与技术"

    class FakePdf:
        pages = [FakePage()]

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

    monkeypatch.setattr("app.services.pdf_text_extractor.pdfplumber.open", lambda _: FakePdf())

    extractor = PdfTextExtractor()
    text = extractor.extract(BytesIO(b"%PDF-1.4"))

    assert "教育经历" in text
