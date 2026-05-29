# Phase 5 — Eval And Polish

## Goal
Every prompt or rule change produces a measurable signal in a typed eval report.
Metric tasks stay parallel-safe by writing only their own modules and tests; one
integration task wires them into tournament JSON output. Phase closes when a
prompt-template change can be demonstrated to produce a measurable metric
delta — the regression test suite (5.8) IS the close gate.

**Scope decisions (lock these before dispatching any task):**

- **Hub + eager parallel fan-out.** Task 5.1 (eval report schema) is the hub;
  5.2–5.5 (the four independent metric modules) fan out in parallel after 5.1
  merges. Task 5.6 integrates them. After the mid-phase metric audit, 5.7
  (dashboard frontend) and 5.8 (regression suite) fan out in parallel.
- **Phase 4 carryover preludes: 4.16 and 4.17 land first.** Two
  post-Phase-4 hygiene tasks must merge BEFORE Phase 5 dispatch
  begins: Task 4.16 (ReplayLog fail-loud — fixes the silent doubled-
  files corruption pattern that would otherwise pollute every Phase 5
  metric output) and Task 4.17 (refresh-samples workflow + verify-
  samples + MANIFEST.md — provides the fixture-system substrate that
  Task 5.8's prompt regression suite needs). Format versioning is
  folded into Task 5.1 (eval report schema). The remaining Phase 4
  carryover items (belief rules 2/3/5, per-tick BeliefMatrix coverage,
  `BeliefEntryView.snapshot_tick` semantics tightening) stay
  deferred — they are not Phase 5 prerequisites and belong to a later
  agent-intelligence or UI-enrichment axis.
- **Mid-phase metric correctness audit** runs after 5.6 integrates, before
  5.7/5.8 fan out. Single-tool or two-tool with reconciliation (decide at
  audit-authoring time). Different from the Phase 4 DTO leak audit — the
  defect class is "does the metric compute what it claims?", not "does this
  DTO field leak?". Audit prompt lives at
  `audits/prompts/mid-phase-5-metric-audit-prompt.md` (to be authored after
  5.6 is in flight; do not author it prematurely against substrate that
  doesn't exist yet).
- **Performance pass deferred to 5.9.** DESIGN.md §9 names "≥ 1 game/min
  headless on a laptop" as Phase 5 scope. Lands as a discrete task AFTER the
  dashboard ships. The dashboard works at current rates; perf is polish.
- **Acceptance gate is automated, not manual.** Phase 4 closed on a manual
  UX session; Phase 5 closes on the regression suite (5.8) demonstrating
  one full prompt-change → metric-diff loop. No UX session needed.

## Parallelism
Preludes: Task 4.16 (ReplayLog fail-loud) merges first, then Task 4.17
(refresh-samples workflow + MANIFEST). Then Phase 5 begins at Task 5.1.
Tasks 5.2 through 5.5 fan out after 5.1 because they touch independent
metric modules. Task 5.6 integrates them after 5.2 through 5.5 merge.
Mid-phase metric audit runs after 5.6. Then 5.7 + 5.8 fan out in parallel.
Task 5.9 (performance pass) lands after 5.7 and 5.8.

## Tasks

### Task 5.1 — Eval report schema (with format versioning)
**Branch:** `phase-5-eval-report-schema`
**Depends on:** 4.16 merged, 4.17 merged
**Section refs:** DESIGN.md §11.3, DESIGN.md §11.4
**Complexity:** Small

Define the typed tournament/eval report schema in `eval/report_schema.py`.
This is the Phase 5 hub: every metric module (Tasks 5.2–5.5), the tournament
integration (Task 5.6), the dashboard (Task 5.7), and the regression suite
(Task 5.8) consume this one schema instead of scraping raw replay JSONL ad
hoc (DESIGN.md §11.3). It is the contract those six tasks build against, so
its field names and nesting are load-bearing — get them stable here.

The data this report must carry already exists as typed replay records
written per game during Phase 3/4 (DESIGN.md §11.4):

- `orchestrator.replay.GameEndReplayEntry` — decisive winner + reason per game.
- `orchestrator.replay.MeetingReplayEntry` — per meeting: `transcript`
  (`MeetingTranscript`), `ballots` (`tuple[VoteBallot, ...]`),
  `contradictions` (`tuple[ContradictionRef, ...]`), `outcome`
  (`MeetingOutcome`), `ejected_player_id`, `llm_calls`
  (`tuple[LLMCallRecord, ...]`), and `prompt_versions` (`Mapping[str, str]`).
- `orchestrator.replay.LLMCallRecord` — per call: `model`, `input_tokens`,
  `output_tokens`, `cost_usd`, `agent_id`, `call_kind`.
- `eval.balance_eval.BalanceReport` — current tournament-level outcome buckets
  (a frozen dataclass; see the BalanceReport decision below).

So 5.1 is largely an **aggregation + typing** task, not a from-scratch data
model: define a per-tournament Pydantic v2 artifact that composes these
existing per-game records into one typed object that downstream code reads
without re-parsing JSONL. Reuse the leaf meeting artifact types from
`meetings.schemas` (`MeetingTranscript`, `VoteBallot`, `ContradictionRef`,
`MeetingOutcome`, `PlayerId`) by import — do NOT redefine them. The `eval/`
package may import `meetings/`, `orchestrator/`, `engine/`, and `llm/`
freely; only `agents/` is firewalled from `engine/`, and this task touches
neither side of that boundary.

The schema carries a top-level `format_version: int` (carryover from Phase
4's deferred replay-format-versioning item) so future schema evolution is
explicit rather than relying on Pydantic's default-on-missing backward
compatibility. This task defines and versions the schema only. It does NOT
wire `scripts/run_tournament.py` to emit it and does NOT migrate
`run_balance_eval`'s return type — that integration is Task 5.6, which holds
`eval/balance_eval.py` and `scripts/run_tournament.py` in its scope.

**Files in scope:**
- eval/report_schema.py
- orchestrator/replay.py (add a `format_version` field to the replay entry models ONLY if the implementing agent resolves the format-version-namespace decision toward a shared namespace; the documented bias is report-only, which leaves replay.py untouched)
- tests/eval/test_report_schema.py

**Files NOT in scope:**
- engine/
- agents/
- llm/
- meetings/ (import its schemas; do not modify them)
- api/
- frontend/
- eval/balance_eval.py (BalanceReport migration is Task 5.6)
- eval/vote_correctness.py
- eval/accusation_calibration.py
- eval/alibi_fabrication.py
- eval/cost_dashboard.py
- eval/meeting_quality.py
- scripts/run_tournament.py
- DESIGN.md
- AGENT_IMPLEMENTATION.md

**Definition of done:**
- [ ] `eval/report_schema.py` defines a top-level tournament report model (Pydantic v2) that composes, per game: the decisive outcome/winner, a reference to the game's replay file, the per-meeting artifacts (transcript, ballots, contradictions, outcome, ejected player), the per-call LLM cost/usage/model metadata, and the prompt-template versions in play. These are the structured inputs Phase 5 metrics consume; the report does NOT itself compute metric outputs.
- [ ] Leaf meeting artifact types (`MeetingTranscript`, `VoteBallot`, `ContradictionRef`, `MeetingOutcome`, `PlayerId`) are imported from `meetings.schemas`, not redefined.
- [ ] The top-level model carries a `format_version: int` field whose current value is `1`. A Pydantic field validator rejects any value greater than the current version (an unknown future format) with a clear error; a value less than current is accepted only if a documented migration path exists — for v1 there is no prior version, so only `1` is valid.
- [ ] The schema is structured so Phase 5 metric outputs can be attached by downstream tooling (Task 5.6) WITHOUT changing the raw per-game replay records — i.e. metrics compose over the report, they do not mutate replay JSONL.
- [ ] All models are `extra="forbid"` and frozen, consistent with `orchestrator.replay` and `meetings.schemas` conventions.
- [ ] Decision recorded in the PR's `## Decisions` block: whether `format_version` is namespaced to the report only (bias) OR shared across report + replay JSONL records. If shared, the replay entry models in `orchestrator/replay.py` gain the field; if report-only, `replay.py` is untouched. State which and why.
- [ ] Decision recorded in the PR's `## Decisions` block: the relationship between the new Pydantic report schema and the existing `eval.balance_eval.BalanceReport` dataclass. The bias is that the Pydantic report supersedes `BalanceReport` as the typed tournament artifact (Pydantic is the project convention for cross-module DTOs per AGENTS.md), with the actual `run_balance_eval` migration deferred to Task 5.6. Confirm the report can represent everything `BalanceReport` does (outcome buckets, seeds used) so 5.6 can drop the dataclass without information loss. Do NOT edit `balance_eval.py` in this task.
- [ ] `tests/eval/test_report_schema.py` covers: round-trip serialize/deserialize of a fully populated report; the `format_version` validator accepting `1` and rejecting `2`; `extra="forbid"` rejecting an unknown field; and a report built from a realistic multi-game / multi-meeting fixture.
- [ ] `uv run mypy --strict eval` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes (firewall preserved).
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

Read `orchestrator/replay.py` (the `LLMCallRecord`, `MeetingReplayEntry`,
`GameEndReplayEntry`, `FailedCallReplayEntry`, `ReplayLogEntry` models) and
`eval/balance_eval.py` (`BalanceReport`) before designing the schema. The
report is the aggregation layer over those per-game records.

A proposed model skeleton (the implementing agent may refine names, but keep
the three-level tournament → game → meeting nesting):

```python
CURRENT_FORMAT_VERSION: Final[int] = 1

class GameCostSummary(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    total_cost_usd: float
    total_input_tokens: int
    total_output_tokens: int
    by_model: Mapping[str, float]  # model id -> cost_usd

class MeetingReport(BaseModel):
    # composes MeetingReplayEntry's structured payloads, reusing
    # MeetingTranscript / VoteBallot / ContradictionRef / MeetingOutcome
    ...

class GameReport(BaseModel):
    game_id: str
    seed: int
    winner: WinnerSide | None
    reason: str
    replay_ref: str            # e.g. "replay-seed-42.jsonl"
    meetings: tuple[MeetingReport, ...]
    prompt_versions: Mapping[str, str]
    cost: GameCostSummary

class TournamentReport(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    format_version: int = CURRENT_FORMAT_VERSION
    games: tuple[GameReport, ...]
    seeds_used: tuple[int, ...]

    @field_validator("format_version")
    @classmethod
    def _reject_unknown_version(cls, v: int) -> int:
        if v > CURRENT_FORMAT_VERSION:
            raise ValueError(f"unknown report format_version {v} ...")
        return v
```

Decide whether `replay_ref` is a bare filename or a relative path — match
how `run_balance_eval` names files (`replay-seed-{seed}.jsonl`). Do not
build a loader that reads JSONL into this schema in this task; that adapter
lands in Task 5.6. This task ships the schema + its validator + unit tests
only. Construct test fixtures by instantiating the models directly, not by
running a tournament.

**Public types introduced:**
- eval.report_schema.TournamentReport
- eval.report_schema.GameReport
- eval.report_schema.MeetingReport
- eval.report_schema.GameCostSummary
- eval.report_schema.CURRENT_FORMAT_VERSION

**Integration risk:**

This schema is the convergence point for all of Phase 5 — 5.2–5.8 build on
it. Breaking or reshaping it later breaks every downstream consumer.

- **Name stability is the real risk, not code volume.** The task is small to
  implement but high-leverage: a field rename after 5.2–5.5 ship forces a
  six-way edit. Get the nesting and field names right here; that is why this
  task carries the `format_version` field from day one.
- **Do not over-reach into integration.** The temptation is to also write the
  JSONL→report loader and wire `run_tournament.py`. That is Task 5.6 and is
  explicitly out of scope. A loader written here against an un-merged
  integration would be dead code the audit has to reconcile.
- **Reuse, don't fork, meeting artifact types.** Redefining
  `MeetingTranscript` / `VoteBallot` in `eval/` would create two
  drifting definitions of the same payload. Import from `meetings.schemas`.
- **The format-version validator must fail loud** (AGENTS.md "no silent
  fallbacks"): an unknown future version raises, it does not coerce or warn.
- **BalanceReport coexists until 5.6.** Leaving `balance_eval.py` untouched
  means `BalanceReport` and the new report briefly overlap. That is
  intentional — the migration is sequenced into 5.6 so this task stays a
  pure additive schema definition with no behavioral change to the tournament
  path.

**Ready-to-paste prompt:** `agent_prompts/task-5-1-eval-report-schema.md`

### Task 5.2 — Vote-correctness metric
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


**Implementation hint:**

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

**Public types introduced:**
- eval.vote_correctness.VoteCorrectnessReport
- eval.vote_correctness.compute_vote_correctness

**Integration risk:**

- **Parallel-safe with 5.3–5.5.** This task writes only `eval/vote_correctness.py` and its test. It must not edit `eval/report_schema.py` or any sibling metric module; if it needs a schema change, that is a signal the 5.1 schema was wrong — stop and report rather than widening scope.
- **Ground truth comes only from `roles`.** Deriving impostor identity from accusations or vote outcomes would make the metric circular (it would measure agreement with the vote, not correctness of it).
- **Define the predicate once, test it adversarially.** The whole metric hinges on the "real evidence" predicate; a fixture where an impostor is ejected on *no* evidence must score as incorrect, or the metric is just the impostor-ejection rate.

**Ready-to-paste prompt:** `agent_prompts/task-5-2-vote-correctness-metric.md`

### Task 5.3 — Accusation-calibration metric
**Branch:** `phase-5-accusation-calibration-metric`
**Depends on:** 5.1 merged
**Section refs:** DESIGN.md §11.3
**Complexity:** Medium

A pure analyzer over `eval.report_schema.TournamentReport` that answers
DESIGN.md §11.3's calibration question: are high-confidence accusations
correct (the target really is an impostor) more often than low-confidence
ones? A well-calibrated agent population shows actual-impostor-rate rising
monotonically with stated confidence.

Accusations carry an explicit confidence in two places, both reachable from
the report:

- `AccusationClaim` (`type="accusation"`, `against: PlayerId`, `confidence:
  float` in [0,1], `reason: str`) — nested in `Statement.claims` and
  `ReportDocument.claims` inside `MeetingReport.transcript`.
- `VoteBallot` (`voter`, `target: PlayerId | "SKIP"`, `confidence: float`) on
  `MeetingReport.ballots`.

Correctness is decided by `GameReport.roles[target] == "IMPOSTOR"` — the
ground-truth map the 5.6 loader fills, never an inferred role.

**Files in scope:**
- eval/accusation_calibration.py
- tests/eval/test_accusation_calibration.py

**Files NOT in scope:**
- engine/
- agents/
- llm/
- api/
- frontend/
- scripts/run_tournament.py
- eval/report_schema.py
- eval/vote_correctness.py
- eval/alibi_fabrication.py
- eval/cost_dashboard.py
- DESIGN.md
- AGENT_IMPLEMENTATION.md

**Definition of done:**
- [ ] `eval/accusation_calibration.py` exposes a pure function from a `TournamentReport` to a frozen Pydantic result model binning accusations by confidence and reporting per-bin actual-impostor-rate, count, and mean confidence.
- [ ] Bin edges are an explicit, documented choice (e.g. fixed-width deciles or quartiles over [0,1]); the binning is deterministic and total. Because `confidence` is `Field(ge=0.0, le=1.0)`, `1.0` is a legal value: bins are half-open `[lo, hi)` except the final bin, which is closed `[lo, 1.0]`, so `confidence == 1.0` lands in the top bin (implement as `bin_index = min(int(c * n_bins), n_bins - 1)`).
- [ ] Each accusation's correctness is `roles[target] == "IMPOSTOR"` (subscript, not `.get`); a `"SKIP"` ballot target is excluded BEFORE the lookup (it accuses no one). `roles` is post-game ground truth covering every player by construction, so a target absent from `roles` signals a malformed report and MUST fail loud (raise) — AGENTS.md "no silent fallbacks". Do not add an "unresolved" bucket and do not let a failed lookup silently count as a non-hit (which would bias that bin's actual-impostor-rate downward). The no-accusations / no-meetings / all-`SKIP` robustness below applies to the ABSENCE of accusations, never to a present accusation with an unresolvable target.
- [ ] Decision recorded in the PR's `## Decisions` block: which confidence source(s) the metric consumes — `AccusationClaim` only, `VoteBallot` only, or both (and if both, whether they are pooled into one curve or reported as two). Bias: report `AccusationClaim`-based and `VoteBallot`-based calibration separately, since a vote and a mid-meeting accusation are different acts.
- [ ] The result model exposes enough to judge calibration (per-bin actual-impostor-rate vs bin midpoint); a scalar calibration error (e.g. expected-calibration-error) is optional but, if included, documented.
- [ ] Partial-replay robustness: a game with no accusations, no meetings, or all-`SKIP` ballots produces empty/zero bins without raising.
- [ ] `tests/eval/test_accusation_calibration.py` builds report fixtures directly covering: high-confidence accusations against real impostors (well-calibrated); high-confidence accusations against crewmates (mis-calibrated); a spread across bins including `confidence` exactly `0.0` and exactly `1.0` (to pin the boundary convention); the no-accusations / all-`SKIP` case; and a malformed accusation whose target is absent from `roles`, asserting the analyzer raises.
- [ ] `uv run mypy --strict eval` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` and `uv run python scripts/validate_task_docs.py` pass.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.


**Implementation hint:**

See DESIGN.md §11.3. Walk every `MeetingReport`; pull `AccusationClaim`s out
of `transcript.reports[*].claims` and `transcript.statements[*].claims`
(filter the `Claim` union on `type == "accusation"`), and/or `ballots` per
the source decision. For each `AccusationClaim`, bucket by `confidence` and
tally `roles[claim.against] == "IMPOSTOR"`. For a `VoteBallot` (if the source
decision includes ballots), first skip `target == "SKIP"`, then tally
`roles[ballot.target] == "IMPOSTOR"` — note the ballot field is `target` (not
`against`) and may be the literal `"SKIP"`. A bin's actual-impostor-rate is
`impostor_hits / accusations_in_bin`. Calibration is read off by comparing
that rate to the bin's confidence midpoint. Build fixtures by instantiating
the schema models directly; this task does NOT touch the tournament runner
(that is Task 5.6).

**Public types introduced:**
- eval.accusation_calibration.AccusationCalibrationReport
- eval.accusation_calibration.CalibrationBin
- eval.accusation_calibration.compute_accusation_calibration

**Integration risk:**

- **Parallel-safe with 5.2/5.4/5.5.** Writes only its own module + test; must not edit `report_schema.py` or siblings.
- **Confidence-source ambiguity is the main trap.** `AccusationClaim` and `VoteBallot` both carry confidence but mean different things; pooling them silently would muddy the curve. Resolve and document before coding.
- **Empty-bin handling.** Bins with zero accusations must report a count of 0 and a well-defined (not NaN) rate, or downstream rendering (5.7) breaks.

**Ready-to-paste prompt:** `agent_prompts/task-5-3-accusation-calibration-metric.md`

### Task 5.4 — Alibi-fabrication-rate metric
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


**Implementation hint:**

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

**Public types introduced:**
- eval.alibi_fabrication.AlibiFabricationReport
- eval.alibi_fabrication.compute_alibi_fabrication_rate

**Integration risk:**

- **Parallel-safe with 5.2/5.3/5.5.** Writes only its own module + test; must not edit `report_schema.py` or siblings.
- **The alibi↔contradiction join is the core hazard.** `ContradictionRef` has no tick/room, so the choice is subject-membership (coarse: false-positive "catches" from cross-author same-subject conflicts, and over-attribution across multiple same-subject alibis) vs event-id reconstruction (precise, but couples to private transcript helpers). Pick a rule, document its accepted failure mode, and test both the survived and caught directions — including the cross-author case — so the rule is pinned.
- **Author vs subject confusion.** "Impostor alibi" is by author role, not by the player the alibi is *about*. Getting this backwards silently changes what the metric measures.

**Ready-to-paste prompt:** `agent_prompts/task-5-4-alibi-fabrication-rate-metric.md`

### Task 5.5 — Cost dashboard metric
**Branch:** `phase-5-cost-dashboard`
**Depends on:** 5.1 merged
**Section refs:** DESIGN.md §10.4, DESIGN.md §11.3
**Complexity:** Medium

A pure analyzer over `eval.report_schema.TournamentReport` that produces the
cost-dashboard data (DESIGN.md §10.4 Cost bullet for the ~$0.20/game target;
§11.3 reporting; the per-game cost substrate is
`orchestrator.replay.compute_cost_usd` / `eval.report_schema.GameCostSummary`):
cost-per-game and cost-per-prompt-version, so a prompt change's cost impact
is legible alongside its quality impact. This is the cost half of the Phase 5
close loop — a prompt-template change should show both a metric delta (5.2–5.4)
and a cost delta here.

The inputs, all on the merged schema:

- `GameReport.cost: GameCostSummary` — per game: `total_cost_usd`,
  `total_input_tokens`, `total_output_tokens`, `by_model: Mapping[str,
  float]` (USD keyed by model id).
- `GameReport.prompt_versions: Mapping[str, str]` — template name → version
  marker in play for that game (templates load once per run, so this is
  game-granular).
- `GameReport.failed_calls: tuple[FailedCallReplayEntry, ...]` — meeting-
  aborting LLM calls whose `cost_usd` was still charged. `GameCostSummary.total_cost_usd`
  ALREADY includes this spend: the canonical reducer
  `orchestrator.replay.compute_cost_usd` sums meeting `llm_calls` cost PLUS
  every `failed_call` cost (replay.py:452-458), and the `GameReport.failed_calls`
  docstring states the total counts them. So the dashboard reads
  `total_cost_usd` as authoritative and must NOT add `failed_calls` cost again.
- `MeetingReport.llm_calls` — per-call `LLMCallRecord` (`model`, `cost_usd`,
  tokens) if finer-than-game slicing is needed.

**Files in scope:**
- eval/cost_dashboard.py
- tests/eval/test_cost_dashboard.py

**Files NOT in scope:**
- engine/
- agents/
- llm/ provider behavior
- api/
- frontend/
- scripts/run_tournament.py
- eval/report_schema.py
- eval/vote_correctness.py
- eval/accusation_calibration.py
- eval/alibi_fabrication.py
- DESIGN.md
- AGENT_IMPLEMENTATION.md

**Definition of done:**
- [ ] `eval/cost_dashboard.py` exposes a pure function from a `TournamentReport` to a frozen Pydantic result model with at least: total tournament cost, mean cost-per-game, and a cost-per-prompt-version breakdown.
- [ ] Cost-per-prompt-version is keyed by `(template_name, version)` drawn from each game's `prompt_versions`, summing the games that ran that version. A game runs several templates at once; bias: attribute the full game cost once under EACH `(template, version)` present (do NOT split it across templates). Document in the PR's `## Decisions` block that the per-version totals therefore OVERLAP and are NOT a partition — summing them across versions does not recover the tournament total and must not be presented as if it does.
- [ ] Within a single tournament run `prompt_versions` is constant across all games (one template set is loaded per run), so for a real one-run report the per-`(template, version)` breakdown collapses to one key equal to the tournament total. Its comparative value (version A vs version B) is therefore a CROSS-REPORT comparison — two runs, consumed by Task 5.8's regression loop — not a within-report delta. The result model should be cleanly comparable/mergeable across two `CostDashboard`s for that purpose, or the contract states that 5.8 computes the cross-run delta from two dashboards.
- [ ] The metric treats `GameCostSummary.total_cost_usd` as the authoritative complete per-game spend and does NOT add `sum(fc.cost_usd for fc in failed_calls)` on top — `total_cost_usd` already includes failed-call cost (via `orchestrator.replay.compute_cost_usd`; confirmed by the `GameReport.failed_calls` docstring). Note this no-double-count invariant in the PR's `## Decisions` block. (The matching loader-side obligation — Task 5.6 populates `total_cost_usd` via `compute_cost_usd` and does not double-add — is carried into 5.6's elaboration.)
- [ ] A per-model cost roll-up is available (aggregating `GameCostSummary.by_model` across games), so a mixed-tier tournament is auditable per model.
- [ ] Partial-replay robustness: a game with zero meetings/zero cost, an empty `prompt_versions`, or a tournament with one game all produce well-defined numbers (no division-by-zero, no NaN).
- [ ] `tests/eval/test_cost_dashboard.py` builds report fixtures directly covering: a structural/constructibility fixture with two prompt-versions present (verify per-version keying and summation — labelled as a constructibility test, since a real single run carries one version set); a single-version report that collapses to one key equal to the total cost; a game carrying `failed_calls` (verify the dashboard does NOT double-count failed-call spend); and a mixed-`by_model` game.
- [ ] `uv run mypy --strict eval` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` and `uv run python scripts/validate_task_docs.py` pass.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.


**Implementation hint:**

See DESIGN.md §10.4. Aggregate over `report.games`: total cost is the sum of
each game's `cost.total_cost_usd` (which already includes failed-call spend —
do NOT add `failed_calls` again); cost-per-prompt-version groups games by
their `prompt_versions` entries. `orchestrator.replay.compute_cost_usd` is the
canonical file-level cost reducer (and is what already folds failed calls
in), but this metric works over the already-aggregated report, not raw JSONL —
do not re-read files. Build fixtures by instantiating the schema
models directly; this task does NOT wire the dashboard into tournament JSON
output (Task 5.6) and does NOT build the frontend (Task 5.7) — it produces
the typed data those consume.

**Public types introduced:**
- eval.cost_dashboard.CostDashboard
- eval.cost_dashboard.PromptVersionCost
- eval.cost_dashboard.compute_cost_dashboard

**Integration risk:**

- **Parallel-safe with 5.2–5.4.** Writes only its own module + test; must not edit `report_schema.py` or siblings.
- **Failed-call double-counting is the cost trap.** `failed_calls` carry real spend that `total_cost_usd` already includes (via `compute_cost_usd`). The risk is the dashboard adding it a second time, or the 5.6 loader populating `total_cost_usd` some other way and then the dashboard adding failed calls. The fix is one-sided and pinned here: read `total_cost_usd`, never add `failed_calls`; the loader-side half is carried into 5.6.
- **Attribution semantics must be explicit.** "Cost per prompt version" is ambiguous when a game mixes templates; an undocumented choice makes the dashboard's numbers unfalsifiable. Document and test the attribution rule.

**Ready-to-paste prompt:** `agent_prompts/task-5-5-cost-dashboard-per-prompt-version-cost.md`

### Task 5.6 — Tournament metric integration
**Branch:** `phase-5-tournament-metric-integration`
**Depends on:** 5.2 merged, 5.3 merged, 5.4 merged, 5.5 merged
**Section refs:** DESIGN.md §11.3
**Complexity:** Integration

The convergence point for Phase 5. Four things, in order:

1. **Build the JSONL→`TournamentReport` loader** (deferred from Task 5.1, does
   not exist yet). A tournament run already writes one
   `replay-seed-{seed}.jsonl` per seed (`eval.balance_eval.run_balance_eval`)
   and `orchestrator.replay.read_all_entries(path)` parses each back into the
   typed record union (`ReplayEntry` / `MeetingReplayEntry` /
   `GameEndReplayEntry` / `FailedCallReplayEntry`). The loader folds those
   records into a `GameReport` per seed and collects them into a
   `TournamentReport`. The `MeetingReplayEntry` → `MeetingReport` mapping is
   near 1:1 (same `meeting_id`/`tick`/`triggered_by`/`outcome`/
   `ejected_player_id`/`transcript`/`ballots`/`contradictions`/`llm_calls`).
   `GameEndReplayEntry` gives `winner`/`reason`/`final_tick`;
   `FailedCallReplayEntry` rows become `GameReport.failed_calls`.
2. **Populate `GameReport.roles` from the seeded game setup** — the single
   report field with no replay-JSONL source (roles are kept out of replay by
   the leak firewall, `report_schema.py:28-29`). `HeadlessGame.run()` returns a
   `HeadlessGameResult` whose `final_state: WorldState` carries
   `players[id].role` (`engine.world.WorldState.players` →
   `engine.entities.PlayerState.role`). Capture roles from that in-memory
   result during the run — NOT by re-parsing the replay file. An empty `roles`
   map is fail-loud: tasks 5.2–5.4 silently score zero impostor ejections /
   all-unresolved targets without it.
3. **Run the four metrics and wrap.** Call the merged public analyzers —
   `eval.vote_correctness.compute_vote_correctness`,
   `eval.accusation_calibration.compute_accusation_calibration`,
   `eval.alibi_fabrication.compute_alibi_fabrication_rate`,
   `eval.cost_dashboard.compute_cost_dashboard` — over the `TournamentReport`,
   and wrap report + the four results into a new frozen `TournamentEvalReport`
   model. Because `TournamentReport` is frozen + `extra="forbid"`, the metric
   outputs CANNOT be added as fields on it; they live on the new wrapper, which
   is the single typed shape Task 5.7 (dashboard) and Task 5.8 (regression
   suite) consume.
4. **Emit + supersede.** `scripts/run_tournament.py` emits the
   `TournamentEvalReport` as JSON. This supersedes `eval.balance_eval.BalanceReport`
   as the tournament artifact per Task 5.1's `## Decisions` (Task 5.1 deferred
   the migration here).

**Files in scope:**
- eval/meeting_quality.py
- eval/balance_eval.py
- scripts/run_tournament.py
- tests/eval/test_tournament_report.py
- tests/eval/test_balance_eval.py (only if the `run_balance_eval` refactor in the migration decision perturbs its existing assertions; leave untouched otherwise)

**Files NOT in scope:**
- engine/
- agents/
- llm/ provider behavior
- api/
- frontend/
- meetings/ (import its schemas; do not modify)
- orchestrator/ (import `read_all_entries`, `compute_cost_usd`, `HeadlessGame`; do not modify)
- eval/report_schema.py (the frozen 5.1 hub — import `TournamentReport`/`GameReport`/`MeetingReport`/`GameCostSummary`; do NOT edit it. The metric-output wrapper is a NEW model in eval/meeting_quality.py, not a field added here.)
- eval/vote_correctness.py
- eval/accusation_calibration.py
- eval/alibi_fabrication.py
- eval/cost_dashboard.py
- DESIGN.md
- AGENT_IMPLEMENTATION.md

**Definition of done:**
- [ ] A loader builds a `eval.report_schema.TournamentReport` from a tournament run: one `GameReport` per seed assembled from that seed's replay records (via `orchestrator.replay.read_all_entries`), with `meetings` from `MeetingReplayEntry`, `winner`/`reason`/`final_tick` from `GameEndReplayEntry`, and `failed_calls` from `FailedCallReplayEntry`.
- [ ] `GameReport.roles` is populated from the seeded game setup (`HeadlessGameResult.final_state.players[id].role`), NOT the replay JSONL. An empty/missing `roles` for a finished game is a fail-loud error.
- [ ] `GameReport.cost` (`GameCostSummary`) is built so `total_cost_usd` equals `orchestrator.replay.compute_cost_usd(path)` — the canonical reducer, which ALREADY folds in `failed_calls` cost. `total_input_tokens` / `total_output_tokens` / `by_model` are summed across the same records (meeting `llm_calls` plus `failed_calls`) in one pass. The dashboard (5.5) must NOT add failed-call cost again — this loader is the single place that spend is counted (the no-double-count invariant).
- [ ] A new frozen, `extra="forbid"` wrapper model in `eval/meeting_quality.py` (e.g. `TournamentEvalReport`) holds the immutable `TournamentReport` plus the four metric result models (`VoteCorrectnessReport`, `AccusationCalibrationReport`, `AlibiFabricationReport`, `CostDashboard`) as named fields. A builder (e.g. `build_tournament_eval_report`) calls the four `compute_*` analyzers and assembles it; it consumes their public APIs and duplicates no metric logic.
- [ ] `scripts/run_tournament.py` emits the `TournamentEvalReport` as JSON (validated round-trip: `model_validate_json(model_dump_json(...))`). `python scripts/run_tournament.py --num-games 200 --output-dir <dir>` (the merge criteria's "--N=200") produces a JSON report carrying all four Phase 5 metrics over a 200-game run.
- [ ] The `BalanceReport` migration decision (below) is executed: the `TournamentReport`/`TournamentEvalReport` supersedes `BalanceReport` as the emitted artifact, with crew/impostor/tick-budget buckets recoverable from `GameReport.winner` (`CREWMATES`/`IMPOSTORS`/`None`) and `seeds_used` — no information loss (already proven by `tests/eval/test_report_schema.py`).
- [ ] Partial-run robustness: a seed whose game crashed before a `game_over` record yields a `GameReport` with `winner=None`, `final_tick=None`, and whatever meetings were recorded — the loader does not raise on a missing `game_over` (it still fails loud on a doubled/corrupted file via `read_all_entries`'s `CorruptedFileError`).
- [ ] `tests/eval/test_tournament_report.py` runs a small tournament with the FAKE provider (no network), and asserts: every `GameReport.roles` is non-empty with key set == the game's players and exactly `num_impostors` entries `== "IMPOSTOR"`; the emitted JSON validates against the schema; all four metric blocks are present; and per-game `cost.total_cost_usd` equals `compute_cost_usd` for that seed (no double-count).
- [ ] All four `compute_*` are invoked via their public module entry points; no metric math is reimplemented in this task.
- [ ] `uv run mypy --strict eval` passes (and `scripts` if covered by mypy config).
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes (the firewall: `eval/` may import `engine`/`orchestrator`/`meetings`; none of those import back).
- [ ] `uv run python scripts/generate_prompts.py --check` and `uv run python scripts/validate_task_docs.py` pass.
- [ ] `uv run pytest` passes (including the untouched `test_balance_eval.py`, unless the migration decision intentionally edits it).
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

Loader recipe, per seed:

```python
entries = read_all_entries(output_dir / f"replay-seed-{seed}.jsonl")
meetings = tuple(MeetingReport(...) for e in entries if isinstance(e, MeetingReplayEntry))
failed   = tuple(e for e in entries if isinstance(e, FailedCallReplayEntry))
end      = next((e for e in entries if isinstance(e, GameEndReplayEntry)), None)
roles    = {pid: ps.role for pid, ps in result.final_state.players.items()}  # from HeadlessGameResult
cost     = _game_cost_summary(entries)  # total via compute_cost_usd; tokens + by_model summed in-pass
game = GameReport(game_id=..., seed=seed, winner=end.winner if end else None,
                  reason=end.reason if end else "...", final_tick=end.tick if end else None,
                  roles=roles, replay_ref=f"replay-seed-{seed}.jsonl",
                  meetings=meetings, failed_calls=failed, prompt_versions=..., cost=cost)
```

Recommended structure: add `run_tournament_eval(...) -> TournamentReport` to
`eval/balance_eval.py` doing the run + roles capture + assembly, and reduce the
existing `run_balance_eval(...) -> BalanceReport` to a thin wrapper over it
(so `test_balance_eval.py` stays green and there is one game-running path).
`prompt_versions` collapses from the per-meeting `MeetingReplayEntry.prompt_versions`
(constant within a run); for a game with no meetings, leave it empty (the cost
dashboard handles empty). The wrapper + builder live in `eval/meeting_quality.py`.
Use the FAKE provider in tests — never call a real model in CI.

**Public types introduced:**
- eval.meeting_quality.TournamentEvalReport
- eval.meeting_quality.build_tournament_eval_report
- eval.balance_eval.run_tournament_eval

**Decisions to resolve and record in the PR's `## Decisions` block:**
- Migration shape: `run_tournament_eval` + `run_balance_eval`-as-thin-reducer (bias — keeps `test_balance_eval.py` green, single run path) vs full retirement of `BalanceReport` (requires editing `test_balance_eval.py`).
- Roles source: capture from `HeadlessGameResult.final_state.players` during the run (bias) vs re-derive from the seeded setup.
- Where the wrapper's `format_version` comes from: reuse `TournamentReport.format_version` (bias) vs a wrapper-level version.
- JSON emit destination: a file under `--output-dir` (bias) and/or stdout; whether the human-readable balance summary is retained.

**Integration risk:**

Convergence point for Phase 5 — Tasks 5.7 and 5.8 build on the `TournamentEvalReport` shape this task defines.

- **`roles` population is the silent-zero trap.** If the loader is built purely from replay files (the obvious reading of "fold metrics into the report"), `roles` is empty and vote-correctness / accusation-calibration / alibi-fabrication all silently report zero impostor signal. Roles MUST come from the in-memory seeded result, and the test asserts non-empty coverage.
- **No double-counting cost.** `compute_cost_usd` already includes failed-call spend; the loader populates `total_cost_usd` via it and the 5.5 dashboard never re-adds `failed_calls`. Building `total_cost_usd` any other way risks drift.
- **Do not edit the frozen hub or the metric modules.** `report_schema.py` and the four `eval/*` metric files are import-only. A schema change here means 5.1 was wrong — stop and report.
- **Determinism / no network.** Integration tests run the fake provider on a few seeds; the 200-game JSON check is a local/manual gate, not CI.
- **BalanceReport migration must not break out-of-scope tests.** `test_balance_eval.py` asserts `isinstance(report, BalanceReport)`; the thin-reducer approach preserves that. Full retirement requires pulling that test into scope deliberately.

**Ready-to-paste prompt:** `agent_prompts/task-5-6-tournament-metric-integration.md`

### Mid-phase metric correctness audit

After 5.6 merges, run the Phase 5 mid-phase metric correctness audit
before dispatching 5.7 and 5.8. The audit prompt lives at
`audits/prompts/mid-phase-5-metric-audit-prompt.md` (to be authored
after 5.6 is in flight; do not author it prematurely against substrate
that doesn't exist yet).

**Audit scope:**
- For each metric in `eval/` (`vote_correctness`, `accusation_calibration`,
  `alibi_fabrication`, `cost_dashboard`): does the computed number match
  the docstring claim? Construct a synthetic fixture replay where the
  ground-truth metric value is known by inspection; confirm the metric
  matches.
- Partial-replay robustness: does each metric handle replays with no
  meetings, ejected impostors, partial runs (no `game_over` record)?
- Schema integrity: does the `eval.report_schema` artifact emitted by
  `scripts/run_tournament.py` validate against the 5.1 schema? Are
  there fields populated that the schema doesn't promise, or schema
  fields that the integration leaves empty?
- Prompt-version provenance: does the report correctly attribute each
  metric value to the prompt-template versions in play?

**Audit verdict shape:** "Mid-phase metric audit passes — proceed to
fan out 5.7 + 5.8" OR "Mid-phase metric audit blocks fan-out —
repair tasks required: ..."

Two-tool with reconciliation (per the Phase 4 pattern) is the
recommended shape; single-tool is acceptable if the audit surface is
small. Output: one Markdown audit at
`audits/audit-YYYY-MM-DD-HHMM-mid-phase-5-metric.md`.

### Task 5.7 — Tournament dashboard frontend page
**Branch:** `phase-5-tournament-dashboard-frontend-page`
**Depends on:** 5.6 merged
**Section refs:** DESIGN.md §11.3, DESIGN.md §7
**Complexity:** Integration

Add a Tournament Dashboard view to the spectator frontend that renders the
`eval.meeting_quality.TournamentEvalReport` (the artifact Task 5.6 emits as
`tournament-eval-report.json`): the four Phase 5 metrics (vote correctness,
accusation calibration, alibi fabrication, cost dashboard) plus the balance
outcome summary. The Phase 4 app is a single-page replay viewer; this task adds
a SECOND top-level view, reached by tab navigation, backed by its own store and
a new read endpoint. This is a full-stack slice (backend read endpoint →
typed client → store → component), so its scope is wider than the other Phase 5
tasks; that is expected for the dashboard.

The merged data shape it renders (`eval/meeting_quality.py`):
`TournamentEvalReport { report: TournamentReport, vote_correctness:
VoteCorrectnessReport, accusation_calibration: AccusationCalibrationReport,
alibi_fabrication: AlibiFabricationReport, cost_dashboard: CostDashboard }`. All
five are frozen Pydantic models that round-trip through JSON.

**Decisions resolved (record any deviation in the PR's `## Decisions` block):**
- **Navigation: tabs, not a router.** Add tab state to `App.tsx`
  ("Replay Viewer" | "Tournament Dashboard"); render one view at a time. No
  `react-router-dom` dependency (the app is single-page; a router is dead
  weight for two views).
- **Store: a sibling `useTournamentStore`, NOT an extension of
  `useReplayStore`.** The Phase 4 store is explicitly frozen (its header says
  adding a field requires touching all consumers). The dashboard's state is
  independent (one fetched report, no playback), so it gets its own Zustand
  store.
- **Report source: a new read endpoint** `GET /api/tournament-report` (in
  `api/routes/eval.py`, mirroring the existing `/cost-summary` thin-adapter
  pattern) serving the latest `tournament-eval-report.json` from the configured
  replay/eval directory via `ReplayLoader`. Returns 404 when no report is
  present. This matches the replay-viewer architecture (frontend fetches typed
  JSON via `api/client.ts`); a committed static asset would go stale. The
  endpoint is privileged like the rest of the spectator API and intentionally
  exposes `roles` ground truth for the dashboard.
- **Rendering: plain React + CSS/SVG, NOT PixiJS.** The metric views are tables,
  bars, a calibration curve (rate-vs-confidence), and a cost breakdown — data
  widgets, not a spatial canvas. PixiJS is the map renderer; do not pull it into
  a data view. No new charting dependency unless a clear need is documented.

**Files in scope:**
- frontend/src/components/TournamentDashboard.tsx (and small co-located subcomponents if needed)
- frontend/src/store/tournamentStore.ts (new sibling Zustand store)
- frontend/src/api/client.ts (add `getTournamentReport()`)
- frontend/src/types/api.ts (add the `TournamentEvalReport` TS types mirroring the Pydantic models)
- frontend/src/App.tsx (tab navigation between the replay viewer and the dashboard)
- api/routes/eval.py (add `GET /tournament-report`)
- api/replay_loader.py (add a method that reads the eval-report JSON from the configured dir, mirroring `cost_summary()`)
- tests/api/ (a test for the new endpoint: present → 200 + valid body; absent → 404)

**Files NOT in scope:**
- engine/
- agents/
- llm/
- eval/ (consume `TournamentEvalReport`'s JSON shape; do not modify the metric or schema modules)
- frontend/src/store/replayStore.ts (frozen Phase 4 store — do not extend it)
- DESIGN.md
- AGENT_IMPLEMENTATION.md

**Definition of done:**
- [ ] `GET /api/tournament-report` returns the `TournamentEvalReport` JSON for the configured eval dir (200) or 404 when no `tournament-eval-report.json` exists; the loader method mirrors `ReplayLoader.cost_summary()` and reads the same configured directory.
- [ ] `frontend/src/types/api.ts` carries TS types mirroring `TournamentEvalReport` + its four nested metric models (and the `TournamentReport` fields the dashboard reads); `getTournamentReport()` in `api/client.ts` fetches `/tournament-report` and returns the typed shape, raising `ApiError` on failure like the sibling methods.
- [ ] `useTournamentStore` (new) holds the fetched report + load/error state; it does not import or mutate `useReplayStore`.
- [ ] `App.tsx` renders tab navigation; selecting "Tournament Dashboard" mounts `TournamentDashboard`, which renders: the balance summary (crew/impostor/tick-budget from `report` winners), vote-correctness rate, the accusation-calibration curve (per-bin actual-impostor-rate vs confidence, claim and ballot curves shown separately), the alibi-fabrication survival rate, and the cost dashboard (total, mean-per-game, per-`(template, version)` breakdown, per-model). Each metric's `None`/empty states render without crashing (e.g. `vote_correctness_rate === null` shows "n/a", not NaN).
- [ ] The dashboard does NOT pull in PixiJS or a new charting dependency (or, if one is genuinely needed, the choice is justified in `## Decisions`).
- [ ] `npm run build` (tsc + vite build) and any configured `tsc`/lint check pass; `bash scripts/check.sh` passes (backend gates green for the new endpoint).
- [ ] `uv run mypy --strict` on the API surface it touches passes; `uv run ruff check .` passes.

**Implementation hint:**

Backend: `api/routes/eval.py` already exposes `GET /cost-summary` as a thin
adapter over `ReplayLoader`. Add `GET /tournament-report` the same way — a new
`ReplayLoader` method reads `<replay_dir>/tournament-eval-report.json` (the file
`scripts/run_tournament.py` writes), validates it against
`eval.meeting_quality.TournamentEvalReport`, and returns it; missing file → a
404 (`HTTPException`). Serve the model directly as `response_model` rather than
re-modeling a parallel DTO — the structure is deep and the dashboard is
privileged. Generate a sample `tournament-eval-report.json` for local testing
with `uv run python scripts/run_tournament.py --num-games 5 --output-dir /tmp/tdash`
(fake provider, no network).

Frontend: model the tab on the existing single-page layout in `App.tsx`; the
dashboard view is a sibling of the replay-viewer `<main>`. The calibration curve
can be a simple inline SVG or styled divs (per-bin bar whose height is
`actual_impostor_rate`, x = bin midpoint). Mirror `api/client.ts`'s `getJson`
helper for the fetch.

**Public types introduced:**
None.

**Integration risk:**

- **Scope is full-stack.** Unlike 5.8 (which is parallel-safe in `eval/` +
  `tests/`), this task touches `api/` and `frontend/`. It does not touch any
  file 5.8 touches, so the two still fan out in parallel — but this one is the
  larger PR.
- **Privileged exposure is intentional.** The endpoint serves `roles` ground
  truth. That is consistent with the spectator API's privileged model (the
  replay viewer already exposes role), but note it explicitly so a future DTO
  audit does not flag it as an accidental leak.
- **Do not extend the frozen replay store.** Adding fields to `useReplayStore`
  would force edits across every Phase 4 component; the sibling store keeps the
  blast radius to this task.
- **TypeScript/Pydantic drift.** The TS types are hand-mirrored from the
  Pydantic models; keep them faithful (especially nullable fields like
  `vote_correctness_rate: number | null` and the empty-bin
  `actual_impostor_rate: number | null`) or the dashboard silently renders
  `undefined`.

**Ready-to-paste prompt:** `agent_prompts/task-5-7-tournament-dashboard-frontend-page.md`

### Task 5.8 — Prompt regression test suite
**Branch:** `phase-5-prompt-regression-test-suite`
**Depends on:** 5.6 merged
**Section refs:** DESIGN.md §11.3
**Complexity:** Integration

The prompt regression suite — **this task IS the Phase 5 close gate**: it must
demonstrate one full loop, a prompt-template change producing a measurable,
attributable metric delta in the tournament report, deterministically in CI.

The enabling insight: the Phase 5 metrics are pure analyzers over a
`TournamentReport`, which is assembled from replay records — and recorded real
meetings already exist as replay JSONL under `replays/samples/` (the
meeting-bearing seeds carry real transcripts, ballots, and contradictions, with
their prompt-template versions logged in `replays/samples/MANIFEST.md`). So the
regression suite needs NO live model and NO engine re-run: build a
`TournamentReport` from frozen recorded JSONL plus a deterministically-derived
`roles` map, run the four metrics, and compare to a committed baseline. The
`FakeProvider` is NOT usable here — it emits empty/stub outputs, so a fake run
yields trivial metric values; the regression signal must come from recorded
real outputs.

`roles` is the one field not in the JSONL; derive it deterministically from the
seed via `orchestrator.seeder.seed_initial_state(seed, num_players,
num_impostors).players[id].role` — no LLM, no network, fully reproducible.

**Decisions resolved (record any deviation in the PR's `## Decisions` block):**
- **Fixture provenance: a frozen, owned copy under
  `tests/fixtures/prompt_regression/`, NOT the live `replays/samples/`.** The
  live samples are rewritten by `scripts/refresh_samples.sh`; a regression
  baseline must be stable. Copy a small set of meeting-bearing seeds' replay
  JSONL into the fixture dir, tagged by prompt version (from MANIFEST).
- **Report build path: promote a public loader in `eval/balance_eval.py`.**
  Extract the existing per-seed assembly (`_game_report_from_replay` +
  `_game_cost_summary`) into a public `load_tournament_report(replay_dir, *,
  roles_by_seed)` (refactor-only, no behavior change to `run_tournament_eval`,
  which keeps using the same code). The regression module calls it — it does
  NOT duplicate the record→`GameReport` mapping (avoids drift from 5.6).
- **`roles` for fixtures: derived at test time via `seed_initial_state`**, not
  stored in the fixture (decoupled, no duplicated ground truth).
- **Regression signal: exact-match on frozen fixtures.** Because the fixtures
  are recorded and the metrics are deterministic, the baseline metric scalars
  are exact; any drift is a real regression in a metric, the loader, or the
  schema. The `> X%` tolerance is the documented policy for the *manual*
  real-provider re-record comparison (via `refresh_samples.sh`), which is out of
  CI; state the chosen X and that CI uses exact match.

**Files in scope:**
- eval/prompt_regression.py
- eval/balance_eval.py (promote `load_tournament_report` from the existing private assembly; refactor-only)
- tests/fixtures/prompt_regression/ (frozen recorded replay JSONL tagged by prompt version + a committed baseline of expected metric scalars)
- tests/eval/test_prompt_regression.py

**Files NOT in scope:**
- engine/
- agents/tactical/
- llm/ provider behavior
- api/
- frontend/
- eval/report_schema.py, eval/vote_correctness.py, eval/accusation_calibration.py, eval/alibi_fabrication.py, eval/cost_dashboard.py, eval/meeting_quality.py (consume their public APIs; do not modify)
- scripts/refresh_samples.sh (the real-provider re-record path; referenced, not modified)
- DESIGN.md
- AGENT_IMPLEMENTATION.md

**Definition of done:**
- [ ] `eval/prompt_regression.py` builds a `TournamentReport` from a fixture directory of recorded replay JSONL (via the promoted `eval.balance_eval.load_tournament_report`, with `roles` derived from `seed_initial_state`), runs `eval.meeting_quality.build_tournament_eval_report`, and produces a metric summary tagged by the prompt-template versions in play (from `GameReport.prompt_versions`). No network, no live/fake model call to generate outputs.
- [ ] A committed baseline (e.g. `tests/fixtures/prompt_regression/baseline.json`) records the expected metric scalars per prompt version. `tests/eval/test_prompt_regression.py` asserts the computed summary matches the baseline EXACTLY for the frozen fixtures; a mismatch fails the test (a real metric/loader/schema regression). The `> X%` tolerance is documented as the policy for the manual real-provider re-record path; CI uses exact match.
- [ ] **Close-gate demonstration:** the suite includes TWO prompt-version fixture sets — a baseline version `v_a` and a variant `v_b` whose recorded meeting outputs differ such that at least one metric (e.g. alibi-fabrication survival rate or vote-correctness rate) measurably changes. A test asserts the regression suite DETECTS the delta and ATTRIBUTES it to the prompt-version change (via `prompt_versions` provenance and/or the cost-per-version breakdown). This is the prompt-change → metric-diff loop, run deterministically without a model.
- [ ] Results are tagged by prompt version (the summary keys by `(template_name, version)` or the per-version provenance), so a delta is traceable to which template changed.
- [ ] Tests use recorded fixtures only and make no network calls; `AILIBI_LLM_PROVIDER` is irrelevant (no provider is invoked).
- [ ] `load_tournament_report` is a behavior-preserving extraction: `run_tournament_eval` and the existing `test_balance_eval.py` / `test_tournament_report.py` still pass unchanged.
- [ ] `uv run mypy --strict eval` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` and `uv run python scripts/validate_task_docs.py` pass.
- [ ] `uv run pytest` passes; `bash scripts/check.sh` passes locally.

**Implementation hint:**

For each fixture seed, derive roles with
`seed_initial_state(seed, num_players=…, num_impostors=…).players` (the same
deterministic setup the loader's `_seeded_roles` uses), call
`load_tournament_report(fixture_dir, roles_by_seed=…)` → `TournamentReport`,
then `build_tournament_eval_report(report)` → pull scalars
(`vote_correctness.vote_correctness_rate`,
`alibi_fabrication` survival rate, `accusation_calibration.*_ece`,
`cost_dashboard.total_cost_usd` + `per_prompt_version`). Pick a couple of
meeting-bearing sample seeds (e.g. 22/24/26 per MANIFEST) and copy their
`replay-seed-N.jsonl` into `tests/fixtures/prompt_regression/v_a/`. For `v_b`,
either copy a different recorded run of the same seeds at a different prompt
version, or hand-author a minimal variant transcript that moves one metric
(e.g. add an `alibi_conflict` contradiction so an impostor alibi flips from
survived to caught); commit it under `…/v_b/` tagged with a distinct
`prompt_versions`. Keep fixtures small — a few seeds is enough to pin the loop.

To regenerate fixtures from a real provider (manual, out of CI): change the
prompt template, run `scripts/refresh_samples.sh --meetings`, copy the new
samples into the fixture dir, and update `baseline.json`. Document this
provenance procedure in the module docstring.

**Public types introduced:**
- eval.prompt_regression.PromptRegressionSummary
- eval.prompt_regression.run_prompt_regression
- eval.balance_eval.load_tournament_report

**Integration risk:**

This task is the Phase 5 acceptance gate; getting the loop genuinely
demonstrated (not stubbed) is the point.

- **Determinism is everything.** Recorded fixtures + pure analyzers + derived
  roles = byte-stable metric values. Never invoke a real OR fake model to
  generate outputs in the suite — a fake run produces empty meetings and a
  meaningless signal. If a metric value is not reproducible from the frozen
  fixture, the fixture or the loader is wrong.
- **The `load_tournament_report` extraction must not change `run_tournament_eval`
  behavior.** It is a pure refactor of code 5.6 already shipped; the existing
  loader/integration tests are the guardrail.
- **The close-gate demo must be a REAL delta, not a tautology.** `v_b` must
  differ from `v_a` in recorded outputs such that a metric genuinely moves and
  the suite reports it; a test that asserts `report_a != report_b` by comparing
  unrelated fields does not demonstrate the loop. Tie the asserted delta to a
  specific metric and to the changed prompt version.
- **Fixtures are frozen.** Do not point the suite at `replays/samples/` (those
  get rewritten); copy what you need into `tests/fixtures/prompt_regression/`.

**Ready-to-paste prompt:** `agent_prompts/task-5-8-prompt-regression-test-suite.md`

### Task 5.9 — Performance pass
**Branch:** `phase-5-performance-pass`
**Depends on:** 5.7 merged, 5.8 merged
**Section refs:** DESIGN.md §9
**Complexity:** Medium

Hit the DESIGN.md §9 Phase 5 target: ≥ 1 headless game per minute on a laptop.
Measure the current rate, profile to find the real bottlenecks, apply targeted
fixes to the hot paths, and prove no behavior change. This is the final Phase 5
task and pure polish — the dashboard (5.7) and regression suite (5.8) already
ship at the current rate.

**Benchmark on the FAKE provider.** The rate must be measured deterministically
and network-free, so the benchmark runs headless games with
`AILIBI_LLM_PROVIDER=fake` (instant LLM stubs). That means the measured cost is
ENGINE + serialization throughput per tick — NOT LLM latency. The confirmed hot
paths (cited, not guessed):

- **Per-tick full-state hash** — `orchestrator.replay._state_hash`
  (`orchestrator/replay.py:546`) sha256s the entire serialized `WorldState`
  every tick.
- **Per-tick replay JSONL write** — `ReplayLog.record_tick`
  (`orchestrator/replay.py:244`) serializes via `_stable_json`
  (`json.dumps(sort_keys=True…)`, `orchestrator/replay.py:585`) and writes one
  line per tick.
- **Per-agent-per-tick observation packet construction** —
  `ObservationService.build_packet` (`observation/service.py:36`).

LLM-call concurrency (`orchestrator/`) is a REAL-run lever only — it does not
show up in a fake-provider benchmark (the fake is instant) — so it is secondary
here and any change to it must not alter determinism or the recorded replay.

**Files in scope:**
- engine/ (hot paths only; no rule/behavior change)
- orchestrator/ (per-tick serialization / hash / write-cadence hot paths; concurrency tuning is secondary and determinism-preserving)
- observation/ (packet-construction hot path, if it appears in the profile)
- eval/benchmark.py (a small reusable throughput harness, if one is wanted; else inline in the test)
- tests/eval/test_performance.py (records the benchmark; skipped by default — see DoD)
- scripts/run_tournament.py (only if perf surfaces a tuning knob worth a CLI flag)

**Files NOT in scope:**
- agents/ behavior (FSM or strategic prompt changes)
- llm/ provider behavior
- meetings/ behavior (cap raises etc. are Phase 3 territory)
- api/, frontend/ (the spectator UI is read-only; perf is engine + orchestrator)
- eval/ metric modules, report_schema.py, meeting_quality.py (perf must not change metric values)
- DESIGN.md
- AGENT_IMPLEMENTATION.md

**Definition of done:**
- [ ] BEFORE rate recorded (games/min on the target laptop, fake provider) in the PR's `## Decisions`, with the exact command and hardware noted.
- [ ] Bottlenecks identified via profiling (`cProfile` or `py-spy`); the profile output (top cumulative-time frames) captured in `## Decisions`. Only paths that actually appear in the profile are optimized — no speculative changes.
- [ ] Targeted fixes applied with NO behavior change. The proof is byte-identity: for a fixed seed, the AFTER `replay-seed-{seed}.jsonl` is byte-identical to BEFORE, and `eval/determinism_test.py` (the three scripted games) still passes byte-identically. Any change to `_state_hash` / `_stable_json` serialization is forbidden unless provably output-identical, since the state hash IS the determinism contract.
- [ ] AFTER rate recorded; meets or exceeds ≥ 1 game/min on the target laptop (documented alongside BEFORE).
- [ ] A benchmark harness is committed that times N headless fake-provider games and reports games/min (e.g. via `time.perf_counter` over `HeadlessGame`/`run_balance_eval`; no `pytest-benchmark` dependency — it is not in `pyproject.toml`). It lives in `tests/eval/test_performance.py` and is **skipped by default** (behind an env-gate or marker) so it never flakes CI on hardware variance; running it is opt-in. Decision recorded: record-only vs a generous non-flaky floor — bias toward record-only (or a floor far below the target, e.g. a smoke assertion that the rate is finite/positive), with the real ≥ 1 game/min target verified manually and documented, never asserted as a tight CI threshold.
- [ ] No regression in any existing test, including `eval/determinism_test.py` and `eval/leak_test.py` (byte-identity + leak firewall both still hold).
- [ ] `uv run mypy .` passes; `uv run ruff check .` and `uv run ruff format --check .` pass; `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` and `uv run python scripts/validate_task_docs.py` pass.
- [ ] `uv run pytest` passes; `bash scripts/check.sh` passes locally.

**Implementation hint:**

First action is to record a baseline — do NOT optimize before measuring. Time a
small batch of fake-provider games (e.g. `AILIBI_LLM_PROVIDER=fake` over a seed
range that reaches meetings, so the meeting path is exercised) with
`time.perf_counter`, and profile the same batch with `cProfile`
(`python -m cProfile -s cumtime`). Then target only the frames the profile
surfaces — the three cited hot paths are the likely candidates, but let the
profile decide.

When optimizing the per-tick hash/write: the determinism contract is that the
recorded replay is byte-identical from a seed. So you may make `_state_hash` /
`_stable_json` faster ONLY if the bytes are unchanged (e.g. caching, avoiding
redundant re-serialization), never by changing the serialization format. Re-run
a tournament for a fixed seed before and after and `diff` the replay files —
they must be identical. `eval/determinism_test.py` is the automated guard.

**Decisions to resolve and record in the PR's `## Decisions` block:**
- CI gating of the benchmark: record-only / skip-by-default (bias) vs a hard threshold (rejected — hardware variance makes a tight `≥ 1 game/min` CI assertion flaky).
- Benchmark provider: fake (bias — deterministic, network-free, measures engine throughput) vs real (network-bound, non-reproducible, costs money — rejected for the gate).
- Harness home: `eval/benchmark.py` (reusable) vs inline in `tests/eval/test_performance.py`.

**Public types introduced:**
None.

**Integration risk:**

- **Determinism is the load-bearing gate.** Any engine/orchestrator hot-path
  change risks breaking byte-identical replays. The state hash is the contract;
  `eval/determinism_test.py` plus a before/after replay `diff` for a fixed seed
  are the proof. A perf win that changes a single recorded byte is a regression,
  not a win.
- **No behavior change.** This task does NOT touch agent reasoning, prompt
  content, FSM rules, LLM behavior, or any metric value. Perf-only.
- **Single-laptop variance.** Pin BEFORE and AFTER to the same hardware and
  document it; do not compare rates across machines. This is exactly why the
  committed benchmark is record-only and not a CI threshold.
- **Fake-provider benchmark scope.** The benchmark measures engine +
  serialization throughput, not LLM latency, so it will not reflect
  LLM-concurrency changes; keep the optimization focus on the per-tick hot
  paths the profile surfaces.

**Ready-to-paste prompt:** `agent_prompts/task-5-9-performance-pass.md`

## Merge Criteria
- **Preludes landed:** Tasks 4.16 (ReplayLog fail-loud) and 4.17 (refresh-samples workflow + MANIFEST) merged before any Phase 5 task.
- **Schema-driven reporting:** running `python scripts/run_tournament.py --N=200` produces a JSON report with all Phase 5 metrics (5.2–5.5) validated against the 5.1 schema.
- **Dashboard renders:** the frontend tournament dashboard renders the report end-to-end.
- **Mid-phase metric audit passes** before 5.7/5.8 fan-out.
- **Close gate:** the prompt regression suite (5.8) demonstrates one full loop — a prompt-template change produces a measurable metric delta in the tournament report. This is the Phase 5 acceptance criterion; no manual UX session.
- **Performance target met:** ≥ 1 headless game/min on the target laptop (Task 5.9).
- **Metric task parallelism preserved:** 5.2–5.5 do not require simultaneous edits to shared tournament files; 5.7/5.8 do not require simultaneous edits to shared frontend files.
- **All Phase 4 static + behavioral gates still green:** `bash scripts/check.sh`, determinism tests, leak tests, frontend `tsc:check` + `vite build`.
