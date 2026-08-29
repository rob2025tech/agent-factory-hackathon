from mem0 import Memory


class Mem0Memory:

    def __init__(self):
        self.memory = Memory()

    def add(self, user_id, text):
        self.memory.add(
            text,
            user_id=user_id
        )

    def search(self, user_id, query):
        return self.memory.search(
            query,
            user_id=user_id
        )