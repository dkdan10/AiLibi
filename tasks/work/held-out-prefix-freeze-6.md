# Freeze a sixth held-out band after the fifth run rendered all of the fifth

**Status:** ready

## Outcome

A sixth held-out set of fifty proof-free scripted prefixes is frozen and hashed
from a band preregistered in this card, by a preparer session that will never
run the evaluation, so a sixth run has inputs nobody has rendered. The fifth
band's record is marked development in place, the way the first four were, and
the open-ended debugging range is closed, because one unspent thousand of seeds
is left. The owner's merge is the freeze.

## Evidence

The fifth live run (PR #465, branch `work/fresh-deduction-run-5`, merged at
`42c7181f`; archive `audits/deduction-candidate/run-2026-09-16/`) is the first
attempt that finished, 100 of 100 units in one sitting, so it rendered **all
fifty** accepted prefixes of the 8000-8999 band, and its verdict is
INCONCLUSIVE. It informed
[the diagnosis of 2026-09-18](../diagnosis-2026-09-18-fifth-run.md), whose ten
decisions the owner approved as a set that date with the rulings in its section
11; decision 8 is this card, and a rendered prefix is development data by the
preregistration (`audits/deduction-candidate/execution-manifest.md:1802-1806`).
Every earlier conversion left unrendered seeds behind; this one leaves nothing
to re-draw.

| Band | Rendered by its run | Development since |
| --- | --- | --- |
| 3000-3999 | 3000 | 2026-09-10 |
| 5000-5999 | 5000 | 2026-09-13 |
| 6000-6999 | 6000, 6001 | 2026-09-13 |
| 7000-7999 | 13 seeds | 2026-09-15 |
| 8000-8999 | all 50 | 2026-09-16 |

The procedure is the second through fifth freeze cards', unchanged, over
`experiments/held_out_prefixes.py:146` (`MANIFEST_PATH`), `:345-350`
(`PREREGISTERED_BAND`), `:375-400` (`CONVERTED_BANDS`), `:1413`
(`DEPENDENCY_RESTAMPS`, empty at a freeze), `:1416` (`ConvertedRecord`) and
`:1449` (`build_manifest`, whose `status` at `:1482` reads `held_out` only with
no `converted` record). `SeedBand` (`:244-258`) constrains direction and size
only, so a band below the converted ones is as legal as one above.

**The band, chosen by search.** Five thousands are spent. 4000-4999 is the
out-of-band tally range every freeze card quotes, and the co-evolution rankings
under `training/artifacts/coevo/realpath/` record games on seeds 4000-4005
besides. The debugging guidance is open-ended, "9001 onward"
(`tasks/work/held-out-prefix-freeze-2.md:129`), so 9000 and above are
contaminated. That leaves two bands, and a census of every tracked file for a
four-digit number within 24 characters of `seed`, ISO dates excluded, says
neither is clean and by how much:

| Range | Distinct seed-adjacent values | Occurrences | Verdict |
| --- | --- | --- | --- |
| 1000-1999 | 191 | 93,662 | spent |
| 2000-2999 | 27, none above 2026 | 401 | spent to 2026 |
| 2100-2999 | 4, none of them a seed | 4 | clean |

1000-1999 is the ML corpus: `git ls-files 'replays/ml_corpus/*' | grep -cE
'replay-seed-1[0-9]{3}\.jsonl$'` prints **200** committed replays, and
`experiments/tactical_gameplay.py:735` declares that experiment's splits as
`range(1000, 1008)` and `range(2000, 2016)`. The second is recorded in
`audits/tactical-gameplay/held-out.json`, where `git grep -cE '"seed":
2[0-9]{3},'` prints **288** rows over 16 seeds; `audit-phase-18-meeting-gate.md`
records a probe on seeds 2000-2024 on **3** lines; committed tests seed 2024
twice and 2026 once (`tests/engine/test_rng_fast_path.py:110`,
`tests/llm/test_ollama_client.py:703`,
`tests/agents/test_impostor_answer_arm.py:754`). The four matches above 2099 are
`wall_seconds` values, a duration and a dollar amount, and a pass over every
committed `"seeds": [...]` list and `--seeds` argument agrees, its largest value
being 2015.

So **2100-2999** is preregistered, ascending, size 50. Not 2027-2999: 2100
leaves a 73-seed quarantine above the highest committed use, so a use this
search missed by a few seeds does not cost the band. 900 seeds is ample against
the 86.4% out-of-band acceptance rate (`--tally 4000 4999` prints `seeds 1000 /
accepted 864 / witnessed_kill 136`, reproduced here) and the 53 to 59 draws each
earlier band took to fill fifty. That leaves 10000-10999 the only unspent
thousand, which is why the debug range has to close at 9999.

One coupling is load-bearing, the fifth freeze's unchanged: the Inputs row
(`execution-manifest.md:1210`) still binds 8000-8999 after this card, so
`tests/experiments/test_fresh_deduction_instrument.py:4788` takes its converted
branch, reads the moved record's `converted.informed` and requires that card to
be open and to name the live `manifest.json`. A missing file there is a red
suite, so the limits card has to exist in this tree.

## Acceptance

- [ ] The preregistered band is seeds 2100 to 2999 drawn ascending; the first
  fifty prefixes passing the unchanged proof-free filter form the set, every
  skipped seed carries its reason code, and seed 1, the seven development
  definitions and the five converted bands' seeds are excluded by construction.
  Only the band constant, its comment and the converted-band list move, and
  `size` stays 50, so `planned_units`
  (`experiments/fresh_deduction_instrument.py:582-585`) is unchanged.
- [ ] The 8000-8999 record moves to
  `audits/deduction-candidate/held-out/manifest-band-8000-8999.json` with
  `git mv`, bytes preserved except `status: development` and a `converted`
  record whose `date` is 2026-09-16, `pull_request` `#465`, `branch`
  `work/fresh-deduction-run-5`, `rendered_seeds` all fifty accepted seeds in
  order, `superseded_by` `MANIFEST_PATH`, and whose `note` names the complete
  but INCONCLUSIVE result and `tasks/diagnosis-2026-09-18-fifth-run.md`. A test
  asserts its `accepted` and `skipped` blocks equal the ones frozen at
  `405d7a8a`: fifty seeds running 8000 to 8057, eight `witnessed_kill` skips, an
  empty `dependency_restamps.entries`. `rendered_seeds` is derived from that
  `accepted` block, so a conversion describing a run that rendered seeds this
  set never held is red: the fifth card's check at full width.
- [ ] `converted.informed` names the sixth authorization's limits card, expected
  at `tasks/work/fresh-deduction-limits-6.md`, present and open in the tree this
  branch merges into, so
  `test_a_binding_to_a_converted_record_stays_an_open_obligation`
  (`tests/experiments/test_fresh_deduction_instrument.py:4788`) passes rather
  than erroring on an unresolvable path. Under a different slug it names the
  slug that exists; the diagnosis goes in `note`, which the gate reads as a card
  path.
- [ ] The 8000-8999 entry is appended to `CONVERTED_BANDS`, not prepended: the
  3000-3999 entry stays first because `DEFAULT_CALIBRATION_RECORD` is
  `CONVERTED_BANDS[0].manifest_path`
  (`experiments/fresh_deduction_instrument.py:7474`). `PREREGISTERED_BAND` moves
  to 2100-2999 and the range guard
  (`experiments/held_out_prefixes.py:1187-1230`) then refuses five converted
  bands and the live one; it reads intervals, not order, so 4000-4999 still
  tallies with the live band below it.
- [ ] The new record is written to `MANIFEST_PATH` by the unchanged
  `build_manifest` (status `held_out`, `dependency_restamps` empty, the seven
  development definitions and all five converted bands' digests asserted
  absent), so `verify_frozen_set`
  (`experiments/fresh_deduction_instrument.py:3091`, status check `:3116`, band
  check `:3146`) and the regeneration test cover the new band unchanged.
- [ ] `assert_manifest_binds_the_live_band`'s docstring
  (`experiments/fresh_deduction_instrument.py:1094-1110`) names 8000-8999 and
  2026-09-16 alongside the four earlier conversions, which is what
  `test_the_gate_says_which_bands_actually_moved`
  (`tests/experiments/test_fresh_deduction_instrument.py:1513`) reads out of
  `CONVERTED_BANDS` and each record's `converted.date`. No constant, no
  behaviour and no `GENERATOR_SOURCES` file moves with it.
- [ ] The debugging range is closed to seeds 1-50 and 9001-9999, in the
  `PREREGISTERED_BAND` comment and the module docstring of
  `tests/experiments/test_held_out_prefixes.py`, because 10000-10999 is the only
  unspent thousand a seventh freeze can draw. A test asserts `_DEBUG_SEEDS`
  (`:68`) and the widest debug walk (`:1196`, 9001-9100) lie inside it and that
  9001-9999 intersects no band.
- [ ] The band's skip split is re-read off the published skips, not carried
  forward: `_reporter_witnessed_seed_one_prefix`'s docstring
  (`tests/experiments/test_held_out_prefixes.py:154-162`) states this band's
  reporter and bystander counts from `--skip-roles manifest`, and says a band's
  split is a small sample.
- [ ] No prefix bytes are committed; the preparer inspects no generated prefix
  beyond the automated filter and hash computation, runs no arm and makes no
  provider call, and debugs on seeds 1-50 and 9001-9999 only.
- [ ] `audits/deduction-candidate/README.md` indexes all six records, and the
  `audits/` row (`docs/artifacts.md:109`, today 25,974,591 tracked bytes / 324
  files) is recomputed with them staged; `scripts/verify_ml_evidence.py` passes
  offline.
- [ ] Every acceptance item that adds a gate has a planted failure showing it
  detects the defect it claims to, applied to the tree, run, and reverted.
- [ ] Results states the accepted and skipped counts, the reason histogram, the
  last accepted seed, the record's sha256 and byte size, and the two commands
  (`--tally FIRST LAST` out of band, `--skip-roles manifest`).

## Constraints

No live provider call of any kind; fake and scripted providers only, and the
credentials file is never opened. The band is preregistered here and may not be
changed; a band that cannot fill fifty is a stop, not a wider band. The owner's
merge of the diagnosis's decisions on 2026-09-18 authorizes the conversion date
2026-09-16, the fifty rendered seeds the archive records, and the decision to
freeze a sixth band at all. The band 2100-2999 and the closed range 9001-9999
are this card's own proposals, argued in Evidence; the merge fixes them.

The preparer edits `experiments/held_out_prefixes.py` only for the band constant
with its comment and the converted-band list, and
`experiments/fresh_deduction_instrument.py` only for the one gate docstring the
conversion list is read against. It does not edit the execution manifest,
`experiments/deduction_scenarios.py` or `experiments/deduction_evaluation.py`:
that manifest's Inputs table (`execution-manifest.md:1210`) is re-bound to
2100-2999, and its Roles table's preparer row (`:1798`) extended with this
session and its pull request, by the limits card. Until that lands,
`assert_manifest_binds_the_live_band` refuses a live run on this tree, which is
intended and is not something to relax.

No adoption, no re-record, no committed recording or report rewritten.
Prompt-byte and meeting-layer changes are not this card's and stay default-OFF
behind `public_account_version`, `attributed_testimony_version` and
`evidence_reasoning_version` (`orchestrator/experiment_config.py`,
`meetings/evidence_profile.py`), on
[the v5 prompt card](accounts-prompt-set-v5.md) and
[the citation-guard card](relevance-aware-citation-guard.md). The live run's
primary outcome, decision rule, minimum actionable effect,
`WRONGFUL_EJECTION_TRADEOFF` and `STOP_RULE` do not change. `agents/` never
imports `engine/` and `meetings/` never imports `experiments/`; this card
touches neither, keeps one writer per file in the wave, and recomputes the
artifacts row for any `audits/` byte change.

## Expected scope

`experiments/held_out_prefixes.py` (band constant and comment, converted-band
list), `tests/experiments/test_held_out_prefixes.py`,
`experiments/fresh_deduction_instrument.py` (the one gate docstring),
`tests/experiments/test_fresh_deduction_instrument.py` only where it pins the
first accepted seed, the band or the conversion list, both
`audits/deduction-candidate/held-out/` records, that directory's `README.md`,
`docs/artifacts.md` (the `audits/` row), `tasks/README.md`'s derived inventory
sentence, this card.

Delivered on `work/held-out-prefix-freeze-6` with one pull request into `main`,
a merge commit or fast-forward and never a squash, every commit carrying
`Card: tasks/work/held-out-prefix-freeze-6.md`. It shares no source file with
the wave and bases on `main` rather than stacking. The order is wave A,
[the v5 accounts prompt set](accounts-prompt-set-v5.md) in parallel with
[the diagnostics card](fresh-deduction-instrument-diagnostics.md); wave B,
[the guard](relevance-aware-citation-guard.md) on the diagnostics branch; then
[the third calibration](fresh-deduction-calibration-3.md) on all three; then,
once it reports, the sixth authorization with
[its limits card](fresh-deduction-limits-6.md), and this card dispatched
alongside that limits card, which is what `converted.informed` names and what
re-binds the Inputs row.

## Record impact

Adds a sixth frozen evaluation-input record under `audits/` and flips the fifth
to development in place; no recording, report, DTO, metric or weight byte moves,
no experiment becomes ON, no adopting record is created. The conversion does
make the 8000-8999 record eligible as a calibration input
(`verify_calibration_set`, `experiments/fresh_deduction_instrument.py:3270`,
status check `:3317`), widening that draw's acceptable record prefixes by one,
which `test_only_a_prefix_of_the_converted_records_is_accepted`
(`tests/experiments/test_fresh_deduction_instrument.py:8283`) derives from
`len(paths)`. Nothing draws from it yet:
[the third calibration](fresh-deduction-calibration-3.md) reports before this
card lands and pins its draw to the earlier records.

## Validation

`uv run pytest tests/experiments -q`, then `uv run python
scripts/validate_task_docs.py`, `uv run python scripts/check_doc_facts.py`,
`uv run python scripts/verify_ml_evidence.py` (offline; never `--complete`),
`uv run pytest tests/scripts/test_verify_ml_evidence.py -q`, and
`bash scripts/check.sh` run whole, in a clean worktree, so no gate after the
first failure is masked. Never the live evaluation, and never the generator on
a band.
