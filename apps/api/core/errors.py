# apps/api/core/errors.py

class AgentServiceError(Exception):
    """Base exception for AgentService errors."""
    pass


class ProviderInitError(AgentServiceError):
    """Raised when a provider fails to initialize."""
    pass


class MemoryProviderError(AgentServiceError):
    """Raised when the memory provider operation fails."""
    pass


class LLMProviderError(AgentServiceError):
    """Raised when the LLM provider operation fails."""
    pass


class MemorySearchError(MemoryProviderError):
    """Raised when memory.search() fails."""
    pass


class MemorySaveError(MemoryProviderError):
    """Raised when memory.save() fails."""
    pass


class InvalidMemoryDataError(AgentServiceError):
    """Raised when memory.search() returns invalid data (non-iterable)."""
    pass


class InvalidLLMResponseError(AgentServiceError):
    """Raised when llm.generate() returns invalid data."""
    pass