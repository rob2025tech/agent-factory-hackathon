import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from apps.api.providers.llm.ollama import OllamaLLM


@pytest.mark.anyio
async def test_ollama_generate():
    provider = OllamaLLM()

    mock_response = MagicMock()
    mock_response.json.return_value = {"response": "Hello from mock ollama!"}
    mock_response.raise_for_status = MagicMock()

    with patch(
        "apps.api.providers.llm.ollama.httpx.AsyncClient.post",
        new_callable=AsyncMock,
        return_value=mock_response,
    ) as mock_post:
        response = await provider.generate(
            prompt="Say hello in one word",
            memories=[],
        )

    assert response == "Hello from mock ollama!"

    mock_response.raise_for_status.assert_called_once()

    mock_post.assert_awaited_once_with(
        f"{provider.url}/api/generate",
        json={
            "model": provider.model,
            "prompt": "Say hello in one word",
            "stream": False,
        },
        timeout=60,
    )
