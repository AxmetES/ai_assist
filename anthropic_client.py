import os
from dataclasses import dataclass

import httpx
from dotenv import load_dotenv

load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages"
ANTHROPIC_VERSION = "2023-06-01"
MODEL = "claude-sonnet-4-6"


class AnthropicError(Exception):
    def __init__(self, message: str, status_code: int | None = None):
        super().__init__(message)
        self.status_code = status_code


@dataclass
class ClaudeAnswer:
    answer: str
    input_tokens: int
    output_tokens: int


def _headers() -> dict:
    return {
        "x-api-key": ANTHROPIC_API_KEY,
        "anthropic-version": ANTHROPIC_VERSION,
        "content-type": "application/json",
    }


async def ask_claude(question: str) -> ClaudeAnswer:
    if not ANTHROPIC_API_KEY:
        raise AnthropicError("ANTHROPIC_API_KEY не задан на сервере")

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            ANTHROPIC_API_URL,
            headers=_headers(),
            json={
                "model": MODEL,
                "max_tokens": 2048,
                "messages": [{"role": "user", "content": question}],
            },
        )

    if response.status_code != 200:
        body = response.json() if response.content else {}
        message = body.get("error", {}).get("message", response.text)
        raise AnthropicError(message, status_code=response.status_code)

    data = response.json()
    text_parts = [block["text"] for block in data.get("content", []) if block.get("type") == "text"]
    usage = data.get("usage", {})

    return ClaudeAnswer(
        answer="".join(text_parts).strip(),
        input_tokens=usage.get("input_tokens", 0),
        output_tokens=usage.get("output_tokens", 0),
    )


async def check_api_key() -> dict:
    """Минимальный запрос к Anthropic API (max_tokens=1) для проверки статуса ключа."""
    if not ANTHROPIC_API_KEY:
        return {"status": "invalid", "detail": "ANTHROPIC_API_KEY не задан на сервере"}

    async with httpx.AsyncClient(timeout=15.0) as client:
        response = await client.post(
            ANTHROPIC_API_URL,
            headers=_headers(),
            json={
                "model": MODEL,
                "max_tokens": 1,
                "messages": [{"role": "user", "content": "Hi"}],
            },
        )

    if response.status_code == 200:
        return {"status": "valid", "detail": None}

    body = response.json() if response.content else {}
    error = body.get("error", {})
    err_type = error.get("type", "")
    message = error.get("message", response.text)

    if response.status_code == 401:
        # Anthropic API возвращает один и тот же authentication_error и для
        # невалидного, и для отозванного/истёкшего ключа - различаем по тексту
        # сообщения на лучших основаниях (best-effort).
        if "expired" in message.lower():
            return {"status": "expired", "detail": message}
        return {"status": "invalid", "detail": message}

    return {"status": "error", "detail": f"{err_type or response.status_code}: {message}"}
