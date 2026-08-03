# Agent Prompt — 16.9 Personas: the role-neutral bank + deterministic assignment (inert until 16.16)

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-16.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 16.9 — Personas: the role-neutral bank + deterministic assignment (inert until 16.16), anchored to audits/post-phase-14-Voice-and-Judgment-planning.md §4.1 (the without-replacement design + the rejected hash scheme); orchestrator/seeder.py (the random.Random(seed) discipline + the role-neutral id invariant this must mirror); meetings/manager.py MeetingParticipant (the field 16.3 landed); eval/leak_test.py (the suite that must cover the bank). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-16.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-16-persona-assignment`
**Depends on:** 16.3
**Section refs:** audits/post-phase-14-Voice-and-Judgment-planning.md §4.1 (the without-replacement design + the rejected hash scheme); orchestrator/seeder.py (the random.Random(seed) discipline + the role-neutral id invariant this must mirror); meetings/manager.py MeetingParticipant (the field 16.3 landed); eval/leak_test.py (the suite that must cover the bank)
**Complexity:** Medium

The Voice track's substrate: a committed persona bank (data file, ≥12 entries — at exactly nine,
every 9p2i game uses the whole bank and only seat order varies; twelve-plus makes COMPOSITION vary
game-to-game) and a deterministic assignment: a seeded Fisher–Yates permutation of the bank keyed
by `game_seed`, seat i takes the i-th entry — sampling WITHOUT replacement, so no persona repeats
within a game (the planning doc explicitly rejects independent per-seat hashing: birthday
collisions re-introduce the homogeneity personas exist to break). Every persona is ROLE-NEUTRAL by
construction and by test — assignment happens before roles are known to anything downstream, and
the leak suite asserts no persona↔role correlation across the committed seed range (a persona
that correlates with impostorhood leaks the game). The assignment fills
`MeetingParticipant.persona` (the field 16.3 landed, inert): no template reads it until 16.16, so
this task changes ZERO rendered bytes — the golden proves it.

**Files in scope:**
- orchestrator/personas.py (new: the bank loader + assign_personas)
- data/personas.json (new: the committed bank — disposition-varied cards: aggressive accuser, cautious hedger, quiet observer, jokester, methodical analyst, … ≥12)
- orchestrator/game.py (participant-persona fill region in _build_participants — disjoint from 16.7's accessor region and the registry line)
- tests/orchestrator/test_personas.py (new: determinism, without-replacement, bank-size floor, role-neutrality sweep)

**Files NOT in scope:**
- agents/strategic/prompts/ (no template reads persona until 16.16)
- meetings/ (the field exists from 16.3; consumed as-is)
- orchestrator/seeder.py (personas are meeting-layer inputs, not world-state — seeding stays untouched, replays unaffected)

**Definition of done:**
- [ ] Assignment is a pure function of (seed, roster): two runs at the same seed produce identical assignments (pinned across the committed seed range); no two living players share a persona in any game; the bank-size floor (≥12) is asserted.
- [ ] Role-neutrality is tested, not asserted: across the committed seeds, persona↔role association is measured at chance level (the leak-suite extension), and the bank file carries no role-suggestive text (reviewed field: each card names diction/disposition only).
- [ ] Zero rendered-byte change: the golden and `verify_samples.sh` green with assignment live (the field fills; nothing reads it).
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

Mirror the seeder's discipline exactly: one `random.Random(derived_seed)` instance, shuffle a
sorted copy of the bank, zip with sorted seats. Derive the persona seed from the game seed with a
fixed offset/namespace so persona assignment never perturbs the seeder's existing draws (replay
byte-identity depends on the seeder's stream staying untouched — do NOT share its Random
instance). Keep the bank's cards short (a disposition line + two diction notes); 16.16 writes the
full preamble text.

## Public types this task introduces
- `orchestrator.personas.PersonaCard`
- `orchestrator.personas.assign_personas`

These are the symbols downstream tasks will import. Keep their signatures stable.

## Dependency contract check
Run these before editing. If any fail, stop and report — your dependencies are not where this task expects them.

- `uv run python -c "import agents.memory.beliefs"`

## Pre-flight checklist
- Read AGENTS.md, the architecture routing it names, and the task section before editing.
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
Open a PR from branch `phase-16-persona-assignment` with a title like `task 16.9: personas: the role-neutral bank + deterministic assignment (inert until 16.16)`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing audits/post-phase-14-Voice-and-Judgment-planning.md §4.1 (the without-replacement design + the rejected hash scheme); orchestrator/seeder.py (the random.Random(seed) discipline + the role-neutral id invariant this must mirror); meetings/manager.py MeetingParticipant (the field 16.3 landed); eval/leak_test.py (the suite that must cover the bank)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
