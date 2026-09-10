# Freeze a second held-out band after the stopped run revealed the first

**Status:** ready

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

- [ ] The preregistered band is seeds 5000 to 5999 drawn ascending; the first
  fifty prefixes that pass the unchanged proof-free filter form the set, every
  skipped seed is recorded with its reason code, and seed 1, the seven
  development definitions and every seed of the 3000-3999 band are excluded by
  construction. The generator's drawing logic, filter and roster do not change;
  only the band constant moves.
- [ ] The 3000-3999 freeze record is preserved byte-for-byte except for its
  status: it moves to `audits/deduction-candidate/held-out/manifest-band-3000-3999.json`
  with `status` set to `development` and a `converted` record naming the date,
  the run (PR #445, branch `work/fresh-deduction-run`), which seed was rendered
  (3000) and which fix the result informed. A test asserts its `accepted` and
  `skipped` blocks equal the ones frozen at `23a23c2d`.
- [ ] The new freeze record is written to `MANIFEST_PATH`
  (`audits/deduction-candidate/held-out/manifest.json`) by the unchanged
  `build_manifest`, so the instrument's `verify_frozen_set` and the regeneration
  test cover the current band without an instrument change. It records the
  band, the roster, the source digests, the fifty accepted digests, the skips,
  the development definitions' digests asserted absent, and a `dependency_restamps`
  list that starts empty for this band.
- [ ] No prefix bytes are committed; the preparer inspects no generated prefix
  beyond the automated filter and hash computation, runs no arm, and makes no
  provider call. Debugging uses seeds outside both bands.
- [ ] `docs/artifacts.md`'s `audits/` inventory row is recomputed with both
  manifests staged, and `scripts/verify_ml_evidence.py` passes offline.
- [ ] Results states the accepted and skipped counts, the reason histogram, the
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
