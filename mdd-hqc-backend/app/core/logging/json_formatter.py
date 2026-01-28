"""Custom formatters and filters for structured (JSON) and console logging."""

import datetime as dt
import json
import logging


class JSONFormatter(logging.Formatter):
    """Formatter that emits each log record as a single JSON object (one line)."""

    def __init__(self, fmt_keys: dict[str, str] | None = None) -> None:
        """Initialize with optional mapping of output keys to LogRecord attributes."""
        super().__init__()
        self.fmt_keys = fmt_keys or {}

    def format(self, record: logging.LogRecord) -> str:
        """Serialize the log record to a JSON string (utf-8, default=str for dates)."""
        payload = self._build_payload(record)
        return json.dumps(payload, default=str, ensure_ascii=False)

    def _build_payload(self, record: logging.LogRecord) -> dict:
        """Build a dict from the log record (message, timestamp, exc_info, fmt_keys)."""
        base_fields: dict[str, object] = {
            "message": record.getMessage(),
            "timestamp": dt.datetime.fromtimestamp(
                record.created, tz=dt.timezone.utc
            ).isoformat(),
        }

        if record.exc_info is not None:
            base_fields["exc_info"] = self.formatException(record.exc_info)

        if record.stack_info is not None:
            base_fields["stack_info"] = self.formatStack(record.stack_info)

        payload: dict[str, object] = {}

        for out_key, record_attr in self.fmt_keys.items():
            if record_attr in base_fields:
                payload[out_key] = base_fields[record_attr]
            else:
                payload[out_key] = getattr(record, record_attr, None)

        payload.update(base_fields)
        return payload


class BelowWarningFilter(logging.Filter):
    """Filter that passes only records with level below WARNING (DEBUG, INFO)."""

    def filter(self, record: logging.LogRecord) -> bool:
        """Return True if levelno < WARNING."""
        return record.levelno < logging.WARNING


class WarningAndAboveFilter(logging.Filter):
    """Filter that passes only records with level WARNING or above."""

    def filter(self, record: logging.LogRecord) -> bool:
        """Return True if levelno >= WARNING."""
        return record.levelno >= logging.WARNING
