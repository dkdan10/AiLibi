# Mid-Phase-5 Metric Correctness Audit — Codex — 2026-05-29 13:34

## 1. Verdict

**Mid-phase metric audit passes — proceed to fan out 5.7 + 5.8.**

Zero blocking findings. The four metric modules compute the values their docstrings and DESIGN.md §11.3 claim on independently constructed fixtures; the Task 5.6 loader preserves roles, costs, replay records, partial runs, and prompt-version provenance; the emitted JSON validates and round-trips through the frozen schema.

## 2. Environment

- **HEAD:** `91e0595`
- **`bash scripts/check.sh`:** passed locally; pytest reported `964 passed, 12 skipped in 9.05s`, and frontend `tsc:check` + `vite build` completed.
- **No real provider calls:** all tournament runs forced or defaulted to the fake provider; observed total cost was `0.0000` on the real fake-provider tournament.
- **`git log --oneline -6`:**
  ```text
  91e0595 Merge pull request #80 from dkdan10/claude/zen-archimedes-ME5g0
  e8d1f18 task 5.6: recover partial game on per-seed meeting abort
  c9e2e56 task 5.6: tournament metric integration
  5a48c61 expand task 5.6
  2d2b1ad Merge pull request #77 from dkdan10/phase-5-cost-dashboard
  3a0aab2 Merge pull request #79 from dkdan10/phase-5-alibi-fabrication-rate-metric
  ```
- **Audit window:** `git log --oneline --name-status ddc34b3~1..HEAD` enumerated Task 5.1 through Task 5.6 plus the 5.6 partial-abort follow-up. Task 5.6 is merged: `eval/balance_eval.py`, `eval/meeting_quality.py`, `scripts/run_tournament.py`, and `tests/eval/test_tournament_report.py` are present.

## 3. Class A — Metric vs. Docstring Correctness Findings

### vote_correctness

No findings in this class. Independent fixtures built direct `TournamentReport` models and matched the module contract at `eval/vote_correctness.py:166`, `eval/vote_correctness.py:191`, `eval/vote_correctness.py:202`, and `eval/vote_correctness.py:222`.

Evidence:
- No-evidence impostor ejection returned `total_ejections=1`, `impostor_ejections=1`, `evidence_backed_impostor_ejections=0`, `vote_correctness_rate=0.0`.
- Zero impostor ejections returned `crewmate_ejections=1`, `impostor_ejections=0`, `vote_correctness_rate=None`.
- A contradiction naming the ejected impostor returned evidence-backed `1/1`.
- A found-body plus same-room sighting within the 5-tick window returned evidence-backed `1/1`.
- Accusation/ballot-only ejection returned evidence-backed `0/1`.
- Malformed `EJECTED` with `ejected_player_id=None` was skipped with `total_ejections=0`.

### accusation_calibration

No findings in this class. Independent fixtures matched the separate-curve, fail-loud, boundary, and ECE behavior implemented at `eval/accusation_calibration.py:153`, `eval/accusation_calibration.py:201`, `eval/accusation_calibration.py:218`, `eval/accusation_calibration.py:241`, and `eval/accusation_calibration.py:287`.

Evidence:
- With `n_bins=2`, a claim at confidence `1.0` landed in the closed top bin.
- `AccusationClaim` and `VoteBallot` samples were reported separately: claim total `4`, ballot total `2`; one `SKIP` ballot was excluded before role lookup.
- Expected calibration error used empirical mean confidence: the constructed claim bins produced `claim_ece=0.18749999999999997`.
- A missing target raised fail-loud: `ValueError: malformed report: accusation-claim target 'ghost' ... is absent from the post-game role ground truth`.
- A no-accusations report returned `accusation_claim_ece=None`.

### alibi_fabrication

No findings in this class. The shipped rule is subject-membership, implemented at `eval/alibi_fabrication.py:150`, `eval/alibi_fabrication.py:181`, `eval/alibi_fabrication.py:197`, and `eval/alibi_fabrication.py:223`; independent fixtures matched the documented accepted failure mode.

Evidence:
- Cross-author case where two crewmates conflicted about subject `imp`, while the impostor also had an alibi about `imp`, returned `total_impostor_alibis=1`, `survived=0`, `survival_rate=0.0`. This is the documented subject-membership false positive, not a blocking defect.
- Author role, not subject role, drove the denominator: an impostor-authored alibi about a crewmate counted, while a crewmate-authored alibi about the impostor did not; result `total_impostor_alibis=1`, `survived=1`.
- The same alibi tuple restated in a report and statement counted once; result `total_impostor_alibis=1`, `survived=1`.

### cost_dashboard

No findings in this class. Independent fixtures matched the authoritative-cost and overlapping-prompt-version behavior at `eval/cost_dashboard.py:119`, `eval/cost_dashboard.py:137`, `eval/cost_dashboard.py:152`, and `eval/cost_dashboard.py:157`.

Evidence:
- A game with `GameCostSummary.total_cost_usd=0.05` and a `failed_calls` row costing `0.02` produced dashboard total `0.05`, not `0.07`.
- Per-version totals overlapped: two games costing `0.05` and `0.20` produced tournament total `0.25`, while summing three per-version rows produced `0.50`.
- Zero-game report returned `game_count=0`, `total_cost_usd=0.0`, `mean_cost_per_game=0.0`, and empty prompt/model breakdowns.

## 4. Class B — Loader Fidelity & Roles Ground Truth Findings

No findings in this class. I ran:

```bash
env AILIBI_LLM_PROVIDER=fake uv run python scripts/run_tournament.py --num-games 3 --start-seed 3 --num-players 5 --num-impostors 2 --max-ticks 300 --output-dir /private/tmp/ailibi-phase5-audit --force
```

Observed:
```text
games:                3
crew_wins:            3
impostor_wins:        0
tick_budget_reached:  0
total_cost_usd:       0.0000
mean_cost_per_game:   0.0000
report:               /private/tmp/ailibi-phase5-audit/tournament-eval-report.json
```

For seeds `3`, `4`, and `5`, every `GameReport` had non-empty roles, role keys equal to `seed_initial_state(...).players`, exactly `2` impostors, and `_seeded_roles(...)` matched the report roles. This is consistent with the live-result role capture at `eval/balance_eval.py:261` and abort-path seeded fallback at `eval/balance_eval.py:242` and `eval/balance_eval.py:313`.

For every game, `cost.total_cost_usd == compute_cost_usd(replay-seed-{seed}.jsonl)`, token totals and `by_model` matched meeting `llm_calls` plus `failed_calls`, and the first `MeetingReplayEntry` mapped 1:1 to `MeetingReport` fields. The relevant loader paths are `eval/balance_eval.py:399`, `eval/balance_eval.py:411`, `eval/balance_eval.py:423`, `eval/balance_eval.py:438`, and `eval/balance_eval.py:461`; the canonical cost reducer is `orchestrator/replay.py:432`.

`run_balance_eval` remains a thin reducer over `run_tournament_eval` at `eval/balance_eval.py:279`; running the same seeds into a separate temp directory returned `BalanceReport(games=3, crew_wins=3, impostor_wins=0, tick_budget_reached=0, seeds_used=(3, 4, 5))`, matching the buckets reduced from the emitted `TournamentReport`.

## 5. Class C — Partial-Replay Robustness Findings

No findings in this class.

Evidence:
- No-meeting tick-budget run via a wait-agent fixture returned one `GameReport` with `winner=None`, `final_tick=None`, `reason="TICK_BUDGET_REACHED"`, `meetings=()`, non-empty roles, and empty metric outputs (`vote_total_ejections=0`, `alibi_total=0`, `cost_total=0.0`). This matches the partial path at `eval/balance_eval.py:382` and `eval/balance_eval.py:426`.
- Synthetic partial replay with no `game_over` and one `FailedCallReplayEntry(cost_usd=0.07)` loaded as `winner=None`, `final_tick=None`, `failed_calls=1`, `cost.total_cost_usd=0.07`, and `compute_cost_usd=0.07`.
- Meeting-abort recovery through a stubbed `HeadlessGame` produced a partial report with `winner=None`, `final_tick=None`, `reason` containing `aborted`, non-empty roles, one impostor, `failed_calls=1`, and both per-game cost and dashboard total `0.02`. The abort recovery branch is at `eval/balance_eval.py:220`.
- A doubled/corrupted replay raised `ReplayLog.CorruptedFileError` with `Duplicate tick 0 ...`, confirming `read_all_entries` still fails loud via `orchestrator/replay.py:461` and `orchestrator/replay.py:491`.
- `EJECTED` with `ejected_player_id=None` was independently verified under Class A to skip rather than crash.
- Empty `prompt_versions` on a no-meeting game remained `{}` and did not corrupt the cost dashboard.

## 6. Class D — Schema Integrity Findings

No findings in this class.

Evidence:
- The emitted `/private/tmp/ailibi-phase5-audit/tournament-eval-report.json` loaded with `TournamentEvalReport.model_validate_json(...)`.
- `TournamentEvalReport.model_validate_json(eval_report.model_dump_json()) == eval_report` returned `True`; the embedded `TournamentReport` validated back to itself.
- `format_version == CURRENT_FORMAT_VERSION == 1`; bumping the embedded report version to `2` raised `1 validation error for TournamentReport`, as enforced by `eval/report_schema.py:245`.
- Adding an unexpected top-level field to the wrapper raised `1 validation error for TournamentEvalReport`, consistent with `extra="forbid"` at `eval/meeting_quality.py:61`.
- `scripts/run_tournament.py` validates before writing (`scripts/run_tournament.py:143`) and writes the report after building all four metric blocks (`scripts/run_tournament.py:168` and `scripts/run_tournament.py:183`).
- `build_tournament_eval_report` calls the four public metric functions and performs no local metric math (`eval/meeting_quality.py:70` through `eval/meeting_quality.py:85`).

No promised integration field was empty where data existed: all three meeting-bearing games had roles, cost, meetings, and prompt versions populated.

## 7. Class E — Prompt-Version Provenance Findings

No findings in this class.

Evidence:
- Every meeting-bearing real-run game carried the same four prompt-version keys:
  `crewmate_report=crewmate_report.v1`, `impostor_report=impostor_report_v1`, `accusation_round=accusation_round.v2`, `vote_ballot=vote_ballot/v1`.
- The loader collapses meeting prompt versions to game granularity at `eval/balance_eval.py:416`.
- The cost dashboard keyed real `(template_name, version)` pairs and each key had `game_count=3`, covering every game in the single-run report.
- The no-meeting partial game had `prompt_versions={}` and contributed no per-version row, while leaving total cost well-defined.

## 8. Repair Task Proposals

None. No blocking findings were observed.

## 9. Required Closing Fields

- **Report path:** `audits/audit-2026-05-29-1334-mid-phase-5-metric-codex.md`
- **Verdict:** Mid-phase metric audit passes — proceed to fan out 5.7 + 5.8.
- **Findings count by class:**
  - Class A — Metric vs. docstring correctness: 0
  - Class B — Loader fidelity & roles ground truth: 0
  - Class C — Partial-replay robustness: 0
  - Class D — Schema integrity: 0
  - Class E — Prompt-version provenance: 0
- **Total findings:** 0
