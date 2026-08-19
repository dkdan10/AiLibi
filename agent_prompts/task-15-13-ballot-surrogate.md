# Agent Prompt — 15.13 The ballot-predictor surrogate MeetingRunner (GO/NO-GO + the fallback ladder)

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-15.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 15.13 — The ballot-predictor surrogate MeetingRunner (GO/NO-GO + the fallback ladder), anchored to audits/post-phase-14-ML-training-signal.md §5 (the rebuild design); orchestrator/game.py:420-440 (the MeetingRunner protocol), :942-979 (result validation); meetings/voting.py:120-213 (tally_ballots); meetings/constants.py (the gate constant home after 15.6); meetings/manager.py:2841 (roster off ballots); eval/balance_eval.py:228 (run_tournament_eval). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-15.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-15-ballot-surrogate`
**Depends on:** 15.11, 15.12
**Section refs:** audits/post-phase-14-ML-training-signal.md §5 (the rebuild design); orchestrator/game.py:420-440 (the MeetingRunner protocol), :942-979 (result validation); meetings/voting.py:120-213 (tally_ballots); meetings/constants.py (the gate constant home after 15.6); meetings/manager.py:2841 (roster off ballots); eval/balance_eval.py:228 (run_tournament_eval)
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
fake-provider MeetingManager as the training-time runner, (b) the 15.8 env's explicit
`episode_boundary="first_meeting"` opt-in with meeting-free fitness terms (the env marks those
episodes truncated and no full-game term reads them — the deliberate boundary mode 15.8 contracts,
not silent truncation), (c) periodic real-LLM re-grounding recordings (operator, $0). Whatever the
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
- [ ] The GO/NO-GO bar is OWNER-RATIFIED (2026-07-09, mid-wave review Q1) and stated in the report and in code BEFORE training — population-relative on all three axes, no absolute constants (every absolute number in this project's history moved when the population changed: FO-6 64% → 26%; ceiling 65.1 → 70.6): **GO ⇔ held-out top-1 ≥ 0.75 × the honest ceiling MEASURED ON THE SAME scored population by the 15.11 harness (never the samples-set 70.6% figure) AND held-out top-1 > the corpus-re-baselined FO-6 logistic AND SKIP-vs-eject accuracy > the scored population's own `always_eject_baseline`** (on the corpus test split that trivial constant is ~0.82 — the samples-set 78.4% does not transfer). Pre-committed in the same breath: NO-GO ⇒ fallback (a) becomes the bake-off's training-time runner and the surrogate ships as a DIAGNOSTIC only (its fidelity report still lands; nothing trains against it). The verdict is reported against this bar with the held-out numbers from the 15.11 harness.
- [ ] The fallback path is exercised by test regardless of verdict: the training env runs under fallback (a) today, proving the bake-off cannot be blocked by a NO-GO.
- [ ] Surrogate inference is deterministic under a fixed weights artifact (double-run hash test); the fitted weights are COMMITTED under `training/artifacts/surrogate/` with a sha256 sidecar the 15.9 stamp schema can reference, and the bake-off reloads exactly that artifact (a round-trip test loads it and reproduces the reported fidelity numbers).
- [ ] The staleness cap is real code the bake-off consumes (exceeding it raises), with its unit and ownership pinned: a max-use integer committed beside the weights artifact, whose use-counter keys on the weights sha256 and is CUMULATIVE across a bake-off run — constructing a fresh runner instance never resets it. The re-grounding recipe (record fresh real-LLM meetings, rebuild the table, re-fit, re-measure) is documented step-by-step in the report.
- [ ] Fit/predict leakage is fenced by test: the predictor's side-channel into the 15.11 meeting table (the per-voter rows behind the meeting-collapsed `MeetingView`) reads label columns (`ballot_target`, `ejected_player_id`) ONLY for fit-side seeds; a committed test proves predict on a test meeting never touches a test row's labels, and fit never reads a row from outside the fit-side seed set.
- [ ] The report includes the surrogate's PREDICTED-ballot calibration (Brier/ECE of the predicted confidences vs whether the named target was ejected) as its own channel — the harness's committed `ballot_brier`/`ballot_ece` are the model-independent RECORDED-ballot reference and are never presented as surrogate calibration.
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
Open a PR from branch `phase-15-ballot-surrogate` with a title like `task 15.13: the ballot-predictor surrogate meetingrunner (go/no-go + the fallback ladder)`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing audits/post-phase-14-ML-training-signal.md §5 (the rebuild design); orchestrator/game.py:420-440 (the MeetingRunner protocol), :942-979 (result validation); meetings/voting.py:120-213 (tally_ballots); meetings/constants.py (the gate constant home after 15.6); meetings/manager.py:2841 (roster off ballots); eval/balance_eval.py:228 (run_tournament_eval)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
