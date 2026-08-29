from dataclasses import dataclass

@dataclass
class ModelCapabilities:
    provider: str
    model: str

    supports_chat: bool
    supports_tools: bool
    supports_json: bool
    supports_vision: bool

    context_window: int | None

    input_cost_per_1m: float | None
    output_cost_per_1m: float | None