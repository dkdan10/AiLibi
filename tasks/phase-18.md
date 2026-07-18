# Phase 18 — The ML phase: emergent deception and deduction under environmental pressure

STATUS: OPEN 2026-07-18. The owner re-chartered this phase (recorded in
`audits/audit-phase-18-planning.md`): Phase 18 is the ML phase — advance the learned agents
until deception and deduction arise from environmental pressure rather than scripting.
Presentation is DEFERRED; Phase 19 is re-chartered as REVIEW-AND-REFRESH (deep code review +
frontend/data-display refresh); the human seat is OUT; heterogeneous-model lobbies are not in
Phase 19 either (a later decision, after the review/refresh work). The five locked decisions
below were ratified by the owner on 2026-07-18 at the planning session's decision menu
(`audits/audit-phase-18-planning.md` §8), sign-off additionally riding the merge of this
phase doc (the 15.18 convention).

## Locked decisions (owner-ratified 2026-07-18)

1. **Training signal: layered — conviction-economy proxy + real-path selection.** A
   conviction-economy proxy model (predicting per-meeting evidence supply and conviction
   from channels a training-time runner can honestly reconstruct — `audits/
   audit-phase-18-planning.md` §2.3) enters the inner fitness as a REWARD-side term and
   serves as a referee pre-screen; real-path signal reaches selection via per-generation
   top-K re-ranks (~2 h/generation at 2 workers). The citation-aware BALLOT surrogate is
   REJECTED (it would train on features the live runner cannot serve — the 6-feature
   live-parity fence failure). The real-path fine-tune stage (design D) is NOT adopted; it
   may be proposed later via an owner gate only if campaigns plateau, and it would be
   recorded as its own non-reproducible tier, never silently.
2. **The meeting-layer package runs in-phase, FIRST, behind a gate.** Roll-call round +
   endpoint-band whereabouts exemption + impostor-answer templates + vent widening re-rule +
   absence-prior graduation re-run, all measured in an evidence memo with the pre-registered
   bars in 18.11 BEFORE any adoption. The gate rules FULL / CREW-ONLY / NONE; the CREW-ONLY
   fallback is pre-authored inside 18.11's ruling directions, and the NONE surgery is
   enumerated in the Baseline-numbering block. Standing rule 2 sequencing: the package's
   adopting record (18.12) and the corpus re-record (18.13) precede every training record.
3. **Co-evolution: alternating-freeze with the stabilizer stack, impostor-first.** Frozen
   hall-of-fame + hardness-weighted opponent sampling (PFSP-lite) + absolute
   scripted-FSM anchor benchmarks as the cycling detector + a per-side exploiter probe. The
   naive simultaneous two-population form stays BARRED (pause decision 4). The crew
   deployment surface is built now (18.7), opt-in only; crew champion ADOPTION has no path
   this phase except through the standing gates. The impostor campaign runs first — crew
   deduction fitness is structurally dead until training meetings convict
   (`training/rewards.py:211-218`; the fake/surrogate paths eject nobody).
4. **Success bars: the §1.3 flip bar is the TARGET, emergence instruments co-equal.** The
   recorded default-flip bar stands unchanged (flags/meeting ≥ 0.50279 at the baseline-5
   economy — re-pinned at whatever baseline the phase adopts — AND the population-relative
   conversion floor cleared AND win ≥ the same-substrate FSM's). The pre-registered
   emergence instruments (18.4) are the co-equal second success axis; landing either with
   the other honestly measured is a successful close, and missing both closes as a measured
   finding (findings-not-failures).
5. **Architecture: the menu-bounded champion ships; encoder work rides the co-evolution
   wave.** First-principles action primitives are REJECTED (the masked intent space already
   spans them — `training/env.py:239-361`; the gap is perception, not actions). Encoder v3 +
   within-kind target resolution (18.22) advance the free-policy family only inside the
   co-evolution wave, where opponent pressure punishes tells, with the off-menu instrument
   (18.3) watching its recordings.

## Designer rulings (recorded here so contracts inherit them)

- **Watchability stays a gate, never a reward — and never a fitness term in disguise.** The
  conviction-economy proxy (18.15/18.16) predicts pre-meeting evidence supply from tactical
  facts; it must never read, wrap, or re-derive `eval/watchability.py` scores. The
  gate/reward boundary line is `training/bakeoff/harness.py:582-585` and it does not move.
- **The proxy is not the ballot surrogate.** `training/surrogate/` (the ballot predictor,
  its 6-feature fence, its GO bar, its staleness cap) is untouched by the conviction model;
  the two are independent artifacts with independent verdicts. The Goodhart probe re-runs
  when the training-signal role grows (18.18) — the standing rule.
- **Meeting-layer mechanisms land default-OFF and inert** (the 13.5/14.10 lever pattern):
  the roll-call round (18.8), the endpoint-band exemption (18.9), and the impostor-answer
  variant (18.10) each ship flag-gated with no default-path byte movement, proven by
  committed-bytes counterfactuals where offline measurement is possible; the gate (18.11)
  rules what graduates; the adopting record (18.12) flips what ships.
- **Pre-registration precedes measurement.** The emergence bars (18.4) are ratified before
  any campaign records; campaign reports read against them, never the reverse. An emergence
  claim needs the full discipline: significance vs the same-seed FSM comparator,
  split-reproducibility, a counterfactual ablation, and selected-for status (present in the
  champion, not only the archive).
- **Two-identity stamps for two learned sides.** A recording carrying learned policies on
  both sides must attribute each side honestly (18.19's additive crew stamp beside the
  existing `tactical_policy` stamp); one policy never wears two stamps, and no stamp is ever
  echoed from launch config rather than read back from bytes.
- **Operator sessions follow the standing runbook**: staggered workers, jittered backoff,
  `AILIBI_SEED_MAX_ATTEMPTS=8`, per-seed atomic staging, checkpoint-push for long
  recordings; the Q5 tag arm may need the owner's local machine (this environment's
  credential refuses tag pushes — the 16.14/16.17 limitation).

## The DAG

```
Wave 0 (roots, layer-neutral, dispatch in parallel):
  18.1 (Tier-A deception instruments)   18.2 (kill-craft + action-entropy folds)
  18.3 (off-menu action instrument)     18.5 (anchor study: lambda sweep + filtered-BC)
  18.6 (MAP-Elites cell persistence)    18.7 (crew deployment surface, opt-in)
  18.17 (real-path re-rank recorder — numbered with Wave 2, dispatchable from day one)
  (18.1, 18.2, 18.3) -> 18.4 THE EMERGENCE PRE-REGISTRATION [OWNER]

Wave 1 (the meeting-layer package — before anything trains):
  18.8 (roll-call round)   18.9 (endpoint-band exemption)   18.10 (impostor-answer variant)
  (18.8, 18.9, 18.10) -> 18.11 THE MEETING-LAYER GATE [OPERATOR ~8-9h + OWNER]
  18.11 -> 18.12 adopting record: baseline 6 [OPERATOR ~6-7h]
  18.12 -> 18.13 corpus re-record [OPERATOR ~18-20h]
  18.13 -> 18.14 surrogate re-ground + selection-bar re-pins

Wave 2 (training signal):
  18.13 -> 18.15 conviction-economy model + GO bar
  (18.14, 18.15) -> 18.16 fitness term + referee pre-screen integration
  18.16 -> 18.18 Goodhart re-probe (conviction path + the carried d4 exploit)

Wave 3 (co-evolution):
  (18.7, 18.16) -> 18.19 dual-role rollout + two-identity stamp
  (18.6, 18.19) -> 18.20 hall-of-fame + PFSP-lite sampler
  18.20 -> 18.21 alternating-freeze driver + stabilizers
  18.19 -> 18.22 encoder v3 + within-kind target resolution
  18.16 -> 18.23 scenario staging (state injection + skill scenarios)
  (18.17, 18.21, 18.22) -> 18.24 THE IMPOSTOR CAMPAIGN [OPERATOR multi-session]
  18.24 -> 18.25 THE CREW CAMPAIGN [OPERATOR]

Wave 4 (selection + close):
  (18.24, 18.25) -> 18.26 real-LLM finalist eval [OPERATOR ~5h/finalist]
  (18.4, 18.18, 18.26) -> 18.27 THE FLIP + EMERGENCE READING [OWNER]
  (18.5, 18.23, 18.27) -> 18.28 mover record + phase close [OPERATOR + OWNER]
```

Critical path: 18.8/18.9/18.10 → 18.11 → 18.12 → 18.13 → 18.15 → 18.16 → 18.19 → 18.20 →
18.21 → 18.24 → 18.26 → 18.27 → 18.28. Wave 0 is seven independent roots; nothing outside
the gate chain waits on the owner.

**Baseline numbering.** The ladder tip stands at baseline 5 (`audits/
audit-phase-17-close.md`). The meeting-layer adopting record at 18.12 is **baseline 6**; a
mover flip at 18.28 records **baseline 7**. Gate-conditional surgery, pre-enumerated per the
16.2/17.7 discipline (removal, not labeling — `scripts/compute_next_task.py` has no dropped
state): a FULL or CREW-ONLY ruling at 18.11 changes no structure (the arms that ship are the
ruling's business; 18.12–18.14 proceed either way). A **NONE** ruling removes 18.12, 18.13,
and 18.14 (contracts + prompts, with a drop record naming the gate audit), rewires 18.15's
`Depends on:` to `18.11`, binds 18.15 to the standing baseline-5 corpus (its contract names
this fallback), leaves `BAKEOFF_BASELINE_ID = "baseline-5"` untouched, and renumbers the
18.28 mover record baseline 7 → 6. Under NONE the absence prior stays OFF with the ratified
bar unmet, restated in the gate audit.

**Collision discipline.** `meetings/manager.py` single-toucher 18.8; `meetings/
transcript.py` 18.9; `agents/strategic/prompts/` 18.10; `eval/watchability.py` floor blocks
18.12 only; `replays/samples/` 18.12; `replays/ml_corpus/` + `scripts/record_ml_corpus.sh`
18.13; `training/bakeoff/harness.py` 18.14 (constants) then 18.16 (term/pre-screen),
serialized by the dep chain; `training/bakeoff/map_elites.py` 18.6; `agents/tactical/
learned/` 18.7 then 18.27 (ordered via the dep chain); `scripts/run_tournament.py` 18.7 then
18.19 (dep edge); `orchestrator/replay.py` 18.19; `orchestrator/game.py` + `training/env.py`
18.23; `agents/tactical/features.py` 18.22; `training/coevo/` is 18.19/18.20/18.21 in
dep order with per-task module files; `tasks/phase-18.md` + `agent_prompts/` surgery 18.11
(and the close banner at 18.28, ordered).

**Operator/owner gates.** Operator sessions: 18.11 (probe recordings ~8–9 h), 18.12 (~6–7 h),
18.13 (~18–20 h — the long pole; checkpoint-push), 18.24 (multi-session; ~40–50 h of
unattended real-path re-rank legs spread across the campaign), 18.25, 18.26 (~5 h/finalist),
18.28 (~6 h on the flip path). Owner gates: **18.4** (emergence pre-registration), **18.11**
(the meeting-layer ruling), **18.27** (the flip + emergence reading), **18.28** (the close).

---

## Wave 0 — instruments, studies, and surfaces (seven roots)

### Task 18.1 — Tier-A deception instruments: false-vouch, frame jobs, teammate immunity
**Branch:** `phase-18-deception-instruments`
**Depends on:** none (root)
**Section refs:** audits/audit-phase-18-planning.md §3.1–§3.2 (the census: 455 frame attempts, 34 false vouches, 5 conversions; the gap table); eval/funnel.py `_vouch_census` (:1404) + `_grounded_vouch_set` (:1430); eval/alibi_fabrication.py:153 (the survival analyzer to adopt); eval/meeting_quality.py:2277 (`EffectiveDeflectionReport`, the role-agnostic neighbor)
**Complexity:** Medium

The deception behaviors the phase targets already exist in the committed bytes and are
un-instrumented. Build the Tier-A analyzer set as one pure module over `TournamentReport`:
**false-vouch rate** (impostor turns whose `SawPlayerObservation`/`CorroborationClaim`
subject is the co-impostor; grounded-vs-fabricated split via the production
`grounded_vouch_subjects` chokepoint), **frame-attempt and frame-conversion rate** (impostor
`AccusationClaim` against a true crewmate; conversion = that crewmate ejected — rare-event,
reported with the advisory discipline), **teammate-non-accusation index** (0/455 on the
corpus today), and adoption wrappers surfacing the existing fabricated-alibi survival and
deflection-efficacy analyzers beside them. Every cell population-relative in framing; every
committed-bytes value pinned (corpus + samples denominators).

**Files in scope:**
- eval/deception_instruments.py (new)
- tests/eval/test_deception_instruments.py (committed-bytes pins + synthetic fixtures)

**Files NOT in scope:**
- eval/funnel.py + eval/alibi_fabrication.py + eval/meeting_quality.py (consumed, never edited)
- eval/watchability.py (no floor changes — these are diagnostics, not gates)

**Definition of done:**
- [ ] On the committed corpus bytes the module reports the census cells (impostor→crew accusations, teammate accusations 0, false vouches, frame conversions) with numerators/denominators pinned; the grounded-vs-fabricated vouch split runs through the production grounding chokepoint, never a re-derivation.
- [ ] Rare-event cells (frame conversions ≤ 7 numerator) carry the advisory label and a Wilson interval beside the point estimate, per the 15.19 rare-event rule.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

Follow the `eval/alibi_fabrication.py` shape: a pure function over the assembled report +
roles, one frozen Pydantic report model, committed-bytes pins as the primary tests. The
vouch census and subject-membership patterns you need already exist (`eval/funnel.py:1404`,
`eval/alibi_fabrication.py:219`) — reuse their logic via import where public, otherwise
mirror with a comment naming the source.

**Public types introduced:**
- `eval.deception_instruments.DeceptionInstrumentsReport`
- `eval.deception_instruments.compute_deception_instruments`

**Ready-to-paste prompt:** `agent_prompts/task-18-1-deception-instruments.md`

### Task 18.2 — The kill-craft fold: kill-timing vs witness density + action-stream entropy
**Branch:** `phase-18-kill-craft-fold`
**Depends on:** none (root)
**Section refs:** audits/audit-phase-18-planning.md §3.2 (the Tier-B gap rows); eval/watchability.py:1031 (`_reconstruct_kills`, the engine walk to extend); engine/events.py:76 (`KilledEvent.tick/room/witnesses`); eval/vj_instruments.py:704-719 (the lexical diversity cells this complements)
**Complexity:** Medium

Two new reconstruction folds, one module. **Kill-timing vs witness density**: per recorded
kill, the count of living crew co-present or one hop away at the kill tick (a per-tick
occupancy census added to the existing engine reconstruction walk), correlated with the
witnessed bit — the first byte-grounded gauge of kill-craft (does the mover kill into
witnesses or wait them out?). **Action-stream behavioral entropy**: per-agent entropy of
action-kind choices bucketed by coarse agent-state (room occupancy count, cooldown state),
the intent-level diversity metric beside the existing lexical one. Both offline over
committed bytes; both pinned on corpus + samples.

**Files in scope:**
- eval/kill_craft.py (new)
- tests/eval/test_kill_craft.py

**Files NOT in scope:**
- eval/watchability.py (its walk is consumed via import or a faithful local walk — the referee itself does not move)
- engine/ (read-only reconstruction)

**Definition of done:**
- [ ] On committed corpus bytes the fold reports per-kill witness-density cells (co-present, one-hop) and the witnessed correlation, plus per-side action-entropy cells, all pinned; the occupancy census agrees with the engine walk's per-tick state (state-hash-verified reconstruction).
- [ ] The entropy bucketization is documented in the module docstring and deterministic (sorted, quantized) — no float-ordering hazards.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

The reconstruction walk (`re-seed + advance_tick` over recorded actions) already exists in
two places (`eval/watchability.py:1031`, `eval/funnel.py:287`); build the occupancy census
as a fold over that walk rather than a third walk implementation if a shared seam is
reachable without editing the referee — otherwise a local walk with the state-hash check is
acceptable and the duplication is noted for Phase 19's review.

**Public types introduced:**
- `eval.kill_craft.KillCraftReport`
- `eval.kill_craft.compute_kill_craft_report`

**Ready-to-paste prompt:** `agent_prompts/task-18-2-kill-craft-fold.md`

### Task 18.3 — The off-menu action instrument (free-policy recordings)
**Branch:** `phase-18-off-menu-instrument`
**Depends on:** none (root)
**Section refs:** audits/audit-phase-18-planning.md §3.2 (the corrected off-menu finding: vacuous for the menu-bounded champion, meaningful for free-policy recordings); training/bakeoff/utility_es.py:209 (`enumerate_options`, the pure public oracle); agents/tactical/learned/forward.py:227 (the production port); eval/funnel.py:287 (the packet-reconstruction walk precedent)
**Complexity:** Medium

The byte-grounded detector of behavior outside the FSM's own option menu: at each recorded
impostor decision, reconstruct the agent-visible packet/memory offline, materialize
`enumerate_options`, and test the recorded action's intent for membership — yielding an
off-menu RATE over a recording. Stated honestly in the module docstring and report: the
menu-bounded champion is on-menu by construction (rate 0 always), so this instrument is
meaningful only for free-policy-family recordings (18.22/18.24) and FSM-generated bytes are
its all-on-menu fixture. This is the emergence gauge for "behavior classes unreachable by
the FSM menu" — a Tier-B pre-registration input.

**Files in scope:**
- eval/off_menu.py (new)
- tests/eval/test_off_menu.py (all-on-menu committed-bytes pin + a synthetic off-menu fixture)

**Files NOT in scope:**
- training/bakeoff/utility_es.py + agents/tactical/learned/forward.py (the oracle is imported, never forked)
- training/bakeoff/harness.py (anchor-CE is a different quantity — rollout-time, distributional; do not conflate)

**Definition of done:**
- [ ] On committed FSM-generated corpus bytes the instrument reads all-on-menu (rate 0) with the reconstruction state-hash-verified; a synthetic recording carrying one off-menu intent reads exactly 1/N with the decision identified.
- [ ] The report distinguishes off-menu-by-kind vs off-menu-by-target (a kind the menu lacks vs a menu kind at a target the menu would not offer), so 18.27 can read WHAT kind of novelty appeared.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

The oracle needs the agent's own reconstructed memory state (the menu is a function of the
packet + episodic recency). The funnel's memory-augmented walk already rebuilds exactly this
(real `TacticalAgent`s fed reconstructed packets); drive the same machinery and call the
oracle at each impostor decision tick. `enumerate_options` raises on empty memory — the
walk's warm-up handles it.

**Public types introduced:**
- `eval.off_menu.OffMenuActionReport`
- `eval.off_menu.compute_off_menu_report`

**Ready-to-paste prompt:** `agent_prompts/task-18-3-off-menu-instrument.md`

### Task 18.4 — THE EMERGENCE PRE-REGISTRATION (owner)
**Branch:** `phase-18-emergence-preregistration`
**Depends on:** 18.1, 18.2, 18.3
**Section refs:** audits/audit-phase-18-planning.md §5 (the operationalization + the four-part claim discipline); the 18.1/18.2/18.3 committed pins (the baseline cells); audits/audit-phase-17-close.md §3 (the corpus-denominator anchor discipline this memo inherits)
**Complexity:** Medium

The memo that makes "emergence" falsifiable before anything trains. Author
`audits/audit-phase-18-emergence-preregistration.md`: for each pre-registered instrument
(Tier A: false-vouch, frame attempt/conversion, teammate immunity, fabricated-alibi
survival, deflection efficacy; Tier B: kill-timing vs witness density, off-menu rate,
action entropy), quote the committed baseline cell with its denominator, and register the
claim discipline: a behavior counts as EMERGENT only if (a) its instrument delta vs the
same-seed scripted-FSM comparator on the real path is significant at |z| ≥ 1.96 on the
pre-registered denominator; (b) the delta reproduces across at least 2 of the 3 corpus
seed-splits; (c) a named counterfactual ablation (remove the enabling lever/feature) shows
the behavior recede; (d) the behavior is selected-for — present in the champion's
recordings, not only the archive. Watchability improvement is never itself an emergence
claim. The owner ratifies bars and instrument list by merge; amendments are recorded in the
memo, and 18.27 reads against this memo verbatim.

**Files in scope:**
- audits/audit-phase-18-emergence-preregistration.md (new: the memo + the ratified bars)

**Files NOT in scope:**
- eval/ (no instrument changes at pre-registration; defects found here route back as contracts)
- tasks/phase-18.md (no surgery at this gate)

**Definition of done:**
- [ ] Every pre-registered instrument's baseline cell is quoted from a committed test pin or committed report with its source named; no hand-computed figures.
- [ ] The four-part claim discipline is stated with the exact statistical rule (pooled two-proportion z for rates; the split-reproducibility rule; the ablation naming convention) and the owner's ratification is recorded verbatim.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

The 17.7 gate shape: evidence first, decision slots explicit, bars proposed with both
directions priced. Rare-event cells (frame conversions at n=5) get advisory framing — the
memo must say what denominator would power them and whether the phase expects to reach it.

**Ready-to-paste prompt:** `agent_prompts/task-18-4-emergence-preregistration.md`

### Task 18.5 — The anchor study: λ sweep + filtered-BC anchor refinement
**Branch:** `phase-18-anchor-study`
**Depends on:** none (root)
**Section refs:** audits/audit-phase-18-planning.md §2.4 (the two levers) + §6 (the piKL reading); training/bakeoff/harness.py `inner_episode_fitness` (:569-590, the anchor penalty seam); training/bakeoff/utility_es.py:708-718 (the full budget: 285 s/run on the fake path); replays/ml_corpus/ (the filtered-BC source)
**Complexity:** Medium

The cheapest levers on the exact gauges the champion failed. (1) **λ sweep**: re-run the
utility-es training at a grid of anchor weights (e.g. 0.25/0.5/1.0/2.0/4.0), score each
champion through the standing fake-path protocol, and report the fitness/anchor-CE/
descriptor-footprint Pareto — the training-time dial that piKL says controls legibility.
(2) **Filtered-BC anchor refinement**: fit an alternative anchor policy over the FSM option
features from the corpus's crew-winning/high-flag games (numpy weighted logistic — the
corpus as a prior source, never a training environment), and run one ES leg anchored to it.
Report-only: no champion ships from this task; the winners are candidate entrants for the
18.24 campaign. Deterministic, $0, CPU.

**Files in scope:**
- training/anchor_study.py (new: the sweep driver + the filtered-BC fit)
- training/reports/report-anchor-study.md (new)
- tests/training/test_anchor_study.py

**Files NOT in scope:**
- training/bakeoff/harness.py + utility_es.py (consumed through their public seams)
- training/artifacts/impostor/ (the committed champions do not move)

**Definition of done:**
- [ ] The sweep reproduces the λ=1.0 committed champion byte-identically (the determinism cross-check), and every sweep row carries fitness, anchor-CE, win rate, take-rate, and descriptor footprint on the standing 30-seed protocol.
- [ ] The filtered-BC anchor's fit is deterministic (documented platform caveat per the surrogate precedent), its game filter is stated (which games, why), and its ES leg reports the same row shape; the report names which candidates (if any) the 18.24 campaign should seed with.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

Full utility-es training is 285 s on the fake path, so the whole grid is under an hour of
CPU — resist any urge to subsample the protocol. The filtered-BC fit mirrors the
`Fo6Logistic` deterministic recipe (zeros init, fixed epochs/lr, no RNG).

**Public types introduced:**
- `training.anchor_study.AnchorStudyReport`
- `training.anchor_study.fit_filtered_bc_anchor`

**Ready-to-paste prompt:** `agent_prompts/task-18-5-anchor-study.md`

### Task 18.6 — MAP-Elites cell persistence + referee-tension descriptors
**Branch:** `phase-18-map-elites-persistence`
**Depends on:** none (root)
**Section refs:** audits/audit-phase-18-planning.md §4 (#10) + §6 (the GAME/QD transfer); training/bakeoff/map_elites.py:207-219 (in-memory cell genomes), :407-418 + :452-458 (the freeze that discards them); training/bakeoff/harness.py:843-868 (`write_candidate_artifact`, the layout to mirror)
**Complexity:** Medium

Two changes to the QD instrument. (1) **Persist every filled cell's genome** at freeze
(per-cell weights + sha sidecars under the archive artifact dir, mirroring the candidate
layout) so the archive becomes a reloadable behaviorally-diverse pool — the hall-of-fame
seed source 18.20 consumes. (2) **Add a second descriptor configuration** whose axes are the
referee's tension quantities computed from tactical facts (per-episode evidence-supply
proxies: witnessed-kill fraction and meeting cadence beside win) — watchability quantities
as DESCRIPTORS (diversity dimensions), never fitness; cell quality stays the standing inner
fitness. The existing 3-axis archive and its committed rows stay byte-stable; the new
configuration is additive and selected explicitly.

**Files in scope:**
- training/bakeoff/map_elites.py (cell persistence + the additive descriptor configuration)
- tests/training/test_bakeoff_methods.py (the map-elites regions: round-trip of persisted cells; the additive config; byte-stability of the default run)
- training/artifacts/impostor/map-elites/ (the persisted-cell layout, regenerated deterministically)

**Files NOT in scope:**
- training/bakeoff/harness.py (its artifact writer is imported, never edited)
- eval/watchability.py (descriptors are computed from rollout facts, never from the referee)

**Definition of done:**
- [ ] A full-budget run persists every filled cell's genome with sha sidecars and reloads them bit-exactly; the default-configuration run's champion, jsonl row, and existing artifact tree are byte-identical to the committed state (pinned).
- [ ] The referee-tension descriptor configuration is additive, documented, and its axes are computed from `DecisionTrace`/rollout facts only — grep-provably no `eval.watchability` import in the entrant module (the standing AST firewall extends to it).
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

The witnessed-kill fraction and meeting-cadence descriptors already exist as rollout
descriptor fields — the new configuration is a re-binning, not new plumbing. Persistence
must be deterministic in iteration order (sorted cell keys) so re-runs are byte-identical.

**Public types introduced:**
- `training.bakeoff.map_elites.write_archive_cell_artifacts`
- `training.bakeoff.map_elites.load_archive_cell_genomes`

**Ready-to-paste prompt:** `agent_prompts/task-18-6-map-elites-persistence.md`

### Task 18.7 — The crew deployment surface (opt-in, adoption gated)
**Branch:** `phase-18-crew-surface`
**Depends on:** none (root)
**Section refs:** audits/audit-phase-18-planning.md §4 (#7); agents/tactical/learned/factory.py:141-152 (the impostor-only wrapper), :199-232 (the factory + stamp); training/crew/scorer.py:197-230, 681-745 (the crew menu's re-validation + emergency bookkeeping the shipped wrapper must carry), :747-769 (`_CrewCandidateAgent`, the hook precedent); training/crew/options.py (the portable menu); audits/audit-phase-15-pause.md decision 6 (the Q4 bit-exact gate)
**Complexity:** Integration

The missing half of co-evolution: a production-tier, opt-in crew scorer surface beside the
untouched scripted default — the 15.20/15.21 pattern on the crew side. Port the crew option
scorer to a firewall-clean shipped forward pass (`agents/tactical/learned/crew_forward.py`),
commit the owned-task-base measurement-tier weights as the loadable artifact (adoption
stays gated — this ships a SURFACE, not a champion), add the crew stamp, the factory entry,
and the `--agent-factory learned-crew` CLI arm. The crew wrapper carries what the impostor
wrapper never needed: override re-validation against the submission mask and the
emergency-uses bookkeeping via the meeting-concluded hook.

**Files in scope:**
- agents/tactical/learned/crew_forward.py (new) + agents/tactical/learned/factory.py (the crew factory + stamp) + the committed crew weights artifact under agents/tactical/learned/
- scripts/run_tournament.py (the `learned-crew` factory arm + stamp wiring)
- tests/training/test_learned_factory_acceptance.py (the crew twin: Q4 bit-exact gate vs `CrewOptionScorer`, determinism double-run, leak-mode scan)
- tests/scripts/test_run_tournament_candidate_artifact.py (the crew factory arm's guards)

**Files NOT in scope:**
- training/crew/ (the training-side scorer is the reference implementation — mirrored, never moved)
- agents/tactical/crewmate_policy.py (the scripted default is untouched; it remains the anchor and the default)

**Definition of done:**
- [ ] The shipped crew forward pass is bit-exact against `training.crew.scorer.CrewOptionScorer` over the committed weights on a committed-bytes decision sweep (the Q4 gate, crew edition), pure-Python, firewall-clean (no numpy/torch/engine imports — the existing firewall test extends).
- [ ] A `learned-crew` recording carries the crew stamp read back from bytes (never echoed), sha-verified against the committed sidecar; the default path is byte-identical with the factory unset (pinned).
- [ ] The wrapper re-validates every override against the submission mask and carries `emergency_uses_remaining` across meetings via the concluded hook, fixture-pinned including the mask-violation fail-loud case.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

Follow the `utility_es.py` → `forward.py` port line-for-line where possible: drop the
`engine.world`/`training` imports, freeze the weights as float-hex + sha sidecar, and gate
on bit-exactness rather than approximate equality (the forward pass is pure float64
arithmetic). The crew menu module already imports only firewall-legal packages.

**Integration risk:**

This touches production `agents/` and the recording CLI in one PR. The two guards that keep
it safe: the default path byte-identity pin (no factory ⇒ scripted crew, proven on committed
bytes), and the stamp conflation guard (a crew recording must never wear the impostor
champion's stamp — assert distinct `policy_id`/`weights_sha256` namespaces in the CLI arm).

**Public types introduced:**
- `agents.tactical.learned.crew_forward.LearnedCrewScorer`
- `agents.tactical.learned.factory.build_learned_crew_factory`
- `agents.tactical.learned.factory.LearnedCrewPolicyStamp`

**Ready-to-paste prompt:** `agent_prompts/task-18-7-crew-surface.md`

---

## Wave 1 — the meeting-layer package (gate-before-corpus)

### Task 18.8 — The roll-call round (turn-allocation surface, default-OFF)
**Branch:** `phase-18-roll-call-round`
**Depends on:** none (root)
**Section refs:** audits/audit-phase-18-planning.md §3.4 (the 53%-never-speak decomposition; the 2.13× turn-call cost); meetings/manager.py:952-1051 (the three-phase turn allocation), :1940-2010 (`_opt_in_eligible_ids`); audits/audit-phase-17-absence-gate.md Ruling 3(a) (the turn-taking routing this executes)
**Complexity:** Medium

The only surface that can reach the ratified 0.60 crew clause: a flag-gated roll-call round
after the reactive chain — one turn per living player who has not yet spoken, asked for a
structured whereabouts placement (role-blind ask; what impostor templates DO with it is
18.10's separate arm). Default-OFF via an env-gated resolver (the `absence_prior_enabled`
pattern); OFF-path bytes provably identical. Cost honesty in the module docstring: +~3.1
turns/meeting at today's economy (496 → 1057 turn calls over the samples denominator),
~+36% meeting LLM calls — the number the gate and the 18.13 duration plan both quote.

**Files in scope:**
- meetings/manager.py (the round + the resolver)
- tests/meetings/test_manager.py (OFF-path byte-identity; ON-path allocation fixtures: who is asked, order determinism, living-only, no double-turns)

**Files NOT in scope:**
- meetings/transcript.py (18.9's region)
- agents/strategic/prompts/ (18.10's region — the round uses the existing role-blind whereabouts ask surface)

**Definition of done:**
- [ ] With the flag OFF (default), committed-bytes reconstruction and all existing meeting fixtures are byte-identical (pinned); with it ON, every living non-speaker receives exactly one roll-call turn in deterministic order after the chain and before ballots, fixture-pinned.
- [ ] The resolver follows the graduated-lever conventions (env override for tests, default-OFF constant, one call site) and the docstring quotes the measured turn-cost arithmetic with its source.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

The round slots into `MeetingManager.run` between the chain termination and the ballot
phase; reuse the opt-in turn's prompt surface (the role-blind info-share branch already
asks for a whereabouts observation) so no template work happens here. Deadline handling
mirrors opt-in turns.

**Public types introduced:**
- `meetings.manager.roll_call_round_enabled`

**Ready-to-paste prompt:** `agent_prompts/task-18-8-roll-call-round.md`

### Task 18.9 — The endpoint-band whereabouts exemption (default-OFF) + counterfactual
**Branch:** `phase-18-endpoint-band-exemption`
**Depends on:** none (root)
**Section refs:** audits/audit-phase-18-planning.md §3.3 (why roll-call lies can never mint STRONG flags); meetings/transcript.py:529 (`WEAK_REASON_ENDPOINT_TICK`), :2262-2270 (the band application), :1927-1945 (the single-tick self-alibi indexing); audits/audit-phase-17-close.md §6 (the routed detector-band relaxation this executes)
**Complexity:** Medium

The lever that converts roll-call answers into conviction-economy currency: a flag-gated
exemption under which a single-tick whereabouts self-alibi contradicted by a first-hand
sighting mints a STRONG (interior-class) flag instead of being endpoint-banded to weak.
Default-OFF; OFF-path bytes identical. With the mechanism, the committed-bytes
counterfactual the gate reads: over the corpus and samples, how many recorded whereabouts
lies would have minted STRONG flags under the exemption, by liar role (today: 25 corpus
lies, 20 crew-authored / 5 impostor-authored, all weak) — the honest price of the change in
both directions (crew misremembering becomes ejectable evidence too).

**Files in scope:**
- meetings/transcript.py (the exemption + resolver)
- tests/meetings/test_contradictions.py (OFF-path byte-identity; ON-path STRONG-mint fixtures; the committed-bytes counterfactual pins by liar role)

**Files NOT in scope:**
- meetings/manager.py (18.8's region)
- eval/ (instruments read recorded flags; the counterfactual lives in the detector's own test pins)

**Definition of done:**
- [ ] With the flag OFF, `detect_contradictions` output over committed bytes is byte-identical (pinned); ON, a contradicted single-tick whereabouts claim mints a STRONG `alibi_vs_sighting` flag, fixture-pinned, while multi-tick alibi endpoint semantics are untouched.
- [ ] The committed-bytes counterfactual is pinned: the would-be STRONG-mint census over corpus + samples, split by liar role, quoted in the PR for the 18.11 gate memo.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

Scope the exemption to the degenerate `from_tick == to_tick` self-alibi class only — the
narrow-window weak reason and the two-source discipline for genuine multi-tick alibis do
not move. The counterfactual is a re-run of the current detector with the flag ON over
reconstructed transcripts, the 17.5 pin pattern.

**Public types introduced:**
- `meetings.transcript.whereabouts_interior_flags_enabled`

**Ready-to-paste prompt:** `agent_prompts/task-18-9-endpoint-band-exemption.md`

### Task 18.10 — The impostor-answer template arm (variant, default untouched)
**Branch:** `phase-18-impostor-answer-arm`
**Depends on:** none (root)
**Section refs:** audits/audit-phase-18-planning.md §3.4 (the structural refusal: hard-coded empty observations); agents/strategic/prompts/qwen3_6_27b/impostor_report.j2:8-12, 29-36, 76, 109-110 (the ladder history + the ≥44% self-flag caution) + accusation_round.j2:179, 198-200; agents/strategic/prompts/loader.py:155-157, 481-483 (role-selected routing); audits/audit-phase-17-absence-gate.md Ruling 3(d) (template changes re-read the bar on new bytes)
**Complexity:** Medium

The gate's highest-variance arm, built inert: a flag-selected impostor template variant in
which the impostor opening and reply ANSWER the whereabouts ask with a structured
self-placement (which the two-tier design lets be a lie — the tactical record is what it
is; the claim is the LLM's), instead of the hard-coded `"observations": []`. The cover
instruction ("every location detail you mention must be about OTHER players") is replaced in
the variant with plausible-self-account guidance. Default routing untouched — the variant
is reachable only through the flag, and the standing prompt-registry versioning applies.
This arm exists so the 18.11 probe can MEASURE what the ladder only feared: the impostor
self-flag rate and win cost when impostors must account for themselves.

**Files in scope:**
- agents/strategic/prompts/qwen3_6_27b/ (the variant templates)
- agents/strategic/prompts/loader.py (the flag-selected variant routing + resolver)
- tests/agents/ (routing fixtures: default path renders byte-identically; variant path renders the self-placement contract; version stamps distinguish the variant)

**Files NOT in scope:**
- meetings/ (18.8/18.9's regions)
- eval/funnel.py (its refusal-artifact note updates only at an adopting record)

**Definition of done:**
- [ ] With the flag OFF the rendered prompt set is byte-identical to the committed registry (pinned across the fixture sweep); ON, impostor opening and reply render the structured whereabouts self-placement ask and the variant's prompt-version stamp appears in recorded bytes.
- [ ] The variant's design rationale and the ladder's ≥44% self-flag caution are quoted in the template header (the house convention), naming the 18.11 bars that will judge it.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

The variant must keep the teammate firewall intact — a self-placement never places or
implicates the co-impostor (the §7.12 input-side guard). Follow the registry's version-bump
conventions so validity-gate provenance can tell variant bytes from default bytes.

**Public types introduced:**
- `agents.strategic.prompts.loader.impostor_roll_call_enabled`

**Ready-to-paste prompt:** `agent_prompts/task-18-10-impostor-answer-arm.md`

### Task 18.11 — THE MEETING-LAYER GATE: probe + ruling (operator ~8–9h + owner) + phase-doc surgery
**Branch:** `phase-18-meeting-layer-gate`
**Depends on:** 18.8, 18.9, 18.10
**Section refs:** audits/audit-phase-18-planning.md §3.4 + §7 (the package and its arms); audits/audit-phase-17-absence-gate.md (the ratified 0.20/0.60 bar + Ruling 3; the gate-with-surgery precedent); tasks/phase-17.md 17.7 (the memo-then-ruling shape); the 18.8/18.9/18.10 counterfactual pins (the offline evidence)
**Complexity:** Integration

The phase's substrate decision, made on evidence. Operator leg: record two probe sets on
the real path at 25 seeds 9p2i each — FULL (roll-call round + endpoint exemption +
impostor-answer variant ON) and CREW-ONLY (round + exemption ON, impostor templates
default) — ~8–9 h total at 2 workers, working artifacts outside the tree, measurements
committed. Memo leg: assemble `audits/audit-phase-18-meeting-gate.md` quoting the probe
cells and the Wave-1 offline counterfactuals against the PRE-REGISTERED bars: (a) crew
roll-call coverage on the probe ≥ **0.60** (the ratified crew clause, measured live); (b)
the absence counterfactual re-run on probe bytes reads new-over-gate ≤ **0.20** (the
ratified ceiling); (c) the impostor-answer arm ships only if probe impostor win ≥ **0.20**
(not annihilated; FSM comparator 0.36) AND the STRONG self-flag rate ≤ **0.25** of answered
impostor roll-calls; (d) the vent widening re-ruled with the package (the 17.7 Ruling 2
HOLD travels here). The owner rules **FULL / CREW-ONLY / NONE**; absence-prior graduation
rides the ruling per the ratified bar. Then the surgery in the ruled direction, exactly as
the Baseline-numbering block enumerates; prompts regenerate; validator green.

**Files in scope:**
- audits/audit-phase-18-meeting-gate.md (new: the memo + the recorded ruling)
- tasks/phase-18.md (the surgery + the banner note)
- agent_prompts/ (regenerated)

**Files NOT in scope:**
- meetings/ + agents/strategic/prompts/ (the mechanisms are built; the gate rules, never edits)
- replays/samples/ + replays/ml_corpus/ (no committed record at the gate — probe sets are working artifacts)

**Definition of done:**
- [ ] Both probe sets recorded 25/25 on the real Featherless path ($0, stamp-proven substrate flags for the arms under test), validity-gated, with every bar cell quoted beside its pre-registered threshold and the ruling recorded verbatim (FULL / CREW-ONLY / NONE, plus the vent-widening and absence-graduation components).
- [ ] The surgery is complete in the ruled direction (the Baseline-numbering block's enumeration): validator green, prompts regenerated, `scripts/compute_next_task.py --phase 18` consistent with the surviving DAG, no orphan references.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

Memo before ruling (the 15.18 shape). The 25-seed probe is deliberately underpowered for
fine effects — the bars are chosen so a fail is a >1σ read at n=25 (quote the two-proportion
z beside each verdict; the crew-coverage and self-flag cells have per-meeting denominators
well above 25). Price both directions honestly: what CREW-ONLY forfeits (no new impostor
lie material) and what FULL risks (the self-flag class).

**Integration risk:**

An operator + owner + surgery task in one PR, like 17.7 but with a recording leg. Keep the
probe recordings out of the tree (the finalist-eval separation discipline); if the ruling
stalls, the PR stays open with the memo complete and the DoD honest (the 17.14 PENDING
pattern) — never merge a ruling that has not happened.

**Ready-to-paste prompt:** `agent_prompts/task-18-11-meeting-layer-gate.md`

### Task 18.12 — The adopting record: baseline 6 (operator ~6–7h, $0)
**Branch:** `phase-18-baseline-6-record`
**Depends on:** 18.1, 18.2, 18.3, 18.11
**Section refs:** audits/audit-phase-16-close.md (the baseline-5 adopting-record runbook this reprises); eval/watchability.py:755-762 (the baseline-5 floor block the new block sits beside); audits/audit-phase-17-close.md §3 (the corpus canary anchors the pre-registration reads); the 18.11 ruling (which arms flip)
**Complexity:** Integration

The meeting-layer record. Flip the ruled arms to unconditional (graduation per the 16.17
slate pattern — the flags become always-on for the shipped arms; unshipped arms stay inert),
re-record `replays/samples/` (9p2i + 4p1i, 50 seeds each) at the new layer, pin the
baseline-6 floor block from the recorded bytes, execute the absence-prior graduation
component of the 18.11 ruling, and write the record audit with the §0 pre-registration
read against the phase-17 close's corpus-denominator anchors. Duration honesty: the
roll-call round adds ~36% meeting calls — plan ~6–7 h. Every byte-coupled committed pin
this record moves is re-pinned in the same PR.

**Files in scope:**
- meetings/manager.py (the ruled arms' graduation flips ONLY — mechanism bodies froze at Wave 1)
- meetings/transcript.py (same)
- agents/strategic/prompts/ (same)
- agents/memory/beliefs.py (the absence graduation component if ruled)
- replays/samples/9p2i/ + replays/samples/4p1i/ (the baseline-6 record)
- eval/watchability.py (the baseline-6 floor block)
- audits/audit-phase-18-baseline-6.md (new: the record audit)
- tests/eval/ (the byte-coupled committed-bytes re-pins this record moves, incl. the 18.1/18.2/18.3 instrument pins)
- tests/agents/ (the absence counterfactual + prompt-registry re-pins)
- tests/meetings/ (the graduation-flip re-pins)

**Files NOT in scope:**
- replays/ml_corpus/ (18.13's record)
- training/ (18.14 consumes; this task records)

**Definition of done:**
- [ ] Both samples sets recorded at the ruled layer, validity gate PASS (`--expected-model Qwen/Qwen3.6-27B --require-zero-cost`), byte-identical reconstruction under a bare environment, substrate flags in recorded bytes matching the ruling exactly.
- [ ] The baseline-6 floor block is pinned from these bytes with the derivation self-consistency check (referee PASS at exact floor equality on its own record), and the record audit quotes the funnel/V&J/deception-instrument before/after against baseline 5 with the §0 pre-registered canary bands on the corpus denominators.
- [ ] The absence-prior component of the ruling is executed (graduated per the ratified bar, or its stay-OFF restated with the probe cells named).
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

The 16.17 close-record runbook is the template (graduation flips + record + floor pins +
byte-coupled re-pin sweep in one PR). Record 4p1i first to validate the pipeline, then the
9p2i leg. The Q5 provenance convention applies (recording sha back-filled on merge; the tag
arm may need the owner's machine).

**Integration risk:**

The widest byte-coupled re-pin sweep of the phase: every committed-bytes pin over
`replays/samples/` moves (funnel, V&J, conversion partition, absence counterfactual,
deception instruments, kill-craft). Budget the re-pin pass explicitly and run the full
suite before the record commit is cut — a stale pin discovered post-merge is a two-artifact
seam.

**Ready-to-paste prompt:** `agent_prompts/task-18-12-baseline-6-record.md`

### Task 18.13 — The corpus re-record at baseline 6 (operator ~18–20h, $0)
**Branch:** `phase-18-corpus-rerecord`
**Depends on:** 18.12
**Section refs:** scripts/record_ml_corpus.sh (the pin block moves to the baseline-6 substrate); replays/ml_corpus/README.md; tasks/phase-17.md 17.9 (the runbook this reprises); audits/audit-phase-17-close.md §5 (the staleness rule this discharges)
**Complexity:** Integration

The long pole, re-run at the adopted layer: 150-game 9p2i + 50-game 4p1i, seeds 1000+, the
same `seed % 5` split rule, freeze-path staging, MANIFEST provenance exact. Duration
honesty: baseline-5 ran ~14–15 h and the roll-call round adds ~36% meeting calls — plan
**~18–20 h** with checkpoint-push (commit-and-push completed seed ranges so a container
reclaim never loses a leg). The README refreshes end-to-end; the Q3 canary-denominator
restoration re-states (the corpus is again canonical from this record; the 18.12 samples are
the continuity anchor).

**Files in scope:**
- replays/ml_corpus/9p2i/ + replays/ml_corpus/4p1i/ (the re-recorded bytes + MANIFESTs + splits.json)
- replays/ml_corpus/README.md (full substrate refresh)
- scripts/record_ml_corpus.sh (the substrate pin flip + duration note)
- tests/training/ + tests/scripts/ (corpus-derived re-pins ONLY — the surrogate/bar re-derivations are 18.14's)

**Files NOT in scope:**
- replays/samples/ (18.12's record — pinned)
- training/ (18.14/18.15 consume)

**Definition of done:**
- [ ] Both corpus sets recorded at baseline 6, validity gate PASS with exact provenance (model, versions, the ruled substrate flags, $0), byte-identical reconstruction, splits regenerated non-degenerate under the same rule.
- [ ] The README and the recorder script agree on every operative line (substrate, env, duration), the Q3 restoration is stated, and the conversion/deception-instrument reads over the new corpus are quoted in the PR.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

The 17.9 runbook verbatim plus the checkpoint-push discipline (an ~20 h session WILL span
reclaim risk). 4p1i first, then the 9p2i long leg sharded across 2 staggered workers with
jittered backoff and `AILIBI_SEED_MAX_ATTEMPTS=8`.

**Integration risk:**

The mixed-date MANIFEST precedent applies across a multi-day session. Corpus-pinned
training tests move; re-pin only what this record moves and leave the bar/surrogate
constants to 18.14 (the 17.9/17.11 split, kept).

**Ready-to-paste prompt:** `agent_prompts/task-18-13-corpus-rerecord.md`

### Task 18.14 — Surrogate re-ground + re-verdict + selection-bar re-pins (baseline 6)
**Branch:** `phase-18-surrogate-bars-reground`
**Depends on:** 18.13
**Section refs:** training/reports/report-ballot-surrogate.md §8 (the executed re-grounding recipe); training/surrogate/ (the 17.10 machinery, re-run); training/bakeoff/harness.py:174-181 (`GOODHART_9P2I_BASELINE`) + `BAKEOFF_BASELINE_ID`; tasks/phase-17.md 17.10 + 17.11 (the two contracts this combines)
**Complexity:** Medium

One turn of the standing re-grounding crank at the new substrate: re-validate the belief
walk on the baseline-6 corpus BEFORE trusting any fit, re-fit the ballot predictor
(6-feature fence kept — locked decision 1 rejected widening it), re-derive the staleness
cap under the ~143× rule, re-state the GO/NO-GO on the same population-relative bar, and
flip the selection constants (`BAKEOFF_BASELINE_ID` → `"baseline-6"`, the Goodhart
fake-path baseline re-measured, the report refreshed). The 17.10 honesty discipline
travels: the decision-channel diagnosis is re-stated on the new economy, whichever way it
reads.

**Files in scope:**
- training/artifacts/surrogate/ (weights + sidecar + max-uses, re-fit)
- training/reports/report-ballot-surrogate.md (the baseline-6 reading)
- training/bakeoff/harness.py (the two constant blocks ONLY)
- tests/training/ (surrogate + bar re-pins)

**Files NOT in scope:**
- training/surrogate/*.py (the machinery re-runs; it does not change)
- eval/watchability.py (floors pinned at 18.12)

**Definition of done:**
- [ ] Walk re-validation (fold fidelity 0 mismatches; J1 divergence re-measured) recorded BEFORE the fit; the re-fit artifact + re-derived cap committed together with the re-stated verdict on the unchanged bar; coerced-SKIP census quoted.
- [ ] `BAKEOFF_BASELINE_ID` and the Goodhart baseline constants read baseline-6, with the fake-path ceiling re-measured, and every dependent pin green.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

The §8 recipe is executable as written; the only judgment call is the verdict prose — state
the skip/eject economy of the new corpus plainly (a roll-call-round economy may no longer be
skip-majority, which would put axis 3 back at full strength; that is a finding, not a
problem).

**Ready-to-paste prompt:** `agent_prompts/task-18-14-surrogate-bars-reground.md`

---

## Wave 2 — the training signal

### Task 18.15 — The conviction-economy model: dataset, fit, fidelity, GO bar
**Branch:** `phase-18-conviction-model`
**Depends on:** 18.13
**Section refs:** audits/audit-phase-18-planning.md §2.3 (the design + the honesty argument); training/surrogate/fidelity.py:213-243, 452-487 (the live-reconstructable channels + the voice-driven-share ceiling); training/surrogate/dataset.py (the table machinery to mirror); training/surrogate/runner.py:177-192 (what run_meeting-time state contains)
**Complexity:** Integration

The training-signal instrument the phase was chartered around: a model
`g(pre-meeting typed state) → (expected contradiction flags minted, expected
testimony-backed conversion)` fit on the corpus's recorded triples, over ONLY channels a
training-time runner reconstructs at `run_meeting` time (vent-witness records, first-hand
sightings, body-proximity/seen-at-kill, belief scalars — never transcript-derived
features). Deterministic numpy fit, float-hex + sha artifact, its own staleness cap under
the ~143× rule, and a pre-stated population-relative GO bar: **held-out per-meeting
flag-count rank correlation (Spearman) ≥ 0.5 AND conversion-prediction fidelity ≥ 0.75 ×
(1 − voice_driven_share measured on the same population)** — with NO-GO pre-committed to
diagnostic-only (the fitness term does not ship, 18.16 integrates the pre-screen only as
advisory). If the 18.11 ruling was NONE (surgery path), this task binds to the standing
baseline-5 corpus and the contract's numbers re-read there.

**Files in scope:**
- training/conviction/ (new package: dataset.py, model.py, fidelity.py)
- training/artifacts/conviction/ (weights + sidecar + max-uses)
- training/reports/report-conviction-model.md (new)
- tests/training/test_conviction_model.py

**Files NOT in scope:**
- training/surrogate/ (independent artifact, untouched — the designer ruling)
- training/bakeoff/harness.py (18.16's integration)

**Definition of done:**
- [ ] The dataset walk re-validates against production folds before any fit (the 17.10 discipline: 0 raw mismatches, divergences measured and recorded); the fit is deterministic with the platform caveat documented; the artifact round-trips byte-stably.
- [ ] The verdict is taken on the FIRST held-out evaluation against the pre-stated bar, with the honest ceiling (voice-driven share) quoted as the structural denominator and the GO/NO-GO consequence machine-readable for 18.16.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

Mirror the surrogate package's shapes (table builder honoring `splits.json`, fidelity
report, `decide_*` verdict function, sha-keyed use counter) so the staleness/re-grounding
doctrine applies mechanically. The feature fence is the live-parity argument re-run: every
input must be derivable from `(trigger, state, agents)` at meeting time — write that test
(feature-by-feature provenance assertions), not just the docstring.

**Integration risk:**

The model's labels (flags minted, backed conversion) are exactly the quantities the referee
gates — the Goodhart-adjacent seam of the phase. The two structural guards: the model never
reads `eval/watchability.py` (AST-firewalled like the entrants), and 18.18 re-runs the
Goodhart probe with the conviction term live before any campaign selection leans on it.

**Public types introduced:**
- `training.conviction.model.ConvictionEconomyModel`
- `training.conviction.dataset.build_conviction_table`
- `training.conviction.fidelity.decide_conviction_go`

**Ready-to-paste prompt:** `agent_prompts/task-18-15-conviction-model.md`

### Task 18.16 — Fitness-term + referee pre-screen integration
**Branch:** `phase-18-conviction-integration`
**Depends on:** 18.14, 18.15
**Section refs:** training/bakeoff/harness.py:569-590 (`inner_episode_fitness` + the gate/reward boundary comment at :582-585); audits/audit-phase-18-planning.md §2.3 (the two consumption modes); the 18.15 verdict (which modes are live)
**Complexity:** Medium

Wire the conviction model into the bake-off under the GO verdict: an additive
`conviction_weight × predicted-supply` term in the inner fitness (side-specific: the
impostor term prices surviving a convicting economy, the crew term prices supplying one),
and a pre-screen hook the campaign driver calls before spending real-path evals. Under
NO-GO the term is structurally absent (not zero-weighted) and the pre-screen is
advisory-labeled. The gate/reward boundary comment extends to name the new term's
provenance; use-counting flows through the model's own sha-keyed counter.

**Files in scope:**
- training/bakeoff/harness.py (the term + the pre-screen seam + the boundary comment)
- tests/training/test_bakeoff_harness.py (term-provenance fixtures; NO-GO structural absence; counter threading; the AST firewall extended to training/conviction)

**Files NOT in scope:**
- training/conviction/ (consumed via its public seam)
- training/rewards.py (the dense terms do not move — this is bake-off-level fitness composition)

**Definition of done:**
- [ ] With a GO artifact the inner fitness carries the term for both sides with its weight named in the row metadata; with NO-GO the term is absent and rows say so; both fixture-pinned.
- [ ] The pre-screen returns a machine-readable predicted-floors verdict consumed by tests, metered against the conviction counter, and documented as advisory-only under NO-GO.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

The anchor-CE penalty's integration is the template (a named, weighted, metadata-carried
term). Keep the default `conviction_weight` conservative (≤ the anchor weight) — the λ/
weight tuning belongs to the 18.24 campaign protocol, not this integration.

**Public types introduced:**
- `training.bakeoff.harness.conviction_prescreen`

**Ready-to-paste prompt:** `agent_prompts/task-18-16-conviction-integration.md`

### Task 18.17 — The real-path re-rank recorder (selection designs B/C, productized)
**Branch:** `phase-18-realpath-rerank`
**Depends on:** none (root)
**Section refs:** audits/audit-phase-18-planning.md §2.2 (the cost table; design B ~2 h/gen, design C ~21 h/run); eval/balance_eval.py:241 (the `meeting_runner_factory` seam); training/bakeoff/es.py:154 (`champion_trace`); scripts/run_tournament.py --candidate-artifact (the 17.14 recorder whose stamp discipline this inherits); orchestrator/game.py:397-399 (deadline-free headless meetings — the timeout gap)
**Complexity:** Medium

Productize the two real-path selection loops the training-signal decision adopted: (B)
per-generation top-K re-rank — given K candidate genomes and a seed list, record each on the
real provider path, score through the committed CLIs, and emit a machine-readable ranking
row; (C) champion-trace re-rank — the same over an `ESResult.champion_trace`. Library-first
(a `training/realpath.py` module the 18.21 driver calls), with per-candidate provenance
stamps read back from bytes (the 17.14 discipline), per-seed crash-retry, and the missing
wall-clock guard: a per-meeting timeout wrapping the runner so a hung provider fails the
seed loudly instead of stalling the loop (headless meetings are deadline-free today).
Recordings are working artifacts outside the tree; the committed truth is the ranking jsonl.

**Files in scope:**
- training/realpath.py (new)
- tests/training/test_realpath.py (fake-provider protocol tests: ranking rows, stamp read-back, timeout fail-loud, retry budget)

**Files NOT in scope:**
- scripts/run_tournament.py (the CLI recorder is 17.14's; this is the library loop — no CLI change)
- training/bakeoff/es.py + harness.py (consumed, never edited)

**Definition of done:**
- [ ] The re-rank loop records K candidates × N seeds through the real seam (exercised in tests via the fake provider), scores each with the committed validity/core/watchability CLIs' library entry points, and emits ranking rows carrying the full candidate stamp read back from bytes plus per-seed retry/timeout telemetry.
- [ ] A hung meeting (simulated in tests) fails that seed loudly within the configured timeout and the retry budget re-records it; nothing hangs the loop.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

The provider-nondeterminism honesty note belongs in the module docstring: real-path ranks
are selection signal, not fitness — two runs of the same genome may differ, which selection
tolerates and the ES fitness contract does not. Never write these scores into an ES fitness
channel.

**Public types introduced:**
- `training.realpath.RealPathRerankResult`
- `training.realpath.run_realpath_rerank`

**Ready-to-paste prompt:** `agent_prompts/task-18-17-realpath-rerank.md`


### Task 18.18 — The Goodhart re-probe: conviction path + the carried 4p1i exploit
**Branch:** `phase-18-goodhart-reprobe`
**Depends on:** 18.16
**Section refs:** training/bakeoff/goodhart.py (the probe machinery); audits/audit-phase-17-close.md §6 (the carried `d4-contest-farming` finding: +61.8% on the 4p1i reference roster — re-probe before any 4p1i-scored selection); training/reports/report-goodhart-probe.md (the standing report this extends); the standing rule: the probe re-runs when the training-signal role grows
**Complexity:** Medium

The training-signal role grew (the conviction term + pre-screen), so the probe re-runs
BEFORE any campaign selection leans on the new signal: the forced-lever sweep with the
conviction term live (can a lever family launder predicted-supply into fitness without
supplying real evidence?), the composed-gate laundering check, and the carried
`d4-contest-farming` 4p1i exploit re-probed at the current substrate. Findings recorded
with the materiality bar; any exploitable seam becomes a named blocker for 18.24's
protocol, never a silent caveat.

**Files in scope:**
- training/bakeoff/goodhart.py (the conviction-path probe arms)
- training/reports/report-goodhart-probe.md (the re-probe reading)
- tests/training/test_goodhart_probe.py (re-pins + the new arms' fixtures)

**Files NOT in scope:**
- training/conviction/ + training/bakeoff/harness.py (probed, never edited)

**Definition of done:**
- [ ] The probe reports the conviction-term delta per forced lever beside the standing bars, the composed-gate verdict, and the 4p1i `d4-contest-farming` re-read, each with its materiality arithmetic; any above-bar finding is named in the report's blocker section.
- [ ] Conviction-model use during the probe is metered and quoted (the consumption discipline).
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

The probe's delta convention is unchanged; the new question is narrow — does the conviction
TERM (a prediction) diverge from the recorded REALITY (flags in bytes) under adversarial
levers, and by how much. Report predicted-vs-actual side by side per lever.

**Ready-to-paste prompt:** `agent_prompts/task-18-18-goodhart-reprobe.md`

---

## Wave 3 — co-evolution

### Task 18.19 — Dual-role co-evo rollout + the two-identity stamp
**Branch:** `phase-18-coevo-rollout`
**Depends on:** 18.7, 18.16
**Section refs:** audits/audit-phase-18-planning.md §4 (#8) + the dive finding it cites (`rollout_candidate` hardwires the opposing side to the scripted FSM — harness.py:426-427, 490-496; scorer.py:799-806); training/bakeoff/harness.py:280-311 (`BakeoffPolicy`, the shared shape); orchestrator/replay.py (the stamp schema the crew stamp extends)
**Complexity:** Integration

The seam co-evolution has never had: a role-dispatching rollout in which EACH side is
independently the scripted FSM, a live candidate, or a frozen learned artifact — and an
honest two-identity provenance story: an additive crew-policy stamp beside the existing
`tactical_policy` stamp on recorded games, each read back from bytes, sha-verified, never
conflated. `rollout_coevo` scores both sides' fitness from one rollout (both reward sides
exist already); the recording path extends `scripts/run_tournament.py` with a
`--crew-artifact` arm mirroring `--candidate-artifact`, mutual-exclusion-guarded against
the single-side flags.

**Files in scope:**
- training/coevo/__init__.py + training/coevo/factory.py + training/coevo/rollout.py (new)
- orchestrator/replay.py (the additive crew stamp record + reader)
- scripts/run_tournament.py (the `--crew-artifact` arm + dual-stamp wiring)
- tests/training/test_coevo_rollout.py + tests/scripts/test_run_tournament_candidate_artifact.py (the dual-stamp guards)

**Files NOT in scope:**
- training/bakeoff/harness.py (its wrappers are imported/mirrored, never rewired — the single-side paths stay byte-identical)
- agents/tactical/learned/ (18.7 shipped the surface; consumed here)

**Definition of done:**
- [ ] A rollout with learned policies on BOTH sides runs deterministically on the fake path, yields both sides' fitness from one trace, and a recorded eval carries both stamps read back from bytes with distinct sha-verified identities; every single-side path (existing flags, no factory) is byte-identical to before (pinned).
- [ ] Conflation is structurally impossible: a crew artifact in the impostor slot (or vice versa) fails loud before any game runs, fixture-pinned; the stamp reader round-trips games with zero, one, or two stamps.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

Both existing wrappers (`_CandidateAgent`, `_CrewCandidateAgent`) already share the
`BakeoffPolicy` evaluate shape — the dual factory is a role branch over two of them, not a
new agent class. The stamp extension is additive on the replay schema (a game with no crew
stamp parses exactly as before — the 15.9 compatibility discipline).

**Integration risk:**

`orchestrator/replay.py` is byte-adjacent to every committed set: the additive field must
leave all committed replays parsing byte-identically (round-trip pins over the samples +
corpus). The CLI arm compounds with 17.14's guards — extend its test file rather than
forking a second guard suite.

**Public types introduced:**
- `training.coevo.factory.build_coevo_factory`
- `training.coevo.rollout.rollout_coevo`
- `orchestrator.replay.CrewTacticalPolicyStamp`

**Ready-to-paste prompt:** `agent_prompts/task-18-19-coevo-rollout.md`

### Task 18.20 — The hall of fame + PFSP-lite opponent sampler
**Branch:** `phase-18-hall-of-fame`
**Depends on:** 18.6, 18.19
**Section refs:** audits/audit-phase-18-planning.md §4 (#8) + §6 (the AlphaStar/PSRO transfer: frozen pool + hardness-weighted sampling); training/bakeoff/harness.py:843-868 (the artifact layout); training/surrogate/runner.py:88-131 (the sha-keyed use-counter doctrine the opponent bookkeeping mirrors); the 18.6 cell artifacts (a seed source)
**Complexity:** Medium

The frozen opponent pool: a `hall_of_fame.json`-indexed artifact store
(`training/artifacts/coevo/<side>/gen-<N>/`) holding frozen genomes with provenance
(generation, sha, trained-against sha), a deterministic PFSP-lite sampler (opponents
weighted toward currently-hard members — hardness from the exact deterministic payoff
entries, re-normalized each generation, seeded RNG), ingestion from the 18.6 MAP-Elites
cells as behaviorally-diverse founders, and opponent-staleness bookkeeping (a capped
generation count per frozen opponent before refresh, sha-keyed). Pure numpy/stdlib;
everything reloadable bit-exactly.

**Files in scope:**
- training/coevo/hall_of_fame.py (new)
- tests/training/test_hall_of_fame.py

**Files NOT in scope:**
- training/coevo/factory.py + rollout.py (18.19's modules — consumed)
- training/bakeoff/map_elites.py (its cell artifacts are read via 18.6's public loader)

**Definition of done:**
- [ ] The store round-trips frozen genomes with sha verification (fail-loud on drift), the index carries full provenance, and MAP-Elites cells ingest as founders through 18.6's loader.
- [ ] The sampler is deterministic under its seed, its hardness weighting is computed from supplied payoff entries (no hidden state), and the staleness cap raises loudly at exhaustion — all fixture-pinned.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

Deterministic evals make the payoff matrix exact — the sampler needs no win-rate estimation
machinery, just the recorded per-pair fitness cells. Keep the weighting function small and
documented (the survey's lesson: a ≤30-member pool with win-weighted sampling captures the
benefit; resist meta-Nash solvers).

**Public types introduced:**
- `training.coevo.hall_of_fame.HallOfFame`
- `training.coevo.hall_of_fame.sample_opponents`

**Ready-to-paste prompt:** `agent_prompts/task-18-20-hall-of-fame.md`

### Task 18.21 — The alternating-freeze driver + stabilizers
**Branch:** `phase-18-alternating-driver`
**Depends on:** 18.20
**Section refs:** audits/audit-phase-18-planning.md §4 (#8) + §6 (the stabilizer kit); audits/audit-phase-15-pause.md decision 4 (the barred naive form; the entry condition this satisfies); experiments/lab/ml_spike/fo2_coevolution.py (the absolute-anchor cycling detector precedent); training/coevo/ (18.19/18.20's seams)
**Complexity:** Integration

The campaign engine: an alternating-freeze loop — evolve one side's population (the
standing ES) against a PFSP-sampled slate of frozen opponents while the other side is
frozen, freeze the champion into the hall of fame, swap sides, repeat — with the full
stabilizer instrumentation emitted per generation: the absolute anchor benchmark (champion
vs scripted FSM, both directions — the cycling detector: oscillating co-matchup with a flat
anchor = cycling, monotone anchor = progress), a per-side short-horizon exploiter probe (a
small ES bred purely to beat the current champion; its found exploits join the hall of
fame), and the anchor-CE term retained toward the FIXED scripted FSM on both sides (never
toward the moving opponent). One side moves at a time, always — the barred simultaneous
form is structurally unreachable. Deterministic end-to-end on the fake/surrogate path;
machine-readable campaign rows.

**Files in scope:**
- training/coevo/driver.py (new)
- tests/training/test_coevo_driver.py (a miniature two-swap campaign on tiny budgets: freeze/swap mechanics, HoF growth, benchmark emission, exploiter integration, determinism digest)

**Files NOT in scope:**
- training/coevo/hall_of_fame.py + factory.py + rollout.py (consumed)
- training/bakeoff/es.py (the optimizer is imported unchanged)

**Definition of done:**
- [ ] A miniature campaign (2 swaps, tiny budgets) runs deterministically twice with identical digests, grows the hall of fame with full provenance, emits the absolute-benchmark and exploiter rows per generation, and never updates both sides in one step (structurally asserted).
- [ ] The campaign row schema carries everything 18.24's report needs (per-gen fitness, anchor benchmarks both directions, opponent slate shas, exploiter outcomes, conviction/surrogate consumption).
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

The driver owns ALL the meters (surrogate + conviction use counters threaded once,
cumulative) — a campaign that exhausts a cap must stop loudly at a swap boundary, which is
the natural re-grounding point. The exploiter probe is the standing ES at a tiny budget
(e.g. 5×6) with fitness = beat-the-champion only.

**Integration risk:**

This is where compounding budgets can silently explode: population × generations × seeds ×
opponent-slate size. The driver must compute and log its total game count up front and
refuse a configuration whose fake-path game count exceeds a stated ceiling without an
explicit override flag — no accidental week-long runs.

**Public types introduced:**
- `training.coevo.driver.run_alternating_freeze`
- `training.coevo.driver.CoevoCampaignRow`

**Ready-to-paste prompt:** `agent_prompts/task-18-21-alternating-driver.md`

### Task 18.22 — Encoder v3 + within-kind target resolution (free-policy family)
**Branch:** `phase-18-encoder-v3`
**Depends on:** 18.19
**Section refs:** audits/audit-phase-18-planning.md §4 (#14) + the dive findings (the PR #242 lexical-tie limit at policy_es.py:214-221; encoder gaps: witness-awareness, meeting-history, claimed-location); agents/tactical/features.py:88, 125-143, 176-187 (the versioned layout + golden pins); training/bakeoff/policy_es.py:97-106 (input-dim auto-resize)
**Complexity:** Medium

The perception upgrade locked decision 5 sequenced here: an additive, versioned encoder v3
(the v2 layout untouched and still pinned) adding the deception-relevant channels the dive
priced — per-target witness-co-presence at decision time, meeting-history scalars (meetings
survived, prior ejection outcomes) fed from the meeting-concluded hook, and per-player
last-seen recency the belief slots do not carry — plus within-kind target resolution for
the masked head (per-target KILL scoring, closing the lexical-tie limit). Firewall-legal
throughout (agent-own packet + memory only); pure-Python; the golden layout test extends to
v3.

**Files in scope:**
- agents/tactical/features.py (the additive v3 encoder + golden layout)
- training/bakeoff/policy_es.py (the per-target head + v3 selection)
- tests/training/test_bakeoff_harness.py (encoder/head fixtures ONLY — the v3 golden pins, mask/tie fixtures)

**Files NOT in scope:**
- agents/tactical/learned/ (the shipping champion is v1-featured; untouched)
- training/bakeoff/utility_es.py (the menu family does not move)

**Definition of done:**
- [ ] Encoder v2 output is byte-identical everywhere (golden pins unchanged); v3 is additive, versioned, firewall-legal (no engine/other-agent state — the leak-style provenance test extends), with its layout golden-pinned.
- [ ] The per-target head resolves within-kind ties by learned score (lexical fallback only on exact score ties), fixture-pinned including the masked-legality invariant; a v3-featured policy-es trains end-to-end on the miniature budget.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

Meeting-history needs a small memory-side channel populated from the concluded hook before
the encoder can read it — keep that channel in the agent's own memory store (firewall-clean
by construction) and quantize everything through the established integer-grid helpers (the
§6.3 residue hazard).

**Public types introduced:**
- `agents.tactical.features.encode_features_v3`

**Ready-to-paste prompt:** `agent_prompts/task-18-22-encoder-v3.md`

### Task 18.23 — Scenario staging: state injection + the skill-scenario library
**Branch:** `phase-18-scenario-staging`
**Depends on:** 18.16
**Section refs:** audits/audit-phase-18-planning.md §4 (#12) + the dive findings (both entry points hardwire `seed_initial_state` — orchestrator/game.py:1495-1501, 1556; `WorldState` hand-construction precedent at tests/training/test_env.py:531-543; dense terms score truncated episodes — training/rewards.py:250-256); orchestrator/seeder.py:29-133
**Complexity:** Integration

The training-grounds instrument: an `initial_state` injection seam on the headless game
(bypassing `seed_initial_state`, with the rng-snapshot discipline that keeps injected
episodes deterministic and hash-coherent), and a scenario library of constructed mid-game
skill situations with per-scenario dense fitness from tactical facts only — first four:
kill-with-witness-nearby-then-survive-the-meeting, vent-unseen-under-patrol,
force-parity-endgame, body-discovery-latency. Scenario episodes are truncated by
construction and score through the dense terms (never `compute_shaped_reward`'s terminal
gate); scenarios feed FITNESS pressure, and the standing gates/referee never move. The
campaign driver may mix scenario legs into a side's evolution; watchability quantities
never appear in scenario fitness.

**Files in scope:**
- orchestrator/game.py (the additive `initial_state` seam)
- training/env.py (the env-side plumbing + no-replay path integration)
- training/scenarios.py (new: builders + per-scenario fitness)
- tests/training/test_scenarios.py + tests/training/test_env.py (the seam's determinism + hash-coherence fixtures)

**Files NOT in scope:**
- orchestrator/seeder.py (bypassed, never edited)
- training/rewards.py (dense terms consumed as-is)
- engine/ (already accepts any valid state)

**Definition of done:**
- [ ] An injected-state episode runs deterministically (same scenario + seed ⇒ identical digest twice), its rng snapshot is canonical, and the default seeded path is byte-identical everywhere with the seam unused (pinned across the replay/recording suites).
- [ ] All four scenarios construct valid states (engine-accepted, hash-coherent), each with a documented fitness definition from tactical facts, and a miniature ES leg on one scenario runs end-to-end in tests.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

The injection must ride the no-replay live-assembly path (reconstruction verifies recorded
hashes an injected episode does not have). Scenario states set `rng_state` to a canonical
`EngineRng.from_seed(...)` snapshot; `advance_tick` is then a pure function and the
determinism story is inherited, not re-invented.

**Integration risk:**

`orchestrator/game.py` is the most byte-adjacent file in the tree; the seam must be
provably inert when unused (the full replay/recording byte-identity suites are the gate —
run them before and after). Scenario fitness definitions are the Goodhart-adjacent part:
each must name what it deliberately does NOT reward (e.g. discovery-latency must not reward
meeting suppression — the FO-2 lesson).

**Public types introduced:**
- `training.scenarios.ScenarioSpec`
- `training.scenarios.build_scenario_state`

**Ready-to-paste prompt:** `agent_prompts/task-18-23-scenario-staging.md`

### Task 18.24 — THE IMPOSTOR CAMPAIGN (operator, multi-session)
**Branch:** `phase-18-impostor-campaign`
**Depends on:** 18.17, 18.21, 18.22
**Section refs:** audits/audit-phase-18-planning.md §7 (the campaign shape); the 18.21 driver + 18.20 hall of fame + 18.16 fitness stack + 18.17 real-path re-rank + 18.5 anchor-study candidates; audits/audit-phase-17-close.md §1.3 (the flip bar the campaign aims at)
**Complexity:** Integration

The phase's first live campaign: evolve the impostor side against the frozen scripted crew
plus hall-of-fame opponents (as the crew side gains members, later swaps use them),
entrants seeded from the committed champion, the 18.5 anchor-study candidates, and (for the
free-policy family) 18.22's v3 features — inner fitness on the fake/surrogate path with the
conviction term, per-generation real-path top-K re-ranks (18.17, ~2 h/gen), pre-screen
before every real spend, all meters quoted. Report: campaign rows, the cycling-detector
reading, per-entrant floor-sensitivity on the real re-ranks, the emergence-instrument
sweeps (18.1/18.2/18.3) over the campaign's real-path recordings against the 18.4 memo's
cells, and the named finalists for 18.26. Operator shape: fake-path legs are hours;
real-path legs total ~40–50 h spread across sessions — checkpoint-push per generation.

**Files in scope:**
- training/reports/report-impostor-campaign.md (new) + training/reports/results-impostor-campaign.jsonl (new)
- training/artifacts/coevo/ (the campaign's frozen artifacts, via the driver)
- tests/training/test_coevo_driver.py (campaign-row pins from the committed rows ONLY)

**Files NOT in scope:**
- training/coevo/*.py + training/bakeoff/ (the machinery froze at Wave 3 — a campaign is a run, not a redesign)
- agents/tactical/learned/ (no champion swap here — 18.27's evidence decides)

**Definition of done:**
- [ ] The campaign report carries every generation's row (fitness, anchor benchmarks both directions, opponent slates, exploiter outcomes, meter consumption), the cycling-detector verdict stated against the pre-registered signature, and the real-path re-rank tables with stamp proofs and floor sensitivity per the 17.14 discipline.
- [ ] The emergence instruments are swept over the campaign's real-path recordings with deltas quoted against the 18.4 baseline cells (claims deferred to 18.27 — this task reports, never rules), and the finalists for 18.26 are named with their artifacts frozen.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

Run the standing runbook per real-path leg (2 staggered workers, jittered backoff,
`AILIBI_SEED_MAX_ATTEMPTS=8`, per-seed atomic staging, checkpoint-push). If a meter (cap)
exhausts mid-campaign, the swap-boundary stop is the design working — re-ground and
resume, and say so in the report.

**Integration risk:**

The first run composes every new subsystem (conviction term, pre-screen, HoF sampling,
driver, real re-ranks) — expect integration findings. The discipline: a defect found
mid-campaign becomes a routed contract or an in-report finding; the campaign never patches
machinery silently (merge-equals-done applies to the tools it runs on).

**Ready-to-paste prompt:** `agent_prompts/task-18-24-impostor-campaign.md`

### Task 18.25 — THE CREW CAMPAIGN (operator)
**Branch:** `phase-18-crew-campaign`
**Depends on:** 18.24
**Section refs:** the 18.24 report (the frozen impostor champions this campaign trains against); training/crew/ (the crew bases); audits/audit-phase-18-planning.md §4 (#8, the impostor-first rationale) + the crew-fitness finding (correct_reports dead on non-convicting paths — the conviction term is the counterweight)
**Complexity:** Integration

The counter-adaptation half: evolve the crew side (both bases: general + owned-task)
against the frozen impostor campaign champions + hall of fame, with the conviction-supply
term giving crew fitness the conviction-economy gradient the fake path denies it, the
interrupt-preserving constraint kept (the 15.22 guard — starvation stays unreachable), and
real-path re-ranks per generation. Report mirrors 18.24 (rows, cycling detector, floor
sensitivity, emergence sweeps — crew-side instruments emphasized: roll-call coverage,
conversion, counter-adaptation evidence against the specific impostor champions). Crew
champion adoption is NOT this task's call: candidates route to 18.26/18.27 evidence.

**Files in scope:**
- training/reports/report-crew-campaign.md (new) + training/reports/results-crew-campaign.jsonl (new)
- training/artifacts/coevo/ (crew-side frozen artifacts, via the driver; disjoint gen dirs from 18.24's — the store layout separates sides)
- tests/training/test_coevo_driver.py (crew-campaign row pins ONLY — additive to 18.24's region)

**Files NOT in scope:**
- training/coevo/*.py + training/crew/*.py (runs, not redesigns)
- agents/tactical/learned/ (adoption is 18.27's evidence question)

**Definition of done:**
- [ ] The campaign report carries the full row/benchmark/meter discipline, the counter-adaptation reading (does trained crew close the frozen champion's win edge, and through which instrument channels), and the real-path re-rank tables with stamp proofs.
- [ ] The gate-validity discipline holds throughout (no starvation-family candidate survives selection; validity-gate columns quoted per entrant), and crew finalists (if any clear the bars) are named for 18.26.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

The interesting cell is pace-to-wins conversion on the REAL path (the 17.13 open question:
does the citation-era conviction channel move an owned-task crew's pace advantage?) —
answer it with the campaign's real re-rank data and say so explicitly either way.

**Integration risk:**

Crew real-path evals are the phase's first learned-crew recordings — the 18.7/18.19 stamp
guards get their first live exercise; any conflation or leak finding stops the campaign leg
until routed.

**Ready-to-paste prompt:** `agent_prompts/task-18-25-crew-campaign.md`

---

## Wave 4 — selection + close

### Task 18.26 — The real-LLM finalist eval (operator, ~5h/finalist, $0)
**Branch:** `phase-18-finalist-eval`
**Depends on:** 18.24, 18.25
**Section refs:** training/reports/report-finalist-eval.md (the 17.14 recorder + protocol this re-runs); scripts/run_tournament.py --candidate-artifact + the 18.19 --crew-artifact arm; the campaign reports' named finalists; the standing floors (whichever baseline the phase adopted)
**Complexity:** Integration

The selection evidence: 50-seed real-path evals of the named finalists on the canonical
seed set at the standing substrate — impostor finalists against the scripted-FSM crew (the
§1.3 comparator discipline: the same-seed FSM row re-recorded if the substrate moved), and
(if crew finalists exist) crew finalists against both the scripted impostor and the frozen
impostor champion, dual-stamped. Full 17.14 discipline: stamp proofs, validity gates, floor
sensitivity with rare-event z beside every verdict, the committed jsonl + report tables
18.27 reads.

**Files in scope:**
- training/reports/results-finalist-eval.jsonl + training/reports/report-finalist-eval.md (the phase-18 rows/reading — history preserved per the 17.14 precedent)
- tests/training/ (jsonl-row pins ONLY)

**Files NOT in scope:**
- scripts/run_tournament.py + training/ machinery (recorders froze earlier)
- replays/samples/ + replays/ml_corpus/ (working recordings stay out of the tree)

**Definition of done:**
- [ ] Every finalist recorded 50/50 on the real path, stamp-proven (uniform, sha==sidecar), validity PASS, $0, with the same-substrate FSM comparator row recorded on the same seeds; the evidence table carries win edge, referee verdict, and per-gauge floor sensitivity with the statistical reads.
- [ ] The emergence instruments are computed over every finalist's recordings and quoted beside the selection cells (18.27's second axis reads from here).
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

The 17.14 §6 recipe generalizes; the new leg is the dual-stamped crew-vs-champion cell —
plan its seeds so the crew finalist's two opponents are same-seed comparable. Wall-clock
scales with finalist count: cap the slate at what the campaign reports justify (~3–4).

**Integration risk:**

The comparator discipline is where selection evidence goes quietly wrong: if the substrate
moved at 18.12, every Phase-17 comparator number is stale and the same-seed FSM row MUST be
re-recorded here, never quoted from the old report. The contract makes that a DoD cell.

**Ready-to-paste prompt:** `agent_prompts/task-18-26-finalist-eval.md`

### Task 18.27 — THE FLIP + EMERGENCE READING (owner) + conditional productization
**Branch:** `phase-18-flip-emergence-reading`
**Depends on:** 18.4, 18.18, 18.26
**Section refs:** audits/audit-phase-17-close.md §1.3 (the flip bar, verbatim); audits/audit-phase-18-emergence-preregistration.md (the ratified second axis); tasks/phase-17.md 17.16 (the evidence-gated flip shape, both branches); the 18.26 evidence tables
**Complexity:** Integration

The phase's owner reading, two axes in one memo. **Axis 1 — the flip:** the champion
candidate read against the standing bar (referee PASS at the adopted baseline's floors AND
win ≥ the same-seed FSM comparator); PASS ⇒ productize (the champion surfaces swap to the
new artifact, default-selector flip, the 17.16 machinery in its PASS branch) and 18.28
records the mover baseline; FAIL ⇒ the champion stays opt-in, the finding recorded, 18.28
closes NO-FLIP. **Axis 2 — emergence:** every pre-registered instrument read against the
18.4 memo's four-part discipline (significance, split-reproducibility, ablation,
selected-for), each claim ruled EMERGENT / NOT-DEMONSTRATED with the evidence quoted. A
crew-adoption question, if the crew evidence supports one, is put to the owner here as its
own slot — never folded silently into either axis.

**Files in scope:**
- audits/audit-phase-18-flip-emergence.md (new: the two-axis memo + rulings)
- agents/tactical/learned/ (PASS branch only: the productization swap) + tests/scripts/test_champion_flip_ruling.py (the ruling pins, either branch)
- tasks/phase-18.md (the ruling's banner note)

**Files NOT in scope:**
- eval/ + training/ (evidence is read, never regenerated here)
- replays/ (no record at the reading — 18.28 records)

**Definition of done:**
- [ ] The memo reads axis 1 against the bar with every floor cell + win edge quoted from the 18.26 committed rows, the ruling recorded verbatim, and the ruled branch implemented + pinned (default provably flipped, or provably unmoved).
- [ ] Axis 2 rules every pre-registered claim with its four-part evidence quoted (including the ablation runs' provenance), and any crew-adoption slot is put and recorded explicitly.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

The 17.16 both-branches-pre-authored pattern: write the FAIL branch first (it is the
historical base rate), then the PASS branch's swap surface. The ablation evidence for axis
2 comes from the campaign reports — if an ablation was not run for a claimed behavior, the
claim reads NOT-DEMONSTRATED, honestly.

**Integration risk:**

Two owner rulings in one PR risks a stalled merge if one axis's evidence is contested —
keep the memo's axes separable so the owner can rule one and hold the other (the PR stays
open on the held axis, the 17.14 PENDING pattern).

**Ready-to-paste prompt:** `agent_prompts/task-18-27-flip-emergence-reading.md`

### Task 18.28 — The mover record + the phase close (operator + owner, $0)
**Branch:** `phase-18-close`
**Depends on:** 18.5, 18.23, 18.27
**Section refs:** tasks/phase-17.md 17.17 + audits/audit-phase-17-close.md (the close shape, both paths); the 18.12 record audit (the canary pre-registration source); tasks/post-phase-14-plan.md (the roadmap spine this close annotates)
**Complexity:** Integration

The close, on whichever path 18.27 ruled. FLIP ⇒ record the mover baseline (baseline 7; or
6 under the NONE surgery) with the §0 pre-registered canary bands from the standing corpus
anchors, floors pinned from the record, the full instrument battery, ~6 h operator. NO-FLIP
⇒ no record, the battery re-run over existing bytes at HEAD (the 17.17 shape). Either way:
the close audit (findings-not-failures — the campaign findings, the emergence rulings, the
staleness rules for whatever Phase 19 inherits, routed contracts for anything deferred),
the banner/README/roadmap updates in the same PR, `compute_next_task.py --phase 18`
demonstrated complete, and the Q5 provenance arms stated honestly.

**Files in scope:**
- audits/audit-phase-18-close.md (new)
- replays/samples/ + eval/watchability.py (FLIP path only: the mover record + its floor block)
- tasks/phase-18.md (STATUS banner) + tasks/post-phase-14-plan.md (the spine annotation) + README.md (project status)
- tests/ (byte-coupled re-pins on the FLIP path; ruling pins re-run either way)

**Files NOT in scope:**
- training/ + agents/ (frozen at 18.27's ruling)
- replays/ml_corpus/ (a mover flip does not invalidate meeting-layer calibration data — the standing forward rule; champion-era caveat recorded)

**Definition of done:**
- [ ] The ruled path is executed exactly (record + gates + canaries pre-registered in §0 before the first seed, or the NO-record battery at HEAD), all four committed sets re-verified (validity 10/10, bare byte-identity), and the close audit quotes every number from committed artifacts via the committed CLIs.
- [ ] The banner, README, and roadmap record the close; the phase computes complete with the merged-title index; every deferred item is a named routed contract, never a silent gap.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

The 17.17 contract's "resist recording anything on the NO-FLIP path" discipline holds. The
Phase-19 hand-off section matters more than usual: Phase 19 is REVIEW-AND-REFRESH — the
close audit should hand it the dead-spot candidates this phase noticed (duplicated walks,
retired seams, the `episode_boundary` orphan) as review inputs, not as contracts.

**Integration risk:**

Same as every close: the byte-coupled re-pin sweep on the FLIP path, and the two-owner-gate
compression (the flip ruled at 18.27, the close ratified here) — keep the close PR free of
any new evidence so the owner's merge ratifies a reading, never a surprise.

**Ready-to-paste prompt:** `agent_prompts/task-18-28-close.md`
