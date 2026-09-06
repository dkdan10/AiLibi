# Measure and improve evidence use at meetings

**Status:** active

## Outcome

Roadmap 14–20 have reproducible, separately evaluated implementations or an
explicit evidence-based retained decision. Agents can distinguish discoveries
from death bounds, use map-grounded counterevidence, and retain the provenance
of an observation through memory and testimony. Existing unadopted candidates
receive a concrete next disposition without changing their historical FINDING.

## Evidence

The temporal observation card repairs entitled delivery. The portfolio cases
show a certified vent deduction, an unsupported but persuasive travel charge,
and justified uncertainty. The phase-21 hardening audit carries H-44–H-49,
H-52–H-53, H-60–H-62, H-64–H-71 and H-74; the close carries B-39, G7(b/c), the
roll-call variant gap, and the analysis/stamp seams. Reproduce each relevant
claim on current code; historical allegations are not automatically defects.

## Acceptance

- [x] Write a compact scorecard before candidate measurements: proof/no-proof
  strata, development and held-out recordings/scenarios, source hashes, exact
  numerators/denominators, correction and wrongful-ejection measures, evidence
  retention/attribution, repetition, calls, tokens and latency. Separate offline
  mechanics from fresh-model decision quality and abstention from correctness.
- [x] Inspect reporter reasoning, corroboration discipline and testimony shapes
  independently; retain the original missed bars. Give each an implemented
  revision, measured retention, or justified retirement decision and a precise
  future live-evaluation requirement if needed. Do not adopt the combined slate.
- [x] Implement bounded death/discovery and legal/impossible travel evidence
  handling with positive/adverse cases, public-knowledge bounds, exact map
  semantics and no private role/time oracle. A true legal route must contest a
  false impossibility claim without proving innocence.
- [x] Implement and independently measure an opt-in bounded reply opportunity
  for consequential new allegations, including repetition and call bounds,
  no-new-allegation controls, cancellation and already-dead speakers.
- [x] Preserve independent witnesses versus repetitions/hearsay. Audit movement
  observations, sightings, cross-meeting memory, coalesced citations, budget
  loss, breadcrumb counterevidence and rewritten ballots through the actual
  pipeline; fix reproduced transformation defects and expose irreducible loss.
- [x] Current replay/live analysis uses the recorded substrate; mismatched
  environments and unsupported experimental versions raise. Coordinate this
  seam with the provenance card rather than duplicating reconstruction logic.
- [ ] Every changed prompt/detector path stays default-OFF with an explicit
  stamp and OFF-byte controls. Measurements, source-bound artifacts and current
  dispositions cover all seven roadmap items; targeted/full gates and samples
  pass. No fake-provider win-rate claim is presented as improved model reasoning.

## Constraints

Follow docs/architecture.md; agents and meetings remain engine-free. No live
provider calls, new model, training, deployment, or adoption. Use committed
recordings and deterministic scripted provider responses for bounded mechanism
experiments. Original recordings, prompts under historical contracts, and
historical verdicts remain preserved. Do not silently reinterpret an intended
rule as a bug. Root assigns shared-file ownership before implementation.

## Expected scope

Meeting schemas/manager/transcript/corroboration, agent memory and strategic
rendering/new gated templates, relevant eval evidence instruments, shared
orchestration delivery/stamp follow-through after temporal handover; focused
tests, one reproducible scorecard command and compact evidence/disposition docs.
Coordinate API/UI fields, training consumers and shared registry with root.

## Record impact

Lever-gated until an adopting record for prompt or detector changes. Mechanical
instrumentation and explicit invalid-input refusal may be unconditional if old
valid records remain interpretable. Declare each candidate's scope separately.

## Validation

Use paired legal/impossible, first-hand/hearsay, public/private and
before/after-death controls through real memory and meeting paths. Run held-out
offline scenarios with a bounded documented run budget and publish exact
commands/hashes. Root runs bash scripts/check.sh and scripts/verify_samples.sh.

## Results

Implementation is locally reviewable; the coordinated full gate and final
owner review remain pending. Architecture references: layering, structured
memory, the observation firewall, and determinism/substrate contracts in
`docs/architecture.md`. Current decisions and every named carried limitation
are in [the disposition ledger](../../audits/reasoning-evidence/dispositions.md).

The independent versions are `evidence_reasoning_version=1` and
`bounded_rebuttal_version=1` in the shared closed `RecordedExperimentConfig`.
They are absent by default and have independent environment selectors; no
second boolean substrate registry was introduced. Inputs freeze once at runner
construction. Unknown switch values, unsupported/coerced versions and conflicting
runtime/recorded settings raise. Portfolio owns the shared live/API/eval/training
binding, including genuine live→API rendered-memory parity after changing the
ambient environment.

The evidence candidate preserves public death bounds, conditional public-map
travel, transcript provenance, move breadcrumbs, suppression-aware transitions
and active belief filtering. It never turns reported speech into a private
observation. The typed detector band resists model-authored marker strings;
point conflicts retain intentional narrow-window weakness. Public roster
snapshots are idempotent and contradictory snapshots raise. The independent
reply candidate adds at most one existing reply-surface call to an unanswered
new structured allegation and reuses deadlines/defaults/cancellation handling.

Review caught and repaired three additional boundary defects: own-victim bodies
cannot reappear as discoveries in the new context; legacy witnessed-action rows
retain uncertain timing; and candidate transitions distinguish withheld
sightings from physical departures. Review also required strict replay
verification before fixed-outcome counts and an all-input fingerprint/inventory
check. Every correction has positive and planted adverse controls.

The final source-bound [scorecard](../../audits/reasoning-evidence/scorecard.json)
records 36/36 mechanics, 300 strictly verified files, 672 meetings and all four
required rosters. Fixed recordings have 333 proof meetings and 339 no-proof
meetings; the latter partition into 50 correct ejections, 46 wrongful ejections
and 243 skips. Those fixed outcomes establish no candidate quality improvement.
The source-aware count is 645 raw flags versus 638 independent accounts, with
seven duplicate rows across six named meetings. Frozen surrogate features and
historical experiment verdicts retain their existing semantics.

The scripted reply treatment adds one call/seven tokens only when eligible:
6→7 calls, 42→49 returned tokens. Zero new model outcomes means candidate
correction/wrongful-ejection rates are undefined. The memory fixture retains
3/3 source IDs in the store and prints 1/3 at all three budgets, exposing its
coalescing loss rather than labeling valid citations as complete retention.
The scorecard's exact source/input hashes bind these results; wall latency is
measured locally and is not a model-provider forecast.

Targeted verification:

```bash
uv run pytest tests/meetings tests/agents/test_reported_testimony.py tests/agents/test_beliefs.py tests/agents/test_evidence_context.py tests/eval/test_reasoning_scorecard.py tests/scripts/test_reasoning_scorecard_cli.py -q --tb=short
uv run pytest tests/agents/test_memory_rendering.py tests/agents/test_evidence_context.py tests/meetings/test_reasoning_evidence.py tests/eval/test_reasoning_scorecard.py tests/scripts/test_reasoning_scorecard_cli.py tests/orchestrator/test_substrate_binding.py -q --tb=short
uv run python scripts/measure_reasoning_evidence.py --output /tmp/reasoning-scorecard.json
```

The first command passed 1501 tests before the final death-bound follow-through. The second
passed 191 after strict input/version/clock repairs; its subsequent B36 controls
passed within 146 tests via `uv run pytest tests/agents/test_evidence_context.py
tests/agents/test_memory_rendering.py -q --tb=short`. Strict mypy and Ruff passed
on the 16 owned Python files; root will record the final combined gate. The
[isolated baseline command](../../audits/reasoning-evidence/baseline-proof.md)
reproduces the old defect and checks exact legacy JSON against `ee7cbe7a`.

Final review additionally prevented ambiguous legacy action delivery from
becoming a precise last-alive time. Ordinary sightings and source-timed events
retain their precise bounds; the legacy control retains its earlier precise
sighting. `uv run pytest tests/agents/test_evidence_context.py -q --tb=short`
passed 24 tests; strict mypy/format passed on the two affected files. The
scorecard was recaptured after this repair and the last game/API handover.

Historical phase contracts, generated prompts, recordings, model artifacts and
slate verdicts are unchanged. No live provider, new dependency, training run,
experimental adoption or main merge occurred. Deferrals in the disposition
ledger distinguish new detector/protocol semantics from repaired deterministic
transformations; they are not credited as completed repairs.

The final pure-reducer caller sweep migrated the historical counterfactual
instrument to explicit OFF/ON booleans while retaining its original arms; all
112 instrument checks passed. Root independently reran the final precise-alive
context controls (24 passed). The isolated runtime/measurement commit snapshot
passed strict mypy across 436 files and all 235 selected mechanism, profile,
reader and counterfactual tests. The combined project gate remains pending.
