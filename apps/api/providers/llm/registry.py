# apps/api/providers/llm/registry.py

from apps.api.providers.llm.ollama import OllamaLLM
from apps.api.providers.llm.fireworks import FireworksLLM


llm_provider_classes = {

    "ollama": OllamaLLM,

    "fireworks": FireworksLLM,

}


def get_llm_provider(name: str):

    provider_class = llm_provider_classes[name]

    return provider_class()