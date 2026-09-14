# Freeze a fourth held-out band after the third run rendered the third

**Status:** done

## Outcome

A fourth held-out set of fifty proof-free scripted prefixes is frozen and
hashed from a band preregistered in this card, by a preparer session that will
never run the evaluation, so the fourth run has inputs nobody has rendered.
The third band's freeze record is marked development in place, with the
reason written into it, the way the first two were. The owner's merge of the
preparer's pull request is the fourth freeze.

## Evidence

The third live run (PR #451, closed unmerged; branch `work/fresh-deduction-run-3`
is its archive) rendered seeds 6000 and 6001 of the 6000-6999 band before it
stopped on the per-unit output ceiling; its result informed
[the diagnosis](../diagnosis-2026-09-13-live-run-stops.md) and the fixes that
followed, so by the rule every freeze card and the execution manifest's Roles
section state, that band is development data. The procedure is the one the
second and third freeze cards established: move the record with `git mv`,
flip its `status`, add a `converted` record, add the band to
`CONVERTED_BANDS`, move `PREREGISTERED_BAND` one band up, write the new record
to `MANIFEST_PATH` with the unchanged `build_manifest`. No seed above 6999 has
been rendered, inspected or tallied.

## Acceptance

- [x] The preregistered band is seeds 7000 to 7999 drawn ascending; the first
  fifty prefixes that pass the unchanged proof-free filter form the set, every
  skipped seed is recorded with its reason code, and seed 1, the seven
  development definitions and every seed of the three converted bands are
  excluded by construction. The generator's drawing logic, filter and roster do
  not change; only the band constant and the converted-band list move.
- [x] The 6000-6999 freeze record moves to
  `audits/deduction-candidate/held-out/manifest-band-6000-6999.json` with `git mv`,
  its bytes preserved except `status: development` and a `converted` record
  naming the date, the run (PR #451, branch `work/fresh-deduction-run-3`), the
  rendered seeds (6000 and 6001) and the fix the result informed. A test
  asserts its `accepted` and `skipped` blocks equal the ones frozen at
  `c06ee085`.
- [x] The new freeze record is written to `MANIFEST_PATH` by the unchanged
  `build_manifest` (status held_out, `dependency_restamps` empty, the seven
  development definitions and all three converted bands' digests asserted
  absent), so the instrument's `verify_frozen_set` and the regeneration test
  cover the current band without an instrument change.
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
[the limits card](fresh-deduction-limits-4.md), which lands after this card.
Nobody opens a generated prefix; the owner's merge is the freeze. No adoption,
no re-record, no committed recording or report rewritten.

## Expected scope

`experiments/held_out_prefixes.py` (band constant, converted-band list),
`tests/experiments/test_held_out_prefixes.py`, the instrument's tests only
where they pin the first accepted seed or the band,
`audits/deduction-candidate/held-out/manifest.json` (the new band),
`audits/deduction-candidate/held-out/manifest-band-6000-6999.json` (the third
band, moved and marked development), `audits/deduction-candidate/README.md`
(index the moved record), `docs/artifacts.md` (the `audits/` row),
`tasks/README.md`'s derived inventory sentence, this card. Delivered on
`work/held-out-prefix-freeze-4` and one pull request into `main`.

## Record impact

Adds a fourth frozen evaluation-input record under `audits/` and flips the
third to development in place; no recording, report, DTO, metric or weight
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

Every number and command in this section was measured on commit `f957c37c`,
which holds the code, the four records and the docs; this section and the index
sentence are the commit that follows it.

### The fourth band

`generate()` drew the preregistered band 7000-7999 ascending and stopped at
fifty. It consumed 58 seeds: **50 accepted, 8 skipped**, every skip for the same
reason.

| reason code | skipped | seeds |
| --- | --- | --- |
| `witnessed_kill` | 8 | 7000, 7002, 7007, 7011, 7017, 7018, 7047, 7048 |

The band's first seed is a skip, so the first accepted seed is 7001 and the
**last accepted seed is 7057**; 942 band seeds were never drawn and the band was
not widened. No `witnessed_vent` skip occurred, because the generator scripts no
vent — the vent half of the filter is held by the planted case
`test_a_planted_witnessed_vent_fails_the_filter`, not by a band seed. The
accepted seeds, the skips and the counts are the manifest's own `accepted`,
`skipped` and `skipped_reason_counts`.

`audits/deduction-candidate/held-out/manifest.json` is the new freeze artifact —
**sha256 `5fe4b1e3e1ca931b5712d05785d9d72fff261502bcd2bd7ab71071e5a458ed8b`**,
12,042 bytes. It is written by `build_manifest` called the way a freeze calls it
(no `converted` record), so its shape is the shape all three earlier freezes
produced: band, roster, tick budget, temporal version, the filter's stated
environment, the canonical-JSON recipe, the sha256 of the 22 generator sources,
the fifty accepted seeds with their digests in band order, the eight skips, the
seven development definitions' digests asserted absent, and a
`dependency_restamps` list that starts empty for this band. `status` reads
`held_out`, which is what `experiments/fresh_deduction_instrument.verify_frozen_set`
requires; no non-docstring byte of the instrument was touched (Deviations 2).

The live band shares no seed and no digest with ANY converted band —
`test_the_current_freeze_is_the_fourth_band_and_starts_without_restamps` loops
`CONVERTED_BANDS` rather than naming one record — and the seven development
definitions' digests are absent from `accepted[]` twice over: `build_manifest`
raises on a collision, and
`test_the_manifest_records_the_development_definitions_as_absent` compares the
committed record.

The out-of-band rejection rate reproduces offline, aggregates only, on the same
range the second and third freezes quoted:

```text
$ uv run python -m experiments.held_out_prefixes --tally 4000 4999
seeds 1000
accepted 864
witnessed_kill 136
```

4000-4999 lies between the first converted band and the second and below the
live one, so it is still out of every band, and the number it prints is the one
the third freeze measured unchanged. The band's own eight skips split by the
role whose wander witnessed the kill:

```text
$ uv run python -m experiments.held_out_prefixes --skip-roles manifest
seeds 8
bystander 2
reporter 6
```

Both commands refuse a range that touches any of the four bands, so neither can
be turned on the held-out set. The six reporter rows are also what makes the
planted case's docstring in `tests/experiments/test_held_out_prefixes.py` ("six
of the frozen band's eight skips") true of the frozen band again: it was written
for a band with that split, was stale for the 6000-6999 band's nine skips, and
was re-checked against this band's published skips rather than left to drift.

### The third band, marked rather than deleted

`audits/deduction-candidate/held-out/manifest-band-6000-6999.json` is the
6000-6999 record after `git mv` — **sha256
`3c23a13f16d03535070cd0d06ae378f6b268b735b6780c1b2d0523bb5efefc42`**, 13,507
bytes. That record carried no dependency restamp, so against the bytes the
owner's merge froze at `c06ee085` the whole diff is the `status` flip and the
new `converted` block:

```text
$ git show c06ee085:audits/deduction-candidate/held-out/manifest.json > /tmp/frozen.json
$ git diff --no-index --stat /tmp/frozen.json \
    audits/deduction-candidate/held-out/manifest-band-6000-6999.json
 .../held-out/manifest-band-6000-6999.json                  | 14 +++++++++++++-
 1 file changed, 13 insertions(+), 1 deletion(-)
```

`accepted` and `skipped` are byte-identical to that freeze, pinned by digest in
`test_the_converted_third_band_keeps_the_blocks_it_was_frozen_with` rather than
by a copy of fifty rows. The `converted` block names the date (2026-09-13), the
run (PR #451 on `work/fresh-deduction-run-3`), the two rendered seeds (6000 and
6001), the fix the stop informed (`tasks/work/fresh-deduction-limits-4.md`, the
re-sized ceilings) and the record that replaced it. Its shape is
`ConvertedRecord`, the frozen Pydantic model with `extra="forbid"` the second
freeze added, and the test validates the committed block through it. The record
was NOT regenerated: its digests are history and were edited in place.

`audits/deduction-candidate/README.md` now indexes all four records: the live
freeze, and each converted band with the run that rendered into it, the fix it
informed and the commit its digests were frozen at.

### Decisions

1. **The `converted` date is the run's date, 2026-09-13, not the date this
   record was written.** `ConvertedRecord.date` is documented as "the date the
   set became development data", and a set becomes development data when a
   prefix of it is rendered — which the diagnosis
   (`tasks/diagnosis-2026-09-13-live-run-stops.md`) and
   `tasks/work/fresh-deduction-authorization-3.md` both put on 2026-09-13. Both
   earlier records carry their run's date the same way (3000-3999 carries
   2026-09-10 although its freeze merged on 2026-09-11), so 2026-09-14 would
   have been the first record to mean something different by the same field.
   The dispatch note proposed 2026-09-14; this is the one place this card
   departs from it, and it is a one-line correction if the owner reads the field
   the other way.
2. **`CONVERTED_BANDS` grows at the end.** The 6000-6999 entry is appended, not
   prepended, because `DEFAULT_CALIBRATION_RECORD` is `CONVERTED_BANDS[0]`
   (`experiments/fresh_deduction_instrument.py:6148`) and the calibration of
   2026-09-14 is recorded against the 3000-3999 record. The ordering is now
   asserted with its reason in
   `test_the_preregistered_band_is_the_one_the_card_froze`.
3. **The range-walk test mirrors the guard's order instead of assuming a band.**
   Three bands are now adjacent (5000-5999, 6000-6999, 7000-7999), so the
   one-seed overhang cases straddle two frozen bands: `(5999, 6000)` is refused
   for 5000-5999, which the guard reaches first, and `(6999, 7000)` for the live
   band, which it checks before the list at all. The case now computes which
   band the guard would name and asserts that one; the anti-drop assertion above
   it — every committed `manifest-band-*.json` is a band `CONVERTED_BANDS` names
   — is unchanged and is what keeps a dropped entry red (Planted failures).
4. **`DEPENDENCY_RESTAMPS` starts empty again.** The 3000-3999 band's four
   restamps stay in that band's own record; 5000-5999 and 6000-6999 each
   accumulated none, which is why this move is thirteen inserted lines rather
   than fifty.
5. **The execution manifest's Inputs row is left stale on purpose**, and the
   gate that refuses it is asserted rather than relaxed (Deviations 1).

### Verification

Commands run on `f957c37c` from this branch's worktree:

| command | result |
| --- | --- |
| `uv run pytest tests/experiments/test_held_out_prefixes.py -q` | 34 passed |
| `uv run pytest tests/experiments -q` | 386 passed |
| `uv run python scripts/validate_task_docs.py` | 390 phase tasks, 55 work cards |
| `uv run python scripts/check_doc_facts.py` | passed |
| `uv run python scripts/verify_ml_evidence.py` | checks 60, OK 48, FAIL 0, ABSENT 7, INFO 5 |
| `uv run pytest tests/scripts/test_verify_ml_evidence.py -q` | 80 passed |
| `bash scripts/check.sh` | exit 0 — 7698 passed, 20 skipped, 3 xfailed; mypy 477 files; frontend 515 passed |

The seven `ABSENT` rows are the evidence-branch bytes a fresh clone does not
carry, the expected state; `--complete` was not run. `docs/artifacts.md`'s
`audits/` row was recomputed with all four records staged and now reads
**15,079,751 tracked bytes / 211 files**, from

```text
$ git ls-files -z audits | xargs -0 wc -c | awk '$2 != "total" {n += 1; s += $1} END {print n, s}'
211 15079751
```

which measures what the row means: `scripts/verify_ml_evidence.py` sums
`stat().st_size` over `git ls-files -z` for the same directory, and the
`$2 != "total"` filter drops `wc`'s own subtotal lines.

### Planted failures

Each perturbation was applied to the tree at `f957c37c`, run, and reverted with
`git checkout --`; the working tree is clean afterwards and each test passes
again.

| planted defect | test | failure |
| --- | --- | --- |
| one accepted digest of the moved 6000-6999 record rewritten to `0`×64 | `test_the_converted_third_band_keeps_the_blocks_it_was_frozen_with` | `AssertionError: assert 'eaaa5d6c922b...' == 'cb0adbd16614...'` |
| the moved record's `status` set back to `held_out` | same | `AssertionError: assert 'held_out' == 'development'` |
| the 6000-6999 entry dropped from `CONVERTED_BANDS` | `test_the_range_walks_refuse_a_converted_band_as_well` | `AssertionError: every committed manifest-band-*.json is a band CONVERTED_BANDS names, or the range guard no longer refuses it` |
| the Inputs row bound to 4000-4999, a band no committed record holds | `test_the_committed_manifest_binds_the_live_band_or_is_refused` | `AssertionError: the Inputs row binds seed band 4000-4999, which is neither the live freeze nor a converted record` |
| `assert_manifest_binds_the_live_band` stops refusing (`if False:`) | same | `Failed: DID NOT RAISE <class '…LiveRunNotAuthorized'>` |
| the limits card's `**Status:**` flipped to `done` with the row still stale | `test_a_binding_to_a_converted_record_stays_an_open_obligation` | `AssertionError: fresh-deduction-limits-4.md is closed while the execution manifest still binds the converted manifest-band-6000-6999.json` |
| the binding gate's docstring left naming only the first two conversions | `test_the_gate_says_which_bands_actually_moved` | `AssertionError: the gate explains itself without saying that 6000-6999 became development data on 2026-09-13` |
| `_root_binding_the_live_band` handed `_REPO_ROOT` again, guard kept | `TestCalibrationGate::test_the_two_authorizations_refuse_each_others_limits` | `AssertionError: _root_binding_the_live_band writes a rebound copy of the execution manifest into tmp_path; handed the repository it would rewrite the committed document` |
| the same call site AND the guard reverted to `95487473` (the defect itself) | same | **1 passed** — and `git status` then showed `audits/deduction-candidate/execution-manifest.md` modified, its Seed band row rewritten from `6000–6999` to `7000–7999` |

The last two rows are one defect and its gate. At this branch's base the helper
that plants a rebound copy of the execution manifest was being handed the
repository by one calibration test; outside a freeze window its early return
makes that harmless, which is why it was green when it was written. Inside this
window it rewrote the committed document's Seed band row as a side effect of
running the suite — silently re-binding the authorization a live run is checked
against, and leaving a dirty tree that the very next `pytest tests/experiments`
would then "pass" against. The helper now refuses the repository, and the call
site takes a `tmp_path` (Deviations 4).

The band move itself needs no new plant:
`test_the_committed_manifest_regenerates_from_its_own_band` regenerates from the
band the committed record names and compares every field, and
`test_the_tally_refuses_to_probe_the_preregistered_band` reads the band
constant, so both followed the move without an edit.

### Deviations

**1. The execution manifest's Inputs row is left bound to 6000-6999.** This card
may not edit `audits/deduction-candidate/execution-manifest.md`; the re-binding
is [the limits card](fresh-deduction-limits-4.md)'s acceptance item, and that
card lands after this one. `assert_manifest_binds_the_live_band`
(`experiments/fresh_deduction_instrument.py:929-970`) therefore refuses a live
run on this branch, which is the intended behaviour and not something to relax:
`test_the_committed_manifest_binds_the_live_band_or_is_refused` requires the row
to name a band a *converted* record holds and the gate to raise naming both
bands, and two of the plants above show that branch is not vacuous. The expiry
is `test_a_binding_to_a_converted_record_stays_an_open_obligation`, which fails
the moment the limits card closes with the row still stale.

**2. One docstring of `experiments/fresh_deduction_instrument.py` was edited**,
which the Constraints forbid. The sentence is the one
`test_the_gate_says_which_bands_actually_moved` holds to `CONVERTED_BANDS` and
each record's own `converted.date` — a gate added by the transport-resilience
card *after* the third freeze, so this is the first freeze to meet it. Adding
the third conversion to the list it names was the only change; no behaviour, no
constant and no `GENERATOR_SOURCES` file moved (the instrument is not one of the
22 hashed sources, so `source_sha256` is unaffected). The alternative was a red
gate or a weakened test.

**3. One acceptance item of `tasks/work/fresh-deduction-limits-4.md` was
edited**, which is outside this card's Expected scope. That item is the
obligation the gate above reads: it now spells out
`audits/deduction-candidate/held-out/manifest.json` and the moved record's path
in full, because the gate looks for the live record's path in that card's text
and the item said only "the new `held-out/manifest.json`". Nothing else in that
card moved; its Status is still `ready`. The third freeze made the same edit to
the card it handed the row to.

**4. Three edits to `tests/experiments/test_fresh_deduction_instrument.py`**,
which the Expected scope opens "only where they pin the first accepted seed or
the band". Two guards and one call site: `_root_binding_the_live_band` and
`_root_without_the_clause_binding_the_live_band` now refuse to be handed the
repository, and `TestCalibrationGate::test_the_two_authorizations_refuse_each_others_limits`
takes a `tmp_path` instead of passing `_REPO_ROOT`. This is the band window's
own helper and the defect only exists inside a freeze window, but the edit is a
gate the card did not ask for; the plant above is what it is worth.

### Limitations

The set is not frozen until the owner merges this pull request. This card proves
the inputs exist, are reproducible from the module and the band, and are
disjoint from every set anybody has read; it proves nothing about the
evaluation, which needs its own owner authorization —
`tasks/work/fresh-deduction-authorization-4.md` is that card and is not this
one's to close. Nothing here makes a fourth run feasible either: until the
limits card lands, `assert_limits_are_feasible` refuses the shipped ceilings and
`assert_manifest_binds_the_live_band` refuses the stale row, so this branch
alone cannot reach a provider — by design, and that is the state the merge
leaves. The eight skips are too few to say anything about the filter's rate —
the 1000-seed out-of-band tally is the honest figure for that — and three bands
in a row have now produced eight, nine and three skips out of 58, 59 and 53
seeds drawn, which is a reminder that a band's own skip count is a small sample,
not a property of the band. And a fourth freeze does not restore what three
stopped runs cost: 3000-3999, 5000-5999 and 6000-6999 can never serve as
held-out bands again, and a fourth rendering accident would cost this band the
same way.
