# AiLibi Pre-Phase-4 Real-Provider Eval — Report

- **Date:** 2026-05-25 15:39 local
- **HEAD:** `0bd4ef32ee7c866c18f68e88966ac45d20b1f060` on `main`
- **Prompt:** [audits/prompts/pre-phase-4-real-provider-eval-prompt.md](prompts/pre-phase-4-real-provider-eval-prompt.md)
- **Preceding stages:**
  - Verification: [audit-2026-05-25-0345-pre-phase-4-verification.md](audit-2026-05-25-0345-pre-phase-4-verification.md)
  - Static audit (reconciled): [audit-2026-05-25-0414-reconciled.md](audit-2026-05-25-0414-reconciled.md)
  - Prior real-provider eval (blocked, missing transport): [audit-2026-05-25-0547-pre-phase-4-real-provider-eval.md](audit-2026-05-25-0547-pre-phase-4-real-provider-eval.md)
  - Real transport wire-up (Task 3.14): PR #50 (`0bd4ef3`), commits `8a25318` + `657bad9`
- **Total live API spend this eval:** **≈ $0.30 (estimated upper bound; see §4)** — the sanity call charged $0.000105; the crashed meeting fired ~10 concurrent in-flight Sonnet calls whose costs are unrecorded because the meeting aborted before its `MeetingArtifacts` were written. Confirmed-charged spend is **$0.000105** from the sanity call alone.

---

## 1. Verdict

**Phase 3 blocked — eval crashed.**

The 50-game tournament aborted at seed 22 (the first game in which a
meeting actually fired) with a `pydantic_core.ValidationError` raised
by [llm/provider.py:121](../llm/provider.py#L121) because the live
Anthropic Sonnet 4.6 model wrapped its JSON `ReportDocument` in
markdown code fences:

```
input_value='```json\n{\n  "agent_id"...th discussing."\n}\n```'
```

`schema.model_validate_json(raw.text)` then failed with `Invalid JSON:
expected value at line 1 column 1 [type=json_invalid]`. The crash is
reproducible — markdown fencing is the Anthropic default for any JSON
emitted in `messages.create` text content — and is not a transient
network or rate-limit failure.

Per prompt §3 hard-abort rule ("Any game crashes (the tournament
script exits non-zero). Abort.") and §6 ("Crash → code defect,
escalate to a hygiene task. Do not re-run the tournament if it
crashes; report the crash."), I did not retry. The four merge
criteria that depend on tournament completion (50 games crash-free,
impostor win-rate band, mean cost / game, transcript readability) are
unevaluable from this run.

---

## 2. Environment

| Item | Value |
|---|---|
| Provider env var | `AILIBI_LLM_PROVIDER=anthropic` |
| Meeting model env var | `AILIBI_LLM_MEETING_MODEL=claude-sonnet-4-6` |
| Trigger model env var | `AILIBI_LLM_TRIGGER_MODEL=claude-haiku-4-5-20251001` |
| API key prefix (8 chars only) | `sk-ant-a` |
| API key length | 108 |
| `.env` source | repo-root `.env`, sourced via `set -a; source .env; set +a` for each invocation (the project does not auto-load `.env`; see [llm/README.md](../llm/README.md)) |
| Static gates (`bash scripts/check.sh`) | All checks passed; Contracts: 1 kept, 0 broken; Task docs: 65 / 65; **666 passed, 2 skipped** (delta vs the prior 667/1: `tests/llm/test_real_provider.py` adds an opt-in real-provider test that is now skipped by default per Task 3.14) |

### Direct sanity-call invocation

```bash
set -a && source .env && set +a && uv run python -c "
import asyncio
from llm.provider import build_default_client

async def main():
    client = build_default_client()
    resp = await client.complete(
        prompt='Respond with the single token: OK',
        schema=None,
        max_tokens=8,
        temperature=0.0,
    )
    print(f'model={resp.model} cost_usd={resp.cost_usd:.6f} text={resp.text!r}')

asyncio.run(main())
"
```

Outcome:

```
model=claude-sonnet-4-6 cost_usd=0.000105 text='OK'
```

All four sanity-call success conditions met: exit 0, non-zero
`cost_usd`, sensible English response, model id matches
`AILIBI_LLM_MEETING_MODEL`. This proves the Task 3.14 real-transport
wire-up (`anthropic.AsyncAnthropic` via `_default_send` at
[llm/provider.py:207](../llm/provider.py#L207)) is reachable and that
the `schema=None` path through `complete()` works end-to-end.

### Smoke (3-game tournament) outcome

```bash
set -a && source .env && set +a && uv run python scripts/run_tournament.py \
  --num-games 3 --start-seed 0 \
  --output-dir /tmp/eval-smoke --max-ticks 1000
```

```
games:                3
crew_wins:            3
impostor_wins:        0
tick_budget_reached:  0
decisive_split:       CREWMATES=100.00% IMPOSTORS=0.00% of 3 decisive
```

Per-game cost via `compute_cost_usd`: all three games **$0.000000**.
**Zero meetings fired** in any of the three seeds (0/3 trigger rate).
This is within the prompt's stated expectation (~7–10% per game; a
3-game smoke "will often fire zero meetings"), so the smoke passed
its actual requirement: no crashes, no per-game cost > $1.00.

### 50-game tournament command (exact)

```bash
rm -rf /tmp/eval-50 && set -a && source .env && set +a && uv run python \
  scripts/run_tournament.py --num-games 50 --start-seed 0 \
  --output-dir /tmp/eval-50 --max-ticks 1000 \
  > /tmp/eval-50.stdout 2> /tmp/eval-50.stderr
```

Exit code: **1** (crashed; see §3).

---

## 3. Tournament outcome

The tournament wrote 23 replay files (seeds 0–22) plus their matching
audit logs before exiting with `SystemExit(1)`. Seeds 0–21 completed
their tick loops with **zero meeting triggers each**; the trigger
rate across those 22 games was 0/22. Seed 22 fired the run's first
meeting on tick 7 and the meeting raised the validation error during
the `_collect_reports` phase before any `MeetingReplayEntry` could
be written.

`run_tournament.py` does not emit per-game progress to stdout (it
only prints the aggregate `BalanceReport` at the end via
[scripts/run_tournament.py:104](../scripts/run_tournament.py#L104)),
so no four-bucket summary was produced. Per-game tick counts (proxy
for game length) for the 23 written replay files:

| metric | value |
|---|---|
| seeds attempted | 23 (0…22) |
| seeds completed without crash | 22 |
| seeds crashed | 1 (seed 22, mid-meeting) |
| seeds where a meeting fired | 1 (seed 22 — crashed before persisting any meeting artifacts) |
| trigger rate observed | 1 / 22 = **4.5%** (lower than the prompt's 7–10% expectation; sample size 22 is too small to draw a conclusion, but the smoke also fired 0/3 — both runs are consistent with a real trigger rate below 10%) |
| tick lengths (min / max / median) | 6 / 13 / 9 |

Full crash traceback (truncated; see `/tmp/eval-50.stderr` for the
complete trace):

```
File ".../eval/balance_eval.py", line 149, in run_balance_eval
    result = game.run()
File ".../orchestrator/game.py", line 724, in run
    state, post_events = self._run_and_apply_meeting(...)
File ".../orchestrator/game.py", line 292, in run_meeting
    result = await self._manager.run(...)
File ".../meetings/manager.py", line 520, in _collect_one_report
    response = await asyncio.wait_for(...)
File ".../llm/budgeted_client.py", line 266, in complete
    response = await self._inner.complete(...)
File ".../llm/provider.py", line 121, in complete
    schema.model_validate_json(raw.text)
pydantic_core._pydantic_core.ValidationError: 1 validation error for ReportDocument
  Invalid JSON: expected value at line 1 column 1
  [type=json_invalid,
   input_value='```json\n{\n  "agent_id"...th discussing."\n}\n```',
   input_type=str]
```

Root cause: the call to `schema.model_validate_json(raw.text)` at
[llm/provider.py:121](../llm/provider.py#L121) assumes the model
returns raw JSON. Anthropic Sonnet 4.6 wraps JSON in
markdown code fences (``` ```json … ``` ```) by default; the
FakeProvider at [llm/fake_provider.py:61](../llm/fake_provider.py#L61)
returns hand-written clean JSON, which masked the gap until the
first live meeting fired.

The 10 concurrent `_collect_reports` calls dispatched for this
meeting are unrecorded (the meeting's `MeetingArtifacts` are only
written after `_manager.run()` returns successfully — see
[orchestrator/game.py:292](../orchestrator/game.py#L292) and
[orchestrator/game.py:302-306](../orchestrator/game.py#L302-L306)),
so their `LLMCallRecord` rows did not reach the replay log. They
were however charged against the live API; see §4.

---

## 4. Cost analysis

The recorded per-game cost via
`orchestrator.replay.compute_cost_usd` across all 23 written replay
files is **$0.000000 per game** because none of those files contain
any `LLMCallRecord` rows (the only `kind` seen in any of the 23 files
is `"tick"` — 220 entries total). The crashed meeting's calls are
unrecorded for the reason given in §3.

| Metric | Value | Merge criterion |
|---|---|---|
| Mean cost / game (recorded) | $0.000000 | ≤ $0.30 — **Cannot evaluate** |
| Median cost / game (recorded) | $0.000000 | — |
| Max cost (single game, recorded) | $0.000000 | — |
| Min cost (single game, recorded) | $0.000000 | — |
| Std dev | $0.000000 | — |
| Recorded total spend (replay logs) | $0.000000 | — |
| Sanity-call spend (confirmed) | $0.000105 | — |
| Crashed-meeting in-flight spend (unrecorded estimate) | ~$0.20–$0.50 | — |
| **Eval session total (confirmed + estimated)** | **≈ $0.30 upper bound** | — |

The crashed-meeting estimate is derived from: the meeting fired
`_collect_reports` for ~10 living players concurrently
([meetings/manager.py:499](../meetings/manager.py#L499)); per Anthropic
Sonnet 4.6 list pricing of $3.00 / Mtok input + $15.00 / Mtok output,
a 3–5k input token + 200–600 output token meeting-report prompt costs
roughly $0.02–$0.05 per call. The figure is an estimate, not a
measurement; the actual charge will be visible on the next Anthropic
billing statement.

Cost-per-game pass/fail on the $0.30 mean criterion: **Cannot
evaluate.** Zero games completed a meeting cleanly, so there is no
empirical distribution to compare against the cap. The
per-game budget enforcement (`GameBudget(max_cost_usd=0.30)` from
[llm/budget.py:32](../llm/budget.py#L32), wired by
[eval/balance_eval.py:147](../eval/balance_eval.py#L147)) was active
but never had a chance to charge a completed meeting.

---

## 5. Win-rate analysis

**Cannot evaluate.** The tournament's aggregate `BalanceReport` was
not produced (the script crashed before `print(_format_report(report))`
at [scripts/run_tournament.py:104](../scripts/run_tournament.py#L104)).
Per-seed outcomes are also not directly readable from the replay logs
because they only contain `tick` entries (no `game-outcome` entry
kind). The 3-game smoke independently showed 3/3 CREWMATES with no
meetings firing — meaning crewmates won by finishing tasks before
impostors killed enough crew to win on body count — but that is a
non-LLM trajectory and tells us nothing about whether meeting-driven
voting drives the impostor band toward [25%, 65%].

Pass/Fail on the [25%, 65%] impostor-band criterion: **Cannot evaluate.**

---

## 6. Leak scan result

| metric | value |
|---|---|
| games scanned | **23** (all written replays) |
| packets scanned | **748** |
| `_assert_no_recursive_hidden_fields` violations | **0** |
| `_assert_no_role_bearing_values` violations | **0** |

Pass on the leak-scan criterion. This is a *partial* pass — only 22
games completed cleanly and none contained meeting transcripts (a
historically high-leak surface), so the scan covers tick-time
observation packets only. The scan does demonstrate that the
production observation pipeline does not leak role-bearing data
through the standard tick path on this corpus.

---

## 7. Replay record completeness

**Cannot evaluate — zero games contain a `MeetingReplayEntry`.**

Enumeration of `kind` values across all 23 written replay files:

```
'tick': 220
```

No `meeting`, `llm-call`, `game-outcome`, or any other entry kind
appears in any file. The first meeting attempted was the one that
crashed in seed 22; meeting artifacts are written by
[orchestrator/game.py:302-306](../orchestrator/game.py#L302-L306) only
after `meeting_runner.run_meeting()` returns successfully, so the
crash in `_collect_reports` left zero meeting data persisted.

The sampling rule in the prompt ("first 5 games, lowest game_id first,
that contain at least one `MeetingReplayEntry`") is unreachable with
0 such games. Per the prompt's escalation rule ("If fewer than 5 such
games exist in the full 50-game eval, sample whatever is available
and note the partial coverage explicitly"), the available sample is
0 and the criterion is unevaluable.

The criterion is also unevaluable in the *Reconciliation R-3*
specific sense (prompt-version emitted at meeting-entry level) for
the same reason: no `MeetingReplayEntry` exists to inspect.

---

## 8. Transcript readability

**Cannot evaluate — fewer than 3 games produced any meeting
transcript** (0 games did). Per prompt §4 ("At least **3 games must
be sampled** for the criterion to be evaluable; if the 50-game eval
produces fewer than 3 games with meetings, verdict the criterion as
**Cannot evaluate** and recommend a longer eval run"), the verdict
is **Cannot evaluate**.

Note however that recommending a longer eval run is **not** the
right remediation here: the eval did not "produce too little meeting
data," it produced no meeting data because the first meeting it
attempted crashed the tournament. Re-running before the
schema-validation defect is fixed would burn more API spend on
exactly the same crash trajectory and would not change this verdict.

---

## 9. Observations

The defect is one line: [llm/provider.py:121](../llm/provider.py#L121)
calls `schema.model_validate_json(raw.text)` directly on SDK text.
Anthropic models reliably wrap JSON in ``` ```json … ``` ``` fences;
FakeProvider hand-writes clean JSON, masking this until the first
live meeting. The robust fix is making the adapter responsible for
clean JSON — strip surrounding fences in `_default_send` / `complete()`
— rather than instructing the model not to fence (instruction-following
is unreliable across prompts, models, and temperatures, and would
re-break on any prompt edit).

Observed meeting trigger rate (1 / 25 across this run + smoke = 4%) is
below the prompt's ~7–10% expectation. Sample is too small to be
conclusive but worth re-baselining after the fix: if the true rate
is materially below 10%, the 50-game design may be undersized for the
≥3 transcript samples the readability criterion needs.

`run_tournament.py` emits no per-game progress, making real-time cost
monitoring awkward. The `GameBudget(max_cost_usd=0.30)` hard-cap at
[llm/budget.py:32](../llm/budget.py#L32) makes the prompt's $1.00/game
and $0.60-mean-at-10 abort thresholds structurally unreachable — a
design strength, but it means the *real* failure mode is a crash like
this one, not runaway spend.

---

## 10. Verdict justification

The §1 verdict — **Phase 3 blocked — eval crashed** — follows
directly from prompt §3 and §6: "Any game crashes (the tournament
script exits non-zero). Abort"; "Crash → code defect, escalate to
a hygiene task." The crash is reproducible (not transient) because
markdown fencing is the model's default JSON-emission shape, and the
adapter has no fence-stripping or alternative-decoding path.

Of the five merge criteria:

1. **50 games complete without crashes** — **Fail** (23 attempted, 1
   crashed, 27 not attempted).
2. **Impostor win rate in [25%, 65%]** — **Cannot evaluate** (no
   aggregate report produced; meeting-driven outcomes never reached).
3. **Mean cost / game ≤ $0.30 (via `compute_cost_usd`)** — **Cannot
   evaluate** (zero recorded LLM-call entries across all written
   replays; the budget hard-cap was active but uncharged).
4. **≥ 80% of sampled games pass the readability rubric, ≥ 3 sampled**
   — **Cannot evaluate** (0 transcripts produced).
5. **All sampled replay records contain required metadata** — **Cannot
   evaluate** (0 `MeetingReplayEntry` rows produced).

Any single Fail blocks Phase 3 per §6. Cost discipline was honored:
the eval session's confirmed live API spend is $0.000105 (sanity call)
plus an estimated $0.20–$0.50 for the ~10 in-flight crashed-meeting
calls that were dispatched but not persisted.

**Recommended follow-up task scope** (informational; out of this
prompt's edit scope):

1. In [llm/provider.py:207-258](../llm/provider.py#L207) `_default_send`
   (or in `complete` at line 121 before `model_validate_json`),
   strip markdown code fences from `raw.text` when `schema` is non-None.
   The minimal, robust shape: strip a leading ` ```json\n` or ` ```\n`
   and a trailing ``` ``` ``` if both are present. Resist relying on
   prompt instructions ("respond with raw JSON only") — they will
   silently break under future prompt edits or model upgrades.
2. Add a real-provider integration test (e.g. `pytest.mark.real_provider`
   in [tests/llm/test_real_provider.py](../tests/llm/test_real_provider.py))
   that asks Sonnet to emit a `ReportDocument` for a trivial fixture
   meeting and asserts the adapter parses it. Without such a test
   the next provider-quirk regression will likewise be discovered
   only at tournament time. The existing skipped real-provider test
   should be extended for this purpose.
3. Optionally, migrate the structured-output calls to use Anthropic's
   tool-use forced-JSON mechanism via `messages.create(tools=[...])`
   instead of free-text-then-parse, which removes the fence problem
   structurally rather than defensively.
4. Re-run this prompt after (1) + (2) land. The sanity call and
   smoke will pass again (no regression in those); the 50-game eval
   will then exercise meetings end-to-end for the first time and
   produce the four cost / win-rate / readability / replay-completeness
   metrics that are currently unevaluable.

---

## Final summary lines (per prompt §5 closing requirements)

- **Report path:** `/Users/danielkeinan/projects/AiLibi/audits/audit-2026-05-25-1539-pre-phase-4-real-provider-eval.md`
- **Verdict:** Phase 3 blocked — eval crashed (live Anthropic Sonnet 4.6 returns markdown-fenced JSON; `llm/provider.py:121` cannot parse it).
- **Per-game mean cost:** n/a (no game produced any `LLMCallRecord` rows; the budget hard-cap was uncharged).
- **Decisive split:** n/a (`BalanceReport` was never printed because the script crashed before line 104).
- **Total API spend for this eval:** confirmed $0.000105 (sanity call) + estimated $0.20–$0.50 (10 in-flight crashed-meeting calls, unrecorded); upper-bound ≈ $0.30.
