# apps/api/routers/execute.py

from fastapi import APIRouter

# from httpcore import request
# from ..models.request_models import ExecuteRequest
# from ..models.response_models import ExecuteResponse
# from ..services.execution_service import execute_agent
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


@router.post("/execute")
async def execute(request: dict):

    result = await agent_service.execute(
        user_id=request.get(
            "user_id",
            "anonymous",
        ),
        prompt=request["prompt"],
    )

    # return result
    return {
        "status": result["status"],
        "backend": request.get(
            "backend",
            "agent-service",
        ),
        "prompt": request["prompt"],
        "output": result["output"],
        "memory_count": result.get(
            "memory_count",
            0,
        ),
    }
