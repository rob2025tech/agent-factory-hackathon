# apps/api/tests/nextgen/test_skill_routing.py

from apps.api.skills.router import select


def test_select_echo_skill_for_simple_prompt():
    skill = select("Hello, can you echo this?")
    assert skill.name == "echo"


def test_select_search_skill_for_search_prompt():
    skill = select("Search for Python tutorials")
    assert skill.name == "web_search"


def test_select_calculator_skill_for_math_prompt():
    skill = select("Calculate: 15 * 3 + 4")
    assert skill.name == "calculator"


def test_select_default_skill_for_unmatched_prompt():
    skill = select("What is the meaning of life?")
    assert skill.name == "echo"
