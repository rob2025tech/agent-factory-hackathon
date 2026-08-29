# apps/api/providers/llm/registry.py

from apps.api.providers.llm.fireworks import FireworksLLM
from apps.api.providers.llm.mock import MockLLM
from apps.api.providers.llm.ollama import OllamaLLM

llm_provider_classes = {

    "mock": MockLLM,

    "ollama": OllamaLLM,

    "fireworks": FireworksLLM,

}


def get_llm_provider(name: str):

    provider_class = llm_provider_classes[name]

    return provider_class()