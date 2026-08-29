from apps.api.providers.storage.base import StorageProvider


class LocalStorage(StorageProvider):

    async def save(self,item):

        # write JSON/database

        pass