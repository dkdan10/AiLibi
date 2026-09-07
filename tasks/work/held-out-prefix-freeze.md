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

- [x] Verification-round correction: `evaluate_prefix` certifies a digest only
  for a schedule the replay honoured IN FULL. The duplicate gate below closed
  one route to that defect; three more stayed open — a step past `report_tick`,
  a step past `max_ticks`, and a step addressed to a player the roster never
  seats or that the loop stopped asking because it was dead. The first two are
  refused by a second `model_validator`; the third cannot be judged from the
  schedule alone, so `_replay_prefix` counts the steps the replay actually
  executed against the steps the digest binds and raises `HeldOutPrefixError`
  on a shortfall. Proved by
  `test_a_step_outside_the_replayed_window_is_refused` and
  `test_a_step_the_replay_never_executes_never_reaches_a_digest`.
- [x] Verification-round correction: the filter environment claim names the
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
$ .venv/bin/python -m experiments.held_out_prefixes --tally 1 50
seeds 50
accepted 45
witnessed_kill 5
```

`tally_reasons` evaluates each seed exactly as `generate()` does and returns
only these three rows. It refuses any range that intersects seeds 3000–3999, so
the same command cannot be turned on the held-out set: an aggregate count over
band seeds is still a probe, and a narrow enough range would be a per-seed read.

`audits/deduction-candidate/held-out/manifest.json` is the freeze artifact —
**sha256 `c060f3cac7fba8546c160f634e5788a052663458ceefd51e1fd2c366cd38b78e`**,
11,524 bytes (the review corrections below re-stamped one `source_sha256` entry;
the digest before them was
`75de872360ae06aeaa0a80f22efbdfda20b2210db66cd8f3fbec6ebfd58740f7` at the same
byte count). It records the band, the roster, the tick budget, the temporal
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
   'sha256': 'ab053eef…'}`. Reverted; `14 passed`.
2. **A non-behavioural generator edit.** Appending a comment line left every
   prefix digest identical but moved the module's own digest, and the same test
   went red on `rebuilt["source_sha256"] != manifest["source_sha256"]`
   (`experiments/held_out_prefixes.py`: `8ab1186e…` vs `9c6ec3ab…`, the entry
   frozen at the time of this plant — two later correction passes have
   re-stamped that one entry, and the frozen value now reads `9e467dd1…`).
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
sha256 moved to
`c060f3cac7fba8546c160f634e5788a052663458ceefd51e1fd2c366cd38b78e`.

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
   Membership and liveness are not, so `_PrefixAgent` now records the scripted
   ticks it actually served and `_replay_prefix` raises `HeldOutPrefixError` when
   the served total falls short of `len(prefix.steps)` — before a
   `PrefixEvaluation` exists, so no partly executed schedule can reach a digest.
   The error message carries counts only, never a step. Planted cases:
   `test_a_step_outside_the_replayed_window_is_refused` (a step at
   `report_tick + 1`, a step at tick 99, and a `report_tick` equal to
   `max_ticks`, each through both the constructor and `model_validate`) and
   `test_a_step_the_replay_never_executes_never_reaches_a_digest` (an unseated
   `p-9` and a step for the victim two ticks after its death, each asserted to
   move `prefix_sha256` and then to raise). Both plants are built on seed 1.

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
run; each neuter turned exactly its own planted case red, and each was reverted
(`shasum -a 256 experiments/held_out_prefixes.py` back to
`89d0220e15d491210b58a1f4231afeddc05a3323f76732eb782ea7bc2f09af94`, `git status
--porcelain` clean for the module):

| neutered | red |
| --- | --- |
| the `_replay_prefix` served-count comparison (`if False:`) | `test_a_step_the_replay_never_executes_never_reaches_a_digest` |
| `_every_step_falls_inside_the_replayed_window` (early `return self`) | `test_a_step_outside_the_replayed_window_is_refused` |
| `filter_environment` returning a stored module mapping | `test_the_filter_environment_is_built_per_use_and_refuses_mutation` |

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
`3089c2d7361c70e6fb49981b374e0b9d167111bbf98b4b901055251b77964e9b`.

**Out-of-band tally, re-run under the new gates** — unchanged, which is the check
that the certifying seam does not reject legal generated schedules:

```text
$ .venv/bin/python -m experiments.held_out_prefixes --tally 1 50
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
