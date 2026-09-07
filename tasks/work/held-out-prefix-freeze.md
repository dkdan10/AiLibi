# Freeze the held-out prefixes for the fresh-model deduction evaluation

**Status:** done

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

- [x] A new module `experiments/held_out_prefixes.py` defines a `HeldOutPrefix`
  model (seed, roster, max ticks, the scripted steps up to and including the
  report that opens the meeting, the report tick, the kill tick) that does not
  pin seed or roster as literals, and a deterministic generator
  `generate(band, roster)` that, for each seed drawn ascending from the
  preregistered band, builds a legal schedule on the canonical map for 4p1i
  with exactly one kill before the meeting (three living voters at meeting
  open) and a crewmate body report as the meeting trigger, then keeps the
  prefix only if the proof-free filter passes. Every unlisted action is an
  explicit wait, as in the development cases.
- [x] The preregistered band is seeds 3000 to 3999 drawn ascending; the first
  fifty prefixes that pass the filter form the set, and every skipped seed is
  recorded with its rejection reason. Seed 1 and the seven development
  definitions are excluded by construction and their definition hashes are
  asserted absent from the set.
- [x] The proof-free filter runs the prefix through `HeadlessGame` with the
  fake provider under temporal observation version 2 and rejects a prefix if
  any living crewmate's episodic memory holds an observed `saw_player` row with
  a `kill` or `vent` action at meeting open; the impostor's own kill record is
  not counted. A planted prefix with a witnessed kill fails the filter; a
  planted prefix with a witnessed vent fails the filter.
- [x] Under temporal version 2, no rendered meeting trigger line and no prefix
  step text matches `body-p-\d+-\d+`; the assertion is a test, and a planted
  legacy handle fails it.
- [x] The freeze artifact `audits/deduction-candidate/held-out/manifest.json`
  records the band, the roster, the generator's source sha256, the engine and
  observation source hashes it depends on, the fifty accepted seeds in order,
  the sha256 of each accepted prefix's canonical JSON, and the skipped seeds
  with reasons. No prefix bytes are committed: the runner regenerates them from
  the committed generator and the band and refuses to proceed if any hash
  differs from the manifest.
- [x] A test regenerates the set from the committed manifest's band and asserts
  every hash matches; a planted one-step change to the generator makes that
  test fail, which is the fail-loud a source edit after the freeze must
  produce.
- [x] `docs/artifacts.md`'s `audits/` inventory row is recomputed after the
  manifest is staged, and `scripts/verify_ml_evidence.py` passes without
  `--complete`.
- [x] Results states that the preparer session did not inspect any generated
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

## Results

**Preparer statement.** This session did not inspect any generated prefix beyond
the automated filter and hash computation, did not run any arm, and made no
provider call. No prefix bytes were printed, committed or pasted anywhere: the
only per-prefix values that left the generator were the seeds, the reason codes
and the sha256 digests recorded in the manifest.

### The set

`generate()` drew the preregistered band ascending and stopped at fifty. Of the
58 seeds it consumed, **50 were accepted and 8 were skipped**, every skip for the
same reason:

| reason code | skipped |
| --- | --- |
| `witnessed_kill` | 8 |

The first accepted seed is 3000 and the **last accepted seed is 3057**; the band
was not widened and 942 of its seeds were never drawn. No `witnessed_vent` skip
occurred, because the generator scripts no vent — the vent half of the filter is
proved by the planted case below, not by a band seed. The filter is not
decorative on real seeds either: 8/58 band seeds and 5/50 of the out-of-band
debugging seeds were removed for a living crewmate's firsthand kill row.

`audits/deduction-candidate/held-out/manifest.json` is the freeze artifact —
**sha256 `75de872360ae06aeaa0a80f22efbdfda20b2210db66cd8f3fbec6ebfd58740f7`**,
11,524 bytes. It records the band, the roster, the tick budget, the temporal
version, the filter's stated environment, the canonical-JSON recipe, the sha256
of 22 generator/engine/observation source files, the fifty accepted seeds with
their prefix digests in band order, the eight skips with reason codes, the seven
development definitions' digests with `absent_from_accepted`, and a `status` of
`held_out` whose note says a later flip to `development` is recorded in this file
rather than by deleting it. It contains **no prefix bytes**; a test asserts the
tokens `"steps"`, `"to_room"`, `"actor"` and `"payload"` never appear in it and
that no accepted prefix's canonical JSON is a substring of it.

### Design decisions

The filter runs each prefix through `HeadlessGame` with `meeting_runner=None`
and `replay_path=None`. The loop therefore halts at `MEETING_PHASE_REACHED` —
after the meeting tick's event observations have reached every agent, before any
meeting exists — so **no provider object is constructed at all**, which is
stricter than the fake provider the acceptance item names; the filter's stated
environment additionally pins `AILIBI_LLM_PROVIDER=fake` and
`AILIBI_TEMPORAL_OBSERVATIONS=2` rather than inheriting the shell, so a
developer's environment cannot move which prefixes pass. Nothing is written to
disk: the observation audit is routed to the null device.

One rejection is deliberately not counted. A player killed part-way through a
tick has already submitted an action for that tick, and the engine rejects it as
"player is dead" whenever the killer's id sorts ahead of the victim's in the
tick's action order (`orchestrator/action_ordering.py` sorts by actor). That is
the engine resolving a death, not a defect in the schedule, so the victim's own
action on its own death tick is exempt; every other `ActionRejectedEvent` is a
`engine_rejected_action` skip, and a planted two-room move proves that gate
fires.

Both uninvolved crewmates wander on seeded legal random walks that may take them
into the kill room on the kill tick. That is what makes the proof-free filter
load-bearing rather than a formality, and it is where all eight band skips came
from.

The manifest's `source_sha256` covers `orchestrator/game.py`, the engine and the
observation layer as well as the generator, and the regeneration test asserts
those digests against the working tree. An unrelated edit to one of those files
therefore turns this test red. That is intended — after the freeze, a change to
the source the frozen inputs are derived from must be noticed before the run, not
after it — but it is a real coupling, and the remedy is a decision, not a
refresh: if regeneration still produces the same fifty digests the set is
unchanged and the manifest's dependency digests may be restamped; if it does not,
the set is no longer frozen and a new band belongs under a new card.

### Fail-loud evidence

Both halves of the freeze were proved by planting and reverting; neither plant is
committed.

1. **A one-step generator change.** Moving the impostor's post-kill departure
   from `kill_tick + 1` to `kill_tick + 2` — one step in every schedule — turned
   `test_the_committed_manifest_regenerates_from_its_own_band` red at the first
   accepted seed: `{'seed': 3000, 'sha256': '1482ce81…'} != {'seed': 3000,
   'sha256': 'ab053eef…'}`. Reverted; `14 passed`.
2. **A non-behavioural generator edit.** Appending a comment line left every
   prefix digest identical but moved the module's own digest, and the same test
   went red on `rebuilt["source_sha256"] != manifest["source_sha256"]`
   (`experiments/held_out_prefixes.py`: `8ab1186e…` vs the frozen `9c6ec3ab…`).
   Reverted; `14 passed`.

The planted adverse cases that live in the suite: a witnessed kill (a second
crewmate standing in ADMIN when the kill lands) is rejected `witnessed_kill`; a
witnessed vent (an unwitnessed kill, then the killer dropping into `ADMIN_VENT`
in front of a crewmate) is rejected `witnessed_vent`; an illegal two-room move is
rejected `engine_rejected_action`; and the legacy body handle is proved by
rendering the SAME meeting both ways — `_build_meeting_trigger` under temporal v2
yields `p-2 reported body body-p-1 at tick 7`, which the assertion accepts, while
the pre-v2 renderer yields `body-p-1-4`, which
`assert_no_legacy_body_handles` refuses. An accepted prefix additionally reports
`killer_own_kill_records == 1` beside `living_crew_proof_rows == 0`, so the
exclusion of the killer's own record is visible in the filter's own output rather
than inferred from an absence.

### Seeds inspected outside the band

Debugging used seeds **1 to 50** and **9001 to 9002**, all outside the
preregistered 3000–3999 band. Seed 1 is the seed the seven committed development
cases already use and every planted case in the test module is built on it, so
it was development data before this card. No seed in the band was ever printed,
opened or reasoned about beyond its reason code and digest.

### Gate

Run in order on this branch:

| check | result |
| --- | --- |
| `uv run pytest tests/experiments/test_held_out_prefixes.py -q` | 14 passed in 1.93 s |
| `uv run python scripts/validate_task_docs.py` | 390 phase tasks, 390 prompts, 43 work cards |
| `uv run python scripts/check_doc_facts.py` | doc facts, front door, ml-program and budgets verified |
| `uv run python scripts/verify_ml_evidence.py` (offline, never `--complete`) | checks 60, OK 48, FAIL 0, ABSENT 7, INFO 5 |
| `uv run pytest tests/scripts/test_verify_ml_evidence.py -q` | 80 passed in 81.85 s |
| `bash scripts/check.sh` | exit 0: ruff, lint-imports, task docs, `generate_prompts --check`, mypy over 469 source files, **7,187 passed / 20 skipped / 3 xfailed** in 197.14 s, then the frontend leg — lint, three `tsc --noEmit` passes, 514 vitest tests over 19 files, and a clean production build |

`docs/artifacts.md`'s `audits/` inventory row moved from
`14,838,764 tracked bytes / 201 files` to `14,850,288 tracked bytes / 202 files`,
recomputed from `git ls-files audits/` with the manifest staged.

### Limitations

A green gate here says the held-out set is legal, proof-free, deterministic and
frozen. It says nothing about whether any model can reason from these prefixes:
no arm ran and no model saw one. The set's usefulness is exercised by the
instrument card's run, and the owner's merge of this pull request — not this
card's completion — is the freeze.
