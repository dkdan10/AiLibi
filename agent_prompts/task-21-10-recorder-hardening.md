# Agent Prompt — 21.10 The recorders earn the next record: the dead-owner streak, a tested recording engine, the version pin's CLI, and the loader guard sweep

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-21.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 21.10 — The recorders earn the next record: the dead-owner streak, a tested recording engine, the version pin's CLI, and the loader guard sweep, anchored to B-18 [ADJUSTED P2, defect], B-21 [CONFIRMED P1, quality-debt], B-19 [ADJUSTED P3, design-limitation], B-48 [CONFIRMED P2, defect], B-23 [ADJUSTED P2, defect — listing half only], B-51 [CONFIRMED P2, defect] and B-52 [CONFIRMED P2, defect] — all seven in audits/review-2026-08-26/B/collated-findings.md (B-18 :1069, B-19 :1147, B-21 :1266, B-23 :1382, B-48 :2532, B-51 :2689, B-52 :2744), read with their verifier evidence and verifier notes, which BIND the claims below. The precedent this task back-ports from is Task 20.21 (tasks/phase-20.md:3312) and its follow-up `28599ec3` ("task 20.21 follow-up: the lock's dead-owner verdict must survive a release racing the probe", #388); the routing that dropped is tasks/phase-20.md:3384 ("mirror any fix there in 20.36, not here") against `efcd43b8` (20.36, #389), which edited scripts/record_ml_corpus.sh without the mirror, and audits/audit-phase-20-close.md:224, which records 20.21 VERIFIED and names no open mirror. Anchors re-verified at HEAD `4002f19b` (the Wave-0 audit commit; the code tree is unchanged from the registers' `d8ec0a1c`): scripts/record_ml_corpus.sh is 1,307 lines with `record_set()` at :929 closing at :1284 and the four pool functions NESTED inside it — `acquire_lock` :1032-1050 (`local owner` only; ERROR + `touch "$stage_dir/.failed"` + `return 1` on the FIRST dead probe; owner written `${BASHPID:-$$}` at :1049), `release_lock` :1051, `claim_next_seed` :1055-1066, `record_one_seed` :1073, `run_worker` :1162, with `freeze_manifest` (top-level, :740) reachable only from :1279; the sibling streak is scripts/refresh_samples.sh:776-817 `_acquire_lock` (`local owner last_dead_owner dead_polls`, the race stated verbatim at :791-797, the increment at :798-803, `if [[ "$dead_polls" -ge 10 ]]` at :804); contention is the default (`REFRESH_WORKERS="${AILIBI_REFRESH_WORKERS:-2}"` at :320) and the claim mints its transient owner from a command substitution (`seed="$(claim_next_seed)"` at :1166); `grep -c 'def test_' tests/scripts/test_record_ml_corpus.py tests/scripts/test_refresh_samples.py` → 54 / 82 and the four pool names appear in the corpus recorder's test file only as `test_dry_run_worker_count_is_overridable` (:388), while the sibling's family drives them by name (tests/scripts/test_refresh_samples.py:1055-1056, the `bash -x` assertion list :1358-1361, the verbatim-extraction `_lock_driver` :1630-1646 with its two streak cases at :1659 and :1685); the provider refusal is scripts/record_ml_corpus.sh:839-843 pinned by tests/scripts/test_record_ml_corpus.py:442, and the sibling's hermetic seam is scripts/refresh_samples.sh:616-640 (the fake arm's `replays/` target refusal) with `DEFAULT_FAKE_MODEL="fake-meeting"` at :403 and the `active_model` resolution at :703-719 used at :928; scripts/record_ml_corpus.sh:156 is `REQUIRED_PROMPT_VERSIONS`, asserted forward by `check_prompt_version_registry` :499-520 and backward by `check_recorded_prompt_versions` :530, while `grep -n add_argument scripts/validity_gate.py` returns exactly four (:68 `replay_set_dir`, :73 `--json`, :78 `--expected-model`, :86 `--require-zero-cost`) against `eval/validity.py:905` and `:1142`, which both accept `expected_prompt_versions`, thread it at :1240 and turn it into an exact violation at :1001-1012 — and scripts/record_ml_corpus.sh:825 prints the acceptance line without it; scripts/verify_ml_evidence.py:143-155 `WALK_SKIP_DIRS` has no `.claude` and no nested-checkout rule, consumed once at :910, and `run_sidecars` (:980) fails on the raw walk (`in_tree` :994-996 → `status="FAIL" if in_tree_failures` :1021) while the inventory row below it does scope to `git_tracked_sidecars` (:1054); api/replay_loader.py:1101-1103 places `_assert_substrate_matches` (:603-651) inside `_walk` (:1069) only, `list_replays` (:753-785) and `cost_summary` (:806-844) both catch `(ReplayLog.CorruptedFileError, ValueError)` and `ReplaySubstrateMismatchError` subclasses `RuntimeError` (:354); the diff at :631-635 and the error's own at :387-391 both iterate `SUBSTRATE_FLAG_KEYS`, never `recorded`'s keys, mirrored at orchestrator/replay.py:646-648 in `retired_levers_stamped_off` (:623, docstring :626-642, whose registry is append-only by construction — orchestrator/replay.py:585-589); api/main.py:231 is the ONLY `add_exception_handler` call, for `ReplayStateMismatchError` alone (`_handle_state_mismatch` :157-165), while all three error docstrings promise the same body (api/replay_loader.py:339, :373, :441). Re-measured here, on the owner's checkout: the sidecar walk is 817 files, 758 of them under `.claude/worktrees/` (14 checkouts), 59 outside, against `git ls-files '*.sha256'` = 59 tracked — 93% of the failing row's input is not in this checkout's index.. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-21.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-21-recorder-hardening`
**Depends on:** 21.3, 21.4, 21.5, 21.7
**Section refs:** B-18 [ADJUSTED P2, defect], B-21 [CONFIRMED P1, quality-debt], B-19 [ADJUSTED P3, design-limitation], B-48 [CONFIRMED P2, defect], B-23 [ADJUSTED P2, defect — listing half only], B-51 [CONFIRMED P2, defect] and B-52 [CONFIRMED P2, defect] — all seven in audits/review-2026-08-26/B/collated-findings.md (B-18 :1069, B-19 :1147, B-21 :1266, B-23 :1382, B-48 :2532, B-51 :2689, B-52 :2744), read with their verifier evidence and verifier notes, which BIND the claims below. The precedent this task back-ports from is Task 20.21 (tasks/phase-20.md:3312) and its follow-up `28599ec3` ("task 20.21 follow-up: the lock's dead-owner verdict must survive a release racing the probe", #388); the routing that dropped is tasks/phase-20.md:3384 ("mirror any fix there in 20.36, not here") against `efcd43b8` (20.36, #389), which edited scripts/record_ml_corpus.sh without the mirror, and audits/audit-phase-20-close.md:224, which records 20.21 VERIFIED and names no open mirror. Anchors re-verified at HEAD `4002f19b` (the Wave-0 audit commit; the code tree is unchanged from the registers' `d8ec0a1c`): scripts/record_ml_corpus.sh is 1,307 lines with `record_set()` at :929 closing at :1284 and the four pool functions NESTED inside it — `acquire_lock` :1032-1050 (`local owner` only; ERROR + `touch "$stage_dir/.failed"` + `return 1` on the FIRST dead probe; owner written `${BASHPID:-$$}` at :1049), `release_lock` :1051, `claim_next_seed` :1055-1066, `record_one_seed` :1073, `run_worker` :1162, with `freeze_manifest` (top-level, :740) reachable only from :1279; the sibling streak is scripts/refresh_samples.sh:776-817 `_acquire_lock` (`local owner last_dead_owner dead_polls`, the race stated verbatim at :791-797, the increment at :798-803, `if [[ "$dead_polls" -ge 10 ]]` at :804); contention is the default (`REFRESH_WORKERS="${AILIBI_REFRESH_WORKERS:-2}"` at :320) and the claim mints its transient owner from a command substitution (`seed="$(claim_next_seed)"` at :1166); `grep -c 'def test_' tests/scripts/test_record_ml_corpus.py tests/scripts/test_refresh_samples.py` → 54 / 82 and the four pool names appear in the corpus recorder's test file only as `test_dry_run_worker_count_is_overridable` (:388), while the sibling's family drives them by name (tests/scripts/test_refresh_samples.py:1055-1056, the `bash -x` assertion list :1358-1361, the verbatim-extraction `_lock_driver` :1630-1646 with its two streak cases at :1659 and :1685); the provider refusal is scripts/record_ml_corpus.sh:839-843 pinned by tests/scripts/test_record_ml_corpus.py:442, and the sibling's hermetic seam is scripts/refresh_samples.sh:616-640 (the fake arm's `replays/` target refusal) with `DEFAULT_FAKE_MODEL="fake-meeting"` at :403 and the `active_model` resolution at :703-719 used at :928; scripts/record_ml_corpus.sh:156 is `REQUIRED_PROMPT_VERSIONS`, asserted forward by `check_prompt_version_registry` :499-520 and backward by `check_recorded_prompt_versions` :530, while `grep -n add_argument scripts/validity_gate.py` returns exactly four (:68 `replay_set_dir`, :73 `--json`, :78 `--expected-model`, :86 `--require-zero-cost`) against `eval/validity.py:905` and `:1142`, which both accept `expected_prompt_versions`, thread it at :1240 and turn it into an exact violation at :1001-1012 — and scripts/record_ml_corpus.sh:825 prints the acceptance line without it; scripts/verify_ml_evidence.py:143-155 `WALK_SKIP_DIRS` has no `.claude` and no nested-checkout rule, consumed once at :910, and `run_sidecars` (:980) fails on the raw walk (`in_tree` :994-996 → `status="FAIL" if in_tree_failures` :1021) while the inventory row below it does scope to `git_tracked_sidecars` (:1054); api/replay_loader.py:1101-1103 places `_assert_substrate_matches` (:603-651) inside `_walk` (:1069) only, `list_replays` (:753-785) and `cost_summary` (:806-844) both catch `(ReplayLog.CorruptedFileError, ValueError)` and `ReplaySubstrateMismatchError` subclasses `RuntimeError` (:354); the diff at :631-635 and the error's own at :387-391 both iterate `SUBSTRATE_FLAG_KEYS`, never `recorded`'s keys, mirrored at orchestrator/replay.py:646-648 in `retired_levers_stamped_off` (:623, docstring :626-642, whose registry is append-only by construction — orchestrator/replay.py:585-589); api/main.py:231 is the ONLY `add_exception_handler` call, for `ReplayStateMismatchError` alone (`_handle_state_mismatch` :157-165), while all three error docstrings promise the same body (api/replay_loader.py:339, :373, :441). Re-measured here, on the owner's checkout: the sidecar walk is 817 files, 758 of them under `.claude/worktrees/` (14 checkouts), 59 outside, against `git ls-files '*.sha256'` = 59 tracked — 93% of the failing row's input is not in this checkout's index.
**Complexity:** Medium
**Record impact:** none — every edit here is to a recorder, a gate, a loader guard or a test. No prompt template, no detector, no rendered byte moves, and nothing under `replays/` is written: the hermetic recording family records only into a scratch corpus root.
**Measurement:** `uv run pytest tests/scripts/test_record_ml_corpus.py tests/scripts/test_validity_gate_cli.py tests/scripts/test_verify_ml_evidence.py tests/api/test_replay_loader.py tests/api/test_main.py tests/orchestrator/test_replay.py -q` green, with the PR quoting a `bash -x` trace from the hermetic case naming `acquire_lock`, `claim_next_seed`, `record_one_seed` and `run_worker`; `uv run python scripts/verify_ml_evidence.py --only sidecars` reports the IN-TREE row over the checkout's own sidecars only (59 on the drafting machine, down from 817) with the 758 nested-worktree files gone from the row that can FAIL; `uv run python scripts/validity_gate.py replays/samples/9p2i --expected-prompt-versions "$(uv run python -c 'from orchestrator.game import PROMPT_VERSION_SETS; print(",".join(f"{k}={v}" for k,v in sorted(PROMPT_VERSION_SETS["qwen3_6_27b"].items())))')"` exits 0 on the committed set and exits 1 on a deliberately wrong pin.

The next record runs this machinery. Task 21.15 re-records four sets on the corrected
substrate with `scripts/record_ml_corpus.sh` for two of the four legs — the same script
whose ~355-line recording engine (`record_set`, :929-1284) executes in none of its 54
tests, and whose lock declares the whole run failed on ONE dead-owner probe. Both facts
are known and both were routed: the streak fix landed in `scripts/refresh_samples.sh` at
`28599ec3` with the commit body promising "Same fix for the twin lock in
record_ml_corpus.sh", the mirror was descoped to Task 20.36 per tasks/phase-20.md:3384,
and 20.36 merged (`efcd43b8`, #389) having edited the file without it. This task executes
the dropped route before the recorder is asked to run for another ~19 hours.

The race is structural, not hypothetical. `claim_next_seed` (:1055-1066) takes and releases
the lock inside itself, and its only call site is a command substitution —
`seed="$(claim_next_seed)"` at :1166 — so `${BASHPID:-$$}` writes the substitution
subshell's pid as the owner, `release_lock` removes the owner file, and that pid dies
microseconds later. A waiter that `cat`s the owner just before the release and runs
`kill -0` just after sees a dead pid, and `acquire_lock` at :1040-1044 immediately
declares the set incomplete. Two workers contend on every seed claim and every MANIFEST
merge by default (:320). The sibling's comment at scripts/refresh_samples.sh:791-797 names
this exact shape ("a seed-claim command-substitution subshell whose pid dies with the
claim") because it fired three times in CI on `test_two_workers_lose_no_manifest_row`
(PRs #369/#372/#378). The verifier's correction is carried here rather than the finder's
framing: the blast radius is a spurious abort plus operator restart latency, not the leg —
scripts/record_ml_corpus.sh:991 prints a resume line off a provenance-checked skip-scan
(:952-990), each seed lands by an atomic `mv` from a private stage, and the `.failed`
sentinel lives under a per-run `mktemp` stage dir. That is why this is P2 and not P1, and
the contract says so rather than inheriting a severity it cannot support.

The reason the mirror could drop unnoticed is B-21, and it is the larger half. Every one
of the 54 tests stops before a seed stages: the deepest two (`:693-724`, `:898-926`) fail
at the roster pin (:966-975), upstream of the seed-list build, the stage `mktemp` and the
pool. The four pool functions are nested inside `record_set`, so nothing can reach them
without entering it, and `freeze_manifest` is likewise reachable only from :1279. The
sibling recorder got a hermetic family at Task 20.21 that drives exactly these functions
because it was given ONE seam — an explicit `fake` provider whose targets must lie outside
`$REPO_ROOT/replays` (scripts/refresh_samples.sh:616-640). The corpus recorder refuses
every non-featherless provider at :839-843 and has no such seam. This task gives it the
same one, on the same terms, plus the `--seeds N,N,N` subset mode the sibling has carried
since its first version (scripts/refresh_samples.sh:59) — which is what makes a 150-seed
locked range testable in seconds, and what lets a 21.15 operator re-record one bad seed
without a 19-hour leg. Neither seam weakens a freeze: `check_seed_count` (:463) already
refuses to freeze a short set, `check_replay_provenance` (:607) already refuses bytes that
are not baseline provenance, and both run before `freeze_manifest`. The hermetic family
therefore ends at a loud, documented "NOT freezing" refusal with its replays and MANIFEST
rows on disk — which is the honest coverage boundary, and the contract states it instead
of implying the freeze path is exercised. `freeze_manifest` gets its own verbatim-extraction
driver, the pattern tests/scripts/test_refresh_samples.py:1630-1646 already established.

The remaining five are guard-shape repairs, all of them cheap and all of them read by
someone downstream. B-19 survives only as its second half, and the contract carries the
verifier's correction rather than the finding's headline: `scripts/refresh_samples.sh`
carrying no version literal is a DECLARED design decision stated in its own comment
(:552-566, "the registry in orchestrator/game.py is the version authority"), the finding's
supporting quote at :560 is about substrate levers and not versions, and a registry bump is
already caught by two default-tier tests. What is genuinely missing is a CLI surface:
`eval/validity.py` implements `expected_prompt_versions` end to end (:905, :1001-1012,
:1142, :1240) and no operator-facing command can reach it, so the acceptance line both
recorders print (scripts/record_ml_corpus.sh:825) cannot pin per-template versions — it can
only catch a MIXED set (:988-992), never a set recorded homogeneously at the wrong version,
which is exactly the shape a full re-record after a bump produces. Phase 21 bumps the
prompt set, so 21.15's acceptance run is the first one that needs the flag.

B-48 is a false-red waiting for the next hand-run of the offline gate. `WALK_SKIP_DIRS`
(:143-155) justifies itself as "build output, caches and dependency trees"; a nested git
worktree is none of those, and 758 of the 817 sidecars the FAILING row hashes on this
checkout live under `.claude/worktrees/`. The inventory row directly below already scopes
itself to `git_tracked_sidecars` and reports the extras as a note; the row that decides the
exit code does not. The generalizing fix is the verifier's, not the finding's first
suggestion: skip any directory that contains a `.git` entry, because a nested worktree marks
itself and a worktree outside `.claude` would still leak in under a bare `.claude` skip.
`.gitignore:8` keeps CI clean of these directories, so the exposure is developer-local — but
this gate is explicitly the offline one-command local truth and the close audit runs it by
hand on exactly the machine that carries the worktrees (audits/audit-phase-20-close.md:57).

B-23, B-51 and B-52 are one seam seen from three sides, and the loader's substrate stamp is
the seam. B-23: `_assert_substrate_matches` runs only inside `_walk`, so a mismatched replay
is advertised by the picker and 500s when opened; the verifier's correction is carried —
the cost-summary half is DROPPED, because `_ReplaySummary` (:667-694) reduces recorded bytes
only (cost, winner, ticks, meeting count), none of them reconstruction-dependent, so a
substrate-mismatched game is a real game that really cost that much and counting it is
defensible. Only the listing is repaired. B-52: both the loader's diff (:631-635) and the
audit spine's `retired_levers_stamped_off` (orchestrator/replay.py:646-648) iterate the
BUILD's key set and never the recording's own, so a stamp carrying a lever this build has
never heard of reconstructs silently — verified end to end, a full 52-file copy of
`replays/samples/9p2i` with one unknown key added to the `game_over` stamp serves 200 while
the paired known-lever flip 500s. The registry is append-only by design
(orchestrator/replay.py:585-589), which is precisely what makes a newer build's stamp a
strict superset, and "no silent fallbacks" is the rule this violates. B-51: all three error
docstrings promise "HTTP 500 with the offending game id in the response body" and only one
has a handler, so the substrate error's carefully-built remediation text — the differing
levers and the `AILIBI_*` variables to export, api/replay_loader.py:392-421 — is constructed
and discarded, leaving `Internal Server Error` in a `text/plain` body. Zero committed bytes
are affected by any of the three: all 300 committed replays stamp identically to the build
snapshot today. The exposure is procedural and it is a live workflow here — levers graduate
on branches, recordings are made in containers, and lab bytes get read back on `main`.

**Files in scope:**
- scripts/record_ml_corpus.sh; (the 10-poll dead-owner streak back-ported verbatim; the explicit `fake` provider arm with its outside-`replays/` target refusal and its own model attribution; `--seeds N,N,N`; the acceptance line gains the version pin)
- tests/scripts/test_record_ml_corpus.py; (the hermetic recording family, the two-worker contention case, the verbatim-extraction lock driver and freeze driver, the retargeted fake-provider refusal)
- scripts/validity_gate.py; (`--expected-prompt-versions KEY=VER,…` threaded into the existing parameter)
- tests/scripts/test_validity_gate_cli.py; (the flag in both directions, plus the parse-error case)
- scripts/verify_ml_evidence.py; (`walk_sidecars` stops at any nested checkout)
- tests/scripts/test_verify_ml_evidence.py; (the planted nested worktree and the planted in-tree failure that proves the leg still bites)
- orchestrator/replay.py; (the shared stamp comparison both the loader and the audit spine call)
- tests/orchestrator/test_replay.py; (the unknown-key and toggleable cases)
- api/replay_loader.py; (the listing drops a substrate-mismatched replay; the guard and both errors read the recording's own keys and expose what diverged)
- tests/api/test_replay_loader.py
- api/main.py; (two more exception handlers beside the existing one)
- tests/api/test_main.py; (the response body carries the game id and the divergence)
- audits/workflows/extract_gameplay_facts.py; (the `$0` re-extraction spine's refusal reads the full comparison instead of the retired-only half)

**Files NOT in scope:**
- scripts/refresh_samples.sh (the source of the streak, the fake arm and the `--seeds` mode — read and copied FROM, never edited; its 82-test family is the pattern, not a target)
- replays/ and replays/ml_corpus/ (nothing is recorded into the tree: the hermetic family sets `AILIBI_ML_CORPUS_ROOT` to a scratch dir, and the new fake arm refuses a target under `$REPO_ROOT/replays` outright)
- eval/validity.py (the `expected_prompt_versions` parameter, the mixed-set check and the exact-violation branch already exist and are correct — this task adds only the CLI surface that reaches them)
- eval/replay_walk.py (21.11 owns the one-line substrate check there via `orchestrator.replay.retired_levers_stamped_off`; that function keeps its exact signature and semantics here so 21.11's edit lands unchanged)
- api/schemas.py and frontend/ (the annotate-the-picker option from B-23's fix sketch is deliberately NOT taken: no DTO field, no spectator change; 21.12 owns the frontend gates and the raw-500 message the store surfaces at frontend/src/store/replayStore.ts:432-435 improves as a side effect of B-51, without a frontend edit)
- scripts/check.sh (the gate composition is not this task's; every new case runs under the ordinary `uv run pytest`)
- training/, agents/, meetings/ (no fit, no detector, no prompt path is touched)

**Definition of done:**
- [ ] `acquire_lock` in scripts/record_ml_corpus.sh carries the streak verbatim from scripts/refresh_samples.sh:776-817 — `local owner last_dead_owner dead_polls`, increment on a repeated dead owner, reset when the owner changes or the probe is live, and `touch "$stage_dir/.failed"` only at `dead_polls >= 10` — with the sibling's own explanation of why one probe is not a verdict, not a second explanation of the same race, and the existing Bash-3.2 degradation note (:1018-1031) left intact with its ledger pointers.
- [ ] The streak gate can fail, driven off the committed implementation rather than a copy: a test extracts `acquire_lock`/`release_lock` from scripts/record_ml_corpus.sh by regex into a driver script (the nesting means the extraction must tolerate the two-space indent) and asserts BOTH directions — a lock dir whose owner file names an already-reaped pid is NOT failed within a few polls when the owner file disappears (the benign release race), and IS failed with the "died holding the lock" message once the same dead pid survives 10 consecutive polls.
- [ ] scripts/record_ml_corpus.sh accepts an explicit `AILIBI_LLM_PROVIDER=fake` on the same terms the sibling does and no looser: unset/empty still resolves to `featherless`, every other non-featherless value is still refused with the existing message, and a `fake` run whose resolved `CORPUS_ROOT` lies inside `$REPO_ROOT/replays` fails loud before any staging, naming the path and the rule. Physical paths are compared (a symlink or a `..` cannot smuggle a target back under `replays/`).
- [ ] No fake row can ever render as a real one: on the fake path the per-seed `_manifest_writer.py update` call at :1128-1134 passes the fake client's own model id (the sibling's `DEFAULT_FAKE_MODEL` shape at scripts/refresh_samples.sh:403), never `$DEFAULT_FEATHERLESS_MODEL`, and a test asserts the recorded MANIFEST row carries it with `0.0000` cost.
- [ ] `tests/scripts/test_record_ml_corpus.py:442::test_preflight_refuses_fake_provider` is retargeted rather than deleted, and the PR states the retarget: `fake` pointed at the committed corpus tree stays refused by name (`replays/ml_corpus/9p2i` and `replays/ml_corpus/4p1i`), while `fake` pointed at a scratch `AILIBI_ML_CORPUS_ROOT` is allowed. The FEATHERLESS_API_KEY preflight (:845-849) is skipped on the fake path; the substrate-lever preflight and the prompt-set registry pin still run unchanged, and a test asserts both still fire under `fake`.
- [ ] `--seeds N,N,N` records a comma-separated subset of the selected set's LOCKED range, mutually exclusive with `--splits-only`, composing with `--dry-run` and `--set`, refusing a seed outside the range and refusing an empty list — mirroring scripts/refresh_samples.sh:237-246 and :275. It is documented in `usage()` (:170-189) as an operator mode, and a test pins that a subset run cannot freeze: `check_seed_count` refuses at the finalize with "is not the exact locked seed set; NOT freezing", exit non-zero.
- [ ] A hermetic recording case runs the REAL path (no `--dry-run`) as `--set 4p1i --seeds 1000,1001` with `AILIBI_LLM_PROVIDER=fake` into a scratch `AILIBI_ML_CORPUS_ROOT`, and asserts: both replay files land in the set dir, the MANIFEST holds exactly one row per seed, the per-run stage dir is gone, and the run ends at the short-set freeze refusal — and the PR quotes a `bash -x` trace naming `run_worker`, `claim_next_seed`, `record_one_seed` and `acquire_lock`, asserted by name the way tests/scripts/test_refresh_samples.py:1358-1361 does.
- [ ] A contention case runs the same path with `AILIBI_REFRESH_WORKERS=2` over ≥4 seeds and asserts no MANIFEST row is lost, no seed is recorded twice, and the lock-guarded merge at :1124-1140 is what makes it safe — the exact failure `28599ec3` attributes to three CI flakes on the sibling. `record_one_seed`'s fail-loud branch is exercised by a deterministic injected failure ending in exit 1 and the "INCOMPLETE and must NOT be frozen/committed" message (:1193-1196), never by a timing-dependent race.
- [ ] `freeze_manifest` (:740) gains coverage through a verbatim-extraction driver over a scratch MANIFEST, since the finalize's provenance guards correctly make it unreachable from a fake recording; the PR states that boundary explicitly rather than implying the freeze path runs end to end.
- [ ] `scripts/validity_gate.py` gains `--expected-prompt-versions KEY=VER,…`, parsed into a mapping and threaded into `run_validity_gate`'s existing `expected_prompt_versions` parameter, with a malformed value exiting 2 as a usage error (the file's documented exit-code contract at :19-24). The acceptance line scripts/record_ml_corpus.sh:825 echoes it. A test pins that the committed 9p2i set PASSES against its own recorded versions and FAILS against a homogeneous wrong pin — the case eval/validity.py:988-992 cannot see.
- [ ] `walk_sidecars` no longer descends into a nested checkout: any directory containing a `.git` entry (file or dir — a worktree's `.git` is a file) is skipped, applied to descendants only so the repo root is unaffected. The rule is stated in the comment at :140-142 in the same voice, and `WALK_SKIP_DIRS`'s own justification stays true of what remains in it.
- [ ] That gate can fail in both directions: a planted temp tree with a nested `.git` and a deliberately mismatched sidecar is EXCLUDED from the walk (and would fail `_verify_sidecar` if it were not), while a mismatched sidecar OUTSIDE any nested checkout still sets the IN-TREE row to FAIL. The PR quotes `uv run python scripts/verify_ml_evidence.py --only sidecars` before and after, with the before/after sidecar counts and the machine's nested-worktree count named as machine-local.
- [ ] `orchestrator.replay.substrate_stamp_mismatches` compares a recording's stamp against an ambient snapshot in BOTH directions — keys the build knows whose values differ, and keys the recording carries that the build's registry does not — and returns them separately, defaulting `ambient` to `substrate_flag_snapshot()`. `retired_levers_stamped_off` keeps its exact signature and semantics (21.11's `eval/replay_walk.py` one-liner and the phase-20 close routing at audits/audit-phase-20-close.md:408 both depend on it), gaining one docstring line naming the fuller comparison.
- [ ] `_assert_substrate_matches` and `ReplaySubstrateMismatchError` both call it; the error stores its divergence as attributes (the differing levers and the unknown ones) instead of computing them into a local, and gains a third hint branch for unknown keys stating that the recording was made by a build this one is behind. A test reproduces the finding's exact repro — a `GameEndReplayEntry` whose `substrate_flags` is `substrate_flag_snapshot()` plus one unknown key — and asserts it now RAISES, alongside the paired known-lever flip that already did.
- [ ] `ReplayLoader.list_replays` drops and logs a substrate-mismatched replay on the same terms as the three corrupt classes, reading the stamp from the cheap summary pass (`_read_summary` at :1774-1817 already walks every entry, so no second read is added) and extending `_log_skipped_replay` (:492-509) with the fourth reason string and its docstring. `cost_summary` is DELIBERATELY unchanged and both docstrings say why: the summary reduces recorded bytes only, so a substrate-mismatched game is a real game whose cost and winner are real. A test asserts exactly that asymmetry over a mixed-substrate scratch set — the picker omits it, `total_replays` still counts it — so the divergence is pinned rather than discovered later.
- [ ] `api.main.create_app` registers handlers for `ReplaySubstrateMismatchError` and `ReplayPolicyMismatchError` beside the existing one (a small table or three registrations, not three copies of one function), each returning a 500 JSON body carrying `detail`, `game_id` and the divergence the error already computed. Two API-level tests assert the body: the substrate one through a served mixed-substrate set, and the policy one through a loader constructed with `expected_tactical_policy` and injected via the `get_replay_loader` dependency override — because that error is unreachable from HTTP today (`SetLoaderRegistry._build_loader` at :3353-3354 builds every served loader bare), which the PR states rather than leaving the reader to assume it is live.
- [ ] The mixed-substrate fixture used by these tests copies the WHOLE committed 9p2i set and rewrites one `game_over` line: a byte-identical copy of a single replay served from a directory holding only that file fails its own tick-0 state hash, so a single-file fixture silently tests the wrong thing (the verifier's incidental note at audits/review-2026-08-26/B/collated-findings.md:2740).
- [ ] `audits/workflows/extract_gameplay_facts.py:2169` refuses on the full comparison instead of the retired-only half, keeping its existing message for the retired case and adding the unknown-key case. The widening is stated as a decision in the PR: a toggleable lever whose stamp disagrees with the ambient environment now also refuses, which is the same rule the API loader already enforces, and which no committed byte trips (all 300 stamp identically to the snapshot).
- [ ] Blast radius stated from a fresh grep, per AGENTS.md rule 6: `retired_levers_stamped_off` has exactly one production caller before this task (audits/workflows/extract_gameplay_facts.py:169, :2169); `walk_sidecars` has one (`run_sidecars`); the four `add_argument` calls in scripts/validity_gate.py are the whole CLI surface. Any hit outside these files in scope is reported, not silently absorbed.
- [ ] No committed byte moves: `git status --porcelain replays/` is empty at the end of the run, and the PR says so alongside the reason this task is dispatched before 21.14 — the smoke and the re-record run this recorder, and 21.15 records the corrected substrate onto the baseline-7 record, which is canon by explicit owner override of a FINDING verdict.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

Step 1 — the streak, first and alone. Copy scripts/refresh_samples.sh:776-817 into
scripts/record_ml_corpus.sh:1032-1050 and rename `_lockdir` to `lockdir` to match the
surrounding scope; after the edit the two bodies should be byte-comparable modulo the
`_`-prefixed names. Keep the existing Bash-3.2 comment block above it untouched — it
documents a different, ledgered degradation and its pointers (audits/audit-phase-18-close.md
§7 row 5, training/README.md §6 row 5) are still true. Write the driver test before the
edit and watch the streak case fail at HEAD; that is the cheap proof the gate bites.
Extraction differs from the sibling's `_lock_driver` in one way only: these functions are
indented two spaces inside `record_set`, so the regex is `(?ms)^  acquire_lock\(\) \{\n.*?\n  \}$`
and the driver must dedent or tolerate the indent. `_reaped_pid`-style helpers already exist
in tests/scripts/test_refresh_samples.py:1649 — mirror the approach rather than inventing one.

Step 2 — the provider seam. The refusal at :839-843 is the single resolution point; give it
a `fake` arm that leaves `PROVIDER="fake"` and then immediately asserts the target, in the
shape scripts/refresh_samples.sh:616-640 uses: resolve `CORPUS_ROOT` to a physical path
(`cd … && pwd -P` in a subshell) and refuse when it is `$REPO_ROOT/replays` or below. The
sibling has a `resolve_physical_path` helper at :209; do not import it across scripts —
copy the five lines, the same way the two mutexes are copies. Then skip the API-key block
at :845-848 on the fake arm and set a `DEFAULT_FAKE_MODEL` constant beside the existing
model constants, used at :1132 in place of `$DEFAULT_FEATHERLESS_MODEL`. Note what the
existing tests inherit: `tests/conftest.py` forces `AILIBI_LLM_PROVIDER=fake` for the whole
suite, and `_clean_env()` (tests/scripts/test_record_ml_corpus.py:117) already strips every
`AILIBI_*` and both provider keys — so the ambient `fake` reaches the script only where a
test puts it back, and the `replays/` refusal, not the provider refusal, is what protects
the committed corpus from here on.

Step 3 — `--seeds`. Parse it beside `--set` in the `while` loop at :214-251, store the list,
and intersect it with the seed list built at :980-992 rather than replacing that block: the
resume skip-scan and the "already recorded" line must keep working, and a seed outside
`start..last` must fail loud before the stage dir is created. Everything downstream is
unchanged — `check_seed_count` at the finalize is what stops a subset from freezing, and
that refusal is the hermetic family's assertion point, not a problem to route around.

Step 4 — the recording family. Build on `_on_slate_env` (tests/scripts/test_record_ml_corpus.py:885),
which already threads `AILIBI_ML_CORPUS_ROOT`; add a `_fake_env` sibling that sets the
provider to `fake`, drops `FEATHERLESS_API_KEY` and points the corpus root at `tmp_path`.
Use the 4p1i set (seeds 1000-1049): a fake 4p1i game measured 0.4 s at Task 20.21, and two
seeds plus two `uv run` manifest writes is a few seconds. For the trace, run the case a
second time under `bash -x` (or `BASH_XTRACEFD`) and assert the four function names off
stderr — that beats asserting on progress strings a later edit may reword. For the fail-loud
injection prefer a deterministic one: a set dir made read-only after `roster.json` is
written, so the atomic `mv` into place fails into the `.failed` path; skip the case when the
test process is root.

Step 5 — the validity-gate flag. `KEY=VER,KEY=VER` splits into the same mapping
`eval/validity.py:1001-1012` compares against `game.prompt_versions`; note that the registry's
values already carry the template prefix (`accusation_round.qwen3_6_27b.v4`), so a probe of
`PROMPT_VERSION_SETS` prints doubled-looking pairs — that is the real shape, not a bug, and
the flag's help text should show one worked example so an operator does not guess.

Step 6 — the sidecar walk. One predicate inside the `dirnames[:]` filter at :910:
`(Path(dirpath) / name / ".git").exists()` skips it. `.exists()` covers both a worktree's
`.git` FILE and a real `.git` directory. `.git` itself is already in `WALK_SKIP_DIRS`, so
the root is never re-entered and the rule only ever fires on a descendant. Plant the failing
case in `tmp_path`, never in the repo.

Step 7 — the substrate seam, in dependency order: the helper in orchestrator/replay.py
first, then api/replay_loader.py's guard and error, then the listing, then api/main.py's
handlers, then the audit spine. Keep the helper's return separable — the loader's hint
branches and the spine's message both need to say WHICH class diverged, and collapsing the
two lists into one loses that. For the listing, `_read_summary` already visits every
`GameEndReplayEntry`; carry the stamp onto `_ReplaySummary` there rather than adding a read.
For the handler test, `TestClient(create_app(replay_dir=…), raise_server_exceptions=False)`
is the shape both the finder and the verifier used, and the whole-set fixture rule in the
DoD is not optional — a single-file copy fails on its own tick-0 hash and would prove
nothing about the substrate path.

## Public types this task introduces
- `orchestrator.replay.SubstrateStampMismatch`
- `orchestrator.replay.substrate_stamp_mismatches`

These are the symbols downstream tasks will import. Keep their signatures stable.

## Dependency contract check
Run these before editing. If any fail, stop and report — your dependencies are not where this task expects them.

- `uv run python -c "import eval.meeting_quality"`
- `uv run python -c "import eval.watchability.SupplyFloors"`
- `uv run python -c "import orchestrator.replay"`
- `uv run python -c "import meetings.schemas"`
- `uv run python -c "import eval.replay_walk.ReplayWalkConfig"`

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
Open a PR from branch `phase-21-recorder-hardening` with a title like `task 21.10: the recorders earn the next record: the dead-owner streak, a tested recording engine, the version pin's cli, and the loader guard sweep`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing B-18 [ADJUSTED P2, defect], B-21 [CONFIRMED P1, quality-debt], B-19 [ADJUSTED P3, design-limitation], B-48 [CONFIRMED P2, defect], B-23 [ADJUSTED P2, defect — listing half only], B-51 [CONFIRMED P2, defect] and B-52 [CONFIRMED P2, defect] — all seven in audits/review-2026-08-26/B/collated-findings.md (B-18 :1069, B-19 :1147, B-21 :1266, B-23 :1382, B-48 :2532, B-51 :2689, B-52 :2744), read with their verifier evidence and verifier notes, which BIND the claims below. The precedent this task back-ports from is Task 20.21 (tasks/phase-20.md:3312) and its follow-up `28599ec3` ("task 20.21 follow-up: the lock's dead-owner verdict must survive a release racing the probe", #388); the routing that dropped is tasks/phase-20.md:3384 ("mirror any fix there in 20.36, not here") against `efcd43b8` (20.36, #389), which edited scripts/record_ml_corpus.sh without the mirror, and audits/audit-phase-20-close.md:224, which records 20.21 VERIFIED and names no open mirror. Anchors re-verified at HEAD `4002f19b` (the Wave-0 audit commit; the code tree is unchanged from the registers' `d8ec0a1c`): scripts/record_ml_corpus.sh is 1,307 lines with `record_set()` at :929 closing at :1284 and the four pool functions NESTED inside it — `acquire_lock` :1032-1050 (`local owner` only; ERROR + `touch "$stage_dir/.failed"` + `return 1` on the FIRST dead probe; owner written `${BASHPID:-$$}` at :1049), `release_lock` :1051, `claim_next_seed` :1055-1066, `record_one_seed` :1073, `run_worker` :1162, with `freeze_manifest` (top-level, :740) reachable only from :1279; the sibling streak is scripts/refresh_samples.sh:776-817 `_acquire_lock` (`local owner last_dead_owner dead_polls`, the race stated verbatim at :791-797, the increment at :798-803, `if [[ "$dead_polls" -ge 10 ]]` at :804); contention is the default (`REFRESH_WORKERS="${AILIBI_REFRESH_WORKERS:-2}"` at :320) and the claim mints its transient owner from a command substitution (`seed="$(claim_next_seed)"` at :1166); `grep -c 'def test_' tests/scripts/test_record_ml_corpus.py tests/scripts/test_refresh_samples.py` → 54 / 82 and the four pool names appear in the corpus recorder's test file only as `test_dry_run_worker_count_is_overridable` (:388), while the sibling's family drives them by name (tests/scripts/test_refresh_samples.py:1055-1056, the `bash -x` assertion list :1358-1361, the verbatim-extraction `_lock_driver` :1630-1646 with its two streak cases at :1659 and :1685); the provider refusal is scripts/record_ml_corpus.sh:839-843 pinned by tests/scripts/test_record_ml_corpus.py:442, and the sibling's hermetic seam is scripts/refresh_samples.sh:616-640 (the fake arm's `replays/` target refusal) with `DEFAULT_FAKE_MODEL="fake-meeting"` at :403 and the `active_model` resolution at :703-719 used at :928; scripts/record_ml_corpus.sh:156 is `REQUIRED_PROMPT_VERSIONS`, asserted forward by `check_prompt_version_registry` :499-520 and backward by `check_recorded_prompt_versions` :530, while `grep -n add_argument scripts/validity_gate.py` returns exactly four (:68 `replay_set_dir`, :73 `--json`, :78 `--expected-model`, :86 `--require-zero-cost`) against `eval/validity.py:905` and `:1142`, which both accept `expected_prompt_versions`, thread it at :1240 and turn it into an exact violation at :1001-1012 — and scripts/record_ml_corpus.sh:825 prints the acceptance line without it; scripts/verify_ml_evidence.py:143-155 `WALK_SKIP_DIRS` has no `.claude` and no nested-checkout rule, consumed once at :910, and `run_sidecars` (:980) fails on the raw walk (`in_tree` :994-996 → `status="FAIL" if in_tree_failures` :1021) while the inventory row below it does scope to `git_tracked_sidecars` (:1054); api/replay_loader.py:1101-1103 places `_assert_substrate_matches` (:603-651) inside `_walk` (:1069) only, `list_replays` (:753-785) and `cost_summary` (:806-844) both catch `(ReplayLog.CorruptedFileError, ValueError)` and `ReplaySubstrateMismatchError` subclasses `RuntimeError` (:354); the diff at :631-635 and the error's own at :387-391 both iterate `SUBSTRATE_FLAG_KEYS`, never `recorded`'s keys, mirrored at orchestrator/replay.py:646-648 in `retired_levers_stamped_off` (:623, docstring :626-642, whose registry is append-only by construction — orchestrator/replay.py:585-589); api/main.py:231 is the ONLY `add_exception_handler` call, for `ReplayStateMismatchError` alone (`_handle_state_mismatch` :157-165), while all three error docstrings promise the same body (api/replay_loader.py:339, :373, :441). Re-measured here, on the owner's checkout: the sidecar walk is 817 files, 758 of them under `.claude/worktrees/` (14 checkouts), 59 outside, against `git ls-files '*.sha256'` = 59 tracked — 93% of the failing row's input is not in this checkout's index.), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
