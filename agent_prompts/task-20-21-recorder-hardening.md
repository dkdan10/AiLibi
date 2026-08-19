# Agent Prompt — 20.21 The recorder's worker paths get real coverage before the record

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-20.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 20.21 — The recorder's worker paths get real coverage before the record, anchored to C-74 (audits/review-2026-08-19/B/collated-findings.md row C-74; audits/review-2026-08-19/B/eval-and-scripts.md §2 P1 F1 + §1 item 8 + §5 item 2; audits/review-2026-08-19/B/tests-ci-tooling.md §3 "Script gigantism in the tooling tier" :530-532); audits/review-2026-08-19/D/FINAL-synthesis.md §4 wave-2 row 2.0 (:251) + §6 note 2 (:420, "the record itself runs on 917 lines of untested Bash"); audits/review-2026-08-19/D/cross-track-map.md row C-74 + the "1-pre" row ("the record runs on untested Bash"); audits/review-2026-08-19/B/verdicts.md C-6 verdict (**"lock-race attribution refuted"** — replays land via a per-seed private stage + atomic `mv -f`, so the recorder race cannot truncate a replay; the exposure is a lost MANIFEST row, not a truncated file). Re-verified at HEAD: `scripts/refresh_samples.sh` = 917 lines, `set -euo pipefail` at :27; the provider remap comment :256-268 and its code `PROVIDER="$(...)"` :289 + `case` :290-297 with `anthropic | fake) PROVIDER="anthropic" ;;` at :293; the ANTHROPIC_API_KEY preflight :490-495; the Task-18.12 substrate-lever preflight :497-534 (the 20.33 hook point); `export AILIBI_LLM_PROVIDER="$PROVIDER"` :566; the stage mktemp + EXIT trap :611-612; `_acquire_lock` :639-659 with a bare `$BASHPID` at :657; `_release_lock` :661; `claim_next_seed` :666-680; `record_one_seed` :689-795 (the guarded stage mktemp :701-706, the atomic `mv -f` :739-746, the lock-held `_manifest_writer.py update` :760-775); `run_worker` :801-809; the pool spawn/join :811-836; the `.failed` fail-loud check :838-842. `tests/scripts/test_refresh_samples.py` = 915 lines / 59 `def test_`, every one `--dry-run` (module docstring :3-6; the review's quoted example `assert "[dry-run] seed workers: 2 parallel" in proc.stdout` at :228). The un-back-ported hardening: `scripts/record_ml_corpus.sh:994-999` + `:1017` uses `${BASHPID:-$$}` with the recorded Bash-3.2 degradation, ledgered at audits/audit-phase-18-close.md §7 row 5 and training/README.md §6 row 5. `scripts/_manifest_writer.py::update_manifest` :446-472 is a whole-file read-modify-write with `_atomic_write_text` :361-385.. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-20.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-20-recorder-hardening`
**Depends on:** none (root)
**Section refs:** C-74 (audits/review-2026-08-19/B/collated-findings.md row C-74; audits/review-2026-08-19/B/eval-and-scripts.md §2 P1 F1 + §1 item 8 + §5 item 2; audits/review-2026-08-19/B/tests-ci-tooling.md §3 "Script gigantism in the tooling tier" :530-532); audits/review-2026-08-19/D/FINAL-synthesis.md §4 wave-2 row 2.0 (:251) + §6 note 2 (:420, "the record itself runs on 917 lines of untested Bash"); audits/review-2026-08-19/D/cross-track-map.md row C-74 + the "1-pre" row ("the record runs on untested Bash"); audits/review-2026-08-19/B/verdicts.md C-6 verdict (**"lock-race attribution refuted"** — replays land via a per-seed private stage + atomic `mv -f`, so the recorder race cannot truncate a replay; the exposure is a lost MANIFEST row, not a truncated file). Re-verified at HEAD: `scripts/refresh_samples.sh` = 917 lines, `set -euo pipefail` at :27; the provider remap comment :256-268 and its code `PROVIDER="$(...)"` :289 + `case` :290-297 with `anthropic | fake) PROVIDER="anthropic" ;;` at :293; the ANTHROPIC_API_KEY preflight :490-495; the Task-18.12 substrate-lever preflight :497-534 (the 20.33 hook point); `export AILIBI_LLM_PROVIDER="$PROVIDER"` :566; the stage mktemp + EXIT trap :611-612; `_acquire_lock` :639-659 with a bare `$BASHPID` at :657; `_release_lock` :661; `claim_next_seed` :666-680; `record_one_seed` :689-795 (the guarded stage mktemp :701-706, the atomic `mv -f` :739-746, the lock-held `_manifest_writer.py update` :760-775); `run_worker` :801-809; the pool spawn/join :811-836; the `.failed` fail-loud check :838-842. `tests/scripts/test_refresh_samples.py` = 915 lines / 59 `def test_`, every one `--dry-run` (module docstring :3-6; the review's quoted example `assert "[dry-run] seed workers: 2 parallel" in proc.stdout` at :228). The un-back-ported hardening: `scripts/record_ml_corpus.sh:994-999` + `:1017` uses `${BASHPID:-$$}` with the recorded Bash-3.2 degradation, ledgered at audits/audit-phase-18-close.md §7 row 5 and training/README.md §6 row 5. `scripts/_manifest_writer.py::update_manifest` :446-472 is a whole-file read-modify-write with `_atomic_write_text` :361-385.
**Complexity:** Medium
**Record impact:** none
**Measurement:** `uv run pytest tests/scripts/test_refresh_samples.py -q` green with the end-to-end and concurrency cases present; the fake-provider `--seeds 0,1` end-to-end case records two replays, writes two MANIFEST rows, and `bash scripts/verify_samples.sh <scratch dir>` exits 0, in < 30 s wall (a fake 4p1i game measured 0.4 s at HEAD, so the whole case is seconds); the `bash -x` trace quoted in the PR names `_acquire_lock`, `claim_next_seed`, `record_one_seed` and `run_worker`.

The project's canonical baseline is produced by 917 lines of Bash whose worker pool has
never been executed by a test. All 59 tests in `tests/scripts/test_refresh_samples.py` are
`--dry-run` echo assertions; not one reaches `run_worker`, `claim_next_seed`,
`_acquire_lock` or `record_one_seed`, because `AILIBI_LLM_PROVIDER=fake` — the only
hermetic provider — is remapped to `anthropic` at `refresh_samples.sh:293`, which then
demands a real key at :490-495 and spends. Three review reports reached this
independently (audits/review-2026-08-19/B/eval-and-scripts.md §2 F1;
audits/review-2026-08-19/B/tests-ci-tooling.md §3 "Script gigantism"; the cross-track row in
audits/review-2026-08-19/D/cross-track-map.md), and the synthesis routes it as the FIRST
item of wave 2 — before the record — precisely because ~23 h of operator wall and the
comparator every Phase-20 number is measured against ride on it
(audits/review-2026-08-19/D/FINAL-synthesis.md §4 row 2.0 and §6 note 2).

The gap is not hypothetical. Drafting this contract, a single execution of the real path
found a live defect that the dry-run suite cannot see: `_acquire_lock` writes its owner PID
with a bare `"$BASHPID"` (`refresh_samples.sh:657`) under `set -euo pipefail` (:27), and
`$BASHPID` does not exist in Bash 3.2 — the only `bash` on the owner's machine
(`/bin/bash` and PATH `bash` are both GNU bash 3.2.57(1)-release, arm64-apple-darwin24).
Repro at HEAD, into a scratch `AILIBI_SAMPLE_DIR`, single-worker path, after the roster
descriptor is written and before any provider call: `scripts/refresh_samples.sh: line 657:
BASHPID: unbound variable`. Every real refresh on the host interpreter dies at the first
seed claim. It fails loud rather than corrupting anything, which is the doctrine working —
but the script is unusable on stock macOS bash and no gate says so. The identical hazard
was already found and fixed once in the sibling recorder: `record_ml_corpus.sh:1017` uses
`${BASHPID:-$$}` and its comment block :994-999 records exactly why (the
dead-owner-detection degradation on 3.2 is a ledgered, accepted limitation —
audits/audit-phase-18-close.md §7 row 5, training/README.md §6 row 5). This is the same
shape as C-6's finding: the hardening exists, un-back-ported.

One review claim needs correcting in flight, and this contract corrects it rather than
inheriting it. The recorder lock-race does NOT produce truncated replay files.
audits/review-2026-08-19/B/verdicts.md's C-6 verdict refuted that attribution: the mutex
guards `MANIFEST.md` only, replays are staged per-seed in a private `mktemp -d` and land
via an atomic same-filesystem `mv -f` (`refresh_samples.sh:739-746`), and every row is
flushed. The real concurrency exposure is a LOST MANIFEST ROW:
`_manifest_writer.py::update_manifest` (:446-472) parses the whole manifest, mutates one
seed's row and atomically replaces the file, so two workers updating different seeds
without serialization leave one row silently missing — and a missing row is fatal at the
next gate (`verify_samples.sh` refuses an unmanifested sample: "replay-seed-N.jsonl is
present but not listed in MANIFEST.md"). The lock at :760-775 is what prevents it, and
nothing pins that the lock is load-bearing. This task pins it.

The hermetic path is cheap and already proven to work end to end: a fake-provider 4p1i
game records in 0.4 s, `_manifest_writer.py update` writes a well-formed row from it
(model column carries the fake model, `cost_usd 0.0000`), and `verify_samples.sh`
reconstructs it byte-identically. What is missing is only the script's permission to run
that way, plus a guard strong enough that the permission can never become a way to write
fake bytes over a committed set. The safety property the remap was protecting is
specifically "an UNSET `AILIBI_LLM_PROVIDER` must never silently record fake output over
real samples" (:559-566); that property is preserved untouched here — unset/empty still
resolves to `anthropic`. Only an EXPLICIT `fake`, targeting a sample dir outside the
repo's committed replay tree, is newly allowed.

**Files in scope:**
- scripts/refresh_samples.sh; (the fake-provider path runs end-to-end as a real worker; the lock/append race fixed or documented with a guard; the 20.33 preflight hook point kept)
- tests/scripts/test_refresh_samples.py; (a fake-provider end-to-end run of 2 seeds into a tmp dir exercising run_worker/_acquire_lock/record_one_seed and the MANIFEST writer; a concurrent two-worker lock test)
- scripts/_manifest_writer.py; (only if the end-to-end run exposes a defect)
- tests/scripts/test_manifest_writer.py

**Files NOT in scope:**
- replays/ (no bytes move — this task records only into scratch dirs and never touches a committed set)
- scripts/record_ml_corpus.sh (the corpus recorder; 20.36 reprises its runbook — the two scripts share the mutex SHAPE, not a function, so mirror any fix there in 20.36, not here)
- orchestrator/replay.py (20.33 registers the Phase-20 levers into the substrate stamp for all levers at once; the preflight here READS `substrate_flag_snapshot()` and must keep doing so unchanged)
- scripts/check.sh (the gate composition is not this task's; the new cases run under the ordinary `uv run pytest`)
- scripts/verify_samples.sh and scripts/_verify_samples.py (used as an assertion, never edited)
- agents/strategic/prompts/ and every `.j2` template (20.31 owns the single Phase-20 prompt-set bump; no prompt bytes move here)

**Definition of done:**
- [ ] Verify-then-fix recorded: before any edit, the `BASHPID: unbound variable` abort is reproduced at HEAD on Bash 3.2 (or the interpreter's version is quoted if it does not reproduce there) and the failing line + the exact stderr are quoted in the PR Summary.
- [ ] `scripts/refresh_samples.sh:657` writes the lock owner as `${BASHPID:-$$}`, carrying the same degradation note `scripts/record_ml_corpus.sh:994-999` already records (on Bash 3.2 every worker shares `$$`, so dead-owner detection degrades to a no-op while the mutex still serializes); a test runs the real worker path under the host `bash` and fails if the unbound-variable abort returns.
- [ ] The provider remap is made EXPLICIT, not removed wholesale: unset/empty `AILIBI_LLM_PROVIDER` still resolves to `anthropic` (the anti-silent-fake guard at `:559-566` is preserved and its comment updated to state the new rule), an explicit `fake` resolves to `fake`, and a `fake` refresh whose resolved `$SAMPLE_DIR` lies inside the repo's `replays/` tree fails loud before any staging, naming the dir and the rule. Both branches are test-pinned, including the refusal against `replays/samples/4p1i` and `replays/samples/9p2i` by name.
- [ ] Under the `fake` provider the ANTHROPIC_API_KEY preflight (:490-495) is skipped (no spend is possible) while the Task-18.12 substrate-lever preflight (:497-534) still runs unchanged — it is provider-independent and it is the hook point 20.33 extends; a test asserts the substrate preflight still fires on the fake path.
- [ ] A new end-to-end test runs the real script (no `--dry-run`) as `--seeds 0,1` with `AILIBI_LLM_PROVIDER=fake` into a scratch `AILIBI_SAMPLE_DIR`/`AILIBI_MANIFEST`, and asserts: both `replay-seed-0.jsonl` and `replay-seed-1.jsonl` land in the sample dir; the MANIFEST holds exactly one row per seed with the fake model and `0.0000` cost; the staging dir is gone (the EXIT trap at :612 fired); and `bash scripts/verify_samples.sh <scratch dir>` exits 0.
- [ ] A concurrency test runs the same end-to-end case with `AILIBI_REFRESH_WORKERS=2` over ≥4 seeds and asserts no row is lost, no seed is recorded twice, exactly one manifest header block is present, and the run exits 0 — i.e. the lock at `:760-775` is what makes the read-modify-write safe. The claim it pins is the LOST-ROW race, not truncated replays (audits/review-2026-08-19/B/verdicts.md's C-6 verdict refuted the truncation attribution); the PR Summary states that correction.
- [ ] The concurrency gate can fail: a perturbation case shows that concurrent `update_manifest` calls WITHOUT the serialization lose a row (drive `scripts/_manifest_writer.py::update_manifest` from two processes, or interleave read-then-write deterministically if the natural race is not reproducible within a bounded retry — ship a deterministic pin, never a flaky one).
- [ ] `run_worker`, `claim_next_seed`, `_acquire_lock` and `record_one_seed` each have ≥1 real (non-dry-run) test path; the PR quotes a `bash -x` trace from the end-to-end case showing all four invoked, and `record_one_seed`'s fail-loud branch is exercised by a deterministic injected failure that ends in exit 1 plus the "INCOMPLETE and must NOT be committed" message (:838-842).
- [ ] The script's CLI is byte-identical: all 59 pre-existing `--dry-run` tests pass unmodified, and any new dry-run output added for the fake path is asserted rather than left unpinned (20.33 adds a preflight and 20.36 runs this script for ~23 h — neither may need to relearn the interface).
- [ ] `scripts/_manifest_writer.py` and `tests/scripts/test_manifest_writer.py` are edited only if the end-to-end run exposes an actual defect; if it does not, the PR says so explicitly and those two files carry no diff.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

Step 1 — reproduce before fixing. Point `AILIBI_SAMPLE_DIR` and `AILIBI_MANIFEST` at a
scratch dir, export `AILIBI_LLM_PROVIDER=fake` and a dummy `ANTHROPIC_API_KEY`, run
`bash scripts/refresh_samples.sh --seeds 0`, and watch it die at :657 before the
tournament call. That is the whole finding in one command, and it is what the dry-run
suite has been unable to see.

Step 2 — the provider gate. Keep the `case` at :290-297 as the single resolution point.
Add a `fake)` arm that leaves `PROVIDER="fake"`, then immediately assert the target:
resolve `$SAMPLE_DIR` to an absolute real path and refuse when it is inside
`$REPO_ROOT/replays`. Prefer a positive comparison over a string prefix that a symlink or
a `..` can defeat — `cd` into the dir in a subshell and `pwd -P`, or compare against
`$REPO_ROOT/replays` with the same `-ef`-style device/inode reasoning the rubric block at
:890 already uses on `SAMPLE_DIR`. Fail with the dir, the rule, and the sentence that
nothing was staged. On the fake arm also skip the key preflight, and set `active_model`
from the fake client's own model id rather than `DEFAULT_MEETING_MODEL`, so no fake row
can ever render as a Sonnet or Featherless row in a MANIFEST.

Step 3 — the lock. `${BASHPID:-$$}` is the whole fix at :657; copy the wording of
`record_ml_corpus.sh:994-999` rather than inventing a second explanation of the same
degradation, and keep the pointer to the ledger rows (audit-phase-18-close.md §7 row 5,
training/README.md §6 row 5). Do not switch to `flock`: it is absent on stock macOS and
the mkdir mutex is the portable choice both recorders already made.

Step 4 — the tests. Reuse the file's existing `_run` and `_clean_env` helpers and add a
fixture that builds a scratch set dir with `AILIBI_SAMPLE_DIR`, `AILIBI_MANIFEST` and the
default 4-player / 1-impostor / 1-task roster. Watch the roster: the loader reconstructs
from `roster.json`, so a run whose `--tasks-per-crewmate` disagrees with the descriptor
verifies as a tick-0 hash divergence rather than a missing file — let the script write the
descriptor itself and do not pass roster overrides unless the test is about them. Two
seeds are enough for the end-to-end case (~0.4 s each under the fake client); use ≥4 for
the two-worker case so the queue actually hands work to both. For the fail-loud injection,
the cheapest deterministic one is a sample dir made read-only before the run with its
`roster.json` already written and agreeing: `mkdir -p` and the descriptor step no-op, the
tournament records into the writable stage, and the `mv -f` at :739-746 fails into the
`.failed` path and exit 1. Skip that case when the test process is root, where mode 0555
does not block a write.

Step 5 — proving coverage. Run the end-to-end case a second time with `BASH_XTRACEFD`
pointed at a file (or plain `bash -x`) and assert the trace contains the four function
invocations; that is the quotable evidence the DoD asks for, and it beats asserting on
progress strings that a later refactor may reword.

Step 6 — what not to touch. The substrate-lever preflight at :497-534 stays exactly as it
is, including which levers it names: 20.33 extends that block for the whole Phase-20 lever
slate at once, and a second author editing it here would collide. Likewise leave the
`build_sample_report` / rubric tail (:864-917) alone — the audits/experiments shell-out
that F1 also flags is a separate finding and is not in this scope.

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
Open a PR from branch `phase-20-recorder-hardening` with a title like `task 20.21: the recorder's worker paths get real coverage before the record`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing C-74 (audits/review-2026-08-19/B/collated-findings.md row C-74; audits/review-2026-08-19/B/eval-and-scripts.md §2 P1 F1 + §1 item 8 + §5 item 2; audits/review-2026-08-19/B/tests-ci-tooling.md §3 "Script gigantism in the tooling tier" :530-532); audits/review-2026-08-19/D/FINAL-synthesis.md §4 wave-2 row 2.0 (:251) + §6 note 2 (:420, "the record itself runs on 917 lines of untested Bash"); audits/review-2026-08-19/D/cross-track-map.md row C-74 + the "1-pre" row ("the record runs on untested Bash"); audits/review-2026-08-19/B/verdicts.md C-6 verdict (**"lock-race attribution refuted"** — replays land via a per-seed private stage + atomic `mv -f`, so the recorder race cannot truncate a replay; the exposure is a lost MANIFEST row, not a truncated file). Re-verified at HEAD: `scripts/refresh_samples.sh` = 917 lines, `set -euo pipefail` at :27; the provider remap comment :256-268 and its code `PROVIDER="$(...)"` :289 + `case` :290-297 with `anthropic | fake) PROVIDER="anthropic" ;;` at :293; the ANTHROPIC_API_KEY preflight :490-495; the Task-18.12 substrate-lever preflight :497-534 (the 20.33 hook point); `export AILIBI_LLM_PROVIDER="$PROVIDER"` :566; the stage mktemp + EXIT trap :611-612; `_acquire_lock` :639-659 with a bare `$BASHPID` at :657; `_release_lock` :661; `claim_next_seed` :666-680; `record_one_seed` :689-795 (the guarded stage mktemp :701-706, the atomic `mv -f` :739-746, the lock-held `_manifest_writer.py update` :760-775); `run_worker` :801-809; the pool spawn/join :811-836; the `.failed` fail-loud check :838-842. `tests/scripts/test_refresh_samples.py` = 915 lines / 59 `def test_`, every one `--dry-run` (module docstring :3-6; the review's quoted example `assert "[dry-run] seed workers: 2 parallel" in proc.stdout` at :228). The un-back-ported hardening: `scripts/record_ml_corpus.sh:994-999` + `:1017` uses `${BASHPID:-$$}` with the recorded Bash-3.2 degradation, ledgered at audits/audit-phase-18-close.md §7 row 5 and training/README.md §6 row 5. `scripts/_manifest_writer.py::update_manifest` :446-472 is a whole-file read-modify-write with `_atomic_write_text` :361-385.), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
