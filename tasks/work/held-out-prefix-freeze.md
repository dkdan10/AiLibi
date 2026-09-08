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

- [x] Review correction: the card, the module comment and the pull request
  describe what the report-tick drop actually did to the set. It is NOT true that
  a move drawn for the report tick is never executed, nor that only the hashed
  schedule moved: an actor whose id sorts BEFORE the reporter's has its
  report-tick action applied before the report flips the phase, so of the 61
  steps the drop removed from the fifty accepted prefixes, 26 were phantoms the
  engine never resolved and 35 were moves it ran. Every draw, role, kill room,
  kill tick, route and walk is unchanged and every seed's world is byte-identical
  through `report_tick - 1` (0 of 50 pre-report event streams differ), but 28 of
  the 50 prefixes now open the meeting with a different living-player room
  assignment and a different episodic memory. That is deliberate — a frozen
  scenario must not depend on the actor-sort tiebreak at the report tick — and it
  is now stated as such wherever the drop is described. The executed half of the
  behaviour is held by
  `test_a_report_tick_step_the_engine_does_resolve_passes_the_seam`.
- [x] Review correction: the certifying seam compares the hashed schedule with
  what the ENGINE resolved, not with what the scripted agent served. Every hashed
  `(tick, actor)` pair must appear among the events the tick function emitted for
  a resolved action — the executed action's own event, or the
  `ActionRejectedEvent` the loop appends when the engine refuses one — and
  `_replay_prefix` raises `HeldOutPrefixError` with counts only otherwise. Proved
  by `test_a_step_the_engine_never_resolves_never_reaches_a_digest` and by
  `test_a_step_the_meeting_tick_discards_never_reaches_a_digest`, whose planted
  move is discarded by the opening meeting rather than rejected, and bounded from
  the other side by
  `test_a_report_tick_step_the_engine_does_resolve_passes_the_seam`.
- [x] Review correction: nobody but the reporter is scheduled on the report tick.
  The meeting interrupts that tick, so whether an action drawn for it runs depends
  on how its actor's id sorts against the reporter's, and a hashed schedule must
  not depend on that tiebreak: `build_prefix` draws the walks exactly as before —
  same calls, same `last_tick`, same RNG consumption — and DROPS the drawn step
  for EVERY non-reporter, the ones the engine would have executed included. Proved
  by `test_the_generator_scripts_nobody_but_the_reporter_on_the_report_tick`, and
  bounded by `test_a_report_tick_step_the_engine_does_resolve_passes_the_seam`,
  which shows an earlier-sorting actor's report-tick move IS executed and does
  pass the seam. The set kept the same fifty accepted seeds, the same eight skips
  and the same last accepted seed, and no filter verdict or rendered trigger line
  moved; it did not keep the same worlds, and the item above states what did move.
- [x] Review correction: a seed whose own draw overruns the tick budget is a
  recorded `schedule_exceeds_tick_budget` skip rather than an abort of the whole
  draw, and `tally_reasons` returns its totals as fields of a `ReasonTally`
  beside the reason histogram, so no future reason code can overwrite a total.
  Proved by `test_a_seed_whose_schedule_overruns_the_budget_is_skipped_not_a_stop`,
  `test_an_unauthorized_roster_still_raises_rather_than_becoming_a_skip` and
  `test_the_tally_counts_an_out_of_band_range_without_opening_a_prefix`.
- [x] Review correction: `evaluate_prefix` certifies a digest only
  for a schedule the replay honoured IN FULL. The duplicate gate below closed
  one route to that defect; three more stayed open — a step past `report_tick`,
  a step past `max_ticks`, and a step addressed to a player the roster never
  seats or that the loop stopped asking because it was dead. The first two are
  refused by a second `model_validator`; the third cannot be judged from the
  schedule alone, so `_replay_prefix` compares the schedule against the replay
  and raises `HeldOutPrefixError` on a shortfall. Proved by
  `test_a_step_outside_the_replayed_window_is_refused` and
  `test_a_step_the_engine_never_resolves_never_reaches_a_digest`. The comparison
  this pass wrote counted what the agent SERVED, which the round-3 item above
  replaced with what the engine resolved.
- [x] Review correction: the filter environment claim names the
  mechanism that actually enforces it. `filter_environment()` BUILDS its mapping
  from this module's pinned constants on every call, so prefix selection depends
  on no stored state a same-process caller can reach, and the returned
  `MappingProxyType` refuses mutation; the card, the module and the pull request
  all state plainly that a caller which REBINDS a module attribute is rewriting
  the module, which the manifest's `filter_environment` and `source_sha256`
  catch rather than any in-module guard. Proved by
  `test_the_filter_environment_is_built_per_use_and_refuses_mutation`.
- [x] Review correction: `HeldOutPrefix` rejects a second step for the same
  `(tick, actor)`, so a digest can never bind a schedule the replay would only
  partly honour (`_PrefixAgent` keys its script by tick and would have kept the
  last action silently). Proved by
  `test_a_duplicate_action_for_one_actor_and_tick_is_refused`, which appends a
  duplicate step to a valid seed-1 prefix and asserts both the constructor and
  `model_validate` raise.
- [x] Review correction: the card's out-of-band rejection rate is reproducible.
  `tally_reasons` plus `python -m experiments.held_out_prefixes --tally FIRST
  LAST` prints the seeds walked, the accepted count and the reason-code
  histogram and nothing else, and REFUSES any range touching the preregistered
  band. Proved by `test_the_tally_counts_an_out_of_band_range_without_opening_a_prefix`
  and `test_the_tally_refuses_to_probe_the_preregistered_band`; the command and
  its output are in Results.
- [x] Review correction: Results cites the `docs/architecture.md` sections this
  generator and filter rest on, plus the preregistration that binds the held-out
  discipline, under the heading "Architecture and design references".
- [x] Review correction: the filter's environment is stated rather than
  inherited from the shell, and is not a mutable module-level dict. Superseded
  in wording and mechanism by the verification-round correction above: the
  `MappingProxyType` this pass introduced blocks in-place mutation only, which
  is less than the "a same-process caller cannot move it" the item first
  claimed.
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
debugging seeds were removed for a living crewmate's firsthand kill row. The
band figures are the manifest's own `skipped_reason_counts` and
`last_accepted_seed`; the out-of-band figure reproduces offline, aggregates
only, from

```text
$ uv run python -m experiments.held_out_prefixes --tally 1 50
seeds 50
accepted 45
witnessed_kill 5
```

`tally_reasons` evaluates each seed exactly as `generate()` does and returns a
`ReasonTally` whose `seeds` and `accepted` totals are fields beside the reason
histogram, which is what the command prints. It refuses any range that intersects
seeds 3000–3999, so the same command cannot be turned on the held-out set: an
aggregate count over band seeds is still a probe, and a narrow enough range would
be a per-seed read.

`audits/deduction-candidate/held-out/manifest.json` is the freeze artifact —
**sha256 `21190ab58f940a4d0085aa6a72118a1b5f8a14e2b62aa45323246fd3adc65946`**,
11,524 bytes. The set is not frozen until the owner merges this pull request, and
four correction rounds moved the file before then; each dated subsection below
names the digest it left behind, and only the value above describes the file as
it now stands. It records the band, the roster, the tick budget, the temporal
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
from. Their wander, and the impostor's, stop being HASHED at the report tick: the
meeting interrupts that tick, so whether an action ordered there runs at all
depends on how the actor's id sorts against the reporter's, and a hashed schedule
must not depend on that tiebreak. The walks are still drawn to the report tick —
the draws are what the seed determines — and the drawn step for that one tick is
discarded for every non-reporter, the ones the engine would have EXECUTED
included, so the generator remains a pure function of the seed and the reporter is
the only actor scheduled on the tick that ends the prefix. Dropping the executed
ones is a change to the prefixes' content, not only to their hashes, and the
round-3 and round-4 subsections below record its size across the set.

The manifest's `source_sha256` covers `orchestrator/game.py`, the engine and the
observation layer as well as the generator, and the regeneration test asserts
those digests against the working tree. An unrelated edit to one of those files
therefore turns this test red. That is intended — after the freeze, a change to
the source the frozen inputs are derived from must be noticed before the run, not
after it — but it is a real coupling, and the remedy is a decision, not a
refresh: if regeneration still produces the same fifty digests the set is
unchanged and the manifest's dependency digests may be restamped; if it does not,
the set is no longer frozen and a new band belongs under a new card.

### Architecture and design references

The generator and its filter rest on four already-documented properties, and
add none of their own.

*Determinism and the substrate ladder* (`docs/architecture.md`) states that a
seed, configuration, agent factory and provider responses determine replay bytes
within their recorded runtime scope, and that recordings and manifests stamp the
substrate while readers refuse incompatible settings. That is exactly the
guarantee the freeze converts into a hash: every choice this generator makes is
drawn from `random.Random` seeded from the prefix seed alone, and the filter
stamps its own substrate rather than inheriting a shell, through the same
`substrate_flag_snapshot` the section describes.

*Enforced boundaries* and *Layering* are what let the filter read a crewmate's
knowledge without reading engine truth. Agents may not import engine, and the
firewall delivers audited packets; the filter therefore asks each agent's own
episodic memory — filled through the real perception seam by `ingest_packet` —
whether a living crewmate holds an observed `saw_player` row, instead of asking
the engine who was in the room. A proof-free claim made from engine state would
not be a claim about what the crew can prove.

*Observation timing and public identities* is what the `body-p-\d+-\d+`
assertion is about: it records that packets use victim-derived body handles and
that default-OFF `temporal_observations` adds event-local movement entitlement
and source-tick delivery before meetings, while legacy-OFF opening prompts still
expose internal body IDs. The prefixes are generated and filtered under temporal
version 2 for that reason, and the assertion runs over `_build_meeting_trigger`'s
real output, so it tests the renderer of record rather than a copy of its format
string.

The held-out discipline itself is not an architecture property but a
preregistered commitment: `audits/deduction-candidate/preregistration.md`
("Use the known seven cases only for development/operational checks") requires a
separate reviewer to prepare and freeze held-out schedules before the candidate
is evaluated on them, and converts any inspected or fix-informing input into
development data. The band, the preparer/runner split, the hashes-only manifest
and the tally's refusal to touch the band all follow from that paragraph.

### Fail-loud evidence

Both halves of the freeze were proved by planting and reverting; neither plant is
committed.

1. **A one-step generator change.** Moving the impostor's post-kill departure
   from `kill_tick + 1` to `kill_tick + 2` — one step in every schedule — turned
   `test_the_committed_manifest_regenerates_from_its_own_band` red at the first
   accepted seed: `{'seed': 3000, 'sha256': '1482ce81…'} != {'seed': 3000,
   'sha256': 'ab053eef…'}`. Reverted; `14 passed`. `1482ce81…` is the planted
   digest and is committed nowhere, by design; `ab053eef…` was seed 3000's frozen
   digest at the time of the plant and stayed so through `3eb49dfc`. The round-3
   correction below rebuilt every schedule that carried a phantom report-tick
   step, so seed 3000's digest now reads `ab8db76d…`.
2. **A non-behavioural generator edit.** Appending a comment line left every
   prefix digest identical but moved the module's own digest, and the same test
   went red on `rebuilt["source_sha256"] != manifest["source_sha256"]`
   (`experiments/held_out_prefixes.py`: `8ab1186e…`, the planted value, committed
   nowhere, versus `9c6ec3ab…`, the entry frozen at the time of this plant).
   Reverted; `14 passed`. Four correction passes have since re-stamped that one
   entry, and the chain of committed values is `9c6ec3ab…` at `f9d02ad2` and
   `2daa5612`, then `0b94fec1…` at `92bec106`, then `89d0220e…` at `3eb49dfc`,
   then `1c8ce570…` at `27e6d952`, then `9bc18db8…` at the head of this branch.

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

### Review corrections (2026-09-07)

Codex left four P1 inline comments on pull request #438. All four were assessed
valid and fixed on the branch; none of them moved an accepted digest or a skip.

1. **Duplicate per-tick actions were silently dropped**
   (`experiments/held_out_prefixes.py`). `_PrefixAgent` keys its script by tick,
   so two steps for the same actor and tick collapsed to the last one, while
   `canonical_prefix_json` and `prefix_sha256` still bound both — `evaluate_prefix`
   could have certified a digest for a schedule the replay only partly honoured.
   `HeldOutPrefix` now carries a `model_validator(mode="after")` that raises on a
   repeated `(tick, actor)` pair, and `_PrefixAgent` says in a comment that its
   dict is safe *because* the model validated it. Planted case:
   `test_a_duplicate_action_for_one_actor_and_tick_is_refused` appends a duplicate
   step to a valid seed-1 prefix and asserts both `HeldOutPrefix(...)` and
   `HeldOutPrefix.model_validate` raise. Generated prefixes never contained one —
   each actor's scripted ticks are disjoint by construction — which is why no
   digest moved.
2. **The 5/50 out-of-band figure had no reproducing command** (this card). Added
   `tally_reasons(first_seed, last_seed, roster)` and the
   `python -m experiments.held_out_prefixes --tally FIRST LAST` subcommand, which
   evaluate a seed range exactly as `generate()` does and print only the seeds
   walked, the accepted count and the reason-code histogram. The command and its
   verbatim output are in "The set" above; the figure was correct and is
   unchanged. The tally raises `HeldOutPrefixError` on any range intersecting
   seeds 3000–3999, so it cannot be used to probe the frozen set
   (`test_the_tally_refuses_to_probe_the_preregistered_band` covers a
   single-seed, a straddling-low, a straddling-high and an enclosing range, plus
   a backwards range); `test_the_tally_counts_an_out_of_band_range_without_opening_a_prefix`
   checks the shape of the tally on seeds 9001–9002. No band seed was walked.
   Confirmed while implementing this: no seed in 1–50 raises out of
   `build_prefix`, so `generate()` needs no new skip path and none was added.
3. **Results had no architecture or design reference** (this card). Added
   "Architecture and design references" above, naming the `docs/architecture.md`
   sections the generator, the filter and the body-handle assertion rest on, and
   the preregistration paragraph the held-out discipline comes from.
4. **The filter environment was a mutable module-level dict**
   (`experiments/held_out_prefixes.py`). `_FILTER_ENV` was wrapped in a
   `types.MappingProxyType`. **This pass overstated what that buys** — the
   accompanying claim, "a same-process caller cannot move the substrate flags
   the set was screened under", is false: a proxy blocks item assignment on the
   object, not a rebinding of the module attribute both consumers read at call
   time. The verification round refuted it in four lines and the wording, the
   mechanism and the planted case were all replaced; see "Verification-round
   corrections" below.

**Manifest impact.** Regenerating with
`.venv/bin/python -m experiments.held_out_prefixes` changed exactly one line: the
`source_sha256` entry for `experiments/held_out_prefixes.py`, from `9c6ec3ab…` to
`0b94fec1…`. Verified field by field with `jq` — `accepted`, `skipped`,
`skipped_reason_counts`, `last_accepted_seed`, `band`, `roster`,
`filter_environment`, `development_definitions`, `body_handle_assertion`,
`status`, `status_note`, `card`, `max_ticks`,
`temporal_observation_version`, `canonical_json`, `version`, `prefix_bytes` and
`filter` are byte-identical, and the other twenty-one `source_sha256` entries are
unchanged. The file's byte count is unchanged at 11,524, so
`docs/artifacts.md`'s `audits/` inventory row still reads
`14,850,288 tracked bytes / 202 files` and was not touched. The manifest's own
sha256 moved from
`75de872360ae06aeaa0a80f22efbdfda20b2210db66cd8f3fbec6ebfd58740f7` — the digest
at the first push, commit `f9d02ad2`, unchanged by the docs-only `2daa5612` — to
`c060f3cac7fba8546c160f634e5788a052663458ceefd51e1fd2c366cd38b78e` at commit
`92bec106`. Both are superseded pre-freeze revisions; the digest of the file as
it now stands is in "The set" above.

**Preparer statement, restated for this pass.** No prefix from the preregistered
band was printed, opened or reasoned about during the corrections. The tally was
run on seeds 1–50 and 9001–9002 only, both already recorded above as out-of-band
development seeds; no seed outside that existing debugging set was walked, and
no arm ran and no provider call was made.

**Gate after the corrections**, run in order on this branch:

| check | result |
| --- | --- |
| `.venv/bin/pytest tests/experiments/test_held_out_prefixes.py -q` | 18 passed in 1.98 s (4 new: the duplicate step, the frozen filter environment, and the tally's shape and its band refusal) |
| `.venv/bin/python scripts/validate_task_docs.py` | 390 phase tasks, 390 prompts, 43 work cards |
| `.venv/bin/python scripts/check_doc_facts.py` | doc facts, front door, ml-program and budgets verified |
| `.venv/bin/python scripts/verify_ml_evidence.py` (offline, never `--complete`) | checks 60, OK 48, FAIL 0, ABSENT 7, INFO 5 |
| `.venv/bin/pytest tests/scripts/test_verify_ml_evidence.py -q` | 80 passed in 80.52 s |
| `bash scripts/check.sh` | exit 0: ruff (498 files formatted), 4 import-linter contracts kept, task docs, `generate_prompts --check` (390 in sync), mypy over 469 source files, **7,191 passed / 20 skipped / 3 xfailed** in 261.07 s, then the frontend leg — lint, three `tsc --noEmit` passes, 514 vitest tests over 19 files, and a clean production build |

### Verification-round corrections (2026-09-07)

A verification round over the corrections above found two of them incomplete.
Both are repaired here; neither repair moved an accepted digest or a skip.

1. **The duplicate gate closed one route to the defect, not the defect**
   (`experiments/held_out_prefixes.py`). Codex's comment named the semantic
   failure — "`evaluate_prefix` can therefore certify a digest whose replay omits
   part of the hashed schedule" — and the duplicate `(tick, actor)` gate closed
   only the route Codex happened to point at. Three others stayed open through
   the public API: a step past `report_tick` (the loop halts at
   `MEETING_PHASE_REACHED`, so `decide` is never asked for that tick), a step
   past `max_ticks` (the scheduler stops first), and a step addressed to a player
   the roster never seats (no `_PrefixAgent` exists for that id, so
   `_PrefixAgent`'s comprehension filters it out) or to a player the loop stopped
   asking because it was dead. In every case `prefix_sha256` moved while the
   replay executed less than the digest bound, and `evaluate_prefix` returned
   `reason=None`. The comment added in the previous pass — that keying the script
   by tick "can never drop a hashed action" — was therefore false as written for
   the unseated-actor case, and it has been narrowed to what the model actually
   guarantees.

   The repair is at both seams. `HeldOutPrefix` gained a second
   `model_validator(mode="after")`, `_every_step_falls_inside_the_replayed_window`,
   which refuses `report_tick` outside `0..max_ticks-1` and any step outside
   `0..report_tick`; those two shapes are visible in the schedule alone.
   Membership and liveness are not, so `_PrefixAgent` recorded the scripted ticks
   it actually served and `_replay_prefix` raised `HeldOutPrefixError` when the
   served total fell short of `len(prefix.steps)` — before a `PrefixEvaluation`
   exists, so no partly executed schedule can reach a digest. The error message
   carries counts only, never a step. Planted cases:
   `test_a_step_outside_the_replayed_window_is_refused` (a step at
   `report_tick + 1`, a step at tick 99, and a `report_tick` equal to
   `max_ticks`, each through both the constructor and `model_validate`) and
   `test_a_step_the_replay_never_executes_never_reaches_a_digest` (an unseated
   `p-9` and a step for the victim two ticks after its death, each asserted to
   move `prefix_sha256` and then to raise). Both plants are built on seed 1.
   **Superseded in mechanism by round 3 below**: a served count says the agent
   handed the loop an action, not that the engine ran it, and the report tick's
   opening meeting discards what is ordered after the reporter. The comparison
   now runs against the engine's own events, and that test is renamed
   `test_a_step_the_engine_never_resolves_never_reaches_a_digest`.

2. **The `MappingProxyType` claim was stronger than the mechanism**
   (`experiments/held_out_prefixes.py`, and Acceptance and Results here). A proxy
   blocks item assignment on the object; it does not stop
   `m._FILTER_ENV = {...}`, and both consumers read the module global at call
   time, so a four-line same-process rebinding moved the four live meeting
   toggles the set was screened under and `build_manifest` would have stamped the
   moved dict into the manifest as the frozen environment. The previous pass's
   planted case asserted only the `TypeError`, so it did not cover the defect its
   own name claimed.

   Codex's other sanctioned option is taken instead: the environment is
   CONSTRUCTED inside the owning operation. `_FILTER_ENV` is gone; a
   `filter_environment()` function builds the mapping from this module's pinned
   constants (`_FILTER_PROVIDER`, `TEMPORAL_OBSERVATION_VERSION`) on every call,
   and `_replay_prefix` and `build_manifest` call it. Prefix selection therefore
   depends on no stored state a same-process caller can reach, and the returned
   proxy still refuses mutation. The limitation is now stated rather than
   overclaimed, in the function's own docstring, in Acceptance and here: a caller
   that REBINDS a module attribute is rewriting the module, and no in-module
   mechanism prevents that — what catches it is the manifest, which records both
   `filter_environment` and the module's own bytes in `source_sha256`, and
   `test_the_committed_manifest_regenerates_from_its_own_band`, which compares
   both against the committed record. Planted case:
   `test_the_filter_environment_is_built_per_use_and_refuses_mutation` asserts
   the mapping refuses item assignment AND that a second call returns a different
   object, which is what makes a held reference useless to a caller.

**Fail-loud for the three new gates.** Each was neutered in turn and the suite
run; each was reverted (`shasum -a 256 experiments/held_out_prefixes.py` back to
`89d0220e15d491210b58a1f4231afeddc05a3323f76732eb782ea7bc2f09af94`, `git status
--porcelain` clean for the module). This pass first wrote that each neuter turned
"exactly its own planted case" red, which does not reproduce: every edit to the
module also moves its `source_sha256` entry, so
`test_the_committed_manifest_regenerates_from_its_own_band` goes red beside the
planted case, by design. The table below is the reproducible result, re-run at
the head of this branch against the round-3 gates:

| neutered | red |
| --- | --- |
| the `_replay_prefix` engine-resolved comparison (`if False:`) | `test_a_step_the_engine_never_resolves_never_reaches_a_digest`, `test_a_step_the_meeting_tick_discards_never_reaches_a_digest`, and `test_the_committed_manifest_regenerates_from_its_own_band` through `source_sha256` |
| `_every_step_falls_inside_the_replayed_window` (early `return self`) | `test_a_step_outside_the_replayed_window_is_refused`, and `test_the_committed_manifest_regenerates_from_its_own_band` through `source_sha256` |
| `filter_environment` returning a stored module mapping | `test_the_filter_environment_is_built_per_use_and_refuses_mutation`, and `test_the_committed_manifest_regenerates_from_its_own_band` through `source_sha256` |

**Manifest impact of this pass.** Regenerating with
`.venv/bin/python -m experiments.held_out_prefixes` again changed exactly one
line — the `source_sha256` entry for `experiments/held_out_prefixes.py`, from
`0b94fec1…` to `89d0220e…`. `git diff` on the manifest reports one insertion and
one deletion; `accepted`, `skipped`, `skipped_reason_counts`,
`last_accepted_seed`, `band`, `roster`, `filter_environment`,
`development_definitions`, `body_handle_assertion`, `status`, `status_note`,
`card`, `max_ticks`, `temporal_observation_version`, `canonical_json`, `version`,
`prefix_bytes` and `filter` are untouched, as are the other twenty-one
`source_sha256` entries. `test_the_committed_manifest_regenerates_from_its_own_band`
asserted `accepted` and `skipped` equal BEFORE the regeneration and failed on
`source_sha256` alone, which is the direct evidence that the new gates moved
neither the set nor a skip: `generate()` walked the band under them and produced
the same fifty digests and the same eight skips. The file's byte count is
unchanged at 11,524 (a sha256 entry is 64 hex characters either way), so
`docs/artifacts.md`'s `audits/` inventory row still reads
`14,850,288 tracked bytes / 202 files` and was not touched. The manifest's own
sha256 moved from `c060f3ca…` to
`3089c2d7361c70e6fb49981b374e0b9d167111bbf98b4b901055251b77964e9b` at commit
`3eb49dfc` — a superseded pre-freeze revision; round 3 below moved it again.

**Out-of-band tally, re-run under the new gates** — unchanged, which is the check
that the certifying seam does not reject legal generated schedules:

```text
$ uv run python -m experiments.held_out_prefixes --tally 1 50
seeds 50
accepted 45
witnessed_kill 5
```

**Preparer statement, restated for this pass.** No prefix from the preregistered
band was printed, opened or reasoned about during these corrections. Every
planted case and every probe used seed 1 or seeds 9001–9002; the tally used
seeds 1–50. All are outside the band and were already recorded above as
development seeds. No arm ran, no provider call was made, and the only band
values that appear anywhere are the seeds, reason codes and digests the manifest
already records.

**Gate after the verification-round corrections**, run in order on this branch:

| check | result |
| --- | --- |
| `.venv/bin/pytest tests/experiments/test_held_out_prefixes.py -q` | 20 passed in 1.99 s (2 new: the replayed-window refusal and the unexecuted-step refusal; the filter-environment case was rewritten, not added) |
| `.venv/bin/python scripts/validate_task_docs.py` | 390 phase tasks, 390 prompts, 43 work cards |
| `.venv/bin/python scripts/check_doc_facts.py` | doc facts, front door, ml-program and budgets verified |
| `.venv/bin/python scripts/verify_ml_evidence.py` (offline, never `--complete`) | checks 60, OK 48, FAIL 0, ABSENT 7, INFO 5 |
| `.venv/bin/pytest tests/scripts/test_verify_ml_evidence.py -q` | 80 passed |
| `bash scripts/check.sh` | exit 0: ruff (498 files formatted), 4 import-linter contracts kept, task docs, `generate_prompts --check` (390 in sync), mypy over 469 source files, **7,193 passed / 20 skipped / 3 xfailed** in 207.96 s, then the frontend leg — lint, three `tsc --noEmit` passes, 514 vitest tests over 19 files, and a clean production build |

### Review corrections, round 3 (2026-09-07)

A second verification round over the corrections above found the certifying seam
still open, and four documentation statements that do not reproduce. This is the
first pass that MOVED the set: the schedules changed, so forty-five of the fifty
accepted digests changed with them. The set is not frozen until the owner merges
this pull request, so a pre-freeze digest move is a correction, not a break of
the freeze. **This pass then described its own set change wrongly** — it said the
worlds were untouched and only the hashes moved, which does not reproduce; the
round-4 subsection below measures what actually moved and every statement of it in
this card, the module and the pull request now says that instead.

1. **The seam counted what the agent SERVED, not what the engine EXECUTED**
   (`experiments/held_out_prefixes.py`). `_PrefixAgent.decide` returning an
   action says only that the loop asked and the agent answered.
   `advance_tick` returns the instant a report puts the world in `MEETING`
   (`engine/tick.py`, step 1), and the tick's actions are ordered by actor
   (`orchestrator/action_ordering.py`), so an action from an actor whose id sorts
   AFTER the reporter's is discarded on the report tick with no event at all —
   not even an `ActionRejectedEvent`. The served count read "honoured in full"
   for exactly that shape. Measured on the committed set at `3eb49dfc`: **23 of
   the 50 accepted prefixes carried at least one hashed step the engine never
   resolved** — 26 such steps in total. The repair compares against the engine's
   own events instead: `_resolved_action_pairs` collects every `(tick, actor)`
   the tick function emitted a resolved-action event for, and `_replay_prefix`
   raises `HeldOutPrefixError` — counts only, never a step — when a hashed pair
   is missing from it. `_PrefixAgent`'s served counter is gone rather than
   renamed: nothing needs it now, and a number that measured the wrong thing is
   not worth keeping for its diagnostic value. Planted case on the out-of-band
   debugging seed 9001, whose reporter `p-2` does not sort last among the living:
   `test_a_step_the_meeting_tick_discards_never_reaches_a_digest` adds one legal
   move for the later-sorting actor on the report tick, and the seam refuses the
   prefix. `test_a_report_tick_step_the_engine_does_resolve_passes_the_seam`
   bounds it from the other side on seed 9002, whose reporter sorts last: there
   the same shape IS executed, emits its `Moved` event, and passes. The two
   earlier plants (an unseated `p-9`, a step for the victim after its death) are
   kept and now assert the new message; that test is renamed
   `test_a_step_the_engine_never_resolves_never_reaches_a_digest`.

2. **Nobody but the reporter is scheduled on the report tick**
   (`experiments/held_out_prefixes.py`). A true seam alone would have turned
   twenty-three band seeds into hard errors, so the generator stops drawing the
   phantom step as well. `build_prefix` draws the impostor's post-kill wander and
   both bystanders' wanders EXACTLY as before — same calls, same `last_tick`,
   same RNG consumption — and then discards the drawn step whose tick is the
   report tick and whose actor is not the reporter. Because no draw moved, every
   seed's roles, kill room, kill tick, routes and walk are the ones they always
   were. **This pass wrote here that "the world up to the report is unchanged;
   only the hashed schedule is", which is false and is corrected in round 4
   below**: the drop is unconditional on the actor sort, so it also removed 35
   moves the engine really executed, and 28 of the 50 prefixes changed content,
   not only digest. The mechanism the drop is there for is the one stated in the
   design-decisions section — a hashed schedule must not depend on how an actor's
   id sorts against the reporter's — and that is what the corrected wording says.
   Proved by
   `test_the_generator_scripts_nobody_but_the_reporter_on_the_report_tick`, and
   by the set comparison below.

3. **A build failure aborted the draw, and the tally flattened its totals**
   (`experiments/held_out_prefixes.py`). `build_prefix` can raise "staged the
   reporter beyond the tick budget" for a seed whose own draw overruns the
   budget; neither `generate` nor `tally_reasons` converted it, so one unlucky
   seed would have stopped the whole band instead of being recorded and walked
   past. That failure now raises the narrower `ScheduleTickBudgetError` and both
   callers record it as a `schedule_exceeds_tick_budget` skip; every other
   `HeldOutPrefixError` out of `build_prefix` — an unauthorized roster, a map
   with no route — is invalid input and still raises.
   `tally_reasons` returns a frozen `ReasonTally` whose `seeds` and `accepted`
   are FIELDS beside a `reasons` histogram, so a future reason code named `seeds`
   or `accepted` can no longer overwrite a total; the command prints the same
   rows as before. No seed walked so far draws an overrunning schedule, so the
   path is planted:
   `test_a_seed_whose_schedule_overruns_the_budget_is_skipped_not_a_stop` makes
   `build_prefix` raise for seed 9001 and asserts the skip is recorded, the draw
   continues to 9002 and the tally counts it, while
   `test_an_unauthorized_roster_still_raises_rather_than_becoming_a_skip` holds
   the other side.

4. **Four documentation statements did not reproduce** (this card). The headline
   freeze digest named `c060f3ca…`, which is the manifest at `92bec106`, not the
   committed file; "The set" now states the digest of the file at the head of
   this branch and every earlier value is named as a superseded pre-freeze
   revision inside its own dated subsection. The fail-loud narrative cited a
   frozen `source_sha256` of `9e467dd1…`, which matches no object on this branch
   and no revision of it — it was fabricated; the true chain is `9c6ec3ab…` at
   `f9d02ad2` and `2daa5612`, `0b94fec1…` at `92bec106`, `89d0220e…` at
   `3eb49dfc`, `1c8ce570…` at `27e6d952` (this pass's head; round 4 moved it
   again), and every other elided digest in this
   card was re-verified against committed bytes in the same pass. "Each neuter
   turned exactly its own planted case red" does not reproduce — every module
   edit also moves `source_sha256`, so
   `test_the_committed_manifest_regenerates_from_its_own_band` goes red beside
   the planted case — and the table above now says so. The tally command was
   written with a repo-relative `.venv/bin/python` that does not run in a fresh
   clone; it is `uv run python` throughout. Two Acceptance items carried a
   `Verification-round correction:` prefix instead of the documented
   `Review correction:`.

**Set impact.** `test_the_committed_manifest_regenerates_from_its_own_band` was
run BEFORE regenerating and failed on `accepted` alone, at seed 3000's digest.
Compared field by field against the manifest at `3eb49dfc`: `accepted[].seed` is
identical for all fifty, `skipped` and `skipped_reason_counts` are identical
(eight seeds, all `witnessed_kill`), `last_accepted_seed` is identical at 3057,
and `band`, `roster`, `filter_environment`, `development_definitions`,
`body_handle_assertion`, `status`, `status_note`, `card`, `max_ticks`,
`temporal_observation_version`, `canonical_json`, `version`, `prefix_bytes` and
`filter` are untouched. **Forty-five of the fifty accepted digests moved** —
exactly the forty-five schedules that carried a non-reporter step on the report
tick; the other five drew none and are byte-identical. Seed 3000's digest moved
from `ab053eef…` to `ab8db76d…`. Regenerating with
`uv run python -m experiments.held_out_prefixes` produced 46 insertions and 46
deletions in the manifest: the forty-five digests plus the `source_sha256` entry
for `experiments/held_out_prefixes.py`, which moved from `89d0220e…` to
`1c8ce570…`; the other twenty-one source entries are unchanged. The file's byte
count is unchanged at 11,524, so `docs/artifacts.md`'s `audits/` inventory row
still reads `14,850,288 tracked bytes / 202 files` and was not touched. The
manifest's own sha256 moved from `3089c2d7…` to
`c5fb806e7b115cd168227ec89f02c5624d02e19ee49b650d6035ef09debebad9` at commit
`27e6d952` — a superseded pre-freeze revision; round 4 below moved it once more.

**What the digest move actually was**, measured in round 4 and stated here beside
the two figures this pass published (23 of 50 prefixes carrying a phantom step,
45 of 50 digests moved). The drop removed **61 steps** across the fifty accepted
prefixes: **26 the engine never resolved** (the phantoms, spread over 23
prefixes) and **35 moves the engine DID execute**, for actors whose ids sort
before their reporter's. So of the 45 prefixes whose digest moved, **17 dropped
only phantom steps** and **28 dropped at least one executed move** — and those 28
are exactly the prefixes whose **meeting-open world moved**: a different
living-player room assignment and a different episodic memory (7,267 → 7,218
rows over the four agents' stores, 49 movement observations fewer). Nothing
before the report tick moved at all (0 of 50 pre-report event streams differ),
and no filter verdict, proof-row count or rendered meeting-trigger line moved in
any of the fifty.

**Fail-loud for the round-3 gates.** Each was neutered in turn, the module's
suite run, and the module restored byte-for-byte
(`shasum -a 256 experiments/held_out_prefixes.py` back to
`1c8ce5700f61b3d920a1057b50788c209fed5fe7e12788db19901fccaba476d3`):

| neutered | red |
| --- | --- |
| the `_replay_prefix` engine-resolved comparison (`if False:`) | `test_a_step_the_engine_never_resolves_never_reaches_a_digest`, `test_a_step_the_meeting_tick_discards_never_reaches_a_digest`, `test_the_committed_manifest_regenerates_from_its_own_band` (3 failed, 22 passed) |
| the report-tick drop in `build_prefix` | 8 failed, 17 passed — the generator's own assertion, both report-tick seam cases, and every test that calls `generate()` or `tally_reasons`, because the seam then refuses the phantom-carrying schedules outright |
| the `schedule_exceeds_tick_budget` conversion in `generate` | `test_a_seed_whose_schedule_overruns_the_budget_is_skipped_not_a_stop`, `test_the_committed_manifest_regenerates_from_its_own_band` (2 failed, 23 passed) |

**Out-of-band tally, re-run at this head** — unchanged from both earlier rounds,
which is the check that removing the report-tick steps moved no filter verdict:

```text
$ uv run python -m experiments.held_out_prefixes --tally 1 50
seeds 50
accepted 45
witnessed_kill 5
```

**Preparer statement, restated for this pass.** No prefix from the preregistered
band was printed, opened or reasoned about during these corrections. The only
band values that left the generator are the ones the manifest already records —
seeds, reason codes and digests — plus the two aggregate counts stated above (23
of 50 prefixes affected, 45 of 50 digests moved); the further aggregates in "What
the digest move actually was" were measured in round 4 and carry the same
statement. Every planted case and every probe used seed 1 or seeds 9001–9002, and
the tally used seeds 1–50; all are outside the band and were already recorded as
development seeds. No arm ran and no provider call was made.

**Gate after the round-3 corrections**, run in order on this branch:

| check | result |
| --- | --- |
| `.venv/bin/pytest tests/experiments/test_held_out_prefixes.py -q` | 25 passed in 2.33 s (5 new: the meeting-tick plant, its executed counterpart, the generator's report-tick assertion, the schedule-overrun skip and the unauthorized-roster raise; the unexecuted-step case was renamed, not added) |
| `.venv/bin/python scripts/validate_task_docs.py` | 390 phase tasks, 390 prompts, 43 work cards |
| `.venv/bin/python scripts/check_doc_facts.py` | doc facts, front door, ml-program and budgets verified |
| `.venv/bin/python scripts/verify_ml_evidence.py` (offline, never `--complete`) | checks 60, OK 48, FAIL 0, ABSENT 7, INFO 5 |
| `.venv/bin/pytest tests/scripts/test_verify_ml_evidence.py -q` | 80 passed in 87.99 s |
| `bash scripts/check.sh` | exit 0: ruff (498 files formatted), 4 import-linter contracts kept, task docs, `generate_prompts --check` (390 in sync), mypy over 469 source files, **7,198 passed / 20 skipped / 3 xfailed** in 240.21 s, then the frontend leg — lint, three `tsc --noEmit` passes, 514 vitest tests over 19 files, and a clean production build |

### Review corrections, round 4 (2026-09-07)

A third verification round found the round-3 pass's own description of its set
change false in four places. No gate, filter or generated schedule changes here:
the only code edit is the comment above the report-tick drop in `build_prefix`.
The set at `27e6d952` is correct and was NOT regenerated into a different set —
regenerating with `uv run python -m experiments.held_out_prefixes` moved one line,
the module's own `source_sha256`, exactly as a comment edit should.

**What was wrong.** Round 3 justified dropping the non-reporters' report-tick
step with an after-the-reporter argument and then generalised it: "a move drawn
for it is never executed", "every seed's world up to the report is the world it
always was", "only the hashed schedule is". The drop in `build_prefix` is
unconditional on the actor sort (`if tick != report_tick or action.actor ==
reporter`), while the justification held only for actors sorting AFTER the
reporter. `orchestrator/action_ordering.py::_action_order_key` sorts a tick's
actions by actor, so an actor whose id sorts BEFORE the reporter's has its
report-tick action applied by `engine/tick.py` before the report flips the phase
to `MEETING` — which is exactly what this branch's own
`test_a_report_tick_step_the_engine_does_resolve_passes_the_seam` asserts. The
mechanism the drop is FOR is the one the design-decisions section and that test
already state correctly: a hashed schedule must not depend on that tiebreak. The
four statements now say that, and say what the drop cost.

**What the round-3 drop actually did**, measured over the fifty accepted seeds by
replaying each one twice — once with `experiments/held_out_prefixes.py` at
`3eb49dfc`, once at this head, both against the same canonical map — and
comparing counts and per-seed hashes only, never a step:

| measure | at `3eb49dfc` | at this head |
| --- | --- | --- |
| accepted seeds / skips / last accepted seed | 50 / 8 `witnessed_kill` / 3057 | identical |
| accepted prefix digests that differ | — | **45 of 50** |
| steps the drop removed | — | **61** (26 the engine never resolved, **35 it executed**) |
| prefixes dropping only phantom steps | — | 17 |
| prefixes dropping at least one executed move | — | **28** |
| prefixes carrying at least one phantom step | 23 | 0 |
| engine-executed `Moved` events at the report tick, summed | **35** | **0** |
| event streams for every tick `< report_tick` that differ | — | **0 of 50** |
| meeting-open living-player room assignments that differ | — | **28 of 50** |
| meeting-open episodic memories that differ | — | **28 of 50** (7,267 → 7,218 rows) |
| filter verdicts, proof-row counts, rendered trigger lines that differ | — | **0 of 50** |

So the true statement is: every draw, role, kill room, kill tick, route and walk
is unchanged, and every seed's world is byte-identical through
`report_tick - 1`; at the report tick the drop removed 26 phantom steps AND 35
moves the engine really ran, so **28 of the 50 frozen prefixes now open the
meeting with a different living-player room assignment and a different episodic
memory** — the evaluated content moved, not only the hash. That is deliberate:
the frozen scenario must not depend on how an actor's id sorts against the
reporter's on the tick the meeting interrupts. It is also why the freeze is the
owner's merge and not this card's completion — the change is pre-freeze.

**Where it is corrected.** `experiments/held_out_prefixes.py` (the comment above
the drop in `build_prefix`), the Acceptance item on the report-tick drop plus a
new Acceptance item stating the set change, the design-decisions paragraph on the
wanderers, round 3's item 2 and its "Set impact" paragraph — each marked as
corrected rather than rewritten in silence — and the pull-request body.

**Manifest impact of this pass.** Running
`.venv/bin/pytest tests/experiments/test_held_out_prefixes.py -q -k regenerates`
BEFORE regenerating failed on `source_sha256` alone: `rebuilt["accepted"] ==
manifest["accepted"]` and `rebuilt["skipped"] == manifest["skipped"]` both held,
which is the direct evidence that a comment edit moved no prefix. Regenerating
produced one insertion and one deletion — the `source_sha256` entry for
`experiments/held_out_prefixes.py`, from `1c8ce570…` to `9bc18db8…`; the other
twenty-one source entries, all fifty accepted seeds and digests (seed 3000 still
`ab8db76d…`), the eight skips, `skipped_reason_counts`, `last_accepted_seed`
(3057), `band`, `roster`, `filter_environment`, `development_definitions`,
`body_handle_assertion`, `status`, `status_note`, `card`, `max_ticks`,
`temporal_observation_version`, `canonical_json`, `version`, `prefix_bytes` and
`filter` are untouched. The file's byte count is unchanged at 11,524, so
`docs/artifacts.md`'s `audits/` inventory row still reads
`14,850,288 tracked bytes / 202 files` (recomputed from `git ls-files audits/` at
this head) and was not touched. The manifest's own sha256 moved from
`c5fb806e…` at `27e6d952` to
`21190ab58f940a4d0085aa6a72118a1b5f8a14e2b62aa45323246fd3adc65946`.

**Digest audit.** Every elided digest in this card was re-verified against a
committed object at this head. `9c6ec3ab…`, `0b94fec1…`, `89d0220e…`,
`1c8ce570…` and `9bc18db8…` are the sha256 of
`experiments/held_out_prefixes.py` at `f9d02ad2`/`2daa5612`, `92bec106`,
`3eb49dfc`, `27e6d952` and this head respectively, and each equals that
revision's own `source_sha256` entry. `75de8723…`, `c060f3ca…`, `3089c2d7…`,
`c5fb806e…` and `21190ab5…` are the sha256 of the manifest file at the same five
points. `ab053eef…` is seed 3000's prefix digest in the manifest from `f9d02ad2`
through `3eb49dfc`; `ab8db76d…` is seed 3000's digest at `27e6d952` and here.
`1482ce81…` and `8ab1186e…` are planted values from the two fail-loud plants and
appear in no committed object, by design; `9e467dd1…` appears only in round 3's
record of the fabricated value it replaced. No other elided digest occurs in this
card.

**No new gate.** This pass adds no invariant and no test: the behaviour it
describes is already held by
`test_a_report_tick_step_the_engine_does_resolve_passes_the_seam` (an
earlier-sorting actor's report-tick move IS executed and passes the seam),
`test_a_step_the_meeting_tick_discards_never_reaches_a_digest` (a later-sorting
one is discarded and refused) and
`test_the_generator_scripts_nobody_but_the_reporter_on_the_report_tick` (the
generator scripts neither). The suite count is therefore unchanged at 25.

**Out-of-band tally, re-run at this head** — unchanged from all three earlier
rounds:

```text
$ uv run python -m experiments.held_out_prefixes --tally 1 50
seeds 50
accepted 45
witnessed_kill 5
```

**Preparer statement, restated for this pass.** No prefix from the preregistered
band was printed, opened or reasoned about during these corrections. The
comparison above ran in-process and emitted counts and per-seed hashes only; the
only band values that left it are the ones the manifest already records — seeds,
reason codes and digests — plus the aggregate counts in the table. Every planted
case and every probe used seed 1 or seeds 9001–9002, and the tally used seeds
1–50; all are outside the band and were already recorded as development seeds. No
arm ran and no provider call was made.

**Gate after the round-4 corrections**, run in order on this branch:

| check | result |
| --- | --- |
| `.venv/bin/pytest tests/experiments/test_held_out_prefixes.py -q` | 25 passed in 2.29 s (unchanged; this pass adds no test) |
| `.venv/bin/python scripts/validate_task_docs.py` | 390 phase tasks, 390 prompts, 43 work cards |
| `.venv/bin/python scripts/check_doc_facts.py` | doc facts, front door, ml-program and budgets verified |
| `.venv/bin/python scripts/verify_ml_evidence.py` (offline, never `--complete`) | checks 60, OK 48, FAIL 0, ABSENT 7, INFO 5 |
| `.venv/bin/pytest tests/scripts/test_verify_ml_evidence.py -q` | 80 passed in 88.92 s |
| `bash scripts/check.sh` | exit 0: ruff (498 files formatted), 4 import-linter contracts kept, task docs, `generate_prompts --check` (390 in sync), mypy over 469 source files, **7,198 passed / 20 skipped / 3 xfailed** in 226.63 s, then the frontend leg — lint, three `tsc --noEmit` passes, 514 vitest tests over 19 files, and a clean production build |
