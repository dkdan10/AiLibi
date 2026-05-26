# Pre-Phase-4 Real-Provider Eval — 2026-05-26 03:25 UTC

## 1. Verdict

**Phase 3 complete — Phase 4 may begin.** All five merge criteria
passed:

1. **50 games complete without crashes** — 50/50 finished cleanly,
   exit 0, no stderr output, every replay terminates in a winner
   record.
2. **Impostor win rate in [25%, 65%]** — 38.00% (19/50 decisive).
3. **Mean cost / game ≤ $0.30** — mean $0.0177, max $0.2405. Total
   spend $0.886 across the 50-game eval (well under any single-game
   abort threshold).
4. **Transcript readability ≥ 80% of sampled games** — 4/4 sampled
   games passed the rubric (100%). Sample size ≥ 3 satisfied.
5. **Replay record completeness** — every sampled meeting carries
   `MeetingTranscript` (reports + statements), `Ballots` with
   non-empty justifications, `prompt_versions` map at meeting-entry
   level (R-3 placement confirmed), and 12 `LLMCallRecord` rows each
   with `model`, `cost_usd`, input/output tokens. Per-game cost is
   reconstructable via `orchestrator.replay.compute_cost_usd` and
   matches a manual `sum(call.cost_usd)` to 1e-9.

Two non-blocking data-artifact observations are recorded in §9 and
should be considered for a Phase-4-side hygiene task, but neither
fails any merge criterion: (a) seed 24's statements use
`subject: "p-0"` for non-reporter speakers (no `p-0` exists in that
game), and (b) seed 49's impostor report uses `subject: "p-self"`
(post-Task-3.18 template artifact — `self` is normalized but the
literal string `p-self` appears to bypass the rewrite). Prose
rationales remain coherent and grounded in both cases.

## 2. Environment

- Provider: `AILIBI_LLM_PROVIDER=anthropic`
- Meeting model: `AILIBI_LLM_MEETING_MODEL=claude-sonnet-4-6`
- Trigger model: `AILIBI_LLM_TRIGGER_MODEL=claude-haiku-4-5-20251001`
- `ANTHROPIC_API_KEY` prefix: `sk-ant-a` (8-char prefix only)
- `bash scripts/check.sh` (with `AILIBI_LLM_PROVIDER` unset per
  `llm/README.md`): **699 passed, 11 skipped in 4.73s.** Static gates
  green.
- Direct sanity call:
  `model=claude-sonnet-4-6 cost_usd=0.000105 text='OK'`. Non-zero
  cost confirms the live provider was reached (not the fake adapter);
  model id matches `AILIBI_LLM_MEETING_MODEL`.
- 3-game smoke (`/tmp/eval-smoke`, seeds 0–2, `--max-ticks 1000`):
  3/3 games completed; outcome CREW/CREW/CREW; zero meetings fired
  (expected at ~7-10% trigger rate × 3 games); per-game cost $0.00
  (no LLM calls because no meetings triggered); no crashes. The
  smoke validates the tournament wrapper does not crash; the direct
  sanity call already validated live-provider reachability.

Tournament invocation (exactly):

```bash
uv run python scripts/run_tournament.py \
  --num-games 50 \
  --start-seed 0 \
  --output-dir /tmp/eval-50 \
  --max-ticks 1000
```

Background runtime: ~3 minutes wall clock. Exit code 0. Stderr empty.

## 3. Tournament outcome

Raw printed summary:

```
games:                50
crew_wins:            31
impostor_wins:        19
tick_budget_reached:  0
decisive_split:       CREWMATES=62.00% IMPOSTORS=38.00% of 50 decisive
```

No crashed games. No tick-budget timeouts. No abort triggered.

## 4. Cost analysis

Per-game cost stats over all 50 games (computed via
`orchestrator.replay.compute_cost_usd`, the canonical helper added
by Task 3.13):

| Metric | Value | Merge criterion |
|---|---|---|
| Mean cost / game | $0.017719 | ≤ $0.30 ✅ |
| Median cost / game | $0.000000 | — |
| Max cost (single game) | $0.240534 | (well under $1.00 abort) |
| Min cost (single game) | $0.000000 | — |
| Std dev | $0.060800 | — |
| Total spend | $0.885948 | — |

Only the 4 games that fired a meeting carried non-zero cost
(seeds 22 / 24 / 26 / 49). Per-meeting cost ranged $0.208 to $0.241
across 12 LLM calls per meeting (3 reports + 3 statements/round × 2
rounds + 3 votes). Median is $0 because 46/50 games never invoked
the LLM. **Pass.**

## 5. Win-rate analysis

Decisive split: CREWMATES 62.00% / IMPOSTORS 38.00% (50/50 decisive,
zero tick-budget games).

Merge band check: impostor win rate 38.00% ∈ [25%, 65%]. **Pass.**

## 6. Leak scan result

Ran `eval.leak_test._assert_no_recursive_hidden_fields` +
`_assert_no_role_bearing_values` over every packet in every audit
log:

| Metric | Value |
|---|---|
| Games scanned | 50 |
| Packets scanned | 1674 |
| Violations | **0** |

**Pass.**

## 7. Replay record completeness

Sampled the 4 games containing a `MeetingReplayEntry` (the first 4 by
seed order; full eval produced exactly 4 such games, below the
nominal-5 sample target — the criterion's sample-size floor of 3 is
satisfied and this is noted as partial coverage). For each sampled
game:

| seed | MeetingReplayEntry | LLMCallRecord rows | sample `model` | `cost_usd` present | cost helper matches manual sum |
|---|---|---|---|---|---|
| 22 | Yes (1) | 12 | claude-sonnet-4-6 | Yes | Yes ($0.208035) |
| 24 | Yes (1) | 12 | claude-sonnet-4-6 | Yes | Yes ($0.213714) |
| 26 | Yes (1) | 12 | claude-sonnet-4-6 | Yes | Yes ($0.223665) |
| 49 | Yes (1) | 12 | claude-sonnet-4-6 | Yes | Yes ($0.240534) |

Each meeting entry carries:

- `transcript` with `reports` (3) and `statements` (6 — 3 speakers ×
  2 rounds).
- `ballots` (3) with `voter`, `target`, `confidence`,
  `rationale_text` (non-empty for all 12 sampled ballots),
  `primary_reason_id`, `considered_alternatives`.
- `contradictions` list (empty in all 4 sampled games — first-meeting
  scenarios).
- `prompt_versions` map at entry level (per R-3 placement):
  `{"accusation_round": "accusation_round.v1", "crewmate_report":
  "crewmate_report.v1", "impostor_report": "impostor_report_v1",
  "vote_ballot": "vote_ballot/v1"}`. Each version string is non-empty
  and identifies the prompt template used.
- `llm_calls`: 12 rows per meeting, each row populated with
  `call_kind`, `model`, `cost_usd`, `input_tokens`, `output_tokens`,
  `prompt`, `response_text`.
- `state_hash_before` / `state_hash_after` (replay-determinism
  anchors).

**Pass.**

## 8. Transcript readability

Sampled the same 4 games. Each rated against the 4-dimension rubric;
game passes if ≥ 3 of 4 dimensions Pass with no Fails (Partials
tolerated).

| game | Coherent English | Role-appropriate | Grounded | Vote justifications | Game verdict |
|---|---|---|---|---|---|
| seed 22 | Pass | Pass | Pass | Pass | **Pass (4/4)** |
| seed 24 | Pass | Pass | Partial | Pass | **Pass (3/4 + 1 partial)** |
| seed 26 | Pass | Pass | Pass | Pass | **Pass (4/4)** |
| seed 49 | Pass | Pass | Partial | Pass | **Pass (3/4 + 1 partial)** |

Per-game reasoning:

- **Seed 22** — Impostor `p-2` (ejected, CREWMATES win). Reports
  reference real ticks/rooms (CAFETERIA, ADMIN, EAST_HALL).
  Crewmates `p-3`/`p-4` mutually corroborate ADMIN/EAST_HALL alibis
  during the kill window. Impostor `p-2`'s deflection ("p-3 and p-4
  both claim to have found the body") is fluent in-game lying.
  Ballot rationales tie target to specific tick-window evidence.

- **Seed 24** — Impostor `p-2` (ejected, CREWMATES win). The
  impostor's report claim "found p-1 body in CAFETERIA at tick 2"
  combined with "no meeting was called until tick 9 when p-3
  reported" is the structural tell crewmates correctly exploit.
  Prose rationales are tightly grounded. **Partial on Grounded:**
  the structured `subject` field in 4/6 statements is filled with
  `"p-0"` (a non-existent player ID); the prose claims are correct
  but the structured subject is corrupted. Does not break human
  readability; flagged in §9.

- **Seed 26** — Impostor `p-4` (ejected, CREWMATES win). Three-way
  alibi network (p-2 in STORAGE, p-3 in ENGINEERING, mutual
  witnessing at tick 7). All `subject` fields populated with real
  player ids. Ballot rationales correctly identify "p-4 found body
  at tick 2 but never called a meeting" as the decisive tell.

- **Seed 49** — Impostor `p-4` (ejected, CREWMATES win). Same body-
  not-reported tell. **Partial on Grounded:** impostor `p-4`'s
  report alibi claim uses `"subject": "p-self"` rather than `"p-4"` —
  a Task-3.18 template artifact where the literal token `self`
  appears to escape the post-3.18 normalization when emitted as
  `p-self`. Prose remains coherent; flagged in §9.

Overall: 4/4 = 100% ≥ 80% threshold; sample size 4 ≥ 3 floor.
**Pass.**

## 9. Observations

Two non-blocking data-artifact issues surfaced in the sampled
transcripts and merit a Phase-4-side hygiene investigation:

(a) **`subject: "p-0"` in seed 24 statements.** All four
statements emitted by the two non-reporting speakers (`p-2`, `p-4`)
carry `subject: "p-0"` in their structured alibi claims, even though
`p-0` is not a player in this game. The reporter (`p-3`) emits the
correct `subject: "p-3"`. The prose `rationale_text` and free-text
fields are unaffected. Hypothesis: a prompt-template placeholder
defaulting to `p-0` when the speaker's own id is not threaded through
the statement prompt context, or the model substituting `p-0` from a
few-shot example.

(b) **`subject: "p-self"` in seed 49 impostor report.** Task 3.18
introduced impostor `subject: "self"` normalization, but in seed 49
the model emits the literal string `"p-self"` (note the `p-` prefix),
which the post-3.18 rewrite does not match. Worth verifying the
normalizer pattern (likely a string-equality check on `"self"` that
should be a substring or regex match).

Neither issue affects merge-criterion outcomes — votes correctly
ejected the impostor in all 4 sampled games, and prose readability
is unaffected — but both should be tracked because Task 3.11's
contradiction detection depends on `subject` matching across
speakers, and a `subject: "p-0"` claim cannot participate in
contradiction analysis with any other speaker's claims. Recommend a
small Phase-4-prelude task to (i) audit the impostor and crewmate
statement-prompt templates for `subject` field handling and
(ii) extend the post-3.18 normalizer to match `p-self`.

## 10. Verdict justification

The 50-game tournament completed end-to-end on the live Anthropic
provider with zero crashes (§3), an impostor win rate within the
balance band (§5), and total spend an order of magnitude below the
$0.30/game target (§4). All 1674 audit-log packets passed the leak
test (§6). The 4 games that fired meetings produced fully-populated
replay records with transcripts, ballots, prompt versions, and per-
call cost metadata that reconstructs the helper-computed game cost
exactly (§7). Transcript readability passes at 100% of sampled games
(§8); two minor structured-field artifacts (§9) do not affect the
rubric. Phase 3 merges criteria are met; Phase 4 may begin.

---

**Required closing fields:**

- **Report path:** `/Users/danielkeinan/projects/AiLibi/audits/audit-2026-05-26-0325-pre-phase-4-real-provider-eval.md`
- **Verdict:** Phase 3 complete — Phase 4 may begin.
- **Per-game mean cost:** $0.017719
- **Decisive split:** CREWMATES=62.00% / IMPOSTORS=38.00%
- **Total API spend for this eval:** $0.885948 USD
