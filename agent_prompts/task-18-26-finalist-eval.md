# Agent Prompt — 18.26 The real-LLM finalist eval (operator, ~5h/finalist, $0)

You are working on AiLibi. Before starting, read AGENTS.md, DESIGN.md, and the task section in tasks/phase-18.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth and the task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 18.26 — The real-LLM finalist eval (operator, ~5h/finalist, $0), anchored to training/reports/report-finalist-eval.md (the 17.14 recorder + protocol this re-runs); scripts/run_tournament.py --candidate-artifact + the 18.19 --crew-artifact arm; the campaign reports' named finalists; the standing floors (whichever baseline the phase adopted). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-18.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

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
hand-off). Crew slots are owner-justified at dispatch; the piloted protocol if taken:
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
or an artifact.

**Files in scope:**
- training/reports/results-finalist-eval.jsonl + training/reports/report-finalist-eval.md (the phase-18 rows/reading — history preserved per the 17.14 precedent)
- tests/training/test_finalist_eval_pins.py (new — the jsonl-row pins)

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

## Implementation hint

The 17.14 §6 recipe generalizes; the new leg is the dual-stamped crew-vs-champion cell —
plan its seeds so the crew finalist's two opponents are same-seed comparable. Wall-clock
scales with finalist count: cap each campaign's slate at what its own report justifies —
the impostor slate is the ratified 4-arm cut, and any crew arms take their own
owner-justified slots beyond it.

## Integration risk

The comparator discipline is where selection evidence goes quietly wrong: if the substrate
moved at 18.12, every Phase-17 comparator number is stale and the same-seed FSM row MUST be
re-recorded here, never quoted from the old report. The contract makes that a DoD cell.

## Dependency contract check
Run these before editing. If any fail, stop and report — your dependencies are not where this task expects them.

- `uv run python -c "import training.coevo.hall_of_fame"`
- `uv run python -c "import training.conviction.serving"`
- `uv run python -c "import training.bakeoff.harness"`
- `uv run python -c "import training.conviction.model"`
- `uv run python -c "import training.conviction.dataset"`
- `uv run python -c "import training.conviction.fidelity"`
- `uv run python -c "import agents.strategic.prompts.loader"`
- `uv run python -c "import agents.tactical.learned.crew_forward"`
- `uv run python -c "import agents.tactical.learned.factory"`
- `uv run python -c "import orchestrator.replay"`
- `uv run python -c "import meetings.transcript"`
- `uv run python -c "import meetings.manager"`
- `uv run python -c "import eval.off_menu"`
- `uv run python -c "import eval.kill_craft"`
- `uv run python -c "import eval.deception_instruments"`
- `uv run python -c "import agents.tactical.features"`
- `uv run python -c "import training.coevo.factory"`
- `uv run python -c "import training.coevo.rollout"`
- `uv run python -c "import training.coevo.driver"`
- `uv run python -c "import training.bakeoff.map_elites"`
- `uv run python -c "import training.realpath"`
- `uv run python -c "import training.anchor_study"`

## Pre-flight checklist
- Read AGENTS.md, DESIGN.md, and the task section before editing.
- Inspect the current implementation before editing.
- Identify the existing local patterns for the files in scope and follow them.

## Constraints and non-goals
Do not modify DESIGN.md.
Do not modify AGENT_IMPLEMENTATION.md.
Do not modify tasks/phase-*.md unless this task explicitly lists those files in scope.
Do not implement work outside this task.

## Verification checklist
- Run every command listed in the Definition of done.
- Run `git diff --name-only` and confirm the diff stays within scope.
- If any Definition of done item is unchecked, report it explicitly in the PR description instead of declaring the task complete.

## Decisions vs questions
- If something is **ambiguous and blocking** (you cannot make a reasonable choice without further information): stop, open a draft PR, add a `## Questions` section, request review.
- If something is **ambiguous but resolvable by judgment** (a default value, a tie-break, a naming choice): document the choice in a `## Decisions` section in the PR description and proceed.

## Output expectation
Open a PR from branch `phase-18-finalist-eval` with a title like `task 18.26: the real-llm finalist eval (operator, ~5h/finalist, $0)`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing training/reports/report-finalist-eval.md (the 17.14 recorder + protocol this re-runs); scripts/run_tournament.py --candidate-artifact + the 18.19 --crew-artifact arm; the campaign reports' named finalists; the standing floors (whichever baseline the phase adopted)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
