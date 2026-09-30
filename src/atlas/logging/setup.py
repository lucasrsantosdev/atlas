from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path


def _project_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _logs_dir() -> Path:
    return _project_root() / "logs"


def configure_logging() -> None:
    """
    Configura logging técnico do Atlas.

    Saídas:
    - console;
    - arquivo logs/atlas.log.

    O arquivo utiliza rotação para evitar crescimento infinito.
    """

    logs_dir = _logs_dir()
    logs_dir.mkdir(parents=True, exist_ok=True)

    log_file = logs_dir / "atlas.log"

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    if root_logger.handlers:
        return

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=2_000_000,
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)

    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)
