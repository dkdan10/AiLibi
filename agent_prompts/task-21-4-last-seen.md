# Agent Prompt — 21.4 The belief line believes its own eyes: last-seen reads every sighting the agent has

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-21.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 21.4 — The belief line believes its own eyes: last-seen reads every sighting the agent has, anchored to B-8 [CONFIRMED, P1] — audits/review-2026-08-26/B/collated-findings.md §B-8 (the single-writer read, the verifier's own hand-built probe, the independent corpus scan, the byte-for-byte seed-1001 exemplar, and the "NOT SPECIFIED" ruling that no document sanctions a movement-only last-seen); B-35 [ADJUSTED, P3] — same file §B-35 (the breadcrumb's vent/kill path exclusion, the verifier's 213/19,729 rate with kinds `{vent: 213, kill: 0}`, the zero-uptake measurement that downgraded it, and the "this moves rendered prompt bytes, so it rides a re-record wave" note). Anchors re-verified at HEAD `4002f19b`: agents/memory/store.py:2007-2060 `_record_movement_sightings` — the `if event.type != EVENT_SAW_PLAYER_MOVE: continue` filter at :2037-2038, the §4.7 firewall call at :2043-2051, the idempotency skip at :2053-2059, the single write at :2060; :439-449 (the one call site, immediately before the belief lines are built); :2126 (`_format_last_seen_suffix(working.last_seen(player_id))`) and :2198-2201 (`f"last seen in {last_seen.room} at tick {last_seen.tick}"`); :2296-2302 (`non_elastic_blocks` carries `beliefs_block`) and :2314-2330 (the non-elastic text is charged first, then the trail, then the observations); :1045-1081 `_sighting_is_suppressed` and :1017-1042 `_is_kill_window_sighting`; :918-985 `_collect_movement_breadcrumbs` with the vent/kill `continue` at :952-953 and the anchor/prior selection at :966-984; :988-1014 `_movement_suffix_for`; :1781-1863 `_render_saw_player`, whose vent line returns at :1810-1816 and kill line at :1817-1823 BEFORE the breadcrumb suffix is computed at :1833-1835. agents/memory/working.py:11-22 (the docstring's "for every witnessed room→room transition" claim) and :130-145 `record_sighting` (negative-tick reject, non-decreasing-tick guard, equal tick allowed and overwriting). agents/tactical/features.py:456-482 `_episodic_last_seen` (reads BOTH `EVENT_SAW_PLAYER` and `EVENT_SAW_PLAYER_MOVE`, keeps the latest) and :485-508 `_combined_last_seen` (max-by-tick over the episodic value and the render cache). agents/perception.py:189-215 (visible players are appended before moved players within one tick) and :383-388 / :391-402 (the two payload shapes: `room` versus `from_room`/`to_room`). My own re-run of the blast radius: `grep -rn "record_sighting" --include="*.py" .` has zero non-test callers besides store.py:2060, and `working.last_seen` has exactly two non-test readers outside the writer's own idempotency check at store.py:2053 — store.py:2126 and features.py:503 (training/crew/options.py:382 and agents/tactical/learned/crew_forward.py:375 read `_episodic_last_seen` directly, not the cache). tests/agents/test_memory_rendering.py:230-244 (`TestGoldenFixtures`), :696-703, :1157-1194, :1323-1500 (`TestMovementPerceptionRender`, including the §4.7 pin at :1411 and the self-subject pin at :1464), :1611 and :2185 (the trail and coalesced golden comparisons). The repair gate this task ships behind: orchestrator/replay.py:104-118 (the locally-resolved `ENV_IMPOSTOR_ROLL_CALL` mirror and its truthy-token set — the shape a second default-OFF resolver clones), :121 `_impostor_roll_call_enabled`, :610-632 `_RETIRED_ALWAYS_ON_LEVERS` (twenty-one keys), :634-656 `_TOGGLEABLE_LEVER_RESOLVERS` (ONE entry at HEAD), :648-650 (the missing-key-reads-False rule that makes a stamp recorded before a key existed read the key OFF — the precedent that keeps every committed byte reconstructing), :664-674 (`TOGGLEABLE_SUBSTRATE_FLAG_KEYS` / `SUBSTRATE_FLAG_KEYS`, both append-only), :677-700 `substrate_flag_snapshot`; .env.example:121-141 (the existing default-OFF entry's voice, ending on the documented `# AILIBI_IMPOSTOR_ROLL_CALL=0` line); scripts/check_doc_facts.py:1195-1297 (the registry-versus-`.env.example` check: every `AILIBI_*=` assignment in the belief-substrate section must resolve to a live registered key, commented or not, so a registered key without its documented line — or a documented line without its key — fails the gate). The verifier's measured blast radius under an in-memory simulation of the UNGATED writer half alone, which is why the gate exists: 47 tests red — 45 across seven files (tests/meetings/test_prompt_byte_golden.py 2 failed + 14 errors over both sets, tests/agents/test_absence_prior.py 14 errors, tests/agents/test_beliefs_hard_evidence_gate.py 6 errors, tests/eval/test_evidence_honesty.py 4 failed, tests/agents/test_episodic_ids.py 1 failed + 2 errors, tests/agents/test_reported_testimony.py 1 failed, tests/agents/test_memory_store.py 1 failed — the last one the committed `_EXPECTED_FIXTURE_RENDER` at :934-948, a file this contract never listed) plus the two `tests/agents/test_memory_rendering.py` goldens this contract does own; first failure signature `headless-seed-0:meeting-0: reconstructed state_hash_after … != recorded …` raised from tests/meetings/test_prompt_byte_golden.py:611. The same simulation left `bash scripts/verify_samples.sh` clean, which locates the breakage exactly: the engine/state-hash chain is untouched and it is the PROMPT reconstruction that moves. AGENTS.md craft rules 1, 2, 5, 6, 7.. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-21.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-21-last-seen`
**Depends on:** 21.3
**Section refs:** B-8 [CONFIRMED, P1] — audits/review-2026-08-26/B/collated-findings.md §B-8 (the single-writer read, the verifier's own hand-built probe, the independent corpus scan, the byte-for-byte seed-1001 exemplar, and the "NOT SPECIFIED" ruling that no document sanctions a movement-only last-seen); B-35 [ADJUSTED, P3] — same file §B-35 (the breadcrumb's vent/kill path exclusion, the verifier's 213/19,729 rate with kinds `{vent: 213, kill: 0}`, the zero-uptake measurement that downgraded it, and the "this moves rendered prompt bytes, so it rides a re-record wave" note). Anchors re-verified at HEAD `4002f19b`: agents/memory/store.py:2007-2060 `_record_movement_sightings` — the `if event.type != EVENT_SAW_PLAYER_MOVE: continue` filter at :2037-2038, the §4.7 firewall call at :2043-2051, the idempotency skip at :2053-2059, the single write at :2060; :439-449 (the one call site, immediately before the belief lines are built); :2126 (`_format_last_seen_suffix(working.last_seen(player_id))`) and :2198-2201 (`f"last seen in {last_seen.room} at tick {last_seen.tick}"`); :2296-2302 (`non_elastic_blocks` carries `beliefs_block`) and :2314-2330 (the non-elastic text is charged first, then the trail, then the observations); :1045-1081 `_sighting_is_suppressed` and :1017-1042 `_is_kill_window_sighting`; :918-985 `_collect_movement_breadcrumbs` with the vent/kill `continue` at :952-953 and the anchor/prior selection at :966-984; :988-1014 `_movement_suffix_for`; :1781-1863 `_render_saw_player`, whose vent line returns at :1810-1816 and kill line at :1817-1823 BEFORE the breadcrumb suffix is computed at :1833-1835. agents/memory/working.py:11-22 (the docstring's "for every witnessed room→room transition" claim) and :130-145 `record_sighting` (negative-tick reject, non-decreasing-tick guard, equal tick allowed and overwriting). agents/tactical/features.py:456-482 `_episodic_last_seen` (reads BOTH `EVENT_SAW_PLAYER` and `EVENT_SAW_PLAYER_MOVE`, keeps the latest) and :485-508 `_combined_last_seen` (max-by-tick over the episodic value and the render cache). agents/perception.py:189-215 (visible players are appended before moved players within one tick) and :383-388 / :391-402 (the two payload shapes: `room` versus `from_room`/`to_room`). My own re-run of the blast radius: `grep -rn "record_sighting" --include="*.py" .` has zero non-test callers besides store.py:2060, and `working.last_seen` has exactly two non-test readers outside the writer's own idempotency check at store.py:2053 — store.py:2126 and features.py:503 (training/crew/options.py:382 and agents/tactical/learned/crew_forward.py:375 read `_episodic_last_seen` directly, not the cache). tests/agents/test_memory_rendering.py:230-244 (`TestGoldenFixtures`), :696-703, :1157-1194, :1323-1500 (`TestMovementPerceptionRender`, including the §4.7 pin at :1411 and the self-subject pin at :1464), :1611 and :2185 (the trail and coalesced golden comparisons). The repair gate this task ships behind: orchestrator/replay.py:104-118 (the locally-resolved `ENV_IMPOSTOR_ROLL_CALL` mirror and its truthy-token set — the shape a second default-OFF resolver clones), :121 `_impostor_roll_call_enabled`, :610-632 `_RETIRED_ALWAYS_ON_LEVERS` (twenty-one keys), :634-656 `_TOGGLEABLE_LEVER_RESOLVERS` (ONE entry at HEAD), :648-650 (the missing-key-reads-False rule that makes a stamp recorded before a key existed read the key OFF — the precedent that keeps every committed byte reconstructing), :664-674 (`TOGGLEABLE_SUBSTRATE_FLAG_KEYS` / `SUBSTRATE_FLAG_KEYS`, both append-only), :677-700 `substrate_flag_snapshot`; .env.example:121-141 (the existing default-OFF entry's voice, ending on the documented `# AILIBI_IMPOSTOR_ROLL_CALL=0` line); scripts/check_doc_facts.py:1195-1297 (the registry-versus-`.env.example` check: every `AILIBI_*=` assignment in the belief-substrate section must resolve to a live registered key, commented or not, so a registered key without its documented line — or a documented line without its key — fails the gate). The verifier's measured blast radius under an in-memory simulation of the UNGATED writer half alone, which is why the gate exists: 47 tests red — 45 across seven files (tests/meetings/test_prompt_byte_golden.py 2 failed + 14 errors over both sets, tests/agents/test_absence_prior.py 14 errors, tests/agents/test_beliefs_hard_evidence_gate.py 6 errors, tests/eval/test_evidence_honesty.py 4 failed, tests/agents/test_episodic_ids.py 1 failed + 2 errors, tests/agents/test_reported_testimony.py 1 failed, tests/agents/test_memory_store.py 1 failed — the last one the committed `_EXPECTED_FIXTURE_RENDER` at :934-948, a file this contract never listed) plus the two `tests/agents/test_memory_rendering.py` goldens this contract does own; first failure signature `headless-seed-0:meeting-0: reconstructed state_hash_after … != recorded …` raised from tests/meetings/test_prompt_byte_golden.py:611. The same simulation left `bash scripts/verify_samples.sh` clean, which locates the breakage exactly: the engine/state-hash chain is untouched and it is the PROMPT reconstruction that moves. AGENTS.md craft rules 1, 2, 5, 6, 7.
**Complexity:** Medium
**Record impact:** the record itself, GATED — both halves land behind ONE default-OFF repair gate (`last_seen_from_sightings`), so this PR moves no committed byte and every committed byte keeps reconstructing; the gate flips unconditional and its mechanism is DELETED at Task 21.15, whose combined re-record writes the corrected bytes and re-pins the goldens on them
**Measurement:** OFF-path (the default, and the merge condition) — `uv run pytest tests/meetings/test_prompt_byte_golden.py tests/agents tests/eval/test_evidence_honesty.py -q` green, so all 47 tests the verifier's simulation of the ungated change turned red stay green, and `bash scripts/verify_samples.sh` reports 100/100 committed samples reconstructing byte-identically. ON-path — `AILIBI_LAST_SEEN_FROM_SIGHTINGS=1 uv run pytest tests/agents/test_memory_rendering.py tests/agents/test_memory.py tests/agents/test_features.py -q` green over the planted fixture-pinned cases named in the DoD (the two stale-sighting probes, the argmax invariant, the equal-tick rule, the breadcrumb pair, and the two ON-arm golden lines asserted as a one-line diff against the committed OFF goldens), with the two firewall pins unchanged in BOTH arms. Registration — `uv run pytest tests/orchestrator/test_replay.py -q` green with a bare environment stamping the key `False` and a stamp recorded before the key existed still reading `False`. Behaviour — a fake-provider 9p2i game recorded to a scratch path under `AILIBI_LAST_SEEN_FROM_SIGHTINGS=1` and re-scanned with the register's own row-versus-observations comparison reports zero belief rows contradicted by a later sighting in the same rendered prompt and zero breadcrumb suffixes contradicted by a later sighting in the room they name, against the same scan's counts on the OFF arm as the before column; the PR states the count of newly-suffixed belief rows and newly-minted breadcrumbs the ON arm produces on that one game, and states that committed prompt bytes do not move until Task 21.15.

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

**Deferring the bytes is not free, and this contract pays for it with a gate.**
The reverification measured what the ungated change costs from this branch point,
by monkeypatching the folded writer in and running the suite: 47 tests red, and
the first one is `tests/meetings/test_prompt_byte_golden.py:611` reporting
`headless-seed-0:meeting-0: reconstructed state_hash_after … != recorded …`. That
golden does not read recorded prompt strings as data — it RE-RENDERS them,
driving the real `MeetingManager` against a stub whose dict is keyed by the EXACT
prompt, so a one-byte render drift is a stub miss, a fail-soft default turn, and a
diverged meeting. `bash scripts/verify_samples.sh` stayed clean under the same
patch, which locates the damage precisely: the engine and its state-hash chain are
untouched, and it is the prompt reconstruction that moves. Locked decision 2 of
this phase's charter prescribes the remedy by name — Wave-1a repairs "use
byte-identity seams (the v4 prompt archive, default-OFF gating where a seam does
not exist)" — and no archive seam exists for a memory render. So this repair ships
behind a gate.

ONE gate covers BOTH halves, because they are one sentence in one render fed by
one argmax question: substrate key `last_seen_from_sightings`, environment
variable `AILIBI_LAST_SEEN_FROM_SIGHTINGS`, registered in
`orchestrator/replay.py::_TOGGLEABLE_LEVER_RESOLVERS` beside the one live toggle
already there (the 18.11/20.33 pattern), documented in `.env.example` in the voice
of that entry. Two properties make the gate safe rather than merely convenient.
First, a substrate stamp recorded BEFORE a key is registered reads that key OFF —
the missing-key rule at orchestrator/replay.py:648-650, the same rule that lets
the committed sets keep reconstructing across every `impostor_roll_call`
registration — so every byte under `replays/` still verifies against a bare
build, and the loader's mismatch guard stays quiet. Second, the OFF path is not
"approximately unchanged": it is the code that exists today, so the byte-golden,
`verify_samples.sh` and all 47 measured tests are green by construction rather
than by re-blessing, and the ONE uncontracted casualty the reverification found —
`tests/agents/test_memory_store.py`'s committed `_EXPECTED_FIXTURE_RENDER` at
:934-948, in neither this task's scope nor its Measurement — never moves at all.

The gate is a REPAIR gate, not a lever, and the difference is what it costs at the
end. Locked decision 2 says repairs are not levers: nothing is being decided on
these bytes, no arm is recorded ON, and the key exists only to hold the seam from
this merge until the re-record. So it GRADUATES at Task 21.15 — flipped
unconditional and its mechanism DELETED, per the AGENTS.md graduation sweeps:
the resolver, the registry entry, the `AILIBI_*` read, the `.env.example` line
and the OFF-arm tests all go, and 21.15 re-records the four sets on the flipped
render and re-pins the two goldens on the new bytes. It is deleted OUTRIGHT rather
than promoted into `_RETIRED_ALWAYS_ON_LEVERS`, because no committed record ever
ran it ON — which is exactly what keeps 21.15's MANIFEST `flags` cell
byte-identical to today's twenty-one-key string, the equality that record uses as
its own proof that nothing graduated in the lever sense. Between this merge and
that flip the corrected render is reachable only by exporting the variable, which
is what the ON-arm tests here do and what any pre-record smoke of the corrected
substrate must do.

**Files in scope:**
- agents/memory/store.py; (the last-seen writer folds ordinary sightings through the same firewall; the breadcrumb path stops erasing vent/kill placements — both behind the one repair gate)
- agents/memory/working.py; (the module docstring's "for every witnessed room→room transition" description of the writer, now false on the ON path and stated as gated)
- orchestrator/replay.py; (register `last_seen_from_sightings` in `_TOGGLEABLE_LEVER_RESOLVERS` — a local default-OFF resolver in the shape of the one already there at :104-121, since importing an `agents.memory` reader into a replay-only module would drag the memory stack into sample byte-verification and MANIFEST reads)
- tests/orchestrator/test_replay.py; (the registration pins: a bare env stamps the new key `False`, a stamp recorded before the key existed still reads `False` through the missing-key rule, and the stamp key order stays a pure append so every already-recorded key keeps its index)
- .env.example; (the gate documented in the voice of the existing default-OFF entry at :121-141, ending on the `# AILIBI_LAST_SEEN_FROM_SIGHTINGS=0` line `scripts/check_doc_facts.py` demands for a registered key)
- tests/agents/test_memory_rendering.py; (planted stale cases, the argmax invariant, the breadcrumb case, the firewall and idempotency pins re-asserted — each written to run under BOTH arms, asserting today's render OFF and the corrected render ON)

**Files NOT in scope:**
- tests/fixtures/memory_rendering/coalesced_memory_render.expected.md and tests/fixtures/memory_rendering/self_location_trail.expected.md (the two committed goldens stay BYTE-IDENTICAL: they are the OFF render, which is the render this build still ships. The ON arm is pinned in the test module instead — each fixture rendered with the gate exported and asserted to differ from its committed golden by EXACTLY one line, that line being `- p-4: suspicion 0.60 (last seen in ADMIN at tick 10)` for the coalesced fixture and `… at tick 9` for the trail one. Task 21.15's graduation re-derives the two files onto the flipped render, old line kept beside the new one)
- agents/tactical/features.py (`_episodic_last_seen` is the reference derivation this task converges the render on; it is read, never edited, and `_combined_last_seen`'s max keeps the encoder's value unchanged)
- training/crew/options.py and agents/tactical/learned/crew_forward.py (their roster and grouping read `_episodic_last_seen` directly at :382 and :375, never the working cache, so both are grep-verified untouched)
- observation/service.py and the audible vent copy (the duplicate mint and its firewall residue are Task 21.5's object; this task changes no packet field and adds no episodic row)
- agents/perception.py (the two payload shapes are read as evidence for the tie rule; the ingest itself is unchanged)
- agents/strategic/prompts/ (no template byte moves here; Task 21.1 owns the v4 → v5 set bump and the version cascade)
- eval/ (no instrument over committed prompts: a rendered-row honesty cell measured against baseline-7 bytes is red by construction until Task 21.15 re-records)
- DESIGN.md (the §6 HEAD-status note at :651-653 is a dated historical record of the pre-13.5.4 state, not a current-architecture claim; AGENTS.md gives `docs/architecture.md` that role and it enumerates no render rule)
- replays/ and replays/samples/ (no re-record in this PR; the committed record moves at Task 21.15)

**Definition of done:**
- [ ] BOTH halves — the folded last-seen writer and the breadcrumb's vent/kill placement — land behind ONE default-OFF repair gate, never two: substrate key `last_seen_from_sightings`, environment variable `AILIBI_LAST_SEEN_FROM_SIGHTINGS`, accepting the same `1/true/yes/on` token set as the existing toggle and reading OFF for anything else including unset. The two halves are one sentence in one render and split gates would let the record capture half a repair.
- [ ] `last_seen_from_sightings` is REGISTERED in `orchestrator.replay._TOGGLEABLE_LEVER_RESOLVERS` (a local resolver in the shape of orchestrator/replay.py:104-121, not an import of the memory stack into a replay-only module), so `TOGGLEABLE_SUBSTRATE_FLAG_KEYS` and `SUBSTRATE_FLAG_KEYS` grow by a pure append at the live-toggle end and every already-recorded key keeps its index; `tests/orchestrator/test_replay.py` pins that a bare environment stamps it `False`, that the truthy-token grid resolves as the existing toggle's does, and that a substrate stamp recorded BEFORE this key existed still reads it `False` through the missing-key rule at orchestrator/replay.py:648-650 — the property that keeps every committed replay reconstructing across this registration.
- [ ] The six shipped assertions the registration breaks are updated deliberately, and `_BASELINE7_STAMP` is NOT one of them: `tests/orchestrator/test_replay.py:106-129` `_BASELINE7_STAMP` is the stamp the committed bytes actually carry and stays a twenty-two-key literal WITHOUT the new key, while :134 `_BARE_STAMP` (today `dict(_BASELINE7_STAMP)`) gains `last_seen_from_sightings: False`, because a bare snapshot taken after the registration includes it. That splits the two literals for the first time, so :394's `assert _BARE_STAMP == _BASELINE7_STAMP` is RESTATED as the missing-key seam — the bare stamp is the committed stamp plus the one key registered after that record, reading False — never deleted and never repaired by adding the key to `_BASELINE7_STAMP`, which would silently redefine what the committed record claims to carry. The four count pins follow: :341 `len(_TOGGLEABLE_LEVER_RESOLVERS) == 1` becomes 2, :324 and :346 `TOGGLEABLE_SUBSTRATE_FLAG_KEYS == (ENV_IMPOSTOR_ROLL_CALL_KEY,)` gain the second key, and :351's written-out `SUBSTRATE_FLAG_KEYS` literal gains it at the live-toggle end.
- [ ] `.env.example` documents the gate in the voice of the existing default-OFF entry at :121-141, ending on a `# AILIBI_LAST_SEEN_FROM_SIGHTINGS=0` line, and says plainly that it is a Wave-1a REPAIR gate rather than a lever: it exists to hold the byte-identity seam until Task 21.15, nothing is decided on it, no committed record runs it ON, and it is deleted at that record rather than retired into the graduated list. `scripts/check_doc_facts.py`'s registry-versus-`.env.example` check (:1195-1297) requires a registered key to carry exactly this documented assignment, so the line is a gate requirement, not a courtesy.
- [ ] The OFF path is byte-identical to HEAD, demonstrated rather than asserted, and this is the merge condition: `uv run pytest tests/meetings/test_prompt_byte_golden.py tests/agents tests/eval/test_evidence_honesty.py -q` is green — all 47 tests the reverification's simulation of the ungated change turned red, `tests/agents/test_memory_store.py`'s committed `_EXPECTED_FIXTURE_RENDER` among them — and `bash scripts/verify_samples.sh` reports 100/100 committed samples reconstructing byte-identically. The PR quotes both outputs beside the verifier's measured red list, so the reader can see which failures the gate is buying off.
- [ ] The render's last-seen writer reads every first-hand sighting the agent holds: one pass over `episodic.recent(since_tick=0)` takes `room` from a `saw_player` row and `to_room` from a `saw_player_move` row — the same two-branch extraction `agents/tactical/features.py:472-481` already performs — and records the latest per subject, so the rendered suffix is the argmax-tick sighting in the agent's own log.
- [ ] The §4.7 firewall covers the newly folded rows with the row's OWN action: `_sighting_is_suppressed` is called with `action=` the `saw_player` payload's action string (not `None`, which is correct only for a move row), so a teammate carrying a `kill` action or standing in a kill-window room is suppressed from the suffix exactly as `_render_saw_player` suppresses the line — and the self-subject row stays suppressed for every role.
- [ ] The equal-tick rule is decided and pinned, not left to iteration order by accident: within one tick the move row wins, because perception appends visible players before moved players (agents/perception.py:189-215) and `record_sighting` allows an equal tick and overwrites (working.py:140-145). A test asserts the resulting room for a subject carrying both a `saw_player` row and a `saw_player_move` row at the same tick.
- [ ] The writer's name and docstring state what it now does: `_record_movement_sightings` is renamed (`_record_last_seen_sightings` or equivalent), its docstring leads with the rule — the latest non-suppressed first-hand sighting of each subject, whether a transition or a plain look — and the "for every witnessed room→room transition" sentence in agents/memory/working.py:11-22 and the call-site comment at store.py:439-442 are corrected in the same commit. Provenance stays at most one trailing line (craft rule 1).
- [ ] Idempotency survives: the skip for a row older than the recorded last-seen (store.py:2053-2059) still guards `record_sighting`'s non-decreasing-tick raise, and `tests/agents/test_memory_rendering.py:1386` (`test_repeated_render_is_idempotent_after_two_moves`) plus the deterministic-repeat test are joined by an equivalent case built from ORDINARY sightings, so a second render of a sighting-only memory is byte-identical and does not raise.
- [ ] Every planted case below is written as a TWO-ARM case, not an ON-only one: it asserts today's render with the gate unset and the corrected render with it exported, in the same test module, so the seam itself is pinned and a gate that silently leaks into the default path fails here rather than at the byte-golden. The firewall and idempotency properties hold identically in both arms: the existing pins stay UNEDITED and green on the default path, and the ON arm gets its own equivalent case rather than a re-blessed one.
- [ ] Planted cases prove the gate bites, written first and failing at HEAD: the verifier's probe shape (a witnessed move into ADMIN at tick 2, then plain sightings in LABS at ticks 3-5) renders `last seen in LABS at tick 5` and NOT `last seen in ADMIN at tick 2`; and the seed-1001 shape (a sighting at tick 6, a move at tick 8, a vent at tick 12, a sighting at tick 13) renders the tick-13 room.
- [ ] An invariant test, not just examples: over a handful of hand-built logs mixing both row kinds, the rendered suffix for every belief row equals the argmax-tick entry of the firewall-filtered sightings computed independently in the test, and the same table asserts the ONE deliberate divergence from `agents.tactical.features._episodic_last_seen` — an impostor whose teammate row is suppressed keeps the older value while the encoder's map holds the newer one.
- [ ] The existing firewall pins stay green UNEDITED: `test_teammate_move_into_kill_window_room_is_suppressed` (:1411) and `test_self_subject_move_row_is_suppressed` (:1464), and the two hand-seeded enrichment tests at :696-703 and :1169-1194 (:696's subject p-3 has no episodic sighting row at all, and :1169's hand-seeded `p-2 / MEDBAY / tick 10` is exactly what the folded writer re-derives from that same test's tick-10 `saw_player` row, so both still render the seeded value).
- [ ] The breadcrumb keeps its evidence: `_collect_movement_breadcrumbs` no longer drops `vent`/`kill` rows from the subject's path, while the ANCHOR of the breadcrumb stays the subject's most recent ORDINARY sighting and prior candidates are restricted to rows at or before that anchor's tick — so exactly one line per moving subject is still suffixed, that line is still never a vent or kill line, and a witnessed vent can no longer be under-reported as an earlier tick in the room it happened in.
- [ ] A planted breadcrumb case pins the seed-1001 shape end to end: a witnessed vent in LABS at tick 12 followed by an ordinary sighting in MEDBAY at tick 13 renders `(moved from LABS, last seen there at tick 12)`, and the vent line itself renders with no suffix; a second case pins the newly-minted class — a subject seen ONLY in one ordinary room plus a vent elsewhere now gets a breadcrumb where the ordinary path alone yielded none — so the byte-widening is deliberate and covered rather than discovered at the re-record.
- [ ] The two fixture goldens become the ON-ARM pins WITHOUT their committed bytes moving: `tests/fixtures/memory_rendering/coalesced_memory_render.expected.md` and `…/self_location_trail.expected.md` stay byte-identical (they are the OFF render this build still ships), and a test renders each one with the gate exported and asserts the result differs from its committed golden by EXACTLY one line — `- p-4: suspicion 0.60 (last seen in ADMIN at tick 10)` for the coalesced fixture (p-4's `saw_player` rows are ticks 0, 7, 8, 10) and `- p-4: suspicion 0.60 (last seen in ADMIN at tick 9)` for the trail one (its single `saw_player` row). A second changed line in either fixture is a bug in this change, not a golden to re-bless, and the one-line-diff assertion is what makes that reviewable without a second committed fixture. `crewmate_basic`, `impostor_minimal` and `tight_budget_drops_low_salience` render identically in BOTH arms, and the PR says why: crewmate_basic's seeded value already agrees with its tick-395 sighting, and the other two have no belief row to suffix. Task 21.15's graduation is what re-derives the two `.expected.md` files onto the flipped render.
- [ ] The budget consequence is stated and bounded in the PR: the non-elastic belief block grows by the added suffixes, so the elastic observation section sheds marginally sooner; the parametrized tight-budget tests at tests/agents/test_memory_rendering.py:1248 stay green and no budget constant is tuned to make room.
- [ ] The change is re-measured on freshly rendered bytes, with the command in the PR: one fake-provider 9p2i game is recorded to a scratch path with the gate exported (`AILIBI_LAST_SEEN_FROM_SIGHTINGS=1 uv run python scripts/run_game.py --seed 4104 --num-players 9 --num-impostors 2 --replay-path <scratch>/lastseen-check.jsonl`) and the same seed recorded again with the gate unset as the before column, and the register's own comparison — every `- p-N: … (last seen in ROOM at tick T)` row against the latest placement-bearing observation for that subject in the SAME prompt, and every `(moved from PRIOR, last seen there at tick T)` suffix against a later sighting in PRIOR at or before the suffixed line's tick — reports zero contradictions in both classes, against the OFF recording's non-zero counts printed beside them.
- [ ] The blast radius is re-walked and reported from a fresh grep, not from this contract: `record_sighting`'s non-test callers, `working.last_seen`'s non-test readers (store.py:2126 and features.py:503), and `_episodic_last_seen`'s consumers (features.py:535, training/crew/options.py:382, agents/tactical/learned/crew_forward.py:375 — the last two read the episodic derivation directly, never the working cache, so neither is touched) — with the PR stating that the tactical feature vector is unchanged because `_combined_last_seen` takes the max of two values one of which is now a subset of the other.
- [ ] `uv run pytest tests/agents/test_memory_rendering.py tests/agents/test_memory.py tests/agents/test_features.py -q` passes, and the same command under `AILIBI_LAST_SEEN_FROM_SIGHTINGS=1` passes too — both outputs in the PR, because a suite that is only ever run on the default path does not test the arm the record will ship.
- [ ] `uv run pytest tests/orchestrator/test_replay.py -q` passes (the registration pins).
- [ ] `bash scripts/verify_samples.sh` reports 100/100 committed samples reconstructing byte-identically.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

Step 0 — the gate, before any behaviour moves. Clone the shape at
orchestrator/replay.py:104-121: a module-local `ENV_LAST_SEEN_FROM_SIGHTINGS`
constant, the same `{"1", "true", "yes", "on"}` frozenset, a
`_last_seen_from_sightings_enabled(env=None)` resolver, and a second entry
appended to `_TOGGLEABLE_LEVER_RESOLVERS`. Resolve it LOCALLY for the same reason
the existing one does — importing an `agents.memory` reader into a replay-only
module would drag the memory stack into sample byte-verification and MANIFEST
reads — and let `agents/memory/store.py` read the same variable through its own
one-line helper, with `tests/orchestrator/test_replay.py` pinning the two
resolvers EQUIVALENT over the env grid exactly as it already does for
`impostor_roll_call` (that equivalence pin is the CI substitute for an import
binding, and it is what stops the read site and the stamp drifting apart). Then
add the `.env.example` entry — `scripts/check_doc_facts.py` fails the moment a
key is registered without one — and run `bash scripts/check.sh` on the gate
alone, before a single render line changes. A green run here is the baseline the
rest of the task must not disturb.

Step 1 — write the two planted render tests first and watch them fail at HEAD.
Put them in a new class beside `TestMovementPerceptionRender` (tests/agents/
test_memory_rendering.py:1323) rather than rewriting that class: its subject is
the movement channel and its pins stay valid. The module already has
`_saw_player_event(tick=…, player_id=…, room=…, action=…)` and
`_saw_player_move_event(…)` helpers plus `_self_state_event`, and a belief row
only renders when suspicion is off-neutral, so `memory.beliefs.adjust_suspicion`
is still needed to make the suffix visible.

Step 2 — the writer. Keep ONE loop over `episodic.recent(since_tick=0)` and
branch on `event.type`, mirroring agents/tactical/features.py:472-481 for the
field names: `room` for a `saw_player` row, `to_room` for a `saw_player_move`
row. Read `action` from the payload for the sighting branch and pass it into
`_sighting_is_suppressed`; the move branch keeps `action=None` as today. Leave
the older-than-recorded skip exactly where it is — it is what keeps repeated
renders from tripping working.py:140-144. The events arrive in append order with
non-decreasing ticks (agents/memory/episodic.py:138-153), so a plain
last-write-wins pass yields the argmax without sorting.

Step 3 — the breadcrumb. In `_collect_movement_breadcrumbs` (store.py:918-985)
replace the `continue` at :952-953 with a recorded flag on the path entry — an
`(tick, room, is_ordinary)` triple is enough — then in the second loop pick
`ordered[-1]` from the ORDINARY entries only (a subject with no ordinary
sighting yields no breadcrumb, as today) and scan backwards for the most recent
different-room entry among ALL entries whose tick is at or before that anchor.
Do not touch `_movement_suffix_for`: the vent and kill lines already return early
at :1810-1823, so no suffix can reach them regardless of what the path contains,
and the anchor rule keeps exactly one suffixed line per subject.

Step 4 — the goldens, which do NOT move. `test_render_matches_the_coalesced_golden`
(:2185) and `test_render_matches_the_trail_golden` (:1611) keep comparing against
the committed `.expected.md` bytes and stay green on the default path. Add one
ON-arm test beside each that renders the same fixture with the gate exported and
diffs the result against the committed golden line by line, asserting exactly one
changed line and its exact text — the p-4 belief row gaining a suffix whose tick
and room appear in that fixture's own `saw_player` rows. Any second changed line
means the anchor or the firewall moved and is a bug in this change. Asserting the
DIFF rather than committing a second `.expected.md` is deliberate: it keeps the
OFF bytes as the single committed golden until Task 21.15 re-derives them, and it
makes the one moving line the reviewable record.

Step 5 — the re-measurement. `scripts/run_game.py` runs the deterministic fake
provider (no network, no key) and writes the meeting prompts into the replay's
`llm_calls[].prompt` fields, which is the same surface the register scanned. A
~30-line throwaway scan over that one file is enough to state the before and
after counts; paste it and its output into the PR under craft rule 5 rather than
committing it.

Step 6 — before pushing, grep once more for `last_seen` outside `tests/` and
confirm the two readers are still the only ones, and read
`agents/memory/working.py`'s module docstring top to bottom: it describes the
writer's contract to the next reader, and after this task two of its sentences
are no longer true.

## Dependency contract check
Run these before editing. If any fail, stop and report — your dependencies are not where this task expects them.

- `uv run python -c "import orchestrator.replay"`
- `uv run python -c "import meetings.schemas"`

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
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing B-8 [CONFIRMED, P1] — audits/review-2026-08-26/B/collated-findings.md §B-8 (the single-writer read, the verifier's own hand-built probe, the independent corpus scan, the byte-for-byte seed-1001 exemplar, and the "NOT SPECIFIED" ruling that no document sanctions a movement-only last-seen); B-35 [ADJUSTED, P3] — same file §B-35 (the breadcrumb's vent/kill path exclusion, the verifier's 213/19,729 rate with kinds `{vent: 213, kill: 0}`, the zero-uptake measurement that downgraded it, and the "this moves rendered prompt bytes, so it rides a re-record wave" note). Anchors re-verified at HEAD `4002f19b`: agents/memory/store.py:2007-2060 `_record_movement_sightings` — the `if event.type != EVENT_SAW_PLAYER_MOVE: continue` filter at :2037-2038, the §4.7 firewall call at :2043-2051, the idempotency skip at :2053-2059, the single write at :2060; :439-449 (the one call site, immediately before the belief lines are built); :2126 (`_format_last_seen_suffix(working.last_seen(player_id))`) and :2198-2201 (`f"last seen in {last_seen.room} at tick {last_seen.tick}"`); :2296-2302 (`non_elastic_blocks` carries `beliefs_block`) and :2314-2330 (the non-elastic text is charged first, then the trail, then the observations); :1045-1081 `_sighting_is_suppressed` and :1017-1042 `_is_kill_window_sighting`; :918-985 `_collect_movement_breadcrumbs` with the vent/kill `continue` at :952-953 and the anchor/prior selection at :966-984; :988-1014 `_movement_suffix_for`; :1781-1863 `_render_saw_player`, whose vent line returns at :1810-1816 and kill line at :1817-1823 BEFORE the breadcrumb suffix is computed at :1833-1835. agents/memory/working.py:11-22 (the docstring's "for every witnessed room→room transition" claim) and :130-145 `record_sighting` (negative-tick reject, non-decreasing-tick guard, equal tick allowed and overwriting). agents/tactical/features.py:456-482 `_episodic_last_seen` (reads BOTH `EVENT_SAW_PLAYER` and `EVENT_SAW_PLAYER_MOVE`, keeps the latest) and :485-508 `_combined_last_seen` (max-by-tick over the episodic value and the render cache). agents/perception.py:189-215 (visible players are appended before moved players within one tick) and :383-388 / :391-402 (the two payload shapes: `room` versus `from_room`/`to_room`). My own re-run of the blast radius: `grep -rn "record_sighting" --include="*.py" .` has zero non-test callers besides store.py:2060, and `working.last_seen` has exactly two non-test readers outside the writer's own idempotency check at store.py:2053 — store.py:2126 and features.py:503 (training/crew/options.py:382 and agents/tactical/learned/crew_forward.py:375 read `_episodic_last_seen` directly, not the cache). tests/agents/test_memory_rendering.py:230-244 (`TestGoldenFixtures`), :696-703, :1157-1194, :1323-1500 (`TestMovementPerceptionRender`, including the §4.7 pin at :1411 and the self-subject pin at :1464), :1611 and :2185 (the trail and coalesced golden comparisons). The repair gate this task ships behind: orchestrator/replay.py:104-118 (the locally-resolved `ENV_IMPOSTOR_ROLL_CALL` mirror and its truthy-token set — the shape a second default-OFF resolver clones), :121 `_impostor_roll_call_enabled`, :610-632 `_RETIRED_ALWAYS_ON_LEVERS` (twenty-one keys), :634-656 `_TOGGLEABLE_LEVER_RESOLVERS` (ONE entry at HEAD), :648-650 (the missing-key-reads-False rule that makes a stamp recorded before a key existed read the key OFF — the precedent that keeps every committed byte reconstructing), :664-674 (`TOGGLEABLE_SUBSTRATE_FLAG_KEYS` / `SUBSTRATE_FLAG_KEYS`, both append-only), :677-700 `substrate_flag_snapshot`; .env.example:121-141 (the existing default-OFF entry's voice, ending on the documented `# AILIBI_IMPOSTOR_ROLL_CALL=0` line); scripts/check_doc_facts.py:1195-1297 (the registry-versus-`.env.example` check: every `AILIBI_*=` assignment in the belief-substrate section must resolve to a live registered key, commented or not, so a registered key without its documented line — or a documented line without its key — fails the gate). The verifier's measured blast radius under an in-memory simulation of the UNGATED writer half alone, which is why the gate exists: 47 tests red — 45 across seven files (tests/meetings/test_prompt_byte_golden.py 2 failed + 14 errors over both sets, tests/agents/test_absence_prior.py 14 errors, tests/agents/test_beliefs_hard_evidence_gate.py 6 errors, tests/eval/test_evidence_honesty.py 4 failed, tests/agents/test_episodic_ids.py 1 failed + 2 errors, tests/agents/test_reported_testimony.py 1 failed, tests/agents/test_memory_store.py 1 failed — the last one the committed `_EXPECTED_FIXTURE_RENDER` at :934-948, a file this contract never listed) plus the two `tests/agents/test_memory_rendering.py` goldens this contract does own; first failure signature `headless-seed-0:meeting-0: reconstructed state_hash_after … != recorded …` raised from tests/meetings/test_prompt_byte_golden.py:611. The same simulation left `bash scripts/verify_samples.sh` clean, which locates the breakage exactly: the engine/state-hash chain is untouched and it is the PROMPT reconstruction that moves. AGENTS.md craft rules 1, 2, 5, 6, 7.), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
