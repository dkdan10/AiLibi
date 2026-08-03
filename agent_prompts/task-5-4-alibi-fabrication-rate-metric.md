# Agent Prompt — 5.4 Alibi-fabrication-rate metric

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-5.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 5.4 — Alibi-fabrication-rate metric, anchored to DESIGN.md §11.3. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-5.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-5-alibi-fabrication-rate-metric`
**Depends on:** 5.1 merged
**Section refs:** DESIGN.md §11.3
**Complexity:** Medium

A pure analyzer over `eval.report_schema.TournamentReport` that answers
DESIGN.md §11.3's alibi-fabrication question: how often do impostors produce
alibis that *survive* contradiction detection? A high survival rate means
impostors are getting away with fabricated cover; a low rate means the §5.4
contradiction detector is catching them. This is an impostor-effectiveness /
detector-effectiveness signal, not a per-agent score.

The inputs, all on the merged schema:

- `AlibiClaim` (`type="alibi"`, `subject: PlayerId`, `from_tick`, `to_tick`,
  `room`, `evidence`) — nested in `ReportDocument.claims` and
  `Statement.claims` inside `MeetingReport.transcript`. The *author* of the
  alibi is the enclosing `ReportDocument.agent_id` / `Statement.speaker`; an
  impostor alibi is one authored by a player with
  `roles[author] == "IMPOSTOR"`.
- `MeetingReport.contradictions` — `ContradictionRef` exposes only
  `contradiction_id`, `kind` (in `{"alibi_conflict", "alibi_vs_sighting"}`),
  `event_a_id`, `event_b_id`, `subjects: tuple[PlayerId, ...]`, and
  `description`. It has **no `tick` and no `room` field**, so a
  "subject + tick-overlap + room" join is NOT computable from a
  `ContradictionRef`. Two join rules ARE available:
  - **subject-membership** — the alibi's `subject` appears in an
    `alibi_*`-kind contradiction's `subjects`. Public and stable, but coarse:
    it credits a "catch" whenever the subject is named — even by a
    contradiction between two OTHER authors' alibis about that subject (a
    false positive), and it over-attributes when one subject has several
    alibis.
  - **event-id reconstruction** — `event_a_id`/`event_b_id` encode the
    authoring artifact and claim index
    (`report:{agent_id}@{tick}:claim:{index}` /
    `stmt:{statement_id}:claim:{index}`, produced by the PRIVATE helpers
    `_report_claim_id`/`_statement_claim_id` in `meetings/transcript.py`), so
    the analyzer can reconstruct the exact alibi's id and test membership in a
    contradiction's event ids. Precise, but couples `eval/` to private
    transcript helpers whose format could drift.

  An impostor alibi "survives" when no contradiction catches it under the
  chosen rule.

**Files in scope:**
- eval/alibi_fabrication.py
- tests/eval/test_alibi_fabrication.py

**Files NOT in scope:**
- engine/
- agents/
- llm/
- api/
- frontend/
- scripts/run_tournament.py
- eval/report_schema.py
- eval/vote_correctness.py
- eval/accusation_calibration.py
- eval/cost_dashboard.py
- DESIGN.md
- AGENT_IMPLEMENTATION.md

**Definition of done:**
- [ ] `eval/alibi_fabrication.py` exposes a pure function from a `TournamentReport` to a frozen Pydantic result model: total impostor-authored alibis, how many survived contradiction detection, and the fabrication-survival rate.
- [ ] An "impostor alibi" is identified by the enclosing report/statement author's role (`roles[author] == "IMPOSTOR"`), NOT by `AlibiClaim.subject` alone (an impostor may file an alibi about another player). The author→role resolution is documented.
- [ ] "Survived" is computed per meeting (the contradiction detector runs per-transcript) under the chosen join rule from the inputs above — subject-membership or event-id reconstruction. The "subject + tick + room" phrasing is NOT used, because `ContradictionRef` carries no tick or room. The exact rule and its accepted failure mode are recorded in the PR's `## Decisions` block.
- [ ] Decision recorded in the PR's `## Decisions` block, covering three points: (a) the matching rule — **subject-membership** (`subject ∈ ContradictionRef.subjects` with an `alibi_*` kind; simple/public but credits cross-author conflicts about the subject and over-attributes across multiple same-subject alibis) vs **event-id reconstruction** (precise, but couples to private transcript helpers); pick one and state the accepted failure mode. (b) the denominator — bias toward impostor-authored self-alibis (`subject == author`), which makes the common single-author case exact under subject-membership. (c) multiplicity — when the SAME alibi value tuple `(author, subject, from_tick, to_tick, room)` appears in both an impostor's `ReportDocument` and one or more of their `Statement`s in one `MeetingTranscript`, it counts ONCE (dedup by that tuple, since `AlibiClaim` has no id), not per occurrence.
- [ ] Partial-replay robustness: meetings with no alibis, no contradictions, or no impostor participants produce zero counts without raising; a game with no meetings contributes nothing.
- [ ] `tests/eval/test_alibi_fabrication.py` builds report fixtures directly covering: an impostor self-alibi with NO matching contradiction (survived → counts as fabrication); an impostor alibi flagged by an `alibi_conflict` contradiction (caught); a crewmate alibi (excluded from numerator and denominator); the no-alibis case; a cross-author case (an `alibi_conflict` whose `subjects` name the impostor's subject but which is authored by two OTHER players — pins whether the chosen rule falsely counts the impostor's own alibi as caught); and a multiplicity case (the same alibi tuple restated in a report and a statement — asserts it counts once).
- [ ] `uv run mypy --strict eval` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` and `uv run python scripts/validate_task_docs.py` pass.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

See DESIGN.md §11.3 and §5.4. Walk `MeetingReport`s; for each, collect
`AlibiClaim`s from `transcript.reports` (author = `report.agent_id`) and
`transcript.statements` (author = `statement.speaker`), keep those whose
author is an impostor per `roles`, dedup by the `(author, subject, from_tick,
to_tick, room)` tuple, and check each against the meeting's `contradictions`
under the chosen join rule (subject-membership filtered to `alibi_*` kinds, or
event-id reconstruction). `ContradictionRef` has no tick/room, so do not
attempt a tick/room overlap join against it. Survival rate = survived / total
impostor alibis. Build fixtures by instantiating the schema models directly;
do NOT touch the tournament runner (Task 5.6).

## Public types this task introduces
- `eval.alibi_fabrication.AlibiFabricationReport`
- `eval.alibi_fabrication.compute_alibi_fabrication_rate`

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
Open a PR from branch `phase-5-alibi-fabrication-rate-metric` with a title like `task 5.4: alibi-fabrication-rate metric`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing DESIGN.md §11.3), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
