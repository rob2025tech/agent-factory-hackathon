from ..models.request_models import ExecuteRequest
from ..models.response_models import ExecuteResponse
from .base_adapter import BaseAdapter


class MockAdapter(BaseAdapter):
    """
    Fake backend used during development.

    This allows the entire execution pipeline to be tested
    without any external AI provider.
    """

    def execute(
        self, request: ExecuteRequest, context: str | None = None
    ) -> ExecuteResponse:

        return ExecuteResponse(
            status="ok",
            backend="mock",
            prompt=request.prompt,
            output="hello from mock backend",
        )
