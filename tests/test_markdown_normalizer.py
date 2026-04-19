from app.services.resume_markdown_pipeline import ResumeMarkdownPipeline
from app.config import settings


def test_default_model_switched_to_mimo_flash():
    assert settings.modelscope_model == "XiaomiMiMo/MiMo-V2-Flash:xiaomi"


def test_pipeline_falls_back_when_api_key_missing(monkeypatch):
    monkeypatch.setattr(
        "app.services.resume_markdown_pipeline.PdfTextExtractor.extract",
        lambda self, content: "# 项目经历\n\nAgent Tool-Calling 架构优化\n",
    )
    monkeypatch.setattr(
        "app.services.markdown_normalizer.settings",
        type("Settings", (), {"modelscope_api_key": None})(),
    )

    result = ResumeMarkdownPipeline().process(b"%PDF-1.4")

    assert result.raw_markdown.startswith("# 项目经历")
    assert result.normalized_markdown == result.raw_markdown
    assert result.used_fallback is True
    assert result.fallback_reason == "missing_api_key"


def test_pipeline_uses_llm_result_when_available(monkeypatch):
    monkeypatch.setattr(
        "app.services.resume_markdown_pipeline.PdfTextExtractor.extract",
        lambda self, content: "# 项目经历\n\n原始内容\n",
    )
    monkeypatch.setattr(
        "app.services.markdown_normalizer.settings",
        type("Settings", (), {"modelscope_api_key": "token"})(),
    )
    monkeypatch.setattr(
        "app.services.markdown_normalizer.MarkdownNormalizer._stream_completion",
        lambda self, api_key, markdown: "## 项目经历\n\n整理后的内容\n",
    )

    result = ResumeMarkdownPipeline().process(b"%PDF-1.4")

    assert result.raw_markdown.startswith("# 项目经历")
    assert result.normalized_markdown.startswith("## 项目经历")
    assert result.used_fallback is False
    assert result.fallback_reason is None


def test_pipeline_falls_back_when_llm_request_fails(monkeypatch):
    monkeypatch.setattr(
        "app.services.resume_markdown_pipeline.PdfTextExtractor.extract",
        lambda self, content: "# 技能清单\n\nPython Redis\n",
    )
    monkeypatch.setattr(
        "app.services.markdown_normalizer.settings",
        type("Settings", (), {"modelscope_api_key": "token"})(),
    )
    monkeypatch.setattr(
        "app.services.markdown_normalizer.MarkdownNormalizer._stream_completion",
        lambda self, api_key, markdown: (_ for _ in ()).throw(RuntimeError("boom")),
    )

    result = ResumeMarkdownPipeline().process(b"%PDF-1.4")

    assert result.normalized_markdown == result.raw_markdown
    assert result.used_fallback is True
    assert result.fallback_reason == "llm_request_failed"


def test_pipeline_falls_back_when_llm_returns_empty_content(monkeypatch):
    monkeypatch.setattr(
        "app.services.resume_markdown_pipeline.PdfTextExtractor.extract",
        lambda self, content: "# 技能清单\n\nPython Redis\n",
    )
    monkeypatch.setattr(
        "app.services.markdown_normalizer.settings",
        type("Settings", (), {"modelscope_api_key": "token"})(),
    )
    monkeypatch.setattr(
        "app.services.markdown_normalizer.MarkdownNormalizer._stream_completion",
        lambda self, api_key, markdown: "   ",
    )

    result = ResumeMarkdownPipeline().process(b"%PDF-1.4")

    assert result.normalized_markdown == result.raw_markdown
    assert result.used_fallback is True
    assert result.fallback_reason == "llm_empty_response"
