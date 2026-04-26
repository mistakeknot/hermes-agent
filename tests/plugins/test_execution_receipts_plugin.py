import json

import yaml

from hermes_cli.plugins import PluginManager


SCHEMA_VERSION = "hermes.execution_receipt.v0"


def _enable_execution_receipts(home):
    home.mkdir(parents=True, exist_ok=True)
    (home / "config.yaml").write_text(
        yaml.safe_dump({"plugins": {"enabled": ["execution-receipts"]}}),
        encoding="utf-8",
    )


def _load_manager(tmp_path, monkeypatch):
    monkeypatch.setenv("HERMES_HOME", str(tmp_path))
    monkeypatch.delenv("HERMES_EXECUTION_RECEIPTS_PATH", raising=False)
    _enable_execution_receipts(tmp_path)
    manager = PluginManager()
    manager.discover_and_load(force=True)
    loaded = manager._plugins.get("execution-receipts")
    assert loaded is not None
    assert loaded.enabled, loaded.error
    return manager


def _sample_receipt(**overrides):
    receipt = {
        "schema_version": SCHEMA_VERSION,
        "receipt_id": "receipt-1",
        "receipt_type": "tool_complete",
        "trace_id": "trace-1",
        "span_id": "span-1",
        "parent_span_id": None,
        "sequence_number": 1,
        "session_id": "session-1",
        "task_id": "task-1",
        "tool_call_id": "call-1",
        "tool_name": "web_search",
        "status": "ok",
        "duration_ms": 12,
        "timestamp": "2026-04-25T00:00:00.000Z",
        "args_metadata": {"keys": ["query"], "redacted": True},
        "result_metadata": {"size_chars": 24, "redacted": True},
        "redaction": {"strategy": "metadata_only", "preview_included": False},
        "evidence_gaps": [],
    }
    receipt.update(overrides)
    return receipt


def _receipt_lines(home):
    path = home / "execution-receipts" / "receipts.jsonl"
    assert path.exists()
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def test_execution_receipts_is_disabled_by_default(tmp_path, monkeypatch):
    monkeypatch.setenv("HERMES_HOME", str(tmp_path))
    (tmp_path / "config.yaml").write_text(
        yaml.safe_dump({"plugins": {"enabled": []}}),
        encoding="utf-8",
    )

    manager = PluginManager()
    manager.discover_and_load(force=True)

    loaded = manager._plugins.get("execution-receipts")
    assert loaded is not None
    assert not loaded.enabled
    assert "not enabled" in (loaded.error or "")
    assert "receipts" not in manager._plugin_commands


def test_execution_receipts_records_execution_receipt_with_redaction(tmp_path, monkeypatch):
    manager = _load_manager(tmp_path, monkeypatch)

    receipt = _sample_receipt(
        args_metadata={"keys": ["query", "api_key"], "api_key": "sk-test-secret-value"},
        result_metadata={"size_chars": 24, "authorization": "Bearer abc123"},
    )
    manager.invoke_hook("execution_receipt", receipt=receipt)

    receipts = _receipt_lines(tmp_path)
    assert len(receipts) == 1
    recorded = receipts[0]
    assert recorded["schema_version"] == SCHEMA_VERSION
    assert recorded["receipt_type"] == "tool_complete"
    assert recorded["session_id"] == "session-1"
    assert recorded["tool_name"] == "web_search"
    assert recorded["status"] == "ok"
    assert recorded["args_metadata"]["api_key"] == "[REDACTED]"
    assert recorded["result_metadata"]["authorization"] == "[REDACTED]"
    assert "sk-test-secret-value" not in json.dumps(recorded)
    assert "Bearer abc123" not in json.dumps(recorded)


def test_execution_receipts_command_reports_status_and_gaps(tmp_path, monkeypatch):
    manager = _load_manager(tmp_path, monkeypatch)

    manager.invoke_hook(
        "execution_receipt",
        receipt=_sample_receipt(
            status="error",
            evidence_gaps=["parent_span_unavailable", "child_session_id_unavailable"],
        ),
    )

    handler = manager._plugin_commands["receipts"]["handler"]
    status = handler("status")
    assert "Execution receipts: 1 event(s)" in status
    assert "tool_complete: 1" in status
    assert "error: 1" in status
    assert "child_session_id_unavailable: 1" in status

    gaps = handler("gaps")
    assert "parent_span_unavailable: 1" in gaps
    assert "child_session_id_unavailable: 1" in gaps

    tail = handler("tail 1")
    receipt = json.loads(tail)
    assert receipt["receipt_type"] == "tool_complete"
    assert receipt["session_id"] == "session-1"


def test_execution_receipts_respects_path_override(tmp_path, monkeypatch):
    custom_path = tmp_path / "custom" / "receipts.jsonl"
    manager = _load_manager(tmp_path, monkeypatch)
    monkeypatch.setenv("HERMES_EXECUTION_RECEIPTS_PATH", str(custom_path))

    manager.invoke_hook("execution_receipt", receipt=_sample_receipt(receipt_id="receipt-2"))

    assert custom_path.exists()
    receipt = json.loads(custom_path.read_text(encoding="utf-8").strip())
    assert receipt["schema_version"] == SCHEMA_VERSION
    assert receipt["receipt_id"] == "receipt-2"


def test_execution_receipts_ignores_malformed_hook_payload(tmp_path, monkeypatch):
    manager = _load_manager(tmp_path, monkeypatch)

    manager.invoke_hook("execution_receipt", receipt="not-a-receipt")

    assert not (tmp_path / "execution-receipts" / "receipts.jsonl").exists()
