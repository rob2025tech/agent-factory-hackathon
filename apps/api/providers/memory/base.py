# apps/api/providers/memory/base.py

from abc import ABC, abstractmethod


class MemoryProvider(ABC):

    @abstractmethod
    async def save(
        self,
        user_id: str,
        data: dict
    ):
        pass


    # @abstractmethod
    # async def load(
    #     self,
    #     user_id: str
    # ):
    #     pass


    @abstractmethod
    async def search(
        self,
        user_id: str,
        query: str
    ):
        pass