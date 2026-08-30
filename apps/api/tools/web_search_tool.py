# apps/api/tools/web_search_tool.py
from .base_tool import BaseTool


class WebSearchTool(BaseTool):
    """Simulated web search tool."""

    def execute(self, input_text: str) -> str:
        query = input_text.strip()

        mock_results = {
            "python": "Python is a programming language. Key features: readable, versatile, large ecosystem.",
            "agent": "AI agents are autonomous systems that perceive and act in an environment.",
            "factory": "A factory in software is a design pattern that creates objects without exposing logic.",
            "ai": "Artificial Intelligence (AI) simulates human intelligence in machines.",
        }

        for key, value in mock_results.items():
            if key.lower() in query.lower():
                return f"Search result for '{query}': {value}"

        return f"Search results for '{query}': Found relevant information about {query}."
