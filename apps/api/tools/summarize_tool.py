# apps/api/tools/summarize_tool.py
from .base_tool import BaseTool


class SummarizeTool(BaseTool):
    """Tool for summarizing text."""

    def execute(self, input_text: str) -> str:
        words = input_text.split()

        if len(words) <= 10:
            return f"Summary: {input_text}"

        first_part = " ".join(words[:10])
        last_part = " ".join(words[-10:])

        if len(words) > 20:
            return f"Summary: {first_part} ... {last_part}"
        else:
            return f"Summary: {first_part} {last_part}"
