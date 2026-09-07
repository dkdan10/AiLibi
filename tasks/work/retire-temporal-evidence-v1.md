# Retire temporal v1 and evidence v1

**Status:** ready

## Outcome

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

- [ ] **BLOCKED until an adopting record for evidence v2 exists.** Do not start
  this card before that record is committed: retiring v1 makes v2 the only
  behaviour, which is an adoption, and an adoption needs its own record. Confirm
  the record by path in Results before any deletion.
- [ ] Every v1 resolver, `ENV_*` constant, `__all__` entry, `env` parameter and
  `if <lever>_enabled():` guard for both levers is **deleted**, not defaulted to
  2 and not left dead behind an always-true branch.
- [ ] Legacy recordings stamped temporal v1 or evidence v1 still load and still
  reconstruct with the meaning they were recorded under; the loader still refuses
  a legacy stamp recording a retired lever OFF. A committed v1-stamped fixture
  proves it.
- [ ] The repo-wide prose sweep is done: grep each lever's snake_case name and
  rewrite every docstring, comment and doc line that still describes it as live
  or default-OFF. Nothing may tell a reader it can be switched off.
- [ ] `tests/meetings/test_lever_registry.py` passes with **no exemption added**
  for either lever, and a planted resurrection (a reintroduced `*_enabled`
  returning a bare `True`) fails it.
- [ ] The four v1 defects above are gone because the code path is gone, and each
  is confirmed absent by the reproduction that found it.

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
