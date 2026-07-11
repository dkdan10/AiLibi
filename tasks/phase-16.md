# Phase 16 — Voice & Judgment on a probe-locked model (Wave 0: model probe → lock; Wave 1: judgment/pooling substrate; Wave 2: baseline 4 [GO-conditional]; Wave 3: elicitation + personas; Wave 4: baseline 5 close)

> **STATUS: OPEN (authored 2026-07-11).** All eighteen contracts below are dispatchable, with the
> Wave-2 tasks (16.12–16.14) CONDITIONAL on the 16.2 model lock: under GO they activate as written;
> under NO-GO 16.2 REMOVES their three contracts and generated prompts outright, replacing them with
> a prose drop record — `scripts/compute_next_task.py` treats any surviving `### Task` header as
> dispatchable, so an inline "dropped" label is not enough — and rewrites BOTH 16.15 and 16.16
> (dependency edges, template paths, and per-template version arithmetic; the contract for that
> surgery is inside 16.2). Two owner gates: the mid-phase MODEL LOCK
> (16.2) and the baseline-5 GRADUATION SLATE (16.17's preflight — which levers graduate is an owner
> decision on committed counterfactuals, named here so it is not discovered mid-record). Scoping
> inputs: `audits/audit-phase-15-close.md` §10–§11, `audits/audit-phase-15-pause.md` §9,
> `audits/post-phase-14-Voice-and-Judgment-planning.md` (the program design; its "Phase 15 / 15.x"
> labels predate the roadmap renumbering), `tasks/post-phase-14-plan.md` (the ladder). Phase 15
> closed on branch A: baseline 3 stays canonical, the `utility-es` champion is opt-in, and
> `_TOGGLEABLE_LEVER_RESOLVERS` is empty — this phase repopulates it.

Goal: make the meeting layer's TALK worth the evidence the substrate now carries — and, first,
decide the model that talk runs on. Phase 15 proved the game generates and keeps hard evidence
(structured vents 0 → 55, innocent-reporter ejections 22 → 4) and that better tactical play makes
the deduction game stronger; but the close measured the binding constraint moving INTO the meeting
layer: testimony-backed conversion is the champion close's one failing gauge (0.5743 vs the
FSM-pinned 0.6636), ~20/73 held vents still go unspoken on the samples (53/73 mentioned; corpus
188/255), the residual zero-flag conviction channel survives (voice beating evidence), and voices
are one indistinguishable analyst times nine. Phase 16 closes those holes with FOUR coordinated
programs: (1) **Judgment** — suspicion provenance, a hard-evidence render gate, and citation-gated
ballots (a zero-flag conviction must cite a transcript turn or a stable-id'd private observation —
the C3/C8 chain from the V&J planning doc, built enforcement-last); (2) **Pooling** — roll-call/
whereabouts elicitation, typed-grounded vouching (the 15.4 chokepoint pattern generalized to
sightings, feeding the EXISTING corroboration channel — a grounded sighting proves the speaker's
honesty, not the subject's guilt, so it never mints a strong flag), and a capped sub-gate absence
prior (making visibility a strategic resource for the first time — the incentive Phase 17's
retraining needs); (3) **Voice** — a deterministic, role-neutral persona layer landing STRICTLY
after the citation gate (the planning doc's thesis: louder voices without an evidence bound worsen
the zero-flag channel); (4) **the model decision** — Qwen3.6-27b evaluated probe-first against the
incumbent `Qwen/Qwen3-32B` on the committed contexts, locked by the owner, and (under GO) landed as
its OWN baseline 4 with mechanics untouched, so the model effect and the V&J effect are separately
attributable. The phase closes on **baseline 5** with the funnel + the new V&J instruments as the
before/after.

Locked decisions (owner, 2026-07-11):
- **Model swap is probe-first and evidence-gated.** No production model change before the 16.1
  sweep report and the 16.2 lock decision. Under GO, the swap is its OWN layer: baseline 4 records
  the new model with every Phase-16 lever OFF/inert and the prompt SEMANTICS ported exactly —
  model is the only change. Under NO-GO the phase proceeds on `Qwen/Qwen3-32B`/`qwen3_32b`
  unchanged and Wave 2 is dropped with the reason recorded. One-layer-per-baseline
  (`tasks/post-phase-14-plan.md` §4) is why the swap cannot share a record with the V&J mechanics.
- **Full pooling package.** Roll-call/whereabouts elicitation + typed-grounded vouching + the
  absence prior + the citation gate all ship this phase. Vouching feeds the existing
  `CORROBORATION_SUSPICION_DELTA` channel (−0.05) — NEVER a strong flag (not role-proving) and
  NEVER the trust field (`adjust_trust` has zero production callers; do not build on dead code).
- **Personas ship, evidence-gated.** Deterministic per-seed assignment (sampling WITHOUT
  replacement), role-NEUTRAL bank (≥12 entries so composition varies game-to-game), and the
  persona TEXT lands only after the citation gate is merged (enforced by the 16.16 ← 16.15 ← 16.6
  edges) — the C10 ordering.
- **Conversion floor re-anchors population-relative** (the Q1 precedent; close audit §10): the
  referee's `testimony_backed_conversion` floor derives from the scored population rather than the
  FSM constant, with `training/reports/results-champion-close.jsonl` as the committed calibration
  fixture and a synthetic starved set still failing loud.
- **Lever doctrine unchanged:** every behavioral change ships default-OFF, proven byte-identical
  OFF against committed bytes (the 16.3 prompt-byte golden + `verify_samples.sh` bare), offline
  counterfactuals committed BEFORE graduation, graduation-at-record at the baseline that adopts it
  (C6), and every new suspicion delta composes through `_joint_capped_suspicion` +
  `CONTRADICTION_RENDER_CEIL` — nothing re-opens the railroad class Phases 13–14 closed.
- **Canary honesty this phase (Q3 degraded):** the ML corpus is baseline-3/Qwen3-32B substrate;
  the moment baseline 4 lands there is NO corpus-scale same-substrate set. Canaries at baselines 4
  and 5 are judged on the 50-seed sets with the 15.18 two-proportion discipline (UNDERPOWERED is a
  recorded outcome, not a judgment call), and the corpus figure is reported as stale context.
  Phase 17 re-grounds the corpus/surrogate/champion on the phase-16 close substrate.

Parallelism: three independent roots dispatch immediately: `16.1 ∥ 16.3 ∥ 16.11` (the model probe
runs beside the model-INDEPENDENT judgment/pooling substrate — no code task waits for the probe).
Then `16.1 → 16.2` [OWNER: the model lock]; `16.2 → (16.12 ∥ 16.13)` [GO only];
`(16.3, 16.11, 16.12, 16.13) → 16.14` [operator: baseline 4 — 16.3 gates it because the
preflight requires the prompt-byte golden; 16.3 is a root, so no wall-clock cost]; `16.3 → (16.4 ∥ 16.7 ∥ 16.9)`;
`16.4 → 16.5 → 16.6` (the `orchestrator/replay.py` lever-registry chain — the 16.4 → 16.5 edge
exists ONLY to serialize that registry region, the 15.6 → 15.8 precedent; nothing semantic);
`(16.6, 16.7) → 16.8`; `(16.5, 16.7) → 16.7.1`; `(16.3, 16.5, 16.7) → 16.10` (the citation-
compliance metrics type against 16.5's ballot field);
`(16.2, 16.5, 16.6, 16.7, 16.14) → 16.15 → 16.16` (16.9 → 16.16 as well — persona text needs the
bank); `(16.7.1, 16.8, 16.10, 16.11, 16.16) → 16.17` [operator + OWNER: baseline 5 + close].
The critical path is two length-7 chains joining at 16.15 — code:
`16.3 → 16.4 → 16.5 → 16.6 → 16.15 → 16.16 → 16.17`; model:
`16.1 → 16.2 → 16.13 → 16.14 → 16.15 → 16.16 → 16.17` — overlapped by construction: the probe,
lock, A/B and baseline-4 sessions run while the lever chain proceeds. Under NO-GO the model chain
collapses to `16.1 → 16.2` and the code chain alone is critical.
Shared-file overlaps are covered by dependency edges or disjoint-region annotations:
`meetings/manager.py` five ways — 16.3's render seams + participant fields, 16.5's
ballot-validation/observation-id region, 16.6's post-guard citation region, 16.7's turn-validation
+ participant-threading region, 16.8's pre-vote absence region (serialized by edges except
16.5 ∥ 16.7, which are provably disjoint regions, annotated in both);
`meetings/schemas.py` — 16.5's ballot-field region ∥ 16.7's observation-union region (disjoint,
both behind 16.3); `meetings/render_contract.py` — 16.3 single-toucher;
`agents/memory/beliefs.py` — 16.3 → 16.4 → 16.8 → 16.17 (serialized);
`meetings/transcript.py` — 16.7 → 16.8 (serialized); `orchestrator/replay.py` lever registry —
16.4 → 16.5 → 16.6 → 16.8 → 16.17 (serialized end-to-end); `orchestrator/game.py` — 16.7's
protocol/accessor region, 16.9's participant-persona region (disjoint from each other and from
the `PROMPT_VERSION_SETS` registry line, which serializes 16.13 → 16.15 → 16.16); the winning
prompt-set directory — 16.13 → 16.15 → 16.16; recording-script literals — `refresh_samples.sh`:
16.12's model line ∥ 16.13's set line (disjoint lines) with `tests/scripts/test_refresh_samples.py`
split the same way (16.12's model-pin region ∥ 16.13's set-gate region, both behind 16.2) — it
carries NO version literal, so 16.17 does not edit it (HEAD's registry governs the versions it
records); `record_ml_corpus.sh`: comment-only at 16.12, untouched by 16.13 (the preflight couples
set+versions), the full pin block re-pinned at 16.17;
`eval/watchability.py` floors — 16.11 → 16.14 → 16.17 (the direct 16.11 → 16.17 edge keeps the
ordering under NO-GO); `eval/funnel.py` + `scripts/measure_baseline.py` — 16.10 single-toucher;
`api/` + `frontend/` — 16.7.1 single-toucher; `.env.example` — lever lines (16.4/16.5/16.6/16.8,
chain-serialized) vs model lines (16.12), disjoint.
Operator-run / spend gates: **16.1** (sweep probe, $0, hours), **16.13** (A/B re-sweep, $0),
**16.14** (baseline-4 record, $0, ~4–5h, GO only), **16.17** (baseline-5 record + close, $0,
~4–5h). Owner gates: **16.2** (the model lock), **16.17 preflight** (the graduation slate).
Everything else is agent-dispatchable and CI-green on the fake provider.
Track with `python3 scripts/compute_next_task.py --phase 16`.

Merge criteria (Wave 0 → the conditional branch — the MODEL LOCK gate): (1) the sweep report is
committed with the new model's full row (parse success on both call kinds, thinking-mode behavior,
`response_format_mode` verdict, latency, token shape) beside the incumbent's re-run row, every
number regenerated from the committed sweep JSONL; (2) the owner decision is recorded in
`audits/audit-phase-16-model-lock.md` (the 14.6 LOCKED-DECISION shape) with the exact served model
id and the NO path's rationale; (3) `tasks/phase-16.md` is re-authored per the decision — 16.12–
16.14 ACTIVE with concrete paths, or DROPPED with reason and 16.15's edge/paths rewritten — with
prompts regenerated and `validate_task_docs.py` + `generate_prompts.py --check` green; (4) nothing
model-conditional merged before the gate, and nothing in 16.3–16.11 waited for it; (5) under GO,
baseline 4's preconditions are restated: every Phase-16 lever OFF/inert, the prompt-byte golden
green, model as the only layer.

Merge criteria (end of phase): (1) **baseline 5 recorded, validity-gated, byte-verified BARE**
(levers graduated at record — resolvers constant-true + registry retirement, no `AILIBI_*`
export), one atomic PR per set replacement, Q5 annotated tags on every operator record, at most
TWO re-records this phase; (2) every graduated lever is backed by its committed offline
counterfactual (J1's over-damping canary: zero hard-backed outcome changes; J2's soundness: near
zero honest catches blocked; absence's boundary pins), and every lever NOT graduated is a recorded
owner decision, not a silent omission; (3) the citation gate is live end-to-end — observations
carry stable rendered ids, `primary_reason_observation_id` validates, zero-flag EJECTs cite or are
coerced, and the spectator mirror serves the new surface; (4) the pooling package is measurable —
16.10's folds report roll-call coverage, vouch and grounded-vouch rates, and absence-set sizes on
baseline 5 with the BEFORE column regenerated from committed bytes; (5) personas are live and
evidence-gated (persona text merged after the citation gate, provable from the merge record),
assignment is seed-deterministic without replacement, and voice metrics are reported ALONGSIDE the
zero-flag conviction rate — a zero-flag rise attributable to personas is the phase's named NO-GO
for an owner call; (6) the referee runs the population-relative conversion floor with floors
re-pinned per baseline and the champion-close row reproduced as the calibration fixture; (7)
canaries (genuine-class conversion, R1) are judged on the 50-seed sets with the corpus figure as
stale context, per the degraded-Q3 rule above — a canary regression pauses the phase; (8) the
close audit re-states the Phase-17 staleness rule (the surrogate, `replays/ml_corpus/`, and the
champion's numbers are prior-substrate-anchored), records the champion re-audit figures (GO path),
and flips this banner.

## Wave 0 — the model probe and the lock

### Task 16.1 — Qwen3.6-27b sweep probe: the new Qwen generation on the committed contexts
**Branch:** `phase-16-model-probe`
**Depends on:** none
**Section refs:** experiments/lab/featherless_sweep.py (SLATE :247-275, ModelSpec :226-243, preflight :904-957, corpora/detectors :1-96); agent_prompts/task-14-4-model-sweep.md (the precedent probe); llm/featherless_client.py:18-32 (the response_format_mode posture the probe must re-verify); audits/audit-phase-16-model-lock.md (the 16.2 consumer)
**Complexity:** Medium

Evaluate the newer Qwen generation before any production change: add Qwen3.6-27b to the committed
sweep harness's `SLATE` as a candidate `ModelSpec` (probing BOTH thinking-axis settings and the
transport `qwen_kwarg`, exactly how the Phase-14 slate rows are declared) and operator-run the
sweep over the SAME reconstructed 9p2i contexts as the incumbent — model is the only moving
variable. The probe must establish, with committed evidence: (a) the exact served model id on the
flat-rate plan (the generation preflight 404s an unserved id — an unserved model is a NO-GO
finding, not an error); (b) parse success on both call kinds under `json_object`, and whether the
newer generation supports strict `json_schema` (the incumbent deterministically 400s on it — a
newer model may not; re-verify, do not assume); (c) the thinking-kwarg behavior the 16.12
`_THINKING_KWARG_BY_MODEL` entry will encode; (d) grade rows on the four corpora (opening
fabrication, reply/cover 2×2, vote parse + conversion, latency) beside a re-run incumbent row so
the comparison is same-day, not archival. This task is EXPERIMENT-TIER only: no `llm/` production
edit, no constant change — the fail-loud registry entry is 16.12's, post-lock.

**Files in scope:**
- experiments/lab/featherless_sweep.py (SLATE + any new-generation transport handling the probe needs)
- experiments/lab/results-featherless-sweep-qwen3-6-27b.jsonl (new: the committed sweep rows)
- experiments/lab/report-featherless-sweep-qwen3-6-27b.md (new: the graded comparison + the served-id/response-format/thinking findings)
- tests/experiments/test_probe_backends.py (slate-entry pins region — the new ModelSpec is well-formed; no network)

**Files NOT in scope:**
- llm/ (production client untouched — the registry entry and default swap are 16.12's, behind the lock)
- agents/strategic/prompts/ (no set work before the lock; the probe runs the new model against the EXISTING qwen3_32b set, which is itself a finding — a bespoke set is 16.13's)
- scripts/refresh_samples.sh + scripts/record_ml_corpus.sh (recording surfaces untouched)

**Definition of done:**
- [ ] The new `ModelSpec` rides the existing harness unmodified in shape: pinned corpus ids re-rendered per cell, model-outer loop, switch pacing, generation preflight — a served-id failure produces a documented NO-GO row, never a crash.
- [ ] The committed JSONL carries, for the new model AND a same-day incumbent re-run: parse_ok rates per call kind, thinking-axis behavior, response_format verdict (`json_object` and `json_schema` both probed), token counts, latency, and the four corpora's grade booleans.
- [ ] The report ends in a RECOMMENDATION-SHAPED summary (the ranked-not-self-declared discipline): the head-to-head table, the served id, and the open risks — it recommends; 16.2 decides.
- [ ] Every reported number regenerates from the committed JSONL; the report names the exact reproduce command.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

Clone a candidate row's shape from the existing `SLATE` (:247-275) — `served_id`, `label`,
`thinking_axis`, `qwen_kwarg`, `role="candidate"` — and let the harness do the rest; the pinned
corpus-id mechanism (`_pin_ids` :969-992) guarantees the new model sees byte-identical contexts.
The served id for a new release is a guess until the preflight confirms it: try the obvious
Featherless namespace forms (`Qwen/Qwen3.6-27B` and variants) and record what the API actually
serves — the preflight probe (:904-957) is the arbiter, and "not served on the plan" is a
first-class NO-GO outcome for 16.2, not a task failure. Operator gate: `FEATHERLESS_API_KEY`,
hours-scale, $0 flat-rate.

**Ready-to-paste prompt:** `agent_prompts/task-16-1-model-probe.md`

### Task 16.2 — The model lock: owner decision + the conditional-wave surgery
**Branch:** `phase-16-model-lock`
**Depends on:** 16.1
**Section refs:** agent_prompts/task-14-6-lock-decision.md (the LOCKED-DECISION shape); tasks/phase-15.md 15.18 (the pause precedent for phase-doc surgery + prompt regeneration); scripts/validate_task_docs.py + scripts/generate_prompts.py (the tooling the surgery must keep green)
**Complexity:** Medium

The mid-phase owner gate. Consume 16.1's committed evidence and record the GO/NO-GO in
`audits/audit-phase-16-model-lock.md` (the 14.6 LOCKED-DECISION shape: the exact served model id,
thinking policy, `response_format_mode` posture, parse/latency evidence, the rejected path's
rationale — including "not served on the flat-rate plan" if that is the finding). Then perform the
phase-doc surgery this file's banner promises: under **GO**, concretize the Wave-2 contracts
(16.12–16.14 stay as written; fill the exact served id where this document says Qwen3.6-27b) and
confirm 16.15/16.16's template paths point at `agents/strategic/prompts/qwen3_6_27b/`; under
**NO-GO**, REMOVE the 16.12–16.14 contracts and their generated prompts entirely, replacing the
three with ONE prose drop record carrying the rationale (removal, not labeling:
`scripts/compute_next_task.py` computes dispatchability from `### Task` headers + merged PRs and
has no dropped state — a surviving header would surface forever as dispatchable), then rewrite
BOTH downstream prompt tasks: 16.15 (`Depends on:` drops 16.14; template paths to
`agents/strategic/prompts/qwen3_32b/`; bump arithmetic per-template — the three v5 templates → v6,
`vote_ballot` v6 → v7) and 16.16 (paths likewise to `qwen3_32b/`; its SECOND bump per-template —
the three → v7, `vote_ballot` → v8 — a set-level relabel would mint colliding stamps), and adjust
16.17's BEFORE column to baseline 3 plus the DAG/critical-path text. Either way: regenerate
`agent_prompts/`, keep the validator green, and update this file's STATUS banner to record the
lock outcome.

**Files in scope:**
- audits/audit-phase-16-model-lock.md (new: the decision record)
- tasks/phase-16.md (the conditional-wave surgery + banner line — this file)
- agent_prompts/ (mechanically regenerated task-16-* prompts — generator output, never hand-edited)

**Files NOT in scope:**
- llm/ + agents/strategic/prompts/ + scripts/ (no code or template change — the decision record and the doc surgery only; 16.12/16.13 implement)
- audits/ other than the new lock audit
- replays/ (untouched)

**Definition of done:**
- [ ] The lock audit records the decision in the 14.6 shape with every quoted number traced to `results-featherless-sweep-qwen3-6-27b.jsonl`, the exact served id (GO) or the NO-GO reason, and owner sign-off (the owner merges this PR — the 15.18 convention).
- [ ] The phase doc reflects the decision: GO → Wave 2 active with the served id concretized; NO-GO → the 16.12–16.14 contracts AND their prompts are REMOVED (one prose drop record remains; task/prompt counts fall by three, validator + `--check` green at the new counts, and `compute_next_task.py --phase 16` no longer lists them), 16.15 AND 16.16 rewritten (edges, paths, per-template arithmetic — 16.15: three v5 → v6, `vote_ballot` v6 → v7; 16.16's second bump: three → v7, `vote_ballot` → v8), 16.17's BEFORE column re-anchored to baseline 3, and the DAG/critical-path text updated.
- [ ] `uv run python scripts/validate_task_docs.py` and `uv run python scripts/generate_prompts.py --check` pass on the re-authored doc (the full-file validation discipline: a malformed phase doc breaks the repo's validator for every phase).
- [ ] The STATUS banner names the lock outcome and the date.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

The surgery is textual but validator-bound: after every edit run the validator + `--check` locally
before committing (the 7-line tail is your own gate). The decision itself is the owner's — this
task's agent prepares the audit from the sweep evidence and presents both branches; the owner's
merge IS the sign-off. Keep the surgery minimal: contracts not named in the decision do not change.

**Ready-to-paste prompt:** `agent_prompts/task-16-2-model-lock.md`

## Wave 1 — the model-independent V&J substrate (dispatches immediately, ∥ Wave 0)

### Task 16.3 — Foundation: suspicion provenance + inert render-contract widening + the prompt-byte golden
**Branch:** `phase-16-vj-foundation`
**Depends on:** none
**Section refs:** audits/post-phase-14-Voice-and-Judgment-planning.md §3.2 + task "15.0" (the foundation design + the C4/C9 catches); agents/memory/beliefs.py (the accumulator this task decomposes); meetings/render_contract.py:38-195 (the three Protocols + SuspicionEntry); agents/strategic/prompts/loader.py (the four wrappers); meetings/manager.py (render seams + MeetingParticipant)
**Complexity:** Integration

The seam both tracks need, landed ONCE so Judgment and Voice never collide on the render contract
(the C4 catch). Three parts, all provably inert. (a) **Suspicion provenance**: record a
source-tagged decomposition beside the aggregate scalar in the belief store — per subject, the
accumulated lift attributable to flag-lift / body-proximity / kill-or-vent pin / testimony-spread
/ accusation-carry, with the cross-meeting carry SPLIT into carried-HARD and carried-SOFT
components (the hard/soft attribution PERSISTS through the carry: a grounded vent flag from
meeting 1 is still a hard component of the prior at meeting 3 — collapsing carry into one soft
bucket would let 16.4's clamp suppress persistent hard evidence, the exact outcome its canary
forbids) — WITHOUT changing the scalar's value, the fold's arithmetic, or any rendered byte. This is what 16.4's clamp classifies on and what 16.15's provenance-rendered
surface displays; today a carried soft prior at 0.70 is indistinguishable from a body-proximity
pin at 0.70. (b) **Render-contract widening, inert**: `persona` and `suspicion_provenance` kwargs
through the three `meetings/render_contract.py` Protocols, the four loader wrappers, and the
manager render seams; provenance fields on `SuspicionEntry`; a `MeetingParticipant.persona` field
— every input defaulted so unmodified templates render byte-identically (the widen-the-contract-
inert pattern the reporter lever shipped). (c) **The prompt-byte golden** (the C9 catch):
`verify_samples.sh` re-checks engine state hashes only — it is belief- and prompt-BLIND, so it
cannot prove (a)+(b) left prompts unchanged. Commit a test that re-renders every committed
meeting's opening/turn/ballot prompts (and `rendered_memory`) from the recorded inputs and asserts
byte-equality with the committed `llm_calls[].prompt`. That golden is the OFF-path proof
instrument every later render lever in this phase reuses (16.5's id-rendering, 16.15, 16.16).

**Files in scope:**
- agents/memory/beliefs.py (provenance decomposition region — recorded beside the scalar; arithmetic untouched)
- meetings/render_contract.py (persona + provenance kwargs, SuspicionEntry provenance fields — all defaulted)
- agents/strategic/prompts/loader.py (the four wrapper signatures + render bodies — defaulted pass-through)
- meetings/manager.py (render seams + MeetingParticipant.persona/provenance threading region — disjoint from 16.5/16.6/16.7/16.8's regions per the preamble map)
- orchestrator/game.py (the `suspicion_graph_for_meeting` builder region — POPULATE the new `SuspicionEntry` provenance fields from the belief store; without this, live graphs carry defaults and 16.15's surface has nothing to render; disjoint from 16.7/16.9's regions and the registry line)
- tests/agents/test_beliefs_provenance.py (new: decomposition-sums-to-scalar pins)
- tests/meetings/test_prompt_byte_golden.py (new: the golden over both committed sets)

**Files NOT in scope:**
- agents/strategic/prompts/qwen3_32b/ + every template directory (no template references the new kwargs yet — that is 16.15/16.16)
- meetings/transcript.py + meetings/voting.py (no detection or tally change)
- orchestrator/replay.py (no lever here — everything in this task is inert, not toggleable)
- replays/samples/ (the golden READS them; nothing rewrites them)

**Definition of done:**
- [ ] Provenance decomposition: for every subject in every committed meeting, the recorded source-tagged components sum to the aggregate scalar within documented float tolerance (pinned over both committed sets), and the fold's rendered values are bit-identical to before (the golden proves it).
- [ ] Hard/soft attribution survives the cross-meeting carry: a fixture where a grounded hard flag lands in meeting 1 shows a carried-HARD component (never carried-soft) in meeting 2+'s decomposition, including through decay and the pre-vote re-render path.
- [ ] The prompt-byte golden re-renders EVERY committed meeting prompt (all four template kinds) and `rendered_memory` across `replays/samples/{9p2i,4p1i}` and asserts byte-equality against `llm_calls[].prompt` — and it FAILS on a deliberate one-byte template perturbation (a golden that cannot fail is not a gate).
- [ ] The widened contract is inert: all new kwargs defaulted, `SuspicionEntry` extended additively, `MeetingParticipant.persona` defaults empty, and `bash scripts/verify_samples.sh` reconstructs both committed sets clean.
- [ ] The production graph builder POPULATES the provenance fields (a fixture proves live `MeetingParticipant.suspicion_graph` rows carry the hard/soft split, not defaults) — populated-but-unrendered is the inert contract; defaults-forever would starve 16.15's surface.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Public types introduced:**
- agents.memory.beliefs.SuspicionProvenance

**Implementation hint:**

Decompose by ACCUMULATING per-source alongside the existing writes — every site that adds to a
subject's suspicion tags its delta with a source enum; do NOT re-derive provenance after the fact
(the fold's ordering and caps make post-hoc attribution wrong). The golden's re-render loop is the
15.3 walk plus the recorded render inputs: reconstruct state, build the participants exactly as
`_build_participants` does, call the SAME renderers production calls, compare bytes. Expect the
golden to be the phase's most-reused test — name its helpers for reuse, not for this task.

**Integration risk:**

The whole task is a byte-identity claim with three moving layers; the golden is the only honest
proof, so land it FIRST in the commit sequence and keep it green through (a) and (b). The
provenance record must survive the pre-vote re-render path (the 13.5.5 rerender hook) — a
decomposition that drifts from the scalar on re-render poisons 16.4's clamp downstream. The
manager edit sits in the same file four later tasks touch: keep to the render-seam region the
preamble maps to this task.

**Ready-to-paste prompt:** `agent_prompts/task-16-3-vj-foundation.md`

### Task 16.4 — J1: the hard-evidence render gate (default-OFF lever)
**Branch:** `phase-16-j1-hard-evidence-gate`
**Depends on:** 16.3
**Section refs:** audits/post-phase-14-Voice-and-Judgment-planning.md §3.4 J1 (the measured 24/31 vs 6/16 trade — baseline-2-era, re-measure); agents/memory/beliefs.py (the 0.60 gate discipline + REPORTER_EXCULPATION precedent); orchestrator/replay.py:395-431 (_TOGGLEABLE_LEVER_RESOLVERS, currently empty, + _RETIRED_ALWAYS_ON_LEVERS)
**Complexity:** Integration

Close the zero-flag channel at its root: a conviction-grade rendered suspicion (≥ 0.60) whose
provenance is ENTIRELY soft (testimony-spread + accusation-carry + carried-SOFT prior — no fresh
hard component AND no carried-HARD component; a prior fed by an earlier meeting's grounded
flag/pin stays hard through the carry, per 16.3's split) is clamped to render just below the gate
in the pre-vote surface. Hard-backed suspicion renders untouched; the clamp classifies on 16.3's typed provenance,
never on the scalar or on prose. Ships as the first lever back into the now-empty
`_TOGGLEABLE_LEVER_RESOLVERS` (default-OFF, `substrate_flag_snapshot` stamped, the 13.5/14.10
pattern end-to-end). The planning doc's static counterfactual measured 24/31 crew mis-ejects
neutralized vs 6/16 impostor catches risked — but those are BASELINE-2-era figures and the
champion close reshaped exactly the relevant distribution (witnessed kills 5 → 32, structured
vents 0 → 55, innocent-reporter ejections 22 → 4); this task's DoD RE-MEASURES the counterfactual
on the committed baseline-3 bytes, and the 16.17 graduation decision re-checks it on the adopting
baseline's bytes. The trade is a hypothesis to re-measure, not a carried fact.

**Files in scope:**
- agents/memory/beliefs.py (the clamp rule as a PURE helper + `hard_evidence_gate_enabled` resolver — behind 16.3's provenance region; stored state never mutates)
- agents/memory/store.py (the belief-line render read-site — `_build_belief_lines`/`_format_belief_score` apply the clamp helper lever-ON; the prompt rows are produced HERE, not in beliefs.py)
- orchestrator/game.py (the suspicion-graph builder read-site — the graph rows the vote template renders apply the same helper; region disjoint from 16.3's provenance-population edit, behind the 16.3 edge)
- orchestrator/replay.py (lever registration region — the first entry back into `_TOGGLEABLE_LEVER_RESOLVERS` + `substrate_flag_snapshot`)
- .env.example (the lever env line)
- tests/agents/test_beliefs_hard_evidence_gate.py (new: clamp classification + OFF-path byte pins)
- tests/orchestrator/test_replay.py (lever stamp region)

**Files NOT in scope:**
- meetings/manager.py + meetings/voting.py (the clamp lives in the belief render path; no guard or tally change — J2's guard is 16.6)
- meetings/render_contract.py (16.3 landed the contract; consumed as-is)
- replays/samples/ (OFF must be byte-identical; the re-record is 16.17)

**Definition of done:**
- [ ] Lever OFF = byte-identical: the 16.3 prompt-byte golden and `bash scripts/verify_samples.sh` both green with the lever merged OFF.
- [ ] The clamp classifies on typed provenance only: a soft-only 0.70 renders sub-gate; the SAME scalar with any hard component renders unchanged — both pinned by fixture, including the pre-vote re-render path AND the persistent-hard case (meeting-1 grounded flag, meeting-2 clamp evaluation: the carried-hard component exempts — the cross-meeting fixture is mandatory).
- [ ] The offline counterfactual is RE-MEASURED on committed baseline-3 bytes via the 14.8 `allow_substrate_mismatch` machinery and reported in the PR: how many soft-only convictions the clamp would keep sub-gate, how many hard-backed catches change outcome (the over-damping canary — the contract's hard line is ZERO hard-backed outcome changes), with the baseline-2-era 24/31 vs 6/16 quoted only as the prior hypothesis.
- [ ] The lever is registered, stamped, and its OFF/ON behavior covered by the lever-pattern test suite (registration, stamp, resolver constant-ness at graduation readiness).
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Public types introduced:**
- agents.memory.beliefs.hard_evidence_gate_enabled

**Implementation hint:**

Clone the reporter-exculpation lever end-to-end (resolver + registration + stamp + counterfactual
+ byte-coupled OFF tests — the pattern has now shipped six times); the novelty is only the
classification predicate, which 16.3's decomposition makes a pure function of recorded provenance.
Clamp at render time (the pre-vote surface), never mutate the stored scalar — the fold and its
caps stay untouched, and OFF-path storage is bit-identical by construction. ONE pure helper in
beliefs.py, applied at BOTH render read-sites (the store's belief lines and the game.py graph
builder) so the memory prose and the suspicion graph can never disagree about the clamped value;
non-render consumers keep reading the raw scalar.

**Integration risk:**

Over-damping is the real risk, exactly as it was for the reporter lever: the counterfactual's
zero-hard-backed-changes canary is the contract's hard line, and a marginal result routes to the
16.17 graduation slate as an owner decision, not a silent graduation. Second: the clamp interacts
with `_joint_capped_suspicion` and `CONTRADICTION_RENDER_CEIL` — compose, never bypass; a clamp
applied before the joint cap produces different bytes than after, so pin the ordering by test.

**Ready-to-paste prompt:** `agent_prompts/task-16-4-j1-hard-evidence-gate.md`

### Task 16.5 — Observation identity: stable ids + the citation plumbing (enforcement-free)
**Branch:** `phase-16-observation-identity`
**Depends on:** 16.3, 16.4
**Section refs:** audits/post-phase-14-Voice-and-Judgment-planning.md §3.4 C3/C8 (the private-evidence citation chain); agents/memory/episodic.py:19-30 (EpisodicEvent — no id today); agents/memory/store.py (the memory render the ids must appear in); meetings/schemas.py:317-330 (VoteBallot + primary_reason_id); meetings/manager.py:2264-2303 (_normalize_ballot_reason_id — the validation pattern to mirror)
**Complexity:** Integration

The C8 chain, built enforcement-LAST so every piece is provable before anything blocks a ballot:
(a) **stable observation ids** on episodic events — deterministic (derived from agent/tick/
sequence, never RNG), assigned at write time in the perception path, surviving the store's
compaction; (b) **id rendering** in the memory prompt behind a default-OFF render lever
(`observation_id_rendering_enabled`) — rendering ids changes `rendered_memory` bytes, so OFF is
proven by the 16.3 golden and ON becomes real only at the 16.15 elicitation surface; (c) the
ballot gains `primary_reason_observation_id` (additive, optional — committed replays parse
unchanged); (d) the manager receives each voter's valid-id set (the same participant-threading
pattern as `vent_witness_records`) and VALIDATES the new field exactly as
`_normalize_ballot_reason_id` validates turn ids — mark-and-null on a dangling id, never a crash —
but NO gate consults it yet: 16.6 enforces. This is the task that makes private hard evidence
(a witnessed kill or vent the voter holds but nobody spoke) CITABLE, which is the C3 catch: a
citation gate without this path would block the honest convictions it exists to protect.
Dependency note: the 16.4 edge exists ONLY to serialize the `orchestrator/replay.py` lever-
registry region (the 15.6 → 15.8 precedent) — nothing semantic.

**Files in scope:**
- agents/memory/episodic.py (stable id field + deterministic assignment)
- agents/perception.py (id assignment at the observed-event write sites)
- agents/memory/store.py (id-rendering region behind the lever — the render changes only lever-ON)
- meetings/schemas.py (ballot citation-field region: `primary_reason_observation_id`, additive — disjoint from 16.7's observation-union region)
- meetings/manager.py (observation-id validation region beside `_normalize_ballot_reason_id` + participant threading — disjoint from 16.6's guard region and 16.7's turn-validation region)
- orchestrator/game.py (participant observation-id-set accessor region — the vent-accessor pattern; disjoint from 16.9's persona region and the registry line)
- orchestrator/replay.py (lever registration region — behind 16.4's entry)
- .env.example (the lever env line)
- tests/agents/test_episodic_ids.py (new)
- tests/meetings/test_ballot_observation_citation.py (new)

**Files NOT in scope:**
- meetings/voting.py (tally untouched)
- meetings/transcript.py (no detection change — vouch grounding is 16.7's)
- agents/strategic/prompts/ (no template edit; the ids render lever-ON only and the elicitation ask is 16.15's)

**Definition of done:**
- [ ] Observation ids are deterministic and stable: two reconstructions of any committed replay assign identical ids (pinned over a committed set); ids survive store compaction; no RNG anywhere in the scheme.
- [ ] Id-rendering OFF = byte-identical (the golden green with the lever merged OFF); lever-ON renders each remembered observation with its id in a fixture (mechanism-proven; model uptake is 16.15/16.17's business).
- [ ] `primary_reason_observation_id` round-trips the ballot schema additively — every committed replay still parses (backward-compat pinned) — and the manager nulls a dangling id with a marker exactly like the turn-id path, never rejecting the ballot.
- [ ] The voter's valid-id set reaches the manager through typed participant threading (never prose parsing), and a fixture proves a private witnessed-kill observation's id validates while a fabricated id nulls.
- [ ] No gate, guard, or tally consults the new field (asserted) — enforcement is 16.6's, and this task's surface is provably inert with both levers OFF.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Public types introduced:**
- agents.memory.episodic.ObservationId
- agents.memory.store.observation_id_rendering_enabled

**Implementation hint:**

Derive ids as `{agent_id}:{tick}:{seq}` (or equivalent) so replay reconstruction regenerates them
byte-for-byte — the determinism suite is your proof, and any hash-of-content scheme that includes
floats is a trap. The threading is a near-copy of `vent_witness_records_for_meeting` → 
`MeetingParticipant` → validation; mirror the naming so the two channels read as siblings. Keep
(a)–(d) in separately revertable commits: enforcement-free means each layer is independently
provable.

**Integration risk:**

The id scheme is forever — once a recorded baseline renders ids into prompts (16.17), changing the
scheme re-records. Get the determinism suite ruthless now. The ballot-field addition touches the
same schemas file as 16.7's union work: keep to the ballot region, and rebase deliberately if 16.7
lands adjacent edits first (the preamble declares the regions disjoint — honor the declaration).

**Ready-to-paste prompt:** `agent_prompts/task-16-5-observation-identity.md`

### Task 16.6 — J2: citation-gated ballots (default-OFF lever)
**Branch:** `phase-16-j2-citation-gate`
**Depends on:** 16.5
**Section refs:** audits/post-phase-14-Voice-and-Judgment-planning.md §3.4 J2 (the gate design + the null-citation allowance it must respect); meetings/manager.py:1602-1648 (_collect_ballots guard chain — the slot after guard_ballot_target_graph); agents/strategic/prompts/qwen3_32b/vote_ballot.j2:134-153 (the sanctioned null-citation prose the gate must accommodate)
**Complexity:** Integration

The enforcement tooth, last in its chain: a zero-flag EJECT ballot (target carries no
contradiction flag this meeting) whose `primary_reason_id` AND `primary_reason_observation_id`
are both null/invalid is coerced to SKIP with a marker (never a crash, never a re-prompt), as a
new guard slotted AFTER `guard_ballot_target_graph` in `_collect_ballots` — the mark-and-coerce
pattern the guard chain already speaks. Scope honesty, straight from the planning doc's own
analysis: the gate cannot distinguish an honest memory-only conviction from a bare pile-on when
the voter cites nothing — that is WHY 16.5's observation-citation path must land first (an honest
witness can cite their private observation id), and why the DoD's soundness counterfactual is the
task's most important number. Default-OFF lever (`citation_gate_enabled`), registered behind
16.5's entry in the registry chain, stamped, byte-identical OFF.

**Files in scope:**
- meetings/manager.py (the citation-guard region after guard_ballot_target_graph — disjoint from 16.5's validation region and 16.7's turn-validation region)
- meetings/constants.py (the `citation_gate_enabled` resolver — the constants leaf keeps the manager import-clean)
- orchestrator/replay.py (lever registration region — behind 16.5's entry)
- .env.example (the lever env line)
- tests/meetings/test_citation_gate.py (new: coercion fixtures — zero-flag+no-citation coerced; flagged-target unaffected; turn citation satisfies; observation citation satisfies; fabricated citation nulls then coerces)

**Files NOT in scope:**
- meetings/voting.py (the tally consumes coerced ballots; it never learns about citations)
- agents/memory/ (no belief change — this is a ballot-surface guard)
- agents/strategic/prompts/ (the elicitation that ASKS for citations is 16.15's; the gate must behave correctly on today's prompts, where null citations are sanctioned prose)

**Definition of done:**
- [ ] Lever OFF = byte-identical (golden + `verify_samples.sh` green); lever ON changes ONLY the guard chain's output for the gated case (fixtures pin all five cases above).
- [ ] The soundness counterfactual on committed baseline-3 bytes: with the gate hypothetically ON and 16.5's citation path available, the report counts how many CORRECT impostor ejections would have been coerced (the contract's target: near zero, and every such case examined by hand in the PR) and how many soft-only mis-ejects would have been prevented — the J2 half of the judgment trade, measured before any graduation decision.
- [ ] Guard ordering is pinned: the citation guard runs after target-graph redirect (a redirected target's flag status is the redirected target's, not the original's — fixture-proven).
- [ ] The gate coerces, never rejects: a gated ballot becomes SKIP with a marker the transcript/artifacts record (the spectator surface reads it via the existing marker plumbing).
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Public types introduced:**
- meetings.constants.citation_gate_enabled

**Implementation hint:**

Mirror `INVALID_REASON_ID_MARKER`'s shape for the coercion marker and slot the guard exactly where
the chain comment says post-redirect guards live. The zero-flag predicate reads this meeting's
`contradictions` tuple (already in `_collect_ballots` scope) keyed by target — no new plumbing.
The counterfactual rides the same offline machinery as 16.4's; run them on the same bytes so the
16.17 graduation slate reads one coherent judgment table.

**Integration risk:**

This gate is a railroading-INVERSE — its failure mode is silencing honest convictions, which is
invisible in aggregate win rates. The soundness counterfactual (near-zero honest catches blocked)
is the merge bar, and any nonzero count is enumerated case-by-case in the PR for the graduation
slate. Ordering with 16.8's absence delta matters at the margins (absence can push a target over
the gate's zero-flag boundary only via flags, which absence never mints — assert that
non-interaction by test).

**Ready-to-paste prompt:** `agent_prompts/task-16-6-j2-citation-gate.md`

### Task 16.7 — Pooling substrate: typed grounded vouching + the whereabouts claim
**Branch:** `phase-16-pooling-substrate`
**Depends on:** 16.3
**Section refs:** meetings/schemas.py:56-149 (the observation union + VentWitnessRecord — the pattern to generalize); orchestrator/game.py:2369-2403 (the vent accessor to near-copy); meetings/transcript.py:989-1092 (reconstruct_stated_paths — where whereabouts integrate) + :2251-2309 (the vent grounding chokepoint); agents/memory/beliefs.py:387-423 (CORROBORATION_SUSPICION_DELTA — the channel vouching feeds)
**Complexity:** Integration

Make sightings speakable-and-checkable the way 15.4 made vents speakable-and-checkable — with the
polarity inverted. Two halves. (a) **Typed grounded vouching**: a `SightingRecord`
(subject, room, tick, co_present) beside `VentWitnessRecord`; a `sighting_records_for_meeting()`
accessor on the `MeetingAwareAgent` protocol implemented by `TacticalAgent` off the same episodic
rows the vent accessor reads (drop the vent-action filter); `MeetingParticipant.sighting_records`
threading; and a grounding chokepoint in the transcript layer: a spoken `SawPlayerObservation`
that matches the SPEAKER's own typed record (subject + room, tick within tolerance) becomes a
GROUNDED VOUCH — which feeds the existing `corroborated` set (the −0.05 exculpation channel),
NEVER a strong flag and NEVER the dead trust field. The asymmetry with vents is the design:
grounding a sighting proves the speaker honestly reported what they saw — it does not prove the
subject innocent, so it earns the weak exculpation the corroboration channel already prices. An
ungrounded vouch stays ordinary testimony. (b) **The whereabouts claim**: `WhereaboutsClaim`
(room, tick — SELF-placement only; vouching for OTHERS needs no new kind, `SawPlayerObservation`
already expresses it) as the additive fifth observation-union member, validated in the manager's
turn path and integrated into `reconstruct_stated_paths` — answering roll-call places you on the
public record (removing you from 16.8's absence set), and LYING in it creates exactly the
contradiction-detectable material the alibi rules already prosecute.

**Files in scope:**
- meetings/schemas.py (observation-union + SightingRecord + WhereaboutsClaim region — disjoint from 16.5's ballot region)
- orchestrator/game.py (protocol accessor + TacticalAgent implementation region — the vent-accessor sibling; disjoint from 16.9's persona region and the registry line)
- meetings/manager.py (turn-validation + participant-threading region — disjoint from 16.5's ballot-validation and 16.6's guard regions)
- meetings/transcript.py (vouch grounding chokepoint + whereabouts stated-paths integration)
- agents/memory/beliefs.py — NOT edited; the grounded vouch reaches the existing corroborated-set argument through the manager's evidence derivation (listed here to declare the negative explicitly)
- tests/meetings/test_schemas_pooling.py (new)
- tests/meetings/test_vouch_grounding.py (new: grounded feeds corroboration; ungrounded is testimony; fabricated vouch never exculpates)
- tests/orchestrator/test_sighting_accessor.py (new: accessor determinism + protocol coverage, incl. the meeting-double sweep the 15.4 precedent taught)

**Files NOT in scope:**
- meetings/voting.py (tally untouched)
- agents/memory/beliefs.py (no new constant, no new channel — the corroboration delta is consumed as-is; the absence delta is 16.8's)
- agents/strategic/prompts/ (roll-call elicitation is 16.15's; this task is mechanism, fixture-proven)
- api/ + frontend/ (the spectator mirror is 16.7.1's)

**Definition of done:**
- [ ] `SightingRecord` and `WhereaboutsClaim` round-trip their schemas; every committed replay still parses (additive union, backward-compat pinned by loading a committed meeting entry).
- [ ] The accessor is deterministic and self-only (leak-suite covered: an agent reports only its OWN sightings), and every meeting-enabled test double crossing `_build_participants` gains it (the 15.4 protocol-extension sweep, applied on day one).
- [ ] Grounding: a spoken sighting matching the speaker's own record feeds the corroborated set (fixture: subject's suspicion moves by exactly the corroboration delta through the existing caps); an ungrounded or fabricated vouch changes NOTHING in the belief fold (the anti-collusion floor: two impostors vouching for each other with fabricated sightings earn zero exculpation — pinned).
- [ ] A `WhereaboutsClaim` places its speaker in `reconstruct_stated_paths` output (pinned), and a claim contradicting a grounded sighting of the same speaker raises the EXISTING alibi-vs-sighting flag path (no new flag kind — pinned).
- [ ] With no template asking for the new kinds, committed-set behavior is byte-identical (golden + `verify_samples.sh` green) — the mechanism is inert until 16.15 elicits it.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Public types introduced:**
- meetings.schemas.SightingRecord
- meetings.schemas.WhereaboutsClaim

**Implementation hint:**

The accessor is genuinely a near-copy: `game.py:2369-2403` minus the vent-action filter, plus
`co_present` projection — mirror the naming (`sighting_records_for_meeting`) so the channels read
as siblings. The grounding comparator belongs beside `_vent_observation_matches_record` with its
own tolerance constant (start at the vent value; it is a named constant precisely so 16.17's
measurement can retune it). The corroboration feed goes through the manager's existing
evidence-derivation call into `apply_meeting_evidence_rules(corroborated=...)` — thread the
grounded subjects into that argument rather than inventing a parallel path.

**Integration risk:**

Impostor collusion is the adversarial case: two impostors vouching for each other. The fabricated-
vouch fixture (zero exculpation without a matching record) is the floor, but note what grounding
CANNOT catch — an impostor who truthfully vouches for its partner ("I really did see them in
Medbay") earns the −0.05 legitimately. That is correct behavior (the sighting is true), it is
small by design, and the collusion PATTERN (mutual vouching) becomes visible material for Phase
17's detectors — record it as a known property in the module docstring, not a bug. Second risk:
the whereabouts/alibi interaction — a self-placement is almost an alibi claim; reuse the alibi
validators' chronology discipline rather than duplicating it.

**Ready-to-paste prompt:** `agent_prompts/task-16-7-pooling-substrate.md`

### Task 16.7.1 — Spectator mirror: the pooling/citation surface end-to-end
**Branch:** `phase-16-pooling-spectator-mirror`
**Depends on:** 16.5, 16.7
**Section refs:** tasks/phase-15.md 15.4.1 (the mirror precedent); api/schemas.py (the observation-view union + ballot DTO); api/replay_loader.py (the exhaustive claim-view mapping that raises on unknown types); frontend/src/types/api.ts (generated) + the ObservationLine renderer
**Complexity:** Medium

The 15.4.1 lesson, applied on schedule this time: the replay API's observation-claim mapping is
exhaustive-with-raise by doctrine, so any recording that contains a `WhereaboutsClaim` — or a
ballot carrying `primary_reason_observation_id` — would crash or silently drop in the spectator
path unless the mirror lands BEFORE the first such recording (16.17). Mirror `WhereaboutsClaim`
through the API view union, the loader mapping, the regenerated frontend types, and the
`ObservationLine` renderer; surface the ballot's observation-citation field in the ballot DTO
(display-only). Committed sets serve byte-identically.

**Files in scope:**
- api/schemas.py (WhereaboutsClaimView + ballot citation field region)
- api/replay_loader.py (claim-view mapping region — the exhaustive raise stays exhaustive)
- frontend/src/types/api.ts (regenerated — generator output)
- frontend/src/components/ (ObservationLine + ballot-panel render regions)
- tests/api/test_replay_loader_pooling_views.py (new)

**Files NOT in scope:**
- meetings/ (schema source of truth is 16.5/16.7's; the mirror consumes)
- replays/samples/ (served bytes unchanged — pinned)

**Definition of done:**
- [ ] A fixture replay entry carrying a `WhereaboutsClaim` and an observation-cited ballot serves through the full API path and renders (view mapped, types regenerated, renderer displays); the unknown-type raise still fires on a genuinely unknown claim (the doctrine survives).
- [ ] Both committed sets load, serve, and byte-verify unchanged; the frontend type generation is clean (`tsc` green via check.sh).
- [ ] The second observation-rendering switch (the MemoryPanel path the 15-midwave review flagged as a dormant trap) either renders the new kind or is proven structurally unreachable for it — no silent blank.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Public types introduced:**
- api.schemas.WhereaboutsClaimView

**Implementation hint:**

Clone 15.4.1's commit shape: schema view → loader mapping → regenerate types → renderer → tests,
in that order. The ballot citation field is display-only — resist any spectator-side validation
logic; the manager already validated.

**Ready-to-paste prompt:** `agent_prompts/task-16-7-1-pooling-spectator-mirror.md`

### Task 16.8 — The absence prior: a capped sub-gate delta for the publicly unplaced (default-OFF lever)
**Branch:** `phase-16-absence-prior`
**Depends on:** 16.6, 16.7
**Section refs:** meetings/transcript.py:989-1092 (reconstruct_stated_paths — the absence complement is roster minus its keys, computed nowhere today); meetings/manager.py:1830-1861 (_joint_capped_suspicion — the cap everything composes through); agents/memory/beliefs.py:80-99 (the lone-weak-signal discipline); tasks/phase-15.md 15.5 (the boundary-sum pin precedent)
**Complexity:** Medium

The channel that makes visibility a resource: at the pre-vote fold, the ABSENT set — living
players whom nobody's public testimony placed anywhere this meeting (roster minus
`reconstruct_stated_paths(...)` keys, a fold that exists but whose complement is computed
nowhere) — receives a WEAK suspicion delta, `ABSENCE_SUSPICION_DELTA ≤ +0.08`, composed through
`_joint_capped_suspicion` like every meeting-time lift. The sizing is the contract: alone, the
delta must stay sub-gate (0.50 + 0.08 = 0.58 < 0.60 — a quiet crewmate is NEVER ejectable on
absence alone), but absence + testimony-spread deliberately CAN cross the gate (two independent
weak signals is the two-signal eject discipline). That intent must be a TEST, not an accident:
this task pins the lone-signal case AND the stacked combinations (the 15.5 boundary-sum
precedent — every documented crossing combination crosses, every documented non-crossing stays
under, IEEE-luck excluded). Default-OFF lever, registered behind 16.6 in the registry chain.
Note the loop this closes: answering 16.7's roll-call removes you from the absent set — so
impostors gain a reason to account for their time, lying creates prosecutable material, and
staying unseen finally has a price. That is the incentive Phase 17's retraining climbs.

**Files in scope:**
- meetings/transcript.py (the absent-set helper beside reconstruct_stated_paths — behind 16.7's edits)
- agents/memory/beliefs.py (ABSENCE_SUSPICION_DELTA + `absence_prior_enabled` resolver + the fold application region — behind 16.4's clamp region)
- meetings/manager.py (pre-vote absence-fold invocation region — disjoint from 16.3/16.5/16.6/16.7's regions per the preamble map)
- orchestrator/replay.py (lever registration region — behind 16.6's entry)
- .env.example (the lever env line)
- tests/agents/test_absence_prior.py (new: lone-signal + stacked boundary pins + cap composition)
- tests/meetings/test_absent_set.py (new: the set derivation — whereabouts answers remove; unplaced remain; dead players excluded)

**Files NOT in scope:**
- meetings/voting.py (tally untouched)
- agents/perception.py + observation/ (absence is derived from PUBLIC transcript testimony only — the firewall exposes no liveness channel, and this task must not create one)
- replays/samples/ (OFF byte-identical; the re-record is 16.17)

**Definition of done:**
- [ ] The absent set derives ONLY from public testimony (stated paths + whereabouts claims): fixture-pinned, including the firewall negative (no private memory of others feeds it).
- [ ] Lone-signal discipline pinned: absence alone renders 0.58 on a neutral prior — below the gate — and the stacked combinations are pinned BOTH ways (absence + graduated spread crosses; absence + decay-drifted prior does not; the documented table in the test is the design intent).
- [ ] Composition: the delta routes through `_joint_capped_suspicion` and respects `CONTRADICTION_RENDER_CEIL` (asserted); it interacts with 16.6's citation gate only through flag-independence (absence mints no flag — asserted).
- [ ] Lever OFF = byte-identical (golden + `verify_samples.sh` green); the offline counterfactual on committed baseline-3 bytes reports how often the absent set is non-empty, its size distribution, and how many outcomes the delta would flip (the calibration evidence for the 16.17 graduation slate).
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Public types introduced:**
- agents.memory.beliefs.ABSENCE_SUSPICION_DELTA
- agents.memory.beliefs.absence_prior_enabled

**Implementation hint:**

The helper is three lines on top of `reconstruct_stated_paths` — the work is the pins. Build the
boundary table first (every delta combination the docstrings document, with the expected
gate-side), then implement to the table; quantize-then-compare where the 15.6 band lesson applies.
On committed bytes the absent set will often be LARGE (roll-call does not exist yet — 16.15
elicits it), so the counterfactual's honest reading is "what would this delta do TODAY," which is
exactly why the lever stays OFF until the elicitation lands and 16.17 measures the pair together.

**Ready-to-paste prompt:** `agent_prompts/task-16-8-absence-prior.md`

### Task 16.9 — Personas: the role-neutral bank + deterministic assignment (inert until 16.16)
**Branch:** `phase-16-persona-assignment`
**Depends on:** 16.3
**Section refs:** audits/post-phase-14-Voice-and-Judgment-planning.md §4.1 (the without-replacement design + the rejected hash scheme); orchestrator/seeder.py (the random.Random(seed) discipline + the role-neutral id invariant this must mirror); meetings/manager.py MeetingParticipant (the field 16.3 landed); eval/leak_test.py (the suite that must cover the bank)
**Complexity:** Medium

The Voice track's substrate: a committed persona bank (data file, ≥12 entries — at exactly nine,
every 9p2i game uses the whole bank and only seat order varies; twelve-plus makes COMPOSITION vary
game-to-game) and a deterministic assignment: a seeded Fisher–Yates permutation of the bank keyed
by `game_seed`, seat i takes the i-th entry — sampling WITHOUT replacement, so no persona repeats
within a game (the planning doc explicitly rejects independent per-seat hashing: birthday
collisions re-introduce the homogeneity personas exist to break). Every persona is ROLE-NEUTRAL by
construction and by test — assignment happens before roles are known to anything downstream, and
the leak suite asserts no persona↔role correlation across the committed seed range (a persona
that correlates with impostorhood leaks the game). The assignment fills
`MeetingParticipant.persona` (the field 16.3 landed, inert): no template reads it until 16.16, so
this task changes ZERO rendered bytes — the golden proves it.

**Files in scope:**
- orchestrator/personas.py (new: the bank loader + assign_personas)
- data/personas.json (new: the committed bank — disposition-varied cards: aggressive accuser, cautious hedger, quiet observer, jokester, methodical analyst, … ≥12)
- orchestrator/game.py (participant-persona fill region in _build_participants — disjoint from 16.7's accessor region and the registry line)
- tests/orchestrator/test_personas.py (new: determinism, without-replacement, bank-size floor, role-neutrality sweep)

**Files NOT in scope:**
- agents/strategic/prompts/ (no template reads persona until 16.16)
- meetings/ (the field exists from 16.3; consumed as-is)
- orchestrator/seeder.py (personas are meeting-layer inputs, not world-state — seeding stays untouched, replays unaffected)

**Definition of done:**
- [ ] Assignment is a pure function of (seed, roster): two runs at the same seed produce identical assignments (pinned across the committed seed range); no two living players share a persona in any game; the bank-size floor (≥12) is asserted.
- [ ] Role-neutrality is tested, not asserted: across the committed seeds, persona↔role association is measured at chance level (the leak-suite extension), and the bank file carries no role-suggestive text (reviewed field: each card names diction/disposition only).
- [ ] Zero rendered-byte change: the golden and `verify_samples.sh` green with assignment live (the field fills; nothing reads it).
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Public types introduced:**
- orchestrator.personas.PersonaCard
- orchestrator.personas.assign_personas

**Implementation hint:**

Mirror the seeder's discipline exactly: one `random.Random(derived_seed)` instance, shuffle a
sorted copy of the bank, zip with sorted seats. Derive the persona seed from the game seed with a
fixed offset/namespace so persona assignment never perturbs the seeder's existing draws (replay
byte-identity depends on the seeder's stream staying untouched — do NOT share its Random
instance). Keep the bank's cards short (a disposition line + two diction notes); 16.16 writes the
full preamble text.

**Ready-to-paste prompt:** `agent_prompts/task-16-9-persona-assignment.md`

### Task 16.10 — The V&J instruments: pooling folds + judgment metrics + deterministic voice tier
**Branch:** `phase-16-vj-instruments`
**Depends on:** 16.3, 16.5, 16.7
**Section refs:** eval/funnel.py (the three-stage instrument this extends); audits/post-phase-14-Voice-and-Judgment-planning.md §2 (the measurement harness design: zero-flag channel, claim-ECE, voice metrics); scripts/measure_baseline.py (the CLI the folds surface through); audits/audit-phase-15-close.md §11 (the conversion-seam finding these instruments must make measurable)
**Complexity:** Medium

The phase's own before/after instrument, committed BEFORE the levers turn on (the 15.1/15.3
lesson: the instrument lands first, the close reads it). Three groups. (a) **Pooling folds**
(`eval/funnel.py` extension region): roll-call coverage (share of living players publicly placed
per meeting), vouch rate and GROUNDED-vouch rate, absence-set size distribution, and
whereabouts-lie detection rate (claims contradicted by grounded sightings). (b) **Judgment
metrics** (new `eval/vj_instruments.py`): the zero-flag conviction rate with its soft/hard split
read off 16.3's TYPED provenance (replacing the planning doc's rendered-value proxy — the
instrument upgrade the foundation makes possible), citation-compliance rate (ballots citing turn
or observation, valid vs dangling), and ballot-confidence calibration (Brier/ECE against
conviction correctness — the 15.11 harness pattern applied to the recorded ballots). (c) **The
deterministic voice tier**: within-meeting echo rate, response-skeleton share, distinct-n
diversity — the cheap, deterministic slice of the planning doc's voice metrics (the LLM-judged
tier is explicitly out: $0 discipline). All folds run on any replay-set directory and surface
through a `scripts/measure_baseline.py --vj` region; committed baseline-3 bytes are the
reproduction fixture wherever a figure already exists (the close audit's zero-flag and conversion
cells), and every new fold ships with a synthetic fixture proving it can move.

**Files in scope:**
- eval/funnel.py (pooling-folds extension region — additive; the 15.3 folds untouched)
- eval/vj_instruments.py (new: judgment metrics + voice tier + report types)
- scripts/measure_baseline.py (the --vj fold region — this task is the phase's ONLY measure_baseline toucher)
- tests/eval/test_vj_instruments.py (new: reproduction pins where figures exist + synthetic movement fixtures)
- tests/eval/test_funnel_pooling.py (new)

**Files NOT in scope:**
- eval/watchability.py (the referee is 16.11's; instruments here are diagnostics, never gates)
- eval/validity.py (no gate change)
- meetings/ + agents/ (read-only reconstruction — the folds observe, never touch)

**Definition of done:**
- [ ] On committed baseline-3 bytes, the zero-flag conviction rate and citation-compliance folds reproduce the close audit's cells where they exist, and the soft/hard split cross-checks against 16.3's provenance sums (the typed upgrade is consistent with the rendered-value proxy within documented tolerance).
- [ ] Every pooling fold reads zero/empty on committed bytes where the mechanism doesn't exist yet (no roll-call → coverage 0, absence set = unplaced share as-is) and moves on a synthetic fixture — an instrument that cannot move is not an instrument.
- [ ] The voice tier is deterministic (double-run identical) and $0; its per-meeting rows join the same report as the judgment metrics so 16.17 reads voice ALONGSIDE zero-flag (the phase's named NO-GO pairing).
- [ ] `scripts/measure_baseline.py --vj` emits the machine-readable report the 16.17 close consumes; the JSON shape is documented in the module docstring.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Public types introduced:**
- eval.vj_instruments.VJInstrumentReport
- eval.vj_instruments.compute_vj_instruments

**Implementation hint:**

Reuse the 15.3 walk (the folds are meeting-scoped reconstructions over the same replay stream);
the provenance cross-check is the one novel join — read 16.3's decomposition off the
reconstructed belief state at pre-vote, exactly where the render reads it. Keep gate-shaped
language out of this module: these are diagnostics the close QUOTES; the referee alone gates.

**Ready-to-paste prompt:** `agent_prompts/task-16-10-vj-instruments.md`

### Task 16.11 — The referee re-anchor: population-relative testimony-backed conversion
**Branch:** `phase-16-referee-reanchor`
**Depends on:** none
**Section refs:** audits/audit-phase-15-close.md §10 (the owner ruling this implements) + §11 (the conversion-seam finding); eval/watchability.py (the per-baseline floors block + the subject-aware backing definition 15.19 landed); training/reports/results-champion-close.jsonl (the committed calibration fixture)
**Complexity:** Medium

Implement the owner-ratified recalibration (2026-07-11): the `testimony_backed_conversion` floor
stops being the FSM baseline's absolute constant (0.6636 — the value the champion close FAILED
against, first non-FSM population ever measured) and becomes POPULATION-RELATIVE: the floor
derives from the scored population's own evidence supply and backing base-rate, so a candidate is
judged on whether its games CONVERT the testimony they actually contain, not on whether they
reproduce another population's ratio. The starvation catch must stay sharp: a synthetic
evidence-starved set (high meeting rate, zero backed accusations) fails regardless of population.
The committed champion-close row is the calibration fixture: under the new definition it must
read as the intended non-blocking outcome (the owner's close-over ruling, now derived rather than
ruled), documented in the module with the derivation. The other two supply floors
(witnessed-event rate, flags-per-meeting) keep their per-baseline pinned form — this task
re-anchors exactly the one gauge the close contracted forward.

**Files in scope:**
- eval/watchability.py (the conversion-floor definition + the per-baseline floors block region — ahead of 16.14/16.17's pins)
- tests/eval/test_watchability_reanchor.py (new: the champion-close fixture reproduction + the synthetic-starved FAIL + the FSM-baseline consistency check)

**Files NOT in scope:**
- eval/validity.py + eval/vj_instruments.py (gate definitions only here; diagnostics are 16.10's)
- training/reports/ (the fixture is read, never rewritten)
- scripts/measure_baseline.py (16.10 owns the CLI region this phase; the referee's existing --watchability surface is unchanged in shape)

**Definition of done:**
- [ ] The population-relative definition is implemented with its derivation documented (what "the scored population's own achievable conversion" means, mechanically), and the per-baseline floors block carries it for baseline-3 (existing sets re-measured, values pinned with the derivation in comments).
- [ ] The champion-close fixture reproduces: `results-champion-close.jsonl`'s recorded gauges, re-scored under the new definition, yield the non-blocking outcome the owner ruling anticipated — with the old-definition FAIL preserved in the test as the historical contrast.
- [ ] A synthetic starved set still FAILS (the floor's reason to exist survives the re-anchor), and the FSM baseline itself still PASSES at equality (self-consistency).
- [ ] The referee's module docstring records the ruling's provenance (close audit §10, owner 2026-07-11) and the Q1-precedent rationale.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Public types introduced:**
- eval.watchability.population_relative_conversion_floor

**Implementation hint:**

The honest derivation ties the floor to the population's own backing supply: of the accusations
its games produce, what share is subject-aware-backed (the 15.19 definition), and what conversion
does that supply support — the floor is a function of measured supply, not a constant. Keep the
function pure and the derivation quotable (the 16.17 close audit will print it). Resist widening
scope: one gauge re-anchors; the geomean, the other floors, and the integrity floor are untouched.

**Ready-to-paste prompt:** `agent_prompts/task-16-11-referee-reanchor.md`

## Wave 2 — the model swap (GO-conditional; activated or dropped by 16.2)

### Task 16.12 — Model onboarding: the production client, the locked literals, the doctrine docs
**Branch:** `phase-16-model-onboarding`
**Depends on:** 16.2
**Section refs:** audits/audit-phase-16-model-lock.md (the decision this implements); llm/featherless_client.py:135 (DEFAULT_FEATHERLESS_MODEL) + :556-592 (_THINKING_KWARG_BY_MODEL — the fail-loud exact-id registry) + :18-32 (response_format_mode posture); llm/provider.py:64-73 (the $0 provider-keyed pricing — assert, don't touch); scripts/refresh_samples.sh + scripts/record_ml_corpus.sh (the locked literals)
**Complexity:** Small

GO-path only. Make the locked model the production default, everywhere the incumbent is pinned:
the `_THINKING_KWARG_BY_MODEL` entry (the exact served id from the lock audit, with the
thinking-kwarg boolean the 16.1 probe verified — an unregistered id fails loud on every call, by
design), `DEFAULT_FEATHERLESS_MODEL`, the `refresh_samples.sh` model literal, a loud
comment in `record_ml_corpus.sh` that the committed corpus remains baseline-3/old-model substrate
pending Phase-17 re-grounding — the corpus script's PIN BLOCK (model + set + versions) is NOT
edited: its preflight couples the three, and the pins coherently describe the frozen artifacts
they guard; 16.17 re-pins the whole block to the baseline-5 substrate — the `response_format_mode`
posture if the probe's verdict differs from `json_object`, the client test pins, and the doctrine
docs (AGENTS.md provider section, README provider table, .env.example). The $0 cost path needs NO
change (provider-keyed empty pricing dict — every Featherless model resolves to the 0.0 fallback);
assert it in a test rather than re-implementing anything.

**Files in scope:**
- llm/featherless_client.py (the registry entry + DEFAULT_FEATHERLESS_MODEL + response_format posture region)
- scripts/refresh_samples.sh (the model-literal lines — disjoint from 16.13's prompt-set-literal lines)
- scripts/record_ml_corpus.sh (the stale-corpus COMMENT only — the model/set/versions pin block is untouched; 16.17 owns it)
- tests/llm/test_featherless_client.py (default-model + registry pins)
- tests/scripts/test_refresh_samples.py (model-literal pin region — disjoint from 16.13's set-gate pin region)
- AGENTS.md (provider doctrine region)
- README.md (provider table region — the sample-provenance paragraph is 16.14's)
- .env.example (the featherless model lines — disjoint from the lever lines)

**Files NOT in scope:**
- llm/provider.py (the $0 table is provider-keyed and correct as-is — a test asserts the new id resolves to $0; no edit)
- agents/strategic/prompts/ (the bespoke set is 16.13's)
- replays/ (committed sets untouched; they verify regardless of the default — reconstruction never re-invokes a model)

**Definition of done:**
- [ ] The locked served id is registered in `_THINKING_KWARG_BY_MODEL` with the probe-verified boolean, is the `DEFAULT_FEATHERLESS_MODEL`, and a payload-construction test exercises it (the fail-loud path proven by a deliberate unknown-id fixture).
- [ ] A test asserts the new id resolves to $0 under `_compute_cost_usd` (provider-keyed fallback — asserted, not re-implemented).
- [ ] `refresh_samples.sh` carries the new model literal with its script-test pins updated in this task; `record_ml_corpus.sh` carries the stale-corpus comment with its pin block UNCHANGED (`tests/scripts/test_record_ml_corpus.py` stays green untouched — asserted); committed sets still byte-verify (`bash scripts/verify_samples.sh` green — the default swap cannot touch recorded bytes).
- [ ] AGENTS.md / README / .env.example name the new canonical model with the lock-audit citation.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Ready-to-paste prompt:** `agent_prompts/task-16-12-model-onboarding.md`

### Task 16.13 — The bespoke set `qwen3_6_27b` v1: semantics ported exactly, restyled to the new model
**Branch:** `phase-16-bespoke-set`
**Depends on:** 16.2
**Section refs:** audits/audit-phase-16-model-lock.md; agent_prompts/task-14-5-new-model-prompts.md (the bespoke-set precedent); agents/strategic/prompts/qwen3_32b/ (the v5/v6 source semantics); orchestrator/game.py PROMPT_VERSION_SETS (:317 — the registry the new entry joins); experiments/lab/featherless_sweep.py (the A/B instrument, --prompt-set axis)
**Complexity:** Medium

GO-path only, ∥ 16.12. Author `agents/strategic/prompts/qwen3_6_27b/` — the four templates,
porting the `qwen3_32b` v5/v6 SEMANTICS exactly (the vent-elicitation instructions, the
reporter-exculpation section, the schema examples, every mechanical directive) restyled to the
new model's idioms per the 16.1 probe's findings. Baseline 4 must be MECHANICS-PURE: same asks,
same sections, same defaults — a reader diffing the two sets should find style, never semantics
(the 16.15 elicitation batch adds the NEW asks afterward, on this set, as its own attributable
layer). Register `_bespoke_versions("qwen3_6_27b", version="v1")` in `PROMPT_VERSION_SETS`
(one new line — the registry line then serializes 16.13 → 16.15 → 16.16), add the set to
`BESPOKE_SETS` in the bespoke-set test suite, flip `refresh_samples.sh`'s `REQUIRED_PROMPT_SET`
literal (a disjoint line from 16.12's model literal; `record_ml_corpus.sh` is NOT touched — its
preflight couples set+versions and flipping one alone fails it; 16.17 re-pins that block whole),
register the set in the sweep harness's `_SET_OWNER` map (the sweep REJECTS an unregistered
`--prompt-set` before it starts — without this the A/B is unrunnable in scope), and operator-run
the A/B as a TWO-PASS protocol on the one new set (`_SET_OWNER` binds each set to its model, so
`--prompt-set qwen3_32b` on the Qwen3.6 model is structurally rejected — the control cannot be a
cross-set run): pass 1 sweeps the VERBATIM-PORT commit of `qwen3_6_27b/` (the control arm — commit
it first, sweep it, record the template-source sha in the rows), pass 2 sweeps the RESTYLED
commit (the candidate arm); the committed rows carry the sha per arm so the comparison is
control-vs-restyle on the same model, same contexts — the evidence that the restyle helps, or at least does not
hurt, before baseline 4 spends a record on it.

**Files in scope:**
- agents/strategic/prompts/qwen3_6_27b/ (new: crewmate_report.j2, impostor_report.j2, accusation_round.j2, vote_ballot.j2)
- orchestrator/game.py (the new PROMPT_VERSION_SETS line — disjoint from 16.7/16.9's regions; serializes ahead of 16.15/16.16)
- tests/agents/test_bespoke_prompt_sets.py (BESPOKE_SETS registration — the parametrized suites pick the set up automatically)
- scripts/refresh_samples.sh (REQUIRED_PROMPT_SET literal — disjoint from 16.12's model lines)
- tests/scripts/test_refresh_samples.py (set-gate pin region — disjoint from 16.12's model-literal pin region)
- experiments/lab/featherless_sweep.py (_SET_OWNER map entry + any slate wiring the A/B needs)
- experiments/lab/results-featherless-sweep-qwen3-6-27b-ab.jsonl (new: the A/B rows)
- experiments/lab/report-featherless-sweep-qwen3-6-27b.md (A/B section appended)

**Files NOT in scope:**
- agents/strategic/prompts/qwen3_32b/ (the source set is frozen — provenance-versioned bytes)
- scripts/record_ml_corpus.sh (its preflight compares `PROMPT_VERSION_SETS[$REQUIRED_PROMPT_SET]` to `REQUIRED_PROMPT_VERSIONS` — a set flip without a versions flip fails it, and its pins coherently describe the FROZEN corpus; 16.17 re-pins the whole block)
- meetings/ + agents/memory/ (templates only)
- replays/ (the record is 16.14's)

**Definition of done:**
- [ ] The four templates render under StrictUndefined with the full kwarg surface (the bespoke-set suite green), and a semantics diff table in the PR maps every v5/v6 mechanical directive to its ported location — nothing added, nothing dropped (the mechanics-pure claim, reviewable).
- [ ] The registry entry, BESPOKE_SETS registration, the refresh_samples set literal (with its script-test pins updated here), and the `_SET_OWNER` sweep registration all land; `AILIBI_PROMPT_SET=qwen3_6_27b` is env-selectable end-to-end (suite-proven), and `tests/scripts/test_record_ml_corpus.py` stays green UNTOUCHED (the corpus script is out of scope — asserted).
- [ ] The operator A/B rows are committed under the two-pass protocol (pass 1 = verbatim-port commit, pass 2 = restyled commit, each row carrying its template-source sha) — parse rates, grade booleans, latency per arm on the same model and contexts — and the report states the verdict (restyle adopted or the verbatim port kept; either is a finding).
- [ ] The prompt-byte golden still passes on committed sets (nothing here touches the old set or its renders).
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

Start from a verbatim copy of the v5/v6 set, then restyle incrementally with the A/B as the judge —
the 14.5 lesson is that bespoke sets earn their keep on parse reliability and instruction-following
under the target model's chat template, not on prose elegance. The probe's thinking/response-format
findings dictate the frame (system-message shape, JSON envelope phrasing). Keep every section
anchor the loader/tests reference.

**Ready-to-paste prompt:** `agent_prompts/task-16-13-bespoke-set.md`

### Task 16.14 — Baseline 4: the model-only atomic re-record + the champion re-audit (operator-run, $0)
**Branch:** `phase-16-baseline-4`
**Depends on:** 16.3, 16.11, 16.12, 16.13
**Section refs:** tasks/phase-15.md 15.7 (the atomic re-record runbook this clones); audits/audit-phase-16-model-lock.md (the substrate this records); eval/watchability.py (16.11's re-anchored referee + the per-baseline floors block); training/reports/results-champion-close.jsonl (the stamp-proof row convention the re-audit follows)
**Complexity:** Integration

GO-path only. Record **baseline 4** — both canonical sets on the locked model + the `qwen3_6_27b`
v1 set — with the model as the ONLY layer change: every Phase-16 lever merged OFF/inert (the
preflight: the prompt-byte golden green and `verify_samples.sh` bare on the pre-record tree),
mechanics byte-equivalent to baseline 3's. The 15.7 runbook end-to-end: 2 Featherless workers,
per-seed crash-retry, atomic staging, MANIFEST + report + rubric regeneration,
`audits/baseline3-final-measure.json` captured at the pre-replacement tip (the BEFORE column —
baseline 3 survives only in git history after this), the Q5 annotated tag at the recording
commit, README sample-provenance refresh, and the byte-coupled test re-pin sweep. Measurement:
the validity gate (with `--expected-model` flipped to the locked id), the re-anchored referee
(16.11's definition; baseline-4 floors pinned from the new bytes), the funnel, and the canaries
under the DEGRADED-Q3 rule (50-seed sets, two-proportion discipline, UNDERPOWERED recorded
honestly; the corpus quoted as stale context only). Same operator session, second artifact: the
opt-in champion's 50-seed re-audit against the new meeting substrate —
`scripts/run_tournament.py --agent-factory learned-champion` on the audit seeds, measurement
committed as `training/reports/results-champion-qwen35-audit.jsonl` with the stamp-proof rows
(read back from bytes, never echoed), raw recordings uncommitted. The champion was selected under
Qwen3-32B meetings; this is the honest re-reading, NOT a retrain (Phase 17's business), and a
degraded champion result is a FINDING for the close + Phase 17, never a blocker.

**Files in scope:**
- replays/samples/9p2i/ (the baseline-4 set)
- replays/samples/4p1i/ (the baseline-4 set)
- audits/baseline3-final-measure.json (new: the BEFORE column, captured pre-replacement)
- audits/audit-phase-16-baseline-4.md (new: the model-swap measurement — funnel/R-gate/referee/canaries before/after + the champion re-audit reading)
- training/reports/results-champion-qwen35-audit.jsonl (new: the champion re-audit rows, stamp-proven)
- eval/watchability.py (baseline-4 floors in the per-baseline block region — behind 16.11's definition)
- scripts/validity_gate.py + scripts/measure_baseline.py — NOT edited; invoked (listed to declare the negative)
- README.md (sample-provenance paragraph region)
- tests/ (the byte-coupled re-pin sweep: manifest rows, committed-report aggregates, transcript pins — the 15.7 list plus whatever the sweep finds)

**Files NOT in scope:**
- replays/ml_corpus/ (stale by design after this record — Phase 17 re-grounds; the close audit re-states it)
- agents/ + meetings/ + engine/ (zero mechanics — the preflight proves it)
- agents/tactical/learned/ (the champion is measured, never modified)

**Definition of done:**
- [ ] Preflight proven and quoted in the audit: golden green + bare `verify_samples.sh` on the pre-record tree, every `_TOGGLEABLE_LEVER_RESOLVERS` entry OFF, `refresh_samples.sh`'s `REQUIRED_PROMPT_SET` literal matching the locked set, and HEAD's `PROMPT_VERSION_SETS` resolving that set to exactly `*.qwen3_6_27b.v1` (the registry is the version authority — `refresh_samples.sh` carries no version literal, and `record_ml_corpus.sh`'s coupled block stays baseline-3 until 16.17; the recorded MANIFEST provenance check below is the on-disk proof).
- [ ] Both sets recorded at the locked substrate, committed atomically with MANIFEST provenance exact (locked model id, v1 versions, six retired flags, git_sha, $0, winner) and the Q5 annotated tag; `scripts/validity_gate.py --expected-model <locked-id> --require-zero-cost` PASSES both sets; byte-identical reconstruction clean BARE.
- [ ] The BEFORE column is committed (`audits/baseline3-final-measure.json`, named with its tip sha) and the audit's before/after table regenerates from it + the new bytes via the committed CLIs — funnel, R-gate, referee (16.11 definition), canaries (degraded-Q3 discipline, UNDERPOWERED honestly recorded when the CI spans both hypotheses).
- [ ] Baseline-4 floors pinned in the per-baseline block with measured values; `measure_baseline.py --watchability` clean on the new sets.
- [ ] The champion re-audit rows are committed with the stamp-equality proof (all 50 games, read back from recording bytes) and the audit reads the result explicitly as finding-not-blocker, routed to the close + Phase 17.
- [ ] The byte-coupled re-pin sweep lands in this PR; `bash scripts/check.sh` green on the final tree is the proof.
- [ ] A canary regression (genuine-class conversion or R1 outside the pre-registered band on the 50-seed test) PAUSES the phase for an owner call — recorded as the one NO-GO, not absorbed.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

The 15.7 runbook transfers nearly verbatim — the deltas are the `--expected-model` flip, the
16.11-definition referee, and the champion re-audit leg (clone the 15.18 finalist-eval recipe:
tournament CLI with the factory flag, measurement via the committed CLIs, stamp rows from
`read_tactical_policy_stamp`). Budget ~4–5h wall for the two sets + ~2.5h for the champion leg;
the pre-registered canary bands go in the audit BEFORE the record starts (the 15.18 discipline).

**Integration risk:**

This is a substrate re-record with a model nobody has recorded at scale: the A/B sweep de-risks
parse behavior, but live full-game recording is where latency/truncation/format edge cases
surface — the per-seed crash-retry budget and the "record-only discipline" (a disappointing
uptake number is a finding for 16.15, never a mid-record prompt iteration) are the guardrails.
The re-pin sweep is the usual long tail; 15.7's list is the map, but the model swap may move
cells 15.7's didn't (different dialogue → different transcript pins).

**Ready-to-paste prompt:** `agent_prompts/task-16-14-baseline-4.md`

## Wave 3 — elicitation and personas on the locked set

### Task 16.15 — The elicitation batch: citations, roll-call, provenance surface, the vent tail, the self-accusation fix
**Branch:** `phase-16-elicitation-batch`
**Depends on:** 16.2, 16.5, 16.6, 16.7, 16.14
**Section refs:** audits/post-phase-14-Voice-and-Judgment-planning.md §3.4 J2a/J3 (the surface design); audits/audit-phase-15-close.md §11 (the vent-tail cells: samples 53/73 mentioned; corpus 188/255) + §5.2 of the wave-0 close (the self-accusation artifact, 3/851); the locked set directory per 16.2 (GO: agents/strategic/prompts/qwen3_6_27b/; the NO-GO rewrite is 16.2's surgery)
**Complexity:** Integration

The prompt surface that makes the Wave-1 machinery SPEAK, all four templates, ONE version bump
owned here (GO path: the set advances v1 → v2 in its `PROMPT_VERSION_SETS` entry; under NO-GO
16.2 rewrites this task to per-template bumps on `qwen3_32b` — three v5 templates → v6,
`vote_ballot` v6 → v7 — never a set-level relabel that would mint a colliding
`vote_ballot.qwen3_32b.v6`). Five coordinated asks: (a) **J2a provenance surface** — the ballot
template renders each candidate's suspicion WITH its provenance split (carried prior vs
this-meeting evidence, soft-only rows annotated) via 16.3's kwargs; (b) **J3 citation-required
confidence** — the ballot asks for a cited turn id or observation id with every EJECT (16.5's
rendered ids give it something to cite; the sanctioned gut-read example is REWRITTEN to cite or
skip), with confidence verbalized against the citation; (c) **roll-call elicitation** — the
opening/turn templates ask each speaker to state where they were (emitting 16.7's
`WhereaboutsClaim`) and to voice relevant sightings of others; (d) **the vent tail** — the
elicitation ask that targets the ~20/73 unspoken held vents (close audit cells; the mechanism
exists, the ask must land harder); (e) **the self-accusation fix** — the impostor turn/ballot
framing that closes the 3/851 self-naming artifact. Every ask is mechanism-tested by fixture
(template output contains the elicitation; a compliant response parses into the typed kinds);
UPTAKE is 16.17's measurement, record-only discipline.

**Files in scope:**
- agents/strategic/prompts/qwen3_6_27b/ (all four templates — the locked set per 16.2; behind 16.13's creation and 16.14's record)
- orchestrator/game.py (the locked set's PROMPT_VERSION_SETS entry — the single bump this task owns; behind 16.13's line)
- tests/meetings/test_elicitation_fixtures.py (new: per-ask mechanism fixtures)
- tests/agents/test_bespoke_prompt_sets.py (version-pin region for the bumped entry)

**Files NOT in scope:**
- meetings/ + agents/memory/ (the machinery landed in Wave 1; this is surface only)
- scripts/refresh_samples.sh + scripts/record_ml_corpus.sh (version literals flip at 16.17, the adopting record)
- replays/samples/ (the re-record is 16.17)

**Definition of done:**
- [ ] All five asks land with per-ask fixtures: rendered output carries the elicitation; a synthetic compliant response round-trips into `WhereaboutsClaim`/observation-cited ballots/vent observations through the real validation path.
- [ ] The provenance surface renders ONLY when the render inputs supply it (lever/kwarg-gated — committed-set renders stay byte-identical, golden green), and the soft-only annotation matches 16.3's typed decomposition on a fixture.
- [ ] The gut-read example is gone: the ballot template's exemplars either cite (turn or observation id) or SKIP — no sanctioned null-citation EJECT remains in any template.
- [ ] The version bump is exactly one registry entry (pinned); pre- and post-batch prompt bodies can never share a version stamp.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

Write the asks as tight structural directives with one worked example each (the v5 vent-elicitation
lesson: the example moves uptake more than the instruction). The J3 rewrite is the delicate one —
the template currently BLESSES null citations; invert the exemplar without inverting the SKIP
allowance (memory-based SKIP stays legitimate; memory-based EJECT now cites the observation id
16.5 renders). Fixtures assert presence and parseability, never model behavior.

**Integration risk:**

Five asks in one bump is deliberate (one attributable prompt layer at 16.17) but couples their
review: a defect found in one ask after the bump re-bumps the set. Mitigate with per-ask fixture
coverage and the A/B habit — an operator spot-run on a handful of contexts before merge is cheap
insurance the contract permits (not a recorded artifact, just diligence). The roll-call ask
interacts with turn budget (nine speakers stating whereabouts consumes tokens) — keep the ask to
one line of the response schema, not a paragraph.

**Ready-to-paste prompt:** `agent_prompts/task-16-15-elicitation-batch.md`

### Task 16.16 — Persona text: the voice layer, evidence-gated (second bump)
**Branch:** `phase-16-persona-text`
**Depends on:** 16.9, 16.15
**Section refs:** audits/post-phase-14-Voice-and-Judgment-planning.md §4.1-4.2 (the persona-conditioning design + the distinctness toolkit + the design caution); orchestrator/personas.py (16.9's bank + assignment); the locked set directory (behind 16.15's bump)
**Complexity:** Medium

The Voice half, landing last by design (the edges enforce the planning doc's thesis: the citation
gate and the judgment surface are merged before any voice gets louder). Render each participant's
persona card into the instruction preamble of all four templates — disposition + diction notes
shaping HOW the agent talks (`free_text`/`rationale_text` style), never WHAT it may claim
(observations/claims/ballots stay schema-locked; the persona never enters `rendered_memory` — the
firewall-orthogonality the planning doc proves). Guarded byte-identical: an empty persona renders
the exact pre-16.16 bytes (golden-proven), so the layer is inert wherever assignment is off. One
version bump owned here (the second on the locked set: v2 → v3 GO path; the NO-GO arithmetic per
16.2's surgery). Distinctness discipline from the toolkit: contrasting dispositions in the bank,
per-turn re-anchoring line, and the anti-sycophancy contrast (the aggressive-accuser /
cautious-hedger / quiet-follower spread that resists premature consensus). The phase's named
pairing is enforced at close: 16.17 reads the voice metrics ALONGSIDE the zero-flag conviction
rate — a zero-flag rise attributable to personas is the phase NO-GO.

**Files in scope:**
- agents/strategic/prompts/qwen3_6_27b/ (persona preamble region in all four templates — behind 16.15's edits)
- orchestrator/game.py (the locked set's version entry — the second bump; behind 16.15's)
- data/personas.json (card-text refinement region — the bank 16.9 committed; structure unchanged)
- tests/meetings/test_persona_render.py (new: empty-persona byte-identity + per-card render fixtures + the re-anchor line presence)

**Files NOT in scope:**
- orchestrator/personas.py (assignment logic frozen from 16.9; only card TEXT refines)
- meetings/ + agents/memory/ (no mechanism — pure surface)
- replays/samples/ (the re-record is 16.17)

**Definition of done:**
- [ ] Empty persona = byte-identical render (golden green on committed sets); each bank card renders into the preamble on a fixture with the schema-locked sections untouched.
- [ ] The persona text shapes style only: fixtures assert the persona block appears in the instruction preamble and NOWHERE in the memory/observation sections; the leak-suite role-neutrality sweep re-runs green on the refined cards.
- [ ] The second version bump is exactly one registry entry; the per-turn re-anchor line is present in the turn template (drift discipline).
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

Persona cards read as stage directions, not biographies: one disposition sentence, two diction
notes, one thing this voice never does. The re-anchor line ("stay in the voice described above")
goes at the turn template's response instructions — the cheap fix for multi-turn drift the
literature and the toolkit both point at. Resist trait taxonomies; the bank is a spread of
argumentative dispositions, which is what breaks consensus cascades.

**Ready-to-paste prompt:** `agent_prompts/task-16-16-persona-text.md`

## Wave 4 — the close

### Task 16.17 — Baseline 5: the graduation slate, the atomic re-record, the phase close (operator + owner, $0)
**Branch:** `phase-16-baseline-5-close`
**Depends on:** 16.7.1, 16.8, 16.10, 16.11, 16.16
**Section refs:** tasks/phase-15.md 15.7 + 15.23 (the graduate-at-record runbook + the close-gates pattern); the Wave-1 counterfactuals (16.4/16.6/16.8's committed reports — the graduation evidence); eval/vj_instruments.py (16.10 — the before/after instrument); audits/audit-phase-16-baseline-4.md (the BEFORE column, GO path; NO-GO: the baseline-3 measure file per 16.2's rewrite)
**Complexity:** Integration

The phase's terminal record and its second owner gate. **Preflight — the GRADUATION SLATE (owner
decision):** for each Wave-1 lever — J1 hard-evidence gate (16.4), observation-id rendering
(16.5), J2 citation gate (16.6), the absence prior (16.8) — the owner rules graduate-ON or
stay-OFF, each ruling citing the lever's committed counterfactual against its named canary (J1:
zero hard-backed outcome changes; J2: near-zero honest catches blocked; absence: the boundary
pins + set-size evidence; id-rendering: golden-proven inertness + 16.15's citation surface needs
it ON). A lever that fails its canary stays OFF as a RECORDED decision — with the disable-path
honesty this contract can actually deliver: for levers whose surface is kwarg/lever-gated with no
template presence (J1, the absence prior), stay-OFF is coherent as-is; but for the COUPLED pair
whose elicitation surface 16.15 already landed (the citation gate + observation-id rendering —
the templates now ask for citations the substrate would neither render ids for nor honor), a
stay-OFF ruling CANNOT be absorbed by this task (the template retreat is out of scope and needs
its own version bump), so that outcome PAUSES the close for owner re-planning and the surface
retreat becomes a new contract — a defect the close finds becomes a contract, never a close edit. **Then the 15.7 runbook:** graduate the slate
at the record (resolvers constant-true, registry entries → `_RETIRED_ALWAYS_ON_LEVERS` — C6
discharged, bare reconstruction), re-pin `record_ml_corpus.sh`'s coupled pin block (model + set +
`REQUIRED_PROMPT_VERSIONS`) to the baseline-5 substrate with its stale-corpus comment updated to
name the substrate any future corpus records at (`refresh_samples.sh` needs no edit here — it has
no version literal; HEAD's registry governs, and the MANIFEST provenance check is the proof), record both sets
atomically on the locked model + final prompt versions, Q5 tag, validity gate + the re-anchored
referee + baseline-5 floor pins. **The close reading:** the full before/after on 16.10's
instruments — zero-flag conviction rate (soft/hard split), citation compliance, roll-call
coverage, vouch and grounded-vouch rates, absence-set sizes, whereabouts-lie detections, voice
metrics ALONGSIDE zero-flag (the named NO-GO pairing), conversion under the population-relative
floor, the funnel, canaries under the degraded-Q3 discipline — every number from the committed
CLIs, BEFORE column from the committed measure file. `audits/audit-phase-16-close.md` records
the slate rulings, the uptake findings (elicitation asks vs measured compliance — findings, not
pass bars), re-states the Phase-17 staleness rule (surrogate/corpus/champion are
prior-substrate-anchored; re-ground before any training), and flips this file's banner to CLOSED.

**Files in scope:**
- replays/samples/9p2i/ (the baseline-5 set)
- replays/samples/4p1i/ (the baseline-5 set)
- agents/memory/beliefs.py (resolver graduation region — constants to True per the slate; behind the lever chain)
- meetings/constants.py (citation-gate resolver graduation region)
- agents/memory/store.py (id-rendering resolver graduation region)
- orchestrator/replay.py (registry graduation region — slate entries to retired)
- scripts/record_ml_corpus.sh (the FULL pin block — model + set + versions — re-pinned coherently to the baseline-5 substrate, with the stale-corpus comment updated; its preflight couples the three, so this is the one task that moves them together) + its tests/scripts pin sweep. NOTE: `scripts/refresh_samples.sh` carries NO version literal (only the set-name gate, already flipped by 16.13) — it records whatever HEAD's registry resolves, which at this task IS the 16.15/16.16 versions; the version proof is the recorded MANIFEST provenance check in the DoD, not a script literal
- eval/watchability.py (baseline-5 floors region — behind 16.11/16.14's)
- audits/baseline4-final-measure.json (new: the BEFORE column, captured pre-replacement — GO path naming; 16.2's surgery renames under NO-GO)
- audits/audit-phase-16-close.md (new)
- tasks/phase-16.md (the STATUS banner flip to CLOSED — or to PAUSED on the slate's pause path; the 15.23 precedent)
- README.md (sample-provenance paragraph)
- tests/ (graduation re-pins + the byte-coupled sweep)

**Files NOT in scope:**
- replays/ml_corpus/ (stale; Phase 17 re-grounds — the audit re-states it)
- agents/tactical/learned/ (untouched; its Phase-17 re-grounding is out of scope)
- meetings/manager.py + meetings/transcript.py (no mechanism change at the close — graduation touches resolvers/registry only)

**Definition of done:**
- [ ] The graduation slate is recorded in the close audit BEFORE the record (each lever's ruling + its counterfactual citation + the owner sign-off via PR merge). Stay-OFF is coherent in-scope ONLY for the template-free levers (J1, absence); a stay-OFF ruling on the citation gate or id-rendering AFTER 16.15's asks landed PAUSES the close. **PAUSE-path DoD** (replaces every bullet below except the CI tail): the slate audit section is committed with the pause ruling and its counterfactual evidence, the banner flips to PAUSED naming the re-plan owner-side, NO record is performed, and the surface-retreat successor contract is named — the remaining bullets bind ONLY on the proceed path.
- [ ] [proceed path] The recorded substrate matches the slate exactly (stamped flags = graduated set).
- [ ] Both sets recorded atomically at the final substrate (locked model, 16.15/16.16 versions, slate graduated), Q5 tags, MANIFEST provenance exact; validity gate PASSES with `--expected-model`; BARE byte-verification clean (no `AILIBI_*` export — C6 discharged by graduation).
- [ ] The before/after table regenerates end-to-end from committed artifacts (the BEFORE measure file + the new bytes via the committed CLIs); the named pairing is explicit: voice metrics and zero-flag conviction rate in one table, with the persona-attribution question answered (a zero-flag rise with voice-metric movement and no judgment-lever change = the phase NO-GO, paused for the owner).
- [ ] Canaries on the 50-seed sets per the degraded-Q3 rule (pre-registered bands, two-proportion tests, UNDERPOWERED recorded honestly); a regression pauses the close.
- [ ] Baseline-5 floors pinned; the population-relative conversion floor reported for the new population with its derivation quoted.
- [ ] The close audit records uptake per elicitation ask (roll-call answer rate, citation compliance, vent-tail movement, self-accusation recurrence — findings scoping Phase 17/18), re-states the staleness rule, and flips the banner.
- [ ] The byte-coupled re-pin sweep lands in this PR; `bash scripts/check.sh` green on the final tree.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

Sequence the PR like 15.7: slate + graduation commits first (offline-provable), the record next,
the re-pins last. The slate's owner sign-off rides the PR merge (the 15.18 convention) but the
AUDIT text with the rulings must be in the tree before the recording session starts — the operator
records what the slate says, nothing else. Budget ~4–5h; the uptake numbers land wherever they
land (record-only discipline — a weak roll-call answer rate scopes Phase-17/18 prompt work, it
does not reopen 16.15 inside this task).

**Integration risk:**

This record graduates up to FOUR levers plus two prompt bumps in one substrate — the largest
single-record behavioral delta since 14.12. That is the deliberate design (the offline
counterfactuals + the golden are the proof the risk is priced), but the close audit must
attribute honestly: the before/after table reports against baseline 4 (model held constant, GO
path) so the V&J delta is clean; under NO-GO it reports against baseline 3 with the model
unchanged — either way ONE layer moved per record and the attribution chain from baseline 3 to 5
is unbroken. The one unhedged risk is elicitation uptake at scale (the A/B and fixtures de-risk
mechanism, not model behavior) — hence findings-not-failures, and Phase 17 trains against
whatever this close measures.

**Ready-to-paste prompt:** `agent_prompts/task-16-17-baseline-5-close.md`
