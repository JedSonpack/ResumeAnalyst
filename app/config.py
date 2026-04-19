from pydantic import BaseModel


class Settings(BaseModel):
    allowed_suffixes: tuple[str, ...] = (".pdf",)
    max_upload_size_mb: int = 5


settings = Settings()
