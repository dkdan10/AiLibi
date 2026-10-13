# Pre-Phase-4 Checkpoint Audit — Prompt

You are auditing the AiLibi repository at its current `HEAD` of `main`,
at the end of Phase 3 (sub-phase C: Tasks 3.9, 3.10, 3.11, 3.12). Phase
3's merge criteria split between a static / fake-provider dimension
(this audit) and a real-provider dimension (a separate eval prompt
runs the 50-game live tournament). The next phase (Phase 4) is
spectator UI / FastAPI / WebSocket / React work; it builds on top of
the Phase 3 substrate but does not extend the LLM call surface. A
defect in the closing-Phase-3 substrate compounds across the entire
Phase 4 effort.

You will produce **one audit report** in `audits/` following the
format, rigor, and section structure of the most recent prior audit
(`audits/audit-2026-05-16-2239-claude.md`). That file is the canonical
template; do not invent a new shape.

You are running independently from another auditor (a different LLM
tool) who may be producing their own report from the same prompt.
**Do not read any other audit file under `audits/` newer than
`audit-2026-05-16-2239-claude.md`, and do not read any file under
`audits/prompts/` except this one.** If two reports get produced, they
will be reconciled in a later step using
`audits/prompts/pre-phase-3-reconciliation-prompt.md` (auto-discovers
the two newest unreconciled files); their value depends on being
produced blind to each other.

---

## 1. Identity and constraints

- **Role:** read-only auditor. You may read any file, run any
  non-mutating shell command, and execute the full test/lint/type
  suite. You may not edit source files, tests, fixtures,
  configuration, task documents, agent prompts, or any file outside
  `audits/`. The only file you write is your audit report.
- **No fixes.** If you see a defect, record it as a finding. Do not
  patch it, even one line. Repair work is owned by a separate task
  that will be authored from this audit (or its reconciliation, if
  two reports are produced).
- **No speculation.** Every finding must cite a `file:line` (or a
  reproducible shell command and its observed output). A finding
  without a citation is not a finding.
- **No drive-by suggestions.** If a recommendation does not address
  a cited defect or unverified invariant, omit it.
- **No real LLM provider calls.** Tests in this repo use a fake
  deterministic provider. You may run `bash scripts/check.sh` and
  any pytest invocation, but do not invoke the real Anthropic
  client. The real-provider 50-game eval is a separate stage and
  out of scope here. Validating the *static* / *fake-provider*
  dimension of every Phase 3 Merge Criterion is the goal.

## 2. Scope

**Audit window:** commits `45e664f` (HEAD when the post-3.8 audit
ran, after Task 3.8 merged) → current `HEAD` of `main`. Use
`git log 45e664f..HEAD --oneline --name-status` to enumerate every
commit and changed file in the window.

**Tasks landed in the window** (verify each against
`tasks/phase-3.md`):

- Task 3.9 — Strategic reasoner + sub-phase C integration substrate
  (PR #45, merged `d2e27c8`). Integration complexity. Bundles the
  strategic reasoner + Jinja loader (C-4) + BudgetedLLMClient (C-5)
  + L-1 / L-2 pins + R-10/strategic acceptance gate.
- Task 3.10 — Voting (PR #46, merged `d951caf`).
- Task 3.11 — Contradiction detection (PR #47, merged `918284b`).
- Task 3.12 — Meeting/orchestrator integration (PR #48, merged
  `639debc`). Integration complexity. Closes R-9 (replay format
  extension).

Plus the post-3.8 audit commit and any small task-doc-only commits.

**Explicitly out of scope:** Phase 0, Phase 1, Phase 2, and earlier
Phase 3 code (3.1–3.8) that was verified in previous audits and has
not changed in the window. Use `git diff 45e664f..HEAD -- <path>` to
confirm "no diff" before marking anything as "Still Pass (no diff)"
in your Regression Baseline section. Phase 4 work has not started;
the FastAPI app, WebSocket layer, and React frontend do not exist
yet.

**Real-provider behavior is also out of scope.** The 50-game eval,
impostor win rate in [25%, 65%], cost per game ≤ $0.30, and
transcript readability are validated by a separate prompt
(`pre-phase-4-real-provider-eval-prompt.md`) which will run after
this audit verdicts pass. This audit verifies the *infrastructure*
that the eval will exercise: replay format, end-to-end fake-provider
game completion, schema discipline, budget wiring, prompt loader
correctness. If you find a defect that would *cause* a real-provider
eval to fail (e.g. a meeting that crashes on a specific input shape),
that is in scope.

## 3. Required evidence

Run all of the following from the repo root. Record exit codes and
the last line of output for each in §3 of your report:

- `bash scripts/check.sh`
- `uv run lint-imports`
- `uv run mypy --strict agents observation orchestrator engine llm meetings`
- `uv run ruff check .`
- `uv run ruff format --check .`
- `uv run pytest`
- `uv run pytest tests/meetings -v`
- `uv run pytest tests/llm -v`
- `uv run pytest tests/agents -v`
- `uv run pytest tests/observation -v`
- `uv run pytest tests/orchestrator -v`
- `uv run pytest eval/leak_test.py eval/determinism_test.py -v`
- `uv run python scripts/validate_task_docs.py`
- `uv run python scripts/generate_prompts.py --check`
- `git grep -nE "_BODY_ID_VICTIM_PATTERN" agents/`
  (must return empty — R-4 retirement should still hold)
- `git grep -nE "['\"](player|impostor)-[0-9]+['\"]" eval/ tests/`
  (must return empty — pre-existing guard)
- `git grep -nE "anthropic|cache_control|extended_thinking" agents/ meetings/ orchestrator/`
  (must return empty — no Anthropic-specific concepts outside `llm/`)
- `grep -rn "from engine\|import engine" agents/ llm/ meetings/`
  (must return empty — firewall preserved)

Then run the live harnesses to verify outcomes:

- Six-seed sweep:
  `for seed in 0 1 2 7 42 100; do uv run python scripts/run_game.py --seed $seed --replay-path /tmp/audit-r-$seed.jsonl --max-ticks 1000; done`
  — Phase 2 substrate balance was 62.37%/37.63% post-3.8; the
  six-seed outcomes were 5 CREWMATES + 1 IMPOSTORS at ticks
  11/9/7/7/8/10. Re-verify they have not drifted.
- 100-game fake-provider tournament (orchestrator-driven full games,
  including LLM-driven meetings against the fake provider):
  `uv run python scripts/run_tournament.py --num-games 100 --start-seed 0 --output-dir /tmp/audit-tournament-pre-phase-4 --max-ticks 1000`
  — Both decisive sides must still > 20% (Phase 2 Merge Criterion).
  Phase 3 may shift the numbers compared to post-3.8's
  62.37%/37.63% because meetings now actually fire when the fake
  provider is wired all the way through. Record the new split.
- Long-horizon byte-identity check (R-9 closure):
  `uv run python scripts/run_game.py --seed 0 --replay-path /tmp/audit-byte-a.jsonl --max-ticks 500`
  twice, then `cmp /tmp/audit-byte-a.jsonl /tmp/audit-byte-b.jsonl`.
  Must be byte-identical AND must include at least one
  `MeetingReplayEntry` (verify with `grep MEETING /tmp/audit-byte-a.jsonl`
  or read the JSONL).
- 100-game tournament leak scan: walk all 100 audit logs through
  `eval/leak_test.py::_assert_no_recursive_hidden_fields` +
  `_assert_no_role_bearing_values`. Zero violations required.

Run additional commands as needed to verify specific findings.
Every command you run appears in §3 with its output evidence.

## 4. Required report structure

Mirror the structure of `audit-2026-05-16-2239-claude.md`:

1. Executive Summary (≤ 8 sentences; lead with the verdict).
2. Verdict — one of: **Ready for Phase 4 (pending real-provider eval)**,
   **Ready with fixes**, **Not ready**. Quantify what "fixes" means
   if applicable. The "(pending real-provider eval)" qualifier
   acknowledges that the live-LLM merge criteria are validated by a
   separate prompt.
3. Commands Run and Evidence Sources.
4. Regression Baseline — table comparing every prior-Pass row in
   `audit-2026-05-16-2239-claude.md` §4 to current state. "No
   diff" ⇒ Still Pass; "diff exists" ⇒ re-verified with citation.
5. Prior Audit Follow-Through — for each finding L-1, L-2, C-1,
   C-2, C-4, C-5 in `audit-2026-05-16-2239-claude.md` §10, state
   whether the in-window work closed it. The Pre-Phase-4 verification
   audit (if it ran before this one) already evaluated each — cite
   its conclusion if available, then independently confirm. R-9
   (May-15 Phase-3 addendum) was assigned to Task 3.12; verify
   the resolution.
6. Task-by-Task DoD Audit — one subsection per in-window task (3.9,
   3.10, 3.11, 3.12). For each: enumerate every DoD bullet from
   `tasks/phase-3.md`, mark Pass / Fail / Partial, cite evidence.
   Task 3.9's bundled deliverables (strategic reasoner, Jinja loader,
   BudgetedLLMClient, L-1, L-2, R-10/strategic, C-2 awareness) and
   Task 3.12's R-9 closure are the highest-priority verifications.
7. Architectural Invariant Audit — re-run every invariant from
   `audit-2026-05-16-2239-claude.md` §7. The new
   `agents/strategic/reasoner.py`, `llm/budgeted_client.py`,
   `meetings/voting.py`, and the orchestrator changes expand the
   LLM call surface and the engine→meeting interpose path; firewall
   and engine-purity invariants must be re-verified.
8. Specific Questions for the Phase 4 Layer — answer each question
   in §7 below.
9. Test Quality and Coverage Gaps — scrutinize the new tests
   (`tests/agents/test_strategic_reasoner.py`,
   `tests/agents/test_strategic_prompts.py`,
   `tests/llm/test_budgeted_client.py`,
   `tests/meetings/test_voting.py`,
   `tests/meetings/test_contradiction_detection.py`,
   `tests/orchestrator/test_meeting_integration.py` — exact names
   may vary) for false-positive risk and for whether they actually
   catch the regressions they claim to.
10. Defects and Risks (ordered by severity) — `[Severity] short title`
    then Status / Evidence / Why it matters / Recommended action.
    Severity buckets: **Critical**, **High**, **Medium**, **Low**,
    **Concern**.
11. Document Conflicts — `DESIGN.md`, `AGENTS.md`,
    `AGENT_IMPLEMENTATION.md`, `tasks/phase-*.md`, and code. Note
    new conflicts only.
12. Readiness for Phase 4 — direct answer with citations. See §7
    below. Note explicitly that the real-provider 50-game eval is
    the remaining gate and that this audit does not cover it.

## 5. Severity grading rubric

- **Critical** — A documented invariant is violated by code currently
  on `main`, OR observation packets leak hidden information, OR
  determinism is broken across two runs of the same seed, OR a Phase
  2 Merge Criterion fails on a real harness invocation, OR an
  Anthropic-specific concept leaks through the `LLMClient` Protocol
  surface, OR a fake-provider full game fails to complete, OR R-9
  replay format is not recording the required metadata.
- **High** — A DoD bullet for an in-window task is unmet, OR an
  architectural invariant is no longer pinned by a test, OR
  `BudgetedLLMClient` is not actually wired into the
  meeting/reasoner/orchestrator flow (silent bypass), OR voting
  tally has a bug that mis-attributes the outcome, OR contradiction
  detection produces false positives at a rate the test surface does
  not catch, OR the orchestrator's `MEETING_PHASE_REACHED` branch is
  still in place (Task 3.12 should have replaced it with the
  `MeetingManager` dispatch).
- **Medium** — Scope discipline violation (a PR touched files
  outside its contract's `Files in scope`, beyond what `## Decisions`
  documented), OR a documented behaviour is contradicted by another
  document, OR a regression test required by a DoD is missing but
  the underlying behaviour is correct.
- **Low** — Brittleness, latent failure modes that are currently
  unreachable, or coupling that is not enforced by a test.
- **Concern** — Worth flagging for Phase 4 (or the real-provider
  eval) but not a defect in current code.

If unsure between two buckets, choose the more conservative
(higher-severity) reading and say why in the finding body.

## 6. Deep-focus areas (do not skip)

These are the highest-blast-radius spots in the four in-window PRs.
Produce a verdict for each with citations, even if the verdict is
"Pass".

### 6.1 R-9 closure: replay format extension (Task 3.12)

R-9 (May-15 Phase-3 addendum, post-3.8 still open) requires
`ReplayEntry` (or its Phase 3 successor) to record meeting
transcripts, prompt versions, LLM outputs, and cost metadata per
DESIGN.md §11.4. Verify:

- `orchestrator/replay.py` exposes `MeetingReplayEntry` and
  `LLMCallRecord` (or equivalently named types).
- `MeetingReplayEntry` carries the full `MeetingTranscript` (reports,
  statements in canonical order, votes, result).
- `LLMCallRecord` carries `model`, `prompt_version`, parsed output,
  and `cost_usd`. Cumulative cost per game is reconstructable from
  the replay.
- At least one test runs a fake-provider game ≥ 200 ticks (or one
  full meeting cycle), captures the replay, then runs the same seed
  again and asserts byte-identical replay bytes.
- The replay is JSONL-parseable; lines can be read sequentially.

If `MeetingReplayEntry` exists but is missing one of the four
required metadata categories, that is **Critical** (R-9 is not
closed). If all four exist but the long-horizon byte-identity test
is missing, that is **High** (the metadata is present but its
determinism is not pinned).

### 6.2 Strategic reasoner pipeline correctness (Task 3.9)

`agents/strategic/reasoner.py` wires composite memory + Jinja
template + budgeted LLM call + Pydantic parse into a single
reasoner. Verify the full pipeline:

- `StrategicReasoner` (or equivalent) takes an `AgentMemory`, the
  budgeted client, and the four prompt callables in its constructor.
- The render flow uses `render_for_prompt(memory, token_budget)` to
  produce the rendered-memory string.
- The prompt-template flow calls the loaded Jinja callables with
  the rendered memory + meeting context.
- The LLM call goes through `BudgetedLLMClient.complete` with the
  appropriate schema parameter.
- The parsed output is type-checked against the expected schema
  (`ReportDocument`, `Statement`, or `VoteBallot`).
- Two runs of the same reasoner with the same inputs produce
  byte-identical outputs (fake provider).

A reasoner that bypasses any of these layers is **High**.

### 6.3 Voting tally semantics (Task 3.10)

`meetings/voting.py` implements the vote-tally logic. DESIGN.md
§5.2 specifies "If tie or below threshold, skip." Verify:

- Plurality below the configured threshold → `SKIPPED` outcome.
- Multi-way tie at the top → `SKIPPED` outcome (the C-3 narrowing
  from Task 3.8 collapsed `TIE` into `SKIPPED`).
- Single-winner above threshold → `EJECTED` with the correct
  `ejected_player_id`.
- Skip votes are tallied correctly (a `SKIP` vote counts toward the
  skip total).
- Hallucinated vote targets (player ids the LLM made up) are
  normalized to `SKIP`, not allowed to corrupt the tally.

If any of these is wrong, that is **High** — Phase 4 (and the
real-provider eval) cannot trust vote outcomes.

### 6.4 Contradiction detection (Task 3.11)

`agents/strategic/...` (or `meetings/contradictions.py` — wherever
3.11 landed it) detects cross-round contradictions in a
`MeetingTranscript`. The C-3 canonical-order contract from Task 3.8
makes cross-round comparison clean. Verify:

- The detector reads `transcript.statements` in canonical order
  (relies on the producer guarantee, does not re-sort).
- The detector returns `ContradictionRef` instances (per
  `meetings/schemas.py`) when an agent's round-N statement
  contradicts their round-(N−1) statement (or another agent's
  earlier claim, per DESIGN.md §5.4).
- False positives are bounded: at least one test exercises a
  scenario where statements are *consistent* and asserts no
  contradictions are flagged.
- True positives are caught: at least one test plants a contradiction
  and asserts the detector finds it with the correct
  `ContradictionRef` shape.

### 6.5 Orchestrator meeting integration (Task 3.12)

Task 3.12's critical deliverable: replace the
`MEETING_PHASE_REACHED` early-exit branch in `orchestrator/game.py`
with a `MeetingManager` dispatch. Verify:

- `orchestrator/game.py` no longer returns `MEETING_PHASE_REACHED`
  as an early-exit outcome. Instead, when `state.phase == "MEETING"`,
  it dispatches into `MeetingManager.run(...)` and applies the
  result.
- An `apply_meeting_result(state, result)` engine function exists
  (or equivalent) that consumes a `MeetingResult` and produces a
  new `WorldState` with the ejection (if any) and the updated
  alive list.
- The orchestrator records the meeting in the replay log as a
  `MeetingReplayEntry`.
- A fake-provider end-to-end test runs a full game where at least
  one meeting fires (e.g. body report → meeting → vote → ejection
  or skip → tick clock resumes).
- The game can reach `CREWMATES` or `IMPOSTORS` outcome through
  the meeting path (not just through the kill/parity/tasks paths).

A surviving `MEETING_PHASE_REACHED` branch is **High** (Task 3.12's
DoD is unmet). A successful dispatch but missing replay entry is
**Medium**.

### 6.6 Fake-provider end-to-end game completion

The Phase 3 Merge Criteria require: "full-LLM games complete
end-to-end using fake-provider tests in CI." Verify:

- At least one CI test runs a full game with `MeetingManager` wired
  in via the fake provider. The test does not skip in CI.
- The test asserts a sensible terminal outcome (CREWMATES,
  IMPOSTORS, or — once meetings are real — possibly a meeting-driven
  ejection followed by continued play).
- The 100-game fake-provider tournament (run above in §3) completes
  without crashes.

If no such end-to-end test exists, that is **Critical** — the merge
criterion is not testable in CI.

### 6.7 Engine isolation and budget wiring

With four new modules added (`reasoner.py`, `budgeted_client.py`,
`voting.py`, and 3.11's contradiction detector), reconfirm:

- `lint-imports` still kept the agent→engine firewall.
- `meetings/` does not import from `engine/`. The state machine
  reads engine-shaped types only through `observation/` schemas or
  shared `meetings/schemas.py` types.
- `BudgetedLLMClient` is actually wired into the meeting flow.
  `MeetingManager` either takes a `BudgetedLLMClient` directly OR
  the orchestrator constructs it that way. Confirm with
  `grep -rn "BudgetedLLMClient" orchestrator/ meetings/ agents/strategic/`.
- The budget tracks cumulative spend across a full game's meeting
  calls. Confirm with a test that exercises a multi-meeting game.

### 6.8 Cross-provider portability preserved

The real-provider eval (Stage 3) and any future swap to OpenAI /
DeepSeek depends on `LLMClient`-shaped consumers staying
provider-neutral. Verify:

- `git grep -nE "anthropic|cache_control|extended_thinking" agents/strategic/ meetings/ orchestrator/`
  returns empty.
- `BudgetedLLMClient` does not expose Anthropic-specific knobs on
  its public surface.
- The four `.j2` templates do not reference Anthropic-specific
  formatting (no XML tags expected only by Claude unless explicitly
  documented).

Anthropic-specific leakage outside `llm/` is **Critical** (Phase 3
Merge Criteria implicitly require provider neutrality; explicitly
required by DESIGN.md §7).

### 6.9 Phase 2 substrate still healthy

Sub-phase C added significant new surface but should not have
touched Phase 2 engine code. Verify:

- 100-game fake-provider tournament meets the merge criterion
  (both decisive sides > 20%). The post-3.8 baseline was
  62.37%/37.63%; this checkpoint should reproduce, with possible
  shift now that meetings fire end-to-end.
- Six-seed sweep all decisive.
- 200-tick same-seed byte identity still PASS.
- Tournament leak scanner still PASS.
- 500-tick byte identity (R-9 long-horizon requirement) PASS.

Any Phase 2 gate failure is **Critical**.

## 7. Specific questions for the Phase 4 layer

Answer each in §12 of your report with a one-paragraph verdict and
citations:

1. **Is the replay format ready for the eval harness?** Phase 4
   spectator UI and Phase 5 eval metrics consume the replay log.
   Read `orchestrator/replay.py`. Does `MeetingReplayEntry` carry
   enough to render meeting transcripts in a spectator UI and to
   compute Phase 5 metrics (per-meeting vote tallies, contradiction
   counts, per-call cost)?
2. **Does the meeting interpose point allow Phase 4's WebSocket
   broadcasts?** Phase 4.2 (game broadcast) will need to push tick
   events AND meeting events. Is the `MeetingManager.run` flow
   currently structured so that intermediate states (report
   submitted, round started, vote cast) can be observed by a
   broadcast layer, or does it run as one opaque async block?
3. **Are there any Anthropic-specific assumptions in
   `agents/strategic/reasoner.py` or `meetings/manager.py` that
   would block a future provider swap?** Run the grep above; for
   each hit, decide whether it's a real coupling or documentation
   only.
4. **Does the cost-tracking machinery support the
   ≤ $0.30/game merge criterion check?** The real-provider eval will
   need to extract per-game cost from the replay log. Read
   `LLMCallRecord` and the per-game aggregation path. Is the
   aggregation a simple sum, or does the eval need to write its own
   reduction?
5. **Did Phase 3 introduce any new Phase 2 risks?** Tournament
   balance, byte identity, leak scan — re-verify.
6. **New Critical/High findings introduced by this audit window?**
   List any. If yes, they must be addressed before the real-provider
   eval (Stage 3) runs; if no, the real-provider eval may proceed.
7. **Is the substrate ready for Phase 4 dispatch after the
   real-provider eval passes?** Phase 4 begins with FastAPI scaffolding,
   game broadcast, React frontend. None of these should require
   further Phase 3 changes; if you spot a Phase-3 piece that Phase
   4's first task (4.1) will need but is missing, flag it.

## 8. Output

Write your report to:

`audits/audit-YYYY-MM-DD-HHMM-<tool>.md`

where `<tool>` is `codex` or `claude` (whichever you are). Use the
current local date and time. Include `<tool>` in the filename so
two independent reports (if run in parallel) do not collide.

If only one tool is running this audit, the filename suffix is
still required — reconciliation tooling auto-discovers the two
newest unreconciled audit files. A single-tool run still produces
a canonical audit when no reconciliation is needed; the reviewer
reads the single report directly.

Do not commit. Do not open a PR. Do not modify any other file. When
finished, print the absolute path of the report and a one-paragraph
summary naming: the verdict, the count of Critical / High / Medium
findings, the single most important thing to fix before the
real-provider eval, and whether the substrate is ready for Phase 4.

---

## Anti-patterns (do not do these)

- Do not paraphrase the post-3.8 audit's findings as if you
  re-verified them. Either re-run the check and cite the new
  evidence, or omit the finding.
- Do not produce a "looks good" section. Either a thing is verified
  with evidence, or it is a Concern.
- Do not include code suggestions, refactor proposals, or
  architectural improvements that are not tied to a cited defect.
- Do not soften severities to be polite. A Critical finding stays
  Critical even if the responsible PR is recent.
- Do not invoke the real Anthropic provider. Every test in this
  audit runs against the fake. The real-provider 50-game eval is
  a separate stage.
- Do not write more than ~500 lines. The audit window is four
  tasks; that bounds the report length.
- Do not re-litigate Task 3.8's C-3 choice (producer-guaranteed
  canonical order). The decision is final.
- Do not audit Phase 4 tasks that do not exist yet. If a question
  depends on Phase 4 code that hasn't been written, frame it as a
  Phase 4 readiness question (§7), not a finding.
- Do not preempt the real-provider eval. Findings about the live
  LLM's behavior (transcript readability, win-rate band, actual
  cost) belong to the separate eval prompt; this audit verifies the
  infrastructure that the eval will exercise, not the eval itself.
