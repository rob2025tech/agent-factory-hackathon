# apps/api/routers/butterbase.py

from fastapi import APIRouter
from apps.api.models.request_models import ConversationCreate
from apps.api.providers.butterbase.client import butterbase_client

router = APIRouter(
    prefix="/butterbase",
    tags=["butterbase"],
)


@router.get("/health")
async def health():
    return await butterbase_client.health()

@router.get("/conversations")
async def list_conversations():
    return await butterbase_client.list_conversations()

@router.post("/conversations")
async def create_conversation(payload: ConversationCreate):
    return await butterbase_client.create_conversation(
        prompt=payload.prompt,
        response_text=payload.response,
        model=payload.model,
    )