from io import BytesIO
from pathlib import Path

from app.services.pdf_text_extractor import PdfTextExtractor


def test_extract_pdf_text(monkeypatch):
    class FakeResult:
        text_content = "项⽬经历\nAgent Tool-Calling 架构优化：通过 Workﬂow 对原\n⼦⼯具进⾏编排封装。\n"

    class FakeMarkItDown:
        def convert(self, source):
            assert Path(source).suffix == ".pdf"
            return FakeResult()

    monkeypatch.setattr("app.services.pdf_text_extractor.MarkItDown", FakeMarkItDown)

    extractor = PdfTextExtractor()
    text = extractor.extract(BytesIO(b"%PDF-1.4"))

    assert "项目经历" in text
    assert "Workflow" in text
    assert "原子工具" in text


def test_extract_pdf_text_raises_when_markdown_empty(monkeypatch):
    class FakeResult:
        text_content = " \n \n"

    class FakeMarkItDown:
        def convert(self, source):
            return FakeResult()

    monkeypatch.setattr("app.services.pdf_text_extractor.MarkItDown", FakeMarkItDown)

    extractor = PdfTextExtractor()

    try:
        extractor.extract(BytesIO(b"%PDF-1.4"))
    except ValueError as exc:
        assert str(exc) == "PDF 中未提取到有效文本"
    else:
        raise AssertionError("expected ValueError when markdown is empty")
