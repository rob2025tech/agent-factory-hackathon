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


@pytest.mark.anyio
async def test_full_sentence_query_retrieves_prior_memory():

    provider = EverMindMemory()

    await provider.save(
        "alice",
        {
            "prompt": "My favorite language is Python.",
            "response": "echo: My favorite language is Python.",
        },
    )

    results = await provider.search(
        "alice",
        "What is my favorite language?",
    )

    assert len(results) == 1


@pytest.mark.anyio
async def test_unrelated_query_returns_no_memories():

    provider = EverMindMemory()

    await provider.save(
        "alice",
        {
            "fact": "likes pizza",
        },
    )

    results = await provider.search(
        "alice",
        "orbital mechanics of distant galaxies",
    )

    assert results == []


@pytest.mark.anyio
async def test_higher_overlap_sorts_first():

    provider = EverMindMemory()

    low_overlap = {"fact": "alpha only"}
    high_overlap = {"fact": "alpha beta gamma"}

    await provider.save("alice", low_overlap)
    await provider.save("alice", high_overlap)

    results = await provider.search(
        "alice",
        "alpha beta gamma",
    )

    assert len(results) == 2
    assert results[0] == high_overlap
    assert results[1] == low_overlap


@pytest.mark.anyio
async def test_equal_scores_keep_insertion_order():

    provider = EverMindMemory()

    first = {"fact": "alpha one"}
    second = {"fact": "alpha two"}

    await provider.save("alice", first)
    await provider.save("alice", second)

    results = await provider.search(
        "alice",
        "alpha",
    )

    assert results == [first, second]