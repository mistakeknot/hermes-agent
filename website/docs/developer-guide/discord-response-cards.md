---
sidebar_position: 8
title: "Discord Response Cards"
description: "Contract for compact Hermes Discord cards and button affordances"
---

# Discord Response Cards

Hermes can render compact Discord response cards with optional platform-native buttons when an assistant response includes an explicit visible fallback line.

The feature is intentionally narrow: a button click is equivalent to the user typing the selected label back into the same Hermes session. It is not a Discord management API, a hidden workflow dispatcher, or a way to run privileged actions directly.

## Card shape

Use a card when the next useful operator action can be expressed as one question with two to four answers.

```md
**<State> — <topic>**

**Recommendation:** <one clear next move>
**Why:**
- <reason 1>
- <reason 2, optional>
**Risk/approval:** <none | approval needed because ...>

Buttons: [Proceed] [Adjust] [More detail] [Stop]
```

Rules:

- One recommendation, one question, two to four options.
- Keep button labels short, human-readable, and safe as plain text.
- Preserve the `Buttons:` text line as fallback for transcripts and surfaces without component support.
- Do not use buttons for arbitrary command execution, broad Discord management, or hidden dispatch.
- If a decision has more than four meaningful branches, show the top recommendation plus `Show options` rather than rendering a crowded card.

## Canonical button sets

### Approval / side effects

```md
Buttons: [Proceed] [Adjust] [Defer] [Stop]
```

Use when Hermes needs operator confirmation before meaningful side effects such as committing, pushing, or starting a bounded implementation lane.

### What next / status

```md
Buttons: [Do recommended next] [Show options] [Handoff packet] [Pause]
```

Use for pickup and next-lane requests where Hermes has enough evidence to recommend one move.

### Review output

```md
Buttons: [Patch blockers] [Accept findings] [Run second review] [Summarize only]
```

Use when review results need reintegration, not when the system should blindly accept external findings.

### Routing

```md
Buttons: [Hermes] [Claude Code] [Codex/Oracle] [More context]
```

Use for recommendation-first routing cards. Do not dispatch the selected body directly unless a separate approved workflow explicitly does so.

## Discord component behavior

On Discord, Hermes may attach native buttons when a response contains a valid `Buttons:` line with two to four bracketed labels.

Click behavior:

1. The click is authorized with the same allowlist posture used by Discord interactive controls.
2. Bot accounts are rejected so another bot cannot route synthetic operator choices.
3. The original message is edited to show the selected option and disable the buttons.
4. The selected label is routed back into the same Discord session as a normal user message.
5. If the card is already resolved, expired, or unauthorized, Hermes sends an ephemeral notice and does not route a new message.

Choice cards are intentionally short-lived non-persistent views: they time out after about five minutes and do not survive a gateway restart. Button labels must be plain text and must not start with `/` or `!`.

This is a response affordance: it is equivalent to the user typing the selected label. It is not a broad Discord management API and is not exposed through `tools/discord_tool.py`.

## Anti-patterns

Avoid:

- open-ended `What do you want to do?` when a recommended next move is available;
- five-plus options in one card;
- buttons whose labels hide destructive or privileged actions;
- dispatching Claude Code, Codex, Oracle, shell commands, or Discord management directly from a card click;
- raw prompt examples or sensitive transcript excerpts in docs.

## Example

```md
**Next — implementation closeout**

**Recommendation:** Run the focused tests before committing.
**Why:**
- The change affects Discord delivery behavior.
- A small regression test gives reviewers confidence that fallback text remains visible.
**Risk/approval:** No privileged action is triggered by the button itself.

Buttons: [Run tests] [Adjust] [Handoff] [Pause]
```
