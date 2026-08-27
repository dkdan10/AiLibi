# Agent Prompt — 21.4 The belief line believes its own eyes: last-seen reads every sighting the agent has

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-21.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 21.4 — The belief line believes its own eyes: last-seen reads every sighting the agent has, anchored to B-8 [CONFIRMED, P1] — audits/review-2026-08-26/B/collated-findings.md §B-8 (the single-writer read, the verifier's own hand-built probe, the independent corpus scan, the byte-for-byte seed-1001 exemplar, and the "NOT SPECIFIED" ruling that no document sanctions a movement-only last-seen); B-35 [ADJUSTED, P3] — same file §B-35 (the breadcrumb's vent/kill path exclusion, the verifier's 213/19,729 rate with kinds `{vent: 213, kill: 0}`, the zero-uptake measurement that downgraded it, and the "this moves rendered prompt bytes, so it rides a re-record wave" note). Anchors re-verified at HEAD `4002f19b`: agents/memory/store.py:2007-2060 `_record_movement_sightings` — the `if event.type != EVENT_SAW_PLAYER_MOVE: continue` filter at :2037-2038, the §4.7 firewall call at :2043-2051, the idempotency skip at :2053-2059, the single write at :2060; :439-449 (the one call site, immediately before the belief lines are built); :2126 (`_format_last_seen_suffix(working.last_seen(player_id))`) and :2198-2201 (`f"last seen in {last_seen.room} at tick {last_seen.tick}"`); :2296-2302 (`non_elastic_blocks` carries `beliefs_block`) and :2314-2330 (the non-elastic text is charged first, then the trail, then the observations); :1045-1081 `_sighting_is_suppressed` and :1017-1042 `_is_kill_window_sighting`; :918-985 `_collect_movement_breadcrumbs` with the vent/kill `continue` at :952-953 and the anchor/prior selection at :966-984; :988-1014 `_movement_suffix_for`; :1781-1863 `_render_saw_player`, whose vent line returns at :1810-1816 and kill line at :1817-1823 BEFORE the breadcrumb suffix is computed at :1833-1835. agents/memory/working.py:11-22 (the docstring's "for every witnessed room→room transition" claim) and :130-145 `record_sighting` (negative-tick reject, non-decreasing-tick guard, equal tick allowed and overwriting). agents/tactical/features.py:456-482 `_episodic_last_seen` (reads BOTH `EVENT_SAW_PLAYER` and `EVENT_SAW_PLAYER_MOVE`, keeps the latest) and :485-508 `_combined_last_seen` (max-by-tick over the episodic value and the render cache). agents/perception.py:189-215 (visible players are appended before moved players within one tick) and :383-388 / :391-400 (the two payload shapes: `room` versus `from_room`/`to_room`). My own re-run of the blast radius: `grep -rn "record_sighting" --include="*.py" .` has zero non-test callers besides store.py:2060, and `working.last_seen` has exactly two non-test readers — store.py:2126 and features.py:503 (training/crew/options.py:382 reads `_episodic_last_seen` directly, not the cache). tests/agents/test_memory_rendering.py:230-244 (`TestGoldenFixtures`), :696-703, :1157-1194, :1323-1500 (`TestMovementPerceptionRender`, including the §4.7 pin at :1411 and the self-subject pin at :1464), :1611 and :2185 (the trail and coalesced golden comparisons). AGENTS.md craft rules 1, 2, 5, 6, 7.. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-21.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-21-last-seen`
**Depends on:** none (root)
**Section refs:** B-8 [CONFIRMED, P1] — audits/review-2026-08-26/B/collated-findings.md §B-8 (the single-writer read, the verifier's own hand-built probe, the independent corpus scan, the byte-for-byte seed-1001 exemplar, and the "NOT SPECIFIED" ruling that no document sanctions a movement-only last-seen); B-35 [ADJUSTED, P3] — same file §B-35 (the breadcrumb's vent/kill path exclusion, the verifier's 213/19,729 rate with kinds `{vent: 213, kill: 0}`, the zero-uptake measurement that downgraded it, and the "this moves rendered prompt bytes, so it rides a re-record wave" note). Anchors re-verified at HEAD `4002f19b`: agents/memory/store.py:2007-2060 `_record_movement_sightings` — the `if event.type != EVENT_SAW_PLAYER_MOVE: continue` filter at :2037-2038, the §4.7 firewall call at :2043-2051, the idempotency skip at :2053-2059, the single write at :2060; :439-449 (the one call site, immediately before the belief lines are built); :2126 (`_format_last_seen_suffix(working.last_seen(player_id))`) and :2198-2201 (`f"last seen in {last_seen.room} at tick {last_seen.tick}"`); :2296-2302 (`non_elastic_blocks` carries `beliefs_block`) and :2314-2330 (the non-elastic text is charged first, then the trail, then the observations); :1045-1081 `_sighting_is_suppressed` and :1017-1042 `_is_kill_window_sighting`; :918-985 `_collect_movement_breadcrumbs` with the vent/kill `continue` at :952-953 and the anchor/prior selection at :966-984; :988-1014 `_movement_suffix_for`; :1781-1863 `_render_saw_player`, whose vent line returns at :1810-1816 and kill line at :1817-1823 BEFORE the breadcrumb suffix is computed at :1833-1835. agents/memory/working.py:11-22 (the docstring's "for every witnessed room→room transition" claim) and :130-145 `record_sighting` (negative-tick reject, non-decreasing-tick guard, equal tick allowed and overwriting). agents/tactical/features.py:456-482 `_episodic_last_seen` (reads BOTH `EVENT_SAW_PLAYER` and `EVENT_SAW_PLAYER_MOVE`, keeps the latest) and :485-508 `_combined_last_seen` (max-by-tick over the episodic value and the render cache). agents/perception.py:189-215 (visible players are appended before moved players within one tick) and :383-388 / :391-400 (the two payload shapes: `room` versus `from_room`/`to_room`). My own re-run of the blast radius: `grep -rn "record_sighting" --include="*.py" .` has zero non-test callers besides store.py:2060, and `working.last_seen` has exactly two non-test readers — store.py:2126 and features.py:503 (training/crew/options.py:382 reads `_episodic_last_seen` directly, not the cache). tests/agents/test_memory_rendering.py:230-244 (`TestGoldenFixtures`), :696-703, :1157-1194, :1323-1500 (`TestMovementPerceptionRender`, including the §4.7 pin at :1411 and the self-subject pin at :1464), :1611 and :2185 (the trail and coalesced golden comparisons). AGENTS.md craft rules 1, 2, 5, 6, 7.
**Complexity:** Small
**Record impact:** the record itself — rendered prompt bytes move, so this rides the Task 21.15 combined re-record; no committed byte changes in this PR
**Measurement:** `uv run pytest tests/agents/test_memory_rendering.py tests/agents/test_memory.py tests/agents/test_features.py -q` green (the planted stale-sighting cases, the argmax invariant, the two firewall pins unchanged, and the two re-derived render goldens); a fake-provider 9p2i game recorded to a scratch path and re-scanned with the register's own row-versus-observations comparison reports zero belief rows contradicted by a later sighting in the same rendered prompt and zero breadcrumb suffixes contradicted by a later sighting in the room they name; `bash scripts/verify_samples.sh` reports 100/100 committed samples clean (the engine chain is untouched by a render change); the PR states the count of newly-suffixed belief rows and newly-minted breadcrumbs the change produces on that one game, and states that committed prompt bytes do not move until Task 21.15.

The rendered belief block ends each row with "last seen in ROOM at tick T", and
that sentence has exactly one production writer: `_record_movement_sightings`,
which skips every episodic row that is not a witnessed room→room transition
(store.py:2037-2038). An ordinary `saw_player` row — the agent looking straight
at the subject — never reaches `working.record_sighting`. The result is a belief
line that contradicts the observations printed two lines above it in the same
prompt. The verifier's own hand-built probe (one witnessed move into ADMIN at
tick 2, then plain sightings in LABS at ticks 3-5) renders:

```
- [tick 2] You saw p-3 move from CAFETERIA to ADMIN.
- You saw p-3 in LABS ticks 3-5.
- p-3: suspicion 0.80 (last seen in ADMIN at tick 2)
```

The scale is not marginal. Scanning all 200 recorded corpus files, the verifier
counted 7,863 belief rows carrying a last-seen suffix; 2,703 of them (34.4%) are
contradicted by a strictly later sighting visible in the same rendered memory,
and 1,539 (19.6%) name a room the agent's own later sighting refutes. The
finder's independent counts were 2,533 (32.2%) and 1,523 (19.4%); the 7,863
denominator and the headline 19% reproduce to the digit between the two runs, and
the drift is parse-vocabulary breadth, not disagreement.

Two things make this worse than a cosmetic staleness. First, the belief block is
the NON-elastic carve-out: store.py:2296-2302 puts it in `non_elastic_blocks` and
:2314-2330 charges that text against the budget before the trail and before the
observations, which are shed against what remains. Under a tight budget the
contradicting observation is the half that disappears and the false statement is
the half that survives — the model can be left holding only the wrong room.
Second, the codebase already computes the right answer and disagrees with itself
about it: `agents/tactical/features.py:456-482` scans both `saw_player` and
`saw_player_move` rows and keeps the latest, so the tactical feature encoder and
the LLM prompt render different beliefs from the same log.

One committed prompt carries both halves of this task at once. In
`replays/ml_corpus/9p2i/replay-seed-1001.jsonl`, agent p-6's meeting prompt
(`llm_calls[0].prompt`, re-read at HEAD for this contract) contains:

```
- [obs p-6:12:1] [tick 12] You witnessed p-3 vent in LABS.
- [obs p-6:13:1] [tick 13] You saw p-3 in MEDBAY (with p-7) (moved from LABS, last seen there at tick 7).
- [obs p-6:13:2] [tick 13] You saw p-7 in MEDBAY (with p-3) (moved from LABS, last seen there at tick 12).
- p-3: suspicion 1.00 (last seen in MEDBAY at tick 8)
```

The belief row is five ticks stale — it reads the tick-8 move row and ignores the
tick-13 sighting on the line above. And p-3's breadcrumb says LABS at tick 7 while
p-7's, one line down, says LABS at tick 12: p-7's ordinary tick-12 LABS sighting
is kept, p-3's tick-12 LABS *vent* is dropped, on the single strongest piece of
evidence the game produced. After this task that prompt would read "last seen in
MEDBAY at tick 13" and "moved from LABS, last seen there at tick 12" — the tick
the render already states one line above.

That second half is B-35, and it is dropped for a reason that does not hold.
`_collect_movement_breadcrumbs` skips rows whose action is `vent` or `kill`
(store.py:952-953) and its docstring justifies the skip as "vent / kill are
witnessed events rendered as their own high-salience lines, never suffixed"
(:934-939). But the never-suffixed property is enforced somewhere else entirely:
`_render_saw_player` returns the vent line at :1810-1816 and the kill line at
:1817-1823 before `_movement_suffix_for` is ever called at :1833. Removing the
placement from the path is an undeclared second effect — it erases the evidence
those rows carry about where the subject *was*, for the benefit of other lines.
The verifier measures 213 contradicted suffixes out of 19,729 across both replay
trees (1.1%), every one of them a vent and none a kill, and — the reason it is P3
and not P2 — zero of the 213 recorded responses ever spoke the stale placement:
the correct vent tick sits one line above at higher salience and the template
tells the model to copy the vent line exactly. It is included here anyway because
it is the same sentence in the same render fed by the same argmax question, and
because it changes rendered bytes: split across two records it costs a second
~23-hour re-record to fix a one-line defect.

The fix keeps every guard that is load-bearing. The §4.7 team-internal firewall
(`_sighting_is_suppressed`, :1045-1081) must apply to the folded ordinary rows
exactly as it already applies to the move rows, and with the row's own `action`
value, so an impostor's teammate seen at a kill room or carrying a `kill` action
can never resurface as a last-seen suffix — the suppression `_render_saw_player`
performs on the sighting line itself. That is the difference between the render's
derivation and `features.py`'s: the encoder reads private memory and needs no
firewall, the prompt is spoken from. Nothing else diverges, and because
`_combined_last_seen` (:485-508) takes the max-by-tick of the episodic derivation
and the render cache, and the cache is now a firewall-filtered subset of the same
rows, the tactical feature vector is arithmetically unchanged by this task.

Nothing is specified against the change. DESIGN.md:651-653 records only that Task
13.5.4 wires `last_seen` from movement perception; no document states that a
plain sighting must not refresh it, and "last seen in ROOM at tick T" admits no
other honest reading. No prompt template moves, so no prompt-version bump belongs
here: `DEFAULT_PROMPT_VERSIONS` (orchestrator/game.py:304) keys template bytes and
Task 21.1 owns the v4 → v5 set bump. What does move is the size of a non-elastic
block: a belief row that carried no suffix may now carry one, so a tight budget
sheds marginally more elastic content. That is the trade this task is buying —
the block that always survives is the block that must be true.

The record impact is the record itself, and it is deferred: committed bytes do
not move in this PR. `replays/samples/` and `replays/ml_corpus/` remain the
baseline-7 record — canon by explicit owner override of a FINDING verdict, bars 1
and 2 missed — and
Task 21.15 re-records them on the corrected substrate, where the corpus-level
cells above are re-measured. That is also why no eval instrument is added here: a
gauge asserting that every rendered last-seen row is the argmax over the speaker's
own sightings would be red by construction against the committed prompts for the
whole of Wave 1a, which is a gate that fails for the wrong reason.

**Files in scope:**
- agents/memory/store.py; (the last-seen writer folds ordinary sightings through the same firewall; the breadcrumb path stops erasing vent/kill placements)
- agents/memory/working.py; (the module docstring's "for every witnessed room→room transition" description of the writer, now false)
- tests/agents/test_memory_rendering.py; (planted stale cases, the argmax invariant, the breadcrumb case, the firewall and idempotency pins re-asserted)
- tests/fixtures/memory_rendering/coalesced_memory_render.expected.md; (p-4's belief row gains the suffix its own tick-10 sighting supports)
- tests/fixtures/memory_rendering/self_location_trail.expected.md; (p-4's belief row gains the suffix its own tick-9 sighting supports)

**Files NOT in scope:**
- agents/tactical/features.py (`_episodic_last_seen` is the reference derivation this task converges the render on; it is read, never edited, and `_combined_last_seen`'s max keeps the encoder's value unchanged)
- training/crew/options.py (its roster and grouping read `_episodic_last_seen` directly at :382, never the working cache, so it is grep-verified untouched)
- observation/service.py and the audible vent copy (the duplicate mint and its firewall residue are Task 21.5's object; this task changes no packet field and adds no episodic row)
- agents/perception.py (the two payload shapes are read as evidence for the tie rule; the ingest itself is unchanged)
- agents/strategic/prompts/ (no template byte moves here; Task 21.1 owns the v4 → v5 set bump and the version cascade)
- eval/ (no instrument over committed prompts: a rendered-row honesty cell measured against baseline-7 bytes is red by construction until Task 21.15 re-records)
- DESIGN.md (the §6 HEAD-status note at :651-653 is a dated historical record of the pre-13.5.4 state, not a current-architecture claim; AGENTS.md gives `docs/architecture.md` that role and it enumerates no render rule)
- replays/ and replays/samples/ (no re-record in this PR; the committed record moves at Task 21.15)

**Definition of done:**
- [ ] The render's last-seen writer reads every first-hand sighting the agent holds: one pass over `episodic.recent(since_tick=0)` takes `room` from a `saw_player` row and `to_room` from a `saw_player_move` row — the same two-branch extraction `agents/tactical/features.py:472-481` already performs — and records the latest per subject, so the rendered suffix is the argmax-tick sighting in the agent's own log.
- [ ] The §4.7 firewall covers the newly folded rows with the row's OWN action: `_sighting_is_suppressed` is called with `action=` the `saw_player` payload's action string (not `None`, which is correct only for a move row), so a teammate carrying a `kill` action or standing in a kill-window room is suppressed from the suffix exactly as `_render_saw_player` suppresses the line — and the self-subject row stays suppressed for every role.
- [ ] The equal-tick rule is decided and pinned, not left to iteration order by accident: within one tick the move row wins, because perception appends visible players before moved players (agents/perception.py:189-215) and `record_sighting` allows an equal tick and overwrites (working.py:140-145). A test asserts the resulting room for a subject carrying both a `saw_player` row and a `saw_player_move` row at the same tick.
- [ ] The writer's name and docstring state what it now does: `_record_movement_sightings` is renamed (`_record_last_seen_sightings` or equivalent), its docstring leads with the rule — the latest non-suppressed first-hand sighting of each subject, whether a transition or a plain look — and the "for every witnessed room→room transition" sentence in agents/memory/working.py:11-22 and the call-site comment at store.py:439-442 are corrected in the same commit. Provenance stays at most one trailing line (craft rule 1).
- [ ] Idempotency survives: the skip for a row older than the recorded last-seen (store.py:2053-2059) still guards `record_sighting`'s non-decreasing-tick raise, and `tests/agents/test_memory_rendering.py:1386` (`test_repeated_render_is_idempotent_after_two_moves`) plus the deterministic-repeat test are joined by an equivalent case built from ORDINARY sightings, so a second render of a sighting-only memory is byte-identical and does not raise.
- [ ] Planted cases prove the gate bites, written first and failing at HEAD: the verifier's probe shape (a witnessed move into ADMIN at tick 2, then plain sightings in LABS at ticks 3-5) renders `last seen in LABS at tick 5` and NOT `last seen in ADMIN at tick 2`; and the seed-1001 shape (a sighting at tick 6, a move at tick 8, a vent at tick 12, a sighting at tick 13) renders the tick-13 room.
- [ ] An invariant test, not just examples: over a handful of hand-built logs mixing both row kinds, the rendered suffix for every belief row equals the argmax-tick entry of the firewall-filtered sightings computed independently in the test, and the same table asserts the ONE deliberate divergence from `agents.tactical.features._episodic_last_seen` — an impostor whose teammate row is suppressed keeps the older value while the encoder's map holds the newer one.
- [ ] The existing firewall pins stay green UNEDITED: `test_teammate_move_into_kill_window_room_is_suppressed` (:1411) and `test_self_subject_move_row_is_suppressed` (:1464), and the two hand-seeded enrichment tests at :696-703 and :1169-1194 (whose subjects have no episodic sighting rows, so the seeded value still renders).
- [ ] The breadcrumb keeps its evidence: `_collect_movement_breadcrumbs` no longer drops `vent`/`kill` rows from the subject's path, while the ANCHOR of the breadcrumb stays the subject's most recent ORDINARY sighting and prior candidates are restricted to rows at or before that anchor's tick — so exactly one line per moving subject is still suffixed, that line is still never a vent or kill line, and a witnessed vent can no longer be under-reported as an earlier tick in the room it happened in.
- [ ] A planted breadcrumb case pins the seed-1001 shape end to end: a witnessed vent in LABS at tick 12 followed by an ordinary sighting in MEDBAY at tick 13 renders `(moved from LABS, last seen there at tick 12)`, and the vent line itself renders with no suffix; a second case pins the newly-minted class — a subject seen ONLY in one ordinary room plus a vent elsewhere now gets a breadcrumb where the ordinary path alone yielded none — so the byte-widening is deliberate and covered rather than discovered at the re-record.
- [ ] The two moved goldens are re-derived and reviewed as the change's own evidence, not silently regenerated: `tests/fixtures/memory_rendering/coalesced_memory_render.expected.md` renders `- p-4: suspicion 0.60 (last seen in ADMIN at tick 10)` (p-4's `saw_player` rows are ticks 0, 7, 8, 10) and `tests/fixtures/memory_rendering/self_location_trail.expected.md` renders `- p-4: suspicion 0.60 (last seen in ADMIN at tick 9)` (its single `saw_player` row). `crewmate_basic`, `impostor_minimal` and `tight_budget_drops_low_salience` are byte-identical, and the PR says why: crewmate_basic's seeded value already agrees with its tick-395 sighting, and the other two have no belief row to suffix.
- [ ] The budget consequence is stated and bounded in the PR: the non-elastic belief block grows by the added suffixes, so the elastic observation section sheds marginally sooner; the parametrized tight-budget tests at tests/agents/test_memory_rendering.py:1248 stay green and no budget constant is tuned to make room.
- [ ] The change is re-measured on freshly rendered bytes, with the command in the PR: one fake-provider 9p2i game is recorded to a scratch path (`uv run python scripts/run_game.py --seed 4104 --num-players 9 --num-impostors 2 --replay-path <scratch>/lastseen-check.jsonl`), and the register's own comparison — every `- p-N: … (last seen in ROOM at tick T)` row against the latest placement-bearing observation for that subject in the SAME prompt, and every `(moved from PRIOR, last seen there at tick T)` suffix against a later sighting in PRIOR at or before the suffixed line's tick — reports zero contradictions in both classes. The PR records the same scan's counts at HEAD for the same game as the before column.
- [ ] The blast radius is re-walked and reported from a fresh grep, not from this contract: `record_sighting`'s non-test callers, `working.last_seen`'s non-test readers (store.py:2126 and features.py:503), and `_episodic_last_seen`'s consumers (features.py, training/crew/options.py:382) — with the PR stating that the tactical feature vector is unchanged because `_combined_last_seen` takes the max of two values one of which is now a subset of the other.
- [ ] `uv run pytest tests/agents/test_memory_rendering.py tests/agents/test_memory.py tests/agents/test_features.py -q` passes.
- [ ] `bash scripts/verify_samples.sh` reports 100/100 committed samples reconstructing byte-identically.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

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
Open a PR from branch `phase-21-last-seen` with a title like `task 21.4: the belief line believes its own eyes: last-seen reads every sighting the agent has`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing B-8 [CONFIRMED, P1] — audits/review-2026-08-26/B/collated-findings.md §B-8 (the single-writer read, the verifier's own hand-built probe, the independent corpus scan, the byte-for-byte seed-1001 exemplar, and the "NOT SPECIFIED" ruling that no document sanctions a movement-only last-seen); B-35 [ADJUSTED, P3] — same file §B-35 (the breadcrumb's vent/kill path exclusion, the verifier's 213/19,729 rate with kinds `{vent: 213, kill: 0}`, the zero-uptake measurement that downgraded it, and the "this moves rendered prompt bytes, so it rides a re-record wave" note). Anchors re-verified at HEAD `4002f19b`: agents/memory/store.py:2007-2060 `_record_movement_sightings` — the `if event.type != EVENT_SAW_PLAYER_MOVE: continue` filter at :2037-2038, the §4.7 firewall call at :2043-2051, the idempotency skip at :2053-2059, the single write at :2060; :439-449 (the one call site, immediately before the belief lines are built); :2126 (`_format_last_seen_suffix(working.last_seen(player_id))`) and :2198-2201 (`f"last seen in {last_seen.room} at tick {last_seen.tick}"`); :2296-2302 (`non_elastic_blocks` carries `beliefs_block`) and :2314-2330 (the non-elastic text is charged first, then the trail, then the observations); :1045-1081 `_sighting_is_suppressed` and :1017-1042 `_is_kill_window_sighting`; :918-985 `_collect_movement_breadcrumbs` with the vent/kill `continue` at :952-953 and the anchor/prior selection at :966-984; :988-1014 `_movement_suffix_for`; :1781-1863 `_render_saw_player`, whose vent line returns at :1810-1816 and kill line at :1817-1823 BEFORE the breadcrumb suffix is computed at :1833-1835. agents/memory/working.py:11-22 (the docstring's "for every witnessed room→room transition" claim) and :130-145 `record_sighting` (negative-tick reject, non-decreasing-tick guard, equal tick allowed and overwriting). agents/tactical/features.py:456-482 `_episodic_last_seen` (reads BOTH `EVENT_SAW_PLAYER` and `EVENT_SAW_PLAYER_MOVE`, keeps the latest) and :485-508 `_combined_last_seen` (max-by-tick over the episodic value and the render cache). agents/perception.py:189-215 (visible players are appended before moved players within one tick) and :383-388 / :391-400 (the two payload shapes: `room` versus `from_room`/`to_room`). My own re-run of the blast radius: `grep -rn "record_sighting" --include="*.py" .` has zero non-test callers besides store.py:2060, and `working.last_seen` has exactly two non-test readers — store.py:2126 and features.py:503 (training/crew/options.py:382 reads `_episodic_last_seen` directly, not the cache). tests/agents/test_memory_rendering.py:230-244 (`TestGoldenFixtures`), :696-703, :1157-1194, :1323-1500 (`TestMovementPerceptionRender`, including the §4.7 pin at :1411 and the self-subject pin at :1464), :1611 and :2185 (the trail and coalesced golden comparisons). AGENTS.md craft rules 1, 2, 5, 6, 7.), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
