# Reject unsupported map traversal durations

**Status:** done

## Outcome

Maps cannot declare multi-tick movement that the engine executes immediately.
Validate the supported one-tick contract before a game or public map is created.

## Evidence

`engine/world.py` accepts any positive edge/vent traversal duration, while
`engine/rules.py` and `engine/tick.py` apply movement in a single tick. Public
pathing and map-grounded meeting checks also count adjacency hops. Every
canonical edge and vent uses one tick.

## Acceptance

- [x] Reject non-unit edge and vent traversal durations at map validation.
- [x] Genuine one-tick maps remain valid; task and sabotage durations remain
  independently configurable.
- [x] Adverse cases fail on the old implementation and pass after the repair;
  affected tests and the combined project gate pass.

## Constraints

Follow `docs/architecture.md` Packages and Determinism. Work on `codex/cleanup`.
Do not introduce in-transit state or change valid canonical gameplay. No prompt,
detector, recording, dependency, or provider changes belong to this card.

## Expected scope

`engine/world.py`, `tests/engine/test_map_loader.py`, `engine/README.md`, and this
card. Consumers were inspected across engine, observation, tactical pathing,
meetings, and spectator projections; no consumer needs a behavior change.

## Record impact

Post-record validation repair for unsupported custom maps. Canonical maps and
historical recordings retain their existing behavior and bytes.

## Validation

`uv run pytest tests/engine/test_map_loader.py tests/engine/test_tick.py
tests/agents/test_pathing.py`, affected ruff/format/mypy, and
`bash scripts/check.sh`. The regression includes direct model validation and
map loading, with valid controls and unsupported positive durations.

## Results

The four non-unit traversal controls failed before the validator change while
both one-tick controls passed. Afterward, all 107 map-loader, tick, and tactical
pathing tests passed. Ruff, formatting, and strict mypy passed for the two
edited Python files. Direct model validation and YAML loading reject durations
of two and ten; task and sabotage duration controls retain seven and nine ticks.

Independent portfolio-agent review found no blocker. Its probes mutated actual
canonical edge and vent rows with `"2"` and `2.0`; both were rejected. Canonical
map loading and its public-map projection passed. Trusted `model_construct` and
`model_copy` validation bypasses remain Pydantic's existing explicit escape
hatches, not external map-loading paths. This follows `docs/architecture.md`
Packages and Determinism without changing canonical or historical bytes.
The combined project gate passed; verification is recorded below.

### Combined verification and review

The final `bash scripts/check.sh` run passed: 6,409 Python tests (20 optional
skips, three expected failures), 455 frontend tests, strict typing, lint,
formatting, import boundaries, 390 historical contracts/prompts, and the build.
`bash scripts/verify_samples.sh` verified all 100 canonical recordings. No
canonical recording or historical report bytes changed. Logs: `/tmp/ailibi-cleanup-
batch2-check-final.log` and `/tmp/ailibi-cleanup-batch2-samples.log`.

Independent review: Portfolio-review agent; real canonical-map mutations and valid controls checked.
Implemented and verified for cleanup; the owner's final Claude review and merge
remain pending. This work does not adopt an experimental behavior.
