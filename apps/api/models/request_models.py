# apps/api/models/request_models.py

from pydantic import BaseModel

# class ExecuteRequest(BaseModel):
#     input: str
#     backend: str = "mock"

# class ExecuteRequest(BaseModel):
#     message: str
#     user_id: str | None = None


class ExecuteRequest(BaseModel):
    prompt: str
    backend: str = "mock"
    user_id: str | None = None

class ConversationCreate(BaseModel):
    prompt: str
    response: str
    model: str