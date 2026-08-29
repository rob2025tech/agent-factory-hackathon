# apps/api/providers/llm/base.py

from abc import ABC, abstractmethod


class LLMProvider(ABC):

    @abstractmethod
    # async def execute(
    #     self,
    #     prompt: str,
    # ):
    #     pass

    async def generate(
        self,
        prompt: str,
        memories: list | None = None,
    ) -> str:
        pass