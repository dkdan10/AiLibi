# Agent Prompt — 3.18 Statement/Vote max_tokens raise + impostor `subject: "self"` normalization

You are working on AiLibi. Before starting, read AGENTS.md, DESIGN.md, and the task section in tasks/phase-3.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth and the task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 3.18 — Statement/Vote max_tokens raise + impostor `subject: "self"` normalization, anchored to DESIGN.md §5.3, DESIGN.md §7, DESIGN.md §10.4. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-3.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-3-statement-vote-caps-and-impostor-self`
**Depends on:** 3.17 merged
**Section refs:** DESIGN.md §5.3, DESIGN.md §7, DESIGN.md §10.4
**Complexity:** Small

Close the three findings surfaced by the seed-23 deep debug at
`audits/audit-2026-05-25-2320-seed-23-deep-debug.md`. The investigation
walked the full meeting flow against the live Anthropic provider for
seed 22 (the actual first-meeting seed; prior eval reports
miscounted partial replay files and attributed the crash to seed 23 —
see §3 of the debug report) and surfaced three distinct issues in one
$0.12 pass, breaking the prior one-defect-per-eval pattern.

**Finding 1 (Critical, production crash path): `Statement` truncation
at `max_tokens=512`.** All 3 accusation-round calls in the deep debug
saturated at exactly 512 output tokens and raised
`JSONDecodeError: Unterminated string`. Task 3.17 explicitly
excluded `Statement` and `VoteBallot` from its max_tokens raise on the
(now-empirically-falsified) reasoning that "statement and vote outputs
are inherently smaller." The 3/3 saturation rate is deterministic, not
a margin issue. The next eval will crash here unless this task lands.

**Finding 2 (Medium, margin risk): `VoteBallot` at 70% of
`max_tokens=384`.** The deep debug's top vote response was 268/384
output tokens. Not yet failing but tight; the same defense-in-depth
reasoning applies.

**Finding 3 (Medium, transcript correctness): Impostor template emits
`subject: "self"` on nested `AlibiClaim`.** The crewmate template
injects the agent's own `agent_id` into prompt context so the model
emits `subject: "p-3"` (or whichever id) on self-referencing alibi
claims. The impostor template at
`agents/strategic/prompts/impostor_report.j2` does not — it has the
literal placeholder `"subject": "self"` embedded. The live model
follows the placeholder faithfully and emits `"self"`, which survives
into the meeting transcript. Schemas validate cleanly because
`subject` is just a `PlayerId`-shaped string, but downstream
contradiction detection (Task 3.11) cannot match `"self"` against any
real player and will silently miss impostor self-incriminating alibis.

This task closes all three findings in one bundled PR. Same code path
(meeting LLM calls), same defect family (live-provider quirks the
fake provider doesn't reproduce).

**Out of scope** (explicit decisions deferred):

- The seven Concern-level findings in §9 of the debug report
  (impostor placeholder `agent_id`/`tick`, accusation template's
  collapsed-Markdown transcript rendering, fence-mode split between
  reports and statements, hallucinated `speaker: "p-0"` placeholder,
  FakeProvider's verbose-output gap, `check.sh`-with-anthropic-exported
  failure mode, no-per-game-outcome-in-replay) are NOT in scope. None
  block the eval. Recommend a separate hygiene task (Task 3.19 or
  post-Phase-3) to bundle them.
- Migration to Anthropic's tool-use forced-JSON mechanism (would
  structurally eliminate the entire truncation class). Still deferred
  per Task 3.17's reasoning — keep ratcheting cap raises until proven
  insufficient.

**Files in scope:**
- meetings/manager.py
- agents/strategic/prompts/impostor_report.j2
- tests/llm/test_real_provider.py

**Files NOT in scope:**
- meetings/schemas.py
- meetings/transcript.py
- meetings/voting.py
- meetings/__init__.py
- agents/strategic/prompts/crewmate_report.j2
- agents/strategic/prompts/accusation_round.j2
- agents/strategic/prompts/vote_ballot.j2
- agents/strategic/prompts/loader.py
- agents/strategic/prompts/__init__.py
- agents/strategic/reasoner.py
- agents/strategic/output_schemas.py
- agents/
- llm/
- engine/
- observation/
- orchestrator/
- api/
- frontend/
- eval/
- scripts/
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
- [ ] **`DEFAULT_STATEMENT_MAX_TOKENS` raised from 512 to 2048** at `meetings/manager.py:80`. Matches the report cap from Task 3.17. Empirical justification: deep debug showed 3/3 statements saturated at 512; doubling to 2048 doubles the headroom. Cost impact: 8 statement calls × 2048 × $15/Mtok = $0.24 per meeting worst case, under Task 3.16's $1.00/game budget cap.
- [ ] **`DEFAULT_VOTE_MAX_TOKENS` raised from 384 to 1024** at `meetings/manager.py:82`. Empirical justification: deep debug showed top vote response at 268/384 = 70% of cap; raising to 1024 quadruples the margin. Cost impact: 5 vote calls × 1024 × $15/Mtok = $0.077 per meeting worst case.
- [ ] **Impostor template `subject: "self"` replaced with `agent_id` injection.** In `agents/strategic/prompts/impostor_report.j2`, every occurrence of `"subject": "self"` in alibi-claim examples / schema descriptions is replaced with `"subject": "{{ agent_id }}"` (or the canonical Jinja-variable expression matching the crewmate template's pattern). The crewmate template at `agents/strategic/prompts/crewmate_report.j2` is the reference — the impostor template should be symmetric with it for self-referencing alibi claims. The impostor's adversarial framing (lying about location, claiming false alibis, etc.) is unchanged; only the literal `"self"` placeholder is fixed so the model emits a real player_id.
- [ ] **New `@real_provider` regression test for `Statement` truncation.** Add to `tests/llm/test_real_provider.py::TestAnthropicTruncationFailureMode` (or sibling class), analogous to the existing `test_truncated_report_fails_with_validation_error_not_backtick`. The test:
  - Constructs `AnthropicClient` directly.
  - Calls `await client.complete(prompt=<short prompt asking for a Statement>, schema=Statement, max_tokens=50, temperature=0.0)` to force truncation.
  - Asserts the call raises `pydantic_core.ValidationError` (truncated JSON → Pydantic missing-fields error).
  - Asserts the error message does NOT contain `"line 1 column 1"` (the pre-3.17 leading-backtick failure mode).
  - Skipped in CI by default via `@real_provider`. Cost: ~$0.001 per invocation.
- [ ] **New `@real_provider` regression test for `VoteBallot` truncation.** Same shape as the Statement test, with `schema=VoteBallot` and a prompt asking for a vote.
- [ ] **Post-merge local verification.** With `AILIBI_LLM_PROVIDER=anthropic` and `ANTHROPIC_API_KEY` set:
  - Run `AILIBI_RUN_REAL_PROVIDER_TESTS=1 uv run pytest tests/llm/test_real_provider.py -v` — all existing `@real_provider` tests pass, the two new truncation tests pass. Cost: ~$0.06 total.
  - Render the impostor template with a fixture `agent_id` and confirm the rendered prompt contains `"subject": "p-X"` (the agent_id), NOT `"subject": "self"`. Can be a one-liner: `python -c "from agents.strategic.prompts.loader import impostor_report_prompt; print(impostor_report_prompt(agent_id='p-3', ...))"` then grep for `"self"` in the output.
  - Re-run the eval prompt's direct sanity call to confirm transport is still healthy.
  - Paste verbatim outputs (test results, impostor template grep result, sanity call output) into `## Decisions`. API key prefix only (8 chars).
- [ ] **Document the seed-22-not-seed-23 finding** in the PR's `## Decisions` block (one paragraph, referencing `audits/audit-2026-05-25-2320-seed-23-deep-debug.md` §3). The next eval prompt and audit reports should reference seed 22 as the first meeting seed; no source change required (the eval prompt already uses adaptive "first 5 games with meetings" sampling).
- [ ] No imports from `engine/` under `agents/`, `llm/`, or `meetings/` (firewall preserved). `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes (with the two new `@real_provider` tests skipped by default in CI).
- [ ] `uv run mypy .` passes.
- [ ] `uv run mypy --strict agents observation orchestrator engine llm meetings` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `bash scripts/check.sh` passes locally.

## Dependency contract check
Run these before editing. If any fail, stop and report — your dependencies are not where this task expects them.

- `uv run python -c "import orchestrator.game"`
- `uv run python -c "import orchestrator.replay"`
- `uv run python -c "import agents.strategic.reasoner"`
- `uv run python -c "import llm.budgeted_client"`
- `uv run python -c "import meetings.manager"`

## Pre-flight checklist
- Read AGENTS.md, DESIGN.md, and the task section before editing.
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
Open a PR from branch `phase-3-statement-vote-caps-and-impostor-self` with a title like `task 3.18: statement/vote max_tokens raise + impostor `subject: "self"` normalization`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing DESIGN.md §5.3, DESIGN.md §7, DESIGN.md §10.4), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
