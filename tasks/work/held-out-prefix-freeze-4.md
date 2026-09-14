# Freeze a fourth held-out band after the third run rendered the third

**Status:** ready

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

- [ ] The preregistered band is seeds 7000 to 7999 drawn ascending; the first
  fifty prefixes that pass the unchanged proof-free filter form the set, every
  skipped seed is recorded with its reason code, and seed 1, the seven
  development definitions and every seed of the three converted bands are
  excluded by construction. The generator's drawing logic, filter and roster do
  not change; only the band constant and the converted-band list move.
- [ ] The 6000-6999 freeze record moves to
  `audits/deduction-candidate/held-out/manifest-band-6000-6999.json` with `git mv`,
  its bytes preserved except `status: development` and a `converted` record
  naming the date, the run (PR #451, branch `work/fresh-deduction-run-3`), the
  rendered seeds (6000 and 6001) and the fix the result informed. A test
  asserts its `accepted` and `skipped` blocks equal the ones frozen at
  `c06ee085`.
- [ ] The new freeze record is written to `MANIFEST_PATH` by the unchanged
  `build_manifest` (status held_out, `dependency_restamps` empty, the seven
  development definitions and all three converted bands' digests asserted
  absent), so the instrument's `verify_frozen_set` and the regeneration test
  cover the current band without an instrument change.
- [ ] No prefix bytes are committed; the preparer inspects no generated prefix
  beyond the automated filter and hash computation, runs no arm, and makes no
  provider call. Debugging uses seeds outside every band.
- [ ] `docs/artifacts.md`'s `audits/` inventory row is recomputed with the
  records staged, and `scripts/verify_ml_evidence.py` passes offline.
- [ ] Results states the accepted and skipped counts, the reason histogram, the
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
