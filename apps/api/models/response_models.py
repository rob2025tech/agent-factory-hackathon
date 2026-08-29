# apps/api/models/response_models.py

from pydantic import BaseModel

# class ExecuteResponse(BaseModel):
#     status: str
#     backend: str
#     output: str

# class ExecuteResponse(BaseModel):
#     status: str
#     mode: str
#     input: str
# output: str


class ContextTrace(BaseModel):
    user_id: str | None = None
    task: str | None = None


class ToolTrace(BaseModel):
    name: str
    output: str


class LLMTrace(BaseModel):
    provider: str
    output: str


class ExecutionTrace(BaseModel):
    context: ContextTrace
    skill: str
    tool: ToolTrace | None = None
    llm: LLMTrace


class ExecuteResponse(BaseModel):
    status: str
    backend: str
    prompt: str
    output: str
    memory_count: int = 0
    trace: ExecutionTrace | None = None
