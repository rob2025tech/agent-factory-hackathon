# apps/api/providers/llm/fireworks.py

from apps.api.providers.llm.base import LLMProvider


class FireworksLLM(LLMProvider):

    def __init__(self):
        pass


    async def generate(
        self,
        prompt: str,
        memories: list | None = None,
    ) -> str:

        # TODO:
        # call Fireworks API

        return "Fireworks response placeholder"

    