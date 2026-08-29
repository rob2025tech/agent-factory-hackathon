from abc import ABC, abstractmethod


class AnalyticsProvider(ABC):

    @abstractmethod
    async def record(self, event):
        pass