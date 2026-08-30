# apps/api/skills/skill.py
from typing import List, Optional
from pydantic import BaseModel


class Skill(BaseModel):
    """Represents a skill with its capabilities."""
    name: str
    backend: str
    tools: List[str]
    description: Optional[str] = None
    keywords: List[str] = []
    priority: int = 0  # Higher = more likely to be selected
