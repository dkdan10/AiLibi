# Agent Prompt — 13.8 Asymmetric visibility: crew `same_room_only` / impostor `same_room_and_adjacent`

You are working on AiLibi. Before starting, read AGENTS.md, DESIGN.md, and the task section in tasks/phase-13.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth and the task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 13.8 — Asymmetric visibility: crew `same_room_only` / impostor `same_room_and_adjacent`, anchored to experiments/lab/report-phase-b-plan.md (visibility); experiments/lab/visibility_resim_asymmetric.py (the probe — impostor NOT re-blinded); engine/visibility.py (`compute_visibility_for_player`, `resolve_visibility_mode`, `visible_rooms_for_player`); engine/maps/canonical_1.yaml (`visibility_defaults`). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-13.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-13-asym-visibility`
**Depends on:** none
**Section refs:** experiments/lab/report-phase-b-plan.md (visibility); experiments/lab/visibility_resim_asymmetric.py (the probe — impostor NOT re-blinded); engine/visibility.py (`compute_visibility_for_player`, `resolve_visibility_mode`, `visible_rooms_for_player`); engine/maps/canonical_1.yaml (`visibility_defaults`)
**Complexity:** Integration
**Files in scope:**
- engine/visibility.py
- tests/engine/test_visibility.py
**Files NOT in scope:**
- agents/ and meetings/ — the detector (13.2–13.4), belief-wiring (13.5), and prompts (13.6) are the other levers; this is the engine sight rule only
- engine/maps/canonical_1.yaml — the BASE stays `same_room_and_adjacent`; the asymmetry is role-parameterized IN CODE, not a yaml base flip (so the lights sabotage + the default stay intact)
- recordings — the balance effect is measured at the smoke re-record; NO re-record here

File-disjoint from 13.5 (beliefs.py) and 13.6 (store.py + prompts), so it runs in PARALLEL with them. Role-parameterize
`engine/visibility.py` so an observer's visibility depends on its ROLE: at BASE visibility a CREWMATE sees
`same_room_only` while an IMPOSTOR keeps the base `same_room_and_adjacent`; an ACTIVE sabotage degrade (mode != base, e.g.
lights → `same_room_only`) still degrades EVERYONE. `compute_visibility_for_player` already holds the observer (with
`.role`), so choose the mode on it. This is the genre-correct impostor information economy (the predator keeps the sight
edge; the crew must INFER) and the FORCING FUNCTION that makes the inferential detector load-bearing (crew room-only →
private kills → testimony-based deduction). Probe-validated the impostor is NOT re-blinded
(`visibility_resim_asymmetric.py`: kills 168 / wins 11 ≈ baseline vs the symmetric flip's crater 141 / 5). Firewall-clean:
an observer's sight depending on ITS OWN role leaks nothing about others' hidden info.
**Definition of done:** crew observers get `same_room_only` and impostor observers `same_room_and_adjacent` at base, with
an active sabotage degrade still applying to everyone (unit-tested for crew, impostor, and the sabotage case); state-hash
determinism + the observation leak-property + firewall import tests stay green; a fake-provider sweep confirms the impostor
is NOT cratered (kills / parity-wins hold near baseline, per `visibility_resim_asymmetric.py`); NO re-record (the
deduction-side BALANCE swing is a REAL-PROVIDER readout gated at the Wave-B smoke re-record + owner sign-off);
`scripts/check.sh` is green.

## Implementation hint
the seam is inside `compute_visibility_for_player` (it has the observer): when `resolve_visibility_mode` returns the base,
use `same_room_only` for a crewmate and the base for an impostor; otherwise keep the resolved mode (so an active lights
degrade still hits the impostor too) — exactly the predicate in `visibility_resim_asymmetric.py`. No yaml base change.

## Integration risk
OWNER BALANCE LEVER (same class as the frozen clock) — it favors the impostor (it hunts AND evades better while crew
detect less); the fake sweep only certifies "impostor not cratered", and the real swing (does it overshoot the Phase-11
~14% floor?) is a real-provider readout gated at the smoke re-record + your sign-off. Firewall: role-parameterized sight
must not leak others' hidden state — the leak-property test is the guard. Determinism: role is fixed per game, so
byte-determinism holds. Ships (re-records) AFTER the detector + 13.6 render — crew room-only needs the inferential
detector to deduce — but is BUILT in parallel.

## Pre-flight checklist
- Read AGENTS.md, DESIGN.md, and the task section before editing.
- Inspect the current implementation before editing.
- Identify the existing local patterns for the files in scope and follow them.

## Constraints and non-goals
Do not modify DESIGN.md.
Do not modify AGENT_IMPLEMENTATION.md.
Do not modify tasks/phase-*.md unless this task explicitly lists those files in scope.
Do not implement work outside this task.

## Verification checklist
- Run every command listed in the Definition of done.
- Run `git diff --name-only` and confirm the diff stays within scope.
- If any Definition of done item is unchecked, report it explicitly in the PR description instead of declaring the task complete.

## Decisions vs questions
- If something is **ambiguous and blocking** (you cannot make a reasonable choice without further information): stop, open a draft PR, add a `## Questions` section, request review.
- If something is **ambiguous but resolvable by judgment** (a default value, a tie-break, a naming choice): document the choice in a `## Decisions` section in the PR description and proceed.

## Output expectation
Open a PR from branch `phase-13-asym-visibility` with a title like `task 13.8: asymmetric visibility: crew `same_room_only` / impostor `same_room_and_adjacent``.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing experiments/lab/report-phase-b-plan.md (visibility); experiments/lab/visibility_resim_asymmetric.py (the probe — impostor NOT re-blinded); engine/visibility.py (`compute_visibility_for_player`, `resolve_visibility_mode`, `visible_rooms_for_player`); engine/maps/canonical_1.yaml (`visibility_defaults`)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
