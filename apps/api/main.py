from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

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
