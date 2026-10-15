from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.models.memory import Memory
from app.models.memory_repository import (
    create_memory,
    delete_memory,
    get_memory,
    list_memories,
    update_memory,
)


class MemoryCreate(BaseModel):
    type: str
    key: str
    value: str
    source: str
    project_id: int | None = None
    confidence: float | None = None


class MemoryUpdate(BaseModel):
    type: str | None = None
    key: str | None = None
    value: str | None = None
    source: str | None = None
    project_id: int | None = None
    confidence: float | None = None


router = APIRouter(prefix="/memories", tags=["memories"])


@router.get("", response_model=list[Memory])
def list_memories_endpoint(project_id: int | None = None) -> list[Memory]:
    return list_memories(project_id)


@router.post("", response_model=Memory)
def create_memory_endpoint(payload: MemoryCreate) -> Memory:
    try:
        return create_memory(**payload.model_dump())
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/{memory_id}", response_model=Memory)
def get_memory_endpoint(memory_id: int) -> Memory:
    memory = get_memory(memory_id)
    if memory is None:
        raise HTTPException(status_code=404, detail="Memory not found")
    return memory


@router.patch("/{memory_id}", response_model=Memory)
def update_memory_endpoint(memory_id: int, payload: MemoryUpdate) -> Memory:
    try:
        update_fields = payload.model_dump(exclude_unset=True)
        if "project_id" in update_fields and update_fields["project_id"] is None:
            update_fields["clear_project_id"] = True
        memory = update_memory(memory_id, **update_fields)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    if memory is None:
        raise HTTPException(status_code=404, detail="Memory not found")
    return memory


@router.delete("/{memory_id}")
def delete_memory_endpoint(memory_id: int) -> dict[str, bool]:
    if not delete_memory(memory_id):
        raise HTTPException(status_code=404, detail="Memory not found")
    return {"deleted": True}
