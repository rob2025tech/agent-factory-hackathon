# apps/api/providers/butterbase/client.py

import httpx

from apps.api.config.settings import settings


class ButterbaseClient:
    def __init__(self):
        self.base_url = settings.butterbase_api_base
        self.api_key = settings.butterbase_api_key

    def _headers(self):
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    async def health(self):
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/conversations",
                headers=self._headers(),
            )

            response.raise_for_status()

            return {
                "status": "ok",
                "butterbase_status": response.status_code,
            }

    async def list_conversations(self):
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/conversations",
                headers=self._headers(),
            )

            response.raise_for_status()

            return response.json()

    async def create_conversation(
        self,
        prompt: str,
        response_text: str,
        model: str,
    ):
        payload = {
            "prompt": prompt,
            "response": response_text,
            "model": model,
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/conversations",
                headers=self._headers(),
                json=payload,
            )

            response.raise_for_status()

            return response.json()


butterbase_client = ButterbaseClient()
