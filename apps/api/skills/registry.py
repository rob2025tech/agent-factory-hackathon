# apps/api/skills/registry.py
from .skill import Skill

skills = [
    Skill(
        name="echo",
        backend="mock",
        tools=["echo"],
        description="Echo back the user's input",
        keywords=["echo", "repeat", "mirror"],
        priority=1,
    ),
    Skill(
        name="web_search",
        backend="mock",
        tools=["web_search", "summarize"],
        description="Search the web for information",
        keywords=["search", "find", "look up", "google", "web", "lookup"],
        priority=5,
    ),
    Skill(
        name="calculator",
        backend="mock",
        tools=["calculate"],
        description="Perform calculations and conversions",
        keywords=["calculate", "math", "convert", "sum",
                  "add", "multiply", "subtract", "divide"],
        priority=3,
    ),
    Skill(
        name="default",
        backend="ollama",
        tools=[],
        description="Default fallback skill for general conversations",
        keywords=[],
        priority=0,
    ),
]
