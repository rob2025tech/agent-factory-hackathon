# apps/api/tests/integration/test_ollama.py

import pytest

from apps.api.providers.llm.ollama import OllamaLLM


@pytest.mark.integration
@pytest.mark.anyio
async def test_ollama_live():

    provider = OllamaLLM()

    response = await provider.generate(
        prompt="Say hello in one word",
    )

    assert isinstance(response, str)
    assert len(response) > 0