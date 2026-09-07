# Build the fresh-model deduction evaluation instrument and manifest

**Status:** ready

## Outcome

A frozen, reviewable instrument and an execution manifest exist for the smallest
useful fresh-model comparison of deduction without direct kill or vent proof.
The instrument runs end to end against a fake provider at zero cost, and the
manifest binds every preregistration field except the owner's authorization
fields, which stay empty until the owner fills them. No live call is authorized
by this card.

## Evidence

Review claims are leads, not measurements of this tree. Reproduce the design
claims from the archived follow-up review
([report](../../audits/review-2026-09-06/REVIEW_REPORT_FOLLOWUP.md) sections 11
and 12.4) on this checkout before implementing.

`audits/deduction-candidate/preregistration.md:105-118` states what the execution
manifest must bind: candidate and reference source inventories, prompt and
template versions, development versus held-out inputs and their seed lists,
exact provider and model, sampling configuration, token caps, elapsed-time and
cost limits with the owner's explicit authorization, and the decision rules and
margins justified before outcomes are inspected. `:120-122` states that no live
call, "including a pilot or retry on flat-rate service", is authorized by that
draft. [The planning card](fresh-deduction-evaluation.md) completed that
preregistration and is planning only; it is not an execution authorization.

The follow-up review's section 12.4 dry-ran a concrete design with the fake
provider: 50 held-out proof-free scripted prefixes x 2 arms = 100 meeting units,
about 600 model calls. It also established what this instrument must not be: the
committed harnesses (`experiments/deduction_evaluation.py`,
`experiments/investigation_evaluation.py`) are stage-1 MECHANICS_ONLY
instruments whose refusal of real providers is their own acceptance criterion
and must stay. The public API already supports the run without editing tracked
code: `HeadlessGame` (`orchestrator/game.py:1978`) with
`build_default_agent_factory(experiment_config=...)` (`:4283`) and
`build_default_meeting_runner(llm_client=...)` (`:1258`) accepts an injected
client. The committed token figures are `len//4` heuristics; calibrated against
the real usage rows in `replays/samples/`, real input runs about 1.27x and real
output about 3.7x those figures.

The owner's spending authorization for this instrument is assessed in
[the 2026-09-07 decision memo](../owner-decisions-2026-09-07.md) item B, whose
decision-input sheet (B.1) and ruling (B.12) supply the exact owner-field list,
the recommended values and their anchors; the manifest copies the owner's
ruled values verbatim. That memo
corrects the output calibration stated above: real output is about **1.51x** the
`len//4` heuristic, not 3.7x — the 3.7x figure compares real output per call
against the scripted capture's per-call output, a different denominator, on
which the honest ratio is 3.05x. Any ratio the manifest quotes must name its
denominator.

## Acceptance

- [ ] A new instrument, separate from the two committed MECHANICS_ONLY
  harnesses, driving the run through the public API only
  (`HeadlessGame`, `build_default_agent_factory`, `build_default_meeting_runner`).
  The committed harnesses keep refusing real providers; that refusal is not
  relaxed, reused or subclassed away.
- [ ] 50 held-out proof-free scripted physical prefixes are generated, frozen and
  hashed before any arm runs, prepared by someone other than the runner. No
  living crew member holds a firsthand kill or vent observation before the
  meeting, the killer's own record included. The seven committed development
  cases are excluded by hash.
- [ ] Two arms paired on identical prefixes: `repaired_clock` (temporal 2,
  evidence 2, nothing else) versus `combined_accounts` (plus public accounts and
  attributed testimony). Investigation changes the world and is out of scope.
- [ ] The paired exact McNemar test is computed by
  `scripts/paired_stats.py::exact_mcnemar_p` (`:95`) over the discordant units,
  with the decision rule, the minimum actionable effect and the stop rule written
  into the manifest before any outcome is inspected.
- [ ] A per-call token cap and a wall-clock deadline are wired into the
  instrument and abort visibly; a planted overrun stops the run and reports the
  partial state rather than continuing quietly.
- [ ] A "supported" grader over the ballot's `primary_reason_id` /
  `primary_reason_observation_id`: the cited turn or observation must be present
  in that voter's own prompt. A separate frozen privileged grader scores "right
  for that reason"; judge information never returns to a listener or a tactic.
- [ ] `audits/deduction-candidate/execution-manifest.md` exists and binds every
  preregistration field, with the owner-authorization fields present and EMPTY:
  provider, exact model, per-call token cap, total token budget (about 2.5 M
  projected from the calibrated ratios), wall-clock deadline and dollar limit. A
  cost statement is required even on flat-rate service.
- [ ] A fake-provider dry run of the full pipeline completes at $0 and is
  recorded as a mechanics check. It is stated in Results that a green dry run
  says nothing about model judgment.

## Constraints

This card authorizes planning and an offline-exercisable instrument only. **No
live provider call is authorized, including a pilot, a smoke run or a retry, and
including on flat-rate service.** Executing the design needs a separate card
carrying the owner's filled-in authorization fields.

Inspecting a held-out input converts it to development data; the generator and
the runner are different roles for that reason. No adoption, no new maps, roles,
providers, dependencies or training. Existing baseline-only training campaigns
stay unchanged. The committed captures remain MECHANICS_ONLY and are not
recategorised. Follow `docs/architecture.md` Layering, Enforced boundaries and
Determinism; keep listener-visible evidence distinct from the privileged grader.
Any `audits/` byte change requires refreshing the `audits/` row of
`docs/artifacts.md`.

Preconditions: [the renderer repair](evidence-renderer-salience.md) and
[the provenance gaps](recorded-provenance-gaps.md) must both have landed —
otherwise the candidate arm is evaluated with its own evidence evicted, the two
arms are not distinguishable in provenance, and the reconstructed memories are
not provably the ones the model saw. The death-tick body handle is either left
as-is and stated in the manifest, or masked identically in both arms.


The held-out set is the one frozen by the owner's merge of the
[freeze card](held-out-prefix-freeze.md)'s pull request: before any arm runs,
the instrument regenerates it with `experiments.held_out_prefixes.generate()`
from the band in `audits/deduction-candidate/held-out/manifest.json`, checks
every prefix digest and the skip list against that manifest, and stops on any
mismatch. The runner opens no prefix, prints none, and consumes them only
through the `HeldOutPrefix` model; the prefixes are archived with the results
after the run, when they are no longer held out.

## Expected scope

A new instrument module under `experiments/`, its tests, the frozen prefix
generator and its hash inventory, and
`audits/deduction-candidate/execution-manifest.md`, plus the `docs/artifacts.md`
audits row that follows. `experiments/deduction_evaluation.py` and
`experiments/investigation_evaluation.py` are read, not edited. Reuse
`scripts/paired_stats.py` rather than reimplementing the test.

## Record impact

A prospective design and an offline-exercisable instrument. No recording, report
or DTO byte changes and no committed measurement is superseded. A green
fake-provider run is a mechanics check and never model judgment: it establishes
that the pipeline carries a non-SKIP decision through to a graded outcome, not
that any model would produce one. Completing this card grants no spending
authorization, adoption or merge. `audits/` tracked bytes move when the manifest
lands, so the registry row moves with them.

## Validation

`uv run pytest tests/eval tests/experiments -q` — the committed harness tests
live under `tests/eval`; the new instrument's tests go beside them and the fake
provider is the only provider any of them may reach. Then
`uv run python scripts/validate_task_docs.py`, then `bash scripts/check.sh`,
then `uv run python scripts/check_doc_facts.py` and
`uv run python scripts/verify_ml_evidence.py`, because the manifest moves the
`audits/` byte total that registry row promises. Do not run the prospective live
evaluation as a check.
