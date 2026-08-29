# apps/api/providers/memory/evermind.py

from apps.api.providers.memory.base import MemoryProvider


class EverMindMemory(MemoryProvider):

    def __init__(self):
        # Temporary local storage.
        # Later replace this with EverOS client.
        self.memories = {}

    async def save(
        self,
        user_id: str,
        data: dict,
    ):

        if user_id not in self.memories:
            self.memories[user_id] = []

        self.memories[user_id].append(data)


    async def search(
        self,
        user_id: str,
        query: str,
    ):

        user_memories = self.memories.get(
            user_id,
            [],
        )

        results = []

        for memory in user_memories:
            if query.lower() in str(memory).lower():
                results.append(memory)

        return results

    async def load(
        self,
        user_id: str,
    ):
        return self.memories.get(user_id, [])