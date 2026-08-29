from abc import ABC, abstractmethod


class BaseTool(ABC):

    name: str

    @abstractmethod
    def execute(self, input):

        pass
