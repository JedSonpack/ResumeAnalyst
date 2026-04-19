from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, File, HTTPException, Request, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.config import settings
from app.services.diagnosis_engine import DiagnosisEngine
from app.services.markdown_renderer import render_markdown
from app.services.resume_markdown_pipeline import ResumeMarkdownPipeline
from app.services.resume_section_parser import ResumeSectionParser

router = APIRouter()
TEMPLATE_DIR = Path(__file__).resolve().parents[1] / "templates"
templates = Jinja2Templates(directory=str(TEMPLATE_DIR))


def extract_and_analyze_resume(content: bytes) -> dict:
    markdown_result = ResumeMarkdownPipeline().process(content)
    parsed = ResumeSectionParser().parse(markdown_result.normalized_markdown)
    analysis = DiagnosisEngine().analyze(parsed)
    analysis.raw_markdown = markdown_result.raw_markdown
    analysis.normalized_markdown = markdown_result.normalized_markdown
    analysis.used_fallback = markdown_result.used_fallback
    analysis.fallback_reason = markdown_result.fallback_reason
    return analysis.model_dump()


@router.get("/", response_class=HTMLResponse)
def home(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"request": request, "title": "简历诊断助手"},
    )


@router.post("/analyze", response_class=HTMLResponse)
async def analyze_resume(
    request: Request,
    resume: Annotated[UploadFile | None, File()] = None,
) -> HTMLResponse:
    if resume is None:
        raise HTTPException(status_code=400, detail="请先选择简历文件")

    if not resume.filename:
        raise HTTPException(status_code=400, detail="请先选择简历文件")

    if Path(resume.filename).suffix.lower() not in settings.allowed_suffixes:
        raise HTTPException(status_code=400, detail="仅支持 PDF 文件")

    try:
        content = await resume.read()
        analysis = extract_and_analyze_resume(content)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=f"PDF 解析失败：{exc}") from exc

    return templates.TemplateResponse(
        request=request,
        name="result.html",
        context={
            "request": request,
            "title": "分析结果",
            "analysis": analysis,
            "raw_markdown_html": render_markdown(analysis["raw_markdown"]),
            "normalized_markdown_html": render_markdown(analysis["normalized_markdown"]),
        },
    )
