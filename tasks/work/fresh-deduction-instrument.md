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

- [x] Review correction: a meeting-internal default is counted per unit and per
  arm rather than vanishing into the ballot verdicts, and the manifest says what
  actually stops the run instead of promising a stop the code never made.
- [x] Review correction: the model-work window bounds each provider await, so it
  stops the run during the call that exhausts it rather than one whole call
  later.
- [x] Review correction: the card's own test count and its round-1 delta are the
  numbers the collect-only command prints.
- [x] Review correction: the declared blast radius names both `audits/` files
  this branch moved.
- [x] Review correction: the live run builds its client from the authorized
  provider and model rather than from the ambient environment, and a response
  from any other model is a stop on the call that returns it.
- [x] Review correction: a live invocation is authenticated against the
  committed manifest's own path and bytes, not against the fields of the object
  handed in.
- [x] Review correction: `--units` is a dry-run knob; a live invocation carrying
  one is refused, so the authorized command cannot run a one-unit pilot.
- [x] Review correction: every way a unit can fail stops the run with a
  partial-state record, the truncation stop included, and the stopped unit's
  spend is retained rather than dropped.
- [x] Review correction: the manifest binds the sampling temperatures and the
  acceptable wrongful-decision tradeoff, and the instrument serves and enforces
  both.
- [x] Review correction: the frozen set's band, tick budget and task count are
  compared and then used, so `verify_frozen_set` enforces what its docstring
  claims.
- [x] Review correction: the held-out scan figure in Results is the reproducible
  332 distinct step encodings, quoted with the command that prints it.
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
generator and its hash inventory,
`audits/deduction-candidate/execution-manifest.md` and the entry for it in
`audits/deduction-candidate/README.md` (that directory's index, which names each
file in it), plus the `docs/artifacts.md`
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

`tests/experiments/test_fresh_deduction_instrument.py` — 127 tests, every one on
the fake provider (82 when this card was first closed; the round-1 corrections
below took it to 113 and the round-2 corrections to 127):

```sh
.venv/bin/pytest tests/experiments/test_fresh_deduction_instrument.py \
  -q --collect-only | tail -1
```

```
127 tests collected in 0.65s
```

*(That paragraph read "112 tests … added 30" until round 2; both figures were
wrong, and the round-1 verification table below already said `113 passed`.)*

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
`LiveRunInvocation`, and takes nothing on that object's word: it re-resolves
`audits/deduction-candidate/execution-manifest.md` under the repository root and
requires the invocation to name exactly that file, re-hashes the file and
requires the invocation's digest to match, requires the invocation's model to be
the authorized one, and refuses moved limits, a moved sampling configuration and
any `--units` override. `LiveRunInvocation.naming` applies the same full-path
check when the invocation is built and additionally refuses a manifest that does
not name the authorized provider, model and prompt set. The client such a run
uses is `build_authorized_client`'s — the provider and model pinned from the
authorization, with only the API key crossing over from the shell — and a
response from any other model stops the run. `run_dry` refuses a
`LiveRunInvocation` outright so the mechanics check cannot become the run, and a
tree scan keeps `--i-am-the-runner` out of every committed test, script and
workflow. No live provider call of any kind was made on this card.

**The analysis is frozen in code and in the record before any outcome exists.**
`PRIMARY_OUTCOME`, `DECISION_RULE`, `MINIMUM_ACTIONABLE_EFFECT_UNITS`,
`WRONGFUL_EJECTION_TRADEOFF` and `STOP_RULE` are module constants; the manifest
quotes each verbatim and a test asserts it does. The decision rule is the
conjunction of three conditions — p below 0.05, a net of at least 10, and a net
increase in wrongful crew ejections no larger than that net — and
`PairedResult.meets_decision_rule` computes all three. The minimum actionable
effect (net 10 of 50) is justified from the design's own resolution, and every
figure in that justification recomputes:

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
result the run produced. It was amended in round 2 — still before any held-out
outcome exists — to state that a meeting-internal default is counted rather than
stopped, which is what the code does; the amendment is recorded below.

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
| defaulted turns / votes | 0 / 0 | 0 / 0 |
| units carrying a default | 0 | 0 |
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

Measured at `87dfd918`, when the suite held 82 tests. Every gate this card added
was removed or perturbed in turn, its own test run, and the source restored. One
worked example, then the table of all ten produced the same way:

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

All ten went red; the source was restored and, at `87dfd918`,
`.venv/bin/pytest tests/experiments/test_fresh_deduction_instrument.py -q`
returned `82 passed` again. The round-1 corrections below add their own planted
cases and their own table.

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

`cd frontend && npm run e2e` was not run: no served DTO changed. No
`tests/fixtures/` byte moved. Two `audits/` files moved: the new
`audits/deduction-candidate/execution-manifest.md` and eight added lines in
`audits/deduction-candidate/README.md`, the directory index, which gained an
entry for the freeze and one for the manifest. *(This sentence read "No `audits/`
or `tests/fixtures/` byte outside this card's own new manifest moved" until round
2; the README had already moved in `87c4ef3d`, two commits earlier, so the
sentence was wrong when it was written. `git diff --name-status 5682ea2a..HEAD --
audits/ tests/fixtures/` prints exactly those two paths.)*

### The frozen held-out set

Regenerated in process and checked against
`audits/deduction-candidate/held-out/manifest.json` before anything else runs: 50
accepted digests (seeds 3000-3057) and 8 skips, all `witnessed_kill`, under the
band, tick budget and roster the manifest itself names. No prefix was printed,
logged or written into any report. That last claim is checked rather than
asserted — 382 search needles, being the 50 prefixes' canonical JSON plus their
332 distinct step encodings, over all 2,094 tracked files on this branch:

```sh
git ls-files > /tmp/tracked.txt
.venv/bin/python -c "
import json, pathlib
from experiments.held_out_prefixes import canonical_prefix_json, generate
g = generate()
whole = {canonical_prefix_json(p) for p in g.prefixes}
steps = {json.dumps(s.model_dump(mode='json'), sort_keys=True, separators=(',', ':')) for p in g.prefixes for s in p.steps}
files = pathlib.Path('/tmp/tracked.txt').read_text('utf-8').split()
bad = [f for f in files if any(n in pathlib.Path(f).read_text('utf-8', errors='ignore') for n in whole | steps)]
print(f'{len(whole)} prefixes; {len(steps)} distinct step encodings; {len(files)} tracked files; offenders {bad}')
"
```

```
50 prefixes; 332 distinct step encodings; 2094 tracked files; offenders []
```

The prose here first read "382 distinct step encodings"; 382 is the needle total
and 332 is the step count, corrected in round 1 below. This branch edits no
`GENERATOR_SOURCES` file,
so the freeze manifest needed no `dependency_restamps` entry;
`tests/experiments/test_held_out_prefixes.py::test_the_committed_manifest_regenerates_from_its_own_band`
passes unchanged inside the `tests/eval tests/experiments` run above.

### Registry row

`audits/` gained one file, the execution manifest, and eight lines in the
directory's own README index. Recomputed with the change staged, by listing the
tracked paths and summing their sizes:

```sh
git ls-files audits | wc -l
git ls-files audits | tr '\n' '\0' | xargs -0 stat -f %z | awk '{s+=$1} END {print s}'
```

```
203
14882522
```

`docs/artifacts.md` now reads `14,882,522 tracked bytes / 203 files`, up from
`14,852,791 / 202` on the base commit, and `scripts/verify_ml_evidence.py`
compares that row against disk. *(The same one manifest has grown on each round:
the total was `14,873,520` at first close, `14,878,444` after the round-1
corrections and `14,882,522` after the round-2 ones.)*

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
- **A meeting-internal default is counted, not stopped, and it biases the
  primary outcome upward.** The meeting layer substitutes a placeholder turn or
  a marked SKIP ballot for a payload that fails schema validation, at a rate the
  lab accepts at about 1 in 50 calls. The instrument reports every such
  substitution per arm (`defaulted_turns`, `defaulted_votes`, by trigger, plus
  `units_with_defaults`), but it does not repair one: a defaulted ballot is a
  SKIP the voter did not choose, and because the privileged grader's "every
  naming ballot supported" is an `all()` over the ballots naming the ejected
  player, a defaulted ballot removes a constraint rather than failing it.
  `units_with_defaults` per arm is the bound on how many decisions that can
  touch, and a run whose arms differ materially on it is not a clean comparison.
- **The `degraded` split the manager keeps is not fully recoverable from a
  replay.** `DefaultedCall.degraded` is in-process only; the replay's
  `deadline_default` row carries no such field. The instrument recovers the
  opening half of it from the typed `opening_degraded_unsure` turn annotation,
  so a degraded opening is counted, but a degrade on any other turn kind is not
  separable from a full placeholder default.
- **The freeze manifest's `source_sha256` is not re-checked here.** The freeze's
  own regeneration test owns it; duplicating the check would stop a run for a
  reason that test states better.
- **Nothing is authorized to spend.** The manifest binds limits and this card
  authorizes no call. Executing the design needs a separate card carrying an
  explicit runner invocation, and the result of such a run would be a
  measurement, not an adoption.

### Review corrections, round 1 (2026-09-09)

Eighteen blocking findings from the independent verifiers and Codex; nine
distinct defects, eight of them in the code and one in this card's prose. Seven
of the eight sit in the two places this card asked to be trusted about — the
live-run gate and the stop path — and one pattern runs through them: the
instrument DESCRIBED limits it did not enforce. Source, tests, the manifest and
the registry row moved in `2dde0c91`; this subsection and the rest of the card
moved in the commit after it, which edits this Results section only. Every
command quoted here was run on `2dde0c91`.

**1 — the live client came from the shell, not from the authorization.**
`main()` validated `--provider featherless` and then built the client with a bare
`build_default_client()`, which reads `AILIBI_LLM_PROVIDER` and
`AILIBI_LLM_MEETING_MODEL`. An invocation labelled `featherless` therefore
reached whatever the shell named: with the variable unset it reached the fake
provider and wrote a report reading `provider: featherless`, `dry_run: False`;
with `anthropic` and a key in the environment it would have reached a metered
provider the manifest's own cost statement excludes. The live client is now
`build_authorized_client`'s — the provider and both model variables pinned to
the authorized values, with exactly one ambient value crossing over, the API key
— and `_InstrumentClient` refuses a RESPONSE whose `model` is not the authorized
one, on the call that returns it rather than in the report afterwards.

**2 — `--units` was honoured on the live path.** `main()` passed
`units=args.units` into `run_instrument`, which sliced `frozen.prefixes[:units]`,
and the gate inspected only provider, invocation and limits. `--provider
featherless --i-am-the-runner --units 1` therefore ran the one-unit pilot the
authorization card, this card and the manifest all refuse, against a set the rest
of which stays held out. `assert_live_run_is_authorized` now refuses any
non-`None` `units` for a live invocation, and `main` runs that gate BEFORE it
constructs a client.

**3 — `LiveRunInvocation.naming` authenticated a path suffix.** It compared the
last three components of the resolved path and looked for three substrings in the
text, and neither the recorded digest nor the path was re-checked at the
authorization boundary. A 41-byte file at any
`.../audits/deduction-candidate/execution-manifest.md` carrying only
`featherless Qwen/Qwen3.6-27B qwen3_6_27b` authorized a run, and a directly
constructed `LiveRunInvocation` skipped even that. `naming` now compares the full
resolved path against `repo_root / EXECUTION_MANIFEST_PATH`, and
`assert_live_run_is_authorized` re-resolves that path, re-hashes the file and
compares the invocation's digest and model against it — the dataclass's own
fields are no longer evidence for anything.

**4 — stops escaped without a partial run.** The abort wrapper caught four
classes. A provider transport failure left `run_instrument` as a raw
`RuntimeError`, a mid-run legacy body handle as a `HeldOutPrefixError`, and an
unreconciled spend or a wrong ballot count as a plain `InstrumentError` — none
carrying the `PartialRun` the stop rule and the manifest both promise. The
wrapper now catches `Exception`: every way a unit can fail is a stop that reports
its partial state, the class and message are copied into `reason` and the
original is chained, and `BaseException` is deliberately left alone so an
interrupt is not a run stop.

**5 — the truncation stop discarded the spend it claimed to retain.**
`_InstrumentClient.complete` raised `PerCallCapExceeded` before appending the
`CapturedCall` and before charging the model-work clock, so the one stop
condition this gate itself creates reported zero calls and zero tokens. Every
stop in the client now records the response first — it came back, so it was
spent. Fixing that surfaced the same defect one level up: `run_unit` drained the
client with `take()` before the handle and prompt-mirror checks, so a stop in
either handed the abort handler an empty client. Those checks now read
`client.calls`, and a unit is drained only once it has been accepted.

**6 — the manifest bound no sampling configuration.**
`audits/deduction-candidate/preregistration.md:113-115` requires it to; the
manifest named no temperature and the instrument constructed no `MeetingConfig`,
so the run inherited `meetings/manager.py:211,213` and a later edit to those
defaults would have moved a frozen design's sampling distribution without moving
the manifest. Turn 0.4 and vote 0.2 are now `AUTHORIZED_*` constants gathered
with the two caps into a frozen `AUTHORIZED_SAMPLING`, served through an explicit
`MeetingConfig` (carrying the HEADLESS deadlines, so an explicit config does not
opt this run into the interactive 30 s per-turn wall), recorded on every report,
refused by the live gate if moved, and pinned against the shipped values by a
test.

**7 — the advancement rule carried no acceptable tradeoff.** The preregistration
requires the manifest to bind "acceptable tradeoffs" and makes advancement
conditional on the predeclared wrongful-decision tradeoff; `DECISION_RULE` was p
and net alone, so a candidate that bought 10 supported-correct ejections while
converting reference-arm skips into wrongful crew ejections advanced.
`WRONGFUL_EJECTION_TRADEOFF` is now frozen beside the rest of the analysis and
before any held-out outcome exists: the candidate's net increase in wrongful crew
ejections may not exceed its net paired gain, one for one.
`PairedResult.meets_decision_rule` is the conjunction of all three conditions,
and the per-arm wrongful count is reported beside the role-correct one (31 per
arm on the dry run).

**8 — `verify_frozen_set` claimed three comparisons it did not make.** Its
docstring named the band, the roster and the tick budget; the body read `status`,
the clock, `num_players`, `num_impostors`, the digests and the skips, and called
`generate()` on the module defaults, so a manifest describing band 9000-9999, a
999-tick budget or 7 tasks per crewmate stayed green. All three are compared now,
against the generator's own frozen values, and the parsed band and roster are
what `generate()` is driven with.

**9 — "382 distinct step encodings" was not a count of anything.** 382 is the
needle total: the 50 prefixes' canonical encodings plus their 332 distinct step
encodings. "The frozen held-out set" above attributed it to steps alone; it now
carries 332, the arithmetic, and the command that prints both counts together
with the empty offender list.

#### Planted and perturbed failures, round 1

Each new gate was neutered in turn, its own test run, and the source restored:

| Gate removed or perturbed | Test that went red |
| --- | --- |
| `if units is not None:` → `if False:` | `TestLiveGate::test_a_live_invocation_carrying_a_unit_override_is_refused` |
| `if resolved != expected:` → `if False:` | `TestLiveGate::test_a_same_named_manifest_outside_the_repository_is_refused` |
| `if invocation.manifest_sha256 != committed:` → `if False:` | `TestLiveGate::test_a_hand_built_invocation_with_a_stale_digest_is_refused` |
| `if invocation.model != AUTHORIZED_MODEL:` → `if False:` | `TestLiveGate::test_a_hand_built_invocation_naming_another_model_is_refused` |
| `if sampling != AUTHORIZED_SAMPLING:` → `if False:` | `TestLiveGate::test_a_live_run_may_not_move_the_authorized_sampling` |
| the pinned environment reads `AILIBI_LLM_PROVIDER` from the ambient one | `TestAuthorizedClient::test_the_pinned_environment_ignores_the_ambient_provider_and_model` |
| the response-model check → `if False:` | `TestAuthorizedClient::test_a_response_from_another_model_stops_the_run` |
| the truncation stop raises before the call is recorded and the clock charged | `TestPerCallCaps::test_a_truncation_stop_retains_the_capped_calls_spend` |
| `except Exception as exc:` → `except InstrumentError as exc:` | `TestBudgetAndDeadline::test_a_provider_transport_failure_stops_the_run_with_partial_state` |
| the handle check drains the client with `take()` before it runs | `TestBudgetAndDeadline::test_a_mid_run_legacy_body_handle_stops_the_run_with_partial_state` |
| `if band != PREREGISTERED_BAND:` → `if False:` | `TestFrozenSet::test_a_moved_band_is_refused` |
| `if manifest.get("max_ticks") != MAX_TICKS:` → `if False:` | `TestFrozenSet::test_a_moved_tick_budget_is_refused` |
| `if parsed_roster != FROZEN_PREFIX_ROSTER:` → `if False:` | `TestFrozenSet::test_a_moved_task_count_is_refused` |
| `and meets_tradeoff` dropped from the decision rule | `TestPairedStatistics::test_a_candidate_that_buys_ejections_with_innocents_is_blocked` |
| `config=sampling.meeting_config(),` dropped from the runner call | `TestAuthorizedConstants::test_the_run_serves_the_authorized_meeting_config` |

All fifteen went red and the source was restored;
`.venv/bin/pytest tests/experiments/test_fresh_deduction_instrument.py -q` then
returned `113 passed` at `2dde0c91`.

#### Verification, round 1

Every row was run on `2dde0c91`, the commit that carries the source, the tests,
the manifest and the registry row; the commit after it edits this Results section
only, and `validate_task_docs` was re-run on it.

| Command | Result |
| --- | --- |
| `bash scripts/check.sh` | exit 0 — `Contracts: 4 kept, 0 broken`; `Success: no issues found in 473 source files`; `7378 passed, 20 skipped, 3 xfailed`; frontend `Test Files 19 passed`, `Tests 515 passed` |
| `.venv/bin/pytest tests/eval tests/experiments -q` | `1290 passed, 1 skipped in 135.03s` |
| `.venv/bin/pytest tests/experiments/test_fresh_deduction_instrument.py -q` | `113 passed` |
| `.venv/bin/python scripts/validate_task_docs.py` | `390 historical phase tasks and 390 prompts; 43 work cards` |
| `.venv/bin/python scripts/check_doc_facts.py` | `Doc facts verified` / `Front door verified` / `Budgets verified` |
| `.venv/bin/python scripts/verify_ml_evidence.py` | `checks: 60 \| OK 48 \| FAIL 0 \| ABSENT 7 \| INFO 5`; `every check passed` |
| `bash scripts/verify_samples.sh` | `All 50 samples verified clean.` for both sets |
| `scripts/build_sample_report.py --check` x 4 | all four `is consistent with its replays` |
| `.venv/bin/pytest tests/orchestrator/ --collect-only -q` | `583 tests collected` |
| `.venv/bin/python -m experiments.fresh_deduction_instrument --dry-run` | 100 units, 600 calls, `total_cost_usd` 0.0; per arm 50 ejections, 19 role-correct, 31 wrongful, 18 supported-correct; `sampling` recorded as `turn_temperature` 0.4 / `vote_temperature` 0.2 |

The dry run's per-arm counts and token totals are unchanged from the closing run
above, which is the point: the explicit `MeetingConfig` states the values the
meeting layer was already defaulting to, so binding them moved no byte.

`cd frontend && npm run e2e` was not run: no served DTO changed. The frontend
gate leg needed `npm ci` in this worktree before `scripts/check.sh` could reach
it — the first attempt exited 127 on `eslint: command not found` and is not a
result of this branch. This round changed no `tests/fixtures/` byte and no
`GENERATOR_SOURCES` file, so the freeze manifest still needs no
`dependency_restamps` entry; only `audits/deduction-candidate/execution-manifest.md`
moved, and its registry row moved with it.

No live provider call of any kind was made in this round. The two new gate tests
that touch a client factory (`TestAuthorizedClient`) assert refusals: each one
runs with no Featherless credential in the environment it is handed, so the
pinned environment stops before a client is constructed.

### Review corrections, round 2 (2026-09-09)

Seven blocking findings from the three verifiers; four distinct defects, two in
the code and two in this card's prose. Both code defects are the same shape as
round 1's pattern — the instrument DESCRIBED a limit it did not enforce — and
both were raised as Codex P1 comments that round 1 left undispositioned. Source,
tests, the manifest and the registry row moved in this round's implementation
commit; every command quoted here was run on that commit.

**1 — a meeting-internal default was neither stopped nor reported.** Codex P1
`3966328120` ("Report failure defaults separately from voluntary abstentions"),
raised on `ArmSummary` and unaddressed in round 1. The meeting layer does not
abort on a payload that fails schema validation: a turn falls back to a
placeholder and a ballot to a marked SKIP (`meetings/manager.py:1911`,
`:2260-2295`, the runaway class the lab accepts at about 1 in 50 calls), and the
orchestrator records each one as a `deadline_default`
`FailedCallReplayEntry` (`orchestrator/game.py:3055-3087`). `run_unit` read only
the `MeetingReplayEntry`, so those rows were discarded: a defaulted ballot
reached the report as one more `uncited` verdict, indistinguishable from a voter
who chose to abstain, and a defaulted TURN reached it as nothing at all. On the
committed tree a provider whose turn payloads all fail validation produced
`units 1, ejections 1, supported 3` — a fully complete, fully supported unit on
a meeting in which no model-authored turn existed.

Meanwhile `audits/deduction-candidate/execution-manifest.md` bound the
preregistration's "Missing or truncated attempts remain visible"
(`preregistration.md:112`) with "A missing or truncated attempt is a stop, and
the partial state is reported rather than replaced" — false of the code, and not
what the preregistration asks for either: it asks for visibility, and `:136`
asks for failed attempts to be retained.

Both halves are repaired, and in the direction the record supports. The
substitution is not made a stop: it is a shipped fail-soft with a committed
accepted rate, so on the ~600 authorized calls it would fire roughly a dozen
times and abort a fixed 50-unit paired sample for something the engine is
designed to do. Instead `count_defaulted_attempts` reads the unit's
`deadline_default` rows, classifies each by phase and trigger against the
producer's own wording, and `ArmSummary` now carries `defaulted_turns`,
`defaulted_votes`, `defaults_by_validation`, `defaults_by_deadline`,
`degraded_openings` (recovered from the typed `opening_degraded_unsure` turn
annotation, because the replay row carries no `degraded` field) and
`units_with_defaults`. A row whose phase and trigger cannot be classified IS a
stop — the producer's wording would have moved and the counts would no longer be
evidence. `STOP_RULE`, the manifest's Inputs row, its Measures table and a new
"Meeting-internal defaults: counted, not stopped" section now say exactly that,
including the direction of the bias: because the privileged grader's "every
naming ballot supported" is an `all()` over the ballots naming the ejected
player, a defaulted ballot removes a constraint rather than failing it, so the
primary outcome is biased UPWARD and `units_with_defaults` is the bound on how
many decisions that can touch. The card's Limitations carries the same statement.

**2 — the 4 h model-work window was charged only after a call returned.** Codex
P1 `3966328096`, also unaddressed in round 1. `_InstrumentClient.complete`
awaited the provider and charged `_ModelWorkClock` afterwards, so the window was
a one-call-granular limit; one call on the authorized provider is six sends at a
600 s timeout with exponential backoff (`llm/featherless_client.py:540,785`),
close to an hour in flight. A run at 3 h 59 m of model work could therefore spend
a fifth hour against an owner authorization of four, with only the separate 6 h
elapsed clock behind it — spend beyond an authorized limit, not a tuning choice.
Each await is now bounded by `_ModelWorkClock.remaining()`, mirroring
`orchestrator/run_limits.py:42-56`; `window.expired()` separates this stop from a
timeout the provider raised itself, so a transport timeout is not relabelled as a
limit; and the cut-off attempt's elapsed wall is charged to the clock and its
call recorded in the partial accounting (marked `aborted-in-flight`, with unknown
usage recorded as zero) before the stop is raised.

**3 — "112 tests … the round-1 corrections added 30".** Both numbers were wrong
and the card contradicted its own round-1 verification row, which already read
`113 passed`. The suite held 113 at `2dde0c91` (82 at first close, so round 1
added 31, not 30) and holds 127 at this round's commit. "What was built" now
carries 127 and the `--collect-only` command that prints it.

**4 — "No `audits/` byte outside this card's own new manifest moved".** False
when it was written: `audits/deduction-candidate/README.md`, the directory's own
index, gained eight lines in `87c4ef3d`, two commits BEFORE the `87dfd918` that
Verification section is pinned to, and the README was not in Expected scope
either. Both are corrected; `git diff --name-status 5682ea2a..HEAD -- audits/
tests/fixtures/` prints exactly the two paths now named.

#### Planted and perturbed failures, round 2

Each new gate was neutered in turn, its own test run, and the source restored:

| Gate removed or perturbed | Test that went red |
| --- | --- |
| `defaults=count_defaulted_attempts(…)` → `defaults=DefaultedAttempts()` | `TestMeetingDefaults::test_a_unit_whose_turns_all_defaulted_is_counted_not_hidden` |
| `if matched is None:` → `if False:` | `TestMeetingDefaults::test_a_default_the_counter_cannot_classify_stops_the_run` |
| `degraded_openings=sum(` → `degraded_openings=0 * sum(` | `TestMeetingDefaults::test_a_degraded_opening_is_counted_as_the_degrade_it_was` |
| `asyncio.timeout(self._work_clock.remaining())` → `asyncio.timeout(None)` | `TestModelWorkWindow::test_the_window_stops_during_the_call_that_exhausts_it` |
| `if not window.expired():` → `if False:` | `TestModelWorkWindow::test_a_providers_own_timeout_is_not_relabelled_as_the_window` |
| the aborted attempt's `CapturedCall` is not recorded | `TestModelWorkWindow::test_the_cut_off_attempt_is_charged_and_reported` |

All six went red and the source was restored;
`.venv/bin/pytest tests/experiments/test_fresh_deduction_instrument.py -q` then
returned `127 passed`.

The three defaulted-attempt cases are planted end to end rather than in a
fixture: a provider whose turn payloads never validate, one whose first ballot
payload is unparseable, and one whose opening parses but takes no position on
both attempts (the Task 10.6 unsure-degrade). The window's stop is planted on
WHEN it fires — a 0.2 s window against a call that stays in flight for 5 s — so
the assertion fails on the one-call-granular behaviour rather than passing on it.
The counter's regex is pinned against `orchestrator.game._deadline_default_message`
itself for both phases and both triggers, since the `deadline` trigger is
interactive-only and no headless test can reach it end to end.

#### Verification, round 2

Every row was run on `bfd5696b`, the commit that carries the source, the tests,
the manifest and the registry row; the commit after it edits this Results section
only, and `validate_task_docs` was re-run on it.

| Command | Result |
| --- | --- |
| `bash scripts/check.sh` | exit 0 — `Contracts: 4 kept, 0 broken`; `Success: no issues found in 473 source files`; `7392 passed, 20 skipped, 3 xfailed`; frontend `Test Files 19 passed`, `Tests 515 passed` |
| `.venv/bin/pytest tests/experiments tests/eval -q` | `1304 passed, 1 skipped in 183.07s` |
| `.venv/bin/pytest tests/experiments/test_fresh_deduction_instrument.py -q` | `127 passed` |
| `.venv/bin/python scripts/validate_task_docs.py` | `390 historical phase tasks and 390 prompts; 43 work cards` |
| `.venv/bin/python scripts/check_doc_facts.py` | `Doc facts verified` / `Front door verified` / `Budgets verified` |
| `.venv/bin/python scripts/verify_ml_evidence.py` | `checks: 60 \| OK 48 \| FAIL 0 \| ABSENT 7 \| INFO 5`; `every check passed` |
| `bash scripts/verify_samples.sh` | `All 50 samples verified clean.` for both sets |
| `scripts/build_sample_report.py --check` x 4 | all four `is consistent with its replays` |
| `.venv/bin/pytest tests/orchestrator/ --collect-only -q` | `583 tests collected` |
| `.venv/bin/python -m experiments.fresh_deduction_instrument --dry-run` | 100 units, 600 calls, `total_cost_usd` 0.0; per arm 50 ejections, 19 role-correct, 31 wrongful, 18 supported-correct, and 0 defaulted turns, 0 defaulted votes, 0 units carrying a default |

The dry run's per-arm counts and token totals are unchanged from both earlier
rounds, which is the point twice over: the new counts are zero on a provider
whose payloads all validate, and bounding the await moved no figure because no
dry-run call comes close to the window.

`cd frontend && npm run e2e` was not run: no served DTO changed. This round
changed no `tests/fixtures/` byte and no `GENERATOR_SOURCES` file, so the freeze
manifest still needs no `dependency_restamps` entry; only
`audits/deduction-candidate/execution-manifest.md` moved under `audits/`, and its
registry row moved with it.

No live provider call of any kind was made in this round. The three new
default-path providers and the two new clock providers are in-process fakes;
none of them constructs a client factory or reads a credential.
