# Agent Prompt — 20.23 Completed-task memory comes from the engine event, not a pending-id flip

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-20.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 20.23 — Completed-task memory comes from the engine event, not a pending-id flip, anchored to G-3 (audits/review-2026-08-19/A/collated-findings.md §G-3, severity P0, corroboration 5; audits/review-2026-08-19/A/verdicts.md §claim 3 — VERDICT CONFIRMED-BUG, with the four-set prevalence table, the 100% redistribution correlation and the three minted STRONG flags) and C-2 (audits/review-2026-08-19/B/collated-findings.md §C-2 row, severity P1; audits/review-2026-08-19/B/verdicts.md §claim 4 — VERDICT CONFIRMED, with the engine+ObservationService+ingest+render repro); audits/review-2026-08-19/D/FINAL-synthesis.md §1 RC3 (the root cause) and §4 wave-2 row 2.1 (the roadmap item this task implements); agents/memory/store.py:1155-1207 (the inference inside `_build_observations`), :1161-1168 (the false invariant comment), :1170-1177 (the PR #155 impostor-gate rationale), :1179 (the `role == "CREWMATE"` gate), :1189-1203 (the emit), :78 (`_SALIENCE_COMPLETED_TASK`); engine/tick.py:314-367 (`redistribute_dead_tasks`), :365-366 (the owned set GROWS), :401 (the kill-path call); orchestrator/game.py:1235 (the ejection-path call), :2026-2027 (dead players get no packet); engine/maps/canonical_1.yaml:45 (`dead_task_rule: redistribute`); observation/service.py:638-645 (the lexicographically-first pending pick), :647-691 (`_owned_task_ids_for_agent`, impostor branch :672-683); observation/packet.py:73 (`SelfView.owned_task_ids`, present since 15.22); agents/perception.py:326-361 (`_self_state_payload`, records no `owned_task_ids`); tests/agents/test_memory_rendering.py:835-852 (the pin that enshrines the wrong rule); tests/agents/test_perception.py:128-135 (the exact self-state payload assertion); the lever pattern — agents/strategic/prompts/loader.py:321-364 (the live default-OFF `*_enabled(env)` resolver) and orchestrator/replay.py:547-572 (`_TOGGLEABLE_LEVER_RESOLVERS`); the OFF-path instruments — tests/meetings/test_prompt_byte_golden.py:1-40 and scripts/verify_samples.sh:1-24. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-20.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-20-completion-from-events`
**Depends on:** 20.15 — the evidence-honesty instrument set must land first: its committed I-5 fabricated-completion cell is the OFF number this task's ON path must drive to zero, and re-running it green is the proof that the perception widening moved no cell; the ON census over the committed games belongs to the offline-counterfactual task, which owns the only OFF/ON entry point (audits/audit-phase-20-preregistration.md §8).; also after 20.22 (no lever merges before the bars are ratified); also after 20.32 (the mover repair and its I-11 instrument-mode change land before any lever, so the levers’ counterfactual pins read one instrument shape and the comparator is repaired before the freeze)
**Section refs:** G-3 (audits/review-2026-08-19/A/collated-findings.md §G-3, severity P0, corroboration 5; audits/review-2026-08-19/A/verdicts.md §claim 3 — VERDICT CONFIRMED-BUG, with the four-set prevalence table, the 100% redistribution correlation and the three minted STRONG flags) and C-2 (audits/review-2026-08-19/B/collated-findings.md §C-2 row, severity P1; audits/review-2026-08-19/B/verdicts.md §claim 4 — VERDICT CONFIRMED, with the engine+ObservationService+ingest+render repro); audits/review-2026-08-19/D/FINAL-synthesis.md §1 RC3 (the root cause) and §4 wave-2 row 2.1 (the roadmap item this task implements); agents/memory/store.py:1155-1207 (the inference inside `_build_observations`), :1161-1168 (the false invariant comment), :1170-1177 (the PR #155 impostor-gate rationale), :1179 (the `role == "CREWMATE"` gate), :1189-1203 (the emit), :78 (`_SALIENCE_COMPLETED_TASK`); engine/tick.py:314-367 (`redistribute_dead_tasks`), :365-366 (the owned set GROWS), :401 (the kill-path call); orchestrator/game.py:1235 (the ejection-path call), :2026-2027 (dead players get no packet); engine/maps/canonical_1.yaml:45 (`dead_task_rule: redistribute`); observation/service.py:638-645 (the lexicographically-first pending pick), :647-691 (`_owned_task_ids_for_agent`, impostor branch :672-683); observation/packet.py:73 (`SelfView.owned_task_ids`, present since 15.22); agents/perception.py:326-361 (`_self_state_payload`, records no `owned_task_ids`); tests/agents/test_memory_rendering.py:835-852 (the pin that enshrines the wrong rule); tests/agents/test_perception.py:128-135 (the exact self-state payload assertion); the lever pattern — agents/strategic/prompts/loader.py:321-364 (the live default-OFF `*_enabled(env)` resolver) and orchestrator/replay.py:547-572 (`_TOGGLEABLE_LEVER_RESOLVERS`); the OFF-path instruments — tests/meetings/test_prompt_byte_golden.py:1-40 and scripts/verify_samples.sh:1-24
**Complexity:** Medium
**Record impact:** lever-gated (default-OFF) until the Phase-20 adopting record
**Measurement:** `uv run pytest tests/agents/test_memory_rendering.py tests/agents/test_perception.py tests/eval/test_evidence_honesty.py -q` green; `uv run python scripts/measure_baseline.py --honesty replays/samples/9p2i` reports the committed OFF cell (the ratified pin 19/458 over rendered rows that reached a model; the review's offline re-render measured 53/529) with `AILIBI_TASK_COMPLETION_FROM_EVENTS=1` exported AND with it unset — the instrument scores I-5 off the recorded prompt bytes and exposes no lever slate by design (audits/audit-phase-20-preregistration.md §8), so the ON census over the 300 committed games is Task 20.34's `scripts/counterfactual_phase20.py` and the ON rule here is fixture-pinned in tests/agents/test_memory_rendering.py; and `bash scripts/verify_samples.sh` plus the prompt byte-golden stay green with the lever unset.

The memory store mints first-hand completions that never happened. `agents/memory/store.py:1161-1166`
justifies its inference on an invariant — "Its owned set only ever shrinks -- a task completes; none is
added mid-game -- so the pending id changes if and only if the previous pending task completed" — that
`engine/maps/canonical_1.yaml:45` broke two phases later: under `dead_task_rule: redistribute` a victim's
unfinished instances are re-keyed onto living crewmates (`engine/tick.py:365-366`, reached from the kill
path at :401 and the ejection path at `orchestrator/game.py:1235`), so a live crewmate's owned set GROWS
mid-game. `observation/service.py:638-645` then hands the packet the lexicographically-first owned
unfinished map id, so an inherited earlier-sorting task silently displaces the pending id and
`store.py:1178-1203` renders `[tick N] You completed X (you were in ROOM).` for a task the agent never
touched. The line carries an `observation_id`, so it is citable evidence in the meeting. Both review
tracks confirmed it independently with separate repros: A/verdicts.md §claim 3 (CONFIRMED-BUG) and
B/verdicts.md §claim 4 (CONFIRMED), and D/FINAL-synthesis.md §1 RC3 names it a root cause.

The review-measured rates over the committed baseline-6 bytes: 53/529 = 10.0% of rendered completion
lines in samples/9p2i, 15/65 = 23.1% in samples/4p1i, 140/1528 in ml_corpus/9p2i, 14/64 in
ml_corpus/4p1i — 159 of the 300 committed games hit, 67 of the false lines spoken at the table, and 3 of
them minted STRONG `alibi_vs_sighting` flags against innocents (s11 p-6 `upload_logs@14 MEDBAY`, s46 p-1
`fuel_reserves@10 ADMIN`, s13 p-5 `fuel_reserves@14 LABS`), per A/verdicts.md §claim 3. The correlation
with redistribution is 100%, not merely enriched: of the false lines in `samples/`, 58 sit at T−1/T−2 of a
crewmate kill and the remaining 7 at T−1 of a meeting ejection — both paths call `redistribute_dead_tasks`.
Because the inference is gated to `role == "CREWMATE"` (store.py:1179 — the Task-10.14 / PR #155 fix that
kept the impostor's rotating pretend id from minting fiction), the damage is strictly one-sided: the crew
poisons its own first-hand channel, on exactly the tick the next meeting litigates, while the impostors
are exempt. The store's own comment at :1174-1176 names the failure it is now suffering — a fabricated
`completed_task` alibi that "corrupt[s] the meeting/eval evidence".

The fix is to key the inference on the true invariant instead of the broken one. For a LIVING agent the
owned set loses an id only when that instance completes: redistribution only ever ADDS to a survivor
(`engine/tick.py:365-366`) and only ever empties the VICTIM, who receives no further packet
(`orchestrator/game.py:2026-2027`). So "an id that was in `owned_task_ids` last tick and is absent this
tick" is a truthful completion signal available entirely inside the observation firewall — strictly better
than the pending-id flip, because it also catches the completion the current rule DROPS (a genuine
completion whose pending id was already displaced by an inherited earlier-sorting task). It costs one
recorded field: `SelfView.owned_task_ids` has existed since Task 15.22 (`observation/packet.py:73`) but
`agents/perception.py:355-361` never writes it into the self-state payload, which is why the store
"genuinely cannot see the set" (B/verdicts.md §claim 4). The role gate then goes away without reopening
PR #155: an impostor's `owned_task_ids` is the per-seat camouflage WINDOW from
`observation/service.py:672-683`, which is constant for the whole game (no tick argument; seats are taken
over all `role == "IMPOSTOR"` players alive or dead), so the rotating pretend id never leaves it and the
disappearance rule mints nothing for an impostor — by construction, not by a role bit.

Everything ships behind `AILIBI_TASK_COMPLETION_FROM_EVENTS`, default-OFF, so the committed baseline and
every gate stay green until the Phase-20 adopting record. OFF-path bytes are identical (the perception
field is additive and unread; the render path is unchanged), pinned by the prompt byte-golden and
`scripts/verify_samples.sh` over the 100 committed sample games and by the honesty instrument's OFF cells
reproducing the review's numbers over all four sets. ON-path behaviour is fixture-pinned and paid for with
the counterfactual the record's gate reads: re-render the 300 committed games under the lever and publish
the fabricated-completion census, which must be 0. This task does NOT re-date or re-room the line (the
uniform +1 agent-clock stamp and the room-at-that-tick belong to the self-location trail task), does NOT
register the lever in the substrate stamp (Task 20.33 registers all eight Phase-20 levers at once), and
touches no prompt template (Task 20.31 owns the single prompt-set bump).

**Files in scope:**
- agents/memory/store.py; (the lever: the `task_completion_from_events_enabled` resolver beside `observation_id_rendering_enabled`, the env constant, the read once in `render_for_prompt` threaded into `_build_observations`, the ON-path disappearance rule, the deleted false-invariant comment, `__all__`)
- agents/perception.py; (record `owned_task_ids` into `_self_state_payload` — additive, one key, only read under the lever)
- agents/memory/working.py; (only if the self-state model needs the field — the episodic payload is `Mapping[str, Any]`, so the expected diff is empty)
- tests/agents/test_memory_rendering.py; (the wrong-rule pin replaced; OFF-path byte-identity; ON-path: a redistribution never mints a completion, a real completion still renders, a payload without the field renders nothing)
- tests/agents/test_perception.py; (the exact-payload assertion at :128-135 gains `owned_task_ids`)
- tests/eval/test_evidence_honesty.py; (the committed I-5 pins re-run unchanged after the perception widening — the instrument rebuilds memory through `agents.perception` — plus a lever-exported-ON re-read proving it is inert; the ON census is the offline-counterfactual task's)
- observation/service.py; (the :63-66 comment only — the same false invariant in prose; no behaviour change)

**Files NOT in scope:**
- engine/ (redistribution is correct engine behaviour and DESIGN.md §3.5's sanctioned variant; nothing about the rule changes)
- orchestrator/replay.py (Task 20.33 registers this lever in `_TOGGLEABLE_LEVER_RESOLVERS` and the substrate stamp, together with the other Phase-20 levers; this task registers nothing)
- agents/strategic/prompts/ (Task 20.31 owns the single prompt-set bump; no template may move here)
- the line's tick and room (the self-location trail task owns the re-dating and the room-at-that-tick; this task must not shift a genuine completion's tick or room relative to the OFF path)
- replays/ (no bytes are re-recorded; the record is Task 20.36)

**Definition of done:**
- [ ] With `AILIBI_TASK_COMPLETION_FROM_EVENTS` unset, rendered memory and rendered prompts are byte-identical: `tests/meetings/test_prompt_byte_golden.py` and `bash scripts/verify_samples.sh` stay green over the 100 committed sample games, the three `tests/fixtures/memory_rendering/*.expected.md` fixtures are untouched, and the honesty instrument's OFF fabricated-completion cells still read the committed values over all four sets.
- [ ] `agents.memory.store.task_completion_from_events_enabled` follows the 13.5 signature `(env: Mapping[str, str] | None = None) -> bool`, reads `AILIBI_TASK_COMPLETION_FROM_EVENTS` from the passed mapping (defaulting to the process environment), accepts `1/true/yes/on` case-insensitively, is read exactly ONCE in `render_for_prompt` and threaded down as a boolean, and is pinned both ways in `tests/agents/test_memory_rendering.py` without mutating `os.environ`.
- [ ] `agents/perception.py::_self_state_payload` records `owned_task_ids` from `packet.self_state`; `tests/agents/test_perception.py` asserts the new exact payload for a crewmate AND an impostor, and asserts the field is the packet's tuple verbatim (no re-sorting, no filtering).
- [ ] With the lever ON, a crewmate whose pending task is displaced by a redistributed instance renders NO completion line — the fixture reproduces B/verdicts.md §claim 4's repro shape (pre-kill pending `upload_logs`, post-kill pending `align_engine_output`, `upload_logs` still owned) and asserts `"You completed" not in view`.
- [ ] With the lever ON, a genuine completion still renders `[tick N] You completed X (you were in ROOM).` with the same tick, room and `observation_id` as the OFF path — including the rollover case the old pin covered, the final-clear case, and the case the OLD rule dropped: a task that completes while the pending id is already held by an inherited earlier-sorting instance now renders its completion.
- [ ] The `role == "CREWMATE"` asymmetry is gone: the ON path applies the same rule to both roles, and a test drives an impostor's rotating pretend `pending_task_id` over a constant camouflage window and asserts zero completion lines — the PR #155 property held by construction rather than by a role gate.
- [ ] Fail-closed on missing evidence: a self-state payload without an `owned_task_ids` key (a hand-built fixture or a pre-widening row) mints NO completion under the lever ON, pinned by a test — the ON path never fabricates when it cannot see the set.
- [ ] `tests/agents/test_memory_rendering.py:835-852 test_pending_rollover_to_next_map_id_emits_completion` no longer pins the any-change-emits rule; it is rewritten to pin the disappearance rule (or replaced by named ON/OFF tests) and its comment states why the old premise was false.
- [ ] `tests/eval/test_evidence_honesty.py::test_i5_fabricated_completion_pins` still reads 19/458, 40/1311, 15/61 and 14/58 — unchanged by the perception widening and unchanged with `AILIBI_TASK_COMPLETION_FROM_EVENTS=1` exported, because the instrument scores I-5 off the recorded prompt bytes and deliberately exposes no lever slate (audits/audit-phase-20-preregistration.md §8); the ON census over the four sets is Task 20.34's, and this PR quotes the OFF column beside the fixture-level ON proof.
- [ ] The false invariant comment at `agents/memory/store.py:1161-1168` is deleted; the replacement states the true rule in one sentence plus one provenance line (no docstring history narration), and the impostor-gate rationale at :1170-1177 is rewritten to say the property now holds by construction.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

Step 1 — the field. `_self_state_payload` (agents/perception.py:326-361) gains one key,
`"owned_task_ids": self_state.owned_task_ids`, beside `pending_task_id`. It is a tuple of map ids; keep it
a tuple (the payload already carries `fellow_impostor_ids` as one). Nothing else in production reads the
self-state payload's shape — the tactical policies read named keys (agents/tactical/impostor_policy.py:467,
agents/tactical/crewmate_policy.py:430) and the training features read `packet.self_state.owned_task_ids`
directly (agents/tactical/learned/crew_forward.py:728) — so the blast radius is the one exact-dict
assertion at tests/agents/test_perception.py:128-135. Grep before you widen.

Step 2 — the resolver. Put it in agents/memory/store.py next to `observation_id_rendering_enabled`
(:189-208), which is the same module's lever home, but copy the LIVE default-OFF shape from
agents/strategic/prompts/loader.py:321-364 rather than the retired always-True bodies: an
`ENV_TASK_COMPLETION_FROM_EVENTS` constant, a frozenset of truthy strings, `env if env is not None else
os.environ`. Export both from `__all__` (:1886). `render_for_prompt` already takes `env` and already reads
one lever this way at :275-285 — read yours in the same place and pass a plain `bool` into
`_build_observations`; do not thread the mapping into the loop.

Step 3 — the rule. In `_build_observations` (:1117-1207) keep the OFF branch byte-for-byte as it is and
add the ON branch beside it. Track the previous payload's `owned_task_ids` as a frozenset alongside
`last_pending_task` / `last_pending_task_room`; on each `self_state` event, the completed ids are
`previous_owned - current_owned`. Emit at most the ids that were the previous pending task if you want the
minimal diff, or emit each departed id — decide it, state the choice in the comment, and pin it; the
review's cell counts LINES, so a rule that emits more than one line per tick must be reflected in the
counterfactual. Keep the existing tick, room, salience and `observation_id` sources untouched so a genuine
completion's bytes do not move (the trail task re-dates later). If either payload lacks the key, emit
nothing.

Step 4 — the pins. The OFF-path proof already exists: tests/meetings/test_prompt_byte_golden.py
reconstructs every committed meeting through the real render path
(`api.replay_loader.ReplayLoader._walk` with `collect_memory=True`, then `render_for_prompt`), so an
additive payload key that nothing reads under OFF is proven inert by running it. The ON path is
proved by fixture, not by that instrument: the honesty module scores I-5 by matching its
`_COMPLETED_LINE` regex against the recorded `LLMCallRecord.prompt` (eval/evidence_honesty.py:1496-1528)
and takes no lever-slate parameter by design (audits/audit-phase-20-preregistration.md §8), so its cells
cannot move under this lever — Task 20.34's `scripts/counterfactual_phase20.py` owns the OFF/ON census.
Toggle through the `env` parameter, never `os.environ`, so the pins stay parallel-safe.

Step 5 — the numbers. Quote the four RATIFIED OFF cells — 19/458, 40/1311, 15/61, 14/58
(audits/audit-phase-20-preregistration.md §3.1) — not the review's offline re-render (53/529, 140/1528,
15/65, 14/64). §3.2 already rules on the divergence: the pin counts rendered rows that actually REACHED a
model, the review re-rendered memory offline, and the review disagrees with itself on the samples-pooled
total (68 vs 65; the instrument's own recount over the prompt population is 34). Cite that ruling in the
PR; do not re-litigate it.

## Public types this task introduces
- `agents.memory.store.task_completion_from_events_enabled`
- `agents.memory.store.ENV_TASK_COMPLETION_FROM_EVENTS`

These are the symbols downstream tasks will import. Keep their signatures stable.

## Dependency contract check
Run these before editing. If any fail, stop and report — your dependencies are not where this task expects them.

- `uv run python -c "import eval.evidence_honesty"`
- `uv run python -c "import eval.solvability"`

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
Open a PR from branch `phase-20-completion-from-events` with a title like `task 20.23: completed-task memory comes from the engine event, not a pending-id flip`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing G-3 (audits/review-2026-08-19/A/collated-findings.md §G-3, severity P0, corroboration 5; audits/review-2026-08-19/A/verdicts.md §claim 3 — VERDICT CONFIRMED-BUG, with the four-set prevalence table, the 100% redistribution correlation and the three minted STRONG flags) and C-2 (audits/review-2026-08-19/B/collated-findings.md §C-2 row, severity P1; audits/review-2026-08-19/B/verdicts.md §claim 4 — VERDICT CONFIRMED, with the engine+ObservationService+ingest+render repro); audits/review-2026-08-19/D/FINAL-synthesis.md §1 RC3 (the root cause) and §4 wave-2 row 2.1 (the roadmap item this task implements); agents/memory/store.py:1155-1207 (the inference inside `_build_observations`), :1161-1168 (the false invariant comment), :1170-1177 (the PR #155 impostor-gate rationale), :1179 (the `role == "CREWMATE"` gate), :1189-1203 (the emit), :78 (`_SALIENCE_COMPLETED_TASK`); engine/tick.py:314-367 (`redistribute_dead_tasks`), :365-366 (the owned set GROWS), :401 (the kill-path call); orchestrator/game.py:1235 (the ejection-path call), :2026-2027 (dead players get no packet); engine/maps/canonical_1.yaml:45 (`dead_task_rule: redistribute`); observation/service.py:638-645 (the lexicographically-first pending pick), :647-691 (`_owned_task_ids_for_agent`, impostor branch :672-683); observation/packet.py:73 (`SelfView.owned_task_ids`, present since 15.22); agents/perception.py:326-361 (`_self_state_payload`, records no `owned_task_ids`); tests/agents/test_memory_rendering.py:835-852 (the pin that enshrines the wrong rule); tests/agents/test_perception.py:128-135 (the exact self-state payload assertion); the lever pattern — agents/strategic/prompts/loader.py:321-364 (the live default-OFF `*_enabled(env)` resolver) and orchestrator/replay.py:547-572 (`_TOGGLEABLE_LEVER_RESOLVERS`); the OFF-path instruments — tests/meetings/test_prompt_byte_golden.py:1-40 and scripts/verify_samples.sh:1-24), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
