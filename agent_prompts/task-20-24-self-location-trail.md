# Agent Prompt — 20.24 The self-location trail: an agent's memory says where it was

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-20.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 20.24 — The self-location trail: an agent's memory says where it was, anchored to G-1 [audits/review-2026-08-19/A/verdicts.md §"VERDICT: PARTIALLY-TRUE — mechanism is a CONFIRMED-BUG" — the 971-render line-shape census, the 843 completed-task instances, the 16.0% / 97.0% / 100% room-match triple, the 44.3% victim-caused / 21.5% witness-caused split]; audits/review-2026-08-19/A/collated-findings.md §G-1 (P0, corroboration 10, the s30-m3 and 4p1i-s10 exemplars); audits/review-2026-08-19/A/ideas-among-us-veteran.md §V8 (the render shape); audits/review-2026-08-19/D/FINAL-synthesis.md §1 RC1 + §4 wave-2 row 2.2 (the roadmap item this task implements); audits/audit-phase-20-preregistration.md §2 instrument I-2, §3 cell I-2 (148/723 = 20.5% samples/9p2i), §4 bar 3, §8 ("I-2 after the trail exists" is explicitly NOT predictable offline); agents/memory/store.py:1010 + :1024-1028 (`own_room_by_tick`, a LOCAL of `_collect_transitions`, consumed only at :1046 and :1063-1073 to scope OTHERS' sightings), :1178-1203 (the completed-task emission), :1204-1206 (the previous-iteration room roll-forward that mis-rooms it), :189-208 (the resolver signature to clone), :211-217 and :280 (`render_for_prompt`'s `env` thread and the resolve-once read site), :1778-1852 (`_assemble_view`'s block order and budget arithmetic); agents/strategic/prompts/qwen3_6_27b/accusation_round.j2:184 and :209, crewmate_report.j2:96 and :110 (the roll-call ask — "copied from your own record"); DESIGN.md:705 (the §6.6 worked example that specifies a tick RANGE, never built; historical design record per AGENTS.md:20-23); DESIGN.md:473 + orchestrator/game.py:1186-1190 (a meeting freezes movement); meetings/manager.py:2820-2859 (`_normalize_ballot_observation_id` nulls any id outside the voter's own set and splices a marker into `rationale_text`); AGENTS.md:76-110 craft rules 1, 2, 5, 6, 7. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-20.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-20-self-location-trail`
**Depends on:** 20.23 — the completed-task line must already be derived from the engine completion event before this task re-dates it and re-rooms it; both edits land in the same self-state loop of the memory store, and the evidence-honesty instrument arrives transitively along the same chain
**Section refs:** G-1 [audits/review-2026-08-19/A/verdicts.md §"VERDICT: PARTIALLY-TRUE — mechanism is a CONFIRMED-BUG" — the 971-render line-shape census, the 843 completed-task instances, the 16.0% / 97.0% / 100% room-match triple, the 44.3% victim-caused / 21.5% witness-caused split]; audits/review-2026-08-19/A/collated-findings.md §G-1 (P0, corroboration 10, the s30-m3 and 4p1i-s10 exemplars); audits/review-2026-08-19/A/ideas-among-us-veteran.md §V8 (the render shape); audits/review-2026-08-19/D/FINAL-synthesis.md §1 RC1 + §4 wave-2 row 2.2 (the roadmap item this task implements); audits/audit-phase-20-preregistration.md §2 instrument I-2, §3 cell I-2 (148/723 = 20.5% samples/9p2i), §4 bar 3, §8 ("I-2 after the trail exists" is explicitly NOT predictable offline); agents/memory/store.py:1010 + :1024-1028 (`own_room_by_tick`, a LOCAL of `_collect_transitions`, consumed only at :1046 and :1063-1073 to scope OTHERS' sightings), :1178-1203 (the completed-task emission), :1204-1206 (the previous-iteration room roll-forward that mis-rooms it), :189-208 (the resolver signature to clone), :211-217 and :280 (`render_for_prompt`'s `env` thread and the resolve-once read site), :1778-1852 (`_assemble_view`'s block order and budget arithmetic); agents/strategic/prompts/qwen3_6_27b/accusation_round.j2:184 and :209, crewmate_report.j2:96 and :110 (the roll-call ask — "copied from your own record"); DESIGN.md:705 (the §6.6 worked example that specifies a tick RANGE, never built; historical design record per AGENTS.md:20-23); DESIGN.md:473 + orchestrator/game.py:1186-1190 (a meeting freezes movement); meetings/manager.py:2820-2859 (`_normalize_ballot_observation_id` nulls any id outside the voter's own set and splices a marker into `rationale_text`); AGENTS.md:76-110 craft rules 1, 2, 5, 6, 7
**Complexity:** Medium
**Record impact:** lever-gated (default-OFF) until the Phase-20 adopting record
**Measurement:** `uv run pytest tests/agents/test_memory_rendering.py tests/eval/test_evidence_honesty.py -q` green; with the lever unset the three committed render goldens are byte-identical and `bash scripts/verify_samples.sh` is 100/100 clean; with `AILIBI_SELF_LOCATION_TRAIL=1` the pinned self-placement coverage cell reads 100% of crew `whereabouts` claim ticks over each of the four committed sets (the OFF value recorded as measured beside it), and the completed-task room/tick agreement pin reads 843/843 over samples/9p2i

The agent has no record of itself. Across all 971 rendered memories in
`replays/samples/9p2i` the review's line-shape census found 41 distinct "You"
shapes and exactly one that places the agent anywhere: the suffix of `[tick N]
You completed <task> (you were in ROOM).` — 843 instances, and no dated
self-position line of any kind (audits/review-2026-08-19/A/verdicts.md §G-1).
Meanwhile every meeting prompt orders the speaker to answer the roll-call with
"one room, one tick, copied from your own record" (`accusation_round.j2:184`,
`:209`; `crewmate_report.j2:96`, `:110`). There is no such row to copy, so the
model extrapolates: crew `whereabouts` answers name a room the speaker was in
at neither the stated tick nor the tick before it 148/723 = 20.5% of the time
in samples/9p2i and 402/2038 = 19.7% in the corpus (review-measured over the
committed baseline-6 bytes; the same definition is pinned as instrument I-2).
Those inventions are then stamped VERIFIED and convict: of the 79 innocent
ejections corpus-wide, 44.3% are the victim mis-stating its own position and
21.5% are a witness's mis-dated sighting, and games carrying at least one
innocent ejection end in an impostor win 39/68 = 57% against 14/132 = 11%
without.

The one anchor that does exist is itself mis-dated. For all 843 completed-task
lines the agent's real room matches the stated tick only 16.0% of the time,
matches at N−1 97.0%, and at N−2 100% — because `store.py:1204-1206` rolls the
room forward from the PREVIOUS self-state iteration while `:1193-1197` stamps
the CURRENT event's tick. One line, two clocks. `DESIGN.md:705` specified more
than was ever built — `- [tick 380] You completed wiring_admin (you were in
Admin tick 375-385).`, with a range — so the shipped shape is not the designed
one.

The data is already in the store: `store.py:1010` builds `own_room_by_tick`
from the agent's own self-state events at `:1024-1028` and then uses it only
to decide which of OTHERS' sightings happened in the observer's room (`:1046`,
`:1063-1073`). This task is rendering, not modelling: no new perception, no
new engine read, no prompt-template edit (the roll-call ask is unchanged, and
every game template is frozen until the single prompt-set bump task). It
renders the trail the store already keeps as coalesced spans, and it makes the
completed-task line take its tick and its room from one event instead of two.

What ships is a default-OFF lever, `AILIBI_SELF_LOCATION_TRAIL`, resolved by
`self_location_trail_enabled(env)`: with it unset the rendered bytes and every
committed replay reproduce byte-identically, so the baseline-6 gates stay
green until the adopting record. The counterfactual this task can honestly pin
offline is COVERAGE — whether the record the prompt orders the agent to copy
from now exists at the tick under discussion — because whether the model then
copies it is a behavioural question the pre-registration explicitly lists as
not predictable offline (`audits/audit-phase-20-preregistration.md` §8); bar 3
(I-2, 20.5% → < 5%) is judged on the recorded bytes. Two costs are stated
rather than hidden: the block consumes token budget the observations block
used to have, so its cap is pinned against measured claim ticks and its effect
on higher-salience lines is measured; and the impostor gets the same truthful
own-record, which is the design's standing position — the tactical record is
what it is, and fabrication is the LLM's job (DESIGN.md §4.7). Crew inability
to retrace its own route was never a balance mechanism.

**Files in scope:**
- agents/memory/store.py; (the lever: a coalesced self-location trail rendered as "You were in ROOM from tick a to b" spans, plus the completed-task line re-dated to the tick its room belongs to; OFF-path bytes identical)
- tests/agents/test_memory_rendering.py; (OFF byte-identity with a perturbation case; ON: the spans match the per-tick own-room record; the completed-task tick and room agree with the engine event)
- tests/fixtures/memory_rendering/; (a new ON-path expected render fixture pair)
- tests/eval/test_evidence_honesty.py; (the counterfactual: with the trail rendered, the share of crew whereabouts claim ticks that COULD have been copied from the record is 100%; the false-rate bar itself is judged at the record)

**Files NOT in scope:**
- agents/strategic/prompts/ (the roll-call instruction is unchanged; the whole game prompt set moves once, at the prompt-set bump task, and nowhere else)
- meetings/ (grounding the prosecutorial side is its own task; this one changes what the agent can read, not what the detector accepts)
- orchestrator/replay.py (the stamp registration task binds every Phase-20 lever key to its home resolver at once — register nothing here)
- api/replay_loader.py (its `render_for_prompt` call site passes no `env` and therefore reads the same ambient default; with the lever OFF the spectator's `rendered_memory_text` is unchanged)
- eval/evidence_honesty.py and scripts/measure_baseline.py (the instrument module and its emitter belong to the honesty-instrument task upstream; this task consumes them)
- DESIGN.md (the historical design record per AGENTS.md:20-23, cited as evidence, not edited)
- engine/, observation/ (per-tick self-state perception is already correct; nothing new is perceived)

**Definition of done:**
- [ ] `self_location_trail_enabled(env: Mapping[str, str] | None = None) -> bool` lives in `agents/memory/store.py`, reads `ENV_SELF_LOCATION_TRAIL` from `env` or the process environment against the repo's truthy set, and DEFAULTS OFF; it is resolved exactly ONCE in `render_for_prompt` beside the observation-id fold and the boolean is threaded down (no deeper environment read). Pinned in `tests/agents/test_memory_rendering.py` for unset, "0", "1" and a garbage value.
- [ ] OFF-path byte-identity: with the lever unset and with it set to "0", the three committed fixtures (`crewmate_basic`, `tight_budget_drops_low_salience`, `impostor_minimal`) render byte-identically, `uv run pytest tests/meetings/test_prompt_byte_golden.py -q` is green, and `bash scripts/verify_samples.sh` is 100/100. The identity assertion ships with a perturbation case proving it bites (a deliberately altered expected byte fails the test), per craft rule 2.
- [ ] ON-path shape: a `## Where you were:` block renders between the fixed role/tasks block and the observations block; consecutive ticks in the same room coalesce into one span, `- [ticks 12-16] You were in REACTOR.`, and a lone tick renders `- [tick 17] You were in ADMIN.`; spans are ordered oldest first so the block reads as a route. Pinned by a NEW golden fixture pair under `tests/fixtures/memory_rendering/` rendered with the lever ON, and by unit cases; the existing OFF-path golden parametrization keeps exactly its three names.
- [ ] The trail never claims a tick it has no record for: a gap between recorded self-state ticks BREAKS a span (no interpolation), while a meeting-boundary tick does NOT break one, because the meeting freezes movement (DESIGN.md:473, `orchestrator/game.py:1186-1190`). A property test over generated event streams asserts the spans partition the recorded ticks exactly — no gaps invented, no overlaps, no tick outside the recorded set.
- [ ] No synthetic citation ids: a trail line carries either the real `observation_id` of the self-state event that OPENS its span or no `[obs …]` prefix at all. A test asserts that every `[obs …]` id appearing anywhere in a rendered view is a member of the store's own id set — the same set `meetings/manager.py:2820-2859` validates a ballot citation against — so no rendered line can teach a model to cite an id the citation validator will null and prefix with a marker into spoken text.
- [ ] The cap is documented and empirically justified: `SELF_LOCATION_TRAIL_MAX_SPANS` is a named module constant; when it binds, the OLDEST spans are dropped (the recent route survives) and the block states the truncation in one plain-English line carrying no ids or arithmetic (craft rule 4). Its value is chosen so the coverage pin below reads 100% on every committed set, and the PR quotes the measured distribution of (meeting tick − claimed whereabouts tick) that justifies it.
- [ ] Budget interplay is measured, not assumed: the trail block is charged through the same `_estimate_tokens` arithmetic as every other block, and over the reconstructed memories of samples/9p2i at `DEFAULT_TOKEN_BUDGET` the ON path drops NO observation at or above `_SALIENCE_REPORTED_TESTIMONY` that the OFF path kept. The PR quotes the mean added lines and tokens per render. If the block cannot fit at all, trail lines are shed oldest-first BEFORE any observation is dropped.
- [ ] The completed-task line takes its tick and its room from ONE event: the stated tick is the completion event's engine tick plus one (the agent clock the packet loop stamps) and the stated room is the agent's own recorded room at that same tick; the previous-iteration roll-forward at `store.py:1204-1206` no longer feeds the rendered line. Self-consistency leg: the room a completed-task line names equals the room the trail gives for the tick it states — asserted over the fixtures and as a property over generated streams.
- [ ] Engine-agreement leg for the same line: over samples/9p2i, 843/843 completed-task lines name the agent's engine-truth room at the stated tick under the honesty instrument's documented clock alignment (agent tick minus one equals the engine tick), with any residual disagreement enumerated and explained in the test comment rather than rounded away.
- [ ] No role asymmetry: the trail renders for every role (the crew-only gate is the shape of the bug the upstream task just removed; it is not re-introduced here). An impostor's in-vent ticks render distinguishably inside the self channel, and `test_render_passes_canonical_leak_scanners` stays green with its planted-leak counterpart still failing as designed.
- [ ] The offline coverage pin in `tests/eval/test_evidence_honesty.py`: with the lever ON, the share of crew `whereabouts` claim ticks covered by a span in the SPEAKER's own memory as rendered at THAT meeting is 100% over all four committed sets; the OFF-path value is recorded as measured beside it, never predicted. The pin's docstring states in one sentence that the false-placement rate itself (bar 3 / cell I-2) is judged at the adopting record because it depends on the model reading the line, quoting `audits/audit-phase-20-preregistration.md` §8.
- [ ] `render_for_prompt`'s docstring documents the block, the span shape, the gap and meeting-boundary rules, the cap and the id rule in one paragraph, with at most one trailing provenance line and no history narration added anywhere in the file (craft rule 1).
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

Step 1 — verify the anchors before editing, then decide the seam.
`own_room_by_tick` is a LOCAL of `_collect_transitions` (declared at :1010,
filled at :1024-1028), not shared state; its only consumers today are the
own-room sighting scope at :1046 and the adjacency walk at :1063-1073. Lift
the per-tick map into one small module-level helper that both
`_collect_transitions` and the new span builder call, so there is a single
answer to "where was I at tick N". Grep every consumer first (craft rule 6):
that helper and the completed-task emission are the whole blast radius inside
this file.

Step 2 — the resolver. Clone the default-OFF shape already in the tree
(`agents/strategic/prompts/loader.py:258-301` is the live example): a `Final`
`ENV_SELF_LOCATION_TRAIL` constant, a module-level frozenset of truthy
strings, `environment = env if env is not None else os.environ`. Resolve once
in `render_for_prompt` next to the observation-id fold and pass the boolean
into the builder; the offline counterfactual toggles levers through the `env`
parameter and never mutates `os.environ`, so the parameter must reach the
resolver.

Step 3 — spans. Walk the recorded ticks ascending and coalesce a run only when
the next tick is adjacent AND the room is equal. Never bridge a missing tick.
Do bridge a meeting boundary: the agent does not move during a meeting, so a
span across it is true, and that is the one place where this walk deliberately
differs from `_collect_transitions` (which must NOT bridge, because OTHERS
change discontinuously across a meeting). Write that difference down in one
comment.

Step 4 — the block. `_assemble_view` owns block order and the budget
arithmetic; add the trail as a new block between the fixed lines and the
observations block so `view.startswith("## Your role: ...")` and the existing
header assertions still hold. Apply the cap before charging tokens, and shed
trail lines oldest-first if the remaining budget cannot take the whole block —
the observations block must never pay for the trail's overflow.

Step 5 — the completed-task line. After the upstream engine-event fix the
emission point may have moved; whatever it is, take the stated tick and the
stated room from the SAME self-state event, and delete the roll-forward's role
in the rendered line. Keep the line's existing `observation_id` behaviour so
its citation handle stays valid.

Step 6 — the counterfactual. Reconstruct each meeting's rendered memories the
way the honesty instrument does (the replay walker plus the served
transcripts), and resolve each spoken crew `whereabouts` claim tick against
the spans in that speaker's own render. Coverage is a property of the RENDER,
so it is computable offline; the truth of the claim is not, and the pin must
say so rather than implying the bar moved.

Step 7 — leave the neighbours alone. Co-presence coalescing, the spawn-block
drop and the salience re-order arrive later on this same file's chain, as does
the meetings block; do not pre-implement any of them, and do not tune the
token budget constant to make room.

## Public types this task introduces
- `agents.memory.store.self_location_trail_enabled`
- `agents.memory.store.ENV_SELF_LOCATION_TRAIL`
- `agents.memory.store.SELF_LOCATION_TRAIL_MAX_SPANS`

These are the symbols downstream tasks will import. Keep their signatures stable.

## Dependency contract check
Run these before editing. If any fail, stop and report — your dependencies are not where this task expects them.

- `uv run python -c "import agents.memory.store"`
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
Open a PR from branch `phase-20-self-location-trail` with a title like `task 20.24: the self-location trail: an agent's memory says where it was`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing G-1 [audits/review-2026-08-19/A/verdicts.md §"VERDICT: PARTIALLY-TRUE — mechanism is a CONFIRMED-BUG" — the 971-render line-shape census, the 843 completed-task instances, the 16.0% / 97.0% / 100% room-match triple, the 44.3% victim-caused / 21.5% witness-caused split]; audits/review-2026-08-19/A/collated-findings.md §G-1 (P0, corroboration 10, the s30-m3 and 4p1i-s10 exemplars); audits/review-2026-08-19/A/ideas-among-us-veteran.md §V8 (the render shape); audits/review-2026-08-19/D/FINAL-synthesis.md §1 RC1 + §4 wave-2 row 2.2 (the roadmap item this task implements); audits/audit-phase-20-preregistration.md §2 instrument I-2, §3 cell I-2 (148/723 = 20.5% samples/9p2i), §4 bar 3, §8 ("I-2 after the trail exists" is explicitly NOT predictable offline); agents/memory/store.py:1010 + :1024-1028 (`own_room_by_tick`, a LOCAL of `_collect_transitions`, consumed only at :1046 and :1063-1073 to scope OTHERS' sightings), :1178-1203 (the completed-task emission), :1204-1206 (the previous-iteration room roll-forward that mis-rooms it), :189-208 (the resolver signature to clone), :211-217 and :280 (`render_for_prompt`'s `env` thread and the resolve-once read site), :1778-1852 (`_assemble_view`'s block order and budget arithmetic); agents/strategic/prompts/qwen3_6_27b/accusation_round.j2:184 and :209, crewmate_report.j2:96 and :110 (the roll-call ask — "copied from your own record"); DESIGN.md:705 (the §6.6 worked example that specifies a tick RANGE, never built; historical design record per AGENTS.md:20-23); DESIGN.md:473 + orchestrator/game.py:1186-1190 (a meeting freezes movement); meetings/manager.py:2820-2859 (`_normalize_ballot_observation_id` nulls any id outside the voter's own set and splices a marker into `rationale_text`); AGENTS.md:76-110 craft rules 1, 2, 5, 6, 7), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
