# Agent Prompt — 3.16 Prompt-template ↔ schema alignment + per-game budget cap raise

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-3.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 3.16 — Prompt-template ↔ schema alignment + per-game budget cap raise, anchored to DESIGN.md §5.3, DESIGN.md §5.5, DESIGN.md §7. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-3.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-3-prompt-schema-alignment`
**Depends on:** 3.15 merged
**Section refs:** DESIGN.md §5.3, DESIGN.md §5.5, DESIGN.md §7
**Complexity:** Medium

Close the defect surfaced by the third Pre-Phase-4 real-provider eval at
`audits/audit-2026-05-25-2038-pre-phase-4-real-provider-eval.md`, which
exited with verdict **Phase 3 blocked — tournament crashed** when the
first live meeting fired (seed 23 of 50). Confirmed live spend on the
crashed run: ~$0.0001 sanity call + estimated ~$0.10–$0.30 of unrecorded
in-flight crashed-meeting calls. The eval pre-flight + fence-strip
defense both worked correctly; the new defect is at a different layer.

**The defect — prompt ↔ schema drift.** The Pydantic schemas in
`meetings/schemas.py` use the field names `subject`, `room`,
`from_tick`, `to_tick`, `against`, `body_of` with `extra='forbid'`. The
production prompt templates in `agents/strategic/prompts/*.j2` describe
the schema using **legacy field names** (`player_id`, `location`,
`tick_start`, `tick_end`, `description`, `target_id`). The live
Anthropic Sonnet 4.6 model follows the prompt's described field names
faithfully — the output is internally consistent but uses the wrong
keys. `schema.model_validate_json(...)` then rejects with 38 validation
errors per `ReportDocument`.

This drift exists because:
- The `FakeProvider` in `llm/fake_provider.py` constructs schema
  objects directly from internal fixtures rather than round-tripping
  JSON through the prompt template. So the templates' field-name
  instructions are never exercised by the fake-provider tests.
- Static audits compared code-to-code, not prompt-template-to-schema.
  The drift was invisible to every audit stage.
- Task 3.15's `@real_provider` schema test (added to catch the
  markdown-fence class of defect) hand-wrote its own prompt asking for
  specific field names — the model followed the test's explicit
  instructions, not the production template's instructions, so the
  test gave a false-pass on prompt-template correctness.

This task closes the drift across all four templates AND preempts the
next-most-likely failure mode (per-game budget cap exceeded
mid-meeting) by raising the cap from $0.30 to $1.00 in the eval entry
points.

**The defect is "all-four templates" not just `ReportDocument`.** The
eval crashed at the report-collection phase, but the same drift class
applies to `accusation_round.j2` ↔ `Statement` (the audit's stack
trace already showed `claims.0.alibi.tick_start` and
`claims.1.accusation.target_id` as drift — those are `Claim` subclass
fields embedded in `Statement`) and almost certainly to
`vote_ballot.j2` ↔ `VoteBallot`. Fixing only the report templates
would land the next eval at the same crash on the accusation phase.

**Budget cap raise rationale.** The current `GameBudget()` default cap
of $0.30 in `llm/budget.py` was set when the project assumed
FakeProvider (zero cost). Live Anthropic Sonnet 4.6 pricing at
$3.00/Mtok input + $15.00/Mtok output yields per-call cost
~$0.01–$0.015. A 5-agent meeting with 1 report + 2 accusation rounds ×
1 statement + 1 vote = ~20 calls = $0.20–$0.30 per meeting, sitting at
the budget cap. `BudgetExceededError` propagating mid-meeting would
crash the tournament exactly the way the schema-drift crash does now.
The Phase 3 merge criterion is **mean cost ≤ $0.30/game** across 50
games, NOT per-game cap ≤ $0.30; with ~7–10% meeting trigger rate,
non-meeting games cost $0 and the mean stays well under the criterion
even if individual meeting games cost $0.50–$1.00. The cap is a safety
stop; the merge gate is post-hoc mean.

**Files in scope:**
- agents/strategic/prompts/crewmate_report.j2
- agents/strategic/prompts/impostor_report.j2
- agents/strategic/prompts/accusation_round.j2
- agents/strategic/prompts/vote_ballot.j2
- tests/llm/test_real_provider.py
- scripts/run_game.py
- scripts/run_tournament.py
- eval/balance_eval.py

**Files NOT in scope:**
- meetings/schemas.py
- meetings/manager.py
- meetings/transcript.py
- meetings/voting.py
- llm/budget.py
- llm/provider.py
- llm/fake_provider.py
- llm/client.py
- llm/budgeted_client.py
- llm/cache.py
- llm/README.md
- llm/__init__.py
- agents/strategic/reasoner.py
- agents/strategic/prompts/loader.py
- agents/strategic/prompts/__init__.py
- agents/strategic/output_schemas.py
- agents/
- engine/
- observation/
- orchestrator/
- api/
- frontend/
- AGENTS.md
- AGENT_IMPLEMENTATION.md
- DESIGN.md
- pyproject.toml
- uv.lock
- tasks/
- agent_prompts/
- audits/
- README.md
- open_issues.md
- tests/agents/
- tests/engine/
- tests/meetings/
- tests/observation/
- tests/orchestrator/
- tests/eval/
- tests/llm/test_client.py
- tests/llm/test_budget.py
- tests/llm/test_budgeted_client.py
- tests/test_firewall.py

**Definition of done:**
- [ ] **`crewmate_report.j2` aligned with `ReportDocument`.** Read `meetings/schemas.py` to enumerate every field on `ReportDocument`, `ObservationClaim` (and its discriminated-union subclasses `SawPlayerClaim`, `FoundBodyClaim`, etc.), and `Claim` (and its subclasses `AlibiClaim`, `AccusationClaim`, etc.). Update the template's prose, examples, and JSON skeletons to use the current field names (`subject`, `room`, `from_tick`, `to_tick`, `against`, `body_of`, ...) rather than the legacy names (`player_id`, `location`, `tick_start`, `tick_end`, `description`, `target_id`). Preserve the template's version-marker substring (the loader's smoke tests assert it).
- [ ] **`impostor_report.j2` aligned with `ReportDocument`.** Same schema as the crewmate report; same alignment work. The impostor template's adversarial prose stays unchanged; only field-name references are updated.
- [ ] **`accusation_round.j2` aligned with `Statement`.** Read the `Statement` schema and its embedded `Claim` discriminated-union subclasses. Update template references to match. The audit's stack trace already cited drift in `claims.0.alibi.tick_start` and `claims.1.accusation.target_id`, so this template is confirmed-affected.
- [ ] **`vote_ballot.j2` aligned with `VoteBallot`.** Read the `VoteBallot` schema. Update field-name references. The schema is smaller than the report/statement schemas, so this is the lightest of the four.
- [ ] **Real-provider round-trip test per template (4 tests, all `@real_provider`-marked).** `tests/llm/test_real_provider.py` gains four new tests, one per template, each:
  - Loads the **actual production template** via the Jinja loader (`agents.strategic.prompts.loader`) — NOT a hand-written prompt.
  - Renders the template against a minimal but realistic fixture context (a rendered-memory string + meeting context appropriate to the template's call kind).
  - Calls `AnthropicClient(api_key=os.environ["ANTHROPIC_API_KEY"]).complete(prompt=..., schema=<corresponding schema>, max_tokens=1024, temperature=0.0)`.
  - Asserts the call returns without raising (i.e. the production template + fence-strip + Pydantic validation all succeed end-to-end).
  - Asserts `response.cost_usd > 0`, `response.text` parses cleanly as the corresponding schema (`ReportDocument` / `Statement` / `VoteBallot`).
  - Skipped in CI by default via the existing `@real_provider` marker keyed on `AILIBI_RUN_REAL_PROVIDER_TESTS=1`.
  - Per-test cost ~$0.005–$0.01; total opt-in cost ~$0.04 for the four tests.
- [ ] **Per-game budget cap raised from $0.30 to $1.00 in eval entry points.** In `scripts/run_game.py`, `scripts/run_tournament.py`, and `eval/balance_eval.py`, every `GameBudget()` constructor invocation that currently uses the $0.30 default is changed to `GameBudget(cost_usd_cap=1.00)`. The constant `1.00` is acceptable — a CLI flag is not required for this task and would introduce surface that isn't yet needed. Document the change in `## Decisions` with the rationale: the merge criterion is mean ≤ $0.30/game across 50 games; the per-game cap is a safety stop, not the gate. Do NOT modify the `GameBudget` default in `llm/budget.py` — the default stays $0.30 so that direct unit-test consumers of `GameBudget` keep the conservative default.
- [ ] **No template re-emits legacy field names.** Run `git grep -nE "player_id|location|tick_start|tick_end|target_id" agents/strategic/prompts/` — must return only references to fields that legitimately remain in the schema (if any). Document any retained legacy-style references in `## Decisions` with the schema-field they correspond to.
- [ ] **Post-merge local verification.** Before opening the PR, with `AILIBI_LLM_PROVIDER=anthropic` and `ANTHROPIC_API_KEY` set:
  - Run `AILIBI_RUN_REAL_PROVIDER_TESTS=1 uv run pytest tests/llm/test_real_provider.py -v` — all four new template round-trip tests must pass against the live provider.
  - Re-run the eval prompt's direct sanity call — must still pass (this confirms the budget-cap raise didn't break the simple-call path).
  - Paste verbatim outputs (model + cost_usd + response text for each test, API key 8-char prefix only) into `## Decisions`.
- [ ] No imports from `engine/` under `agents/`, `llm/`, or `meetings/` (firewall preserved). `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes (with the four new `@real_provider` tests skipped by default in CI).
- [ ] `uv run mypy .` passes.
- [ ] `uv run mypy --strict agents observation orchestrator engine llm meetings` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

Step 1 — read the schemas first. Open `meetings/schemas.py` and enumerate every model relevant to the four templates. For `ReportDocument`, the relevant types include `ObservationClaim` (likely a discriminated union — list its variants) and `Claim` (also likely a discriminated union). Build a small mapping table mentally before editing any template:

```
ReportDocument fields:        agent_id, tick, observations, claims, ...
ObservationClaim variants:    SawPlayerClaim { subject, room, ... },
                              FoundBodyClaim { body_of, room, ... },
                              ...
Claim variants:               AlibiClaim    { subject, room, from_tick, to_tick, ... },
                              AccusationClaim { against, justification, ... },
                              ...
```

Drift mapping (from the audit's stack trace):
- `player_id` → `subject` (in `SawPlayerClaim`) OR `body_of` (in `FoundBodyClaim`)
- `location` → `room`
- `tick_start` → `from_tick`
- `tick_end` → `to_tick`
- `description` → may have been removed entirely; check the schema
- `target_id` → `against`

The mapping is non-trivial because `player_id` maps to different fields depending on the discriminated-union variant. Read the schema; do not guess.

Step 2 — update each template with corrected field names in prose, JSON examples, and schema-shape descriptions. Preserve:
- The template's version-marker substring (the Jinja-loader smoke tests assert it).
- The template's role-appropriate prose (impostor adversarial framing, crewmate truthful framing, etc.).
- The template's Jinja variable references (`{{ rendered_memory }}`, `{{ meeting_trigger }}`, etc.).

Update:
- Every field-name mention in instructional prose.
- Every JSON example showing the shape of the expected output.
- Any inline schema description.

Step 3 — write the real-provider tests. Model on the existing `TestAnthropicSchemaRoundTrip` from Task 3.15, but use the production template loader rather than a hand-written prompt. Suggested shape:

```python
# tests/llm/test_real_provider.py — illustrative
import os
import pytest
from agents.strategic.prompts.loader import (
    crewmate_report_prompt,
    impostor_report_prompt,
    accusation_round_prompt,
    vote_ballot_prompt,
)
from llm.provider import AnthropicClient
from meetings.schemas import ReportDocument, Statement, VoteBallot
from tests.llm.test_client import real_provider


_MINIMAL_RENDERED_MEMORY = """## Your role: CREWMATE
## Tasks completed (global): 0 / 12

## Recent observations (most salient first):
- [tick 5] You saw p2 in MedBay.

## Your current beliefs:
- p2: trust 0.50 (default)
"""


class TestProductionTemplateSchemaRoundTrips:
    @real_provider
    @pytest.mark.asyncio
    async def test_crewmate_report_template_produces_valid_report_document(
        self,
    ) -> None:
        api_key = os.environ["ANTHROPIC_API_KEY"]
        client = AnthropicClient(api_key=api_key)
        prompt = crewmate_report_prompt(
            agent_id="p-1",
            tick=10,
            rendered_memory=_MINIMAL_RENDERED_MEMORY,
            meeting_trigger="body_reported",
            # ... whatever other kwargs the template expects
        )
        response = await client.complete(
            prompt=prompt,
            schema=ReportDocument,
            max_tokens=1024,
            temperature=0.0,
        )
        assert response.cost_usd > 0.0
        doc = ReportDocument.model_validate_json(response.text)
        assert doc.agent_id == "p-1"

    # ... three more tests, one per template
```

The exact kwargs each template expects depend on how Task 3.4–3.7 wrote them. Read each template's `{{ }}` references before constructing the fixture.

Step 4 — raise the budget cap. The change at each call site is mechanical:

```python
# scripts/run_game.py — before
runner = build_default_meeting_runner(budget=GameBudget())

# After
runner = build_default_meeting_runner(budget=GameBudget(cost_usd_cap=1.00))
```

Apply to all three call sites in `scripts/run_game.py`, `scripts/run_tournament.py`, and `eval/balance_eval.py`. Do NOT modify `llm/budget.py`'s default — unit tests that construct `GameBudget()` directly should keep the conservative default.

## Dependency contract check
Run these before editing. If any fail, stop and report — your dependencies are not where this task expects them.

- `uv run python -c "import orchestrator.game"`
- `uv run python -c "import orchestrator.replay"`
- `uv run python -c "import agents.strategic.reasoner"`
- `uv run python -c "import llm.budgeted_client"`
- `uv run python -c "import meetings.manager"`

## Pre-flight checklist
- Read AGENTS.md, the architecture routing it names, and the task section before editing.
- Inspect the current implementation before editing.
- Identify the existing local patterns for the files in scope and follow them.

## Constraints and non-goals
Do not modify DESIGN.md.
Do not modify AGENT_IMPLEMENTATION.md.
Do not modify tasks/phase-*.md unless this task explicitly lists those files in scope.
Do not implement work outside this task.
Do not add LLM calls inside agents/tactical/.
Do not import engine/ from agents/.
If the task mentions engine-free boundary schemas, keep agents/ free of engine imports and put engine translation only in orchestrator-owned code.

## Verification checklist
- Run every command listed in the Definition of done.
- Run `git diff --name-only` and confirm the diff stays within scope.
- If any Definition of done item is unchecked, report it explicitly in the PR description instead of declaring the task complete.

## Decisions vs questions
- If something is **ambiguous and blocking** (you cannot make a reasonable choice without further information): stop, open a draft PR, add a `## Questions` section, request review.
- If something is **ambiguous but resolvable by judgment** (a default value, a tie-break, a naming choice): document the choice in a `## Decisions` section in the PR description and proceed.

## Output expectation
Open a PR from branch `phase-3-prompt-schema-alignment` with a title like `task 3.16: prompt-template ↔ schema alignment + per-game budget cap raise`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing DESIGN.md §5.3, DESIGN.md §5.5, DESIGN.md §7), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
