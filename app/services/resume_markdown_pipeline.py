from app.schemas.resume import MarkdownPipelineResult
from app.services.markdown_normalizer import MarkdownNormalizer
from app.services.pdf_text_extractor import PdfTextExtractor


class ResumeMarkdownPipeline:
    def __init__(
        self,
        extractor: PdfTextExtractor | None = None,
        normalizer: MarkdownNormalizer | None = None,
    ) -> None:
        self.extractor = extractor or PdfTextExtractor()
        self.normalizer = normalizer or MarkdownNormalizer()

    def process(self, content: bytes) -> MarkdownPipelineResult:
        raw_markdown = self.extractor.extract(content)
        normalized_markdown, used_fallback, fallback_reason = self.normalizer.normalize(
            raw_markdown
        )
        return MarkdownPipelineResult(
            raw_markdown=raw_markdown,
            normalized_markdown=normalized_markdown,
            used_fallback=used_fallback,
            fallback_reason=fallback_reason,
        )
