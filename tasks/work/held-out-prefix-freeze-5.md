# Freeze a fifth held-out band after the fourth run rendered thirteen seeds

**Status:** ready

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
`tests/experiments/test_fresh_deduction_instrument.py:4412` takes its
converted branch: it reads the path in the moved record's `converted.informed`,
requires that card to be open (no `**Status:** done`) and requires it to name
`audits/deduction-candidate/held-out/manifest.json`. A missing file there is a
red suite, not a soft warning. The fifth authorization's limits card is that
card, so it has to exist in the tree this freeze merges into.

## Acceptance

- [ ] The preregistered band is seeds 8000 to 8999 drawn ascending; the first
  fifty prefixes that pass the unchanged proof-free filter form the set, every
  skipped seed is recorded with its reason code, and seed 1, the seven
  development definitions and every seed of the four converted bands are
  excluded by construction. The generator's drawing logic, filter and roster do
  not change; only the band constant and the converted-band list move.
- [ ] The 7000-7999 freeze record moves to
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
- [ ] `converted.informed` names the fifth authorization's limits card,
  expected at `tasks/work/fresh-deduction-limits-5.md`, and that card is
  present and open in the tree this branch merges into, so
  `test_a_binding_to_a_converted_record_stays_an_open_obligation`
  (`tests/experiments/test_fresh_deduction_instrument.py:4412`) passes rather
  than erroring on a path that does not resolve. If the coordinator dispatches
  that card under a different slug, the record names the slug that exists; the
  diagnosis is named in `note`, not here, because the gate reads this field as
  a card path.
- [ ] The 7000-7999 entry is appended to `CONVERTED_BANDS`, not prepended: the
  3000-3999 entry stays first because `DEFAULT_CALIBRATION_RECORD` is
  `CONVERTED_BANDS[0].manifest_path`
  (`experiments/fresh_deduction_instrument.py:6239`), and the second
  calibration is sized against a record, not against a list position.
  `PREREGISTERED_BAND` moves to 8000-8999 and the range guard
  (`experiments/held_out_prefixes.py:1181-1225`) then refuses four converted
  bands and the live one.
- [ ] The new freeze record is written to `MANIFEST_PATH` by the unchanged
  `build_manifest` (status `held_out`, `dependency_restamps` empty, the seven
  development definitions and all four converted bands' digests asserted
  absent), so `verify_frozen_set`
  (`experiments/fresh_deduction_instrument.py:2686`, whose status check is at
  `:2711`) and the regeneration test cover the current band without an
  instrument behaviour change.
- [ ] `assert_manifest_binds_the_live_band`'s docstring
  (`experiments/fresh_deduction_instrument.py:990-1001`) names 7000-7999 and
  2026-09-15 alongside the three earlier conversions, which is what
  `test_the_gate_says_which_bands_actually_moved`
  (`tests/experiments/test_fresh_deduction_instrument.py:1454`) reads out of
  `CONVERTED_BANDS` and each record's own `converted.date`. No constant, no
  behaviour and no `GENERATOR_SOURCES` file moves with it.
- [ ] No prefix bytes are committed; the preparer inspects no generated prefix
  beyond the automated filter and hash computation, runs no arm, and makes no
  provider call. Debugging uses seeds outside every band.
- [ ] `audits/deduction-candidate/README.md` indexes all five records, and
  `docs/artifacts.md`'s `audits/` inventory row (`docs/artifacts.md:109`,
  today 15,096,108 tracked bytes / 211 files) is recomputed with the records
  staged; `scripts/verify_ml_evidence.py` passes offline.
- [ ] Every acceptance item above that adds a gate has a planted failure
  showing it detects the defect it claims to detect, applied to the tree,
  run, and reverted.
- [ ] Results states the accepted and skipped counts, the reason histogram, the
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
