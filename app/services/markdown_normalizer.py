try:
    from openai import OpenAI
except ImportError:  # pragma: no cover - depends on optional runtime dependency
    OpenAI = None

from app.config import settings


class MarkdownNormalizer:
    def normalize(self, markdown: str) -> tuple[str, bool, str | None]:
        api_key = settings.modelscope_api_key
        if not api_key:
            return markdown, True, "missing_api_key"

        try:
            normalized = self._stream_completion(api_key, markdown).strip()
        except Exception as e:
            print(e)# noqa: BLE001
            return markdown, True, "llm_request_failed"

        if not normalized:
            return markdown, True, "llm_empty_response"

        return normalized + "\n", False, None

    def _stream_completion(self, api_key: str, markdown: str) -> str:
        if OpenAI is None:
            raise RuntimeError("openai dependency is not installed")

        client = OpenAI(
            base_url=settings.modelscope_base_url,
            api_key=api_key,
        )
        response = client.chat.completions.create(
            model=settings.modelscope_model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "你是简历 Markdown 整理助手。"
                        "请在不编造信息的前提下，只整理结构、换行、标题和列表格式，"
                        "输出适合后续规则分析的 Markdown。"
                    ),
                },
                {
                    "role": "user",
                    "content": markdown,
                },
            ],
            stream=True,
            extra_body={"enable_thinking": settings.modelscope_enable_thinking},
        )

        answer_chunks: list[str] = []
        for chunk in response:
            if not chunk.choices:
                continue
            content = chunk.choices[0].delta.content or ""
            if content:
                answer_chunks.append(content)
        return "".join(answer_chunks)
