# apps/api/providers/memory/registry.py

from typing import Callable, Dict, Type

from apps.api.providers.memory.evermind import EverMindMemory


def _load_mem0_provider() -> Type:
    try:
        from apps.api.providers.memory.mem0 import Mem0Memory
    except ImportError as e:
        raise ImportError(
            "The 'mem0' memory provider requires the optional 'mem0ai' "
            "package, which is not installed. Install it with: "
            "pip install '.[mem0]'"
        ) from e
    return Mem0Memory


memory_provider_factories: Dict[str, Callable[[], Type]] = {
    "evermind": lambda: EverMindMemory,
    "mem0": _load_mem0_provider,
}


def get_memory_provider(name: str):
    factory = memory_provider_factories[name]
    provider_class = factory()
    return provider_class()
