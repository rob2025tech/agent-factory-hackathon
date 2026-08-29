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


class ExecuteResponse(BaseModel):
    status: str
    backend: str
    prompt: str
    output: str
