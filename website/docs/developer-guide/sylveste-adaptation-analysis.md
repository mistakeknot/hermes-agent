---
sidebar_position: 22
title: "Sylveste Adaptation Analysis"
description: "Read-only evaluation of Sylveste concepts, modules, and operating patterns worth adapting or exapting into Hermes Agent"
---

# Sylveste Adaptation Analysis for Hermes Agent

Date: 2026-04-24
Status: read-only ecosystem evaluation, converted into a Hermes developer document
Source ecosystem: `/Users/sma/projects/Sylveste`
Target system: `/Users/sma/.hermes/hermes-agent`

## Executive Thesis

Hermes should not become Sylveste or Clavain. Hermes is a general-purpose agent runtime spanning CLI, gateway, cron, ACP, tools, memory, skills, plugins, MCP, providers, delegation, and evals. Sylveste is an opinionated autonomous software-development agency platform.

The highest-value adaptation is therefore not a direct plugin port. It is Sylveste's closed-loop autonomy architecture:

```text
Durable receipts -> evidence -> calibration -> earned authority -> safer autonomy
```

Hermes already has a broad runtime and extension surface. What it lacks is a durable evidence and coordination layer that treats workflow state, quality gates, artifacts, trust, routing decisions, and outcome history as first-class queryable objects.

The recommended approach is plugin-first and sidecar-first:

1. Add passive receipt and event capture using existing Hermes hooks.
2. Add optional run, phase, and gate metadata over existing sessions.
3. Add local analytics for tools, models, costs, retries, and subagents.
4. Add trust and calibration layers only after enough evidence exists.
5. Add adaptive routing and delegated autonomy last, behind canaries and audits.

## Why Sylveste Is Worth Studying

Sylveste's core doctrine is unusually aligned with agent runtime evolution:

- Infrastructure unlocks autonomy.
- Review phases are leverage points.
- Receipts close loops: if it did not produce a receipt, it did not happen.
- Autonomy is a dial, not a binary.
- Authority is earned progressively.
- Mechanism and policy should be separated.
- Small composable tools should have explicit interfaces.
- Human attention is the bottleneck.
- Gates should enable velocity, not bureaucracy.
- Evidence should be independently verifiable.
- Host-specific surfaces should not define the system's identity.

These ideas translate well to Hermes because Hermes already has the extensible runtime surfaces needed to host them: plugin hooks, SessionDB, tools, toolsets, MCP, skills, cron, provider runtime, and subagent delegation.

## What Hermes Already Has

Hermes already provides many of the mechanisms needed for a Sylveste-inspired evidence loop:

- `AIAgent` runtime loop in `run_agent.py`.
- SQLite `SessionDB` in `hermes_state.py`.
- Tool registry and toolsets in `tools/registry.py`, `model_tools.py`, and `toolsets.py`.
- Plugin hooks in `hermes_cli/plugins.py`:
  - `pre_tool_call`
  - `post_tool_call`
  - `transform_terminal_output`
  - `transform_tool_result`
  - `pre_llm_call`
  - `post_llm_call`
  - `pre_api_request`
  - `post_api_request`
  - `on_session_start`
  - `on_session_end`
  - `on_session_finalize`
  - `on_session_reset`
  - `subagent_stop`
  - `pre_gateway_dispatch`
- Blocking capability in `pre_tool_call` hooks.
- Memory providers and durable user/project memory.
- Skills as procedural memory.
- `session_search` for long-term transcript recall.
- `delegate_task` for subagents.
- Cron jobs for autonomous scheduled execution.
- Provider runtime, fallback models, credential pools, and budget/cost fields.
- Trajectory and environment infrastructure for evaluation.
- MCP support for external tools.

Hermes therefore does not need a wholesale orchestration rewrite. It needs a thin, durable governance layer that records what happened, why it happened, what evidence was produced, and how that evidence should influence future behavior.

## Main Gaps Relative to Sylveste

### 1. Receipts are not first-class enough

Hermes stores sessions and messages, but it does not yet expose a typed, queryable receipt model for meaningful actions such as:

- model call started/completed/failed
- tool call allowed/blocked/completed/failed
- file artifact created/modified
- subagent dispatched/completed
- cron job executed/delivered
- policy decision made
- fallback model activated
- gate passed/failed/overridden
- user correction recorded

### 2. Workflow phase is implicit

Hermes skills often instruct agents to discover, plan, implement, verify, review, and ship, but the runtime does not have a durable phase or gate object that can be queried later.

### 3. Trust and routing are not sufficiently empirical

Hermes can route across providers and delegate to subagents, but it does not yet maintain evidence-based scorecards for:

- model quality by task type
- provider reliability by platform
- subagent usefulness
- tool failure rates
- skill usefulness
- memory accuracy
- policy false positives/false negatives

### 4. Multi-agent coordination is mostly social, not structural

Hermes can spawn subagents, but concurrent edits in the same repository need stronger coordination:

- file reservations
- conflict detection
- negotiated release
- commit/push enforcement
- durable dispatch records

### 5. Documentation and memory freshness are not closed-loop

Hermes has memory and docs, but not a fully systematic loop for:

- stale doc detection
- stable memory promotion
- evidence anchors for memory
- decay and archival
- distinguishing independently validated facts from primed/repeated assumptions

## Specific Clavain Flows: `/route` and `/sprint`

The earlier analysis should call these out explicitly. In Clavain, `/route` and `/sprint` are not just convenience commands. They are the user-facing workflow shell around Sylveste's evidence, routing, phase, budget, review, and recovery infrastructure.

### `/route`: universal intake and dispatcher

Clavain's `/route` is the primary entry point. It decides whether the user is trying to resume existing work, select backlog work, classify a bead, start a fresh lifecycle, or dispatch directly to execution.

Key mechanics:

- Active sprint detection and resume before starting anything new.
- Argument parsing for:
  - empty input -> discovery scan
  - bead ID -> inspect bead state and artifacts
  - free text -> classify requested work
  - lane flags -> scoped discovery
- Discovery scan when no explicit work is given.
- Staleness checks for possibly already-implemented beads.
- Context warmth annotation from recent sessions touching related files.
- Bead claiming and session attribution.
- Complexity classification and caching.
- Fast-path deterministic heuristics before LLM routing.
- Haiku fallback only when heuristics lack confidence.
- Dispatch to `/sprint`, `/work`, `/write-plan`, `/strategy`, `/quality-gates`, `/reflect`, or `/sprint-status`.
- Stop immediately after dispatch.

The durable pattern to adapt is:

```text
one entry point -> inspect state -> classify intent -> claim/scope work -> dispatch to the right workflow
```

For Hermes, this should become a Hermes-native route flow, not a Clavain clone. A future Hermes `/route` should inspect:

- current session and parent session lineage
- recent sessions from `session_search`
- current repository state
- dirty files and changed files
- existing plans or artifacts
- open issues from available trackers
- user-provided args
- configured profile/toolsets
- available skills and MCP servers
- provider/model/cost constraints
- receipt/event history when available

Potential Hermes dispatch targets:

- planning: `plan`, `writing-plans`
- debugging: `systematic-debugging`
- implementation: direct tool use or `subagent-driven-development`
- test-first work: `test-driven-development`
- review: `requesting-code-review`
- research: web/search/delegation workflows
- automation: cron job creation/update
- continuation: resume prior session/run/work item
- status: project/workflow health scan

Hermes should copy the shape, not the policy. Do not require beads. Use an adapter model for work items:

- local run records
- GitHub issues
- Linear issues
- beads when present
- plain repo-local plans
- user-supplied free text

### `/sprint`: phase sequencer and evidence-producing lifecycle

Clavain's `/sprint` is the structured execution lifecycle. After the `/route` unification, `/sprint` is intentionally slimmed down into a phase sequencer rather than an intake command.

Key mechanics:

- Exactly 10 steps:
  1. Brainstorm
  2. Strategy
  3. Write Plan
  4. Plan Review
  5. Execute
  6. Test & Verify
  7. Quality Gates
  8. Resolve
  9. Reflect
  10. Ship
- Artifacts are written to disk and consumed by later steps.
- Steps execute in order unless an explicit resume flag is used.
- Checkpoints and gates stop for user approval unless the autonomy tier allows auto-advance.
- Complexity maps to autonomy tier:
  - Tier 1: low-complexity work can auto-advance if review gates are clean.
  - Tier 2: moderate work pauses at key checkpoints.
  - Tier 3: high-complexity work is interactive.
- Review gates run through Interflux and record outcomes for calibration.
- Phase state and artifact paths are recorded after each step.
- Artifact provenance is written per output.
- Budget/cost context is surfaced throughout the lifecycle.
- Test-pass SHA is recorded as an artifact.
- Reflection is a firm gate before shipping.
- Degraded modes define how to continue when subsystems fail.

The durable pattern to adapt is:

```text
phase sequencer -> artifact bus -> gates -> checkpointing -> reflection -> ship receipt
```

For Hermes, this should become an optional software-development workflow, not the default chat mode. A future Hermes sprint flow should probably use fewer default phases, while preserving the important control points:

```text
discover -> plan -> review plan -> implement -> verify -> review -> reflect/record -> ship
```

Hermes-specific sprint mechanics should include:

- `run_id` or `sprint_id` tied to SessionDB and receipt DB records.
- Artifact paths under a configurable project directory.
- Tool and model receipts for every phase.
- Gate records for tests, lint, typecheck, review, docs, and push.
- Optional subagent dispatch with reservation/coordination records.
- Autonomy tiers controlled by profile, complexity, risk, and trust scores.
- Reflection that can promote stable facts into memory or skills only with evidence.
- Resume based on receipts and artifacts, not just conversation context.

### Why these flows matter for Hermes

`/route` and `/sprint` are the missing product shape around the lower-level recommendations in this document.

Without `/route`, users must know whether to ask for planning, debugging, implementation, review, continuation, cron automation, or status scanning. A route flow lets Hermes decide the appropriate operating mode from context.

Without `/sprint`, receipts and gates remain infrastructure without a visible lifecycle. A sprint flow gives Hermes a repeatable way to turn larger software tasks into grounded artifacts, reviews, implementation, verification, reflection, and shipping.

### Recommended priority

These flows should be treated as user-facing adapters over the receipt/gate substrate:

- Build passive receipts first or in parallel.
- Implement a lightweight Hermes `/route` as an advisory skill/command early.
- Implement Hermes `/sprint` only for software-development profiles.
- Do not enforce Clavain's 10-step lifecycle globally.
- Make dispatch explainable: every route decision should emit a receipt with input signals, heuristic/LLM source, confidence, and chosen target.

A minimal Hermes route receipt could look like:

```json
{
  "event_type": "route_decision",
  "input_kind": "free_text|session_resume|work_item|empty",
  "signals": ["dirty_repo", "existing_plan", "bug_keywords"],
  "decision": "debug|plan|implement|review|resume|status|sprint",
  "confidence": 0.86,
  "policy": "heuristic:v1",
  "target": "systematic-debugging"
}
```

A minimal Hermes sprint receipt could look like:

```json
{
  "event_type": "phase_transition",
  "run_id": "...",
  "from_phase": "plan",
  "to_phase": "implement",
  "gate": "plan_review",
  "gate_status": "passed|warned|blocked|overridden",
  "artifacts": ["docs/plans/...md"]
}
```

## Highest-Value Adaptations

## Tier 1: Adapt Soon

### 1. Intercore-style receipt and event ledger

What Sylveste has:

- Durable system of record for runs, phases, gates, dispatches, events, and token budgets.
- SQLite WAL persistence.
- Event-driven phase transitions.
- Mechanism-first design.

What Hermes should take:

- Append-only event records.
- Stable receipt IDs.
- Artifact records with hashes.
- Run and dispatch records.
- Cost and token reconciliation.
- Correlation fields such as `session_id`, `task_id`, `tool_call_id`, `parent_session_id`, `platform`, and `source`.

Hermes mapping:

- Capture events through existing plugin hooks.
- Store in a sidecar SQLite database first.
- Later migrate proven tables into SessionDB if appropriate.

Why it matters:

Everything else depends on durable evidence. Gates, trust scores, routing, analytics, and memory provenance are weak if they are reconstructed from ad hoc transcript text.

Risks:

- Over-designed schema.
- Excessive write volume.
- Secret leakage in captured payloads.

Mitigation:

- Keep v1 minimal.
- Redact or hash sensitive arguments.
- Store summaries and references rather than raw payloads by default.

### 2. Interphase-style optional phases and gates

What Sylveste has:

- Phase tracking over work lifecycle.
- Gate checks before transitions.
- Observability-first defaults.
- Hard fail-closed mode only for high-risk transitions.
- Audited emergency overrides.

What Hermes should take:

- Optional workflow phases:
  - discover
  - plan
  - implement
  - verify
  - review
  - ship
  - reflect
- Gate records:
  - tests run
  - lint/typecheck run
  - code review completed
  - docs updated
  - file reservations released
  - push completed
- Advisory gates by default.
- Hard gates only for explicitly configured risky actions.

Hermes mapping:

- Use skills for default behavior.
- Use `pre_tool_call` hooks for warnings or blocks.
- Store gate evaluations in the event ledger.

Why it matters:

Hermes already has excellent procedural skills. Optional phase/gate state makes those procedures measurable and auditable.

Risks:

- Workflow friction.
- Over-constraining normal chat usage.

Mitigation:

- Keep gates profile-scoped and opt-in.
- Default to warning, not blocking.

### 3. Tool-time and Interstat-style local analytics

What Sylveste has:

- Tool usage telemetry.
- Error and rejection rate tracking.
- Edit-without-read detection.
- Bash dominance detection.
- Tool diversity metrics.
- Cost and token efficiency reporting.

What Hermes should take:

- Local-only usage analytics over SessionDB and receipts.
- Reports for:
  - tool failures
  - retries
  - rejected/blocked calls
  - terminal overuse
  - file-edit-before-read patterns
  - subagent overuse/underuse
  - cost per task family
  - provider fallback rate

Hermes mapping:

- Most capture points already exist in plugin hooks and SessionDB.
- Add reporting commands such as:
  - `hermes stats tools`
  - `hermes stats models`
  - `hermes stats cost`
  - `hermes doctor usage`

Why it matters:

Hermes has strong behavioral instructions. Analytics can verify whether agents actually follow them.

Risks:

- Privacy concerns.
- Goodharting shallow metrics.

Mitigation:

- Keep local by default.
- Make sharing opt-in and allow-list based.
- Use metrics as signals, not absolute truth.

### 4. Interspect and Intertrust-style calibration

What Sylveste has:

- Agent/reviewer scoring from accepted and discarded findings.
- Severity weighting.
- Time decay.
- Project/global blending.
- Canary windows for routing changes.

What Hermes should take:

- Trust scores for tools, subagents, skills, memory, and models.
- Manual correction events.
- Canary windows for policy or routing changes.
- Advisory recommendations before automatic behavior changes.

Hermes mapping:

- Use `post_tool_call`, `post_llm_call`, `subagent_stop`, and `on_session_end` hooks.
- Store feedback and correction events in the receipt ledger.
- Report candidate routing/policy changes before enforcing them.

Why it matters:

Hermes delegates and routes, but should learn from whether those decisions were useful.

Risks:

- Weak or noisy labels.
- Accidental entrenchment of bad defaults.

Mitigation:

- Require explicit correction/evidence for promotion.
- Use canaries and decay.
- Keep overrides reversible.

## Tier 2: Adapt After Receipts Exist

### 5. Interflux and FluxBench-style model qualification

What Sylveste has:

- Multi-agent review with triage.
- Domain-specific review agents.
- Budget-aware dispatch.
- Model lifecycle: candidate -> qualifying -> qualified -> active -> retired.
- Gates for format compliance, finding recall, false positives, severity accuracy, and persona adherence.

What Hermes should take:

- Model qualification registry.
- Task-family benchmark suites.
- Shadow and challenger runs.
- Promotion/demotion based on evidence.
- Routing by quality, cost, latency, and reliability.

Hermes mapping:

- Start in `environments/` and `batch_runner.py` workflows.
- Use existing trajectory support.
- Use `delegate_task` for shadow reviews.
- Integrate with provider runtime only after scorecards are reliable.

Why it matters:

Hermes supports many providers and fallback models. Evidence-based routing is the natural next step.

Risks:

- Premature adaptive routing.
- Overfitting to benchmark tasks.

Mitigation:

- Keep routing advisory at first.
- Track real-world outcomes separately from benchmark outcomes.

### 6. Multi-agent review council patterns

What Sylveste has:

- Review agent roster: architecture, safety, correctness, performance, product, quality, and cognitive lenses.
- Triage to decide which agents fire.
- Dropout to avoid redundant launches.
- Shared findings and synthesis.

What Hermes should take:

- A review council skill/plugin using `delegate_task`.
- Role templates as skills.
- Mandatory triage before delegation.
- Budget-aware agent selection.
- Final synthesis and deduplication.

Hermes mapping:

- Existing `delegate_task` is enough for v1.
- Persist dispatches and findings in receipts.
- Use model overrides later when qualification data exists.

Why it matters:

Hermes has delegation infrastructure. Sylveste contributes disciplined delegation topology.

Risks:

- Token explosion.
- Duplicate findings.

Mitigation:

- Sparse delegation by default.
- Require triage and synthesis.

### 7. Interlab-style experiment campaigns

What Sylveste has:

- Experiment initialization, execution, and logging.
- JSONL state reconstruction.
- Git isolation.
- Simple `METRIC` protocol.
- Circuit breakers for crashes, no-improvement runs, and experiment count.

What Hermes should take:

- Lightweight experiment campaigns for agent/runtime improvements.
- Metric-line protocol for easy benchmark integration.
- Mutation provenance.
- Circuit breakers and rollback requirements.

Hermes mapping:

- Start as a skill plus scripts.
- Later become a Hermes plugin or MCP server.
- Connect to trajectory/eval infrastructure.

Why it matters:

Hermes has eval infrastructure, but it could use a practical day-to-day improvement loop.

Risks:

- Unsafe self-modification.
- Poor benchmark design.

Mitigation:

- Require rollback.
- Require quality gates.
- Keep campaigns scoped and bounded.

## Tier 3: Exapt as Optional Integrations

### 8. tldr-swinton for token-efficient code context

What Sylveste has:

- AST, call graph, CFG, DFG, and program slicing.
- Diff-context extraction.
- Semantic search.
- Code structure summaries.
- Context packs.

What Hermes should take:

- Optional MCP integration.
- Context-engine plugin integration.
- Skill rule: use static context tools before broad file sweeps when available.

Hermes mapping:

- Integrate through MCP or a context-engine plugin.
- Keep `read_file` and `search_files` as fallback.

Why it matters:

Hermes spends tokens reading code. Static slicing can sharply reduce context load on large repos.

Risks:

- Heavy dependencies.
- Index staleness.
- Language coverage variance.

Mitigation:

- Keep optional.
- Include freshness checks.

### 9. Intercache and Intersearch ideas for context reuse

What Sylveste has:

- Content-addressed blob cache.
- Per-project manifests.
- Session tracking.
- Cache warming.
- Semantic search separated into a dedicated module.

What Hermes should take:

- File-read receipts with path, hash, mtime, and size.
- Hot-file prefetch suggestions.
- Session-to-session context warming.
- Optional cache-aware context engine.

Hermes mapping:

- Start by recording file read/search patterns.
- Later add pre-LLM context suggestions.
- Avoid changing file tool semantics until proven safe.

Why it matters:

Hermes often returns to the same projects. Cross-session context reuse can improve speed and cost.

Risks:

- Stale cache reads.
- Secret retention.

Mitigation:

- Hash validation.
- Explicit invalidation.
- Secret redaction and retention controls.

### 10. Interknow and Intermem for provenance-aware memory

What Sylveste has:

- Durable knowledge records with frontmatter.
- Evidence anchors.
- Provenance and `lastConfirmed` fields.
- Memory promotion workflows.
- Deduplication and validation.

What Hermes should take:

- Memory confidence and provenance.
- Staleness/decay tracking.
- Stable fact promotion from sessions to memory.
- Distinction between independently validated facts and repeated prompt assumptions.

Hermes mapping:

- Build as a memory-provider plugin.
- Keep built-in memory curated and compact.
- Use `session_search` and receipts as evidence sources.

Why it matters:

Hermes memory is valuable but intentionally compact. Provenance and decay would make it safer to trust.

Risks:

- Memory bloat.
- Auto-promoting false facts.

Mitigation:

- Human approval for persistent facts.
- Evidence anchors.
- Decay and archive policies.

### 11. Interdoc and Interwatch for documentation hygiene

What Sylveste has:

- Recursive `AGENTS.md` generation/update.
- Dry-run and diff preview.
- Drift detection from changes, renames, version bumps, stale counts, broken references, and commits since update.

What Hermes should take:

- Documentation freshness checks.
- Cross-AI `AGENTS.md`/developer-doc update workflow.
- Drift signal registry.
- Preview-only doc updates by default.

Hermes mapping:

- Start as a skill or cron job.
- Later add a plugin that can inspect docs against source reality.

Why it matters:

Hermes has many docs, skills, plugins, and runtime surfaces. Drift is inevitable without explicit monitoring.

Risks:

- Bland auto-generated docs.
- Incorrect automated rewrites.

Mitigation:

- Dry-run first.
- Human review before write.
- Favor deterministic corrections.

### 12. Interlock and Intermute for subagent file coordination

What Sylveste has:

- File reservations.
- Conflict detection.
- Inter-agent messaging.
- Negotiated release.
- Advisory edit hook and mandatory pre-commit enforcement.

What Hermes should take:

- Optional file reservations for parallel subagents.
- Conflict preflight for subagent-driven development.
- Pre-commit or pre-push safety around reserved files.
- Durable dispatch and ownership records.

Hermes mapping:

- Start inside `delegate_task` orchestration.
- Store reservations in a sidecar DB.
- Enforce at commit/push boundaries before enforcing edits.

Why it matters:

Hermes subagents have isolated terminal sessions but can still collide in a shared working tree.

Risks:

- Deadlocks.
- Annoying false conflicts.

Mitigation:

- Cooperative reservations with TTLs.
- Warnings before hard blocks.

## Tier 4: Useful but Lower Priority

### 13. Tuivision for TUI testing

What Sylveste has:

- MCP server for TUI automation.
- Spawn TUI, send input, inspect screen, screenshot, resize, list, close.

What Hermes should take:

- Optional TUI regression testing for `ui-tui/` and CLI flows.

Why lower priority:

Useful for Hermes' own UI quality, but not central to the evidence/trust architecture.

### 14. Intertrace and Intermap for integration-gap analysis

What Sylveste has:

- Trace changed files from a bead.
- Inspect events, contracts, and companion graph.
- Rank gaps by evidence strength.

What Hermes should take:

- Integration-gap checks for plugin/toolset/provider/gateway changes.

Why lower priority:

It requires declared contracts and companion edges first.

### 15. Interlore-style philosophy drift detection

What Sylveste has:

- Observes decisions and detects doctrine drift.

What Hermes should take later:

- Detect repeated conflicts among `AGENTS.md`, skills, docs, and user corrections.
- Propose doctrine updates when patterns recur.

Why lower priority:

It becomes more useful after receipts and correction events exist.

## What Not To Copy

### Do not copy the whole Clavain lifecycle

Clavain is an autonomous software agency. Hermes is a general agent runtime. Hermes should support Clavain-like workflows without forcing all users into them.

### Do not make beads mandatory

Beads fits Sylveste. Hermes should support generic work items and adapters for GitHub, Linear, beads, local SQLite, and project-specific trackers.

### Do not rewrite `AIAgent` around an Intercore clone

Use an overlay first. Hermes has enough plugin hooks to test the design passively before core integration.

### Do not use memory as the receipt log

Memory is curated recall. Receipts are immutable evidence. Mixing them will pollute prompts and weaken auditability.

### Do not make strict gates the default

Strict gates should be opt-in, scoped, and reserved for high-risk transitions. The default should be observability and advisory warnings.

### Do not port Claude Code-specific assumptions directly

Many Sylveste modules assume Claude Code paths, hooks, and plugin layouts. Hermes should translate these into Hermes-native concepts:

- `HERMES_HOME` instead of `~/.claude`
- Hermes plugin hooks instead of Claude hooks
- SessionDB and receipt DB instead of transcript scraping
- Hermes skills/toolsets/MCP instead of Claude-specific command surfaces

### Do not optimize cost without quality

Cost only matters with quality held constant. Hermes should optimize outcome per dollar, not dollars alone.

## Proposed Roadmap

### Phase 1: Evidence Overlay

Goal: create the durable substrate.

Deliverables:

- `hermes-receipts` plugin or core sidecar.
- Append-only events from session, tool, API, LLM, gateway, and subagent hooks.
- Receipts for tool calls, model calls, file writes, terminal commands, approvals/denials, fallbacks, cron runs, and subagent results.
- Artifact records with path, hash, size, and creating event.

Default behavior:

- Passive capture only.
- No blocking.
- No routing changes.

### Phase 2: Run, Phase, and Gate Layer

Goal: make workflows visible.

Deliverables:

- Optional `run_id` per task/session.
- Optional phase state.
- Gate evaluation records.
- Advisory warnings for missing gates.
- Configurable hard gates for risky actions.

### Phase 3: Analytics and Reports

Goal: turn receipts into insight.

Deliverables:

- Tool stats.
- Model/provider stats.
- Cost stats.
- Usage doctor.
- Weekly cron summary.
- Failure/retry/rejection rates.
- Pattern detection for terminal overuse, edit-without-read, and unused subagent output.

### Phase 4: Trust and Calibration

Goal: improve decisions from evidence.

Deliverables:

- Tool trust scores.
- Subagent trust scores.
- Skill usefulness signals.
- Model scorecards by task family.
- Manual correction records.
- Canary windows for policy changes.

### Phase 5: Adaptive Routing

Goal: route empirically.

Deliverables:

- Model qualification registry.
- Shadow/challenger runs.
- Promotion/demotion criteria.
- Cost/quality/reliability profiles by task family.
- Runtime provider integration after advisory mode proves reliable.

### Phase 6: Knowledge and Documentation Compounding

Goal: keep learned context fresh and grounded.

Deliverables:

- Provenance-aware memory provider.
- Stable memory promotion workflow.
- Documentation drift scanner.
- Knowledge entries with evidence anchors and decay.

## Best First Implementation Slice

Name: `hermes-receipts`

Scope: passive plugin that records events and receipts without changing behavior.

Suggested storage path:

```text
$HERMES_HOME/receipts/receipts.db
```

Suggested tables:

- `events`
- `receipts`
- `artifacts`
- `runs`
- `dispatches`
- `gate_evaluations`

Suggested hooks:

- `on_session_start`
- `on_session_end`
- `pre_api_request`
- `post_api_request`
- `pre_tool_call`
- `post_tool_call`
- `subagent_stop`
- `pre_gateway_dispatch`

Suggested commands:

- `hermes receipts status`
- `hermes receipts tail`
- `hermes receipts session <id>`
- `hermes receipts summarize --since 7d`
- `hermes receipts export --format jsonl`

Success criteria after one week of normal use:

- We can identify the highest-failure tools.
- We can identify fallback-prone providers/models.
- We can list files changed by a session.
- We can attribute artifacts to tool calls or subagents.
- We can summarize cron job activity and delivery.
- We can estimate cost by task family.
- We can find actions that lack receipts.

## Prioritized Recommendation List

| Priority | Recommendation | Impact | Effort | Risk |
| --- | --- | --- | --- | --- |
| P0 | Build passive receipt/event store | Very high | Medium | Low |
| P0 | Add lightweight Hermes `/route` advisory flow | Very high | Medium | Medium |
| P0 | Add artifact hashing for file writes and patches | High | Low-medium | Low |
| P0 | Add analytics over tool/model/session outcomes | High | Low-medium | Low |
| P1 | Add optional phase/gate workflow state | High | Medium | Medium |
| P1 | Add software-development `/sprint` phase sequencer | High | Medium-high | Medium |
| P1 | Add manual correction/evidence events | High | Medium | Low |
| P1 | Add trust scores for tools, subagents, skills, and models | High | Medium | Medium |
| P1 | Add doc drift checker for Hermes docs/skills/plugins | Medium-high | Medium | Low |
| P2 | Add FluxBench-like model qualification registry | Very high | High | Medium-high |
| P2 | Add tldr-swinton optional integration/context engine | Medium-high | Medium | Medium |
| P2 | Add Interlab-like experiment campaigns | High | Medium-high | High |
| P3 | Add file reservations for parallel subagents | Medium | Medium | Medium |
| P3 | Add Tuivision optional TUI testing | Medium | Medium | Low-medium |

## Design Principles for the Hermes Adaptation

1. Mechanism before policy.
2. Passive observation before enforcement.
3. Advisory gates before hard gates.
4. Human correction before automatic authority changes.
5. Local-first telemetry.
6. Redaction before persistence.
7. Profile-scoped behavior.
8. Optional integrations before core dependencies.
9. Reversible routing and policy changes.
10. Outcome metrics over proxy metrics.

## Strategic Conclusion

Sylveste's strongest contribution to Hermes is not a particular plugin. It is an operating doctrine for trustworthy autonomy:

```text
Durable receipts -> evidence -> calibration -> earned authority
```

Hermes already has the general-purpose runtime and extension surfaces needed to host this doctrine. The most valuable next step is a passive receipt/event layer that can later support analytics, gates, trust scores, adaptive routing, memory provenance, and documentation freshness.

Alignment: this supports Hermes' existing architecture: platform-agnostic core, loose coupling, profile isolation, plugin hooks, SessionDB, skills, cron, delegation, provider runtime, and eval environments.

Conflict/Risk: the main risk is importing too much Clavain/Sylveste product opinion into Hermes' general runtime. Keep mechanisms generic, policies optional, telemetry local-first, and strict autonomy auditable.
