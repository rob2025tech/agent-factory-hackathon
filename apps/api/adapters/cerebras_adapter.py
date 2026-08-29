# apps/api/adapters/cerebras_adapter.py

from openai import OpenAI

from apps.api.config.settings import settings
from .base_adapter import BaseAdapter
from ..models.request_models import ExecuteRequest
from ..models.response_models import ExecuteResponse


class CerebrasAdapter(BaseAdapter):

    def __init__(self):
        if not settings.cerebras_api_key:
            raise RuntimeError(
                "CEREBRAS_API_KEY is not configured."
            )
        self.client = OpenAI(
            api_key=settings.cerebras_api_key,
            base_url="https://api.cerebras.ai/v1",
        )

    def execute(
        self,
        request: ExecuteRequest,
        context: str | None = None,
    ) -> ExecuteResponse:

        response = self.client.chat.completions.create(
            model="gpt-oss-120b",
            messages=[
                {
                    "role": "user",
                    "content": request.prompt,
                }
            ],
        )

        content = response.choices[0].message.content

        if content is None:
            raise RuntimeError("Cerebras returned no content")

        return ExecuteResponse(
            status="ok",
            backend="cerebras",
            prompt=request.prompt,
            output=content,
        )