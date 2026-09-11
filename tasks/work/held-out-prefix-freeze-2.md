# Freeze a second held-out band after the stopped run revealed the first

**Status:** done

## Outcome

A second held-out set of fifty proof-free scripted prefixes is frozen and
hashed from a band preregistered in this card, by a preparer session that will
never run the evaluation, so the fresh-model deduction instrument can be run
again on inputs nobody has rendered. The first band's freeze record is marked
development rather than deleted, with the reason written into it. The owner's
merge of the preparer's pull request is the second freeze.

## Evidence

The live run of 2026-09-10 (PR #445, branch `work/fresh-deduction-run`, left
unmerged by the owner's decision) rendered seed 3000 of the 3000-3999 band to
the model before an instrument accounting defect stopped it; seeds 3001-3057
were digest-checked and discarded unrendered. The preregistration
(`audits/deduction-candidate/preregistration.md:143-149`) and the first freeze
card (`held-out-prefix-freeze.md`, Constraints) make a rendered or inspected
held-out input development data, and the execution manifest's Roles section
says a result that informs a fix marks the set development by setting the
freeze manifest's `status`, never by deleting the file. The stop informs
[the reconciliation fix](fresh-deduction-instrument-reconciliation.md), so the
first band is development data and the preregistered design of fifty paired
units needs a clean band.

`experiments/held_out_prefixes.py` pins the band as `PREREGISTERED_BAND`
(`:349`) and the current freeze record's path as `MANIFEST_PATH` (`:146`); the
instrument's `verify_frozen_set` reads that path, and the module's `--tally`
and `--skip-roles` guards refuse any range touching the preregistered band. The
review tally over 4000-4999 printed counts only (864 accepted, 136 skipped); no
seed above 3999 has been rendered or inspected. The band below is chosen above
that range so no earlier command has touched it even in aggregate.

## Acceptance

- [x] Review correction: the execution manifest's Inputs row may bind a
  converted record only while the re-binding is an open obligation. The binding
  test asserts the bound record's `status`: a held-out binding has to be the
  live freeze itself, and a development one has to name that freeze as its
  replacement and leave the card that owes the row open and still naming the
  record it owes. Three planted defects fail it. The runtime band check the
  review asks for lands in `assert_live_run_is_authorized`, which this card may
  not edit, so it is an acceptance item of the card that owns that file.
- [x] Review correction: the `audits/` byte-count command quoted in
  Verification is portable rather than the BSD-only `stat -f %z`, re-run with
  its output quoted verbatim; the row it recomputes is unchanged at 14,940,217
  bytes across 205 files.
- [x] The preregistered band is seeds 5000 to 5999 drawn ascending; the first
  fifty prefixes that pass the unchanged proof-free filter form the set, every
  skipped seed is recorded with its reason code, and seed 1, the seven
  development definitions and every seed of the 3000-3999 band are excluded by
  construction. The generator's drawing logic, filter and roster do not change;
  only the band constant moves.
- [x] The 3000-3999 freeze record is preserved byte-for-byte except for its
  status: it moves to `audits/deduction-candidate/held-out/manifest-band-3000-3999.json`
  with `status` set to `development` and a `converted` record naming the date,
  the run (PR #445, branch `work/fresh-deduction-run`), which seed was rendered
  (3000) and which fix the result informed. A test asserts its `accepted` and
  `skipped` blocks equal the ones frozen at `23a23c2d`.
- [x] The new freeze record is written to `MANIFEST_PATH`
  (`audits/deduction-candidate/held-out/manifest.json`) by the unchanged
  `build_manifest`, so the instrument's `verify_frozen_set` and the regeneration
  test cover the current band without an instrument change. It records the
  band, the roster, the source digests, the fifty accepted digests, the skips,
  the development definitions' digests asserted absent, and a `dependency_restamps`
  list that starts empty for this band.
- [x] No prefix bytes are committed; the preparer inspects no generated prefix
  beyond the automated filter and hash computation, runs no arm, and makes no
  provider call. Debugging uses seeds outside both bands.
- [x] `docs/artifacts.md`'s `audits/` inventory row is recomputed with both
  manifests staged, and `scripts/verify_ml_evidence.py` passes offline.
- [x] Results states the accepted and skipped counts, the reason histogram, the
  last accepted seed, the new manifest's sha256 and byte size, and the
  reproducible commands (`uv run python -m experiments.held_out_prefixes
  --tally FIRST LAST` on an out-of-band range and `--skip-roles manifest`).

## Constraints

No live provider; fake and scripted providers only, and no meeting model call
of any kind. The band is preregistered here and may not be changed by the
preparer; a band that cannot fill fifty is a stop, not a wider band. The
preparer edits `experiments/held_out_prefixes.py` only to move the band and to
add the `converted` record shape; it does not edit
`experiments/fresh_deduction_instrument.py`, the execution manifest,
`experiments/deduction_scenarios.py` or `experiments/deduction_evaluation.py`.
The execution manifest's Inputs table is re-bound to the new band by
[the reconciliation card](fresh-deduction-instrument-reconciliation.md), which
lands after this card. Nobody opens a generated prefix; the review surface is
generator code, tests and the hash manifests; the owner's merge is the freeze.
No adoption, no re-record, no committed recording or report rewritten.

## Expected scope

`experiments/held_out_prefixes.py` (band constant, `converted` record shape),
`tests/experiments/test_held_out_prefixes.py`,
`audits/deduction-candidate/held-out/manifest.json` (the new band),
`audits/deduction-candidate/held-out/manifest-band-3000-3999.json` (the first
band, moved and marked development), `audits/deduction-candidate/README.md`
(index the moved record), `docs/artifacts.md` (the `audits/` row), this card.
Delivered on `work/held-out-prefix-freeze-2` and one pull request into `main`.

## Record impact

Adds a second frozen evaluation-input record under `audits/` and flips the
first to development in place; no recording, report, DTO, metric or weight byte
moves, no experiment becomes ON, no adopting record is created.

## Validation

`uv run pytest tests/experiments/test_held_out_prefixes.py -q`, then
`uv run python scripts/validate_task_docs.py`, `uv run python
scripts/check_doc_facts.py`, `uv run python scripts/verify_ml_evidence.py`
(offline; never `--complete`), `uv run pytest
tests/scripts/test_verify_ml_evidence.py -q`, and `bash scripts/check.sh`. Do
not run the live evaluation as a check.

## Results

**Preparer statement.** This session inspected no generated prefix beyond the
automated filter and hash computation, ran no arm, and made no provider call of
any kind. Nothing outside the filter ever held a prefix: the only per-seed
values that left the generator are the seeds, the reason codes and the sha256
digests the manifest records. Seeds inspected outside both bands: seed 1 (the
seven committed development cases' seed, used by every planted prefix in
`tests/experiments/test_held_out_prefixes.py`) and the debugging seeds
9001-9002. The tally ranges below (4000-4999, and 9001 onward inside the
`build_manifest` shape test) were walked for counts only; no prefix from them
was printed or opened either.

Every number and command in this section was measured on commit `be65f34e`,
which holds the code, the two manifests and the docs; this section and the
index sentence are the commit that follows it.

### The second band

`generate()` drew the preregistered band 5000-5999 ascending and stopped at
fifty. It consumed 53 seeds: **50 accepted, 3 skipped**, every skip for the same
reason.

| reason code | skipped | seeds |
| --- | --- | --- |
| `witnessed_kill` | 3 | 5011, 5029, 5045 |

The first accepted seed is 5000 and the **last accepted seed is 5052**; 947 band
seeds were never drawn and the band was not widened. No `witnessed_vent` skip
occurred, because the generator scripts no vent — the vent half of the filter is
held by the planted case `test_a_planted_witnessed_vent_fails_the_filter`, not
by a band seed. The accepted seeds, the skips and the counts are the manifest's
own `accepted`, `skipped` and `skipped_reason_counts`.

`audits/deduction-candidate/held-out/manifest.json` is the new freeze artifact —
**sha256 `b93262acc21af1b2c98ec97f84d9f3b23a8740ab7b22fc91ac79f3c2911cdfa1`**,
11,712 bytes. It is written by `build_manifest` called the way a freeze calls it
(no `converted` record), so its shape is the shape the first freeze produced:
band, roster, tick budget, temporal version, the filter's stated environment,
the canonical-JSON recipe, the sha256 of the 22 generator sources, the fifty
accepted seeds with their digests in band order, the three skips, the seven
development definitions' digests asserted absent, and a `dependency_restamps`
list that starts empty for this band. `status` reads `held_out`, which is what
`experiments/fresh_deduction_instrument.verify_frozen_set` requires; the
instrument was not edited.

The two bands share no seed and no digest
(`test_the_current_freeze_is_the_second_band_and_starts_without_restamps`), and
the seven development definitions' digests are absent from `accepted[]` twice
over: `build_manifest` raises on a collision, and
`test_the_manifest_records_the_development_definitions_as_absent` compares the
committed record.

The out-of-band rejection rate reproduces offline, aggregates only:

```text
$ uv run python -m experiments.held_out_prefixes --tally 4000 4999
seeds 1000
accepted 864
witnessed_kill 136
```

which is the same 864/136 the card's Evidence quotes from the first freeze's
review, on the same generator logic. The band's own three skips split by the
role whose wander witnessed the kill:

```text
$ uv run python -m experiments.held_out_prefixes --skip-roles manifest
seeds 3
bystander 1
reporter 2
```

Both commands refuse a range that touches either frozen band, so neither can be
turned on the held-out set.

### The first band, marked rather than deleted

`audits/deduction-candidate/held-out/manifest-band-3000-3999.json` is the
3000-3999 record after `git mv` — **sha256
`ca4cd057acb2119646190fb6fff923a897ec207d5f54c491c3e1dfae0944cf3c`**, 15,677
bytes. Against the bytes the owner's merge froze at `23a23c2d`, the whole diff
is the `status` flip, the new `converted` block and the four dependency
restamps that landed between `23a23c2d` and this branch's base:

```text
$ git diff --stat 23a23c2d:audits/deduction-candidate/held-out/manifest.json \
    be65f34e:audits/deduction-candidate/held-out/manifest-band-3000-3999.json
 ...{manifest.json => manifest-band-3000-3999.json} | 52 ++++++++++++++++++++--
 1 file changed, 48 insertions(+), 4 deletions(-)
```

`accepted` and `skipped` are byte-identical to that freeze, pinned by digest in
`test_the_converted_band_keeps_the_blocks_it_was_frozen_with` rather than by a
copy of fifty rows. The `converted` block names the date (2026-09-10), the run
(PR #445 on `work/fresh-deduction-run`), the one rendered seed (3000), the fix
the stop informed
(`tasks/work/fresh-deduction-instrument-reconciliation.md`) and the record that
replaced it. Its shape is `ConvertedRecord`, a frozen Pydantic model with
`extra="forbid"`, and the test validates the committed block through it.

### Decisions

1. **The guards refuse the converted band too.** A walk over 3000-3999 would
   leak nothing now — those prefixes are development data — so the refusal is
   not a secrecy claim. What it protects is the meaning of the number `--tally`
   and `--skip-roles` print, which both freeze cards quote as the *out-of-band*
   rejection rate. The message says which band and where its record lives.
2. **`build_manifest` gained one optional keyword.** The Acceptance item asks
   for the unchanged function, and the drawing, hashing and held-out output are
   unchanged: called without `converted` — which is how the freeze calls it and
   how `write_manifest` calls it — the manifest carries no `converted` key at
   all and has exactly the shape it had before. The parameter exists so the
   module, not a session's prose, defines the block an in-place conversion
   writes. The already committed manifest was NOT regenerated: its digests are
   history and were edited in place.
3. **`DEPENDENCY_RESTAMPS` starts empty.** The first band's four restamps stay
   in that band's own record, where they describe the sources its digests were
   drawn under. Carrying them into a new band's manifest would claim restamps
   for a set that has never been restamped.
4. **Four band pins in `tests/experiments/test_fresh_deduction_instrument.py`
   were decoupled** (see Deviations).

### Verification

Commands run on `be65f34e` from a clean worktree:

| command | result |
| --- | --- |
| `uv run pytest tests/experiments/test_held_out_prefixes.py -q` | 32 passed |
| `uv run pytest tests/experiments -q` | 231 passed |
| `uv run python scripts/validate_task_docs.py` | 390 phase tasks, 45 work cards |
| `uv run python scripts/check_doc_facts.py` | passed |
| `uv run python scripts/verify_ml_evidence.py` | checks 60, OK 48, FAIL 0, ABSENT 7, INFO 5 |
| `uv run pytest tests/scripts/test_verify_ml_evidence.py -q` | 80 passed |
| `bash scripts/check.sh` | exit 0 — 7516 passed, 20 skipped, 3 xfailed; mypy 474 files; frontend 515 passed |

The seven `ABSENT` rows are the evidence-branch bytes a fresh clone does not
carry, the expected state; `--complete` was not run. `docs/artifacts.md`'s
`audits/` row was recomputed with both manifests staged and now reads
**14,940,217 tracked bytes / 205 files**, from

```text
$ git ls-files -z audits | xargs -0 wc -c | awk '$2 != "total" {n += 1; s += $1} END {print n, s}'
205 14940217
```

(The command was BSD-only when this card was first closed; see round 1 below.
The total it prints did not change.)

### Planted failures

Each perturbation was applied to the tree at `be65f34e`, run, and reverted with
`git checkout --`; the working tree is clean afterwards and each test passes
again.

| planted defect | test | failure |
| --- | --- | --- |
| the range guard iterates no converted bands (`for converted in ():`) | `test_the_range_walks_refuse_a_converted_band_as_well` | `Failed: DID NOT RAISE <class 'experiments.held_out_prefixes.HeldOutPrefixError'>` |
| one accepted digest of the moved record rewritten to `0`×64 | `test_the_converted_band_keeps_the_blocks_it_was_frozen_with` | `assert '103dd63ca12a...' == '88ae6211483a...'` |
| the moved record's `status` set back to `held_out` | `test_the_converted_band_keeps_the_blocks_it_was_frozen_with` | `assert 'held_out' == 'development'` |
| `build_manifest` writes `"status": "held_out"` unconditionally | `test_a_converted_record_flips_the_status_and_changes_nothing_else` | `assert 'held_out' == 'development'` |

The band-move itself needs no new plant: the pre-existing
`test_the_committed_manifest_regenerates_from_its_own_band` regenerates from the
band the committed manifest names and compares every field, and
`test_the_tally_refuses_to_probe_the_preregistered_band` reads the band constant,
so both followed the move without an edit.

### Deviations

`tests/experiments/test_fresh_deduction_instrument.py` is outside this card's
Expected scope, and four assertions in it pinned the first band's seeds: the
first accepted seed (`== 3000`), two dry-run replay file names
(`repaired_clock-seed-3000.jsonl`, `combined_accounts-seed-3000.jsonl`) and the
execution manifest's Inputs binding. They fail on the new band, and
`bash scripts/check.sh` is a delivery condition, so they were decoupled rather
than re-pinned: the three seed pins now read the first accepted seed from the
committed manifest, and the binding test resolves the band the Inputs row names
to the freeze record that holds it — the live one, or a converted one while a
re-binding is outstanding. That last change relaxes an assertion: until
[the reconciliation card](fresh-deduction-instrument-reconciliation.md) re-binds
the Inputs table, the execution manifest cites the converted record instead of
the live freeze, and the test accepts that intermediate state — but only while
the re-binding stays an open obligation, which round 1 below is what tightened.
It still refuses a row whose numbers match no committed record and a row naming
more than one band. The file's next writer is that card, which lands after this
one; no non-test instrument byte was touched. Round 1 also writes one acceptance
item into that card, `tasks/work/fresh-deduction-instrument-reconciliation.md`,
which is likewise outside this card's Expected scope.

### Limitations

The set is not frozen until the owner merges this pull request. This card
proves the inputs exist, are reproducible from the module and the band, and are
disjoint from every set anybody has read; it proves nothing about the
evaluation, which needs a new owner authorization card. The three skips are too
few to say anything about the filter's rate — the 1000-seed out-of-band tally is
the honest figure for that. A second freeze also does not restore what the
stopped run cost: 3000-3999 can never serve as a held-out band again, and a
third rendering accident would cost this band the same way.

### Review corrections, round 1 (2026-09-10)

One review lens returned one blocking finding over the head `a6f3d4d0`, and the
Codex reviewer left two P1 inline comments on that same commit; the finding is
the first of those comments, reported again. Both are valid. The first is
repaired at `34004a90`, the second in the Verification block above. No `audits/`
byte, no manifest and no generator source moved in this round, so every number
in the sections above still stands as measured.

**1. A stale binding could have gone silent.** Codex P1 on
`tests/experiments/test_fresh_deduction_instrument.py:2419`, "Block live runs
until the manifest names the new band".

*What was true at `a6f3d4d0`.* The execution manifest's Inputs table still binds
the first band (`audits/deduction-candidate/execution-manifest.md:128-129`:
"Seed band | 3000–3999 … accepted seeds run 3000–3057 with 8 skips") while
`MANIFEST_PATH` holds 5000-5999. The assertion that had coupled the document to
the inputs — the old binding test, which required the LIVE manifest's band to
appear in the manifest text — was replaced on this branch by one that accepts a
converted record and never reads its `status`.
`assert_live_run_is_authorized` (`experiments/fresh_deduction_instrument.py:637-724`)
checks the provider, the model, the units, the limits, the sampling, the
execution manifest's path and its sha256, and no band. So at that head nothing,
offline or at run time, required the authorization document to name the band
`verify_frozen_set` regenerates, and the relaxation the Deviations note
describes had no expiry.

*Repaired at `34004a90`.* The binding test resolves the bound record as before
and now asserts its `status`. A `held_out` binding has to be the live freeze at
`MANIFEST_PATH` itself. A `development` binding is allowed only as an open
obligation: the record's `converted.superseded_by` has to name `MANIFEST_PATH`,
that record has to be `held_out` and of a different band, and the card the
conversion named in `converted.informed` has to be still open and still name the
record it owes the row. The relaxation therefore cannot become permanent — the
moment the reconciliation card closes with the row still stale, the gate fails.

*Not repaired here, and routed.* The runtime cross-check Codex asks for belongs
in `assert_live_run_is_authorized`, and this card's Constraints forbid editing
`experiments/fresh_deduction_instrument.py`. It is now the fourth acceptance
item of `tasks/work/fresh-deduction-instrument-reconciliation.md`, the card that
owns that file and re-binds the Inputs table: the gate reads the band the
manifest's Inputs row names, compares it against the record at `MANIFEST_PATH`,
raises `LiveRunNotAuthorized` before a client exists, and carries a planted
stale binding as its proof.

*What stands until then,* stated exactly, because neither of these is the band
check. First, no live run is authorized at all: the second run needs a new owner
authorization card carrying the owner's fields and none exists, and the
execution manifest says so of itself — "This document authorizes no live call"
and "#437 authorized LIMITS, not a run", both pinned by
`test_the_manifest_states_that_it_authorizes_no_run`. Second, the converted band
cannot be re-run by this mismatch in either direction: `verify_frozen_set`
refuses any record at `MANIFEST_PATH` whose `status` is not `held_out`
(`experiments/fresh_deduction_instrument.py:1448-1453`), and the 3000-3999
record is not at that path and is marked `development`. What the mismatch could
still do, until the gate lands, is spend the second band under a document whose
Inputs row describes the first — a provenance defect in the run's own record,
which is why it is an acceptance item rather than a note.

Planted defects for the tightened gate, each applied to the tree at `34004a90`,
run, and reverted with `git checkout --`:

| planted defect | failure |
| --- | --- |
| the re-binding card's `**Status:**` flipped to `done` with the row still stale | `AssertionError: fresh-deduction-instrument-reconciliation.md is closed while the execution manifest still binds the converted manifest-band-3000-3999.json` |
| that card's text no longer names `audits/deduction-candidate/held-out/manifest.json` | `AssertionError: fresh-deduction-instrument-reconciliation.md owes the Inputs row a binding to audits/deduction-candidate/held-out/manifest.json and no longer names it` |
| the converted record's `superseded_by` pointed at a band that is not the live freeze | `AssertionError: manifest-band-3000-3999.json is bound while development and names 'audits/deduction-candidate/held-out/manifest-band-4000-4999.json' as its replacement, not the live freeze audits/deduction-candidate/held-out/manifest.json` |

All three fail `TestExecutionManifest::test_a_binding_to_a_converted_record_stays_an_open_obligation`,
which passes on the unperturbed tree.

**2. The byte-count command was BSD-only.** Codex P1 on this card's
Verification block, "Replace the nonportable byte-count command".

Valid. `stat -f %z` is the BSD spelling and is what this macOS session ran; with
GNU coreutils `-f` asks for filesystem status and `%z` is read as a file name,
so the quoted pipeline prints an error and no sizes on the Linux image. The two
numbers were right — `docs/artifacts.md`'s `audits/` row has not moved — but the
command as written reproduced nowhere but this machine. The Verification block
above now quotes the portable form, re-run at `34004a90`:

```text
$ git ls-files -z audits | xargs -0 wc -c | awk '$2 != "total" {n += 1; s += $1} END {print n, s}'
205 14940217
```

It measures what the row means: `scripts/verify_ml_evidence.py` sums
`stat().st_size` over `git ls-files -z` for the same directory
(`scripts/verify_ml_evidence.py:2885`), and the `$2 != "total"` filter drops
`wc`'s own subtotal lines so the count is right however `xargs` batches.

*Gates re-run on this round's tree.*

| command | result |
| --- | --- |
| `uv run pytest tests/experiments/test_held_out_prefixes.py -q` | 32 passed |
| `uv run pytest tests/experiments -q` | 232 passed |
| `uv run python scripts/validate_task_docs.py` | 390 phase tasks, 45 work cards |
| `uv run python scripts/check_doc_facts.py` | passed |
| `uv run python scripts/verify_ml_evidence.py` | checks 60, OK 48, FAIL 0, ABSENT 7, INFO 5 |
| `uv run pytest tests/scripts/test_verify_ml_evidence.py -q` | 80 passed |
| `bash scripts/check.sh` | exit 0 — 7517 passed, 20 skipped, 3 xfailed; mypy 474 files; frontend 515 passed |

No prefix was inspected, no arm was run and no provider call of any kind was
made in this round; no seed outside those already listed was touched.
