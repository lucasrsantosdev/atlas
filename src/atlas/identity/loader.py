from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from atlas.identity.models import AtlasIdentity


class AtlasIdentityError(RuntimeError):
    """Erro ao carregar ou validar a identidade do Atlas."""


def _project_root() -> Path:
    return Path(__file__).resolve().parents[3]


def identity_config_dir() -> Path:
    return _project_root() / "config" / "identity"


def _load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise AtlasIdentityError(
            f"Arquivo de identidade não encontrado: {path}"
        )

    try:
        with path.open("r", encoding="utf-8") as file:
            data = yaml.safe_load(file)
    except yaml.YAMLError as exc:
        raise AtlasIdentityError(
            f"YAML inválido em {path}: {exc}"
        ) from exc
    except OSError as exc:
        raise AtlasIdentityError(
            f"Não foi possível ler {path}: {exc}"
        ) from exc

    if not isinstance(data, dict):
        raise AtlasIdentityError(
            f"O arquivo deve possuir um objeto YAML na raiz: {path}"
        )

    return data


def _required_dict(
    data: dict[str, Any],
    key: str,
    source: str,
) -> dict[str, Any]:
    value = data.get(key)

    if not isinstance(value, dict):
        raise AtlasIdentityError(
            f"'{source}.{key}' deve ser um objeto."
        )

    return value


def _required_list(
    data: dict[str, Any],
    key: str,
    source: str,
) -> list[Any]:
    value = data.get(key)

    if not isinstance(value, list):
        raise AtlasIdentityError(
            f"'{source}.{key}' deve ser uma lista."
        )

    return value


def _required_string(
    data: dict[str, Any],
    key: str,
    source: str,
) -> str:
    value = data.get(key)

    if not isinstance(value, str) or not value.strip():
        raise AtlasIdentityError(
            f"'{source}.{key}' deve ser uma string não vazia."
        )

    return value.strip()


def load_identity() -> AtlasIdentity:
    base_dir = identity_config_dir()

    identity_data = _load_yaml(base_dir / "identity.yaml")
    personality_data = _load_yaml(base_dir / "personality.yaml")
    preferences_data = _load_yaml(base_dir / "preferences.yaml")
    principles_data = _load_yaml(base_dir / "principles.yaml")
    capabilities_data = _load_yaml(base_dir / "capabilities.yaml")

    atlas_data = _required_dict(
        identity_data,
        "atlas",
        "identity",
    )

    mission_data = _required_dict(
        identity_data,
        "mission",
        "identity",
    )

    architecture_data = _required_dict(
        identity_data,
        "architecture",
        "identity",
    )

    continuity_data = _required_dict(
        identity_data,
        "continuity",
        "identity",
    )

    personality = _required_dict(
        personality_data,
        "personality",
        "personality",
    )

    principles = _required_list(
        principles_data,
        "principles",
        "principles",
    )

    capabilities = _required_dict(
        capabilities_data,
        "capabilities",
        "capabilities",
    )

    return AtlasIdentity(
        name=_required_string(
            atlas_data,
            "name",
            "identity.atlas",
        ),
        version=_required_string(
            atlas_data,
            "version",
            "identity.atlas",
        ),
        agent_type=_required_string(
            atlas_data,
            "type",
            "identity.atlas",
        ),
        created_at=_required_string(
            atlas_data,
            "created_at",
            "identity.atlas",
        ),
        mission=_required_string(
            mission_data,
            "primary",
            "identity.mission",
        ),
        architecture=architecture_data,
        continuity=continuity_data,
        personality=personality,
        preferences=preferences_data,
        principles=principles,
        capabilities=capabilities,
    )