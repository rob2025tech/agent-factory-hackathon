# apps/api/tests/integration/%20%20%20%20test_cerebras_adapter.py

import os
import pytest

from apps.api.adapters.cerebras_adapter import CerebrasAdapter
from apps.api.models.request_models import ExecuteRequest


@pytest.mark.skipif(
    not os.getenv("CEREBRAS_API_KEY"),
    reason="CEREBRAS_API_KEY missing"
)
def test_cerebras_adapter():

    adapter = CerebrasAdapter()

    request = ExecuteRequest(
        backend="cerebras",
        prompt="Say hello in one word"
    )

    response = adapter.execute(request)

    assert response.status == "ok"
    assert response.backend == "cerebras"
    assert len(response.output) > 0