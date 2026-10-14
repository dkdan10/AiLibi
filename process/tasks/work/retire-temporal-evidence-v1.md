# Closed unexecuted: temporal v1 and evidence v1 were not retired

**Status:** done

## Outcome

CLOSED UNEXECUTED on 2026-10-10, on the owner's D15 word, verbatim: "close it".
The card could start only once an adopting record for evidence reasoning
version 2 existed, and that record has no source: round 3 took the narrow route
field rather than version 2 and leaves `evidence_reasoning_version` unset
(decision memo 8.2 item 2), and the merged route field refuses to run beside
version-2 evidence. Nothing below was executed: no resolver, constant, guard or
test was deleted, and both levers stay selectable and default OFF. The rest of this card is the contract as it stood at
`225d2b77`, kept as the record of what was proposed, with two sentences moved
to the past tense where they said what stays (the Evidence paragraph of
2026-09-19 and the Expected scope paragraph on the body handle) and its six
Acceptance items replaced by the closure item; the Results say
what closed and what stays. The outcome it contracted:

Temporal observation version 1 and evidence reasoning version 1 no longer exist
as selectable behaviour. Four defects and one switch go with them. Legacy
recordings stamped with either version still load and still mean what they meant
when they were recorded.

## Evidence

Review claims are leads, not measurements of this tree. Reproduce each claim
from the archived follow-up review
([report](../../audits/review-2026-09-06/REVIEW_REPORT_FOLLOWUP.md), findings
NG3-4, NC1-2/FU-ALIBI-1, FU-ALIBI-2 and FU-ALIBI-3) on this checkout before
implementing.

- **NG3-4.** Temporal v1 renders an internally contradictory prompt: the
  movement-ledger line at `agents/memory/store.py:1503`
  (`[tick {tick}] {subject} left {room}.`) is dated one tick later than the event
  lines describing the same move. Pre-existing.
- **NC1-2 / FU-ALIBI-1.** With evidence v1 the movement breadcrumb inverts a
  witnessed departure and prints the destination as where the subject was last
  seen, placing a killer in a room they had not yet reached. The v2 path takes
  both endpoints of a witnessed transition at their source tick
  (`agents/memory/store.py:1030-1035`); v1 falls through to the last-changed-room
  reconstruction and its prior-room selection at `:1069-1075`. Refuters found it
  at higher prevalence than filed.
- **FU-ALIBI-2.** `agents/memory/evidence_context.py:125-126` returns early
  unless `evidence_reasoning_version` is 2, so under evidence v1 with
  `meeting_reset=hub_with_grace` the engine's regroup teleport is invisible and
  every teleported player is accused of impossible travel.
- **FU-ALIBI-3.** Evidence v1 keeps only the last changed room pair per subject,
  so a later benign sighting erases an earlier impossible-travel finding.

**Re-assessed on 2026-09-19 and still blocked.** The adopting record for
evidence reasoning v2 that this card's first acceptance item waits for will not
come from the fresh-model deduction evaluation: the owner closed that evaluation
that day, accepting decisions D1, D2 and D8 of
[the direction memo](../direction-2026-09-19-process-over-outcome.md), and its
five runs and three calibrations are context rather than adoption evidence. It
was the only planned source of such a record. The only record the accepted
direction produces is [the wave's single re-record](process-rerecord.md), and
what that record adopts is that card's decision to state, not this one's to
assume. So nothing here executed: Status stayed `ready`, every box stayed
unchecked, and no deletion was performed, until the card closed unexecuted on
2026-10-10 (Results).

The procedure is `docs/agent-procedures.md` "Retiring substrate levers" (`:6`):
delete the `*_enabled()` resolver, the `ENV_*` constant and its `__all__` entry,
the `env` parameter wherever no live resolver is reachable, and every guard
(replaced by its always-taken side); keep the lever's snake_case key in
`orchestrator/replay.py::_RETIRED_ALWAYS_ON_LEVERS` (`:883`) so a recording keeps
self-describing its substrate. Task 20.37 is the precedent. The structural gate
is `tests/meetings/test_lever_registry.py`, which walks `agents/`, `meetings/`
and `orchestrator/` with `ast` and fails on any `*_enabled` function that neither
reads its `env` argument nor returns anything but a bare `True`.

## Acceptance

- [x] **Closed unexecuted on 2026-10-10, on the owner's D15 word; nothing was deleted.**
  The adopting record for evidence reasoning version 2 that this card's first
  item waited for has no source: round 3 records with
  `evidence_reasoning_version` unset (decision memo 8.2 item 2), and the merged
  route field refuses to run beside version 2. Both resolvers stay
  (`temporal_observations_enabled`, `observation/version.py:12`;
  `evidence_reasoning_enabled`, `meetings/evidence_profile.py:45`, at
  `225d2b77`), neither key joined `_RETIRED_ALWAYS_ON_LEVERS`, no test or
  recording moved, and the four v1 defects in Evidence stay on the version-1
  paths.
  - Mechanism: at the closing commit, a count-only `git grep -c` for the two
    resolvers' `def` lines prints 1 in each file (the command is in Results).
    `scripts/validate_task_docs.py` (`:160-164`) accepts a `done` card only
    with every box checked and a non-empty `## Results`.
  - Planted: this card with one former item restored unchecked fails that
    validator with "done card has unchecked acceptance items", and with its
    Results emptied fails with "done card needs ## Results with evidence".
  - The six items this card carried are in the repository history:
    `git show 225d2b77:tasks/work/retire-temporal-evidence-v1.md`.

## Constraints

Do not start before an adopting record for evidence reasoning v2 exists; this is
the card's first acceptance item and its hardest prerequisite. Do not add an
exemption to the lever-registry gate — the gate exists because nine dead
resolvers accumulated across five graduations. No re-record and no committed
recording rewritten: historical stamps keep their meaning. No new lever, no
provider calls, no behaviour change beyond making v2 unconditional. Follow
`docs/agent-procedures.md` "Retiring substrate levers" exactly; the prose sweep
is the larger half of the work, not an optional tail.

## Expected scope

`agents/memory/store.py`, `agents/memory/evidence_context.py`,
`observation/temporal.py`, `meetings/`, `orchestrator/replay.py` (registry keys
only), `.env.example`, the tests that pin the parameter rather than the
behaviour, and every doc line naming either lever as switchable. Directly
necessary call-site follow-through is permitted; new behaviour is not.

The body-handle field (scope added 2026-09-26 by
[the body-handle card](report-body-handle.md)). Once temporal version 2 is the
only live behaviour, the live game names every reported corpse by its public
handle, so `_build_meeting_trigger`'s `report_body_handle_version == 1` branch
in `orchestrator/game.py` and its `report_body_handle_version` keyword are
dead code for play and are deleted with the graduation (craft rule 3), unless
the Stage-B adopting card has already graduated them. One condition binds the
deletion: the prompt-byte golden re-renders each recorded opening from a
trigger rebuilt through that keyword, so while any recording it walks records
the field ON with temporal delivery OFF (the Stage-B candidate does), the
branch stays as the golden's read path, or the deletion moves that reading
into the reconstruction in the same change. Either way `report_body_handle_version`
stays in `RecordedExperimentConfig` as a read-only recorded key whose missing
value means `None`: the model forbids unknown keys, so deleting the field would
make every recording that carries it unparseable. This paragraph added scope
only; the Status stayed `ready` and every box unchecked until the card closed
unexecuted on 2026-10-10 (Results), so the branch and its keyword stay.

## Record impact

Retires two levers. Future recordings no longer carry a selectable version for
either; their snake_case keys stay in `_RETIRED_ALWAYS_ON_LEVERS`, so a recording
still self-describes its substrate and a legacy stamp recording the lever OFF is
still refused. Historical v1-stamped recordings keep their recorded meaning and
are not re-interpreted, re-recorded or relabelled. Every measurement taken on a
v1 arm remains a historical measurement of a behaviour that no longer exists —
do not restate it as current.

## Validation

`uv run pytest tests/meetings/test_lever_registry.py -q` with the planted
resurrection, then `bash scripts/check.sh`, then
`bash scripts/verify_samples.sh`, then the four derived report checks:

```sh
uv run python scripts/build_sample_report.py --sample-dir replays/samples/4p1i --check
uv run python scripts/build_sample_report.py --sample-dir replays/samples/9p2i --check
uv run python scripts/build_sample_report.py --sample-dir replays/ml_corpus/4p1i --check
uv run python scripts/build_sample_report.py --sample-dir replays/ml_corpus/9p2i --check
```

## Results

### Closed unexecuted, 2026-10-10

**Why it closes.** On 2026-10-10 the owner ruled under the baselines memo's
D15, verbatim: "close it". The first acceptance item blocked this card until an
adopting record for evidence reasoning version 2 existed. The baselines memo of
2026-10-03 (`baselines-2026-10-03/baselines-memo.md`, an advisory memo kept with
the session's records outside the tree) named the one source such a record
could come from: a round 3 spent on version 2, its D2 option (b), "what would
unblock D15's retirement card". The owner's ruling 2 of 2026-10-06 deferred
to the orchestrator's recommendation, the narrow route field, D2 option (a)
(decision memo 8.1 and 8.2 item 2,
`tasks/decision-2026-09-24-stage-b-wave.md:1358-1360` and `:1376-1399`, at
`225d2b77`). Round 3 records the eight rules plus cooldown 6 and the route
field, and `evidence_reasoning_version = 2` "is not used" (`:1399`;
`tasks/work/stage-b-record-r3.md:353`). The merged route field (PR #501, merge
`47bee59a`) refuses to run beside version-2 evidence
(`MeetingEvidenceProfile._route_lines_refuse_version_two_evidence`,
`meetings/evidence_profile.py:137-156`, held by
`test_the_profile_refuses_it_beside_version_two_evidence`,
`tests/meetings/test_route_lines_arm.py:581`), so the dial round 3 took and the
version this card waited on cannot share a ballot. No committed declared
config sets either version (the count-only command below prints 0 for each of
the three). The card closes on the owner's word quoted above, on that basis.

**What this closure decides, and what it does not.** It decides only that this
card will not run, on the owner's D15 word; it is not the orchestrator's reading.
It retires no lever and adopts nothing:
`temporal_observations` stays one of the five live default-OFF substrate toggles
(`docs/architecture.md:111-117`), `evidence_reasoning_version` stays a
default-off switch of the meeting-experiment registry (`EXPERIMENT_ENV_NAMES`,
`meetings/evidence_profile.py:25`), and their version-1 paths stay selectable.
The baselines memo's D15-R1 and D15-R2 stay the owner's unless the same word
rules them, so the reasoning scorecard's twelve version-1 cases and its baseline
probe, whose retirement D15-R2 tied to this card, stay as they are. The body-handle branch in
Expected scope (`report_body_handle_version == 1`, `orchestrator/game.py:3832`)
stays, since it was to go only with temporal version 2's graduation.

**The four v1 defects stay where they were.** NG3-4, NC1-2 / FU-ALIBI-1,
FU-ALIBI-2 and FU-ALIBI-3 are not repaired and were not re-measured; they live
on the version-1 paths, which no committed declared config selects. FU-ALIBI-2's
combination, evidence version 1 with the regroup reset, is refused by the
recorded config itself (`RecordedExperimentConfig._meeting_reset_guards`,
`orchestrator/experiment_config.py:136-147`), so the adopted rules cannot record
it. The three first-pass ids routed here by mechanism (G1-02, M3-02, G4-2) move
from routed to retained in `docs/cleanup-dispositions.md` in the same commit.

**Delivery states.** Implemented, verified and independently reviewed: not
applicable, as no implementation exists. Merged: the closure is a `docs:` commit
on `main`, checked by the documentation lens alone (decision memo 8.7, item 4).
Adopted: not applicable; no experiment, adopting record or lever moved.

**Verification.** At the closing commit, each command below gives the output
beside it:

```sh
uv run python scripts/validate_task_docs.py      # passes with the derived inventory sentence
uv run python scripts/check_doc_facts.py         # passes
git grep -c -E 'def (temporal_observations_enabled|evidence_reasoning_enabled)\(' -- observation/version.py meetings/evidence_profile.py
                                                 # meetings/evidence_profile.py:1 and observation/version.py:1
grep -c -E 'evidence_reasoning_version|temporal_observation' replays/samples/9p2i/experiment-config.json replays/candidates/stage-b-r1/experiment-config.json replays/candidates/stage-b-r2/experiment-config.json
                                                 # 0 for each file
```

Planted, the validator fails on this card with one former item restored
unchecked, and again with this section emptied, printing the two messages
Acceptance quotes.

**Reopening.** An adopting record for either version 2, or an owner ruling
under D15 to retire the version-1 paths without one, starts a new card that
cites this one; this card is not flipped back. That card reproduces the four
defects at its own head, because nothing here re-measured them.
