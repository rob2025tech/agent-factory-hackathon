# apps/api/tools/registry.py
from apps.api.tools.echo_tool import EchoTool
from apps.api.tools.web_search_tool import WebSearchTool
from apps.api.tools.calculate_tool import CalculateTool
from apps.api.tools.summarize_tool import SummarizeTool

tools = {
    "echo": EchoTool(),
    "web_search": WebSearchTool(),
    "calculate": CalculateTool(),
    "summarize": SummarizeTool(),
}
