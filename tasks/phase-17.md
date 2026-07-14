# Phase 17 — Co-adaptation: re-ground, re-run, re-select on baseline 5

STATUS: OPEN (authored 2026-07-14) — ABSENCE GATE: STAY-OFF (owner, 2026-07-14,
`audits/audit-phase-17-absence-gate.md` §7; sign-off rides the 17.7 PR merge — the 15.18
convention). The 17.7 gate is decided: `absence_prior` STAYS OFF (the ratified bar —
new-over-gate ≤ 0.20 at crew roll-call coverage ≥ 0.60 — fails both clauses at 53/179 = 0.296
and 0.4624), the PR #264 vent widening HOLDS (the flag stays inert; both travel to Phase 18 as
one package under the ratified routing note), and the corpus re-record (17.9) is unblocked at
the baseline-5 meeting layer. The GO-only adopting-record task was REMOVED by the gate's
surgery (the 16.2 discipline); its drop record sits in Wave 1. Baseline 5 is canonical
(`Qwen/Qwen3.6-27B`, `qwen3_6_27b` v3, nine always-on levers, `absence_prior` the sole
live toggle — `audits/audit-phase-16-close.md`). Phase 17 is the roadmap's co-adaptation phase
(`tasks/post-phase-14-plan.md` owner goal 3): everything trained or selected before the
Phase-16 close is PRIOR-SUBSTRATE-ANCHORED (the close §8 staleness rule), so this phase
re-grounds the calibration corpus and the ballot surrogate on baseline-5 meetings, re-runs
the Phase-15 training recipe (full entrant slate), and re-selects champions through the
same gates with the 16.11 population-relative referee as the selection bar.

## Locked decisions (owner-ratified 2026-07-14)

1. **Full slate re-run.** All four impostor methods (`bc-dagger`, `utility-es`,
   `policy-es`, `map-elites`) and both crew bases re-enter the bake-off. Baseline 5
   changed the meeting economy (convictions demand citations; impostor win rate rose
   0.24 → 0.36) enough that the Phase-15 ranking could flip; the harness exists so
   re-runs are cheap. Torch stays retired experiment-tier (pause decision 3 binding);
   the crew side re-runs MEASUREMENT-ONLY — no crew deployment surface ships this phase
   (the learned factory is impostor-only, `agents/tactical/learned/factory.py:145`; a
   crew opt-in surface is Phase-18 heterogeneous-lobby territory).
2. **Evidence-gated default-ON.** If the re-selected champion PASSES the baseline-5
   referee (supply floors + population-relative conversion + geomean) AND retains its
   win edge at the real-LLM finalist eval, it becomes the DEFAULT mover and the phase
   closes on a mover-layer baseline record. FAIL on either ⇒ it stays opt-in (the
   15.20/15.21 posture), the close records the finding, and NO mover baseline is
   recorded (the ladder tip stays where the meeting layer left it).
3. **Absence prior: early evidence + owner gate, BEFORE the corpus record.** Standing
   rule 2 (nothing trains against a layer scheduled to change) forces the sequencing:
   the gate (17.7) rules on graduation + the PR #264 vent-placement widening BEFORE the
   ~14h corpus re-record, so the corpus is recorded at the FINAL meeting layer either
   way. Wave 0 builds the missing evidence first (per-role roll-call uptake, the
   widening counterfactual). Stay-OFF ⇒ graduation routes to Phase 18 with the
   pooling-prompt work that raises the 0.363 answer rate.
4. **Surrogate: re-fit + re-verdict on the recorded bar.** Rebuild on the baseline-5
   corpus, re-measure the owner-ratified three-axis GO/NO-GO honestly, keep the
   6-feature live-parity fence (`training/surrogate/ballots.py:103-110` —
   `BALLOT_FEATURE_NAMES` stays; baseline-5 channels a training-time meeting runner
   cannot reconstruct stay out). Promotion happens only if the bar passes; a repeat
   NO-GO stays diagnostic-only and NEVER blocks the bake-off — the referee selects
   champions, the surrogate verdict governs only its own usage tier (the two gates are
   independent by construction).

## Designer rulings (recorded here so contracts inherit them)

- **Genuine-class instrument re-anchors EVAL-SIDE** (17.6): the instrument reads NO-DATA
  on two consecutive substrates because the alibi-lie supply collapsed and single-tick
  roll-call placements are endpoint-banded out of the genuine class. Phase 17 re-anchors
  the canary on channels this substrate actually supplies (vents, sightings,
  whereabouts-lies) and keeps the old alibi-class cell as a reported column. The
  alternative — relaxing the detector's endpoint band so roll-call lies mint interior
  flags — is a RECORD-TIME substrate change (one-layer-per-baseline) and is routed to
  the absence gate's record (GO path) or Phase 18, never done inside an instrument task
  (the gate ruled STAY-OFF, so: Phase 18).
- **Coerced SKIPs are a by-design bucket, not inversions** (17.2): the conversion
  report's SKIP partition learns `UNCITED_ZERO_FLAG_EJECT_MARKER` as a new by-design
  sub-bucket (the invalid-target/teammate precedent) — never a missed skip, never a
  threshold inversion; the partition invariant extends to cover it.
- **Coerced SKIPs are excluded from the surrogate fit** (17.10): a J2-coerced ballot
  records `target="SKIP"` but was a forced eject, not a chosen skip — poison for the
  decision channel the verdict hinges on. Fit-side rows carrying the marker are dropped
  and COUNTED (reported in the surrogate report); the fidelity replay still scores them
  as recorded bytes.
- **The corpus keeps its shape**: same 150-game 9p2i + 50-game 4p1i scale, seeds 1000+,
  the same `seed % 5` split rule, so `CORPUS_SPLITS_PATH` stays structurally identical.
  Duration honesty: baseline-5 meetings are ~2× heavier — the operator plan says
  **~14–15h**, not the stale ~7h. The mid-Phase-15 Q3 ruling (corpus as the canonical
  canary denominator, samples as continuity anchor) — DEGRADED through Phase 16 — is
  RESTORED by the re-record (17.9 re-states it; future closes re-adopt it).
- **The vent-placement widening is grounded-only and scope-firewalled** (17.5): only a
  vent sighting matched against the speaker's own `VentWitnessRecord` (the 15.4
  grounding chokepoint) can place its subject, and the widening feeds ONLY the
  absent-set derivation behind an `include_vent_sightings` flag — stated-path
  contradiction detection reads exactly what it read before (byte-preserving). Feeding
  vent placements into the physical-contradiction detector is a flag-minting substrate
  move, routed with the detector-band option above. Whether the widening SHIPS was the
  17.7 gate's ruling (the close routes the two decisions together) — ruled HOLD (owner,
  2026-07-14, the gate audit's Ruling 2).
- **The staleness cap re-derives** (17.10): `max-uses.json` was ~143× the 349
  baseline-3 fit-side meetings; the re-fit re-derives the cap from the baseline-5
  fit-side count under the same rule, not held at 50000 by habit.
- **Selection-bar honesty** (17.12/17.17): a co-adapted impostor's objective is to make
  convictions harder — the exact direction the baseline-5 conversion floor (0.474,
  population-relative, capped by the flags supply floor) prices. The floor STAYS the
  bar (owner charter), but the bake-off report and the close audit must show floor
  sensitivity beside the verdict (how close each finalist sits to each floor), so a
  starved-economy rejection is visible as the instrument working, never silent.

## The DAG

```
Wave 0 (all roots, dispatch in parallel):
  17.1 (VJ gauge clamp-exemption)      17.2 (conversion-report coerced-SKIP bucket)
  17.3 (spectator marker chips)        17.4 (roll-call uptake breakdown)
  17.5 (vent-placement widening + counterfactual)
  17.6 (genuine-class re-anchor)

Wave 1 (the gate):
  (17.4, 17.5) -> 17.7 THE ABSENCE GATE [OWNER] (RULED: STAY-OFF, 2026-07-14)

Wave 2 (re-grounding, the critical path):
  (17.2, 17.7) -> 17.9 corpus re-record [OPERATOR ~14-15h]
  17.9 -> 17.10 surrogate re-ground + re-verdict
  17.9 -> 17.11 selection-bar re-pins

Wave 3 (training):
  (17.10, 17.11) -> 17.12 impostor bake-off re-run [OPERATOR compute]
  (17.10, 17.11) -> 17.13 crew track re-run
  (17.10, 17.11) -> 17.15 Goodhart re-probe
  17.12 -> 17.14 multi-finalist recorder + real-LLM finalist eval [OPERATOR]

Wave 4 (adoption + close):
  17.14 -> 17.16 champion productization + the evidence-gated default flip
  (17.1, 17.3, 17.6, 17.13, 17.15, 17.16) -> 17.17 mover baseline record + phase close [OPERATOR + OWNER]
```

Critical path: 17.5 → 17.7 → 17.9 → 17.10 → 17.12 → 17.14 → 17.16 → 17.17. Wave 0 is
six independent roots; nothing outside the gate chain waits on the owner.

**Baseline numbering.** Contracts below are written on the gate's STAY-OFF path — and
the gate RULED STAY-OFF (owner, 2026-07-14, `audits/audit-phase-17-absence-gate.md` §7),
so this numbering is final: the mover record at 17.17 is **baseline 6**, its BEFORE
column is `baseline5-final-measure.json`, and the corpus (17.9) records at the
baseline-5 meeting layer. The GO-only surgery this block formerly enumerated (an
adopting-record task kept between the gate and the corpus, its edge inserted into 17.9's
`Depends on:` line, a 6 → 7 mover renumber across 17.11/17.12/17.17, and a
BEFORE-column rename) was NOT performed — the rejected path's rationale is §6–§7 of the
gate audit (the 16.2 GO-banner convention, inverted). The STAY-OFF surgery WAS performed
by the 17.7 PR: the adopting-record contract and its prompt are removed with a drop
record in Wave 1, and the GO-conditional clauses in 17.9/17.10/17.11/17.16 are
scrubbed — dependencies and scopes otherwise untouched, validator-green.

**Collision discipline.** `training/bakeoff/harness.py` is touched by 17.11 (constants)
then 17.12 (protocol run) — serialized by the dep edge. `tests/agents/test_absence_prior.py`
and `meetings/transcript.py` are single-toucher 17.5 (the STAY-OFF ruling removed the
adopting record's GO re-pins and the widening's always-on flip). `eval/funnel.py`
single-toucher 17.4; `eval/meeting_quality.py` 17.2; `eval/vj_instruments.py` 17.1;
`eval/vote_correctness.py` 17.6; `api/` + frontend 17.3 — Wave 0 is pairwise disjoint.
`agents/tactical/learned/` is touched only by 17.16. `meetings/manager.py` is untouched
this phase (the widening HOLDS). `eval/watchability.py`: 17.11 touches ONLY the :794-798
lag note; the floor BLOCKS are touched only by 17.17.

**Operator/owner gates.** Operator sessions: 17.9 (~14–15h — the
long pole; plan it like the 15.12 session, with the 16.14/16.17 concurrency notes:
staggered workers, jittered backoff, `AILIBI_SEED_MAX_ATTEMPTS=8`), 17.12 (compute),
17.14 (real-LLM eval), 17.17 (~5h). Owner gates: **17.7** (the absence ruling + the
vent-widening ruling — RULED: STAY-OFF + HOLD, 2026-07-14) and **17.16/17.17** (the
default-flip evidence reading + the close).

---

## Wave 0 — instrument repairs + gate evidence (six roots)

### Task 17.1 — The VJ provenance gauge learns the J1 clamp-exemption
**Branch:** `phase-17-vj-gauge-clamp-exemption`
**Depends on:** none (root)
**Section refs:** audits/audit-phase-16-close.md §8 (routed contract (a)) + §2 (the five by-design clamped rows); eval/vj_instruments.py `_cross_check_graphs` (the gauge with no J1 exemption); tests/eval/test_vj_instruments.py:375 (the live-pinned wrong cell: `provenance_sum_breaches == 5`); agents/memory/beliefs.py (the graduated J1 clamp semantics the gauge must mirror)
**Complexity:** Small

The close found the defect and routed it here: `_cross_check_graphs` asserts
`0.5 + Σ(eight channels) == rendered suspicion`, but the graduated J1 gate CLAMPS the
rendered value for soft-only rows — so five by-design clamped rows on the baseline-5
9p2i bytes report as phantom `provenance_sum_breaches`. Teach the gauge the exemption:
a row whose typed decomposition is soft-only under the J1 predicate (the 16.4
classification, `SUSPICION_PROVENANCE_ATOL` tolerance) checks the clamp arithmetic
instead of the raw sum. The gauge must still catch REAL breaches — a fixture with a
genuinely broken sum on a clamped row must fail.

**Files in scope:**
- eval/vj_instruments.py (`_cross_check_graphs` — the exemption predicate)
- tests/eval/test_vj_instruments.py (the ==5 pin becomes ==0 with the exemption asserted per-row; a synthetic true-breach fixture)

**Files NOT in scope:**
- agents/memory/beliefs.py (the clamp is production truth; the gauge mirrors, never moves)
- eval/meeting_quality.py (17.2's region)

**Definition of done:**
- [ ] On committed baseline-5 bytes the gauge reports 0 provenance-sum breaches, with the five previously-phantom rows individually asserted as J1-clamp-exempt (their identities pinned); a synthetic genuinely-broken clamped row still counts as a breach.
- [ ] The exemption predicate is the 16.4 soft-only classification verbatim (shared or byte-equivalent logic, tolerance `SUSPICION_PROVENANCE_ATOL`) — never a looser re-derivation.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Ready-to-paste prompt:** `agent_prompts/task-17-1-vj-gauge-clamp-exemption.md`

### Task 17.2 — The conversion report learns the coerced SKIP (a by-design bucket)
**Branch:** `phase-17-conversion-coerced-skip`
**Depends on:** none (root)
**Section refs:** audits/audit-phase-16-close.md §8 (routed contract (b): 2 of 99 inversions on the baseline-5 samples are J2-coerced SKIPs); eval/meeting_quality.py `compute_conversion_report` (the SKIP partition + its invariant); meetings/manager.py `UNCITED_ZERO_FLAG_EJECT_MARKER` (the literal + the `{x!r}` marker shape); the invalid-target/teammate by-design-bucket precedent in the same report
**Complexity:** Medium

A J2-coerced ballot records `target="SKIP"` with the coercion marker prefixed to
`rationale_text`; the report's partition predates the marker and mis-files those
ballots as §4.6 threshold inversions. Add a by-design sub-bucket: a SKIP carrying
`UNCITED_ZERO_FLAG_EJECT_MARKER` is neither a missed skip nor an inversion — it is the
gate working. The partition invariant (every ballot lands in exactly one bucket)
extends to cover the new bucket; the report surfaces its count. This must land BEFORE
the corpus re-record (17.9's dep): every conversion read over baseline-5-era bytes is
over-counting inversions until it does.

**Files in scope:**
- eval/meeting_quality.py (the SKIP partition + invariant + report field)
- tests/eval/test_meeting_quality.py (the 2/99 committed-bytes pin moves to the new bucket; partition-invariant fixtures; a marker-stacked ballot fixture — coercion atop a 16.5 nulled-citation marker)

**Files NOT in scope:**
- meetings/manager.py (the marker literal is production truth — imported, never re-spelled)
- eval/vj_instruments.py (17.1's region)

**Definition of done:**
- [ ] On committed baseline-5 9p2i bytes the report shows the two previously-mis-filed ballots in the coerced-SKIP bucket, threshold inversions drop accordingly, and the partition invariant holds over every committed meeting (asserted).
- [ ] Marker detection uses the imported literal via the established `{x!r}` marker-parsing convention (the `api.replay_loader._marker_pattern` shape) — stacked markers (16.5 null + 16.6 coercion) parse correctly, fixture-pinned.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

Follow the report's existing by-design buckets (invalid-target, teammate) for naming and
invariant wiring. The marker rides `rationale_text` as a PREFIX — strip-and-classify
before any prose-level reads, and remember 16.6's stacking order (gate prefix outside
the redirect marker).

**Ready-to-paste prompt:** `agent_prompts/task-17-2-conversion-coerced-skip.md`

### Task 17.3 — Spectator chips for the coercion + nulled-observation markers
**Branch:** `phase-17-spectator-marker-chips`
**Depends on:** none (root)
**Section refs:** audits/audit-phase-16-close.md §8 (routed contract (c)); api/replay_loader.py:2425 `_BALLOT_PREFIX_MARKERS` (the registration table + `_marker_pattern`); meetings/manager.py `UNCITED_ZERO_FLAG_EJECT_MARKER` + `INVALID_OBSERVATION_ID_MARKER` (the two unregistered audit rewrites, both live on committed bytes); tasks/phase-15.md 15.4.1 (the mirror precedent)
**Complexity:** Medium

Two ballot audit-trail rewrites now fire on committed bytes but are invisible in the
spectator's `BallotView.rewrite_reasons` chips: the 16.6 coercion marker and the 16.5
nulled-observation marker. Register both in `_BALLOT_PREFIX_MARKERS` with chip labels
following the table's existing label style, regenerate the frontend types if the label
union is typed, and render them through the existing chip surface. Committed sets serve
byte-identically (view-layer only).

**Files in scope:**
- api/replay_loader.py (`_BALLOT_PREFIX_MARKERS` — two rows; markers imported from meetings.manager)
- frontend/src/ (chip label handling if labels are enumerated; regenerated types)
- tests/api/ (chip extraction fixtures for both markers, incl. stacked)

**Files NOT in scope:**
- meetings/ (marker literals are production truth)
- replays/samples/ (served bytes unchanged — pinned)

**Definition of done:**
- [ ] A committed baseline-5 ballot carrying each marker serves with the corresponding chip in `rewrite_reasons` (the two live cases found on the committed sets are the fixtures); stacked markers yield both chips in stack order.
- [ ] Both committed sets load, serve, and byte-verify unchanged; frontend type generation clean (`tsc` green via check.sh).
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

Clone the existing marker rows — `_marker_pattern` already handles the `{x!r}` repr
interpolation. Chip label text follows the table's register (short snake_case labels);
if the frontend enumerates labels, extend the enum rather than widening to bare string.

**Ready-to-paste prompt:** `agent_prompts/task-17-3-spectator-marker-chips.md`

### Task 17.4 — Roll-call uptake breakdown (who is not answering)
**Branch:** `phase-17-rollcall-uptake-breakdown`
**Depends on:** none (root)
**Section refs:** audits/audit-phase-16-close.md §6 (roll-call coverage 0.363 — the aggregate the gate cannot rule on) + §0.1.4 (the calibration question the breakdown answers); eval/funnel.py (the 16.10 pooling-folds region — `_roll_call_placed` and the whereabouts census); meetings/schemas.py `WhereaboutsClaim`
**Complexity:** Small

The absence gate needs to know whether the 0.363 coverage is uniform silence or
structured refusal: extend the pooling folds with a per-role (crew vs impostor) and
per-surface (opening vs reply vs info-share) whereabouts-uptake breakdown, plus a
per-meeting answered/asked census. Additive fields on the existing pooling report —
no fold semantics change; committed-bytes cells pinned. This is 17.7's evidence, so it
reads the committed baseline-5 sets as-is.

**Files in scope:**
- eval/funnel.py (additive breakdown fields in the pooling-folds region)
- tests/eval/test_funnel_pooling.py (committed-bytes pins + a synthetic role-split fixture)

**Files NOT in scope:**
- eval/vj_instruments.py + eval/meeting_quality.py (17.1/17.2's regions)
- meetings/ (measurement only)

**Definition of done:**
- [ ] The pooling report carries whereabouts uptake split by speaker role and by template surface, with the committed baseline-5 cells pinned (the aggregate must still reproduce 0.363 on 9p2i — the new cells decompose it, never move it).
- [ ] A synthetic fixture proves the role attribution (an impostor's whereabouts claim counts under impostor, never crew).
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Ready-to-paste prompt:** `agent_prompts/task-17-4-rollcall-uptake-breakdown.md`

### Task 17.5 — Vent-placement widening: the mechanism (inert) + the double-count counterfactual
**Branch:** `phase-17-vent-placement-widening`
**Depends on:** none (root)
**Section refs:** audits/audit-phase-16-close.md §0.1.4 + §8 (the PR #264 question, routed WITH the absence decision); meetings/transcript.py:1205 `absent_players` + `reconstruct_stated_paths` (the placement substrate — `saw_player` observations only, by contract); the 15.4 vent-grounding chokepoint (grounded vent sightings — the only class that may place); tests/agents/test_absence_prior.py `TestAbsencePriorOnCommittedBytes` (the counterfactual harness the new column extends)
**Complexity:** Medium

Build what the gate needs and nothing the substrate would feel: (1) an
`include_vent_sightings` flag on the absent-set derivation — a GROUNDED vent sighting
(matched against the speaker's own `VentWitnessRecord`, the 15.4 chokepoint; spoken but
ungrounded claims never place) removes its subject from the absent set; the flag
defaults OFF and NOTHING in production passes it, so every committed byte and every
stated-path contradiction read is untouched. (2) The double-count counterfactual on
committed baseline-5 bytes: how many meetings hold a vent-sighted subject who is ALSO
absent (the population the widening would re-place), and the absent-set size / new-over-
gate / top-churn deltas with the widening hypothetically applied — the missing evidence
row the 17.7 gate reads beside 17.4's uptake breakdown.

**Files in scope:**
- meetings/transcript.py (the `include_vent_sightings` parameter on the absent-set derivation — the stated-paths reconstruction itself is untouched)
- tests/meetings/test_absent_set.py (flag semantics: grounded places, ungrounded never; default-OFF byte-identity)
- tests/agents/test_absence_prior.py (the counterfactual extension — the widened column beside the existing pinned walk)

**Files NOT in scope:**
- meetings/manager.py + agents/memory/beliefs.py (no live consumer passes the flag — the gate rules first)
- `_detect_alibi_vs_physical` and every contradiction detector (byte-preserving by contract — the flag-minting variant is routed, never done here)

**Definition of done:**
- [ ] Flag OFF (the default and the only production state) is byte-identical everywhere: no call site passes it, committed reconstruction and golden stay green, and the absent-set derivation's existing pins are unmoved.
- [ ] Flag ON semantics fixture-pinned: a grounded vent sighting places its subject (removed from the absent set); an ungrounded spoken vent claim places nobody; a grounded sighting of an already-placed subject changes nothing.
- [ ] The double-count counterfactual on committed baseline-5 9p2i bytes is pinned: the vent-sighted∩absent population per meeting, and the widened-column deltas (absent-set sizes, new-over-gate count, top-churn count) beside the existing counterfactual's cells — the gate's evidence row, quoted in the PR description.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

The grounding predicate exists — reuse the 15.4/16.7 chokepoint logic (the vent accessor
+ witness-record match), never a fresh text parse. Keep the flag on the DERIVATION
(`absent_players` or its input assembly), not on `reconstruct_stated_paths` itself: the
stated-paths surface is the alibi-contradiction substrate and must not learn vents.

**Ready-to-paste prompt:** `agent_prompts/task-17-5-vent-placement-widening.md`

### Task 17.6 — The genuine-class instrument re-anchors on supplied channels
**Branch:** `phase-17-genuine-class-reanchor`
**Depends on:** none (root)
**Section refs:** audits/audit-phase-16-close.md §8 (the NO-DATA routing: re-anchor "on channels this substrate actually supplies (vents, sightings, whereabouts-lies)") + §6 (the second consecutive 0/0); eval/vote_correctness.py (the genuine-class definition + `genuine_class_subjects`'s endpoint-band exclusion); audits/audit-phase-16-baseline-4.md §6 (the supply collapse anatomy: alibi flags 190 → 7)
**Complexity:** Medium

The Phase-10 primary-progress instrument (genuine-class conversion: did the crew convert
a genuinely-contradicted subject into an ejection?) reads 0/0 on baselines 4 and 5 —
the bespoke model stopped volunteering checkable alibi lies, and roll-call placements are
endpoint-banded out of the class. Re-anchor: define the successor instrument over the
evidence classes this substrate supplies — witnessed vents, sighting contradictions, and
whereabouts-lies (the recorded contradiction event ids from 16.10's fold) — measuring
the same question (supplied hard evidence against a subject → conviction?). The old
alibi-anchored cell stays as a reported column (labeled starved, never a canary); the
successor becomes the canary-eligible cell. Definitions, denominators, and the
committed-bytes cells are pinned so 17.17's close (and any future canary bands) read
one unambiguous instrument.

**Files in scope:**
- eval/vote_correctness.py (the successor instrument beside the legacy cell)
- tests/eval/test_vote_correctness.py (committed-bytes pins for both cells; synthetic fixtures per supplied channel)

**Files NOT in scope:**
- meetings/transcript.py (detector semantics untouched — the endpoint-band relaxation is routed, never done here)
- eval/funnel.py (17.4's region)

**Definition of done:**
- [ ] The successor instrument is defined and pinned on committed baseline-5 bytes with a NON-ZERO denominator (the substrate supplies vents/sightings/whereabouts-lies — quoted in the PR), and the legacy alibi-anchored cell is preserved as a labeled reported column reading 0/0.
- [ ] Per-channel synthetic fixtures prove the numerator/denominator semantics (a witnessed-vent subject ejected counts; the same subject skipped counts the denominator only; an unsupplied channel contributes nothing).
- [ ] The instrument's docstring records the re-anchor decision and its provenance (the close §8 routing) so a future substrate that re-supplies alibi lies can re-examine the legacy cell.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

Reuse 16.10's recorded-contradiction-id reads (never re-derive detection) and the
existing conviction census join. The design risk is denominator inflation — a vent
witnessed by the eventual voter is a different evidential position than one spoken
second-hand; split the denominator by witness-vs-testimony if the committed bytes make
the distinction measurable, and say so in the report either way.

**Ready-to-paste prompt:** `agent_prompts/task-17-6-genuine-class-reanchor.md`

## Wave 1 — the absence gate

### Task 17.7 — THE ABSENCE GATE: graduation + vent-widening ruling (owner) + phase-doc surgery
**Branch:** `phase-17-absence-gate`
**Depends on:** 17.4, 17.5
**Section refs:** audits/audit-phase-16-close.md §0.1.4 (the stay-OFF ruling this gate re-opens, its evidence bar, and the coupled PR #264 question); tests/agents/test_absence_prior.py (the baseline-5 counterfactual: 53/179 new-over-gate, 114/179 top-churn + 17.5's widened column); eval/funnel.py (17.4's uptake breakdown); tasks/phase-15.md 15.18 + tasks/phase-16.md 16.2 (the gate-with-surgery precedents)
**Complexity:** Medium

The phase's first owner gate, sequenced BEFORE the corpus record by locked decision 3.
Assemble the decision memo in `audits/audit-phase-17-absence-gate.md`: the baseline-5
counterfactual (already pinned), 17.4's who-is-not-answering breakdown, 17.5's
double-count counterfactual with the widened deltas, and a stated graduation bar the
owner ratifies or amends (the close never defined one — this memo must propose a
numeric bar, e.g. a new-over-gate ceiling at a stated roll-call coverage, so the ruling
is a criterion, not a vibe). The owner rules THREE couplings together: graduate/stay-OFF,
ship/hold the vent widening (a widening that ships travels WITH the graduation record —
it is meeting-layer), and (if stay-OFF) the Phase-18 routing note. Then the surgery,
exactly as the preamble's Baseline-numbering block enumerates: GO ⇒ 17.8 stays, 17.8
enters 17.9's `Depends on:` line (the parsed edge that makes the corpus wait), the
mover baseline renumbers 6 → 7 across 17.11/17.12/17.17, 17.17's before-column artifact
renames to `baseline6-final-measure.json`, and this doc's banner records the ruling;
STAY-OFF ⇒ 17.8's contract + prompt are REMOVED with the reason recorded (the 16.2
surgery discipline) and the GO-conditional 17.8 clauses in 17.9's DoD and 17.11's body
are scrubbed — dependencies and scopes otherwise untouched. Prompts regenerate;
validator green either way.

**Files in scope:**
- audits/audit-phase-17-absence-gate.md (new: the memo + the recorded ruling)
- tasks/phase-17.md (the surgery + the banner note)
- agent_prompts/ (regenerated)

**Files NOT in scope:**
- agents/memory/beliefs.py + orchestrator/replay.py (graduation mechanics are 17.8's, GO only)
- replays/samples/ (no record at the gate)

**Definition of done:**
- [ ] The memo quotes every evidence row (counterfactual, uptake breakdown, widening deltas) with its committed source, proposes the numeric bar, and records the owner's three rulings verbatim (graduate/stay-OFF; widening ship/hold; routing).
- [ ] The surgery is complete in the ruled direction: validator green, prompts regenerated, `scripts/compute_next_task.py --phase 17` consistent with the surviving DAG; under STAY-OFF no orphan reference to 17.8 survives anywhere in tasks/ or agent_prompts/.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

Write the memo BEFORE asking for the ruling (the 15.18 pause shape: evidence first,
decision slots explicit). The bar proposal should price both directions honestly — the
lever's designed value (pricing refusal-to-account) against the quiet-crewmate cost at
the measured uptake, and what the widening buys (17.5's delta) toward shrinking the
absent set.

**Ready-to-paste prompt:** `agent_prompts/task-17-7-absence-gate.md`

**Dropped — Task 17.8, the [GATE-GO ONLY] absence adopting record.** Removed by the
17.7 STAY-OFF ruling (owner, 2026-07-14, `audits/audit-phase-17-absence-gate.md` §7–§8),
per the 16.2 surgery discipline: removal, not labeling — `scripts/compute_next_task.py`
computes dispatchability from `### Task` headers and has no dropped state, so a
surviving header would surface forever as dispatchable. The task would have graduated
`absence_prior` at its own meeting-layer baseline (the 16.17 runbook) and optionally
shipped the vent widening with it; the gate audit's ratified bar failed both clauses
(new-over-gate 53/179 = 0.296 > 0.20; crew roll-call coverage 0.4624 < 0.60), so NO
adopting record exists this phase and the corpus records at the baseline-5 meeting
layer. Its generated prompt is deleted; graduation re-enters at Phase 18 through the
audit's Ruling-3 routing note and must pass the same bar there. The lever and widening
MECHANISMS stay in the tree, tested and inert (`agents/memory/beliefs.py`'s
`absence_prior` resolver; `meetings/transcript.py`'s `include_vent_sightings` flag) —
the surgery removed a contract, never code.

## Wave 2 — re-grounding (the critical path)

### Task 17.9 — The corpus re-record at the final meeting layer (operator, ~14–15h, $0)
**Branch:** `phase-17-corpus-rerecord`
**Depends on:** 17.2, 17.7
**Section refs:** scripts/record_ml_corpus.sh (the pin block — already baseline-5-coupled: model + set + v3, moved by 16.17; its freeze-path guards refuse stale bytes); replays/ml_corpus/README.md (baseline-3 prose — stale against the script, refreshed here); tasks/phase-15.md 15.12 (the operator-session precedent); audits/audit-phase-16-close.md §0.5 (concurrency notes) + §8 (the staleness rule this task discharges)
**Complexity:** Integration

The long pole. Re-record `replays/ml_corpus/` (150-game 9p2i + the 4p1i set, seeds
1000+, same `seed % 5` split rule) at the FINAL Phase-17 meeting layer — the gate has
ruled, so this substrate is what movers train against, by construction. Duration
honesty: baseline-5 meetings run ~2× baseline-3; plan **~14–15h** with the 16.14/16.17
operator notes (staggered starts, jittered backoff, `AILIBI_SEED_MAX_ATTEMPTS=8`,
per-seed atomic staging). The recorder's guards enforce the substrate; add the one
missing positive gate if absent (assert the graduated-lever slate in recorded bytes,
not just the env refusal). Refresh the corpus README end-to-end (substrate, env, the
duration figure, `--expected-model`), regenerate `splits.json`, and RE-STATE the Q3
canary-denominator restoration: the corpus is again the canonical canary denominator,
samples the continuity anchor (the mid-Phase-15 ruling, DEGRADED through Phase 16,
operative again from this record).

**Files in scope:**
- replays/ml_corpus/9p2i/ + replays/ml_corpus/4p1i/ (the re-recorded bytes + MANIFESTs + splits.json)
- replays/ml_corpus/README.md (full substrate refresh)
- scripts/record_ml_corpus.sh (the duration note + the positive graduated-slate assertion if missing — never the pin block, which is already correct)
- tests/scripts/test_record_ml_corpus.py (the new assertion's fixtures)
- tests/training/ (corpus-derived number re-pins ONLY — the pinned cells this record moves; the constant flips stay 17.11's and the protocol re-pins 17.12's)

**Files NOT in scope:**
- replays/samples/ (the measurement sets — pinned)
- training/ (17.10 consumes; this task records)

**Definition of done:**
- [ ] Both corpus sets recorded at the final meeting layer and PASS the validity gate (`--expected-model Qwen/Qwen3.6-27B --require-zero-cost`); byte-identical reconstruction; MANIFEST provenance exact (model, v3 versions, flags, git_sha, $0); splits.json regenerated under the same rule with the eval/train/val partition non-degenerate.
- [ ] The recorder asserts the graduated-lever slate POSITIVELY in recorded bytes (the `substrate_flag_snapshot` stamp checked, not just env refusal), fixture-pinned.
- [ ] The corpus README agrees with the script on every operative line (model, set, versions, env, duration), and the Q3 restoration is stated in both the README and the PR.
- [ ] The conversion report (17.2's partition) over the new corpus is quoted in the PR — the coerced-SKIP bucket populated, inversions honest.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

The recorder is already correct — resist editing its pin block. The session plan is the
15.12 runbook with doubled wall-clock: record 4p1i first (short, validates the pipeline
end-to-end), then the 9p2i long leg. Commit atomically only after both validity gates
pass; the freeze-path staging keeps partial runs off the tree.

**Integration risk:**

A ~14–15h operator session spanning UTC midnight — the 16.14 mixed-date MANIFEST
precedent applies (dates are honest, the gate checks coherence not uniformity).
Training tests that pin corpus-derived numbers (tests/training/test_bakeoff_harness.py,
test_surrogate_runner.py, test_crew_options.py, test_goodhart_probe.py) will move —
re-pin ONLY what this record moves, in this PR, so the suite is green at merge (the
17.11 constants stay 17.11's).

**Ready-to-paste prompt:** `agent_prompts/task-17-9-corpus-rerecord.md`

### Task 17.10 — Surrogate re-ground + re-verdict on the recorded bar
**Branch:** `phase-17-surrogate-reground`
**Depends on:** 17.9
**Section refs:** training/surrogate/ballots.py (the fit pipeline + `BALLOT_FEATURE_NAMES` — the 6-feature live-parity fence, kept by locked decision 4); training/surrogate/dataset.py (the reconstruction walk + the hand-mirrored belief pins); training/reports/report-ballot-surrogate.md (the baseline-3 report this regenerates end-to-end, incl. the three-axis bar + the always-eject anchor); training/artifacts/surrogate/ (the artifact bundle + max-uses.json)
**Complexity:** Integration

Rebuild the meeting table on the new corpus, re-fit the predictor, re-measure the
owner-ratified three-axis GO/NO-GO, re-commit the artifact bundle (weights + sha
sidecar + a max-uses cap RE-DERIVED from the recorded corpus's fit-side meeting count under
the ~143× rule — baseline 5), and regenerate the report end-to-end — every baseline-3 anchor
(honest ceiling, FO-6 re-baseline, always-eject constant 0.802) re-measured, never
copied. Three baseline-5-specific validations are load-bearing: (1) coerced-SKIP rows
are EXCLUDED from the fit and counted in the report (designer ruling — forced ejects
are not skip labels); (2) live-parity under graduated J1: the dataset's raw
`belief_suspicion` column vs the clamped rendered value the live runner would serve —
measure the divergence and state which side the fit uses and why; (3) the dataset walk
re-validates on corpus bytes that now carry whereabouts turns, observation-cited
ballots, and marker-prefixed rationales. A repeat NO-GO is a finding: the surrogate
stays diagnostic-only, its usage tier unchanged, and NOTHING downstream re-plans (the
bake-off consumes it as a training-time runner either way).

**Files in scope:**
- training/surrogate/dataset.py (baseline-5 re-validation + the coerced-row filter)
- training/surrogate/ballots.py (fit-side filter wiring; feature set UNCHANGED)
- training/artifacts/surrogate/ (ballot-predictor.json + .sha256 + max-uses.json)
- training/reports/report-ballot-surrogate.md (regenerated)
- tests/training/test_surrogate_dataset.py + test_surrogate_fidelity.py + test_surrogate_runner.py (re-pins + the stale baseline-3 docstrings corrected)

**Files NOT in scope:**
- training/bakeoff/ (17.11/17.12)
- replays/ (consumes 17.9's bytes)

**Definition of done:**
- [ ] The artifact bundle is re-committed with coherent provenance (new sha in the sidecar and the re-derived max-uses key; the fit corpus named); the report regenerates every cell from the new corpus with the three-axis verdict stated and the axis-by-axis arithmetic beside it.
- [ ] Coerced-SKIP handling pinned: fit-side rows carrying the coercion marker are dropped and counted (the count in the report); fidelity replay scores recorded bytes unfiltered.
- [ ] The J1 live-parity divergence is measured on committed bytes and recorded (raw vs clamped, which side the fit reads, the count of rows where it matters).
- [ ] The GO/NO-GO verdict and its consequences are stated in the report exactly as locked decision 4 defines them (promotion iff the bar passes; diagnostic-only otherwise; the bake-off is not blocked in either direction).
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

Sequence: re-validate the dataset walk on the new bytes FIRST (the fidelity cross-check),
then filter, then fit, then verdict — a fit on an unvalidated table wastes the session.
The report regeneration is mechanical once the cells exist; keep the three-axis
arithmetic in the same table shape as the Phase-15 report so the verdicts diff cleanly.

**Integration risk:**

The dataset's hand-mirrored perception→belief pins (`_WindowStats`) are unprotected by
state-hash verification — if any baseline-5 belief-rule nuance drifted them, the
`belief_suspicion` column corrupts SILENTLY. The re-validation must include at least one
end-to-end cross-check against the production fold on real corpus meetings (the 16.10
walk precedent: measure fidelity, don't assume it) before any fit is trusted.

**Ready-to-paste prompt:** `agent_prompts/task-17-10-surrogate-reground.md`

### Task 17.11 — Selection-bar re-pins: the bake-off flips to the baseline-5 floors
**Branch:** `phase-17-selection-bar-repins`
**Depends on:** 17.9
**Section refs:** training/bakeoff/harness.py:114 `CORPUS_SPLITS_PATH` + :125 `BAKEOFF_BASELINE_ID` + :165 `GOODHART_9P2I_BASELINE` (the three baseline-3 anchors); eval/watchability.py:799 `_DEFAULT_BASELINE_ID` (already baseline-5 — the note at :795 says the bake-off constant lags deliberately until this task); training/crew/scorer.py (imports the constant); training/bakeoff/goodhart.py (the default baseline_id)
**Complexity:** Small

Flip the training-side selection anchors to the close-era floors: `BAKEOFF_BASELINE_ID`
→ `"baseline-5"` (the literal pinned by the 17.7 STAY-OFF ruling), the goodhart
default with it, and re-measure `GOODHART_9P2I_BASELINE`'s
fake-provider probe numbers at the current tree ($0, offline). `CORPUS_SPLITS_PATH`
stays put — 17.9 regenerated its file in place. Re-pin the training tests that read
these constants. After this task, every candidate the harness scores is judged against
the floors the phase selects on.

**Files in scope:**
- training/bakeoff/harness.py (the two constants + the probe re-measure)
- training/bakeoff/goodhart.py (the default)
- training/crew/scorer.py (only if the import shape needs the explicit id)
- eval/watchability.py (the :794-798 lag note ONLY — the note says the bake-off constant deliberately lags until Phase 17; this task closes it. Floor BLOCKS stay record-pinned and are not touched)
- tests/training/test_bakeoff_harness.py + test_goodhart_probe.py (constant + probe re-pins)

**Files NOT in scope:**
- eval/watchability.py floor blocks (floors are pinned by records — 17.17 — never by this task; only the :794-798 note region above is in scope)
- training/surrogate/ (17.10)

**Definition of done:**
- [ ] Both constants name the selection baseline; the watchability note at eval/watchability.py:795-798 is updated to say the lag is closed; no test or module still selects baseline-3 floors on the training side (grepped, stated in the PR).
- [ ] `GOODHART_9P2I_BASELINE` is re-measured at HEAD (the probe run quoted), never hand-copied.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Ready-to-paste prompt:** `agent_prompts/task-17-11-selection-bar-repins.md`

## Wave 3 — training

### Task 17.12 — The impostor bake-off re-run (full slate) + finalist selection
**Branch:** `phase-17-impostor-bakeoff-rerun`
**Depends on:** 17.10, 17.11
**Section refs:** tasks/phase-15.md 15.15 (the recipe this re-runs verbatim); training/bakeoff/harness.py (the protocol: surrogate path + fake-provider real path, `--entrant all`); audits/audit-phase-15-pause.md (the decisions binding re-runs: methods in, torch out, stabilizers); the 16.11 referee floors via 17.11's constants
**Complexity:** Integration

Re-run the Phase-15 recipe with the full slate (locked decision 1) against the
re-grounded surrogate and the baseline-5 selection floors: all four impostor methods
through the same seeds/compute protocol, results table regenerated, finalists chosen
by the same referee-gated ranking. The report must show FLOOR SENSITIVITY per finalist
(distance to each supply floor and the conversion floor) beside the ranking — the
designer ruling on selection-bar honesty: a starved-economy rejection must be legible
as the instrument working. Method ranking changes vs Phase 15 are findings to explain
(what about the baseline-5 economy moved them), not anomalies to smooth.

**Files in scope:**
- training/reports/results-impostor-bakeoff.jsonl (regenerated rows)
- training/reports/report-impostor-bakeoff.md (the re-run report + floor sensitivity)
- training/artifacts/impostor/ (candidate artifacts per method)
- tests/training/test_bakeoff_harness.py (protocol re-pins if rows move)

**Files NOT in scope:**
- agents/tactical/learned/ (productization is 17.16's, after the real-LLM eval)
- training/crew/ (17.13)

**Definition of done:**
- [ ] All four methods complete the protocol on the re-grounded substrate; the results table carries per-entrant referee scoring under the flipped floors with floor-sensitivity columns; finalists are named by the recorded ranking rule.
- [ ] The Phase-15 vs Phase-17 ranking delta is stated with a substrate-grounded explanation per mover; every artifact row stamps the 15.9 provenance (policy_id, method, encoder_version, weights sha, anchor).
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

`--entrant all` re-runs the recorded protocol; the work is in the reading, not the
wiring. Budget the ES loops first (they dominated Phase 15); quote surrogate max-uses
consumption per entrant as you go so the cap never surprises the tail entrants.

**Integration risk:**

Operator compute: the ES/DAgger loops are the long pole after the corpus. If a method
fails to converge on the new economy, record the failure as a finding row (the Phase-14
doctrine) — the slate is full so the phase never hinges on one method. The surrogate's
staleness cap is live: the harness must respect the re-derived max-uses budget, and the
report quotes consumption.

**Ready-to-paste prompt:** `agent_prompts/task-17-12-impostor-bakeoff-rerun.md`

### Task 17.13 — The crew track re-run (measurement-only)
**Branch:** `phase-17-crew-track-rerun`
**Depends on:** 17.10, 17.11
**Section refs:** tasks/phase-15.md 15.16 + 15.22 (the crew bases: the general track + the owned-task surface); training/crew/scorer.py (the referee import 17.11 flipped); locked decision 1 (measurement-only — no crew deployment surface this phase)
**Complexity:** Medium

Re-run both crew bases under the baseline-5 economy and floors, regenerate the crew
results and report. Measurement-only by locked decision: rankings, referee scores, and
findings are recorded; no crew artifact ships to a production surface (there is none —
`factory.py` wraps impostor decisions only). The interesting question the report must
answer: does the citation-era economy change what crew utility learns (e.g. does the
owned-task base's advantage move when convictions demand citations)?

**Files in scope:**
- training/reports/results-crew-track.jsonl + results-crew-owned-tasks.jsonl (regenerated)
- training/reports/report-crew-track.md (the re-run reading)
- training/artifacts/crew/ (candidate artifacts, measurement-tier)
- tests/training/test_crew_options.py (re-pins if rows move)

**Files NOT in scope:**
- agents/tactical/learned/ (no crew deployment — locked decision 1)
- training/bakeoff/harness.py (17.11/17.12's)

**Definition of done:**
- [ ] Both crew bases complete under the flipped floors; the report states the baseline-5 vs baseline-3 delta per base with the economy-grounded reading, and every artifact row carries provenance stamps.
- [ ] The measurement-only posture is stated in the report with the Phase-18 routing note (a crew deployment surface is heterogeneous-lobby work).
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

This is a re-run, not a redesign — the 15.16/15.22 protocol verbatim on the new
substrate. Resist adding crew-side features; the value is the clean before/after.

**Ready-to-paste prompt:** `agent_prompts/task-17-13-crew-track-rerun.md`

### Task 17.14 — The multi-finalist recorder + the real-LLM finalist eval (operator, $0)
**Branch:** `phase-17-finalist-eval`
**Depends on:** 17.12
**Section refs:** audits/audit-phase-15-pause.md:145-184 (the uncommitted per-finalist driver this task productizes); scripts/run_tournament.py:244-265 (`--agent-factory learned-champion` — loads only the ONE committed artifact today); tasks/phase-16.md 16.14 §5 (the stamp-proven champion-row precedent); audits/audit-phase-16-close.md §0.5 (operator concurrency notes)
**Complexity:** Integration

Close the tooling gap the pause left: the CLI can only run the committed champion, so
evaluating MULTIPLE new finalists on the real Featherless path needs a productized
multi-finalist recorder — extend `run_tournament.py` (or a sibling entry point) to load
a named candidate artifact by path with full provenance stamping (the 15.9 stamp,
sha-verified against the artifact sidecar), never touching the committed champion
surface. Then the operator leg: each finalist runs the 50-seed 9p2i real-path eval at
the current substrate, rows stamp-proven (the 16.14 discipline), validity-gated, $0.
The output table — win edge vs the same-substrate scripted baseline + referee scoring
per finalist — is 17.16's evidence.

**Files in scope:**
- scripts/run_tournament.py (the candidate-artifact loading path + stamping)
- training/reports/results-finalist-eval.jsonl (new: stamp-proven finalist rows)
- training/reports/report-finalist-eval.md (the evidence table)
- tests/scripts/ (loader fixtures: sha mismatch fails loud; stamp fields exact)

**Files NOT in scope:**
- agents/tactical/learned/ (the committed champion is untouched until 17.16)
- training/bakeoff/ (selection already happened; this is the real-path check)

**Definition of done:**
- [ ] The recorder loads an arbitrary candidate artifact with sha verification (mismatch fails loud before any spend) and stamps every game row with the full 15.9 provenance; fixture-pinned.
- [ ] Every finalist's 50-seed eval is committed with stamp-proof rows, validity gate PASS, and the evidence table (win edge, referee scoring, floor sensitivity) in the report.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

Productize the pause's driver as a thin loader parameter on the existing tournament
path — the champion factory already does artifact-loading + sha verification; generalize
its entry point rather than writing a second loader. Stamp fields come from the
candidate's own config, never from the committed champion's constants.

**Integration risk:**

Two learned movers must never be conflated in one recording: the loader binds ONE
candidate per tournament invocation and the stamp names it — assert no ambient state
leaks between runs. Real-path concurrency: champion games collide in ballot phases
(the 16.14 finding) — single-worker tails or staggering, attempts ≥8.

**Ready-to-paste prompt:** `agent_prompts/task-17-14-finalist-eval.md`

### Task 17.15 — The Goodhart probe re-run on the re-grounded surrogate
**Branch:** `phase-17-goodhart-rerun`
**Depends on:** 17.10, 17.11
**Section refs:** tasks/phase-15.md 15.14 (the probe design); training/bakeoff/goodhart.py (the probe machinery + the baseline delta anchor 17.11 re-measured); training/reports/report-goodhart-probe.md (regenerated)
**Complexity:** Medium

Re-run the reward-hacking probe against the re-grounded surrogate: can an optimizer
exploit surrogate-vs-real divergence on the baseline-5 economy? The Phase-15 reading
(bounded divergence, no exploitable seam at the measured scale) must be re-earned, not
assumed — the new economy has MORE structure in ballots (citations) that the 6-feature
surrogate cannot see, which is exactly where a gap could open. Regenerate the report
with the delta anchors from 17.11's re-measured baseline.

**Files in scope:**
- training/reports/report-goodhart-probe.md (regenerated)
- training/bakeoff/goodhart.py (probe-run wiring only if the protocol needs the new anchors threaded)
- tests/training/test_goodhart_probe.py (re-pins)

**Files NOT in scope:**
- training/surrogate/ (consumes 17.10's artifact)
- training/bakeoff/harness.py (17.12's)

**Definition of done:**
- [ ] The probe re-runs end-to-end on the re-grounded surrogate with the re-measured anchors; the report states the divergence reading and whether the Phase-15 no-exploitable-seam conclusion survives baseline 5, with the citation-blindness caveat addressed explicitly.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

The probe is an instrument, not a gate — a widened divergence is a finding that bounds
how hard 17.12's optimizers may lean on the surrogate (the max-uses budget already
prices this); say the implication, don't re-plan the bake-off.

**Ready-to-paste prompt:** `agent_prompts/task-17-15-goodhart-rerun.md`

## Wave 4 — adoption + close

### Task 17.16 — Champion productization + the evidence-gated default flip
**Branch:** `phase-17-champion-flip`
**Depends on:** 17.14
**Section refs:** locked decision 2 (the flip criterion: referee PASS + retained win edge at 17.14); agents/tactical/learned/factory.py + forward.py (the opt-in surface, swapped in place); training/reports/report-finalist-eval.md (the evidence); tasks/phase-15.md 15.20/15.21 (the productization + factory precedents); orchestrator/replay.py `TacticalPolicyStamp` + `FSM_DEFAULT_POLICY_ID` (the default-mover identity the flip moves)
**Complexity:** Integration

Read 17.14's evidence against locked decision 2 and act on the ruled branch — the
referee floors are the ladder tip's at selection time (baseline 5 — the literal pinned
by the 17.7 STAY-OFF ruling). PASS
(referee floors + conversion + retained win edge): swap the committed champion artifact
to the winning finalist (weights + sha + config + stamp constants), then flip the
DEFAULT mover — the scripted-default factory yields to the learned factory at the
DEFAULT-SELECTOR surfaces (the run_tournament default and the orchestrator's default
factory selection). `FSM_DEFAULT_POLICY_ID` and the absent-stamp fallback
interpretation are PRESERVED untouched: an absent `tactical_policy` stamp is read as
`fsm_default_tactical_policy_stamp()` today, so moving that identity would reinterpret
historical/unstamped replays as champion games — the flip changes what future runs
SELECT, never how recorded bytes are READ. The scripted FSM stays the named
fallback/opt-out. FAIL: swap nothing OR swap the opt-in artifact
only if the new finalist referee-dominates the old one — either way the default stays
scripted and the finding is recorded. Both branches are contracted; the evidence
reading is quoted in the PR and ratified by the owner merging it. NO baseline records
here — 17.17 records the flipped substrate.

**Files in scope:**
- agents/tactical/learned/weights.json + .sha256 + config (the artifact swap)
- agents/tactical/learned/factory.py + forward.py (stamp constants; the default wiring on the PASS branch)
- scripts/run_tournament.py + orchestrator/ (the default-mover flip surfaces, PASS branch only)
- tests/ (stamp + default-identity re-pins on the ruled branch)

**Files NOT in scope:**
- replays/ (17.17 records)
- training/ (evidence is committed; this task consumes)

**Definition of done:**
- [ ] The evidence reading is stated against locked decision 2's criterion verbatim (each floor, the conversion figure, the win edge) and the ruled branch is fully implemented; on PASS the default-SELECTOR surfaces change (grepped and listed) while `FSM_DEFAULT_POLICY_ID` and the absent-stamp fallback interpretation are provably untouched — a fixture pins that an unstamped/absent-stamp replay still resolves to the FSM stamp; the opt-out to the scripted FSM works and is fixture-pinned; on FAIL the default provably does not move.
- [ ] The committed artifact (if swapped) is sha-coherent (weights, sidecar, stamp constants, factory verification) and the provenance stamp names the new policy exactly.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

Grep for `fsm-default` and the factory-selection surfaces BEFORE writing: the flip is a
default-identity change in a small named set of places, and the DoD requires listing
them. Keep the scripted path fully alive behind the opt-out — the FSM is the fallback
and the anchor baseline for every future comparison.

**Integration risk:**

The default flip is the phase's riskiest single change: every replay consumer assumes
the mover identity stamped in recorded bytes, and committed sets were recorded
`fsm-default` — the flip must change FUTURE defaults without re-interpreting committed
history (stamps are per-record truth; nothing rewrites them). The 17.17 record is where
the flipped default first meets a canonical set — keep this task record-free.

**Ready-to-paste prompt:** `agent_prompts/task-17-16-champion-flip.md`

### Task 17.17 — Baseline 6: the mover record + the phase close (operator + owner, $0)
**Branch:** `phase-17-baseline-6-close`
**Depends on:** 17.1, 17.3, 17.6, 17.13, 17.15, 17.16
**Section refs:** tasks/phase-16.md 16.17 (the close runbook: atomic record, validity gates, floors, canaries, Q5, banner); audits/audit-phase-16-close.md §0.4 (the canary-band discipline + the R1 band-edge warning) + §8 (the staleness rule this close re-states for Phase 18); eval/vote_correctness.py (17.6's successor instrument — canary-eligible for the first time); replays/ml_corpus/ (the Q3-restored canonical denominator)
**Complexity:** Integration

The phase's terminal record and second owner gate. FLIP path (17.16 flipped the
default): atomic re-record of both sample sets with the champion as the default mover —
**baseline 6**, the first mover-layer baseline — MANIFEST provenance exact (the policy
column names the champion stamp), validity gates, byte-identical bare reconstruction,
floors re-pinned, pre-registered canary bands on the Q3-restored corpus denominator
(the close's canaries finally leave the 50-seed UNDERPOWERED regime) with 17.6's
successor instrument as a named canary cell, full before/after on 16.10's instruments,
Q5 tag (the owner completes the push), close audit, banner flip to CLOSED, README +
roadmap provenance. NO-FLIP path: no record — the ladder tip stands, and the close
audit documents the finding (which floor failed, by how much, what Phase 18 would need)
with the same instrument reads over the existing bytes. Either way the audit re-states
the staleness rule for Phase 18 (heterogeneous lobbies change the meeting layer AGAIN —
nothing in this phase's artifacts survives that unexamined) and routes the deferred
items (crew deployment surface, detector-band relaxation, absence-prior Phase-18
re-run if stay-OFF, pooling-prompt uptake work).

**Files in scope:**
- replays/samples/9p2i/ + replays/samples/4p1i/ (the baseline-6 record — FLIP path only)
- eval/watchability.py (baseline-6 floors — FLIP path only)
- audits/baseline5-final-measure.json (new: the BEFORE column, captured pre-replacement — FLIP path)
- audits/audit-phase-17-close.md (new)
- tasks/phase-17.md (the banner flip)
- README.md + tasks/post-phase-14-plan.md (status + provenance)
- tests/ (re-pins + the byte-coupled sweep)

**Files NOT in scope:**
- replays/ml_corpus/ (recorded once at 17.9 — the mover flip does not invalidate meeting-layer calibration data; the close audit SAYS so explicitly, with the caveat that impostor-behavior-conditioned cells are champion-era from baseline 6 on)
- agents/ + training/ (frozen at 17.16)

**Definition of done:**
- [ ] FLIP path: both sets recorded with the champion default and PASS the validity gate; byte-identical bare reconstruction; the MANIFEST policy column names the champion stamp on every row; floors pinned; canaries judged on the corpus denominator with the pre-registered bands quoted (17.6's successor cell among them); the before/after instrument read committed. NO-FLIP path: the close audit's finding section carries the full floor arithmetic and instrument reads with no record.
- [ ] The close audit re-states the Phase-18 staleness rule and the routed items, names the Q5 tag arm (or its fallback), and the banner/README/roadmap lines record the close.
- [ ] `scripts/compute_next_task.py --phase 17` shows the phase complete; validator green.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

Pre-register the canary bands and capture the BEFORE column before the first recorded
seed (the 15.18/16.17 discipline). On the no-flip path resist recording anything — the
close's value is the honest finding; on the flip path the record session is the 16.17
runbook with the mover as the only changed layer.

**Integration risk:**

First mover-layer record on the ladder: the R-gate and funnel cells will move for
CHAMPION reasons, not meeting-layer reasons — the audit must attribute every canary
band to the right layer (the before column is same-meeting-layer, so deltas ARE the
mover; say so). The 16.4-era counterfactual tests that walk committed bytes with
recorded roles must be re-pinned for the new bytes — the same byte-coupled sweep every
record performs, budgeted in the session.

**Ready-to-paste prompt:** `agent_prompts/task-17-17-baseline-6-close.md`

---

## Merge criteria — the absence gate (mid-phase)

The 17.7 PR merges only when: the memo quotes every evidence source; the numeric bar is
proposed and the owner's three rulings are recorded verbatim; the surgery is complete
in the ruled direction with validator/prompts green and no orphan references; and the
sequencing consequence is stated (the corpus record is unblocked, at which meeting
layer).

## Merge criteria — end of phase

Phase 17 closes when 17.17 merges with: the ruled path fully executed (record + canaries
+ floors, or the no-flip finding); every wave-0 instrument repair live in the close's
own reads; the surrogate verdict recorded with its usage tier; the bake-off + crew +
finalist evidence committed with provenance stamps; the staleness rule re-stated for
Phase 18 with the routed items named; and the banner, README, and roadmap all recording
the close. Deferred items leave as CONTRACTS routed to Phase 18, never as silent gaps.
