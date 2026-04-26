"""Passive Hermes execution receipt recorder.

This plugin persists execution receipts emitted by the Hermes agent loop. It is
intentionally passive: hooks must never block execution, and persisted receipts
carry metadata only unless an upstream emitter deliberately adds sanitized
preview fields.
"""

from __future__ import annotations

import json
import os
import re
import threading
from collections import Counter
from pathlib import Path
from typing import Any, Iterable

from hermes_constants import get_hermes_home

SCHEMA_VERSION = "hermes.execution_receipt.v0"
DEFAULT_TAIL = 5
_LOCK = threading.Lock()

_SECRET_KEY_RE = re.compile(
    r"(^|[_-])(api[_-]?key|access[_-]?token|refresh[_-]?token|auth[_-]?token|authorization|password|secret|credential)([_-]|$)",
    re.IGNORECASE,
)
_SECRET_VALUE_PATTERNS = (
    re.compile(r"(?i)bearer\s+[A-Za-z0-9._~+/=-]+"),
    re.compile(r"sk-[A-Za-z0-9_-]{12,}"),
)


def _receipt_path() -> Path:
    override = os.getenv("HERMES_EXECUTION_RECEIPTS_PATH", "").strip()
    if override:
        return Path(override).expanduser()
    return get_hermes_home() / "execution-receipts" / "receipts.jsonl"


def _is_secret_key(key: Any) -> bool:
    return isinstance(key, str) and bool(_SECRET_KEY_RE.search(key))


def _redact_string(value: str) -> str:
    redacted = value
    for pattern in _SECRET_VALUE_PATTERNS:
        redacted = pattern.sub("[REDACTED]", redacted)
    return redacted


def _sanitize(value: Any) -> Any:
    if isinstance(value, dict):
        sanitized: dict[str, Any] = {}
        for key, item in value.items():
            str_key = str(key)
            sanitized[str_key] = "[REDACTED]" if _is_secret_key(str_key) else _sanitize(item)
        return sanitized
    if isinstance(value, (list, tuple, set)):
        return [_sanitize(item) for item in value]
    if isinstance(value, str):
        return _redact_string(value)
    if isinstance(value, (int, float, bool)) or value is None:
        return value
    return _redact_string(repr(value))


def _coerce_receipt(receipt: Any) -> dict[str, Any] | None:
    if not isinstance(receipt, dict):
        return None
    sanitized = _sanitize(receipt)
    sanitized.setdefault("schema_version", SCHEMA_VERSION)
    sanitized.setdefault("evidence_gaps", [])
    return sanitized


def _append_jsonl(receipt: dict[str, Any]) -> None:
    line = json.dumps(receipt, ensure_ascii=False, sort_keys=True, default=str)
    path = _receipt_path()
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    with _LOCK:
        fd = os.open(path, os.O_APPEND | os.O_CREAT | os.O_WRONLY, 0o600)
        with os.fdopen(fd, "a", encoding="utf-8") as fh:
            fh.write(line + "\n")


def _safe_write_receipt(receipt: Any) -> None:
    try:
        coerced = _coerce_receipt(receipt)
        if coerced is None:
            return
        _append_jsonl(coerced)
    except Exception:
        # Receipt storage is passive and must never affect agent execution.
        return


def _on_execution_receipt(**payload: Any) -> None:
    _safe_write_receipt(payload.get("receipt"))


def _load_receipts() -> tuple[list[dict[str, Any]], int]:
    path = _receipt_path()
    if not path.exists():
        return [], 0
    receipts: list[dict[str, Any]] = []
    malformed = 0
    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                parsed = json.loads(line)
            except json.JSONDecodeError:
                malformed += 1
                continue
            if isinstance(parsed, dict):
                receipts.append(parsed)
            else:
                malformed += 1
    return receipts, malformed


def _tail_lines(lines: Iterable[str], n: int) -> list[str]:
    buf: list[str] = []
    for line in lines:
        buf.append(line.rstrip("\n"))
        if len(buf) > n:
            buf.pop(0)
    return buf


_HELP = """\
/receipts — passive Hermes execution receipts

Subcommands:
  status          Count receipts, statuses, and evidence gaps
  path            Show the JSONL receipt path
  tail [n]        Show the last n receipt JSON lines (default 5)
  gaps            Show evidence-gap counts only

Environment:
  HERMES_EXECUTION_RECEIPTS_PATH  Override receipt JSONL path
"""


def _format_status() -> str:
    receipts, malformed = _load_receipts()
    path = _receipt_path()
    if not receipts:
        suffix = f" Malformed lines skipped: {malformed}." if malformed else ""
        return f"No execution receipts yet. Path: {path}.{suffix}"
    types = Counter(r.get("receipt_type", "unknown") for r in receipts)
    statuses = Counter(r.get("status", "unknown") for r in receipts)
    gaps = Counter(
        gap
        for receipt in receipts
        for gap in receipt.get("evidence_gaps", [])
    )
    lines = [
        f"Execution receipts: {len(receipts)} event(s)",
        f"Path: {path}",
        "Receipt types:",
    ]
    for receipt_type, count in sorted(types.items()):
        lines.append(f"  {receipt_type}: {count}")
    lines.append("Statuses:")
    for status, count in sorted(statuses.items()):
        lines.append(f"  {status}: {count}")
    if gaps:
        lines.append("Evidence gaps:")
        for gap, count in sorted(gaps.items()):
            lines.append(f"  {gap}: {count}")
    if malformed:
        lines.append(f"Malformed lines skipped: {malformed}")
    return "\n".join(lines)


def _format_gaps() -> str:
    receipts, malformed = _load_receipts()
    gaps = Counter(
        gap
        for receipt in receipts
        for gap in receipt.get("evidence_gaps", [])
    )
    if not gaps:
        suffix = f" Malformed lines skipped: {malformed}." if malformed else ""
        return f"No evidence gaps recorded.{suffix}"
    lines = [f"{gap}: {count}" for gap, count in sorted(gaps.items())]
    if malformed:
        lines.append(f"malformed_lines_skipped: {malformed}")
    return "\n".join(lines)


def _format_tail(raw_args: str) -> str:
    argv = raw_args.split()
    n = DEFAULT_TAIL
    if len(argv) > 1:
        try:
            n = max(1, min(50, int(argv[1])))
        except ValueError:
            return "Usage: /receipts tail [n]"
    path = _receipt_path()
    if not path.exists():
        return f"No receipt file at {path}"
    with path.open("r", encoding="utf-8") as fh:
        tail = _tail_lines(fh, n)
    return "\n".join(tail) if tail else f"No receipt lines at {path}"


def _handle_command(raw_args: str) -> str:
    raw_args = (raw_args or "").strip()
    if not raw_args or raw_args in {"help", "-h", "--help"}:
        return _HELP
    subcommand = raw_args.split()[0]
    if subcommand == "path":
        return str(_receipt_path())
    if subcommand == "status":
        return _format_status()
    if subcommand == "gaps":
        return _format_gaps()
    if subcommand == "tail":
        return _format_tail(raw_args)
    return f"Unknown subcommand: {subcommand}\n\n{_HELP}"


def register(ctx) -> None:
    ctx.register_hook("execution_receipt", _on_execution_receipt)
    ctx.register_command(
        "receipts",
        handler=_handle_command,
        description="Inspect passive Hermes execution receipts.",
    )
