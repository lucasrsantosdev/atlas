from urllib import error, request
import json

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.models.model import Model
from app.models.repository import create_model, get_model, list_models, update_model


class ModelCreate(BaseModel):
    name: str = Field(min_length=1)
    provider: str = Field(min_length=1)
    model_name: str = Field(min_length=1)
    configuration: dict = Field(default_factory=dict)
    enabled: bool = True


class ModelUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1)
    configuration: dict | None = None
    enabled: bool | None = None


router = APIRouter(prefix="/models", tags=["models"])


@router.post("", response_model=Model)
def create_model_endpoint(payload: ModelCreate) -> Model:
    try:
        return create_model(
            name=payload.name,
            provider=payload.provider,
            model_name=payload.model_name,
            configuration=payload.configuration,
            enabled=payload.enabled,
        )
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("", response_model=list[Model])
def list_models_endpoint() -> list[Model]:
    return list_models()


@router.get("/status")
def model_provider_status() -> dict:
    """Report real Ollama reachability and currently running models."""
    try:
        with request.urlopen("http://localhost:11434/api/ps", timeout=2) as response:
            payload = json.loads(response.read().decode("utf-8"))
        running = [item.get("name") for item in payload.get("models", []) if item.get("name")]
        return {"provider": "ollama", "online": True, "running_models": running}
    except (error.URLError, TimeoutError, json.JSONDecodeError):
        return {"provider": "ollama", "online": False, "running_models": []}


@router.get("/{model_id}", response_model=Model)
def get_model_endpoint(model_id: int) -> Model:
    model = get_model(model_id)
    if model is None:
        raise HTTPException(status_code=404, detail="Model not found")
    return model


@router.patch("/{model_id}", response_model=Model)
def update_model_endpoint(model_id: int, payload: ModelUpdate) -> Model:
    model = get_model(model_id)
    if model is None:
        raise HTTPException(status_code=404, detail="Model not found")
    try:
        return update_model(
            model_id,
            name=payload.name,
            configuration=payload.configuration,
            enabled=payload.enabled,
        )
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
