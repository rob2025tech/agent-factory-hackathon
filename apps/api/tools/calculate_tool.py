# apps/api/tools/calculate_tool.py

import ast
import operator

from .base_tool import BaseTool

_ALLOWED_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
}


def _eval_node(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _ALLOWED_OPS:
        return _ALLOWED_OPS[type(node.op)](_eval_node(node.left), _eval_node(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in _ALLOWED_OPS:
        return _ALLOWED_OPS[type(node.op)](_eval_node(node.operand))
    raise ValueError("Unsupported expression")


class CalculateTool(BaseTool):
    """Tool for performing arithmetic calculations."""

    def execute(self, input_text: str) -> str:
        try:
            tree = ast.parse(input_text, mode="eval")
            result = _eval_node(tree.body)
            return f"Result: {result}"
        except Exception:
            return "Invalid calculation. Please provide a plain arithmetic expression."
