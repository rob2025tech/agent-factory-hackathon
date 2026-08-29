from mem0 import Memory


class Mem0Client:

    def __init__(self):
        self.client = Memory()


    async def add(
        self,
        user_id,
        data
    ):

        return self.client.add(
            messages=data,
            user_id=user_id
        )


    async def search(
        self,
        user_id,
        query
    ):

        return self.client.search(
            query=query,
            user_id=user_id
        )