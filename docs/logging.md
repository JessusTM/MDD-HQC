# Logging in the MDD-HQC Backend

### Goal
The backend includes a centralized logging setup to:
- keep a consistent format across the entire application (including third-party libraries),
- correctly split normal output (stdout) from warnings/errors (stderr),
- persist structured logs on disk (JSON Lines) with rotation,
- allow changing the log level and file parameters via environment variables.

### Components and repository location
The implementation lives under:

- `mdd-hqc-backend/app/core/logging/`
  - `logging.py`: runtime entry point for configuring logging (`setup_logging()`).
  - `logging_config.json`: base configuration in `dictConfig` format.
  - `json_formatter.py`: JSON formatter and filters for stdout/stderr splitting.

Additionally:
- `mdd-hqc-backend/app/core/config.py`: centralized settings (pydantic) that read `.env`.
- `mdd-hqc-backend/app/main.py`: calls `setup_logging()` at startup.
- `<repo_root>/logs/`: directory where persistent logs are written (created automatically if missing).

Additional detail:
- `logging.py` acts as a “composition layer”: it loads the base config from JSON, applies runtime overrides from `config` (env), and only then applies the final config via `logging.config.dictConfig`.
- `json_formatter.py` encapsulates persistent log standardization: it defines a stable JSON schema and avoids “hard to parse” logs (multi-line messages, tracebacks embedded in free-form text, etc.).

### Initialization flow
Logging is initialized at service startup by calling `setup_logging()` from `app/main.py` before the backend starts doing real work. This guarantees:
- any logs emitted during startup, imports, or router loading are captured under the configured pipeline,
- partial configurations do not mix with Python defaults.

Recommended snippet in `app/main.py`:

```python
from app.core.logging.logging import setup_logging

setup_logging()

from fastapi import FastAPI

app = FastAPI()
````

The setup is intended to be idempotent: `setup_logging()` includes a check to avoid reconfiguring logging multiple times (e.g., dev reloads or repeated imports). Conceptually, it checks for:

* an existing `QueueHandler` already attached to the root logger, or
* the presence of the configured handler by name.

### Base configuration (`logging_config.json`)

The configuration is defined via `dictConfig` and is structured as follows.

##### Root logger

* `root.level`: the global level (default `INFO`, but overridable via env).
* `root.handlers`: uses `queue` as the primary handler.

By centralizing handlers on `root`, any logger created via `logging.getLogger(__name__)` can emit events without local handlers; by propagation, events reach root and follow the same pipeline. This also matters for third-party dependencies: with `disable_existing_loggers` set to `false`, external libraries may emit events that pass through the same handlers/formatters.

##### Configured handlers

* `stdout` (`StreamHandler`):

  * receives only logs below `WARNING` (via filter),
  * output: `sys.stdout` (via `ext://sys.stdout`),
  * formatter: `console` (human-readable text).
* `stderr` (`StreamHandler`):

  * receives logs `WARNING` and above (via filter),
  * output defaults to `sys.stderr`,
  * formatter: `console`.
* `file` (`RotatingFileHandler`):

  * writes persistent logs in JSON Lines (`.jsonl`),
  * rotates by size (`maxBytes`) and retains backups (`backupCount`),
  * formatter: `json` (uses `JSONFormatter`).
* `queue` (`QueueHandler`):

  * enqueues log records and dispatches to `stdout`, `stderr`, and `file`.

With `dictConfig`, the `stream` field cannot directly reference a Python object (like `sys.stdout`) because the config is JSON. The special resolver is used instead (e.g., `ext://sys.stdout`).

##### Formatters

* `console`: console text format (timestamp, level, logger name, module and line).
* `json`: serializes a record to JSON (one JSON object per line in the `.jsonl` file).

The console formatter is intended for fast human scanning: it typically includes a timestamp (with timezone), the severity, the logger name, a code location (`module:lineno`), and the message.

##### Filters

* `BelowWarningFilter`: allows only levels `< WARNING` (prevents stdout duplicates).
* `WarningAndAboveFilter`: allows only levels `>= WARNING` (routes anomalies to stderr).

Filters (not only handler levels) enforce a strict split: without the stdout-side filter, `WARNING+` records could appear on both stdout and stderr.

### Output behavior

The system produces three complementary outputs:

1. stdout (normal)

* `DEBUG` and `INFO`

2. stderr (anomalies)

* `WARNING`, `ERROR`, `CRITICAL`
* when exceptions occur, tracebacks should be included (`exc_info=True` or `logger.exception`).

3. file `<repo_root>/logs/<LOG_FILE_NAME>` (persistent)

* everything emitted according to the global level
* JSON Lines format (1 event = 1 JSON line)
* automatic rotation by size

Example: console output

```text
2026-01-27T21:12:33+0000 [INFO] app.api.metrics (metrics:18) - CIM metrics requested: input_path=data/model.xml
```

Example: `.jsonl` output (one line per event)

```json
{"timestamp":"2026-01-27T21:12:33.123456+00:00","level":"INFO","logger":"app.api.metrics","module":"metrics","function":"get_cim_metrics","line":18,"thread":"MainThread","message":"CIM metrics requested: input_path=data/model.xml"}
```

### Supported environment variables

Runtime behavior is controlled through these variables (defined in `app/core/config.py` and shown in `.env.example`):

* `LOG_LEVEL`
  Root logger global level. Allowed values: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`.

* `LOG_FILE_NAME`
  File name under `<repo_root>/logs/` (e.g., `mdd_hqc.jsonl`).

* `LOG_MAX_BYTES`
  Max file size before rotation (e.g., `10485760`).

* `LOG_BACKUP_COUNT`
  Number of rotated backups to keep (e.g., `5`).

`setup_logging()` applies these overrides at runtime before calling `logging.config.dictConfig(...)`.

Example `.env`:

```env
LOG_LEVEL=INFO
LOG_FILE_NAME=mdd_hqc.jsonl
LOG_MAX_BYTES=10485760
LOG_BACKUP_COUNT=5
```

Conceptually, the overrides patch the in-memory configuration dict before `dictConfig`:

```python
logging_configuration_dict["root"]["level"] = config.LOG_LEVEL.upper()

file_handler_config = logging_configuration_dict["handlers"]["file"]
file_handler_config["filename"] = str(log_file_path)
file_handler_config["maxBytes"] = int(config.LOG_MAX_BYTES)
file_handler_config["backupCount"] = int(config.LOG_BACKUP_COUNT)
```

### Usage inside code (project convention)

Each module that needs logging creates a module-level logger:

```python
import logging
logger = logging.getLogger(__name__)
```

Log calls use “lazy formatting” (`%s` placeholders) to avoid interpolation cost when the level is disabled:

```python
logger.info("CIM metrics requested: input_path=%s", request.path)
logger.debug("XML indexes built: path=%s, intentional_types=%s", file_path, len(self._intentional_elements))
logger.warning("Upload rejected: only .xml files allowed, got extension=%s", extension)
logger.error("CIM metrics calculation failed: input_path=%s", request.path, exc_info=True)
```

A typical endpoint pattern includes:

* `INFO` at start (request received) and `INFO` at end (result with key metrics),
* `ERROR` with `exc_info=True` on exceptions,
* `DEBUG` for internal counts (visible when `LOG_LEVEL=DEBUG`).

Example (conceptual):

```python
logger.info("PIM-to-PSM requested: input_path=%s", request.path)
try:
    model = PimToPsm(uvl).transform()
    logger.info("PIM-to-PSM completed: classes=%s", len(model.classes))
except Exception as exc:
    logger.error("PIM-to-PSM failed: input_path=%s, error=%s", request.path, exc, exc_info=True)
    raise
```

### Exceptions and tracebacks

Tracebacks can be included in logs as follows:

* inside an `except` block: `logger.exception("...")` (automatically includes traceback),
* anywhere: `logger.error("...", exc_info=True)`.

Recommended XML parsing example:

```python
try:
    tree = ET.parse(self.file_path)
except ET.ParseError as exc:
    logger.error("XML parse error: path=%s, error=%s", self.file_path, exc, exc_info=True)
    raise
```

### `logs/` directory

`<repo_root>/logs/` is created automatically if it does not exist. It should not be committed to Git (e.g., add it to `.gitignore`) because it is runtime output.

Example `.gitignore`:

```gitignore
mdd-hqc-backend/logs/
logs/
*.log
*.jsonl
```

### `QueueHandler` considerations

`QueueHandler` is used to reduce the impact of logging I/O on the main execution flow:

* application code logs normally,
* the primary handler enqueues records,
* downstream handlers write outside the critical path.

This is especially helpful when:

* log volume is high,
* file logging is enabled,
* blocking I/O should be minimized.

Additional detail: what each piece does

* `QueueHandler`: receives a `LogRecord` and pushes it into a queue (fast operation).
* `QueueListener`: runs in a thread and drains the queue; for each record it dispatches to final handlers (`stdout`, `stderr`, `file`).
* Benefit: the request/worker thread does not wait on file/console flushes.

Conceptual listener startup:

```python
listener.start()
atexit.register(listener.stop)
```

### Persistent log schema (`.jsonl`)

Persistent logs are written in JSON Lines (`.jsonl`), meaning:

* one event equals one JSON object,
* one line equals one event,
* the file is a stream of JSON objects, not a single JSON document.

##### Fields emitted by `JSONFormatter`

`JSONFormatter` builds a base payload and also emits keys according to `fmt_keys` defined in `logging_config.json`.

Base fields:

* `timestamp`: ISO 8601 in UTC (derived from `record.created`),
* `message`: rendered message (`record.getMessage()`).

Optional fields (only if present):

* `exc_info`: serialized traceback (`record.exc_info`),
* `stack_info`: serialized stack info (`record.stack_info`).

Additional fields by configuration (`fmt_keys`) typically include `level`, `logger`, `module`, `function`, `line`, `thread`, and `message`, depending on the mapping in `logging_config.json`.

Compatibility notes:

* `ensure_ascii=False` is used, so UTF-8 characters are preserved without ASCII escaping.

### Logs directory and path resolution

The log file is written to:

* `<repo_root>/logs/<LOG_FILE_NAME>`

Where `<repo_root>` is computed at runtime as:

* `Path(__file__).resolve().parents[3]`

This assumes the current project structure (location of `app/core/logging/logging.py`). If this module moves up/down the tree in the future, the computed repo root can change, and logs may end up in a different directory.

### File rotation and retention

The persistent handler uses `logging.handlers.RotatingFileHandler` with:

* `maxBytes`: maximum size before rotation,
* `backupCount`: number of backups to keep.

Operational effect:

* once the file exceeds `maxBytes`, the active file rolls over and backups are created with incremental suffixes (e.g., `mdd_hqc.jsonl.1`, `mdd_hqc.jsonl.2`, …),
* at most `backupCount` backups are retained, plus the active file.

### Third-party library integration

The config sets:

* `disable_existing_loggers = false`

This means existing loggers (including third-party libraries) are not disabled. As a consequence, logs emitted by dependencies can propagate and be formatted/routed through the project’s root logger pipeline.

### Actual `QueueHandler` behavior in this system

The pipeline declares a `queue` handler of type `logging.handlers.QueueHandler`, and `setup_logging()` contains a startup routine for a `listener` if available.

Documented behavior (matching the implementation):

* `setup_logging()` applies `dictConfig`,
* it attempts to fetch the `"queue"` handler by name via `logging.getHandlerByName("queue")` (if supported by the runtime),
* if the handler exists and exposes a `listener` attribute, it attempts to:

  * start the listener (and avoid failing if already started),
  * register `listener.stop` via `atexit` for graceful shutdown.

The system is prepared to run a “queue + listener” model when a listener is present, and it tolerates environments where no listener exists (startup does not break; it simply does not start an extra thread). This is complemented by `_is_logging_already_configured()` to avoid multiple initializations.

### Minimal repository policy

The `logs/` directory is runtime output and must not be versioned. It should stay out of Git (e.g., `.gitignore`) to avoid committing local log files.

### See also

For deeper detail on Python’s standard logging (`logging`)—including the mental model, `dictConfig`, handlers/formatters/filters, JSON Lines, and queue-based patterns—refer to:

* [Python Logging Guide](./notes/python_logging_guide.md)
