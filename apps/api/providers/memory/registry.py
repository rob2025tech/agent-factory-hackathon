from apps.api.providers.memory.evermind import EverMindMemory
from apps.api.providers.memory.mem0 import Mem0Memory


memory_provider_classes = {
    "evermind": EverMindMemory,
    "mem0": Mem0Memory,
}


def get_memory_provider(name: str):

    provider_class = memory_provider_classes[name]

    return provider_class()