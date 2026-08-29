from .base_memory import BaseMemory


class InMemory(BaseMemory):

    def __init__(self):
        self.store = {}

    def load(self, user_id):

        return self.store.get(user_id, [])

    def save(self, user_id, prompt, response):

        self.store.setdefault(user_id, []).append(
            {
                "prompt": prompt,
                "response": response.output,
            }
        )
