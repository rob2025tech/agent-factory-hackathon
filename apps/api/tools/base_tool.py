# apps/api/tools/base_tool.py
from abc import ABC, abstractmethod


class BaseTool(ABC):
    """Base class for all tools."""

    @abstractmethod
    def execute(self, input_text: str) -> str:
        """Execute the tool with the given input."""
        pass
