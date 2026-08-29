import httpx

from apps.api.config.settings import settings
from apps.api.providers.llm.base import LLMProvider


class OllamaLLM(LLMProvider):

    def __init__(self):

        self.url = settings.ollama_url
        self.model = settings.ollama_model


    async def generate(
        self,
        prompt: str,
        memories: list | None = None,
    ) -> str:

        final_prompt = prompt


        if memories:

            context = "\n".join(
                str(memory)
                for memory in memories
            )

            final_prompt = f"""
Context:
{context}

User:
{prompt}
"""


        payload = {
            "model": self.model,
            "prompt": final_prompt,
            "stream": False,
        }


        async with httpx.AsyncClient() as client:

            response = await client.post(
                f"{self.url}/api/generate",
                json=payload,
                timeout=60,
            )


        response.raise_for_status()

        data = response.json()

        return data.get(
            "response",
            "",
        )