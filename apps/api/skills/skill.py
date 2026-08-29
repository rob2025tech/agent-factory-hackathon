from dataclasses import dataclass


@dataclass
class Skill:

    name: str

    backend: str

    tools: list[str]
