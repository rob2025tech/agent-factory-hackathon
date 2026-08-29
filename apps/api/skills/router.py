from .registry import skills


def select(request=None):
    """
    Deterministic skill selection for the vertical slice.

    Always returns the first registered skill (the deterministic
    echo/mock skill), so the same input always takes the same path.
    """

    return skills[0]
