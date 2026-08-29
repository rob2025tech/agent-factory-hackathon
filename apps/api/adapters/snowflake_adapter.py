from ..models.request_models import ExecuteRequest
from ..models.response_models import ExecuteResponse
from .base_adapter import BaseAdapter


class SnowflakeAdapter(BaseAdapter):
    """
    Executes prompts using Snowflake Cortex.
    """

    def execute(
        self, request: ExecuteRequest, context: str | None = None
    ) -> ExecuteResponse:
        raise NotImplementedError("Snowflake adapter has not been implemented yet.")
