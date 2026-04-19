from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, File, HTTPException, Request, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.config import settings

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


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

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "request": request,
            "title": "简历诊断助手",
            "message": "文件校验通过，分析功能待接入",
        },
    )
