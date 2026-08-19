# Code review — eval/ + scripts/ (label: eval-and-scripts)

Scope: `eval/` (25 modules, 20,938 lines), the named `scripts/` (13 files, 8,497 lines incl. two large bash scripts), `tests/eval` + `tests/scripts` (47 files, 32,625 lines, 1,258 tests). Read-only; branch `main` @ b809b19c. Machine load during timings: 4.4–7.4 (10-core, other reviewers concurrent). All commands run via `uv run` in the repo venv. Nothing edited.

Labels: **[VERIFIED]** = I ran/observed it; **[JUDGMENT]** = assessment from reading.

---

## 1. Executive read (10 lines)

1. The area is functionally sound: **1,257 tests pass, 1 skipped, in 140 s** (`uv run pytest tests/eval tests/scripts`); both committed sample sets reconstruct byte-identically (4p1i 0.18 s, 9p2i 0.71 s bare walk); every one of 18 pure analyzers handles empty/undefined denominators with the `None`-not-`0.0` sentinel [VERIFIED].
2. The best design in the area is `eval/replay_walk.py`: one generator-based engine walk with typed per-tick events, per-consumer check profiles, and a negative fixture per profile — genuinely good, and it made six eval modules thinner.
3. But the walk consolidation stopped at the eval boundary: `api/replay_loader.py`, `eval/off_menu.py`, three `training/` modules and one `audits/workflows/` script still carry their own advance/apply loops; `_meeting_result_from_entry` exists 4×, `_ACTION_ADAPTER` 8× outside tests, seed-globbing ~15×, Wilson interval 3× [VERIFIED].
4. Prose dominates: module docstrings of 100–350 lines restate phase history (report_schema.py is 71 % prose; meeting_quality's docstring is a 170-line changelog), and **1,513 lines of Pydantic `model_validator`s** recompute derived fields the same module just computed (653 lines in deduction_metrics alone) [VERIFIED].
5. Doc/code/data drift on a headline metric: `vote_correctness_rate` is documented as "structurally pinned to 1.0; any value below 1.0 is a detector/recording bug", the README sells it as the circularity guard, and the committed 9p2i report reads **0.923** with 6 zero-flag impostor ejections [VERIFIED]. It survives only "to avoid schema churn".
6. The metric layer regex-scrapes rendered LLM prompt text (suspicion graph, §4.6 max line, voter id from an `error_message`) — acknowledged as FROZEN/fragile — and the same regexes are duplicated in three modules despite a module named as their "single shared home" [VERIFIED].
7. Consequence of (6): the committed `tournament-eval-report.json` (28 MB) is **95 % raw LLM prompt/response text** re-embedded from the replays; metrics are <1 % of it; 33 historical versions = 546 MB of uncompressed blobs in `.git` [VERIFIED].
8. `scripts/refresh_samples.sh` is 917 lines of bash implementing a worker pool, an mkdir mutex with dead-owner detection, per-seed retry and atomic moves — the riskiest logic in the area — and that path has **zero automated coverage** because `AILIBI_LLM_PROVIDER=fake` is deliberately remapped to `anthropic`; its 59 tests pin `--dry-run` echo strings [VERIFIED].
9. Tests pin implementation shape in places: `run_tournament.main` keeps three identical `run_tournament_eval(...)` call branches solely because test spies have keyword-only signatures without `agent_factory`; report-schema tests assert field annotations, module-namespace identity and `CURRENT_FORMAT_VERSION == 2`; 30/47 test files pin golden numbers on committed bytes [VERIFIED].
10. `check.sh` is cheap on the static side (~6 s warm) and dominated by a single-process `pytest` over 4,644 default-tier tests; `set -e` stops at the first failing gate; `slow`/`perf` markers are registered but unused [VERIFIED].

---

## 2. Findings, ranked by severity

### P1

**F1 — refresh_samples.sh: 300 lines of untested bash concurrency on the money path.** `scripts/refresh_samples.sh:620-830` [VERIFIED]
- What: a job queue (`.next_idx` claim counter), an mkdir mutex with PID-based dead-owner detection (`_acquire_lock`), per-seed retry with backoff, atomic `mv` staging, `MANIFEST.md` read-modify-write under the lock, worker `wait` aggregation, then a `.failed` sentinel check. It also shells out to `audits/workflows/extract_gameplay_facts.py` and `experiments/lab/rubric_score.py` (audit- and lab-tier code) as a hard step of the production refresh (`refresh_samples.sh:870-916`).
- Why it matters: this is the only path that re-records the canonical baselines (multi-hour, real spend). A lock bug or a mis-joined worker silently canonicalizes a mixed set (the script's own comments describe three prior review fixes for exactly this).
- Evidence: `AILIBI_LLM_PROVIDER=fake` → `PROVIDER="anthropic"` (`refresh_samples.sh:262`), so no hermetic run of the worker path is possible; `tests/scripts/test_refresh_samples.py` (915 lines, 59 tests) has no test touching `run_worker`/`_acquire_lock`/`record_one_seed`; grep for `worker|lock` in the test file hits only dry-run echo assertions (`assert "[dry-run] seed workers: 2 parallel" in proc.stdout`).
- Severity P1 (serious maintainability + un-verifiable robustness); confidence high.
- Fix: move orchestration to Python (`scripts/refresh_samples.py`) using `concurrent.futures`, a real lock, and `subprocess.run` per seed; keep a thin `.sh` shim; allow `fake` provider for hermetic worker-path tests. Drop the audits/experiments dependency or promote `rubric_score` into `eval/`.

**F2 — `vote_correctness_rate`: docstring, README and committed data disagree.** `eval/vote_correctness.py:11-31`, README.md:190, `replays/samples/9p2i/tournament-eval-report.json` [VERIFIED]
- Docstring: "structurally pinned to 1.0 … any value below 1.0 on a recorded set means an impostor ejection happened WITHOUT its own triggering evidence — a detector/recording bug to chase". README: "vote correctness — were ejections evidence-backed, or coin-flips? (guards against circular … scoring)".
- Data: committed 9p2i report → `impostor_ejections=78, evidence_backed=72, vote_correctness_rate=0.923`. My probe (`scratchpad/work/eval-and-scripts/probe_vc.py`) lists the six: seeds 4/17/18/22/29/40, each with `contradictions=[]` and 2–4 eject ballots — i.e. legitimate zero-flag convictions, which Task 16.10 even instruments as a named channel. The sentinel semantics are dead, the README description is aspirational, and the field is kept "because removing it would churn the schema".
- Why it matters: a metrics project whose headline `vote_correctness_rate` has no coherent interpretation on its own baseline; a reader following the docstring would file a bug.
- Severity P1 (doc/data correctness on a shipped metric), confidence high. Fix: either delete the field (bump `format_version`) or re-document it honestly as "share of impostor ejections carrying a naming flag or kill-witness chain" and update README.

**F3 — The eval report is a second copy of the replays; metrics scrape prompt prose.** [VERIFIED]
- `replays/samples/9p2i/tournament-eval-report.json` = 27.9 MB; `report.games[*].meetings[*].llm_calls` (with full `prompt` bodies, ~8.8 KB each) = **95 %** of bytes; transcripts 2 %; all metric blocks together <1 %. Git history: 33 blobs, 546 MB uncompressed (`git rev-list --objects` + `cat-file -s`).
- The prompt bodies are carried because analyzers regex-parse them: `eval/_suspicion_parse.py` (the §4.6 max line), `eval/meeting_quality.py:321-328` and `eval/validity.py:169-173` and `audits/workflows/extract_gameplay_facts.py:268-273` (three copies of the suspicion-graph header+row regex; validity's copy accepts one header, meeting_quality's two), plus `meeting_quality._persisted_vote_verdict_maxes` recovering the voter id from `failed_call.error_message` text. All annotated "FROZEN … rendered-prose scrape — unreliable under prompt-shape change".
- Why it matters: every prompt-template edit can silently zero a metric (non-matching rows "are silently skipped"); the report duplicates 55 MB of replay content into a JSON that is regenerated on every re-record; consumers (API `/eval/tournament-report`, frontend types) must load 28 MB to show a dashboard.
- Severity P1 (fragility + repo bloat), confidence high. Fix: persist typed per-ballot telemetry (rendered max, suspicion graph) on the replay `MeetingReplayEntry`/`VoteBallot` at record time; make the report carry `llm_calls` metadata without prompt bodies (or a replay ref); one parser module actually used by all three consumers.

**F4 — Replay-walk duplication remains outside eval; the byte-identity gate uses the heaviest walk.** [VERIFIED]
- Remaining independent advance/apply loop bodies (non-test): `api/replay_loader.py:1003-1334` (`_walk`), `eval/off_menu.py:434`, `training/rollout.py:545`, `training/anchor_study.py:562`, `training/surrogate/dataset.py:901`, `audits/workflows/extract_gameplay_facts.py:2295`. `_meeting_result_from_entry` is defined in `eval/replay_walk.py:340`, `api/replay_loader.py:2195`, `training/rollout.py:412`, `training/surrogate/dataset.py:437`. `_ACTION_ADAPTER = TypeAdapter(Action)` in 8 non-test modules (`orchestrator/boundary.py` already exports one).
- `scripts/_verify_samples.py::verify_samples` (the byte-identity check behind `verify_samples.sh` and `eval.validity.check_byte_identical_reconstruction`) calls `ReplayLoader.load_replay`, which runs `_walk(collect_visibility=True)` — the per-agent observation pipeline plus full `TickView` construction — to check hashes. Measured (`bench_verify.py`): 4p1i 0.51 s vs 0.18 s bare `walk_replay` with all hash checks; 9p2i 2.01 s vs 0.71 s. Absolute cost is small, so this is a design/duplication finding, not perf.
- Also: `eval/validity.py:138-142` inserts `scripts/` into `sys.path` at import time to reach `_verify_samples`, creating an eval→scripts→api→eval package cycle; `eval` imports the private `api.replay_loader._load_roster_config` and `orchestrator.replay._state_hash`.
- Severity P1 (maintainability; the walker exists precisely to end this), confidence high. Fix: give `api/replay_loader._walk` a `viewer` profile on `walk_replay` (its extra checks are already expressible: tick hash + post hash + truncate); move `_check_meeting_pre_hashes`+`verify_samples` into `eval/` on top of the walker; export the action adapter from one place.

**F5 — Tests pin implementation shape and force accidental complexity.** [VERIFIED]
- `scripts/run_tournament.py:1180-1230`: three near-identical `run_tournament_eval(...)` calls, with the comment "the two pre-18.7 call sites stay BYTE-IDENTICAL for their spies — the fsm-default path passes NO agent_factory kwarg". `tests/scripts/test_run_tournament.py:35-59` installs a spy with a keyword-only signature lacking `agent_factory`; passing `agent_factory=None` would `TypeError`. Production shape is dictated by test doubles.
- `tests/eval/test_report_schema.py:317-320` (`assert CURRENT_FORMAT_VERSION == 2`), `:510-548` (asserts `model_fields[...].annotation is MeetingTranscript`, `vars(module)["VoteBallot"] is meetings_schemas.VoteBallot`) — structural pins with no behavioural content.
- 30 of 47 test files in the area reference the committed `4p1i`/`9p2i` bytes; e.g. `test_deduction_metrics.py` mentions them 138 times; names like `test_committed_w2_reads_64_of_179`. Golden pins are a deliberate doctrine (Task 19.27) and do catch drift, but they mean any legitimate metric fix or re-record re-pins dozens of literals across files.
- Severity P1 for the run_tournament case (production code contorted for spies), P2 for the rest; confidence high.

### P2

**F6 — Docstring/comment sprawl restating history.** [VERIFIED] Prose share per module (docstring+comment lines / total): report_schema 71 %, `_suspicion_parse` 67 %, alibi_fabrication 58 %, cost_dashboard 58 %, prompt_regression 51 %, vote_correctness 49 %, watchability 48 %, meeting_quality 45 %, balance_eval 43 %. Module docstrings: watchability 321 lines, deduction_metrics 354, kill_craft 189, meeting_quality 170 (a per-phase changelog: "Phase 7 Wave 0 (W0.3) adds…", "Phase 10 Wave 1 repair (Task 10.9.1, PR #147 F1)…"). `report_schema.py` is 417 lines for four Pydantic classes with ~30 fields. History belongs in `audits/`; docstrings should state the current contract.

**F7 — Self-consistency validators recompute derived fields.** [VERIFIED] 1,513 lines of `@model_validator`/`@field_validator` bodies in eval (deduction_metrics 653, meeting_quality 431, deception_instruments 183, vote_correctness 146). Pattern: `WilsonRateCell` stores numerator/denominator AND rate/low/high/advisory, then a validator recomputes all four and demands exact float equality (`deduction_metrics.py:893-925`); `_validate_rate` in the same file uses `1e-12` tolerance, `ConversionReport._validate_rate` checks only range. `computed_field`s (or plain properties) would delete most of this and remove the inconsistency.

**F8 — Duplicated helpers.** [VERIFIED] `eval/validity.py::{resolve_roster_knobs, seeds_on_disk, roles_by_seed, _FLAT_DEFAULT_KNOBS}` ≡ `scripts/build_sample_report.py::{_roster_knobs, _seeds_on_disk, _roles_by_seed, _FLAT_DEFAULT_*}` (validity's docstring even says "mirrors scripts/build_sample_report.py"); replay-seed globbing in ~15 non-experiment modules (validity 5 sites, kill_craft 3, `_verify_samples`, `_manifest_writer.discover_seeds`, `api.replay_loader._replay_paths`, `verify_ml_evidence._seed_of`, …); `_wilson_interval` verbatim in `deduction_metrics.py:852` and `deception_instruments.py:194` plus `paired_stats.wilson_interval`; `RareEventCell` vs `WilsonRateCell` (same concept, same `_WILSON_Z`/`_RARE_EVENT_ADVISORY_MAX_NUMERATOR` constants copied); `_FrozenModel` defined 3×. There is no `ReplaySet` abstraction (dir + roster + seeds + roles) although every CLI needs one.

**F9 — Layering / placement smells.** [VERIFIED] `eval/determinism_test.py` and `eval/leak_test.py` are pytest modules (import `pytest`, `tests._helpers`) inside the production `eval/` package and are collected by the bare `pytest` run; `pyproject.toml:21-24` still says training/eval "remain dev-environment surfaces until Task 19.24 promotes the scanners" although 19.24 landed (`training/bakeoff/harness.py:83` now imports `eval.leak_scan`). `import-linter` root packages exclude `eval`, `api`, `orchestrator`, so the eval↔api cycle is unguarded.

**F10 — CLI ergonomics.** [VERIFIED] `scripts/measure_baseline.py` takes `--funnel`, `--watchability`, `--vj` as independent booleans with silent priority; `measure_baseline.py replays/samples/4p1i --funnel --vj` ran only the funnel (0.79 s) with no warning — should be one `--mode` choice or a mutually-exclusive group. Every offline eval CLI prints `agents.strategic.prompts.loader: AILIBI_PROMPT_SET is unset — falling back …` on stderr at import time (irrelevant to a byte reader; and "falling back" against a "no silent fallbacks" doctrine reads oddly). `cost_dashboard.mean_cost_per_game` returns `0.0` for zero games, breaking the area's `None`-for-undefined convention (`cost_dashboard.py:190`). Positive: bad paths give clean messages and non-zero exits (`validity_gate.py`, `measure_baseline.py`, `_verify_samples.py`, `build_sample_report.py`), `build_demo_bundle.assert_safe_out_dir` is a model of a destructive-op guard.

**F11 — Docs-as-data machinery: high line count per fact.** [VERIFIED/JUDGMENT] `scripts/check_doc_facts.py` (606 lines) + `tests/scripts/test_check_doc_facts.py` (35 tests) regex-check ~6 README/.env facts (a date, two win-rate percentages, counts, the "ladder tip" sentence, lever names) — runs in 0.15 s, so cost is maintenance not runtime; it is not in `check.sh` but a test asserts HEAD is clean, so it is effectively gated. `scripts/verify_ml_evidence.py` (2,855 lines) parses markdown report tables (`fraction_from_report`, `bonferroni_from_report`, `_displayed_drift`) and `docs/artifacts.md` as a registry; its two slowest tests take 17.5 s and 12.9 s. `scripts/_manifest_writer.py` (931 lines) maintains `MANIFEST.md` as a database that `refresh_samples.sh` re-parses with awk and `check_doc_facts` re-parses again. `build_demo_bundle.parse_featured_games` regex-parses a `.tsx` source file for `FEATURED_GAMES` (with a brace-count guard). Each is defensible alone; together they mean the project's truth lives in prose and is guarded by regexes. Generating prose from JSON (not checking prose with regex) is the cheaper direction.

**F12 — check.sh composition.** [VERIFIED] Sequential `set -euo pipefail`; static gates warm: ruff 0.09 s, format 0.06 s, lint-imports 0.12 s, validate_task_docs 0.23 s, generate_prompts --check 0.78 s, mypy 4.7 s; then one single-process `uv run pytest` (4,644 default-tier tests; this area alone 140 s; `pytest-xdist` is not installed — `-n0` errors). First failing gate hides later ones (the memory note "set -e masks later gates" is real). `slow` and `perf` markers are registered in `pyproject.toml` "for a future cut" but used 0 times.

**F13 — Watchability floors as code constants.** [JUDGMENT] `eval/watchability.py:538-855`: ~300 lines of per-baseline `SupplyFloors` literals (baseline-2 … baseline-6), including a "FROZEN HISTORICAL PIN … the baseline-2 bytes left the tree so this block CANNOT be re-measured". Measured numbers with provenance belong in a data file next to the set that produced them, not in Python source.

**F14 — Minor.** `eval/balance_eval._game_report_from_replay` parses each replay twice (`read_all_entries` + `compute_cost_usd`, which itself calls `read_all_entries`) [VERIFIED]. `report_schema.TournamentReport` roll-ups (`kill_gifted_wins`, …) are stored but "NOT cross-validated against games" by design while every other report validates such invariants — inconsistent doctrine [JUDGMENT]. `run_throughput_benchmark` shares one `agent_factory` across seeds while `run_tournament_eval` builds fresh runners per game — fine, but the docstring's "wired exactly as the production tournament path" overstates [JUDGMENT].

### What is GOOD [VERIFIED unless noted]
- `eval/replay_walk.py`: generator of typed events (`TickOpened/TickAdvanced/MeetingOpened/MeetingApplied/WalkComplete`), profile config, `on_violation` must raise; `tests/eval/test_replay_walk.py` has a positive and negative fixture per profile (tolerates partial meeting / bites tampered hash / bites doubled row / bites untallying ballots / bites forged outcome). This is the right shape.
- Analyzers are pure and total: probe of 18 analyzers on an empty `TournamentReport` and a one-game/no-meeting report — all return; `None`-for-undefined consistently (except F10's cost mean).
- Determinism holds on both committed sets (0 failures; 4p1i 0.18 s, 9p2i 0.71 s bare walk); the engine walk is cheap enough that every CLI's 1–2 walks per game are ≤3.5 s for 50 games.
- `eval/validity.py`: small typed `ValidityCheck`s, malformed inputs converted to failed checks instead of crashes, human + JSON output; `check_all_games_reach_game_over` catches a forged `game_over` label the hash chain cannot.
- `report_schema.TournamentReport`: frozen, `extra="forbid"`, `format_version` required and fail-loud both ways; leaf types imported not forked.
- Statistics are correct and stdlib-only: exact two-sided binomial McNemar (`paired_stats.exact_mcnemar_p`), Wilson score intervals, ECE with per-bin means; calibration bins clamp `confidence==1.0` correctly.
- `_manifest_writer._atomic_write_text` (mkstemp + `os.replace`); `_verify_samples` rejects seed aliases and manifest/disk mismatch; `build_demo_bundle.assert_safe_out_dir` refuses to `--emptyOutDir` the repo.
- CLI failure modes are clean (message + exit code) across the five CLIs probed.

---

## 3. Architecture / design assessment

**Well-designed.** The layered idea is right: replay JSONL (engine-owned, hash-chained) → `walk_replay` (mechanics + profiles) → typed `TournamentReport` (aggregation) → pure analyzers → CLIs. Where the code follows that shape (`replay_walk`, `validity`, `accusation_calibration`, `cost_dashboard`, `paired_stats`) it is small, testable and correct. The `None`-not-`0.0` sentinel and "no silent fallbacks" doctrine are applied consistently enough to be trusted.

**Accidental complexity.**
1. *Prose as substrate.* Metrics depend on prompt text; docs/manifests are databases; verification is regex over markdown. This is the single largest source of fragility and line count (F3, F11) and it exists because typed telemetry was never added at record time.
2. *History in code.* Docstrings, comments and constant tables (F6, F13) carry phase-by-phase narrative that already lives in `audits/` and `tasks/`. It roughly doubles reading cost and hides the actual contract.
3. *Defensive recomputation.* 1.5k lines of validators re-deriving fields the builder just set (F7). The intent (a JSON tampered by hand fails loud) could be met by `computed_field` + a single "counts partition" check per report.
4. *Missing abstractions.* No `ReplaySet` (dir/roster/seeds/roles), no shared stats/cell module, no single action adapter — hence the duplication in F4/F8.
5. *Bash as an application runtime.* F1.

**What I would refactor, in order.**
- Introduce `orchestrator/replay_set.py` (or `eval/replay_set.py`): `ReplaySet.from_dir(path)` with `roster`, `seeds`, `replay_path(seed)`, `roles_by_seed()` (cached), `manifest`. Replace the ~15 glob sites and both `roster_knobs`/`roles_by_seed` copies.
- Put `api/replay_loader._walk` on `walk_replay` with a `viewer` profile; move `_verify_samples` under `eval/` on the walker; delete the `sys.path` hack in `eval/validity.py`; add `eval`, `api`, `orchestrator` to import-linter roots with an `eval must not import api` contract (or the reverse, but pick one).
- `eval/_stats.py`: `wilson_interval`, `RateCell` (numerator, denominator, computed rate/low/high/advisory), `rate_or_none`, `_FrozenModel`; migrate deduction_metrics/deception_instruments/vote_correctness/meeting_quality onto it; drop the recompute validators.
- Record typed telemetry (`rendered_vote_max`, suspicion graph) on the replay meeting row; drop prompt bodies from `TournamentReport.llm_calls` (keep model/tokens/cost/agent/kind); bump `format_version`; delete the three regex parsers.
- Rewrite `refresh_samples.sh` in Python; keep the preflight logic; make the worker path hermetically testable under the fake provider.
- Trim module docstrings to the current contract + a one-line pointer to the audit that motivated it.

---

## 4. Test assessment

- **Volume/health:** 1,257 pass, 1 skip, 140 s wall (load 4.5–8) [VERIFIED]. Slowest: `test_verify_ml_evidence.py::test_recompute_reproduces_every_committed_verdict` 17.5 s, `::test_a_fit_corpus_record_keyed_to_other_weights_fails` 12.9 s, `test_validity_gate_cli.py::test_expected_model_flag_pins_provenance` 6.4 s, deception/off_menu corpus fixtures 3–6 s setup each. Test code (32.6k lines) is ~1.1× the code it covers.
- **Behavioural vs. structural:** `test_replay_walk.py`, `test_validity.py`, `test_accusation_calibration.py`, `test_paired_stats.py`, `test_manifest_writer.py`, `test_verify_samples.py` test behaviour with hand-built fixtures — good. `test_report_schema.py` (789 lines for 4 classes) and the run_tournament spies pin structure (F5). `test_refresh_samples.py` tests printed dry-run text and never the worker path (F1).
- **Golden pins:** the "pins to goldens" doctrine (30/47 files touch committed bytes) is honest regression protection for a byte-parity project, but pins are scattered as literals in test bodies rather than one goldens file per set, so a re-record or a legitimate metric fix means editing dozens of files. `tests/scripts/_goldens` exists for some scripts — extend that pattern to eval.
- **Gaps:** no hermetic test of refresh worker/lock/retry; no test that `measure_baseline` mode flags are exclusive; `slow`/`perf` markers unused so no way to trim the 140 s locally except by path; the perf benchmark is env-gated rather than marker-gated.
- **Good:** negative fixtures per walk profile; malformed-input → failed-check tests for the validity gate; empty-report handling is implicitly covered (my probe found no crash).

---

## 5. Recommendations (prioritized)

1. **Typed telemetry + slim report** (F3, F2): persist rendered vote max / suspicion graph on the meeting replay row; remove prompt bodies from `TournamentReport.llm_calls`; delete or honestly re-document `vote_correctness_rate`; bump `format_version` once and regenerate. Biggest fragility and repo-size win.
2. **Python-ise `refresh_samples.sh`** (F1): keep preflights, move queue/lock/retry/atomic-move to `concurrent.futures` + `subprocess`; allow the fake provider so the worker path gets tests; drop the audits/experiments shell-outs from the production refresh.
3. **Finish the walker consolidation** (F4): `api/replay_loader._walk` and `_verify_samples` on `walk_replay`; one `_ACTION_ADAPTER`; remove the `sys.path` import in `eval/validity.py`; add eval/api/orchestrator to import-linter.
4. **`ReplaySet` + `eval/_stats.py`** (F8, F7): one abstraction for dir/roster/seeds/roles, one for rate cells and Wilson; replace recompute-validators with computed fields.
5. **De-pin the spies and structural tests** (F5): give test spies `**kwargs` passthrough and collapse `run_tournament.main` to one call; delete annotation/namespace/version-literal assertions; centralize golden numbers per set in one fixture file.
6. **Prose diet** (F6, F13): cap module docstrings at the contract; move phase narrative to `audits/`; move watchability floor tables to a JSON beside each sample set with provenance fields.
7. **check.sh**: add `pytest-xdist` (`-n auto`) and run static gates first-fail-fast but report all; either use or delete the `slow`/`perf` markers; make `measure_baseline` modes mutually exclusive; silence the import-time `AILIBI_PROMPT_SET` warning for offline readers.
8. **Prefer generating prose from data over checking prose with regex** (F11): render the README provenance paragraph and MANIFEST tables from JSON, and let `check_doc_facts` shrink to a diff.

---

### Appendix — evidence commands (scratch: `/private/tmp/claude-501/-Users-danielkeinan-projects-AiLibi/d2f79696-15f2-4a2e-a7e2-cb7d5b023724/scratchpad/work/eval-and-scripts/`)
- `pytest_area.txt` — full area run with `--durations=40` (1257 passed, 1 skipped, 139.65 s).
- `bench_verify.py` — verify_samples (loader) vs bare walk timings.
- `probe_empty.py` — 18 analyzers on empty / no-meeting reports (all OK).
- `probe_vc.py` — the six zero-flag impostor ejections behind `vote_correctness_rate=0.923`.
- `count_walks.py` — walks/seeds per CLI entry (validity 50+50 walks/3.5 s; build_report 100 walks/2.2 s).
- `gates_timing.txt` — check.sh static-gate timings.
- Prose/validator counts: inline `ast` scripts (see transcript); vulture at ≥60 % confidence found no true dead code (its two hits were `for/else` and validator `cls` false positives).
