# apps/api/models/error_models.py

from pydantic import BaseModel


class ErrorResponse(BaseModel):
    """Typed body returned when an AgentServiceError reaches the app
    boundary (single exception handler registered in main.py)."""

    error_type: str
    detail: str
