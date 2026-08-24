# Agent Prompt — 20.35 The smoke record (operator): 3–5 seeds, STOP-and-report, with the abandon branch

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-20.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 20.35 — The smoke record (operator): 3–5 seeds, STOP-and-report, with the abandon branch, anchored to audits/review-2026-08-19/D/FINAL-synthesis.md §4 wave 2 (the pre-record protocol — the $0 offline counterfactual "de-risks a 23 h event"; the record order; the primary bars) + §6 fact 2 ("The record itself runs on 917 lines of untested Bash (C-74). Harden that first … or the 23 h is at risk"); audits/review-2026-08-19/B/collated-findings.md C-74 (P1: `refresh_samples.sh` = 917 lines of worker pool + mkdir mutex + per-seed retry, `tests/scripts/test_refresh_samples.py` = 915 lines / 59 all-`--dry-run` tests, none touching `run_worker`/`_acquire_lock`/`record_one_seed` — CLOSED at HEAD by Task 20.21, PR #359: the wrapper is now 1,052 lines with `_acquire_lock` at scripts/refresh_samples.sh:774, `record_one_seed` at :824, `run_worker` at :936, and tests/scripts/test_refresh_samples.py is 1,610 lines / 80 tests carrying a hermetic fake-provider RECORDING family (:1053 onward) that drives `run_worker` / `claim_next_seed` / `record_one_seed` / `_acquire_lock` end to end, asserted by name off a `bash -x` trace at :1355-1361); scripts/refresh_samples.sh:36-37 (`AILIBI_SAMPLE_DIR`, and `AILIBI_MANIFEST` defaulting under it), :566 (`REQUIRED_PROMPT_SET="qwen3_6_27b"`), :588 (`REQUIRED_SET_OWNER_MODEL="Qwen/Qwen3.6-27B"`), :289-326 (the substrate-lever preflight — since Task 20.33 a POSITIVE whole-slate equality against the operator-declared `--expect-levers`, delegating the comparison to `orchestrator.replay.substrate_slate_mismatches`; NOT the baseline-6 blacklist this contract was authored against), :55 + :61-65 (the `--expect-levers` usage block) and :248-260 (its argument parse, an explicitly empty value meaning the bare slate), :524-526 and :649-652 (the preflight's TWO call sites — the dry-run path refuses as well as the real path), :669-673 (the pre-spend roster descriptor write, after `mkdir -p "$SAMPLE_DIR"` at :660), :737 (the stage dir created under `dirname "$SAMPLE_DIR"`); scripts/verify_samples.sh:16-23 (a bare invocation walks EVERY set under the samples root); scripts/validity_gate.py:78-85 (`--expected-model`) and :86-93 (`--require-zero-cost`); eval/validity.py:26-56 (the ten named checks — still exactly ten; :49 `cost_and_provenance_exact`, which since Task 20.33 ALSO requires every game's substrate-flag stamp to equal the canonical snapshot with the canonical key set, and :54 `byte_identical_reconstruction`); orchestrator/replay.py:587-599 (`_TOGGLEABLE_LEVER_RESOLVERS` — nine keys at HEAD: `impostor_roll_call` plus the eight Phase-20 levers, in registration order), :607-609 (`TOGGLEABLE_SUBSTRATE_FLAG_KEYS`), :614-618 (`SUBSTRATE_FLAG_KEYS`), :620 (`substrate_flag_snapshot`), :652 (`substrate_slate_mismatches` — the one comparison the wrapper preflight, the record and this report must all use rather than re-derive); tasks/phase-18.md:941-944 (the standing record watch item — the `cost_and_provenance_exact` blindness around the `(deadline_default)` synthetic marker, and "a seed whose opening defaults is a FAILED recording and re-records"); audits/audit-phase-16-baseline-4.md §7 (the precedent: 9p2i seed 5 re-recorded after a `(deadline_default)` phantom, its MANIFEST row stamped honestly); tasks/phase-10.md:1133 (the 5-seed smoke that covered no emergency meeting — the full run then crashed on the uncovered path), :668-680 (smoke-first STOP-for-go and the smoke-abandon evidence branch); audits/audit-phase-20-preregistration.md and audits/audit-phase-20-counterfactual.md (the ratified bars, the decision rule, and the abandon criteria this smoke executes rather than invents). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-20.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-20-smoke-record`
**Depends on:** 20.34 — the offline counterfactual memo must be committed before the first live seed: it fixes the abandon criteria this smoke rules against, and its published predictions are what the smoke's directional read is compared to.
**Section refs:** audits/review-2026-08-19/D/FINAL-synthesis.md §4 wave 2 (the pre-record protocol — the $0 offline counterfactual "de-risks a 23 h event"; the record order; the primary bars) + §6 fact 2 ("The record itself runs on 917 lines of untested Bash (C-74). Harden that first … or the 23 h is at risk"); audits/review-2026-08-19/B/collated-findings.md C-74 (P1: `refresh_samples.sh` = 917 lines of worker pool + mkdir mutex + per-seed retry, `tests/scripts/test_refresh_samples.py` = 915 lines / 59 all-`--dry-run` tests, none touching `run_worker`/`_acquire_lock`/`record_one_seed` — CLOSED at HEAD by Task 20.21, PR #359: the wrapper is now 1,052 lines with `_acquire_lock` at scripts/refresh_samples.sh:774, `record_one_seed` at :824, `run_worker` at :936, and tests/scripts/test_refresh_samples.py is 1,610 lines / 80 tests carrying a hermetic fake-provider RECORDING family (:1053 onward) that drives `run_worker` / `claim_next_seed` / `record_one_seed` / `_acquire_lock` end to end, asserted by name off a `bash -x` trace at :1355-1361); scripts/refresh_samples.sh:36-37 (`AILIBI_SAMPLE_DIR`, and `AILIBI_MANIFEST` defaulting under it), :566 (`REQUIRED_PROMPT_SET="qwen3_6_27b"`), :588 (`REQUIRED_SET_OWNER_MODEL="Qwen/Qwen3.6-27B"`), :289-326 (the substrate-lever preflight — since Task 20.33 a POSITIVE whole-slate equality against the operator-declared `--expect-levers`, delegating the comparison to `orchestrator.replay.substrate_slate_mismatches`; NOT the baseline-6 blacklist this contract was authored against), :55 + :61-65 (the `--expect-levers` usage block) and :248-260 (its argument parse, an explicitly empty value meaning the bare slate), :524-526 and :649-652 (the preflight's TWO call sites — the dry-run path refuses as well as the real path), :669-673 (the pre-spend roster descriptor write, after `mkdir -p "$SAMPLE_DIR"` at :660), :737 (the stage dir created under `dirname "$SAMPLE_DIR"`); scripts/verify_samples.sh:16-23 (a bare invocation walks EVERY set under the samples root); scripts/validity_gate.py:78-85 (`--expected-model`) and :86-93 (`--require-zero-cost`); eval/validity.py:26-56 (the ten named checks — still exactly ten; :49 `cost_and_provenance_exact`, which since Task 20.33 ALSO requires every game's substrate-flag stamp to equal the canonical snapshot with the canonical key set, and :54 `byte_identical_reconstruction`); orchestrator/replay.py:587-599 (`_TOGGLEABLE_LEVER_RESOLVERS` — nine keys at HEAD: `impostor_roll_call` plus the eight Phase-20 levers, in registration order), :607-609 (`TOGGLEABLE_SUBSTRATE_FLAG_KEYS`), :614-618 (`SUBSTRATE_FLAG_KEYS`), :620 (`substrate_flag_snapshot`), :652 (`substrate_slate_mismatches` — the one comparison the wrapper preflight, the record and this report must all use rather than re-derive); tasks/phase-18.md:941-944 (the standing record watch item — the `cost_and_provenance_exact` blindness around the `(deadline_default)` synthetic marker, and "a seed whose opening defaults is a FAILED recording and re-records"); audits/audit-phase-16-baseline-4.md §7 (the precedent: 9p2i seed 5 re-recorded after a `(deadline_default)` phantom, its MANIFEST row stamped honestly); tasks/phase-10.md:1133 (the 5-seed smoke that covered no emergency meeting — the full run then crashed on the uncovered path), :668-680 (smoke-first STOP-for-go and the smoke-abandon evidence branch); audits/audit-phase-20-preregistration.md and audits/audit-phase-20-counterfactual.md (the ratified bars, the decision rule, and the abandon criteria this smoke executes rather than invents)
**Complexity:** Small
**Record impact:** the record itself — the first live seeds of the Phase-20 recording window; the bytes land in a scratch directory and never enter the tree.
**Measurement:** `uv run python scripts/validity_gate.py "$SMOKE_DIR" --expected-model Qwen/Qwen3.6-27B --require-zero-cost` PASS (all ten checks green, quoted in the report); `bash scripts/verify_samples.sh "$SMOKE_DIR"` reconstructs every smoke seed byte-identically; `uv run python scripts/measure_baseline.py --honesty "$SMOKE_DIR"` prints the cells the report quotes with denominators; and the committed sets are untouched — `bash scripts/verify_samples.sh` (bare) clean and `git status --porcelain replays/` empty.

The standing cadence rule is smoke before full-record: 3–5 seeds, STOP-and-report, with an
explicit abandon branch for guard trips. Phase 20 buys one measurement with roughly 23 h of
operator wall across four sets (audits/review-2026-08-19/D/FINAL-synthesis.md §4 wave 2,
which prices the record at "~23 h operator wall, $0 flat-rate"), and the review named the
hazard on the way in: the recorder is 917 lines of Bash whose worker pool, mkdir mutex and
per-seed retry had zero automated coverage (C-74 in
audits/review-2026-08-19/B/collated-findings.md). Task 20.21 CLOSED that before this task —
PR #359, merged: the wrapper is 1,052 lines and its test file 1,610 lines / 80 tests, with a
fake-provider family that records into a scratch dir and drives `run_worker`,
`claim_next_seed`, `record_one_seed` and `_acquire_lock` for real. This is the cheap proof — five seeds, an hour, $0 — that the whole
stack is live and coherent before the expensive event starts: the lever slate, the v4 prompt
set, the recorder's real worker path, the substrate stamp, the validity gate, and the
honesty instruments reading a freshly recorded set rather than committed bytes.

The slate under test is the phase's, exactly: all eight Phase-20 levers ON,
`impostor_roll_call` OFF, prompt set `qwen3_6_27b` at v4, Featherless
`Qwen/Qwen3.6-27B` non-thinking, 9p2i roster. Two independent things must agree and the
smoke is where the disagreement is cheap to find. First, the wrapper's substrate-lever
preflight refuses a stale `AILIBI_*` export before any seed stages
(scripts/refresh_samples.sh:289-326, called at :524-526 on the dry-run path and :649-652 on the real one) — the guard that exists because a mis-substrated
multi-hour record only reveals itself in the MANIFEST afterwards. Second, the recorded
bytes self-describe: `substrate_flag_snapshot` (orchestrator/replay.py:620) folds
`_TOGGLEABLE_LEVER_RESOLVERS` (:587-599) into the `SUBSTRATE_FLAG_KEYS` ordering (:614-618) and
stamps it into every `game_over` row, so the report reads the slate out of the recorded
games rather than out of the shell it was launched from. A slate that disagrees between
those two reads is an ABANDON, not a footnote.

The seed slate is a coverage decision, not a convenience one, and this project has already
paid for the lesson: the phase-10 smoke ran 5 seeds green, fired zero emergency meetings, and
the full run then crashed on that uncovered path (tasks/phase-10.md:1133). Re-derived at HEAD
over the committed baseline-6 `replays/samples/9p2i` (50 seeds, 165 meetings — the same
denominator the honesty instrument's venting-participant cell uses): every seed carries at
least 2 meetings and at least 1 ejection, so meeting-outcome memory is covered by any slate;
but the recorded contradiction rows are 96 `vent_sighting`, 76 `alibi_vs_sighting` and 8
`alibi_conflict`, with `alibi_vs_sighting` present in only 33 of 50 seeds and `alibi_conflict`
in 6 (seeds 12, 21, 28, 31, 40, 47). Seeds 0–4 carry 0, 2, 0, 0 and 0 `alibi_vs_sighting`
rows: four of five would exercise the phase's centrepiece lever — grounded prosecution —
zero times. Baseline-6 coverage is only a proxy, because the corrected substrate moves
trajectories; so the slate is chosen from it and coverage is then reported as OBSERVED on
the smoke bytes, with any lever the five seeds never exercised named as untested rather
than implied green.

The output is a report and a fork. GO means the recording window opens and the adopting
record starts on frozen source. ABANDON means the defect is described concretely enough to
author a follow-up contract, the routing is named, and the record does not start. Unlike the
phase-10 attempt-1 evidence branch — closed UNMERGED because its deliverable was the record —
the deliverable here IS the report, so this PR merges on both branches: a smoke that found
something is the smoke working. The freeze is ALREADY in force and this task adds nothing to it: the ratified
pre-registration §9 declares the freeze AT THE 20.33 MERGE (fc5cf719, merged), covering
`agents/`, `meetings/`, `observation/`, `orchestrator/` and the prompt set — so this smoke runs
inside the window rather than opening it, and no merge into those trees may land
between this report and the record, and a routed fix reopens the window — the
smoke then runs again from zero, on the changed source, with every number re-derived.

**Files in scope:**
- audits/audit-phase-20-smoke.md; (new: the smoke report — per-seed outcome, validity gate, the honesty cells on the smoke seeds, any guard trip, the GO/ABANDON call)
- audits/README.md; (one index row for the new audit — `scripts/check_doc_facts.py::check_audits_index` (:1322) errors on any un-indexed top-level `audits/*.md`, and `tests/scripts/test_check_doc_facts.py:191` runs `check_facts` against the REAL repo, so without this row the DoD's `uv run pytest` and `bash scripts/check.sh` lines cannot pass. Task 20.34 recorded the same two files at merge)
- docs/artifacts.md; (:107, the `audits/` in-tree inventory row — `scripts/verify_ml_evidence.py::inventory_problems` (:2174, reached from `run_availability` at :2558) compares the stated `N files` against `git ls-files audits`, pinned on the real repo by `tests/scripts/test_verify_ml_evidence.py:1411-1413`. `git ls-files audits` = 151 at HEAD and the row reads `151 files`; the smoke audit makes it 152)

**Files NOT in scope:**
- replays/samples/, replays/ml_corpus/ (the smoke records into a scratch directory that is NOT committed; committed bytes do not move at this task)
- every code path (no edits: a defect found here routes to a named follow-up contract before the adopting record — no papering fixes inside the recording session)
- tasks/phase-20.md (the phase-doc surgery for any routed follow-up is owner-side, in its own PR)
- audits/audit-phase-20-preregistration.md, audits/audit-phase-20-counterfactual.md (ratified/committed upstream; this report reads against them, errata only)

**Definition of done:**
- [ ] Five seeds of 9p2i recorded into a scratch directory OUTSIDE `replays/` at the full slate (the eight Phase-20 levers ON, `impostor_roll_call` OFF, `AILIBI_PROMPT_SET=qwen3_6_27b` at v4, Featherless `Qwen/Qwen3.6-27B`), with the resolved environment and the seed-selection rationale quoted in the report; `git status --porcelain` shows no replay bytes and no staging dir at the end.
- [ ] `uv run python scripts/validity_gate.py "$SMOKE_DIR" --expected-model Qwen/Qwen3.6-27B --require-zero-cost` PASS with all ten checks named individually in the report (`byte_identical_reconstruction` and `cost_and_provenance_exact` quoted verbatim), and a second run of the same seeds under the same environment reproduces byte-identically.
- [ ] The recorded substrate stamp is read out of the five `game_over` rows (not out of a live snapshot) and carries the eight Phase-20 lever keys True with `impostor_roll_call` False; any disagreement between the recorded stamp and the wrapper's preflight is reported as a defect, not reconciled by hand.
- [ ] The honesty cells are computed on the smoke seeds and quoted with numerators and denominators beside the counterfactual memo's predicted direction, each labelled directional-only at this n; no pre-registered bar is declared met or missed on five seeds, and the report says so in those words.
- [ ] Lever coverage is reported as OBSERVED on the smoke bytes (which levers actually fired, with counts), and any lever the slate never exercised is named as untested.
- [ ] Operating data for the record's re-plan is recorded: per-seed wall clock, tokens per call and per meeting, worker occupancy, and every retry or transport blip the run absorbed — so the roughly 23 h projection is re-derived from measured tokens before the adopting record starts.
- [ ] GO or ABANDON is recorded verbatim against the abandon criteria in `audits/audit-phase-20-counterfactual.md` — no criterion invented here; a seed whose opening defaults is a STOP per the ratified memos (counterfactual §9 item 2, pre-registration §8) — the report records it and the go/no-go on restarting is the owner's; the phase-18 standing rule (tasks/phase-18.md:944) is SUPERSEDED for this window (orchestrator ruling 2026-08-24: ratified text beats a contract clause).
- [ ] On ABANDON: the defect is described with symptom, seed, suspected file and a reproduction; the follow-up is named as a routing slot for the owner to land; and the report states plainly that the adopting record does not start.
- [ ] Committed bytes untouched: `bash scripts/verify_samples.sh` (bare) still verifies every committed set clean, and no file under `replays/` differs from HEAD.
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
- `uv run python -c "import check_doc_facts"`
- `uv run python -c "import eval.leak_scan"`
- `uv run python -c "import meetings.render_contract"`
- `uv run python -c "import agents.strategic.prompts.loader"`
- `uv run python -c "import agents.memory.store"`
- `uv run python -c "import meetings.transcript"`
- `uv run python -c "import meetings.constants"`
- `uv run python -c "import meetings.schemas"`
- `uv run python -c "import eval.evidence_honesty"`
- `uv run python -c "import eval.solvability"`
- `uv run python -c "import meetings.manager"`
- `uv run python -c "import api.schemas"`

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
Open a PR from branch `phase-20-smoke-record` with a title like `task 20.35: the smoke record (operator): 3–5 seeds, stop-and-report, with the abandon branch`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing audits/review-2026-08-19/D/FINAL-synthesis.md §4 wave 2 (the pre-record protocol — the $0 offline counterfactual "de-risks a 23 h event"; the record order; the primary bars) + §6 fact 2 ("The record itself runs on 917 lines of untested Bash (C-74). Harden that first … or the 23 h is at risk"); audits/review-2026-08-19/B/collated-findings.md C-74 (P1: `refresh_samples.sh` = 917 lines of worker pool + mkdir mutex + per-seed retry, `tests/scripts/test_refresh_samples.py` = 915 lines / 59 all-`--dry-run` tests, none touching `run_worker`/`_acquire_lock`/`record_one_seed` — CLOSED at HEAD by Task 20.21, PR #359: the wrapper is now 1,052 lines with `_acquire_lock` at scripts/refresh_samples.sh:774, `record_one_seed` at :824, `run_worker` at :936, and tests/scripts/test_refresh_samples.py is 1,610 lines / 80 tests carrying a hermetic fake-provider RECORDING family (:1053 onward) that drives `run_worker` / `claim_next_seed` / `record_one_seed` / `_acquire_lock` end to end, asserted by name off a `bash -x` trace at :1355-1361); scripts/refresh_samples.sh:36-37 (`AILIBI_SAMPLE_DIR`, and `AILIBI_MANIFEST` defaulting under it), :566 (`REQUIRED_PROMPT_SET="qwen3_6_27b"`), :588 (`REQUIRED_SET_OWNER_MODEL="Qwen/Qwen3.6-27B"`), :289-326 (the substrate-lever preflight — since Task 20.33 a POSITIVE whole-slate equality against the operator-declared `--expect-levers`, delegating the comparison to `orchestrator.replay.substrate_slate_mismatches`; NOT the baseline-6 blacklist this contract was authored against), :55 + :61-65 (the `--expect-levers` usage block) and :248-260 (its argument parse, an explicitly empty value meaning the bare slate), :524-526 and :649-652 (the preflight's TWO call sites — the dry-run path refuses as well as the real path), :669-673 (the pre-spend roster descriptor write, after `mkdir -p "$SAMPLE_DIR"` at :660), :737 (the stage dir created under `dirname "$SAMPLE_DIR"`); scripts/verify_samples.sh:16-23 (a bare invocation walks EVERY set under the samples root); scripts/validity_gate.py:78-85 (`--expected-model`) and :86-93 (`--require-zero-cost`); eval/validity.py:26-56 (the ten named checks — still exactly ten; :49 `cost_and_provenance_exact`, which since Task 20.33 ALSO requires every game's substrate-flag stamp to equal the canonical snapshot with the canonical key set, and :54 `byte_identical_reconstruction`); orchestrator/replay.py:587-599 (`_TOGGLEABLE_LEVER_RESOLVERS` — nine keys at HEAD: `impostor_roll_call` plus the eight Phase-20 levers, in registration order), :607-609 (`TOGGLEABLE_SUBSTRATE_FLAG_KEYS`), :614-618 (`SUBSTRATE_FLAG_KEYS`), :620 (`substrate_flag_snapshot`), :652 (`substrate_slate_mismatches` — the one comparison the wrapper preflight, the record and this report must all use rather than re-derive); tasks/phase-18.md:941-944 (the standing record watch item — the `cost_and_provenance_exact` blindness around the `(deadline_default)` synthetic marker, and "a seed whose opening defaults is a FAILED recording and re-records"); audits/audit-phase-16-baseline-4.md §7 (the precedent: 9p2i seed 5 re-recorded after a `(deadline_default)` phantom, its MANIFEST row stamped honestly); tasks/phase-10.md:1133 (the 5-seed smoke that covered no emergency meeting — the full run then crashed on the uncovered path), :668-680 (smoke-first STOP-for-go and the smoke-abandon evidence branch); audits/audit-phase-20-preregistration.md and audits/audit-phase-20-counterfactual.md (the ratified bars, the decision rule, and the abandon criteria this smoke executes rather than invents)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
