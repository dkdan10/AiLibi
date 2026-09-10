# Close the nonblocking follow-up improvements

**Status:** done

## Outcome

The operator paths, untested guards and doc gates the follow-up review listed as
worth cards rather than gates are closed, one focused commit each, every one with
a planted failure proving the new check detects the defect it claims.

## Evidence

Review claims are leads, not measurements of this tree. Reproduce each item from
the archived follow-up review
([report](../../audits/review-2026-09-06/REVIEW_REPORT_FOLLOWUP.md) section 7,
plus the follow-up appendix) on this checkout before implementing it.

Verified anchors at this tree:
`scripts/run_tournament.py:1210-1215` (protection is scoped to `--output-dir`
and matched by name);
`scripts/_verify_samples.py:55-60` (`VerifyFailure.render`);
`orchestrator/game.py:753` (`MeetingArtifacts.skip_confidence_threshold`,
default `None`), `:757` (the `MeetingRunner` protocol), `:2636` (its consumer);
`observation/temporal.py:71` (`can_watch = observer.alive and not observer.in_vent`);
`meetings/manager.py:1683` (the off-profile `TaskActivityAccount` refusal);
`.env.example:243,244,249,250` (the four new experiment env names);
`tasks/README.md` (derived card and gate counts, and the ownership table);
`api/public_results.py:228-232` with `api/replay_loader.py:949-956` and `:1305`
(`clear_cache`); `orchestrator/recording.py:134-139` (the exclusive probe
descriptors, released before the write) and `:60-67` (the zero-byte rollback).

## Acceptance

One commit per item; each box needs its named planted-failure proof, not merely
an implementation.

- [x] Review correction: the card-inventory gate reads the whole breakdown, so a
  repeated status or unmatched text in the index sentence is refused rather than
  skipped over. Planted proof: `999 ready, 2 ready, 1 done` and
  `2 ready and lots else, 1 done` both fail where the previous parser reported
  nothing at all.
- [x] Review correction: both `.env.example` registry checks read an `export`
  prefix and padding around the `=` as an active assignment. Planted proof:
  `export AILIBI_PUBLIC_ACCOUNTS=1` and `AILIBI_PUBLIC_ACCOUNTS = 1` are refused,
  as are the substrate check's equivalents for `AILIBI_IMPOSTOR_ROLL_CALL`.
- [x] Review correction: the NC5-03 row states what its command prints on the
  committed tree — 1,405 passing beside the one new failure — not 1,429.
- [x] Review correction: the index no longer says every commit a branch carries
  is registered. It names the register's coverage tip and the one commit that
  cannot carry its own row, and the register covers the two commits the
  instrument merge brought in.
- [x] **NC4-2 / FU-5.** `scripts/run_tournament.py` refuses a `--report-output`
  or `--progress-output` whose basename parses as a recording, regardless of the
  directory it names. Planted proof: a destination outside `--output-dir` whose
  basename is `replay-seed-1.jsonl` is refused before any game runs.
  [Report destinations](report-destinations.md) owns the in-directory alias
  protection this extends; do not weaken it.
- [x] **FU-03.** `scripts/_verify_samples.py::VerifyFailure.render` prints the
  integrity code instead of `recorded None, reconstructed None` when the recorded
  and reconstructed values are absent. Planted proof: an integrity violation
  carrying a tick renders its code, not two `None`s.
- [x] **FU-06.** A `MeetingRunner` that resolves under a non-default skip cutoff
  must set `MeetingArtifacts.skip_confidence_threshold`. Document the contract at
  `orchestrator/game.py` on the protocol (`:757`) and the field (`:753`), and
  consider a write-time check so the recorder refuses an unattributable cutoff
  rather than leaving the reader to discover a permanently unreadable recording.
  Planted proof: bytes a custom runner would write are refused at write time, or
  the contract change is shown to make them unwritable.
- [x] **NC5-02.** Adverse test for the vented v2 observer guard at
  `observation/temporal.py:71`. Planted proof: dropping `not observer.in_vent`
  fails the new test where it passes the whole suite today.
- [x] **NC5-03.** Adverse test for the off-profile `TaskActivityAccount` refusal
  at `meetings/manager.py:1683`. Planted proof: disabling the guard fails the new
  test where it passes the whole suite today.
- [x] **P-04.** A `check_doc_facts.py` lever-registry rule covering the four new
  experiment env names in `.env.example` (`AILIBI_EVIDENCE_REASONING`,
  `AILIBI_BOUNDED_REBUTTAL`, `AILIBI_PUBLIC_ACCOUNTS`,
  `AILIBI_ATTRIBUTED_TESTIMONY`). Planted proof: renaming one in `.env.example`
  without updating its documentation fails the gate.
- [x] **P-05 / CMP-01.** Card and gate counts in `tasks/README.md` are derived
  from `tasks/work/*.md` rather than typed. Planted proof: flipping a card's
  Status to `active` without touching the README fails the gate.
- [x] **P-06 / P-10.** The `tasks/README.md` ownership label describes the
  current batch rather than a finished one, and `tasks/review-ledger.md` gains a
  row per post-review commit. Planted proof for the ledger half: a post-review
  commit with no ledger row is visible in the check.
- [x] **CONC-6.** `api/public_results.py`'s `clear_cache()` plus install
  (`:228-232`) is serialised under a per-loader lock, and the loader's `lru`
  keys (`api/replay_loader.py:949-956`) carry a cache-generation counter so a
  same-length, same-mtime replacement during a concurrent cold build cannot
  install pre-flip parsed replays under the post-flip fingerprint. Amend the
  [cache card](public-results-cache.md)'s constraint sentence, which currently
  rules out locking. Planted proof: the controlled interleaving that reproduced
  the silent corrupt install now refuses.
- [x] **Probe-descriptor lifetime.** Either hold the exclusive probe descriptors
  in `orchestrator/recording.py:134-139` for the recording's lifetime — which
  closes the peer-unlink race the zero-byte rollback at `:60-67` opened, by
  construction — or drop the item and keep the module's existing disclaimer.
  Decide explicitly and record the decision; do not leave it implied.

## Constraints

One commit per item, each with its own planted failure; do not batch them into
one change. No re-record, no committed recording or report rewritten, no
provider calls, no new dependencies, no gameplay behaviour change. Volatile
counts in `tasks/README.md` need an explicit "as of" stamp so a derived number is
never read as a standing measurement. Candidates stay default-OFF and nothing
here adopts one. Concurrency work stays inside the area
`orchestrator/recording.py` already disclaims; this card does not introduce a
multi-process transaction protocol. Coordinate on shared files: the accounts card
owns `meetings/manager.py` and the provenance card owns `api/public_results.py`
and `api/replay_loader.py` — take those items after those cards land, or hand
them over explicitly.

## Expected scope

`scripts/run_tournament.py`, `scripts/_verify_samples.py`,
`scripts/check_doc_facts.py`, `orchestrator/game.py` (docstrings and an optional
write-time check), `orchestrator/recording.py`, `api/public_results.py`,
`api/replay_loader.py`, `tasks/README.md`, `tasks/review-ledger.md`,
`tasks/work/public-results-cache.md` (one constraint sentence), and the matching
tests under `tests/scripts`, `tests/observation`, `tests/meetings`, `tests/api`
and `tests/orchestrator`.

## Record impact

No recorded bytes change: no recording, report, DTO or prompt byte moves, and
the default gameplay path is untouched. Two effects to state plainly. A new doc
gate can newly fail an existing document that was green before — name in Results
which documents the new rules now bind. A `MeetingRunner` contract change or a
write-time cutoff check changes future failure handling for custom runners
without changing any committed recording; no in-tree runner is affected today,
since the shipped runners tally at the default cutoff.

## Validation

`uv run pytest tests/scripts tests/meetings/test_lever_registry.py tests/api/test_public_results.py -q`
for the planted failures, plus the targeted observation and orchestrator tests
each item adds, then `bash scripts/check.sh`, then
`bash scripts/verify_samples.sh`.

## Results

Ten commits, one per acceptance item plus the held-out restamp the cutoff
contract required, each with the planted or perturbed failure its box names.
Scope follows `docs/architecture.md` Packages and Determinism and the
privileged script, reader and meeting-layer boundaries; no engine transition,
prompt byte, recording, report or served DTO moved, and every candidate stays
default-OFF. Numbers below were measured on the commit each row names.

| Item | Commit | Perturbation | What the check then said |
| --- | --- | --- | --- |
| NC4-2 / FU-5 | `444a47fd` | the two guard calls replaced by `pass` | 8 destination cases fail with "destination validation must precede the evaluator" |
| FU-03 | `db885271` | the pre-repair tick branch restored | `assert 'ballot_roster_mismatch' in 'FAIL: headless-seed-22 diverged at tick 7: recorded None, reconstructed None'` |
| FU-06 | `29393cda` | the write-time guard call removed | `Failed: DID NOT RAISE <class 'ValueError'>` |
| NC5-02 | `c8efd12a` | `not observer.in_vent` dropped | all three arms fail; 152 other v2 tests still pass |
| NC5-03 | `f8a68519` | the off-profile condition disabled | the new case fails; the other 1,405 pass (see round 1 below) |
| P-04 | `666dfbbb` | `AILIBI_PUBLIC_ACCOUNTS` renamed in `.env.example` | exit 1, naming the undocumented switch and the unregistered one |
| CONC-6 | `54c623e8` | the cache generation frozen | `DID NOT RAISE`; the silent install publishes `crew_wins 1` under the post-flip fingerprint |
| Probe descriptors | `4a7c0071` | the empty-output removal dropped | the pinned case fails with the peer's file still present |
| P-05 / CMP-01 | `51118004` | one card flipped to `active` | exit 1: "breaks down as '3 ready, 40 done', but tasks/work/ holds 2 ready, 1 active, 40 done" |
| P-06 / P-10 | `2d06e0b4` | one register row deleted | "post-review commits with no ledger row: [('54c623e8', ...)]" |

Two commits carry no acceptance box of their own. `d282dd06` restamps the
frozen held-out manifest, which `29393cda` moved by editing one of the
twenty-two hashed generator sources: regenerating the band left all fifty
accepted prefix digests and all eight skips byte-identical, `last_accepted_seed`
still 3057, and only `source_sha256` and the new dated `dependency_restamps`
entry changed. No prefix was printed or opened; the `docs/artifacts.md`
`audits/` row was recomputed with the change staged (14,925,876 → 14,926,477
bytes across the same 204 files) and `scripts/verify_ml_evidence.py` reported
`checks: 60 | OK 48 | FAIL 0 | ABSENT 7 | INFO 5`. `d210c04c` then repairs two
strict-mypy re-export errors that only the whole-tree run reaches.

### Decisions

**The destination guard runs after the preflight, not before.** A destination
inside `--output-dir` is refused by the existing preflight, whose message names
the exact recording it collides with; the new basename rule is what remains for
the recordings no preflight can enumerate. Running it second keeps the more
specific message where both apply. What counts as a recording is read from
`orchestrator.recording_fingerprint`'s shared filename contract plus the audit
sidecar built from the same stem, so `replay-seed-debug.jsonl` and other names
the recorder never writes stay usable as report destinations. This extends
[report destinations](report-destinations.md)' in-directory alias protection
and changes none of it.

**FU-06 took the write-time refusal, not documentation alone.** The check is
small — when a runner reports no cutoff, its ballots must reproduce its own
outcome at `LEGACY_SKIP_CONFIDENCE_THRESHOLD` — and it makes the unreadable
bytes unwritable rather than leaving the reader to discover them. It sits
inside the meeting's `try` block, so a refusal still retains the meeting's
provider attempts on the abort record, and it is gated on a replay being
recorded, since the defect is a recording that no reader will accept. Every
shipped runner tallies at the legacy cutoff; the default runner reports its
cutoff and never reaches the tally.

**P-05's gate lives in `scripts/validate_task_docs.py`, not
`check_doc_facts.py`.** The finding suggested the latter, but the former is the
gate that already parses every `tasks/work/*.md`, is invoked directly by
`scripts/check.sh`, and needs no document-fixture surgery to read the cards.

**"Post-review commit" is defined from git, not by hand:** every non-merge
commit reachable from this branch and not from the cleanup merge `8161689a`.
A commit cannot contain its own sha, so the register declares the coverage tip
it reaches; the tip must be the register's own last row and an ancestor of
`HEAD`, and the commit after the one it records advances it. The residual is
stated rather than hidden: a tip that lags leaves later commits uncovered until
it moves.

**The probe-descriptor lifetime: declined, and why.** Holding the exclusive
probes open for the recording's lifetime does not close the peer-unlink race
the zero-byte rollback opened. An open descriptor confers no exclusion on
POSIX: a peer running with `force` replaces the path and creates its own file
whoever holds a handle, and both writers in the observed race passed `force`.
Making retention decisive would need advisory locking every writer honours — a
multi-process protocol this card explicitly does not introduce — and it would
break the recorder's "nothing on disk until the first append" contract, since
the probe file would survive as a zero-byte output. The window therefore stays
disclaimed, the disclaimer now names it, and a test pins the behaviour so a
future change is a decision rather than a surprise.

**CONC-6 keeps the cache's shape.** A per-loader lock and a generation counter
in the LRU keys; no thread created, no in-flight work coalesced, still one
immutable result per loader. The [cache card](public-results-cache.md)'s
constraint sentence, which read "no new threads" as ruling this out, is amended
with a dated subsection in its own Results recording what changed.

### Verification

Focused, on the tree at `2d06e0b4`:

```sh
.venv/bin/pytest tests/scripts tests/meetings/test_lever_registry.py \
  tests/api/test_public_results.py -q
.venv/bin/pytest tests/observation/test_temporal_v2.py \
  tests/meetings/test_public_accounts.py \
  tests/orchestrator/test_experimental_evaluation_integrity.py \
  tests/orchestrator/test_recording_replacement.py -q
```

The first selection passed 1,389 tests with one warning; the second passed 148.
Every perturbation in the table above was applied to the working tree, run, and
restored, on the commit its row names.

Combined — the figures in this block are pinned to the tree at `d210c04c` plus
the card, index and ledger records in the commit that carried this paragraph,
and the round-1 subsection below re-runs the same gate at the delivered head:

```sh
bash scripts/check.sh
bash scripts/verify_samples.sh
AILIBI_SAMPLES_ROOT="$PWD/replays/ml_corpus" bash scripts/verify_samples.sh
.venv/bin/pytest tests/orchestrator/ --collect-only -q
uv run python scripts/build_sample_report.py --sample-dir <set> --check
```

`scripts/check.sh` exited 0: 7,508 Python tests, 20 optional skips and three
expected failures; 515 frontend tests across 19 files; strict typing on 474
sources; ruff lint and format; four import contracts kept; task-doc and
generated-type checks; and the production build. `verify_samples.sh` verified
all 300 canonical recordings — 100 under `replays/samples/` and 200 under
`replays/ml_corpus/` — without modifying their bytes. `tests/orchestrator/`
collects 586 tests in a fresh interpreter. All four
`build_sample_report.py --check` runs report their committed report consistent
with its replays. The browser journeys were not run: no served DTO changed.
An earlier run of the same gate at `2d06e0b4` failed on two strict-mypy
re-export errors that only the whole-tree run reaches; `d210c04c` repairs them.

### Which documents the new rules now bind

Three documents are held to derived facts they were not held to before, and
each is green at this tree: `.env.example`'s
independently-versioned-experiments section (every registered switch documented
as a commented bare default, no active export, no unregistered assignment);
`tasks/README.md`'s card inventory (total and per-status breakdown, with an
as-of stamp); and `tasks/review-ledger.md`'s post-merge commit register (every
sha, card and subject re-derived from `git log`).

### Limitations

The destination guard is a name rule: a genuine recording stored under a name
the recorder never writes is still not protected outside `--output-dir`, and
the in-directory protection that covers that case is unchanged. The cutoff
refusal binds recordings only — a runner used without a replay is unaffected —
and it cannot detect a runner that reports a cutoff other than the one it
actually resolved under. The concurrency work is confined to the cache's own
clear-and-install: concurrent cold requests still each reconstruct, and
`orchestrator/recording.py`'s concurrent-writer disclaimer stands, now with the
peer-unlink window named. The commit register's coverage tip can lag the
branch; nothing forces it forward except the next commit's author. The
git-derived half of that check skips, with its reason, on a shallow clone,
where the merge checkpoint is not in the object store — CI checks out at
`fetch-depth: 1`. No live provider was called, no recorded bytes were rewritten
and nothing here adopts a candidate.

### Review corrections, round 1 (2026-09-10)

Four corrections: two gate repairs the review reproduced against the committed
code, one figure that did not reproduce, and one completeness claim two records
disagreed about at the delivered head.

**The card-inventory gate accepted a fabricated count** (`f23d53cc`).
`scripts/validate_task_docs.py` built its `{status: count}` map with
`_INVENTORY_ITEM.findall` over the breakdown, so a repeated status kept only the
last pair and any text between two pairs was discarded. Reproduced at
`9ae7d2a1`: rewriting the index sentence to
`holds 43 cards: 999 ready, 2 ready, 41 done.` left
`.venv/bin/python scripts/validate_task_docs.py` printing
`Task docs validation passed: 390 historical phase tasks and 390 prompts; 43 work cards.`
at exit 0, with the file visibly claiming 999 ready cards. That is the hole
`P-05 / CMP-01` exists to close, so the sentence the same card added to
`tasks/README.md` — "recomputes the total and the per-status breakdown ... and
fails when either drifts" — was ahead of the code. `parse_inventory_breakdown`
now matches each comma-separated item end to end, refuses a repeated status, and
reports a malformed breakdown separately from a drifted one. Planted, in
`tests/scripts/test_work_cards.py`: `999 ready, 2 ready, 1 done` and
`2 ready and lots else, 1 done` against a tree of 2 ready and 1 done. Restoring
the `findall` comprehension fails both with `assert 0 == 1` — the previous
parser reported nothing at all for either.

**A shell `export` bypassed both `.env.example` registry checks** (`7b25ad36`).
Each check allows its switch only as a commented example, and each read "active"
as `^[ \t]*<VAR>=`, which matches neither an `export` prefix nor padding around
the `=` — forms python-dotenv and `set -a; . .env` both read as the same
assignment. Reproduced in-process at `9ae7d2a1` without editing a file:
`check_experiment_registry` over `.env.example` plus
`export AILIBI_PUBLIC_ACCOUNTS=1` returned zero errors where the bare form
returned the active-export error, and `check_lever_registry` behaved identically
for `AILIBI_IMPOSTOR_ROLL_CALL`. Both now build the pattern with
`active_assignment()`, which accepts the `export` prefix and the padding, as does
`_ENV_ASSIGNMENT` for the unregistered-name scan; both docstrings state which
forms they cover. Planted, one test per check in
`tests/scripts/test_check_doc_facts.py`, each running `export <VAR>=1` and
`<VAR> = 1` beside the required commented example; narrowing the helper back to
`^[ \t]*<VAR>=` fails both. The committed `.env.example` carries no `export`
line, so no document moves under the widening.

**The NC5-03 figure did not reproduce, and is restated.** The table above said
1,429 other meeting tests pass with the guard disabled. Measured on the committed
tree with `meetings/manager.py`'s off-profile condition disabled in place:

```sh
.venv/bin/pytest tests/meetings tests/agents/test_public_account_prompts.py \
  tests/orchestrator/test_public_account_scenario.py -q -p no:randomly
```

prints `1 failed, 1405 passed`, the failure being
`test_a_task_account_cannot_enter_a_transcript_recorded_without_the_profile` —
the new case, and only it. `--collect-only` over the same selection returns 1406.
The conclusion the row draws was verified and is unchanged; the number was not
reproducible from any selection, and the row now states 1,405.

**The index claimed a completeness the register did not have.**
`tasks/README.md` said every commit those branches carry is registered, one row
each. At `9ae7d2a1` that was false, and that commit's own message said so:
`git log --no-merges --reverse --abbrev=8 8161689a..9ae7d2a1` printed 106 commits
against 103 register rows, leaving `5031e735`, `cca2321c` and `9ae7d2a1`
unregistered — while the register's own paragraph qualified itself and the index
sentence did not. Both are repaired rather than one. The register's coverage tip
now sits after the merge `6bcd5e0f`, so the covered range is both lines of
authorship: it carries 108 rows, adding those three plus this round's two code
commits, and `.venv/bin/pytest tests/scripts/test_review_ledger_register.py -q`
passes 3. `5031e735` and `cca2321c` derive a `—` card column because git reads
trailers only from a message's last paragraph and both put a blank line between
`Card:` and `Co-Authored-By:`; the register says so and names the card their
bodies give. The index sentence now names the coverage tip and the residual that
remains — the commit that writes the register cannot carry its own row, which is
the commit carrying this paragraph.

No recorded byte changes in this round. The commits touch
`scripts/validate_task_docs.py`, `scripts/check_doc_facts.py`, their tests, this
card, `tasks/README.md` and `tasks/review-ledger.md`. No `GENERATOR_SOURCES` file
moved, so no held-out restamp is due, and no `audits/` byte moved, so the
`docs/artifacts.md` `audits/` row stands at 14,926,913 tracked bytes / 204 files
— confirmed against disk, and now the figure PR #444's body states, having
carried the pre-merge 14,926,477 until this round.

Re-run at this head — the tree at `7b25ad36` plus the card, index and ledger
records in the commit that carries this paragraph:

```sh
bash scripts/check.sh
bash scripts/verify_samples.sh
AILIBI_SAMPLES_ROOT="$PWD/replays/ml_corpus" bash scripts/verify_samples.sh
.venv/bin/pytest tests/orchestrator/ --collect-only -q
.venv/bin/pytest tests/scripts tests/meetings/test_lever_registry.py \
  tests/api/test_public_results.py -q
uv run python scripts/build_sample_report.py --sample-dir <set> --check
```

`scripts/check.sh` exited 0: 7,512 Python tests (the ten previous rows' 7,508
plus this round's four planted cases), 20 optional skips and three expected
failures; 515 frontend tests across 19 files; strict typing on 474 sources; ruff
lint and format; four import contracts kept; task-doc and generated-type checks;
and the production build. `verify_samples.sh` verified all 300 canonical
recordings — 100 under `replays/samples/` and 200 under `replays/ml_corpus/` —
without modifying their bytes. `tests/orchestrator/` collects 586 tests in a
fresh interpreter. The card's targeted selection passed 1,393 with one warning,
four more than the 1,389 of round 0. All four `--check` runs report their
committed report consistent with its replays. The browser journeys were not run:
no served DTO changed, and no frontend byte moved this round.
