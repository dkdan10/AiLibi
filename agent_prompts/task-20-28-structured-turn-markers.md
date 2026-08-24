# Agent Prompt — 20.28 Dev markers leave spoken text: structured turn annotations, chips in the spectator

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-20.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 20.28 — Dev markers leave spoken text: structured turn annotations, chips in the spectator, anchored to G-25 (audits/review-2026-08-19/A/verdicts.md verdict 11 — turn half CONFIRMED-BUG, ballot half CONFIRMED-DESIGN-CHOICE; audits/review-2026-08-19/A/collated-findings.md §D "G-25 — Dev audit markers leak into `free_text`") + C-67 (audits/review-2026-08-19/B/collated-findings.md §4 row C-67; audits/review-2026-08-19/B/meetings-manager.md §P2-9); roadmap item audits/review-2026-08-19/D/FINAL-synthesis.md §4 wave-2 row 2.8, audits/review-2026-08-19/D/synth-credibility.md §4 row 9, audits/review-2026-08-19/D/cross-track-map.md §2.2 G-25 row; meetings/manager.py:382-384, :403-408, :479-481, :516-518 (the five turn-side marker literals), :1595-1597 + :1648-1652 (the two splice sites, both inside `MeetingManager._collect_turn` at :1353), :3937-3940 (the contract the splice breaks), :3910-3981 (`_drop_non_roster_claims`, the markers built in its loop at :3958-3966); agents/strategic/prompts/qwen3_6_27b/accusation_round.j2:136 + :154, accusation_round_roll_call.j2:133 + :151, vote_ballot.j2:91 (the five unfiltered `turn.free_text` renders); api/replay_loader.py:2528-2550 (`_turn_view` and today's one-off emergency-strip), :2856-2863 (`_BALLOT_PREFIX_MARKERS`), :2874-2882 (`_MARKER_REPR_VALUE` / `_marker_pattern`), :2893-2923 (`_parse_rewrite_reasons`); api/schemas.py:627-657 (`TurnView`), :840-876 (`BallotView`, the chip precedent); meetings/schemas.py:358-383 (`MeetingTurn`); DESIGN.md:595-597 (the ballot-marker sanction); audits/audit-2026-06-11-2218-gameplay-data.md:38 (H-H-4, the "Frankenstein turn record" that bounded the quote and left the visibility); tasks/phase-18.md 18.9 (the default-OFF lever shape with committed-bytes counterfactuals). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-20.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-20-structured-turn-markers`
**Depends on:** 20.16 (the spectator DTO pass settles the view-model contract and regenerates the same TypeScript type files this task extends, so the generated-types diff stays one change per PR), 20.25 (the additive movement-claim shape lands in the turn schema first, so the annotations field is added to a settled turn model rather than racing it), 20.26 (the grounded-prosecution wiring edits the same manager call-site region and the same manager test module, so it merges ahead)
**Section refs:** G-25 (audits/review-2026-08-19/A/verdicts.md verdict 11 — turn half CONFIRMED-BUG, ballot half CONFIRMED-DESIGN-CHOICE; audits/review-2026-08-19/A/collated-findings.md §D "G-25 — Dev audit markers leak into `free_text`") + C-67 (audits/review-2026-08-19/B/collated-findings.md §4 row C-67; audits/review-2026-08-19/B/meetings-manager.md §P2-9); roadmap item audits/review-2026-08-19/D/FINAL-synthesis.md §4 wave-2 row 2.8, audits/review-2026-08-19/D/synth-credibility.md §4 row 9, audits/review-2026-08-19/D/cross-track-map.md §2.2 G-25 row; meetings/manager.py:382-384, :403-408, :479-481, :516-518 (the five turn-side marker literals), :1595-1597 + :1648-1652 (the two splice sites, both inside `MeetingManager._collect_turn` at :1353), :3937-3940 (the contract the splice breaks), :3910-3981 (`_drop_non_roster_claims`, the markers built in its loop at :3958-3966); agents/strategic/prompts/qwen3_6_27b/accusation_round.j2:136 + :154, accusation_round_roll_call.j2:133 + :151, vote_ballot.j2:91 (the five unfiltered `turn.free_text` renders); api/replay_loader.py:2528-2550 (`_turn_view` and today's one-off emergency-strip), :2856-2863 (`_BALLOT_PREFIX_MARKERS`), :2874-2882 (`_MARKER_REPR_VALUE` / `_marker_pattern`), :2893-2923 (`_parse_rewrite_reasons`); api/schemas.py:627-657 (`TurnView`), :840-876 (`BallotView`, the chip precedent); meetings/schemas.py:358-383 (`MeetingTurn`); DESIGN.md:595-597 (the ballot-marker sanction); audits/audit-2026-06-11-2218-gameplay-data.md:38 (H-H-4, the "Frankenstein turn record" that bounded the quote and left the visibility); tasks/phase-18.md 18.9 (the default-OFF lever shape with committed-bytes counterfactuals)
**Complexity:** Small
**Record impact:** lever-gated (default-OFF) until the Phase-20 adopting record
**Measurement:** `uv run pytest tests/meetings/test_manager.py tests/api -q` green; the committed-bytes census pin reads marker-bearing turns 53/971 and contaminated prompts 246/1956 over samples/9p2i with zero raw marker substrings surviving into any served `TurnView.free_text`; with `AILIBI_STRUCTURED_TURN_MARKERS=1` a fresh fake-provider 9p2i tournament records 0 marker-bearing turns and 0 contaminated prompts (I-8, `eval/evidence_honesty.py`'s marker-contamination cell, reads 0); with the lever OFF `uv run pytest tests/meetings/test_prompt_byte_golden.py -q` and `bash scripts/verify_samples.sh` stay green

Editor-console text is sitting inside quoted dialogue in one prompt in eight. The manager's
per-turn roster guard drops a claim naming a non-living participant and prepends an audit
marker to the turn's `free_text` (`meetings/manager.py:1595-1597`, the marker built at
:3961-3965 from the constant at :382-384); every later speaker's prompt then renders that
string verbatim inside the transcript block — `accusation_round.j2:136` and
`accusation_round_roll_call.j2:133` both emit `said: "{{ turn.free_text }}"`, and
`vote_ballot.j2:91` repeats it into the vote prompt. Re-verified by me at HEAD over the
committed baseline-6 bytes, exactly reproducing the review's census: marker-bearing turns
53/971 in samples/9p2i and 139/2726 in ml_corpus/9p2i (0/117 and 0/120 in the two 4p1i sets
— one-impostor games rarely produce dead-target accusations), and prompts carrying a marker
246/1956 and 671/5502, i.e. 33/165 and 91/463 meetings across 25/50 and 68/150 games. The
kind split is narrow: 53 invalid-accusation-target in samples/9p2i, 137 of the same plus 2
invalid-corroboration-supports in ml_corpus/9p2i, and zero instances of the emergency-strip
or opening-degrade markers anywhere in the committed corpus.

The function's own docstring is the contract this breaks. `meetings/manager.py:3937-3940`
promises that "a dropped claim never reaches the transcript, contradiction detection, the
post-meeting belief fold, or any prompt surface" — and the *claim* does not; the *marker*
does. The 2026-06-11 gameplay audit already called a spliced marker "a Frankenstein turn
record" (audits/audit-2026-06-11-2218-gameplay-data.md:38) and fixed only the 60-char quote
bound, never the visibility. The review's own reading of the harm is that the token lands
immediately before the sentence that usually names a vent sighting — an unexplained
editor-console string injected into the deliberation context at the highest-leverage moment,
and read verbatim by any spectator watching the transcript.

This task stops the splice behind an env lever and gives turns the structured treatment
ballots have had since Task 17.3. Recording side, default-OFF: with
`AILIBI_STRUCTURED_TURN_MARKERS` set, `_collect_turn` records each dropped claim as a typed
`TurnAnnotation` on the turn instead of prepending a string, and `free_text` is exactly what
the model authored. Reading side, unconditional: `api/replay_loader._turn_view` projects
BOTH shapes — the legacy spliced markers already frozen into the committed bytes and the new
structured field — onto one chip vocabulary, using the imported constants and the existing
repr-aware `_marker_pattern` rather than a second regex, so the spectator half ships now with
no re-record (audits/review-2026-08-19/D/synth-credibility.md §4 row 9 asks for exactly this
split). That read-side change is the one deliberate exception to OFF-path identity: recorded
bytes and rendered prompts stay byte-identical with the lever OFF, but the SERVED transcript
stops printing dev jargon immediately, the same way `fabricated_opening` already lifts the
emergency-strip marker out of `free_text` into a role-neutral chip
(`api/replay_loader.py:2528-2550`).

Scope discipline, both halves. The ballot markers are NOT touched: the review verified they
reach 0/7458 prompts (ballots are post-meeting) and `DESIGN.md:597` explicitly sanctions "an
audit marker in `rationale_text`" — that half is a design choice with no model-facing effect,
and the spectator already strips it into labelled chips. And the four other packages C-67
names as marker consumers keep working unchanged on committed bytes: `eval/vj_instruments.py`
strips leading `[...]` spans before its voice folds (:653-660, tolerant of absence by
construction), and the offline `audits/workflows/extract_gameplay_facts.py` counts marker
substrings on recorded `free_text` (:1264-1265) — a count that reads 0 for ON-path recordings
and is re-pointed at the structured field with the adopting record, not here.

**Files in scope:**
- meetings/manager.py; (the lever: the validator records dropped/invalid claims in a structured `annotations` field on the turn instead of splicing into free_text; OFF-path bytes identical)
- meetings/schemas.py; (the additive `MeetingTurn.annotations` field)
- api/replay_loader.py; (turn annotations → the same chip projection ballots already get; legacy spliced markers in committed bytes still parsed into chips)
- api/schemas.py; (TurnView.annotations)
- frontend/src/components/TurnCard.tsx; (render the chips)
- frontend/src/types/api.ts; (regenerated)
- api.fidelity.ts; (same)
- tests/meetings/test_manager.py; (OFF byte-identity; ON: free_text carries no marker; the annotation carries the dropped claim)
- tests/api/test_replay_loader.py; (legacy marker → chip; new annotation → chip)
- frontend/src/stories/MeetingView.stories.tsx; (the TurnView literal gains the annotations field)
- frontend/src/stories/MindInspector.stories.tsx; (same)

Recorded deviations at merge (PR #380, orchestrator-ratified per the #377 precedent): four files outside scope, all forced by the SawMoveObservationView DoD item widening ObservationClaimView — frontend/src/ui/ObservationLine.tsx and frontend/src/components/MemoryPanel.tsx (exhaustive TS switches), scripts/gen_frontend_types.py (union/enum alias lists), tests/api/test_leak.py (EXPECTED_DTOS + two EXPECTED_EVAL_REPORT_FIELDS names; FORBIDDEN_EVAL_ENGINE_FIELDS untouched). Ruling implemented as shipped: MeetingTurn stays the single wire shape with `annotations` an optional system-authored field stripped at the parse boundary (no AuthoredTurn type exists); MARKER_QUOTED_ORIGINAL_MAX_CHARS moved to meetings/schemas.py with re-exports, MARKER_TRUNCATION_SUFFIX beside it. A prose record, not scope entries.

**Files NOT in scope:**
- agents/strategic/prompts/ (the transcript block renders free_text; with the lever ON the free_text is clean so no template change is needed — and the single prompt-set bump of this phase is another task's, no template byte moves here)
- the ballot marker path (sanctioned by DESIGN.md:595-597, spectator-stripped, 0/7458 prompts — the four ballot-side constants and `_BALLOT_PREFIX_MARKERS` are imported, never edited)
- orchestrator/replay.py (registering this lever into `_TOGGLEABLE_LEVER_RESOLVERS` and the substrate stamp is Task 20.33's, which does it for every Phase-20 lever at once, before any ON-path seed records)
- audits/workflows/extract_gameplay_facts.py (an offline audit tool whose drop-marker count reads committed bytes today; its re-point at the structured field rides the adopting record)
- eval/vj_instruments.py + eval/meeting_quality.py + training/surrogate/dataset.py (marker consumers that already tolerate absence; read as evidence, never edited)
- eval/evidence_honesty.py (a FOURTH marker consumer, landed by 20.15 after this contract was authored: its I-8 cells derive their marker set from the three `_drop_non_roster_claims` constants and are ratified at audits/audit-phase-20-preregistration.md:169-170; this task READS those cells and must not redefine or re-implement one — if a needed split is missing, say so in the PR)

**Definition of done:**
- [ ] `structured_turn_markers_enabled` follows the 13.5 signature (optional `env` mapping, default OFF, accepting `1/true/yes/on`), is read ONCE per turn collection and threaded down, and with the lever OFF `MeetingManager._collect_turn` prepends the identical marker string in BOTH its branches (the normal path and the degraded-opening path) — pinned in `tests/meetings/test_manager.py`, plus a committed-line re-serialization pin in `tests/api/test_replay_loader.py` showing a recorded meeting entry round-trips byte-identically (the empty `annotations` tuple is elided from the serialized turn, so newly recorded bytes do not gain a key on the OFF path).
- [ ] Lever ON: a manager test plants EACH of the five turn-side marker constants' trigger conditions and asserts none of the five literals survives into `free_text`, into the rendered transcript block, or into any recorded prompt; each dropped claim is recoverable from `MeetingTurn.annotations` in claim order with its bounded original (the `MARKER_QUOTED_ORIGINAL_MAX_CHARS` bound still applied), and a perturbation shows the assertion bites when a marker is re-spliced.
- [ ] OFF-path identity holds at the gates: `tests/meetings/test_prompt_byte_golden.py` and `bash scripts/verify_samples.sh` stay green, and no prompt template byte moves in this PR.
- [ ] `api/replay_loader._turn_view` projects BOTH shapes to one chip vocabulary via the IMPORTED constants and the existing `_marker_pattern` (no second regex, no hard-coded literal): a committed replay's legacy spliced markers become `TurnView.annotations` labels with `free_text` cleaned, a recorded structured annotation becomes the same label, and `fabricated_opening` is derived from either shape — all three pinned in `tests/api/test_replay_loader.py`.
- [ ] The committed-bytes counterfactual is pinned over the two samples sets and quoted for all four in the PR (the four rate cells are ALREADY pinned by `tests/eval/test_evidence_honesty.py::test_i8_marker_contamination_pins` — cite that test rather than duplicating it; only the kind split is new here): marker-bearing turns 53/971 and contaminated prompts 246/1956 for samples/9p2i (33/165 meetings, 25/50 games), 0/117 and 0/234 for samples/4p1i, 139/2726 and 671/5502 for ml_corpus/9p2i (91/463 meetings, 68/150 games), 0/120 and 0/240 for ml_corpus/4p1i, with the kind split (53 invalid-accusation-target; 137 plus 2 invalid-corroboration-supports; zero emergency-strip and zero opening-degrade markers corpus-wide) and the stated would-be effect — every one of those turns carries a structured annotation instead, and the contaminated-prompt cell reads 0 at the adopting record.
- [ ] `TurnCard` renders the annotation labels as ink/paper chips beside the existing FABRICATED chip, in every perspective, with a one-line comment recording why no turn-annotation label carries role information (unlike the ballot side's `teammate_coerced` gate); the regenerated types are committed and `uv run python scripts/gen_frontend_types.py --check` passes.
- [ ] The spectator mirror of the movement shape exists: api/replay_loader.py::_observation_claim_view maps SawMoveObservation to a SawMoveObservationView (api/schemas.py + the generated types), pinned — the first recorded saw_move turn must not break the viewer before the record.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Public types this task introduces
- `meetings.manager.structured_turn_markers_enabled`
- `meetings.schemas.TurnAnnotation`
- `meetings.schemas.TurnAnnotationKind`

These are the symbols downstream tasks will import. Keep their signatures stable.

## Dependency contract check
Run these before editing. If any fail, stop and report — your dependencies are not where this task expects them.

- `uv run python -c "import meetings.transcript"`
- `uv run python -c "import meetings.constants"`
- `uv run python -c "import meetings.schemas"`
- `uv run python -c "import agents.memory.store"`
- `uv run python -c "import eval.evidence_honesty"`
- `uv run python -c "import eval.solvability"`
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

## Verification checklist
- Run every command listed in the Definition of done.
- If the contract carries a `**Measurement:**` field, run that command and paste its output into the PR's `## Summary`; a Measurement that cannot be run is reported under `## Questions`, never asserted.
- Run `git diff --name-only` and confirm the diff stays within scope.
- If any Definition of done item is unchecked, report it explicitly in the PR description instead of declaring the task complete.

## Decisions vs questions
- If something is **ambiguous and blocking** (you cannot make a reasonable choice without further information): stop, open a draft PR, add a `## Questions` section, request review.
- If something is **ambiguous but resolvable by judgment** (a default value, a tie-break, a naming choice): document the choice in a `## Decisions` section in the PR description and proceed.

## Output expectation
Open a PR from branch `phase-20-structured-turn-markers` with a title like `task 20.28: dev markers leave spoken text: structured turn annotations, chips in the spectator`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing G-25 (audits/review-2026-08-19/A/verdicts.md verdict 11 — turn half CONFIRMED-BUG, ballot half CONFIRMED-DESIGN-CHOICE; audits/review-2026-08-19/A/collated-findings.md §D "G-25 — Dev audit markers leak into `free_text`") + C-67 (audits/review-2026-08-19/B/collated-findings.md §4 row C-67; audits/review-2026-08-19/B/meetings-manager.md §P2-9); roadmap item audits/review-2026-08-19/D/FINAL-synthesis.md §4 wave-2 row 2.8, audits/review-2026-08-19/D/synth-credibility.md §4 row 9, audits/review-2026-08-19/D/cross-track-map.md §2.2 G-25 row; meetings/manager.py:382-384, :403-408, :479-481, :516-518 (the five turn-side marker literals), :1595-1597 + :1648-1652 (the two splice sites, both inside `MeetingManager._collect_turn` at :1353), :3937-3940 (the contract the splice breaks), :3910-3981 (`_drop_non_roster_claims`, the markers built in its loop at :3958-3966); agents/strategic/prompts/qwen3_6_27b/accusation_round.j2:136 + :154, accusation_round_roll_call.j2:133 + :151, vote_ballot.j2:91 (the five unfiltered `turn.free_text` renders); api/replay_loader.py:2528-2550 (`_turn_view` and today's one-off emergency-strip), :2856-2863 (`_BALLOT_PREFIX_MARKERS`), :2874-2882 (`_MARKER_REPR_VALUE` / `_marker_pattern`), :2893-2923 (`_parse_rewrite_reasons`); api/schemas.py:627-657 (`TurnView`), :840-876 (`BallotView`, the chip precedent); meetings/schemas.py:358-383 (`MeetingTurn`); DESIGN.md:595-597 (the ballot-marker sanction); audits/audit-2026-06-11-2218-gameplay-data.md:38 (H-H-4, the "Frankenstein turn record" that bounded the quote and left the visibility); tasks/phase-18.md 18.9 (the default-OFF lever shape with committed-bytes counterfactuals)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
