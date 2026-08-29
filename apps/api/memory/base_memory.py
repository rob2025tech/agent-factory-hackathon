from abc import ABC, abstractmethod


class BaseMemory(ABC):

    @abstractmethod
    def load(self, user_id):
        pass

    @abstractmethod
    def save(self, user_id, prompt, response):
        pass
