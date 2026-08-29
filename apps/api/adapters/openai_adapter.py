from ..models.request_models import ExecuteRequest
from ..models.response_models import ExecuteResponse
from .base_adapter import BaseAdapter


class OpenAIAdapter(BaseAdapter):
    """
    Executes prompts using the OpenAI API.
    """

    def execute(
        self, request: ExecuteRequest, context: str | None = None
    ) -> ExecuteResponse:
        raise NotImplementedError("OpenAI adapter has not been implemented yet.")
