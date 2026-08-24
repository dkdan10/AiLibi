# Agent Prompt — 20.30 The memory render earns its budget: coalesced spans, no spawn block, testimony survives

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-20.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 20.30 — The memory render earns its budget: coalesced spans, no spawn block, testimony survives, anchored to audits/review-2026-08-19/A/collated-findings.md §G-34 (P1, corrob 6); audits/review-2026-08-19/A/s4-info-economy-beliefs.md §1.2 (duplicate rows + the spawn block), §1.3 (memory is 32–38% of the prompt, 70.4% of it sightings + spawn), §1.4 (the budget cuts the social memory first), §10 design-hole D6; audits/review-2026-08-19/A/ideas-multi-agent-researcher.md §D7 + proposal R8; audits/review-2026-08-19/A/ideas-game-designer.md §0.4 (the seed-17 smoking gun) + idea #5; audits/review-2026-08-19/B/agents-memory.md §1 items 6 and 10 + §2 F2 (register id C-73); audits/review-2026-08-19/B/collated-findings.md C-73; audits/review-2026-08-19/D/FINAL-synthesis.md §4 wave-2 row 2.11 (the enabler + its measurement); audits/review-2026-08-19/D/cross-track-map.md G-34 row; anchors re-verified at HEAD ee7634dc: agents/memory/store.py:47 (`DEFAULT_TOKEN_BUDGET = 1500`), :55-92 (the salience ladder; `_SALIENCE_REPORTED_TESTIMONY = 25` at :91 under the "load-bearing band invariant" comment at :85-90), :142-157 (`_Observation.observation_id`), :212-231 (the graduated `observation_id_rendering_enabled` resolver shape, hard-returning True at :231), :234-264 / :267-312 / :315-348 (the three DEFAULT-OFF resolver siblings that landed IN THIS FILE since this contract was authored — `task_completion_from_events_enabled` 20.23, `self_location_trail_enabled` 20.24, `meeting_outcome_memory_enabled` 20.29 — the in-file shape to copy), :505-518 (the lever reads inside `render_for_prompt`, `ids_on` at :510), :541-544 (the `(-salience, -tick, line)` sort), :953 (`_known_roster_ids`), :1213-1281 (`_collect_co_presence` keyed by `(tick, room)` + `_co_presence_suffix`), :1566-1794 (`_build_observations`), :1795-1866 (`_render_saw_player`), :1922-2000 (`_render_reported_testimony`, which since 20.29 takes a lever bool keyword `meeting_outcome_memory`), :2264-2374 (`_assemble_view`, where the meeting record and the trail are charged before the elastic block), :2413-2442 (`_select_within_budget`, the strict salience-ordered prefix); agents/memory/episodic.py:138 (`recent`, now a `bisect_left` over the sorted `_ticks` index 20.19 added at :94); orchestrator/game.py:1131 (`observation_ids=agent.observation_ids_for_meeting()`) and meetings/manager.py:2129-2132 (the ballot observation-id validation the ids feed, `_normalize_ballot_observation_id` at :2987-3026); agents/strategic/prompts/loader.py:321-364 (the default-OFF resolver shape this lever clones, moved by 20.19's cached environment); orchestrator/replay.py:570-572 (`_TOGGLEABLE_LEVER_RESOLVERS`, where this key is NOT registered by this task); eval/evidence_honesty.py:704-721 (`RenderBudgetCells` — the merged render census, whose docstring hands the candidate-count bucketing to THIS task) with tests/eval/test_evidence_honesty.py:1217-1234 (`test_render_budget_pins`, the committed OFF-path cell) and :1341-1469 (`_self_placement_census`, 20.24's merged OFF/ON re-render walk); audits/audit-phase-20-preregistration.md:351-356 (the ratified §5 render-census row: 20.30's cells, secondary and observed-and-reported, never gated); DESIGN.md:667 (stage-1 coalescing "NOT IMPLEMENTED at HEAD"), :668 (the unmet "elides routine task work" claim), :724 (the specified tick-range line shape). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-20.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-20-coalesced-memory-render`
**Depends on:** 20.29, 20.27, 20.19 — the meetings-outcome block and the testimony-as-content lines land in the same store module first, so this task coalesces and re-bands the FINAL line set instead of a superseded one; the map-aware arbitration lever writes its counterfactual cells into the shared evidence-honesty test module before this task adds the render-budget cells there; and the bisecting episodic scan lands in the episodic module first, so any span helper builds on the sorted-tick index rather than colliding with it.
**Section refs:** audits/review-2026-08-19/A/collated-findings.md §G-34 (P1, corrob 6); audits/review-2026-08-19/A/s4-info-economy-beliefs.md §1.2 (duplicate rows + the spawn block), §1.3 (memory is 32–38% of the prompt, 70.4% of it sightings + spawn), §1.4 (the budget cuts the social memory first), §10 design-hole D6; audits/review-2026-08-19/A/ideas-multi-agent-researcher.md §D7 + proposal R8; audits/review-2026-08-19/A/ideas-game-designer.md §0.4 (the seed-17 smoking gun) + idea #5; audits/review-2026-08-19/B/agents-memory.md §1 items 6 and 10 + §2 F2 (register id C-73); audits/review-2026-08-19/B/collated-findings.md C-73; audits/review-2026-08-19/D/FINAL-synthesis.md §4 wave-2 row 2.11 (the enabler + its measurement); audits/review-2026-08-19/D/cross-track-map.md G-34 row; anchors re-verified at HEAD ee7634dc: agents/memory/store.py:47 (`DEFAULT_TOKEN_BUDGET = 1500`), :55-92 (the salience ladder; `_SALIENCE_REPORTED_TESTIMONY = 25` at :91 under the "load-bearing band invariant" comment at :85-90), :142-157 (`_Observation.observation_id`), :212-231 (the graduated `observation_id_rendering_enabled` resolver shape, hard-returning True at :231), :234-264 / :267-312 / :315-348 (the three DEFAULT-OFF resolver siblings that landed IN THIS FILE since this contract was authored — `task_completion_from_events_enabled` 20.23, `self_location_trail_enabled` 20.24, `meeting_outcome_memory_enabled` 20.29 — the in-file shape to copy), :505-518 (the lever reads inside `render_for_prompt`, `ids_on` at :510), :541-544 (the `(-salience, -tick, line)` sort), :953 (`_known_roster_ids`), :1213-1281 (`_collect_co_presence` keyed by `(tick, room)` + `_co_presence_suffix`), :1566-1794 (`_build_observations`), :1795-1866 (`_render_saw_player`), :1922-2000 (`_render_reported_testimony`, which since 20.29 takes a lever bool keyword `meeting_outcome_memory`), :2264-2374 (`_assemble_view`, where the meeting record and the trail are charged before the elastic block), :2413-2442 (`_select_within_budget`, the strict salience-ordered prefix); agents/memory/episodic.py:138 (`recent`, now a `bisect_left` over the sorted `_ticks` index 20.19 added at :94); orchestrator/game.py:1131 (`observation_ids=agent.observation_ids_for_meeting()`) and meetings/manager.py:2129-2132 (the ballot observation-id validation the ids feed, `_normalize_ballot_observation_id` at :2987-3026); agents/strategic/prompts/loader.py:321-364 (the default-OFF resolver shape this lever clones, moved by 20.19's cached environment); orchestrator/replay.py:570-572 (`_TOGGLEABLE_LEVER_RESOLVERS`, where this key is NOT registered by this task); eval/evidence_honesty.py:704-721 (`RenderBudgetCells` — the merged render census, whose docstring hands the candidate-count bucketing to THIS task) with tests/eval/test_evidence_honesty.py:1217-1234 (`test_render_budget_pins`, the committed OFF-path cell) and :1341-1469 (`_self_placement_census`, 20.24's merged OFF/ON re-render walk); audits/audit-phase-20-preregistration.md:351-356 (the ratified §5 render-census row: 20.30's cells, secondary and observed-and-reported, never gated); DESIGN.md:667 (stage-1 coalescing "NOT IMPLEMENTED at HEAD"), :668 (the unmet "elides routine task work" claim), :724 (the specified tick-range line shape)
**Complexity:** Medium
**Record impact:** lever-gated (default-OFF) until the Phase-20 adopting record
**Measurement:** `uv run pytest tests/agents -q` and `uv run pytest tests/eval/test_evidence_honesty.py -q` green; with the key unset `bash scripts/verify_samples.sh` reports 100/100 and `uv run pytest tests/meetings/test_prompt_byte_golden.py -q` is green; under the lever ON the pinned cells over `replays/samples/9p2i` read mean rendered lines per snapshot ≤ 36 (the committed OFF-path baseline is now the 20.15 pin — mean 51.1038 over 1,956 snapshots, `tests/eval/test_evidence_honesty.py::test_render_budget_pins`, ratified at audits/audit-phase-20-preregistration.md:351-356; the review's 53.2 was pooled over BOTH samples sets, and per 20.22's standing rule the pin replaces the baseline cell while the ≤ 36 target does not move) and reported-testimony rows kept ≥ 80% in every candidate bucket (0/4,150 at >150 candidates today).

The information economy is spent on noise. Over the 1,088 memory snapshots reconstructed
from `replays/samples/`, the mean rendered block is 53.2 lines, of which bare
co-presence/sightings are 51.7%, the tick-0 spawn block 12.5%, `[meeting] CLAIM` stubs
15.6% and movement 20.3% — while vent lines are 0.69% and body lines 0.82%
(audits/review-2026-08-19/A/ideas-multi-agent-researcher.md §D7). The gameplay register
states the same shape set-wide: 66.1% of lines are bare co-presence or movement, hard
evidence is 1.54%, and 49.8% of all memory snapshots contain zero hard-evidence line;
duplicate `(subject, room)` rows are 23.1–23.7% and the tick-0 spawn block 14.4–14.7%
(19.7–20.7% in the 4p1i sets) — audits/review-2026-08-19/A/collated-findings.md §G-34.
That spawn block is eight lines saying every player started in CAFETERIA: identical in
every game ever played, carrying no discriminating information. Run-length-coalescing the
co-presence rows removes 37.4% of them — about 19% of the whole block — and dropping the
spawn block adds another 12.5%: ~32% of the context is recoverable at ZERO information
loss (§D7 again, and audits/review-2026-08-19/D/FINAL-synthesis.md §4 row 2.11).

What the noise displaces is the game's only cross-meeting social memory.
`agents/memory/store.py:47` sets the production budget at 1500 tokens; `:85-91` places
`_SALIENCE_REPORTED_TESTIMONY = 25` below every first-hand row with a comment declaring
that "a budget-tight render sheds reported rows BEFORE any first-hand observation" is the
load-bearing band invariant; `_select_within_budget` at `:2413-2442` keeps a strict
salience-ordered prefix. Measured over 60 committed `replays/ml_corpus/9p2i` games and
1,656 renders: reported rows are kept 0 of 4,150 times once a render carries more than 150
candidate observations, 718 of 5,886 in the 101–150 bucket, and in 166 of the 835 renders
that HAD reported rows every one of them was shed; the agent's own completed-task row goes
0/52 in the same regime (audits/review-2026-08-19/B/agents-memory.md §2 F2, register id
C-73). The gameplay track measured the same shedding from the other side: 365 of 456
budget-pressure transitions in the corpus cut prior-meeting testimony while retaining the
8-line spawn block at full size, 143 of 188 (76.1%) in samples
(audits/review-2026-08-19/A/s4-info-economy-beliefs.md §1.4). The band invariant is
defensible; the elastic pool it protects is dead weight, so the game trades away its social
memory to keep eight constant lines.

The reasoning cost is legible in one exemplar. In seed 17 the voter p-9 spoke a stale
CAFETERIA sighting — but p-9's own rendered memory CONTAINED the right row,
`You saw p-1 in EAST_HALL (with p-4) (moved from CAFETERIA, last seen there at tick 4)`,
sitting at line 22 underneath twelve near-identical CAFETERIA co-presence rows and above
the eight-line lobby block. In the review's words, the model is reading the top of a badly
sorted list, not hallucinating
(audits/review-2026-08-19/A/ideas-game-designer.md §0.4). That reframes the phase: this is
a rendering defect, not a model-capacity ceiling. It is also the wave's ENABLER — the
self-location trail, the meetings-outcome block and the testimony-content lines the
upstream levers add are exactly the rows the current band sheds first, so without this task
they arrive and are cut in the long games where later meetings happen
(audits/review-2026-08-19/D/FINAL-synthesis.md §4 row 2.11).

This task builds the fix as ONE default-OFF lever behind
`AILIBI_COALESCED_MEMORY_RENDER`, three folds under a single key: (a) consecutive
same-subject, same-room, same-action sightings with an unchanged companion set coalesce
into one span line carrying the tick range; (b) the tick-0 group renders as one line when
and only when it names the full known roster; (c) the salience ladder is re-banded so
reported testimony and every first-hand hard-evidence row rank strictly above bare
co-presence, with hard evidence still strictly above testimony. `DESIGN.md:667` already
records stage-1 coalescing as NOT IMPLEMENTED and `:724` already specifies the tick-range
line shape, so the ON path moves the render TOWARD the design of record rather than away
from it. OFF-path bytes are byte-identical over all 300 committed games; the ON path is
fixture-pinned and carries the committed-bytes counterfactual the pre-registration reads.

**Files in scope:**
- agents/memory/store.py; (the lever: coalesce consecutive co-presence sightings of the same subject in the same room into one span line; drop the tick-0 spawn block when it names the full roster; raise reported testimony and first-hand vent/body/kill lines above bare co-presence in salience; OFF-path bytes identical)
- agents/memory/episodic.py; (only if a span helper belongs there)
- tests/agents/test_memory_rendering.py; (OFF byte-identity; ON: spans, spawn-block rule, salience order, budget behaviour)
- tests/agents/test_reported_testimony.py; (reported rows kept ≥80% at every budget over the committed memories)
- tests/fixtures/memory_rendering/; (ON-path expected fixtures)
- tests/eval/test_evidence_honesty.py; (lines/snapshot and testimony-kept cells under the lever over samples/9p2i)

Recorded at merge (PR #382, orchestrator-ratified): the ≤ 36 rows/snapshot criterion is a FALSIFIED PREDICTION — the review projection (53.2 × 0.68) was computed against already-budget-capped renders and `_select_within_budget`'s refill makes any candidate-side fold unable to reach it; the cell re-pins at the measured mean 42.1493 (971 snapshots, samples/9p2i), with the refill arithmetic pinned (18,050 sighting rows removed − 8,663 net = 9,387 refill) and the decomposition cells kept (fold alone 40,924 rows / 39,012 subject-ticks — strictly better than OFF on both axes; the band lift costs 17.8% first-hand coverage for 0% → 95.8% testimony survival in the largest renders). One out-of-scope cell in docs/artifacts.md (tests/fixtures/ 21 → 23) accepted per the 20.24 precedent. Prose records, not scope entries.

**Files NOT in scope:**
- agents/strategic/prompts/ (no template change — the single prompt-set bump is the phase's only template edit, and it is a different task)
- meetings/ (consumes the render; the citation gate and the detector are read as consumers, never edited here)
- orchestrator/replay.py (Task 20.33 registers every Phase-20 lever in the substrate stamp at once — this task registers nothing)
- api/replay_loader.py (the served render stays on the OFF path; the counterfactual re-renders reconstructed memories explicitly)
- scripts/measure_baseline.py + eval/evidence_honesty.py (the instrument module and its CLI are the honesty-instrument task's surface; this task pins its cells in the shared test module)
- DESIGN.md (the §6.2 stage-1 "NOT IMPLEMENTED" note becomes false only at the adopting record's doc sweep)

**Definition of done:**
- [ ] `agents.memory.store.coalesced_memory_render_enabled(env: Mapping[str, str] | None = None) -> bool` exists with the 13.5 resolver signature — DEFAULT OFF, accepting `1/true/yes/on` case-insensitively, reading `os.environ` only when `env` is `None` — and is resolved ONCE inside `render_for_prompt` beside the existing observation-id resolution; `ENV_COALESCED_MEMORY_RENDER` names the key and both are exported from the module's `__all__`.
- [ ] OFF-path byte-identity: with the key unset the rendered memory is byte-identical over all 300 committed games — `uv run pytest tests/meetings/test_prompt_byte_golden.py -q` green, `bash scripts/verify_samples.sh` 100/100, and the three committed OFF-path goldens under `tests/fixtures/memory_rendering/` — `crewmate_basic`, `tight_budget_drops_low_salience`, `impostor_minimal`, the set parametrised at `tests/agents/test_memory_rendering.py:219-233` — unchanged in the diff. That directory now holds a FOURTH `*.expected.md` (`self_location_trail.expected.md`, Task 20.24's ON-path fixture), which is likewise untouched, so the glob no longer names the OFF-path three.
- [ ] The OFF-path pin can FAIL: a perturbation test asserts the ON-path render of the same fixture memory DIFFERS from the OFF-path render (a byte-identity pin that would pass with the lever inert is not a gate).
- [ ] ON, spans: consecutive same-subject / same-room / same-action sightings whose co-presence set does not change render as ONE line carrying the tick range (shape: `You saw p-9 in CAFETERIA ticks 0–4 (with p-8).`), and a change of room, action or companion set BREAKS the run into a new span — both directions pinned in `tests/agents/test_memory_rendering.py` against a committed ON-path expected fixture under `tests/fixtures/memory_rendering/`.
- [ ] ON, the spawn block: the tick-0 sighting group collapses to a single line when and only when it names the full known roster (`_known_roster_ids`) minus the observer; a PARTIAL tick-0 view keeps its individual rows because a missing player at spawn is real information — both directions pinned.
- [ ] ON, salience: the ladder places reported testimony and every first-hand hard-evidence row (body, own kill, witnessed kill, witnessed vent, heard vent) strictly ABOVE bare co-presence/sighting rows, and hard evidence strictly above testimony; the band comment at `agents/memory/store.py:85-90` is rewritten to state the OFF-path invariant and the ON-path ordering as two truthful, lever-conditional sentences.
- [ ] Salience stays a SORT KEY, not a filter: at an unbounded budget the ON-path candidate set is the same set of facts as the OFF path (the same subjects, rooms, ticks and companions, re-shaped into spans) — asserted by a test that reconstructs the per-tick `(subject, room, companions)` triples from both renders and compares them as sets.
- [ ] The budget cell: mean rendered lines per snapshot over `replays/samples/9p2i` falls to ≤ 36 under the lever ON — pinned as an asserted range in `tests/eval/test_evidence_honesty.py`, with the OFF-path value from the SAME re-render pinned beside it so the delta is visible, and the committed baseline named: mean 51.1038 over 1,956 snapshots and 99,959 rendered rows (`test_render_budget_pins` at :1217-1234, stated VERIFIED and secondary/observed-not-gated at audits/audit-phase-20-preregistration.md:351-356). The review's 53.2 was pooled over BOTH `replays/samples/` sets, so per 20.22's standing rule the pin replaces the baseline cell and the ≤ 36 target does not move with it; the PR quotes all three numbers.
- [ ] Reported-testimony survival: at `DEFAULT_TOKEN_BUDGET` over the committed memories, reported rows are kept in ≥ 80% of renders in EVERY candidate bucket (≤60, 61–100, 101–150, >150), against the committed baseline of 0/4,150 at >150 candidates and 718/5,886 at 101–150 — pinned per bucket WITH denominators in `tests/agents/test_reported_testimony.py`.
- [ ] Citation ids still resolve: every rendered `[obs …]` prefix under the lever names an id present in that agent's own store id set (the universe `orchestrator/game.py:1086` hands the manager and `meetings/manager.py:1962-1965` validates against) — a span carries the FIRST tick's `observation_id` and the range lives in the line text; asserted as a property over reconstructed memories, and the meeting citation path stays green on a fake-provider 9p2i game run with the lever ON.
- [ ] The new code carries the current rule in one sentence plus at most one provenance line — no changelog narration in the docstrings (the standing convention).
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

Step 1 — the resolver. The default-OFF shape now has three siblings IN THIS FILE, landed by
20.23 / 20.24 / 20.29: `task_completion_from_events_enabled` (store.py:234-264),
`self_location_trail_enabled` (:267-312) and `meeting_outcome_memory_enabled` (:315-348).
Copy one of those verbatim in structure — a module-level `ENV_COALESCED_MEMORY_RENDER`
constant, a `_..._FLAG_TRUE` frozenset, and a resolver that reads `env` when given and
`os.environ` otherwise — rather than reaching for
`agents/strategic/prompts/loader.py:321-364`, which is the same shape one module away. Do
NOT clone the GRADUATED shape at `agents/memory/store.py:212-231` — that one hard-returns
`True` at :231. Resolve once in `render_for_prompt` beside the existing
`ids_on = observation_id_rendering_enabled(env)` line at store.py:510 (the other three
levers are read immediately below it, :511-518), and thread the boolean, not the env
mapping, into the helpers.

Step 2 — where the fold belongs. Everything happens between `_build_observations`
(store.py:1566) and the sort at store.py:541-544, on the list of `_Observation` records —
NOT inside the per-event renderers. Coalescing after the observations are built keeps the
firewall suppressions, the co-presence suffix and the breadcrumb suffix exactly as they are
today, and keeps the OFF path a single early return. Prefer keeping the whole fold in
store.py; touch `agents/memory/episodic.py` only if a genuinely reusable sorted-run helper
falls out, and remember the bisecting tick index landed there upstream.

Step 3 — the span. Group the bare-sighting rows (the `_SALIENCE_SAW_PLAYER` and
`_SALIENCE_SAW_PLAYER_ACTIVE` classes only — never a vent, kill, body, move or testimony
row) by `(subject, room, action, companions)` and cut the run at any gap in ticks or any
change in that tuple. `_collect_co_presence` (store.py:1213, keyed by `(tick, room)`) is the
companion source; a changed "with" list is NEW information and must break the run. The span
keeps the FIRST tick's `observation_id` so the citation universe still resolves, and states
the range in the text; a run of length one renders exactly as today's single line, which is
what keeps the ON-path diff small and reviewable.

Step 4 — the spawn block. Derive the roster with `_known_roster_ids` (store.py:953) and
collapse the tick-0 group only when subject-plus-companions equals roster-minus-self. A
one-line summary is better than a deletion: the fact that everyone started together is
still a fact, it just costs one line instead of eight. Keep an observation id on the
summary line for the same reason as the spans.

Step 5 — the band. The ordering is the contract; the exact integers are yours. The shape
that satisfies it without disturbing anything else is a single elevated constant for
reported testimony placed above `_SALIENCE_SAW_PLAYER_ACTIVE` and below
`_SALIENCE_SABOTAGE_HEARD`, selected by the lever at render time. `_render_reported_testimony`
(store.py:1922-1926) already takes a lever bool as a keyword — `meeting_outcome_memory`, added
by 20.29 — so thread the second one the same way, never an env read
there. Leave the within-band
tie-break alone — the reviewers flagged the alphabetical `CLAIM by p-N` ordering as
arbitrary, and re-ranking within a band is a different change than re-ranking the bands.
Do not touch `_select_within_budget`: it stays a strict salience-ordered prefix, and the
whole point of the task is that the prefix now contains different things.

Step 6 — the counterfactual. Compute both cells by re-rendering the memories the honesty
instrument already reconstructs, once with an empty env mapping and once with
`{"AILIBI_COALESCED_MEMORY_RENDER": "1"}` — pass the mapping explicitly, never mutate
`os.environ`, so the pin is deterministic and the offline counterfactual task can reuse the
same call. Task 20.24 already landed exactly this walk: `_self_placement_census`
(tests/eval/test_evidence_honesty.py:1341) stops the instrument's replay walk at each
`MeetingOpened` and calls `render_for_prompt(composite, token_budget=DEFAULT_TOKEN_BUDGET,
env=…)` twice on the RETAINED composite (:1409-1414) — reuse that shape instead of building a
second walk. And note that `eval/evidence_honesty.py`'s own `render_budget` cells count rows
in the RECORDED prompt text, so the instrument can produce the OFF number and never the ON
one; the ON cell has to come from the re-render, which is why it lives in the test
module. Quote both directions in the PR summary: lines per snapshot OFF and ON, and the
per-bucket kept/total for reported rows OFF and ON.

Step 7 — honesty about what this does not do. This lever changes no gameplay rule and mints
no flag; it changes which true rows reach the model. Say that in the PR, and do not claim a
reasoning improvement the offline instruments cannot measure — the conviction-side effect
is the record's business, not this task's.

## Public types this task introduces
- `agents.memory.store.coalesced_memory_render_enabled`

These are the symbols downstream tasks will import. Keep their signatures stable.

## Dependency contract check
Run these before editing. If any fail, stop and report — your dependencies are not where this task expects them.

- `uv run python -c "import meetings.transcript"`
- `uv run python -c "import meetings.constants"`
- `uv run python -c "import meetings.schemas"`
- `uv run python -c "import agents.memory.store"`
- `uv run python -c "import eval.evidence_honesty"`
- `uv run python -c "import eval.solvability"`
- `uv run python -c "import meetings.manager"`
- `uv run python -c "import eval.leak_scan"`
- `uv run python -c "import api.schemas"`

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
Open a PR from branch `phase-20-coalesced-memory-render` with a title like `task 20.30: the memory render earns its budget: coalesced spans, no spawn block, testimony survives`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing audits/review-2026-08-19/A/collated-findings.md §G-34 (P1, corrob 6); audits/review-2026-08-19/A/s4-info-economy-beliefs.md §1.2 (duplicate rows + the spawn block), §1.3 (memory is 32–38% of the prompt, 70.4% of it sightings + spawn), §1.4 (the budget cuts the social memory first), §10 design-hole D6; audits/review-2026-08-19/A/ideas-multi-agent-researcher.md §D7 + proposal R8; audits/review-2026-08-19/A/ideas-game-designer.md §0.4 (the seed-17 smoking gun) + idea #5; audits/review-2026-08-19/B/agents-memory.md §1 items 6 and 10 + §2 F2 (register id C-73); audits/review-2026-08-19/B/collated-findings.md C-73; audits/review-2026-08-19/D/FINAL-synthesis.md §4 wave-2 row 2.11 (the enabler + its measurement); audits/review-2026-08-19/D/cross-track-map.md G-34 row; anchors re-verified at HEAD ee7634dc: agents/memory/store.py:47 (`DEFAULT_TOKEN_BUDGET = 1500`), :55-92 (the salience ladder; `_SALIENCE_REPORTED_TESTIMONY = 25` at :91 under the "load-bearing band invariant" comment at :85-90), :142-157 (`_Observation.observation_id`), :212-231 (the graduated `observation_id_rendering_enabled` resolver shape, hard-returning True at :231), :234-264 / :267-312 / :315-348 (the three DEFAULT-OFF resolver siblings that landed IN THIS FILE since this contract was authored — `task_completion_from_events_enabled` 20.23, `self_location_trail_enabled` 20.24, `meeting_outcome_memory_enabled` 20.29 — the in-file shape to copy), :505-518 (the lever reads inside `render_for_prompt`, `ids_on` at :510), :541-544 (the `(-salience, -tick, line)` sort), :953 (`_known_roster_ids`), :1213-1281 (`_collect_co_presence` keyed by `(tick, room)` + `_co_presence_suffix`), :1566-1794 (`_build_observations`), :1795-1866 (`_render_saw_player`), :1922-2000 (`_render_reported_testimony`, which since 20.29 takes a lever bool keyword `meeting_outcome_memory`), :2264-2374 (`_assemble_view`, where the meeting record and the trail are charged before the elastic block), :2413-2442 (`_select_within_budget`, the strict salience-ordered prefix); agents/memory/episodic.py:138 (`recent`, now a `bisect_left` over the sorted `_ticks` index 20.19 added at :94); orchestrator/game.py:1131 (`observation_ids=agent.observation_ids_for_meeting()`) and meetings/manager.py:2129-2132 (the ballot observation-id validation the ids feed, `_normalize_ballot_observation_id` at :2987-3026); agents/strategic/prompts/loader.py:321-364 (the default-OFF resolver shape this lever clones, moved by 20.19's cached environment); orchestrator/replay.py:570-572 (`_TOGGLEABLE_LEVER_RESOLVERS`, where this key is NOT registered by this task); eval/evidence_honesty.py:704-721 (`RenderBudgetCells` — the merged render census, whose docstring hands the candidate-count bucketing to THIS task) with tests/eval/test_evidence_honesty.py:1217-1234 (`test_render_budget_pins`, the committed OFF-path cell) and :1341-1469 (`_self_placement_census`, 20.24's merged OFF/ON re-render walk); audits/audit-phase-20-preregistration.md:351-356 (the ratified §5 render-census row: 20.30's cells, secondary and observed-and-reported, never gated); DESIGN.md:667 (stage-1 coalescing "NOT IMPLEMENTED at HEAD"), :668 (the unmet "elides routine task work" claim), :724 (the specified tick-range line shape)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
