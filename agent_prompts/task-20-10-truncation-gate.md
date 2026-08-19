# Agent Prompt — 20.10 The corpus acceptance gate rejects a truncated replay

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-20.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 20.10 — The corpus acceptance gate rejects a truncated replay, anchored to register C-6 in audits/review-2026-08-19/B/collated-findings.md (P1, "reconstruct_episode reads a corrupted replay as a legitimate truncation"); audits/review-2026-08-19/B/training-ml.md §3 F1 (P1, VERIFIED — the `and not truncated` guard, with the seed-1000 repro); audits/review-2026-08-19/B/verdicts.md:204-228 (the C-6 adversarial verdict — PARTIALLY-TRUE: mechanism CONFIRMED, the recorder-lock-race CAUSE REFUTED, and the NEW worse instance named at `eval/validity.py`); audits/review-2026-08-19/D/FINAL-synthesis.md §1 RC7 ("gates validate shape, not entitlement") and §4 Wave 1 item 1.4 (back-port the anchor_study check; measurement = the corrupt fixture is rejected by `validity_gate.py`); audits/audit-phase-20-planning.md §3 Wave 1 ("the corpus gate rejects truncation"); anchors re-verified at HEAD `b809b19c`: eval/validity.py:491-536 (`check_all_games_reach_game_over`; :509 the only truncation-adjacent violation, :517-518 the winner cross-check skipped when `reconstructed_winner is None`, :529-535 the summary + facts), training/rollout.py:652-663 (the cross-check with `and not truncated` at :656) and :23-32 (the "Silent truncation is structurally unreachable" docstring claim), training/anchor_study.py:627-646 (the correct three-part check, the back-port source), scripts/validity_gate.py:3 ("the eight composed checks" — the gate reports ten) and :19-21 (the exit-code contract), orchestrator/game.py:1776 (`TICK_BUDGET_REACHED` returns WITHOUT `record_game_end`) vs :1838-1844 (`record_game_end` fires only after a `GameOverEvent`), training/README.md:240 (§6 item 5, the recorder lock-race label the review refuted as this defect's cause). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-20.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-20-truncation-gate`
**Depends on:** none (root)
**Section refs:** register C-6 in audits/review-2026-08-19/B/collated-findings.md (P1, "reconstruct_episode reads a corrupted replay as a legitimate truncation"); audits/review-2026-08-19/B/training-ml.md §3 F1 (P1, VERIFIED — the `and not truncated` guard, with the seed-1000 repro); audits/review-2026-08-19/B/verdicts.md:204-228 (the C-6 adversarial verdict — PARTIALLY-TRUE: mechanism CONFIRMED, the recorder-lock-race CAUSE REFUTED, and the NEW worse instance named at `eval/validity.py`); audits/review-2026-08-19/D/FINAL-synthesis.md §1 RC7 ("gates validate shape, not entitlement") and §4 Wave 1 item 1.4 (back-port the anchor_study check; measurement = the corrupt fixture is rejected by `validity_gate.py`); audits/audit-phase-20-planning.md §3 Wave 1 ("the corpus gate rejects truncation"); anchors re-verified at HEAD `b809b19c`: eval/validity.py:491-536 (`check_all_games_reach_game_over`; :509 the only truncation-adjacent violation, :517-518 the winner cross-check skipped when `reconstructed_winner is None`, :529-535 the summary + facts), training/rollout.py:652-663 (the cross-check with `and not truncated` at :656) and :23-32 (the "Silent truncation is structurally unreachable" docstring claim), training/anchor_study.py:627-646 (the correct three-part check, the back-port source), scripts/validity_gate.py:3 ("the eight composed checks" — the gate reports ten) and :19-21 (the exit-code contract), orchestrator/game.py:1776 (`TICK_BUDGET_REACHED` returns WITHOUT `record_game_end`) vs :1838-1844 (`record_game_end` fires only after a `GameOverEvent`), training/README.md:240 (§6 item 5, the recorder lock-race label the review refuted as this defect's cause)
**Complexity:** Small
**Record impact:** none
**Measurement:** `uv run python scripts/validity_gate.py` over each of `replays/samples/4p1i`, `replays/samples/9p2i`, `replays/ml_corpus/4p1i`, `replays/ml_corpus/9p2i` still exits 0 with every check PASS (300 committed games, gate output quoted in the PR); the truncated fixture exits 1 with `all_games_reach_game_over` as its ONLY failing check and `truncated_replay` in the violation text; `uv run pytest tests/eval/test_validity.py tests/training/test_rollout.py tests/scripts/test_validity_gate_cli.py -q` green.

The corpus acceptance gate accepts a replay it should reject. Drop the trailing
tick rows of a committed replay while leaving its `game_over` row in place, and
`eval/validity.py`'s `check_all_games_reach_game_over` reports PASS — because the
recorded row is still there (`check.game_over_tick is not None`, so the :509
violation never fires) while the engine's reconstruction never reaches
`GAME_OVER` (`reconstructed_winner is None`, so the :517-518 forged-label
cross-check is skipped by its own `is not None` guard). Re-verified at HEAD
`b809b19c` on a scratch copy of `replays/samples/9p2i/replay-seed-12.jsonl` with
its last tick row removed: the WHOLE gate exits 0, all ten checks PASS, and
`all_games_reach_game_over` prints `1/1 games reached game_over with a
consistent win condition` for a game whose reconstruction stopped a tick short.
Every state hash still verifies — dropping trailing rows shortens the walk
without breaking the chain — so nothing downstream catches it either. This is
the corpus acceptance gate, sitting directly under the byte-reconstruct claim
the front door is about to feature (`audits/review-2026-08-19/D/FINAL-synthesis.md`
§4 Wave 1 item 1.4), and it is the RC7 pattern in miniature: the check validates
that a row is present, not that the walk earned it.

`training/rollout.py` carries the same inversion in the form the review found
first. At :655-658 the winner cross-check is guarded by `and not truncated` —
disabled in exactly the case that needs it. Re-verified at HEAD on the same
fixture: intact, `reconstruct_episode` returns `outcome=IMPOSTORS truncated=False
winner=IMPOSTORS complete=True` over 20 tick frames; with one tick row dropped it
returns `outcome=TICK_BUDGET truncated=True winner=None complete=False` over 19
tick frames and raises nothing, matching the review's seed-1000 repro
(`audits/review-2026-08-19/B/training-ml.md` §3 F1: 25 ticks → 23, and → 14 with
ten rows dropped). The guard is vestigial and provably so: it dates from when
`EpisodeBoundary` still had `first_meeting`, a boundary that legitimately
truncated a winner-bearing replay; Task 19.19 retired the boundary and left the
clause, and `EpisodeBoundary` is now `Literal["full_game"]` alone
(training/rollout.py:73). The module docstring at :29-31 promises "Silent
truncation is structurally unreachable"; the bytes say otherwise.

Two corrections the contract inherits from the adversarial verdict, so this task
does not re-publish a refuted claim. First, the CAUSE is not the recorder: the
`record_ml_corpus.sh` mutex guards `MANIFEST.md` only, each seed lands by an
atomic `mv -f` from a private stage, and `orchestrator/replay.py` flushes every
row — the lock-race labelled at `training/README.md:240` cannot produce this byte
shape. The reachable routes are an interrupted direct tournament writing into a
set dir, a bad copy, or a hand edit; the fix is worth making because the gate is
what admits foreign bytes, not because a live producer is corrupting them today.
Second, the blast radius through `reconstruct_episode` is narrow: every caller
(`training/env.py:719`, `training/bakeoff/harness.py:717`,
`training/crew/scorer.py:942`, `training/coevo/rollout.py:210`) reconstructs a
replay it wrote seconds earlier, and the reward channel already refuses to score
an incomplete episode. The `eval/validity.py` instance is the P1 — it is the one
that reads committed corpus bytes.

The correct check already exists in this repo, un-back-ported. `training/anchor_study.py:627-646`
rejects the same bytes with three explicit clauses (no terminal `game_over`
winner; the reconstructed walk never reached `GAME_OVER`; reconstructed winner
disagrees with the recorded one), raising `CorpusWalkError: seed …: the
reconstructed walk never reached GAME_OVER (truncated tick stream)`. Back-port
its semantics into the two sites that lack them. The check cannot false-positive
on a legitimate recording: `orchestrator/game.py:1776` returns
`TICK_BUDGET_REACHED` WITHOUT calling `record_game_end`, and :1838-1844 writes
the `game_over` row only after the engine fires a `GameOverEvent`, so "a
`game_over` row exists AND the reconstruction never reached `GAME_OVER`" is
unconditionally corruption, and a genuinely tick-budget-capped rollout has no
`game_over` row to trip the new clause.

Craft rule 2 governs the fixture, and it is the part this task is easiest to get
wrong. A truncation that removes a tick row carrying a meeting trigger already
turns seven other checks red today (verified at HEAD on both
`replays/samples/9p2i/replay-seed-0.jsonl` and
`replays/ml_corpus/9p2i/replay-seed-1000.jsonl`), so a fixture of that shape
would "fail the gate" before the fix and prove nothing. The fixture must be a
replay whose trailing tick rows come AFTER its last meeting row — 16 of the 50
committed 9p2i samples end `tick, tick, tick, game_over`, and `replay-seed-12`
is the verified green-today case — so that at HEAD the gate is fully PASS and
after the fix `all_games_reach_game_over` is the ONLY failing check.

**Files in scope:**
- eval/validity.py; (the truncation check: a replay whose last record is not game_over, or whose game_over winner disagrees with the reconstructed final state, FAILS the gate)
- training/rollout.py; (the same check in reconstruct_episode; the `and not truncated` guard inverted to what the docstring promises)
- tests/eval/test_validity.py; (the truncated-fixture rejection)
- tests/training/test_rollout.py; (the corrupt-as-truncation repro becomes a failing case)
- scripts/validity_gate.py; (exit code + message for the new failure class)
- tests/scripts/test_validity_gate_cli.py

**Files NOT in scope:**
- replays/ (the committed sets are intact — the gate must stay green on all four, pinned; no replay byte moves)
- training/anchor_study.py (the reference implementation is read, not edited)
- eval/win_condition_selfcheck.py (the `WinConditionSelfCheck` shape and its predicate are reused as-is)
- training/bakeoff/harness.py, training/crew/scorer.py, training/bakeoff/goodhart.py (gate consumers — grep them for blast radius, edit none)
- scripts/measure_baseline.py (shares the loaders; the R-gate measurement is untouched)
- tests/training/_goldens/finalist_eval_pins.json (a record of closed-campaign gate outcomes; if the new clause would move a pinned failing-check list, stop and report rather than re-pinning)
- agents/strategic/prompts/ (no prompt template moves in this phase outside the single prompt-set bump)

**Definition of done:**
- [ ] `check_all_games_reach_game_over` fails a game whose recorded `game_over` row is present while the reconstruction never reached `GAME_OVER`, and fails a game whose recorded `game_over` row carries no winner; both violations carry the reason token `truncated_replay` plus the seed, mirroring `training/anchor_study.py:627-646`. Pinned by new cases in `tests/eval/test_validity.py` beside `test_all_games_reach_game_over_fails_without_game_over`.
- [ ] The check's summary and `facts["games_reached_game_over"]` count reconstruction-confirmed terminals, so a truncated game can never be summarised as having "reached game_over"; asserted in `tests/eval/test_validity.py`. Blast-radius grep for `games_reached_game_over` recorded in the PR (at HEAD the only hit is its own definition).
- [ ] An end-to-end fixture: a copy of `replays/samples/9p2i/replay-seed-12.jsonl` with its trailing tick row dropped (the `game_over` row kept) is REJECTED by `run_validity_gate`, and `report.failing_checks() == ("all_games_reach_game_over",)` — the gate-can-fail proof that the fixture is otherwise green. The same fixture is pinned through the CLI in `tests/scripts/test_validity_gate_cli.py`: exit code 1 and `truncated_replay` in the rendered output.
- [ ] All four committed sets still pass unchanged: `run_validity_gate` green over `replays/samples/{4p1i,9p2i}` and `replays/ml_corpus/{4p1i,9p2i}` (300 games), with the existing 9p2i/4p1i reproduction tests in `tests/eval/test_validity.py` untouched and the gate output for all four quoted in the PR.
- [ ] `reconstruct_episode` raises `RolloutReconstructionError` on the same fixture instead of returning `outcome="TICK_BUDGET"` silently: the cross-check no longer carries `and not truncated`, and fires when a recorded `game_over` winner exists and the walk either truncated or disagrees. Pinned by a new case in `tests/training/test_rollout.py` beside `test_reconstruction_fails_loud_on_state_hash_drift`.
- [ ] The legitimate tick-budget path is proven unaffected: a capped episode (no `game_over` row) still reconstructs as `outcome="TICK_BUDGET" truncated=True` without raising — `tests/training/test_scenarios.py::test_scenario_episodes_score_dense_while_the_terminal_gate_refuses` and `tests/training/test_env.py` stay green, and the PR names them as the guard against a false positive.
- [ ] The prose matches the bytes: `training/rollout.py`'s module docstring no longer claims silent truncation is structurally unreachable as a property of the boundary alone but names the check that enforces it, and `scripts/validity_gate.py:3` says ten composed checks (the gate reports ten) with its exit-code paragraph naming the truncated-replay failure class. One trailing provenance line at most, per Craft rule 1.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Public types this task introduces
- `eval.validity.TRUNCATED_REPLAY_REASON`

These are the symbols downstream tasks will import. Keep their signatures stable.

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
Open a PR from branch `phase-20-truncation-gate` with a title like `task 20.10: the corpus acceptance gate rejects a truncated replay`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing register C-6 in audits/review-2026-08-19/B/collated-findings.md (P1, "reconstruct_episode reads a corrupted replay as a legitimate truncation"); audits/review-2026-08-19/B/training-ml.md §3 F1 (P1, VERIFIED — the `and not truncated` guard, with the seed-1000 repro); audits/review-2026-08-19/B/verdicts.md:204-228 (the C-6 adversarial verdict — PARTIALLY-TRUE: mechanism CONFIRMED, the recorder-lock-race CAUSE REFUTED, and the NEW worse instance named at `eval/validity.py`); audits/review-2026-08-19/D/FINAL-synthesis.md §1 RC7 ("gates validate shape, not entitlement") and §4 Wave 1 item 1.4 (back-port the anchor_study check; measurement = the corrupt fixture is rejected by `validity_gate.py`); audits/audit-phase-20-planning.md §3 Wave 1 ("the corpus gate rejects truncation"); anchors re-verified at HEAD `b809b19c`: eval/validity.py:491-536 (`check_all_games_reach_game_over`; :509 the only truncation-adjacent violation, :517-518 the winner cross-check skipped when `reconstructed_winner is None`, :529-535 the summary + facts), training/rollout.py:652-663 (the cross-check with `and not truncated` at :656) and :23-32 (the "Silent truncation is structurally unreachable" docstring claim), training/anchor_study.py:627-646 (the correct three-part check, the back-port source), scripts/validity_gate.py:3 ("the eight composed checks" — the gate reports ten) and :19-21 (the exit-code contract), orchestrator/game.py:1776 (`TICK_BUDGET_REACHED` returns WITHOUT `record_game_end`) vs :1838-1844 (`record_game_end` fires only after a `GameOverEvent`), training/README.md:240 (§6 item 5, the recorder lock-race label the review refuted as this defect's cause)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
