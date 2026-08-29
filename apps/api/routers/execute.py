# apps/api/routers/execute.py

from fastapi import APIRouter

# from httpcore import request
# from ..models.request_models import ExecuteRequest
# from ..models.response_models import ExecuteResponse
# from ..services.execution_service import execute_agent
from apps.api.models.request_models import ExecuteRequest
from apps.api.models.response_models import ExecuteResponse
from apps.api.services.agent_service import AgentService

router = APIRouter()

agent_service = AgentService()

# @router.post("/execute")
# def execute(payload: dict):
#     return {
#         "status": "ok",
#         "mode": "mock",
#         "input": payload,
#         "output": "hello from agent platform",
#     }


# @router.post(
#     "/execute",
#     response_model=ExecuteResponse,
# )
# def execute(request: ExecuteRequest):
#     # return {
#     #     "status": "ok",
#     #     "mode": "mock",
#     #     "input": request,
#     #     "output": "hello from agent platform",
#     # }
#     return execute_agent(request)


@router.post("/execute", response_model=ExecuteResponse)
async def execute(request: ExecuteRequest):

    user_id = (
        request.user_id
        if "user_id" in request.model_fields_set
        else "anonymous"
    )

    backend = (
        request.backend
        if "backend" in request.model_fields_set
        else "agent-service"
    )

    result = await agent_service.execute(
        user_id=user_id,
        prompt=request.prompt,
    )

    return ExecuteResponse(
        status=result["status"],
        backend=backend,
        prompt=request.prompt,
        output=result["output"],
        memory_count=result.get(
            "memory_count",
            0,
        ),
    )
