# Agent Prompt — 5.2 Vote-correctness metric

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-5.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 5.2 — Vote-correctness metric, anchored to DESIGN.md §11.3. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-5.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-5-vote-correctness-metric`
**Depends on:** 5.1 merged
**Section refs:** DESIGN.md §11.3
**Complexity:** Medium

A pure analyzer over `eval.report_schema.TournamentReport` that answers
DESIGN.md §11.3's vote-correctness question: when a meeting ejects an
impostor, was the ejection *driven by real evidence* (a genuine contradiction
against the ejected player, or a kill-witness chain) rather than a lucky or
unfounded vote? A high impostor-ejection rate that is not evidence-backed is
a worse signal than a lower rate that is — this metric separates the two.

The metric reads only `eval.report_schema` data (no engine, agents, or LLM
imports). The relevant fields, all already on the merged schema:

- `GameReport.roles: Mapping[PlayerId, Role]` — post-game ground truth;
  `roles[ejected_player_id] == "IMPOSTOR"` decides whether an ejection hit an
  impostor. (`Role` is `Literal["CREWMATE", "IMPOSTOR"]` from
  `engine.entities`.)
- `MeetingReport.outcome` (`"EJECTED"` / `"SKIPPED"`) and
  `MeetingReport.ejected_player_id`.
- `MeetingReport.contradictions` — `ContradictionRef.subjects` and `.kind`
  (`"alibi_conflict"` / `"alibi_vs_sighting"`) say whether a real
  contradiction names the ejected player.
- `MeetingReport.transcript.reports` — witness evidence lives on
  `ReportDocument.observations` (the `ObservationClaim` union:
  `FoundBodyObservation` / `SawPlayerObservation`), which is a DIFFERENT field
  from `ReportDocument.claims` (the `Claim` union: alibi/accusation/
  corroboration). Do not look for observations on `.claims`.
- `MeetingReport.transcript.statements` — `Statement.claims` carries
  `AccusationClaim` (accusations also appear on `ReportDocument.claims`).
- `MeetingReport.ballots` — `VoteBallot.target` and `primary_reason_id`
  (references a `Statement` id) for the ejecting-vote rationale.

**Files in scope:**
- eval/vote_correctness.py
- tests/eval/test_vote_correctness.py

**Files NOT in scope:**
- engine/
- agents/
- llm/
- api/
- frontend/
- scripts/run_tournament.py
- eval/report_schema.py
- eval/accusation_calibration.py
- eval/alibi_fabrication.py
- eval/cost_dashboard.py
- DESIGN.md
- AGENT_IMPLEMENTATION.md

**Definition of done:**
- [ ] `eval/vote_correctness.py` exposes a pure function from a `TournamentReport` (or a sequence of `GameReport`) to a frozen Pydantic result model — no I/O, no engine/LLM calls.
- [ ] The metric considers only `EJECTED` meetings. For each, it classifies the ejection as (a) impostor vs crewmate via `roles[ejected_player_id]` (subscript — fail-loud if a real player is absent from `roles`; see the partial-replay bullet for the `ejected_player_id is None` case), and (b) evidence-backed vs not. "Evidence-backed" is computed from structured report data, not free text, via two schema-expressible signals: a `ContradictionRef` whose `subjects` include the ejected player, OR a kill-witness chain — a `FoundBodyObservation` reporting a body in room R at tick T, plus a `SawPlayerObservation` whose `subject == ejected_player_id` with `room == R` and `tick` within a documented window K of T. The accusation-at-scene variant is EXCLUDED: `AccusationClaim` carries no location or tick, so counting "someone accused the ejected player" collapses into the circular accusation/vote-driven signal this metric exists to avoid (DESIGN.md §11.3 names only "a real contradiction or kill witness"). The exact predicate and the window K are recorded in the PR's `## Decisions` block.
- [ ] The result model reports at least: total ejections, impostor ejections, evidence-backed impostor ejections, and the vote-correctness rate (evidence-backed impostor ejections / impostor ejections, defined as 0.0 or `None`—pick and document—when there are no impostor ejections).
- [ ] Decision recorded in the PR's `## Decisions` block: the precise "real evidence" predicate (contradiction-subjects and/or the precise kill-witness chain above; a ballot `primary_reason_id`→`Statement` chain may corroborate but must not be the sole signal, to avoid circularity), the kill-witness tick window K, and the denominator choice. DESIGN.md §11.3 frames it as impostor ejections backed by a real contradiction or kill witness; bias toward the impostor-ejection denominator.
- [ ] Partial-replay robustness: meetings with no contradictions, an empty transcript, a `SKIPPED` outcome, or a game with no meetings never raise — they contribute zero to the relevant buckets. Note that `MeetingReport` (unlike `meetings.schemas.MeetingResult`, schemas.py:263-273) does NOT enforce the `outcome=="EJECTED"` ↔ non-None `ejected_player_id` coupling, so an `EJECTED` meeting with `ejected_player_id is None` is type-possible; treat it as malformed and skip it (or fail-loud) — pick one and record it in `## Decisions`.
- [ ] `tests/eval/test_vote_correctness.py` builds `report_schema` fixtures directly (no tournament run) covering: ejected impostor with a naming contradiction (correct); ejected impostor with no evidence (incorrect); ejected crewmate; a `SKIPPED` meeting; and a game with zero meetings.
- [ ] `uv run mypy --strict eval` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` and `uv run python scripts/validate_task_docs.py` pass.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

Read `eval/report_schema.py` and `meetings/schemas.py` first — the metric is
a fold over `GameReport.meetings`. Pseudocode:

```python
for game in report.games:
    for meeting in game.meetings:
        if meeting.outcome != "EJECTED":
            continue
        ejected = meeting.ejected_player_id
        if ejected is None:
            continue  # malformed: MeetingReport does not enforce EJECTED<->ejected_player_id
        is_impostor = game.roles[ejected] == "IMPOSTOR"  # subscript: fail-loud if a real player is absent
        backed = _has_real_evidence(meeting, ejected)  # ContradictionRef.subjects / FoundBody+SawPlayer co-location
        ...
```

`AccusationClaim` carries no ground truth — only `roles` does; never infer a
role from an accusation. The metric does NOT wire itself into tournament JSON
output; that is Task 5.6. Construct test fixtures by instantiating
`TournamentReport`/`GameReport`/`MeetingReport` directly.

## Public types this task introduces
- `eval.vote_correctness.VoteCorrectnessReport`
- `eval.vote_correctness.compute_vote_correctness`

These are the symbols downstream tasks will import. Keep their signatures stable.

## Dependency contract check
Run these before editing. If any fail, stop and report — your dependencies are not where this task expects them.

- `uv run python -c "import eval.report_schema"`
- `uv run python -c "import orchestrator.replay.ReplayLog"`
- `uv run python -c "import api.schemas.BeliefEntryView"`
- `uv run python -c "import orchestrator.replay"`
- `uv run python -c "import api.schemas"`
- `uv run python -c "import frontend/src/types/api.ts::*` (every DTO from 4"`
- `uv run python -c "import frontend/src/api/client"`
- `uv run python -c "import api.replay_loader"`
- `uv run python -c "import api.main"`

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
Open a PR from branch `phase-5-vote-correctness-metric` with a title like `task 5.2: vote-correctness metric`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing DESIGN.md §11.3), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
