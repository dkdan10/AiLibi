# Agent Prompt — 21.19 Testimony needs a second source (lever `corroboration_discipline`, default OFF)

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-21.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 21.19 — Testimony needs a second source (lever `corroboration_discipline`, default OFF), anchored to audits/review-2026-08-26/A/collated-findings.md §A-10 (:1138, P1 defect, ADJUSTED — the per-case ledger behind the 42 pooled innocent ejections: hearsay 79 of the 145 ejecting ballots, 37 of 42 ejectees flagless, RC 30 / BOOM 29 / PIT 17 / IMP-RIDES 33 / WEAKFLAG 5 / REDIRECT 4 / ENDGAME 5, all reproduced by the verifier under an independently written classifier), §A-11 (:1346, P2 acceptable-emergent, ADJUSTED — the boomerang is a reply template in 492/668 meetings that convicts the opener 5.9% overall and 10.7% within the no-vent-flag half against 1.4% without; the 0/387 contrast is a tautology and is dropped), §A-12 (:1449, P1 acceptable-emergent, ADJUSTED — 17/42 innocent ejections carry a physical-impossibility charge, 15/42 carry it in half or more of the convicting ballots, 1.9x within-stratum not 4.6x pooled, "provably false every time" replaced), §A-19 (:2252, P2, ADJUSTED and narrowed to the MEASUREMENT half — the pooled turn≥2 band is a mixture, not noise: same-target 79.2%/88.5% against different-target 4.7%/3.1%, so the filing's "down-weight turn≥2" advice is WITHDRAWN); prior art G-30 "Confidence is bimodal, not calibrated" (audits/review-2026-08-19/A/collated-findings.md:387-392, P2). Anchors re-verified at HEAD `4002f19b`: agents/strategic/prompts/qwen3_6_27b/vote_ballot.j2:110-118 (the ballot `<transcript>` block — turn id, kind, speaker, accusation target + confidence, free text, and no structured observation rows), :119-141 (the three flag groups), :142-148 (the `<map>` card and its one-tick sentence), :171-175 (the reporter block, unconditional since the Task-15.7 record), :183-185 ("## How to decide", the citation ask and the honest-confidence sentence), :187-197 (the 7-key output contract); agents/strategic/prompts/qwen3_6_27b/accusation_round.j2:252 (the calibration ladder verbatim — "1.0 only for a kill or a vent you watched happen first-hand; ~0.7 for a case a second account or a contradiction flag corroborates; ~0.5 for a hunch read off movement alone", the anchor A-19's verifier confirmed at that exact line); meetings/manager.py:1006-1009 (`render_inputs`, per-GAME facts built once), :1036-1058 (the per-speaker `sighting_records` mapping with the §4.7 teammate firewall re-applied at this seam), :1816-1841 (the ballot render call, `reporter_id` threaded at :1831), :2029 (the citation-gate call site), :3244-3332 (`guard_ballot_citation`, the zero-flag predicate), :355 (`UNCITED_ZERO_FLAG_EJECT_MARKER`); meetings/transcript.py:832 (`CANONICAL_ROOM_NEIGHBORS`), :1231-1237 (`reconstruct_stated_paths`), :1466-1488 (`grounded_vent_subjects_from_flags`), :2454-2470 (`_move_observation_matches_record`), :2859-2888 (`_room_hops`), :2891-2913 (`_adjacent_within_one_tick`), :3140-3166 (`_sighting_observation_matches_record`), :4087-4133 (`__all__`); meetings/constants.py:54-55 (`MAP_ARBITRATION_MAX_HOPS` 1, `MAP_ARBITRATION_MAX_TICK_GAP` 1); meetings/render_contract.py:99-125 (`PromptRenderInputs`) and :260-313 (`VotePromptRenderer`); agents/strategic/prompts/loader.py:309, :329-345, :838-902, :923-969; orchestrator/replay.py:524-546, :568-570, :585-588, :591-614, :617-620; orchestrator/game.py:304-309, :349-392, :415-421, :424-469; eval/validity.py:930-966 (a recording predating a default-OFF toggle omits the key, which reads False on both sides); scripts/check_doc_facts.py:1215-1246 (the `.env.example` live-toggle check); .env.example:85-141; .importlinter:36-42 (`agents` must not import `meetings.manager`).. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-21.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-21-corroboration`
**Depends on:** 21.18
**Section refs:** audits/review-2026-08-26/A/collated-findings.md §A-10 (:1138, P1 defect, ADJUSTED — the per-case ledger behind the 42 pooled innocent ejections: hearsay 79 of the 145 ejecting ballots, 37 of 42 ejectees flagless, RC 30 / BOOM 29 / PIT 17 / IMP-RIDES 33 / WEAKFLAG 5 / REDIRECT 4 / ENDGAME 5, all reproduced by the verifier under an independently written classifier), §A-11 (:1346, P2 acceptable-emergent, ADJUSTED — the boomerang is a reply template in 492/668 meetings that convicts the opener 5.9% overall and 10.7% within the no-vent-flag half against 1.4% without; the 0/387 contrast is a tautology and is dropped), §A-12 (:1449, P1 acceptable-emergent, ADJUSTED — 17/42 innocent ejections carry a physical-impossibility charge, 15/42 carry it in half or more of the convicting ballots, 1.9x within-stratum not 4.6x pooled, "provably false every time" replaced), §A-19 (:2252, P2, ADJUSTED and narrowed to the MEASUREMENT half — the pooled turn≥2 band is a mixture, not noise: same-target 79.2%/88.5% against different-target 4.7%/3.1%, so the filing's "down-weight turn≥2" advice is WITHDRAWN); prior art G-30 "Confidence is bimodal, not calibrated" (audits/review-2026-08-19/A/collated-findings.md:387-392, P2). Anchors re-verified at HEAD `4002f19b`: agents/strategic/prompts/qwen3_6_27b/vote_ballot.j2:110-118 (the ballot `<transcript>` block — turn id, kind, speaker, accusation target + confidence, free text, and no structured observation rows), :119-141 (the three flag groups), :142-148 (the `<map>` card and its one-tick sentence), :171-175 (the reporter block, unconditional since the Task-15.7 record), :183-185 ("## How to decide", the citation ask and the honest-confidence sentence), :187-197 (the 7-key output contract); agents/strategic/prompts/qwen3_6_27b/accusation_round.j2:252 (the calibration ladder verbatim — "1.0 only for a kill or a vent you watched happen first-hand; ~0.7 for a case a second account or a contradiction flag corroborates; ~0.5 for a hunch read off movement alone", the anchor A-19's verifier confirmed at that exact line); meetings/manager.py:1006-1009 (`render_inputs`, per-GAME facts built once), :1036-1058 (the per-speaker `sighting_records` mapping with the §4.7 teammate firewall re-applied at this seam), :1816-1841 (the ballot render call, `reporter_id` threaded at :1831), :2029 (the citation-gate call site), :3244-3332 (`guard_ballot_citation`, the zero-flag predicate), :355 (`UNCITED_ZERO_FLAG_EJECT_MARKER`); meetings/transcript.py:832 (`CANONICAL_ROOM_NEIGHBORS`), :1231-1237 (`reconstruct_stated_paths`), :1466-1488 (`grounded_vent_subjects_from_flags`), :2454-2470 (`_move_observation_matches_record`), :2859-2888 (`_room_hops`), :2891-2913 (`_adjacent_within_one_tick`), :3140-3166 (`_sighting_observation_matches_record`), :4087-4133 (`__all__`); meetings/constants.py:54-55 (`MAP_ARBITRATION_MAX_HOPS` 1, `MAP_ARBITRATION_MAX_TICK_GAP` 1); meetings/render_contract.py:99-125 (`PromptRenderInputs`) and :260-313 (`VotePromptRenderer`); agents/strategic/prompts/loader.py:309, :329-345, :838-902, :923-969; orchestrator/replay.py:524-546, :568-570, :585-588, :591-614, :617-620; orchestrator/game.py:304-309, :349-392, :415-421, :424-469; eval/validity.py:930-966 (a recording predating a default-OFF toggle omits the key, which reads False on both sides); scripts/check_doc_facts.py:1215-1246 (the `.env.example` live-toggle check); .env.example:85-141; .importlinter:36-42 (`agents` must not import `meetings.manager`).
**Complexity:** Integration
**Record impact:** lever-gated (default-OFF) until the Phase-21 adopting record
**Measurement:** `uv run pytest tests/meetings/test_corroboration.py tests/meetings/test_prompt_byte_golden.py tests/meetings/test_lever_registry.py -q` green; `bash scripts/verify_samples.sh` 100/100 and `uv run python scripts/check_doc_facts.py` clean with the lever unset; and the PR Summary quotes the four offline cells re-derived over the committed 21.15 bytes — accused subjects whose case has no first-hand source, ejected subjects whose case had none, ejections whose case originates in a turn answering the ejectee's own accusation, and ejected subjects carrying at least one map-satisfied placement pair — each stated as a count over the walk, never as a predicted outcome.

Half of what the meeting knows about a case never reaches the ballot: how many people
actually SAW something. The committed record — baseline 7, canon by explicit owner
override of a FINDING verdict (audits/audit-phase-20-baseline-7.md §6.1), where bar 2
asked for fewer than 35 innocent ejections and the record MISSED it at 42 — says what
happens without that half. Of the 145 ballots that ejected those 42 innocents, 79 cite
another player's turn and no observation of their own; 37 of the 42 ejectees carried no
contradiction flag at all; the pile's most-cited source was a crewmate in roughly 27 of
the 42 cases against an impostor in 12 (the verifier measures 28/12/2 under a different
modal tie-break, so both cells are quoted as approximate). The shape, in the finders' own
sentence, is one crewmate's movement read repeated by two or three others who cite that
turn rather than any observation, at a mean stated confidence of 0.8. Every one of the 42
is a body-report meeting; 30 of them ejected the meeting's own reporter, who is innocent
with probability 1 — 71% of the entire innocent-ejection population. The verifier's one
correction to that ledger tightens rather than softens it: six of the 42 carry no tag
beyond the generic herd and/or a provably-false transit, and only three — ml_corpus/9p2i
1008:m2, 1066:m0 and 1106:m3 — are pure herd, so the defensible-on-available-information
set is three cases, not the four the filing claimed.

This lever does not suppress the repeats. It labels them. A-19's verifier ran the one
conditioning variable the filing omitted and refuted its headline: turn≥2 accusations that
name the SAME target as the opener are right 79.2% (n=48) and 88.5% (n=122) of the time
against a ~29% chance line, while turn≥2 accusations naming a DIFFERENT target are right
4.7% and 3.1% — the pooled −0.013/−0.002 lift is a mixture artifact, agreement with the
opener is the strongest soft signal in the corpus, and the filing's "exclude or down-weight
turn≥2 soft accusations" advice was WITHDRAWN as advice that would discard it. So the
discipline here is informational, not mechanical: the ballot is told how many independent
first-hand accounts stand behind each name and how many voices merely repeat one, and is
asked to price the difference. Nothing is coerced, no ballot is rewritten, and the §4.6
tally is untouched — the vote resolution and its leader-max floor stay exactly as recorded
(A-44 measured that making the cutoff exclusive would flip exactly one of the 429 recorded
ejections, so a confidence shift is not an outcome lever and must not be read as one).

Three surfaces move, all on the ballot, all derived from bytes the meeting already holds.
(a) SOURCE COUNTING. For every accused subject the ballot renders how many distinct
speakers backed the charge with a first-hand observation their OWN typed record confirms,
how many repeated it adding nothing they saw, and which turn the charge started in. The
grounding predicate is the graduated one — the same `_sighting_observation_matches_record`
the vouch channel and the grounded-prosecution flag banding already use — so the ledger
publishes exactly the class of fact the substrate already publishes to every voter through
a demoted flag's weak reason, and opens no new channel. It reads the manager's
firewall-filtered mapping (meetings/manager.py:1036-1058), so an impostor's rows naming a
teammate cannot ground a case against that teammate. (b) OPENER CONTEXT. When the accused
is the meeting's opener and the charge originates in a turn whose speaker the opener had
just accused, the ballot says so: an answer to a charge is not a second witness. That is
the boomerang treated as provenance, not as turn-order surgery — turn 0 belongs to the
reporter and the reply's optional counter-accusation is specified (DESIGN.md:496-505), and
A-11's verifier showed the boomerang is a near-universal reply template (492/668 meetings)
with a real but modest ~8x lift on opener-ejection, not destiny. (c) THE MAP'S COUNTER.
Where two spoken placements about one subject are one doorway apart within the arbitration
tick gap, the ballot says the walk is legal for that pair, by name. The `<map>` card
already ships in every meeting call — A-12's verifier confirmed it in all 8 calls of the
anchor meeting, stating the exact adjacency the ballots then denied — so the counter is
moved from a general card to the specific pair a voter is being asked to convict on.

The honesty of the class matters more than its size. A-12's "provably false every time" is
a tautology on this substrate (the engine rejects a non-adjacent move and only impostors
vent, so every crewmate passes that test), and its 4.6x enrichment double-counts the
vent-flag stratum where an innocent ejection cannot occur; the defensible figures are 15
of 42 innocent ejections carried by a map-refutable argument in half or more of their
convicting ballots, and 15/19 = 78.9% innocent within the no-vent-flag stratum against a
40.8% base — 1.9x. Those numbers, and every other cell above, were measured on the
baseline-7 bytes. Task 21.15 re-recorded the whole record on the corrected substrate
before this task starts, so they are the motivation, never the target: this task
re-derives its cells over the 21.15 bytes and reports what it finds.

**Files in scope:**
- meetings/corroboration.py; (NEW: the `corroboration_discipline` resolver, the two frozen ledger DTOs, and the pure builder — engine-free, no env read below the resolver)
- meetings/transcript.py; (promotion ONLY: `_room_hops`, `_sighting_observation_matches_record` and `_move_observation_matches_record` become public under the same names without the underscore, bodies byte-identical, `__all__` extended, the four existing call sites renamed — no detector behavior changes)
- meetings/manager.py; (build the ledger ONCE after the chain closes, thread it into the ballot render call at :1816 — call-site only; every guard in the ballot chain is byte-unchanged)
- meetings/render_contract.py; (`VotePromptRenderer` gains ONE defaulted keyword, the 15.5 `reporter_id` / 16.3 `persona` widening pattern; `PromptRenderInputs` is not touched — it carries per-GAME facts and the ledger is per-meeting)
- agents/strategic/prompts/loader.py; (`vote_ballot_prompt` passes the ledger through to the template; no other renderer changes)
- agents/strategic/prompts/qwen3_6_27b/vote_ballot.j2; (the guarded `<testimony_sources>` block plus the band sentence; an absent ledger renders the exact pre-task bytes)
- orchestrator/replay.py; (register `corroboration_discipline` in `_TOGGLEABLE_LEVER_RESOLVERS`, newest last)
- orchestrator/game.py; (the lever-ON prompt-version overlay, the 18.10 `IMPOSTOR_ROLL_CALL_PROMPT_VERSION_SETS` shape — the default registry entry is NOT re-bumped)
- .env.example; (the new toggle's commented bare default and its paragraph; the "ONE substrate toggle" sentence becomes true again)
- tests/meetings/test_corroboration.py; (NEW: the builder's unit fixtures with their perturbations, the ON/OFF render pins, the stamp, and the committed-set walk)

**Files NOT in scope:**
- agents/strategic/prompts/qwen3_6_27b/accusation_round.j2 and the other three templates of every set (the speech side belongs to the reporter-voice lever; the frozen `qwen3_5_9b` reference set never moves, and this task renders on the ballot only)
- meetings/voting.py (the §4.6 tally and its leader-max floor decide the outcome and are untouched: this lever changes what a voter READS, never how ballots resolve)
- meetings/schemas.py (no recorded DTO gains a field — the ledger is render-only and is never written to a replay; the substrate stamp is what records that the lever ran)
- agents/memory/ (the memory-content half belongs to the testimony-shapes lever; this task reads the records the manager already builds and stores nothing)
- eval/ (the accusation-calibration re-aim and the dialect gauge are the instrument task's; this lever must not define or redefine an instrument cell — if a needed cell is missing, say so in the PR)
- scripts/counterfactual_phase20.py and the Phase-21 counterfactual harness (the OFF/ON tables over the committed bytes are Task 21.21's; this task ships the builder and its own walk, and hands the cells over)
- replays/ (no committed byte moves; the walk reads them and writes nothing)
- tests/meetings/test_prompt_byte_golden.py (the OFF-path proof is RUN unchanged, never edited — an edited golden proves nothing)

**Definition of done:**
- [ ] `meetings.corroboration.corroboration_discipline_enabled(env)` follows the standing resolver signature: reads `AILIBI_CORROBORATION_DISCIPLINE` from an optional `env` mapping (defaulting to the process environment), accepts `1/true/yes/on` case-insensitively, and is OFF for unset / empty / unrecognised values. It is read ONCE per meeting in `meetings/manager.py`, which threads the resulting ledger (or `None`) down — the one-read convention, so no code below the manager consults the environment.
- [ ] `build_testimony_ledger` is a pure function of the transcript, the meeting's detected contradictions, the per-speaker record mappings and the trigger's opener: no RNG, no clock, no env read, no free-text parsing. Given identical inputs it returns an identical ledger, pinned by a repeat-call equality assertion in `tests/meetings/test_corroboration.py`.
- [ ] A source is FIRST-HAND only when the accusing speaker's own typed record confirms an observation they spoke about the accused: a `saw_player` matched by `sighting_observation_matches_record`, a `saw_move` matched by `move_observation_matches_record`, or a spoken vent whose subject appears in `grounded_vent_subjects_from_flags` for this meeting. A speaker with two matching records, or two observations in one turn, is ONE source — the double-count guard has its own fixture, and the perturbation (give a second speaker a matching record) turns a one-source row into a two-source row on an otherwise identical transcript.
- [ ] An ADOPTED source is a distinct speaker who accuses a subject already named at this table and grounds nothing of their own; the row also carries the turn id the charge started in. A fixture pins the exact A-19 pile shape — one originator plus three repeats naming the same target, none adding an observation — and the perturbation (one repeat speaks a record-matched sighting of that target) moves that speaker into the first-hand set.
- [ ] The opener-context field is set only when the accused IS the meeting's opener and the originating accusation's speaker was accused by the opener in an earlier turn of the same meeting; a fixture pins the boomerang shape and a perturbation (the originator was never accused by the opener) leaves the field unset. The field records provenance and nothing else — no turn is reordered, no seat is reassigned, and the reply's counter-accusation stays legal.
- [ ] The walkable-transit cells are computed from `reconstruct_stated_paths` over the spoken placements for one subject, through the promoted `room_hops` with `MAP_ARBITRATION_MAX_HOPS` and `MAP_ARBITRATION_MAX_TICK_GAP` read from `meetings/constants.py` — never a second copy of the geometry. A fixture builds the A-12 anchor shape (a one-doorway pair one tick apart) and asserts the pair is reported as walkable; the perturbation (widen the tick gap beyond the bound, or place the rooms two hops apart) reports nothing.
- [ ] Rendering is bounded and voter-safe: rows are emitted only for subjects in `candidate_targets`, at most two walkable-transit lines per subject, and the block carries no task id, no audit id, no threshold arithmetic and no undefined jargon (craft rule 4) — it says "3 voices, 1 account", not "sole-source hearsay chain". The band sentence restates the calibration ladder the accusation template already asks for (accusation_round.j2:252) and adds no new number.
- [ ] OFF-path byte identity: with the lever unset the manager threads no ledger, the template renders the pre-task bytes, and `uv run pytest tests/meetings/test_prompt_byte_golden.py -q` passes UNEDITED over every committed meeting of the committed sample sets. `bash scripts/verify_samples.sh` reports 100/100 reconstructing byte-identically. Both `env` absent and `env={}` resolve OFF and agree.
- [ ] The ballot guard chain is byte-unchanged: `guard_ballot_citation` (:3244), `guard_ballot_target_graph` and `coerce_teammate_ballot_to_skip` keep their current bodies and call order, and a lever-ON fixture asserts that a ballot's recorded target, confidence, citation ids and rationale text pass through exactly as authored — the lever renders, it does not rewrite.
- [ ] `corroboration_discipline` is registered LAST in `orchestrator.replay._TOGGLEABLE_LEVER_RESOLVERS`, so `SUBSTRATE_FLAG_KEYS` grows by a pure append and every already-recorded key keeps its index. `substrate_flag_snapshot({})` stamps it `False`; exporting the variable flips exactly that key and nothing else. `tests/meetings/test_lever_registry.py` stays green with its `ast` walk unchanged.
- [ ] The 21.15 record stays loadable and valid under the widened registry, proved rather than asserted: `uv run pytest tests/eval/test_validity.py tests/api/test_replay_loader.py -q` green, and the PR states the mechanism from eval/validity.py:940-955 — a recording predating a default-OFF toggle omits the key, which reads False on both sides, so no committed replay is re-stamped and no re-record is triggered.
- [ ] Provenance moves with the bytes: while the lever is ON, `prompt_versions_for_set` serves this task's overlay so a ballot rendered with the block can never share a `vote_ballot` stamp with one rendered without it; while it is OFF, the default registry entry is served byte-identically and is NOT re-bumped (the set version belongs to the prompt-set task, and it was spent once at 21.1's v5). The overlay SEAM already exists when this task starts — Task 21.18 builds it, and 21.18 is upstream in the DAG — so this lever REGISTERS COMPOSITIONALLY into that seam and does not add a second branch to `prompt_versions_for_set`. Composition is required, not optional: 21.24 records with every Wave-2 key ON, so this overlay must resolve correctly ALONGSIDE its siblings under 21.18's three rules (application order is `_TOGGLEABLE_LEVER_RESOLVERS` order; each enabled combination gets a composite per-template stamp derived from the participating overlay names in that order; the all-ON composite is materialised and pinned). This task adds its overlay to the fold and one row to the seam's exhaustive subset test. The PR names the seam it registered into and quotes the subset test asserting that no two distinct subsets of the live overlays share a version string and none collides with a default value.
- [ ] `.env.example` documents the toggle in the belief-substrate section as a commented `# AILIBI_CORROBORATION_DISCIPLINE=0` bare default, never an active export, with a paragraph stating what ON renders and that OFF is byte-identical; the section's "the ONE substrate toggle this build still reads" sentence is corrected to the true count. `uv run python scripts/check_doc_facts.py` passes.
- [ ] The committed-set walk in `tests/meetings/test_corroboration.py` rebuilds the ledger over every meeting of the four committed sets from the recorded transcripts and reconstructed per-speaker records, asserts the structural invariants (a first-hand source is never also counted as adopted; every row's originating turn precedes every adopting turn; the opener-context field implies the subject is the opener), and RECORDS the four measurement cells as re-derived counts printed in the PR — no baseline-7 number is hard-coded as an expected value.
- [ ] The PR Summary states, in one paragraph, what this lever cannot predict offline: which target a voter names and what confidence they state under the block are behavioral, resolved only at the Phase-21 adopting record — the offline cells count renderable evidence, not outcomes.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

BLOCK 1 — the promotions, first and alone. Rename `_room_hops` (:2859),
`_sighting_observation_matches_record` (:3140) and `_move_observation_matches_record`
(:2454) to their underscore-free names, update the four call sites inside
`meetings/transcript.py`, add the three names to `__all__` (:4087, alphabetical, the
file's existing order), and change nothing else. Run
`uv run pytest tests/meetings -q` before writing a line of new logic: this block must be
provably behavior-free, and a red detector test here means the rename was not a rename.
Do NOT re-implement the room walk or the grounding match in the new module — a second
definition of "grounded" is the exact failure the grounded-prosecution work named.

BLOCK 2 — the module. `meetings/corroboration.py` holds the resolver, two frozen
dataclasses and one builder. `TestimonySupport` is the per-subject row: the subject, the
originating turn id, the distinct first-hand speaker ids, the distinct adopting speaker
ids, whether any flag names the subject this meeting (the same zero-flag predicate
`guard_ballot_citation` uses — read the flags, never a suspicion value), the optional
opener-context turn id, and the walkable-transit pairs. `MeetingTestimonyLedger` is the
ordered tuple of rows plus the opener id; order rows by first-named turn index, then by
subject id, so the render is deterministic. Keep the module import-light: `meetings.schemas`,
`meetings.constants`, `meetings.transcript` — nothing from `meetings.manager` (the loader
imports this module for the DTO type, and `agents` must not reach `meetings.manager`,
.importlinter:36-42).

BLOCK 3 — the manager seam. Build the ledger once, after the chain closes and the final
contradictions are detected, immediately before the ballot loop; pass the SAME
firewall-filtered `sighting_records` mapping the detector already receives (:1036-1058),
plus `move_witness_records` (:1031) and the trigger's `triggered_by` as the opener. Thread
it into `self._vote_prompt(...)` beside `reporter_id` (:1831). Resolve the lever ONCE at
the top of `run()` and pass `None` when OFF — one predicate, so an OFF meeting and a
ledger-less caller take the identical path and the byte-golden is trivially true.

BLOCK 4 — the template. One `{% if testimony_ledger %}` block placed AFTER the flag groups
and BEFORE the `<map>` card, so a voter reads the case's provenance next to the flags it
is weighed against. Write the copy in the table's voice — "3 voices, 1 account: p-1 said it
at [turn-1]; p-8 and p-5 repeated it without adding anything they saw" — and close with the
band sentence, which restates the ladder verbatim rather than inventing a fourth number.
The header comment gains one line naming the lever and stating that an absent ledger
renders the previous bytes; keep the rest of that comment as written.

BLOCK 5 — registration and provenance, together or not at all. The resolver goes into
`_TOGGLEABLE_LEVER_RESOLVERS` (orchestrator/replay.py:568) as the newest entry; the
overlay registers into the seam Task 21.18 already built in `prompt_versions_for_set`
(orchestrator/game.py:424) — extend the FOLD, do not fork it, do not add a precedence rule
between overlays, and do not touch the default `PROMPT_VERSION_SETS` entry, whose single move
this phase was 21.1's v5 bump. Your overlay has to survive being ON beside its two siblings,
because that is the slate 21.24 records; add your row to the seam's exhaustive subset test and
watch it stay green. Both sides read the same `env` mapping. A lever read on one side and not
the other is the render-one-stamp-another failure that pairing exists to prevent, and the 18.10
docstring says so at :437-447 — pin both directions in one test.

BLOCK 6 — the walk. Reconstruct per-speaker records the way the prompt-byte golden does
(it drives the real `MeetingManager` over re-seeded engine state and rebuilt memories);
never read omniscient state, and never recover a source class by parsing a description or
a marker string. Toggle the lever through the `env` argument, never by mutating
`os.environ`. Print the four cells in the PR with the command that produced them.

## Public types this task introduces
- `meetings.corroboration.corroboration_discipline_enabled`
- `meetings.corroboration.ENV_CORROBORATION_DISCIPLINE`
- `meetings.corroboration.TestimonySupport`
- `meetings.corroboration.MeetingTestimonyLedger`
- `meetings.corroboration.build_testimony_ledger`
- `meetings.transcript.room_hops`
- `meetings.transcript.sighting_observation_matches_record`
- `meetings.transcript.move_observation_matches_record`
- `orchestrator.game.CORROBORATION_DISCIPLINE_PROMPT_VERSION_SETS`

These are the symbols downstream tasks will import. Keep their signatures stable.

## Integration risk

Risk 1 — laundering a fabricated observation into a "first-hand" label. An impostor that
speaks an invented sighting must not earn a source count for it. This is why the first-hand
test is the graduated grounding predicate against the SPEAKER's own typed record and not
"the turn carried an observation": an invented row matches nothing and stays adopted. The
teammate firewall is re-applied at the same seam the detector uses, so an impostor's record
naming a fellow impostor cannot ground a case against that teammate either. The fabrication
fixture — a speaker with no matching record — is the one that proves the label bites.

Risk 2 — discarding the corpus's strongest soft signal. A-19's verifier established that
agreement with the opener is right 79.2%/88.5% of the time; a lever that told voters to
discount repeats would throw that away, and the filing's ML advice to down-weight turn≥2
accusations was withdrawn for exactly that reason. Nothing here down-weights: the block
counts and names, the band sentence asks for the ladder the template already asks for, and
the tally is untouched. Any implementation that starts capping, coercing or re-scoring is
out of contract — say so in the PR and stop.

Risk 3 — reading a confidence shift as a calibration win. The confidence grid is
prompt-authored (74.7% of 9p2i ballot confidences land on four values), so adding band
language will move stated confidence by template compliance alone, and the §4.6 gate is a
leader-max floor whose exclusive form would flip exactly one of 429 recorded ejections.
State plainly in the PR that a confidence-distribution change is NOT evidence for this
lever, so the pre-registration cannot bank it as one.

Risk 4 — three parallel levers, one meeting stack. This task shares `meetings/manager.py`,
`meetings/render_contract.py`, `agents/strategic/prompts/loader.py`,
`orchestrator/replay.py`, `orchestrator/game.py` and `.env.example` with the phase's other
default-OFF levers, each of which appends its own registry entry and its own defaulted
keyword. Every edit here is an APPEND at the end of an existing list or signature, never a
reflow of a neighbouring line, so the merges stay mechanical. Before pushing, re-read the
lever registry and the `.env.example` toggle count as they stand on main — if a sibling
landed first, this PR's count sentence and registration order must reflect it.

Risk 5 — the OFF path is the record's guarantee. The 21.15 bytes are the phase's ground
truth for the counterfactual, the pre-registration and the adopting record; if this task
moves a rendered byte with the lever unset, all three read a substrate nobody measured.
The unedited prompt-byte golden and `verify_samples.sh` are the proof, and they are cheap
to run — run them before the fixtures, not after.

## Dependency contract check
Run these before editing. If any fail, stop and report — your dependencies are not where this task expects them.

- `uv run python -c "import meetings.manager"`
- `uv run python -c "import meetings.render_contract"`
- `uv run python -c "import orchestrator.game.TacticalAgent"`
- `uv run python -c "import orchestrator.game"`
- `uv run python -c "import eval.reporter_justice"`
- `uv run python -c "import training.rewards"`
- `uv run python -c "import training.bakeoff.harness"`
- `uv run python -c "import training.surrogate.fidelity"`
- `uv run python -c "import orchestrator.replay"`
- `uv run python -c "import meetings.schemas"`
- `uv run python -c "import eval.replay_walk.ReplayWalkConfig"`
- `uv run python -c "import engine.tick"`
- `uv run python -c "import training.surrogate.dataset"`
- `uv run python -c "import training.surrogate.runner"`
- `uv run python -c "import training.conviction.fidelity"`
- `uv run python -c "import eval.accusation_calibration"`
- `uv run python -c "import eval.deduction_metrics"`
- `uv run python -c "import meetings.transcript"`
- `uv run python -c "import eval.meeting_quality"`
- `uv run python -c "import eval.watchability.SupplyFloors"`
- `uv run python -c "import eval.vj_instruments"`
- `uv run python -c "import eval.vj_instruments.VJInstrumentReport"`
- `uv run python -c "import eval.vj_instruments.VJMeetingRow"`
- `uv run python -c "import agents.strategic.prompts.loader"`
- `uv run python -c "import frontend/src/lib/contradictions"`
- `uv run python -c "import check_doc_facts"`

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
Open a PR from branch `phase-21-corroboration` with a title like `task 21.19: testimony needs a second source (lever `corroboration_discipline`, default off)`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing audits/review-2026-08-26/A/collated-findings.md §A-10 (:1138, P1 defect, ADJUSTED — the per-case ledger behind the 42 pooled innocent ejections: hearsay 79 of the 145 ejecting ballots, 37 of 42 ejectees flagless, RC 30 / BOOM 29 / PIT 17 / IMP-RIDES 33 / WEAKFLAG 5 / REDIRECT 4 / ENDGAME 5, all reproduced by the verifier under an independently written classifier), §A-11 (:1346, P2 acceptable-emergent, ADJUSTED — the boomerang is a reply template in 492/668 meetings that convicts the opener 5.9% overall and 10.7% within the no-vent-flag half against 1.4% without; the 0/387 contrast is a tautology and is dropped), §A-12 (:1449, P1 acceptable-emergent, ADJUSTED — 17/42 innocent ejections carry a physical-impossibility charge, 15/42 carry it in half or more of the convicting ballots, 1.9x within-stratum not 4.6x pooled, "provably false every time" replaced), §A-19 (:2252, P2, ADJUSTED and narrowed to the MEASUREMENT half — the pooled turn≥2 band is a mixture, not noise: same-target 79.2%/88.5% against different-target 4.7%/3.1%, so the filing's "down-weight turn≥2" advice is WITHDRAWN); prior art G-30 "Confidence is bimodal, not calibrated" (audits/review-2026-08-19/A/collated-findings.md:387-392, P2). Anchors re-verified at HEAD `4002f19b`: agents/strategic/prompts/qwen3_6_27b/vote_ballot.j2:110-118 (the ballot `<transcript>` block — turn id, kind, speaker, accusation target + confidence, free text, and no structured observation rows), :119-141 (the three flag groups), :142-148 (the `<map>` card and its one-tick sentence), :171-175 (the reporter block, unconditional since the Task-15.7 record), :183-185 ("## How to decide", the citation ask and the honest-confidence sentence), :187-197 (the 7-key output contract); agents/strategic/prompts/qwen3_6_27b/accusation_round.j2:252 (the calibration ladder verbatim — "1.0 only for a kill or a vent you watched happen first-hand; ~0.7 for a case a second account or a contradiction flag corroborates; ~0.5 for a hunch read off movement alone", the anchor A-19's verifier confirmed at that exact line); meetings/manager.py:1006-1009 (`render_inputs`, per-GAME facts built once), :1036-1058 (the per-speaker `sighting_records` mapping with the §4.7 teammate firewall re-applied at this seam), :1816-1841 (the ballot render call, `reporter_id` threaded at :1831), :2029 (the citation-gate call site), :3244-3332 (`guard_ballot_citation`, the zero-flag predicate), :355 (`UNCITED_ZERO_FLAG_EJECT_MARKER`); meetings/transcript.py:832 (`CANONICAL_ROOM_NEIGHBORS`), :1231-1237 (`reconstruct_stated_paths`), :1466-1488 (`grounded_vent_subjects_from_flags`), :2454-2470 (`_move_observation_matches_record`), :2859-2888 (`_room_hops`), :2891-2913 (`_adjacent_within_one_tick`), :3140-3166 (`_sighting_observation_matches_record`), :4087-4133 (`__all__`); meetings/constants.py:54-55 (`MAP_ARBITRATION_MAX_HOPS` 1, `MAP_ARBITRATION_MAX_TICK_GAP` 1); meetings/render_contract.py:99-125 (`PromptRenderInputs`) and :260-313 (`VotePromptRenderer`); agents/strategic/prompts/loader.py:309, :329-345, :838-902, :923-969; orchestrator/replay.py:524-546, :568-570, :585-588, :591-614, :617-620; orchestrator/game.py:304-309, :349-392, :415-421, :424-469; eval/validity.py:930-966 (a recording predating a default-OFF toggle omits the key, which reads False on both sides); scripts/check_doc_facts.py:1215-1246 (the `.env.example` live-toggle check); .env.example:85-141; .importlinter:36-42 (`agents` must not import `meetings.manager`).), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
