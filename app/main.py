from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.routes.web import router as web_router


def create_app() -> FastAPI:
    app = FastAPI(title="简历诊断助手")
    app.include_router(web_router)
    app.mount("/static", StaticFiles(directory="app/static"), name="static")
    return app


app = create_app()
