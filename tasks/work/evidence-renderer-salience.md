# Rank witnessed evidence above own routine under budget pressure

**Status:** ready

## Outcome

Under the production prompt budget a rendered memory keeps the witnessed
evidence a meeting could act on — vent sightings and sightings of other players
— instead of shedding it for the observer's own routine movement and task rows.
Speaker-controlled account-uncertainty text can no longer flood the render.
Lever-OFF and evidence-v1 rendered bytes stay identical.

## Evidence

Review claims are leads, not measurements of this tree. Reproduce each claim
from the archived follow-up review
([report](../../audits/review-2026-09-06/REVIEW_REPORT_FOLLOWUP.md), findings
NG3-1, VENT-2 and GR-1) on this checkout before implementing, and record the
reproduction with the change.

`agents/memory/store.py` sets `_SALIENCE_VENT_WITNESSED = 85` (`:66`) and
`_SALIENCE_SAW_PLAYER = 50` (`:77`), while the observer's own `own_transition`
(`:1601`) and `own_task_attempt` (`:1612`) rows render at salience 90, and every
evidence-context line enters at salience 90 (`:437-443`). The sort key at
`:459` is `(-salience, -tick, line)`, so own routine outranks witnessed evidence
before the token budget truncates. `agents/memory/evidence_context.py:383`
appends one unbounded, undeduplicated `Account uncertainty for <subject>` line
per ingested claim, and the claim volume is under the speaker's control.

`tests/fixtures/memory_rendering/tight_budget_drops_low_salience.json` and its
`.expected.md` already pin that a tight budget sheds lines; they do not pin
which class of line survives. Reviewers reproduced the eviction on real games
with the real agent factory at the default 1,500-token budget, so the fixture is
the pin, not the discovery.

## Acceptance

- [ ] Reproduce the eviction first, as a fixture: at the default 1,500-token
  budget a witnessed vent and a third-party sighting are shed while own
  transitions, own task attempts and account-uncertainty lines survive. The
  fixture fails on the current renderer and passes after the change.
- [ ] Re-rank inside the evidence-reasoning v2 renderer only. A fixture pair
  proves lever-OFF and evidence-v1 rendered bytes are identical before and
  after; the re-ranking is not applied to either.
- [ ] Bound the per-claim account-uncertainty lines with a named constant and
  emit an explicit `N further subjects not shown` line when the bound truncates,
  so shedding is visible rather than silent. Duplicate subjects collapse.
- [ ] Own-kill rows (`_SALIENCE_OWN_KILL` = 96, `store.py:1615`) still outrank
  the re-ranked evidence and survive the same budget.
- [ ] No committed replay's OFF or evidence-v1 render changes: canonical
  reconstruction and all four derived sample reports stay green.
- [ ] Adverse case planted: a speaker emitting many claims cannot push a
  witnessed vent out of the render, and a planted revert of the ordering fails
  the new fixture rather than passing quietly.

## Constraints

Evidence reasoning v2 and temporal v2 stay default-OFF; this repairs a candidate
renderer and is not an adoption or a measurement of model judgment. Add no new
lever, env switch or profile field — the ordering is a property of the v2
renderer, not a new toggle. No re-record, no committed recording or report
rewritten, no provider calls. One writer owns `agents/memory/store.py` for the
duration; card (c) touches the meeting layer and must not run concurrently over
this file. Follow `docs/architecture.md` Layering and Determinism, and keep
listener-visible evidence distinct from privileged reader state.

## Expected scope

`agents/memory/store.py`, `agents/memory/evidence_context.py`,
`tests/agents/test_memory_rendering.py`, and a new fixture pair under
`tests/fixtures/memory_rendering/` (`.json` input plus `.expected.md`).
Directly necessary call-site and docstring updates inside those files may
follow through. Do not edit meeting or reader modules here.

## Record impact

Evidence-v2 rendered prompt bytes only. No committed recording, report, DTO or
schema byte changes, and the default path is untouched. Evaluation impact: every
evidence-v2 arm captured before this lands measured a renderer that evicted its
own evidence, so those captures remain historical mechanics records and are not
comparable to post-repair arms. Adoption remains a separate decision requiring
its own record.

## Validation

`uv run pytest tests/agents/test_memory_rendering.py -q` for the fixture pair
and the planted regression, then `bash scripts/check.sh`, then
`bash scripts/verify_samples.sh`, then the four derived report checks:

```sh
uv run python scripts/build_sample_report.py --sample-dir replays/samples/4p1i --check
uv run python scripts/build_sample_report.py --sample-dir replays/samples/9p2i --check
uv run python scripts/build_sample_report.py --sample-dir replays/ml_corpus/4p1i --check
uv run python scripts/build_sample_report.py --sample-dir replays/ml_corpus/9p2i --check
```
