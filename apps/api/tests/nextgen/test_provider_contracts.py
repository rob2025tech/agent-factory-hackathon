import pytest
import inspect

from apps.api.config.settings import settings
from apps.api.providers.memory.registry import get_memory_provider
from apps.api.providers.llm.registry import get_llm_provider

@pytest.mark.anyio
async def test_memory_provider_has_search_method():
    """Verify the memory provider contract."""
    provider = get_memory_provider(settings.memory_provider)

    # Does it have search?
    assert hasattr(provider, "search"), "Missing .search() method"
    assert callable(provider.search), ".search() is not callable"

    # What does search return? Let's call it with minimal args
    try:
        result = await provider.search(user_id="test_user", query="test")
        print(f"search() returned: {type(result)}")
        print(f"search() result content: {result}")
        # Is it iterable?
        try:
            len(result)
            print(f"len() works: {len(result)}")
        except TypeError:
            print("NOT iterable - len() fails")
    except Exception as e:
        print(f"search() raised: {type(e).__name__}: {e}")

@pytest.mark.anyio
async def test_memory_provider_has_save_method():
    provider = get_memory_provider(settings.memory_provider)

    assert hasattr(provider, "save")
    assert callable(provider.save)

    # Check signature
    import inspect
    sig = inspect.signature(provider.save)
    print(f"save() signature: {sig}")

@pytest.mark.anyio
async def test_llm_provider_has_generate_method():
    provider = get_llm_provider(settings.llm_provider)

    assert hasattr(provider, "generate")
    assert callable(provider.generate)

    # What does it expect?
    import inspect
    sig = inspect.signature(provider.generate)
    print(f"generate() signature: {sig}")