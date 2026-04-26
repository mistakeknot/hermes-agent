# execution-receipts

Passive Hermes execution receipts for reconstructing what happened during an agent run.

This plugin is intentionally disabled by default and passive when enabled. It records `execution_receipt` events emitted by the Hermes agent loop. It does not enforce phase gates, route tools, or claim hard safety.

## Enable

Add the plugin to `plugins.enabled` in the active `HERMES_HOME/config.yaml` profile:

```yaml
plugins:
  enabled:
    - execution-receipts
```

## Storage

Default path:

```text
$HERMES_HOME/execution-receipts/receipts.jsonl
```

Override path for tests or experiments:

```bash
export HERMES_EXECUTION_RECEIPTS_PATH=/tmp/hermes-execution-receipts.jsonl
```

Each line is a JSON receipt with `schema_version: hermes.execution_receipt.v0`. Tool-completion receipts include metadata such as receipt id, receipt type, trace/span identifiers, sequence number, session/task ids, tool name, status, duration, argument keys, result size, redaction metadata, and evidence gaps.

## Slash command

```text
/receipts status
/receipts path
/receipts tail [n]
/receipts gaps
```

## Safety posture

This is a receipt substrate, not an enforcement layer. Hard phase gates still require pre-model-call tool schema filtering and richer profile-scoped policy seams.
