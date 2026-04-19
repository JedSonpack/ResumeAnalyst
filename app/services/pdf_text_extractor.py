from io import BytesIO
from tempfile import NamedTemporaryFile

try:
    from markitdown import MarkItDown
except ImportError:  # pragma: no cover - exercised via dependency installation/runtime
    MarkItDown = None

from app.services.markdown_cleaner import clean_markdown


class PdfTextExtractor:
    def extract(self, content: bytes | BytesIO) -> str:
        try:
            if MarkItDown is None:
                raise ValueError("MarkItDown 未安装")
            with NamedTemporaryFile(suffix=".pdf") as temp_file:
                temp_file.write(self._to_bytes(content))
                temp_file.flush()
                text = MarkItDown().convert(temp_file.name).text_content
        except Exception as exc:  # noqa: BLE001
            raise ValueError("PDF 文本提取失败") from exc

        text = clean_markdown(text)
        if not text.strip():
            raise ValueError("PDF 中未提取到有效文本")

        return text

    def _to_bytes(self, content: bytes | BytesIO) -> bytes:
        if isinstance(content, bytes):
            return content
        return content.getvalue()
