# apps/api/adapters/registry.py

from apps.api.config.settings import settings

from .base_adapter import BaseAdapter
from .mock_adapter import MockAdapter
from .ollama_adapter import OllamaAdapter
from .cerebras_adapter import CerebrasAdapter

class AdapterRegistry:
    """
    Registry of available backend adapters.
    """

    def __init__(self):
        self._adapters: dict[str, BaseAdapter] = {}

        # Default adapters
        self.register("mock", MockAdapter())
        self.register("ollama", OllamaAdapter())
        if settings.cerebras_api_key:
            self.register("cerebras", CerebrasAdapter())

    def get(self, backend: str) -> BaseAdapter:
        """
        Return the adapter for the requested backend.

        Raises:
            ValueError if backend is unknown.
        """

        try:
            return self._adapters[backend.lower()]
        except KeyError:
            available = ", ".join(sorted(self._adapters.keys()))
            raise ValueError(
                f"Unknown backend '{backend}'. " f"Available backends: {available}"
            )

    def register(
        self,
        name: str,
        adapter: BaseAdapter,
    ) -> None:
        """
        Register a new adapter.
        """

        self._adapters[name.lower()] = adapter

    def available_backends(self) -> list[str]:
        """
        Return available backend names.
        """

        return sorted(self._adapters.keys())


# Application-wide registry
registry = AdapterRegistry()
