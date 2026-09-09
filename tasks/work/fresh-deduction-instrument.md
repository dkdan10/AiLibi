# Build the fresh-model deduction evaluation instrument and manifest

**Status:** done

## Outcome

A frozen, reviewable instrument and an execution manifest exist for the smallest
useful fresh-model comparison of deduction without direct kill or vent proof.
The instrument runs end to end against a fake provider at zero cost, and the
manifest binds every preregistration field, the owner's authorization fields
included: the owner filled those by merging
[the authorization card](fresh-deduction-authorization.md) as #437 on
2026-09-07 (merge commit `0f49d8e6`, ruling B.12), which supersedes this card's
original "stay empty until the owner fills them" wording. No live call is
authorized by this card, and none was made.

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

- [x] A new instrument, separate from the two committed MECHANICS_ONLY
  harnesses, driving the run through the public API only
  (`HeadlessGame`, `build_default_agent_factory`, `build_default_meeting_runner`).
  The committed harnesses keep refusing real providers; that refusal is not
  relaxed, reused or subclassed away.
- [x] 50 held-out proof-free scripted physical prefixes are generated, frozen and
  hashed before any arm runs, prepared by someone other than the runner. No
  living crew member holds a firsthand kill or vent observation before the
  meeting, the killer's own record included. The seven committed development
  cases are excluded by hash.
- [x] Two arms paired on identical prefixes: `repaired_clock` (temporal 2,
  evidence 2, nothing else) versus `combined_accounts` (plus public accounts and
  attributed testimony). Investigation changes the world and is out of scope.
- [x] The paired exact McNemar test is computed by
  `scripts/paired_stats.py::exact_mcnemar_p` (`:95`) over the discordant units,
  with the decision rule, the minimum actionable effect and the stop rule written
  into the manifest before any outcome is inspected.
- [x] A per-call token cap and a wall-clock deadline are wired into the
  instrument and abort visibly; a planted overrun stops the run and reports the
  partial state rather than continuing quietly.
- [x] A "supported" grader over the ballot's `primary_reason_id` /
  `primary_reason_observation_id`: the cited turn or observation must be present
  in that voter's own prompt. A separate frozen privileged grader scores "right
  for that reason"; judge information never returns to a listener or a tactic.
- [x] `audits/deduction-candidate/execution-manifest.md` exists and binds every
  preregistration field, with the owner-authorization fields carrying the
  owner's ruled values: provider, exact model, per-call token cap, total token
  budget, wall-clock deadline and dollar limit. A cost statement is required
  even on flat-rate service. **Superseded 2026-09-07:** this item originally
  asked for those fields "present and EMPTY" with the budget stated as "about
  2.5 M projected from the calibrated ratios". The owner's merge of #437
  (`0f49d8e6`, ruling B.12) filled them instead, at 2,400,000 input / 200,000
  output run-level, so they are present and FILLED, copied verbatim from
  [the authorization card](fresh-deduction-authorization.md).
- [x] A fake-provider dry run of the full pipeline completes at $0 and is
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

## Results

Delivered on `work/fresh-deduction-instrument`, based on `5682ea2a` (the
verified tip of `work/recorded-provenance-gaps`, which carries both
preconditions: the renderer repair and
`GameProvenance.temporal_observation_version`). Every figure below was produced
by the quoted command on the tree this card was completed at; a figure measured
at an earlier commit is dated where it appears.

### What was built

`experiments/fresh_deduction_instrument.py` — a new module, separate from the
two committed MECHANICS_ONLY harnesses, that runs one meeting per frozen
held-out prefix under two paired arms and grades the ballots. It drives the run
through the shipped public entry points (`HeadlessGame`,
`build_default_meeting_runner`, the public `TacticalAgent`), consumes the frozen
set through `experiments.held_out_prefixes` rather than regenerating a second
one, and reuses `scripts/paired_stats.py::exact_mcnemar_p` rather than
reimplementing the test.

`audits/deduction-candidate/execution-manifest.md` — the manifest, binding every
field `audits/deduction-candidate/preregistration.md:105-118` names, with the
owner's authorized limits copied verbatim.

`tests/experiments/test_fresh_deduction_instrument.py` — 82 tests, every one on
the fake provider.

### Architecture and design sections

`docs/architecture.md` Layering: the instrument sits in `experiments/`, which
the import-linter contracts leave out by design, and composes `orchestrator/`,
`meetings/` and `llm/` without reaching inside any of them. Enforced
boundaries: nothing here imports `engine/` from `agents/`; the four contracts
stay kept (`Contracts: 4 kept, 0 broken`). Determinism: each unit replays a
frozen prefix through the same tick function the freeze screened it with, and
the tick budget stops the game one tick after the report so nothing downstream
of the decision is claimed. Listener-visible evidence stays distinct from the
privileged grader: `grade_supported` reads only the prompts a voter was handed,
`grade_privileged` reads the hidden roles and takes the support labels as an
argument, and the run path calls neither.

### Decisions

**The arms cannot run on `build_default_agent_factory`, and that is a limitation
of the factory rather than a preference.** Its agents choose their own actions,
so they cannot execute a frozen scripted prefix, and the `AgentMemory` it
constructs carries none of an arm's channel versions
(`orchestrator/game.py:4295-4321` builds `TacticalAgent(agent_id=…, policy=…,
role=…)` with no memory, and `TacticalAgent.__init__` then falls back to a bare
`AgentMemory()`). The instrument therefore builds the same public
`TacticalAgent` with the same public `CrewmatePolicy` / `ImpostorPolicy` that
factory builds and hands it the prefix and the arm's memory — the construction
`experiments/deduction_scenarios.py::run_case` already uses. This is a deviation
from the card's acceptance wording, which names `build_default_agent_factory`
among the public entry points; it is recorded here rather than worked around,
because a scripted prefix and that factory are mutually exclusive.

**The owner-authorization fields are FILLED, not empty.** The card asked for them
"present and EMPTY"; the owner's merge of #437 on 2026-09-07 (`0f49d8e6`, ruling
B.12) filled them. The manifest copies the authorization card's Constraints
table and cost statement verbatim, states the supersession in its own header,
and the Acceptance item above carries the same dated note.

**A live call needs an explicit invocation, not just the manifest.**
`assert_live_run_is_authorized` refuses every provider except `fake` without a
`LiveRunInvocation` naming `audits/deduction-candidate/execution-manifest.md`;
`LiveRunInvocation.naming` refuses any other path, and refuses a manifest that
does not name the authorized provider, model and prompt set; `run_dry` refuses a
`LiveRunInvocation` outright so the mechanics check cannot become the run; and a
tree scan keeps `--i-am-the-runner` out of every committed test, script and
workflow. No live provider call of any kind was made on this card.

**The analysis is frozen in code and in the record before any outcome exists.**
`PRIMARY_OUTCOME`, `DECISION_RULE`, `MINIMUM_ACTIONABLE_EFFECT_UNITS` and
`STOP_RULE` are module constants; the manifest quotes each verbatim and a test
asserts it does. The minimum actionable effect (net 10 of 50) is justified from
the design's own resolution, and every figure in that justification recomputes:

```sh
.venv/bin/python -c "import sys; sys.path.insert(0, 'scripts'); \
from paired_stats import exact_mcnemar_p as p; \
print([(b, c, round(p(b, c), 6)) for b, c in \
[(5, 0), (6, 0), (15, 5), (16, 6)]])"
```

```
[(5, 0, 0.0625), (6, 0, 0.03125), (15, 5, 0.041389), (16, 6, 0.052479)]
```

The stop rule reads no outcome: 50 paired units are a fixed sample with no
interim analysis and no optional stopping, so nothing in it can be tripped by a
result the run produced.

**The observation audit goes to the null device.** It restates the prefix packet
by packet and the instrument reads none of it, so writing it into a results
directory would publish a held-out input for nothing. The precedent is
`experiments/tactical_gameplay.py`.

### The fake-provider dry run

```sh
.venv/bin/python -m experiments.fresh_deduction_instrument --dry-run
```

| | `repaired_clock` | `combined_accounts` |
| --- | --- | --- |
| units | 50 | 50 |
| model calls | 300 | 300 |
| ejections | 50 | 50 |
| role-correct | 19 | 19 |
| supported-correct | 18 | 18 |
| supported ballots | 150 | 150 |
| guard-rewritten ballots | 6 | 6 |
| input tokens (`len // 4`) | 886,054 | 575,251 |
| output tokens (`len // 4`) | 19,800 | 19,800 |

100 units, 600 calls, `total_cost_usd` 0.0, in a few seconds of wall.

**A green dry run says nothing about model judgment.** The dry-run provider reads
the prompt for a valid target and a real turn id and returns them; the run
establishes that the pipeline carries a non-SKIP decision through to a graded
outcome, not that any model would produce one. Its choice does not depend on the
arm, so the dry run's paired result is `b=0, c=0, p=1.0` BY CONSTRUCTION and is
not a comparison between the arms.

The token figures are a headroom check, not a prediction: the prompts are the
real rendered ones but the transcript a real model writes will differ. Applying
the decision memo's calibrated 1.28x real-input ratio to the sum
(886,054 + 575,251 = 1,461,305) gives about 1.87 M against the 2.4 M run-level
ceiling, and the larger arm's 17,721 per unit gives about 22,700 against the
45,000 per-unit ceiling.

### Planted and perturbed failures

Every gate this card adds was removed or perturbed in turn, its own test run, and
the source restored. One worked example, then the table of all ten produced the
same way:

```sh
.venv/bin/python -c "import pathlib; p = pathlib.Path('experiments/fresh_deduction_instrument.py'); \
p.write_text(p.read_text().replace('    if actual_accepted != expected_accepted:', '    if False:'))"
PYTHONDONTWRITEBYTECODE=1 .venv/bin/pytest \
  'tests/experiments/test_fresh_deduction_instrument.py::TestFrozenSet::test_a_moved_digest_stops_the_run' \
  -q --no-header
```

```
FAILED tests/experiments/test_fresh_deduction_instrument.py::TestFrozenSet::test_a_moved_digest_stops_the_run
1 failed in 0.57s
```

| Gate removed or perturbed | Test that went red |
| --- | --- |
| `if actual_accepted != expected_accepted:` → `if False:` | `TestFrozenSet::test_a_moved_digest_stops_the_run` |
| `if actual_skipped != expected_skipped:` → `if False:` | `TestFrozenSet::test_a_changed_skip_list_stops_the_run` |
| `if invocation is None:` → `if False:` | `TestLiveGate::test_a_live_provider_without_an_invocation_is_refused` |
| `if response.usage.output_tokens >= max_tokens:` → `if False:` | `TestPerCallCaps::test_a_truncated_response_stops_the_run` |
| `if max_tokens not in self._allowed_max_tokens:` → `if False:` | `TestPerCallCaps::test_a_call_outside_the_shipped_caps_stops_the_run[512]` |
| `grade_supported` reads every voter's prompts instead of the voter's own | `TestGraders::test_a_citation_only_another_voter_saw_is_unsupported` |
| the prefix-bytes guard searches `model_dump_json()` instead of walking the dumped strings | `TestPrefixSecrecy::test_a_report_carrying_a_scripted_step_is_refused` |
| `if clock != arm.temporal_version:` → `if False:` | `TestProvenance::test_a_mislabelled_clock_stops_the_run_and_reports_partial_state` |
| the abort handler stops charging the stopped unit's calls | `TestBudgetAndDeadline::test_the_stopped_units_spend_is_retained` |
| the primary outcome stops excluding guard-rewritten ballots | `TestGraders::test_a_guard_rewritten_ballot_is_not_the_voters_supported_call` |

All ten went red; the source was restored and
`.venv/bin/pytest tests/experiments/test_fresh_deduction_instrument.py -q`
returned `82 passed` again.

The seventh row is a real defect this exercise found rather than a synthetic one:
the guard originally searched `report.model_dump_json()`, and a prefix step
smuggled into a string field survives that encoding as an ESCAPED substring, so
the search looked clean while the field still carried the input. The guard now
walks the dumped structure.

Two further planted overruns are not in the table because they need no source
edit — the limits are a parameter:
`TestBudgetAndDeadline::test_a_budget_overrun_stops_the_run_and_reports_partial_state`
starves the run-level input budget and asserts the run stops with
`0/4 units completed`, and
`test_an_expired_deadline_stops_the_run_and_reports_partial_state` and
`test_an_exhausted_model_work_window_stops_the_run` do the same for the two
clocks. A live run cannot use those parameters:
`assert_live_run_is_authorized` refuses any limits that are not
`AUTHORIZED_LIMITS`.

### Verification

Every row was run on this branch's code at `87dfd918`, the commit that carries
all of it; the commit after it edits this Results section only.

| Command | Result |
| --- | --- |
| `.venv/bin/pytest tests/eval tests/experiments -q` | `1259 passed, 1 skipped in 184.64s` |
| `.venv/bin/python scripts/validate_task_docs.py` | `390 historical phase tasks and 390 prompts; 43 work cards` |
| `bash scripts/check.sh` | exit 0 — `Contracts: 4 kept, 0 broken`; `Success: no issues found in 473 source files`; `7347 passed, 20 skipped, 3 xfailed`; frontend `Test Files 19 passed`, `Tests 515 passed` |
| `.venv/bin/python scripts/check_doc_facts.py` | `Doc facts verified` / `Front door verified` / `Budgets verified` |
| `.venv/bin/python scripts/verify_ml_evidence.py` | `checks: 60 \| OK 48 \| FAIL 0 \| ABSENT 7 \| INFO 5`; `every check passed` |
| `bash scripts/verify_samples.sh` | `All 50 samples verified clean.` for both sets |
| `scripts/build_sample_report.py --check` x 4 | all four `is consistent with its replays` |
| `.venv/bin/pytest tests/orchestrator/ --collect-only -q` | `583 tests collected` |
| `.venv/bin/pytest tests/experiments/test_fresh_deduction_instrument.py -q` | `82 passed` |

One earlier suite run, made while a second full parallel suite was running on
the same machine, failed
`tests/orchestrator/test_run_limits.py::test_wall_deadline_cancels_meeting_and_retains_success`
with `provider.attempts == 0`. That test builds a `RunDeadline(0.25)` and asserts
two provider attempts inside 250 ms of wall, so it is load-sensitive; it passes
in isolation (`2 passed in 0.45s`) and inside the quiet gate above, and nothing
on this branch touches `orchestrator/run_limits.py`, the meeting runner or the
game loop. Recorded rather than dropped, because a reader running two suites at
once will see it too.

`cd frontend && npm run e2e` was not run: no served DTO changed. No `audits/` or
`tests/fixtures/` byte outside this card's own new manifest moved.

### The frozen held-out set

Regenerated in process and checked against
`audits/deduction-candidate/held-out/manifest.json` before anything else runs: 50
accepted digests (seeds 3000-3057) and 8 skips, all `witnessed_kill`. No prefix
was printed, logged or written into any report. That last claim is checked
rather than asserted: every one of the 50 prefixes' canonical JSON and every one
of their 382 distinct step encodings was searched for across all 2,094 tracked
files on this branch, and no file carries one — the scan regenerates the
fragments through `experiments.held_out_prefixes` and reported `files carrying a
band prefix or one of its steps: []`. This branch edits no `GENERATOR_SOURCES`
file,
so the freeze manifest needed no `dependency_restamps` entry;
`tests/experiments/test_held_out_prefixes.py::test_the_committed_manifest_regenerates_from_its_own_band`
passes unchanged inside the `tests/eval tests/experiments` run above.

### Registry row

`audits/` gained one file, the execution manifest. Recomputed with the change
staged, by listing the tracked paths and summing their sizes:

```
203 files 14873520 bytes
```

`docs/artifacts.md` now reads `14,873,520 tracked bytes / 203 files`, up from
`14,852,791 / 202`, and `scripts/verify_ml_evidence.py` compares that row
against disk (`OK 48 | FAIL 0` above).

### Limitations

- **A green dry run is mechanics, not judgment**, and the dry run cannot produce
  a difference between the arms at all: its provider's choice is
  arm-independent, so `b=0, c=0` is a property of the fixture rather than a
  measurement. Nothing here says anything about how a model decides.
- **The dry run's scripted turns carry one accusation claim and no structured
  observations**, so the accounts and attributed-testimony channels are
  exercised as rendering and reduction paths with a thin ledger. A real model
  fills them; this run does not test how well.
- **`build_default_agent_factory` is not used**, for the reason in Decisions.
- **The freeze manifest's `source_sha256` is not re-checked here.** The freeze's
  own regeneration test owns it; duplicating the check would stop a run for a
  reason that test states better.
- **Nothing is authorized to spend.** The manifest binds limits and this card
  authorizes no call. Executing the design needs a separate card carrying an
  explicit runner invocation, and the result of such a run would be a
  measurement, not an adoption.
