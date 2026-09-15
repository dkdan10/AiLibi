# Freeze a fifth held-out band after the fourth run rendered thirteen seeds

**Status:** done

## Outcome

A fifth held-out set of fifty proof-free scripted prefixes is frozen and
hashed from a band preregistered in this card, by a preparer session that will
never run the evaluation, so a fifth run has inputs nobody has rendered. The
fourth band's freeze record is marked development in place, with the reason
written into it, the way the first three were. The owner's merge of the
preparer's pull request is the fifth freeze.

## Evidence

The fourth live run (PR #458, branch `work/fresh-deduction-run-4` at
`5f2383ea`, unmerged; that branch is its archive) rendered thirteen prefixes of
the 7000-7999 band before it stopped on a truncated ballot in its 26th unit of
100. Its result informed
[the diagnosis of 2026-09-15](../diagnosis-2026-09-15-truncation-stop.md),
whose section 6 decisions the owner approved as a set on that date; decision 8
is this card. The preregistration treats a rendered prefix as development data,
so by the rule every freeze card and the execution manifest's Roles section
state (`audits/deduction-candidate/execution-manifest.md:1343-1355`), the
fourth band is development data from 2026-09-15. The diagnosis records that a
re-run of the band is not a clean sample either, so the set is not recoverable
by re-drawing it.

| Band | Record | Rendered by the stopped run | Development since |
| --- | --- | --- | --- |
| 3000-3999 | `manifest-band-3000-3999.json` | 3000 | 2026-09-10 |
| 5000-5999 | `manifest-band-5000-5999.json` | 5000 | 2026-09-13 |
| 6000-6999 | `manifest-band-6000-6999.json` | 6000, 6001 | 2026-09-13 |
| 7000-7999 | `manifest-band-7000-7999.json`, moved here | 13 seeds | 2026-09-15 |
| 8000-8999 | the new `manifest.json` | none | held out |

The third column is each record's own `rendered_seeds`. A later development
draw does not enter it: the calibration of 2026-09-14 rendered seeds 3000 to
3004 of the first band, which was already development data.

The procedure is the one the second, third and fourth freeze cards
established, and it is unchanged here: move the record with `git mv`, flip its
`status`, add a `converted` record, add the band to `CONVERTED_BANDS`, move
`PREREGISTERED_BAND` one band up, and write the new record to `MANIFEST_PATH`
with the unchanged `build_manifest`. The constants are
`experiments/held_out_prefixes.py:146` (`MANIFEST_PATH`), `:350`
(`PREREGISTERED_BAND`), `:375-394` (`CONVERTED_BANDS`), `:1407`
(`DEPENDENCY_RESTAMPS`, empty at a freeze), `:1410` (`ConvertedRecord`) and
`:1443` (`build_manifest`, whose `status` key at `:1476` reads `held_out` only
when no `converted` record is passed). No seed above 7999 has been rendered,
inspected or tallied.

One coupling is new and is load-bearing. Because the execution manifest's
Inputs row still binds 7000-7999 after this card,
`tests/experiments/test_fresh_deduction_instrument.py:4722` takes its
converted branch: it reads the path in the moved record's `converted.informed`,
requires that card to be open (no `**Status:** done`) and requires it to name
`audits/deduction-candidate/held-out/manifest.json`. A missing file there is a
red suite, not a soft warning. The fifth authorization's limits card is that
card, so it has to exist in the tree this freeze merges into.

## Acceptance

- [x] The preregistered band is seeds 8000 to 8999 drawn ascending; the first
  fifty prefixes that pass the unchanged proof-free filter form the set, every
  skipped seed is recorded with its reason code, and seed 1, the seven
  development definitions and every seed of the four converted bands are
  excluded by construction. The generator's drawing logic, filter and roster do
  not change; only the band constant and the converted-band list move.
- [x] The 7000-7999 freeze record moves to
  `audits/deduction-candidate/held-out/manifest-band-7000-7999.json` with
  `git mv`, its bytes preserved except `status: development` and a `converted`
  record whose `date` is 2026-09-15, `pull_request` is `#458`, `branch` is
  `work/fresh-deduction-run-4`, `rendered_seeds` are 7001, 7003, 7004, 7005,
  7006, 7008, 7009, 7010, 7012, 7013, 7014, 7015 and 7016, `superseded_by` is
  `MANIFEST_PATH`, and whose `note` names the truncation stop and the diagnosis
  path `tasks/diagnosis-2026-09-15-truncation-stop.md`. A test asserts its
  `accepted` and `skipped` blocks equal the ones frozen at `1323cd75`: fifty
  accepted seeds running 7001 to 7057, eight `witnessed_kill` skips, and an
  empty `dependency_restamps.entries`.
- [x] `converted.informed` names the fifth authorization's limits card,
  expected at `tasks/work/fresh-deduction-limits-5.md`, and that card is
  present and open in the tree this branch merges into, so
  `test_a_binding_to_a_converted_record_stays_an_open_obligation`
  (`tests/experiments/test_fresh_deduction_instrument.py:4722`) passes rather
  than erroring on a path that does not resolve. If the coordinator dispatches
  that card under a different slug, the record names the slug that exists; the
  diagnosis is named in `note`, not here, because the gate reads this field as
  a card path.
- [x] The 7000-7999 entry is appended to `CONVERTED_BANDS`, not prepended: the
  3000-3999 entry stays first because `DEFAULT_CALIBRATION_RECORD` is
  `CONVERTED_BANDS[0].manifest_path`
  (`experiments/fresh_deduction_instrument.py:6239`), and the second
  calibration is sized against a record, not against a list position.
  `PREREGISTERED_BAND` moves to 8000-8999 and the range guard
  (`experiments/held_out_prefixes.py:1181-1225`) then refuses four converted
  bands and the live one.
- [x] The new freeze record is written to `MANIFEST_PATH` by the unchanged
  `build_manifest` (status `held_out`, `dependency_restamps` empty, the seven
  development definitions and all four converted bands' digests asserted
  absent), so `verify_frozen_set`
  (`experiments/fresh_deduction_instrument.py:2686`, whose status check is at
  `:2711`) and the regeneration test cover the current band without an
  instrument behaviour change.
- [x] `assert_manifest_binds_the_live_band`'s docstring
  (`experiments/fresh_deduction_instrument.py:990-1001`) names 7000-7999 and
  2026-09-15 alongside the three earlier conversions, which is what
  `test_the_gate_says_which_bands_actually_moved`
  (`tests/experiments/test_fresh_deduction_instrument.py:1476`) reads out of
  `CONVERTED_BANDS` and each record's own `converted.date`. No constant, no
  behaviour and no `GENERATOR_SOURCES` file moves with it.
- [x] No prefix bytes are committed; the preparer inspects no generated prefix
  beyond the automated filter and hash computation, runs no arm, and makes no
  provider call. Debugging uses seeds outside every band.
- [x] `audits/deduction-candidate/README.md` indexes all five records, and
  `docs/artifacts.md`'s `audits/` inventory row (`docs/artifacts.md:109`,
  today 15,096,108 tracked bytes / 211 files) is recomputed with the records
  staged; `scripts/verify_ml_evidence.py` passes offline.
- [x] Every acceptance item above that adds a gate has a planted failure
  showing it detects the defect it claims to detect, applied to the tree,
  run, and reverted.
- [x] Results states the accepted and skipped counts, the reason histogram, the
  last accepted seed, the new record's sha256 and byte size, and the
  reproducible commands (`uv run python -m experiments.held_out_prefixes
  --tally FIRST LAST` on an out-of-band range and `--skip-roles manifest`).

## Constraints

No live provider call of any kind; fake and scripted providers only, and the
credentials file is never opened. The band is preregistered here and may not be
changed; a band that cannot fill fifty is a stop, not a wider band. The owner's
merge of the diagnosis's section-6 decisions on 2026-09-15 is what authorizes
the numbers this card fixes: the band 8000-8999, the conversion date
2026-09-15, and the thirteen rendered seeds the fourth run's archive records.

The preparer edits `experiments/held_out_prefixes.py` only for the band
constant and the converted-band list, and
`experiments/fresh_deduction_instrument.py` only for the one gate docstring the
conversion list is read against. It does not edit
`audits/deduction-candidate/execution-manifest.md`,
`experiments/deduction_scenarios.py` or `experiments/deduction_evaluation.py`.
The execution manifest's Inputs table (`:785-790`) is re-bound to 8000-8999,
and its Roles table's preparer row (`:1347`) extended with this session and its
pull request, by the fifth authorization's limits card, which lands after this
card and after the second calibration reports; until then
`assert_manifest_binds_the_live_band` refuses a live run on this tree, which is
the intended state and is not something to relax.

Nobody opens a generated prefix; the owner's merge is the freeze. No adoption,
no re-record, no committed recording or report rewritten. Prompt-byte changes
to the candidate accounts family are not this card's and stay behind the
default-OFF experiment levers on [their own card](accounts-prompt-set-v4.md),
with no recording and no re-record. The live run's primary outcome, decision
rule, minimum actionable effect, tradeoff bound and `STOP_RULE` do not change
here. The per-arm public-transcript role-leak count the owner reads decision 9
against is pre-declared on
[the second calibration](fresh-deduction-calibration-2.md) and reported by the
next run, not by this card. Any `audits/` byte change recomputes the
`docs/artifacts.md` audits row.

## Expected scope

`experiments/held_out_prefixes.py` (band constant, converted-band list),
`tests/experiments/test_held_out_prefixes.py`,
`experiments/fresh_deduction_instrument.py` (the one gate docstring),
`tests/experiments/test_fresh_deduction_instrument.py` only where it pins the
first accepted seed, the band or the conversion list,
`audits/deduction-candidate/held-out/manifest.json` (the new band),
`audits/deduction-candidate/held-out/manifest-band-7000-7999.json` (the fourth
band, moved and marked development), `audits/deduction-candidate/README.md`
(index the moved record), `docs/artifacts.md` (the `audits/` row),
`tasks/README.md`'s derived inventory sentence, this card.

Delivered on `work/held-out-prefix-freeze-5` with one pull request into `main`.
It shares no file with the other three cards opened with it, so it bases on
`main` rather than stacking; a card that does stack bases on its predecessor's
branch and is retargeted after that branch merges. It is dispatched with the
fifth authorization's limits card, after
[the second calibration](fresh-deduction-calibration-2.md) reports, because
that limits card is what `converted.informed` names and what re-binds the
manifest's Inputs row. The pull request lands as a merge commit or a
fast-forward, never a squash, and every commit carries the trailer
`Card: tasks/work/held-out-prefix-freeze-5.md`. Every acceptance item that
adds a gate carries a planted failure, and any `audits/` byte change
recomputes the `docs/artifacts.md` audits row.

## Record impact

Adds a fifth frozen evaluation-input record under `audits/` and flips the
fourth to development in place; no recording, report, DTO, metric or weight
byte moves, no experiment becomes ON, no adopting record is created. The
conversion does make the 7000-7999 record eligible as a calibration input
(`verify_calibration_set`, `experiments/fresh_deduction_instrument.py:2865`,
accepts a record whose status is `development` and whose band is in
`CONVERTED_BANDS`). Nothing draws from it yet:
[the second calibration](fresh-deduction-calibration-2.md) reports before this
card lands and pins its own draw to the 3000-3999 and 5000-5999 records.

## Validation

`uv run pytest tests/experiments -q`, then `uv run python
scripts/validate_task_docs.py`, `uv run python scripts/check_doc_facts.py`,
`uv run python scripts/verify_ml_evidence.py` (offline; never `--complete`),
`uv run pytest tests/scripts/test_verify_ml_evidence.py -q`, and
`bash scripts/check.sh` run whole, in a clean worktree, so no gate after the
first failure is masked. Do not run the live evaluation as a check.

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
no prefix from them was printed or opened either. The repository's `.env` was
not read and no held-out band's prefix bytes were printed, logged or committed.

Every number and command in this section was measured on commit `88d42f82`,
which holds the code, the five records and the docs; this section and the index
sentence are the commit that follows it.

### The fifth band

`generate()` drew the preregistered band 8000-8999 ascending and stopped at
fifty. It consumed 58 seeds: **50 accepted, 8 skipped**, every skip for the same
reason.

| reason code | skipped | seeds |
| --- | --- | --- |
| `witnessed_kill` | 8 | 8015, 8016, 8018, 8023, 8028, 8029, 8039, 8046 |

The band's first seed passes, so the first accepted seed is 8000 and the **last
accepted seed is 8057**; 942 band seeds were never drawn and the band was not
widened. No `witnessed_vent` skip occurred, because the generator scripts no
vent — the vent half of the filter is held by the planted case
`test_a_planted_witnessed_vent_fails_the_filter`, not by a band seed. The
accepted seeds, the skips and the counts are the manifest's own `accepted`,
`skipped` and `skipped_reason_counts`.

`audits/deduction-candidate/held-out/manifest.json` is the new freeze artifact —
**sha256 `46f2ba616dc4088f4ac3006191c559de9b98d75a0f1044e14220371881fb4c1e`**,
12,042 bytes. It is written by `build_manifest` called the way a freeze calls it
(no `converted` record), so its shape is the shape all four earlier freezes
produced: band, roster, tick budget, temporal version, the filter's stated
environment, the canonical-JSON recipe, the sha256 of the 22 generator sources,
the fifty accepted seeds with their digests in band order, the eight skips, the
seven development definitions' digests asserted absent, and a
`dependency_restamps` list that starts empty for this band. `status` reads
`held_out`, which is what
`experiments/fresh_deduction_instrument.verify_frozen_set` requires; no
non-docstring byte of the instrument was touched (Deviations 2).

The live band shares no seed and no digest with ANY converted band —
`test_the_current_freeze_is_the_fifth_band_and_starts_without_restamps` loops
`CONVERTED_BANDS` rather than naming one record, and all four records are
covered by that loop — and the seven development definitions' digests are absent
from `accepted[]` twice over: `build_manifest` raises on a collision, and
`test_the_manifest_records_the_development_definitions_as_absent` compares the
committed record.

The out-of-band rejection rate reproduces offline, aggregates only, on the same
range the second, third and fourth freezes quoted:

```text
$ uv run python -m experiments.held_out_prefixes --tally 4000 4999
seeds 1000
accepted 864
witnessed_kill 136
```

4000-4999 lies between the first converted band and the second and below every
later one, so it is still out of every band, and the number it prints is the one
the previous two freezes measured unchanged. The band's own eight skips split by
the role whose wander witnessed the kill:

```text
$ uv run python -m experiments.held_out_prefixes --skip-roles manifest
seeds 8
bystander 4
reporter 4
```

Both commands refuse a range that touches any of the five bands, so neither can
be turned on the held-out set. This band's split is even, where the 7000-7999
band's was six reporter rows to two; the docstring of
`_reporter_witnessed_seed_one_prefix` in
`tests/experiments/test_held_out_prefixes.py` quoted that six, so it was re-read
off this band's published skips and now says four, with the reason it is re-read
at every freeze rather than carried forward. A band's own skip split is a small
sample and not a property of the filter.

### The fourth band, marked rather than deleted

`audits/deduction-candidate/held-out/manifest-band-7000-7999.json` is the
7000-7999 record after `git mv` — **sha256
`550eaa23f79132acc58ae46b4335bbe6d2cd7e7f27ec81080d6f6939aa897560`**, 13,823
bytes. That record carried no dependency restamp, so against the bytes the
owner's merge froze at `1323cd75` the whole diff is the `status` flip and the
new `converted` block:

```text
$ git show 1323cd75:audits/deduction-candidate/held-out/manifest.json > /tmp/frozen.json
$ git diff --no-index --stat /tmp/frozen.json \
    audits/deduction-candidate/held-out/manifest-band-7000-7999.json
 .../held-out/manifest-band-7000-7999.json          | 25 +++++++++++++++++++++-
 1 file changed, 24 insertions(+), 1 deletion(-)
```

`accepted` and `skipped` are byte-identical to that freeze, pinned by digest in
`test_the_converted_fourth_band_keeps_the_blocks_it_was_frozen_with` rather than
by a copy of fifty rows. The `converted` block names the date (2026-09-15), the
run (PR #458 on `work/fresh-deduction-run-4`, whose archive is that branch at
`5f2383ea`), the thirteen rendered seeds (7001, 7003, 7004, 7005, 7006, 7008,
7009, 7010, 7012, 7013, 7014, 7015, 7016), the card the result informed
(`tasks/work/fresh-deduction-limits-5.md`, the re-sized ceilings and the
refreshed usage profile) and the record that replaced it. Its `note` states what
stopped the run — a candidate-arm ballot on seed 7016 overran the 1,024-token
per-call vote cap and returned truncated JSON, which `STOP_RULE` gives no retry
— and names `tasks/diagnosis-2026-09-15-truncation-stop.md`. `informed` holds a
card path and nothing else, because
`test_a_binding_to_a_converted_record_stays_an_open_obligation` reads that field
as a path and resolves it. Its shape is `ConvertedRecord`, the frozen Pydantic
model with `extra="forbid"`, and the test validates the committed block through
it. The record was NOT regenerated: its digests are history and were edited in
place.

The thirteen rendered seeds are also cross-checked against the record's own
`accepted` block — they are its first thirteen rows, in order — so a conversion
describing a run that rendered seeds this set never held is red even if the
literal list and the record agree with each other (Planted failures, row 3).

`audits/deduction-candidate/README.md` now indexes all five records: the live
freeze, and each converted band with the run that rendered into it, the fix it
informed and the commit its digests were frozen at.

### Decisions

1. **The `converted` date is the run's date, 2026-09-15.** `ConvertedRecord.date`
   is documented as "the date the set became development data", and a set becomes
   development data when a prefix of it is rendered. The run, the diagnosis and
   the owner's approval of its section-6 decisions are all 2026-09-15, so the
   card's preregistered date and the rule agree here; the three earlier records
   carry their run's date the same way.
2. **`CONVERTED_BANDS` grows at the end.** The 7000-7999 entry is appended, not
   prepended, because `DEFAULT_CALIBRATION_RECORD` is `CONVERTED_BANDS[0]`
   (`experiments/fresh_deduction_instrument.py:7421`) and both calibrations are
   recorded against the 3000-3999 record. `test_the_preregistered_band_is_the_one_the_card_froze`
   asserts the whole list in order, with that reason in its docstring.
3. **The calibration draw's acceptance set widened by one, and is derived rather
   than retyped.** `verify_calibration_draw` accepts a PREFIX of
   `CONVERTED_BANDS` long enough to fill sixty seeds, so a fourth converted
   record makes `[3000, 5000, 6000, 7000]` acceptable alongside the two prefixes
   that were acceptable before. Every accepted prefix still draws the same sixty
   seeds — the first record alone holds fifty — which
   `test_only_a_prefix_of_the_converted_records_is_accepted` asserts candidate by
   candidate against the default draw, and its expected list is now derived from
   `len(paths)` instead of naming two prefixes (Deviations 3). Nothing about the
   second calibration's committed draw moves.
4. **`DEPENDENCY_RESTAMPS` starts empty again.** The 3000-3999 band's four
   restamps stay in that band's own record; 5000-5999, 6000-6999 and 7000-7999
   each accumulated none, which is why this move is 24 inserted lines rather than
   fifty.
5. **The execution manifest's Inputs row is left stale on purpose**, and the gate
   that refuses it is asserted rather than relaxed (Deviations 1).

### Verification

Commands run on `88d42f82` from this branch's worktree:

| command | result |
| --- | --- |
| `uv run pytest tests/experiments/test_held_out_prefixes.py -q` | 35 passed |
| `uv run pytest tests/experiments -q` | 487 passed |
| `uv run python scripts/validate_task_docs.py` | 390 phase tasks, 61 work cards |
| `uv run python scripts/check_doc_facts.py` | passed |
| `uv run python scripts/verify_ml_evidence.py` | checks 60, OK 48, FAIL 0, ABSENT 7, INFO 5 |
| `uv run pytest tests/scripts/test_verify_ml_evidence.py -q` | 80 passed |
| `bash scripts/check.sh` | exit 0 — 7820 passed, 20 skipped, 3 xfailed; mypy 478 files; frontend 515 passed |

The seven `ABSENT` rows are the evidence-branch bytes a fresh clone does not
carry, the expected state; `--complete` was not run. `docs/artifacts.md`'s
`audits/` row was recomputed with all five records staged and now reads
**15,606,662 tracked bytes / 216 files**, from

```text
$ git ls-files -z audits | xargs -0 wc -c | awk '$2 != "total" {n += 1; s += $1} END {print n, s}'
216 15606662
```

which measures what the row means: `scripts/verify_ml_evidence.py` sums
`stat().st_size` over `git ls-files -z` for the same directory, and the
`$2 != "total"` filter drops `wc`'s own subtotal lines.

### Planted failures

Each perturbation was applied to the tree at `88d42f82`, run, and reverted with
`git checkout --`; the working tree is clean afterwards and each test passes
again.

| planted defect | test | failure |
| --- | --- | --- |
| one accepted digest of the moved 7000-7999 record rewritten to `0`×64 | `test_the_converted_fourth_band_keeps_the_blocks_it_was_frozen_with` | `AssertionError: assert 'cfde4386a025...' == 'ad476d635f8c...'` |
| the moved record's `status` set back to `held_out` | same | `AssertionError: assert 'held_out' == 'development'` |
| `rendered_seeds` retyped to thirteen CONTIGUOUS seeds 7001-7013 **and** the literal tuple in the test retyped to match | same | `assert [7001, 7002, ...] == [7001, 7003, ...]` — `At index 1 diff: 7002 != 7003`, from the cross-check against the record's own first thirteen accepted rows |
| the 7000-7999 entry dropped from `CONVERTED_BANDS` | `test_the_range_walks_refuse_a_converted_band_as_well` | `AssertionError: every committed manifest-band-*.json is a band CONVERTED_BANDS names, or the range guard no longer refuses it` |
| the binding gate's docstring left naming only the first three conversions | `test_the_gate_says_which_bands_actually_moved` | `AssertionError: the gate explains itself without saying that 7000-7999 became development data on 2026-09-15` |
| the limits-5 card's `**Status:**` flipped to `done` with the row still stale | `test_a_binding_to_a_converted_record_stays_an_open_obligation` | `AssertionError: fresh-deduction-limits-5.md is closed while the execution manifest still binds the converted manifest-band-7000-7999.json` |
| `assert_manifest_binds_the_live_band` stops refusing (`if False:`) | `test_the_committed_manifest_binds_the_live_band_or_is_refused`, and **both** window-branch cases | 3 failed — `Failed: DID NOT RAISE <class '…LiveRunNotAuthorized'>` |
| the Inputs row bound to 4000-4999, a band no committed record holds | the two window-branch cases | `AssertionError: the execution manifest binds seed band 4000-4999, which is neither the live freeze nor a converted record: that is a stale document, not a re-binding window` |
| the Inputs row's clause for 6000-6999 deleted (a band it replaced, not the one it binds) | `test_the_inputs_row_names_every_converted_band` | `AssertionError: the Seed band row does not name 6000-6999` |

The last three rows are what keep this card's two test relaxations honest. The
window branch added to the rehearsal and mechanics-check cases (Deviations 1) is
not a free pass: it is reached only through a helper that first proves the bound
band is a committed converted record and that the live run is actually refused,
so turning the gate off or binding the row to an invented band turns both cases
red rather than green. And skipping the BOUND band in the Inputs-row case leaves
every band the row replaced enforced, which the last row shows.

The band move itself needs no new plant:
`test_the_committed_manifest_regenerates_from_its_own_band` regenerates from the
band the committed record names and compares every field, and
`test_the_tally_refuses_to_probe_the_preregistered_band` reads the band constant,
so both followed the move without an edit.

### Deviations

**1. The execution manifest's Inputs row is left bound to 7000-7999**, and two
cases that quote figures OF THE BOUND BAND gained a window branch rather than a
re-measurement. This card may not edit
`audits/deduction-candidate/execution-manifest.md`; the re-binding and the
re-measured mechanics-check paragraph are
[the limits card](fresh-deduction-limits-5.md)'s acceptance items, and that card
lands after this one. `assert_manifest_binds_the_live_band` therefore refuses a
live run on this branch, which is the intended behaviour and not something to
relax. `TestUsageReplay.test_the_rehearsal_is_green_under_the_fourth_authorizations_limits`
and `TestDryRun.test_the_mechanics_check_paragraph_quotes_the_run_it_describes`
run everything band-independent and then stop at the manifest quotations,
through a new helper `_the_document_is_mid_rebinding` that asserts the refusal
and the bound band's membership in `CONVERTED_BANDS` before returning it. Only
`arm.terminal_units` and the fake provider's per-arm figures actually moved with
the band; the replay double's token totals did not, which is the
band-independence claim the rehearsal's own docstring makes. The expiry is
`test_a_binding_to_a_converted_record_stays_an_open_obligation`, which fails the
moment the limits card closes with the row still stale — planted above.

**2. Two docstrings of `experiments/fresh_deduction_instrument.py` were edited**,
where the Constraints allow one. The first is the sentence
`test_the_gate_says_which_bands_actually_moved` holds to `CONVERTED_BANDS` and
each record's own `converted.date`; adding the fourth conversion to it was the
only change the gate required. The second is one word of tense in
`_draw_in_converted_order`'s docstring, which said `CONVERTED_BANDS` "holds
three development records" while recounting the round-2 review of 2026-09-15; it
now says "held three at that review", because a present-tense count that this
card makes false is worse than a declared extra line of diff. No behaviour, no
constant and no `GENERATOR_SOURCES` file moved (the instrument is not one of the
22 hashed sources, so `source_sha256` is unaffected).

**3. Six cases of `tests/experiments/test_fresh_deduction_instrument.py` were
edited**, where the Expected scope opens that file "only where it pins the first
accepted seed, the band or the conversion list". All six are the conversion list
or the band, and all six met their first freeze window here:

- three `TestTheCalibrationDrawSpansRecords` cases unpacked exactly three
  converted records (`first, second, third = ...`, and an expected list naming
  two prefixes by hand), which is a `ValueError` at four. They now slice the
  first three for the two band-skipping shapes, which need three records and
  nothing more, and derive the accepted-prefix list from `len(paths)`;
- `test_the_inputs_row_names_every_converted_band` required the row to name
  every converted band as one it REPLACED, which the band the row still binds is
  not. It now skips exactly the bound band, with the obligation case as the
  expiry;
- `test_the_fourth_authorization_section_records_the_change_and_its_basis` read
  that dated entry's "now binds 7000-7999" against `PREREGISTERED_BAND`. A dated
  amendment records the re-binding IT made and is not rewritten when the band
  moves again, so it is now read against the module's own record of that band
  (the `CONVERTED_BANDS` entry whose record is `manifest-band-7000-7999.json`),
  which still catches an entry naming a band this generator never froze;
- the two window-branch cases of Deviations 1.

**4. One acceptance item of `tasks/work/fresh-deduction-limits-5.md` was
edited**, which is outside this card's Expected scope. That item is the
obligation the gate above reads: it now spells out
`audits/deduction-candidate/held-out/manifest.json` and the moved record's path
in full, because the gate looks for the live record's path in that card's text
and the item said only "the new `held-out/manifest.json`". Nothing else in that
card moved; its Status is still `ready`. The third and fourth freezes made the
same edit to the cards they handed the row to.

### Limitations

The set is not frozen until the owner merges this pull request. This card proves
the inputs exist, are reproducible from the module and the band, and are
disjoint from every set anybody has read; it proves nothing about the
evaluation, which needs its own owner authorization —
`tasks/work/fresh-deduction-authorization-5.md` is that card and is not this
one's to close. Nothing here makes a fifth run feasible either: until the limits
card lands, `assert_limits_are_feasible` refuses the shipped ceilings on the
profile the fifth authorization is written against and
`assert_manifest_binds_the_live_band` refuses the stale row, so this branch alone
cannot reach a provider — by design, and that is the state the merge leaves. The
eight skips are too few to say anything about the filter's rate — the 1000-seed
out-of-band tally is the honest figure for that — and four bands in a row have
now produced three, nine, eight and eight skips out of 53, 59, 58 and 58 seeds
drawn, which is a reminder that a band's own skip count is a small sample. And a
fifth freeze does not restore what four stopped runs cost: 3000-3999, 5000-5999,
6000-6999 and 7000-7999 can never serve as held-out bands again, seventeen
prefixes of them are public, and a fifth rendering accident would cost this band
the same way.
