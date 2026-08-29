# apps/api/repositories/conversation_repository.py

from apps.api.providers.butterbase.client import butterbase_client


class ConversationRepository:

    async def create(
        self,
        prompt: str,
        response: str,
        model: str,
    ):
        return await butterbase_client.create_conversation(
            prompt=prompt,
            response_text=response,
            model=model,
        )

    async def list_all(self):
        return await butterbase_client.list_conversations()


conversation_repository = ConversationRepository()
