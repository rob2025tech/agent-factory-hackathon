# apps/api/skills/router.py

from typing import Optional

from .registry import skills


def select(prompt: Optional[str] = None):
    """
    Keyword-scored skill selection with priority as a tie-breaker.

    Priority only applies among skills that matched at least one keyword;
    it never causes selection on its own, so an unmatched prompt still
    falls back to the first registered skill (echo).
    """
    if not prompt:
        return skills[0]

    prompt_lower = prompt.lower()

    best_skill = None
    best_score = 0.0

    for skill in skills:
        keyword_score = sum(
            1 for kw in skill.keywords if kw.lower() in prompt_lower)
        if keyword_score == 0:
            continue
        score = keyword_score + skill.priority * 0.1
        if score > best_score:
            best_score = score
            best_skill = skill

    return best_skill if best_skill is not None else skills[0]
