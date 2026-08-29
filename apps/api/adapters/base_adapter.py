# apps/api/adapters/base_adapter.py

from abc import ABC, abstractmethod

from ..models.request_models import ExecuteRequest
from ..models.response_models import ExecuteResponse


class BaseAdapter(ABC):

    @abstractmethod
    def execute(
        self,
        request: ExecuteRequest,
        context: str | None = None,
    ) -> ExecuteResponse:
        pass
