# Agent Prompt — 21.14 The smoke (operator): five seeds on the corrected substrate, STOP-and-report, and an abandon branch that still merges

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-21.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 21.14 — The smoke (operator): five seeds on the corrected substrate, STOP-and-report, and an abandon branch that still merges, anchored to Wave-0 register entries, read in full including verifier notes — `audits/review-2026-08-26/A/collated-findings.md`: A-6 at :693 [CONFIRMED, P1] (the two template lines that teach the oracle dialect; causal separation is perfect over the 668 committed meetings — leak 45/326 = 13.8% where the proof block renders, 0/342 where it does not), A-17 at :2086 [ADJUSTED] (the ballot render references exactly one turn field; 0 of 3,350 vote prompts in the 9p2i sets carry a current-meeting claim line), A-34 at :3750 [CONFIRMED] (the redaction sentence normalizes to the empty skeleton and is the largest repeated voice cluster in both 9p2i sets), A-14 at :1718 [CONFIRMED] (2,166 of 35,350 recorded actions = 6.13% recorded as submitted with no consequence, including 36 kills, 99 reports, 17 emergency calls), A-3 at :242 [ADJUSTED] (120 guard-redirected ballots, 25 flipped meeting outcomes, 3 ejections no voter authored; the 107-of-120 rationale figure needs case-insensitive matching, 101 exact-case), A-31 at :3501 [CONFIRMED] (1,505 double-minted witness-side vent rows, 0 witnessed-only, 27 distinct heard-only rows that are 27/27 impostors past the teammate firewall), A-1 at :60 [ADJUSTED] (the win check skipped on a meeting-trigger tick is SPECIFIED and test-pinned; the verifier's note binds this contract — both realized cases recorded the correct winner, so this is a latent-correctness repair with zero realized exposure); `audits/review-2026-08-26/B/collated-findings.md`: B-8 [CONFIRMED] (`working.last_seen` has one production writer, so the belief line contradicts the same prompt's own sightings in 19% of rendered rows), B-18 [ADJUSTED] (the corpus recorder aborts on ONE dead-owner probe where the sibling wrapper needs a ten-poll streak; blast radius is a spurious abort plus restart latency, not a lost leg), B-21 [CONFIRMED] (all 54 tests of the corpus recorder stop before any seed stages, so its recording engine executes in no test). Precedents: `tasks/phase-20.md` Task 20.35 (the smoke this one mirrors); `audits/audit-phase-20-smoke.md` §0 and §12 (the ABANDON, and the fact that no ratified criterion named the class that produced it), §9 (the cells that did not exist because the instrument raised), §10 (the measured operating data and the two re-derived wall-clock projections), §13 note 3 (run the honesty instrument on the FIRST completed seed, not after the set) and the §14 addendum (the re-measure on the PRESERVED smoke bytes, at $0, which is why this task preserves its bytes); `audits/audit-phase-20-baseline-7.md` §0.2 (the protocol actually run, two parallel seed workers, the key never reproduced), §0.3 (23h25m42s of operator wall for 300 games at $0) and §0.4 (two `(deadline_default)` seeds refused at the freeze guard and re-recorded in 12m33s). Anchors re-verified at HEAD `d8ec0a1c`: `orchestrator/replay.py`:524-546 (`_RETIRED_ALWAYS_ON_LEVERS`, twenty-one keys), :568-570 (`_TOGGLEABLE_LEVER_RESOLVERS` — ONE live toggle, `impostor_roll_call`), :578-580 and :585-588 (the stamp key order), :591 (`substrate_flag_snapshot`), :623 (`retired_levers_stamped_off`), :651 (`substrate_slate_mismatches` — the one comparison the wrapper preflight, this report and the record must all use rather than re-derive); `scripts/refresh_samples.sh`:36-37 (`AILIBI_SAMPLE_DIR`, `AILIBI_MANIFEST` defaulting under it), :247-260 (the `--dry-run` and `--expect-levers` parse, an explicitly empty value meaning the bare slate), :303 (the substrate-lever preflight, delegating to `substrate_slate_mismatches`) with its TWO call sites at :524 on the dry-run path and :650 on the real one, :441 (two parallel workers by default on featherless) and :461 (four attempts per seed), :547-551 (the key preflight; only `${FEATHERLESS_API_KEY:0:8}` is ever printed), :566 (`REQUIRED_PROMPT_SET="qwen3_6_27b"`), :588 (`REQUIRED_SET_OWNER_MODEL="Qwen/Qwen3.6-27B"`), :660 (the set dir created before any spend), :669 (the roster descriptor written before any spend), :737 (the stage created under `dirname "$SAMPLE_DIR"`); `scripts/record_ml_corpus.sh`:156 (`REQUIRED_PROMPT_VERSIONS`, all four templates locked at v4 TODAY), :499 (`check_prompt_version_registry`) called at :910 on the REAL path only — the dry-run exits at :829 after echoing the locked map at :796, so the comparison this smoke makes is not one the preview performs, :607 (`check_replay_provenance`, whose `deadline_default` refusal at :676 is the freeze guard), :194-196 (the fixed per-set seed ranges — the corpus wrapper has no seed-slice flag); `scripts/verify_samples.sh`:16-23 (a bare invocation walks EVERY set under the samples root); `scripts/validity_gate.py`:78-93 (`--expected-model`, `--require-zero-cost`); `eval/validity.py`:26-56 (the ten named checks — :49 `cost_and_provenance_exact`, which also requires every game's substrate stamp to equal the canonical snapshot, and :54 `byte_identical_reconstruction`); `scripts/measure_baseline.py`:726 (`--honesty`) and :716 (`--solvability`); `api/replay_loader.py`:603 (`_assert_substrate_matches`, reached at :1101); `scripts/check_doc_facts.py`:1722 (`check_audits_index`, which errors on any un-indexed top-level audit) with the real-repo assertion at `tests/scripts/test_check_doc_facts.py`:236; `scripts/verify_ml_evidence.py`:2359 (`inventory_problems`, reached from `run_availability` at :2550) against `docs/artifacts.md`:107, whose row reads `158 files` and `git ls-files audits` returns 158 at HEAD. AGENTS.md craft rules 2, 5 and 7.. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-21.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-21-smoke`
**Depends on:** 21.1, 21.2, 21.3, 21.4, 21.5, 21.6, 21.10, 21.13
**Section refs:** Wave-0 register entries, read in full including verifier notes — `audits/review-2026-08-26/A/collated-findings.md`: A-6 at :693 [CONFIRMED, P1] (the two template lines that teach the oracle dialect; causal separation is perfect over the 668 committed meetings — leak 45/326 = 13.8% where the proof block renders, 0/342 where it does not), A-17 at :2086 [ADJUSTED] (the ballot render references exactly one turn field; 0 of 3,350 vote prompts in the 9p2i sets carry a current-meeting claim line), A-34 at :3750 [CONFIRMED] (the redaction sentence normalizes to the empty skeleton and is the largest repeated voice cluster in both 9p2i sets), A-14 at :1718 [CONFIRMED] (2,166 of 35,350 recorded actions = 6.13% recorded as submitted with no consequence, including 36 kills, 99 reports, 17 emergency calls), A-3 at :242 [ADJUSTED] (120 guard-redirected ballots, 25 flipped meeting outcomes, 3 ejections no voter authored; the 107-of-120 rationale figure needs case-insensitive matching, 101 exact-case), A-31 at :3501 [CONFIRMED] (1,505 double-minted witness-side vent rows, 0 witnessed-only, 27 distinct heard-only rows that are 27/27 impostors past the teammate firewall), A-1 at :60 [ADJUSTED] (the win check skipped on a meeting-trigger tick is SPECIFIED and test-pinned; the verifier's note binds this contract — both realized cases recorded the correct winner, so this is a latent-correctness repair with zero realized exposure); `audits/review-2026-08-26/B/collated-findings.md`: B-8 [CONFIRMED] (`working.last_seen` has one production writer, so the belief line contradicts the same prompt's own sightings in 19% of rendered rows), B-18 [ADJUSTED] (the corpus recorder aborts on ONE dead-owner probe where the sibling wrapper needs a ten-poll streak; blast radius is a spurious abort plus restart latency, not a lost leg), B-21 [CONFIRMED] (all 54 tests of the corpus recorder stop before any seed stages, so its recording engine executes in no test). Precedents: `tasks/phase-20.md` Task 20.35 (the smoke this one mirrors); `audits/audit-phase-20-smoke.md` §0 and §12 (the ABANDON, and the fact that no ratified criterion named the class that produced it), §9 (the cells that did not exist because the instrument raised), §10 (the measured operating data and the two re-derived wall-clock projections), §13 note 3 (run the honesty instrument on the FIRST completed seed, not after the set) and the §14 addendum (the re-measure on the PRESERVED smoke bytes, at $0, which is why this task preserves its bytes); `audits/audit-phase-20-baseline-7.md` §0.2 (the protocol actually run, two parallel seed workers, the key never reproduced), §0.3 (23h25m42s of operator wall for 300 games at $0) and §0.4 (two `(deadline_default)` seeds refused at the freeze guard and re-recorded in 12m33s). Anchors re-verified at HEAD `d8ec0a1c`: `orchestrator/replay.py`:524-546 (`_RETIRED_ALWAYS_ON_LEVERS`, twenty-one keys), :568-570 (`_TOGGLEABLE_LEVER_RESOLVERS` — ONE live toggle, `impostor_roll_call`), :578-580 and :585-588 (the stamp key order), :591 (`substrate_flag_snapshot`), :623 (`retired_levers_stamped_off`), :651 (`substrate_slate_mismatches` — the one comparison the wrapper preflight, this report and the record must all use rather than re-derive); `scripts/refresh_samples.sh`:36-37 (`AILIBI_SAMPLE_DIR`, `AILIBI_MANIFEST` defaulting under it), :247-260 (the `--dry-run` and `--expect-levers` parse, an explicitly empty value meaning the bare slate), :303 (the substrate-lever preflight, delegating to `substrate_slate_mismatches`) with its TWO call sites at :524 on the dry-run path and :650 on the real one, :441 (two parallel workers by default on featherless) and :461 (four attempts per seed), :547-551 (the key preflight; only `${FEATHERLESS_API_KEY:0:8}` is ever printed), :566 (`REQUIRED_PROMPT_SET="qwen3_6_27b"`), :588 (`REQUIRED_SET_OWNER_MODEL="Qwen/Qwen3.6-27B"`), :660 (the set dir created before any spend), :669 (the roster descriptor written before any spend), :737 (the stage created under `dirname "$SAMPLE_DIR"`); `scripts/record_ml_corpus.sh`:156 (`REQUIRED_PROMPT_VERSIONS`, all four templates locked at v4 TODAY), :499 (`check_prompt_version_registry`) called at :910 on the REAL path only — the dry-run exits at :829 after echoing the locked map at :796, so the comparison this smoke makes is not one the preview performs, :607 (`check_replay_provenance`, whose `deadline_default` refusal at :676 is the freeze guard), :194-196 (the fixed per-set seed ranges — the corpus wrapper has no seed-slice flag); `scripts/verify_samples.sh`:16-23 (a bare invocation walks EVERY set under the samples root); `scripts/validity_gate.py`:78-93 (`--expected-model`, `--require-zero-cost`); `eval/validity.py`:26-56 (the ten named checks — :49 `cost_and_provenance_exact`, which also requires every game's substrate stamp to equal the canonical snapshot, and :54 `byte_identical_reconstruction`); `scripts/measure_baseline.py`:726 (`--honesty`) and :716 (`--solvability`); `api/replay_loader.py`:603 (`_assert_substrate_matches`, reached at :1101); `scripts/check_doc_facts.py`:1722 (`check_audits_index`, which errors on any un-indexed top-level audit) with the real-repo assertion at `tests/scripts/test_check_doc_facts.py`:236; `scripts/verify_ml_evidence.py`:2359 (`inventory_problems`, reached from `run_availability` at :2550) against `docs/artifacts.md`:107, whose row reads `158 files` and `git ls-files audits` returns 158 at HEAD. AGENTS.md craft rules 2, 5 and 7.
**Complexity:** Small
**Record impact:** the record itself — these are the first live seeds of the Phase-21 recording window. The bytes land in a scratch directory outside the repository and are never committed; no file under `replays/` moves at this task.
**Measurement:** `uv run python scripts/validity_gate.py "$SMOKE_DIR" --expected-model Qwen/Qwen3.6-27B --require-zero-cost` PASS with all ten checks quoted; `bash scripts/verify_samples.sh "$SMOKE_DIR"` reconstructs every smoke seed byte-identically, twice; `uv run python scripts/measure_baseline.py --honesty "$SMOKE_DIR"` exits 0 and prints every cell family with denominators — run first on the FIRST completed seed alone; and the committed record is untouched: `bash scripts/verify_samples.sh` bare is clean and `git status --porcelain replays/` is empty.

The standing cadence rule is smoke before record: a handful of seeds, STOP-and-report, with an
abandon branch that is a real branch and not a formality. The price of skipping it is known to the
hour — the last record spent **23h25m42s** of operator wall over 300 games at $0
(`audits/audit-phase-20-baseline-7.md` §0.3), and the smoke that preceded it cost 44 minutes and
five seeds. That smoke is also the reason this one exists in its current shape: its verdict was
ABANDON (`audits/audit-phase-20-smoke.md` §0), because the primary honesty instrument raised on
freshly recorded bytes the validity gate had just passed on all ten checks. The
recording half was clean and the measuring half was not, and no cheaper instrument could have found
that.

The dependency list is the smoke's whole premise and is not padding. Five of the seven upstream
contracts change what gets recorded, so a smoke run before any one of them lands would certify
bytes the record will not produce; the sixth is the win-ordering repair, whose recorded effect is
expected to be nil on these seeds but whose merge still moves the source state this report names.
The seventh is the recorder hardening, and it is here for a reason the register measured: the
corpus recorder declares a run failed on ONE dead-owner probe where the sibling wrapper needs a
ten-poll streak (B-18), and every one of its 54 tests stops before a seed stages, so its recording
engine executes in no test (B-21). Two parallel workers on a hosted provider is exactly the
configuration that produces the benign release-then-exit race those findings describe, which makes
this five-seed run the first live exercise of the hardened path rather than a formality.

What is under test here is a *corrected* substrate, not a new lever slate, and the distinction
shapes every criterion below. The next record is maintenance-of-record: it re-records the committed
sets on repaired bytes, publishes every instrument cell before and after, and declares no verdict.
Nothing in this smoke may be read as a bar, met or missed — the standing canon is that **baseline 7
is canon by explicit owner override of a FINDING verdict**, bars 1 and 2 missed
(`audits/audit-phase-20-baseline-7.md` §6.1), so a report that quietly re-imported bar language
would be describing a decision procedure this phase does not have.

The slate is bare, and that is new. At HEAD `orchestrator/replay.py`:524-546 carries twenty-one
retired levers whose env gates were deleted at the records that adopted them, and :568-570 carries
exactly ONE live toggle, `impostor_roll_call`, which stays OFF. So the smoke runs with **no
`AILIBI_*` lever export at all** and `--expect-levers ""` — the explicitly empty value the argument
parse at :248-255 accepts as the bare slate. Two independent reads must still agree, and the smoke
is where disagreement is cheap: the wrapper's preflight at :303 refuses a stale export before
anything stages, and the recorded `game_over` rows self-describe through `substrate_flag_snapshot`
at :591. A slate that disagrees between those two reads is a STOP, not a footnote. One consequence
is worth stating because it inverts a note the last record carried: with no lever exports to carry,
the gate-and-instrument shell no longer needs to mirror the recording shell — but `impostor_roll_call`
must be unset in BOTH, or `api/replay_loader.py`:603 refuses the reconstruction.

Six behavioural repairs ride these bytes and each one has a discriminating marker, which is what
makes this smoke more than a liveness check. The register measured every one of them over the
committed record, so each has a committed reference value to read the smoke against: the taught
oracle line (A-6, 45 of 326 flag-bearing meetings leaking, 0 of 342 without), the ballot render that
drops every structured field (A-17, 0 of 3,350 vote prompts carrying a current-meeting claim line),
the actions recorded as submitted with no consequence (A-14, 2,166 of 35,350), the guard-redirected
ballots with no machine-readable provenance (A-3, 120 ballots and 25 flipped outcomes), the belief
line that contradicts its own sightings (B-8, 19% of rendered rows) and the doubled vent mint
(A-31, 1,505 pairs, with 27 heard-only rows that are 27/27 impostors past the firewall). Any of
these still reading its pre-repair shape on freshly recorded bytes is a STOP: it means a merged
repair does not reach the live path, and the record would freeze it into 300 games.

There is one more thing this smoke can catch in a minute that the record would hit hours in. The
corpus recorder locks the four template versions in source at `scripts/record_ml_corpus.sh`:156,
today at v4 for all four, and asserts the live registry against that lock at :910 — on the REAL
path only. Its dry-run exits at :829 after merely ECHOING the locked map at :796. So if the dialect
repair bumps the set to v5 and nothing moves that lock, the preview looks healthy and legs two and
four of the record abort at preflight after the samples legs have already been spent. The smoke
compares the two directly, before any of it is spent.

The output is a report and a fork. GO means the recording window opens on this exact source state.
ABANDON means the defect is described concretely enough to author a follow-up contract, the routing
is named, and the record does not start. The deliverable is the report either way, so **this PR
merges on both branches** — a smoke that found something is the smoke working. Two operating rules
carry from the last window and are contract items here rather than advice: the honesty instrument
runs on the FIRST completed seed before the rest queue (`audits/audit-phase-20-smoke.md` §13 note
3), and the smoke bytes are PRESERVED at a stable path named in the report, because when the last
smoke's defect was repaired the re-measure ran on the preserved bytes at $0 and no seed was
re-recorded (§14 addendum). Finally, this report fixes the source state it certifies: it names the
sha, and any merge into `agents/`, `meetings/`, `observation/`, `orchestrator/` or the prompt set
between this report and the record reopens the window — the smoke then runs again from zero, on the
changed source, with every number re-derived.

**Files in scope:**
- audits/audit-phase-21-smoke.md; (new: the smoke report — recorded configuration, per-seed table, the gate output, the corrected-behaviour observation table, the honesty and solvability cells, the watch-item scan, operating data, and the GO/ABANDON call)

**Files NOT in scope:**
- replays/ (the smoke records into a scratch directory outside the repository; no committed byte moves at this task)
- every code path (no edits: a defect found here routes to a named follow-up contract before the record — no papering fixes inside a recording session)
- scripts/refresh_samples.sh, scripts/record_ml_corpus.sh (driven, never edited; a wrapper defect is reported and routed)
- tasks/phase-21.md (the phase-doc surgery for any routed follow-up is owner-side, in its own PR)
- audits/README.md and docs/artifacts.md (the `audits/README.md` index line and the `docs/artifacts.md` `audits/`-row bump ride this PR as the standing index amendment — the 20.34 precedent — not as scope entries; both counts are re-read at implementation time, never hard-pinned)

**Definition of done:**
- [ ] Five seeds of the 9p2i roster are recorded into a scratch directory OUTSIDE the repository at the bare slate — no `AILIBI_*` lever export, `--expect-levers ""`, `AILIBI_PROMPT_SET=qwen3_6_27b`, Featherless `Qwen/Qwen3.6-27B` non-thinking, two parallel workers — with the resolved environment and the seed-selection rationale quoted in the report, and `git status --porcelain` showing no replay bytes and no staging directory at the end.
- [ ] The prompt-set version the seeds actually rendered is READ OUT of a recorded meeting prompt and out of the recorded MANIFEST rows, never inferred from the registry; and the corpus recorder's locked map at `scripts/record_ml_corpus.sh`:156 is compared against the live `orchestrator.game.PROMPT_VERSION_SETS["qwen3_6_27b"]` with the result quoted verbatim — a disagreement is a STOP, because that assertion runs at :910 on the real path only and the dry-run at :796 merely echoes the lock.
- [ ] `uv run python scripts/validity_gate.py "$SMOKE_DIR" --expected-model Qwen/Qwen3.6-27B --require-zero-cost` PASSes with all ten checks named individually in the report, `byte_identical_reconstruction` and `cost_and_provenance_exact` quoted verbatim, and `bash scripts/verify_samples.sh "$SMOKE_DIR"` run twice under the same environment reproduces byte-identically both times.
- [ ] The recorded substrate stamp is read out of the five `game_over` rows rather than a live snapshot: the twenty-one retired keys all True, `impostor_roll_call` False, and `orchestrator.replay.substrate_slate_mismatches` returning empty against the declared bare slate. Any disagreement between the recorded stamp and the wrapper's preflight is reported as a defect, never reconciled by hand.
- [ ] `uv run python scripts/measure_baseline.py --honesty` is run on the FIRST completed seed ALONE, before the remaining seeds queue, and again over the whole set; both exit 0 and both are quoted with denominators. A raise on either is a STOP and the run does not continue past it. If the first completed seed carries zero meetings the probe is recorded as VACUOUS and re-run on the first meeting-bearing seed — a vacuous probe is not a passed probe.
- [ ] Each of the six corrected behaviours is reported as OBSERVED on the smoke bytes with counts and denominators beside its committed reference value: the taught oracle line absent from every rendered proof block and the spoken oracle net measured over free_text, ballot rationales and claim reasons; structured testimony rows present in the vote-ballot prompts; recorded action rows carrying an explicit disposition, with the actions queued behind a meeting trigger marked discarded; guard-redirected ballots carrying their machine-readable provenance field; the belief line's last-seen row agreeing with the same prompt's own sighting rows; and exactly one memory row minted per witnessed vent, with no audible copy surviving the teammate firewall. Any behaviour the five seeds never exercise is named UNTESTED rather than implied green — the win-ordering repair in particular is expected to go unexercised at this n, and the report states the verifier's note that both realized cases in the committed record recorded the correct winner.
- [ ] Backward compatibility of the record-fidelity fields is proven at $0 on the committed bytes, which carry none of them: `bash scripts/verify_samples.sh` bare reconstructs every committed set under the loader defaults, and the report states that conclusion rather than implying it.
- [ ] The watch item carried from the last two records is scanned by hand and not delegated to the gate: no recorded failed-call row carries `error_type == "deadline_default"` under either shape, and the recorder's own summary counters for lost openings and vote defaults are quoted. The freeze guard at `scripts/record_ml_corpus.sh`:607 refused two seeds for exactly this at the last record.
- [ ] Operating data for the record's plan is measured and recorded: per-seed wall clock, tokens per call and per meeting, worker occupancy, and every retry or transport blip absorbed — and the four-leg wall-clock projection is re-derived from these measured tokens, stated as a bracket, so the next contract's pre-committed projection is measured rather than inherited.
- [ ] The hardened worker path is exercised as configured and reported: two parallel workers actually claimed seeds from the shared queue, the run log is scanned for any lock, dead-owner or claim diagnostic, and any such line is reported with its timestamp and worker id. A spurious abort here is a defect to describe and route, never something to clear by re-running.
- [ ] The STOP criteria in the implementation hint are quoted verbatim in the report and each is read against the run with a NOT MET / MET line; no criterion is invented mid-run, and a criterion that does not reach the observed case is recorded as not reaching it rather than stretched.
- [ ] GO or ABANDON is recorded in one line with the criterion it was ruled against beside it. On ABANDON the defect carries symptom, seed, suspected file and a reproduction; the follow-up is named as a routing slot for the owner to land; and the report states plainly that the record does not start.
- [ ] The smoke bytes are PRESERVED at a stable absolute path named in the report, not deleted at the end of the session, so a routed repair can be re-measured on the same bytes at $0 without re-recording a seed; the report states the path and the byte count.
- [ ] Committed bytes untouched: `bash scripts/verify_samples.sh` bare still verifies every committed set clean, and no file under `replays/` differs from HEAD.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Dependency contract check
Run these before editing. If any fail, stop and report — your dependencies are not where this task expects them.

- `uv run python -c "import orchestrator.replay"`
- `uv run python -c "import eval.meeting_quality"`
- `uv run python -c "import eval.watchability.SupplyFloors"`
- `uv run python -c "import meetings.schemas"`
- `uv run python -c "import eval.replay_walk.ReplayWalkConfig"`
- `uv run python -c "import engine.tick"`
- `uv run python -c "import training.surrogate.dataset"`
- `uv run python -c "import training.surrogate.runner"`
- `uv run python -c "import training.conviction.fidelity"`
- `uv run python -c "import training.rewards"`
- `uv run python -c "import training.bakeoff.harness"`
- `uv run python -c "import training.surrogate.fidelity"`
- `uv run python -c "import eval.accusation_calibration"`
- `uv run python -c "import eval.deduction_metrics"`
- `uv run python -c "import meetings.transcript"`
- `uv run python -c "import eval.vj_instruments"`
- `uv run python -c "import eval.vj_instruments.VJInstrumentReport"`
- `uv run python -c "import eval.vj_instruments.VJMeetingRow"`
- `uv run python -c "import agents.strategic.prompts.loader"`

## Pre-flight checklist
- Read AGENTS.md, the architecture routing it names, and the task section before editing.
- Inspect the current implementation before editing.
- Identify the existing local patterns for the files in scope and follow them.
- Re-verify every file:line anchor the contract cites at HEAD before editing; if an anchor has moved, record the true location under `## Decisions` — never edit from a stale line number.
- Grep every consumer of each symbol, path, or constant you will change (the blast radius); if a hit lies outside the files in scope, stop and ask rather than widening scope silently.

## Craft rules (AGENTS.md "Craft rules" — non-negotiable for every file you touch)
- Lead with intent: a docstring or comment states what the code does and why, now; provenance (task ids, audit paths) is at most one trailing line. Do not narrate history in source.
- A gate must be able to fail: every new test or check that guards an invariant ships with a planted or perturbed case proving it bites, and checks the semantics it claims, not only the shape.
- Retire means delete: when a lever graduates or a branch dies, delete the resolver, the parameter, the branch and the tests that pin them; keep only the stamp key and one history line.
- No internal dialect on user-facing surfaces: UI copy, rendered game prompts, spoken text and README carry no task or audit ids, no threshold arithmetic, and no undefined jargon.
- Claims are verifiable-shaped: a doc claim names the mechanism that enforces it; a number is recomputed from committed bytes and its command goes in the PR.

## Constraints and non-goals
Do not modify DESIGN.md.
Do not modify AGENT_IMPLEMENTATION.md.
Do not modify tasks/phase-*.md unless this task explicitly lists those files in scope.
Do not implement work outside this task.

## Verification checklist
- Run every command listed in the Definition of done.
- If the contract carries a `**Measurement:**` field, run that command and paste its output into the PR's `## Summary`; a Measurement that cannot be run is reported under `## Questions`, never asserted.
- Run `git diff --name-only` and confirm the diff stays within scope.
- If any Definition of done item is unchecked, report it explicitly in the PR description instead of declaring the task complete.

## Decisions vs questions
- If something is **ambiguous and blocking** (you cannot make a reasonable choice without further information): stop, open a draft PR, add a `## Questions` section, request review.
- If something is **ambiguous but resolvable by judgment** (a default value, a tie-break, a naming choice): document the choice in a `## Decisions` section in the PR description and proceed.

## Output expectation
Open a PR from branch `phase-21-smoke` with a title like `task 21.14: the smoke (operator): five seeds on the corrected substrate, stop-and-report, and an abandon branch that still merges`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing Wave-0 register entries, read in full including verifier notes — `audits/review-2026-08-26/A/collated-findings.md`: A-6 at :693 [CONFIRMED, P1] (the two template lines that teach the oracle dialect; causal separation is perfect over the 668 committed meetings — leak 45/326 = 13.8% where the proof block renders, 0/342 where it does not), A-17 at :2086 [ADJUSTED] (the ballot render references exactly one turn field; 0 of 3,350 vote prompts in the 9p2i sets carry a current-meeting claim line), A-34 at :3750 [CONFIRMED] (the redaction sentence normalizes to the empty skeleton and is the largest repeated voice cluster in both 9p2i sets), A-14 at :1718 [CONFIRMED] (2,166 of 35,350 recorded actions = 6.13% recorded as submitted with no consequence, including 36 kills, 99 reports, 17 emergency calls), A-3 at :242 [ADJUSTED] (120 guard-redirected ballots, 25 flipped meeting outcomes, 3 ejections no voter authored; the 107-of-120 rationale figure needs case-insensitive matching, 101 exact-case), A-31 at :3501 [CONFIRMED] (1,505 double-minted witness-side vent rows, 0 witnessed-only, 27 distinct heard-only rows that are 27/27 impostors past the teammate firewall), A-1 at :60 [ADJUSTED] (the win check skipped on a meeting-trigger tick is SPECIFIED and test-pinned; the verifier's note binds this contract — both realized cases recorded the correct winner, so this is a latent-correctness repair with zero realized exposure); `audits/review-2026-08-26/B/collated-findings.md`: B-8 [CONFIRMED] (`working.last_seen` has one production writer, so the belief line contradicts the same prompt's own sightings in 19% of rendered rows), B-18 [ADJUSTED] (the corpus recorder aborts on ONE dead-owner probe where the sibling wrapper needs a ten-poll streak; blast radius is a spurious abort plus restart latency, not a lost leg), B-21 [CONFIRMED] (all 54 tests of the corpus recorder stop before any seed stages, so its recording engine executes in no test). Precedents: `tasks/phase-20.md` Task 20.35 (the smoke this one mirrors); `audits/audit-phase-20-smoke.md` §0 and §12 (the ABANDON, and the fact that no ratified criterion named the class that produced it), §9 (the cells that did not exist because the instrument raised), §10 (the measured operating data and the two re-derived wall-clock projections), §13 note 3 (run the honesty instrument on the FIRST completed seed, not after the set) and the §14 addendum (the re-measure on the PRESERVED smoke bytes, at $0, which is why this task preserves its bytes); `audits/audit-phase-20-baseline-7.md` §0.2 (the protocol actually run, two parallel seed workers, the key never reproduced), §0.3 (23h25m42s of operator wall for 300 games at $0) and §0.4 (two `(deadline_default)` seeds refused at the freeze guard and re-recorded in 12m33s). Anchors re-verified at HEAD `d8ec0a1c`: `orchestrator/replay.py`:524-546 (`_RETIRED_ALWAYS_ON_LEVERS`, twenty-one keys), :568-570 (`_TOGGLEABLE_LEVER_RESOLVERS` — ONE live toggle, `impostor_roll_call`), :578-580 and :585-588 (the stamp key order), :591 (`substrate_flag_snapshot`), :623 (`retired_levers_stamped_off`), :651 (`substrate_slate_mismatches` — the one comparison the wrapper preflight, this report and the record must all use rather than re-derive); `scripts/refresh_samples.sh`:36-37 (`AILIBI_SAMPLE_DIR`, `AILIBI_MANIFEST` defaulting under it), :247-260 (the `--dry-run` and `--expect-levers` parse, an explicitly empty value meaning the bare slate), :303 (the substrate-lever preflight, delegating to `substrate_slate_mismatches`) with its TWO call sites at :524 on the dry-run path and :650 on the real one, :441 (two parallel workers by default on featherless) and :461 (four attempts per seed), :547-551 (the key preflight; only `${FEATHERLESS_API_KEY:0:8}` is ever printed), :566 (`REQUIRED_PROMPT_SET="qwen3_6_27b"`), :588 (`REQUIRED_SET_OWNER_MODEL="Qwen/Qwen3.6-27B"`), :660 (the set dir created before any spend), :669 (the roster descriptor written before any spend), :737 (the stage created under `dirname "$SAMPLE_DIR"`); `scripts/record_ml_corpus.sh`:156 (`REQUIRED_PROMPT_VERSIONS`, all four templates locked at v4 TODAY), :499 (`check_prompt_version_registry`) called at :910 on the REAL path only — the dry-run exits at :829 after echoing the locked map at :796, so the comparison this smoke makes is not one the preview performs, :607 (`check_replay_provenance`, whose `deadline_default` refusal at :676 is the freeze guard), :194-196 (the fixed per-set seed ranges — the corpus wrapper has no seed-slice flag); `scripts/verify_samples.sh`:16-23 (a bare invocation walks EVERY set under the samples root); `scripts/validity_gate.py`:78-93 (`--expected-model`, `--require-zero-cost`); `eval/validity.py`:26-56 (the ten named checks — :49 `cost_and_provenance_exact`, which also requires every game's substrate stamp to equal the canonical snapshot, and :54 `byte_identical_reconstruction`); `scripts/measure_baseline.py`:726 (`--honesty`) and :716 (`--solvability`); `api/replay_loader.py`:603 (`_assert_substrate_matches`, reached at :1101); `scripts/check_doc_facts.py`:1722 (`check_audits_index`, which errors on any un-indexed top-level audit) with the real-repo assertion at `tests/scripts/test_check_doc_facts.py`:236; `scripts/verify_ml_evidence.py`:2359 (`inventory_problems`, reached from `run_availability` at :2550) against `docs/artifacts.md`:107, whose row reads `158 files` and `git ls-files audits` returns 158 at HEAD. AGENTS.md craft rules 2, 5 and 7.), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
