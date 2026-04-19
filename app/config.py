import os
from pathlib import Path

from pydantic import BaseModel


def load_dotenv_file() -> None:
    env_path = Path(__file__).resolve().parents[1] / ".env"
    if not env_path.exists():
        return

    for line in env_path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        key = key.strip()
        value = value.strip().strip("'").strip('"')
        os.environ.setdefault(key, value)


load_dotenv_file()


class Settings(BaseModel):
    allowed_suffixes: tuple[str, ...] = (".pdf",)
    max_upload_size_mb: int = 5
    modelscope_api_key: str | None = os.getenv("MODELSCOPE_API_KEY")
    modelscope_base_url: str = "https://api-inference.modelscope.cn/v1"
    # modelscope_model: str = "XiaomiMiMo/MiMo-V2-Flash:xiaomi"
    modelscope_model: str = "Qwen/Qwen3.5-27B"
    modelscope_enable_thinking: bool = True


settings = Settings()
