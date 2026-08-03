# Agent Prompt — 7.3 meeting_rate / meetings_total + meeting-trigger breakdown metric

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-7.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 7.3 — meeting_rate / meetings_total + meeting-trigger breakdown metric, anchored to tasks/phase-7-plan.md §"Wave 0 — W0.3"; tasks/phase-7-plan.md §"Close gate — Stage A"; audits/audit-2026-05-30-1952-phase-7-meeting-frequency-diagnosis.md §1, §4; DESIGN.md §11.3. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-7.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-7-meeting-rate-metric`
**Depends on:** 7.1 merged
**Section refs:** tasks/phase-7-plan.md §"Wave 0 — W0.3"; tasks/phase-7-plan.md §"Close gate — Stage A"; audits/audit-2026-05-30-1952-phase-7-meeting-frequency-diagnosis.md §1, §4; DESIGN.md §11.3
**Complexity:** Medium

Wave 0 exists to make meetings frequent enough that the agent-intelligence
metrics stop running on n≈4 (the diagnosis found 4/50 games reach a meeting). The
Stage-A close gate is stated numerically — `meeting_rate ≥ 0.60` with ≥ 30
resolved meetings — but there is no metric that computes it today. This task adds
that metric so the gate is measurable, and adds the body-report-vs-emergency
trigger breakdown so the currently-dead emergency-button pathway (0/50 games in
the diagnosis) becomes visible the moment any later feature revives it.

Add a fifth Phase-5-style analyzer, `eval/meeting_quality.py::compute_meeting_rate`,
that folds a `TournamentReport` (or a bare game sequence, matching the
`compute_vote_correctness` signature) into a new frozen `MeetingRateReport`
carrying: `games_total` (number of games), `games_with_meeting` (games whose
`meetings` tuple is non-empty), `meeting_rate` (`games_with_meeting / games_total`,
and `None` when `games_total == 0` — undefined, not `0.0`, mirroring the
`vote_correctness_rate` convention), `meetings_total` (sum of `len(game.meetings)`
across all games), and a trigger breakdown: `body_report_meetings` and
`emergency_meetings` (which partition exactly into `meetings_total`). The report
carries a `model_validator(mode="after")` that fails loud on the bucket invariants
(non-negative counts; `body_report_meetings + emergency_meetings == meetings_total`;
`games_with_meeting <= games_total`; the `None`-rate-iff-`games_total==0` coupling)
exactly as `VoteCorrectnessReport._validate_buckets` does.

Wire the new analyzer into `build_tournament_eval_report` as a fifth field
`meeting_rate: MeetingRateReport` on `TournamentEvalReport` (the frozen,
`extra="forbid"` wrapper), keeping that function pure assembly — it calls the new
`compute_meeting_rate` and packs the result, never re-deriving counts inline.

FORMAT-VERSION POLICY (decide once, here, so reviewers do not re-litigate on PR):
`meeting_rate` is added to the `TournamentEvalReport` WRAPPER
(`eval/meeting_quality.py:46`), which is NOT version-stamped. `format_version` lives
ONLY on the inner persisted `TournamentReport` (`eval/report_schema.py:254`, a
required field) and governs the replay-derived report-record schema — which this
task does NOT change (the metric is a pure derived analyzer over existing
`MeetingReport` data and adds no persisted report/replay field). Therefore
`CURRENT_FORMAT_VERSION` stays `1`; do NOT bump it. The regenerated
`tournament-eval-report.json` simply carries the new wrapper field; consumers read
the freshly-generated report. Record this one-line policy in the PR `## Decisions`.

REGENERATE THE COMMITTED REPORT (a runtime break CI does not catch, so it is
mandatory here). `ReplayLoader.tournament_report()` `model_validate`s the committed
`replays/samples/tournament-eval-report.json` at runtime, and the new `meeting_rate`
is a REQUIRED member of the frozen `extra="forbid"` `TournamentEvalReport`. So the
committed 4p/1i report (generated before this task) will FAIL to load once this task
lands → `GET /eval/tournament-report` 500s and the dashboard breaks. The eval-route
tests write their own report to `tmp_path`, so `uv run pytest` / `bash scripts/check.sh`
stay GREEN and miss it — this is a latent runtime break, not a CI failure. This task
MUST regenerate the committed `replays/samples/tournament-eval-report.json` from the
frozen 4p/1i replays so it carries `meeting_rate` — offline and free via
`eval.balance_eval.load_tournament_report` + `build_tournament_eval_report` (no
provider run; the 4p/1i replays themselves stay byte-identical, only the derived
report JSON gains the field, consistent with the "4p/1i frozen" decision). The 7p/2i
set's own report is generated fresh by Task 7.8 (post-this-task) and carries the
field natively.

Surface the numbers in `scripts/run_tournament.py::_format_summary` (the operator
print) — add `meetings_total`, a `meeting_rate` line (rendered as a percentage,
guarding the `None`/no-games case the way `decisive_split` already guards the
no-decisive-games case), and a trigger line showing `body=… emergency=…`. This is
the file that overlaps Task 7.1 (which threads `--tasks-per-crewmate` / roster
presets through the same CLI), which is why this task declares `Depends on: 7.1
merged`: 7.1 lands its CLI/summary edits first, then this task adds the
meeting-rate lines on top.

Surface the close-gate scalars in the regression suite: add
`meeting_rate`, `meetings_total`, `body_report_meetings`, and `emergency_meetings`
to `eval/prompt_regression.py::PromptRegressionMetrics`, populated in
`run_prompt_regression` from the new `evaluated.meeting_rate.*` fields (never
re-derived). This makes the Stage-A gate a byte-stable, committed-baseline scalar
like the other §11.3 metrics. NOTE: the single committed
`tests/fixtures/prompt_regression/baseline.json` (keyed by fixture name `v_a` /
`v_b`) will need its expected scalars extended to include the new fields;
regenerate it deterministically (the fixtures are frozen recorded replays, the
analyzers are pure — no provider runs) and commit the updated baseline so
`tests/eval/test_prompt_regression.py`'s exact-match assertion passes.

Mirror the new wrapper field across the served-eval-view chain and the frontend so
the schema-mirror stays 1:1. The eval HTTP route (`api/routes/eval.py`) re-models
the wrapper as `_TournamentEvalReportView` with `extra="forbid"` and re-validates
via `model_dump(mode="json")` → `model_validate`; because that view forbids extras,
a new field on `TournamentEvalReport` MUST be added to `_TournamentEvalReportView`
or `_redact_failed_calls` raises. Reuse `MeetingRateReport` verbatim by import there
(the metric reports are reused, only the failed-call leaf is re-typed). Note the
eval metric reports are NOT declared or re-exported in `api/schemas.py` — they are
imported directly from `eval/*` into `api/routes/eval.py` (where
`_TournamentEvalReportView` / `_TournamentReportEvalView` / `_GameReportEvalView`
live); `api/schemas.py` contributes only `EvalCostSummaryView` / `FailedCallEvalView`
to the eval route, neither of which changes here. So `api/schemas.py` needs NO edit
for this field and is NOT in scope.

**Snapshot tripwire — this is the blocking gate, not `api.schemas.__all__`.** Adding
`meeting_rate: MeetingRateReport` to `TournamentEvalReport` changes the recursive
JSON field set of that model, which trips `test_eval_report_field_set_snapshot` in
`tests/api/test_leak.py` (it asserts `actual == EXPECTED_EVAL_REPORT_FIELDS`, a
hardcoded `frozenset`). The six new field names — `meeting_rate`, `meetings_total`,
`games_total`, `games_with_meeting`, `body_report_meetings`, `emergency_meetings` —
are ALL absent from `EXPECTED_EVAL_REPORT_FIELDS` today, so the assertion fails and
`uv run pytest` / `bash scripts/check.sh` break unless the snapshot is extended. Add
`tests/api/test_leak.py` to Files-in-scope and extend `EXPECTED_EVAL_REPORT_FIELDS`
with exactly those six names (confirming none is engine/role state — they are pure
counts, so `FORBIDDEN_EVAL_ENGINE_FIELDS` and
`test_eval_report_surface_exposes_no_engine_state_field` stay green). Since `MeetingRateReport` is a pure aggregate of counts (no roles, no
transcripts, no internal engine types), it carries no leak risk — document that in
the field's docstring. Finally add a `MeetingRateReport` interface
to `frontend/src/types/api.ts` and the `meeting_rate` field to the
`TournamentEvalReport` interface there, with the nullable `meeting_rate: number |
null` faithful to `float | None` (the file's `## Decisions` note warns drift makes
the dashboard render `undefined`).

DESIGN DECISION — trigger breakdown source (read this; it shapes the whole task).
The trigger kind (body-report vs emergency-button) is NOT carried on
`eval.report_schema.MeetingReport` and is NOT on `orchestrator.replay.MeetingReplayEntry`
either — it lives only on the per-tick `engine.events.MeetingTriggeredEvent`
(`trigger: Literal["report","emergency"]`), which the report-building loader
(`eval/balance_eval.py::_meeting_report_from_entry`) does not fold in. Adding a
real `trigger_kind` field to the report would balloon scope (it would touch
`orchestrator/replay.py`, `eval/balance_eval.py`, and force re-recording every
committed sample — that re-record is Task 7.8's job, and those files are NOT in
this task's scope). So derive the breakdown from data already on `MeetingReport`:
classify a meeting as `body_report` iff the report submitted by the meeting's
`triggered_by` player (found in `meeting.transcript.reports`, matched by
`document.agent_id == meeting.triggered_by`) contains at least one
`meetings.schemas.FoundBodyObservation`; classify it `emergency` otherwise. This
matches the diagnosis ground truth (all observed meetings are body-reports; 0
emergency) and keeps the change additive and pure. Document this heuristic and its
TWO-FOLD limitation explicitly in the analyzer docstring: the `emergency` bucket is
a CATCH-ALL, not a positively-identified emergency-button count — it is
{true emergency-button meetings} ∪ {body-report meetings whose triggering report
lacked a `FoundBodyObservation`}. Today both are ~0 (the diagnosis shows 0/50
emergencies and a clean body-report path), so the bucket is accurate now; but a
future Wave that revives emergency-button play MUST NOT trust `emergency` as a pure
emergency count without first adding a real persisted `trigger_kind`. That cleaner
fix is deferred to a LATER PHASE (not Wave 0): it would touch `orchestrator/replay.py`
+ `eval/balance_eval.py`, which even Task 7.8 explicitly excludes — Task 7.8 only
re-records under THIS same derived heuristic, it does not add the field. Do NOT
widen scope to add the field here.

**Files in scope:**
- eval/meeting_quality.py
- eval/prompt_regression.py
- api/routes/eval.py
- frontend/src/types/api.ts
- tests/eval/test_tournament_report.py
- tests/eval/test_prompt_regression.py
- tests/api/test_eval_routes.py
- tests/api/test_leak.py
- tests/fixtures/prompt_regression/baseline.json
- replays/samples/tournament-eval-report.json (regenerate the committed 4p/1i report so it carries `meeting_rate`; offline/free, replays untouched — prevents the runtime load failure)

**Files NOT in scope:**
- api/schemas.py (the eval metric reports are NOT declared/re-exported here — they ride through `api/routes/eval.py`'s `_TournamentEvalReportView`; `api/schemas.py` only contributes `EvalCostSummaryView` / `FailedCallEvalView` to the eval route, neither of which changes for `meeting_rate`. No `api.schemas.__all__` edit is needed.)
- eval/report_schema.py (do NOT add a `trigger_kind` field to MeetingReport; trigger kind is derived, see the design decision)
- orchestrator/replay.py (MeetingReplayEntry stays as-is; no new persisted field)
- eval/balance_eval.py (the report loader is untouched; the metric reads existing MeetingReport data)
- scripts/run_tournament.py (the `_format_summary` surfacing is owned by Task 7.1's CLI edits this task depends on; coordinate the meeting-rate lines onto 7.1's merged version — listed here as the dependency edge, not an independent scope claim)
- replays/samples/ and scripts/refresh_samples.sh (sample regeneration is Task 7.8)
- orchestrator/seeder.py (roster / tasks-per-crewmate config is Task 7.1)
- frontend dashboard components (rendering the new field in the UI is optional/deferred; this task only mirrors the type)

**Definition of done:**
- [ ] `eval/meeting_quality.py` defines `MeetingRateReport` (frozen, `extra="forbid"`, fail-loud bucket validator) and `compute_meeting_rate`, and `build_tournament_eval_report` packs a fifth `meeting_rate` field on `TournamentEvalReport`.
- [ ] `meeting_rate` is `None` when `games_total == 0`; `body_report_meetings + emergency_meetings == meetings_total`; `games_with_meeting <= games_total` — all enforced by the validator and covered by tests.
- [ ] The trigger breakdown is derived from `MeetingReport` data only (triggering reporter's `FoundBodyObservation`); no field is added to `eval/report_schema.py`, `orchestrator/replay.py`, or `eval/balance_eval.py`.
- [ ] `eval/prompt_regression.py::PromptRegressionMetrics` carries `meeting_rate` / `meetings_total` / `body_report_meetings` / `emergency_meetings`, populated from `evaluated.meeting_rate.*`; the committed `tests/fixtures/prompt_regression/baseline.json` is regenerated and `tests/eval/test_prompt_regression.py` exact-match passes.
- [ ] `api/routes/eval.py::_TournamentEvalReportView` mirrors the new wrapper field (reusing `MeetingRateReport` by import); `_redact_failed_calls`'s round-trip and `tests/api/test_eval_routes.py` pass with the new field present. `api/schemas.py` is NOT edited (the metric reports do not live there).
- [ ] `tests/api/test_leak.py`'s `EXPECTED_EVAL_REPORT_FIELDS` (the `test_eval_report_field_set_snapshot` tripwire) is extended with the six new field names (`meeting_rate`, `meetings_total`, `games_total`, `games_with_meeting`, `body_report_meetings`, `emergency_meetings`); none is engine/role state, so `test_eval_report_surface_exposes_no_engine_state_field` still passes. Without this the snapshot assertion fails `uv run pytest`.
- [ ] `frontend/src/types/api.ts` adds a `MeetingRateReport` interface and the `meeting_rate` field on `TournamentEvalReport`, with `meeting_rate: number | null`.
- [ ] `CURRENT_FORMAT_VERSION` is NOT bumped: `meeting_rate` is a wrapper-level metric on `TournamentEvalReport`; the version-stamped inner `TournamentReport` and the persisted replay-record schema are unchanged. The no-bump policy + reason is recorded in the PR `## Decisions`.
- [ ] The committed `replays/samples/tournament-eval-report.json` (4p/1i) is regenerated offline (via `load_tournament_report` + `build_tournament_eval_report` over the frozen 4p/1i replays — no provider run) so it carries `meeting_rate` and re-validates as a `TournamentEvalReport`. Confirm `GET /eval/tournament-report` loads it post-change (e.g. an added test that loads the committed report through `ReplayLoader.tournament_report()`, since the existing eval-route tests use tmp fixtures and would otherwise miss this runtime break).
- [ ] `scripts/run_tournament.py` summary prints `meetings_total`, a `meeting_rate` percentage line (guarded for the no-games case), and a body/emergency trigger line (added onto Task 7.1's merged `_format_summary`).
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `cd frontend && npm run tsc:check` passes.
- [ ] `cd frontend && npm run build` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint
Model the new analyzer directly on `eval/vote_correctness.py`: same module shape
(a frozen `*_Report` Pydantic model with a `model_validator(mode="after")` for the
bucket invariants + a pure `compute_*` fold that accepts `TournamentReport |
Sequence[GameReport]`), same `None`-when-undefined rate convention, no I/O and no
imports from `engine`/`agents`/`llm`. The fold is small:

```python
games = report.games if isinstance(report, TournamentReport) else tuple(report)
games_total = len(games)
games_with_meeting = sum(1 for g in games if g.meetings)
meetings_total = sum(len(g.meetings) for g in games)
body = sum(
    1
    for g in games
    for m in g.meetings
    if _is_body_report(m)
)
emergency = meetings_total - body
rate = games_with_meeting / games_total if games_total > 0 else None
```

`_is_body_report(meeting)` scans `meeting.transcript.reports` for the document
whose `agent_id == meeting.triggered_by` and returns `True` iff that document has
any `FoundBodyObservation` in its `observations`. A meeting with no matching
report (malformed/partial replay) classifies as `emergency` and never raises —
match the partial-replay robustness the other analyzers state. The docstring must
state the TWO-fold catch-all nature of the `emergency` bucket (see the design
decision above) so a later emergency-reviving Wave does not trust it blindly. Add `MeetingRateReport`
and `compute_meeting_rate` to `eval/meeting_quality.py`'s `__all__`.

Test-file placement (note the deliberate asymmetry vs. `vote_correctness.py`, which
has its own `tests/eval/test_vote_correctness.py`): `compute_meeting_rate` lives in
`eval/meeting_quality.py` (the wrapper/builder module), so its unit tests go in
`tests/eval/test_tournament_report.py` (already in scope), NOT a new
`test_meeting_quality.py`. Put the focused unit coverage there: the bucket-validator
invariants (`body + emergency == meetings_total`, `games_with_meeting <= games_total`),
the `None`-rate-iff-`games_total==0` edge, and the body-vs-emergency classification
edge cases for `_is_body_report` (matching report with a `FoundBodyObservation`,
matching report WITHOUT one, and no matching report at all → `emergency`).

For the regression fixtures: after extending `PromptRegressionMetrics`, run each
fixture dir (`v_a`, `v_b`) through `run_prompt_regression` and dump the summaries
to regenerate the single `tests/fixtures/prompt_regression/baseline.json` (the
object keyed by fixture name that `_load_baseline` parses) — the suite is
deterministic and model-free, so this is reproducible (see the
`eval/prompt_regression.py` module docstring's "regenerating fixtures" note; you
only re-dump the baseline scalars, you do NOT re-record replays). The new
meeting-rate scalars should be identical across `v_a` and `v_b` (the v_b variant
only flips one alibi contradiction; it changes neither the meeting count nor the
trigger classification), which is a useful sanity check that the metric is
orthogonal to the prompt-version change.

For `api/routes/eval.py`: `_TournamentEvalReportView` already reuses the four
metric reports verbatim by import — add `meeting_rate: MeetingRateReport` to it the
same way (import `MeetingRateReport` from `eval.meeting_quality`). Confirm
`tests/api/test_eval_routes.py` builds its fixture via `build_tournament_eval_report`
so the new field is present in the dumped payload that `_redact_failed_calls`
re-validates; the existing round-trip test exercises the full chain.

## Public types this task introduces
- `eval.meeting_quality.MeetingRateReport`

These are the symbols downstream tasks will import. Keep their signatures stable.

## Dependency contract check
Run these before editing. If any fail, stop and report — your dependencies are not where this task expects them.

- `uv run python -c "import orchestrator.game"`

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
Open a PR from branch `phase-7-meeting-rate-metric` with a title like `task 7.3: meeting_rate / meetings_total + meeting-trigger breakdown metric`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing tasks/phase-7-plan.md §"Wave 0 — W0.3"; tasks/phase-7-plan.md §"Close gate — Stage A"; audits/audit-2026-05-30-1952-phase-7-meeting-frequency-diagnosis.md §1, §4; DESIGN.md §11.3), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
