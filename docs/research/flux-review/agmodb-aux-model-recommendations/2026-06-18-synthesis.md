---
artifact_type: review-synthesis
method: flux-review
target: "/Users/sma/.hermes/hermes-agent/.hermes/plans/2026-06-18_103124-agmodb-aux-model-recommendations.md"
target_description: "AgMoDB-backed Hermes auxiliary model recommendations plan"
tracks: 4
track_a_agents: [hermes-architecture, agmodb-data-contract, desktop-ux]
track_b_agents: [package-resolver, marketplace-trust, security-privacy]
track_c_agents: [clinical-formulary, cartography-navigation]
track_d_agents: [manuscript-provenance]
date: 2026-06-18
---

# Flux-Review Synthesis — AgMoDB Auxiliary-Model Recommendations Plan

**Overall verdict:** **Needs changes before implementation.**

All tracks converged on the same core issue: the current plan treats recommendations as lightweight UI hints, but the feature actually needs a **profile-scoped, provenance-aware, resolver-backed recommendation system** before it is safe and trustworthy to expose with one-click Apply.

> Caveat: This was executed in Hermes using `delegate_task` subagents after reading the Interflux `/flux-review` command and `flux-review-engine` protocol from `/Users/sma/projects/Sylveste/interverse/interflux`. It follows the adjacent → orthogonal → distant → esoteric track structure, but did not invoke Claude Code's slash-command runtime directly.

---

## Critical Findings (P0/P1)

### P0

No P0 was identified. The feature is advisory and user-applied, so no track found an immediate data-loss/security-blocking issue if implementation is deferred until the gaps below are resolved.

### P1 — Ranked

1. **Profile scoping is mandatory**
   - Recommendations, availability checks, Apply actions, cache reads, and endpoint behavior must be scoped to the active Hermes profile.
   - Independently raised by Hermes architecture, Desktop UX, and cartography/navigation tracks.
   - Without this, recommendations can be evaluated or applied against the wrong provider state or auxiliary assignments.

2. **Provider/model identity contract is not safe enough**
   - AgMoDB must not publish a generic model string plus loose `provider_candidates` as the Apply substrate.
   - It needs canonical, provider-specific Hermes model coordinates, exact provider/task enums, and preservation of original vs resolved identifiers.
   - This was the strongest convergence across Hermes architecture, AgMoDB data contract, package resolver, security, cartography, and manuscript provenance tracks.

3. **Apply must become a resolver-backed preview, not a direct write**
   - The proposed one-click Apply path is under-specified.
   - Required before writing config:
     - revalidate availability and capability;
     - show config diff;
     - surface cost/latency/vision-routing side effects;
     - handle expensive-model `confirm_required` responses;
     - reject unavailable or untrusted/free-form IDs;
     - record applied recommendation provenance.
   - Best converged abstraction: a backend **ResolutionPlan** contract.

4. **Live AgMoDB fetch needs privacy, integrity, and opt-in controls**
   - Automatic third-party fetch leaks IP/timing/User-Agent even if no local config is sent.
   - Default should be **bundled-only** unless live refresh is explicitly enabled.
   - If live is enabled, the catalog should be origin-allowlisted, redirect/private-IP-safe, cache-controlled, and preferably signed or hash-verified.

5. **Recommendation evidence/provenance is insufficient**
   - “Best available” overclaims without transparent ranking, confidence, evidence grade, benchmark provenance, task mapping, freshness, and conflict/sponsorship disclosure.
   - Need score components, evidence records, method metadata, freshness gates, and UI disclosure.

6. **Local constraints and contraindications are missing**
   - Recommendations must be screened against user/provider constraints:
     - configured providers;
     - local-only preferences;
     - budget/max-cost;
     - latency;
     - context requirements;
     - vision/tool/json capability needs;
     - high-impact auxiliary slots;
     - provider opt-outs.
   - Otherwise Hermes may recommend a theoretically strong but locally inappropriate model.

7. **Desktop state model is too shallow**
   - Recommended pins will currently look like stale/orphaned pins unless UI distinguishes:
     - intentional recommendation;
     - manual pin;
     - stale unavailable assignment;
     - current assignment;
     - auto/main fallback;
     - unavailable recommendation;
     - already-applied recommendation;
     - requires confirmation.
   - Highest-leverage UI artifact: profile-scoped `AuxRecommendationRowState`.

---

## Cross-Track Convergence

### A. Recommendations need a resolver, not just a feed

Multiple tracks independently converged on a backend resolver layer that takes:

- active profile;
- current auxiliary assignment;
- main model;
- provider auth/config state;
- curated model catalog;
- model capabilities;
- pricing/throughput;
- user preferences/constraints;
- AgMoDB recommendation evidence/provenance.

It should return normalized candidates plus an explicit resolution/apply plan.

### B. Identity must be provider-specific and canonical

The feed must provide provider-specific bindings, not a generic model plus candidate providers. The system should preserve both:

- original AgMoDB identifier;
- resolved Hermes provider/model coordinate.

This prevents broken assignments, aggregator/native-provider confusion, and arbitrary free-form catalog injection.

### C. Trust requires provenance and evidence metadata

Recommendations need a “colophon” propagated through the entire chain:

`AgMoDB feed → cache/bundled copy → backend resolver → UI row → Apply provenance record`

That provenance should include source, version, generation time, freshness/expiry, evidence method, score components, candidate measurement dates, and conflict/sponsorship disclosures where applicable.

### D. Apply is the risk boundary

All tracks treated Apply as the critical transition from advisory recommendation to user configuration mutation. Therefore Apply must be guarded by:

- preview;
- revalidation;
- capability/cost checks;
- diff;
- confirmation states;
- provenance/lock record;
- rejection of untrusted arbitrary IDs.

### E. UX should show “best configured” separately from “top overall”

Marketplace/recommendation-trust and package-resolver tracks converged here. The UI should avoid steering users toward provider setup friction by presenting:

- **Best configured** — immediately usable with current profile;
- **Top overall** — may require setup or another provider;
- alternatives with reason codes.

### F. Freshness/versioning is not optional

AgMoDB catalog version, schema version, cache semantics, expiry, ETags, generated timestamps, and per-candidate measurement dates recur across data-contract, security, clinical, cartographic, and manuscript-provenance reviews.

---

## Domain-Expert Insights (Track A)

### Hermes architecture

- Endpoint/helper must be **profile-scoped**, matching existing model API semantics.
- Backend should return normalized candidates with availability, capability fit, cost, source/provenance, and confirmation requirements.
- Vision Apply has a special side effect:
  - explicit `auxiliary.vision` can force text pre-analysis instead of native image attachment;
  - recommend `auto` when the main model is vision-capable unless the override is clearly better;
  - label this behavior in UI.
- Feed/API must use provider-specific Hermes model IDs.
- Picker payload is insufficient unless backed by a full provider/capability oracle covering vision, tool use, JSON/structured output, context, pricing, and free-tier availability.
- Live AgMoDB fetch should reuse existing model-catalog cache patterns and be configurable/opt-out.
- Task registry scope is inconsistent across desktop/backend/CLI/plugins and should be explicitly resolved.

### AgMoDB data contract

- Need a versioned JSON Schema, not a minimal ad hoc payload.
- Must include:
  - `schema_version`;
  - `catalog_version`;
  - `generated_at`;
  - `expires_at`;
  - ETag/cache-control support;
  - provider-specific pricing/throughput;
  - score components;
  - benchmark evidence/provenance;
  - exact Hermes task/provider enums.
- Current scoring and cost fields are too ambiguous for resolver-grade use.

### Desktop UX

- Existing stale-pin warning semantics conflict with recommended auxiliary pins.
- Need profile-scoped row state combining current assignment, recommendation, availability, freshness, stale status, and Apply state.
- Per-row detail blocks risk clutter; prefer compact chips with disclosure.
- Apply states should include auto, already applied, unavailable, requires confirmation, and ready to apply.
- Source freshness/fallback state must be visible.
- Add explicit i18n/copy contract.

---

## Parallel-Discipline Insights (Track B)

### Package-manager / resolver analogy

The feature should behave like dependency resolution:

- Recommendations are candidate constraints, not final assignments.
- Backend should produce a first-class **ResolutionPlan**:
  - selected candidate;
  - rejected alternatives with reason codes;
  - config diff;
  - validation result;
  - opaque recommendation ID/hash;
  - provenance;
  - confirmation requirements.
- Apply should revalidate the plan immediately before mutation.
- Applied recommendations should leave a lock/provenance record.
- Cache/mirror semantics need explicit versioning and replay protection.

### Marketplace / recommendation trust

The label **“Best available”** is too strong unless backed by transparent ranking and confidence.

Required trust metadata:

- source;
- methodology;
- freshness;
- confidence/staleness;
- rank reason codes;
- sponsorship/ownership/bias disclosures;
- distinction between best configured and top overall.

Also missing:

- user preference model for budget/quality/provider affinity;
- provider opt-outs;
- local feedback/trust calibration.

### Security / privacy / supply chain

Security review strongly favors:

- bundled catalog by default;
- live fetch only behind explicit privacy gate/config;
- signed or hash-verified manifests;
- origin allowlist for `agmodb.com`;
- redirect/private-network rejection;
- cache poisoning/replay protections;
- no arbitrary assignment creation from free-form remote model IDs;
- broader privacy tests.

---

## Structural Insights (Track C)

### Clinical formulary analogy

Treat recommendations like formulary entries:

- slot/task = indication;
- model = therapy;
- benchmark evidence = clinical evidence;
- local constraints = contraindications;
- provider availability = formulary coverage;
- Apply = prescribing event.

Needed additions:

- evidence grades;
- provenance and recency gates;
- contraindication screening before Apply;
- formulary tier/substitution rules;
- monitoring for stale evidence after catalog refresh.

### Cartography / navigation analogy

Treat model assignment as route planning:

- Each provider/model binding is a route leg.
- Generic model names are unreliable chart datums.
- Route cards should expose local hazards:
  - current pins;
  - auto/main fallback;
  - cost intent;
  - sticky pin side effects;
  - vision-routing behavior.
- Tide/current equivalent:
  - catalog freshness;
  - provider availability;
  - pricing/capability drift.
- Need a declared chart legend for slot boundaries, especially 8 visible desktop slots vs 11 backend slots.

---

## Frontier Patterns (Track D)

### Manuscript provenance / textual transmission

The strongest Track D contribution is the **colophon** pattern.

Every copied or cached recommendation authority should carry provenance metadata through all layers:

- original source URL;
- source type: bundled, cached, live;
- schema/catalog version;
- generation timestamp;
- expiry/freshness;
- content hash/signature if available;
- transformation/resolution notes;
- original AgMoDB identifier;
- resolved Hermes identifier.

The UI/API should distinguish witnesses:

- bundled fallback;
- cached live copy;
- fresh live fetch.

Also flagged:

- task corpus drift between 8 visible desktop slots and 11 backend slots;
- need explicit canonical task mapping.

---

## Synthesis Assessment

The implementation plan is directionally sound but under-specified at the exact points where user trust, correctness, and safety depend on precision.

The current plan is acceptable as a product concept, but not yet as an implementation plan. Before coding the UI-first one-click Apply flow, revise around four foundation contracts:

1. **Catalog contract**
   - versioned;
   - provider-specific;
   - evidence/provenance-rich;
   - freshness-aware;
   - signed/hashable if live.

2. **Resolver contract**
   - profile-scoped;
   - capability/cost/availability-aware;
   - produces normalized candidates and rejected-candidate reasons.

3. **ResolutionPlan / Apply contract**
   - preview;
   - config diff;
   - revalidation;
   - confirmation;
   - provenance/lock record.

4. **Desktop row-state contract**
   - compact but explicit UI state for current assignment, recommendation, stale/manual/recommended status, availability, source freshness, and Apply state.

Until these are added, the highest-risk gaps are:

- wrong-profile application;
- broken provider/model coordinates;
- untrusted live catalog mutation path;
- misleading “best available” claims;
- stale or unverifiable evidence;
- hidden Apply side effects.

---

## Recommended Revised Plan Sequence

### Phase 0 — Decide scope and defaults

1. Declare whether MVP covers 8 visible desktop slots only or all 11 backend auxiliary slots.
2. Define canonical Hermes task enum mapping.
3. Default live AgMoDB refresh to bundled-only first, or live only behind explicit opt-in/config.

### Phase 1 — Define AgMoDB catalog schema

Create a versioned JSON Schema with:

- `schema_version`;
- `catalog_version`;
- `generated_at`;
- `expires_at`;
- source/colophon metadata;
- exact Hermes task/provider enums;
- provider-specific model bindings;
- original and resolved identifiers;
- capability requirements;
- score components;
- evidence records;
- benchmark provenance;
- pricing/throughput objects;
- measurement dates;
- conflict/sponsorship disclosure fields;
- cache-control/ETag expectations.

### Phase 2 — Build secure catalog loader

Implement loader with:

- bundled fallback;
- profile-independent local cache;
- explicit live-fetch opt-in;
- short timeout;
- origin allowlist;
- redirect/private-IP rejection;
- schema validation;
- catalog version/freshness checks;
- content hash/signature verification if available;
- source witness reporting: bundled/cached/live.

### Phase 3 — Build profile-scoped resolver

Add backend resolver that accepts active profile context and model picker/catalog state.

It should return:

- recommended candidate;
- best configured candidate;
- top overall candidate;
- alternatives;
- unavailable candidates;
- rejected-candidate reason codes;
- capability/cost/latency fit;
- source/evidence/freshness;
- confidence/staleness;
- confirmation requirements.

### Phase 4 — Add ResolutionPlan preview endpoint

Before Apply, produce a plan containing:

- target profile;
- task;
- selected provider/model;
- current assignment;
- proposed assignment;
- config diff;
- validation result;
- capability checks;
- cost warning;
- vision-routing side-effect warning;
- recommendation ID/hash;
- provenance/lock metadata;
- confirmation requirement.

### Phase 5 — Implement guarded Apply

Apply should:

- revalidate the ResolutionPlan;
- reject stale/changed/untrusted candidates;
- require confirmation for expensive or behavior-changing assignments;
- write only locally curated/validated provider/model IDs;
- record provenance of applied recommendation;
- preserve manual override semantics.

### Phase 6 — Add Desktop row-state model

Introduce profile-scoped `AuxRecommendationRowState` with:

- current assignment;
- recommendation candidate;
- availability;
- freshness/source witness;
- stale/manual/recommended pin status;
- auto/main fallback state;
- Apply state;
- unavailable/setup state;
- already-applied state;
- requires-confirmation state.

UI should use compact chips plus disclosure, not large per-row blocks.

### Phase 7 — Add trust-focused UX copy

Update labels:

- avoid unqualified “Best available”;
- use “Best configured” and “Top overall” where appropriate;
- show method/freshness/provenance;
- expose rank reasons and confidence;
- disclose unavailable-provider setup friction;
- add i18n strings.

### Phase 8 — CLI/docs parity

Add lightweight CLI hints only after backend resolver semantics are stable.

Docs should cover:

- what recommendations mean;
- bundled vs live source;
- privacy behavior;
- evidence/freshness;
- Apply preview;
- manual override;
- provider setup;
- how to opt in/out of live AgMoDB refresh.

### Phase 9 — Tests and validation

Add tests for:

- profile scoping;
- schema validation;
- provider-specific ID resolution;
- unavailable/rejected reason codes;
- bundled fallback;
- live-fetch privacy gate;
- origin allowlist and redirect rejection;
- stale/expired catalog handling;
- Apply preview/revalidation;
- expensive-model confirmation;
- vision override side effect;
- source witness UI;
- stale/manual/recommended pin distinction;
- lock/provenance record creation.
