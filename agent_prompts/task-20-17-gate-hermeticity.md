# Agent Prompt — 20.17 Gate hermeticity: the documented restore and the documented gate stop excluding each other; the env surface is pinned

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-20.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 20.17 — Gate hermeticity: the documented restore and the documented gate stop excluding each other; the env surface is pinned, anchored to audits/review-2026-08-19/B/tests-ci-tooling.md §2 P1-3 (C-96, the mypy facet) + §2 P1-2 (C-35, the env surface), §1 items 7-8, §6 recommendations 2-3, Appendix (both repro commands); audits/review-2026-08-19/B/collated-findings.md rows C-96 + C-35; audits/review-2026-08-19/D/FINAL-synthesis.md §4 wave-1 row 1.11; audits/review-2026-08-19/D/cross-track-map.md rows C-96 + C-35; audits/audit-phase-19-close.md §1 F1 (both facets, quoted); pyproject.toml:45-61 (`[tool.mypy]`, the exclude regex at :61); scripts/fetch_evidence.sh:44-45 (`COEVO_DEST` + `SLATE_DEST`), :347-372 (`write_gitignore`); scripts/verify_ml_evidence.py:110-111 (the same two destinations as constants); tests/scripts/test_verify_ml_evidence.py:138-156 (F1's pytest facet, fixed at HEAD by rebuilding coevo/ from `git ls-files`); tests/conftest.py:1-38 (the diagnosis of exactly this failure class) + :57-61 (the one-variable guard); the three hand-rolled cleaners tests/scripts/test_record_ml_corpus.py:117-129, tests/scripts/test_refresh_samples.py:537, tests/api/test_replay_loader.py:959-964; the three opt-in gates tests/llm/test_client.py:619 + :647, tests/llm/test_ollama_client.py:845 + :879 + :897, tests/eval/test_performance.py:30 + :72; tests/experiments/test_torch_probe_excluded.py:92-112 (`test_mypy_exclude_covers_the_probe_directory`, the precedent for pinning a mypy exclude both ways); docs/artifacts.md:58-69 (the `.gitignore` rule) + :116-122 (the restore commands); scripts/check.sh:15-21 (the gate legs); AGENTS.md craft rules 2, 5, 6. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-20.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-20-gate-hermeticity`
**Depends on:** none (root)
**Section refs:** audits/review-2026-08-19/B/tests-ci-tooling.md §2 P1-3 (C-96, the mypy facet) + §2 P1-2 (C-35, the env surface), §1 items 7-8, §6 recommendations 2-3, Appendix (both repro commands); audits/review-2026-08-19/B/collated-findings.md rows C-96 + C-35; audits/review-2026-08-19/D/FINAL-synthesis.md §4 wave-1 row 1.11; audits/review-2026-08-19/D/cross-track-map.md rows C-96 + C-35; audits/audit-phase-19-close.md §1 F1 (both facets, quoted); pyproject.toml:45-61 (`[tool.mypy]`, the exclude regex at :61); scripts/fetch_evidence.sh:44-45 (`COEVO_DEST` + `SLATE_DEST`), :347-372 (`write_gitignore`); scripts/verify_ml_evidence.py:110-111 (the same two destinations as constants); tests/scripts/test_verify_ml_evidence.py:138-156 (F1's pytest facet, fixed at HEAD by rebuilding coevo/ from `git ls-files`); tests/conftest.py:1-38 (the diagnosis of exactly this failure class) + :57-61 (the one-variable guard); the three hand-rolled cleaners tests/scripts/test_record_ml_corpus.py:117-129, tests/scripts/test_refresh_samples.py:537, tests/api/test_replay_loader.py:959-964; the three opt-in gates tests/llm/test_client.py:619 + :647, tests/llm/test_ollama_client.py:845 + :879 + :897, tests/eval/test_performance.py:30 + :72; tests/experiments/test_torch_probe_excluded.py:92-112 (`test_mypy_exclude_covers_the_probe_directory`, the precedent for pinning a mypy exclude both ways); docs/artifacts.md:58-69 (the `.gitignore` rule) + :116-122 (the restore commands); scripts/check.sh:15-21 (the gate legs); AGENTS.md craft rules 2, 5, 6
**Complexity:** Small
**Record impact:** none — tooling and test isolation only; no engine, detector, memory-render or prompt byte moves, and no committed replay is read differently
**Measurement:** `bash scripts/fetch_evidence.sh && bash scripts/check.sh && bash scripts/fetch_evidence.sh --clean && bash scripts/check.sh` — all four legs green, with mypy reporting the SAME source-file count in both states (review-measured today: 354 clean vs *"Found 15 errors in 3 files (checked 358 source files)"* restored); `AILIBI_MAX_COST_USD=0.001 uv run pytest tests/eval/test_balance_eval.py -q` green (review-measured today: 2 failed); `uv run pytest` under every non-gate `AILIBI_*` name exported to a valid value reports the same passed/skipped/xfailed counts as the bare run.

Two steps this repo documents — `bash scripts/fetch_evidence.sh` (docs/artifacts.md:116-122) and
`bash scripts/check.sh` (the one-command gate, AGENTS.md) — currently exclude each other. `ruff`
honours `.gitignore` and `mypy` does not, so after the restore mypy walks the four untracked
helper scripts the slate payload puts under `training/reports/_finalist_eval_raw/`
(`assemble-row.py`, `make-owner-brief.py`, `score-arm.py`, `sync-jsonl.py` — the manifest's §7
digest rows) and reports *"Found 15 errors in 3 files (checked 358 source files)"* against the
clean state's 354. The phase-19 close hit this at its own contract-mandated gate rerun and
recorded it as F1 — routed, not fixed (audits/audit-phase-19-close.md §1). F1's pytest facet WAS
closed at HEAD: the scratch tree now rebuilds `coevo/` from `git ls-files` output instead of
symlinking the live directory (tests/scripts/test_verify_ml_evidence.py:138-156). The mypy facet
is untouched, and the review re-verified the mechanism independently in scratch
(audits/review-2026-08-19/B/tests-ci-tooling.md §2 P1-3: `git check-ignore` hits, `ruff check .`
clean, `mypy .` errors). The fence has to be stated in `pyproject.toml`, because a `.gitignore`
fences `git add`, not a type checker — and docs/artifacts.md:58-69 currently states the `.gitignore`
half as though it were the whole guarantee.

The second half is the environment the suite runs in. tests/conftest.py:57-61 is the only env
guard in 4,621 default-tier tests: one `monkeypatch.setenv(ENV_PROVIDER, PROVIDER_FAKE)`, against
43 distinct `AILIBI_*` names in the tracked `.py`/`.sh` tree (re-counted at HEAD: 43). Review-
measured: `AILIBI_MAX_COST_USD=0.001` alone fails 2 tests in tests/eval/test_balance_eval.py
(*"LLM budget exceeded on cost_usd: current=0.0 + delta=0.072942 > cap=0.001"*), and a realistic
13-variable operator environment over `tests/api tests/scripts tests/eval` gives **10 failed, 1541
passed**. The loud direction is a spurious red for anyone who has ever exported a documented knob;
the silent direction is worse — an ambient value that makes a test pass which would otherwise fail
is undetectable. The conftest's own opening docstring diagnoses exactly this failure class and
then fixes one variable instead of the category, and three modules have since hand-rolled the
categorical fix locally (tests/scripts/test_record_ml_corpus.py:117-129,
tests/scripts/test_refresh_samples.py:537, tests/api/test_replay_loader.py:959-964). Promote the
pattern to the root conftest and every machine's suite runs in CI's environment, which exports
none of these.

The allow-list is where this task can do harm, so it is specified rather than left to taste. Three
families are opt-in BY environment variable — `AILIBI_RUN_REAL_PROVIDER_TESTS`,
`AILIBI_RUN_OLLAMA_TESTS`, `AILIBI_RUN_PERF_BENCHMARK`. Each is read by a module-level `skipif` at
import time AND re-read at call time by a meta-test that asserts the two agree
(tests/llm/test_client.py:619 + :647; tests/llm/test_ollama_client.py:845 + :879;
tests/eval/test_performance.py:30 + :72), so a naive namespace clear turns all three red the moment
an operator exports a gate. The gate keys therefore survive the clear unconditionally; the
credentials and endpoints those families read at call time (`ANTHROPIC_API_KEY`,
`FEATHERLESS_API_KEY`, `AILIBI_LLM_MEETING_MODEL`, `AILIBI_OLLAMA_HOST` — tests/llm/test_real_provider.py:62
and :664-668, tests/llm/test_ollama_client.py:897) survive only while their gate reads `1`. A stray
API key with the gates off is cleared, which is the safety direction: no test can fall into a paid
path from ambient state.

Nothing about game behaviour moves. The by-product is that the subprocess families which hand
`dict(os.environ)` to a child (tests/scripts/test_verify_samples.py:152, :184,
tests/api/test_cwd_independence.py:62, tests/scripts/test_verify_ml_evidence.py:176) inherit the
cleaned parent environment for free — which is where the review's 10 failures lived. This task is
also the precondition for running the suite in parallel: a shared, ambient-dependent process
environment is not parallel-safe, and the task that lands `pytest-xdist` sits directly downstream.

**Files in scope:**
- pyproject.toml; ([tool.mypy] exclude gains the two restore destinations)
- tests/conftest.py; (an autouse session fixture that clears/pins the whole AILIBI_* namespace to the documented bare defaults, with an allow-list for the opt-in gates)
- tests/scripts/test_verify_ml_evidence.py; (if its scratch-tree case still couples to the restored payload — make it independent of the checkout state)
- docs/artifacts.md; (the restore + gate sentence made true)
- tests/test_env_hermeticity.py; (new: asserts the in-process AILIBI_* surface the fixture guarantees)

**Files NOT in scope:**
- scripts/fetch_evidence.sh (the restore is correct; the gate's walkers are the defect — the new test READS its destination assignments, never edits them)
- training/reports/_finalist_eval_raw/ and training/artifacts/coevo/ (operator-machine slate scripts and campaign evidence; not held to the repo bar — excluded from the walk, not fixed, and their restored bytes stay untracked by design)
- scripts/check.sh (its legs are correct as written; the parallel invocation belongs to the xdist task)
- .env.example, README.md (documenting the operator knobs is the first-run-quiet task's item; this task changes what the SUITE reads, not what the docs advertise)
- tests/scripts/test_record_ml_corpus.py, tests/scripts/test_refresh_samples.py, tests/api/test_replay_loader.py (the three hand-rolled cleaners stay: each builds a CHILD env explicitly and remains correct over a clean parent; collapsing them onto the new fixture is a follow-up, not this task)
- tests/llm/, tests/eval/test_performance.py (the opt-in gates are read as evidence and must keep behaving exactly as they do today)
- orchestrator/replay.py, llm/ (read for the live `AILIBI_*` surface; never edited)

**Definition of done:**
- [ ] Verify-then-fix, recorded in the PR: `bash scripts/fetch_evidence.sh` then `uv run mypy .` reproduces the F1 mypy facet at HEAD (quote the error line and the file count), and the same restore then `uv run pytest tests/scripts/test_verify_ml_evidence.py -q` is quoted to show whether the pytest facet is still closed.
- [ ] `[tool.mypy] exclude` covers both destinations `scripts/fetch_evidence.sh` restores into (`training/artifacts/coevo/`, `training/reports/_finalist_eval_raw/`) and swallows no tracked Python: a test in tests/scripts/test_verify_ml_evidence.py derives the two roots from the script's own `COEVO_DEST=`/`SLATE_DEST=` assignments (cross-checked against `verify_ml_evidence.py:110-111`), asserts a path under each is excluded, and asserts the two ADDED alternatives match ZERO paths in `git ls-files '*.py'` (the whole regex cannot: its pre-existing `experiments/lab/` + `design/` alternatives legitimately cover 29 tracked files).
- [ ] That test can fail: it applies its own coverage helper to a deliberately narrowed pattern (the exclude without the two new alternatives) and asserts that pattern does NOT cover the destinations — so a future edit that drops one alternative is caught, not merely described (AGENTS.md craft rule 2).
- [ ] After `bash scripts/fetch_evidence.sh`, `uv run mypy .` prints the same "checked N source files" count as the clean state — the restored `.py` files are outside the walk, not merely error-free — and the full `bash scripts/check.sh` is green in BOTH states (restored, and after `--clean`), with the final line of each run quoted in the PR.
- [ ] tests/conftest.py carries one autouse session fixture that clears every `AILIBI_*` name plus `ANTHROPIC_API_KEY`/`FEATHERLESS_API_KEY` from the process environment and re-pins `AILIBI_LLM_PROVIDER=fake`; the clear is derived BY PREFIX from the live environment (never from a hardcoded list of the 43 names), and the fixture's docstring enumerates the allow-list with the reason each entry is preserved.
- [ ] The allow-list holds: with each of the three opt-in gates exported to `1` in turn, the three marker meta-tests (`uv run pytest tests/llm/test_client.py tests/llm/test_ollama_client.py tests/eval/test_performance.py -k "marker_is_skipif or marker_is_opt_in" -q`) pass; with the gates unset and `ANTHROPIC_API_KEY` exported, a test that prints the in-process environment sees no key — quoted in the PR.
- [ ] Hermeticity is measured, not asserted: with every non-gate `AILIBI_*` name exported to a valid value, `uv run pytest` reports the same passed/skipped/xfailed counts as the bare run, and `AILIBI_MAX_COST_USD=0.001 uv run pytest tests/eval/test_balance_eval.py -q` is green (review-measured today: 2 failed). Both invocations and both outputs go in the PR Summary.
- [ ] tests/scripts/test_verify_ml_evidence.py is independent of the checkout state: the whole file is green with the evidence restored AND after `--clean`, both quoted; any case still reading the working tree where it means the committed inventory is switched to the `git ls-files` pattern already used at :138-156.
- [ ] docs/artifacts.md states the relationship truthfully in the class-(c) rule (:58-69) and beside the restore commands (:116-122): restored bytes are outside `git add` (the per-destination `.gitignore`) AND outside the strict type gate (the pyproject exclude), so the documented restore and the documented gate compose in either state. No sentence claims or implies that the `.gitignore` alone makes the restore gate-safe.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Pre-flight checklist
- Read AGENTS.md, the architecture routing it names, and the task section before editing.
- Inspect the current implementation before editing.
- Identify the existing local patterns for the files in scope and follow them.
- Re-verify every file:line anchor the contract cites at HEAD before editing; if an anchor has moved, record the true location under `## Decisions` — never edit from a stale line number.
- Grep every consumer of each symbol, path, or constant you will change (the blast radius); if a hit lies outside the files in scope, stop and ask rather than widening scope silently.

## Craft rules (AGENTS.md "Craft rules" — non-negotiable for every file you touch)
- Lead with intent: a docstring or comment states what the code does and why, now; provenance (task ids, audit paths) is at most one trailing line. Do not narrate history in source.
- A gate must be able to fail: every new test or check that guards an invariant ships with a planted or perturbed case proving it bites, and checks the semantics it claims, not only the shape.
- Retire means delete: when a lever graduates or a branch dies, delete the resolver, the parameter, the branch and the tests that pin them; keep only the stamp key and one history line.
- No internal dialect on user-facing surfaces: UI copy, rendered game prompts, spoken text and README carry no task or audit ids, no threshold arithmetic, and no undefined jargon.
- Claims are verifiable-shaped: a doc claim names the mechanism that enforces it; a number is recomputed from committed bytes and its command goes in the PR.

## Constraints and non-goals
Do not modify DESIGN.md.
Do not modify AGENT_IMPLEMENTATION.md.
Do not modify tasks/phase-*.md unless this task explicitly lists those files in scope.
Do not implement work outside this task.

## Verification checklist
- Run every command listed in the Definition of done.
- If the contract carries a `**Measurement:**` field, run that command and paste its output into the PR's `## Summary`; a Measurement that cannot be run is reported under `## Questions`, never asserted.
- Run `git diff --name-only` and confirm the diff stays within scope.
- If any Definition of done item is unchecked, report it explicitly in the PR description instead of declaring the task complete.

## Decisions vs questions
- If something is **ambiguous and blocking** (you cannot make a reasonable choice without further information): stop, open a draft PR, add a `## Questions` section, request review.
- If something is **ambiguous but resolvable by judgment** (a default value, a tie-break, a naming choice): document the choice in a `## Decisions` section in the PR description and proceed.

## Output expectation
Open a PR from branch `phase-20-gate-hermeticity` with a title like `task 20.17: gate hermeticity: the documented restore and the documented gate stop excluding each other; the env surface is pinned`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing audits/review-2026-08-19/B/tests-ci-tooling.md §2 P1-3 (C-96, the mypy facet) + §2 P1-2 (C-35, the env surface), §1 items 7-8, §6 recommendations 2-3, Appendix (both repro commands); audits/review-2026-08-19/B/collated-findings.md rows C-96 + C-35; audits/review-2026-08-19/D/FINAL-synthesis.md §4 wave-1 row 1.11; audits/review-2026-08-19/D/cross-track-map.md rows C-96 + C-35; audits/audit-phase-19-close.md §1 F1 (both facets, quoted); pyproject.toml:45-61 (`[tool.mypy]`, the exclude regex at :61); scripts/fetch_evidence.sh:44-45 (`COEVO_DEST` + `SLATE_DEST`), :347-372 (`write_gitignore`); scripts/verify_ml_evidence.py:110-111 (the same two destinations as constants); tests/scripts/test_verify_ml_evidence.py:138-156 (F1's pytest facet, fixed at HEAD by rebuilding coevo/ from `git ls-files`); tests/conftest.py:1-38 (the diagnosis of exactly this failure class) + :57-61 (the one-variable guard); the three hand-rolled cleaners tests/scripts/test_record_ml_corpus.py:117-129, tests/scripts/test_refresh_samples.py:537, tests/api/test_replay_loader.py:959-964; the three opt-in gates tests/llm/test_client.py:619 + :647, tests/llm/test_ollama_client.py:845 + :879 + :897, tests/eval/test_performance.py:30 + :72; tests/experiments/test_torch_probe_excluded.py:92-112 (`test_mypy_exclude_covers_the_probe_directory`, the precedent for pinning a mypy exclude both ways); docs/artifacts.md:58-69 (the `.gitignore` rule) + :116-122 (the restore commands); scripts/check.sh:15-21 (the gate legs); AGENTS.md craft rules 2, 5, 6), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
