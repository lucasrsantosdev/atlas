from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


class ModelConfigError(RuntimeError):
    """Erro na configuração de modelos do Atlas."""


@dataclass(frozen=True)
class ModelRuntimeConfig:
    provider: str
    host: str
    timeout_seconds: int


@dataclass(frozen=True)
class LocalModelConfig:
    name: str
    role: str


@dataclass(frozen=True)
class ModelsConfig:
    runtime: ModelRuntimeConfig
    model: LocalModelConfig


def _project_root() -> Path:
    return Path(__file__).resolve().parents[3]


def default_models_config_path() -> Path:
    return _project_root() / "config" / "models.yaml"


def _load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise ModelConfigError(
            f"Arquivo de modelos não encontrado: {path}"
        )

    try:
        with path.open("r", encoding="utf-8") as file:
            data = yaml.safe_load(file)
    except yaml.YAMLError as exc:
        raise ModelConfigError(
            f"YAML inválido em {path}: {exc}"
        ) from exc
    except OSError as exc:
        raise ModelConfigError(
            f"Não foi possível ler {path}: {exc}"
        ) from exc

    if not isinstance(data, dict):
        raise ModelConfigError(
            f"A configuração raiz deve ser um objeto YAML: {path}"
        )

    return data


def _required_section(
    data: dict[str, Any],
    section: str,
) -> dict[str, Any]:
    value = data.get(section)

    if not isinstance(value, dict):
        raise ModelConfigError(
            f"Seção obrigatória ausente ou inválida: '{section}'"
        )

    return value


def _required_string(
    data: dict[str, Any],
    key: str,
    section: str,
) -> str:
    value = data.get(key)

    if not isinstance(value, str) or not value.strip():
        raise ModelConfigError(
            f"'{section}.{key}' deve ser uma string não vazia."
        )

    return value.strip()


def _required_positive_int(
    data: dict[str, Any],
    key: str,
    section: str,
) -> int:
    value = data.get(key)

    if not isinstance(value, int) or value <= 0:
        raise ModelConfigError(
            f"'{section}.{key}' deve ser um inteiro positivo."
        )

    return value


def load_models_config(
    path: str | Path | None = None,
) -> ModelsConfig:
    config_path = (
        Path(path).expanduser().resolve()
        if path is not None
        else default_models_config_path()
    )

    data = _load_yaml(config_path)

    runtime_data = _required_section(data, "runtime")
    model_data = _required_section(data, "model")

    runtime = ModelRuntimeConfig(
        provider=_required_string(
            runtime_data,
            "provider",
            "runtime",
        ),
        host=_required_string(
            runtime_data,
            "host",
            "runtime",
        ),
        timeout_seconds=_required_positive_int(
            runtime_data,
            "timeout_seconds",
            "runtime",
        ),
    )

    model = LocalModelConfig(
        name=_required_string(
            model_data,
            "name",
            "model",
        ),
        role=_required_string(
            model_data,
            "role",
            "model",
        ),
    )

    return ModelsConfig(
        runtime=runtime,
        model=model,
    )
