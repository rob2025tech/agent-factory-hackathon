# apps/api/providers/llm/mock.py

from apps.api.providers.llm.base import LLMProvider


class MockLLM(LLMProvider):
    """
    Deterministic LLM used for the agent factory vertical slice.

    The same input always produces the same output, which allows the
    full execution pipeline to be tested without any external provider.
    """

    async def generate(
        self,
        prompt: str,
        memories: list | None = None,
    ) -> str:

        return f"echo: {prompt}"
