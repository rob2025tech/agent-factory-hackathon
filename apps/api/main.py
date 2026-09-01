from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from .core.errors import AgentServiceError
from .models.error_models import ErrorResponse
from .routers import butterbase

# @app.post("/execute")
# def execute(payload: dict):
#     return {
#         "status": "ok",
#         "mode": "mock",
#         "input": payload,
#         "output": "hello from agent platform",
#     }
# from routers.execute import router as execute_router
from .routers.execute import router as execute_router

# @app.get("/health")
# def health():
#     return {"status": "ok"}
# from routers.health import router as health_router
from .routers.health import router as health_router

app = FastAPI()


# Single error mapping (ADR-014): every AgentServiceError surfaces as
# HTTP 500 with a typed body. Deliberately undifferentiated for now;
# differentiated statuses are a future decision.
@app.exception_handler(AgentServiceError)
async def agent_service_error_handler(request: Request, exc: AgentServiceError):
    body = ErrorResponse(error_type=type(exc).__name__, detail=str(exc))
    return JSONResponse(status_code=500, content=body.model_dump())


# Static demo UI served same-origin (no CORS needed).
# CWD-independent path: apps/api/main.py -> apps/web
WEB_DIR = Path(__file__).resolve().parent.parent / "web"


@app.get("/")
def root():
    return {"message": "AI Agent Platform Starter"}


app.include_router(health_router)
app.include_router(execute_router)
app.include_router(butterbase.router)

app.mount("/ui", StaticFiles(directory=WEB_DIR, html=True), name="web")
