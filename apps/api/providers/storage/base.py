from abc import ABC, abstractmethod


class StorageProvider(ABC):

    @abstractmethod
    async def save(self, item):
        pass


    @abstractmethod
    async def get(self, key):
        pass