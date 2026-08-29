# apps/api/services/execution_service.py

from ..adapters.registry import registry
from ..memory.memory_manager import memory
from ..models.request_models import ExecuteRequest
from ..models.response_models import ExecuteResponse
from ..skills.router import select


def execute_agent(request: ExecuteRequest) -> ExecuteResponse:
    """
    Main execution pipeline.

    Request
      ↓
    Load Context
      ↓
    Choose Skill
      ↓
    Choose Backend
      ↓
    Backend Adapter
      ↓
    Run LLM
      ↓
    Store Memory
      ↓
    Return Response
    """

    # Load previous conversation memory
    context = memory.load(request.user_id)

    # Select skill
    skill = select(request)

    # Select backend
    backend = request.backend or skill.backend

    # Get adapter
    adapter = registry.get(backend)

    # Execute with optional context
    result = adapter.execute(
        request=request,
        context=context,
    )

    # Save interaction
    memory.save(
        request.user_id,
        request.prompt,
        result,
    )

    return result
