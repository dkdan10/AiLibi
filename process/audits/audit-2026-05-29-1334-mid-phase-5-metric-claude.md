# Mid-Phase-5 Metric Correctness Audit — claude

## 1. Verdict

**Mid-phase metric audit passes — proceed to fan out 5.7 + 5.8.**

Every public `compute_*` returns the value its docstring and DESIGN.md §11.3
definition claim on independently-constructed fixtures whose answer is known by
inspection. The Task 5.6 loader populates `roles` completely from the in-memory
seeded result, reconciles per-seed cost against `compute_cost_usd`, maps replay
records 1:1 into the report, and reduces cleanly to `BalanceReport`. The emitted
JSON validates against the 5.1 schema, round-trips identically, rejects a bumped
`format_version` and an extra field, and the wrapper packs each metric without
recomputation. Partial-replay inputs are handled (or fail loud) exactly where
the contract requires. One **informational** (non-blocking) note in Class E.

## 2. Environment

- **HEAD:** `91e0595` (Merge PR #80; Task 5.6 + per-seed meeting-abort recovery merged).
- **`bash scripts/check.sh`:** `All checks passed!` — task-doc validation passed
  (81 tasks / 81 prompts); **964 passed, 12 skipped**; frontend build OK.
- **Audit window** (`ddc34b3~1..HEAD`): 5.1 schema (`d3f1f5c`/`b898caa`/`0d8af03`),
  5.2 vote (`0a97ce2`), 5.3 calibration (`8de437a`), 5.4 alibi (`06cdd82`),
  5.5 cost (`305da87`), 5.6 integration (`c9e2e56`) + meeting-abort recovery
  (`e8d1f18`). 5.6 is **merged**; loader + `TournamentEvalReport` + JSON emit present.

```
91e0595 Merge pull request #80 from dkdan10/claude/zen-archimedes-ME5g0
e8d1f18 task 5.6: recover partial game on per-seed meeting abort
c9e2e56 task 5.6: tournament metric integration
5a48c61 expand task 5.6
2d2b1ad Merge pull request #77 from dkdan10/phase-5-cost-dashboard
3a0aab2 Merge pull request #79 from dkdan10/phase-5-alibi-fabrication-rate-metric
```

All evidence below was produced on the FAKE provider (zero API spend) via
throwaway `/tmp` fixtures and one 6-seed fake-provider tournament. No source,
test, fixture, or config file was modified.

---

## 3. Class A — Metric vs. docstring correctness

Independent fixtures were built by instantiating the schema models directly
(`/tmp/audit_classA.py`), never reusing the shipped test fixtures. Every probe
returned the value known by inspection.

### vote_correctness — No findings

| Probe | Fixture | Expected | Observed |
|---|---|---|---|
| A1 unfounded impostor eject | eject impostor `p-2`, empty contradictions, no observations, bare ballot | imp_ej=1, evidence=0, rate=0.0 | imp_ej=1, evidence=0, rate=0.0 ✓ |
| A2 zero impostor ejections | eject crewmate `p-3` only | imp_ej=0, crew_ej=1, **rate=None** | imp_ej=0, crew_ej=1, rate=None ✓ |
| A3 naming contradiction | `ContradictionRef.subjects=("p-2",)`, ejected=`p-2` | evidence=1, rate=1.0 | evidence=1, rate=1.0 ✓ |
| A3b contradiction names other | subjects=`("p-3",)`, ejected=`p-2` | evidence=0 | evidence=0 ✓ |
| A4 kill-witness in window | found_body@R/t5 + saw `p-2`@R/t7 (Δ2 ≤ 5) | evidence=1 | evidence=1 ✓ |
| A4b tick window exceeded | saw `p-2`@R/t11 (Δ6 > 5) | evidence=0 | evidence=0 ✓ |
| A4c different room | saw `p-2`@Q (body@R) | evidence=0 | evidence=0 ✓ |
| A5 bare accusation | `AccusationClaim against="p-2"` only | evidence=0 | evidence=0 ✓ |
| A6 EJECTED w/ `ejected_player_id=None` | malformed EJECTED meeting | total_ej=0, no crash | total_ej=0, no crash ✓ |

The high-risk circularity guard holds: an impostor ejection with no contradiction
and no kill-witness scores `evidence_backed=0` (A1) — the metric is *not* the
impostor-ejection rate. The bucket invariant
(`impostor_ejections + crewmate_ejections == total_ejections`) is enforced by the
post-init validator (`eval/vote_correctness.py:136`), `rate` is `None` not `0.0`
on zero impostor ejections, and the "real evidence" predicate matches the docstring
exactly — `ContradictionRef.subjects` membership or a `FoundBody`+`SawPlayer`
co-location, with a bare accusation excluded (A5).

### accusation_calibration — No findings

| Probe | Expected | Observed |
|---|---|---|
| AC1 `confidence==1.0` lands closed top bin | count=1, hits=1, rate=1.0 | count=1, hits=1, rate=1.0 ✓ |
| AC2 two separate curves | claim_total=1, ballot_total=1 | claim_total=1, ballot_total=1 ✓ |
| AC3 `"SKIP"` ballot excluded | bin0 count=1 (only the real ballot) | 1 ✓ |
| AC4 ECE uses empirical `mean_confidence` | claim_ece=0.0 (conf 1.0, hit) | 0.0 ✓ |
| AC4b ECE non-trivial | ballot_ece=\|1.0−0.05\|=0.95 | 0.95 ✓ |
| AC5 target absent from `roles` | **fail loud (ValueError)** | raises ValueError ✓ |
| AC6 zero accusations | both ece = None | None / None ✓ |

`min(int(c*n_bins), n_bins-1)` puts `1.0` in the closed top bin
(`eval/accusation_calibration.py:254`); claim and ballot curves are never pooled;
`"SKIP"` is excluded *before* the role lookup (`:229`); a missing target raises
via `_is_impostor` (`:171`); ECE is the count-weighted mean over populated bins of
`abs(rate − mean_confidence)` and `None` over zero samples.

### alibi_fabrication — No findings

Shipped join rule is **subject-membership** (confirmed at
`eval/alibi_fabrication.py:223-234`; the alternative event-id reconstruction was
explicitly rejected in the module docstring).

| Probe | Expected | Observed |
|---|---|---|
| AF1 impostor self-alibi, no contradiction | total=1, survived=1, rate=1.0 | 1 / 1 / 1.0 ✓ |
| AF2 self-alibi + `alibi_conflict` naming subject | total=1, survived=0 | 1 / 0 ✓ |
| AF3 crewmate author alibis *about* impostor | total=0 (author-role, not subject) | 0 ✓ |
| AF3b impostor author alibis *about* crewmate | total=1 (author-role) | 1 ✓ |
| AF4 same tuple in report + statement | deduped → total=1 | 1 ✓ |
| AF5 cross-author false positive | documented: counted as caught (survived=0) | total=1, survived=0 ✓ |

"Impostor alibi" is keyed by AUTHOR role (`ReportDocument.agent_id` /
`Statement.speaker`), not `AlibiClaim.subject` (AF3/AF3b confirm). The per-meeting
value-tuple dedup collapses a report+statement restatement to one (AF4). AF5
reproduces the documented cross-author false positive (an impostor's uninvolved
alibi about `S` is marked caught when any contradiction names `S`) — this is the
module's own stated, conservative (survival-undercounting) failure mode, not a
defect.

### cost_dashboard — No findings

| Probe | Expected | Observed |
|---|---|---|
| CD1 no double-count of failed-call cost | total=1.0 (not 1.4) given a 0.4 `failed_calls` row | 1.0 ✓ |
| CD2 per-version totals OVERLAP | 2 games × 1.0, both run meeting+trigger → each version total=2.0, sum=4.0 ≠ tournament 2.0 | meeting=2.0, trigger=2.0, sum=4.0, total=2.0 ✓ |
| CD3 zero-game report | total=0.0, mean=0.0 (no NaN/ZeroDivision) | 0.0 / 0.0 ✓ |
| CD4 empty `prompt_versions` | cost counts toward total, 0 version keys | total=1.0, keys=0 ✓ |

`total_cost_usd` is summed straight from `GameCostSummary.total_cost_usd`;
`game.failed_calls` cost is intentionally not re-added
(`eval/cost_dashboard.py:142`). Per-version totals overlap and do not partition.
`mean_cost_per_game` is guarded to `0.0` on zero games (`:160`).

---

## 4. Class B — Loader fidelity & roles ground truth — No findings

A 6-seed fake-provider tournament (seeds 3–8, 5 players / 2 impostors,
max_ticks 300; `/tmp/audit_BCDE.py`) was assembled via `run_tournament_eval`:

- **Roles real & complete (all 6 games):** `roles` non-empty; key set equals the
  game's player set (cross-checked against `seed_initial_state(...).players`);
  exactly `num_impostors == 2` entries are `"IMPOSTOR"`; every value is
  `"CREWMATE"`/`"IMPOSTOR"`. `_seeded_roles` (the abort fallback) yields the
  identical assignment to the live game for the same seed+config
  (`seeded==live=True` for every seed). Roles come from `final_state.players`
  (`eval/balance_eval.py:263-266`), never the replay JSONL.
- **Cost reconciles (all 6 games):** `GameReport.cost.total_cost_usd ==
  compute_cost_usd(replay-seed-{seed}.jsonl)` and `sum(by_model.values()) ==
  total_cost_usd` to 1e-9. No double-count.
- **Record→report mapping (seed 3, meeting-bearing):** `MeetingReplayEntry` →
  `MeetingReport` is exact on `meeting_id`/`tick`/`outcome`/`ejected_player_id`/
  `transcript`/`ballots`/`contradictions`/`llm_calls`; the `GameEndReplayEntry`
  populates `winner`/`reason`/`final_tick` exactly.
- **`run_balance_eval` reduces correctly:** buckets `crew=4`, `imp=2`, `tb=0`
  match the `TournamentReport` winners and sum to `games=6`; the sum-to-games
  invariant holds.

## 5. Class C — Partial-replay robustness — No findings

Hand-written degenerate replays driven through `_game_report_from_replay`
(`/tmp/audit_classC.py`):

- **No `game_over` row:** `winner=None`, `final_tick=None`, `reason` falls back to
  the in-memory outcome, no raise. ✓
- **Failed-call-only replay (5.6 abort path):** `failed_calls` populated, cost
  counted **once** (`total_cost_usd == compute_cost_usd == 0.03`), and
  `compute_cost_dashboard` reports 0.03 (not 0.06). ✓
- **Doubled/corrupted file:** `read_all_entries` raises `CorruptedFileError`
  (fail-loud) via the loader. ✓
- **Empty `roles` for a finished game:** fail-loud `ValueError`
  (`eval/balance_eval.py:390`). ✓
- **Missing replay file (zero-tick):** treated as empty log — 0 meetings,
  cost 0.0, synthetic `game_id` — no raise. ✓
- **EJECTED with `ejected_player_id=None`:** vote_correctness skips it
  (Class A, A6) — no `roles[None]` crash. ✓
- **Empty `prompt_versions`:** cost_dashboard handles it (Class A, CD4). ✓
- Games with no meetings yield empty `meetings`/`failed_calls` and contribute
  zero to every metric (seeds 6–8 in the live run). ✓

## 6. Class D — Schema integrity of the emitted artifact — No findings

Against the emitted `/tmp/audit_tourney/tournament-eval-report.json`:

- **D1** Validates against `TournamentEvalReport`; round-trip
  `model_validate_json(model_dump_json(x)) == x` is identity (the embedded
  `TournamentReport` re-validates too).
- **D2** `format_version == CURRENT_FORMAT_VERSION == 1`; injecting `version+1`
  is **rejected** by the field validator.
- **D3** `roles`, `cost`, and `prompt_versions` are populated for meeting-bearing
  games; injecting a `bogus` field is **rejected** (`extra="forbid"`), so the
  round-trip would catch any schema-bypassing emit.
- **D4** `build_tournament_eval_report` carries all four metric blocks + the
  underlying report; each block equals an independent recomputation
  (`compute_*`), confirming it packs results without re-deriving them.

## 7. Class E — Prompt-version provenance — 1 informational finding (non-blocking)

- `GameReport.prompt_versions` is populated from `MeetingReplayEntry.prompt_versions`
  and reflects the templates in play (e.g. `{accusation_round: accusation_round.v2,
  crewmate_report: crewmate_report.v1, impostor_report: impostor_report_v1,
  vote_ballot: vote_ballot/v1}` for every meeting-bearing seed). ✓
- `cost_dashboard.per_prompt_version` keys by the real `(template_name, version)`
  pairs. ✓
- A game with no meetings has empty `prompt_versions` (documented) and does not
  corrupt the roll-up. ✓

### E-1 (informational) — cost_dashboard's "single-run collapse → per-version total equals the tournament total" is an overstated invariant

`eval/cost_dashboard.py:34-43` (module docstring, "Single-run collapse" decision)
and the `CostDashboard` class docstring assert that within one run *"every
`(template, version)` key appears in every game and each per-version
`total_cost_usd` equals the tournament total."* That holds only when **every game
ran a meeting**. A game with spend but **empty `prompt_versions`** — the
canonical case being the **5.6 meeting-abort recovery path**, where a meeting
crashes before completing so no `MeetingReplayEntry` (and thus no
`prompt_versions`) is written, yet a `FailedCallReplayEntry` carries real spend —
contributes its cost to the tournament total but to **no** per-version key.

Reproduction (`/tmp/audit_costnote.py`): a 2-game report — game A (meeting,
template `meeting/v1`, cost 1.0) + game B (crashed meeting, empty
`prompt_versions`, failed-call cost 0.5):

```
tournament total_cost_usd = 1.5
  per-version meeting/v1: total=1.0 games=1
CONTRADICTION: per-version total 1.0 != tournament total 1.5
```

The live 6-seed run shows the same shape less starkly: `per_prompt_version`
`game_count == 3` (the meeting-bearing seeds) against 6 total games; the equality
is only masked here because the fake provider reports zero cost.

**Why this is informational, not blocking:** the per-version `total_cost_usd`
value is *correct* — it is exactly the sum of game cost over games that ran the
template — so no downstream metric receives a wrong number, and Task 5.8's
cross-run delta (matching keys across two dashboards) is unaffected. Only the
docstring's stated equality invariant is idealized. It is worth recording because
the 5.8 close-gate narrative ("a prompt change shows a cost delta") implicitly
leans on per-version ≈ tournament cost, which the crashed-meeting case breaks; a
one-line docstring qualification (or, optionally, surfacing an "unattributed
spend" residual) would make the roll-up self-describing. No repair task is
required before fan-out.

---

## 8. Repair task proposals

No blocking findings → no repair task is required before 5.7/5.8 dispatch.

Optional (documentation-only, may be folded into 5.7's dashboard contract):
tighten the `eval/cost_dashboard.py` module + `CostDashboard` docstrings so the
"single-run collapse" claim reads as "each per-version total equals the tournament
total *when every game ran a meeting*; games with spend but empty
`prompt_versions` (e.g. a crashed meeting recovered by the 5.6 abort path)
contribute to the total but to no version key." No code change to the metric.

## 9. Required closing fields

- **Report path:** `audits/audit-2026-05-29-1334-mid-phase-5-metric-claude.md`
- **Verdict:** Mid-phase metric audit passes — proceed to fan out 5.7 + 5.8.
- **Findings count by class:**
  - Class A (metric vs. docstring): 0
  - Class B (loader fidelity & roles): 0
  - Class C (partial-replay robustness): 0
  - Class D (schema integrity): 0
  - Class E (prompt-version provenance): 1 informational (non-blocking)
- **Total findings:** 1 (0 blocking, 1 informational)
