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

**18.11 meeting-layer gate — RULED: CREW-ONLY package (owner, 2026-07-19,
`audits/audit-phase-18-meeting-gate.md` §9).** The probe ran 2026-07-19 (two 25-seed 9p2i
real-path sets, seeds 2000–2024, 6 h 07 m at 2 workers) and the owner ruled on the measured
cells: **(A) CREW-ONLY** — the roll-call round (18.8) and endpoint-band exemption (18.9 lever
1) SHIP; the impostor-answer arm (18.10) stays INERT (bar (c) failed both clauses: impostor
win 4/25 = 0.16 < 0.20, STRONG self-flag 42/100 = 0.42 > 0.25 at z = +3.93 — the arm + its
bars stay in the tree for a future owner-gated re-probe on trained bytes); **(B) the absence
prior GRADUATES** (the ratified 17.7 §6 bar passes both clauses for the first time: crew
coverage 1.00 ≥ 0.60, new-over-gate 3/75 = 0.04 ≤ 0.20); **(C) the vent variant + widening
SHIP** (the 17.7 Ruling-2 HOLD lifted; live FULL yield 28 STRONG flags, all impostor). Per the
Baseline-numbering block a CREW-ONLY ruling changes NO structure: 18.12–18.14 proceed, and
18.12's graduation flips cover the round, the exemption, the vent variant/widening, and the
absence prior, while `impostor_roll_call` stays a default-OFF toggle.

**AMENDMENT (owner-directed, 2026-07-22).** Task 18.29 (the composed meeting-outcome
runner) is appended: the 18.14/18.15 verdict pair opened a composition the phase doc could
not have pre-authored — the conviction model answers the meeting-outcome question the
surrogate fails (will it convict: 0.938 accuracy) while the surrogate's ranking channel
answers the one it retains (who: 0.7667 top-1). The composed runner gives training
rollouts real conviction dynamics (rosters shrink, parity arises, crew can win by
ejection) under its OWN pre-registered GO bar, with NO-GO pre-committed to
diagnostic-only and the campaigns unaffected. 18.21 gains the optional runner-factory
seam, 18.24 the swap-boundary adoption note, 18.28 the close edge. Locked decisions
unchanged.

**18.27 flip + emergence reading — RULED: NO-FLIP + zero EMERGENT + NO crew adoption
(owner, 2026-08-01, `audits/audit-phase-18-flip-emergence.md` §13).** Axis 1 FAIL on the
whole slate: the champion candidate `ea4bc955…` (the §4.1 designation; every other
finalist archive for clause (d)) retains the win edge (0.52 vs the same-seed FSM
comparator 0.26, Δ +0.26) and fails the baseline-6 referee on both live supply gauges
(flags 0.93548 < 1.09091; conversion 0.36667 < its derived floor 0.66882), and so does
every finalist (+0.12 to +0.30 win edges, referee FAIL ×4 — `bfd145cb…` on conversion
alone, its flags cell UNRESOLVABLE; `7f73929d…` at n=49 vs 12/49 = 0.24490) — the
scripted FSM stays the default mover, the champion stays opt-in and unswapped, and
**18.28 closes NO-FLIP** (no mover record; the battery re-runs at HEAD). The witnessed
gauge is UNRESOLVABLE on all nine arms (structural at n=50); the bar stays as ratified,
re-pricing an owner decision outside the memo. F13: hypothesis A REJECTED as unsupported
(all three pooled margins negative and noise-barred; zero referee passes on any
finalist arm at n=50), B
operative but not demonstrated, no selection-rule fix contract routes. Axis 2: all
fourteen pre-registered rulings NOT-DEMONSTRATED (ten fail clause (a) or admit no
delta; the crew-witnessed-kill rate z = +3.37 and co-present-kill departure z = +4.32
pass (a)/(b)/(d) and fail (c) unablated — recorded as named findings N1/N2; both entropy
rulings unjudgeable as recorded). The crew-adoption slot closes NO-ADOPTION (`0bf179b7…`
considered; c1 pair null at n=49, McNemar p = 1.0; the routed scripted-crew comparator
arm declined). The ruling pins live in `tests/scripts/test_champion_flip_ruling.py`; the
deferral ledger (memo §12) routes to 18.28.

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
   spans them — `training/env.py:246-368` (post-18.23 anchor); the gap is perception, not actions). Encoder v3 +
   within-kind target resolution (18.22) advance the free-policy family only inside the
   co-evolution wave, where opponent pressure punishes tells, with the off-menu instrument
   (18.3) watching its recordings.

## Designer rulings (recorded here so contracts inherit them)

- **Watchability stays a gate, never a reward — and never a fitness term in disguise.** The
  conviction-economy proxy (18.15/18.16) predicts pre-meeting evidence supply from tactical
  facts; it must never read, wrap, or re-derive `eval/watchability.py` scores. The
  gate/reward boundary line is the NEVER-a-fitness-term boundary block inside `training/bakeoff/harness.py::inner_episode_fitness` (cited by construct — line anchors churned twice) and it does not move.
- **The proxy is not the ballot surrogate.** `training/surrogate/` (the ballot predictor,
  its 6-feature fence, its GO bar, its staleness cap) is untouched by the conviction model;
  the two are independent artifacts with independent verdicts. The Goodhart probe re-runs
  when the training-signal role grows (18.18) — the standing rule.
- **Meeting-layer mechanisms land default-OFF and inert** (the 13.5/14.10 lever pattern):
  the roll-call round (18.8), the endpoint-band exemption (18.9), and the impostor-answer
  variant (18.10) each ship flag-gated with no default-path byte movement, proven by
  committed-bytes counterfactuals where offline measurement is possible; the gate (18.11)
  rules what graduates; the adopting record (18.12) flips what ships. *Ruled 2026-07-19
  (CREW-ONLY, the STATUS banner above): the round, the exemption, the vent variant/widening,
  and the absence prior graduate at 18.12; the impostor-answer variant stays inert.*
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
  (18.7, 18.8, 18.9, 18.10) -> 18.11 THE MEETING-LAYER GATE [OPERATOR ~8-9h + OWNER]
  (the 18.7 edge is orchestrator/replay.py serialization: crew-stamp schema before the
   substrate-flag snapshot registry — a collision edge, not a semantic prerequisite)
  (18.1, 18.2, 18.3, 18.4, 18.11) -> 18.12 adopting record: baseline 6 [OPERATOR ~6-7h]
  18.12 -> 18.13 corpus re-record [OPERATOR ~18-20h]
  18.13 -> 18.14 surrogate re-ground + selection-bar re-pins

Wave 2 (training signal):
  18.13 -> 18.15 conviction-economy model + GO bar
  (18.14, 18.15) -> 18.16 fitness term + referee pre-screen integration
  18.16 -> 18.18 Goodhart re-probe (conviction path + the carried d4 exploit)

Wave 3 (co-evolution):
  (18.7, 18.16) -> 18.19 dual-role rollout + two-identity stamp
  (18.6, 18.19) -> 18.20 hall-of-fame + PFSP-lite sampler
  (18.17, 18.20) -> 18.21 alternating-freeze driver + stabilizers
  (18.19, 18.30) -> 18.22 encoder v3 + within-kind target resolution
  (18.16, 18.21, 18.22) -> 18.23 scenario staging (state injection + skill scenarios)
  (18.4, 18.5, 18.17, 18.18, 18.21, 18.22, 18.30) -> 18.24 THE IMPOSTOR CAMPAIGN [OPERATOR multi-session]
  (18.24, 18.31, 18.32) -> 18.25 THE CREW CAMPAIGN [OPERATOR multi-session]

  (18.16, 18.18) -> 18.29 composed meeting-outcome runner (amendment, 2026-07-22)
  18.16 -> 18.30 the live conviction serving path (amendment, 2026-07-22)
  18.24 -> 18.31 pre-18.25 campaign ergonomics (amendment, 2026-07-27)
  18.31 -> 18.32 the crew re-rank arm (amendment, 2026-07-28; 18.25's real-path legs consume it — its fake-path evolution runs on 18.31 alone)

Wave 4 (selection + close):
  (18.24, 18.25) -> 18.26 real-LLM finalist eval [OPERATOR ~5h/finalist]
  (18.4, 18.18, 18.26) -> 18.27 THE FLIP + EMERGENCE READING [OWNER]
  (18.23, 18.27, 18.29) -> 18.28 mover record + phase close [OPERATOR + OWNER]
  (18.5 reaches the close transitively through 18.24's entrant seeding)
```

Critical path: 18.7 → 18.10 → 18.11 → 18.12 → 18.13 → 18.15 → 18.16 → 18.19 → 18.20 →
18.21 → 18.24 → 18.31 → 18.32 → 18.25 → 18.26 → 18.27 → 18.28 (18.7 and 18.10 entered the head via the
`orchestrator/game.py`/`orchestrator/replay.py` serialization edges — dispatch 18.7 first).
The day-one frontier is nine roots (18.1–18.3, 18.5, 18.6, 18.7, 18.8, 18.9, 18.17);
nothing outside
the gate chain waits on the owner.

**Baseline numbering.** The ladder tip stands at baseline 5 (`audits/
audit-phase-17-close.md`). The meeting-layer adopting record at 18.12 is **baseline 6**; a
mover flip at 18.28 records **baseline 7**. Gate-conditional surgery, pre-enumerated per the
16.2/17.7 discipline (removal, not labeling — `scripts/compute_next_task.py` has no dropped
state): a FULL or CREW-ONLY ruling at 18.11 changes no structure (the arms that ship are the
ruling's business; 18.12–18.14 proceed either way). A **NONE** ruling removes 18.12, 18.13,
and 18.14 (contracts + prompts, with a drop record naming the gate audit), rewires 18.15's
`Depends on:` to `18.11`, rewires 18.16's `Depends on:` to `18.15` alone (the removed
18.14's constant-flip is moot under NONE — the bar stays baseline-5; the Wave-2 DAG edge
becomes `18.15 -> 18.16`), binds 18.15 to the standing baseline-5 corpus (its contract names
this fallback), leaves `BAKEOFF_BASELINE_ID = "baseline-5"` untouched, and renumbers the
18.28 mover record baseline 7 → 6. Under NONE the absence prior stays OFF with the ratified
bar unmet, restated in the gate audit.

**Collision discipline.** `meetings/manager.py` 18.8 then 18.12 (the graduation flip,
ordered via 18.11); `meetings/transcript.py` 18.9 then 18.12 (same); `agents/strategic/
prompts/` 18.10 then 18.12 (same); `agents/memory/beliefs.py` 18.12 only;
`eval/watchability.py` floor blocks 18.12 then 18.28 (FLIP path, ordered);
`replays/samples/` 18.12 then 18.28 (same); `replays/ml_corpus/` +
`scripts/record_ml_corpus.sh` 18.13; `training/bakeoff/harness.py` 18.14 (constants) then
18.16 (term/pre-screen), serialized by the dep chain; `training/bakeoff/map_elites.py` 18.6;
`agents/tactical/learned/` 18.7 then 18.27 (ordered via the dep chain);
`scripts/run_tournament.py` 18.7 then 18.19 (dep edge); `orchestrator/replay.py` is 18.7
(crew-stamp schema) then 18.11 (substrate-flag snapshot registry) then 18.12 (flag
graduation reclassification) then 18.19 (dual-stamp coherence), all dep-ordered;
`orchestrator/game.py` is 18.7 (crew-stamp threading) then 18.10 (prompt-version registry;
the dep edge is this file's serialization) then 18.12 (registry graduation) then 18.22 (the
concluded-hook payload) then 18.23 (the `initial_state` seam) then 18.28 (FLIP-path default
selector), all dep-ordered; `eval/balance_eval.py` 18.7 only; `training/env.py` 18.23; `agents/tactical/features.py` 18.22;
`training/coevo/` is 18.19/18.20/18.21 then 18.31 (the persistence/freeze-writer
amendments), in dep order with per-task module files; `training/realpath.py` is 18.17 then 18.22 (the
sanctioned reload ripple) then 18.31 (the resume path), dep-ordered;
`tasks/phase-18.md` is 18.11 (surgery) then 18.27 (ruling banner) then 18.28 (close banner),
all dep-ordered; `agent_prompts/` surgery 18.11.

**Operator/owner gates.** Operator sessions: 18.11 (probe recordings ~8–9 h), 18.12 (~6–7 h),
18.13 (~18–20 h — the long pole; checkpoint-push), 18.24 (multi-session; ~40–50 h of
unattended real-path re-rank legs spread across the campaign), 18.25 (multi-session;
~30–40 h real-path legs — the crew slate is smaller), 18.26 (~5 h/finalist),
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
- eval/watchability.py; (no floor changes — these are diagnostics, not gates)

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
- eval/watchability.py; (its walk is consumed via import or a faithful local walk — the referee itself does not move)
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
- training/bakeoff/harness.py; (anchor-CE is a different quantity — rollout-time, distributional; do not conflate)

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
memo, and 18.27 reads against this memo verbatim. One standing rule the memo itself
states: the DEFINITIONS, statistical rules, and bars are what the owner ratifies; the
quoted baseline CELLS re-anchor mechanically at any adopting record (18.12/18.13 re-quote
them on the new bytes with provenance) without re-ratification — pre-registration binds
the rules before measurement, and the substrate the rules run on is whatever the phase
adopts BEFORE the campaigns record.

**Files in scope:**
- audits/audit-phase-18-emergence-preregistration.md (new: the memo + the ratified bars)

**Files NOT in scope:**
- eval/ (no instrument changes at pre-registration; defects found here route back as contracts)
- tasks/phase-18.md; (no surgery at this gate)

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
Batch findings the memo MUST navigate (from the merged 18.1–18.3, verified):
(a) the grounded/fabricated vouch split partitions SUBJECT EVENTS (corpus 28 = 21
grounded + 7 fabricated), not the 34-observation numerator — quote the right denominator
per cell (the companion join 26+8=34 reconciles them); the 7 fabricated events are all
Rule-3-excluded weaponized co-presence, none whole-cloth invention. (b) The committed FSM
kills ONLY when alone: co-present-crew is 0 on all 863 pinned kills, so the co-present
correlation cell is None/undefined — pre-register kill-craft on the WITHIN-ONE-HOP
point-biserial (0.27899 corpus 9p2i), and note that any nonzero co-present count in a
learned mover's recordings is itself a behavioral departure. (c) 18.2 pins no corpus-4p1i
cell. (d) Only teammate-accusation and frame-conversion cells ship as RareEventCells; the
memo computes Wilson/advisory itself for any other rare cell it registers (e.g. the n=7
fabricated-vouch cell). (e) The off-menu by-kind/by-target classification plane is the
ENGINE INTENT KIND (action type string), not OptionKind — register on that plane.

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
corpus as a prior source, never a training environment), and evaluate it OFFLINE
(per-decision agreement with the FSM over the corpus decision stream; where it diverges and
toward what). The ES-leg-under-the-refined-anchor is deliberately NOT run here: the
harness's anchor-CE is computed against the FSM's own choice, and swapping the anchor needs
the additive anchor-policy seam 18.16 adds — the refined-anchor ES leg is a named campaign
entrant configuration at 18.24, which holds both the artifact (this task) and the seam
(18.16). Report-only: no champion ships from this task. Deterministic, $0, CPU. Substrate
provenance: every artifact this study freezes carries the corpus/floor substrate sha it was
fitted/selected against — the 18.24 campaign refuses stale-substrate seeds without the
cheap deterministic re-fit/re-run at the adopted substrate.

**Files in scope:**
- training/anchor_study.py (new: the sweep driver + the filtered-BC fit)
- training/artifacts/anchor_study/ (new: the frozen candidate genomes/anchors — float-hex weights + sha sidecars + a config carrying the substrate sha, the byte-addressable seeds 18.24 reloads)
- training/reports/report-anchor-study.md (new)
- tests/training/test_anchor_study.py

**Files NOT in scope:**
- training/bakeoff/harness.py + utility_es.py (consumed through their public seams)
- training/artifacts/impostor/ (the committed champions do not move)

**Definition of done:**
- [ ] The sweep reproduces the λ=1.0 committed champion byte-identically (the determinism cross-check), and every sweep row carries fitness, anchor-CE, win rate, take-rate, and descriptor footprint on the standing 30-seed protocol.
- [ ] The filtered-BC anchor's fit is deterministic (documented platform caveat per the surrogate precedent), its game filter is stated (which games, why), and its offline FSM-agreement/divergence evaluation is reported; the report names which candidates (if any) the 18.24 campaign should seed with, and every frozen artifact carries its substrate sha.
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
- training/bakeoff/harness.py; (its artifact writer is imported, never edited)
- eval/watchability.py; (descriptors are computed from rollout facts, never from the referee)

**Definition of done:**
- [ ] A full-budget run persists every filled cell's genome with sha sidecars and reloads them bit-exactly; the default-configuration run's champion, jsonl row, and existing artifact tree are byte-identical to the committed state (pinned); the persisted-cell index carries the substrate sha the cells were scored against (the 18.24 stale-seed refusal reads it — a Wave-1 substrate adoption makes these cells re-run-before-use, a cheap deterministic re-run).
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
- orchestrator/replay.py; (the ADDITIVE crew-stamp record + reader — `CrewTacticalPolicyStamp` lands HERE so a learned-crew recording has a schema slot from day one; a game with no crew stamp parses byte-identically, committed-set round-trip pinned; 18.19 consumes this for dual-stamp recordings)
- eval/balance_eval.py; (the ADDITIVE `crew_policy_stamp` kwarg on `run_tournament_eval` — the recording path only threads the single tactical stamp today; default None is byte-identical)
- orchestrator/game.py; (the crew-stamp threading into the `ReplayLog` construction ONLY — the mirror of the existing tactical-stamp plumbing)
- scripts/run_tournament.py; (the `learned-crew` factory arm + stamp wiring)
- tests/training/test_learned_factory_acceptance.py (the crew twin: Q4 bit-exact gate vs `CrewOptionScorer`, determinism double-run, leak-mode scan)
- tests/scripts/test_run_tournament_candidate_artifact.py; (the crew factory arm's guards)

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
- `orchestrator.replay.CrewTacticalPolicyStamp`

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
- meetings/manager.py; (the round + the resolver)
- tests/meetings/test_manager.py (OFF-path byte-identity; ON-path allocation fixtures: who is asked, order determinism, living-only, no double-turns)

**Files NOT in scope:**
- meetings/transcript.py; (18.9's region)
- agents/strategic/prompts/; (18.10's region — the round uses the existing role-blind whereabouts ask surface)

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

### Task 18.9 — The endpoint-band whereabouts exemption + the vent-placement flag variant (default-OFF) + counterfactuals
**Branch:** `phase-18-endpoint-band-exemption`
**Depends on:** none (root)
**Section refs:** audits/audit-phase-18-planning.md §3.3 (why roll-call lies can never mint STRONG flags); meetings/transcript.py:529 (`WEAK_REASON_ENDPOINT_TICK`), :2262-2270 (the band application), :1927-1945 (the single-tick self-alibi indexing); audits/audit-phase-17-close.md §6 item 4 (BOTH halves of the routed detector package: the endpoint relaxation AND the grounded-vent flag-minting variant); tasks/phase-17.md §Designer rulings (the 17.5 grounding chokepoint the variant reuses)
**Complexity:** Medium

The detector half of the routed Phase-18 package — both flag-minting levers, each
independently flag-gated and default-OFF. **(1) The endpoint-band exemption**, the lever
that converts roll-call answers into conviction-economy currency: a single-tick whereabouts
self-alibi contradicted by a first-hand sighting mints a STRONG (interior-class) flag
instead of being endpoint-banded to weak. **(2) The vent-placement flag variant** (the 17.5
scope firewall's flag-minting variant, routed by the close): a GROUNDED spoken vent
sighting — matched against the speaker's own `VentWitnessRecord`, the 15.4 chokepoint —
placing subject X in contradiction with X's own stated path mints a physical-contradiction
flag (today the widening feeds only the absent-set derivation; this arm feeds the
detector). OFF-path bytes identical for both. With the mechanisms, the committed-bytes
counterfactuals the gate reads: over the corpus and samples, how many recorded whereabouts
lies would have minted STRONG flags under the exemption, by liar role (today: 25 corpus
lies, 20 crew-authored / 5 impostor-authored, all weak), and how many grounded vent
placements would have minted physical flags, by subject role — the honest price of each
change in both directions.

**Files in scope:**
- meetings/transcript.py; (both mechanisms + resolvers)
- tests/meetings/test_contradictions.py (OFF-path byte-identity; ON-path STRONG-mint and vent-flag fixtures; the committed-bytes counterfactual pins by role)

**Files NOT in scope:**
- meetings/manager.py; (18.8's region)
- eval/ (instruments read recorded flags; the counterfactuals live in the detector's own test pins)

**Definition of done:**
- [ ] With both flags OFF, `detect_contradictions` output over committed bytes is byte-identical (pinned); exemption ON, a contradicted single-tick whereabouts claim mints a STRONG `alibi_vs_sighting` flag while multi-tick alibi endpoint semantics are untouched; variant ON, a grounded vent placement contradicting the subject's stated path mints a physical-contradiction flag and an UNGROUNDED vent claim can never mint one — all fixture-pinned.
- [ ] Both committed-bytes counterfactuals are pinned: the would-be STRONG-mint census (by liar role) and the would-be vent-flag census (by subject role) over corpus + samples, quoted in the PR for the 18.11 gate memo.
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
not move. The vent variant reuses the 17.5 grounding chokepoint verbatim (grounded-only is
the firewall — an ungrounded vent claim minting a flag would be a fabrication channel). The
counterfactuals are re-runs of the current detector with each flag ON over reconstructed
transcripts, the 17.5 pin pattern.

**Public types introduced:**
- `meetings.transcript.whereabouts_interior_flags_enabled`
- `meetings.transcript.vent_placement_contradictions_enabled`

**Ready-to-paste prompt:** `agent_prompts/task-18-9-endpoint-band-exemption.md`

### Task 18.10 — The impostor-answer template arm (variant, default untouched)
**Branch:** `phase-18-impostor-answer-arm`
**Depends on:** 18.7 (an `orchestrator/game.py` serialization edge — the crew-stamp threading before the prompt-version registry entries; a collision edge, not a semantic prerequisite)
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
- orchestrator/game.py; (the `prompt_versions_for_set` registry entries for the variant ONLY — recorded `prompt_versions` come from this registry, not the loader, so without this the variant renders different bytes while recordings still stamp the old versions)
- tests/agents/; (routing fixtures: default path renders byte-identically; variant path renders the self-placement contract; version stamps distinguish the variant in the registry AND the recorded bytes)

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
**Depends on:** 18.7, 18.8, 18.9, 18.10
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
impostor roll-calls; (d) the vent widening AND its flag-minting variant (18.9's second
arm) re-ruled with the package (the 17.7 Ruling 2 HOLD travels here; the FULL probe runs
with the variant ON so its live flag yield is measured, not extrapolated). The owner rules
**FULL / CREW-ONLY / NONE**; absence-prior graduation rides the ruling per the ratified
bar. Then the surgery in the ruled direction, exactly as
the Baseline-numbering block enumerates; prompts regenerate; validator green.

**Files in scope:**
- audits/audit-phase-18-meeting-gate.md (new: the memo + the recorded ruling)
- orchestrator/replay.py; (the substrate-flag snapshot registry ONLY: the four new lever flags — roll-call round, endpoint exemption, vent-flag variant, impostor-answer — wired in BEFORE any probe seed records, so probe/adoption recordings self-describe the arms under test; today the snapshot knows only `absence_prior`)
- tests/orchestrator/ (the snapshot-registry fixtures)
- tests/experiments/test_probe_backends.py (the hard-coded `_FLAGS_ON`/default-snapshot pins — `active_substrate_flags` delegates to the snapshot and grows with it)
- tasks/phase-18.md; (the surgery + the banner note)
- agent_prompts/ (regenerated)

**Files NOT in scope:**
- meetings/ + agents/strategic/prompts/ (the mechanisms are built; the gate rules, never edits)
- replays/samples/ + replays/ml_corpus/ (no committed record at the gate — probe sets are working artifacts)

**Definition of done:**
- [ ] The four new lever flags are registered in the replay substrate-flag snapshot BEFORE the first probe seed records (fixture-pinned; committed sets re-verify byte-identical — the registry addition must not move existing bytes).
- [ ] Both probe sets recorded 25/25 on the real Featherless path ($0, the arms under test stamp-proven via the substrate-flag snapshot in the recorded bytes), validity-gated, with every bar cell quoted beside its pre-registered threshold and the ruling recorded verbatim (FULL / CREW-ONLY / NONE, plus the vent-widening and absence-graduation components).
- [ ] The surgery is complete in the ruled direction (the Baseline-numbering block's enumeration): validator green, prompts regenerated, `scripts/compute_next_task.py --phase 18` consistent with the surviving DAG, no orphan references.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

The probe arm environments, from the merged mechanisms (verified): FULL =
`AILIBI_ROLL_CALL_ROUND=1 AILIBI_WHEREABOUTS_INTERIOR_FLAGS=1
AILIBI_VENT_PLACEMENT_CONTRADICTIONS=1 AILIBI_IMPOSTOR_ROLL_CALL=1`; CREW-ONLY = the
first two only. The impostor-answer variant exists ONLY for `qwen3_6_27b` (any other
prompt set fails loud), and every lever read happens at runner CONSTRUCTION — export the
full arm environment before any worker process starts, never mid-run. The variant's
recorded version strings are `impostor_report_roll_call.qwen3_6_27b.v1` /
`accusation_round_roll_call.qwen3_6_27b.v1`; 18.12's graduation flip folds
`IMPOSTOR_ROLL_CALL_PROMPT_VERSION_SETS` into `PROMPT_VERSION_SETS` (the registry
docstring says so).

Two pre-probe obligations the Wave-1 merges routed here, both load-bearing BEFORE any
ON-path seed records: (a) the four lever flags are deliberately NOT in
`orchestrator.replay._TOGGLEABLE_LEVER_RESOLVERS` (18.8/18.9 deferred registration to
this task — the scope's snapshot-registry leg); (b) the offline audit tool
`audits/workflows/extract_gameplay_facts.py` re-derives Phase-3 opt-in eligibility and
WILL flag ON-path roll-call recordings — relax it under the flag before the probe (its
DESIGN.md §5.2 companion note is owner-side and recorded, never edited here). Cheap
closure while in replay.py: the dedicated committed-set round-trip pin for the crew-stamp
schema (the 18.7 verifier's one soft spot). The offline censuses the memo quotes are
committed and verified: the exemption promotes 20 claims corpus+samples (crew 17 /
impostor 3 — the honest price runs ~5.7:1 against crew), converting only 14/25 of the
audit's funnel-lie cell (11 conflict-only lies stay weak — say so); the vent variant mints
7 flags across 6 subjects, ALL impostor (`tests/meetings/test_contradictions.py`
:2554-2730).

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
**Depends on:** 18.1, 18.2, 18.3, 18.4, 18.11
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
- meetings/manager.py; (the ruled arms' graduation flips ONLY — mechanism bodies froze at Wave 1)
- meetings/transcript.py; (same)
- agents/strategic/prompts/; (same)
- orchestrator/game.py; (the `prompt_versions_for_set` registry graduation flip ONLY — if the impostor-answer arm ships, the variant versions become the default-served entries)
- scripts/refresh_samples.sh (the substrate-lever preflight: the wrapper preflights only prompt/model today — it gains a positive check that the live lever slate equals the RULED shipped/unshipped state, refusing a stale `AILIBI_*` export BEFORE any seed of the ~6-7h record stages)
- tests/scripts/test_refresh_samples.py (the preflight fixtures)
- scripts/record_ml_corpus.sh; (the `REQUIRED_PROMPT_VERSIONS` re-lock ONLY — the recorder's version pin must move WITH the registry or check.sh fails at this PR; the duration/guard edits stay 18.13's)
- tests/scripts/test_record_ml_corpus.py; (the registry-equality pin re-lock ONLY)
- tests/scripts/test_manifest_writer.py (the MANIFEST substrate-flags string pins — the new true flags in recorded bytes)
- agents/memory/beliefs.py (the absence graduation component if ruled)
- orchestrator/replay.py; (the graduation reclassification ONLY — shipped levers move out of `TOGGLEABLE_SUBSTRATE_FLAG_KEYS` so baseline-6 recordings stamp them always-on, never env-toggleable; the snapshot/key ordering follows)
- tests/orchestrator/ (the reclassification pins)
- replays/samples/9p2i/ + replays/samples/4p1i/ (the baseline-6 record)
- eval/watchability.py; (the baseline-6 floor block)
- audits/audit-phase-18-baseline-6.md (new: the record audit)
- tests/eval/; (the byte-coupled committed-bytes re-pins this record moves, incl. the 18.1/18.2/18.3 instrument pins)
- tests/agents/; (the absence counterfactual + prompt-registry re-pins)
- tests/meetings/; (the graduation-flip re-pins)

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

THE RULED SLATE (gate audit §9, CREW-ONLY): exactly FOUR levers graduate — the roll-call
round, the endpoint exemption, the vent variant, and the absence prior. `impostor_roll_call`
STAYS a default-OFF toggle, so this contract's "if the impostor-answer arm ships" clauses
read FALSE: the `IMPOSTOR_ROLL_CALL_PROMPT_VERSION_SETS` fold and the game.py registry flip
DO NOT execute, and the recorder `REQUIRED_PROMPT_VERSIONS` re-lock is a no-op (the registry
does not move) — the preflight leg still lands (slate = four ON + impostor_roll_call OFF).
The record audit carries three coordination corrections when quoting the gate's cells (the
17.17 correction pattern — the ratified memo is not rewritten): (a) the CREW-ONLY coverage
z re-computes to +7.07 on the stated n=75 (the quoted +6.93 back-solves to n=72;
conservative, verdict-neutral); (b) the impostor-win z −2.08 is the memo's declared
one-sample-vs-0.36 convention — the pooled two-proportion read vs 18/50 is −1.79
(immaterial: the 0.16 < 0.20 bright-line miss and the self-flag clause decided bar (c));
(c) memo §6's "each bound to its home-module resolver by identity" holds for 3 of 4 — the
`impostor_roll_call` entry is a deliberate local mirror (loader import-cost isolation).
Watch item during the record: the validity gate's `cost_and_provenance_exact` has a known
blindness around the `(deadline_default)` synthetic marker (routed by PR #299 to a future
eval/ contract, unassigned — the close inherits it if unclaimed); a seed whose opening
defaults is a FAILED recording and re-records, per the standing rule. Shipping-layer
expectations for the §0 sanity read are the gate audit §7's CREW-ONLY cells (coverage 1.00,
impostor win 0.32, conversion 0.525) with the vent variant's yield expected in the [7, 28]
bracket — its first live measurement in the shipping combination is THIS record.

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

### Task 18.13 — The corpus re-record at baseline 6 (operator ~21–22h, $0)
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
- tests/eval/ (the corpus-pinned cells ONLY — test_watchability.py / test_watchability_reanchor.py corpus verdicts and the 18.1/18.2/18.3 instrument corpus pins; samples pins moved at 18.12)
- tests/training/test_bakeoff_harness.py; (corpus-derived re-pins ONLY — the constant flips are 18.14's)
- tests/training/test_surrogate_runner.py; (corpus-derived re-pins ONLY — the re-fit is 18.14's)
- tests/training/test_crew_options.py (corpus-derived re-pins ONLY)
- tests/training/test_goodhart_probe.py; (corpus-derived re-pins ONLY)
- tests/scripts/test_record_ml_corpus.py

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

The 17.9 runbook verbatim plus the checkpoint-push discipline. THIS IS A LOCAL OPERATOR
SESSION (the owner's machine, not a dispatch container — chosen to remove container-reclaim
risk from the ~22 h leg): run `bash scripts/setup_env.sh` first, export ONLY the recording
environment (`AILIBI_LLM_PROVIDER=featherless`, `AILIBI_PROMPT_SET=qwen3_6_27b`,
`AILIBI_SEED_MAX_ATTEMPTS=8`, `FEATHERLESS_API_KEY`) — the four graduated levers are
always-on in code and need no env; `AILIBI_IMPOSTOR_ROLL_CALL` must stay UNSET (the
recorder's preflight refuses it ON); work on the contract branch `phase-18-corpus-rerecord`
from current `main`. Checkpoint-push stays mandatory as crash/interruption insurance:
commit-and-push each completed seed range even though reclaim risk is gone. One arm the
local credential RE-OPENS: the annotated-tag half of the Q5 convention (dispatch
environments refuse tag pushes — the 16.14 limitation; locally
`git tag -a phase-18-corpus-<sha>` is available at the owner's discretion, with the
FROZEN-line shas remaining the operative guarantee either way). 4p1i first, then the 9p2i
long leg sharded across 2 staggered workers with jittered backoff. Context corrections from the 18.12
verification: the record's truth is `audits/audit-phase-18-baseline-6.md` — PR #300's BODY
quotes superseded first-cut numbers from before the vent-widening fix re-record; never cite
the PR body. Two cells this corpus gives their first powered read: the vent variant's
STRONG yield (samples read 6, one under the pre-registered [7,28] bracket — an adjudicated
near-miss; the corpus is the first large-N read) and the absence-prior top-churn (not
re-measured on the baseline-6 samples; last measurement is the gate's 4/75). The audit §2
false-vouch split (34 with grounded 14 / fabricated 4) is internally underdetermined as
printed — this corpus re-derivation states the partition cleanly. The `record_ml_corpus.sh`
relabel routed by PR #300 lands here.

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
- training/artifacts/anchor_study/ + tests/training/test_anchor_study.py (the baseline-6 re-run of the 18.5 study artifacts — cheap and deterministic; clears their substrate tripwires; PR #301's scope question, resolved by coordination: the re-ground task re-grounds everything substrate-bound in one place)
- training/artifacts/impostor/map-elites/ + tests/training/test_bakeoff_methods.py (same, for the 18.6 cell artifacts)
- training/surrogate/runner.py (ONE additive fence: the loader/cap learns the corpus identity — `SurrogateStalenessCap` is blind to substrate drift today; sha-keying extends to the fit corpus, fail-loud on mismatch)
- training/reports/report-ballot-surrogate.md (the baseline-6 reading)
- training/bakeoff/harness.py; (the two constant blocks ONLY)
- tests/training/test_surrogate_runner.py
- tests/training/test_surrogate_fidelity.py
- tests/training/test_surrogate_dataset.py
- tests/training/test_bakeoff_harness.py; (the two constant blocks' pins ONLY)
- tests/training/test_goodhart_probe.py; (the re-measured fake-path baseline pin ONLY)

**Files NOT in scope:**
- training/surrogate/*.py (the machinery re-runs; it does not change)
- eval/watchability.py; (floors pinned at 18.12)

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

The §8 recipe is executable as written. The measured inputs (18.13 verification, computed
from committed bytes): the baseline-6 corpus is **EJECT-MAJORITY** — 302/463 = 65.2%
ejected meetings, voter-ballot SKIP share 42.1% (baseline 5 was skip-majority at 58.4%) —
so axis 3's always-eject constant is back at FULL strength and a NO-GO is a plausible
honest verdict (its consequence is pre-committed: diagnostic-only + the fake-provider
fallback; the bake-off is never blocked, and 18.15's conviction model carries its own
independent GO). Fit-side meetings are **367** (train+val; test 96), so the ~143× cap
re-derives to **52,481**. Clear the seven `_PENDING_SURROGATE_REGROUND_1814` xfails and
the self-clearing tripwires this re-fit trips. Record-provenance note: cite committed
tests/README for corpus cells, never PR #301's body (pre-repair tables); the corpus
MANIFEST per-row shas are the recording truth (the FROZEN lines carry re-finalize shas).

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
- training/bakeoff/harness.py; (18.16's integration)

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
**Section refs:** training/bakeoff/harness.py:577-598 (`inner_episode_fitness` + the gate/reward boundary comment at :586-590); audits/audit-phase-18-planning.md §2.3 (the two consumption modes); the 18.15 verdict (which modes are live)
**Complexity:** Medium

Wire the conviction model into BOTH sides' fitness under the GO verdict: an additive
`conviction_weight × predicted-supply` term in the impostor inner fitness
(`training/bakeoff/harness.py::inner_episode_fitness`) AND in the crew fitness
(`training/crew/scorer.py::crew_inner_episode_fitness` — a separate function that does NOT
route through the harness; the crew campaign trains without the gradient unless this seam
is wired here), plus a pre-screen hook the campaign driver calls before spending real-path
evals. Under NO-GO the term is structurally absent from both sides (not zero-weighted) and
the pre-screen is advisory-labeled. This task also adds the **additive anchor-policy seam**:
`DecisionTrace`/`inner_episode_fitness` accept an optional anchor policy (default: the
scripted FSM, byte-identical behavior when unset) so a campaign entrant can anchor to the
18.5 filtered-BC artifact — the seam's second consumer is 18.24's refined-anchor entrant
configuration. The gate/reward boundary comment extends to name the new term's provenance;
use-counting flows through the model's own sha-keyed counter.

**Files in scope:**
- training/bakeoff/harness.py; (the impostor term + the pre-screen seam + the anchor-policy seam + the boundary comment)
- training/crew/scorer.py (the crew-side conviction term — the fitness composition only)
- tests/training/test_bakeoff_harness.py; (term-provenance fixtures; NO-GO structural absence; counter threading; anchor-policy default byte-identity; the AST firewall extended to training/conviction)
- tests/training/test_crew_scorer.py (the crew-side term fixtures)

**Files NOT in scope:**
- training/conviction/ (consumed via its public seam)
- training/rewards.py (the dense terms do not move — this is fitness composition on both sides)
- training/crew/options.py (the menu does not move)

**Definition of done:**
- [ ] With a GO artifact both sides' fitness carries the term (impostor via the harness, crew via `crew_inner_episode_fitness`) with its weight named in the row metadata; with NO-GO the term is absent from both and rows say so; both fixture-pinned.
- [ ] The anchor-policy seam defaults to the scripted FSM with provably byte-identical fitness when unset, and an alternative anchor policy threads through trace + fitness, fixture-pinned.
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
- training/realpath.py
- tests/training/test_realpath.py (fake-provider protocol tests: ranking rows, stamp read-back, timeout fail-loud, retry budget)

**Files NOT in scope:**
- scripts/run_tournament.py; (the CLI recorder is 17.14's; this is the library loop — no CLI change)
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
- tests/training/test_goodhart_probe.py; (re-pins + the new arms' fixtures)

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
**Section refs:** audits/audit-phase-18-planning.md §4 (#8) + the dive finding it cites (`rollout_candidate` hardwires the opposing side to the scripted FSM — harness.py:564-565, 630-636; scorer.py:850-857); training/bakeoff/harness.py:357-388 (`BakeoffPolicy`, the shared shape); orchestrator/replay.py (the stamp schema the crew stamp extends)
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
- orchestrator/replay.py; (the dual-stamp read-back coherence over 18.7's `CrewTacticalPolicyStamp` — games with zero, one, or two stamps round-trip; the schema field itself landed at 18.7)
- scripts/run_tournament.py; (the `--crew-artifact` arm + dual-stamp wiring)
- tests/training/test_coevo_rollout.py + tests/scripts/test_run_tournament_candidate_artifact.py (the dual-stamp guards)

**Files NOT in scope:**
- training/bakeoff/harness.py; (its wrappers are imported/mirrored, never rewired — the single-side paths stay byte-identical)
- agents/tactical/learned/; (18.7 shipped the surface; consumed here)

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

**Ready-to-paste prompt:** `agent_prompts/task-18-19-coevo-rollout.md`

### Task 18.20 — The hall of fame + PFSP-lite opponent sampler
**Branch:** `phase-18-hall-of-fame`
**Depends on:** 18.6, 18.19
**Section refs:** audits/audit-phase-18-planning.md §4 (#8) + §6 (the AlphaStar/PSRO transfer: frozen pool + hardness-weighted sampling); training/bakeoff/harness.py:1501-1526 (the artifact layout); training/surrogate/runner.py:105-148 (the sha-keyed use-counter doctrine the opponent bookkeeping mirrors); the 18.6 cell artifacts (a seed source)
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
- [ ] The store round-trips frozen genomes with sha verification (fail-loud on drift), the index carries full provenance, and MAP-Elites cells ingest as founders through 18.6's loader — with the founder's SUBSTRATE sha verified against the current campaign substrate at the ingest point: a mismatch refuses ingestion loudly pending the cheap deterministic re-run at the adopted substrate (the stale-seed fence moves here from 18.24, BEFORE the pool is built or sampled).
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
**Depends on:** 18.17, 18.20
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
form is structurally unreachable. The driver additionally exposes TWO ADDITIVE
seams, each inert when unset (digest-identical): a per-swap scenario-provider callable
(18.23's scenarios) and an optional meeting-runner factory per campaign configuration
(default: the fake provider) — the slot 18.29's composed runner (or any future GO-verdict
runner) plugs into without ever editing the frozen driver. Deterministic end-to-end on the fake/surrogate path;
machine-readable campaign rows.

Three merged hand-offs now bind this contract (18.20 at 4173ef1, 18.22 at ea0eb62, 18.29 at
6339116 — all verified against their contracts). (a) HALL-OF-FAME CONSUMPTION DISCIPLINE:
the driver constructs ONE `OpponentStalenessLedger` per run from the cap + the pool's
member shas, `register`s every freshly frozen champion, and treats a capped opponent as
RETIRE-AND-REPLACE (fresh sha) — never an in-place reset; "one generation use" means one
use per DISTINCT sampled member per driver generation, and `sample_opponents` draws WITH
replacement, so the driver dedupes the slate before metering; payoff maps passed to the
sampler must exactly cover the pool (empty = cold-start uniform is the only exception);
founders ingest through the substrate-fenced `ingest_map_elites_founders` BEFORE any pool
build or sampling; `HallOfFame.create` pins the campaign substrate sha, and TWO sha
definitions exist (the 18.24 block: `compute_substrate_sha` composite vs
`bakeoff_substrate_sha` raw MANIFEST) — the driver names which one it passes, in the row
schema. Per-side campaign constants (caps, floors) are this driver's to own;
`DEFAULT_COEVO_ARTIFACT_ROOT` is exported for it. (b) COMPOSED-RUNNER ADOPTION MECHANICS:
the meeting-runner factory seam adopts 18.29 ONLY via `load_composed_runner_factory` on
its DEFAULT path (the committed-GO gate + sha cross-check; `composed_artifact_dir=None` is
a diagnostics-only escape, never a campaign configuration), and only at a swap boundary;
under a composed configuration the row schema's "conviction/surrogate consumption" means
BOTH component counters (gate reads + probe reads), and
`verdict.json.adoption_constraints` is surfaced verbatim in the campaign meters — composed
pre-screen reads are spend advice paired with recorded-bytes floor reads, composed-substrate
probe reads are diagnostic-grade, and champion numbers are never composed-runner-scored.
(c) V3-FAMILY ENTRANT CONFIGS: the per-side entrant config carries `encoder_version` (v2
default, byte-identical artifacts); a hall/side stays SINGLE-FAMILY per campaign (a mixed
family fails loud only at genome-length reload), so the driver pins the family in config —
HoF rows deliberately carry no encoder stamp.

**Files in scope:**
- training/coevo/driver.py (new)
- tests/training/test_coevo_driver.py; (a miniature two-swap campaign on tiny budgets: freeze/swap mechanics, HoF growth, benchmark emission, exploiter integration, determinism digest)

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
cumulative — the harness's one-term/one-counter `resolved_conviction_term()` pattern) — a
campaign that exhausts a cap must stop loudly at a swap boundary, which is the natural
re-grounding point. Consume `CoevoRolloutResult`'s episode-local traces under the 18.19
fold-after-scoring discipline (fresh per-episode traces, fold into accumulators AFTER
scoring, `anchor_policy` inherited from config never from accumulators — the #306 P2 fix
constrains cross-seed accumulation). The exploiter probe is the standing ES at a tiny budget
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
**Depends on:** 18.19, 18.30
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
- agents/memory/store.py (the meeting-history memory channel the v3 encoder reads — populated at the existing deterministic meeting-conclusion fold; today `absorb_meeting_evidence` records no per-meeting outcome history the encoder can consume)
- agents/memory/working.py (the channel's typed carrier, if the design places it there)
- orchestrator/game.py; (the meeting-concluded hook payload ONLY — `_notify_meeting_concluded`/`note_meeting_concluded` carry the public meeting outcome the memory channel folds; today the hook updates only the emergency tracker)
- training/crew/scorer.py; (the `_CrewCandidateAgent.note_meeting_concluded` signature widening ONLY — the wrapper implements the exact current keyword-only signature and would TypeError on the widened payload)
- training/env.py; (the same hook-signature widening ONLY — its wrapper at :454 also implements the exact current signature)
- agents/tactical/learned/; (the learned wrappers' hook signature widening ONLY, if they override the hook)
- training/bakeoff/policy_es.py (the per-target head + v3 selection)
- tests/agents/test_memory_meeting_history.py (new — the channel's fold fixtures, firewall-legality)
- tests/training/test_bakeoff_harness.py; (encoder/head fixtures ONLY — the v3 golden pins, mask/tie fixtures)

**Files NOT in scope:**
- agents/tactical/learned/forward.py + the committed champion weights (the shipping champion's forward pass and artifact are untouched — only wrapper hook SIGNATURES may move, per the in-scope entry)
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

**Post-merge coordination note (2026-07-23):** the merged implementation (ea0eb62) also
touched `training/realpath.py` + `scripts/run_tournament.py` (+ their tests) — the
v3-artifact reload ripple (whitelist + `encoder_version` threading so a v3-stamped
champion rebuilds instead of failing the v2 genome-length check). SANCTIONED as coordination:
coherent, fail-loud, and fixture-pinned; recorded here because the PR body under-declared
it against the contract file list.

**Ready-to-paste prompt:** `agent_prompts/task-18-22-encoder-v3.md`

### Task 18.23 — Scenario staging: state injection + the skill-scenario library
**Branch:** `phase-18-scenario-staging`
**Depends on:** 18.16, 18.21, 18.22
**Section refs:** audits/audit-phase-18-planning.md §4 (#12) + the dive findings (both entry points hardwire `seed_initial_state` — orchestrator/game.py:1579-1585, 1641 (post-18.22 anchors); `WorldState` hand-construction precedent at tests/training/test_env.py:531-543; dense terms score truncated episodes — training/rewards.py:250-256); orchestrator/seeder.py:29-133
**Complexity:** Integration

The training-grounds instrument: an `initial_state` injection seam on the headless game
(bypassing `seed_initial_state`, with the rng-snapshot discipline that keeps injected
episodes deterministic and hash-coherent), and a scenario library of constructed mid-game
skill situations with per-scenario dense fitness from tactical facts only — first four:
kill-with-witness-nearby-then-survive-the-meeting, vent-unseen-under-patrol,
force-parity-endgame, body-discovery-latency. Scenario episodes are truncated by
construction and score through the dense terms (never `compute_shaped_reward`'s terminal
gate); scenarios feed FITNESS pressure, and the standing gates/referee never move. The
campaign consumes scenarios ONLY through 18.21's additive scenario-provider seam — this
task implements a provider conforming to that seam (no driver edit); watchability
quantities never appear in scenario fitness. The merged seam (316d4e5) is exact:
`CoevoScenarioProvider = Callable[[int, Side], Sequence[CoevoScenarioTerm]]`
(training/coevo/driver.py:309), called ONCE per swap with `(swap_index, moving_side)`; a
`CoevoScenarioTerm` carries `label` + `fitness: Callable[[tuple[float, ...]], float]`
receiving ONLY the flat genome — the provider closes over the side's policy builder and
runs its scenario episodes itself, and the term's value ADDS to the moving side's ES
fitness after the slate mean (payoff/benchmark/exploiter games untouched; `label` rides
the campaign rows as `scenario_labels`). Two obligations follow: the fitness callable must
be pure and deterministic (a nondeterministic term is the only way a provider can break
the driver's pinned double-run digest), and scenario-episode budgets sit OUTSIDE the
driver's `projected_game_bound` ceiling guard — the provider owns its own game budget and
states it.

**Files in scope:**
- orchestrator/game.py; (the additive `initial_state` seam)
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
run them before and after). 18.22's hook-payload widening (`_notify_meeting_concluded`
now passes `ejected_id` engine truth to every agent) lives in the same file — the
byte-adjacency caution covers that block too. Scenario fitness definitions are the Goodhart-adjacent part:
each must name what it deliberately does NOT reward (e.g. discovery-latency must not reward
meeting suppression — the FO-2 lesson).

**Public types introduced:**
- `training.scenarios.ScenarioSpec`
- `training.scenarios.build_scenario_state`

**Ready-to-paste prompt:** `agent_prompts/task-18-23-scenario-staging.md`

### Task 18.24 — THE IMPOSTOR CAMPAIGN (operator, multi-session)
**Branch:** `phase-18-impostor-campaign`
**Depends on:** 18.4, 18.5, 18.17, 18.18, 18.21, 18.22, 18.30
**Section refs:** audits/audit-phase-18-planning.md §7 (the campaign shape); the 18.21 driver + 18.20 hall of fame + 18.16 fitness stack + 18.17 real-path re-rank + 18.5 anchor-study candidates; audits/audit-phase-17-close.md §1.3 (the flip bar the campaign aims at)
**Complexity:** Integration

The phase's first live campaign: evolve the impostor side against the frozen scripted crew
plus hall-of-fame opponents (as the crew side gains members, later swaps use them),
entrants seeded from the committed champion, the 18.5 anchor-study candidates, and (for the
free-policy family) 18.22's v3 features — inner fitness on the fake/surrogate path with the
conviction term, per-generation real-path top-K re-ranks (18.17, ~2 h/gen), pre-screen
before every real spend, all meters quoted. The dep edges are load-bearing: no campaign
records before the emergence bars are ratified (18.4) or before the conviction signal it
selects on has been re-probed (18.18). THE PROBE'S FOUR NAMED BLOCKERS BIND THIS CAMPAIGN
(report-goodhart-probe.md "Blockers", folded verbatim): (1) `d4-contest-farming[4p1i]` —
no 4p1i-scored selection until the routed D4 contest floor lands; (2)+(3)
`conviction-supply-laundering[emergency|kill,4p1i]` — no conviction-weighted fitness on
the 4p1i roster, and on ANY roster the term's credit for meeting-count-multiplying play is
conditioned/capped on recorded-bytes confirmation; (4)
`prescreen-substrate-divergence[9p2i]` — a pre-screen PASS is real-path spend advice ONLY;
every gating use pairs with a recorded-bytes floor read on flag-mintless substrates. One
asymmetry this campaign owns (the 18.30 hand-off): the harness/crew eval passes serve the
term live, but the impostor TRAINING loops are deliberately still anchor-composed — 
threading the term into impostor training is THIS campaign's protocol decision, made under
blocker (2)'s guard and recorded in the report. The merged driver (316d4e5) makes the
mechanism concrete: passing `conviction=` to `run_alternating_freeze` serves the term LIVE
into BOTH sides' training fitness (a Codex-round fix — there is no metering-only mode),
while under a composed configuration the term object is inert in training fitness
(contributes exactly zero; conviction pressure flows through real ejection outcomes
instead) — so the protocol decision is exactly: non-composed + `conviction=` under
blocker (2)'s guard, composed, or neither. Scenario legs (18.23) and the composed
meeting-outcome runner (18.29) are deliberately NOT prerequisites: the campaign starts
without them, and if either merges mid-campaign a later swap MAY adopt it (the composed
runner ONLY under its committed GO verdict, through 18.21's runner-factory seam, with both
component use-counters quoted in the campaign meters), recorded per-generation in the
rows — the close (18.28) still waits on both either way. The composed verdict LANDED GO
(6339116: decision accuracy 0.8646 > 0.625, convicting top-1 0.7667 ≥ 0.6375) with three
adoption constraints machine-readable in `training/artifacts/composed/verdict.json`
(`adoption_constraints`) — carried verbatim into the campaign meters on adoption:
composed-provenance-validity (composed-substrate probe reads are diagnostic-grade — every
LLM-free meeting path fails `cost_and_provenance_exact` until the validity gate answers
the stamped-substrate question, an eval/-side open item routed to the close),
prescreen-substrate-divergence-shape (pre-screen PASS = spend advice only; pair every
gating use with a recorded-bytes floor read — blocker (4)'s shape), and
emergency-predicted-supply-above-bar (forced-emergency predicted-supply delta +29.5%
exceeds the 25% materiality bar with recorded 0.0 — the laundering shape; blockers
(2)+(3)'s recorded-bytes conditioning applies unchanged). Driver-consumption facts the
campaign plans around (316d4e5, verified): `CoevoCampaignConfig` requires `work_dir`,
`substrate_sha256` + `substrate_sha_kind` (named per the two-definition rule below and
quoted in every row), both side configs, `master_seed`, `num_swaps`,
`generations_per_swap`, `fitness_seeds`, `benchmark_seeds`, and non-empty unique
`payoff_seeds`; defaults slate_size 3, staleness_cap 8, exploiter 5×6 (the probe cannot be
disabled and dominates the projected game bound at defaults), game_ceiling 25 000 with
`allow_over_ceiling` defaulting False. The driver REFUSES to resume: an existing hall
root or rows file is a no-clobber error, so the multi-session shape is SEQUENTIAL FRESH
RUNS — each session a fresh work_dir + hall_root seeded via `initial_genome=` from the
prior session's frozen champion, the opponent pool restarting from substrate-fenced
MAP-Elites founders (there is NO path to load a prior run's hall as the pool); if
mid-campaign evidence shows cross-session pool continuity is load-bearing, that is a
routed amendment under the integration-risk discipline, never a silent machinery patch.
Composed-adoption hygiene: the merged suite never runs a composed campaign end-to-end
(rows with `meeting_runner="composed"` are unexercised), so the first composed swap is
preceded by a miniature composed smoke campaign whose rows are read before any real
spend; under a composed configuration `opponent_payoffs` are composed-runner-scored
hardness meters, never absolute champion numbers (benchmark/exploiter columns stay
fake-path by construction); and the first retire-and-replace event
(`retired_opponent_shas` non-empty) gets a sanity read in the rows — the suite pins
exhaustion, not continuation. Seed hygiene: every study-artifact entrant (the 18.5
candidates, the 18.6 cells) carries a substrate sha; a seed whose sha mismatches the
campaign substrate is re-fit/re-run at the current substrate before entry (cheap and
deterministic), never consumed stale. Two sha DEFINITIONS exist (merged, verified):
`training.anchor_study.compute_substrate_sha` (composite: baseline + MANIFEST digest +
splits digest + set + floor) and `training.bakeoff.map_elites.bakeoff_substrate_sha`
(raw MANIFEST digest) — the refusal logic dispatches per artifact family, never assumes
one key. The 18.5 report names the seed candidates: `lambda-4.0` (Pareto-dominant —
anchor-CE 0.61 at fitness 19.22; legibility is free at the fake-path budget) and
`filtered-bc-anchor` (via 18.16's anchor-policy seam). Instrument sweeps over campaign
recordings require BYTE-COMPLETE recordings: 18.3's walk accepts partial recordings by
design (an EOF-truncated file silently shrinks the decision denominator — the 18.2
byte-completeness fence is the model); the sweep leg verifies completeness first. Report: campaign rows, the cycling-detector
reading, per-entrant floor-sensitivity on the real re-ranks, the emergence-instrument
sweeps (18.1/18.2/18.3) over the campaign's real-path recordings against the 18.4 memo's
cells, and the named finalists for 18.26. Operator shape: fake-path legs are hours;
real-path legs total ~40–50 h spread across sessions — checkpoint-push per generation.

**Files in scope:**
- training/reports/report-impostor-campaign.md (new) + training/reports/results-impostor-campaign.jsonl (new)
- training/artifacts/coevo/ (the campaign's frozen artifacts, via the driver)
- tests/training/test_coevo_driver.py; (campaign-row pins from the committed rows ONLY)

**Files NOT in scope:**
- training/coevo/*.py + training/bakeoff/ (the machinery froze at Wave 3 — a campaign is a run, not a redesign)
- agents/tactical/learned/; (no champion swap here — 18.27's evidence decides)

**Definition of done:**
- [ ] The campaign report carries every generation's row (fitness, anchor benchmarks both directions, opponent slates, exploiter outcomes, meter consumption), the cycling-detector verdict stated against the pre-registered signature, and the real-path re-rank tables with stamp proofs and floor sensitivity per the 17.14 discipline.
- [ ] The emergence instruments are swept over the campaign's real-path recordings with deltas quoted against the 18.4 baseline cells (claims deferred to 18.27 — this task reports, never rules), and the finalists for 18.26 are named with their artifacts frozen.
- [ ] For every candidate emergence behavior the report surfaces (a delta the 18.27 reading could rule on), the 18.4-named counterfactual ablation is RUN (disable the enabling lever/term/feature; fake-path re-runs suffice where the behavior is tactical) and its provenance recorded in the report — the 18.27 four-part discipline consumes ablation evidence from here, and an unablated candidate reads NOT-DEMONSTRATED by construction.
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
resume, and say so in the report; per the driver's no-clobber discipline "resume" means a
FRESH run in a new work_dir seeded from the frozen champion (the driver-consumption block
above), and checkpoint-push covers the streamed `campaign-rows.jsonl` + frozen hall dirs.

**Integration risk:**

The first run composes every new subsystem (conviction term, pre-screen, HoF sampling,
driver, real re-ranks) — expect integration findings. The discipline: a defect found
mid-campaign becomes a routed contract or an in-report finding; the campaign never patches
machinery silently (merge-equals-done applies to the tools it runs on).

**Post-merge record (2026-07-27, coordination).** Merged b19b952 as **STOPPED, NOT
CONTRACT-COMPLETE** — an owner decision on the report's §4.0 evidence (real-path reads at
n≤6 carry noise ≈68% of the tested threshold; no referee PASS replicated), ratified by
the merge per the standing convention. Coverage as ratified: the champion slice complete
(14 champions, 6 seeds), K=2 complete for run-02 only, run-01/run-03 runner-ups at
3-seed screens (tranche 2 stopped 2026-07-27 under §4.0), run-04/run-05 runner-ups
skipped on the all-arms-win-0.000 evidence. The contract-discharge ruling (owner
adjudication, 2026-07-27): ACCEPTED AS-IS — no further n≤6 spend; the residual (run-04's
6 + run-05's 2 runner-ups) is an UNEVALUATED, UN-RECOVERED residual: those genomes are
not frozen anywhere in the tree — recovering them takes an F1-style scenario-seam pass,
after which they freeze and are evaluated at n=50 (400 games) or not at all (the 48-game
6-seed completion price is superseded with the rest of the n≤6 program); quoted by the
close from F10 (NEVER from the report's superseded §2 remaining-work paragraph). §8 is a
screening shortlist; 18.26's ratified slate is its 4-arm cut. A six-lens post-merge
verification recomputed every table from committed bytes
(all reproduce except the cells §12 corrects; report §12 Errata records the corrections, including the two
repaired run-04 intermediate stamps and the session-5 provenance-log gap). The campaign's
machinery findings route to 18.31 (pre-18.25 ergonomics); no candidate passed the §1.3
flip bar at the screening budget — the finding, not a failure.

**Ready-to-paste prompt:** `agent_prompts/task-18-24-impostor-campaign.md`

### Task 18.25 — THE CREW CAMPAIGN (operator, multi-session, ~30–40h real-path legs)
**Branch:** `phase-18-crew-campaign`
**Depends on:** 18.24, 18.31, 18.32
**Section refs:** the 18.24 report (the frozen impostor champions this campaign trains against); training/crew/ (the crew bases); audits/audit-phase-18-planning.md §4 (#8, the impostor-first rationale) + the crew-fitness finding (correct_reports dead on non-convicting paths — the conviction term is the counterweight)
**Complexity:** Integration

The counter-adaptation half: evolve the crew side (both bases: general + owned-task)
against the frozen impostor campaign champions + hall of fame, with the conviction-supply
term giving crew fitness the conviction-economy gradient the fake path denies it, the
interrupt-preserving constraint kept (the 15.22 guard — starvation stays unreachable), and
real-path re-ranks per generation. Reachability honesty (the merged driver, 316d4e5): the
frozen-champion half of that shape is direct, the hall half is NOT — there is no seam for
adopting 18.24's committed hall as this campaign's opponent pool; the impostor side enters
via `impostor.initial_genome` seeded from a committed 18.24 CANDIDATE (re-frozen as a
fresh lineage in this campaign's own hall), so the counter-adaptation reading is against
that lineage plus this campaign's own accumulating hall, and if the report judges
full-pool continuity load-bearing that is a routed amendment, never a silent driver edit.
Name the seed artifact by exact path: the strongest 18.24 arms live under
`training/artifacts/coevo/intermediates/` and `…/runnerups/` (e.g. `ea4bc955…` at
intermediates/run-02-utility-lambda4/gen-2, `bfd145cb…` — never a champion — at
runnerups/run-02-utility-lambda4/gen-9), NOT only under `<run>/impostor/`; all load
through the four-file artifact (verified post-merge). Founder honesty (the campaign's F2,
sharpened by the slate): the committed MAP-Elites founder pool is v2 free-policy
(1049-gene) — a utility-family (19-gene) impostor side CANNOT ingest it (the driver's
genome-length reload check), so `founder_cells_dir` stays unset for a utility-family
side and its opponent pool starts EMPTY, accumulating swap-frozen members + exploiter
finds only; if pool diversity proves load-bearing mid-campaign, the routed conditional
is a utility-family founder-persistence run (18.6-shaped), recorded in 18.28's deferred
ledger — never an improvised ingest. Crew mechanics the driver pins:
`first_side="crew"`; the crew side config structurally REJECTS `anchor_policy` (crew
anchor-CE is FSM-fixed by construction); the crew builder must emit a `crew-`-prefixed
`encoder_version` (the 18.19 conflation guard, enforced both directions). Scenario
adoption (18.23, merged d63ffab) is available to this campaign but honestly thin on the
crew side: the library holds exactly ONE crew scenario (`body-discovery-latency`, max
1.0) — meaningful crew scenario pressure beyond discovery latency means AUTHORING new
crew specs, which is new work, not configuration. If adopted: pass
`ScenarioProvider(agent_factory_builders=..., fitness_seeds=..., meeting_runner_factory=...,
rng_hash_policy=...)` as the driver's `scenario_provider`, and use the AGENT-FACTORY seam
(genome → `build_coevo_factory`) — the selector seam drives EVERY seat including the
opponents under an unenforced delegation convention and is never a campaign
configuration. Terms add AFTER the slate mean, so row fitness scalars stop being
comparable to pre-scenario rows; the provider's `games_per_evaluation` budget is advisory
only (nothing meters it — quote it in the report); and under the default forced-fake
meeting layer the kill-witness survival clause is vacuous while force-parity gains an
unnamed crew-ejection channel only an ejection-capable runner (the composed runner, under
its GO gate) makes live — name whichever applies in the report. Report mirrors 18.24 (rows, cycling detector, floor
sensitivity, emergence sweeps — crew-side instruments emphasized: roll-call coverage,
conversion, counter-adaptation evidence against the specific impostor champions). Crew
champion adoption is NOT this task's call: candidates route to 18.26/18.27 evidence.
Duration honesty: the crew slate is smaller than 18.24's but the per-generation real-path
re-rank arithmetic is the same — plan **~30–40 h** of unattended real-path legs across
sessions, checkpoint-push per generation.

**Files in scope:**
- training/reports/report-crew-campaign.md (new) + training/reports/results-crew-campaign.jsonl (new)
- training/artifacts/coevo/ (crew-side frozen artifacts, via the driver; disjoint gen dirs from 18.24's — the store layout separates sides)
- tests/training/test_coevo_driver.py; (crew-campaign row pins ONLY — additive to 18.24's region)

**Files NOT in scope:**
- training/coevo/*.py + training/crew/*.py (runs, not redesigns)
- agents/tactical/learned/; (adoption is 18.27's evidence question)

**Definition of done:**
- [ ] The campaign report carries the full row/benchmark/meter discipline, the counter-adaptation reading (does trained crew close the frozen champion's win edge, and through which instrument channels), and the real-path re-rank tables with stamp proofs.
- [ ] Every candidate emergence behavior this campaign surfaces carries its 18.4-named ablation run and provenance in the report (the 18.24 discipline, crew side).
- [ ] The gate-validity discipline holds throughout (no starvation-family candidate survives selection; validity-gate columns quoted per entrant), and crew finalists (if any clear the bars) are named for 18.26.
- [ ] The 18.24 protocol preconditions hold: the §4.0-style stability table is computed after the FIRST retested candidate (and the campaign does not proceed at a seed budget whose measured noise exceeds 25% of any threshold it tests — F12); every frozen artifact this campaign names for 18.26 loads through the consuming entry point (`--crew-artifact` / `--candidate-artifact`) before hand-off (F14); every session's chain/leg log is committed under the provenance root (the blocker-4 ordering evidence — the 18.24 session-5 gap is the cautionary case).
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
answer it with the campaign's real re-rank data and say so explicitly either way. The
18.31 operator surface (merged e2a040b, verified): stamp-grade config is now
config-preflight-enforced — `CoevoSideConfig.encoder_version` names the actual family,
`hidden` is REQUIRED for `v2`/`v3` masked-MLP families and FORBIDDEN for utility/scorer
families, `anchor_policy_label` must name the anchor artifact whenever `anchor_policy`
is set, and `CoevoCampaignConfig.run_label` must be set to the campaign run name (the
default stamps `coevo-campaign` into every freeze's provenance). Resume is OPT-IN:
re-invoke `run_realpath_rerank(..., resume=True)` with the same work_dir/tranche/mode/
config/prompt-set/backend (drift refuses; non-canonical maps refuse resume outright;
tick-budget-capped elements re-record on every resume by design, ~8 min each — budget
for it). The library now writes `leg-log.jsonl` and
`prescreen-quotes-<tranche>-<invocation>.json` natively per invocation — commit them
beside the rankings (they ARE the blocker-4 ordering evidence); new rankings carry
schema `realpath-rerank-v2`. Champion persistence is DEFAULT-ON — checkpoint-push now
includes `gen-champions/` (four files per generation); keep campaign trees on one real
filesystem (symlink/hard-link entries refuse). Report tables come from
`scripts/generate_campaign_tables.py` (`rows`/`legs`/`stability` subcommands), never
hand-assembled, and the F12 stability read runs via `stability` after the first
retested candidate. The
18.24 evidence is on this campaign's side here: the run-01 same-seed `conviction=None`
twin reproduced the impostor champion lineage sha-for-sha while CREW selection diverged —
the term's selection-relevant effect is crew-side, exactly where this campaign wants it
(quote the committed twin artifacts, not the report prose — report §12 Errata lists the
prose defects). Runbook (owner directive 2026-07-28, superseding 18.24's F7 one-leg
correction): run TWO legs concurrently — always on different tranches or different
work_dirs (the 18.31 tranche claim refuses same-tranche concurrency by design), staggered
starts with jittered backoff, keeping F7's `meeting_timeout_seconds=900` and 3-seed
tranches; each leg stays internally sequential (the library records one game at a time —
concurrency exists ONLY at the leg level). F7's one-leg numbers were measured under a
partially-impaired provider window; the two-leg default is the healthy-provider posture,
so if impairment symptoms reappear (rising timeout or retry-exhaustion rates in the
native leg logs), degrade to one leg and record the switch in the report — duration
honesty prices whichever posture actually ran. Sweep legs follow the recording-dir convention (`roster.json`
present, audit sidecars out — the campaign's F5). Founder-game pricing (F3) is moot while
founders cannot load (see the founder-honesty block above); run-05's 2×2 reduced shape is
the sizing precedent if any free-policy side runs. Stamp
obligation (routed by the 18.19 verification): the committed measurement-tier
`training/artifacts/crew/` dirs carry NO `stamp.json`, so the `--crew-artifact` arm fails
loud on them BY DESIGN — every crew artifact this campaign freezes carries the five-field
stamp, and the first dual-stamped crew recordings are this campaign's re-rank legs.

**Integration risk:**

Crew real-path evals are the phase's first learned-crew recordings — the 18.7/18.19 stamp
guards get their first live exercise; any conflation or leak finding stops the campaign leg
until routed.

**Post-merge record (2026-07-29, coordination).** Merged e9da533 (#316), verified PASS on
every DoD bullet — including the pre-registered preconditions actually functioning as
designed: the F12 stability read ran after the first retested slate, showed flags noise
at 183% of threshold on the meeting-scarce lineage (33% meeting-rich), and STOPPED the
real-path spend after the pre-registered core (~7 h recorded vs the 30–40 h envelope — a
deliberate, priced non-spend; the 18.24 non-replication lesson reproduced: 2 referee
screening passes, 0 replicated). The mid-campaign integration finding (CF1: no crew
re-rank seam) became routed Task 18.32 per the discipline — never a silent patch. **Crew
finalists: NONE clear the bars**; four F14-loadable candidates hand to 18.26 UNRANKED by
this campaign's own anti-laundering ruling (§4.4's complete rank inversion between
tranches), with re-frozen gen-0 controls beside them. Counter-adaptation: no crew closes
`ea4bc955…`'s win edge at n=3; the tranche-stable signal is structural (the owned-task
base's meeting-rate advantage persists; the general base starves — CF2, Phase-19
pricing). Pace-to-wins (17.13): structural half YES, wins half NOT RESOLVABLE at this
budget — 18.26's question. Report §12 Errata records the verification residue (a
hand-shortened table label, the underivable ~8.7 h header figure, the 56-min single-leg
window, a margins-vs-rates range, unreachable PR-branch shas); the 18.24 report gains
erratum 15 (`off_menu_decisions` absent from committed sweeps). Two-leg concurrency ran
as directed (staggered starts timestamp-verified), with the §4 posture amendment
disclosed.

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

The 18.24 hand-off, ratified at its merge (b19b952; quote committed artifacts, never the
report prose — report §12 Errata lists the known prose defects): **the impostor slate is
§8's 4-arm cut** — `ea4bc955…` (intermediates/run-02-utility-lambda4/gen-2), `bfd145cb…`
(runnerups/run-02-utility-lambda4/gen-9), `6d327dcb…` (the incumbent control,
run-01-utility-champion/impostor/gen-3), and `7f73929d…`
(runnerups/run-03-utility-bcanchor/gen-8, the F13 test arm). The reserve are NOT
finalists; promoting one is an owner note in this task's PR, and promoting the
win-rate-led alternative `11aa6863…` over `7f73929d…` CHANGES WHAT SLOT 4 TESTS (it swaps
the F13 gauge-hypothesis arm for a win-rate arm) — record it as such if done. The cap
(~3–4) reads over the impostor report; crew finalists from 18.25, if any, take their own
owner-justified slots. Evidence honesty: the screening coverage is UNEQUAL (21 candidates
at 6 seeds, 12 at 3) — slots 1–3 rest on 6-seed screens, slot 4 on a 3-seed screen, and
per §4.0 all screening gaps are within noise; the 18.24 §5.9 3-game comparator does NOT
discharge this task's same-seed FSM comparator row, which is recorded fresh at n=50.
Loadability at hour one: all four arms load through `--candidate-artifact` before the
first seed (verified post-merge; re-verify at run time — the five-second F14 check).
TWO PRE-REGISTERED CELLS, stated before any seed runs: (1) the noise precondition — a
split-half stability read at this task's n, per tested gauge; a gauge whose measured
noise exceeds 25% of its threshold reads **UNRESOLVABLE** (a third verdict outcome beside
PASS/FAIL — findings-not-failures; the §4.0 lesson priced at 40 h), and only gauges
clearing the precondition feed 18.27's axis-1 ruling; (2) the F13 cell — champions
(`6d327dcb…`, `ea4bc955…`) vs runner-ups (`bfd145cb…`, `7f73929d…`) on the referee
gauges: hypothesis A (the ES trades evidence-supply for wins; runner-ups sit one step
less far along the trade — predicts the runner-ups' gauge margins PERSIST at n=50),
hypothesis B (n≤6 referee reads are noise — predicts the champion/runner-up gauge gap
VANISHES at n=50). The cell reports; 18.27 rules.

The 18.25 hand-off (merged e9da533, verified): **no crew finalist clears the bars** — the
crew side of this task is DIAGNOSTIC, not champion selection. Four F14-loadable
candidates arrive UNRANKED by 18.25's own anti-laundering ruling: `0bf179b7…`
(run-c1-crew-owned-tasks/crew/gen-9), `72adb41c…` (c1 gen-3), `515fc066…`
(run-c2-crew-general/crew/gen-9), `7fa59718…` (c2 gen-3), with re-frozen gen-0 controls
at `training/artifacts/coevo/realpath-crew/controls/` (all six loads re-executed green at
hand-off). **Owner directive (2026-07-29): the crew block IS taken** — four crew arms
(the two gen-9 candidates `0bf179b7…`/`515fc066…` plus their same-seed gen-0 controls),
each SINGLE-OPPONENT against the frozen champion `ea4bc955…` (these are diagnostics, not
finalists — the dual-opponent shape in this contract's opening applies only to a crew
CHAMPION candidate, which 18.25 named none of; the gen-0 pairing at the same opponent is
what isolates crew learning). The piloted protocol:
pair every crew arm with its SAME-SEED gen-0 control, read win conversion only at n=50,
expect `flags_per_meeting` to be the UNRESOLVABLE-prone gauge (183% noise at n=3 on the
meeting-scarce lineage vs 33% meeting-rich), and watch `meeting_rate` ≥ 0.60 as the live
starvation floor on the general-base arms. The crew-vs-frozen-champion cell runs through
`run_tournament.py --crew-artifact <crew> --candidate-artifact <ea4bc955 dir>` — the
entry point 18.32 deliberately never touched, so its dual-stamp semantics stand; this
task's new pins must NOT copy the realpath-v3 row convention (there, `stamp`/`stamp_*`
hold the impostor READ-BACK even on crew legs and `opponent_stamp` the declaration), and
the scripted-impostor comparator cell must PROVE opponent absence (fsm-default stamp,
zero verified games). The 18.24 backfill n=3 `ea4bc955`-vs-FSM rows remain a screen —
never this task's comparator. One routed instrument question rides in: the crew-witnessed
kill rate ran 6.5×–15× corpus across all twelve 18.25 arms (confounded at n=3) — the
n=50 comparator pair is what decides whether that is a learned-crew observation effect
or an artifact. Duration honesty: the gate's ~5 h/finalist is the TWO-CONCURRENT-LEG
effective rate — 18.25's committed leg logs measure ~12.2 min/game serial at healthy
provider (7.32 h / 36 games), so a 50-seed arm is ~10 h of recording and ~5 h effective
in a leg pair; the full ratified slate (4 impostor + the same-seed FSM comparator + 4
crew = 9 arms ≈ 450 games) prices at ≈ 46 h wall-clock at the two-leg posture,
sessioned with checkpoint-push. That per-game rate was measured on meeting-rich
crew-vs-champion games — RE-PRICE from the first leg's measured pace before trusting
the projection, and record whichever posture actually ran (the 18.25 §12 lesson: quote
derivable figures only).

**Files in scope:**
- training/reports/results-finalist-eval.jsonl + training/reports/report-finalist-eval.md (the phase-18 rows/reading — history preserved per the 17.14 precedent)
- tests/training/test_finalist_eval_pins.py (new — the jsonl-row pins)
- tests/scripts/test_champion_flip_ruling.py (the minimal set-assertion relaxation forced by the phase-18 row append — every 17.14 value pin unchanged)

**Files NOT in scope:**
- scripts/run_tournament.py + training/ machinery (recorders froze earlier)
- replays/samples/ + replays/ml_corpus/ (working recordings stay out of the tree)

**Definition of done:**
- [ ] Every finalist recorded 50/50 on the real path, stamp-proven (uniform, sha==sidecar), validity PASS, $0, with the same-substrate FSM comparator row recorded on the same seeds; the evidence table carries win edge, referee verdict (domain PASS / FAIL / UNRESOLVABLE per the pre-registered noise precondition), and per-gauge floor sensitivity with the statistical reads.
- [ ] The emergence instruments are computed over every finalist's recordings and quoted beside the selection cells (18.27's second axis reads from here).
- [ ] Both pre-registered cells are reported as registered: the per-gauge split-half stability read with the ≤25% noise-vs-threshold statement quoted beside every gauge verdict, and the F13 champions-vs-runner-ups cell with both hypotheses' predictions stated verbatim before the first seed and the measured answer beside them (the ruling stays 18.27's).
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
scales with finalist count: cap each campaign's slate at what its own report justifies —
the impostor slate is the ratified 4-arm cut, and any crew arms take their own
owner-justified slots beyond it.

**Integration risk:**

The comparator discipline is where selection evidence goes quietly wrong: if the substrate
moved at 18.12, every Phase-17 comparator number is stale and the same-seed FSM row MUST be
re-recorded here, never quoted from the old report. The contract makes that a DoD cell.

**Post-merge record (2026-08-01, coordination).** Merged 384effc (#317), verified PASS on
every DoD cell — every recomputed headline cell matches the committed rows to the last
printed digit; both pre-registered cells committed before the first seed (the 14-second
pre-registration window is disclosed and the cells' substance predates it in this
contract); the fresh 50-seed FSM comparator recorded with opponent absence proven in-row;
the flip-test relaxation exactly as the 6f24ec3 amendment scoped (5 tests green, zero
17.14 value pins moved). One owner-sanctioned deviation: `7f73929d…` scores at n=49
(seed 35 excluded on a content-triggered validation pathology, forensics kept, every
cell annotated). THE RESULT: no candidate satisfies the §1.3 conjunction — every learned
arm beats the comparator on wins (+0.12 to +0.30), every one fails the referee supply
gauges (the Part-I shape reproduced at baseline 6); F13's hypothesis A is unsupported at
n=50 (all pooled margins negative and noise-barred); the crew diagnostics read null
(McNemar p = 1.0) with the witnessed-kill confound resolving toward learned-impostor
kill placement. One reader caveat: `p18-crew-c2-gen0`'s `recording.model` declares the
launch config while the leg made zero LLM calls — the validity gate (FAIL, empty
provenance) is the read of record, never `recording.model` alone. The ruling material
routes to 18.27's evidence map; the operational findings to 18.28's ledger.

**Ready-to-paste prompt:** `agent_prompts/task-18-26-finalist-eval.md`

### Task 18.27 — THE FLIP + EMERGENCE READING (owner) + conditional productization
**Branch:** `phase-18-flip-emergence-reading`
**Depends on:** 18.4, 18.18, 18.26
**Section refs:** audits/audit-phase-17-close.md §1.3 (the flip bar, verbatim); audits/audit-phase-18-emergence-preregistration.md (the ratified second axis); tasks/phase-17.md 17.16 (the evidence-gated flip shape, both branches); the 18.26 evidence tables
**Complexity:** Integration

The phase's owner reading, two axes in one memo. **Axis 1 — the flip:** the champion
candidate read against the standing bar (referee PASS at the adopted baseline's floors AND
win ≥ the same-seed FSM comparator); PASS ⇒ productize the ARTIFACT surface (the champion
weights/stamp under `agents/tactical/learned/` swap to the ruled candidate) and pre-author
the selector flip — the DEFAULT-SELECTOR surfaces (`orchestrator/game.py::
build_default_agent_factory`, the `scripts/run_tournament.py` default path) flip at
18.28's adopting record, not here (adoption-at-record: a default graduates at the baseline
that adopts it); FAIL ⇒ the champion stays opt-in, the finding recorded, 18.28 closes
NO-FLIP. **Axis 2 — emergence:** every pre-registered instrument read against the
18.4 memo's four-part discipline (significance, split-reproducibility, ablation,
selected-for), each claim ruled EMERGENT / NOT-DEMONSTRATED with the evidence quoted. A
crew-adoption question, if the crew evidence supports one, is put to the owner here as its
own slot — never folded silently into either axis.

Inherited from the 18.24 merge (quote committed artifacts; report §12 Errata names the
prose defects): (a) **the F13 ruling is THIS reading's** — 18.26's pre-registered
champions-vs-runner-ups cell measures it, and this memo rules which hypothesis stands; if
the runner-up effect is real (the ES trading evidence-supply for wins), that is a
Phase-18-level finding about the selection rule whose FIX is a routed next-campaign/
Phase-19 contract, never a retrofit into this phase. (b) **F6 bounds attribution**: the
run-01 same-seed `conviction=None` twin reproduced the impostor champion lineage
sha-for-sha, so no axis-2 emergence claim may attribute an impostor-side selection effect
to the conviction term on that lineage (the term's demonstrated selection effect is
crew-side). (c) **F11 is a measurement, not a ruling**: encoder v3 trained 3.8× worse
than its v2 ablation twin at the 12-generation budget — input to the reading, with the
disposition routed to the close's hand-off ledger. (d) The named non-finalist exhibit
`27f852fe…` (v3 gen-9 hall champion) stands ready if the off-menu instrument's
claim-grade denominators are wanted. (e) Any UNRESOLVABLE gauge verdict from 18.26 reads
exactly that in axis 1 — the bar stays as ratified, unresolvability is reported, and
re-pricing the bar remains an owner decision outside this memo. (f) From the 18.25
merge: the conviction-term emergence claim arrives NOT-DEMONSTRATED with its limb states
recorded (limb (a) unsatisfiable at n=3; limb (c) PARTIAL — the recede recording
deliberately withheld under the F12 stop); F6 is EXTENDED, not contradicted — the term's
selection locus is crew-side on BOTH bases with a base-dependent channel (direct
selection reordering where meetings are scarce, exploiter-novelty where meetings are
rich) — and no impostor-side attribution is permitted on the `ea4bc955…`-seeded
lineages either. The cycling-detector inputs: Red-Queen signature PRESENT on the
general-base impostor (flat anchor + oscillating co-matchup), owned-task crew reads
progress, its impostor plateaus. Any crew-adoption slot rests on 18.26 evidence alone —
18.25 supplies none that clears a bar.

The 18.26 evidence map (merged 384effc, verified — the memo quotes THESE rows and cells,
never report prose): rows `p18-imp-{ea4bc955,bfd145cb,6d327dcb,7f73929d}`,
`p18-fsm-comparator`, `p18-crew-{c1-gen9,c1-gen0,c2-gen9,c2-gen0}` in
`training/reports/results-finalist-eval.jsonl`; persisted cells
`f13_intersection_gauges`, `instruments.kill_craft_rider_intersection`,
`instruments.conversion_paired_49_seed`, `instruments.intersection_49_seed_for_7f73929d`,
`instruments.registered_nested_cells`, `instruments.seed_mod5_splits`,
`instruments.kill_craft_co_present_departure`. Axis-1 mechanics the ruling must carry:
`witnessed_event_rate` is UNRESOLVABLE on ALL NINE arms (structural — the rare-event
floor's 25% noise ceiling is unclearable at n=50), so the ratified three-gauge referee is
EFFECTIVELY TWO GAUGES, and on `bfd145cb…` (whose flags cell is also UNRESOLVABLE at a 7%
overshoot) the axis-1 FAIL rests on conversion alone; `7f73929d…` reads against the
49-seed intersection comparator 12/49 = 0.24490, never 0.26 (its n=49 seed-35 exclusion
is owner-sanctioned and annotated everywhere); the comparator-pairing map is full-50 for
the three full arms, the 49-seed block for `7f73929d…`, nothing for crew arms. The
measured axis-1 material: every learned arm beats the comparator on wins (+0.12 to
+0.30) and every one fails the referee supply gauges — NO candidate satisfies the §1.3
conjunction as measured. F13 under §11.2's either-side noise rule: all three pooled
runner-up-minus-champion margins NEGATIVE and noise-barred from supporting hypothesis A
(the hypothesis-B shape; one residual within-lineage conversion cell survives —
"A unsupported" ≠ "B demonstrated", the ruling is this memo's). Axis-2 scoping: ablation
clause (c) is complete on ZERO of the five campaign runs as recorded — inspect per cell;
crew axis-2 columns are NOT-DEMONSTRABLE for want of an opponent-matched comparator
(owner 2026-07-31: label, do not record), with a scripted-crew-vs-`ea4bc955…` comparator
arm ROUTED as an owner-optional follow-up if this memo wants crew claims;
roll-call is CONTEXT, not a ratified instrument; both action-entropy rulings arrive
NOT-DEMONSTRATED (the variance field never landed). Two post-hoc-criterion questions are
put to this memo explicitly rather than answered below it: the equivalence margin
("gen-9 ≈ gen-0" was never operationalized) on both the rider and conversion pairs, and
nothing else — every other cell reads through pre-registered semantics.

**Files in scope:**
- audits/audit-phase-18-flip-emergence.md (new: the two-axis memo + rulings)
- agents/tactical/learned/; (PASS branch only: the artifact-surface productization swap — the default-selector files flip at 18.28's record)
- tests/scripts/test_champion_flip_ruling.py; (the ruling pins, either branch)
- tasks/phase-18.md; (the ruling's banner note)

**Files NOT in scope:**
- eval/ + training/ (evidence is read, never regenerated here)
- replays/ (no record at the reading — 18.28 records)

**Definition of done:**
- [ ] The memo reads axis 1 against the bar with every floor cell + win edge quoted from the 18.26 committed rows, the ruling recorded verbatim, and the ruled branch implemented + pinned (PASS: the artifact surface swapped and the 18.28 selector flip pre-authored, with the default provably NOT yet moved — adoption-at-record; FAIL: the default provably unmoved).
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
**Depends on:** 18.23, 18.27, 18.29
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
- replays/samples/; (FLIP path only: the mover record)
- eval/watchability.py; (FLIP path only: the mover baseline's floor block)
- orchestrator/game.py; (FLIP path only: `build_default_agent_factory` selects the productized champion — the default-selector graduation this record adopts)
- scripts/run_tournament.py; (FLIP path only: the default path follows the flipped factory)
- tests/scripts/test_champion_flip_ruling.py; (FLIP: the default-provably-flipped re-pins; NO-FLIP: re-run green unchanged)
- tasks/phase-18.md; (STATUS banner) + tasks/post-phase-14-plan.md (the spine annotation) + README.md (project status)
- tests/ (byte-coupled re-pins on the FLIP path; ruling pins re-run either way)

**Files NOT in scope:**
- training/ + agents/ (frozen at 18.27's ruling)
- replays/ml_corpus/ (a mover flip does not invalidate meeting-layer calibration data — the standing forward rule; champion-era caveat recorded)

**Definition of done:**
- [ ] The ruled path is executed exactly (record + gates + canaries pre-registered in §0 before the first seed, or the NO-record battery at HEAD), all four committed sets re-verified (validity 10/10, bare byte-identity), and the close audit quotes every number from committed artifacts via the committed CLIs.
- [ ] On the FLIP path the default-selector surfaces provably flip (every default-SELECTOR surface builds the productized champion; the absent-stamp fallback and opt-in surfaces stay coherent — the 17.16 pin suite inverted), and the record's bytes carry the champion stamp; on NO-FLIP the default provably does not move (pins re-run green).
- [ ] The banner, README, and roadmap record the close; the phase computes complete with the merged-title index; every deferred item is a named routed contract, never a silent gap.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

The 17.17 contract's "resist recording anything on the NO-FLIP path" discipline holds. One
outstanding re-anchor this close owns (the 18.13 verification flagged it): the canary-family
cells (R1 eject-decided share, the genuine-class successor, roll-call coverage,
whereabouts-lie mints, ejection accuracy, impostor win) were never re-anchored on the
restored baseline-6 corpus denominator — this close's §0 pre-registration derives its bands
from the baseline-6 corpus, computing the anchors fresh. Scenario accounting (the 18.23
hand-off): campaign rows carry `scenario_labels` but no per-term values — fitness is not
decomposable post-hoc — so wherever a campaign adopted scenarios the close states the
provider config (scenario set, seeds, meeting layer) and quotes `games_per_evaluation`
beside `projected_game_bound`, or the phase's game accounting under-counts. The 18.24
inheritance this close quotes (from F10 and the §12 Errata, never the superseded §2
remaining-work paragraph): the residual as corrected — run-04's 6 + run-05's 2 runner-ups
unevaluated AND un-recovered (no frozen artifacts exist — recovery is an F1-style
scenario-seam pass, then evaluation at n=50 = 400 games, or nothing); run-01/run-03's 12
runner-ups at 3-seed screens; the decision trail (Option B
2026-07-26 → tranche-2 stop 2026-07-27 → merge-ratified STOPPED, NOT CONTRACT-COMPLETE);
the session-5 provenance-log gap (36 Option B games carry no in-repo
pre-screen-ordering evidence — an honest caveat on blocker (4)'s discharge, not a
retro-manufacturable record); and two deferred-ledger entries — the encoder-v3
disposition (F11: a from-scratch v3 ES at the 12-generation budget is a net loss; routes
to Phase-19/free-policy campaign sizing) and the conditional utility-family
founder-persistence run (18.6-shaped; NOT triggered — 18.25 closed without needing pool
diversity, so it lapses to a Phase-19 note). The 18.25 additions to the ledger: the
record/score element-level leg-concurrency split (the §4 posture amendment), CF3 (the
stability tool's zero-meeting-arm refusal wants native exclusion-with-reporting), CF4's
general rule (hand-maintained namespace registries — `DEFAULT_RANKING_ROOTS`,
`WORK_DIR_OWNED_NAMES` — mean NEW campaigns take SIBLING roots, as `realpath-crew/`
did), CF2 (the guardless general base is starvation-family under a strong impostor —
prices any future general-base crew work), the missing generator family for sweeps
(sweep tables stay hand-assembled — the one table class 18.31 didn't cover), and
duration honesty for the close's accounting: quote the derivable real-path figures
(6.76–7.32 h) from the committed leg logs, never the report header's ~8.7 h (its §12
erratum 2). The 18.26 additions: the three stuck-seed classes (rc-0 meeting-bearing
stalemates are INVISIBLE to `rc != 0` retry triggers — caught only by the scorer's
game_over check; a runner-level check is the routed fix), the seed-35 content-triggered
validation pathology (14/14 identical rc-99 at p-8/meeting-0/turn-0 — a substrate
finding, not a transient), the rare-event-floor structural finding (a gauge whose floor
is a rare event cannot clear a 25% noise precondition at n=50 — witnessed read
UNRESOLVABLE on all nine arms; any future bar re-pricing is an owner decision), the
routed scripted-crew-vs-`ea4bc955…` comparator arm + the equivalence-margin
pre-registration gap (both owner-optional), and 18.26 duration honesty (57.3 h busy vs
the 46 h projection — 25% over, attributed to posture/sleep-stalls/stuck-seeds; the
serial per-game prediction landed within 2.5%). The Phase-19 hand-off section
matters more than usual: Phase 19 is REVIEW-AND-REFRESH — the close audit should hand it
the dead-spot candidates this phase noticed (duplicated walks, retired seams, the
`episode_boundary` orphan, the three eval/ walk implementations, the recorder lock-race
and the un-unit-tested deadline_default freeze-guard branch, the unassigned validity-gate
deadline_default blindness, the unassigned validity-gate stamped-substrate question for
LLM-free meeting paths — every zero-LLM composed meeting fails `cost_and_provenance_exact`
for want of a model row, which is why composed-substrate probe reads are pinned
diagnostic-grade in `verdict.json.adoption_constraints` — the platform-sensitive `test_es`
hash pin that fails on non-Linux interpreters, and two coevo-driver trivia: the
`composed_artifact_dir` type-annotation-only escape that fails loud by accident rather
than design, the silently-overwritable `campaign-plan.json`, the scenario selector seam's
unenforced delegation convention — a selector-built agent drives every seat, opponents
included — and two 18.31 residuals: resume refuses non-canonical maps (custom-map
campaigns have no resume path without an eval/ change) and the hand-maintained
`WORK_DIR_OWNED_NAMES` registry) as review inputs, not as contracts.

**Integration risk:**

Same as every close: the byte-coupled re-pin sweep on the FLIP path, and the two-owner-gate
compression (the flip ruled at 18.27, the close ratified here) — keep the close PR free of
any new evidence so the owner's merge ratifies a reading, never a surprise.

**Ready-to-paste prompt:** `agent_prompts/task-18-28-close.md`

---

## Amendment (2026-07-22) — the composed meeting-outcome runner

### Task 18.29 — The composed meeting-outcome runner (conviction-gated ejections in training rollouts)
**Branch:** `phase-18-composed-runner`
**Depends on:** 18.16, 18.18
**Section refs:** training/reports/report-conviction-model.md (the GO cells: decision accuracy 0.938, recall 45/47 on the 96-meeting held-out split; `training/artifacts/conviction/verdict.json`); training/reports/report-ballot-surrogate.md (the NO-GO diagnosis this composes around: ranking top-1 0.7667 retained, decision channel all-SKIP; `SurrogateMeetingRunner` in training/surrogate/runner.py); training/surrogate/runner.py:105-148 (the use-counter doctrine BOTH components meter through); training/env.py:614-628 (the runner-factory seam)
**Complexity:** Integration

The verdict pair's opening: training rollouts currently run fake meetings that convict
nobody, while 65.2% of real baseline-6 meetings convict — so rosters never shrink, parity
never arises, an impostor never loses a teammate, and crew never wins by ejection inside
training. Compose the two committed instruments into a `MeetingRunner`: the conviction
model decides WHETHER the meeting convicts (the question the surrogate fails at 0.375),
and the surrogate's ranking channel decides WHO (the question it retains at 0.7667
top-1); the predicted ballots are synthesized coherently with that outcome and the
ejection actually happens in the rollout. No new weights — the composed artifact is a
manifest pinning both component shas + the bar verdict. Its OWN pre-registered
population-relative GO bar, stated here before any measurement, on the held-out corpus
test split (96 meetings / 60 ejections): (1) meeting-level decision accuracy **> 0.625**
(the strictest trivial constant on this split — always-eject); (2) among convicting
meetings, ejected-target top-1 **≥ 0.6375** (= 0.75 × the 0.8500 honest ceiling, the
standing axis-1 form); (3) exact-outcome match (ejected id or skip) REPORTED beside the
verdict, informational never gating. Pre-committed: **NO-GO ⇒ diagnostic-only** — the
campaigns run the standing plan (fake provider + conviction term) unchanged, and nothing
downstream re-plans. GO ⇒ the runner becomes an OPTIONAL campaign configuration through
18.21's runner-factory seam, adopted only at a swap boundary (the 18.24 note), with the
standing rules untouched: final champion numbers are never composed-runner-scored, and
both component staleness counters meter every composed meeting. The task also runs the
composed-path Goodhart leg (the standing rule — the probe re-runs when the
training-signal role grows; 18.18's conviction-path arms are the machinery this leg
extends): no lever family may launder composed-outcome artifacts into fitness above the
standing materiality bar, reported before any campaign adoption.

**Files in scope:**
- training/composed_runner.py (new)
- training/artifacts/composed/ (new: the component-sha manifest + verdict.json)
- training/reports/report-composed-runner.md (new)
- tests/training/test_composed_runner.py (new)

**Files NOT in scope:**
- training/surrogate/*.py + training/conviction/*.py (composed via public seams, never edited)
- training/bakeoff/harness.py + training/coevo/ (the driver seam is 18.21's; adoption is a campaign configuration, not a wiring change)
- eval/ (the referee and instruments never move; the runner is training-side only)

**Definition of done:**
- [ ] The composed runner implements the `MeetingRunner` protocol end-to-end on the fake-path test harness: conviction-gated decision, surrogate-ranked target, ballots synthesized coherently with the outcome through the REAL tally semantics, both component artifacts sha-verified on load (fail-loud before any use), both use-counters metered per meeting.
- [ ] The verdict is taken on the FIRST held-out evaluation against the pre-registered bar above, with every cell quoted beside its threshold, the exact-outcome match reported informationally, and the machine-readable consequence committed (`verdict.json`: GO ⇒ optional campaign configuration; NO-GO ⇒ diagnostic-only) — the honest diagnosis stated beside the verdict either way.
- [ ] The composed-path Goodhart leg reports its delta per forced lever against the standing bars, with component-consumption metered and quoted; any above-bar finding is a named blocker for campaign adoption, never a silent caveat.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

Compose, never re-fit: both components load through their committed loaders
(`load_surrogate_runner_factory`'s fence semantics; the conviction model's sha-verified
artifact) and the composed module holds NO learned parameters of its own. The decision
gate reads the conviction model's committed P ≥ 0.5 threshold (the pinned fidelity
operating point) — never a re-tuned one. Ballot synthesis must survive the downstream
folds (the cross-meeting belief fold reads `result.ballots`): under a convict decision,
the surrogate's predicted ballots are re-anchored so the plurality lands on the ranked
target through the real `tally_ballots`; under skip, the surrogate's ballots pass through
unchanged. The §7.12 teammate firewall semantics are inherited from the surrogate runner
untouched. The fidelity evaluation mirrors `run_surrogate_fidelity`'s split discipline
(fit-side never evaluated; first-eval verdict). For the Goodhart leg, reuse 18.18's
concrete machinery over the composed runner as the meeting path:
`run_conviction_path_probe`'s arm shapes, the baseline-relative gate split, the
`_signed_relative_gain` laundering convention, and the one-shared-counter discipline —
and note the probe's recorded caveat that `prescreen-substrate-divergence` applies to any
decision-degenerate meeting model equally: the composed runner's own substrate read must
carry the same recorded-bytes pairing rule.

**Integration risk:**

Compounding component errors laundering into training signal — a conviction-model false
positive plus a wrong surrogate top-1 ejects an innocent the real path would not have,
systematically, and an optimizer could learn to farm that seam. Three fences: the
pre-registered bar (a composed channel worse than the strictest trivial constant never
ships), the composed-path Goodhart leg (adoption blocks on above-bar findings), and the
standing rule that no reported champion number is ever composed-runner-scored. The
fallback is always live: NO-GO or a fired probe leaves the campaigns on the standing plan
with nothing re-planned.

**Public types introduced:**
- `training.composed_runner.ComposedMeetingRunner`
- `training.composed_runner.decide_composed_go`

**Ready-to-paste prompt:** `agent_prompts/task-18-29-composed-runner.md`

### Task 18.30 — The live conviction serving path (kill/body accessors + the in-loop term wiring)
**Branch:** `phase-18-conviction-serving`
**Depends on:** 18.16
**Section refs:** training/reports/report-conviction-model.md §10 (the routed serving seam — the four kill/body features have no live accessor); orchestrator/game.py:2548 + :2584 (the vent-witness and sighting `*_for_meeting` accessor patterns to mirror); training/bakeoff/harness.py:892-929 (`inner_episode_fitness` + `ConvictionFitnessTerm` — the wired-but-dormant seam every in-repo loop passes `conviction=None` into); training/crew/scorer.py:933-975 (the crew twin); training/conviction/model.py (`CONVICTION_FEATURE_NAMES` + the provenance map the live path must satisfy feature-for-feature)
**Complexity:** Medium

The 18.16 verification's finding, given an owner: the conviction gradient is wired and
pinned at the seam but DORMANT — no live accessor serves the four kill/body features, so
every training loop passes `conviction=None` and the pre-screen accepts only caller-built
vectors. Land the serving path: (1) the kill-witness and body-proximity `*_for_meeting`
accessor pair on the same surface as the vent-witness accessor, mirroring its pattern
verbatim (orchestrator-side engine reads — the firewall binds agents, not the trainer);
(2) a live feature assembler (`training/conviction/serving.py`) producing the exact
`CONVICTION_FEATURE_NAMES` vector from `run_meeting`-time state; (3) the term threaded
live through the entrant loops and the crew ES loop via `load_conviction_fitness_term()`
(GO ⇒ on by default; NO-GO structural absence preserved); (4) the pre-screen consuming
live-assembled vectors. The contract's heart is the parity pin: over the committed corpus
test split, the live-assembled vector equals the offline table's row feature-for-feature
— the live/offline semantics gap closes by measurement, not assertion.

**Files in scope:**
- training/conviction/serving.py (new: the live assembler)
- orchestrator/game.py; (the kill/body `*_for_meeting` accessor pair ONLY — mirror the :2548/:2584 pattern)
- training/bakeoff/harness.py; (the entrant-loop conviction threading ONLY)
- training/crew/scorer.py; (the crew-loop threading ONLY)
- tests/training/test_conviction_serving.py (new: the live/offline parity pin + accessor fixtures)
- tests/training/test_bakeoff_harness.py; (the loops-serve-live pins ONLY)

**Files NOT in scope:**
- training/conviction/{dataset,model,fidelity}.py (the fence and verdict are frozen; serving consumes them)
- agents/ (the accessors are orchestrator-side; nothing crosses the firewall)
- eval/ (untouched)

**Definition of done:**
- [ ] The accessor pair mirrors the vent-witness pattern (surface, naming, leak discipline) and is fixture-pinned; over the committed corpus test split the live-assembled feature vector equals the offline table row feature-for-feature (the parity pin, every `CONVICTION_FEATURE_NAMES` entry asserted).
- [ ] With the committed GO verdict the entrant and crew loops carry a non-None conviction term by default (rows say so), NO-GO structural absence is preserved (fixture), and the pre-screen accepts live-assembled vectors end-to-end on the fake-path harness.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

Mirror the vent accessor verbatim — same wrapper surface, same record-snapshot semantics,
same teammate-firewall inheritance. The parity pin is the whole game: build it FIRST
against the offline table (`build_conviction_table` honors `splits.json`), then implement
until it passes; any feature that cannot be made live-equal is a stop-and-report, never an
approximation. Threading defaults follow the verdict bytes (`load_conviction_fitness_term`
already encodes GO/NO-GO); the loops' change is passing the loaded term, not new logic.

**Public types introduced:**
- `training.conviction.serving.assemble_live_conviction_features`
- `training.conviction.serving.LiveConvictionFeatureError`

**Ready-to-paste prompt:** `agent_prompts/task-18-30-conviction-serving.md`

---

## Amendment (2026-07-27) — pre-18.25 campaign ergonomics

Authored by coordination after the 18.24 close-out adjudication (owner-ratified at the
#312 merge): the campaign's §11 table demonstrates five machinery defects by incurred
cost — 25 real games lost to no-resume, 66 real games spent recovering unpersisted
genomes, an overwritten pre-screen record, a shortlist that could not load through its
consumer, and six review findings that were transcription errors in hand-assembled
tables — and 18.25 is another 30–40 h operator campaign against the same machinery. One
small task fixes all five (plus the session-5 lesson: leg logs become native) before
18.25 records anything. 18.25's dependency line gains 18.31; the DAG, critical path, and
collision discipline are amended above. Locked decisions unchanged.

### Task 18.31 — Campaign ergonomics: resume, persistence, loadable freezes, generated tables
**Branch:** `phase-18-campaign-ergonomics`
**Depends on:** 18.24
**Section refs:** training/reports/report-impostor-campaign.md §11 (the five demonstrated defects + costs), F1/F9/F12/F14 + §12 Errata items 1 and 10 (the mis-stamp and log-gap lessons); training/realpath.py:702, 873 (`_verify_stamps`, `run_realpath_rerank`); training/coevo/hall_of_fame.py:242, 397 (`create`, `add_member`); training/coevo/driver.py (the freeze/persistence sites); scripts/run_tournament.py:560 (`_load_candidate_policy` — the consuming entry point, NOT edited)
**Complexity:** Integration

The routed machinery task the 18.24 campaign's operational evidence demands (the
integration-risk discipline working as designed: mid-campaign defects became a routed
contract, never silent patches). Six fixes, each small, each priced by incurred cost:
(1) RESUME for `run_realpath_rerank` — skip a (candidate, seed) element whose replay
already exists AND whose read-back stamp `weights_sha256` equals the candidate's genome
digest AND whose recording reaches GAME_OVER with the byte-completeness fence green; the
skip predicate is CONJUNCTIVE and any miss re-records (all three checks exist in the
tree — they are simply not wired to a resume path). (2) Per-generation champion-genome
persistence in the driver — each generation's champion persisted beside the campaign
rows (or the ES champion trace exposed), ADDITIVE AND DIGEST-INERT: the row digest
covers row JSON lines only and must not move; the work-dir no-clobber discipline extends
to the new artifacts. (3) Tranche/invocation-keyed pre-screen records — a native writer
for pre-screen quote records (keyed by tranche/invocation, never in-place overwrite),
plus a native append-only leg log written by the leg library itself (the blocker-4
ordering evidence stops depending on operator shell redirection — the 18.24 session-5
gap is the demonstration). (4) Natively loadable freezes — `HallOfFame.add_member` and
every driver freeze path write the four-file loadable artifact (`weights.json`, sha
sidecar, five-field `stamp.json`, provenance `config.json`), with `encoder_version`/
`hidden` dispatched from the side config per family (the §12 Errata item-1 mis-stamp is
the failure this kills), loadable through `_load_candidate_policy` end-to-end. (5) A
deterministic table generator rendering the campaign-report table families (§3 row
tables, §4 leg tables, the §4.0 stability table) from committed artifacts. (6) The free
protocol precondition documented at the seam: the stability-table computation runs from
the generator against any two-tranche ranking set (what F12 tells every future campaign
to do after its first retest).

**Files in scope:**
- training/realpath.py (the resume path + the native pre-screen/leg-log writers)
- training/coevo/driver.py (the champion-persistence artifact ONLY)
- training/coevo/hall_of_fame.py (the loadable-freeze writer)
- scripts/generate_campaign_tables.py (new — the table/stability generator CLI)
- tests/training/test_realpath.py + tests/training/test_coevo_driver.py + tests/training/test_hall_of_fame.py + tests/scripts/test_generate_campaign_tables.py (the fixes' pins)

**Files NOT in scope:**
- training/coevo/factory.py + rollout.py (untouched)
- training/artifacts/coevo/ (the 18.24 record is frozen history — the generator READS it as its test fixture, never rewrites it)
- scripts/run_tournament.py (the consuming entry point is the invariant this task satisfies, never the thing it edits)
- training/reports/ (18.24's report is a merged record; its §12 Errata is the correction channel)

**Definition of done:**
- [ ] An interrupted re-rank resumes: a leg with pre-existing (candidate, seed) replays skips exactly the verified-complete elements and re-records everything else, refusing to skip on ANY verification miss (stamp-sha mismatch, non-GAME_OVER, completeness-fence fail) — fixture-pinned in both directions; the driver persists every generation's champion digest-inertly (the 18.21 double-run row-digest pin passes unchanged) under the standing no-clobber discipline; pre-screen records and leg logs write natively, tranche/invocation-keyed, append-only.
- [ ] Every hall/driver freeze writes the four-file artifact with family-correct `encoder_version`/`hidden` and loads through `_load_candidate_policy` end-to-end in a test (both families: a utility-genome and a v3 masked-MLP fixture); the table generator reproduces the committed `measurement-stability.json` numbers from the committed ranking artifacts and renders the row/leg table families deterministically (same bytes twice).
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

The resume rule is conjunctive on purpose — a skip on any weaker predicate silently
converts a corrupted or foreign replay into "already done"; when in doubt, re-record (the
cost asymmetry is ~8 minutes vs a poisoned evidence table). Two dispositions the rule
must state: a `TICK_BUDGET_REACHED` replay has no GAME_OVER row by design and is
therefore NEVER skippable — it re-records, deliberately; and the completeness fence is
dir-scoped (`compute_kill_craft_report`), so per-(candidate, seed) verification is
reached via per-seed staging or a roster-first write order — sanctioned here — never by
editing `eval/kill_craft.py` (out of scope). The driver persistence writes
beside the rows file (e.g. a `gen-champions/` dir under the work dir), inheriting the
work-dir no-clobber preflight; 18.21's double-run digest test is the guard that row
emission never moved. The freeze writer needs `hidden` and a stamp-grade run label that
`CoevoSideConfig`/`CoevoCampaignConfig` do not yet carry — additive, default-valued,
digest-inert config-metadata fields are SANCTIONED for exactly this (the frozen-machinery
rule bends for declared additive metadata, never for behavior); take
`encoder_version`/`hidden` from config — never re-derive from genome length (length
collisions between future families are exactly the ambiguity stamps exist to remove). The stability
generator's numbers must reproduce the committed `measurement-stability.json` from the
committed `realpath*/` ranking files — that reproduction IS its acceptance fixture, free
and already in-tree.

**Integration risk:**

`training/coevo/driver.py` and `hall_of_fame.py` are proven-frozen machinery with
determinism digests and 29/22-test suites — every existing test must pass unchanged, and
the persistence/freeze additions must be provably inert to rows, digests, and existing
artifact bytes (the 18.24 record under `training/artifacts/coevo/` is a frozen fixture:
`git status` clean over it after the full suite is part of the review bar). The resume
path touches the same library 18.25's legs will run within days — the conjunctive
predicate's false-positive direction (skipping something unverified) is the only truly
dangerous failure mode; bias every ambiguity toward re-recording.

**Public types introduced:**
- `training.coevo.hall_of_fame.write_loadable_artifact`

**Post-merge record (2026-07-28, coordination).** Merged e2a040b, verified PASS: all six
fixes pinned; every pre-existing test passes unchanged BY NAME (29/22/16 originals across
the three machinery suites, now 48/52/113); the 18.21 campaign digest reproduced
byte-identically across both trees (`7c8fe054…`); zero artifact paths touched. Three
declared deviations SANCTIONED as merged, all refuse-direction: (a) the realpath row
schema bumped `realpath-rerank-v1 → v2` (new recordings gain recorder-identity fields
`recording_backend_sha256`/`game_map_sha256`; frozen `-v1` history untouched; the
generator reads both and distinguishes identity-absent from identity-mismatch); (b) the
adversarial-filesystem hardening (symlink/hard-link/claim guards — fresh runs now refuse
dangling-symlink collisions `.exists()` sailed past); (c) `hall_of_fame.py` now imports
engine/consumer surfaces for reconstruction proof (its old no-engine-imports docstring
line amended honestly; lint-imports contracts keep — they fence agents/observation, not
training→engine). Residual limits recorded for the review ledger: resume refuses
non-canonical maps (custom-map campaigns have no resume path without an eval/ change),
and `WORK_DIR_OWNED_NAMES` is hand-maintained (any future driver-owned path must be
declared there or the collision class re-opens) — both in 18.28's Phase-19 hand-off.

**Ready-to-paste prompt:** `agent_prompts/task-18-31-campaign-ergonomics.md`

### Task 18.32 — The crew re-rank arm: crew candidates, frozen-opponent seam, dual stamps
**Branch:** `phase-18-crew-rerank-arm`
**Depends on:** 18.31
**Section refs:** training/realpath.py (`RealPathCandidate`, `_build_agent_factory`, `_verify_stamps` — the impostor-only surfaces this task widens); training/coevo/factory.py (`build_coevo_factory` + the 18.19 conflation guard, consumed not edited); scripts/run_tournament.py (`--crew-artifact` — the dual-stamp semantics this task mirrors, NOT edited); orchestrator/replay.py (`CrewTacticalPolicyStamp`)
**Complexity:** Integration

The routed amendment 18.25's leg discipline demands (owner-ratified 2026-07-28, the
Amend + overlap ruling): the 18.25 contract requires per-generation real-path re-ranks
whose recordings are the first dual-stamped crew recordings, with ranking rows, native
leg-logs, resume, and tranche claims — but `run_realpath_rerank` was impostor-only end
to end, and the only committed dual-stamp recorder (`run_tournament.py --crew-artifact`)
produces none of that machinery. Six additions, all refuse-direction:
(1) crew candidate families — `RealPathCandidate` accepts `crew-option-features-v1` and
`crew-option-features-v2`; `hidden` refused for them (scorer family). (2) Factory
dispatch — crew families build through `build_crew_scorer` (basis per family) wrapped in
`build_coevo_factory`; the 18.19 conflation guard holds both directions at candidate
preflight, before any spend. (3) The frozen-opponent seam — keyword-only
`opponent_artifact` on `run_realpath_rerank`: a four-file loadable impostor artifact,
loaded + sha-verified + stamp-read before any spend, installed in the impostor slot for
EVERY candidate in the leg; a crew-family opponent refuses; an opponent with
impostor-family candidates refuses — legs stay homogeneous; None with crew candidates
records against the scripted FSM (the comparator cell); the opponent identity rides the
leg manifest, the leg-log `leg-start` event, and every row. (4) Dual-stamp verification
— the crew stamp is read back from bytes and verified sha == computed digest, with
crew-side verified/uniform/equals-computed row fields mirroring the impostor discipline;
row schema bumps `realpath-rerank-v2 → v3`, additive optional fields only, frozen
`-v1`/`-v2` history untouched. (5) Resume/drift — the protocol-drift check folds the
opponent identity and candidate families into the manifest comparison; a resumed leg
whose opponent or family moved refuses. (6) `scripts/generate_campaign_tables.py`
(`legs`, `stability`) accepts `-v3` beside `-v1`/`-v2`.

**Files in scope:**
- training/realpath.py (the crew arm: families, opponent seam, dual stamps, drift)
- training/coevo/hall_of_fame.py (the shared four-file artifact reader)
- scripts/generate_campaign_tables.py (v3 acceptance)
- tests/training/test_realpath.py + tests/training/test_hall_of_fame.py + tests/scripts/test_generate_campaign_tables.py (the arm's pins)

**Files NOT in scope:**
- training/coevo/driver.py + factory.py + rollout.py (consumed frozen)
- training/crew/ (consumed frozen)
- scripts/run_tournament.py (the finalist entry point stays the 18.26 invariant)
- training/artifacts/ (frozen history; committed recordings stay byte-identical)

**Definition of done:**
- [ ] A crew-candidate leg records end to end against a frozen-opponent artifact with both stamps verified (uniform, sha == computed digest per game), and each refusal path is fixture-pinned in both directions: crew hidden, crew-family opponent, opponent-with-impostor-candidates, missing/corrupt/sha-mismatched opponent artifact, resumed leg with a moved opponent.
- [ ] `realpath-rerank-v3` rows render through the table generator's `legs` and `stability` subcommands including mixed-version ranking sets, and impostor-only invocations keep their exact current row shape modulo the version string (the frozen `-v1`/`-v2` corpus reads unchanged).
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

The loader lives under training/ — lint-imports forbids training-imports-scripts, so the
`--crew-artifact` load semantics are mirrored from `run_tournament.py`, never imported.
Bias every ambiguity toward refusal: the false-accept direction in stamp verification
converts another campaign's bytes into this leg's evidence, which is the exact failure
class the 18.19 guards exist to kill. The opponent is leg-constant by design —
per-candidate opponents would make rows incomparable within one ranking.

**Integration risk:**

This library records 18.25's evidence within days of the merge; a defect lands directly
in the campaign's selection tables. Every existing realpath test must pass unchanged,
and the committed recordings and rankings under training/artifacts/coevo/ stay
byte-identical after the full suite.

**Public types introduced:**
- `training.coevo.hall_of_fame.read_loadable_artifact`
- `training.coevo.hall_of_fame.LoadableArtifact`

**Post-merge record (2026-07-28, coordination).** Merged 088d4c2 (#315), all gates green
(the macOS-only ES hash pin verified pre-existing on bare main, identical digest; CI
Linux green). Two declared deviations SANCTIONED at the merge ruling, both
refuse-direction-preserving: (a) on a crew leg the required row `stamp`/`stamp_*` fields
hold the impostor-side READ-BACK proof (the frozen opponent read from recorded bytes; an
fsm-default stamp with 0 verified games in the comparator cell) while `opponent_stamp`
holds the DECLARED artifact stamp — read-back vs declaration stay distinct fields, and
`weights_sha256` is always the candidate's digest; (b) the leg-manifest schema version
is unbumped — the `opponent` manifest key and the `leg-start` `opponent`/`side` fields
are additive, and the drift check reads them regardless.

**Ready-to-paste prompt:** `agent_prompts/task-18-32-crew-rerank-arm.md`
