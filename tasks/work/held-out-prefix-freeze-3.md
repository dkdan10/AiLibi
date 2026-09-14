# Freeze a third held-out band after the second run revealed the second

**Status:** done

## Outcome

A third held-out set of fifty proof-free scripted prefixes is frozen and hashed
from a band preregistered in this card, by a preparer session that will never
run the evaluation, so the fresh-model deduction instrument can be run again on
inputs nobody has rendered. The second band's freeze record is marked
development in place, with the reason written into it, the way the first was.
The owner's merge of the preparer's pull request is the third freeze.

## Evidence

The second live run (PR #448, closed unmerged; branch `work/fresh-deduction-run-2`
is its archive) rendered seed 5000 of the 5000-5999 band to the model before
the provider returned an empty completion and the run stopped inside its first
unit; seeds 5001-5052 were digest-checked and discarded unrendered. The
preregistration (`audits/deduction-candidate/preregistration.md:143-149`) and
both freeze cards make a rendered held-out input development data, and the
execution manifest's Roles section says a result that informs a fix marks the
set development by setting the freeze record's `status`, never by deleting the
file. The stop informs [the transport-resilience card](fresh-deduction-instrument-transport-resilience.md),
so the second band is development data and the preregistered design of fifty
paired units needs a clean band. `experiments/held_out_prefixes.py` already
carries the band constant, the converted-band list (`CONVERTED_BANDS`), the
`converted` record shape and the range guards the second freeze introduced;
this card repeats that procedure one band up. No seed above 5999 has been
rendered, inspected or tallied.

## Acceptance

- [x] The preregistered band is seeds 6000 to 6999 drawn ascending; the first
  fifty prefixes that pass the unchanged proof-free filter form the set, every
  skipped seed is recorded with its reason code, and seed 1, the seven
  development definitions and every seed of the 3000-3999 and 5000-5999 bands
  are excluded by construction. The generator's drawing logic, filter and
  roster do not change; only the band constant and the converted-band list move.
- [x] The 5000-5999 freeze record moves to
  `audits/deduction-candidate/held-out/manifest-band-5000-5999.json` with `git mv`,
  its bytes preserved except `status: development` and a `converted` record
  naming the date, the run (PR #448, branch `work/fresh-deduction-run-2`), the
  rendered seed (5000) and the fix the result informed. A test asserts its
  `accepted` and `skipped` blocks equal the ones frozen at `ca6e97d6`.
- [x] The new freeze record is written to `MANIFEST_PATH` by the unchanged
  `build_manifest` (status held_out, `dependency_restamps` empty, the seven
  development definitions and both converted bands' digests asserted absent),
  so the instrument's `verify_frozen_set` and the regeneration test cover the
  current band without an instrument change.
- [x] No prefix bytes are committed; the preparer inspects no generated prefix
  beyond the automated filter and hash computation, runs no arm, and makes no
  provider call. Debugging uses seeds outside every band.
- [x] `docs/artifacts.md`'s `audits/` inventory row is recomputed with the
  records staged, and `scripts/verify_ml_evidence.py` passes offline.
- [x] Results states the accepted and skipped counts, the reason histogram, the
  last accepted seed, the new record's sha256 and byte size, and the
  reproducible commands (`uv run python -m experiments.held_out_prefixes
  --tally FIRST LAST` on an out-of-band range and `--skip-roles manifest`).

## Constraints

No live provider; fake and scripted providers only. The band is preregistered
here and may not be changed; a band that cannot fill fifty is a stop. The
preparer edits `experiments/held_out_prefixes.py` only for the band constant
and the converted-band list; it does not edit
`experiments/fresh_deduction_instrument.py`, the execution manifest,
`experiments/deduction_scenarios.py` or `experiments/deduction_evaluation.py`.
The execution manifest's Inputs table is re-bound to the new band by
[the transport-resilience card](fresh-deduction-instrument-transport-resilience.md),
which lands after this card. Nobody opens a generated prefix; the owner's merge
is the freeze. No adoption, no re-record, no committed recording or report
rewritten.

## Expected scope

`experiments/held_out_prefixes.py` (band constant, converted-band list),
`tests/experiments/test_held_out_prefixes.py`, the instrument's tests only
where they pin the first accepted seed or the band,
`audits/deduction-candidate/held-out/manifest.json` (the new band),
`audits/deduction-candidate/held-out/manifest-band-5000-5999.json` (the second
band, moved and marked development), `audits/deduction-candidate/README.md`
(index the moved record), `docs/artifacts.md` (the `audits/` row),
`tasks/README.md`'s derived inventory sentence, this card. Delivered on
`work/held-out-prefix-freeze-3` and one pull request into `main`.

## Record impact

Adds a third frozen evaluation-input record under `audits/` and flips the
second to development in place; no recording, report, DTO, metric or weight
byte moves, no experiment becomes ON, no adopting record is created.

## Validation

`uv run pytest tests/experiments -q`, then `uv run python
scripts/validate_task_docs.py`, `uv run python scripts/check_doc_facts.py`,
`uv run python scripts/verify_ml_evidence.py` (offline; never `--complete`),
`uv run pytest tests/scripts/test_verify_ml_evidence.py -q`, and
`bash scripts/check.sh`. Do not run the live evaluation as a check.

## Results

**Preparer statement.** This session inspected no generated prefix beyond the
automated filter and hash computation, ran no arm, and made no provider call of
any kind. Nothing outside the filter ever held a prefix: the only per-seed
values that left the generator are the seeds, the reason codes and the sha256
digests the manifest records. Seeds inspected outside every band: seed 1 (the
seven committed development cases' seed, which every planted prefix in
`tests/experiments/test_held_out_prefixes.py` is built on) and the debugging
seeds 9001-9002. The ranges walked below — 4000-4999 for the tally, and
9001-9100 inside the `build_manifest` shape test — were walked for counts only;
no prefix from them was printed or opened either.

Every number and command in this section was measured on commit `ba5f5b0e`,
which holds the code, the three records and the docs; this section and the
index sentence are the commit that follows it.

### The third band

`generate()` drew the preregistered band 6000-6999 ascending and stopped at
fifty. It consumed 59 seeds: **50 accepted, 9 skipped**, every skip for the same
reason.

| reason code | skipped | seeds |
| --- | --- | --- |
| `witnessed_kill` | 9 | 6002, 6013, 6019, 6026, 6030, 6031, 6038, 6041, 6043 |

The first accepted seed is 6000 and the **last accepted seed is 6058**; 941 band
seeds were never drawn and the band was not widened. No `witnessed_vent` skip
occurred, because the generator scripts no vent — the vent half of the filter is
held by the planted case `test_a_planted_witnessed_vent_fails_the_filter`, not
by a band seed. The accepted seeds, the skips and the counts are the manifest's
own `accepted`, `skipped` and `skipped_reason_counts`.

`audits/deduction-candidate/held-out/manifest.json` is the new freeze artifact —
**sha256 `7ded19906a7026ae3724894af67cf3667d35f4230d532bf825e495d4666ecd37`**,
12,108 bytes. It is written by `build_manifest` called the way a freeze calls it
(no `converted` record), so its shape is the shape both earlier freezes
produced: band, roster, tick budget, temporal version, the filter's stated
environment, the canonical-JSON recipe, the sha256 of the 22 generator sources,
the fifty accepted seeds with their digests in band order, the nine skips, the
seven development definitions' digests asserted absent, and a
`dependency_restamps` list that starts empty for this band. `status` reads
`held_out`, which is what `experiments/fresh_deduction_instrument.verify_frozen_set`
requires; no non-test byte of the instrument was touched.

The live band shares no seed and no digest with EITHER converted band —
`test_the_current_freeze_is_the_third_band_and_starts_without_restamps` loops
`CONVERTED_BANDS` rather than naming one record — and the seven development
definitions' digests are absent from `accepted[]` twice over: `build_manifest`
raises on a collision, and
`test_the_manifest_records_the_development_definitions_as_absent` compares the
committed record.

The out-of-band rejection rate reproduces offline, aggregates only, on the same
range the second freeze quoted:

```text
$ uv run python -m experiments.held_out_prefixes --tally 4000 4999
seeds 1000
accepted 864
witnessed_kill 136
```

4000-4999 lies between the two converted bands and below the live one, so it is
still out of every band. The band's own nine skips split by the role whose
wander witnessed the kill:

```text
$ uv run python -m experiments.held_out_prefixes --skip-roles manifest
seeds 9
bystander 2
reporter 7
```

Both commands refuse a range that touches any of the three bands, so neither can
be turned on the held-out set.

### The second band, marked rather than deleted

`audits/deduction-candidate/held-out/manifest-band-5000-5999.json` is the
5000-5999 record after `git mv` — **sha256
`4fc831dafeda0a6ee7fc311e6557c149506be1fabcf05c69b2117ddb436f7711`**, 12,933
bytes. That record carried no dependency restamp, so against the bytes the
owner's merge froze at `ca6e97d6` the whole diff is the `status` flip and the
new `converted` block:

```text
$ git show ca6e97d6:audits/deduction-candidate/held-out/manifest.json > /tmp/frozen.json
$ git diff --no-index --stat /tmp/frozen.json \
    audits/deduction-candidate/held-out/manifest-band-5000-5999.json
 .../held-out/manifest-band-5000-5999.json | 13 ++++++++++++-
 1 file changed, 12 insertions(+), 1 deletion(-)
```

`accepted` and `skipped` are byte-identical to that freeze, pinned by digest in
`test_the_converted_second_band_keeps_the_blocks_it_was_frozen_with` rather than
by a copy of fifty rows. The `converted` block names the date (2026-09-13), the
run (PR #448 on `work/fresh-deduction-run-2`), the one rendered seed (5000), the
fix the stop informed
(`tasks/work/fresh-deduction-instrument-transport-resilience.md`) and the record
that replaced it. Its shape is `ConvertedRecord`, the frozen Pydantic model with
`extra="forbid"` the second freeze added, and the test validates the committed
block through it. The record was NOT regenerated: its digests are history and
were edited in place.

`audits/deduction-candidate/README.md` now indexes all three records: the live
freeze, and each converted band with the run that rendered into it, the fix it
informed and the commit its digests were frozen at.

### Decisions

1. **The guards refuse the second band too, and the test no longer trusts the
   list.** `CONVERTED_BANDS` gained the 5000-5999 entry, so `--tally` and
   `--skip-roles` refuse that range the way they refuse 3000-3999. What the
   refusal protects is not secrecy — both converted bands are development data —
   but the meaning of the number both commands print, which all three freeze
   cards quote as the *out-of-band* rejection rate. The range-walk test used to
   iterate `CONVERTED_BANDS`, the list under test, so dropping an entry took
   that band's case with it and the test stayed green; it now reads the
   committed `manifest-band-*.json` records off disk first and asserts the list
   names exactly those (`20448533`).
2. **A range that spills off a converted band onto the live one is refused for
   the live band.** The top edge of 5000-5999 is now adjacent to 6000-6999, so
   the case `(5999, 6000)` hits the preregistered-band check first. The test
   asserts that refusal rather than the converted-band wording for exactly the
   ranges that touch both; every range that touches only a converted band still
   has to name that band's record path.
3. **`DEPENDENCY_RESTAMPS` starts empty again.** The 3000-3999 band's four
   restamps stay in that band's own record. The 5000-5999 band accumulated none
   at all between `ca6e97d6` and this branch's base, which is why its diff is
   twelve inserted lines rather than fifty.
4. **The execution manifest's Inputs row is left stale on purpose**, and the
   gate that refuses it is asserted rather than relaxed (see Deviations).

### Verification

Commands run on `ba5f5b0e` from this branch's worktree:

| command | result |
| --- | --- |
| `uv run pytest tests/experiments/test_held_out_prefixes.py -q` | 33 passed |
| `uv run pytest tests/experiments -q` | 261 passed |
| `uv run python scripts/validate_task_docs.py` | 390 phase tasks, 49 work cards |
| `uv run python scripts/check_doc_facts.py` | passed |
| `uv run python scripts/verify_ml_evidence.py` | checks 60, OK 48, FAIL 0, ABSENT 7, INFO 5 |
| `uv run pytest tests/scripts/test_verify_ml_evidence.py -q` | 80 passed |
| `bash scripts/check.sh` | exit 0 — 7546 passed, 20 skipped, 3 xfailed; mypy 475 files; frontend 515 passed |

The seven `ABSENT` rows are the evidence-branch bytes a fresh clone does not
carry, the expected state; `--complete` was not run. `docs/artifacts.md`'s
`audits/` row was recomputed with all three records staged and now reads
**14,964,052 tracked bytes / 206 files**, from

```text
$ git ls-files -z audits | xargs -0 wc -c | awk '$2 != "total" {n += 1; s += $1} END {print n, s}'
206 14964052
```

which measures what the row means: `scripts/verify_ml_evidence.py` sums
`stat().st_size` over `git ls-files -z` for the same directory, and the
`$2 != "total"` filter drops `wc`'s own subtotal lines.

### Planted failures

Each perturbation was applied to the tree at the commit named, run, and reverted
with `git checkout --`; the working tree is clean afterwards and each test passes
again.

| planted defect | tree | test | failure |
| --- | --- | --- | --- |
| one accepted digest of the moved 5000-5999 record rewritten to `0`×64 | `ebb02e44` | `test_the_converted_second_band_keeps_the_blocks_it_was_frozen_with` | `assert '19972c658e56...' == 'fab9a1c584e8...'` |
| the moved record's `status` set back to `held_out` | `ebb02e44` | same | `assert 'held_out' == 'development'` |
| the 5000-5999 entry dropped from `CONVERTED_BANDS` | `20448533` | `test_the_range_walks_refuse_a_converted_band_as_well` | `AssertionError: every committed manifest-band-*.json is a band CONVERTED_BANDS names, or the range guard no longer refuses it` |
| the Inputs row bound to 4000-4999, a band no committed record holds | `20448533` | `test_the_committed_manifest_binds_the_live_band_or_is_refused` | `AssertionError: the Inputs row binds seed band 4000-4999, which is neither the live freeze nor a converted record` |
| `assert_manifest_binds_the_live_band` stops refusing (`if False:`) | `20448533` | same | `Failed: DID NOT RAISE <class '…LiveRunNotAuthorized'>` |
| the transport-resilience card's `**Status:**` flipped to `done` with the row still stale | `20448533` | `test_a_binding_to_a_converted_record_stays_an_open_obligation` | `AssertionError: fresh-deduction-instrument-transport-resilience.md is closed while the execution manifest still binds the converted manifest-band-5000-5999.json` |

The third plant is the one that changed a test on this branch: run against the
gate as the second freeze left it, dropping the entry left
`test_the_range_walks_refuse_a_converted_band_as_well` green and only the roster
case `test_the_preregistered_band_is_the_one_the_card_froze` red. The band move
itself needs no new plant: `test_the_committed_manifest_regenerates_from_its_own_band`
regenerates from the band the committed record names and compares every field,
and `test_the_tally_refuses_to_probe_the_preregistered_band` reads the band
constant, so both followed the move without an edit.

### Deviations

**1. The execution manifest's Inputs row is left bound to 5000-5999, and three
instrument tests moved to keep the gate honest.** This card may not edit
`audits/deduction-candidate/execution-manifest.md`; the re-binding is the
transport-resilience card's acceptance item, and that card lands after this one.
Since the reconciliation fix, `assert_manifest_binds_the_live_band`
(`experiments/fresh_deduction_instrument.py:641-680`) refuses a live run whose
Inputs row names a band the live record does not hold, so on this branch that
gate refuses — which is the intended behaviour and not something to relax. What
moved, all in `tests/experiments/test_fresh_deduction_instrument.py`, which the
Expected scope opens "only where they pin the first accepted seed or the band":

* `test_the_committed_manifest_binds_the_live_band` became
  `…_or_is_refused`: settled means the row and the record agree and the gate
  passes; otherwise the row has to name a band a *converted* record holds and
  the gate has to raise, naming both bands. Two of the plants above show that
  branch is not vacuous — a band no record holds fails it, and so does a gate
  that stops refusing.
* three cases that exercise what happens AFTER that check
  (`test_the_pre_client_gate_stops_on_a_moved_frozen_set`,
  `test_the_pre_client_gate_returns_the_verified_set`,
  `test_a_live_run_binds_the_client_to_the_invocations_model`) now run against
  `_root_binding_the_live_band`, which returns the repository itself whenever
  the row is settled and a copy of the committed document with that one row
  moved while it is not. They stop asserting that the committed tree is
  live-runnable, which it deliberately is not right now; the binding is asserted
  by the class above instead.

The expiry is unchanged and is what keeps this from becoming permanent:
`test_a_binding_to_a_converted_record_stays_an_open_obligation` requires the
bound converted record to name `MANIFEST_PATH` as its replacement and the card
in its `converted.informed` to be still open and still name that record. It
fails the moment the transport-resilience card closes with the row still stale.

**2. One acceptance item of `tasks/work/fresh-deduction-instrument-transport-resilience.md`
was edited**, which is outside this card's Expected scope. That item is the
obligation the gate above reads: it now spells out
`audits/deduction-candidate/held-out/manifest.json` and the moved record's path
in full, because the gate looks for the live record's path in that card's text
and the item said only "the new `held-out/manifest.json`". Nothing else in that
card moved; its Status is still `ready`.

**3. `test_the_range_walks_refuse_a_converted_band_as_well` was hardened**
beyond restating the second freeze's case (`20448533`, Decisions 1). It is
inside this card's Expected scope, but it is a gate the card did not ask for.

### Limitations

The set is not frozen until the owner merges this pull request. This card proves
the inputs exist, are reproducible from the module and the band, and are
disjoint from every set anybody has read; it proves nothing about the
evaluation, which needs its own owner authorization — `tasks/work/fresh-deduction-authorization-3.md`
is that card and is not this one's to close. Nothing here makes the instrument
survive the failure that stopped the second run: until the transport-resilience
card lands, a single empty completion would spend this band the way the last one
was spent. The nine skips are too few to say anything about the filter's rate —
the 1000-seed out-of-band tally is the honest figure for that — though nine
skips in 59 seeds against three in 53 is a reminder that a band's own skip count
is a small sample, not a property of the band. And a third freeze does not
restore what two stopped runs cost: 3000-3999 and 5000-5999 can never serve as
held-out bands again, and a third rendering accident would cost this band the
same way.
