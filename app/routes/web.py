from pathlib import Path
from typing import Annotated
from io import BytesIO

from fastapi import APIRouter, File, HTTPException, Request, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.config import settings
from app.services.diagnosis_engine import DiagnosisEngine
from app.services.pdf_text_extractor import PdfTextExtractor
from app.services.resume_section_parser import ResumeSectionParser

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


def extract_and_analyze_resume(content: bytes) -> dict:
    raw_text = PdfTextExtractor().extract(BytesIO(content))
    parsed = ResumeSectionParser().parse(raw_text)
    return DiagnosisEngine().analyze(parsed).model_dump()


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
        },
    )
