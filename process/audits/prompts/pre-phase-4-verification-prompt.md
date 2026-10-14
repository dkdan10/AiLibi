# Pre-Phase-4 Verification Audit — Prompt

You are running a lightweight, single-tool verification pass at the
end of Phase 3. The question you answer is exactly:

> Are the post-3.8 audit's findings (L-1, L-2, C-1, C-2, C-4, C-5) and
> the May-15 reconciled audit's Phase-3 acceptance gates (R-9, R-10/strategic)
> actually closed at current `HEAD`?

This is the unit test for the implementation work landed in PR #45
(Task 3.9), #46 (3.10), #47 (3.11), and #48 (3.12). It is NOT a fresh
audit. A separate full-pipeline audit
(`audits/prompts/pre-phase-4-audit-prompt.md`) handles fresh-discovery
work; a separate real-provider eval prompt
(`audits/prompts/pre-phase-4-real-provider-eval-prompt.md`) handles
the live-LLM merge criteria. Keep this audit's scope tight.

---

## 1. Identity and constraints

- **Role:** read-only verifier. You may run any non-mutating shell
  command and the full test/lint/type suite. You may not edit any
  source, test, configuration, task, or prompt file. The only file
  you write is your verification report.
- **Verification, not discovery.** Do not surface new findings. If
  you notice something while verifying that is not covered by the
  listed findings, record it in §4 "Observations" — one paragraph,
  no detailed analysis. The full Pre-Phase-4 audit will sweep for
  new findings; do not pre-empt it.
- **No severity re-grading.** The source audits' gradings stand.
- **No real-provider calls.** This verification runs against the
  fake deterministic provider only. The real-provider 50-game eval
  is a separate stage.

## 2. Inputs and forbidden inputs

**Allowed reads:**

- `audits/audit-2026-05-16-2239-claude.md` §10 (the post-3.8 audit's
  Defects and Risks section — read in full).
- `audits/audit-2026-05-15-0225-reconciled.md` §10 (the May-15
  reconciled audit's findings, specifically R-9 and R-10 — read
  those rows and their Phase-3 acceptance-gate language).
- The repository at current `HEAD` of `main`.
- Any PR's diff via `gh pr diff <N>` for PRs #45, #46, #47, #48.

**Forbidden reads:**

- Other audit files under `audits/` (older audits, other source
  audits from the May-16 cycle).
- Other prompt files under `audits/prompts/` except this one.
- The `## Decisions` blocks of the implementation PRs — for closure
  evidence, look at the **code and tests** directly. PR descriptions
  are claims, not evidence.

## 3. Required evidence (commands to run)

Run all of the following from the repo root. Record exit code and
last line of output for each in §2 of your report:

- `bash scripts/check.sh`
- `uv run lint-imports`
- `uv run pytest`
- `uv run pytest tests/llm -v`
- `uv run pytest tests/agents -v`
- `uv run pytest tests/meetings -v`
- `uv run pytest tests/orchestrator -v`
- `uv run pytest eval/leak_test.py eval/determinism_test.py -v`
- `git grep -nE "_assert_no_recursive_hidden_fields\|_assert_no_role_bearing_values" tests/agents/test_strategic_reasoner.py tests/agents/test_strategic_prompts.py`
  (must find direct-import evidence — C-1 closure depends on this)
- `git grep -nE "from eval\.leak_test import" tests/agents/`
  (must find at least one direct import — C-1 closure depends on this)
- `git grep -nE "_COST_USD_CAP_SLACK\|cap.*0\.30.*1e-3\|cap.*0\.30.*1e-9" tests/llm/test_budget.py`
  (L-1 closure must add boundary pins)
- `git grep -nE "last_seen.*confirmed.dead\|saw_body.*last_seen\|confirmed.dead.*last_seen" tests/agents/test_memory_rendering.py`
  (L-2 closure must add a confirmed-dead last-seen pin; the exact
  test name may vary — read the file if grep is too narrow)
- `ls agents/strategic/prompts/`
  (must show a Python loader file, e.g. `loader.py` or `__init__.py`
  exporting callables — C-4 closure depends on this)
- `git grep -nE "StrictUndefined\|jinja2.Environment" agents/strategic/prompts/`
  (C-4: loader must use strict-undefined behavior)
- `ls llm/budgeted_client.py`
  (must exist — C-5 closure)
- `git grep -nE "preflight\|charge_response" llm/budgeted_client.py meetings/manager.py agents/strategic/reasoner.py orchestrator/game.py`
  (C-5: budget is actually wired into the meeting / reasoner / orchestrator flow)
- `git grep -nE "meeting_transcript\|prompt_version\|llm_cost\|cost_usd\|MeetingReplayEntry\|LLMCallRecord" orchestrator/replay.py`
  (R-9 closure: replay format must record meeting artifacts, prompt
  versions, LLM outputs, and cost metadata per DESIGN.md §11.4)
- `git grep -nE "200\b.*byte.identical\|byte.identical.*200\|max_ticks=200\|range\(200\)" tests/orchestrator/`
  (R-9 closure: at least one long-horizon byte-identity test ≥ 200
  ticks)
- Six-seed sweep —
  `for seed in 0 1 2 7 42 100; do uv run python scripts/run_game.py --seed $seed --replay-path /tmp/verify-r-$seed.jsonl --max-ticks 1000; done`
  — all six must reach a decisive outcome (Phase 2 substrate smoke).
- Small fake-provider tournament —
  `uv run python scripts/run_tournament.py --num-games 20 --start-seed 0 --output-dir /tmp/verify-tournament --max-ticks 1000`
  — both decisive sides > 20% (Phase 2 substrate regression check;
  not the real-provider 50-game eval).

## 4. Required report structure

Write to `audits/audit-YYYY-MM-DD-HHMM-pre-phase-4-verification.md`.

Required sections:

1. **Verdict.** One of:
   - **Verification passed — Pre-Phase-4 audit may proceed.** Every
     listed finding is `Closed`.
   - **Verification blocked.** One or more findings are `Not closed`
     or `Partial` in a way that warrants a repair task before the
     full audit runs.
2. **Commands run.** Every command + last-line output.
3. **Finding closure table.** One row per finding:

   | ID | Severity | Source audit | Disposition | Evidence | Blocker? |

   - **Disposition:** `Closed`, `Partial`, or `Not closed`.
   - **Evidence:** the specific `file:line`, commit, test name, or
     reproducible command that proves closure. Cite concretely.
   - **Blocker:** `yes` / `no`.
4. **Observations.** One paragraph (≤ 150 words). Anything you
   noticed outside the listed findings. Write "None." if nothing.
5. **Verdict justification.** One short paragraph stating why the
   verdict in §1 follows from the table in §3.

## 5. Finding-specific closure checks

Walk this list in order. For each finding, the listed evidence is
the minimum for `Closed`. Anything weaker is `Partial` or `Not
closed`.

- **L-1 [Low, post-3.8]** — Budget cap-slack boundary pin.
  `tests/llm/test_budget.py` must contain test(s) that assert
  `cap=0.30, charge=0.30 + 1e-3` raises `BudgetExceededError` and
  `cap=0.30, charge=0.30 + 1e-9` does not. The tests must reference
  the slack constant by name OR pin the documented behavior at the
  boundary.
- **L-2 [Low, post-3.8]** — `last_seen` confirmed-dead suffix pin.
  `tests/agents/test_memory_rendering.py` must contain a test that
  records both a `saw_player` event and a `saw_body` event for the
  same player id, renders via `render_for_prompt`, and asserts the
  `(last seen in ROOM at tick N)` suffix appears on the dead
  player's belief line.
- **C-1 [Concern, post-3.8]** — R-10 leak-scanner reuse via direct
  import. `tests/agents/test_strategic_reasoner.py` (and any
  related strategic-prompt tests) must import
  `_assert_no_recursive_hidden_fields` and
  `_assert_no_role_bearing_values` directly from
  `eval.leak_test`. No Phase-3 successor scanner with the same
  contract is acceptable. The R-10/strategic acceptance gate from
  the May-15 audit requires this; the post-3.8 audit's C-1 flagged
  the "or successors" hedge in `tasks/phase-3.md` — verify the
  implementation chose direct import.
- **C-2 [Concern, post-3.8]** — `render_for_prompt` non-elastic
  carve-out. DESIGN.md §6.6 must contain the carve-out paragraph
  added before Task 3.9 dispatched (role + tasks-completed +
  beliefs + contradictions always retained; observations are
  elastic). `agents/strategic/reasoner.py` must respect this
  contract — it should NOT re-implement elasticity for beliefs /
  contradictions. Verify with a read of both files.
- **C-4 [Concern, post-3.8]** — Jinja loader for the four `.j2`
  templates. `agents/strategic/prompts/` must contain a Python
  loader (e.g. `loader.py` or `__init__.py`) that exposes per-
  template callables using `jinja2.Environment(
  undefined=StrictUndefined)`. `tests/agents/test_strategic_prompts.py`
  must exist and exercise each of the four templates with realistic
  inputs, asserting (a) non-empty output, (b) version-marker
  substring presence, (c) Pydantic schema validation against the
  rendered output using the fake provider.
- **C-5 [Concern, post-3.8]** — `BudgetedLLMClient` adapter.
  `llm/budgeted_client.py` must define `BudgetedLLMClient`
  wrapping any `LLMClient` plus a `GameBudget`. Each `complete()`
  call must invoke `budget.preflight()` before the underlying call
  and `budget.charge_response()` after. `tests/llm/test_budgeted_client.py`
  must exist and exercise a sequence whose cumulative cost
  approaches and then exceeds a configured cap; the test asserts
  `BudgetExceededError` propagates from preflight, NOT from silent
  truncation, NOT after the underlying client was called. The
  adapter must be used by `MeetingManager` (or the orchestrator) —
  verify with the grep for `preflight` / `charge_response` in those
  modules above.
- **R-9 [Concern → Phase-3-addendum, May-15]** — Replay format
  extension. `orchestrator/replay.py` (or its Phase 3 successor)
  must record:
  - meeting transcripts (`MeetingReplayEntry` or equivalent),
  - prompt versions (per-call metadata),
  - LLM outputs (text + parsed schema + model),
  - cost metadata (`cost_usd` per call + cumulative per game).
  At least one test must exercise a long-horizon (≥ 200 ticks or
  one full meeting cycle, whichever is longer) replay and assert
  byte-for-byte identity across two runs of the same seed.
- **R-10/strategic [Concern → Phase-3-addendum, May-15]** — Leak
  scanner reuse on strategic prompt inputs. Closed alongside C-1
  above. Verify
  `tests/agents/test_strategic_reasoner.py` plants at least one
  forbidden role-bearing string into a strategic prompt input and
  asserts the leak scanner trips on it.

## 6. Verdict rules

- **All Closed ⇒ Verification passed.**
- **Any Concern = `Partial`** is a judgment call. The verdict is
  passed if the residual risk is small and well-contained; blocked
  if the partial closure means the full audit would re-discover it
  as a real finding.
- **Any Low = `Not closed`** is blocked only if the underlying
  behavior is also wrong. A coverage gap that is *only* a coverage
  gap (the behavior is correct, just unpinned) is passed with a
  note — it will resurface in the full audit.
- **Any R-9 / R-10/strategic finding = `Not closed` is blocked.**
  These are the Phase-3 acceptance gates from the May-15 audit;
  they must be closed before Phase 4.

When finished, print:

- The absolute path of the report.
- The verdict.
- The count of `Closed` / `Partial` / `Not closed` dispositions.
- Any commands that failed.

---

## Anti-patterns

- Do not surface new findings as IDs. Record observations only.
- Do not run the full 100-game tournament or the real-provider
  50-game eval. Both are handled by other prompts.
- Do not run real-provider calls. Every test in this verification
  uses the fake provider.
- Do not edit any audit, prompt, or task file.
- Do not exceed 250 lines in the output report.
- Do not adjudicate severity. The source audits' gradings stand.
