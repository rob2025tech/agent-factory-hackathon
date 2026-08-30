# apps/api/models/response_models.py

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class ContextTrace(BaseModel):
    user_id: Optional[str] = None
    task: Optional[str] = None


class ToolTrace(BaseModel):
    name: str
    output: str


class ToolExecutionTrace(BaseModel):
    name: str
    input: Optional[str] = None
    output: str
    duration_ms: Optional[float] = None
    order: Optional[int] = None


class LLMTrace(BaseModel):
    provider: str
    model: Optional[str] = None
    prompt: Optional[str] = None
    output: str
    duration_ms: Optional[float] = None
    tokens_used: Optional[int] = None


class SkillSelectionTrace(BaseModel):
    selected_skill: str
    available_skills: List[str] = []
    selection_time_ms: Optional[float] = None
    selection_reason: Optional[str] = None


class MemoryTrace(BaseModel):
    search_duration_ms: Optional[float] = None
    save_duration_ms: Optional[float] = None
    memory_count: Optional[int] = None
    search_query: Optional[str] = None


class ExecutionTrace(BaseModel):
    trace_id: Optional[str] = None
    timestamp: Optional[datetime] = None
    total_duration_ms: Optional[float] = None
    context: ContextTrace
    skill: Optional[str] = None
    skill_selection: Optional[SkillSelectionTrace] = None
    tool: Optional[ToolTrace] = None
    tools: List[ToolExecutionTrace] = []
    llm: LLMTrace
    memory: Optional[MemoryTrace] = None
    status: Optional[str] = None


class ExecuteResponse(BaseModel):
    status: str
    backend: str
    prompt: str
    output: str
    memory_count: int = 0
    trace: Optional[ExecutionTrace] = None
