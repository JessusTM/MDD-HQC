"""Logging setup: dictConfig from JSON, runtime overrides, and queue listener."""

import atexit
import json
import logging
import logging.config
import logging.handlers
from pathlib import Path
from app.core.config import config


def setup_logging() -> None:
    """Configure application logging via dictConfig and optional queue listener.

    Loads ``logging_config.json``, applies runtime overrides (level, file path,
    rotation), and starts the queue listener if configured. Idempotent: skips
    if logging is already configured (e.g. queue handler present).
    """
    if _is_logging_already_configured():
        return

    logging_configuration_path = _get_logging_config_path()
    logging_configuration_dict = _load_logging_configuration(logging_configuration_path)

    project_root = _get_project_root()
    log_file_path = _build_log_file_path(project_root)

    _apply_runtime_overrides(logging_configuration_dict, log_file_path)

    logging.config.dictConfig(logging_configuration_dict)

    _start_queue_listener_if_configured()


def _get_logging_config_path() -> Path:
    """Return the path to ``logging_config.json`` next to this module."""
    return Path(__file__).with_name("logging_config.json")


def _load_logging_configuration(logging_configuration_path: Path) -> dict:
    """Load and return the logging dictConfig from the given JSON file."""
    with logging_configuration_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _get_project_root() -> Path:
    """Return the project root (mdd-hqc-backend) as an absolute path."""
    return Path(__file__).resolve().parents[3]


def _build_log_file_path(project_root: Path) -> Path:
    """Ensure ``logs`` dir exists and return path to the log file (from config)."""
    logs_dir = project_root / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    return logs_dir / config.LOG_FILE_NAME


def _apply_runtime_overrides(
    logging_configuration_dict: dict, log_file_path: Path
) -> None:
    """Mutate the config dict: level, file path, rotation (maxBytes, backupCount)."""
    logging_configuration_dict["root"]["level"] = config.LOG_LEVEL.upper()
    file_handler_config = logging_configuration_dict["handlers"]["file"]
    file_handler_config["filename"] = str(log_file_path)
    file_handler_config["maxBytes"] = int(config.LOG_MAX_BYTES)
    file_handler_config["backupCount"] = int(config.LOG_BACKUP_COUNT)


def _start_queue_listener_if_configured() -> None:
    """Start the queue handler's listener if present; register atexit stop."""
    queue_handler = _get_queue_handler_by_name("queue")
    if queue_handler is None:
        return

    listener = getattr(queue_handler, "listener", None)
    if listener is None:
        return

    try:
        listener.start()
    except RuntimeError:
        pass

    atexit.register(listener.stop)


def _get_queue_handler_by_name(handler_name: str):
    """Return the handler named ``handler_name``, or None if not available."""
    if hasattr(logging, "getHandlerByName"):
        return logging.getHandlerByName(handler_name)
    return None


def _is_logging_already_configured() -> bool:
    """Return True if a queue handler exists or root has a QueueHandler."""
    queue_handler = _get_queue_handler_by_name("queue")
    if queue_handler is not None:
        return True

    root_logger = logging.getLogger()
    return any(
        isinstance(h, logging.handlers.QueueHandler) for h in root_logger.handlers
    )
