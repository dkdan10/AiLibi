# Agent Prompt — 7.2 Impostor mutual-awareness substrate (firewall-safe)

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-7.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 7.2 — Impostor mutual-awareness substrate (firewall-safe), anchored to tasks/phase-7-plan.md W0.2 + Q4 (decision 3); audits/audit-2026-05-30-1952-phase-7-meeting-frequency-diagnosis.md §1, §3 (7p/2i = 63% meeting rate); DESIGN.md §1.3 (observation firewall). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-7.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-7-impostor-mutual-awareness`
**Depends on:** none
**Section refs:** tasks/phase-7-plan.md W0.2 + Q4 (decision 3); audits/audit-2026-05-30-1952-phase-7-meeting-frequency-diagnosis.md §1, §3 (7p/2i = 63% meeting rate); DESIGN.md §1.3 (observation firewall)
**Complexity:** Integration

Phase 7's enablement gate switches the canonical eval roster to 7p/2i (two
impostors) so that meetings actually happen at volume (the diagnosis audit
measured 4p/1i ≈ 10% vs 7p/2i = 63%). But a 7p/2i game is only coherent if the
two impostors know they are on the same side: per locked decision 3, multiple
impostors must know who each other are, so that in meetings they never accuse or
vote one another. They get NO private conversation channel — coordination happens
only through public play — but each impostor must receive the identity of its
fellow impostor(s). Today nothing delivers this, so two impostors at 7p/2i would
treat each other as suspects and the eval signal would be polluted.

This task adds that mutual-awareness as an impostor-only field on `SelfView`
(`observation/packet.py`) — `fellow_impostor_ids: tuple[PlayerId, ...]` — and
populates it in `ObservationService` (`observation/service.py`) ONLY when the
recipient is an impostor. The field reuses the already-privileged self channel
where `role` lives (the agent is entitled to know its own role; by the same
logic an impostor is entitled to know its own team). It is empty `()` for every
crewmate recipient and empty for an impostor in a solo-impostor game (an impostor
has no fellows). It must NOT touch `visible_players` / `PlayerView` — that is the
public, crew-visible channel and the firewall forbids any role-bearing data
there. The recipient's OWN id is excluded from the tuple; only the other
impostors appear.

The field is delivered to agent code by extending
`agents/perception.py::_self_state_payload` so the impostor policy/prompt layer
can read its teammates from the same self-state payload that already carries
`role`. This is the only consumer wiring in scope; actually USING the teammate
list in meeting behavior (defend a teammate, never accuse one) is Wave 2 (J-5),
not this task.

The leak firewall is the hard constraint. Extend `eval/leak_test.py` with a new
explicit invariant: `self_state.fellow_impostor_ids == ()` for every
crewmate-recipient packet. Because player ids are role-neutral (`p-1`, `p-2`,
…; see `orchestrator/seeder.py`), the existing value scanner
(`_FORBIDDEN_VALUE_SUBSTRINGS = ("impostor", "crewmate", "crew")`) is not tripped
by id values, and the recursive field-name scanner keys off specific names
(`role`, `killed_by`, …) not the substring "impostor" in a key — so the new
field is firewall-safe by construction, but the test must PIN that an impostor
seeing its own teammates is allowed while a crewmate's tuple is always empty. The
three committed scripted fixtures are all 4p/1i (one impostor), so they already
exercise the crew-empty path; add a focused multi-impostor unit case in
`tests/observation/test_service.py` to exercise the impostor-sees-teammate path
(crew get `()`, each impostor gets the other impostor id, recipient excluded).

Crucially, ALSO extend the project's strongest leak test — the property-based
sweep `tests/observation/test_leak_property.py` (DESIGN.md §11.2's mandated
many-seeds purity check). Today it parametrizes only `seed` at the default 4p/1i
roster (`@given(seed=st.integers(...))`), so it never generates a multi-impostor
game and never touches the new field. Since `fellow_impostor_ids` is the FIRST new
self-channel field in the project's history, it must ride the strongest guarantee,
not just one hand-built unit case: parametrize the sweep over `num_impostors`
(include ≥ 2, with a valid roster, e.g. 7 players) and assert the crew-empty
invariant (`self_state.fellow_impostor_ids == ()` for every crewmate-recipient
packet) inside the per-packet loop, across many seeds. This closes the gap the
single-impostor fixtures leave (where a misroute into a crew tuple cannot surface).

Schema-mirror check (do this, do not assume): `SelfView` is NOT mirrored into the
spectator DTO surface (`api/schemas.py` shadows engine types directly and does not
reference `SelfView`) and is NOT referenced anywhere in
`frontend/src/types/api.ts` or `frontend/src/`. Confirm both before editing; if
the confirmation holds (it does at HEAD), this task stays entirely inside
`observation/`, `agents/perception.py`, `eval/leak_test.py`, and the listed test
files, and touches NO frontend code. Surfacing impostor coordination in the
privileged spectator UI is a deferred nice-to-have (plan §"Still open"), explicitly
NOT this task. Determinism is a hard constraint: the field is a pure deterministic
function of `WorldState.players` roles (no RNG, stable sort), so byte-identical
replay holds.

**Files in scope:**
- observation/packet.py
- observation/service.py
- agents/perception.py
- eval/leak_test.py
- tests/observation/test_service.py
- tests/agents/test_perception.py
- tests/observation/test_leak_property.py

**Files NOT in scope:**
- observation/audit.py (audit log records whatever the packet serializes; no change needed)
- api/schemas.py (SelfView is not mirrored here; verified, do not edit)
- frontend/ (SelfView is not consumed by the frontend; spectator surfacing is deferred)
- agents/impostor_policy.py (consuming the teammate list in meeting behavior is Wave 2 / J-5)
- orchestrator/seeder.py (roster/task config is Task 7.1; this task reads roles off WorldState, it does not assign them)
- meetings/ (no meeting-behavior change in Wave 0)

**Definition of done:**
- [ ] `SelfView` in `observation/packet.py` gains `fellow_impostor_ids: tuple[PlayerId, ...]` with a default of `()` (so existing `SelfView(...)` construction sites stay valid); the model stays frozen with `extra="forbid"`.
- [ ] `ObservationService` populates `fellow_impostor_ids` with the sorted ids of the OTHER impostors when the recipient's role is `IMPOSTOR`, and `()` for every crewmate recipient and for a sole impostor; the recipient's own id is never included.
- [ ] `visible_players` / `PlayerView` are unchanged; no role-bearing field is added to any crew-visible channel.
- [ ] `agents/perception.py::_self_state_payload` surfaces `fellow_impostor_ids` so the self-state payload exposes the teammate list alongside `role`.
- [ ] `eval/leak_test.py` asserts a new invariant: for every packet whose `self_state.role == "CREWMATE"`, `self_state.fellow_impostor_ids == ()`; the existing "no `PlayerView` carries role" and value/field scanners still pass unchanged.
- [ ] `tests/observation/test_service.py` adds a multi-impostor (>=2 impostors) case proving each impostor sees the other impostor id (self excluded), each crewmate sees `()`, and a solo-impostor build yields `()` for the impostor. Because all three committed scripted fixtures are 4p/1i (single impostor), this unit case (together with the extended property sweep below) is what exercises a roster where a misroute could surface a non-empty CREW tuple — so this case MUST additionally run the crew-empty leak assertion (`self_state.fellow_impostor_ids == ()`) over each crewmate-recipient packet built from the 2-impostor `WorldState`, not just check the populate logic. End-to-end coverage over a real played multi-impostor game lands with Task 7.8's committed 7p/2i set.
- [ ] `tests/observation/test_leak_property.py` (the DESIGN §11.2 many-seeds purity sweep) is extended to parametrize `num_impostors` (include ≥ 2 with a valid roster) AND to assert `self_state.fellow_impostor_ids == ()` for every crewmate-recipient packet in its per-packet loop — so the project's strongest leak test, not just one unit case, guards the first new self-channel field across many seeds and multi-impostor rosters.
- [ ] `tests/agents/test_perception.py` updates the pinned self-state payload assertion to include `fellow_impostor_ids`.
- [ ] Byte-identical replay determinism is preserved (the field is a pure function of roles in `WorldState`; no RNG, stable ordering).
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

Add the field to `SelfView` (`observation/packet.py:18`) as
`fellow_impostor_ids: tuple[PlayerId, ...] = ()`. The default is what keeps the
many existing `SelfView(room=..., role=..., pending_task_id=...)` call sites
(`tests/agents/test_beliefs.py`, `test_runtime.py`, `test_beliefs_wiring.py`,
`test_perception.py`) compiling without edits — only the perception payload test
that pins the dumped dict needs touching. `PlayerId` is already a `TypeAlias` in
this module, so no new import.

In `ObservationService._build_packet_from_visibility`
(`observation/service.py:67-119`), the service already reads
`player.role == "IMPOSTOR"` to compute `cooldown` (line 92) and has
`world_state.players` in hand. Compute the fellows in the same spot, e.g.:
`fellow_impostor_ids = (` `tuple(sorted(pid for pid, p in world_state.players.items()`
`if p.role == "IMPOSTOR" and pid != agent_id))` `if player.role == "IMPOSTOR" else ())`
and pass it into the `SelfView(...)` constructor at line 105. Sorting makes the
tuple deterministic and replay-stable. Do not gate on `alive` — an impostor knows
its teammate even after the teammate dies (it learned the identity at game start);
matching the engine's role-knowledge model and keeping the value independent of
visibility.

In `agents/perception.py::_self_state_payload` (line 195) add
`"fellow_impostor_ids": self_state.fellow_impostor_ids` to the returned mapping
(it serializes to a list in the prompt JSON, same as other tuple fields).

For the leak test, extend the per-packet loop in
`test_no_observation_leaks_hidden_information` (`eval/leak_test.py:271-299`): inside
the `if packet.self_state.role == "CREWMATE":` branch (line 298) add
`assert packet.self_state.fellow_impostor_ids == ()`. The three committed fixtures
are 4p/1i so this exercises the crew-empty path across all of them; the
impostor-sees-teammate path is covered by the new unit test in
`tests/observation/test_service.py`, which can build a 5-player / 2-impostor
`WorldState` (mirror the `_base_world_state` / `_player` helpers already in that
file) and assert the two impostors' packets carry each other's id while the three
crewmates carry `()`.

## Public types this task introduces
- `observation.packet.SelfView.fellow_impostor_ids`

These are the symbols downstream tasks will import. Keep their signatures stable.

## Integration risk

The observation firewall is the project's "most important test" (DESIGN.md §11.2):
this task adds the FIRST self-channel field beyond `role`, so the risk is leaking
team identity into a crew-visible path. Mitigation is structural — the value lives
only inside `SelfView` (the self channel), is populated only for impostor
recipients, and `visible_players`/`PlayerView` are explicitly out of scope and
unchanged. **Coverage (now first-class via the extended sweep):** the NEW crew-empty
invariant (`self_state.fellow_impostor_ids == ()`) is asserted in BOTH the scripted
`eval/leak_test.py::test_no_observation_leaks_hidden_information` (crew branch) AND
the property sweep `tests/observation/test_leak_property.py`, which THIS task extends
to parametrize `num_impostors` (≥ 2) and run the crew-empty assertion across many
seeds. This is necessary because the generic scanners alone would NOT catch a
crewmate erroneously receiving a non-empty `fellow_impostor_ids`: the recursive
field-name scanner keys off `{killed_by, kill_attribution, player_id}` (plus the
allowed `self_state.role` path), and the value scanner trips only on the substrings
`impostor`/`crewmate`/`crew`, none of which match role-neutral ids like `p-2`. So
the EXPLICIT assertion — not the scanners — is the guard, and the extended
multi-impostor sweep now exercises it across many random games (the single-impostor
4p/1i scripted fixtures cannot surface a crew-tuple misroute, since every impostor's
tuple is also `()` there). Task 7.8's committed 7p/2i set then adds end-to-end
coverage on a real played multi-impostor game. The second risk is determinism: the field must be a
pure, stably-ordered function of `WorldState` roles with no RNG and no dependence
on visibility/alive state, so the committed replay goldens and the audit-log
round-trip stay byte-identical. The third risk is construction-site breakage from
adding a field to a frozen `extra="forbid"` model — the `= ()` default neutralizes
it for every existing call site; verify with `uv run pytest` that no unrelated
`SelfView(...)` site regresses.

## Pre-flight checklist
- Read AGENTS.md, the architecture routing it names, and the task section before editing.
- Inspect the current implementation before editing.
- Identify the existing local patterns for the files in scope and follow them.
- Re-verify every file:line anchor the contract cites at HEAD before editing; if an anchor has moved, record the true location under `## Decisions` — never edit from a stale line number.
- Grep every consumer of each symbol, path, or constant you will change (the blast radius); if a hit lies outside the files in scope, stop and ask rather than widening scope silently.

## Craft rules (AGENTS.md "Craft rules" — non-negotiable for every file you touch)
- Lead with intent: a docstring or comment states what the code does and why, now; provenance (task ids, audit paths) is at most one trailing line. Do not narrate history in source.
- A gate must be able to fail: every new test or check that guards an invariant ships with a planted or perturbed case proving it bites, and checks the semantics it claims, not only the shape.
- Retire means delete: when a lever graduates or a branch dies, delete the resolver, the parameter, the branch and the tests that pin them; keep only the stamp key and one history line.
- No internal dialect on user-facing surfaces: UI copy, rendered game prompts, spoken text and README carry no task or audit ids, no threshold arithmetic, and no undefined jargon.
- Claims are verifiable-shaped: a doc claim names the mechanism that enforces it; a number is recomputed from committed bytes and its command goes in the PR.

## Constraints and non-goals
Do not modify DESIGN.md.
Do not modify AGENT_IMPLEMENTATION.md.
Do not modify tasks/phase-*.md unless this task explicitly lists those files in scope.
Do not implement work outside this task.
Do not add LLM calls inside agents/tactical/.
Do not import engine/ from agents/.
If the task mentions engine-free boundary schemas, keep agents/ free of engine imports and put engine translation only in orchestrator-owned code.

## Verification checklist
- Run every command listed in the Definition of done.
- If the contract carries a `**Measurement:**` field, run that command and paste its output into the PR's `## Summary`; a Measurement that cannot be run is reported under `## Questions`, never asserted.
- Run `git diff --name-only` and confirm the diff stays within scope.
- If any Definition of done item is unchecked, report it explicitly in the PR description instead of declaring the task complete.

## Decisions vs questions
- If something is **ambiguous and blocking** (you cannot make a reasonable choice without further information): stop, open a draft PR, add a `## Questions` section, request review.
- If something is **ambiguous but resolvable by judgment** (a default value, a tie-break, a naming choice): document the choice in a `## Decisions` section in the PR description and proceed.

## Output expectation
Open a PR from branch `phase-7-impostor-mutual-awareness` with a title like `task 7.2: impostor mutual-awareness substrate (firewall-safe)`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing tasks/phase-7-plan.md W0.2 + Q4 (decision 3); audits/audit-2026-05-30-1952-phase-7-meeting-frequency-diagnosis.md §1, §3 (7p/2i = 63% meeting rate); DESIGN.md §1.3 (observation firewall)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
