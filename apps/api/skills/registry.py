from .skill import Skill

skills = [
    Skill(
        name="echo",
        backend="mock",
        tools=["echo"],
    ),
    Skill(
        name="default",
        backend="ollama",
        tools=[],
    ),
]
