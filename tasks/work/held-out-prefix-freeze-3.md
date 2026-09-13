# Freeze a third held-out band after the second run revealed the second

**Status:** ready

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

- [ ] The preregistered band is seeds 6000 to 6999 drawn ascending; the first
  fifty prefixes that pass the unchanged proof-free filter form the set, every
  skipped seed is recorded with its reason code, and seed 1, the seven
  development definitions and every seed of the 3000-3999 and 5000-5999 bands
  are excluded by construction. The generator's drawing logic, filter and
  roster do not change; only the band constant and the converted-band list move.
- [ ] The 5000-5999 freeze record moves to
  `audits/deduction-candidate/held-out/manifest-band-5000-5999.json` with `git mv`,
  its bytes preserved except `status: development` and a `converted` record
  naming the date, the run (PR #448, branch `work/fresh-deduction-run-2`), the
  rendered seed (5000) and the fix the result informed. A test asserts its
  `accepted` and `skipped` blocks equal the ones frozen at `ca6e97d6`.
- [ ] The new freeze record is written to `MANIFEST_PATH` by the unchanged
  `build_manifest` (status held_out, `dependency_restamps` empty, the seven
  development definitions and both converted bands' digests asserted absent),
  so the instrument's `verify_frozen_set` and the regeneration test cover the
  current band without an instrument change.
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
