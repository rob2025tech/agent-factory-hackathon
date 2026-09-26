# apps/api/providers/memory/evermind.py

import re

from apps.api.providers.memory.base import MemoryProvider


def _tokenize(text: str) -> set[str]:
    """Lowercase alphanumeric tokens, deterministic across runs."""
    return set(re.findall(r"[a-z0-9]+", text.lower()))


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
        # DECISION: deterministic lexical token-overlap retrieval.
        # Trade-off: this is lexical, not semantic — a natural-language
        # query matches when it shares tokens with a stored memory.
        # Score = number of distinct query tokens present in the memory
        # text; only positive-overlap memories are returned, highest
        # score first, insertion order preserved for ties (sorted() is
        # stable). No embeddings, no external service, no result cap.

        user_memories = self.memories.get(
            user_id,
            [],
        )

        query_tokens = _tokenize(query)

        scored = []

        for memory in user_memories:
            overlap = len(query_tokens & _tokenize(str(memory)))
            if overlap > 0:
                scored.append((overlap, memory))

        scored.sort(key=lambda item: item[0], reverse=True)

        return [memory for _, memory in scored]

    async def load(
        self,
        user_id: str,
    ):
        return self.memories.get(user_id, [])