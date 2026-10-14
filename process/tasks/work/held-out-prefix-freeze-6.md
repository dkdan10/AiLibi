# Retired unexecuted: no sixth held-out band was frozen

**Status:** done

## Outcome

RETIRED UNEXECUTED on 2026-09-19. No sixth held-out band was frozen and none
will be under this card. The evaluation it would have supplied inputs to was
closed that day by the owner's acceptance of decision D2 of
[the direction memo](../direction-2026-09-19-process-over-outcome.md), which
retires the proof-free held-out band as the arena and keeps 2100-2999 unseen.
The one thing this card was also going to do — mark the fifth band's record
development in place — was done instead by
[the closing card](close-deduction-candidate-evaluation.md), which archived it.
What the card would have delivered is stated below unchanged, so the band
search that reserved 2100-2999 stays readable.

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

**The reservation of 2100-2999 is a document, not code (2026-09-19).** The band
search above is why this card stays in the tree rather than being deleted: it is
the record that reserves 2100-2999, and the closing card preserved it on that
footing. Nothing in code holds the reservation — no constant, no test and no
tally range names those seeds, and the range guard
(`experiments/held_out_prefixes.py`) refuses only the five bands that were
actually frozen. A future tally or freeze over 2100-2999 is therefore stopped by
nobody but a reader of this paragraph.

One coupling was load-bearing, the fifth freeze's unchanged: the Inputs row
(`execution-manifest.md:1210`) still binds 8000-8999 after this card, so
`test_a_binding_to_a_converted_record_stays_an_open_obligation` would take its
converted branch, read the moved record's `converted.informed` and require that
card to be open and to name the live `manifest.json`. That is no longer what
happens: the closing card archived the 8000-8999 record AT `MANIFEST_PATH` with
`superseded_by` `null`, and the same test gained a third branch for the closed
state, which asserts that no live run can start instead of that a re-binding is
owed. The sixth authorization's limits card was never created and is not needed.

## Acceptance

- [x] No sixth held-out band was frozen under this card, and none will be: the
  evaluation it prepared inputs for was closed on 2026-09-19 by the owner's
  acceptance of decisions D1, D2 and D8 of
  [the direction memo](../direction-2026-09-19-process-over-outcome.md), so the
  card is retired unexecuted. No prefix was generated, no seed of 2100-2999 was
  walked, no record under `audits/deduction-candidate/held-out/` was written by
  it, and no provider was reached. The items this card carried before are in the
  repository history; the band search in Evidence stays as the document
  reserving 2100-2999.

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

## Results

**Retired unexecuted, 2026-09-19.** Nothing in this card ran. The owner
accepted decisions D1 to D8 of
[the direction memo of 2026-09-19](../direction-2026-09-19-process-over-outcome.md)
as a set that date, with the rulings in its section 12. D2 retires the
proof-free held-out band as the arena and keeps 2100-2999 unseen, which leaves
this card with nothing to prepare: a sixth band would be inputs for a sixth run
that the same ruling forbids. The retirement was carried out by
[the closing card](close-deduction-candidate-evaluation.md) in the same wave,
which is also where the verification evidence for it lives.

**What was and was not done.** No prefix was generated. No seed of 2100-2999
was walked, by the tally command or by anything else, so the band is as unseen
as it was when this card reserved it. `PREREGISTERED_BAND` still names
8000-8999 — the band the archived record holds — and 2100-2999 appears in no
constant, no test and no tally range; the reservation is this document and
nothing more, which the paragraph in Evidence says out loud. `CONVERTED_BANDS`
gained no entry, because the fifth band's record was archived in place at
`MANIFEST_PATH` rather than moved beside the four that a freeze displaced.

**The one item that was delivered elsewhere.** This card would also have marked
the 8000-8999 record development. The closing card did that instead, in place
and with the same facts the acceptance item above described — date 2026-09-16,
pull request `#465`, branch `work/fresh-deduction-run-5`, all fifty rendered
seeds — with two differences that follow from the closure: the record keeps the
path `audits/deduction-candidate/held-out/manifest.json` because nothing
replaced it, and its `superseded_by` is `null` rather than a successor's path.
`converted.informed` names the closing card, which exists and is in the tree.

**Delivery states.** Implemented: not applicable — no implementation exists.
Verified: not applicable. Merged: this retirement merges with the closing card's
pull request. Adopted: not applicable; no experiment and no adopting record is
involved, and no lever moved.

**Limitation.** Nothing in code stops a future tally, freeze or recording over
2100-2999. The range guard refuses only the five bands that were actually
frozen, and a seventh freeze would have to re-run the census in Evidence rather
than trusting it: this document is nearly a year of commits away from whatever
tree reads it next.
