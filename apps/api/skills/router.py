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


def explain(prompt: str | None = None) -> str:
    """
    Return a human-readable reason for the skill that ``select()`` picks.

    Non-breaking helper that mirrors ``select()``'s existing scoring
    without changing it: it reports the winning skill's matched keywords
    and score, or the positional fallback when nothing matched. Used only
    to populate the observability trace (ADR-011 ``skill_selection``).
    """
    if not prompt:
        return (
            f"no prompt provided; fell back to first registered skill "
            f"'{skills[0].name}'"
        )

    prompt_lower = prompt.lower()

    best_skill = None
    best_score = 0.0
    best_matches: list[str] = []

    for skill in skills:
        matches = [kw for kw in skill.keywords if kw.lower() in prompt_lower]
        keyword_score = len(matches)
        if keyword_score == 0:
            continue
        score = keyword_score + skill.priority * 0.1
        if score > best_score:
            best_score = score
            best_skill = skill
            best_matches = matches

    if best_skill is None:
        return (
            f"no keyword match; fell back to first registered skill "
            f"'{skills[0].name}'"
        )

    return (
        f"matched keywords {best_matches} "
        f"(score={best_score:.1f}, priority={best_skill.priority})"
    )
