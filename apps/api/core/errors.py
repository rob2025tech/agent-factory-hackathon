# apps/api/core/errors.py

class AgentServiceError(Exception):
    """Base exception for AgentService errors."""


class ProviderInitError(AgentServiceError):
    """Raised when a provider fails to initialize."""


class MemoryProviderError(AgentServiceError):
    """Raised when the memory provider operation fails."""


class LLMProviderError(AgentServiceError):
    """Raised when the LLM provider operation fails."""


class MemorySearchError(MemoryProviderError):
    """Raised when memory.search() fails."""


class MemorySaveError(MemoryProviderError):
    """Raised when memory.save() fails."""


class InvalidMemoryDataError(AgentServiceError):
    """Raised when memory.search() returns invalid data (non-iterable)."""


class InvalidLLMResponseError(AgentServiceError):
    """Raised when llm.generate() returns invalid data."""
