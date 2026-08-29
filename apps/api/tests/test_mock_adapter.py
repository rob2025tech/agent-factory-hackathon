from apps.api.adapters.mock_adapter import MockAdapter
from apps.api.models.request_models import ExecuteRequest


def test_mock_adapter():
    adapter = MockAdapter()

    request = ExecuteRequest(
        backend="mock",
        prompt="hello",
    )

    response = adapter.execute(request)

    assert response.status == "ok"
    assert response.backend == "mock"
