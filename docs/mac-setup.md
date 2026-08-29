# Mac Setup

## Install
- Python 3.11
- Ollama
- VS Code

## Clone
git clone ...

## Python
python3.11 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

## Models
ollama pull qwen3:8b

## Verify
pytest -v
ruff check .
black .