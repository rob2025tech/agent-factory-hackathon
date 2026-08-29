# apps/api/adapters/ollama_adapter.py

import httpx

from ..config.settings import settings
from ..models.request_models import ExecuteRequest
from ..models.response_models import ExecuteResponse
from .base_adapter import BaseAdapter


class OllamaAdapter(BaseAdapter):
    """
    Executes prompts using a local Ollama server.
    """

    def execute(
        self,
        request: ExecuteRequest,
        context: str | None = None,
    ) -> ExecuteResponse:

        prompt = request.prompt

        if context:
            prompt = f"""
Conversation memory:

{context}

User request:

{request.prompt}
"""

        with httpx.Client() as client:
            response = client.post(
                f"{settings.ollama_url}/api/generate",
                json={
                    "model": settings.ollama_model,
                    "prompt": prompt,
                    "stream": False,
                },
                timeout=120,
            )

        response.raise_for_status()

        result = response.json()

        return ExecuteResponse(
            status="ok",
            backend=request.backend,
            prompt=request.prompt,
            output=result["response"],
        )
