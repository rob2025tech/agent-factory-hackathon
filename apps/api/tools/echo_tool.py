# apps/api/tools/echo_tool.py

from apps.api.tools.base_tool import BaseTool


class EchoTool(BaseTool):
    """
    One simple deterministic tool for the vertical slice.
    """

    name = "echo"

    def execute(self, input):

        return f"tool[echo] received: {input}"

    __call__ = execute
