# apps/api/tests/nextgen/providers/memory/test_evermind.py

import pytest

from apps.api.providers.memory.evermind import (
    EverMindMemory,
)


@pytest.mark.anyio
async def test_save_and_search():

    provider = EverMindMemory()

    await provider.save(
        "alice",
        {
            "fact": "likes pizza",
        },
    )

    results = await provider.search(
        "alice",
        "pizza",
    )

    # assert isinstance(results, list)
    assert isinstance(results, list)
    assert len(results) >= 1