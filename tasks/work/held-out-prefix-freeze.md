# Freeze the held-out prefixes for the fresh-model deduction evaluation

**Status:** ready

## Outcome

Fifty held-out, proof-free scripted physical prefixes exist as a frozen,
hashed set for the authorized roster, prepared by a session that will never run
the evaluation, without any person or session inspecting a prefix before the
run. The generator is deterministic from a seed band preregistered in this
card, so the runner later regenerates the set from the committed generator and
proves it matches the committed hashes rather than reading committed prefix
bytes. The owner's merge of the preparer's pull request is the freeze.

Two roles, ruled by the owner on 2026-09-07 (item B of
[the decision memo](../owner-decisions-2026-09-07.md)): the **preparer** is a
fresh session dispatched on this card alone; the **runner** is a separate
session started after the freeze, dispatched on
[the instrument card](fresh-deduction-instrument.md), which opens no prefix
before the run. The coordinator dispatches both, reviews generator code and
hashes only, and runs neither.

## Evidence

`audits/deduction-candidate/preregistration.md:143-149` requires a separate
reviewer to prepare and freeze new held-out legal schedules and information
patterns before the candidate is evaluated on them; relabeling players or
rerunning an inspected schedule is not independent confirmation, and inputs
that inform a fix become development data. The instrument card restates this
at `fresh-deduction-instrument.md:63-65` and `:98-99` (generator and runner
are different roles because inspecting a held-out input converts it).
[The authorization card](fresh-deduction-authorization.md) binds the roster
these prefixes must fit: 4p1i with three living voters at meeting open,
sequential execution, and a `body-p-\d+-\d+` assertion over the frozen
prefixes as well as the live prompts.

The seven development cases are hand-authored schedules in
`experiments/deduction_scenarios.py`: `ScenarioDefinition` (`:54-76`) pins
seed 1, four players, one impostor, one task per crewmate and fourteen ticks
as `Literal` fields, carries a `steps` tuple of `(tick, ActionIntent)` pairs,
a claimed room and tick, the expected kill and report ticks, and an
information-limit sentence; `scenario_definition` (`:78`) materialises the
routes. `experiments/deduction_evaluation.py:161-174` (`validate_channels`)
and `:255-270` classify observed `saw_player` rows with a `kill` or `vent`
action as firsthand proof; the follow-up review's NG2-6 records that this guard
excludes the killer's own kill record, so a published count of zero coexists
with a firsthand killer record. The filter here counts living crewmates'
observations only and says so in the manifest. The tactical
harness already uses disjoint seed bands for its development and held-out
splits (`experiments/tactical_gameplay.py:721-735`), and its capture re-checks
the runtime fingerprint so inputs cannot move mid-run.

No held-out prefix exists today; every committed scenario is seed 1 and is
development data by construction.

## Acceptance

- [ ] A new module `experiments/held_out_prefixes.py` defines a `HeldOutPrefix`
  model (seed, roster, max ticks, the scripted steps up to and including the
  report that opens the meeting, the report tick, the kill tick) that does not
  pin seed or roster as literals, and a deterministic generator
  `generate(band, roster)` that, for each seed drawn ascending from the
  preregistered band, builds a legal schedule on the canonical map for 4p1i
  with exactly one kill before the meeting (three living voters at meeting
  open) and a crewmate body report as the meeting trigger, then keeps the
  prefix only if the proof-free filter passes. Every unlisted action is an
  explicit wait, as in the development cases.
- [ ] The preregistered band is seeds 3000 to 3999 drawn ascending; the first
  fifty prefixes that pass the filter form the set, and every skipped seed is
  recorded with its rejection reason. Seed 1 and the seven development
  definitions are excluded by construction and their definition hashes are
  asserted absent from the set.
- [ ] The proof-free filter runs the prefix through `HeadlessGame` with the
  fake provider under temporal observation version 2 and rejects a prefix if
  any living crewmate's episodic memory holds an observed `saw_player` row with
  a `kill` or `vent` action at meeting open; the impostor's own kill record is
  not counted. A planted prefix with a witnessed kill fails the filter; a
  planted prefix with a witnessed vent fails the filter.
- [ ] Under temporal version 2, no rendered meeting trigger line and no prefix
  step text matches `body-p-\d+-\d+`; the assertion is a test, and a planted
  legacy handle fails it.
- [ ] The freeze artifact `audits/deduction-candidate/held-out/manifest.json`
  records the band, the roster, the generator's source sha256, the engine and
  observation source hashes it depends on, the fifty accepted seeds in order,
  the sha256 of each accepted prefix's canonical JSON, and the skipped seeds
  with reasons. No prefix bytes are committed: the runner regenerates them from
  the committed generator and the band and refuses to proceed if any hash
  differs from the manifest.
- [ ] A test regenerates the set from the committed manifest's band and asserts
  every hash matches; a planted one-step change to the generator makes that
  test fail, which is the fail-loud a source edit after the freeze must
  produce.
- [ ] `docs/artifacts.md`'s `audits/` inventory row is recomputed after the
  manifest is staged, and `scripts/verify_ml_evidence.py` passes without
  `--complete`.
- [ ] Results states that the preparer session did not inspect any generated
  prefix beyond the automated filter and hash computation, did not run any
  arm, and made no provider call.

## Constraints

No live provider; the fake and scripted providers only, and no meeting model
call of any kind. The band is preregistered here and may not be changed by the
preparer; a generator that cannot fill fifty prefixes from the band stops and
reports, it does not widen the band. The preparer does not edit
`experiments/deduction_scenarios.py`, `experiments/deduction_evaluation.py` or
the instrument the runner will build; the only shared contract is the
`HeldOutPrefix` model this card creates, which the instrument card consumes.
Nobody opens a generated prefix: the preparer's review surface is generator
code, tests and the manifest; the owner's merge is the freeze. If a held-out
result later informs a fix, this set is marked development in the manifest and
a new band is frozen under a new card. No adoption, no re-record, no committed
recording or report rewritten.

## Expected scope

`experiments/held_out_prefixes.py` (new), `tests/experiments/test_held_out_prefixes.py`
(new), `audits/deduction-candidate/held-out/manifest.json` (new),
`docs/artifacts.md` (the `audits/` inventory row only), this card. Delivered on
a `work/held-out-prefix-freeze` branch and one pull request into `main`, per
the delivery policy in `AGENTS.md`.

## Record impact

Adds a frozen evaluation-input record under `audits/`; no recording, report,
DTO, metric or weight byte moves, no experiment becomes ON, and no adopting
record is created. The set's status flips to development data the first time a
held-out result informs a fix, and that flip is recorded in the manifest, never
by deleting it.

## Validation

`uv run pytest tests/experiments/test_held_out_prefixes.py -q` (fake provider,
$0), then `uv run python scripts/validate_task_docs.py`, `uv run python
scripts/check_doc_facts.py`, `uv run python scripts/verify_ml_evidence.py`
(offline half; never `--complete`), `uv run pytest
tests/scripts/test_verify_ml_evidence.py -q` for the inventory row, and
`bash scripts/check.sh`. The set's usefulness is exercised, not validated, by
the instrument card's run; do not run the prospective live evaluation as a
check.
