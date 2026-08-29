## Testing

Run the standard test suite:

    pytest -q

By default, integration tests are excluded.

Run integration tests explicitly:

    pytest -q -m integration

Ollama integration tests require a running local Ollama server.

Run only non-integration tests explicitly:

    pytest -q -m "not integration"
