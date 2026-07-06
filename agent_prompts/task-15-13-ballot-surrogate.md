# Agent Prompt — 15.13 The ballot-predictor surrogate MeetingRunner (GO/NO-GO + the fallback ladder)

You are working on AiLibi. Before starting, read AGENTS.md, DESIGN.md, and the task section in tasks/phase-15.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth and the task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 15.13 — The ballot-predictor surrogate MeetingRunner (GO/NO-GO + the fallback ladder), anchored to audits/post-phase-14-ML-training-signal.md §5 (the rebuild design); orchestrator/game.py:402-422 (the MeetingRunner protocol), :905-943 (result validation); meetings/voting.py:120-213 (tally_ballots); meetings/constants.py (the gate constant home after 15.6); meetings/manager.py:2823 (roster off ballots); eval/balance_eval.py:227 (run_tournament_eval). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-15.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-15-ballot-surrogate`
**Depends on:** 15.11, 15.12
**Section refs:** audits/post-phase-14-ML-training-signal.md §5 (the rebuild design); orchestrator/game.py:402-422 (the MeetingRunner protocol), :905-943 (result validation); meetings/voting.py:120-213 (tally_ballots); meetings/constants.py (the gate constant home after 15.6); meetings/manager.py:2823 (roster off ballots); eval/balance_eval.py:227 (run_tournament_eval)
**Complexity:** Integration

The $0 inner-loop meeting model, rebuilt on the structural fix: predict each living voter's BALLOT
(target, confidence) from the 15.11 features, and let the REAL deterministic tally produce the outcome —
`tally_ballots(ballots, skip_confidence_threshold=DEFAULT_SKIP_CONFIDENCE_THRESHOLD)` (the threshold is
a required keyword with NO default; pass the constants-home value explicitly). This eliminates FO-6's
always-SKIP collapse by construction (SKIP-vs-eject emerges from plurality + the confidence gate, not a
mis-calibrated binary head) and restores belief persistence (one ballot per living voter is exactly the
roster the cross-meeting fold reads). Train on the 15.12 corpus via the 15.11 table (numpy allowed);
wrap as `SurrogateMeetingRunner` conforming to the runtime-checkable `MeetingRunner` protocol: the
returned `MeetingArtifacts` echoes `meeting_id`/`triggered_by`/`trigger_tick` (validated at
`game.py:905-943`), carries a full-roster ballot set, and empty LLM metadata. The GO/NO-GO bar is
written BEFORE training, against the 15.11 honest ceiling; the fallback ladder is in-contract: (a) the
fake-provider MeetingManager as the training-time runner, (b) meeting-boundary episode truncation with
meeting-free fitness terms, (c) periodic real-LLM re-grounding recordings (operator, $0). Whatever the
verdict, the staleness doctrine ships: a use-counter/config cap the bake-off must respect, so no trainer
optimizes indefinitely against a frozen surrogate. Additively, `run_tournament_eval` gains an optional
per-game meeting-runner factory keyword (mirroring its existing per-game default-runner construction) so
surrogate-driven tournaments produce standard reports for diagnostics — final champion scoring still
always uses a real meeting path.

**Files in scope:**
- training/surrogate/ballots.py (new: the predictor + training entry)
- training/surrogate/runner.py (new: the MeetingRunner implementation)
- training/surrogate/fidelity.py (GO/NO-GO wiring region — 15.11 owns the metrics core)
- eval/balance_eval.py (additive optional meeting-runner-factory keyword on run_tournament_eval)
- training/artifacts/surrogate/ (new: the fitted ballot-predictor weights, float-hex JSON + sha256 sidecar — the exact artifact the bake-off reloads and the 15.9 stamp schema references)
- training/reports/report-ballot-surrogate.md (new: fidelity vs ceiling, the verdict, the chosen fallback, the re-grounding cadence)
- tests/training/test_surrogate_runner.py (new)
- tests/eval/test_balance_eval_meeting_runner.py (new)

**Files NOT in scope:**
- meetings/voting.py (the tally is consumed pure, never reimplemented — that is the point)
- meetings/manager.py + llm/ (no meeting-layer change)
- orchestrator/game.py (the Protocol is already injectable)

**Definition of done:**
- [ ] `SurrogateMeetingRunner` satisfies `isinstance(_, MeetingRunner)`; a full surrogate-driven `HeadlessGame` completes with valid artifacts — trigger echo validated, one ballot per living voter, and the cross-meeting belief fold consumes the result (asserted by test).
- [ ] The predicted-ballot path feeds the real `tally_ballots` with the explicit constants-home threshold; no re-implemented tally logic exists anywhere in `training/`.
- [ ] The GO/NO-GO bar is stated in the report and in code BEFORE training (e.g. GO ⇔ held-out top-1 ≥ 0.75 × the honest ceiling AND SKIP-vs-eject ≥ 0.80 — the implementer finalizes the exact bar, but it must be committed before the training run), and the verdict is reported against it with by-game-CV numbers from the 15.11 harness.
- [ ] The fallback path is exercised by test regardless of verdict: the training env runs under fallback (a) today, proving the bake-off cannot be blocked by a NO-GO.
- [ ] Surrogate inference is deterministic under a fixed weights artifact (double-run hash test); the fitted weights are COMMITTED under `training/artifacts/surrogate/` with a sha256 sidecar the 15.9 stamp schema can reference, and the bake-off reloads exactly that artifact (a round-trip test loads it and reproduces the reported fidelity numbers).
- [ ] The staleness cap is real code the bake-off consumes (exceeding it raises), and the re-grounding recipe (record fresh real-LLM meetings, rebuild the table, re-fit, re-measure) is documented step-by-step in the report.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

Keep the predictor simple and calibrated — a standardized multinomial logistic or tiny MLP over the
15.11 features is the determinism-safe default; gradient-boosted trees would need integer-threshold care
and are not worth it at this data size. `MeetingArtifacts(result=…, llm_calls=(), prompt_versions={})`
is the shape the orchestrator dereferences; a bare `MeetingResult` fails. Dead voters cast nothing:
derive the living roster from the trigger-time state the runner receives. The `run_tournament_eval`
keyword must be additive-optional with the default path byte-identical (existing balance-eval tests stay
green untouched).

## Public types this task introduces
- `training.surrogate.ballots.BallotPredictor`
- `training.surrogate.runner.SurrogateMeetingRunner`

These are the symbols downstream tasks will import. Keep their signatures stable.

## Integration risk

Model exploitation is the known failure (MBPO/Dreamer): a trained mover shifts the
sighting/contradiction distribution and the surrogate's blind spot — voice-driven convictions it
structurally cannot see — becomes the attack surface. The mitigations are all structural and land here:
the staleness cap, the pre-stated GO/NO-GO with the honest ceiling as denominator, re-grounding as a
documented operator recipe, and the bake-off's rule that final numbers are never surrogate-scored. Do
not weaken any of the four to make a verdict look better.

## Dependency contract check
Run these before editing. If any fail, stop and report — your dependencies are not where this task expects them.

- `uv run python -c "import orchestrator.replay"`
- `uv run python -c "import api.replay_loader"`
- `uv run python -c "import meetings.constants"`
- `uv run python -c "import meetings.render_contract"`
- `uv run python -c "import meetings.schemas"`
- `uv run python -c "import agents.memory.beliefs"`
- `uv run python -c "import api.schemas"`
- `uv run python -c "import eval.funnel"`
- `uv run python -c "import eval.validity"`
- `uv run python -c "import eval.watchability"`
- `uv run python -c "import training.surrogate.dataset"`
- `uv run python -c "import training.surrogate.fidelity"`
- `uv run python -c "import training.env"`
- `uv run python -c "import training.rollout"`
- `uv run python -c "import training.rewards"`

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
Open a PR from branch `phase-15-ballot-surrogate` with a title like `task 15.13: the ballot-predictor surrogate meetingrunner (go/no-go + the fallback ladder)`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing audits/post-phase-14-ML-training-signal.md §5 (the rebuild design); orchestrator/game.py:402-422 (the MeetingRunner protocol), :905-943 (result validation); meetings/voting.py:120-213 (tally_ballots); meetings/constants.py (the gate constant home after 15.6); meetings/manager.py:2823 (roster off ballots); eval/balance_eval.py:227 (run_tournament_eval)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
