# Code review — area: tests / CI / tooling  (label: `tests-ci-tooling`)

Repo: `/Users/danielkeinan/projects/AiLibi` @ `main` (`b809b19c`), read-only review.
Scope: `tests/`, `.github/workflows/*`, `pyproject.toml`, `.importlinter`, `scripts/check.sh`,
`scripts/setup_env.sh`, `uv.lock`, `docker-compose.yml`, `.env.example`, `.gitignore`, `.hypothesis/`,
plus the frontend test/CI toolchain.
All timings on a 10-core Darwin box with other reviewers running concurrently; `uptime` load recorded
at every measurement (4.5–8.3 throughout).

---

## 1. Executive read (10 lines)

1. This is an unusually *disciplined* gate for an agent-built repo: one command (`scripts/check.sh`),
   SHA-pinned CI actions, `permissions: contents: read`, a locked `uv.lock`, and a provable
   runtime/dev dependency partition. The non-pytest legs total **~3 s warm / ~11 s cold**.
2. `mypy --strict` is real, not decorative: **0 `type: ignore` in production code** (140, all in tests).
   This is the strongest single signal in the area.
3. `ruff`, by contrast, is at **stock defaults** (E4/E7/E9/F only). Enabling the usual families surfaces
   **1,431 findings**, including 18 `zip()`-without-`strict=` in a project whose headline claim is
   byte-identical determinism.
4. The suite is large and *fast for its size*: **4,644 default-tier tests in 338 s** here (783 s on CI).
   But **59 % of wall time sits in 60 tests**, a third of that in fixture setup re-walking the same
   committed replay bytes — **61 modules load them independently; the one shared session fixture is used by 3.**
5. Hermeticity is good on time and network (zero `time.sleep`, zero wall-clock, loopback-only sockets)
   and **bad on process environment and the working tree**.
6. **P1**: `tests/test_firewall.py` plants files at fixed paths inside `agents/` and `observation/`.
   Verified: 2 of 7 concurrent `lint-imports` runs failed with a false BROKEN contract. A crash mid-test
   leaves un-gitignored junk that reds the gate.
7. **P1**: the root `conftest.py` pins exactly one env var. `AILIBI_MAX_COST_USD=0.001` alone
   (verified, single-variable isolation) fails 2 tests; a realistic ambient env fails 10.
8. **P1**: audit F1's mypy facet is still open — verified in a scratch repro that `ruff` honours
   `.gitignore` and `mypy` does not, so the documented evidence restore and the documented gate remain
   mutually exclusive. (F1's pytest facet *was* fixed at HEAD.)
9. Test *infrastructure* is the weakest structural point: 184 files, 134 k LOC, **2 conftest.py files**,
   and 10 hand-copied versions of the same `_saw_player_event` builder — half of which bypass the
   shared constants and hard-code the string literals the constants exist to protect.
10. Frontend is the coverage outlier: **11,128 LOC in `src/components/` behind 2 test files**, against a
    Python core at 1.6–2.8× test:prod. The Playwright config, however, is exemplary.

---

## 2. Findings

### P1-1 — `tests/test_firewall.py` mutates the working tree at fixed paths → concurrent-run false failures and crash residue  [VERIFIED, high confidence]

**Where.** `tests/test_firewall.py:22-23`, `:42-47`, `:143-144`, `:214-215`.

```python
# tests/test_firewall.py:22
bad_import = repo_root / "agents" / "_firewall_bad_import.py"
bad_import.write_text("import engine\n", encoding="utf-8")
try:
    result = subprocess.run(["uv", "run", "lint-imports", "--no-cache"], cwd=repo_root, ...)
```

Five fixed paths are written into the live checkout:
`agents/_firewall_bad_import.py`, `agents/_firewall_bad_transitive_import.py`,
`observation/_firewall_engine_bridge.py`, `agents/_firewall_numpy_bad_import.py`,
`agents/tactical/learned/_firewall_bad_import.py`.

**Evidence (repro).** One process running `tests/test_firewall.py`, another polling the gate's own
`lint-imports` leg:

```
$ uptime          # 2:30, load 7.09 6.87 5.79
--- lint-imports FAILED (run 3):
Agents must not import engine BROKEN
Contracts: 3 kept, 1 broken.
-   agents._firewall_bad_import -> engine (l.1)
--- lint-imports FAILED (run 4):
-   agents._firewall_bad_transitive_import -> observation._firewall_engine_bridge (l.1)
firewall pytest rc=0
lint-imports runs=7 failures=2
```

**Why it matters.**
* Two developers (or two agent sessions, or a human running `check.sh` while a suite runs) in one
  checkout get a *false architectural violation* — the single most alarming failure this repo can print.
  This is almost certainly the "concurrent-session collisions" the project's own working notes record.
* `pytest -n auto` / xdist is permanently unsafe, which caps the only cheap fix for the 13-minute CI leg.
* The cleanup is a `finally`, not a fixture, so SIGKILL/OOM/Ctrl-C during the ~seconds-long
  `lint-imports` subprocess leaves the plant behind. `.gitignore` has **no `_firewall*` pattern**
  (verified by reading it), so `git add -A` commits it and every later `lint-imports` fails until
  someone reads the diff.

**Fix.** Build the plant in `tmp_path` as a *copy-tree or overlay* of `agents/` + `observation/` and
point `lint-imports` at it via a generated `.importlinter` in the temp root, or at minimum register
cleanup through a `pytest.fixture` with `yield` + add `_firewall_*` to `.gitignore` as a belt-and-braces.
The plant-detect-cleanup *shape* is right and worth keeping (see §5 GOOD-5); only the location is wrong.

---

### P1-2 — Test hermeticity: `conftest.py` pins one env var out of 43; ambient `AILIBI_*` leaks into results  [VERIFIED, high confidence]

**Where.** `tests/conftest.py:57-61` — the only env guard in the whole suite:

```python
@pytest.fixture(autouse=True)
def _force_fake_llm_provider(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(ENV_PROVIDER, PROVIDER_FAKE)
```

**Evidence (single-variable isolation).**

```
$ uv run pytest tests/eval/test_balance_eval.py -q                       →  23 passed in 0.99s
$ AILIBI_MAX_COST_USD=0.001 uv run pytest tests/eval/test_balance_eval.py -q
FAILED tests/eval/test_balance_eval.py::test_canonical_balance_keeps_both_sides_alive
FAILED tests/eval/test_balance_eval.py::test_run_balance_eval_reuses_headless_game_outcomes
2 failed, 21 passed in 0.62s
   llm.budget.BudgetExceededError: LLM budget exceeded on cost_usd: current=0.0 + delta=0.072942 > cap=0.001
```

A realistic operator env (`AILIBI_SAMPLES_ROOT`, `AILIBI_NUM_PLAYERS`, `AILIBI_MAX_COST_USD`,
`AILIBI_ML_CORPUS_ROOT`, `ANTHROPIC_API_KEY`, … — 13 vars, all valid values) over
`tests/api tests/scripts tests/eval` gave **10 failed, 1541 passed**.

`grep -rhoE 'AILIBI_[A-Z_]+'` finds **43** distinct `AILIBI_*` names in code; the conftest guards one.

**Why it matters.** The conftest docstring is 30 lines explaining *exactly this failure class* for the
provider variable ("those tests fail locally while passing in CI"). The reasoning was right and the fix
was applied to one variable instead of the category. A developer who has ever exported a documented
knob gets spurious red, and — worse — the reverse direction is silent: an ambient value that makes a
test *pass* which would otherwise fail is undetectable.

**Fix.** Replace the single `setenv` with an autouse fixture that clears the whole namespace and
re-pins the defaults:

```python
@pytest.fixture(autouse=True)
def _hermetic_env(monkeypatch):
    for key in [k for k in os.environ if k.startswith("AILIBI_")]:
        monkeypatch.delenv(key, raising=False)
    for key in ("ANTHROPIC_API_KEY", "FEATHERLESS_API_KEY"):
        monkeypatch.delenv(key, raising=False)
    monkeypatch.setenv(ENV_PROVIDER, PROVIDER_FAKE)
```
…with an explicit opt-out marker for the handful of tests that *are* about env selection
(`tests/scripts/test_record_ml_corpus.py:117 _clean_env()` already hand-rolls exactly this — that helper
is the pattern, it just needs to be the default rather than one file's local defence).

---

### P1-3 — Audit F1's mypy facet is still open: the documented evidence restore and the documented gate are mutually exclusive  [VERIFIED mechanism, high confidence]

**Where.** `pyproject.toml` `[tool.mypy] exclude` (the regex covers only `experiments/lab/ml_spike/`,
`experiments/lab/torch_probe/`, `experiments/lab/(visibility|inference|stopwatch|forward_redesign)_`,
`design/`) vs `scripts/fetch_evidence.sh:347 write_gitignore()`.

`audits/audit-phase-19-close.md` §1 F1 records two facets. The **pytest** facet is fixed at HEAD —
`tests/scripts/test_verify_ml_evidence.py:145-155` now rebuilds `coevo/` from `git ls-files` output
instead of symlinking the real directory (commit `b809b19c`). The **mypy** facet is untouched:

> mypy, unlike ruff, has no gitignore awareness, so it walks the restored slate's untracked helper
> scripts … *"Found 15 errors in 3 files (checked 358 source files)"*

**Evidence (mechanism verified independently, in scratch, no repo writes):**

```
$ git check-ignore -v sub/bad.py     → sub/.gitignore:1:*  sub/bad.py
$ ruff check .                       → All checks passed!
$ mypy .                             → sub/bad.py:2: error: Incompatible return value type ...
                                        Found 1 error in 1 file (checked 1 source file)
```

**Why it matters.** `bash scripts/fetch_evidence.sh` and `bash scripts/check.sh` are both documented,
both required at phase close, and running them in that order produces a spurious red at the mypy leg.
`.gitignore` is not a mypy fence — the fence has to be in `pyproject.toml`.

**Fix (one line).** Extend the mypy `exclude` regex with
`|^training/reports/_finalist_eval_raw/|^training/artifacts/coevo/`, and add a test asserting that the
mypy exclude covers exactly the two restore destinations `fetch_evidence.sh` names, so the two files
cannot drift.

---

### P1-4 — Runtime is concentrated in duplicated walks of the same committed bytes  [VERIFIED, high confidence]

**Evidence.** Full default-tier run, `--durations=60`, `-p no:cacheprovider`, load 4.5–8.3:

```
4621 passed, 20 skipped, 317 deselected, 3 xfailed in 337.96s (0:05:37)
top-60 sum = 198.8s of 337.96s total = 59%
  of which setup = 66.1s (33%)
```

Structural measurement:

| measurement | value |
|---|---|
| modules that independently load `replays/samples/...` | **61** |
| modules using the shared `committed_9p2i_report` session fixture | **3** (`tests/eval/test_gate_metrics.py`, `test_vote_correctness.py`, `test_wave2_metrics.py`) |
| `scope="module"` fixtures | 52 |
| `scope="session"` fixtures | **1** |

The slow list is dominated by *setup*, not by *call*: `test_surrogate_dataset` 8.13 s setup,
`test_deception_instruments` 6.21 s, `test_conviction_serving` 6.05 s, `test_conviction_model` 6.04 s,
`test_beliefs_hard_evidence_gate` 4.54 s, `test_goodhart_probe` 3.93 s, `test_absence_prior` 3.89 s,
`test_off_menu` 3.69 s, `test_surrogate_runner` 3.47 s, `test_prompt_byte_golden` 3.38 s.

**Why it matters.** `tests/conftest.py:64-85` correctly diagnosed this for *one* consumer group
("six `build_report` calls per suite run … one session-scoped walk serves them all") and then stopped.
The same reasoning applies to the state-hash-verified engine walk of `replays/samples/9p2i`, which is a
pure function of committed bytes and is currently performed dozens of times per run at module scope.
Promoting the walk to a session-scoped fixture (or a module-level `functools.cache` on a shared helper)
should remove most of the 66 s of setup — ~20 % of local wall time, and proportionally more of CI's 783 s,
which is the number that actually gates every PR.

**Fix.** One `tests/_helpers/committed.py` exposing session-cached `walk_9p2i()` / `walk_4p1i()` /
`report_9p2i()`; migrate the 61 modules incrementally. This is also the prerequisite for ever making
the suite parallel-safe.

---

### P1-5 — `ruff` runs at stock defaults; 1,431 findings in the standard families, incl. determinism-relevant ones  [VERIFIED, high confidence]

**Where.** `pyproject.toml:33-35` — the entire ruff config:

```toml
[tool.ruff]
target-version = "py311"
line-length = 88
```

No `[tool.ruff.lint] select`, so only ruff's default `E4, E7, E9, F` are enabled.

**Evidence.**

```
$ uv run ruff check --select B,UP,C4,SIM,ARG,PT,I,N,RUF --statistics .   → 1431 findings
```

The ones that are not style noise:

| rule | n | notable sites |
|---|---|---|
| `B905` `zip()` without `strict=` | 18 | `agents/memory/store.py:1064`, `eval/kill_craft.py:749`, `training/bakeoff/map_elites.py:223`, `tests/observation/test_leak_property.py:135`, `tests/training/test_es.py:156` |
| `B904` `raise` without `from` inside `except` | 9 | `api/routes/replays.py` ×7, `api/routes/eval.py` ×2, `api/replay_loader.py:3152` |
| `B017` `pytest.raises(Exception)` | 4 | `tests/agents/test_memory.py:30`, `tests/llm/test_client.py:532`, `tests/scripts/test_verify_ml_evidence.py:1454,1464` |
| `B008` call in argument default | 4 | `experiments/lab/deception_probe*.py` |
| `SIM115` file opened without a context manager | 3 | `experiments/lab/ml_spike/*`, `design/phase-12/gen_map_reference.py` |
| `I001` unsorted imports | 95 | repo-wide |

**Why it matters.** `B905` is a *silent-truncation* class: `zip(a, b)` where `len(a) != len(b)` drops the
tail without error. In `agents/memory/store.py` and `eval/kill_craft.py` that is one refactor away from a
determinism bug that no state-hash check would catch, because both sides would truncate identically.
`B017` means four assertions currently accept *any* exception including `AttributeError` from a typo in
the test itself. And the absence of `I001` means import order is unenforced in a repo where `ruff format`
otherwise enforces everything.

**Fix.** `select = ["E", "F", "W", "I", "B", "C4", "UP", "SIM", "RUF"]` with a per-file-ignores block for
tests, adopted in two commits (auto-fixable first, then the ~40 real ones). Add `RUF100` on day one —
see P2-1.

---

### P2-1 — 114 verified-dead `# noqa` directives; 90 of the 256 name rules that were never enabled  [VERIFIED, high confidence]

```
$ grep -rn 'noqa' --include='*.py' . | grep -v .venv | wc -l        → 256
$ uv run ruff check --extend-select RUF100 --output-format=concise . → Found 114 errors.
   e.g. tests/training/test_surrogate_runner.py:53:21: RUF100 Unused `noqa` (non-enabled: `PLC2701`)
        tests/training/test_surrogate_fidelity.py:536:62: RUF100 Unused `noqa` (non-enabled: `D401`)
```

Distribution of the codes being suppressed:

| code | n | enabled by current config? |
|---|---|---|
| `E402` | 164 | yes |
| `PLC2701` | 48 | **no** |
| `BLE001` | 14 | **no** |
| `PLR2004` | 11 | **no** |
| `SLF001` | 9 | **no** |
| `D401` | 3 | **no** |
| `S603`,`S310`,`PLC0415`,`N802`,`E501` | 1 each | **no** |

This is textbook cargo-culted defence: suppressions copied from a stricter project's rule set, doing
nothing, and creating a false impression that pylint/bandit/flake8-blind-except rules are in force.
Adding `RUF100` to `select` makes the class self-cleaning forever.

### P2-2 — The suite only passes from the repo root: 21 files use cwd-relative paths  [VERIFIED]

Two conventions coexist: **68** files use `Path(__file__).resolve().parents[...]`, **21** use bare
relative paths (`grep -rlE 'Path\("(training|replays|tests|scripts|…)/'`).

```
$ cd <scratch> && uv run --project <repo> pytest <repo>/tests/agents/test_memory_rendering.py -q
E   FileNotFoundError: [Errno 2] No such file or directory: 'tests/fixtures/memory_rendering/impostor_minimal.json'
3 failed, 61 passed in 0.29s
```

`tests/agents/test_memory_rendering.py:32` and `tests/eval/test_prompt_regression.py:43` are the clearest
cases. `tests/scripts/test_champion_flip_ruling.py:91-104` even *documents* the split
("Loaded file-relative — the evidence inputs above stay repo-root-relative — so a cwd change cannot split
the two conventions silently") and then keeps both. Pick one; `parents[N]` is already the majority.

### P2-3 — `slow` and `perf` markers are registered, unused, and pinned in place by a test  [VERIFIED]

`pyproject.toml:60-63` registers `slow` and `perf` with docstrings saying they are "registered for tiering
annotation … carries no default filter … Reserved so a future cut can select on it".

```
$ grep -rn 'mark\.slow' --include='*.py' .   → (nothing)
$ grep -rn 'mark\.perf' --include='*.py' .   → (nothing)
```

`tests/training/test_suite_tiers.py:108` then asserts `{"campaign","slow","perf"} <= registered`, so the
dead config cannot be removed without editing a test. Speculative generality with a lock on it. Delete both
markers and the assertion; re-register when a cut actually needs them.

### P2-4 — Test-infrastructure duplication: the same builders re-typed 10–16 times, half of them bypassing the shared constants  [VERIFIED]

184 test files, 134,094 LOC, **2 `conftest.py` files**, 82 fixtures. Module-level helper name frequency:

```
16 _turn      13 _meeting   13 _ballot   12 _packet   11 _self_state_event
11 _game      10 _saw_player_event       9 _player     7 _saw_body_event   7 _public_map
```

`_saw_player_event` in full — 10 copies, functionally identical, differing only in default args:

```python
# tests/agents/test_impostor_policy.py:112   (uses the constants)
payload={"player_id": player_id, "room": room, "action": action},
provenance=PROVENANCE_OBSERVED,   type=EVENT_SAW_PLAYER

# tests/agents/test_memory_rendering.py:97   (hard-codes the literals)
type="saw_player",  provenance="observed",
```

5 of the 10 use `EVENT_SAW_PLAYER` / `PROVENANCE_OBSERVED`; 5 hard-code `"saw_player"` / `"observed"`.
The constants exist so a rename is a compile-time event; half the test suite has opted out of that
guarantee. `tests/api/fixtures/` shows the project already knows the right pattern (5 modules import
from it) — it was just never generalised. `tests/_helpers/` holds exactly one 105-line file.

### P2-5 — Meta-tests that pin test structure rather than behaviour  [VERIFIED]

* `tests/eval/test_performance.py:63 test_perf_benchmark_marker_is_opt_in_skipif` — asserts
  `perf_benchmark.mark.name == "skipif"`. This tests pytest, not AiLibi.
* `tests/training/test_suite_tiers.py:39-91` hard-codes a list of 10 file paths and 9 test *function names*
  (`_MIXED_TIER_CAMPAIGN_TESTS`, `_MIXED_TIER_ALWAYS_ON_TESTS`) and regex-matches the decorator line above
  each. Renaming any of those nine tests, or reordering a decorator, breaks the meta-test with no behaviour
  change. The *intent* (a tier map that cannot rot) is legitimate; the *implementation* (a regex over source
  bytes, deliberately "read file bytes rather than importing the test modules", :23-24) trades one coupling
  for a more brittle one. `pytest --collect-only -q -m campaign` gives the same guarantee from the real
  collection tree, with no file list to maintain.

### P2-6 — CI hygiene gaps: no dependency caching, no concurrency group, no job timeout, no dependabot  [VERIFIED by reading]

`.github/workflows/ci.yml`:
* `astral-sh/setup-uv@37802adc…` is used **without `enable-cache: true`** (`grep -n 'enable-cache'` → no hits).
  Node *is* cached (`cache: npm`, twice). Three jobs × every push/PR re-resolve and re-download 46 packages
  including numpy 2.2.6. The local `.mypy_cache` / `.ruff_cache` / `.import_linter_cache` have no CI analogue
  either — cold mypy measured at **9.5 s** vs 0.6 s warm.
* No `concurrency: {group: …, cancel-in-progress: true}`. Superseded pushes keep burning the 13-minute suite.
* No `timeout-minutes` on any job → a hung Playwright leg holds a runner for GitHub's 6-hour default.
* Actions are SHA-pinned with the resolved tag in a trailing comment — genuinely good practice — but there is
  **no `.github/dependabot.yml`**, so those pins will silently rot and the "re-resolve the tag and update both
  the SHA and the comment together" instruction at `ci.yml:30-32` has no trigger.

### P2-7 — The campaign tier is schedule-only: a PR can break it and merge green  [VERIFIED by reading]

`.github/workflows/campaign-tier.yml:26-28` fires weekly (Mon 06:17 UTC) plus `workflow_dispatch`. 317 tests
(6.4 % of the suite, 5 m 15 s per the close audit) are therefore invisible to every PR, with a detection
latency of up to 6 days and no bisect anchor. The file's own comment defends *schedule over path-filter*
("it must also catch rot introduced from OUTSIDE training/") — which is correct, but is an argument for
**both**, not for schedule alone. Adding a `paths: ['training/**', 'eval/**', 'tests/training/**']`-filtered
job to `ci.yml` costs ~5 min on the PRs that can actually break it and keeps the weekly job as the
external-rot net.

### P2-8 — Frontend test coverage is an order of magnitude behind Python  [VERIFIED]

| area | prod LOC | test LOC | ratio |
|---|---|---|---|
| `engine` | 2,299 | 3,741 | 1.63 |
| `observation` | 1,107 | 2,867 | 2.59 |
| `meetings` | 8,673 | 23,995 | 2.77 |
| `agents` | 11,250 | 20,173 | 1.79 |
| **`frontend/src`** | **19,177** | **2,789** | **0.15** |

Per-directory, `npm run test` → 173 passed in 360 ms across 6 files:

```
src/components   src=32  tests=2   loc=11128
src/hooks        src=2   tests=0   loc=652
src/ui           src=7   tests=0   loc=290
src/types        src=2   tests=0   loc=1714
```

11 k lines of React/PixiJS behind 2 unit-test files and one 779-line Playwright journey. The journey is
excellent (§5 GOOD-6) but it is a single happy path; component regressions land unobserved.

### P2-9 — Hypothesis is present but unconfigured: CI failures are unreproducible  [VERIFIED]

3 files, 8 `@given` in a 4,644-test suite (`tests/engine/test_tick_properties.py`,
`tests/observation/test_leak_property.py`, `tests/agents/test_beliefs_provenance.py`).

```
$ grep -rn 'register_profile|load_profile|derandomize|database=' --include='*.py' .   → (nothing)
```

Consequences: (a) the example database lives in the gitignored local `.hypothesis/` (2.8 M) and is never
cached or uploaded by CI, so a counterexample found on one CI run is gone on the next; (b) each CI run draws
a *different* 50 examples, making these the only genuinely non-deterministic tests in a repo whose thesis is
determinism; (c) `max_examples=50` is thin for the observation-firewall property
(`test_leak_property.py:235`), which is the load-bearing security claim.
AGENTS.md:60 says "Property tests use `hypothesis`" — true, but 8 of 4,644 is closer to a spike than a practice.

### P2-10 — `pyproject.toml`'s "known, accepted boundary" comment is stale; the boundary it describes no longer exists  [VERIFIED]

`pyproject.toml:22-26`:

> Known, accepted boundary: `training/` and `eval/` are NOT covered by that claim. `eval/leak_test.py:9`
> imports pytest at module level and both production-side consumers (`training/bakeoff/harness.py:107`,
> `training/crew/scorer.py:113`) import from it, so training/eval remain dev-environment surfaces **until
> Task 19.24 promotes the scanners to a pytest-free library.**

Task 19.24 has landed. `eval/leak_scan.py` exists (30 kB, no pytest import); `training/bakeoff/harness.py:83`
documents the move in place ("`eval.leak_scan`, not `eval.leak_test`, since Task 19.24"); the cited lines
107/113 now import `eval.leak_scan`.

```
$ uv run --no-dev --exact python -c "import training.bakeoff.harness, training.crew.scorer, \
      training.env, eval.leak_scan, eval.validity, eval.watchability"
OK: eval+training entry modules import with the dev group uninstalled
$ uv run --no-dev --exact python -c "import eval.leak_test"
ModuleNotFoundError: No module named 'pytest'
```

The *only* residue is that two pytest modules live outside `tests/`: `eval/leak_test.py` and
`eval/determinism_test.py` (both also `from tests._helpers.world_state import …`, i.e. production-tree files
importing the test tree). Move them under `tests/` and the whole comment can be deleted rather than corrected.

### P2-11 — Inconsistent test-package structure + a duplicate module basename  [VERIFIED]

4 of 12 test directories have `__init__.py` (`tests/`, `tests/_helpers/`, `tests/api/`, `tests/experiments/`,
`tests/training/`); 7 do not (`agents`, `engine`, `eval`, `llm`, `meetings`, `observation`, `orchestrator`,
`scripts`). `test_schemas.py` exists twice — `tests/api/` (has `__init__.py`) and `tests/meetings/` (does not).
They do not collide *today* precisely because of that asymmetry; a third `test_schemas.py` in any
`__init__.py`-less directory would be a hard `import file mismatch` collection error. Free fix: add
`__init__.py` everywhere, or set `--import-mode=importlib` in `addopts`.

### P2-12 — Two remaining test-module-as-library imports  [VERIFIED]

`tests/observation/test_leak_property.py:76` → `from tests.engine.test_tick_properties import _unique_actions_per_actor`
and `tests/llm/test_real_provider.py:56` → `from tests.llm.test_client import real_provider`.
`tests/training/test_suite_tiers.py:23-24` states "importing a test module as a library is exactly the pattern
Task 19.27 removed" — it removed it from `tests/training/`, not from the suite. Both belong in
`tests/_helpers/`.

### P2-13 — Running a campaign-marked file directly reports success-shaped output  [VERIFIED]

```
$ uv run pytest tests/training/test_coevo_driver.py -q
56 deselected in 0.43s
$ echo $?
5
```

Exit 5 (`EXIT_NOTESTSCOLLECTED`), so `set -e` scripts *do* catch it — the marker help text at
`pyproject.toml:65-68` warns about this. Still, the interactive output for a developer editing that file is a
green-looking line with no failures. A `pytest_collection_modifyitems` hook that raises when explicit path
args yield zero selected items would close it in five lines.

### P2-14 — `.env.example` documents 11 of the 43 `AILIBI_*` names; the gate's own knobs appear in no `.md`  [VERIFIED]

`.env.example` is 142 well-written lines covering 4 live assignments plus the graduated-lever registry — and
`scripts/check_doc_facts.py` mechanically verifies its lever section against `orchestrator.replay`, which is
excellent. But the *operator* knobs are absent from `.env.example`, README and CONTRIBUTING alike:

```
AILIBI_RUN_PERF_BENCHMARK: docs hits = (none)
AILIBI_SKIP_FRONTEND:      docs hits = (none)
AILIBI_MAX_COST_USD:       docs hits = (none)
AILIBI_SAMPLES_ROOT:       docs hits = (none)
AILIBI_NUM_PLAYERS:        docs hits = (none)
```

(`AILIBI_RUN_REAL_PROVIDER_TESTS` / `AILIBI_RUN_OLLAMA_TESTS` *are* in `AGENTS.md` + `llm/README.md`.)
Given P1-2, `AILIBI_MAX_COST_USD` is doubly worth documenting: it is undocumented *and* it silently breaks the
suite.

### P2-15 — CONTRIBUTING overstates the gate's coverage  [VERIFIED]

CONTRIBUTING.md: *"`scripts/check.sh` is the required gate and the one-command local truth: it runs the same
checks CI runs."* CI additionally runs the `frontend-e2e` Playwright job, which `scripts/check.sh:31-35`
deliberately excludes with a good reason. `check.sh ⊂ CI`, so the claim is wrong in the safe direction, but a
contributor reading it will believe a green `check.sh` predicts a green CI. One clause fixes it.

---

## 3. Architecture / design assessment

**Well designed — keep as-is.**

* **The gate shape.** Seven legs, cheapest-signal-first, one script, `set -euo pipefail`, loud validation of
  its own env input (`check.sh:9-13`, mirrored in `setup_env.sh:15-19`). Warm cost of the six non-pytest legs
  is ~3 s total. This is the right design and it is well executed.
* **Two-tier CI as two workflow *files*.** `campaign-tier.yml:10-15` documents a genuinely subtle attack — a
  shared `schedule`/`dispatch` trigger emits SKIPPED instances of `ci.yml`'s jobs, and GitHub treats a skipped
  job as satisfying a same-named required check. Separating the files is the correct fix and the reasoning is
  recorded where the next reader will find it.
* **The dependency partition.** Runtime deps exact-pinned in `[project]`, gate toolchain in
  `[dependency-groups].dev`, and — unusually — a *runnable proof* of the split written into the comment
  (`uv run --no-dev --exact python -c "import api.main, …"`), including why `--no-dev --exact` is load-bearing
  and why the entry-module list is load-bearing. I ran it; it passes.
* **`scripts/regen_test_goldens.py`.** The right answer to hand-transcribed pins: goldens are *generated* from
  committed evidence, the tests *re-derive* independently and compare, and the docstring states the division of
  labour precisely ("a golden holds MEASURED TRANSCRIPTIONS … independent ANCHORS stay code literals … 
  Regenerating an anchor from the same file the tests check it against would turn a file-vs-plan pin into a
  file-vs-file tautology"). That last sentence is better reasoning than most human-written test suites contain.

**Accidental complexity.**

* **A test suite with no test-infrastructure layer.** 134 k LOC / 184 files / 2 conftests / 1 session fixture.
  Everything is per-module: builders, replay walks, path constants. That single structural choice produces
  P1-4 (runtime), P2-2 (cwd), P2-4 (duplication) and P2-11/P2-12 (structure) as consequences. It is the one
  refactor with compounding returns.
* **Prose density in the tree under test.** Measured by AST across the core production packages
  (`engine agents observation meetings orchestrator llm api eval`): **30.9 % of lines are docstrings, 10.2 %
  are comments, 46.7 % are code — prose:code = 0.88.** `tests/` is healthier at 0.31. Much of the core prose is
  *history* ("since Task 19.24", "the Codex review on PR #349", "superseded by Featherless at Phase 14") rather
  than *contract*, which is exactly how P2-10 happened: the comment described a state of the world, the world
  moved, the comment did not. Comments that assert facts about other files need tests, or they need to not be
  written.
* **Script gigantism in the tooling tier.** `scripts/verify_ml_evidence.py` 2,855 lines,
  `generate_campaign_tables.py` 1,788, `record_ml_corpus.sh` **1,276 lines of bash**, `run_tournament.py` 1,241,
  `refresh_samples.sh` 917, `fetch_evidence.sh` 811. A 1,276-line shell script is a maintenance liability
  regardless of how well commented it is; `record_ml_corpus.sh` and `refresh_samples.sh` are also the two
  files with the most complex concurrency (parallel workers, staging dirs, traps). Both have real test files,
  which is the mitigating factor — but they should be Python.

**What I would refactor, in order.**

1. `tests/_helpers/` becomes a real package: `env.py` (the hermetic-env fixture), `committed.py`
   (session-cached replay walks + report), `events.py` (the ~8 duplicated event builders), `paths.py`
   (`REPO_ROOT` and friends). Then delete 10 copies of `_saw_player_event` and 21 cwd-relative path constants.
2. `tests/test_firewall.py` plants into `tmp_path` with a generated `.importlinter`; the suite becomes
   parallel-safe; `pytest -n auto` becomes available, which is the real answer to the 13-minute CI leg.
3. `ruff` `select` expanded; `RUF100` on; the 114 dead noqa fixed automatically.
4. `eval/leak_test.py` + `eval/determinism_test.py` move to `tests/`; the stale `pyproject.toml` boundary
   comment is deleted rather than updated.

---

## 4. Test assessment for the area

**Counts.** 4,961 collected; 4,644 default tier; 317 campaign. Full default run:
**4,621 passed, 20 skipped, 317 deselected, 3 xfailed in 337.96 s**, exit 0, first try, no flakes observed.
11,932 assertions over 4,644 tests (2.6/test). 152 `parametrize`, 620 `pytest.approx`, 82 fixtures.

**Skips are honest.** 18 of the 20 are opt-in real-provider / Ollama-server / perf-benchmark gates with
explicit reasons; the other 2 are `shutil.which("uv"/"bash")` guards. There is no `@pytest.mark.skip` used to
park a broken test. The 3 `xfail`s (`tests/orchestrator/test_meeting_integration.py:2481,2550,2583`) are
`strict=True` with a named reason — correct usage.

**Flakiness hazards, by class.**

| class | verdict |
|---|---|
| wall-clock / sleep | **clean.** Zero `time.sleep`, zero `datetime.now`, zero `perf_counter` in `tests/`. |
| network | **clean.** Loopback only; `tests/scripts/test_refresh_samples.py:750-769` binds port 0 and probes a deliberately closed port. |
| tmp paths | **clean.** 77 files use `tmp_path`. |
| ordering | **probably clean.** Subsets (`tests/api tests/scripts tests/eval`, `tests/llm tests/scripts`) pass standalone; no `pytest-randomly` installed so this is unproven at the item level. |
| **working tree** | **DEFECT — P1-1.** |
| **process env** | **DEFECT — P1-2.** |
| **cwd** | **DEFECT — P2-2.** |
| randomness | 8 hypothesis properties, unseeded, no example DB in CI — P2-9. |

**Golden / pin brittleness — better than expected.** Only 21 long-hex literals across the whole suite, and the
two `_goldens/` JSON files are machine-regenerated with independent re-derivation in the test. The exposure is
in *prose*: 1,177 `assert … == "…"` and 543 `assert "…" in …`, ~14 % of all assertions, bound to literal text.
Spot-measured blast radius per string is modest (`"You discovered"` → 18 assertions in 5 files;
`"(IMPOSTOR) killed"` → 6 in 3), so a reworded line breaks a handful of tests, not hundreds. Acceptable.

**The two best tests in the area** (worth protecting from any refactor):

* `tests/meetings/test_prompt_byte_golden.py` — re-renders every recorded prompt of every committed replay
  through the **real** `meetings.manager.MeetingManager` (explicitly refusing to re-implement the assembly:
  "Re-implementing that would be a second source of truth and a dishonest golden"), and includes
  `test_one_byte_template_perturbation_breaks_the_golden` — *"a golden that cannot fail is not a gate."*
* `tests/scripts/test_check_doc_facts.py:72` — `assert check_doc_facts.check_facts(_REPO_ROOT) == []`, i.e. the
  documentation-truth checker runs against the **real repository** inside the normal gate, not against a
  fixture. That is how you stop docs from drifting, and it is the reason README/`.env.example` are as accurate
  as they are while `pyproject.toml`'s comment (P2-10, unguarded) is not.

---

## 5. What is genuinely GOOD

1. **`mypy --strict`, honestly.** `strict = true`, no per-module relaxations, exclude limited to explicitly
   exploratory `experiments/lab/*` and `design/`. **Zero `type: ignore` anywhere in
   `engine/agents/observation/meetings/orchestrator/llm/api/eval/training/scripts`** — all 140 live in `tests/`,
   where they mark deliberately-invalid inputs. `warn_unused_ignores` is part of strict, so none of them is
   stale. `Success: no issues found in 354 source files.`
2. **CI supply-chain posture.** Every action pinned to a full commit SHA with the resolved tag in a trailing
   comment and an explicit bump procedure; `permissions: contents: read` at workflow scope with the reasoning
   stated; `uv sync --locked` and `npm ci` so a lock/manifest drift fails rather than silently resolving;
   `uv lock --check` passes.
3. **Fail-loud environment handling in the shell tier.** `check.sh:10-13` and `setup_env.sh:16-19` reject an
   unrecognised `AILIBI_SKIP_FRONTEND` instead of treating it as falsy — "an unrecognised value is a typo, not
   a 'run it anyway'". `setup_env.sh:29-33` then probes every tool version so a missing dev group fails at
   setup rather than mid-gate. `setup_env.sh:57-65` retries `npm ci` with backoff for the ECONNRESET class only.
4. **`docker-compose.yml` publishes to `127.0.0.1` only**, with a comment explaining that the spectator API is
   an unauthenticated GM view and that a bare `"8000:8000"` would expose roles and kill attribution to the LAN.
   Security reasoning at the point of the decision.
5. **Every gate proves it can fail.** `test_one_byte_template_perturbation_breaks_the_golden`,
   `test_numpy_torch_source_scan_rejects_planted_import`, `test_learned_package_scan_rejects_planted_import`,
   `test_verify_sh_detects_corruption`. The plant-detect-cleanup pattern is the right instinct (its *location*
   is P1-1, its *existence* is a strength).
6. **`frontend/playwright.config.ts`.** Browser pinned by pinning `@playwright/test` exactly, with the CI cache
   keyed on the resolved version; `workers: 1`; `retries: process.env.CI ? 1 : 0` ("a local retry hides a real
   bug from the person able to fix it"); `forbidOnly` in CI; `trace: retain-on-failure`; and — verified by
   grep — **zero `waitForTimeout` in `e2e/`**. The IPv4-literal host with the dual-stack rationale is the kind
   of detail that only gets written after someone has lost two hours to it.
7. **Test suite performance is genuinely good for its size.** 4,644 tests in 338 s wall on a loaded box,
   collection in 1.88 s. The 60 slowest are all doing real work over committed bytes.
8. **`tests/scripts/conftest.py`** — 17 lines, and every one of them explains a real constraint (`scripts/` has
   no `__init__.py` because `mypy_path = "scripts"` would otherwise see each file under two module names).
   This is what the other 10 missing conftests should look like.

---

## 6. Recommendations (prioritized)

1. **Make `tests/test_firewall.py` operate on a temp tree.** Copy `agents/` + `observation/` into `tmp_path`
   with a generated `.importlinter`, and run `lint-imports --config <tmp>/.importlinter` there. Add
   `_firewall_*` to `.gitignore` as a second line of defence. *Unblocks:* concurrent gates today, `pytest -n
   auto` tomorrow. (P1-1)
2. **Replace the one-variable conftest guard with a namespace-wide one.** Clear every `AILIBI_*` plus the two
   provider keys autouse; re-pin `AILIBI_LLM_PROVIDER=fake`; give env-selection tests an explicit opt-out
   marker. `tests/scripts/test_record_ml_corpus.py:117` already contains the helper — promote it. (P1-2)
3. **Close F1's mypy facet with one regex.** Extend `[tool.mypy] exclude` to cover
   `training/reports/_finalist_eval_raw/` and `training/artifacts/coevo/`, and add a test asserting the exclude
   list matches the destinations `scripts/fetch_evidence.sh` writes, so the pair cannot drift again. (P1-3)
4. **Build `tests/_helpers/` into a real shared layer** — `committed.py` (session-cached replay walks + report),
   `env.py`, `events.py`, `paths.py` — then migrate the 61 modules that walk the committed sets and the 21 that
   use cwd-relative paths. Expected: ~20 % off local wall time, proportionally more off CI's 783 s, and P2-2 /
   P2-4 / P2-12 disappear as side effects. (P1-4, P2-2, P2-4)
5. **Expand `ruff` `select` to `["E","F","W","I","B","C4","UP","SIM","RUF"]`.** Land the ~1,300 auto-fixable in
   one mechanical commit, then the ~40 real ones (`B905` first — `agents/memory/store.py:1064` and
   `eval/kill_craft.py:749` are in the determinism path). `RUF100` clears the 114 dead noqa and keeps them
   cleared. (P1-5, P2-1)
6. **Four CI one-liners:** `enable-cache: true` on `setup-uv` in all three jobs; a `concurrency` group with
   `cancel-in-progress`; `timeout-minutes: 30` per job; a `.github/dependabot.yml` for `github-actions` so the
   SHA pins have a bump path. (P2-6)
7. **Run the campaign tier on PRs that touch it** — a `paths`-filtered `-m campaign` job in `ci.yml` alongside
   the existing weekly schedule, so a training/eval change cannot merge green and surface six days later.
   (P2-7)
8. **Delete the dead `slow`/`perf` markers and the assertion that pins them; delete
   `test_perf_benchmark_marker_is_opt_in_skipif`; replace `test_suite_tiers.py`'s source-regex file list with a
   `pytest --collect-only -m campaign` comparison.** Then correct the two stale comments —
   `pyproject.toml:22-26` (Task 19.24 has landed) and CONTRIBUTING's "the same checks CI runs" — and move
   `eval/leak_test.py` + `eval/determinism_test.py` under `tests/`. (P2-3, P2-5, P2-10, P2-15)

---

## Appendix — commands run

```
uv run pytest -q --co -p no:cacheprovider                        # 4644/4961 collected (317 deselected) in 1.88s
uv run pytest -q -p no:cacheprovider --durations=60              # 4621 passed … 337.96s, exit 0  (load 4.53→6.05)
uv run pytest tests/test_firewall.py  ×2 concurrent  ×3          # no collision at this granularity
uv run pytest tests/test_firewall.py & poll uv run lint-imports  # 2/7 false BROKEN  ← P1-1 repro
AILIBI_MAX_COST_USD=0.001 uv run pytest tests/eval/test_balance_eval.py   # 2 failed  ← P1-2 repro
cd <scratch> && uv run --project <repo> pytest <repo>/tests/agents/test_memory_rendering.py  # 3 failed ← P2-2
<scratch git repo w/ gitignored bad.py> ruff check . → clean ; mypy . → error   ← P1-3 mechanism
uv run ruff check --select B,UP,C4,SIM,ARG,PT,I,N,RUF --statistics .     # 1431
uv run ruff check --extend-select RUF100 --output-format=concise .       # 114 unused noqa
uv run mypy --cache-dir <fresh> .                                 # 9.5s cold / 0.6s warm, 354 files
uv run --no-dev --exact python -c "import api.main, …"            # OK — the pyproject probe passes
uv run --no-dev --exact python -c "import eval.leak_test"         # ModuleNotFoundError: pytest  ← P2-10
uv lock --check                                                   # Resolved 46 packages
cd frontend && npm run test                                       # 6 files, 173 tests, 360ms
```

Scratch artifacts: `/private/tmp/claude-501/-Users-danielkeinan-projects-AiLibi/d2f79696-15f2-4a2e-a7e2-cb7d5b023724/scratchpad/work/tests-ci-tooling/`
(`full-run.txt`, `fw-conc.txt`, `prose.py`, `env-code.txt`, `env-doc.txt`).
No file inside the repository was created, edited, staged or deleted; `git status --short` is empty.
