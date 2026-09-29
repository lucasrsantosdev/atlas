from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


class AtlasConfigError(RuntimeError):
    """Erro de configuração do Atlas."""


@dataclass(frozen=True)
class AtlasInfoConfig:
    name: str
    version: str


@dataclass(frozen=True)
class RuntimeConfig:
    offline_first: bool
    environment: str
    language: str


@dataclass(frozen=True)
class SystemConfig:
    startup_status: str


@dataclass(frozen=True)
class AtlasConfig:
    atlas: AtlasInfoConfig
    runtime: RuntimeConfig
    system: SystemConfig


def _project_root() -> Path:
    """
    Retorna a raiz atual do projeto Atlas.

    Estrutura esperada:

    project/
      config/
      src/
        atlas/
          core/
            config.py
    """

    return Path(__file__).resolve().parents[3]


def default_config_path() -> Path:
    """
    Permite sobrescrever o arquivo através da variável
    de ambiente ATLAS_CONFIG.

    Caso não exista, utiliza config/atlas.yaml.
    """

    custom_path = os.getenv("ATLAS_CONFIG")

    if custom_path:
        return Path(custom_path).expanduser().resolve()

    return _project_root() / "config" / "atlas.yaml"


def _load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise AtlasConfigError(
            f"Arquivo de configuração não encontrado: {path}"
        )

    try:
        with path.open("r", encoding="utf-8") as file:
            data = yaml.safe_load(file)
    except yaml.YAMLError as exc:
        raise AtlasConfigError(
            f"YAML inválido em {path}: {exc}"
        ) from exc
    except OSError as exc:
        raise AtlasConfigError(
            f"Não foi possível ler {path}: {exc}"
        ) from exc

    if not isinstance(data, dict):
        raise AtlasConfigError(
            f"A configuração raiz deve ser um objeto YAML: {path}"
        )

    return data


def _required_section(
    data: dict[str, Any],
    section: str,
) -> dict[str, Any]:
    value = data.get(section)

    if not isinstance(value, dict):
        raise AtlasConfigError(
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
        raise AtlasConfigError(
            f"'{section}.{key}' deve ser uma string não vazia."
        )

    return value.strip()


def _required_bool(
    data: dict[str, Any],
    key: str,
    section: str,
) -> bool:
    value = data.get(key)

    if not isinstance(value, bool):
        raise AtlasConfigError(
            f"'{section}.{key}' deve ser true ou false."
        )

    return value


def load_config(
    path: str | Path | None = None,
) -> AtlasConfig:
    config_path = (
        Path(path).expanduser().resolve()
        if path is not None
        else default_config_path()
    )

    data = _load_yaml(config_path)

    atlas_data = _required_section(data, "atlas")
    runtime_data = _required_section(data, "runtime")
    system_data = _required_section(data, "system")

    atlas = AtlasInfoConfig(
        name=_required_string(
            atlas_data,
            "name",
            "atlas",
        ),
        version=_required_string(
            atlas_data,
            "version",
            "atlas",
        ),
    )

    runtime = RuntimeConfig(
        offline_first=_required_bool(
            runtime_data,
            "offline_first",
            "runtime",
        ),
        environment=_required_string(
            runtime_data,
            "environment",
            "runtime",
        ),
        language=_required_string(
            runtime_data,
            "language",
            "runtime",
        ),
    )

    system = SystemConfig(
        startup_status=_required_string(
            system_data,
            "startup_status",
            "system",
        ),
    )

    return AtlasConfig(
        atlas=atlas,
        runtime=runtime,
        system=system,
    )