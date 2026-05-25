# Seed 23 Deep Debug — 2026-05-25 23:20 UTC

## 1. Executive summary

Seed 23 does **not** fire a meeting under any provider — under the fake provider
it ends at tick 11 with `IMPOSTORS` winning and zero meeting actions. A
deterministic seed sweep (0–22) confirmed that **seed 22** is the first seed in
the canonical tournament range to fire a live meeting (body discovery at tick 7,
3 living participants). The prior four eval reports' anchoring on "seed 23" was
a miscount of partial replay files; the actual first blocking meeting under the
live provider is seed 22. This investigation pivoted to seed 22 for the live
walk while keeping seed 23 as a documented control.

The full meeting flow was walked sequentially against the live Anthropic
provider (`claude-sonnet-4-6`) for seed 22 across all three phases:
**report**, **accusation_round**, **vote**. Reports (3/3) and votes (3/3) parsed
and validated cleanly; **all three accusation_round (`Statement`) calls
truncated at exactly `max_tokens=512` and raised
`JSONDecodeError: Unterminated string`** before Pydantic was reached — the
identical defect class the 2026-05-25-1823 eval reported on the same code path
([meetings/manager.py:576](../meetings/manager.py#L576), `_collect_statement`),
which Task 3.17 explicitly excluded from its scope on the (now-empirically-
falsified) reasoning that "statement and vote outputs are inherently smaller."
Total live spend: **$0.1233** (well under the $5 cap and the $3 soft cap). One
new critical defect class (statement truncation on the production code path),
two medium-severity latent issues (impostor `subject: "self"` template artifact;
vote at 70% of its cap), and several lower-severity concerns are detailed
below.

## 2. Pre-flight outcome

- `AILIBI_LLM_PROVIDER=anthropic`
- `AILIBI_LLM_MEETING_MODEL=claude-sonnet-4-6`
- `ANTHROPIC_API_KEY` prefix: `sk-ant-a` (8 chars only)
- `bash scripts/check.sh`: 676 passed, 2 failed, 8 skipped. The 2 failures
  are the documented sharp edge from the 1823/2138 eval reports
  ([tests/llm/test_budgeted_client.py](../tests/llm/test_budgeted_client.py)
  `test_default_cap_admits_fake_provider_meeting` and
  [tests/orchestrator/test_meeting_integration.py](../tests/orchestrator/test_meeting_integration.py)
  `test_meetings_fire_and_game_resumes_from_public_factory_path`) — both
  build `build_default_client()` which selects the live adapter when
  `AILIBI_LLM_PROVIDER=anthropic` is already in the shell. Per prior eval
  reports this is "CI must leave the var unset"; not blocking.
- Direct sanity call: **pass** —
  `model=claude-sonnet-4-6 cost_usd=0.0000930 text='OK'`. Non-zero cost
  proves the live provider was reached.

## 3. Fake-provider baseline

Seed 23 under fake provider:

```
outcome: IMPOSTORS
final_tick: 11
cost_usd: 0.000000
meeting: False
```

The actions JSONL shows impostor `p-2` killing `p-4` at tick 4 and `p-1` at
tick 11 with no body ever reported (3 alive crewmates — p-1, p-3, p-4 —
never co-located with the bodies before the second kill ended the game).

Sweep across seeds 0–30 confirms **seed 22 is the first seed in the
sweep to fire a meeting**:

| seed | outcome | final_tick | meeting |
|---|---|---|---|
| 0–21 | various decisive | 5–13 | False |
| **22** | **CREWMATES** | **10** | **True** |

Seed 22 meeting details (from its replay):
- Tick 1: `p-4` (impostor) kills `p-1` in CAFETERIA
- Tick 7: `p-3` reports `body-p-1-1` (body discovered in CAFETERIA at tick 6)
- Meeting fires: trigger=`p-3 reported body body-p-1-1 at tick 7`,
  triggered_by=`p-3`, trigger_tick=`7`
- Fake-provider outcome: `SKIPPED` (FakeProvider emits fake targets which
  the manager's `_normalize_ballot_target` correctly demotes to SKIP)
- Game resumes; ends `CREWMATES` at tick 10

**Implication for prior eval reports.** Prior eval reports
(`audit-2026-05-25-{0547,1539,1823,2038,2138}-pre-phase-4-real-provider-eval.md`)
each said "23 games completed (seeds 0–22), crash at game 24 / seed 23"; the
inference was based on counting `replay-seed-*.jsonl` files in the output
directory. But the orchestrator writes per-tick records to the replay file
incrementally during gameplay and only writes a meeting record after the
meeting completes. So a crash during seed 22's meeting would leave a partial
`replay-seed-22.jsonl` file with ticks 0–6 (or 0–7) and no meeting record.
The inference "23 files exist therefore seed 23 crashed" was wrong; the
actual crashing seed in every prior eval is **seed 22**. This does not
change the diagnosis (still "first meeting attempted on the live provider
fails") but it matters for the next eval's expected crash signature.

## 4. Meeting trigger characterization (seed 22)

| Field | Value |
|---|---|
| Trigger tick | 7 |
| Trigger action | `ReportBodyAction` (`p-3` reported `body-p-1-1`) |
| Triggering agent | `p-3` (`CREWMATE`) |
| Meeting id | `headless-seed-22:meeting-0` |
| Alive participants at trigger | `p-2` (CREWMATE), `p-3` (CREWMATE), `p-4` (IMPOSTOR) |
| Dead | `p-1` (killed by `p-4` at tick 1) |
| Meeting kicked off by | `engine.tick._apply_report` → `state.phase = MEETING` → `orchestrator.game._run_and_apply_meeting` → `DefaultMeetingRunner.run_meeting` |

The trigger is purely tactical: `p-3`'s default tactical agent emits a
`ReportBodyAction` on the tick it ends up co-located with a discovered
body. Tactical agents do not call the LLM, so the trigger is identical
under fake and live providers and is deterministic for the seed.

## 5. Captured prompts

Prompts were captured via an ad-hoc script
(`/tmp/seed-23-debug/capture_prompts.py`) that monkey-patches
`DefaultMeetingRunner.run_meeting` to intercept at meeting entry, capture
each participant's `rendered_memory` + role + suspicion_graph, render the
production Jinja prompts via
[agents/strategic/prompts/loader.py](../agents/strategic/prompts/loader.py),
write them to disk, and raise to abort gameplay before any LLM call.
Token estimates use whitespace-split word count as a rough proxy.

| Participant | Role | rendered_memory (chars) | Report prompt (chars) | Accusation prompt (chars) | Vote prompt (chars) |
|---|---|---|---|---|---|
| p-2 | CREWMATE | 289 | 3,843 | 4,486 (with real reports) | 4,786 (with real reports) |
| p-3 | CREWMATE | 545 | 4,099 | 4,742 (with real reports) | 5,042 (with real reports) |
| p-4 | IMPOSTOR | 681 | 5,046 | 4,878 (with real reports) | 5,178 (with real reports) |

All suspicion graphs were empty tuples — the default tactical agents
(`MeetingAwareDefaultAgent`) do not yet populate suspicion (a Phase 3 wiring
gap, but the schemas accept empty tuples so it does not crash).

**Per-prompt observations:**

- The crewmate report template includes the agent's own player id and the
  meeting tick in the prompt body, so the model gets `agent_id="p-3"`,
  `current_tick=7` directly. The crewmate's report output uses the correct
  ids and tick.
- The impostor template explicitly tells the model that the rendered memory
  does **not** include the impostor's player id ("the reasoner already knows
  this and will override"). The impostor model emitted `agent_id="self"`,
  `tick=6` (the impostor's last-observed tick, not the meeting tick), and
  also `alibi.subject="self"`. The manager overrides `agent_id` and the
  outer `tick`, but does **not** override nested `subject` fields on the
  claims — this is a real downstream issue (see §10 N3).
- The accusation_round template renders the public transcript as one long
  collapsed Markdown blob (no preserved newlines between fields). The
  rendered transcript text is technically readable but is not formatted as
  proper Markdown; the model still parses it correctly (output quality
  looks fine), but the prompt-byte usage is higher than necessary.
- p-3 report prompt head (first ~500 chars): "You are an AI agent
  playing a social-deduction simulation. You are a **crewmate**. A meeting
  has been called and you are at the **report intake** phase: each living
  agent submits one structured report at the same time. No
  accusation-round statements have happened yet, so you must reason only
  from your own memory and from the meeting trigger. Your job in this
  report is twofold: 1. Surface every observation from your memory that
  could help the crew identify the impostor. 2. State your honest beliefs
  and any alibi for yourself, calibrated to the strength of the evidence.
  ## Meeting context - You are: `p-3` - Current tick: 7 - Meeting trigger:
  p-3 reported body body-p-1-1 at tick 7 ## Your memory…"
- p-3 report prompt tail (last ~200 chars): "…- **Stay in role.** You are
  a crewmate. Do not claim to be the impostor and do not invent hidden
  information you "would have" if you were."

Full prompts saved under `/tmp/seed-23-debug/prompts/seed-22-{p-2,p-3,p-4}-{report,accusation,vote}.txt`
and the "-real" suffixed variants (accusation/vote re-rendered with the
captured live reports as transcript context).

## 6. Per-call response capture

Total spend (all 9 calls): **$0.1233** USD. Mean per call: **$0.0137**.
Max single call: **$0.0217** (p-3 report). All calls completed within ~5–15 s
each; no rate-limit or transport errors.

| Phase | Agent | Schema | Raw text len | Stripped len | Open fence | Close fence | Parse ok? | Validation ok? | tokens (in/out) | Cost |
|---|---|---|---|---|---|---|---|---|---|---|
| report | p-2 | ReportDocument | 1,853 | 1,795 | ✓ | ✓ | ✓ | **✓** | 1,139 / 865 | $0.0164 |
| report | p-3 | ReportDocument | 2,553 | 2,494 | ✓ | ✓ | ✓ | **✓** | 1,259 / 1,192 | $0.0217 |
| report | p-4 | ReportDocument | 1,196 | 1,138 | ✓ | ✓ | ✓ | **✓** | 1,468 / 556 | $0.0127 |
| accusation | p-2 | Statement | 1,271 | 1,271 | ✗ | ✗ | **✗** | ✗ | 2,802 / **512** | $0.0161 |
| accusation | p-3 | Statement | 1,251 | 1,251 | ✗ | ✗ | **✗** | ✗ | 2,922 / **512** | $0.0164 |
| accusation | p-4 | Statement | 1,325 | 1,325 | ✗ | ✗ | **✗** | ✗ | 2,985 / **512** | $0.0166 |
| vote | p-2 | VoteBallot | 1,065 | 1,007 | ✓ | ✓ | ✓ | **✓** | 1,331 / 268 | $0.0080 |
| vote | p-3 | VoteBallot | 967 | 909 | ✓ | ✓ | ✓ | **✓** | 1,451 / 227 | $0.0078 |
| vote | p-4 | VoteBallot | 869 | 810 | ✓ | ✓ | ✓ | **✓** | 1,514 / 203 | $0.0076 |

All raw + stripped texts saved under
`/tmp/seed-23-debug/responses/seed-22-*-{report,accusation,vote}.{raw,stripped}.txt`
and per-call JSON metadata under `/tmp/seed-23-debug/responses/seed-22-*-*.json`.

**Pattern observations:**

- **Reports and votes** are wrapped in `` ```json … ``` `` fences by the
  live provider. `_strip_json_code_fences` correctly removes them and
  Pydantic validates cleanly. Task 3.15/3.17 fence work holds.
- **Accusation responses come back WITHOUT fences** (raw JSON, no
  markdown wrapper). The fence stripper is therefore not relevant to
  the accusation failure; the failure is purely token-cap truncation.
- All three accusation responses have `output_tokens = 512` (exactly at
  the `DEFAULT_STATEMENT_MAX_TOKENS=512` cap). The model saturates
  every time. The responses end mid-string inside either an `evidence`
  array element or an `accusation.reason` field. `json.loads` raises
  `JSONDecodeError: Unterminated string` before
  `model_validate_json` reaches Pydantic.
- Input-token counts for the accusation phase (2.8K–3.0K) are
  substantially larger than the report phase (1.1K–1.5K) because the
  accusation prompt embeds the full Phase-1 transcript. With more
  participants alive and round 2 statements accumulated, accusation
  prompts will easily exceed 4K input tokens.

## 7. Pipeline failures

Three failed calls, all in the accusation phase, all on the same code
path ([meetings/manager.py:595](../meetings/manager.py#L595)
`Statement.model_validate_json(response.text)`).

| Phase | Agent | Failed layer | Specific error | Truncation evidence |
|---|---|---|---|---|
| accusation | p-2 | `json.loads` (called by `model_validate_json`) | `JSONDecodeError: Unterminated string starting at: line 32 column 17 (char 1020)` | Response ends `"…during the window when p-1 was killed"` (no closing `"`); output_tokens=512/512 |
| accusation | p-3 | `json.loads` | `JSONDecodeError: Unterminated string starting at: line 40 column 17 (char 1211)` | Response ends `"…p-2 was present in CAFETERIA at ticks 0"` (no closing `"`); output_tokens=512/512 |
| accusation | p-4 | `json.loads` | `JSONDecodeError: Unterminated string starting at: line 29 column 16 (char 1110)` | Response ends `"…p-2 left CAFETERIA toward"` (no closing `"`); output_tokens=512/512 |

All three failures are the **same root cause**: the model emits a
multi-claim statement with verbose evidence strings and reasons, the
output saturates at the `max_tokens=512` cap before the last string
closes, and `json.loads` correctly refuses an unterminated string.
Fence stripping does not apply (no fences present). The fix (Task 3.17
style) is to raise `DEFAULT_STATEMENT_MAX_TOKENS`.

Under the **production** code path the manager runs accusation
statements sequentially (`for round_index in range(self._config.round_count): for participant in speaker_order: ...`),
so the first speaker's call would fail; subsequent agents never get
a chance to fail in the same tick. The reporter (`p-3`) is at index 0
of the rotated speaker order so `p-3`'s statement is the deterministic
crash point in production. (This matches the 2026-05-25-1823 eval's
stack trace, which surfaced the same `_collect_statement` call site.)

## 8. Cost summary

| Metric | Value |
|---|---|
| Pre-flight sanity call | $0.000093 |
| Live walk (9 calls) | $0.1233 |
| **Total live spend** | **$0.1233** |
| Mean per call | $0.0137 |
| Max single call (p-3 report, 1.2K output tokens) | $0.0217 |
| Min single call (p-4 vote, 203 output tokens) | $0.0076 |
| Phase means: report / accusation / vote | $0.0169 / $0.0164 / $0.0078 |

**Per-meeting projection (using the observed means):**

A typical 5-alive-participant meeting (the tournament starts with 4
players + 1 impostor; first-meeting headcount usually 3–4) would run:
- Reports: N_alive × 1 = 4 calls × ~$0.017 = $0.068
- Statements: N_alive × 2 rounds = 8 calls × ~$0.016 = $0.130 (assuming
  the fix lands; current statement-call cost is the same because the
  truncated response still bills for its 512 output tokens)
- Votes: N_alive × 1 = 4 calls × ~$0.008 = $0.032
- **Total: ~$0.23 per meeting** at 4 participants (linear in participant count).

**Per-game projection.** Across 50 games with empirical ~5–10% meeting
rate observed in fake-provider sweeps (one meeting in seeds 0–22 of the
sweep), the live tournament should fire 3–5 meetings, yielding total
meeting spend ~$0.70–$1.15. Mean per-game cost: **~$0.015–$0.025/game**,
well under the merge criterion of $0.30/game. No mid-run abort risk.

The empirical per-call cost is consistent with the eval-prompt estimate
of $0.015–$0.05/call.

## 9. Latent issues surfaced

Each entry: `[Severity] short title` — Status / Evidence / Why it matters /
Recommended remediation.

### [Critical] Statement truncation at 512 tokens (production crash path)

**Status:** Open. Reproduces deterministically (3/3 statement calls
in this walk, identical pattern to the 1823 eval crash).
**Evidence:** All three Phase-2 statement calls returned
`output_tokens=512` and ended mid-string. Specific errors:
`JSONDecodeError: Unterminated string starting at: line {32,40,29}`. The
live provider responses end inside `evidence` arrays or `reason` strings
with no closing quote. The fence stripper is irrelevant — responses
have no fences.
**Why it matters:** This is the next deterministic crash blocking the
50-game eval. The production meeting flow's first crash is now the
reporter's statement at the start of accusation round 0 (per the
sequential speaker order), which means the meeting aborts before any
ballot is collected and `apply_meeting_result` is never invoked. Same
shape as Task 3.17's report fix; same fix shape applies. The 1823 eval
already saw this; Task 3.17 chose not to address it on the reasoning
that "statement and vote outputs are inherently smaller schemas" —
this investigation falsifies that assumption.
**Recommended remediation:** Raise `DEFAULT_STATEMENT_MAX_TOKENS` from
512 to 2048 (matching the Task 3.17 report cap), and add a
`@real_provider` truncation regression test analogous to
[tests/llm/test_real_provider.py](../tests/llm/test_real_provider.py)
`TestAnthropicTruncationFailureMode`. The cost impact is negligible
(statement responses empirically run ~1K tokens, so the new cap will
rarely be approached).

### [Medium] Vote responses at 70% of cap — narrow margin

**Status:** Concern (not yet failing).
**Evidence:** p-2's vote returned `output_tokens=268 / max_tokens=384`
(70% utilization). p-3 and p-4 votes ran 53–59%. This was a 3-living-
participant meeting with no contradictions and no prior accusation
statements; a 4–5 participant meeting with round-2 statements and
contradiction flags would produce longer vote rationales.
**Why it matters:** The 1823 eval prompt cited "Statement (or nested
VoteBallot) field cut off mid-string" — the same truncation class on a
different schema is plausible for VoteBallot in a future seed.
**Recommended remediation:** Raise `DEFAULT_VOTE_MAX_TOKENS` from 384
to 1024 in the same task as the statement fix. Cost impact is minimal
because the model rarely fills the new headroom.

### [Medium] Impostor template emits `subject: "self"` in alibi claims (survives into transcript)

**Status:** Open (template defect; not a crash).
**Evidence:** p-4 (IMPOSTOR) report emitted
`{type: "alibi", subject: "self", from_tick: 0, to_tick: 2, room: "CAFETERIA", ...}`.
The manager overrides only the outer `agent_id` and `tick` on
ReportDocument; nested claim subjects are passed through verbatim.
The rendered impostor transcript line therefore reads
`alibi: self in CAFETERIA from tick 0 to 2`.
**Why it matters:** Downstream contradiction detection (Task 3.11,
indexing `(agent, tick_range, location)`) cannot match `subject="self"`
to a real player id. Impostor alibis silently bypass contradiction
detection. The CONTRADICTION_FLAGS field in subsequent rounds would
miss any impostor-vs-witness alibi conflicts. Crewmate reports use real
player ids correctly because the crewmate template injects the
player_id into the prompt.
**Recommended remediation:** Two options — (a) inject the impostor's
own `player_id` into the impostor template the same way the crewmate
template does (the agent identity is non-secret within the model — the
impostor template is rendered server-side per agent), and update the
template guidance to use it. (b) Normalize nested claim subjects on
the manager side: when `subject == "self"` (or `agent_id`) on an
AlibiClaim, replace with the participant's `agent_id`. Option (a) is
cleaner; (b) is defense-in-depth.

### [Concern] Impostor emits placeholder `agent_id`/`tick` that get overridden silently

**Status:** Working as templated (no crash) — flagged because the
override pattern is fragile.
**Evidence:** p-4 emitted `agent_id="self"`, `tick=6` (not 7 / the
meeting tick). Manager overrides via `parsed.model_copy(update={...})`
at [meetings/manager.py:546](../meetings/manager.py#L546).
**Why it matters:** Any future downstream consumer that reads the
LLM-emitted tick (instead of the manager-overridden tick) on a
ReportDocument from before the override would see wrong values. The
override is in the manager, not on the Pydantic model, so a different
call site that parses the raw response (e.g. a diagnostic dump) would
not benefit. No immediate impact; flagged for design awareness.

### [Concern] Accusation template renders public transcript as collapsed Markdown

**Status:** Cosmetic / token-bloat (no crash).
**Evidence:** Looking at p-2 accusation prompt:
`### Reports submitted in Phase 1- **p-2** at tick 7:  - Observations:    - tick 0 -- saw p-1 in CAFETERIA with p-3, p-4...`
— Markdown bullets and headings are concatenated without proper
newlines. This is likely a Jinja2 `{%- -%}` whitespace-stripping
artifact in `accusation_round.j2`'s transcript-rendering loops.
**Why it matters:** The model still parses the content correctly (all
three accusation responses cited specific ticks / rooms / players
accurately), so this is not a quality regression. But the input-token
count is inflated by the collapsed-onto-one-line formatting making the
content less compressible, and a human reading the prompt for debugging
sees something hard to follow. Minor.
**Recommended remediation:** Audit the Jinja `{%- ... -%}` markers in
[accusation_round.j2](../agents/strategic/prompts/accusation_round.j2)
(and `loader.py`'s `trim_blocks=True, lstrip_blocks=True`) and emit
proper newlines between rendered Report / Statement bullets.

### [Concern] Statement responses do not use markdown fences (provider behavior split)

**Status:** Working as-is.
**Evidence:** Reports and votes use `` ```json … ``` `` fences;
accusation statements arrive as raw JSON (no fences). Pattern is
deterministic across all 3 statement calls in this walk.
**Why it matters:** This is a *good* outcome — the fence-stripper
work in Tasks 3.15/3.17 doesn't need to handle the statement case
because the provider already returns clean JSON. Documented here so a
future investigation does not misattribute statement-related issues to
the fence stripper. The reason for the split is plausibly the prompt
length and structure: the statement prompt's "## Required output"
section ends with `Output the JSON object and nothing else.` while the
report templates end similarly but with more surrounding prose;
prompt-induced behavior.

### [Concern] Hallucinated player ids in placeholder fields (`speaker: "p-0"`)

**Status:** Working as-templated (manager overrides identity fields).
**Evidence:** p-2's accusation statement emitted `speaker: "p-0"` — a
non-existent player id. The accusation_round.j2 template tells the
model to emit any non-empty string for placeholder identity fields,
and the model invents `"p-0"` (perhaps because it has seen the `p-N`
naming pattern from the transcript). Manager overrides with the actual
speaker via `parsed.model_copy(update={"speaker": participant.agent_id, ...})`.
**Why it matters:** No immediate impact (manager always overrides),
but combined with the impostor-`subject:"self"` issue above, it
demonstrates the model is willing to fabricate player ids when given
permission. Anywhere the manager does NOT override an LLM-emitted
identity field, the model's value is untrustworthy. Same recommended
guardrail as the impostor subject issue.

### [Concern] FakeProvider does not exercise truncation or schema-edge cases

**Status:** Known by design.
**Evidence:** FakeProvider builds minimal valid instances via
`_minimal_valid_instance` introspection — strings are
`f"fake-{field_name}-{seed}"` (short, no risk of truncation), arrays
are empty tuples, etc. Total output bytes for a synthesized
ReportDocument: ~250 chars; for a Statement: ~200 chars; for a
VoteBallot: ~150 chars. Far below any `max_tokens` cap.
**Why it matters:** Three of the four pre-Phase-4 evals (and this
investigation's findings) have been blocked by defect classes that
the fake provider cannot surface because the fake never exercises
verbose model output. Worth documenting that "fake provider green"
is necessary but not sufficient evidence the meeting flow works
against the live provider. The `@real_provider` tests in
`tests/llm/test_real_provider.py` are the right place to add
truncation regressions per defect class.

### [Concern] Seed-23 misattribution in the eval prompt and prior audits

**Status:** Documentation defect.
**Evidence:** Prior eval reports (0547, 1539, 1823, 2038, 2138) all
state "crash at game 24 / seed 23" — the inference came from counting
23 `replay-seed-*.jsonl` files under `/tmp/eval-50/`. But the
orchestrator writes per-tick records incrementally, so a crash during
seed 22's meeting leaves a *partial* `replay-seed-22.jsonl` with ticks
0–6 (no meeting record), making it look like 22 was completed and 23
was about to start. The actual blocking meeting is seed 22 in every
prior eval. This investigation's prompt is also anchored on "seed 23".
**Why it matters:** Future debug-prompt authors and re-runs will look
at the wrong seed. A fix-and-retest cycle that re-runs the tournament
expecting the crash at seed 23 may misinterpret a clean seed-23 run as
"fixed" when the actual fix needs to be verified at seed 22.
**Recommended remediation:** Note in the next eval prompt and in any
follow-up task that the first live meeting is at **seed 22**. Optional
substrate-level fix: persist a per-game outcome record into the replay
JSONL on game completion so partial vs complete games are
distinguishable from the file contents (this was already flagged in
the 2138 audit's §9 observations).

## 10. Defect-class taxonomy

Defect classes seen across the chain of pre-Phase-4 real-provider evals
and this investigation, with fix/open status.

| # | Defect class | First seen | Status | Resolving task |
|---|---|---|---|---|
| 1 | Live transport missing (no `_default_send`) | 0547 eval | Closed | Task 3.14 |
| 2 | Markdown JSON fences in ReportDocument | 1539 eval | Closed | Task 3.15 |
| 3 | Prompt-template ↔ schema field-name drift (`player_id`/`location`/`tick_start` vs `subject`/`room`/`from_tick`) | 2038 eval | Closed | Task 3.16 |
| 4 | ReportDocument truncation at `max_tokens=1024` → unclosed fence | 2138 eval | Closed | Task 3.17 |
| 5 | **Statement truncation at `max_tokens=512` (production crash path)** | 1823 eval (rediscovered + characterized here) | **OPEN** | Recommended Task 3.18 |
| 6 | **VoteBallot at 70% of `max_tokens=384` (margin risk)** | This investigation | **OPEN (not yet crashing)** | Bundle into Task 3.18 |
| 7 | **Impostor template emits `subject: "self"` on nested AlibiClaim** | This investigation | **OPEN** (no crash; affects contradiction detection) | Bundle into Task 3.18 or Task 3.19 |
| 8 | FakeProvider does not exercise verbose-output truncation paths | All prior evals | Known by design | No fix; document gap |
| 9 | `check.sh` 2 tests fail when `AILIBI_LLM_PROVIDER=anthropic` exported | 1823 eval onward | Open (low) | Hygiene task |
| 10 | Per-game outcome not persisted to replay JSONL | 2038 eval | Open (low) | Hygiene task |
| 11 | Seed-23 misattribution in prior eval reports | This investigation | Open (doc fix) | Update prompts and next eval |

## 11. Recommended next task scope

**Task 3.18 — Statement (and vote) max_tokens raise + impostor self-subject normalization**

Scope (a single bundled task — same code path, same defect family):

- Files in scope: [meetings/manager.py](../meetings/manager.py),
  [agents/strategic/prompts/impostor_report.j2](../agents/strategic/prompts/impostor_report.j2)
  (or its loader wrapper), [tests/llm/test_real_provider.py](../tests/llm/test_real_provider.py).
- Raise `DEFAULT_STATEMENT_MAX_TOKENS` from `512` to `2048` (matching
  the report cap from Task 3.17). Empirical justification: this
  investigation's 3/3 statement responses saturated at 512; raising to
  2048 doubles the headroom and stays comfortably under the per-game
  cost cap (8 statements × 2048 × $15/Mtok = $0.24 worst case per
  meeting, vs Task 3.16's $1.00/game cap).
- Raise `DEFAULT_VOTE_MAX_TOKENS` from `384` to `1024` for the same
  defense-in-depth reason (this walk's top vote was 268/384 = 70%;
  not yet failing but tight). Empirical impact: ~5 vote calls per
  meeting × 1024 × $15/Mtok = $0.077 worst case per meeting.
- Add two `@real_provider`-marked regression tests in
  `tests/llm/test_real_provider.py::TestAnthropicTruncationFailureMode`
  analogous to the existing report-truncation test, one each for
  `Statement` and `VoteBallot`, that pin the failure mode to
  `ValidationError` (not `Invalid JSON: line 1 column 1`). Cost:
  ~$0.002 per test (tight `max_tokens` cap forces truncation
  cheaply).
- Address the impostor `subject: "self"` issue **either** by injecting
  the impostor's own player_id into the impostor template (preferred —
  symmetric with the crewmate template) **or** by adding a manager-side
  normalization that replaces `"self"` with the participant's agent_id
  on nested claim subjects. The crewmate template already includes
  `agent_id` in its prompt body — adopting the same pattern in the
  impostor template is a 5-line change and avoids surprise overrides.
- Document the seed-22-not-seed-23 finding in the task's `## Decisions`
  block so the next eval prompt verifies against the correct seed.

A single bundled task is appropriate (vs three separate tasks) because
all three changes target the same blocking crash on the first live
meeting and share a code-review surface (meetings + impostor template +
real-provider test).

## 12. Confidence assessment

**High** confidence: the next eval will crash on the first live
meeting (seed 22) at the reporter's accusation_round statement call
unless Task 3.18 lands first. The Statement truncation is
deterministic (3/3 in this walk, all hit exactly `output_tokens=512`).

**High** confidence: the ReportDocument path (Task 3.17's fix) holds —
all 3 report calls in this walk validated cleanly with output_tokens
27–58% of the 2048 cap.

**Medium** confidence: the VoteBallot path will hold for the
first-meeting case (this walk's max was 70% of cap). Lower confidence
that it will hold across all 50 games and through round 2 with
contradiction flags accumulated; raising the cap as part of Task 3.18
removes the risk cheaply.

**Lower** confidence (unverified): later meetings in a single game
(`meeting_index >= 1`) with more accumulated history, contradiction
flags, and/or richer suspicion graphs may produce longer prompts and
longer responses. This investigation walked a single meeting in a
single seed and did not exercise multi-meeting or contradiction-flag
scenarios. The proposed cap raises (2048 / 1024) leave generous
headroom but are not empirically verified against multi-meeting
games. Risk: low (the model's typical output is far below the cap
even at the first meeting; doubling headroom is conservative).

**Unverified risks remaining:**

- Multi-meeting games: prompt growth across two or more meetings per
  game is not characterized here.
- Contradiction-flag-rich meetings: the empty `contradictions` tuple
  in this walk is a best-case scenario. Real Task 3.11 contradiction
  output may inflate accusation/vote prompts.
- 4–5 living-participant meetings: this walk had 3 alive (one had
  been killed by tick 1). Larger meetings produce more reports in the
  transcript, increasing input-token usage for accusation/vote
  prompts.
- The impostor-`subject: "self"` defect's downstream impact on Task
  3.11 contradiction detection: this investigation flagged it but did
  not measure the actual rate at which impostor alibis evade
  contradiction matching.

---

## Investigation deliverables

- **Report:** `/Users/danielkeinan/projects/AiLibi/audits/audit-2026-05-25-2320-seed-23-deep-debug.md`
  (this file).
- **Ephemeral artifacts** (NOT committed) under `/tmp/seed-23-debug/`:
  - `sweep.py`, `sweep-seed-{0..22}.jsonl` — fake-provider seed sweep
  - `capture_prompts.py`, `seed-{22,23}-capture.json` — meeting-entry interception
  - `prompts/seed-22-*-{report,accusation,vote}.txt` — captured production prompts
  - `prompts/seed-22-*-{accusation,vote}-real.txt` — re-rendered with live reports as transcript
  - `live_walk.py`, `all_records.json` — live-provider walk script + aggregated records
  - `responses/seed-22-*-{report,accusation,vote}.json` — per-call metadata
  - `responses/seed-22-*-{report,accusation,vote}.{raw,stripped}.txt` — per-call raw + post-strip text
- **Total live API spend:** **$0.1233** USD (across 9 meeting-pathway calls
  + 1 sanity call; well under the $5 cap and the $3 soft cap).

## Final summary

- **Report path:** `/Users/danielkeinan/projects/AiLibi/audits/audit-2026-05-25-2320-seed-23-deep-debug.md`
- **Total live spend:** $0.1233 USD
- **NEW defect classes (not in 3.15/3.16/3.17):** **1 critical** (Statement
  truncation at 512 tokens — production crash path; surfaced briefly in
  1823 eval, characterized end-to-end here) + **1 medium** (impostor
  template emits `subject: "self"` on nested claims) + **1 margin
  concern** (vote at 70% of cap).
- **Verdict: Fix 1 critical + bundle 2 mediums into a single Task 3.18.**
  Recommended re-eval AFTER the fix lands (do not re-run the 50-game
  tournament against the current code; the first live meeting at seed 22
  will deterministically crash on the statement call).
