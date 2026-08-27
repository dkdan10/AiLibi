# Agent Prompt — 21.5 One vent, one record: the double mint and the audible copy that leaks through the teammate firewall

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-21.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 21.5 — One vent, one record: the double mint and the audible copy that leaks through the teammate firewall, anchored to A-31 [CONFIRMED, P2, defect] — audits/review-2026-08-26/A/collated-findings.md:3501-3597 (the claim, the finder's prompt-level census, the verifier's independent re-run, and the verifier note's two binding additions: the redundancy half is PRIOR ART — audits/review-2026-08-19/B/observation-firewall.md:155 F13 and idea #21 at audits/review-2026-08-19/A/collated-findings.md:587, so the novelty is the 27-row firewall residue, not the duplicate; and the co-emission is PINNED by a shipped test the fix must update); B-28 [CONFIRMED, P2, quality-debt] — audits/review-2026-08-26/B/collated-findings.md:1688-1729, read as context only and explicitly NOT fixed here (`grep -c audible eval/leak_scan.py` → 0 at HEAD, re-run). Anchors re-verified at HEAD `4002f19b`: observation/service.py:359-381 `_audible_events` — the method spans :359-381 at HEAD (the register cites it as :359-377 in A-31's finder evidence and :359-380/:359-381 elsewhere; the vent derivation proper is the comprehension at :366-375 plus the `events.extend` at :376-378), :526-543 `_vent_observation_for_agent` (returns `None` unless `agent_id` is in `event.source_witnesses` / `event.destination_witnesses`, and copies the witnessed room into `audible_room` at :539-543), :192-195 `_ObservedAction` (`audible_room` at :195), :316-319 the `build_packet` call site; observation/packet.py:150-152 `AudibleEvent` (`kind` is `Literal["vent_use_heard", "sabotage_alarm"]`), :181 the packet field, :192-204 the serializer (only `moved_players` is omitted when empty, so the field's JSON shape does not move); agents/perception.py:84-87 `_AUDIBLE_EVENT_TYPES`, :106 the ingest-order docstring, :231-241 the ingest loop; agents/memory/store.py:64-65 (`_SALIENCE_VENT_WITNESSED` 85, `_SALIENCE_VENT_HEARD` 75), :1045-1081 `_sighting_is_suppressed`, :1800-1808 its call in `_render_saw_player`, :1810-1816 the witnessed-vent line, :1599-1607 the heard-vent render, :1986-2004 `_render_heard`; agents/memory/beliefs.py:530-534 (the room-only row "carries no subject and is deliberately not used" by Rule 4); agents/tactical/features.py:107 `ENCODER_VERSION = "v2"`, :160-161 the `heard_vent_use` / `heard_sabotage_alarm` slots, :373-378 and :407-408 the only reader of `packet.audible_events` in `agents/`; api/schemas.py:188-197 `AudibleEventView`; api/replay_loader.py:1452-1462 and :2722-2747 (the audio-field docstrings and the projection); frontend/src/components/EventTicker.tsx:43-46, frontend/src/types/api.ts:140; the shipped pin the verifier names — tests/observation/test_service.py:205 `test_vent_witness_sees_vent_action_and_audible_event` with the co-emission assertion at :245-249 (the register's ":240-249" is the surrounding block); the read-path tests that stay green unedited — tests/agents/test_perception.py:433-449 and :812-818 (the Literal↔map coupling test), tests/orchestrator/test_meeting_integration.py:2796-2810 `test_heard_vent_use_grounds_nothing`, tests/agents/test_features.py:113-115, tests/fixtures/memory_rendering/tight_budget_drops_low_salience.json:33; DESIGN.md:413 (the field is listed with a `# vent use heard, sabotage alarm` comment — the double delivery is specified nowhere); audits/audit-phase-20-close.md:89-113 §F1 (the nine campaign-tier failures this task's campaign run is compared against).. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-21.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-21-vent-mint`
**Depends on:** 21.3
**Section refs:** A-31 [CONFIRMED, P2, defect] — audits/review-2026-08-26/A/collated-findings.md:3501-3597 (the claim, the finder's prompt-level census, the verifier's independent re-run, and the verifier note's two binding additions: the redundancy half is PRIOR ART — audits/review-2026-08-19/B/observation-firewall.md:155 F13 and idea #21 at audits/review-2026-08-19/A/collated-findings.md:587, so the novelty is the 27-row firewall residue, not the duplicate; and the co-emission is PINNED by a shipped test the fix must update); B-28 [CONFIRMED, P2, quality-debt] — audits/review-2026-08-26/B/collated-findings.md:1688-1729, read as context only and explicitly NOT fixed here (`grep -c audible eval/leak_scan.py` → 0 at HEAD, re-run). Anchors re-verified at HEAD `4002f19b`: observation/service.py:359-381 `_audible_events` — the method spans :359-381 at HEAD (the register cites it as :359-377 in A-31's finder evidence and :359-380/:359-381 elsewhere; the vent derivation proper is the comprehension at :366-375 plus the `events.extend` at :376-378), :526-543 `_vent_observation_for_agent` (returns `None` unless `agent_id` is in `event.source_witnesses` / `event.destination_witnesses`, and copies the witnessed room into `audible_room` at :539-543), :192-195 `_ObservedAction` (`audible_room` at :195), :316-319 the `build_packet` call site; observation/packet.py:150-152 `AudibleEvent` (`kind` is `Literal["vent_use_heard", "sabotage_alarm"]`), :181 the packet field, :192-204 the serializer (only `moved_players` is omitted when empty, so the field's JSON shape does not move); agents/perception.py:84-87 `_AUDIBLE_EVENT_TYPES`, :106 the ingest-order docstring, :231-241 the ingest loop; agents/memory/store.py:64-65 (`_SALIENCE_VENT_WITNESSED` 85, `_SALIENCE_VENT_HEARD` 75), :1045-1081 `_sighting_is_suppressed`, :1800-1808 its call in `_render_saw_player`, :1810-1816 the witnessed-vent line, :1599-1607 the heard-vent render, :1986-2004 `_render_heard`; agents/memory/beliefs.py:530-534 (the room-only row "carries no subject and is deliberately not used" by Rule 4); agents/tactical/features.py:107 `ENCODER_VERSION = "v2"`, :160-161 the `heard_vent_use` / `heard_sabotage_alarm` slots, :373-378 and :407-408 the only reader of `packet.audible_events` in `agents/`; api/schemas.py:188-197 `AudibleEventView`; api/replay_loader.py:1452-1462 and :2722-2747 (the audio-field docstrings and the projection); frontend/src/components/EventTicker.tsx:43-46, frontend/src/types/api.ts:140; the shipped pin the verifier names — tests/observation/test_service.py:205 `test_vent_witness_sees_vent_action_and_audible_event` with the co-emission assertion at :245-249 (the register's ":240-249" is the surrounding block); the read-path tests that stay green unedited — tests/agents/test_perception.py:433-449 and :812-818 (the Literal↔map coupling test), tests/orchestrator/test_meeting_integration.py:2796-2810 `test_heard_vent_use_grounds_nothing`, tests/agents/test_features.py:113-115, tests/fixtures/memory_rendering/tight_budget_drops_low_salience.json:33; DESIGN.md:413 (the field is listed with a `# vent use heard, sabotage alarm` comment — the double delivery is specified nowhere); audits/audit-phase-20-close.md:89-113 §F1 (the nine campaign-tier failures this task's campaign run is compared against).
**Complexity:** Medium
**Record impact:** the record itself — 1,613 rendered `You heard a vent use in ROOM.` rows leave the meeting prompts, and the freed render budget can admit other rows, so this is a rendered-bytes change. Committed bytes do not move here: the corrected substrate is recorded once, by the combined re-record at 21.15.
**Measurement:** `uv run pytest tests/observation/test_service.py tests/agents/test_perception.py tests/agents/test_features.py tests/orchestrator/test_meeting_integration.py tests/api/test_leak.py -q` green (the flipped co-emission pin, the teammate-residue case, the non-witness case, the sabotage-alarm case, and every packet-constructed read-path test unedited); `bash scripts/verify_samples.sh` reports 100/100 committed samples reconstructing byte-identically; `uv run pytest -m campaign -q` is run and its failure set compared item by item against the nine recorded in audits/audit-phase-20-close.md §F1, with any new failure named by test id and routed rather than re-pinned here.

Every witnessed vent is written into memory twice. The engine emits one event — for
samples/9p2i seed 0 the walk shows row t7 `VentExited actor p-6 destination ENGINEERING
destination_witnesses ['p-5']` — and p-5's meeting-0 prompt carries two rows with two
citable observation ids: `- [obs p-5:8:1] [tick 8] You witnessed p-6 vent in ENGINEERING.`
and `- [obs p-5:8:2] [tick 8] You heard a vent use in ENGINEERING.` The derivation is
mechanical. `observation/service.py:366-375` builds `vent_rooms` from `observed_actions`
whose `action == "vent"`, and those entries exist only for an agent already in the event's
witness set: `_vent_observation_for_agent` (:526-543) returns `None` otherwise and copies
the witnessed room straight into `audible_room`. The sound is a function of the sight. A
player who did not see the vent hears nothing, and a player who saw it hears it a second
time.

The census reproduces at HEAD. Scanning every meeting row's recorded `llm_calls[].prompt`
across the four committed sets (50 samples/9p2i + 150 ml_corpus/9p2i + 50 samples/4p1i +
50 ml_corpus/4p1i) for the two rendered line shapes: 1,531 prompts carry at least one
heard-vent row; 1,613 heard-vent rows in total; 1,505 `(tick, room)` pairs are rendered
BOTH ways inside one prompt — exactly the finder's and the verifier's numbers. The 108
heard rows with no witnessed twin in the same prompt collapse to 27 distinct
`(set, seed, agent, tick, room)` keys, and re-deriving the speaker's role from the
impostor persona marker in that same prompt gives 27 impostors and 0 crewmates, again
exactly as recorded. One line of the register does not reproduce under this re-run's
population, and nothing here rests on it: "witnessed-only (tick,room): 0". Inside those same
1,531 heard-carrying prompts the re-run counts 318 pairs witnessed-without-heard, which is what a
salience-ordered render budget does to the lower-salience twin (`agents/memory/store.py:64-65`:
witnessed 85, heard 75). That detail matters for 21.15 rather than for the repair: removing
the duplicate is not a pure deletion, because a freed budget slot can admit a different row.

Why a pure duplicate is a defect and not a harmless echo: this substrate runs
observation-id rendering and a citation gate, so one physical event carrying two ids lets
two "independent" citations be built from one perception, and it makes the corpus's
strongest evidence channel look twice as dense as the world is. Nothing specifies the double
delivery — DESIGN.md:413 lists the field and its two kinds and says nothing about delivering
one event through both — which is why the verifier labelled this defect rather than
documented behaviour.

The second half is newer and is the reason this is a firewall task. The §4.7 team-internal
firewall drops an impostor's sighting of a fellow impostor at a kill room and tick
(`agents/memory/store.py:1045-1081`, applied to the sighting line at :1800-1808), so the
`You witnessed <teammate> vent` row never reaches that impostor's prompt. The audible
derivative is rendered unconditionally at :1599-1607, so what survives is a row telling the
impostor "a vent happened in this room, this tick" — 27 of 27 such rows in the committed
record belong to impostors. The verifier's anchor is ml_corpus/9p2i seed 1026: row t7
`Killed actor p-6 target p-3 room ADMIN`, then row t8 `VentEntered actor p-6 room ADMIN
witnesses ['p-9']` — an impostor watching its teammate vent in the kill room, the exact
`_sighting_is_suppressed` case, with the same row showing that p-9's own vent carries
`witnesses []` (the engine never lists an actor as its own witness), so this is the teammate
branch and not the self-subject branch. The leaked bit is information that impostor already
holds, so it is bounded and it is not a role leak; but a suppression that does not suppress
is a broken mechanism, and it is exactly the residue that would carry real information the
day a non-witness audible channel exists.

The ruling is one perception per physical event per agent, enforced at the mint. The audible
copy is not filtered after the fact and it is not routed through a second copy of the
firewall: it stops being minted, which is the strongest form of routing it through the same
firewall the visual copy passes — the copy and the original become one row, so one
suppression decision covers both and the residue class becomes unreachable rather than
merely filtered. Concretely, `_audible_events` loses its vent derivation entirely (retire
means delete, AGENTS.md craft rule 3): the method keeps only the global `sabotage_alarm`,
its now-unused `observed_actions` parameter goes, and with it the dead
`_ObservedAction.audible_room` field and its write. No lever, no env gate, nothing to
register in the substrate stamp — this is an unconditional repair, like every other Wave-1a
task, and it rides the 21.15 re-record with them.

No evidence leaves the crew's hands. Every row this removes is one of two kinds: a duplicate
of a row the same prompt already carries at higher salience (1,505 of them), or a row held by
an impostor who watched its own teammate vent and therefore already knows what happened (the
27 residue keys). A witness keeps `[tick T] You witnessed P vent in ROOM.` with its
observation id and its salience of 85; a non-witness keeps what it had, which was nothing.
That is the test of whether this repair is neutral for the crew's evidence and aggressive
only against fiction, and the PR should assert it in those terms rather than by counting
deleted lines.

What deliberately stays is the READ path. `AudibleEvent.kind` keeps both members, the
perception map at `agents/perception.py:84-87` keeps its entry (the coupling test at
tests/agents/test_perception.py:812-818 pins the map's key set to the Literal's members),
the heard-row render, `AudibleEventView`, and the frontend type all stay: they are how a
heard row is read wherever one exists — the committed prompts carry 1,613 of them, the
memory-render fixture at tests/fixtures/memory_rendering/tight_budget_drops_low_salience.json:33
exercises the render, and the sabotage alarm shares every one of those surfaces. Building a
GENUINE non-witness audible channel — deriving the sound from the vent event's room so
adjacent players hear something the crew can use — is the other half of A-31's fix sketch and
is a NON-GOAL here: it widens the substrate and adds crew evidence, which is lever-shaped
work for Wave 2, not an unconditional repair. This task removes a duplicate; it must not add
a signal.

Blast radius, grep-verified and left alone. The only reader of `packet.audible_events` under
`agents/` is the ML encoder (`agents/tactical/features.py:373-378`, feeding the fixed scalar
slots named at :160-161) — the FSM policies never read it, so rule-based rollouts and the
scenario state-hash chains should not move, and if one does, that is evidence the change
reached a policy path and the PR says so instead of re-pinning. The `heard_vent_use` slot
keeps its index and `ENCODER_VERSION` stays `"v2"`: the layout does not change, only the
value a live packet produces, which becomes structurally 0 for vents. Learned-policy rollouts
CAN therefore move, and any campaign-tier pin that moves is reported and routed to the ML
re-ground (21.17), never re-pinned here — the tier is already RED at HEAD with the nine
failures recorded in audits/audit-phase-20-close.md §F1, so this task's campaign run is a
comparison against that list, never a green claim. `agents/memory/beliefs.py:530-534` already
records that the room-only row is not a Rule-4 signal, so no suspicion scalar moves, and the
packet's JSON shape is unchanged: `observation/packet.py:192-204` omits only `moved_players`
when empty, so `audible_events` was already serialized as `[]` on every tick without a sound.

Coordination. The committed record — baseline 7, canon by explicit owner override of a
FINDING verdict — is untouched by this PR: `scripts/verify_samples.sh` replays recorded
actions against the recorded state-hash chain and is unaffected by packet contents, so it
stays 100/100 and is the proof that nothing moved yet. `agents/memory/store.py` and
`agents/memory/working.py` belong to Task 21.4 in this phase and are not edited here; no
prompt template moves (Task 21.1 owns the only prompt-set bump); the recorded-action
dispositions and ballot provenance belong to 21.3; and B-28's missing entitlement gate for
`audible_events` in `eval/leak_scan.py` stays open — removing the only live producer of
`vent_use_heard` shrinks what that hole can hide, but it does not close it.

**Files in scope:**
- observation/service.py; (delete the vent derivation in `_audible_events` :366-378, its `observed_actions` parameter and the call-site kwarg at :316-319, plus the then-dead `_ObservedAction.audible_room` field at :195 and its write at :539-543)
- tests/observation/test_service.py; (the co-emission pin at :205-249 flips; the teammate-residue, non-witness and sabotage-alarm cases are added)
- observation/packet.py; (one comment above `AudibleEvent` at :150-152 stating which kinds a live packet can carry and why)
- api/schemas.py; (the `AudibleEventView` docstring at :188-197 stops describing a vent-heard channel no producer mints)
- frontend/src/components/EventTicker.tsx; (the fog comment at :43-46 states the mechanism as built — comment only, no behaviour)

**Files NOT in scope:**
- agents/memory/store.py, agents/memory/working.py (Task 21.4 owns the render and belief-line file this phase; the residue dies at the mint, so no render edit is needed and the heard-row render at :1599-1607 stays as the read path for committed bytes)
- agents/perception.py (the ingest map at :84-87 and the loop at :231-241 are read path; the coupling test pins the map to `AudibleEvent.kind`, so the kind stays)
- agents/tactical/features.py (the `heard_vent_use` slot keeps its index; the layout is version-pinned by `ENCODER_VERSION` and its golden test, and the re-fit that reads the slot's new value is Task 21.17's)
- agents/memory/beliefs.py (:530-534 already documents that the room-only row is not a Rule-4 signal — no edit, quote it in the PR)
- eval/leak_scan.py, eval/leak_test.py, tests/observation/test_leak_property.py (B-28's entitlement gate for `audible_events` is a separate CONFIRMED finding, not routed to this task; do not widen scope into it)
- api/replay_loader.py (:1452-1462 and :2722-2747 describe the audio field by its producer and stay true after this change)
- DESIGN.md (:413 lists the field; the double delivery is specified nowhere, so there is no design ruling to amend)
- agents/strategic/prompts/ (no template moves here — Task 21.1 owns the only prompt-set bump)
- replays/ (no re-record: Task 21.15 owns the record on the corrected substrate)

**Definition of done:**
- [ ] The new assertions are written FIRST, and the PR quotes the HEAD run that splits them: the witness case and the teammate-residue case FAIL before the edit (that is the gate biting), the non-witness and sabotage-alarm cases PASS before it and ship as regression guards. A mint-side gate added before its failing test proves nothing (AGENTS.md craft rule 2).
- [ ] `ObservationService._audible_events` no longer derives any `AudibleEvent` from `observed_actions`: the vent-room comprehension at :366-375 and the `events.extend` at :376-378 are deleted rather than disabled, the parameter and the call-site kwarg at :316-319 go with it, and the remaining body emits exactly the global `sabotage_alarm` (`room=None`) while `world_state.sabotage.active`. The method gains a one-line docstring stating what it emits and that a witnessed vent is delivered once, as the visible action — intent, not history (craft rule 1).
- [ ] `_ObservedAction.audible_room` (:195) and its write in `_vent_observation_for_agent` (:539-543) are deleted, since nothing reads them afterwards; `_vent_observation_for_agent` still returns the witnessed room as `room` and still returns `None` for a non-witness, unchanged.
- [ ] `tests/observation/test_service.py::test_vent_witness_sees_vent_action_and_audible_event` is rewritten and renamed to pin the new rule from the same scripted vent: the witness's `visible_players` entry for the actor carries `action == "vent"` and `packet.audible_events == ()`.
- [ ] A teammate-residue case is added in the same file, built from the real service on the shape the verifier anchored (ml_corpus/9p2i seed 1026: an impostor witnessing a FELLOW impostor vent in a room where that teammate has just killed): the packet carries the vent as a visible action and carries no `AudibleEvent`, so the 27-row residue class has no row left to survive the §4.7 suppression that drops the sighting line downstream.
- [ ] A non-witness case is added: an agent who is not in `source_witnesses` or `destination_witnesses` gets neither a `vent` action nor any `AudibleEvent` — the "heard-but-unseen is not a state the bytes contain" claim, asserted rather than narrated.
- [ ] The sabotage alarm is pinned in the same file so the deletion cannot over-reach: with an active sabotage the packet carries exactly one `AudibleEvent(kind="sabotage_alarm", room=None)`, and it is still present on a tick that also has a witnessed vent.
- [ ] The read path is unedited and still green: `tests/agents/test_perception.py:433-449` (packet-constructed ingest), `:812-818` (the Literal↔map coupling), `tests/orchestrator/test_meeting_integration.py:2796-2810` (`test_heard_vent_use_grounds_nothing`), `tests/agents/test_features.py:113-115` and `tests/api/test_leak.py:1019` all pass without modification — if any needs editing, the diff has reached further than this ruling and the PR says why before editing it.
- [ ] The three prose surfaces are true at HEAD after the change: `observation/packet.py`'s comment on `AudibleEvent`, `api/schemas.py`'s `AudibleEventView` docstring (:188-197 currently describes `vent_use_heard` as "an impostor vent heard from the source / destination room"), and `frontend/src/components/EventTicker.tsx:43-46` (whose parenthetical currently explains that the audible cue is derived from the same witness-gated observed action). Each states the mechanism as built, carries no threshold arithmetic or audit ids, and adds at most one provenance line (craft rules 1, 4, 5).
- [ ] The corpus census is restated in the PR from a command the PR prints, not from this contract: a prompt-level scan of `replays/{samples,ml_corpus}/{9p2i,4p1i}/replay-seed-*.jsonl` over meeting rows' `llm_calls[].prompt` reproducing 1,531 heard-carrying prompts, 1,613 heard-vent rows, 1,505 both-rendered `(tick, room)` pairs and 108 residue rows over 27 distinct keys, 27/27 impostor.
- [ ] The PR states the two consequences a reader of the next record needs. First: this is NOT a lever — no `AILIBI_*` gate, no resolver, nothing registered in `orchestrator/replay.py`, so 21.15's `--expect-levers` stays empty and the corrected behaviour is simply the substrate. Second: observation ids are assigned per tick in ingest order (`agents/perception.py:106`), so on a tick that previously carried an audible row every later row's id shifts by one — a within-recording renumbering that is consistent inside any single record and never compared across records.
- [ ] `bash scripts/verify_samples.sh` reports 100/100, and the PR states the conclusion it supports: the committed record still reconstructs byte-identically because the walk replays recorded actions against the recorded state-hash chain and never rebuilds a packet's audio field — the rendered bytes move only when Task 21.15 records the corrected substrate.
- [ ] `uv run pytest -m campaign -q` is run and the PR lists its failures beside the nine in audits/audit-phase-20-close.md §F1. Any failure not on that list is named by test id with the reason it moved and routed — corpus/fit pins to Task 21.17, the mover scenario pin to Task 21.13 — and is NOT re-pinned in this PR. The PR must not describe the tier as green.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `cd frontend && npm run lint && npm run tsc:check && npm run build` pass (the TypeScript edit is comment-only, so this is a no-regression check, not evidence of behaviour).
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

Step 1 — read the two anchors before touching anything. `observation/service.py:359-381` is
the whole producer, and `:526-543` is why its input set is witnesses-only. Confirm for
yourself that `observed_actions` can only carry `action == "vent"` for an agent in the
event's witness tuples; that single fact is what makes the deletion — rather than a filter —
correct, and it is what the PR should state in one sentence.

Step 2 — write the four test cases first and record which of them bite at HEAD: the witness
case and the teammate-residue case FAIL there (both currently receive the audible copy),
while the non-witness and sabotage-alarm cases PASS and ship as regression guards. Say which
is which in the PR — a checklist that reports four green tests without that split hides the
fact that only two of them proved anything. `tests/observation/test_service.py` already has
everything needed:
`_base_world_state`, `_player`, `_action`, `_observation_service(tmp_path)`,
`_visible_player` and the `advance_tick(...)`-driven shape used by the existing vent test at
:205. For the residue case, place two impostors and a crewmate in one room, resolve the kill,
then vent the killer on the next tick with the second impostor still present, and assert on
the SECOND impostor's packet. Assert `packet.audible_events == ()` directly rather than
filtering it: the point is that the tuple is empty, not that vents are absent from it.

Step 3 — the deletion. Remove the `vent_rooms` comprehension and its `events.extend(...)`,
drop the `observed_actions` keyword from the signature and from the `build_packet` call at
:316-319, then delete `_ObservedAction.audible_room` and the `audible_room=` argument at
:542. `mypy --strict` will find any reader you missed; `grep -rn "audible_room"` should
return nothing outside `.claude/worktrees/` when you are done.

Step 4 — the prose. Three edits, each one or two lines. Do not enumerate this task's history
in them; say what a live packet can carry (`sabotage_alarm` only, `room=None`), and — where
the surface names `vent_use_heard` — that it is a kind the schema still reads and no live
path mints. `api/schemas.py`'s docstring is the one that is outright false after the change;
the EventTicker comment's conclusion survives but its mechanism sentence does not.

Step 5 — the hand-off note for the record. The corrected render frees a budget slot on any
prompt where the heard row was competing (`agents/memory/store.py:64-65` ranks it below the
witnessed row at 75 against 85), so the 21.15 legs will see prompts that are not simply the
old prompts minus one line. Nothing to implement — but say it in the PR, because a reviewer
comparing an old and a new prompt side by side needs to know that an ARRIVING row is expected
behaviour and not a second defect.

Step 6 — blast radius before you push. `grep -rn "vent_use_heard" --include="*.py"
--include="*.ts" --include="*.tsx" --include="*.json" .` (excluding `.claude/worktrees/`)
enumerates every consumer; every hit outside this task's files in scope must be a READ of the
kind, not a mint. Then run the campaign tier as its own step — the default filter is
`-m 'not campaign'`, so the ES/bakeoff machinery whose encoder reads `heard_vent_use` does
not run unless you ask for it, and that is precisely the code whose inputs this change
narrows. If a failure appears that is not one of §F1's nine, name it and route it; this task
does not re-ground ML pins.

## Dependency contract check
Run these before editing. If any fail, stop and report — your dependencies are not where this task expects them.

- `uv run python -c "import orchestrator.replay"`
- `uv run python -c "import meetings.schemas"`
- `uv run python -c "import eval.replay_walk.ReplayWalkConfig"`

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

## Verification checklist
- Run every command listed in the Definition of done.
- If the contract carries a `**Measurement:**` field, run that command and paste its output into the PR's `## Summary`; a Measurement that cannot be run is reported under `## Questions`, never asserted.
- Run `git diff --name-only` and confirm the diff stays within scope.
- If any Definition of done item is unchecked, report it explicitly in the PR description instead of declaring the task complete.

## Decisions vs questions
- If something is **ambiguous and blocking** (you cannot make a reasonable choice without further information): stop, open a draft PR, add a `## Questions` section, request review.
- If something is **ambiguous but resolvable by judgment** (a default value, a tie-break, a naming choice): document the choice in a `## Decisions` section in the PR description and proceed.

## Output expectation
Open a PR from branch `phase-21-vent-mint` with a title like `task 21.5: one vent, one record: the double mint and the audible copy that leaks through the teammate firewall`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing A-31 [CONFIRMED, P2, defect] — audits/review-2026-08-26/A/collated-findings.md:3501-3597 (the claim, the finder's prompt-level census, the verifier's independent re-run, and the verifier note's two binding additions: the redundancy half is PRIOR ART — audits/review-2026-08-19/B/observation-firewall.md:155 F13 and idea #21 at audits/review-2026-08-19/A/collated-findings.md:587, so the novelty is the 27-row firewall residue, not the duplicate; and the co-emission is PINNED by a shipped test the fix must update); B-28 [CONFIRMED, P2, quality-debt] — audits/review-2026-08-26/B/collated-findings.md:1688-1729, read as context only and explicitly NOT fixed here (`grep -c audible eval/leak_scan.py` → 0 at HEAD, re-run). Anchors re-verified at HEAD `4002f19b`: observation/service.py:359-381 `_audible_events` — the method spans :359-381 at HEAD (the register cites it as :359-377 in A-31's finder evidence and :359-380/:359-381 elsewhere; the vent derivation proper is the comprehension at :366-375 plus the `events.extend` at :376-378), :526-543 `_vent_observation_for_agent` (returns `None` unless `agent_id` is in `event.source_witnesses` / `event.destination_witnesses`, and copies the witnessed room into `audible_room` at :539-543), :192-195 `_ObservedAction` (`audible_room` at :195), :316-319 the `build_packet` call site; observation/packet.py:150-152 `AudibleEvent` (`kind` is `Literal["vent_use_heard", "sabotage_alarm"]`), :181 the packet field, :192-204 the serializer (only `moved_players` is omitted when empty, so the field's JSON shape does not move); agents/perception.py:84-87 `_AUDIBLE_EVENT_TYPES`, :106 the ingest-order docstring, :231-241 the ingest loop; agents/memory/store.py:64-65 (`_SALIENCE_VENT_WITNESSED` 85, `_SALIENCE_VENT_HEARD` 75), :1045-1081 `_sighting_is_suppressed`, :1800-1808 its call in `_render_saw_player`, :1810-1816 the witnessed-vent line, :1599-1607 the heard-vent render, :1986-2004 `_render_heard`; agents/memory/beliefs.py:530-534 (the room-only row "carries no subject and is deliberately not used" by Rule 4); agents/tactical/features.py:107 `ENCODER_VERSION = "v2"`, :160-161 the `heard_vent_use` / `heard_sabotage_alarm` slots, :373-378 and :407-408 the only reader of `packet.audible_events` in `agents/`; api/schemas.py:188-197 `AudibleEventView`; api/replay_loader.py:1452-1462 and :2722-2747 (the audio-field docstrings and the projection); frontend/src/components/EventTicker.tsx:43-46, frontend/src/types/api.ts:140; the shipped pin the verifier names — tests/observation/test_service.py:205 `test_vent_witness_sees_vent_action_and_audible_event` with the co-emission assertion at :245-249 (the register's ":240-249" is the surrounding block); the read-path tests that stay green unedited — tests/agents/test_perception.py:433-449 and :812-818 (the Literal↔map coupling test), tests/orchestrator/test_meeting_integration.py:2796-2810 `test_heard_vent_use_grounds_nothing`, tests/agents/test_features.py:113-115, tests/fixtures/memory_rendering/tight_budget_drops_low_salience.json:33; DESIGN.md:413 (the field is listed with a `# vent use heard, sabotage alarm` comment — the double delivery is specified nowhere); audits/audit-phase-20-close.md:89-113 §F1 (the nine campaign-tier failures this task's campaign run is compared against).), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
